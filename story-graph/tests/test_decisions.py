"""Stage A: the decision layer (reference/decisions.md) and the dependency weight
that turns the ratification queue from a list into a work plan."""
from pathlib import Path

import story_graph as sg
from conftest import make_graph

SKILL = Path(__file__).resolve().parents[1]
DECISIONS = SKILL / "reference" / "decisions.md"


def _graph(props="", epi="", loops="", canon=None):
    kw = {}
    if props:
        kw["Propositions"] = ("## Propositions\n| prop-id | statement | canon-status | governing-source | span |\n"
                              "|---|---|---|---|---|\n" + props)
    if epi:
        kw["Epistemic States"] = ("## Epistemic States\n| prop-id | holder | mode | since-ch | span |\n"
                                  "|---|---|---|---|---|\n" + epi)
    if loops:
        kw["Open Loops & Setups"] = ("## Open Loops & Setups\n| id | planted-ch | expectation | must-fire-by | status | span |\n"
                                     "|---|---|---|---|---|---|\n" + loops)
    text = make_graph(**kw)
    if canon is not None:
        text = text.replace("| current-canon-chapter | 0 |", f"| current-canon-chapter | {canon} |")
    return sg.parse_graph(text)


def test_blast_radius_counts_holders_evidence_and_weights_irony():
    g = _graph(
        props=("| p1 | contested claim | true | ms | ev1 ev2 |\n"
               "| p2 | quiet claim | true | ms | provisional |\n"),
        epi=("| p1 | reader | knows | 1 | provisional |\n"
             "| p1 | jonah | believes-false | 1 | provisional |\n"))
    b = sg.blast_radius(g)
    assert b["p1"]["holders"] == 2 and b["p1"]["evidence"] == 2
    assert b["p1"]["irony"] is True, "reader knows + a holder believes-false is irony"
    assert b["p1"]["score"] == 2 + 2 + 3
    assert b["p2"] == {"holders": 0, "evidence": 0, "irony": False, "score": 0}


def test_agreement_is_not_irony():
    g = _graph(props="| p1 | x | true | ms | provisional |\n",
               epi=("| p1 | reader | knows | 1 | provisional |\n"
                    "| p1 | jonah | knows | 1 | provisional |\n"))
    b = sg.blast_radius(g)
    assert b["p1"]["irony"] is False and b["p1"]["score"] == 2


def test_queue_ranks_heaviest_first_and_says_why():
    g = _graph(
        props=("| p-heavy | much rests here | true | ms | provisional |\n"
               "| p-light | inert | true | ms | provisional |\n"),
        epi=("| p-heavy | reader | knows | 1 | provisional |\n"
             "| p-heavy | jonah | believes-false | 2 | provisional |\n"))
    ranked = sg.unratified_ranked(g)
    labels = [lab for _, lab, _, _ in ranked]
    assert labels.index("p-heavy") < labels.index("p-light"), "weight must drive the order"
    heavy = next(r for r in ranked if r[1] == "p-heavy")
    assert heavy[2] > 0 and "dramatic irony" in heavy[3] and "2 holders" in heavy[3]
    light = next(r for r in ranked if r[1] == "p-light")
    assert light[2] == 0 and light[3] == "nothing depends on it yet"


def test_overdue_setup_outranks_an_inert_claim():
    """An open loop carries obligation weight, not dependency weight. Without that,
    every overdue setup sorts last — backwards for a work plan. The Book 3 fixture
    can't exercise this (all 10 of its loops have an empty must-fire-by), so it is
    pinned here."""
    g = _graph(props="| p-light | inert | true | ms | provisional |\n",
               loops=("| g-overdue | 2 | the gun fires | 5 | UNFIRED | provisional |\n"
                      "| g-open | 2 | later payoff | 40 | UNFIRED | provisional |\n"),
               canon=12)
    ranked = sg.unratified_ranked(g)
    by = {lab: (score, why) for _, lab, score, why in ranked}
    assert by["g-overdue"][0] > by["p-light"][0]
    assert "overdue by 7 ch" in by["g-overdue"][1]
    assert by["g-open"][0] == 0, "a deadline in the future is not overdue"
    assert ranked[0][1] == "g-overdue"


