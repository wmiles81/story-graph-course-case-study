"""Stage D generators: prose in, candidate rows out.

No test here touches the network — every run uses a scripted chat. What matters is that
the generator DISCARDS bad output rather than passing it downstream: the gate exists to
catch what slips through, not to be the only line of defence.
"""
import json
from pathlib import Path

import pytest
import story_graph as sg
import story_graph_propose as sp
import story_graph_proposals as sgp
from conftest import make_graph

QUOTE = "She watched as Henderson dragged the mats into the middle of the room."


@pytest.fixture
def world(tmp_path):
    ch = tmp_path / "chapters"
    ch.mkdir()
    (ch / "ch05.md").write_text(
        # Henderson appears MID-sentence: a name only ever seen at a sentence start is
        # distrusted by the extractor, and real prose does not keep one permanently there.
        f"The hall was cold. {QUOTE} Margot said nothing at all.\n"
        "She had never trusted the vault. Jonah watched her decide.\n", encoding="utf-8")
    g = tmp_path / "g.md"
    g.write_text(make_graph(
        Entities=("## Entities\n| id | type | status | voice | note |\n|---|---|---|---|---|\n"
                  "| jonah-harrow | Character | active | - | Jonah |\n"
                  "| margot-vance | Character | active | - | Margot |\n"),
        Propositions=("## Propositions\n| prop-id | statement | canon-status | governing-source | span |\n"
                      "|---|---|---|---|---|\n"
                      "| p1 | Henderson dragged the mats into the room | true | ms | provisional |\n"),
    ).replace("| current-canon-chapter | 0 |", "| current-canon-chapter | 30 |"), encoding="utf-8")
    return {"graph": str(g), "chapters": str(ch), "dir": tmp_path}


def _gen(world, kind, reply, **kw):
    out = world["dir"] / "proposals"
    kw.setdefault("min_count", 1)   # the test chapter mentions each name once
    written = sp.generate(kind, world["graph"], world["chapters"],
                          lambda s, u: reply, model="m", provider="ollama",
                          out_dir=str(out), log=lambda *a: None, **kw)
    return [json.loads(Path(p).read_text(encoding="utf-8")) for p in written]


# ------------------------------------------------------------------------------ entities


def test_entities_generator_shapes_rows_and_drops_junk(world):
    reply = json.dumps({"entities": [
        {"id": "henderson", "type": "Character", "aliases": "Henderson",
         "quote": QUOTE, "chapter": "ch05", "confidence": "high"},
        {"id": "jonah-harrow", "type": "Character", "quote": QUOTE, "chapter": "ch05"},
        {"id": "Not Kebab", "type": "Character", "quote": QUOTE, "chapter": "ch05"},
        {"id": "vibes", "type": "Feeling", "quote": QUOTE, "chapter": "ch05"},
    ]})
    props = _gen(world, "entities", reply)
    assert len(props) == 1
    ids = [r["values"]["id"] for r in props[0]["rows"]]
    assert ids == ["henderson"], "duplicate, non-kebab and bad-type rows must be dropped here"
    assert props[0]["rows"][0]["basis"]["quote"] == QUOTE


def test_entities_rows_survive_the_gate_but_still_need_a_human(world):
    """A real run auto-passed `gnome` and `alpha` as Characters. The quote proves the
    NAME APPEARS; it never proves the thing is an entity of that type, which is the
    inclusion decision in decisions.md 1.2."""
    reply = json.dumps({"entities": [{"id": "henderson", "type": "Character",
                                      "aliases": "Henderson", "quote": QUOTE,
                                      "chapter": "ch05", "confidence": "high"}]})
    p = _gen(world, "entities", reply)[0]
    p["_file"] = "x.json"
    verdicts = sgp.verify(p, world["graph"], world["chapters"])
    assert [v for _, v, _ in verdicts] == [sgp.HUMAN], verdicts


# ------------------------------------------------------------------------------ evidence


