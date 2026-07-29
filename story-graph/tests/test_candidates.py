"""Stage C: deterministic candidate generation.

These are recall-first generators, so the tests care most about the failure that makes
one useless: burying real finds under noise. On the Book 3 manuscript the first version
returned 283 candidates topped by "I'm", "You're" and "Chapter"; the extractor rules
pinned here are what turned that into 47 topped by a character who appears 104 times.
"""
import inspect
from pathlib import Path

import pytest
import story_graph as sg
import story_graph_candidates as sgc
from conftest import make_graph

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "series/books/book-3/imported/Story-Graph-from-act1.md"
CHAPTERS = ROOT / "series/books/book-3/phase-7-drafting/chapters"

# The Book 3 manuscript is gitignored (unpublished, and this repo is public), so the two
# tests below that need it skip on any fresh clone. These ship instead: a synthetic graph
# + 3 chapters carrying the same traps at small scale, so the properties are checked
# everywhere and Book 3 remains the real-scale run on the author's machine.
FIXTURES = Path(__file__).resolve().parent / "fixtures"
MINI = FIXTURES / "mini-graph.md"
MINI_CH = FIXTURES / "chapters"


# ------------------------------------------------------------------ proper-noun extraction


def test_sentence_initial_words_are_not_names():
    got = sgc.proper_nouns("Snow came down in fat flakes. Rows of shelves vanished.")
    assert got == {}, got


def test_a_word_seen_midsentence_is_trusted_even_at_a_sentence_start():
    text = "Henderson dragged the mats. The room smelled of Henderson's cigarettes."
    assert any("Henderson" in k for k in sgc.proper_nouns(text))


def test_dialogue_opening_quote_does_not_make_the_first_word_a_name():
    """The bug that produced "Get", "Do", "Let" and "Look" as characters: the first word
    of a quoted sentence isn't at offset 0, so an offset test trusts it."""
    text = '"Get out," he said. "Look at me." "Do it now."'
    assert sgc.proper_nouns(text) == {}


def test_contractions_are_not_characters():
    """"I'm" appeared 98 times and "You're" 47 in the first run, ahead of every real name."""
    text = "Margot said I'm fine. You're not. They're wrong. Don't argue. We're late."
    found = sgc.proper_nouns("The room was quiet. " + text)
    assert not any(w in " ".join(found) for w in ("I'm", "You're", "They're", "Don't", "We're"))


def test_markdown_headings_are_structure_not_prose():
    assert "Chapter" not in " ".join(sgc.proper_nouns("# Chapter Seven\n\nThe snow fell."))


def test_multiword_names_group_into_one_candidate():
    text = "The car stopped. Evelyn Hart signed it. Later Evelyn Hart left."
    assert "Evelyn Hart" in sgc.proper_nouns(text)


# --------------------------------------------------------------------------- unresolved


def _graph(entities):
    body = "## Entities\n| id | type | status | voice | note |\n|---|---|---|---|---|\n"
    return sg.parse_graph(make_graph(Entities=body + entities))


def test_unresolved_reports_only_names_with_no_entity(tmp_path):
    (tmp_path / "ch01.md").write_text(
        "The hall was cold. Jonah nodded at Henderson. Later Jonah found Henderson asleep. "
        "Henderson snored.", encoding="utf-8")
    g = _graph("| jonah-harrow | Character | active | - | Jonah |\n")
    rows = sgc.unresolved(g, tmp_path, sg._alias_cell, min_count=2)
    names = {r[0] for r in rows}
    assert "Henderson" in names
    assert not any("Jonah" in n for n in names), "a modelled entity must not be reported"


def test_token_overlap_resolves_a_first_name_to_a_kebab_id(tmp_path):
    (tmp_path / "ch01.md").write_text("She waited. Margot arrived. Then Margot left.",
                                      encoding="utf-8")
    g = _graph("| margot-vance | Character | active | - |  |\n")
    assert sgc.unresolved(g, tmp_path, sg._alias_cell, 2) == []


def test_a_declared_alias_resolves(tmp_path):
    (tmp_path / "ch01.md").write_text("He turned. Sheriff Harrow spoke. Then Sheriff Harrow left.",
                                      encoding="utf-8")
    g = _graph("| jonah-harrow | Character | active | - | Jonah; Sheriff Harrow |\n")
    assert sgc.unresolved(g, tmp_path, sg._alias_cell, 2) == []


