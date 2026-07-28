"""Stage 1: the proposal spine.

This is the gate every generated row passes before it can touch canon, so the tests are
mostly adversarial: each one is a defect the gate must catch. A gate that passes bad
rows is worse than no gate, because it launders them.
"""
import json
from pathlib import Path

import pytest
import story_graph as sg
import story_graph_proposals as sgp
from conftest import make_graph

QUOTE = "The wolf knew the scent before the man did."


@pytest.fixture
def world(tmp_path):
    """A small graph plus a chapters dir the quote gate can actually check against."""
    ch = tmp_path / "chapters"
    ch.mkdir()
    (ch / "ch05.md").write_text(f"Snow fell all morning. {QUOTE} He said nothing.", encoding="utf-8")
    g = tmp_path / "g.md"
    g.write_text(make_graph(
        Propositions=("## Propositions\n| prop-id | statement | canon-status | governing-source | span |\n"
                      "|---|---|---|---|---|\n| p1 | the wolf recognises her | true | ms | ev1 |\n"),
        Evidence=("## Evidence\n| span-id | source-id | locator | quote | note |\n|---|---|---|---|---|\n"
                  f"| ev1 | ms | ch05 | {QUOTE} | |\n"),
        **{"Epistemic States": ("## Epistemic States\n| prop-id | holder | mode | since-ch | span |\n"
                                "|---|---|---|---|---|\n| p1 | reader | knows | 5 | provisional |\n")}
    ).replace("| current-canon-chapter | 0 |", "| current-canon-chapter | 30 |"), encoding="utf-8")
    return {"graph": str(g), "chapters": str(ch), "dir": tmp_path}


def _prop(rows, **gen):
    g = {"provider": "ollama", "model": "m", "scope": "ch05"}
    g.update(gen)
    return {"kind": "epistemic", "generated": g, "rows": rows, "_file": "p.json"}


def _epi(holder="jonah", mode="suspects", ch="5", pid="p1", quote=QUOTE, loc="ch05", **kw):
    row = {"section": "Epistemic States",
           "values": {"prop-id": pid, "holder": holder, "mode": mode, "since-ch": ch, "span": ""},
           "basis": {"locator": loc, "quote": quote}, "reasoning": "r", "confidence": "high"}
    row.update(kw)
    return row


def _verdicts(world, rows, chapters=True):
    p = _prop(rows)
    return {i: (v, r) for i, v, r in
            sgp.verify(p, world["graph"], world["chapters"] if chapters else "")}, p


# ------------------------------------------------------------------------ the quote gate


def test_fabricated_quote_is_rejected(world):
    v, _ = _verdicts(world, [_epi(quote="She had always known about the vault.")])
    assert v[1][0] == sgp.FAIL and "not in ch05.md" in v[1][1]


def test_a_row_with_no_basis_quote_is_rejected(world):
    v, _ = _verdicts(world, [_epi(quote="")])
    assert v[1][0] == sgp.FAIL and "unanchored" in v[1][1]


def test_without_chapters_the_gate_refuses_rather_than_waves_through(world):
    """The dangerous failure mode: no chapters dir, so nothing can be checked. It must
    refuse, not pass."""
    v, _ = _verdicts(world, [_epi()], chapters=False)
    assert v[1][0] == sgp.FAIL and "without --chapters-dir" in v[1][1]


def test_a_locator_with_no_chapter_file_is_rejected(world):
    v, _ = _verdicts(world, [_epi(loc="ch99")])
    assert v[1][0] == sgp.FAIL and "no chapter file" in v[1][1]


# ------------------------------------------------------------- referential + range gates


@pytest.mark.parametrize("row,fragment", [
    (_epi(pid="p-nope"), "is not declared"),
    (_epi(holder="the-mayor"), "not a declared entity"),
    (_epi(mode="wonders-about"), "unknown mode"),
    (_epi(ch="44"), "beyond current-canon-chapter"),
    (_epi(ch="soon"), "is not a number"),
])
def test_each_referential_gate_fires(world, row, fragment):
    v, _ = _verdicts(world, [row])
    assert v[1][0] == sgp.FAIL and fragment in v[1][1], v[1]


def test_unknown_section_and_unknown_column_are_rejected(world):
    bad_section = {"section": "Vibes", "values": {"id": "x"}, "basis": {"locator": "ch05", "quote": QUOTE}}
    bad_col = _epi()
    bad_col["values"]["mood"] = "tense"
    v, _ = _verdicts(world, [bad_section, bad_col])
    assert v[1][0] == sgp.FAIL and "unknown section" in v[1][1]
    assert v[2][0] == sgp.FAIL and "not in the Epistemic States table" in v[2][1]


