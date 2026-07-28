#!/usr/bin/env python3
"""Stage D: the generators. Prose in, candidate rows out — nothing else.

Every row produced here is written to a proposal file and has to survive
`verify-proposal` before it can touch the graph. This module therefore has exactly one
job: put a well-chosen question to a model and shape the reply into rows. It never
writes to the graph, and it is never the thing that decides a row is correct.

Three kinds, in the order they must run:

  entities   who is in the prose that the graph has never heard of. First, because a
             belief cannot name a holder that does not exist.
  evidence   which verbatim sentence proves a claim the graph asserts but cannot back.
             The safest kind: the quote gate checks it completely.
  epistemic  who knows / believes / believes-false / suspects what. The valuable kind,
             and the one no checker can fully confirm — see decisions.md part 2.

Replies are cached by (kind, scope, chapter digest, prompt version, model), so re-running
after an unrelated edit costs nothing and a crashed run resumes free.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import story_graph as sg
import story_graph_candidates as sgc
from story_graph_decisions import _json_from

PROMPT_VERSION = {"entities": "entities/1", "evidence": "evidence/1", "epistemic": "epistemic/1"}

# What an answer file must contain. The judge picks by NUMBER; it never writes a quote.
ANSWER_SHAPE = {
    "entities": '{"entities": [{"name": "<candidate name, copied exactly>", "id": "kebab-id", '
                '"type": "Character|Object|Location|Faction", "aliases": "A; B", '
                '"confidence": "high|low"}]}',
    "evidence": '{"evidence": [{"prop-id": "...", "sentence": <number, or 0 for none>}]}',
    "epistemic": '{"states": [{"prop-id": "...", "holder": "...", '
                 '"mode": "knows|believes|believes-false|suspects", "sentence": <number>}]}',
}

SYSTEM = (
    "You maintain a story graph: a structured model of a manuscript's hidden state. "
    "You PROPOSE rows; deterministic code verifies them against the manuscript and a human "
    "accepts them. Two rules override everything else:\n"
    "1. Never assert anything the text does not support. If you are unsure, omit the row.\n"
    "2. Every row must quote a VERBATIM sentence from the chapter you were given. The quote "
    "is checked character-for-character; an invented or paraphrased quote is rejected and "
    "wastes the row.\n"
    "Answer with one JSON object and nothing else."
)


# --------------------------------------------------------------------------- utilities


def _digest(*parts):
    h = hashlib.sha256()
    for p in parts:
        h.update(str(p).encode("utf-8", "replace"))
    return h.hexdigest()[:16]


def _cached(cache_dir, key, produce, log=print):
    """Model replies are pure functions of their inputs, so cache them. A 30-chapter book
    is 30 calls; without this, one crash costs all 30 again.

    A failed call returns None rather than raising: one chapter that times out must not
    end a 30-chapter run, and the failure is NOT cached, so a re-run retries only it.
    """
    p = Path(cache_dir) / f"{key}.txt" if cache_dir else None
    if p is not None and p.exists():
        return p.read_text(encoding="utf-8")
    try:
        out = produce()
    except Exception as e:
        log(f"  ! model call failed ({type(e).__name__}: {e}) — skipped, re-run to retry")
        return None
    if not (out or "").strip():
        # Never cache an empty reply. A cached empty is poison: it is served forever and
        # the chapter can never be re-tried, so a transient failure becomes permanent.
        log("  ! model returned nothing — not cached, re-run to retry")
        return None
    if p is not None:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(out, encoding="utf-8")
    return out


def _chapter_no(path):
    m = re.search(r"(\d+)", Path(path).stem)
    return int(m.group(1)) if m else 0


def _rows_of(graph, section):
    return graph["sections"].get(section, [])


def _entity_ids(graph):
    return {r["id"] for r in _rows_of(graph, "Entities") if r.get("id")}


# ------------------------------------------------------------------------ kind: entities


def _ctx_entities(graph, chapters_dir, limit, min_count=4):
    """Unresolved names, each with one real sentence showing how the prose uses it."""
    cands = sgc.unresolved(graph, chapters_dir, sg._alias_cell, min_count=min_count)[:limit]
    if not cands:
        return None
    texts = {p.stem: p.read_text(encoding="utf-8", errors="replace")
             for p in sorted(Path(chapters_dir).glob("*.md"))}
    lines = []
    for name, n, first in cands:
        sample = ""
        for s in re.split(r"(?<=[.!?])\s+", texts.get(first, "")):
            if name in s and 40 < len(s.strip()) < 320:
                sample = " ".join(s.split())
                break
        lines.append({"name": name, "count": n, "chapter": first, "sentence": sample})
    return {"candidates": [c for c in lines if c["sentence"]]}


def _prompt_entities(ctx, graph):
    types = ", ".join(sorted(sg.ENTITY_TYPES))
    known = sorted(_entity_ids(graph))[:60]
    body = [
        "These capitalised names appear in the manuscript but match no entity in the graph.",
        "For each one decide whether it is a real story entity worth modelling.",
        "",
        f"Entity types: {types}. Ids are kebab-case (e.g. jonah-harrow).",
        f"Entities already in the graph (do not duplicate): {', '.join(known)}",
        "",
        "OMIT a candidate when it is: a capitalised common noun, a species or job word used "
        "generically, a place mentioned once in passing, or anything you are unsure about. "
        "A missing row costs nothing; a wrong one corrupts everything that later cites it.",
        "",
        json.dumps(ctx["candidates"], indent=1),
        "",
        'Answer: {"entities": [{"name": "<the candidate name, copied exactly>", '
        '"id": "kebab-id", "type": "Character", "aliases": "Surface; Other Surface", '
        '"confidence": "high|low"}]}',
        "",
        "Do not write a quote — the sentence shown above is attached automatically.",
    ]
    return "\n".join(body)


def _rows_entities(answer, ctx, graph):
    """The quote and locator come from OUR candidate list, keyed by the name the model
    replied about — never from the model's own text.

    This was the one generator still trusting a model-written quote, which is why an
    entity run appeared to fabricate 5 of 9 (it hadn't — but nothing here would have told
    the difference). Same rule as evidence and epistemic: the model chooses, code fills.
    """
    known = _entity_ids(graph)
    by_name = {c["name"]: c for c in (ctx or {}).get("candidates", [])}
    out = []
    for e in (answer or {}).get("entities", []) or []:
        eid = (e.get("id") or "").strip()
        if not eid or eid in known or not sg.KEBAB.fullmatch(eid):
            continue
        if (e.get("type") or "") not in sg.ENTITY_TYPES:
            continue
        # Match the reply back to a candidate we actually offered: by the name field if
        # given, else by the id read as a name. No match means we cannot anchor it.
        cand = by_name.get((e.get("name") or "").strip())
        if cand is None:
            want = eid.replace("-", " ").lower()
            cand = next((c for c in by_name.values() if c["name"].lower() == want), None)
        if cand is None:
            continue
        out.append({
            "section": "Entities",
            "values": {"id": eid, "type": e["type"], "status": "active", "voice": "-",
                       "note": (e.get("aliases") or "").strip()},
            "basis": {"locator": cand["chapter"], "quote": cand["sentence"]},
            "reasoning": f"'{cand['name']}' appears {cand['count']}x with no entity row",
            "confidence": (e.get("confidence") or "high").lower(),
        })
    return out


# ------------------------------------------------------------------------ kind: evidence


def _unbacked(graph):
    """Propositions asserting true/false with no evidence span — the receipt gate's list."""
    return [r for r in _rows_of(graph, "Propositions")
            if r.get("prop-id") and (r.get("canon-status") in ("true", "false"))
            and not sg._span_ids(r.get("span", ""))]


