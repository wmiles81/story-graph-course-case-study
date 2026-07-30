from conftest import make_graph
import story_graph as sg


def prop_report(body, span_ids=frozenset({"s1"})):
    graph = sg.parse_graph(make_graph(Propositions=body))
    report = sg.Report()
    sources = {"ms": {"type": "manuscript", "authority": 100}}
    sg.check_propositions(graph, sources, set(span_ids), report)
    return report


def test_true_prop_needs_span():
    body = ("## Propositions\n| prop-id | statement | canon-status | governing-source | span |\n"
            "|---|---|---|---|---|\n| jackson-alive | Jackson lives | true | ms |  |\n")
    assert any("span" in e for e in prop_report(body).errors)


def test_true_prop_with_span_ok():
    body = ("## Propositions\n| prop-id | statement | canon-status | governing-source | span |\n"
            "|---|---|---|---|---|\n| jackson-alive | Jackson lives | true | ms | s1 |\n")
    assert prop_report(body).errors == []


def test_bad_canon_status_is_error():
    body = ("## Propositions\n| prop-id | statement | canon-status | governing-source | span |\n"
            "|---|---|---|---|---|\n| p1 | x | maybe | ms | s1 |\n")
    assert any("canon-status" in e for e in prop_report(body).errors)


def test_provisional_true_prop_without_span_warns_not_errors():
    body = ("## Propositions\n| prop-id | statement | canon-status | governing-source | span |\n"
            "|---|---|---|---|---|\n| p1 | x | true | ms | provisional |\n")
    r = prop_report(body)
    assert r.errors == [] and any("provisional" in w for w in r.warnings)


# ------------------------------------ stance windows: a corrected belief is not a clash


def _epi(rows, props="| p1 | Jackson dies in the ch20 ambush | true | ms | provisional |\n"):
    return sg.parse_graph(make_graph(
        Propositions=("## Propositions\n| prop-id | statement | canon-status | governing-source | span |\n"
                      "|---|---|---|---|---|\n" + props),
        **{"Epistemic States": ("## Epistemic States\n| prop-id | holder | mode | since-ch | until-ch | span |\n"
                                "|---|---|---|---|---|---|\n" + rows)}))


def test_a_holder_who_learns_better_is_not_a_contradiction():
    """The bug this fixes. The old check compared MODES only and named two explanations —
    the rows are wrong, or the claim is state-shaped. It missed the commonest one: the
    character was wrong and then found out. That is an arc, not an error, and warning about
    it taught authors to avoid `believes-false` entirely — Book 3 ended up with 173 `knows`
    rows and 6 `believes-false`, because the informative mode was the one that complained."""
    g = _epi("| p1 | jonah | believes-false | 1 | 20 | provisional |\n"
             "| p1 | jonah | knows | 20 |  | provisional |\n")
    rep = sg.Report()
    sg.check_stance_contradiction(g, rep)
    assert rep.warnings == [], rep.warnings


def test_overlapping_stances_are_still_a_contradiction():
    g = _epi("| p1 | jonah | believes-false | 1 | 25 | provisional |\n"
             "| p1 | jonah | knows | 20 |  | provisional |\n")
    rep = sg.Report()
    sg.check_stance_contradiction(g, rep)
    # Genuinely overlapping (1-25 vs 20-open): not the closeable case, so no until-ch hint.
    assert len(rep.warnings) == 1 and "overlapping chapters" in rep.warnings[0], rep.warnings
    assert "until-ch" not in rep.warnings[0], "do not suggest a fix that would not work"


def test_undated_stances_still_warn_because_nothing_proves_them_disjoint():
    g = _epi("| p1 | jonah | believes-false | 1 |  | provisional |\n"
             "| p1 | jonah | knows | 20 |  | provisional |\n")
    rep = sg.Report()
    sg.check_stance_contradiction(g, rep)
    assert len(rep.warnings) == 1
    # The commonest case, and the one where the fix is a single cell: name it explicitly.
    assert "until-ch 20" in rep.warnings[0], rep.warnings[0]
    assert "learned better" in rep.warnings[0]


def test_a_stance_cannot_end_before_it_starts():
    g = _epi("| p1 | jonah | believes-false | 20 | 3 | provisional |\n")
    rep = sg.Report()
    ids = {r["id"] for r in g["sections"]["Entities"] if r.get("id")} | {"jonah"}
    sg.check_epistemic(g, ids, {"p1"}, {"provisional"}, rep)
    assert any("not after since-ch" in e for e in rep.errors), rep.errors


def test_dramatic_irony_is_computable_once_stances_have_windows():
    """The payoff: a character confidently wrong about what the reader knows. Invisible to a
    linear read, and pure traversal here."""
    g = _epi("| p1 | reader | knows | 3 |  | provisional |\n"
             "| p1 | jonah | believes-false | 1 | 20 | provisional |\n")
    rows = sg.dramatic_irony(g)
    assert rows == [("p1", "jonah", 3, 20)], rows
    assert "1 pair" in sg.irony_report(rows, g)


def test_no_irony_when_the_reader_is_also_in_the_dark():
    g = _epi("| p1 | reader | knows | 21 |  | provisional |\n"
             "| p1 | jonah | believes-false | 1 | 20 | provisional |\n")
    assert sg.dramatic_irony(g) == [], "the reader learns after Jonah corrects — no irony"


def test_the_empty_irony_report_says_absence_is_suspicious():
    g = _epi("| p1 | reader | knows | 3 |  | provisional |\n")
    text = sg.irony_report(sg.dramatic_irony(g), g)
    assert "none recorded" in text and "unrecorded" in text


def test_a_graph_without_the_column_still_parses_and_validates():
    """Backward compatibility, the same property `depends-on` needed: tables are parsed by
    column NAME, so an older graph with no until-ch is unaffected and every stance is open."""
    g = sg.parse_graph(make_graph(**{"Epistemic States": (
        "## Epistemic States\n| prop-id | holder | mode | since-ch | span |\n"
        "|---|---|---|---|---|\n| p1 | jonah | believes-false | 1 | provisional |\n")}))
    row = g["sections"]["Epistemic States"][0]
    assert sg.stance_window(row) == (1, None), "no until-ch means the stance never closes"