def test_empty_key_column_is_rejected(world):
    v, _ = _verdicts(world, [_epi(holder="")])
    assert v[1][0] == sgp.FAIL and "empty key column" in v[1][1]


def test_citing_an_undeclared_span_is_rejected(world):
    row = _epi()
    row["values"]["span"] = "ev-does-not-exist"
    v, _ = _verdicts(world, [row])
    assert v[1][0] == sgp.FAIL and "not declared in Evidence" in v[1][1]


# ------------------------------------------------------------------------ duplicate gates


def test_a_row_already_in_the_graph_is_rejected(world):
    v, _ = _verdicts(world, [_epi(holder="reader", mode="knows")])
    assert v[1][0] == sgp.FAIL and "already in the graph" in v[1][1]


def test_a_second_stance_by_the_same_holder_is_not_a_duplicate(world):
    """An embargo is modelled as `embargoed-until` followed later by `knows` for the same
    (proposition, holder). Keying duplicates without `mode` rejects that follow-up."""
    v, _ = _verdicts(world, [_epi(holder="reader", mode="suspects", ch="3")])
    assert v[1][0] == sgp.HUMAN, v[1]


def test_two_identical_rows_in_one_proposal_are_caught(world):
    v, _ = _verdicts(world, [_epi(holder="jonah"), _epi(holder="jonah")])
    assert v[1][0] == sgp.HUMAN
    assert v[2][0] == sgp.FAIL and "duplicate of row 1" in v[2][1]


# --------------------------------------------------------------- inference never auto-passes


def test_epistemic_rows_can_never_pass(world):
    """decisions.md: a proposition's quote is on the page, a belief is a reading of it,
    and no checker confirms a reading. This must hold even for a flawless row."""
    v, _ = _verdicts(world, [_epi()])
    assert v[1][0] == sgp.HUMAN and "inferences" in v[1][1]


def test_low_confidence_downgrades_a_row(world):
    row = {"section": "Locations & Distances",
           "values": {"from": "vault", "to": "library", "time": "3 min", "mode": "walk"},
           "basis": {"locator": "ch05", "quote": QUOTE}, "confidence": "low"}
    v, _ = _verdicts(world, [row])
    assert v[1][0] == sgp.HUMAN and "low confidence" in v[1][1]


def test_a_clean_transcription_row_passes(world):
    """Only sections that record a FACT rather than a reading can auto-pass. A distance
    is transcribed; an Evidence row asserts that a quote proves a claim, which is not."""
    row = {"section": "Locations & Distances",
           "values": {"from": "vault", "to": "library", "time": "3 min", "mode": "walk"},
           "basis": {"locator": "ch05", "quote": QUOTE}, "confidence": "high"}
    v, _ = _verdicts(world, [row])
    assert v[1][0] == sgp.PASS


def test_evidence_never_auto_passes(world):
    """A 3B model produced 24 evidence rows that ALL passed the gate while only ~1 in 12
    actually proved its claim. The quote being real is not the claim being proved."""
    row = {"section": "Evidence",
           "values": {"span-id": "ev2", "source-id": "ms", "locator": "ch05", "quote": QUOTE, "note": ""},
           "basis": {"locator": "ch05", "quote": QUOTE}, "confidence": "high"}
    v, _ = _verdicts(world, [row])
    assert v[1][0] == sgp.HUMAN


# ------------------------------------------------------------------- consequence checking


def test_a_row_that_breaks_validation_is_rejected_and_attributed(world):
    """Passes every cheap check, then violates an embargo — exactly what the consequence
    pass exists for."""
    text = Path(world["graph"]).read_text(encoding="utf-8")
    text = text.replace("| p1 | reader | knows | 5 | provisional |",
                        "| p1 | reader | knows | 5 | provisional |\n"
                        "| p1 | jonah | embargoed-until | 10 | provisional |")
    Path(world["graph"]).write_text(text, encoding="utf-8")
    v, _ = _verdicts(world, [_epi(holder="jonah", mode="knows", ch="3")])
    assert v[1][0] == sgp.FAIL and "introduces a validation error" in v[1][1]
    assert "embargo" in v[1][1]


def test_the_consequence_check_simulates_the_commit_line_too(world):
    """The bug this pins: the check simulated only the rows, so a malformed commit-log
    entry passed the gate and broke the graph AFTER the checker said yes."""
    import inspect
    src = inspect.getsource(sgp._errors_with)
    assert "append_commit" in src


