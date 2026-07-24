#!/usr/bin/env python3
"""Import a legacy Story-Graph canon CSV set into an ontology-v2 Story-Graph.md.

Stdlib only. Reads the reconciled/frozen legacy ledgers (entity registry,
proposition registry, routed assertions, scene ledger) and emits a v2 graph
plus a coverage report of everything it could NOT faithfully map. Anything the
legacy data does not support (e.g. missing verbatim evidence quotes) is marked
`provisional` rather than fabricated.

Usage:
    python3 story_graph_import.py <legacy-dir> --out <Story-Graph.md> [--report <coverage.md>] [--title "..."]
"""
from __future__ import annotations

import argparse
import csv
import glob
import os
import re
import sys
from pathlib import Path

ENTITY_TYPE_MAP = {
    "Character": "Character", "Object": "Object", "Location": "Location",
    "Faction": "Faction", "Creature": "Character", "Group": "Faction", "System": "Faction",
}
# NarrativeThread / Event / PhysicalState have no v2 entity home -> coverage report.

PRED_MODE = {"KNOWS": "knows", "BELIEVES": "believes", "SUSPECTS": "suspects"}


def slug(s: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")
    return s or "x"


def cell(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").replace("|", "/")).strip()


def chapter_of(scene_id: str) -> str:
    m = re.search(r"C0*(\d+)", scene_id or "")
    return m.group(1) if m else ""


def _find(legacy_dir: str, pattern: str):
    hits = sorted(glob.glob(os.path.join(legacy_dir, pattern)))
    return hits[0] if hits else None


def _read(path):
    if not path:
        return []
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def build(legacy_dir: str, title: str):
    ents = _read(_find(legacy_dir, "*ENTITY-REGISTRY*.csv"))
    props = _read(_find(legacy_dir, "*PROPOSITION-REGISTRY*.csv"))
    asserts = _read(_find(legacy_dir, "*ASSERTIONS*.csv"))
    scenes = _read(_find(legacy_dir, "*SCENE-LEDGER*.csv"))
    cov = []
    stats = {}

    # ---- Entities -------------------------------------------------------
    ent_by_legacy, ent_by_name, used = {}, {}, set()
    entity_rows = []
    for r in ents:
        et = r.get("entity_type", "")
        v2t = ENTITY_TYPE_MAP.get(et)
        if not v2t:
            cov.append(f"ENTITY dropped — type '{et}' has no v2 entity home: {r.get('canonical_name','?')}")
            continue
        base = slug(r.get("canonical_name") or r.get("entity_id"))
        eid, i = base, 2
        while eid in used:
            eid, i = f"{base}-{i}", i + 1
        used.add(eid)
        ent_by_legacy[r.get("entity_id", "")] = eid
        nm = (r.get("canonical_name") or "").lower().strip()
        if nm:
            ent_by_name[nm] = eid
        note = cell(r.get("aliases", ""))
        entity_rows.append((eid, v2t, cell(r.get("status") or "active"), "-", note))
    stats["entities"] = len(entity_rows)

    def resolve(subj: str):
        s = (subj or "").strip()
        if not s:
            return None
        if s.lower() == "reader":
            return "reader"
        if s in ent_by_legacy:
            return ent_by_legacy[s]
        return ent_by_name.get(s.lower())

    # ---- Propositions (canon-status derived from assertions) ------------
    truth_by_prop = {}
    for a in asserts:
        pid = a.get("proposition_id", "")
        if pid:
            truth_by_prop.setdefault(pid, []).append(
                (a.get("truth_status", ""), a.get("canonical_status", "")))

    def canon_status(lpid):
        vals = truth_by_prop.get(lpid, [])
        truths = {t for t, _ in vals}
        if truths == {"true"} or ("true" in truths and "unknown" not in truths):
            return "true"
        if "unknown" in truths:
            return "undetermined"
        return "undetermined"

    prop_kid = {}
    prop_rows = []
    for r in props:
        lpid = r.get("proposition_id", "")
        kid = slug(lpid)
        prop_kid[lpid] = kid
        st = canon_status(lpid)
        span = "provisional" if st in ("true", "false") else ""
        prop_rows.append((kid, cell(r.get("normalized_proposition", "")), st, "ms-book3", span))
    stats["propositions"] = len(prop_rows)

    # ---- Assertions routed by story_graph_destination -------------------
    epi_rows, log_rows, loop_rows, rel_rows = [], [], [], []
    local_vocab = {}
    quotes_present = 0
    for a in asserts:
        dest = a.get("story_graph_destination", "")
        if a.get("source_quote", "").strip():
            quotes_present += 1
        ch = chapter_of(a.get("valid_from_scene", ""))
        if dest == "Knowledge States":
            holder = resolve(a.get("subject_id", ""))
            pid = prop_kid.get(a.get("proposition_id", ""))
            if not holder or not pid:
                cov.append(f"EPISTEMIC dropped — unresolved holder/proposition: {a.get('subject_id','?')} / {a.get('proposition_id','?')}")
                continue
            mode = PRED_MODE.get(a.get("predicate", ""), "knows")
            if mode == "believes" and a.get("truth_status") == "false":
                mode = "believes-false"
            epi_rows.append((pid, holder, mode, ch, "provisional"))
        elif dest == "Logistics":
            ent = resolve(a.get("subject_id", ""))
            if not ent:
                cov.append(f"LOGISTICS dropped — subject '{a.get('subject_id','?')}' is not a v2 entity (e.g. CANON/world-level): {cell(a.get('predicate',''))} {cell(a.get('object_id_or_value',''))}")
                continue
            log_rows.append((ch, ent, "-", cell(a.get("object_id_or_value", "")), "provisional",
                             cell(a.get("predicate", ""))))
        elif dest == "Open Loops & Guns":
            base = slug(a.get("proposition_id", "") or a.get("assertion_id", ""))
            loop_rows.append((base, ch, cell(a.get("object_id_or_value", "") or a.get("predicate", "")),
                              "", "UNFIRED", "provisional"))
        elif dest == "Relationships":
            frm, to = resolve(a.get("subject_id", "")), resolve(a.get("object_id_or_value", ""))
            if not frm or not to:
                cov.append(f"RELATIONSHIP dropped — unresolved endpoints: {a.get('subject_id','?')} -> {a.get('object_id_or_value','?')}")
                continue
            edge = slug(a.get("predicate", "")).replace("-", "_")
            local_vocab[edge] = f"imported from legacy predicate {a.get('predicate','')}"
            rel_rows.append((frm, edge, to, "stable", ch, "", "imported"))
        # Canon Commit Log destination handled via scene ledger below.
    stats["epistemic"] = len(epi_rows)
    stats["logistics"] = len(log_rows)
    stats["open_loops"] = len(loop_rows)
    stats["relationships"] = len(rel_rows)
    stats["assertion_quotes_present"] = quotes_present
    stats["assertion_total"] = len(asserts)
    if quotes_present == 0 and asserts:
        cov.append(f"EVIDENCE — 0 of {len(asserts)} assertions carry a verbatim source_quote; "
                   "no Evidence spans could be built, so all load-bearing rows are marked provisional.")

    # ---- Timeline + Canon Commit Log from the scene ledger --------------
    chapters = {}
    for s in scenes:
        c = s.get("chapter_index", "")
        if c.isdigit():
            chapters.setdefault(int(c), []).append(s)
    timeline_rows, commit_lines = [], []
    for c in sorted(chapters):
        first = chapters[c][0]
        story_time = cell(first.get("story_time_candidate", ""))
        heading = cell(first.get("chapter_heading", "")) or f"Chapter {c}"
        timeline_rows.append((str(c), story_time or "-", "-", heading))
        events = cell(chapters[c][0].get("major_events_candidate", ""))
        commit_lines.append(f"- ch {c}: {heading}" + (f" — {events[:160]}" if events else ""))
    stats["chapters"] = len(chapters)
    stats["scenes"] = len(scenes)

    md = _render(title, entity_rows, [("ms-book3", "manuscript", "4",
                 "imported: source_class=manuscript, authority_level=4")],
                 prop_rows, epi_rows, loop_rows, log_rows, rel_rows, timeline_rows,
                 commit_lines, local_vocab, max(chapters) if chapters else 0)
    report = _render_report(legacy_dir, stats, cov)
    return md, report, stats


def _tbl(header, rows):
    cols = header.split(" | ")
    out = ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(x) for x in r) + " |")
    return "\n".join(out)