def test_evidence_generator_emits_the_row_and_the_ratifying_update(world):
    """An Evidence row on its own ratifies nothing — the proposition has to point at it."""
    reply = json.dumps({"evidence": [{"prop-id": "p1", "sentence": 1}]})
    p = _gen(world, "evidence", reply)[0]
    ops = [(r["section"], r.get("op", "add")) for r in p["rows"]]
    assert ops == [("Evidence", "add"), ("Propositions", "set")]
    sid = p["rows"][0]["values"]["span-id"]
    assert p["rows"][1]["set"] == {"span": sid}, "the update must cite the row just added"


def test_evidence_pair_survives_the_gate_and_ratifies_once_accepted(world):
    """BOTH halves need a human. The Evidence row asserts a quote proves a claim; the
    update that points the claim at that span asserts exactly the same thing. Letting the
    update auto-pass routed around the rule the gate exists to enforce."""
    reply = json.dumps({"evidence": [{"prop-id": "p1", "sentence": 1}]})
    p = _gen(world, "evidence", reply)[0]
    p["_file"] = "x.json"
    verdicts = sgp.verify(p, world["graph"], world["chapters"])
    assert [v for _, v, _ in verdicts] == [sgp.HUMAN, sgp.HUMAN], verdicts
    text = Path(world["graph"]).read_text(encoding="utf-8")
    merged = sgp.apply_rows(text, p, [1, 2], sg.parse_graph(text))
    g2 = sg.parse_graph(merged)
    prop = g2["sections"]["Propositions"][0]
    assert prop["span"].startswith("ev-p1-ch05"), prop
    assert not sg.is_provisional(prop), "a ratified claim must leave the queue"


def test_evidence_generator_ignores_a_claim_it_was_not_offered(world):
    reply = json.dumps({"evidence": [{"prop-id": "p-invented", "sentence": 1}]})
    assert _gen(world, "evidence", reply) == []


def test_evidence_quotes_cannot_be_fabricated_by_construction(world):
    """The model answers with an INDEX into a shortlist code built from the chapter, so
    the quote is verbatim by construction rather than by good behaviour. A made-up
    sentence has no way to enter: there is no field to put it in."""
    for bad in ({"prop-id": "p1", "sentence": 99}, {"prop-id": "p1", "sentence": 0},
                {"prop-id": "p1", "sentence": "the third one"},
                {"prop-id": "p1", "quote": "Henderson wept for a while."}):
        assert _gen(world, "evidence", json.dumps({"evidence": [bad]})) == [], bad


# ----------------------------------------------------------------------------- epistemic


def test_epistemic_generator_filters_unknown_holders_and_modes(world):
    reply = json.dumps({"states": [
        {"prop-id": "p1", "holder": "margot-vance", "mode": "knows", "sentence": 1},
        {"prop-id": "p1", "holder": "the-mayor", "mode": "knows", "sentence": 1},
        {"prop-id": "p1", "holder": "jonah-harrow", "mode": "vibes", "sentence": 1},
        {"prop-id": "p1", "holder": "jonah-harrow", "mode": "knows", "sentence": 99},
    ]})
    p = _gen(world, "epistemic", reply)[0]
    stances = [r for r in p["rows"] if r["section"] == "Epistemic States"]
    assert [(r["values"]["holder"], r["values"]["mode"]) for r in stances] == [("margot-vance", "knows")]