def test_min_count_filters_walk_ons(tmp_path):
    (tmp_path / "ch01.md").write_text("The bar was loud. A man named Dodge nodded once.",
                                      encoding="utf-8")
    g = _graph("| jonah-harrow | Character | active | - | Jonah |\n")
    assert sgc.unresolved(g, tmp_path, sg._alias_cell, min_count=2) == []
    assert any(r[0] == "Dodge" for r in sgc.unresolved(g, tmp_path, sg._alias_cell, min_count=1))


def test_rows_are_ranked_by_frequency_with_a_first_locator(tmp_path):
    # Each name appears mid-sentence: a word only ever seen at a sentence start is
    # untrusted by design, and real prose does not keep a character permanently there.
    (tmp_path / "ch01.md").write_text("She nodded at Rare. Then Rare left.", encoding="utf-8")
    (tmp_path / "ch02.md").write_text("He found Common there. He asked Common twice. "
                                      "Later Common returned. She saw Common again.",
                                      encoding="utf-8")
    g = _graph("| x | Character | active | - |  |\n")
    rows = sgc.unresolved(g, tmp_path, sg._alias_cell, 2)
    assert rows[0][0] == "Common" and rows[0][1] > rows[1][1]
    assert rows[0][2] == "ch02" and next(r for r in rows if r[0] == "Rare")[2] == "ch01"


# ---------------------------------------------------------------------------- conflicts


def _props(rows, epi=""):
    kw = {"Propositions": ("## Propositions\n| prop-id | statement | canon-status | governing-source | span |\n"
                           "|---|---|---|---|---|\n" + rows)}
    if epi:
        kw["Epistemic States"] = ("## Epistemic States\n| prop-id | holder | mode | since-ch | span |\n"
                                  "|---|---|---|---|---|\n" + epi)
    return sg.parse_graph(make_graph(**kw))


def test_same_chapter_clash_is_separated_from_a_cross_chapter_state_change():
    """The decisions.md 2.4 call, which is the entire reason this command partitions."""
    g = _props(
        "| p1 | Margot entered the sealed basement alone | true | ms | provisional |\n"
        "| p2 | Margot never entered the sealed basement alone | true | ms | provisional |\n"
        "| p3 | Jackson Harrow is held in the battery tank | true | ms | provisional |\n"
        "| p4 | Jackson Harrow is freed from the battery tank | true | ms | provisional |\n",
        epi=("| p1 | reader | knows | 14 | provisional |\n"
             "| p2 | reader | knows | 14 | provisional |\n"
             "| p3 | reader | knows | 3 | provisional |\n"
             "| p4 | reader | knows | 20 | provisional |\n"))
    same, cross, undated = sgc.conflicts(g)
    assert [(r[0], r[1]) for r in same] == [("p1", "p2")], same
    assert [(r[0], r[1]) for r in cross] == [("p3", "p4")], cross
    assert undated == []
    assert same[0][6] is True, "one side negated -> polarity clash"
    assert cross[0][6] is False, "two positive claims -> no clash, still a candidate"


def test_undated_propositions_cannot_be_partitioned():
    g = _props("| p1 | Jackson is held in the tank | true | ms | provisional |\n"
               "| p2 | Jackson is freed from the tank | true | ms | provisional |\n")
    same, cross, undated = sgc.conflicts(g)
    assert (same, cross) == ([], []) and len(undated) == 1


def test_unrelated_claims_are_not_candidates():
    g = _props("| p1 | The library contains active old magic | true | ms | provisional |\n"
               "| p2 | Margot drives a rusted blue truck | true | ms | provisional |\n")
    assert sgc.conflicts(g) == ([], [], [])


def test_cross_chapter_rows_are_ordered_earliest_first():
    g = _props("| p-late | Jackson is freed from the battery tank | true | ms | provisional |\n"
               "| p-early | Jackson is held in the battery tank | true | ms | provisional |\n",
               epi=("| p-late | reader | knows | 20 | provisional |\n"
                    "| p-early | reader | knows | 3 | provisional |\n"))
    _, cross, _ = sgc.conflicts(g)
    assert cross[0][0] == "p-early" and cross[0][2] < cross[0][3], "chronology must read forward"


