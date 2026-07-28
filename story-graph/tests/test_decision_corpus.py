"""Stage B: the decision corpus and its scoring harness.

The harness is what makes a rule change measurable, so the harness itself has to be
trustworthy: a grader that scores a wrong answer as correct is worse than no grader.
No test here touches the network — every scored run uses a substituted chat.
"""
import json
from pathlib import Path

import pytest
import story_graph as sg
import story_graph_decisions as sgd
from conftest import make_graph

CASES = Path(__file__).resolve().parent / "decisions"


def test_shipped_corpus_is_structurally_sound():
    cases = sgd.load_cases(CASES)
    assert len(cases) >= 8
    assert sgd.check_corpus(cases) == []


def test_every_category_carries_both_polarities():
    """Without a control, a degenerate strategy — always 'ambiguous', always
    'unsupported', always propose a row — scores well while deciding nothing."""
    cases = sgd.load_cases(CASES)
    for cat in {c["category"] for c in cases}:
        answers = {tuple(sorted(c["expect"].items())) for c in cases if c["category"] == cat}
        assert len(answers) > 1, f"category '{cat}' has no control case"


def test_corpus_check_catches_a_case_that_can_never_fail(tmp_path):
    (tmp_path / "bad.md").write_text(
        "# bad\n- category: resolution\n- ask: entities\n\n## Scene\nx\n\n## Trap\ny\n",
        encoding="utf-8")
    problems = sgd.check_corpus(sgd.load_cases(tmp_path))
    assert any("no Expect block" in p for p in problems)


def test_corpus_check_catches_a_control_less_category(tmp_path):
    for n in ("a", "b"):
        (tmp_path / f"{n}.md").write_text(
            f"# {n}\n- category: temporal\n- ask: temporal\n\n## Scene\nx\n\n"
            "## Expect\n- verdict: contradiction\n\n## Trap\ny\n", encoding="utf-8")
    assert any("no control" in p for p in sgd.check_corpus(sgd.load_cases(tmp_path)))


def test_corpus_check_catches_unknown_keys_and_missing_claim(tmp_path):
    (tmp_path / "a.md").write_text(
        "# a\n- category: basis\n- ask: basis\n\n## Scene\nx\n\n"
        "## Expect\n- bogus_key: 1\n\n## Trap\ny\n", encoding="utf-8")
    problems = sgd.check_corpus(sgd.load_cases(tmp_path))
    assert any("unknown expectation key" in p for p in problems)
    assert any("needs a Claim" in p for p in problems)


@pytest.mark.parametrize("raw,want", [
    ('```json\n{"verdict": "state-change"}\n```', {"verdict": "state-change"}),
    ('Sure! {"verdict": "contradiction"} — hope that helps', {"verdict": "contradiction"}),
    ('<think>hmm</think>\n{"supported": true}', {"supported": True}),
    ('{"a": {"b": 1}} and then {"c": 2}', {"a": {"b": 1}}),        # first BALANCED object
    ('{"q": "a } brace in a string"}', {"q": "a } brace in a string"}),
    ('no json at all', None),
    ('{"broken": ', None),
])
def test_json_extraction_survives_how_models_actually_reply(raw, want):
    assert sgd._json_from(raw) == want


def test_grader_scores_each_expectation_and_reports_the_miss():
    case = {"expect": {"entity_count": "2", "ambiguity": "yes"}, "ask": "entities"}
    perfect = {"people": [{"canonical": "a"}, {"canonical": "b"}], "ambiguous": True}
    assert sgd.grade(case, perfect)[:2] == (2, 2)
    merged = {"people": [{"canonical": "a"}], "ambiguous": False}
    pts, tot, notes = sgd.grade(case, merged)
    assert (pts, tot) == (0, 2) and sum("MISS" in n for n in notes) == 2
    assert sgd.grade(case, None)[:2] == (0, 2)


def test_grader_is_order_insensitive_on_rows_but_not_lenient():
    case = {"expect": {"rows": "2, 4"}, "ask": "inclusion"}
    assert sgd.grade(case, {"rows": [4, 2]})[0] == 1, "order must not matter"
    assert sgd.grade(case, {"rows": [2, 4, 1]})[0] == 0, "an extra row is a wrong answer"
    assert sgd.grade(case, {"rows": [2]})[0] == 0, "a missing row is a wrong answer"
    empty = {"expect": {"rows": ""}, "ask": "inclusion"}
    assert sgd.grade(empty, {"rows": []})[0] == 1
    assert sgd.grade(empty, {"rows": [1]})[0] == 0


