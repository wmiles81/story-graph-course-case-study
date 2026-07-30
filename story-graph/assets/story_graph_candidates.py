#!/usr/bin/env python3
"""Deterministic candidate generation: code enumerates, judgement decides.

Two open-ended reading tasks turned into finite lists, with no model and no network:

  * ``unresolved`` — proper nouns in the prose that resolve to no entity. Answers
    "who did I forget to model?" without reading the manuscript again.
  * ``conflicts`` — proposition pairs that may not both be true, **partitioned by
    chapter**, because a state change and a contradiction look identical in structure
    and only the chapter tells them apart (reference/decisions.md 2.4).

Both are candidate generators, deliberately tuned for recall over precision: a missed
candidate is invisible, a spurious one costs a glance. Neither writes to the graph.

Their real payoff is downstream — an AI stage that judges 40 candidates costs a
fraction of one that reads 30 chapters, and it can be checked.
"""
from __future__ import annotations

import re
from pathlib import Path

# Capitalised words that are almost never the entity you forgot to model.
STOP = {
    "the", "a", "an", "and", "but", "or", "so", "then", "there", "this", "that", "these",
    "those", "he", "she", "it", "they", "we", "you", "i", "his", "her", "their", "its",
    "our", "your", "my", "me", "him", "them", "us", "who", "what", "when", "where", "why",
    "how", "if", "as", "at", "by", "for", "from", "in", "into", "of", "on", "to", "with",
    "not", "no", "yes", "yeah", "okay", "ok", "well", "just", "still", "only", "even",
    "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
    "january", "february", "march", "april", "may", "june", "july", "august",
    "september", "october", "november", "december", "god", "christ", "jesus", "sir",
    "maam", "ma'am", "mr", "mrs", "ms", "dr", "sheriff", "deputy", "captain", "doctor",
    "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
    # Contraction stems. Without these, "Don't"/"Isn't"/"We're" read as characters —
    # they are capitalised, they recur constantly, and they bury the real finds.
    "don", "doesn", "didn", "isn", "wasn", "aren", "weren", "won", "can", "couldn",
    "shouldn", "wouldn", "hasn", "haven", "hadn", "ain", "let", "that's", "here",
    "chapter", "scene", "part", "epilogue", "prologue",
    # Dialogue openers. Position alone cannot catch these: `he said, "Look at me"` puts
    # the imperative MID-sentence, where capitalisation is indistinguishable from a name.
    # A stoplist is the pragmatic floor for a recall-first generator — the alternative is
    # part-of-speech tagging, which is a dependency this skill deliberately does not have.
    "look", "listen", "get", "go", "come", "wait", "stop", "move", "run", "hold", "take",
    "give", "tell", "put", "keep", "leave", "please", "sorry", "thanks", "thank", "hey",
    "hello", "goodbye", "maybe", "sure", "fine", "good", "right", "wrong", "true",
    "actually", "ideally", "honestly", "obviously", "probably", "perhaps", "instead",
    "besides", "anyway", "meanwhile", "suddenly", "finally", "again", "always", "never",
    "because", "since", "until", "unless", "though", "although", "however", "everything",
    "something", "nothing", "anything", "someone", "everyone", "nobody", "anybody",
}
# Apostrophes are deliberately NOT part of a word: keeping them turns "I'm" into a
# proper noun, and dropping them lets the stem fall through to STOP instead.
_WORD = re.compile(r"[A-Z][a-z\-]+")
# The closing quote matters: without it `me." "Do it now.` is ONE sentence, so "Do"
# reads as mid-sentence and becomes a character.
_SENT = re.compile(r"(?<=[.!?])[\"'”’]?\s+|\n+")
_LEAD = re.compile(r"^[\"'“”‘’—–\-\s]*")


# Determiners. A common noun accepts one; a proper name rejects it. "the Wolf", "a
# Vampire", "three Trolls" are grammatical; "the Margot" is not.
DETERMINERS = {
    "the", "a", "an", "another", "every", "each", "some", "any", "no", "this", "that",
    "these", "those", "both", "either", "neither", "one", "two", "three", "four", "five",
    "six", "seven", "eight", "nine", "ten", "several", "many",
    "my", "your", "his", "her", "its", "our", "their",
    # Deliberately NOT here: more, most, few, other, such, which, what, whose. Each is a
    # determiner in some frames and an adverb or pronoun in others, and "Thump twice more.
    # Thump." scored a false hit on `more` before they were removed.
}
_WORDISH = re.compile(r"[A-Za-z][A-Za-z'\-]*")
# Sentence boundary. Without it the pass reads across the full stop, so a word OPENING a
# sentence inherits whatever preceded the period — which is how "Thump" acquired two
# determiners it never had, from the "more." ending the sentence before it.
_BOUNDARY = re.compile(r"[.!?;:,\"'“”‘’()\[\]—–]|\n")


