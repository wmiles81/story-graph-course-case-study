#!/usr/bin/env python3
"""Story Graph validator + compiler (ontology v2).

Stdlib only for parsing and `validate`. `compile` lazily imports the Kùzu
loader (story_graph_kuzu). See Story-Graph-Ontology-v2.md for the schema.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

CORE_SECTIONS = [
    "Local Vocabulary", "Sources", "Entities", "Locations & Distances",
    "Relationships", "Propositions", "Epistemic States", "Open Loops & Setups",
    "Evidence", "Timeline", "Logistics", "Canon Commit Log",
]
MODULE_SECTIONS = {"spe": ["Physics State"]}

SOURCE_TYPES = {"manuscript", "bible", "outline", "editorial", "draft", "ghost-draft"}
CANON_STATUS = {"true", "false", "undetermined", "contested"}
EPISTEMIC_MODES = {"knows", "believes", "believes-false", "suspects", "embargoed-until"}
ENTITY_TYPES = {"Character", "Object", "Location", "Faction"}
TRENDS = {"hardening", "softening", "stable", "volatile", "broken"}
SETUP_STATUS_RE = re.compile(r"^(UNFIRED|FIRED ch-\d+|DEFUSED ch-\d+)$")
RESERVED_HOLDERS = {"reader"}
KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


class Report:
    def __init__(self):
        self.errors = []
        self.warnings = []

    def error(self, msg):
        self.errors.append(msg)

    def warn(self, msg):
        self.warnings.append(msg)


def parse_sections(text):
    sections, order = {}, []
    name, buf = "HEADER", []
    for line in text.splitlines():
        m = re.match(r"^##\s+(.*?)\s*$", line)
        if m:
            sections[name] = buf
            if name != "HEADER":
                order.append(name)
            name, buf = m.group(1), []
        else:
            buf.append(line)
    sections[name] = buf
    if name != "HEADER":
        order.append(name)
    return sections, order


def parse_table(lines):
    headers, rows = None, []
    for line in lines:
        s = line.strip()
        if not s.startswith("|"):
            if headers is not None and rows:
                break
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if headers is None:
            headers = [c.lower() for c in cells]
            continue
        if all(re.fullmatch(r":?-{3,}:?", c) for c in cells):
            continue
        rows.append(dict(zip(headers, cells)))
    return headers or [], rows


def parse_header_fields(lines):
    _, rows = parse_table(lines)
    return {r.get("field", ""): r.get("value", "") for r in rows}


def parse_graph(text):
    sections, order = parse_sections(text)
    fields = parse_header_fields(sections.get("HEADER", []))
    raw_modules = fields.get("modules", "none").strip()
    modules = [] if raw_modules in ("none", "") else [m.strip() for m in raw_modules.split(",") if m.strip()]
    canon_raw = fields.get("current-canon-chapter", "0")
    canon_ch = int(canon_raw) if re.fullmatch(r"\d+", canon_raw or "") else 0
    rows = {name: parse_table(sections.get(name, []))[1] for name in order}
    graph_raw = {name: sections.get(name, []) for name in order}
    return {"header": fields, "modules": modules, "canon_ch": canon_ch,
            "sections": rows, "order": order, "_raw": graph_raw}


def _raw_section_lines(graph, name):
    return graph.get("_raw", {}).get(name, [])


def required_sections(graph):
    req = list(CORE_SECTIONS)
    for mod in graph["modules"]:
        req += MODULE_SECTIONS.get(mod, [])
    return req


def check_structure(graph, report):
    order = graph["order"]
    for mod in graph["modules"]:
        if mod not in MODULE_SECTIONS:
            report.error(f"unknown module declared: '{mod}'")
    req = required_sections(graph)
    present = [s for s in order if s in req]
    for s in req:
        if s not in order:
            report.error(f"missing required section: '## {s}'")
    known = set(req)
    for s in order:
        if s not in known:
            report.error(f"unknown section: '## {s}' (not core, not from a declared module)")
    core_in_order = [s for s in order if s in CORE_SECTIONS]
    if all(s in order for s in CORE_SECTIONS) and core_in_order != CORE_SECTIONS:
        report.error(f"core sections out of canonical order (expected {CORE_SECTIONS}, found {core_in_order})")


def check_header(graph, report):
    fields = graph["header"]
    for key in ("ontology-version", "modules", "current-canon-chapter"):
        if not fields.get(key):
            report.error(f"header block missing field: {key}")
    if fields.get("ontology-version") != "2":
        report.error(f"ontology-version must be '2', got '{fields.get('ontology-version')}'")
    raw = fields.get("current-canon-chapter", "0")
    if not re.fullmatch(r"\d+", raw or ""):
        report.error(f"current-canon-chapter must be an integer, got '{raw}'")
        return 0
    return int(raw)


def check_sources(graph, report):
    sources = {}
    for r in graph["sections"].get("Sources", []):
        sid = r.get("source-id", "")
        if not sid:
            continue
        if sid in sources:
            report.error(f"Sources: duplicate source-id '{sid}'")
        if not KEBAB.fullmatch(sid):
            report.error(f"Sources: source-id '{sid}' is not kebab-case")
        stype = r.get("type", "")
        if stype not in SOURCE_TYPES:
            report.error(f"Sources: unknown type '{stype}' for '{sid}'")
        auth_raw = r.get("authority", "")
        auth = int(auth_raw) if re.fullmatch(r"-?\d+", auth_raw or "") else None
        if auth is None:
            report.error(f"Sources: authority must be an integer for '{sid}', got '{auth_raw}'")
        sources[sid] = {"type": stype, "authority": auth if auth is not None else 0}
    return sources


def check_authority(graph, sources, report):
    for r in graph["sections"].get("Propositions", []):
        gov = r.get("governing-source", "")
        pid = r.get("prop-id", "?")
        if not gov:
            continue
        if gov not in sources:
            report.error(f"Propositions [{pid}]: governing-source '{gov}' is not a declared source")
            continue
        if sources[gov]["type"] == "editorial":
            report.error(f"Propositions [{pid}]: editorial source '{gov}' cannot be a governing-source (it flags, never asserts)")


def is_provisional(row):
    return any("provisional" in (v or "").lower() for v in row.values())


def _span_ids(cell):
    return [s.strip() for s in re.split(r"[,\s]+", cell or "") if s.strip() and s.strip().lower() != "provisional"]


def _check_span_required(section, row_id, row, span_ids, report):
    ids = _span_ids(row.get("span", ""))
    if not ids:
        if is_provisional(row):
            report.warn(f"{section} [{row_id}]: provisional — no evidence span, claim is unverified")
        else:
            report.error(f"{section} [{row_id}]: load-bearing row has no evidence span (mark 'provisional' if intended)")
        return
    for sid in ids:
        if sid not in span_ids:
            report.error(f"{section} [{row_id}]: span '{sid}' is not a declared Evidence span-id")


def check_propositions(graph, sources, span_ids, report):
    prop_ids = set()
    for r in graph["sections"].get("Propositions", []):
        pid = r.get("prop-id", "")
        if not pid:
            continue
        if pid in prop_ids:
            report.error(f"Propositions: duplicate prop-id '{pid}'")
        if not KEBAB.fullmatch(pid):
            report.error(f"Propositions: prop-id '{pid}' is not kebab-case")
        status = r.get("canon-status", "")
        if status not in CANON_STATUS:
            report.error(f"Propositions [{pid}]: unknown canon-status '{status}'")
        if status in ("true", "false"):
            _check_span_required("Propositions", pid, r, span_ids, report)
        prop_ids.add(pid)
    return prop_ids


def check_epistemic(graph, entity_ids, prop_ids, span_ids, report):
    rows = graph["sections"].get("Epistemic States", [])
    embargo = {}  # (prop, holder) -> ch
    for r in rows:
        if r.get("mode") == "embargoed-until":
            ch = r.get("since-ch", "")
            if ch.isdigit():
                embargo[(r.get("prop-id", ""), r.get("holder", ""))] = int(ch)
    for r in rows:
        pid = r.get("prop-id", "")
        holder = r.get("holder", "")
        mode = r.get("mode", "")
        label = f"{pid}/{holder}"
        if pid and pid not in prop_ids:
            report.error(f"Epistemic States [{label}]: proposition '{pid}' is not declared")
        if holder and holder not in entity_ids and holder not in RESERVED_HOLDERS:
            report.error(f"Epistemic States [{label}]: holder '{holder}' is not a declared entity or reserved holder")
        if mode and mode not in EPISTEMIC_MODES:
            report.error(f"Epistemic States [{label}]: unknown mode '{mode}'")
        if mode in ("knows", "believes", "believes-false", "suspects"):
            _check_span_required("Epistemic States", label, r, span_ids, report)
            ch = r.get("since-ch", "")
            key = (pid, holder)
            if mode == "knows" and ch.isdigit() and key in embargo and int(ch) < embargo[key]:
                report.error(f"Epistemic States [{label}]: embargo violation — knows at ch{ch} but embargoed until ch{embargo[key]}")


def check_evidence(graph, sources, report):
    span_ids = set()
    for r in graph["sections"].get("Evidence", []):
        sid = r.get("span-id", "")
        if not sid:
            continue
        if sid in span_ids:
            report.error(f"Evidence: duplicate span-id '{sid}'")
        if not KEBAB.fullmatch(sid):
            report.error(f"Evidence: span-id '{sid}' is not kebab-case")
        src = r.get("source-id", "")
        if src and src not in sources:
            report.error(f"Evidence [{sid}]: source-id '{src}' is not a declared source")
        if src in sources and sources[src]["type"] == "manuscript" and not r.get("quote", "").strip():
            report.error(f"Evidence [{sid}]: manuscript span requires a verbatim quote")
        span_ids.add(sid)
    return span_ids


def check_entities(graph, report):
    ids, locations = set(), set()
    for r in graph["sections"].get("Entities", []):
        eid, etype = r.get("id", ""), r.get("type", "")
        if not eid:
            continue
        if eid in ids:
            report.error(f"Entities: duplicate id '{eid}'")
        if not KEBAB.fullmatch(eid):
            report.error(f"Entities: id '{eid}' is not kebab-case")
        if etype not in ENTITY_TYPES:
            report.error(f"Entities: unknown type '{etype}' for '{eid}'")
        ids.add(eid)
        if etype == "Location":
            locations.add(eid)
    return ids, locations


def check_open_loops(graph, canon_ch, span_ids, report):
    for r in graph["sections"].get("Open Loops & Setups", []):
        gid, status = r.get("id", "?"), r.get("status", "")
        if gid == "?" or not gid:
            continue
        if not SETUP_STATUS_RE.fullmatch(status):
            report.error(f"Open Loops & Setups [{gid}]: invalid status '{status}'")
            continue
        planted_raw = r.get("planted-ch", "0") or "0"
        if not planted_raw.isdigit():
            report.error(f"Open Loops & Setups [{gid}]: planted-ch must be an integer, got '{planted_raw}'")
            continue
        planted = int(planted_raw)
        m = re.match(r"FIRED ch-(\d+)", status)
        if m and int(m.group(1)) < planted:
            report.error(f"Open Loops & Setups [{gid}]: fired at ch{m.group(1)} before planted at ch{planted}")
        _check_span_required("Open Loops & Setups", gid, r, span_ids, report)
        must_by = r.get("must-fire-by", "")
        if status == "UNFIRED" and must_by.isdigit() and int(must_by) <= canon_ch:
            report.warn(f"Open Loops & Setups [{gid}]: OVERDUE — must fire by ch{must_by}, canon at ch{canon_ch}, still UNFIRED")


def check_logistics(graph, entity_ids, location_ids, span_ids, report):
    for r in graph["sections"].get("Logistics", []):
        eid, loc = r.get("entity", ""), r.get("location", "")
        if eid and eid not in entity_ids:
            report.error(f"Logistics: entity '{eid}' is not declared")
        if loc and loc != "-" and loc not in location_ids:
            report.error(f"Logistics: location '{loc}' is not a Location entity")
        change = (r.get("condition", "").strip() not in ("", "-"))
        if change and _span_ids(r.get("span", "")) == [] and not is_provisional(r):
            report.error(f"Logistics [ch{r.get('ch','?')}/{eid}]: condition change has no evidence span")


LOG_RE = re.compile(r"^-\s*ch\s*(\d+)\s*:")


def check_commit_log(graph, report):
    last = 0
    for line in "\n".join(
        line for line in _raw_section_lines(graph, "Canon Commit Log")
    ).splitlines():
        m = LOG_RE.match(line.strip())
        if not m:
            continue
        ch = int(m.group(1))
        if ch <= last:
            report.error(f"Canon Commit Log: chapter regression — ch{ch} after ch{last} (must strictly increase)")
        last = ch


def _resolve_chapter(chapters_dir, locator):
    base = Path(chapters_dir)
    m = re.fullmatch(r"ch(\d+)", (locator or "").strip())
    candidates = [base / f"{locator}.md"]
    if m:
        candidates.append(base / f"ch{int(m.group(1)):02d}.md")
    for c in candidates:
        if c.is_file():
            return c
    return None


def verify_spans(graph, sources, chapters_dir, report):
    for r in graph["sections"].get("Evidence", []):
        sid = r.get("span-id", "")
        src = r.get("source-id", "")
        if sources.get(src, {}).get("type") != "manuscript":
            continue
        quote = r.get("quote", "").strip()
        if not quote:
            continue  # already an error from check_evidence
        if not chapters_dir:
            report.warn(f"Evidence [{sid}]: could not verify manuscript quote (no --chapters-dir)")
            continue
        chapter = _resolve_chapter(chapters_dir, r.get("locator", ""))
        if chapter is None:
            report.warn(f"Evidence [{sid}]: could not verify — chapter file for '{r.get('locator','')}' not found")
            continue
        if quote not in chapter.read_text(encoding="utf-8"):
            report.error(f"Evidence [{sid}]: quote not found in {chapter.name} — graph-vs-source mismatch")


def validate(graph_path, ontology="", genres_dir="", spe_dir="", chapters_dir=""):
    report = Report()
    try:
        text = Path(graph_path).read_text(encoding="utf-8")
    except OSError as e:
        report.error(f"cannot read graph file: {e}")
        return report
    graph = parse_graph(text)
    canon_ch = check_header(graph, report)
    check_structure(graph, report)
    sources = check_sources(graph, report)
    check_authority(graph, sources, report)
    entity_ids, location_ids = check_entities(graph, report)
    span_ids = check_evidence(graph, sources, report)
    verify_spans(graph, sources, chapters_dir, report)
    prop_ids = check_propositions(graph, sources, span_ids, report)
    check_epistemic(graph, entity_ids, prop_ids, span_ids, report)
    check_open_loops(graph, canon_ch, span_ids, report)
    check_logistics(graph, entity_ids, location_ids, span_ids, report)
    check_commit_log(graph, report)
    return report


def compile_graph(graph_path, out_path, ontology="", chapters_dir=""):
    report = validate(graph_path, ontology=ontology, chapters_dir=chapters_dir)
    if report.errors:
        report.error("refusing to compile: fix validation ERRORs first")
        return report
    try:
        import story_graph_kuzu
    except ImportError:
        report.error("compile requires the 'kuzu' package (pip install kuzu); nothing was written")
        return report
    text = Path(graph_path).read_text(encoding="utf-8")
    story_graph_kuzu.load_graph(parse_graph(text), out_path)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(prog="story_graph")
    sub = parser.add_subparsers(dest="command", required=True)
    v = sub.add_parser("validate")
    v.add_argument("graph")
    v.add_argument("--ontology", default="")
    v.add_argument("--genres-dir", default="")
    v.add_argument("--spe-dir", default="")
    v.add_argument("--chapters-dir", default="")
    c = sub.add_parser("compile")
    c.add_argument("graph")
    c.add_argument("--out", required=True)
    c.add_argument("--ontology", default="")
    c.add_argument("--chapters-dir", default="")
    args = parser.parse_args(argv)
    if args.command == "validate":
        report = validate(args.graph, args.ontology, args.genres_dir, args.spe_dir, args.chapters_dir)
        for e in report.errors:
            print(f"ERROR: {e}")
        for w in report.warnings:
            print(f"WARN: {w}")
        print(f"RESULT: {len(report.errors)} error(s), {len(report.warnings)} warning(s)")
        return 1 if report.errors else 0
    if args.command == "compile":
        report = compile_graph(args.graph, args.out, args.ontology, args.chapters_dir)
        for e in report.errors:
            print(f"ERROR: {e}")
        for w in report.warnings:
            print(f"WARN: {w}")
        ok = not report.errors
        print(f"RESULT: {'compiled to ' + args.out if ok else 'not compiled'}; "
              f"{len(report.errors)} error(s), {len(report.warnings)} warning(s)")
        return 0 if ok else 1
    return 2


if __name__ == "__main__":
    sys.exit(main())
