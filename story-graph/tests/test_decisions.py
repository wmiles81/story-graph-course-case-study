"""Stage A: the decision layer (reference/decisions.md) and the dependency weight
that turns the ratification queue from a list into a work plan."""
from pathlib import Path

import pytest

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
    assert b["p2"] == {"holders": 0, "evidence": 0, "dependents": 0,
                       "irony": False, "score": 0}


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


# ------------------------------------------------ proposition shape (decisions.md 2.4)

# Labelled from real Book 3 statements. decisions.md 2.4 has said "prefer event-shaped"
# since Stage A and nothing enforced it; the cost arrived as an epistemic run proposing
# "reader believes-false: The Founding Scrolls are missing" for chapters after they were
# recovered — correct at those chapters, and unrepresentable without time bounds.
SHAPES = [
    # can flip mid-book
    ("The Founding Scrolls are missing.", "state"),
    ("Margot is inside the library during the disturbance.", "state"),
    ("Margot possesses her grandmother's journal.", "state"),
    ("The current possessor of the Founding Scrolls is unknown.", "state"),
    ("Jackson Harrow is alive and being used as an Alpha-class battery.", "state"),
    # happened, so it stays happened
    ("Jonah takes custody of the original Integration Treaty.", "event"),
    ("Margot converts the private confrontation into public accountability.", "event"),
    ("Jonah's wolf identifies Margot as his mate.", "event"),
    ("Margot realizes she is in love with Jonah.", "event"),
    ("The Founding Scrolls were hidden rather than stolen.", "event"),
    ("The twelve-hour countdown remains active through Chapters 4-6.", "event"),
    # a rule of the world, true throughout
    ("Books in the library can animate and attack.", "rule"),
    # permanent properties that read like states but never flip
    ("The library contains active old magic.", "event"),
    ("The basement contains impossible architecture.", "event"),
    ("Level B1 contains predatory entities that consume text or language.", "event"),
]


def test_proposition_shape_matches_the_labelled_corpus():
    wrong = [(s, want, sg.proposition_shape(s)) for s, want in SHAPES
             if sg.proposition_shape(s) != want]
    assert not wrong, "\n".join(f"{w[1]} != {w[2]}: {w[0]}" for w in wrong)


def test_a_past_tense_fact_is_not_a_mutable_state():
    """'were hidden' is settled; 'are hidden' can stop being true."""
    assert sg.proposition_shape("The Scrolls were hidden in the vault.") == "event"
    assert sg.proposition_shape("The Scrolls are hidden in the vault.") == "state"


def test_an_anchored_claim_is_already_bounded():
    assert sg.proposition_shape("Jackson is alive.") == "state"
    assert sg.proposition_shape("Jackson is alive as of ch12.") == "event"


def test_the_report_ranks_by_what_already_depends_on_the_claim():
    """A state-shaped claim nobody holds is a latent problem; one with holders is a live
    one, because the contradiction is already reachable."""
    g = _graph(props=("| p1 | The Scrolls are missing | true | ms | provisional |\n"
                      "| p2 | The journal is hidden | true | ms | provisional |\n"),
               epi=("| p1 | reader | knows | 2 | provisional |\n"
                    "| p1 | jonah | knows | 3 | provisional |\n"))
    out = sg.shape_report(g)
    assert out.index("p1") < out.index("p2")
    assert "2 holders" in out and "1 of" not in out.splitlines()[0]


def test_a_graph_of_event_shaped_claims_reports_clean():
    g = _graph(props="| p1 | Jonah takes the Treaty in ch09 | true | ms | provisional |\n")
    assert "none —" in sg.shape_report(g)


def test_concealment_is_a_state_not_an_event():
    """"Margot conceals the journal" ends the moment she shows it — a full-book run
    proposed believes-false rows on it at ch30, when the secret was already out."""
    assert sg.proposition_shape("Margot conceals her grandmother's journal from Jonah.") == "state"
    assert sg.proposition_shape("Margot hides the journal from Jonah.") == "state"


def test_a_faction_named_guard_is_not_a_stative_verb():
    """Adding `guards`/`protects` matched the NOUN in this book's Grey Guard and flagged
    four of its plot events as mutable states. Precision first: a checker that is wrong
    a third of the time is one nobody reads."""
    for s in ["The Grey Guard arrives as an anti-magic siege legion under Valerius.",
              "The Escher-floor trap contains the first Grey Guard vanguard.",
              "Jonah uses an obsolete AM transmitter to bypass the Grey Guard jamming field."]:
        assert sg.proposition_shape(s) == "event", s