def _sentences(text):
    """Chapter sentences, long enough to be evidence and short enough to be a span.

    Split PARAGRAPH FIRST, then sentence. Running the sentence split across the whole
    body glued text either side of a scene divider into one "sentence" — candidates like
    'The struggle is over.* --- "We have to walk past them,"' that no reader could find
    as a passage. Those were offered to the model, chosen, and then correctly rejected by
    the gate: rows wasted on a defect in the shortlist rather than a bad judgement.
    """
    body = "\n".join(ln for ln in text.splitlines() if not ln.lstrip().startswith("#"))
    out = []
    for block in re.split(r"\n\s*\n", body):
        # A divider line is a boundary, not prose.
        for chunk in re.split(r"^\s*[-*_=]{3,}\s*$", block, flags=re.M):
            for s in re.split(r"(?<=[.!?])\s+", chunk):
                s = " ".join(s.split())
                if 40 <= len(s) <= 320:
                    out.append(s)
    return out


def _ctx_evidence(graph, chapter_text, limit, per_claim=6):
    """Claims this chapter might prove, each with a SHORTLIST of real sentences.

    Two jobs are being separated here. Finding which sentences could possibly be
    relevant is mechanical, so code does it; deciding which one actually proves the
    claim is judgement, so the model does only that. The model then answers with an
    INDEX into this list rather than a quote — which makes the quote verbatim by
    construction instead of by good behaviour, and takes fabrication off the table.
    """
    ct = sgc._tokens(chapter_text)
    sents = _sentences(chapter_text)
    stoks = [sgc._tokens(s) for s in sents]
    claims = []
    for r in _unbacked(graph):
        t = sgc._tokens(r.get("statement", ""))
        if len(t) < 3 or len(t & ct) / len(t) < 0.6:
            continue
        ranked = sorted(((len(t & st) / max(1, len(t)), i) for i, st in enumerate(stoks)),
                        reverse=True)[:per_claim]
        # _sents must hold EXACTLY the sentences shown, in the same order. When these two
        # lists could differ, a model returning an index it was never offered got a row
        # filled from a sentence with no relation to the claim — and that quote is real
        # prose, so the gate waves it through. Shown-vs-fillable must not diverge.
        shown = [(n + 1, sents[i]) for n, (score, i) in enumerate(ranked) if score > 0]
        cands = [{"n": k, "s": t} for k, (_, t) in enumerate(shown, 1)]
        if cands:
            claims.append({"prop-id": r["prop-id"], "statement": r["statement"],
                           "candidates": cands, "_sents": [t for _, t in shown]})
    return claims[:limit] or None


