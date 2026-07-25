#!/usr/bin/env python3
"""Import a legacy Story-Graph canon CSV set into an ontology-v2 Story-Graph.md.

Stdlib only. Reads the reconciled/frozen legacy ledgers (entity registry,
proposition registry, routed assertions, scene ledger) and emits a v2 graph
plus a coverage report of everything it could NOT faithfully map. Anything the
legacy data does not support (e.g. missing verbatim evidence quotes) is marked
`provisional` rather than fabricated.

Fidelity rules (anti-invention):
  * Entity references are resolved by canonical name, alias, and token overlap
    before anything is dropped.
  * A referenced name that does not resolve is auto-registered as a PROVISIONAL
    entity ONLY when it is the agent (subject/endpoint) of a knowledge or
    relationship assertion and reads as a proper noun. Value strings and events
    are never turned into entities.
  * CANON-subject world/setting facts are already captured by their proposition
    (every such assertion carries a proposition_id present in the registry), so
    they are reported as covered, not dropped, and no bogus Logistics row is
    emitted.

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
AGENT_RE = re.compile(r"^[A-Z][A-Za-z'’]+(?: [A-Z][A-Za-z'’]+)*$")
GROUP_WORDS = {"council", "guard", "government", "forces", "resistance", "magisterium",
               "coalition", "guild", "team", "convoy", "zone", "administration", "signal",
               "hunt", "hunters", "gunship", "guardians"}


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


def _looks_like_agent(s: str) -> bool:
    s = (s or "").strip()
    return bool(s) and len(s) <= 40 and bool(AGENT_RE.fullmatch(s))


def _load_chapters(chapters_dir):
    text = {}
    if not chapters_dir:
        return text
    for p in Path(chapters_dir).glob("ch*.md"):
        m = re.search(r"ch0*(\d+)", p.name)
        if m:
            text[int(m.group(1))] = p.read_text(encoding="utf-8")
    return text


def _quote_cell(q):
    return (q or "").replace("|", "/").replace("\r", " ").replace("\n", " ").strip()


def build(legacy_dir: str, title: str, quotes_path: str = "", chapters_dir: str = ""):
    ents = _read(_find(legacy_dir, "*ENTITY-REGISTRY*.csv"))
    props = _read(_find(legacy_dir, "*PROPOSITION-REGISTRY*.csv"))
    asserts = _read(_find(legacy_dir, "*ASSERTIONS*.csv"))
    scenes = _read(_find(legacy_dir, "*SCENE-LEDGER*.csv"))
    cov, stats = [], {}

    ent_by_legacy, name_map, used = {}, {}, set()
    entity_rows = []

    def register(base, v2t, status, note, legacy_id=None, names=()):
        eid, i = slug(base), 2
        while eid in used:
            eid, i = f"{slug(base)}-{i}", i + 1
        used.add(eid)
        entity_rows.append((eid, v2t, cell(status) or "active", "-", cell(note)))
        if legacy_id:
            ent_by_legacy[legacy_id] = eid
        for nm in names:
            k = (nm or "").lower().strip()
            if k:
                name_map.setdefault(k, eid)
        return eid

    # ---- Entities from the registry ------------------------------------
    for r in ents:
        et = r.get("entity_type", "")
        v2t = ENTITY_TYPE_MAP.get(et)
        if not v2t:
            cov.append(f"ENTITY not imported — type '{et}' is not a v2 entity: {r.get('canonical_name','?')}")
            continue
        aliases = [a for a in re.split(r"[;,/]", r.get("aliases", "") or "") if a.strip()]
        register(r.get("canonical_name") or r.get("entity_id"), v2t,
                 r.get("status", "active"), r.get("aliases", ""),
                 legacy_id=r.get("entity_id", ""),
                 names=[r.get("canonical_name", "")] + aliases)
    stats["entities_from_registry"] = len(entity_rows)

    def resolve(s):
        s = (s or "").strip()
        if not s:
            return None
        if s.lower() == "reader":
            return "reader"
        if s in ent_by_legacy:
            return ent_by_legacy[s]
        k = s.lower()
        if k in name_map:
            return name_map[k]
        toks = set(re.findall(r"[a-z]+", k))
        if toks:
            for nm, eid in name_map.items():
                nt = set(re.findall(r"[a-z]+", nm))
                if nt and (toks <= nt or nt <= toks):
                    return eid
        return None

    # ---- Auto-register provisional agents (subjects/endpoints only) -----
    auto = 0
    for a in asserts:
        dest = a.get("story_graph_destination", "")
        cands = []
        if dest == "Knowledge States":
            cands = [a.get("subject_id", "")]
        elif dest == "Relationships":
            cands = [a.get("subject_id", ""), a.get("object_id_or_value", "")]
        for v in cands:
            v = (v or "").strip()
            if not v or v.upper() == "CANON" or resolve(v) or not _looks_like_agent(v):
                continue
            v2t = "Faction" if (set(re.findall(r"[a-z]+", v.lower())) & GROUP_WORDS) else "Character"
            register(v, v2t, "provisional", f"provisional — auto-registered from an assertion reference; type guessed {v2t}",
                     names=[v])
            cov.append(f"ENTITY auto-registered (provisional {v2t}) from assertion reference: {v}")
            auto += 1
    stats["entities_auto_registered"] = auto
    stats["entities_total"] = len(entity_rows)

    # ---- Evidence: verified verbatim quotes (optional) -----------------
    chapter_text = _load_chapters(chapters_dir)
    quoted = _read(quotes_path) if quotes_path else []
    evidence_rows, prop_span = [], {}
    for r in quoted:
        pid = r.get("proposition_id", "")
        quote = (r.get("source_quote") or "").strip()
        if not pid or not quote or pid in prop_span:
            continue
        c = chapter_of(r.get("valid_from_scene", ""))
        loc = None
        if c.isdigit() and int(c) in chapter_text and quote in chapter_text[int(c)]:
            loc = int(c)
        if loc is None:
            loc = next((n for n, body in chapter_text.items() if quote in body), None)
        if loc is None:
            continue  # not verbatim on the page -> the proposition stays provisional
        sid = f"ev-{slug(pid)}"
        evidence_rows.append((sid, "ms-book3", f"ch{int(loc):02d}", _quote_cell(quote),
                              "imported verbatim quote"))
        prop_span[pid] = sid
    stats["evidence_spans"] = len(evidence_rows)
    if evidence_rows:
        cov.append(f"EVIDENCE — {len(evidence_rows)} propositions backed by verified verbatim "
                   "manuscript quotes; the remaining load-bearing rows stay provisional.")

    # ---- Propositions (canon-status derived from assertions) ------------
    truth_by_prop = {}
    for a in asserts:
        pid = a.get("proposition_id", "")
        if pid:
            truth_by_prop.setdefault(pid, []).append(a.get("truth_status", ""))

    def canon_status(lpid):
        truths = set(truth_by_prop.get(lpid, []))
        if truths and "unknown" not in truths and truths <= {"true"}:
            return "true"
        if truths == {"false"}:
            return "false"
        return "undetermined"

    prop_kid, prop_rows = {}, []
    for r in props:
        lpid = r.get("proposition_id", "")
        kid = slug(lpid)
        prop_kid[lpid] = kid
        st = canon_status(lpid)
        span = prop_span.get(lpid) or ("provisional" if st in ("true", "false") else "")
        prop_rows.append((kid, cell(r.get("normalized_proposition", "")), st, "ms-book3", span))
    stats["propositions"] = len(prop_rows)

    # ---- Assertions routed by story_graph_destination -------------------
    epi_rows, log_rows, loop_rows, rel_rows = [], [], [], []
    local_vocab, quotes = {}, 0
    for a in asserts:
        dest = a.get("story_graph_destination", "")
        if a.get("source_quote", "").strip():
            quotes += 1
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
            if ent is None:
                lpid = a.get("proposition_id", "")
                if lpid in prop_kid:
                    cov.append(f"WORLD-FACT captured as proposition {prop_kid[lpid]} (world/CANON-level, no entity home in Logistics): {cell(a.get('predicate',''))} {cell(a.get('object_id_or_value',''))}")
                else:
                    cov.append(f"LOGISTICS dropped — world/CANON-level with no backing proposition: {cell(a.get('predicate',''))} {cell(a.get('object_id_or_value',''))}")
                continue
            log_rows.append((ch, ent, "-", cell(a.get("object_id_or_value", "")), "provisional",
                             cell(a.get("predicate", ""))))
        elif dest == "Open Loops & Guns":
            loop_rows.append((slug(a.get("proposition_id", "") or a.get("assertion_id", "")), ch,
                              cell(a.get("object_id_or_value", "") or a.get("predicate", "")),
                              "", "UNFIRED", "provisional"))
        elif dest == "Relationships":
            frm, to = resolve(a.get("subject_id", "")), resolve(a.get("object_id_or_value", ""))
            if not frm or not to:
                cov.append(f"RELATIONSHIP dropped — unresolved endpoints: {a.get('subject_id','?')} -> {a.get('object_id_or_value','?')}")
                continue
            edge = slug(a.get("predicate", "")).replace("-", "_")
            local_vocab[edge] = f"imported from legacy predicate {a.get('predicate','')}"
            rel_rows.append((frm, edge, to, "stable", ch, "", "imported"))
    stats.update(epistemic=len(epi_rows), logistics=len(log_rows),
                 open_loops=len(loop_rows), relationships=len(rel_rows),
                 assertion_quotes_present=quotes, assertion_total=len(asserts))
    if quotes == 0 and asserts:
        cov.append(f"EVIDENCE — 0 of {len(asserts)} assertions carry a verbatim source_quote; "
                   "no Evidence spans could be built, so every load-bearing row is provisional.")

    # ---- Timeline + Canon Commit Log from the scene ledger --------------
    chapters = {}
    for s in scenes:
        c = s.get("chapter_index", "")
        if c.isdigit():
            chapters.setdefault(int(c), []).append(s)
    timeline_rows, commit_lines = [], []
    for c in sorted(chapters):
        first = chapters[c][0]
        heading = cell(first.get("chapter_heading", "")) or f"Chapter {c}"
        timeline_rows.append((str(c), cell(first.get("story_time_candidate", "")) or "-", "-", heading))
        events = cell(first.get("major_events_candidate", ""))
        commit_lines.append(f"- ch {c}: {heading}" + (f" — {events[:160]}" if events else ""))
    stats.update(chapters=len(chapters), scenes=len(scenes))

    md = _render(title, entity_rows,
                 [("ms-book3", "manuscript", "4", "imported: source_class=manuscript, authority_level=4")],
                 prop_rows, epi_rows, loop_rows, log_rows, rel_rows, timeline_rows, commit_lines,
                 evidence_rows, local_vocab, max(chapters) if chapters else 0)
    return md, _render_report(legacy_dir, stats, cov), stats


def _tbl(header, rows):
    cols = header.split(" | ")
    out = ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(x) for x in r) + " |")
    return "\n".join(out)


def _render(title, ents, srcs, props, epi, loops, logs, rels, timeline, commits, evidence, local_vocab, canon_ch):
    parts = [f"# Story Graph: {title}", "",
             _tbl("field | value", [("ontology-version", "2"), ("modules", "none"),
                                    ("current-canon-chapter", str(canon_ch))]), "",
             "## Local Vocabulary", _tbl("edge | description", sorted(local_vocab.items())), "",
             "## Sources", _tbl("source-id | type | authority | note", srcs), "",
             "## Entities", _tbl("id | type | status | voice | note", ents), "",
             "## Locations & Distances", _tbl("from | to | time | mode", []), "",
             "## Relationships", _tbl("from | edge | to | trend | since-ch | span | note", rels), "",
             "## Propositions", _tbl("prop-id | statement | canon-status | governing-source | span", props), "",
             "## Epistemic States", _tbl("prop-id | holder | mode | since-ch | span", epi), "",
             "## Open Loops & Setups", _tbl("id | planted-ch | expectation | must-fire-by | status | span", loops), "",
             "## Evidence", _tbl("span-id | source-id | locator | quote | note", evidence), "",
             "## Timeline", _tbl("ch | story-time | elapsed | note", timeline), "",
             "## Logistics", _tbl("ch | entity | location | condition | span | note", logs), "",
             "## Canon Commit Log", "\n".join(commits), ""]
    return "\n".join(parts) + "\n"


def _render_report(legacy_dir, stats, cov):
    lines = ["# Legacy import — coverage report", "", f"Source: `{legacy_dir}`", "",
             "## Imported into the v2 graph", ""]
    for k in ("scenes", "chapters", "entities_from_registry", "entities_auto_registered",
              "entities_total", "propositions", "epistemic", "logistics", "open_loops", "relationships"):
        lines.append(f"- {k.replace('_',' ')}: **{stats.get(k,0)}**")
    lines += ["", f"- assertions carrying a verbatim quote: **{stats.get('assertion_quotes_present',0)}** "
              f"of {stats.get('assertion_total',0)}", "",
              "## Mapping notes — covered elsewhere, dropped, or degraded", ""]
    for c in (cov or ["(nothing to note)"]):
        lines.append(f"- {c}")
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
    p.add_argument("--quotes", default="")
    p.add_argument("--chapters-dir", default="")
    a = p.parse_args(argv)
    md, report, stats = build(a.legacy_dir, a.title, a.quotes, a.chapters_dir)
    Path(a.out).write_text(md, encoding="utf-8")
    if a.report:
        Path(a.report).write_text(report, encoding="utf-8")
    print(f"wrote {a.out}: " + ", ".join(f"{k}={v}" for k, v in stats.items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