def test_unanchored_propositions_are_reported_separately():
    """A different defect from being state-shaped: not that the claim flips, but that it
    was never placed in time — so a generator offers it for belief in every chapter,
    including forty pages before it happens."""
    g = _graph(props=("| p1 | Jonah takes the Treaty | true | ms | provisional |\n"
                      "| p2 | Margot solves the riddle | true | ms | provisional |\n"),
               epi="| p1 | reader | knows | 9 | provisional |\n")
    un = [pid for pid, _ in sg.unanchored_propositions(g)]
    assert un == ["p2"], un
    out = sg.shape_report(g)
    assert "UNANCHORED (1 of 2)" in out and "p2" in out


# --------------------------------------------- depends-on: structural weight, not popularity


def _dep(props, epi=""):
    body = ("## Propositions\n| prop-id | statement | canon-status | governing-source | span | depends-on |\n"
            "|---|---|---|---|---|---|\n" + props)
    kw = {"Propositions": body}
    if epi:
        kw["Epistemic States"] = ("## Epistemic States\n| prop-id | holder | mode | since-ch | span |\n"
                                  "|---|---|---|---|---|\n" + epi)
    return sg.parse_graph(make_graph(**kw))


def test_dependents_are_counted_through_the_chain():
    """A claim underpinning a chain is load-bearing however few people have an opinion
    about it — the whole point of the edge."""
    g = _dep("| a | the vault was sealed in 1974 | true | ms | provisional | |\n"
             "| b | only a Keeper can open it | true | ms | provisional | a |\n"
             "| c | Margot must have taken the Scrolls | true | ms | provisional | b |\n"
             "| d | unrelated weather fact | true | ms | provisional | |\n")
    dep = sg.transitive_dependents(g)
    assert dep["a"] == {"b", "c"}, dep["a"]
    assert dep["b"] == {"c"} and dep["c"] == set() and dep["d"] == set()


def test_structure_outranks_popularity_in_the_queue():
    """The failure this fixes: 49 of Book 3's 122 propositions scored zero, including
    foundational ones, because ranking counted believers only."""
    g = _dep("| root | the vault was sealed in 1974 | true | ms | provisional | |\n"
             "| mid | only a Keeper can open it | true | ms | provisional | root |\n"
             "| leaf | Margot took the Scrolls | true | ms | provisional | mid |\n"
             "| popular | the town is cold in winter | true | ms | provisional | |\n",
             epi=("| popular | reader | knows | 1 | provisional |\n"
                  "| popular | jonah | knows | 1 | provisional |\n"))
    b = sg.blast_radius(g)
    assert b["root"]["dependents"] == 2 and b["root"]["score"] == 4
    assert b["popular"]["holders"] == 2 and b["popular"]["score"] == 2
    ranked = [lab for _, lab, _, _ in sg.unratified_ranked(g)]
    assert ranked.index("root") < ranked.index("popular")
    why = next(w for _, lab, _, w in sg.unratified_ranked(g) if lab == "root")
    assert "2 claims rest on it" in why


def test_a_dependency_cycle_is_an_error():
    """While a cycle exists, "what rests on this" has no answer, so the traversal must
    refuse rather than loop."""
    g = _dep("| a | x | true | ms | provisional | c |\n"
             "| b | y | true | ms | provisional | a |\n"
             "| c | z | true | ms | provisional | b |\n")
    rep = sg.Report()
    sg.check_dependencies(g, {"a", "b", "c"}, rep)
    assert any("cycle" in e for e in rep.errors), rep.errors
    assert sg.transitive_dependents(g)["a"] == {"b", "c"}, "must terminate, not hang"


@pytest.mark.parametrize("row,fragment", [
    ("| a | x | true | ms | provisional | a |\n", "lists itself"),
    ("| a | x | true | ms | provisional | nope |\n", "not a declared proposition"),
])
def test_bad_dependency_references_are_errors(row, fragment):
    rep = sg.Report()
    sg.check_dependencies(_dep(row), {"a"}, rep)
    assert any(fragment in e for e in rep.errors), rep.errors


def test_a_graph_without_the_column_scores_exactly_as_before():
    """Backward compatibility is the whole reason this needed no version bump: an old
    graph has no `depends-on`, so the new term is zero and nothing moves."""
    g = _graph(props="| p1 | x | true | ms | provisional |\n",
               epi="| p1 | reader | knows | 1 | provisional |\n")
    b = sg.blast_radius(g)
    assert b["p1"]["dependents"] == 0 and b["p1"]["score"] == 1
    rep = sg.Report()
    sg.check_dependencies(g, {"p1"}, rep)
    assert rep.errors == []