def _prompt_evidence(claims, chapter_text, locator):
    shown = [{"prop-id": c["prop-id"], "statement": c["statement"], "candidates": c["candidates"]}
             for c in claims]
    return "\n".join([
        f"These claims from chapter {locator} are recorded as canon but cite no evidence.",
        "For each one, say which of its candidate sentences PROVES it — by number.",
        "",
        json.dumps(shown, indent=1),
        "",
        "Use 0 when no candidate proves the claim. A sentence that is merely on the same "
        "topic is not proof; the sentence must actually establish the claim. Omitting a "
        "claim costs nothing, so prefer 0 when unsure.",
        "",
        'Answer: {"evidence": [{"prop-id": "...", "sentence": <number>}]}',
    ])


def _rows_evidence(answer, claims, locator, graph, source_id, seq):
    by_id = {c["prop-id"]: c for c in claims}
    out = []
    for e in (answer or {}).get("evidence", []) or []:
        pid = (e.get("prop-id") or "").strip()
        claim = by_id.get(pid)
        if not claim:
            continue
        try:
            n = int(e.get("sentence", 0))
        except (TypeError, ValueError):
            continue
        if not (1 <= n <= len(claim["_sents"])):
            continue                                   # 0 means "nothing here proves it"
        quote = claim["_sents"][n - 1]
        sid = f"ev-{pid}-{locator}-{seq[0]}"
        seq[0] += 1
        out.append({"section": "Evidence",
                    "values": {"span-id": sid, "source-id": source_id, "locator": locator,
                               "quote": quote, "note": "proposed"},
                    "basis": {"locator": locator, "quote": quote}, "confidence": "high"})
        # The Evidence row alone ratifies nothing: the proposition has to point at it.
        out.append({"section": "Propositions", "op": "set",
                    "key": {"prop-id": pid}, "set": {"span": sid},
                    "basis": {"locator": locator, "quote": quote}, "confidence": "high"})
    return out