def determiner_profile(chapters_dir):
    """token -> (uses, determiner-preceded, pluralised), over the whole manuscript.

    This is the classic proper-noun test and it is the only mechanical signal found that
    separates a NAME from a DESCRIPTION: "the Vampire" and "three Trolls" are grammatical,
    "the Margot" is not.

    A capitalisation test was tried first and is much weaker: this author capitalises
    species and titles consistently, so "Keeper" and "Alpha" never appear lowercase and the
    test misses them entirely. Determiners catch what case does not.
    """
    uses, det = {}, {}
    for ch in _chapters(chapters_dir):
        text = ch.read_text(encoding="utf-8", errors="replace")
        for clause in _BOUNDARY.split(text):
            words = _WORDISH.findall(clause)
            for i, w in enumerate(words):
                t = w.lower()
                uses[t] = uses.get(t, 0) + 1
                if i and words[i - 1].lower() in DETERMINERS:
                    det[t] = det.get(t, 0) + 1
    return {t: (uses[t], det.get(t, 0), uses.get(t + "s", 0)) for t in uses}


def looks_like_description(phrase, profile, min_uses=5, threshold=0.25):
    """True when a ONE-WORD candidate behaves like a common noun rather than a name.

    Single tokens separate cleanly on Book 3 — descriptions 0.47-0.93, names 0.00-0.01, a
    32x gap with nothing in between — so the call is safe there. One documented exception:
    a proper name that idiomatically takes "the" ("the Archives") scores like a description
    and has to be overruled by a reader.

    Multi-word candidates are deliberately NOT classified, because neither available unit
    works and both were measured:

      * scoring the head noun calls "Main Street" a description (0.39 on `street`) and
        "Iron- Jaw" one too (0.90 on `jaw`, mostly from "his jaw");
      * scoring the whole phrase fixes those (0.11, 0.00) but then calls "the Grey Guard"
        (0.91), "the Deep Stacks" (1.00) and "the Sonnet Glade" (1.00) descriptions — and
        those are proper names. English lets a proper name of an institution or a place
        take a determiner exactly as a common noun does, so no determiner test can tell
        "the Grey Guard" from "the Gunship". That distinction needs a reader.

    So a phrase stays on the main work list, unclassified. The asymmetry is deliberate
    throughout: calling a description a name costs a glance, calling a NAME a description
    hides the thing this command exists to find.
    """
    toks = [t for t in _norm(phrase).split() if t]
    if len(toks) != 1:
        return False
    uses, det, plural = profile.get(toks[0], (0, 0, 0))
    if uses < min_uses:
        return False
    return det / uses >= threshold or plural > 2


def _chapters(chapters_dir):
    # Shared with the validator: numeric order, and only files that carry a chapter
    # number — a `word_count_tracker.md` sitting beside the prose is not a chapter.
    import story_graph as sg
    return sg.chapter_files(chapters_dir)


def _norm(s):
    return re.sub(r"[^a-z0-9 ]+", " ", (s or "").lower()).strip()


def _tokens(s):
    return {t for t in _norm(s).split() if t and t not in STOP}


def _owner_tokens(eid):
    """Tokens that name the OWNER in a possessive id, not the thing itself.

    `keeper-s-label-gun` is the label gun belonging to the Keeper — it is not a surface
    form of "Keeper". Indexing the owner made the owner unfindable: "Keeper" appears 34
    times in Book 3 as Margot's title and `unresolved` never reported it, because the
    label gun had already claimed the token. `X-s-Y` is unambiguous, so this needs no
    judgement.
    """
    parts = eid.split("-")
    return {p for i, p in enumerate(parts) if i + 1 < len(parts) and parts[i + 1] == "s"}


