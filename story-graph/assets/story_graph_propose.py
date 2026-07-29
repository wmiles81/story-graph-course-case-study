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

PROMPT_VERSION = {"entities": "entities/1", "evidence": "evidence/1",
                  "epistemic": "epistemic/1", "dependencies": "dependencies/1"}

# What an answer file must contain. The judge picks by NUMBER; it never writes a quote.
ANSWER_SHAPE = {
    "entities": '{"entities": [{"name": "<candidate name, copied exactly>", "id": "kebab-id", '
                '"type": "Character|Object|Location|Faction", "aliases": "A; B", '
                '"confidence": "high|low"}]}',
    "evidence": '{"evidence": [{"prop-id": "...", "sentence": <number, or 0 for none>}]}',
    "epistemic": '{"states": [{"prop-id": "...", "holder": "...", '
                 '"mode": "knows|believes|believes-false|suspects", "sentence": <number>}]}',
    "dependencies": '{"edges": [{"claim": "<prop-id>", "needs": "<prop-id>"}]}',
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
             for p in sg.chapter_files(chapters_dir)}
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


# -------------------------------------------------------------------- kind: dependencies


def _ctx_dependencies(graph, limit=200):
    """Every proposition that has no `depends-on` yet, with the ones that do for context.

    No shortlist, and that is the point. Retrieval by lexical overlap is the WRONG signal
    here: half of Book 3's hand-made edges sit at 0.11 similarity or below — "The Purge
    activates on the ch02 breach" and "The Scrolls are discovered missing" are causally
    linked and share almost no words. A threshold low enough to catch them returns 477
    pairs; one small enough to review misses half the real edges.

    A proposition table is ~2k tokens, so the whole set fits in one prompt and the judge
    can see relationships no similarity score would surface.
    """
    rows = [r for r in _rows_of(graph, "Propositions") if r.get("prop-id")]
    if not rows:
        return None
    have = {r["prop-id"]: sg._span_ids(r.get("depends-on", "")) for r in rows}
    open_ = [r["prop-id"] for r in rows if not have[r["prop-id"]]]
    if not open_:
        return None
    return {"claims": [{"prop-id": r["prop-id"], "statement": r.get("statement", "")}
                       for r in rows][:limit],
            "already": {k: v for k, v in have.items() if v},
            "open": set(open_)}


def _prompt_dependencies(ctx, graph):
    known = "\n".join(f"  {k} needs {', '.join(v)}" for k, v in sorted(ctx["already"].items()))
    return "\n".join([
        "Here is every claim in one story's canon. Which claims NEED another claim in order",
        "to be true? Read `X needs Y` as: if Y were false, X would stop making sense.",
        "",
        json.dumps(ctx["claims"], indent=1),
        "",
        ("Edges already recorded, as examples of the shape wanted:\n" + known) if known else "",
        "",
        "Two tests before you write an edge. Say it aloud — \"X, because Y\" and \"Y, because",
        "X\"; exactly one is true. Then delete each in turn: removing the foundation makes the",
        "other claim nonsense, while removing the dependent leaves the foundation untouched.",
        "",
        "CO-OCCURRENCE IS NOT DEPENDENCY. Two claims can share a scene, a chapter, a",
        "character and a location and still need nothing from each other. Most pairs are",
        "unrelated; a judge hunting for links will invent them. Propose only edges you would",
        "defend one at a time, and none at all rather than a plausible guess.",
        "",
        'Answer: {"edges": [{"claim": "<prop-id>", "needs": "<prop-id>"}]}',
    ])


