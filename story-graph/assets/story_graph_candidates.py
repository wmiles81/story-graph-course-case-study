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


def _chapters(chapters_dir):
    return sorted(p for p in Path(chapters_dir).glob("*.md") if p.is_file())


def _norm(s):
    return re.sub(r"[^a-z0-9 ]+", " ", (s or "").lower()).strip()


def _tokens(s):
    return {t for t in _norm(s).split() if t and t not in STOP}


def entity_index(graph, alias_cell):
    """token -> {entity ids}, from canonical ids and declared aliases. Token-level so
    "Jonah" reaches `jonah-harrow`; SKILL.md already resolves this way for imports."""
    idx, known = {}, set()
    for r in graph["sections"].get("Entities", []):
        eid = r.get("id", "")
        if not eid:
            continue
        known.add(eid)
        surfaces = [eid.replace("-", " ")] + list(alias_cell(r))
        for s in surfaces:
            for t in _tokens(s):
                idx.setdefault(t, set()).add(eid)
    return idx, known


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
    """Proper nouns with no entity behind them, most frequent first."""
    idx, _ = entity_index(graph, alias_cell)
    hits, first = {}, {}
    for ch in _chapters(chapters_dir):
        text = ch.read_text(encoding="utf-8", errors="replace")
        for phrase, n in proper_nouns(text).items():
            toks = _tokens(phrase)
            if not toks or any(t in idx for t in toks):
                continue                                   # some token reaches an entity
            hits[phrase] = hits.get(phrase, 0) + n
            first.setdefault(phrase, ch.stem)
    rows = [(p, n, first[p]) for p, n in hits.items() if n >= min_count]
    rows.sort(key=lambda t: (-t[1], t[0]))
    return rows


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


def unresolved_report(rows, min_count):
    if not rows:
        return f"UNRESOLVED — none (no proper noun appears {min_count}+ times without an entity)"
    out = [f"UNRESOLVED — {len(rows)} proper noun(s) with no entity behind them, "
           f"seen {min_count}+ times", "=" * 60]
    for phrase, n, first in rows:
        out.append(f"  {n:>4}x  {phrase:<34} first in {first}")
    out.append("\nEach is either an entity you have not modelled, an alias you have not "
               "declared,\nor prose the extractor mistook for a name. Judgement decides "
               "which; this only\nguarantees the list is finite.")
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