def test_a_stance_row_keeps_the_receipt_it_was_judged_on(world):
    """The judge picked a real sentence and the gate proved it exists — and the row used to
    land as `span: provisional`, discarding it, so `validate` could only ever answer
    "unverified". On Book 3 that was 183 of 183 stance rows permanently unverifiable."""
    reply = json.dumps({"states": [
        {"prop-id": "p1", "holder": "margot-vance", "mode": "knows", "sentence": 1},
        {"prop-id": "p1", "holder": "jonah-harrow", "mode": "believes", "sentence": 1},
    ]})
    p = _gen(world, "epistemic", reply)[0]
    ev = [r for r in p["rows"] if r["section"] == "Evidence"]
    stances = [r for r in p["rows"] if r["section"] == "Epistemic States"]
    assert len(ev) == 1, "two holders agreeing on one sentence is ONE receipt, not two"
    assert ev[0]["values"]["quote"] == QUOTE
    span = ev[0]["values"]["span-id"]
    assert all(s["values"]["span"] == span for s in stances), "every stance must cite it"
    assert "provisional" not in span
    # and the receipt is emitted BEFORE the rows citing it, since verification is in order
    assert p["rows"].index(ev[0]) < min(p["rows"].index(s) for s in stances)


def test_epistemic_rows_never_auto_pass_even_when_perfect(world):
    reply = json.dumps({"states": [{"prop-id": "p1", "holder": "margot-vance",
                                    "mode": "believes-false", "sentence": 1}]})
    p = _gen(world, "epistemic", reply)[0]
    p["_file"] = "x.json"
    verdicts = sgp.verify(p, world["graph"], world["chapters"])
    # Two rows now (the receipt and the stance) and NEITHER may auto-pass: an Evidence row
    # is a transcription the gate can check, but which claim it supports is still a reading.
    assert [v for _, v, _ in verdicts] == [sgp.HUMAN, sgp.HUMAN], verdicts


def test_epistemic_skips_states_the_graph_already_has(world):
    text = Path(world["graph"]).read_text(encoding="utf-8")
    Path(world["graph"]).write_text(text.replace(
        "## Epistemic States\n| prop-id | holder | mode | since-ch | span |\n|---|---|---|---|---|\n",
        "## Epistemic States\n| prop-id | holder | mode | since-ch | span |\n|---|---|---|---|---|\n"
        "| p1 | margot-vance | knows | 5 | provisional |\n"), encoding="utf-8")
    reply = json.dumps({"states": [{"prop-id": "p1", "holder": "margot-vance",
                                    "mode": "knows", "sentence": 1}]})
    assert _gen(world, "epistemic", reply) == []


def test_a_claim_not_yet_true_is_not_offered_for_an_earlier_chapter(world):
    """A belief cannot be dated before the scene that could cause it. Offering a later
    claim against an earlier chapter invites exactly that error."""
    text = Path(world["graph"]).read_text(encoding="utf-8")
    Path(world["graph"]).write_text(text.replace(
        "| p1 | Henderson dragged the mats into the room | true | ms | provisional |",
        "| p1 | Henderson dragged the mats into the room | true | ms | provisional |\n"
        "| p9 | Henderson dragged the mats into the room later | true | ms | provisional |")
        .replace("## Epistemic States\n| prop-id | holder | mode | since-ch | span |\n|---|---|---|---|---|\n",
                 "## Epistemic States\n| prop-id | holder | mode | since-ch | span |\n|---|---|---|---|---|\n"
                 "| p9 | reader | knows | 20 | provisional |\n"), encoding="utf-8")
    g = sg.parse_graph(Path(world["graph"]).read_text(encoding="utf-8"))
    ctx = sp._ctx_epistemic(g, Path(world["chapters"], "ch05.md").read_text(encoding="utf-8"), 5, 18)
    assert "p9" not in {c["prop-id"] for c in ctx["claims"]}


# -------------------------------------------------------------------------------- caching


def test_replies_are_cached_so_a_rerun_is_free(world):
    calls = []
    reply = json.dumps({"evidence": [{"prop-id": "p1", "sentence": 1}]})
    cache = str(world["dir"] / "cache")

    def chat(s, u):
        calls.append(u)
        return reply

    for _ in range(2):
        sp.generate("evidence", world["graph"], world["chapters"], chat, model="m",
                    provider="ollama", out_dir=str(world["dir"] / "p"), cache_dir=cache,
                    log=lambda *a: None)
    assert len(calls) == 1, "the second run must be served from cache"


