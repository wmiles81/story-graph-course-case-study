"""Multi-book series graphs.

The ontology says a series graph is ONE cumulative canon with series-continuous chapter
numbers, and that it MUST carry a chapter-convention legend. Nothing implemented the
legend, so a series graph's Evidence could never be verified: `--chapters-dir` is a single
directory, and the on-disk numbering (1..20) does not match the series locators
(ch31..ch50). The safety model went quiet — the same silent degradation that the chapter
resolver had, one layer up.
"""
import story_graph as sg
from conftest import make_graph


def _series(tmp_path, legend_lines, ev_locator="ch22", quote="The gap was here.",
            planted=None, log="- ch 22: (B3 ch2) something happened."):
    """Two books on disk with DIFFERENT naming conventions, plus a graph over both."""
    b1 = tmp_path / "book-a" / "chapters"
    b2 = tmp_path / "book-b" / "chapters"
    b1.mkdir(parents=True)
    b2.mkdir(parents=True)
    # `planted` is what actually appears in book B's chapter 2; `quote` is what the
    # Evidence row CITES. They differ only in the wrong-book test, which is the point.
    planted = quote if planted is None else planted
    for n in range(1, 21):
        (b1 / f"chapter-{n}.md").write_text(
            f"Book A chapter {n}. Nothing here.", encoding="utf-8")
    for n in range(1, 31):
        (b2 / f"ch{n:02d}.md").write_text(
            f"Book B chapter {n}. {planted if n == 2 else 'Filler prose only.'}", encoding="utf-8")
    text = make_graph(
        Sources=("## Sources\n| source-id | type | authority | note |\n|---|---|---|---|\n"
                 "| ms | manuscript | 100 | governing |\n"),
        Evidence=("## Evidence\n| span-id | source-id | locator | quote | note |\n|---|---|---|---|---|\n"
                  f"| ev1 | ms | {ev_locator} | {quote} | |\n"),
    ).replace("| current-canon-chapter | 0 |", "| current-canon-chapter | 50 |")
    text = text.replace("## Canon Commit Log", "## Canon Commit Log\n" + log)
    i = text.index("\n## ")
    text = text[:i] + "\n" + "\n".join(legend_lines) + "\n" + text[i:]
    g = tmp_path / "Series-Graph.md"
    g.write_text(text, encoding="utf-8")
    return g


def _legend(tmp_path):
    return [f"> B1 ch1-20 — {tmp_path}/book-a/chapters",
            f"> B2 ch21-50 — {tmp_path}/book-b/chapters"]


def test_a_series_quote_verifies_across_the_book_boundary(tmp_path):
    """No --chapters-dir at all: the legend is what makes this verifiable."""
    g = _series(tmp_path, _legend(tmp_path))
    rep = sg.validate(str(g))
    assert rep.errors == [], rep.errors


def test_the_boundary_arithmetic_is_right(tmp_path):
    """ch21 is the second book's chapter ONE. Off by one here points every quote check at
    the neighbouring chapter, which would verify just often enough to be trusted."""
    g = _series(tmp_path, _legend(tmp_path))
    leg = sg.parse_chapter_legend(g.read_text(encoding="utf-8"))
    got = {loc: (sg.resolve_series_chapter(loc, leg, str(g)) or "").__str__().split("/")[-1]
           for loc in ("ch1", "ch20", "ch21", "ch22", "ch50", "ch51")}
    assert got == {"ch1": "chapter-1.md", "ch20": "chapter-20.md", "ch21": "ch01.md",
                   "ch22": "ch02.md", "ch50": "ch30.md", "ch51": ""}, got


def test_a_quote_from_the_wrong_book_is_caught(tmp_path):
    """The point of the legend: it sends the checker to the RIGHT book, so prose that
    exists elsewhere in the series cannot pass as evidence here."""
    # cite prose that genuinely exists — in the OTHER book
    g = _series(tmp_path, _legend(tmp_path), quote="Book A chapter 3. Nothing here.",
                planted="Filler prose only.")
    rep = sg.validate(str(g))
    assert any("not found" in e for e in rep.errors), rep.errors


def test_a_legend_written_with_ch_on_both_bounds_parses(tmp_path):
    """`ch?` matched "c" plus an optional "h", so it demanded a literal c before the upper
    bound and the legend never parsed at all."""
    leg = sg.parse_chapter_legend("> B1 ch1-ch20 — /tmp/x\n> B2 ch21-ch50 — /tmp/y\n")
    assert [(lo, hi) for lo, hi, _, _ in leg] == [(1, 20), (21, 50)]


def test_overlapping_ranges_are_an_error(tmp_path):
    g = _series(tmp_path, [f"> B1 ch1-20 — {tmp_path}/book-a/chapters",
                           f"> B2 ch15-50 — {tmp_path}/book-b/chapters"])
    assert any("overlaps" in e for e in sg.validate(str(g)).errors)


def test_a_backwards_range_is_an_error(tmp_path):
    g = _series(tmp_path, [f"> B1 ch1-20 — {tmp_path}/book-a/chapters",
                           f"> B2 ch50-21 — {tmp_path}/book-b/chapters"])
    assert any("backwards" in e for e in sg.validate(str(g)).errors)


def test_a_legend_pointing_nowhere_is_an_error(tmp_path):
    g = _series(tmp_path, [f"> B1 ch1-20 — {tmp_path}/book-a/chapters",
                           "> B2 ch21-50 — /no/such/place"])
    assert any("not a directory" in e for e in sg.validate(str(g)).errors)


def test_a_series_log_without_a_legend_is_an_error(tmp_path):
    """`(B# chN)` in the log says series graph. Without a legend it cannot be verified,
    and silently unverified is the failure this whole design exists to prevent."""
    g = _series(tmp_path, [])
    assert any("no chapter-convention legend" in e for e in sg.validate(str(g)).errors)


def test_a_single_book_graph_is_untouched(tmp_path):
    """No legend, no (B# chN) mapping — nothing about series handling may fire."""
    g = _series(tmp_path, [], log="- ch 22: the Scrolls are discovered missing.")
    rep = sg.validate(str(g))
    assert not any("legend" in e for e in rep.errors), rep.errors
