#!/usr/bin/env python3
"""The proposal spine: an AI's output is a file on disk, never an edit to the graph.

Nothing in this module calls a model. It is the gate every generated row has to pass
before it can touch canon, and it must land before any prompt is written — a generator
without a gate is just a faster way to corrupt a graph.

    propose  ->  proposals/<kind>-<scope>.json      (Stage D writes these)
    verify   ->  PASS / FAIL <reason> / NEEDS-HUMAN  (here, deterministic)
    apply    ->  accepted rows only, marked provisional, with one commit-log line

The quote gate is the load-bearing check: a model can invent a belief, but it cannot
invent a sentence that is genuinely on the page. Everything an inference asserts must
be anchored to a passage the checker can find.

Column names are read from the graph's own table headers rather than hardcoded here,
so this cannot drift into disagreeing with the ontology.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import story_graph as sg

PASS, FAIL, HUMAN = "PASS", "FAIL", "NEEDS-HUMAN"

# Sections whose rows are INFERENCES rather than transcriptions. A proposition's quote
# is on the page; a belief is a reading of it, and no grep confirms a reading — so these
# can never auto-ratify, however clean they look. (decisions.md, part 2.)
INFERRED_SECTIONS = {"Epistemic States", "Relationships", "Open Loops & Setups"}

# The column that identifies a row, per section.
KEY_COLS = {
    "Propositions": ("prop-id",),
    # `mode` belongs in the key: one holder legitimately has several stances on one
    # proposition over time — an `embargoed-until ch10` row followed by a `knows ch10`
    # row is how an embargo is modelled, and check_epistemic pairs them by (prop, holder).
    # Keying without mode rejects the follow-up as a duplicate.
    "Epistemic States": ("prop-id", "holder", "mode"),
    "Evidence": ("span-id",),
    "Entities": ("id",),
    "Relationships": ("from", "edge", "to"),
    "Open Loops & Setups": ("id",),
    "Locations & Distances": ("from", "to"),
    "Logistics": ("ch", "entity"),
}


def load(path):
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(d.get("rows"), list):
        raise ValueError("proposal has no 'rows' list")
    return d


def _headers(graph, section):
    """Column order as the graph itself declares it."""
    return sg.parse_table(sg._raw_section_lines(graph, section))[0]


def _key(section, values):
    return tuple((values.get(c) or "").strip().lower() for c in KEY_COLS.get(section, ()))


def verify(proposal, graph_path, chapters_dir="", max_attribution=40):
    """One verdict per row: (index, verdict, reason).

    Cheap per-row checks first, then ONE validate over everything that survived. If that
    batch validate raises errors the graph didn't already have, the rows are re-checked
    individually to attribute the damage — precise when it matters, fast when it doesn't.
    """
    text = Path(graph_path).read_text(encoding="utf-8")
    graph = sg.parse_graph(text)
    S = graph["sections"]
    entities = {r.get("id") for r in S.get("Entities", []) if r.get("id")}
    props = {r.get("prop-id") for r in S.get("Propositions", []) if r.get("prop-id")}
    spans = {r.get("span-id") for r in S.get("Evidence", []) if r.get("span-id")}
    sources = {r.get("source-id") for r in S.get("Sources", []) if r.get("source-id")}
    canon = graph["canon_ch"]

    existing = {}
    for sec in KEY_COLS:
        for r in S.get(sec, []):
            existing.setdefault(sec, set()).add(_key(sec, r))

    out, survivors = [], []
    seen_in_batch = {}
    for i, row in enumerate(proposal["rows"], 1):
        sec = row.get("section", "")
        vals = row.get("values") or {}
        basis = row.get("basis") or {}

        def bad(msg):
            out.append((i, FAIL, msg))

        if sec not in KEY_COLS:
            bad(f"unknown section '{sec}'")
            continue
        heads = _headers(graph, sec)
        if not heads:
            bad(f"section '{sec}' has no table in the graph")
            continue
        unknown = [k for k in vals if k not in heads]
        if unknown:
            bad(f"column(s) not in the {sec} table: {', '.join(sorted(unknown))}")
            continue
        missing = [c for c in KEY_COLS[sec] if not (vals.get(c) or "").strip()]
        if missing:
            bad(f"empty key column(s): {', '.join(missing)}")
            continue

        # --- referential integrity -----------------------------------------------
        err = None
        if sec == "Epistemic States":
            if vals["prop-id"] not in props:
                err = f"proposition '{vals['prop-id']}' is not declared"
            elif vals["holder"] not in entities and vals["holder"] not in sg.RESERVED_HOLDERS:
                err = f"holder '{vals['holder']}' is not a declared entity or reserved holder"
            elif (vals.get("mode") or "") not in sg.EPISTEMIC_MODES:
                err = f"unknown mode '{vals.get('mode', '')}'"
        elif sec == "Propositions":
            if (vals.get("canon-status") or "") not in sg.CANON_STATUS:
                err = f"unknown canon-status '{vals.get('canon-status', '')}'"
            elif vals.get("governing-source") and vals["governing-source"] not in sources:
                err = f"governing-source '{vals['governing-source']}' is not declared"
            elif not sg.KEBAB.fullmatch(vals["prop-id"]):
                err = f"prop-id '{vals['prop-id']}' is not kebab-case"
        elif sec == "Evidence":
            if vals.get("source-id") and vals["source-id"] not in sources:
                err = f"source-id '{vals['source-id']}' is not declared"
        elif sec == "Relationships":
            for side in ("from", "to"):
                if vals[side] not in entities:
                    err = f"{side} '{vals[side]}' is not a declared entity"
                    break
        if err:
            bad(err)
            continue

        # --- chapter range --------------------------------------------------------
        ch = (vals.get("since-ch") or vals.get("planted-ch") or vals.get("ch") or "").strip()
        if ch and not ch.isdigit():
            bad(f"chapter '{ch}' is not a number")
            continue
        if ch and canon and int(ch) > canon:
            bad(f"chapter {ch} is beyond current-canon-chapter {canon}")
            continue

        # --- cited spans must already exist ---------------------------------------
        cited = [s for s in sg._span_ids(vals.get("span", "")) if s]
        unknown_spans = [s for s in cited if s not in spans]
        if unknown_spans:
            bad(f"span(s) not declared in Evidence: {', '.join(unknown_spans)}")
            continue

        # --- duplicates (against the graph AND earlier rows in this file) ---------
        k = _key(sec, vals)
        if k in existing.get(sec, set()):
            bad(f"already in the graph: {' / '.join(x for x in k if x)}")
            continue
        if k in seen_in_batch:
            bad(f"duplicate of row {seen_in_batch[k]} in this proposal")
            continue
        seen_in_batch[k] = i

        # --- the quote gate -------------------------------------------------------
        quote = (basis.get("quote") or "").strip()
        locator = (basis.get("locator") or "").strip()
        if not quote:
            bad("no basis quote — an unanchored claim cannot be checked against anything")
            continue
        if not chapters_dir:
            bad("cannot verify the basis quote without --chapters-dir")
            continue
        chapter = sg._resolve_chapter(chapters_dir, locator)
        if chapter is None:
            bad(f"no chapter file for locator '{locator}'")
            continue
        if quote not in chapter.read_text(encoding="utf-8"):
            bad(f"basis quote is not in {chapter.name} — fabricated or misquoted")
            continue

        survivors.append(i)
        if sec in INFERRED_SECTIONS:
            out.append((i, HUMAN, f"{sec} rows are inferences, not transcriptions — "
                                  f"the quote is real, the reading still needs a human"))
        elif (row.get("confidence") or "").lower() == "low":
            out.append((i, HUMAN, "the generator reported low confidence"))
        else:
            out.append((i, PASS, "verified"))

    # --- consequence: do the survivors break anything that currently works? -------
    if survivors:
        base = {str(e) for e in sg.validate(graph_path, chapters_dir=chapters_dir).errors}
        new = _errors_with(text, proposal, survivors, graph_path, chapters_dir, out) - base
        if new:
            culprits = []
            if len(survivors) <= max_attribution:
                for i in survivors:
                    if _errors_with(text, proposal, [i], graph_path, chapters_dir, out) - base:
                        culprits.append(i)
            hit = set(culprits) if culprits else set(survivors)
            out = [(i, FAIL, f"introduces a validation error: {sorted(new)[0]}") if i in hit else (i, v, r)
                   for i, v, r in out]
    return sorted(out)


def _errors_with(text, proposal, indices, graph_path, chapters_dir, verdicts=()):
    """Validate exactly what apply would write — INCLUDING the commit-log line.

    Simulating only the rows let a malformed commit entry through the gate and break the
    graph after the checker had already said yes. Whatever apply does, this must do.
    """
    import tempfile
    merged = apply_rows(text, proposal, indices, sg.parse_graph(text))
    merged = append_commit(merged, commit_line(proposal, verdicts, indices))
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / Path(graph_path).name
        p.write_text(merged, encoding="utf-8")
        return {str(e) for e in sg.validate(str(p), chapters_dir=chapters_dir).errors}


def _row_line(heads, vals):
    return "| " + " | ".join((vals.get(h) or "").strip() for h in heads) + " |"


def apply_rows(text, proposal, indices, graph):
    """Insert the chosen rows into their tables, marked provisional. Pure string work
    on the graph text; everything outside the touched tables is preserved verbatim."""
    lines = text.splitlines()
    by_section = {}
    for i in indices:
        row = proposal["rows"][i - 1]
        vals = dict(row.get("values") or {})
        # Every applied row enters the ratification queue. An inferred row that cites no
        # evidence span must never look like settled canon just because it validated.
        if "span" in _headers(graph, row["section"]) and not sg._span_ids(vals.get("span", "")):
            vals["span"] = "provisional"
        by_section.setdefault(row["section"], []).append(vals)

    for section, rows in by_section.items():
        heads = _headers(graph, section)
        start = next((n for n, ln in enumerate(lines)
                      if re.match(rf"^##\s+{re.escape(section)}\s*$", ln)), None)
        if start is None:
            continue
        end = next((n for n in range(start + 1, len(lines)) if lines[n].startswith("## ")), len(lines))
        last = max((n for n in range(start, end) if lines[n].strip().startswith("|")), default=None)
        if last is None:
            continue
        for vals in rows:
            last += 1
            lines.insert(last, _row_line(heads, vals))
    return "\n".join(lines) + ("\n" if text.endswith("\n") else "")


def commit_line(proposal, verdicts, accepted):
    """Deliberately NOT in `- ch<N>:` form.

    The Canon Commit Log is a strictly-increasing record of canon ADVANCING one chapter
    at a time. Applying a proposal that back-fills ch05 while canon sits at ch30 is an
    amendment, not an advance — writing it as a chapter entry both lies about what
    happened and trips the log's own regression check.
    """
    g = proposal.get("generated") or {}
    counts = {}
    for i in accepted:
        sec = proposal["rows"][i - 1].get("section", "?")
        counts[sec] = counts.get(sec, 0) + 1
    what = ", ".join(f"+{n} {s.lower()}" for s, n in sorted(counts.items())) or "no rows"
    ok = sum(1 for _, v, _ in verdicts if v != FAIL)
    return (f"- proposal {g.get('scope', '?')}: {what} "
            f"(proposed by {g.get('model', '?')} via {g.get('provider', '?')}, "
            f"{len(proposal['rows'])} rows, {ok} verified, {len(accepted)} accepted) "
            f"[{Path(proposal.get('_file', 'proposal')).name}]")


def append_commit(text, line):
    lines = text.splitlines()
    start = next((n for n, ln in enumerate(lines)
                  if re.match(r"^##\s+Canon Commit Log\s*$", ln)), None)
    if start is None:
        lines += ["", "## Canon Commit Log", "", line]
    else:
        end = next((n for n in range(start + 1, len(lines)) if lines[n].startswith("## ")), len(lines))
        last = max((n for n in range(start, end) if lines[n].strip()), default=start)
        lines.insert(last + 1, line)
    return "\n".join(lines) + "\n"


def verify_report(verdicts, proposal):
    counts = {PASS: 0, HUMAN: 0, FAIL: 0}
    out = [f"VERIFY — {len(proposal['rows'])} proposed row(s)", "=" * 58]
    for i, verdict, reason in verdicts:
        counts[verdict] += 1
        row = proposal["rows"][i - 1]
        label = " / ".join(x for x in _key(row.get("section", ""), row.get("values") or {}) if x)
        out.append(f"  [{verdict:^11}] {i:>3}. {row.get('section', '?')}: {label}")
        out.append(f"                    {reason}")
    out.append("")
    out.append(f"  {counts[PASS]} pass · {counts[HUMAN]} need a human · {counts[FAIL]} rejected")
    if counts[HUMAN]:
        out.append("  NEEDS-HUMAN is not a soft pass: those rows cite a real quote, but what the "
                   "quote\n  MEANS is a reading, and no checker confirms a reading.")
    accept = [i for i, v, _ in verdicts if v == PASS]
    if accept:
        out.append(f"\n  apply-proposal <file> --graph <g> --accept {','.join(map(str, accept))}")
    return "\n".join(out)