def test_cache_key_changes_when_the_chapter_changes(world):
    calls = []
    reply = json.dumps({"evidence": [{"prop-id": "p1", "sentence": 1}]})
    cache = str(world["dir"] / "cache")

    def chat(s, u):
        calls.append(u)
        return reply

    args = dict(model="m", provider="ollama", out_dir=str(world["dir"] / "p"),
                cache_dir=cache, log=lambda *a: None)
    sp.generate("evidence", world["graph"], world["chapters"], chat, **args)
    ch = Path(world["chapters"], "ch05.md")
    ch.write_text(ch.read_text(encoding="utf-8") + "\nA new line of prose.\n", encoding="utf-8")
    sp.generate("evidence", world["graph"], world["chapters"], chat, **args)
    assert len(calls) == 2, "edited prose must invalidate the cached reply"


def test_unknown_kind_is_rejected(world):
    with pytest.raises(ValueError):
        sp.generate("vibes", world["graph"], world["chapters"], lambda s, u: "{}")


def test_garbage_from_the_model_yields_no_rows_rather_than_an_exception(world):
    for junk in ("", "I'd rather not", "{not json", '{"evidence": null}', '{"other": 1}'):
        assert _gen(world, "evidence", junk) == []
        assert _gen(world, "entities", junk) == []


# ------------------------------------------ holes found by the Phase 4 generator review


def test_the_model_can_only_pick_a_sentence_it_was_shown(tmp_path):
    """The index design's whole promise. `_sents` once held every ranked sentence while
    only the positive-scoring ones were SHOWN, so a model returning an index it never saw
    got a row quoting unrelated prose — real prose, so the gate waved it through.
    Evidence for "the wolf knew the scent of mate" came back as "The kettle whistled"."""
    ch = tmp_path / "ch"
    ch.mkdir()
    (ch / "ch05.md").write_text(
        "The wolf knew the scent of mate before the man did at all. "
        "Rain fell steadily on the tin roof throughout the long afternoon. "
        "The kettle whistled and nobody got up to take it off the heat.\n", encoding="utf-8")
    g = tmp_path / "g.md"
    g.write_text(make_graph(
        Propositions=("## Propositions\n| prop-id | statement | canon-status | governing-source | span |\n"
                      "|---|---|---|---|---|\n"
                      "| p1 | the wolf knew the scent of mate | true | ms | provisional |\n")
    ).replace("| current-canon-chapter | 0 |", "| current-canon-chapter | 30 |"), encoding="utf-8")
    graph = sg.parse_graph(g.read_text(encoding="utf-8"))
    claims = sp._ctx_evidence(graph, (ch / "ch05.md").read_text(encoding="utf-8"), 18)
    c = claims[0]
    assert len(c["candidates"]) == len(c["_sents"]), "shown and fillable must not diverge"
    unseen = len(c["_sents"]) + 1
    assert sp._rows_evidence({"evidence": [{"prop-id": "p1", "sentence": unseen}]},
                             claims, "ch05", graph, "ms", [1]) == []


def test_the_same_bound_holds_for_epistemic(tmp_path):
    ch = tmp_path / "ch"
    ch.mkdir()
    (ch / "ch05.md").write_text(
        "The wolf knew the scent of mate before the man did at all. "
        "Rain fell steadily on the tin roof throughout the long afternoon.\n", encoding="utf-8")
    g = tmp_path / "g.md"
    g.write_text(make_graph(
        Entities=("## Entities\n| id | type | status | voice | note |\n|---|---|---|---|---|\n"
                  "| margot-vance | Character | active | - | Margot |\n"),
        Propositions=("## Propositions\n| prop-id | statement | canon-status | governing-source | span |\n"
                      "|---|---|---|---|---|\n"
                      "| p1 | the wolf knew the scent of mate | true | ms | provisional |\n")
    ).replace("| current-canon-chapter | 0 |", "| current-canon-chapter | 30 |"), encoding="utf-8")
    graph = sg.parse_graph(g.read_text(encoding="utf-8"))
    ctx = sp._ctx_epistemic(graph, (ch / "ch05.md").read_text(encoding="utf-8"), 5, 18)
    if ctx is None:
        pytest.skip("no epistemic context for this fixture")
    for c in ctx["claims"]:
        assert len(c["candidates"]) == len(c["_sents"])