def _rows_dependencies(answer, ctx, graph):
    ids = {c["prop-id"] for c in ctx["claims"]}
    stmt = {c["prop-id"]: c["statement"] for c in ctx["claims"]}
    seen, out = set(), []
    for e in (answer or {}).get("edges", []) or []:
        a, b = (e.get("claim") or "").strip(), (e.get("needs") or "").strip()
        if a not in ids or b not in ids or a == b or a not in ctx["open"]:
            continue                      # unknown id, self-edge, or the cell is not empty
        if (a, b) in seen:
            continue
        seen.add((a, b))
        # A dependency is a claim about the STORY's structure, not about a passage, so
        # there is no quote to cite. The basis is the claim it points at, and the gate
        # sends it to a human like every other reading.
        out.append({"section": "Propositions", "op": "set", "key": {"prop-id": a},
                    "set": {"depends-on": b},
                    "basis": {"locator": "", "quote": ""},
                    "reasoning": f'"{stmt[a][:60]}" needs "{stmt[b][:60]}"',
                    "confidence": e.get("confidence", "high")})
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
            # An ellipsis is not a sentence end. Splitting on it cut "The Scrolls
            # contain... inconvenient truths." into two fragments, both under the floor,
            # so a sentence the graph itself cites as evidence could never be offered.
            # The ellipsis is swapped out before splitting and back after, so it simply
            # is not sentence punctuation. No lookaround needed — and a lookbehind pair
            # that both requires and forbids `[.!?]` matches nothing, which silently
            # turned every paragraph into one over-long "sentence" and dropped it.
            for s in re.split(r"(?<=[.!?])\s+", chunk.replace("...", "…")):
                s = " ".join(s.split()).replace("…", "...")
                # 25, not 40: a real line of dialogue is short. '"The lexivore is bound to
                # B1.' is 29 characters and is a cited evidence span in this very graph.
                if 25 <= len(s) <= 320:
                    out.append(s)
    return out


# Verbs that mark a STANCE rather than an event. A sentence showing what someone knows,
# believes or hides is usually built on one of these, and it often shares almost no other
# words with the claim it bears on — "if he knew the truth about the missing scrolls"
# against "The Founding Scrolls were hidden rather than stolen".
STANCE = {
    "knew", "know", "knows", "known", "believe", "believed", "believes", "belief",
    "think", "thought", "thinks", "realise", "realised", "realize", "realized",
    "understood", "understand", "understands", "suspect", "suspected", "suspects",
    "remember", "remembered", "remembers", "forgot", "forgotten", "wonder", "wondered",
    "doubt", "doubted", "assume", "assumed", "guess", "guessed", "denied", "deny",
    "denial", "lie", "lied", "lying", "hid", "hidden", "hide", "hiding", "conceal",
    "concealed", "pretend", "pretended", "secret", "secrets", "truth", "admit",
    "admitted", "confess", "confessed", "told", "tell", "said", "explained", "swore",
    "convinced", "certain", "sure", "unaware", "ignorant", "learned", "discovered",
}


def _idf(stoks):
    """Rarity weight per token, over this chapter's own sentences.

    Counting shared tokens flat treats "scrolls" and "library" as equally informative in a
    book about a library. The diagnostic word is the rare one, and weighting by rarity is
    what lets a claim find the one sentence that is really about it.
    """
    import math
    n = max(1, len(stoks))
    df = {}
    for st in stoks:
        for t in st:
            df[t] = df.get(t, 0) + 1
    return {t: math.log(1 + n / c) for t, c in df.items()}