def _render(title, ents, srcs, props, epi, loops, logs, rels, timeline, commits, local_vocab, canon_ch):
    lv_rows = [(e, d) for e, d in sorted(local_vocab.items())]
    parts = [f"# Story Graph: {title}", "",
             _tbl("field | value", [("ontology-version", "2"), ("modules", "none"),
                                    ("current-canon-chapter", str(canon_ch))]), "",
             "## Local Vocabulary", _tbl("edge | description", lv_rows), "",
             "## Sources", _tbl("source-id | type | authority | note", srcs), "",
             "## Entities", _tbl("id | type | status | voice | note", ents), "",
             "## Locations & Distances", _tbl("from | to | time | mode", []), "",
             "## Relationships", _tbl("from | edge | to | trend | since-ch | span | note", rels), "",
             "## Propositions", _tbl("prop-id | statement | canon-status | governing-source | span", props), "",
             "## Epistemic States", _tbl("prop-id | holder | mode | since-ch | span", epi), "",
             "## Open Loops & Setups", _tbl("id | planted-ch | expectation | must-fire-by | status | span", loops), "",
             "## Evidence", _tbl("span-id | source-id | locator | quote | note", []), "",
             "## Timeline", _tbl("ch | story-time | elapsed | note", timeline), "",
             "## Logistics", _tbl("ch | entity | location | condition | span | note", logs), "",
             "## Canon Commit Log", "\n".join(commits), ""]
    return "\n".join(parts) + "\n"