def test_an_entity_quote_comes_from_our_list_not_the_model(world):
    """Entities was the last generator trusting a model-written quote. The model now
    names a candidate; the sentence and locator are attached from our own shortlist."""
    reply = json.dumps({"entities": [{"name": "Henderson", "id": "henderson",
                                      "type": "Character", "aliases": "Henderson",
                                      "quote": "A sentence the model made up entirely.",
                                      "chapter": "ch99", "confidence": "high"}]})
    p = _gen(world, "entities", reply)[0]
    assert p["rows"][0]["basis"]["quote"] == QUOTE, "the model's quote must be ignored"
    assert p["rows"][0]["basis"]["locator"] == "ch05", "the model's locator must be ignored"


def test_an_entity_we_never_offered_is_dropped(world):
    reply = json.dumps({"entities": [{"name": "Nobody", "id": "nobody",
                                      "type": "Character", "confidence": "high"}]})
    assert _gen(world, "entities", reply) == []


def test_a_candidate_sentence_never_spans_a_scene_divider(tmp_path):
    """Splitting sentences across the whole body glued text either side of a `---` into
    one 'sentence'. Those were offered to the model, chosen, then rejected by the gate —
    rows wasted on a bad shortlist rather than a bad judgement. Every candidate this
    produces must be findable in the prose by the same check the gate uses."""
    text = ('The struggle is over.\n\n---\n\n"We have to walk past them," Margot said, '
            'gripping his arm tightly.\n\nRain kept on falling over the quiet town square.\n')
    for s in sp._sentences(text):
        assert sg.quote_found(text, s), f"offered a candidate the gate would reject: {s!r}"
    assert not any("---" in s for s in sp._sentences(text))


# ----------------------------------------------------------------- kind: dependencies


def _depworld(tmp_path):
    g = tmp_path / "g.md"
    g.write_text(make_graph(
        Propositions=("## Propositions\n| prop-id | statement | canon-status | governing-source | span | depends-on |\n"
                      "|---|---|---|---|---|---|\n"
                      "| a | the vault was sealed in 1974 | true | ms | provisional | |\n"
                      "| b | only a Keeper can open the vault | true | ms | provisional | |\n"
                      "| c | Margot took the Scrolls | true | ms | provisional | b |\n"),
    ).replace("| current-canon-chapter | 0 |", "| current-canon-chapter | 30 |"), encoding="utf-8")
    return g


def test_dependency_candidates_skip_claims_that_already_have_an_edge(tmp_path):
    """`c` is already answered; re-asking wastes the judge's attention and invites a
    second edge on a cell that is no longer empty."""
    g = _depworld(tmp_path)
    ctx = sp._ctx_dependencies(sg.parse_graph(g.read_text(encoding="utf-8")))
    assert ctx["open"] == {"a", "b"} and ctx["already"] == {"c": ["b"]}
    assert {x["prop-id"] for x in ctx["claims"]} == {"a", "b", "c"}, "context still shows all"


def test_dependency_rows_drop_what_cannot_be_written(tmp_path):
    g = _depworld(tmp_path)
    graph = sg.parse_graph(g.read_text(encoding="utf-8"))
    ctx = sp._ctx_dependencies(graph)
    answer = {"edges": [{"claim": "b", "needs": "a"},        # good
                        {"claim": "a", "needs": "a"},        # self
                        {"claim": "b", "needs": "zzz"},      # unknown id
                        {"claim": "c", "needs": "a"},        # cell already filled
                        {"claim": "b", "needs": "a"}]}       # duplicate
    rows = sp._rows_dependencies(answer, ctx, graph)
    assert [(r["key"]["prop-id"], r["set"]["depends-on"]) for r in rows] == [("b", "a")]