def _shortlist(claim_tokens, sents, stoks, idf, per_claim, seed_quote="",
               stance_boost=False, window=1):
    """Sentence indices to offer for one claim, best first, then their neighbours.

    Kept in ONE place because both kinds need exactly the same guarantee — that what is
    shown and what can be filled in are the same list — and two copies of that is how
    they drift apart.
    """
    weight = lambda t: idf.get(t, 1.0)
    denom = sum(weight(t) for t in claim_tokens) or 1.0
    scored = []
    for i, st in enumerate(stoks):
        s = sum(weight(t) for t in (claim_tokens & st)) / denom
        if stance_boost and (st & STANCE):
            # A stance sentence is worth surfacing even on a thin lexical match; this
            # lifts it over topical filler without letting it outrank a real match.
            s += 0.25
        if s > 0:
            scored.append((s, -i))
    scored.sort(reverse=True)                      # ties -> earliest sentence
    seeds = [-negi for _, negi in scored[:per_claim]]
    if seed_quote:
        # The graph may already know: a claim with an evidence span was anchored by
        # someone who read the scene, and the stance reacting to it sits beside it.
        hit = next((i for i, s in enumerate(sents) if sg.quote_found(s, seed_quote)), None)
        if hit is not None and hit not in seeds:
            seeds.insert(0, hit)
    picked, seen = [], set()
    for i in seeds:
        for j in [i] + [d for w in range(1, window + 1) for d in (i + w, i - w)]:
            if 0 <= j < len(sents) and j not in seen:
                seen.add(j)
                picked.append(j)
    return sorted(picked[:per_claim * 2])           # truncate by priority, then read order


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
    idf = _idf(stoks)
    claims = []
    for r in _unbacked(graph):
        t = sgc._tokens(r.get("statement", ""))
        if len(t) < 3 or len(t & ct) / len(t) < 0.6:
            continue
        picked = _shortlist(t, sents, stoks, idf, per_claim)
        if picked:
            claims.append({"prop-id": r["prop-id"], "statement": r["statement"],
                           "candidates": [{"n": k, "s": sents[i]} for k, i in enumerate(picked, 1)],
                           "_sents": [sents[i] for i in picked]})
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
    idf = _idf(stoks)
    ev_quotes = {e.get("span-id"): (e.get("quote") or "")
                 for e in _rows_of(graph, "Evidence") if e.get("span-id")}
    claims = []
    for r in _rows_of(graph, "Propositions"):
        pid = r.get("prop-id")
        if not pid or anchored.get(pid, 0) > ch_no:
            continue                                   # not yet true at this point in the book
        t = sgc._tokens(r.get("statement", ""))
        # 0.4, not 0.5: a claim is written in the AUTHOR's words, so the nouns match the
        # prose and the verbs do not. "Valerius activates a backup Feral Signal…" missed
        # on `activates`/`manufactured`/`public` while matching Valerius, Feral and Signal,
        # and five of Book 3's late-act claims were unreachable in every chapter for that
        # reason. Measured on the 73 chapter-anchored claims: 0.5 offered 67 in their own
        # chapter, 0.4 offers 70. Only the ranking below makes a looser gate safe — the
        # extra low-relevance claims now sort to the bottom and fall off, where before they
        # would have crowded out the good ones by prop-id order.
        # IDF-weighting this overlap was tried and is far worse (27/73): the paraphrase
        # verbs that never appear in the prose are rare, so IDF hands them the most weight.
        if len(t) < 3 or len(t & ct) / len(t) < 0.4:
            continue
        seed = next((ev_quotes.get(sid, "") for sid in sg._span_ids(r.get("span", ""))
                     if ev_quotes.get(sid)), "")
        # Stance boost and a wider window: what someone BELIEVES is shown by a reaction,
        # which is near the event rather than in the sentence that reports it.
        picked = _shortlist(t, sents, stoks, idf, per_claim, seed_quote=seed,
                            stance_boost=True, window=2)
        if picked:
            # Rank, because `claims[:limit]` used to truncate in prop-id order — which is
            # roughly story order, so every chapter's list filled up with early-book claims
            # and the late-book ones fell off the end. Measured on Book 3: the four most
            # load-bearing claims in the manuscript (blast radius 49-58, the Grey Guard
            # siege) were offered in ZERO of 30 chapters, so no judge could ever record who
            # believed them. Order by how much this chapter is actually ABOUT the claim,
            # then break ties toward claims nobody holds yet — closing that gap is the
            # whole point of the pass.
            # The fraction alone SATURATES: "Margot watched the room" is 3 generic tokens
            # and scores a perfect 1.0, tying a 6-token claim naming Valerius and the dam —
            # and on a tie the id tie-break below silently restored the very ordering this
            # ranking exists to remove. Counting matched content words breaks that tie
            # toward the claim the chapter is more specifically about.
            claims.append((
                len(t & ct) / len(t)
                + 0.1 * len(t & ct)
                + (2.0 if anchored.get(pid) == ch_no else 0.0)
                + (1.0 if not any(k[0] == pid for k in have) else 0.0),
                pid,                                   # stable tie-break, keeps runs reproducible
                {"prop-id": pid, "statement": r["statement"],
                 "candidates": [{"n": k, "s": sents[i]} for k, i in enumerate(picked, 1)],
                 "_sents": [sents[i] for i in picked]}))
    if not claims or not present:
        return None
    claims.sort(key=lambda c: (-c[0], c[1]))
    kept = [c[-1] for c in claims[:limit]]
    # A cap that hides what it cut reads as "this chapter has nothing else to say".
    return {"claims": kept, "holders": sorted(present)[:25], "have": have,
            "dropped": [c[1] for c in claims[limit:]]}


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
        "Some claims below describe events LATER in the book than this chapter — 87 of this "
        "book's propositions carry no chapter anchor, so they cannot be filtered out for you. "
        "If a claim has not happened yet by this chapter, leave it out entirely. Nobody can "
        "hold a belief about an event that has not occurred.",
        "",
        "Every row must name the numbered sentence that SHOWS the stance — the line where "
        "the character says, thinks, or acts on it. If a stance is merely plausible and no "
        "listed sentence shows it, leave the claim out.",
        "",
        'Answer: {"states": [{"prop-id": "...", "holder": "...", "mode": "knows", '
        '"sentence": <number>}]}',
    ])


