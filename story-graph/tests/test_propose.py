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
    assert [(r["values"]["holder"], r["values"]["mode"]) for r in p["rows"]] == [("margot-vance", "knows")]


def test_epistemic_rows_never_auto_pass_even_when_perfect(world):
    reply = json.dumps({"states": [{"prop-id": "p1", "holder": "margot-vance",
                                    "mode": "believes-false", "sentence": 1}]})
    p = _gen(world, "epistemic", reply)[0]
    p["_file"] = "x.json"
    verdicts = sgp.verify(p, world["graph"], world["chapters"])
    assert [v for _, v, _ in verdicts] == [sgp.HUMAN], verdicts


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