def _render_report(legacy_dir, stats, cov):
    lines = ["# Legacy import — coverage report", "",
             f"Source: `{legacy_dir}`", "",
             "## Imported into the v2 graph", ""]
    for k in ("scenes", "chapters", "entities", "propositions", "epistemic",
              "logistics", "open_loops", "relationships"):
        lines.append(f"- {k.replace('_',' ')}: **{stats.get(k,0)}**")
    lines += ["", f"- assertions carrying a verbatim quote: **{stats.get('assertion_quotes_present',0)}** "
              f"of {stats.get('assertion_total',0)}", "",
              "## Not faithfully representable in ontology v2 (dropped or degraded)", ""]
    if cov:
        for c in cov:
            lines.append(f"- {c}")
    else:
        lines.append("- (nothing dropped)")
    lines += ["", "## Layers absent from these ledgers entirely", "",
              "- Event layer (events, continuity groups) — lives in the deep-analysis packages, not these masters.",
              "- Plot threads / intersections — same.",
              "- Promise *lifecycle* (introduce→advance→pay-off) — only flat open loops are modeled here."]
    return "\n".join(lines) + "\n"


def main(argv=None):
    p = argparse.ArgumentParser(prog="story_graph_import")
    p.add_argument("legacy_dir")
    p.add_argument("--out", required=True)
    p.add_argument("--report", default="")
    p.add_argument("--title", default="Imported Legacy Canon")
    a = p.parse_args(argv)
    md, report, stats = build(a.legacy_dir, a.title)
    Path(a.out).write_text(md, encoding="utf-8")
    if a.report:
        Path(a.report).write_text(report, encoding="utf-8")
    print(f"wrote {a.out}: " + ", ".join(f"{k}={v}" for k, v in stats.items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