def test_a_perfect_model_scores_full_marks_on_the_shipped_corpus():
    """Proves the corpus is answerable and the grader agrees with its own expectations —
    if this fails, a case is mis-specified and every real score is meaningless."""
    cases = {c["id"]: c for c in sgd.load_cases(CASES)}

    def oracle(system, user):
        c = next(c for c in cases.values() if c["scene"].splitlines()[0] in user)
        e = c["expect"]
        if c["ask"] == "entities":
            return json.dumps({"people": [{"canonical": f"p{i}"} for i in range(int(e["entity_count"]))],
                               "ambiguous": e.get("ambiguity", "no") == "yes"})
        if c["ask"] == "inclusion":
            return json.dumps({"rows": [int(x) for x in e["rows"].replace(",", " ").split()]})
        if c["ask"] == "temporal":
            return json.dumps({"verdict": e["verdict"]})
        return json.dumps({"supported": e["supported"] == "yes"})

    text, (pts, tot) = sgd.run(CASES, oracle, verbose=False)
    assert tot > 0 and pts == tot, text
    assert "MISS" not in text


def test_a_degenerate_model_cannot_pass():
    """The whole reason for controls: a fixed reply must score poorly."""
    always = json.dumps({"people": [{"canonical": "x"}], "ambiguous": True,
                         "rows": [1, 2, 3], "verdict": "contradiction", "supported": True})
    _, (pts, tot) = sgd.run(CASES, lambda s, u: always, verbose=False)
    assert pts <= tot * 0.4, f"a constant answer scored {pts}/{tot} — the corpus lacks controls"


def test_format_failure_is_retried_once_then_reported_separately():
    """A model that can't emit JSON is failing compliance, not judgement. Conflating the
    two makes the score unreadable — and it flakes run to run."""
    calls = []

    def flaky(system, user):
        calls.append(user)
        return "I think about it thus." if len(calls) % 2 else json.dumps({"verdict": "state-change"})

    text, _ = sgd.run(CASES, flaky, verbose=False)
    assert any("JSON object ONLY" in u for u in calls), "must retry with a stricter instruction"
    text2, _ = sgd.run(CASES, lambda s, u: "never json", verbose=False)
    assert "[FMT " in text2 and "compliance failure, not a wrong decision" in text2
    assert "[MISS]" not in text2, "a format failure must not be reported as a wrong decision"


def test_structural_run_needs_no_provider():
    text, (pts, tot) = sgd.run(CASES, None)
    assert "STRUCTURE — ok" in text and "No provider configured" in text and (pts, tot) == (0, 0)


# --------------------------------------------------------------- the deterministic half


def _entities(rows):
    body = "## Entities\n| id | type | status | voice | note |\n|---|---|---|---|---|\n"
    return sg.parse_graph(make_graph(Entities=body + rows))


def test_alias_collision_is_an_error():
    """The real find in Book 3: two Locations both claiming 'Heart of the Archive',
    two minutes' walk apart per the graph's own Locations table."""
    g = _entities("| level-b4 | Location | active | - | B4; Heart of the Archive |\n"
                  "| b4-vault | Location | active | - | Heart of the Archive; Archives proper |\n")
    rep = sg.Report()
    sg.check_aliases(g, {"level-b4", "b4-vault"}, rep)
    assert any("claimed by 2 entities" in e for e in rep.errors)


def test_alias_that_is_another_entitys_id_is_an_error():
    g = _entities("| jonah-harrow | Character | active | - | Jonah |\n"
                  "| sheriff | Character | active | - | jonah-harrow |\n")
    rep = sg.Report()
    sg.check_aliases(g, {"jonah-harrow", "sheriff"}, rep)
    assert any("another entity's canonical id" in e for e in rep.errors)


def test_prose_notes_do_not_become_aliases():
    """Without the guard, 'provisional — auto-registered from an assertion reference'
    splits into convincing nonsense and three entities collide on it. False collisions
    are worse than no checking, because they train you to ignore the checker."""
    g = _entities("| analyst | Character | active | - | provisional — auto-registered from an assertion reference; type guessed Character |\n"
                  "| council | Faction | active | - | provisional — auto-registered from an assertion reference; type guessed Faction |\n")
    rep = sg.Report()
    sg.check_aliases(g, {"analyst", "council"}, rep)
    assert rep.errors == [], rep.errors


def test_real_alias_lists_still_parse_with_the_guard_on():
    g = _entities("| margot-vance | Character | active | - | Margot; Ms. Vance |\n")
    row = g["sections"]["Entities"][0]
    assert sg._alias_cell(row) == ["Margot", "Ms. Vance"], "the guard must not eat real aliases"


def test_explicit_aliases_column_wins_over_note():
    body = ("## Entities\n| id | type | status | voice | aliases | note |\n|---|---|---|---|---|---|\n"
            "| evelyn-hart | Character | active | - | Evie; the prosecutor | she of the sharp pencils. |\n")
    g = sg.parse_graph(make_graph(Entities=body))
    assert sg._alias_cell(g["sections"]["Entities"][0]) == ["Evie", "the prosecutor"]


def test_book3_fixture_has_no_alias_collisions_left():
    f = Path(__file__).resolve().parents[2] / "series/books/book-3/imported/Story-Graph-from-act1.md"
    if not f.exists():
        pytest.skip("book-3 fixture not present")
    rep = sg.Report()
    g = sg.parse_graph(f.read_text(encoding="utf-8"))
    ids = {r["id"] for r in g["sections"]["Entities"] if r.get("id")}
    sg.check_aliases(g, ids, rep)
    assert rep.errors == [], rep.errors