# ----------------------------------------------------------------------- kind: epistemic


def _ctx_epistemic(graph, chapter_text, ch_no, limit, per_claim=6):
    """Same shape as evidence, for the same reason.

    Asking for a free-text quote produced a 100% fabrication rate on a small local model
    — 23 of 23 rows rejected. Numbering real sentences and asking for an index makes the
    quote verbatim by construction, so the model spends its judgement on the only thing
    it should: WHO holds WHAT stance.
    """
    # Only a mind can hold a belief. Offering every entity put `checkout-stamp`,
    # `central-spire` and `biting-animated-book` on the holder list, and a real run duly
    # produced `deep-stacks / knows`. Characters and Factions can know things; objects
    # and locations cannot, however much attention the prose gives them.
    minds = {r["id"] for r in _rows_of(graph, "Entities")
             if r.get("id") and r.get("type") in ("Character", "Faction")}
    ct = sgc._tokens(chapter_text)
    present = [e for e in minds if any(t in ct for t in sgc._tokens(e.replace("-", " ")))]
    anchored = sgc._prop_chapter(graph)
    have = {(r.get("prop-id"), r.get("holder"), r.get("mode"))
            for r in _rows_of(graph, "Epistemic States")}
    sents = _sentences(chapter_text)
    stoks = [sgc._tokens(s) for s in sents]
    ev_quotes = {e.get("span-id"): (e.get("quote") or "")
                 for e in _rows_of(graph, "Evidence") if e.get("span-id")}
    claims = []
    for r in _rows_of(graph, "Propositions"):
        pid = r.get("prop-id")
        if not pid or anchored.get(pid, 0) > ch_no:
            continue                                   # not yet true at this point in the book
        t = sgc._tokens(r.get("statement", ""))
        if len(t) < 3 or len(t & ct) / len(t) < 0.5:
            continue
        # Retrieval for a STANCE is not retrieval for a fact. Ranking purely by overlap
        # with the claim surfaces sentences that restate it, while the line showing what
        # someone BELIEVES is usually a reaction or a denial sharing almost no words with
        # it — "Not now. Not ever." has zero content words in common with "Jonah's wolf
        # identifies Margot as his mate", and that pair is this book's central irony.
        # So: seed with the best matches, then include their neighbours, because a
        # character reacts to a thing next to where the thing happens.
        # Ties break by POSITION, earliest first. `reverse=True` on (score, i) ordered
        # ties by higher index, which silently dropped "The way the wolf knew the scent of
        # *mate*." — the sentence this graph already cites as this claim's evidence.
        ranked = sorted(((len(t & st) / max(1, len(t)), -i) for i, st in enumerate(stoks)),
                        reverse=True)
        seeds = [-negi for score, negi in ranked[:per_claim] if score > 0]
        # The graph may already know the answer: a claim with an evidence span was
        # anchored by someone who read the scene. That sentence is the best possible seed,
        # and the stance that reacts to it is usually within a line or two of it.
        for sid in sg._span_ids(r.get("span", "")):
            q = ev_quotes.get(sid, "")
            if q:
                hit = next((i for i, s in enumerate(sents) if sg.quote_found(s, q)), None)
                if hit is not None and hit not in seeds:
                    seeds.insert(0, hit)
        picked, seen_i = [], set()
        for i in seeds:
            for j in (i, i + 1, i - 1):
                if 0 <= j < len(sents) and j not in seen_i:
                    seen_i.add(j)
                    picked.append(j)
        # Truncate by PRIORITY, then sort for reading. Sorting first threw away the
        # ordering the seeds encode, so the chapter's opening scene crowded out the
        # sentence the graph itself had cited as this claim's evidence.
        picked = sorted(picked[:per_claim * 2])
        cands = [{"n": k, "s": sents[i]} for k, i in enumerate(picked, 1)]
        if cands:
            claims.append({"prop-id": pid, "statement": r["statement"], "candidates": cands,
                           "_sents": [sents[i] for i in picked]})
    if not claims or not present:
        return None
    return {"claims": claims[:limit], "holders": sorted(present)[:25], "have": have}