def test_a_dependency_edge_needs_a_human_but_not_a_quote(tmp_path):
    """A dependency is a claim about the story's STRUCTURE — "the Purge needs the breach"
    is written in no single sentence — so there is no quote to gate on. The checks that
    do apply are structural, and the direction still needs a person."""
    g = _depworld(tmp_path)
    p = {"kind": "dependencies", "generated": {"scope": "all"}, "_file": "d.json",
         "rows": [{"section": "Propositions", "op": "set", "key": {"prop-id": "b"},
                   "set": {"depends-on": "a"}, "basis": {"locator": "", "quote": ""}}]}
    verdicts = sgp.verify(p, str(g), "")
    assert [v for _, v, _ in verdicts] == [sgp.HUMAN], verdicts
    assert "direction is a reading" in verdicts[0][2]


def test_nothing_can_smuggle_another_cell_past_the_quote_gate(tmp_path):
    """The exemption is keyed off the column being EXACTLY depends-on. Pair it with any
    other cell and the quote gate applies again, so a row cannot opt itself out."""
    g = _depworld(tmp_path)
    p = {"kind": "dependencies", "generated": {"scope": "all"}, "_file": "d.json",
         "rows": [{"section": "Propositions", "op": "set", "key": {"prop-id": "b"},
                   "set": {"depends-on": "a", "canon-status": "false"},
                   "basis": {"locator": "", "quote": ""}}]}
    verdicts = sgp.verify(p, str(g), "")
    # Which guard catches it is not the point — the overwrite check happens to fire
    # first. The property is that the dependency exemption does NOT apply, so the row
    # cannot reach the graph by pairing an exempt column with a non-exempt one.
    assert verdicts[0][1] == sgp.FAIL
    assert "direction is a reading" not in verdicts[0][2], "must not get the exemption"


def test_an_edge_that_would_close_a_cycle_is_rejected(tmp_path):
    """`c` already needs `b`. Proposing that `b` needs `c` closes a loop, and while a
    cycle exists "what rests on this" has no answer."""
    g = _depworld(tmp_path)
    p = {"kind": "dependencies", "generated": {"scope": "all"}, "_file": "d.json",
         "rows": [{"section": "Propositions", "op": "set", "key": {"prop-id": "b"},
                   "set": {"depends-on": "c"}, "basis": {"locator": "", "quote": ""}}]}
    verdicts = sgp.verify(p, str(g), "")
    assert verdicts[0][1] == sgp.FAIL and "cycle" in verdicts[0][2], verdicts


# ------------------------------------------- epistemic claim selection (the silent-cap bug)


def _limitworld(tmp_path, n_filler=24):
    """A chapter that is plainly ABOUT one late-numbered claim, plus filler claims that
    each clear the relevance gate on generic words. Filler ids sort BEFORE the real one."""
    ch = tmp_path / "chapters"
    ch.mkdir()
    (ch / "ch09.md").write_text(
        "The convoy stopped at the ridge. Valerius raised the Feral Signal above the dam "
        "and the Grey Guard legion answered him. Margot watched the Feral Signal climb.\n\n"
        "Margot said nothing. Jonah watched the room. The vault was cold and the room "
        "was cold and Margot watched the vault.\n", encoding="utf-8")
    props = ("## Propositions\n| prop-id | statement | canon-status | governing-source | span |\n"
             "|---|---|---|---|---|\n")
    for i in range(n_filler):                      # p-001.. — generic, all gate-passing
        props += f"| p-{i:03d} | Margot watched the room | true | ms | provisional |\n"
    props += "| p-900 | Valerius raised the Feral Signal above the dam | true | ms | provisional |\n"
    # since-ch 1, not 9: an epistemic row anchors its claim, and an anchor on THIS chapter
    # legitimately outranks the unheld bonus — which would mask the tie-break under test.
    epi = ("## Epistemic States\n| prop-id | holder | mode | since-ch | span |\n|---|---|---|---|---|\n"
           "| p-000 | reader | knows | 1 | provisional |\n")
    ents = ("## Entities\n| id | type | status | voice | note |\n|---|---|---|---|---|\n"
            "| margot-vance | Character | active | - | Margot |\n"
            "| jonah-harrow | Character | active | - | Jonah |\n")
    g = tmp_path / "g.md"
    g.write_text(make_graph(Entities=ents, Propositions=props, **{"Epistemic States": epi}),
                 encoding="utf-8")
    return g, ch