def _rows_epistemic(answer, ctx, locator, ch_no, graph, source_id="", seq=None):
    # Mirrors _ctx_epistemic: only minds hold beliefs, plus the reader.
    ids = {r["id"] for r in _rows_of(graph, "Entities")
           if r.get("id") and r.get("type") in ("Character", "Faction")} | sg.RESERVED_HOLDERS
    by_id = {c["prop-id"]: c for c in ctx["claims"]}
    seq = [1] if seq is None else seq
    # The judge picked a REAL sentence and the gate proved it exists — then the row landed
    # as `span: provisional` and the quote was thrown away, so `validate` could only ever
    # answer "claim is unverified". Every epistemic row this tool had ever produced was
    # permanently unverifiable for that reason (183 of 183 on Book 3). Persist the basis as
    # an Evidence row and point the stance at it, exactly as the evidence path already does.
    # Deduped per (locator, quote): four holders agreeing on one sentence is one receipt,
    # not four.
    minted = {}
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
        quote = claim["_sents"][n - 1]
        span = ""
        if source_id:
            span = minted.get((locator, quote))
            if not span:
                span = f"ev-{pid}-{locator}-e{seq[0]}"
                seq[0] += 1
                minted[(locator, quote)] = span
                out.append({"section": "Evidence",
                            "values": {"span-id": span, "source-id": source_id,
                                       "locator": locator, "quote": quote,
                                       "note": "proposed (epistemic basis)"},
                            "basis": {"locator": locator, "quote": quote},
                            "confidence": "high"})
        out.append({"section": "Epistemic States",
                    # since-ch is the chapter being read, NOT whatever the model says. A
                    # per-chapter pass observes a stance in THIS chapter; trusting the model
                    # here produced "since ch81" for a 30-chapter book.
                    "values": {"prop-id": pid, "holder": holder, "mode": mode,
                               "since-ch": str(ch_no), "span": span},
                    "basis": {"locator": locator, "quote": quote},
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

    if kind == "dependencies":
        ctx = _ctx_dependencies(graph, limit=200)
        if not ctx:
            log("  every proposition already has a depends-on, or there are none")
            return written
        answer = resolve("all", {"claims": ctx["claims"]}, _prompt_dependencies(ctx, graph))
        if answer is not None:
            emit("all", _rows_dependencies(answer, ctx, graph))
        return written

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
    files = sg.chapter_files(chapters_dir)
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
            if ctx["dropped"]:
                log(f"  {locator}: {len(ctx['dropped'])} further claim(s) passed the relevance "
                    f"gate but exceeded --limit {limit}: {', '.join(ctx['dropped'][:6])}"
                    f"{' …' if len(ctx['dropped']) > 6 else ''}")
            answer = resolve(locator, {"claims": shown, "holders": ctx["holders"],
                                       "chapter": ch_no, "omitted_over_limit": ctx["dropped"]},
                             _prompt_epistemic(ctx, text, locator, ch_no), _digest(text))
            if answer is not None:
                emit(locator, _rows_epistemic(answer, ctx, locator, ch_no, graph, src, [1]))
    return written