def entity_surfaces(graph, alias_cell):
    """Surface forms OWNED by an entity, in two kinds.

    The old index was one flat `token -> {ids}` map built by exploding every surface form,
    canonical id and alias alike, into loose tokens. Nothing owned anything, so tokens from
    unrelated entities competed in a shared namespace and the most trivial one won. That is
    how Book 3 lost its antagonist: `the-ego-of-inquisitors-a-tragedy` — the book Valerius is
    turned into in ch29 — carries the note "Valerius book", which contributed the token
    `valerius` to the same bag a Character named Valerius would have. He appears 145 times
    across 15 chapters, has no entity row, and `unresolved` never once reported him.

    Ownership fixes it structurally rather than by special case:

    - `exact` — a WHOLE surface form (the canonical id read as words, or any declared alias)
      maps to the entities that declare it. Two entities declaring one form is a collision,
      which `check_aliases` already reports.
    - `components` — single tokens derived from the canonical id ONLY, never from an alias.
      An id is a name, so its parts are names for the thing: `margot-vance` legitimately
      yields "Margot". An alias is a PHRASE, and a phrase's parts are not names for it, so
      "Valerius book" yields the whole phrase and nothing else. Possessive owners are
      excluded too — `keeper-s-label-gun` is not a surface form of "Keeper".

    Returns (exact, components, known).
    """
    exact, components, known = {}, {}, set()
    for r in graph["sections"].get("Entities", []):
        eid = r.get("id", "")
        if not eid:
            continue
        known.add(eid)
        for surf in [eid.replace("-", " ")] + list(alias_cell(r)):
            toks = _tokens(surf)
            if toks:
                exact.setdefault(frozenset(toks), set()).add(eid)
        owners = _owner_tokens(eid)
        for t in _tokens(eid.replace("-", " ")):
            if t not in owners and t != "s":
                components.setdefault(t, set()).add(eid)
    return exact, components, known


def trait_index(graph):
    """trait token -> {entity ids that carry it}, from the optional `traits` column.

    A description resolves through an ATTRIBUTE, not a name: "the Vampire" reaches Aleksei
    because he is one, and it would reach a different character in a book with a different
    cast. That is why a descriptor cannot live in the alias table — an alias is a rigid
    designator and this is not. Traits are plain tokens, so one trait serves every
    descriptor built on it: `alpha` answers "the Alpha", "an Alpha" and "Alpha-class".
    """
    idx = {}
    for r in graph["sections"].get("Entities", []):
        eid = r.get("id", "")
        if not eid:
            continue
        for seg in (r.get("traits") or "").split(";"):
            for t in _tokens(seg):
                idx.setdefault(t, set()).add(eid)
    return idx


def resolve_descriptor(phrase, traits):
    """(kind, owners) for a description. kind is resolved | ambiguous | none.

    Resolves only when exactly one entity carries the trait. Two candidates is reported,
    never guessed: "the Alpha" fits both Jonah and Jackson, and which one a given scene
    means is a reading. Getting it wrong is worse than leaving it open, because a wrong
    resolution is invisible once written.
    """
    toks = [t for t in _norm(phrase).split() if t]
    # The prose says "Trolls" and the trait says `troll`; a plural is the same attribute, and
    # making the author write both spellings would be a tax with no information in it.
    forms = {t for t in toks} | {t[:-1] for t in toks if len(t) > 3 and t.endswith("s")}
    owners = {e for t in forms for e in traits.get(t, ())}
    if len(owners) == 1:
        return "resolved", owners
    if owners:
        return "ambiguous", owners
    return "none", set()


def resolve_name(phrase, exact, components):
    """(kind, owners) for one prose name. kind is exact | component | ambiguous | none.

    A component match must account for EVERY token of the phrase and land on exactly one
    entity: "Miss Vance" does not resolve to `margot-vance` on the strength of `vance`
    alone, because `miss` belongs to nothing — it is an undeclared surface form, and saying
    so is the correct answer. `ambiguous` is a real outcome, not a failure: "Treaty" is a
    component of two different treaties and picking one silently is how the wrong entity
    ends up in a row.
    """
    toks = _tokens(phrase)
    if not toks:
        return "none", set()
    if frozenset(toks) in exact:
        return "exact", set(exact[frozenset(toks)])
    owners = {e for t in toks for e in components.get(t, ())}
    owners = {e for e in owners if all(e in components.get(t, ()) for t in toks)}
    if len(owners) == 1:
        return "component", owners
    if owners:
        return "ambiguous", owners
    return "none", set()