def test_evidence_locator_anchors_a_proposition_without_epistemic_states():
    ev = ("## Evidence\n| span-id | source-id | locator | quote | note |\n|---|---|---|---|---|\n"
          "| ev1 | ms | ch07 | q | |\n")
    g = sg.parse_graph(make_graph(
        Propositions=("## Propositions\n| prop-id | statement | canon-status | governing-source | span |\n"
                      "|---|---|---|---|---|\n| p1 | x | true | ms | ev1 |\n"),
        Evidence=ev))
    assert sgc._prop_chapter(g) == {"p1": 7}


def test_cli_overlap_default_matches_the_function_default():
    """These drifted apart once and the command silently returned nothing: the argparse
    default overrode the function's, so a threshold change had no effect."""
    src = (ROOT / "story-graph/assets/story_graph.py").read_text(encoding="utf-8")
    import re
    m = re.search(r'"--overlap".*?default=([\d.]+)', src)
    assert m, "no --overlap argument found"
    fn_default = inspect.signature(sgc.conflicts).parameters["overlap"].default
    assert float(m.group(1)) == fn_default


# -------------------------------------------------------- against the shipped mini fixture


def test_the_shipped_fixture_is_itself_a_valid_graph():
    """Guards everything else in this section. If the fixture drifts out of the ontology,
    the tests built on it are measuring the wrong thing — and its 7 quotes are hard-verified
    against the shipped chapters here, so a typo in either cannot pass unnoticed."""
    rep = sg.validate(str(MINI), chapters_dir=str(MINI_CH))
    assert rep.errors == [], rep.errors
    # exactly the two rows deliberately marked provisional — no accidental unverified claims
    assert len(rep.warnings) == 2, rep.warnings
    assert all("provisional" in w for w in rep.warnings), rep.warnings


def test_a_frequent_unmodelled_name_surfaces_and_nothing_else_does():
    """The whole point of `unresolved`, on a fixture that always ships. Halloran is named
    9 times and has no entity row; the three modelled characters and every junk token the
    real manuscript produced must stay out. A generator that returns everything is as
    useless as one that returns nothing, so this asserts BOTH directions."""
    g = sg.parse_graph(MINI.read_text(encoding="utf-8"))
    rows = sgc.unresolved(g, MINI_CH, sg._alias_cell, min_count=2)
    names = [r[0] for r in rows]

    assert "Halloran" in names, "an unmodelled name appearing 9 times must be reported"
    assert rows[0][0] == "Halloran" and rows[0][2] == "ch01", rows[0]

    for junk in ("I'm", "You're", "They're", "Don't", "We're", "Get", "Do", "Look",
                 "Chapter", "Beat", "Somebody", "Nobody", "Outside"):
        assert junk not in names, f"'{junk}' is not a character"
    for modelled in ("Delia", "Delia Foss", "Emmett", "Emmett Rourke", "Priya", "Priya Raman"):
        assert modelled not in names, f"'{modelled}' is modelled and must not be unresolved"


def test_every_cited_span_is_reachable_on_the_shipped_fixture():
    """Same ground-truth property as the Book 3 test below, but it runs on a clone. The
    fixture deliberately cites the two sentences that were unreachable in the real book:
    one broken by an ellipsis, one shorter than the old length floor."""
    import story_graph_propose as sp
    g = sg.parse_graph(MINI.read_text(encoding="utf-8"))
    ev = {e["span-id"]: (e.get("locator", ""), e.get("quote", ""))
          for e in g["sections"]["Evidence"] if e.get("span-id")}
    total, unreachable = 0, []
    for p in g["sections"]["Propositions"]:
        for sid in sg._span_ids(p.get("span", "")):
            loc, q = ev.get(sid, ("", ""))
            if not (loc and q):
                continue
            ch = MINI_CH / f"{loc}.md"
            assert ch.is_file(), f"fixture cites a chapter it does not ship: {loc}"
            total += 1
            if not any(sg.quote_found(s, q) for s in sp._sentences(ch.read_text(encoding="utf-8"))):
                unreachable.append((sid, q))
    assert total == 7, f"fixture should cite 7 spans, cited {total}"
    assert unreachable == [], f"cannot be offered as candidates: {unreachable}"


def test_the_two_historic_retrieval_regressions_are_pinned_by_the_fixture():
    """Named explicitly so deleting either quote from the fixture fails loudly rather than
    quietly reducing what the reachability test covers."""
    import story_graph_propose as sp
    quotes = {e["quote"] for e in sg.parse_graph(MINI.read_text(encoding="utf-8"))["sections"]["Evidence"]}
    assert "The March entries are... incomplete on purpose" in quotes, "ellipsis case dropped"
    assert "The vault key never left me" in quotes, "short-dialogue case dropped"
    sents = sp._sentences((MINI_CH / "ch01.md").read_text(encoding="utf-8"))
    assert any("March entries are..." in s and "incomplete on purpose" in s for s in sents), \
        "an ellipsis must not split the sentence"