def _prompt_epistemic(ctx, chapter_text, locator, ch_no):
    shown = [{"prop-id": c["prop-id"], "statement": c["statement"], "candidates": c["candidates"]}
             for c in ctx["claims"]]
    return "\n".join([
        f"In chapter {locator}, who knows, believes, believes-false, or suspects each claim?",
        "",
        f"Claims, each with numbered sentences from the chapter: {json.dumps(shown, indent=1)}",
        f"Holders you may name (plus 'reader'): {', '.join(ctx['holders'])}",
        "",
        "modes: knows (it is true and they have grounds) · believes (they hold it, grounds "
        "weaker) · believes-false (they hold the OPPOSITE of a true claim) · suspects.",
        "",
        "believes-false is the one most often missed and the most valuable: a character "
        "confidently wrong about something the reader knows is dramatic irony, and it is "
        "invisible unless recorded. Look for it specifically.",
        "",
        "Use 'reader' for what the audience has been shown, which is often more than any "
        "character knows.",
        "",
        "Every row must name the numbered sentence that SHOWS the stance — the line where "
        "the character says, thinks, or acts on it. If a stance is merely plausible and no "
        "listed sentence shows it, leave the claim out.",
        "",
        'Answer: {"states": [{"prop-id": "...", "holder": "...", "mode": "knows", '
        '"sentence": <number>}]}',
    ])


def _rows_epistemic(answer, ctx, locator, ch_no, graph):
    # Mirrors _ctx_epistemic: only minds hold beliefs, plus the reader.
    ids = {r["id"] for r in _rows_of(graph, "Entities")
           if r.get("id") and r.get("type") in ("Character", "Faction")} | sg.RESERVED_HOLDERS
    by_id = {c["prop-id"]: c for c in ctx["claims"]}
    out = []
    for s in (answer or {}).get("states", []) or []:
        pid, holder = (s.get("prop-id") or "").strip(), (s.get("holder") or "").strip()
        mode = (s.get("mode") or "").strip()
        claim = by_id.get(pid)
        if not claim or holder not in ids or mode not in sg.EPISTEMIC_MODES:
            continue
        if (pid, holder, mode) in ctx["have"]:
            continue
        try:
            n = int(s.get("sentence", 0))
        except (TypeError, ValueError):
            continue
        if not (1 <= n <= len(claim["_sents"])):
            continue
        out.append({"section": "Epistemic States",
                    # since-ch is the chapter being read, NOT whatever the model says. A
                    # per-chapter pass observes a stance in THIS chapter; trusting the model
                    # here produced "since ch81" for a 30-chapter book.
                    "values": {"prop-id": pid, "holder": holder, "mode": mode,
                               "since-ch": str(ch_no), "span": ""},
                    "basis": {"locator": locator, "quote": claim["_sents"][n - 1]},
                    "reasoning": s.get("why", ""), "confidence": s.get("confidence", "high")})
    return out


# ----------------------------------------------------------------------------- the driver