def proper_nouns(text):
    """Capitalised runs, minus sentence-initial position.

    A word is only trusted as a proper noun if it appears capitalised somewhere that is
    NOT the first word of a sentence — otherwise every sentence-opening "Snow", "The"
    and "Rows" becomes a character you forgot to model, and the list is unusable.
    """
    # Markdown headings are structure, not prose: "## Chapter Seven" is not a character.
    body = "\n".join(ln for ln in text.splitlines() if not ln.lstrip().startswith("#"))
    sents = [s.strip() for s in _SENT.split(body) if s.strip()]

    # Sentence-initial means AT THE START OF THE SENTENCE, not "first capitalised word":
    # in "A man named Dodge nodded", Dodge is the first capitalised word but the fourth
    # word, and treating it as sentence-initial loses a real name. Leading quotes and
    # dashes don't count as the start.
    def lead(s):
        return _LEAD.match(s).end()

    midsentence = set()
    for s in sents:
        at = lead(s)
        for m in _WORD.finditer(s):
            if m.start() > at:
                midsentence.add(m.group(0).lower())

    found = {}
    for s in sents:
        at = lead(s)
        words = list(_WORD.finditer(s))
        i = 0
        while i < len(words):
            run, j = [words[i]], i + 1
            while j < len(words) and words[j].start() <= run[-1].end() + 1:
                run.append(words[j])
                j += 1
            if run[0].start() <= at and run[0].group(0).lower() not in midsentence:
                run = run[1:]                      # untrusted capitalised head, drop it
            phrase = " ".join(w.group(0) for w in run).strip()
            if phrase and _tokens(phrase):
                found[phrase] = found.get(phrase, 0) + 1
            i = j
    return found


def unresolved(graph, chapters_dir, alias_cell, min_count=2):
    """Proper nouns owned by no entity, most frequent first."""
    exact, comp, _ = entity_surfaces(graph, alias_cell)
    hits, first = {}, {}
    for ch in _chapters(chapters_dir):
        text = ch.read_text(encoding="utf-8", errors="replace")
        for phrase, n in proper_nouns(text).items():
            if resolve_name(phrase, exact, comp)[0] != "none":
                continue
            hits[phrase] = hits.get(phrase, 0) + n
            first.setdefault(phrase, ch.stem)
    rows = [(p, n, first[p]) for p, n in hits.items() if n >= min_count]
    rows.sort(key=lambda t: (-t[1], t[0]))
    return rows


def ambiguous_names(graph, chapters_dir, alias_cell, min_count=2):
    """Prose names whose component match is claimed by more than one entity.

    Under the ownership model this is the only remaining way a name can fail to land on a
    single entity, and it is a question for a human rather than a coin-flip: "Treaty" is a
    component of both `original-integration-treaty` and `treaty-evidence-copies`, and
    picking one silently is how the wrong entity ends up cited in a row.
    """
    exact, comp, _ = entity_surfaces(graph, alias_cell)
    types = {r["id"]: r.get("type", "?") for r in graph["sections"].get("Entities", [])
             if r.get("id")}
    hits, meta = {}, {}
    for ch in _chapters(chapters_dir):
        for phrase, n in proper_nouns(ch.read_text(encoding="utf-8", errors="replace")).items():
            kind, owners = resolve_name(phrase, exact, comp)
            if kind != "ambiguous":
                continue
            hits[phrase] = hits.get(phrase, 0) + n
            meta.setdefault(phrase, (ch.stem, sorted(owners)))
    out = [(p, n, meta[p][0], meta[p][1], [types.get(e, "?") for e in meta[p][1]])
           for p, n in hits.items() if n >= min_count]
    out.sort(key=lambda t: (-t[1], t[0]))
    return out


NEG = re.compile(r"\b(not|never|no|none|nothing|nobody|cannot|can't|isn't|wasn't|didn't|"
                 r"doesn't|won't|hasn't|haven't|refused|denied|failed|without|un\w+|"
                 r"dis\w+|dead|gone|lost|missing|destroyed|false)\b", re.I)