# ------------------------------------------------------------------- against the real book


@pytest.mark.skipif(not CHAPTERS.is_dir(), reason="book-3 chapters not present")
def test_noise_stays_below_the_signal_on_the_real_manuscript():
    g = sg.parse_graph(FIXTURE.read_text(encoding="utf-8"))
    rows = sgc.unresolved(g, CHAPTERS, sg._alias_cell, min_count=4)
    names = [r[0] for r in rows]
    assert len(rows) < 80, f"{len(rows)} candidates is a wall of noise, not a work list"
    for junk in ("I'm", "You're", "They're", "Don't", "We're", "Chapter", "Get", "Look"):
        assert junk not in names, f"'{junk}' is not a character"
    # Henderson had 100+ mentions and no entity row until the ch15+ catch-up modelled
    # him. That he is now ABSENT from this list is the catch-up working; asserting the
    # junk-exclusion property above is what keeps holding as more names get modelled.
    g2 = {r["id"] for r in g["sections"]["Entities"] if r.get("id")}
    if "henderson" in g2:
        assert "Henderson" not in names, "a modelled entity must stop being unresolved"


# ------------------------------------------------- retrieval quality (Phase D follow-up)


def test_every_recorded_evidence_span_is_reachable_as_a_candidate():
    """Ground truth the graph supplies about itself: a sentence it cites as evidence must
    be offerable as a candidate. Two were not — one lost to an ellipsis being treated as a
    sentence end, one to a length floor set above real dialogue — and no ranking can find
    a sentence that was never in the pool."""
    import story_graph_propose as sp
    if not CHAPTERS.is_dir():
        pytest.skip("book-3 chapters not present")
    g = sg.parse_graph(FIXTURE.read_text(encoding="utf-8"))
    ev = {e["span-id"]: (e.get("locator", ""), e.get("quote", ""))
          for e in g["sections"]["Evidence"] if e.get("span-id")}
    total = unreachable = 0
    for p in g["sections"]["Propositions"]:
        for sid in sg._span_ids(p.get("span", "")):
            loc, q = ev.get(sid, ("", ""))
            if not (loc and q):
                continue
            ch = CHAPTERS / f"{loc}.md"
            if not ch.is_file():
                continue
            total += 1
            sents = sp._sentences(ch.read_text(encoding="utf-8"))
            if not any(sg.quote_found(s, q) for s in sents):
                unreachable += 1
    assert total and unreachable == 0, f"{unreachable}/{total} cited spans cannot be offered"


def test_an_ellipsis_is_not_a_sentence_end():
    import story_graph_propose as sp
    text = "He paused for a while. The Scrolls contain... inconvenient truths. She looked away."
    assert any("inconvenient truths" in s and "Scrolls contain" in s for s in sp._sentences(text))


def test_short_dialogue_is_still_a_candidate():
    """'"The lexivore is bound to B1.' is 29 characters and is a cited span in this graph."""
    import story_graph_propose as sp
    text = 'They stopped at the door and listened hard. "The lexivore is bound to B1. It cannot follow."'
    assert any("lexivore is bound" in s for s in sp._sentences(text))


def test_a_span_sharing_no_word_with_its_claim_is_flagged():
    """Cannot confirm a quote PROVES a claim — that is a reading. Can say the two are not
    about the same thing, which is mechanical."""
    g = sg.parse_graph(make_graph(
        Propositions=("## Propositions\n| prop-id | statement | canon-status | governing-source | span |\n"
                      "|---|---|---|---|---|\n"
                      "| p1 | The Deep Stacks distort space and direction | true | ms | ev1 |\n"
                      "| p2 | The wolf recognises her scent | true | ms | ev2 |\n"),
        Evidence=("## Evidence\n| span-id | source-id | locator | quote | note |\n|---|---|---|---|---|\n"
                  "| ev1 | ms | ch01 | Margot's flashlight cut a narrow cone | |\n"
                  "| ev2 | ms | ch01 | The wolf knew her scent at once | |\n")))
    rep = sg.Report()
    sg.check_span_relevance(g, rep)
    assert len(rep.warnings) == 1 and "p1" in rep.warnings[0]