def generate(kind, graph_path, chapters_dir, chat=None, model="?", provider="?",
             out_dir="proposals", cache_dir="", limit=18, chapters=None, min_count=4,
             ask=False, answers_dir="", log=print):
    """Write one proposal file per scope. Returns the list of paths written.

    Three ways to supply the judgement, all sharing the same shortlist and the same
    index-not-quote discipline:

      ask=True        write the QUESTION to disk and stop. For the agent already reading
                      this manuscript in an editor — it answers in-session, using the
                      strongest model available, with no HTTP call and no second provider.
      answers_dir=... read those answers back and build the proposal rows from them.
      chat=...        call an external provider. Useful headless or in batch; it is not
                      the main path, and it is the weakest link when the model is small.

    The safety property is identical in all three: the judge picks a numbered sentence,
    code fills the quote, and the gate checks the result.
    """
    if kind not in PROMPT_VERSION:
        raise ValueError(f"unknown kind '{kind}' (expected {', '.join(PROMPT_VERSION)})")
    if not ask and answers_dir == "" and chat is None:
        raise ValueError("supply one of: ask=True, answers_dir=..., or chat=...")
    graph = sg.parse_graph(Path(graph_path).read_text(encoding="utf-8"))
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []

    def resolve(scope, ctx_payload, user, salt=""):
        """The judgement for one scope, however it is being supplied."""
        if ask:
            q = out_dir / f"{kind}-{scope}.question.json"
            q.write_text(json.dumps({"kind": kind, "scope": scope, "graph": str(graph_path),
                                     "answer_shape": ANSWER_SHAPE[kind],
                                     "instructions": user, **ctx_payload}, indent=1),
                         encoding="utf-8")
            written.append(str(q))
            log(f"  {q.name}  — answer it, save as {kind}-{scope}.answer.json")
            return None
        if answers_dir:
            a = Path(answers_dir) / f"{kind}-{scope}.answer.json"
            if not a.exists():
                log(f"  no answer for {scope} ({a.name}) — skipped")
                return None
            return _json_from(a.read_text(encoding="utf-8"))
        # Everything that can change the reply belongs in the key: the chapter's own
        # digest included, since an edit that leaves the shortlist untouched must still
        # invalidate. Provider and SYSTEM too — a cached answer from one model must not
        # be served as another's.
        key = _digest(kind, PROMPT_VERSION[kind], provider, model, SYSTEM, salt, user)
        return _json_from(_cached(cache_dir, key, lambda: chat(SYSTEM, user), log))

    def emit(scope, rows):
        if not rows:
            return
        p = out_dir / f"{kind}-{scope}.json"
        p.write_text(json.dumps({
            "kind": kind, "graph": str(graph_path),
            "generated": {"provider": provider, "model": model, "scope": scope,
                          "prompt_version": PROMPT_VERSION[kind], "temperature": 0},
            "rows": rows}, indent=1), encoding="utf-8")
        written.append(str(p))
        log(f"  {p.name}: {len(rows)} row(s)")

    if kind == "entities":
        ctx = _ctx_entities(graph, chapters_dir, limit, min_count)
        if not ctx:
            log("  no unresolved names above the threshold")
            return written
        answer = resolve("all", {"candidates": ctx["candidates"]}, _prompt_entities(ctx, graph))
        if answer is not None:
            emit("all", _rows_entities(answer, ctx, graph))
        return written

    src = next((r["source-id"] for r in _rows_of(graph, "Sources")
                if r.get("type") == "manuscript"), "ms")
    files = sorted(Path(chapters_dir).glob("*.md"))
    if chapters:
        want = {c.strip() for c in chapters}
        files = [f for f in files if f.stem in want]
    for f in files:
        locator, ch_no = f.stem, _chapter_no(f)
        text = f.read_text(encoding="utf-8", errors="replace")
        if kind == "evidence":
            claims = _ctx_evidence(graph, text, limit)
            if not claims:
                continue
            shown = [{"prop-id": c["prop-id"], "statement": c["statement"],
                      "candidates": c["candidates"]} for c in claims]
            answer = resolve(locator, {"claims": shown},
                             _prompt_evidence(claims, text, locator), _digest(text))
            if answer is not None:
                emit(locator, _rows_evidence(answer, claims, locator, graph, src, [1]))
        else:
            ctx = _ctx_epistemic(graph, text, ch_no, limit)
            if not ctx:
                continue
            shown = [{"prop-id": c["prop-id"], "statement": c["statement"],
                      "candidates": c["candidates"]} for c in ctx["claims"]]
            answer = resolve(locator, {"claims": shown, "holders": ctx["holders"],
                                       "chapter": ch_no},
                             _prompt_epistemic(ctx, text, locator, ch_no), _digest(text))
            if answer is not None:
                emit(locator, _rows_epistemic(answer, ctx, locator, ch_no, graph))
    return written