def test_commit_line_is_not_a_chapter_entry(world):
    """The Canon Commit Log is a strictly-increasing record of canon ADVANCING. A
    back-fill of ch05 while canon sits at ch30 must not claim to be a chapter entry —
    it both lies and trips the log's own regression check."""
    line = sgp.commit_line(_prop([_epi()], scope="ch05"), [(1, sgp.HUMAN, "")], [1])
    assert not sg.LOG_RE.match(line.strip()), line
    assert "proposal ch05" in line and "p.json" in line


# ------------------------------------------------------------------------------- applying


def test_apply_inserts_into_the_right_table_and_forces_provisional(world):
    text = Path(world["graph"]).read_text(encoding="utf-8")
    p = _prop([_epi(holder="jonah")])
    merged = sgp.apply_rows(text, p, [1], sg.parse_graph(text))
    g2 = sg.parse_graph(merged)
    row = next(r for r in g2["sections"]["Epistemic States"] if r["holder"] == "jonah")
    assert row["mode"] == "suspects" and row["span"] == "provisional", row
    assert len(g2["sections"]["Propositions"]) == 1, "no other table may be touched"
    assert merged.count(QUOTE) == text.count(QUOTE), "the prose quote must not be duplicated"


def test_apply_preserves_everything_it_did_not_add(world):
    text = Path(world["graph"]).read_text(encoding="utf-8")
    merged = sgp.apply_rows(text, _prop([_epi(holder="jonah")]), [1], sg.parse_graph(text))
    added = set(merged.splitlines()) - set(text.splitlines())
    assert len(added) == 1
    assert set(text.splitlines()) - set(merged.splitlines()) == set(), "nothing may be lost"


def test_append_commit_lands_inside_the_log_section(world):
    text = Path(world["graph"]).read_text(encoding="utf-8")
    out = sgp.append_commit(text, "- proposal ch05: +1 epistemic states")
    tail = out.split("## Canon Commit Log", 1)[1]
    assert "- proposal ch05" in tail


def test_next_version_path_never_collides(tmp_path):
    g = tmp_path / "Story-Graph.md"
    g.write_text("x", encoding="utf-8")
    first = sg._next_version_path(str(g))
    assert first.endswith("Story-Graph_v1.md")
    Path(first).write_text("x", encoding="utf-8")
    assert sg._next_version_path(str(g)).endswith("Story-Graph_v2.md")


def test_cli_refuses_to_apply_a_rejected_row(world, tmp_path, capsys):
    pf = tmp_path / "p.json"
    pf.write_text(json.dumps(_prop([_epi(holder="jonah"), _epi(quote="not in the book")])),
                  encoding="utf-8")
    rc = sg.main(["apply-proposal", str(pf), "--graph", world["graph"],
                  "--chapters-dir", world["chapters"], "--accept", "1,2"])
    assert rc == 1 and "cannot be applied" in capsys.readouterr().out


def test_cli_apply_keeps_the_previous_version(world, tmp_path, capsys):
    pf = tmp_path / "p.json"
    pf.write_text(json.dumps(_prop([_epi(holder="jonah")])), encoding="utf-8")
    before = Path(world["graph"]).read_text(encoding="utf-8")
    rc = sg.main(["apply-proposal", str(pf), "--graph", world["graph"],
                  "--chapters-dir", world["chapters"], "--accept", "1"])
    assert rc == 0, capsys.readouterr().out
    kept = Path(world["graph"]).with_name("g_v1.md")
    assert kept.exists() and kept.read_text(encoding="utf-8") == before
    assert "jonah" in Path(world["graph"]).read_text(encoding="utf-8")


def test_accept_pass_takes_only_pass_rows_not_needs_human(world, tmp_path):
    """'pass' must mean PASS. Sweeping NEEDS-HUMAN in under a convenience flag would
    quietly undo the rule that inferences need a person."""
    loc = {"section": "Locations & Distances",
           "values": {"from": "vault", "to": "library", "time": "3 min", "mode": "walk"},
           "basis": {"locator": "ch05", "quote": QUOTE}, "confidence": "high"}
    pf = tmp_path / "p.json"
    pf.write_text(json.dumps(_prop([_epi(holder="jonah"), loc])), encoding="utf-8")
    assert sg.main(["apply-proposal", str(pf), "--graph", world["graph"],
                    "--chapters-dir", world["chapters"], "--accept", "pass"]) == 0
    g2 = sg.parse_graph(Path(world["graph"]).read_text(encoding="utf-8"))
    assert any(r["from"] == "vault" for r in g2["sections"]["Locations & Distances"])
    assert not any(r["holder"] == "jonah" for r in g2["sections"]["Epistemic States"])