def test_missing_deadline_can_never_be_overdue():
    """The finding that put 1.4 in decisions.md: an empty must-fire-by makes a promise
    unfalsifiable, and the tool must not pretend otherwise."""
    g = _graph(loops="| g-nodate | 2 | someday |  | UNFIRED | provisional |\n", canon=99)
    score = next(s for _, lab, s, _ in sg.unratified_ranked(g) if lab == "g-nodate")
    assert score == 0


def test_ranking_preserves_the_unranked_queue_contents():
    """unratified() is still the compatibility surface; ranking must not add or drop rows."""
    g = _graph(props="| p1 | a | true | ms | provisional |\n",
               epi="| p1 | jonah | knows | 1 | provisional |\n",
               loops="| g1 | 1 | x | 4 | UNFIRED | provisional |\n", canon=9)
    assert {(s, l) for s, l in sg.unratified(g)} == {(s, l) for s, l, _, _ in sg.unratified_ranked(g)}


def test_decisions_doc_is_wired_into_the_skill_and_states_the_enforced_rule():
    """A decision layer nothing loads is a decision layer nobody follows."""
    skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    assert "reference/decisions.md" in skill
    assert "every mode" in skill.lower()
    doc = DECISIONS.read_text(encoding="utf-8")
    # the receipt gate must match what the validator actually enforces
    for token in ("canon-status", "undetermined", "contested", "embargoed-until",
                  "provisional", "must-fire-by"):
        assert token in doc, f"decisions.md must state the rule involving '{token}'"
    # both directions of the identity failure, not just the memorable one
    assert "Never merge" in doc and "Never split" in doc
    # the ceiling on the weight has to travel with the weight
    assert "one hop" in doc.lower() and "proposition → proposition" in doc


def test_receipt_gate_matches_the_documented_table():
    """decisions.md 1.1 claims undetermined/contested are exempt and true/false are not.
    If the validator ever disagrees, the doc is lying to the agent."""
    def errs(status):
        g = make_graph(Propositions=(
            "## Propositions\n| prop-id | statement | canon-status | governing-source | span |\n"
            "|---|---|---|---|---|\n" + f"| p1 | x | {status} | ms |  |\n"))
        p = Path(__file__).parent / f"_gate_{status}.md"
        p.write_text(g, encoding="utf-8")
        try:
            return [e for e in sg.validate(str(p)).errors if "evidence span" in e]
        finally:
            p.unlink()
    assert errs("true") and errs("false"), "a settled claim with no span must ERROR"
    assert not errs("undetermined") and not errs("contested"), "these are exempt per 1.1"


def test_one_holder_cannot_both_know_and_disbelieve():
    """A full-book run proposed rows where the READER both knows a claim and believes it
    false. That is not subtle — the audience cannot be in both states — and it means
    either the rows disagree or the claim is state-shaped (decisions.md 2.4)."""
    g = _graph(props=("| p1 | The Founding Scrolls are missing | true | ms | provisional |\n"
                      "| p2 | Jonah dies in the ch20 ambush | true | ms | provisional |\n"),
               epi=("| p1 | reader | knows | 2 | provisional |\n"
                    "| p1 | reader | believes-false | 29 | provisional |\n"
                    "| p2 | reader | knows | 20 | provisional |\n"
                    "| p2 | jonah | believes-false | 5 | provisional |\n"))
    rep = sg.Report()
    sg.check_stance_contradiction(g, rep)
    assert len(rep.warnings) == 1, rep.warnings
    assert "p1/reader" in rep.warnings[0] and "state-shaped" in rep.warnings[0]


def test_two_different_holders_disagreeing_is_irony_not_an_error():
    """The whole point of the ontology: one character wrong while the reader is right."""
    g = _graph(props="| p1 | x | true | ms | provisional |\n",
               epi=("| p1 | reader | knows | 1 | provisional |\n"
                    "| p1 | jonah | believes-false | 1 | provisional |\n"))
    rep = sg.Report()
    sg.check_stance_contradiction(g, rep)
    assert rep.warnings == []