# ------------------------------------------- portability (found by running on a 2nd book)


def test_chapters_are_found_whatever_the_project_calls_them(tmp_path):
    """Book 2 names its files `chapter-1.md`. The resolver matched only `<locator>.md` and
    `ch<NN>.md`, so every quote "could not be verified", every proposed row failed with
    "no chapter file", and `deviations` found nothing to compare. All silent."""
    ch = tmp_path / "ch"
    ch.mkdir()
    for n in (1, 2, 10):
        (ch / f"chapter-{n}.md").write_text("prose", encoding="utf-8")
    for loc, want in (("ch01", "chapter-1.md"), ("ch1", "chapter-1.md"),
                      ("chapter-2", "chapter-2.md"), ("ch10", "chapter-10.md")):
        got = sg._resolve_chapter(str(ch), loc)
        assert got is not None and got.name == want, (loc, got)
    assert sg._resolve_chapter(str(ch), "ch99") is None


def test_the_conventional_naming_still_resolves(tmp_path):
    ch = tmp_path / "ch"
    ch.mkdir()
    (ch / "ch01.md").write_text("prose", encoding="utf-8")
    (ch / "ch30.md").write_text("prose", encoding="utf-8")
    assert sg._resolve_chapter(str(ch), "ch01").name == "ch01.md"
    assert sg._resolve_chapter(str(ch), "ch30").name == "ch30.md"


def test_a_known_naming_convention_beats_a_fuzzy_number_match(tmp_path):
    ch = tmp_path / "ch"
    ch.mkdir()
    (ch / "chapter-3.md").write_text("a", encoding="utf-8")
    (ch / "3-draft.md").write_text("b", encoding="utf-8")
    assert sg._resolve_chapter(str(ch), "ch03").name == "chapter-3.md"


def test_an_ambiguous_number_resolves_to_nothing(tmp_path):
    """Two unconventionally-named files both claiming chapter 3 is a question for a
    human, not a coin-flip — and picking one silently is how the wrong prose ends up
    verifying a quote."""
    ch = tmp_path / "ch"
    ch.mkdir()
    (ch / "3-draft.md").write_text("a", encoding="utf-8")
    (ch / "part-3-final.md").write_text("b", encoding="utf-8")
    assert sg._resolve_chapter(str(ch), "ch03") is None


def test_chapter_discovery_is_numeric_and_skips_non_chapters(tmp_path):
    """`sorted()` put chapter-10 before chapter-2 the moment a project stopped
    zero-padding, and Book 2 keeps a `word_count_tracker.md` beside its prose — feeding a
    stats table to a proper-noun extractor pollutes the whole candidate pool."""
    ch = tmp_path / "ch"
    ch.mkdir()
    for n in (1, 2, 10, 11):
        (ch / f"chapter-{n}.md").write_text("prose", encoding="utf-8")
    (ch / "word_count_tracker.md").write_text("| words | 500 |", encoding="utf-8")
    (ch / "notes.md").write_text("nothing", encoding="utf-8")
    got = [p.stem for p in sg.chapter_files(str(ch))]
    assert got == ["chapter-1", "chapter-2", "chapter-10", "chapter-11"], got


def test_unresolved_finds_the_cast_of_an_unseen_book_with_no_entities(tmp_path):
    """The overfitting check: every threshold here was tuned on one supernatural book in
    third-person past. Run against a first-person present-tense contemporary one, with an
    EMPTY entity list, the top of the list must still be the actual cast."""
    ch = tmp_path / "ch"
    ch.mkdir()
    (ch / "chapter-1.md").write_text(
        "# Chapter 1: The Citation\n\n## Beat 1\n\n"
        "If anyone asks, I am not hiding. I set the cumin down and thought of Julian.\n"
        "\"You can't organize a heartbeat, El,\" my sister, Sarah, told me last week.\n"
        "Julian would have laughed. Sarah never laughs. I told Julian so.\n"
        "*   **11:00 AM:** Water the succulents.\n", encoding="utf-8")
    g = _graph("")                                  # no entities at all
    names = [r[0] for r in sgc.unresolved(g, ch, sg._alias_cell, min_count=2)]
    assert "Julian" in names and "Sarah" in names, names
    for junk in ("I", "Chapter", "Beat", "You", "If"):
        assert junk not in names, f"'{junk}' is not a character"