def _prop_chapter(graph):
    """Earliest chapter a proposition is anchored to — its evidence locator, else the
    earliest epistemic since-ch. Propositions carry no chapter of their own."""
    loc = {r.get("span-id"): (r.get("locator") or "") for r in graph["sections"].get("Evidence", [])}
    out = {}

    def note(pid, ch):
        if pid and ch is not None and (pid not in out or ch < out[pid]):
            out[pid] = ch

    for r in graph["sections"].get("Propositions", []):
        pid = r.get("prop-id")
        for sid in re.split(r"[,\s]+", r.get("span", "") or ""):
            m = re.fullmatch(r"ch(\d+)", loc.get(sid.strip(), "").strip())
            if m:
                note(pid, int(m.group(1)))
    for r in graph["sections"].get("Epistemic States", []):
        ch = (r.get("since-ch") or "").strip()
        if ch.isdigit():
            note(r.get("prop-id"), int(ch))
    return out


def conflicts(graph, overlap=0.45, min_tokens=3):
    """Proposition pairs about the same subject, split by what the chapter says they
    are. Returns (same_chapter, cross_chapter, undated); each row is
    (a, b, chapter_a, chapter_b, statement_a, statement_b, polarity_clash).

    The signal is lexical overlap of content words. Negation asymmetry is recorded as a
    FLAG, not required — requiring it finds almost nothing, because the interesting
    pairs in practice are two positive statements describing different states of one
    subject ("Jackson is used as a battery" / "Jackson is freed from the tank"). That
    is exactly the state-change-vs-contradiction call in decisions.md 2.4, and it is
    invisible to a negation test.

    Candidates, not verdicts: high overlap also catches claims that are merely
    compatible ("Margot possesses the journal" / "Margot conceals the journal").
    """
    props = [(r.get("prop-id"), r.get("statement", ""))
             for r in graph["sections"].get("Propositions", []) if r.get("prop-id")]
    chap = _prop_chapter(graph)
    toks = {pid: _tokens(s) for pid, s in props}
    text = dict(props)

    # Inverted index so a big graph doesn't go quadratic over every pair.
    inv = {}
    for pid, ts in toks.items():
        for t in ts:
            inv.setdefault(t, []).append(pid)

    seen, same, cross, undated = set(), [], [], []
    for pid, ts in toks.items():
        if len(ts) < min_tokens:
            continue
        for t in ts:
            for other in inv.get(t, ()):
                if other == pid or (min(pid, other), max(pid, other)) in seen:
                    continue
                ots = toks[other]
                if len(ots) < min_tokens:
                    continue
                j = len(ts & ots) / len(ts | ots)
                if j < overlap:
                    continue
                seen.add((min(pid, other), max(pid, other)))
                na, nb = bool(NEG.search(text[pid])), bool(NEG.search(text[other]))
                ca, cb = chap.get(pid), chap.get(other)
                a, b = (pid, other) if (ca is None or cb is None or ca <= cb) else (other, pid)
                row = (a, b, chap.get(a), chap.get(b), text[a], text[b], na != nb)
                if ca is None or cb is None:
                    undated.append(row)
                elif ca == cb:
                    same.append(row)
                else:
                    cross.append(row)
    for bucket in (same, cross, undated):
        bucket.sort(key=lambda r: (not r[6], r[0], r[1]))   # polarity clashes first
    return same, cross, undated