def test_the_claim_a_chapter_is_about_survives_the_limit(tmp_path):
    """The bug this pins: `claims[:limit]` truncated in prop-id order, which is roughly
    story order, so a chapter's list filled with early-book claims and the late-book ones
    fell off. On Book 3 that hid the four most load-bearing claims in the manuscript
    (blast radius 49-58) from ALL 30 chapters — no judge could record who believed them.
    p-900 sorts last and is the only claim this chapter is actually about."""
    g, ch = _limitworld(tmp_path)
    graph = sg.parse_graph(g.read_text(encoding="utf-8"))
    ctx = sp._ctx_epistemic(graph, (ch / "ch09.md").read_text(encoding="utf-8"), 9, limit=6)
    offered = [c["prop-id"] for c in ctx["claims"]]
    assert "p-900" in offered, f"the chapter's own claim was truncated away: {offered}"
    assert offered[0] == "p-900", f"it should rank first, not merely survive: {offered}"
    assert len(offered) == 6, "the limit must still be honoured"


def test_a_claim_dropped_by_the_limit_is_reported_not_hidden(tmp_path):
    """A cap that says nothing reads as 'this chapter has nothing else to say'."""
    g, ch = _limitworld(tmp_path)
    graph = sg.parse_graph(g.read_text(encoding="utf-8"))
    ctx = sp._ctx_epistemic(graph, (ch / "ch09.md").read_text(encoding="utf-8"), 9, limit=6)
    assert len(ctx["dropped"]) == 19, ctx["dropped"]      # 25 gate-passing, 6 shown
    assert all(p.startswith("p-") for p in ctx["dropped"])
    assert "p-900" not in ctx["dropped"], "the ranked-first claim must never be the dropped one"


def test_a_claim_with_no_holder_outranks_one_already_held(tmp_path):
    """Filling the holder gap is the entire point of the pass, so an unheld claim wins a
    tie against an identical claim that already has a holder."""
    g, ch = _limitworld(tmp_path)
    graph = sg.parse_graph(g.read_text(encoding="utf-8"))
    ctx = sp._ctx_epistemic(graph, (ch / "ch09.md").read_text(encoding="utf-8"), 9, limit=25)
    offered = [c["prop-id"] for c in ctx["claims"]]
    # p-000 is the only filler that already carries a reader row; identical text otherwise.
    assert offered.index("p-000") > offered.index("p-001"), offered


def test_the_relevance_gate_admits_a_claim_written_in_the_authors_words(tmp_path):
    """Nouns match the prose; the author's verbs do not. At the old 0.5 gate this claim
    was unreachable in every chapter of Book 3."""
    g, ch = _limitworld(tmp_path)
    graph = sg.parse_graph(g.read_text(encoding="utf-8"))
    props = graph["sections"]["Propositions"]
    props.append({"prop-id": "p-901",
                  "statement": "Valerius activates a manufactured Feral Signal above the dam",
                  "canon-status": "true", "governing-source": "ms", "span": "provisional"})
    ctx = sp._ctx_epistemic(graph, (ch / "ch09.md").read_text(encoding="utf-8"), 9, limit=30)
    assert "p-901" in [c["prop-id"] for c in ctx["claims"]], \
        "'activates'/'manufactured' never appear in the prose, but Valerius/Feral/Signal/dam do"