def unresolved_report(rows, min_count, profile=None, graph=None):
    if not rows:
        return f"UNRESOLVED — none (no proper noun appears {min_count}+ times without an entity)"
    names = [r for r in rows
             if not (profile and looks_like_description(r[0], profile))]
    descs = [r for r in rows if r not in names]
    out = [f"UNRESOLVED — {len(names)} probable name(s) with no entity behind them, "
           f"seen {min_count}+ times", "=" * 60]
    for phrase, n, first in names:
        out.append(f"  {n:>4}x  {phrase:<34} first in {first}")
    out.append("\nEach is either an entity you have not modelled, an alias you have not "
               "declared,\nor prose the extractor mistook for a name. Judgement decides "
               "which; this only\nguarantees the list is finite.")
    if descs:
        traits = trait_index(graph) if graph is not None else {}
        buckets = {"resolved": [], "ambiguous": [], "none": []}
        for row in descs:
            kind, owners = resolve_descriptor(row[0], traits)
            buckets[kind].append((row, sorted(owners)))
        if buckets["resolved"]:
            out += ["", f"DESCRIPTIONS — {len(buckets['resolved'])} accounted for by a trait"]
            for (phrase, n, _), owners in buckets["resolved"]:
                out.append(f"  {n:>4}x  {phrase:<24} -> {owners[0]}")
        if buckets["ambiguous"]:
            out += ["", f"DESCRIPTIONS — {len(buckets['ambiguous'])} ambiguous: 2+ entities "
                        f"carry the trait", "=" * 60]
            for (phrase, n, first), owners in buckets["ambiguous"]:
                out.append(f"  {n:>4}x  {phrase:<20} first in {first:<6} -> "
                           f"{', '.join(owners)}")
            out.append("  Which one a scene means is a reading. Left unresolved on purpose — "
                       "a wrong\n  resolution is invisible once written.")
        if buckets["none"]:
            out += ["", f"DESCRIPTIONS — {len(buckets['none'])} common noun(s) with no trait "
                        f"behind them", "=" * 60]
            for (phrase, n, first), _ in buckets["none"]:
                uses, det, plural = profile.get(_norm(phrase).split()[-1], (0, 0, 0))
                out.append(f"  {n:>4}x  {phrase:<24} first in {first:<6} "
                           f"det {det}/{uses}"
                           f"{f', {plural} plural' if plural else ''}")
            out.append(
                "\nThese take a determiner (\"the Wolf\", \"three Trolls\"), which a proper "
                "name does\nnot — so they are DESCRIPTIONS and they do not belong in an alias "
                "table. An alias\nis a rigid designator: 'Sheriff Harrow' is Jonah in every "
                "scene. A description\nresolves through an attribute — 'the Vampire' reaches "
                "Aleksei because he IS one.\nGive the bearer a `traits` cell (`vampire`) and "
                "the descriptor stops being homeless;\nrecording it as an alias instead "
                "asserts an identity the prose never gave it.")
    return "\n".join(out)


def ambiguous_report(rows, min_count):
    if not rows:
        return f"AMBIGUOUS — none (no name seen {min_count}+ times is claimed by 2+ entities)"
    out = [f"AMBIGUOUS — {len(rows)} name(s) claimed by more than one entity", "=" * 72]
    for phrase, n, first, ents, types in rows:
        who = ", ".join(f"{e} ({t})" for e, t in zip(ents, types))
        out.append(f"  {n:>4}x  {phrase:<22} first in {first:<6} -> {who}")
    out.append("\nEach is a question, not a failure: the prose uses one name and the graph "
               "offers\ntwo owners for it. Declare the surface form on the entity that "
               "actually bears it,\nor record an ambiguity — do not let a checker pick.")
    return "\n".join(out)


def conflicts_report(same, cross, undated, dated=None, total=None):
    n = len(same) + len(cross) + len(undated)
    out = [f"CONFLICT CANDIDATES — {n} pair(s) of claims about the same subject", "=" * 68]

    def block(title, rows, note):
        out.append(f"\n{title} ({len(rows)}) — {note}")
        if not rows:
            out.append("  none")
        for a, b, ca, cb, sa, sb, clash in rows:
            ca_s = f"ch{ca:02d}" if ca is not None else "ch??"
            cb_s = f"ch{cb:02d}" if cb is not None else "ch??"
            out.append(f"  {'±' if clash else ' '} {a} [{ca_s}]  {sa}")
            out.append(f"    {b} [{cb_s}]  {sb}")
            out.append("")

    block("SAME CHAPTER", same,
          "no event between them can reconcile these — likeliest genuine contradictions")
    block("DIFFERENT CHAPTERS", cross,
          "a state may simply have changed — look for the event that changed it")
    block("UNDATED", undated,
          "no evidence locator and no epistemic since-ch, so they cannot be partitioned")
    out.append("± marks a polarity clash (exactly one side negated) — likelier to be a real")
    out.append("conflict than two positive claims that merely share a subject.")
    if dated is not None and total:
        pct = round(100 * dated / total)
        out.append(f"\nChapter anchoring: {dated}/{total} propositions ({pct}%) resolve to a chapter, "
                   f"via an\nevidence locator or an epistemic since-ch. The rest CANNOT be "
                   f"partitioned — and the\npartition is the whole point, so this number caps how "
                   f"much this command can tell you.")
    out.append("\nCandidates, not verdicts: same chapter is a bug, different chapters is usually")
    out.append("plot, and high overlap also catches claims that are merely compatible "
               "(decisions.md 2.4).")
    return "\n".join(out)
