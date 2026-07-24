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
    return {"header": fields, "modules": modules, "canon_ch": canon_ch,
            "sections": rows, "order": order}


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


def validate(graph_path, ontology="", genres_dir="", spe_dir="", chapters_dir=""):
    report = Report()
    try:
        text = Path(graph_path).read_text(encoding="utf-8")
    except OSError as e:
        report.error(f"cannot read graph file: {e}")
        return report
    graph = parse_graph(text)
    check_structure(graph, report)
    check_header(graph, report)
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
    args = parser.parse_args(argv)
    if args.command == "validate":
        report = validate(args.graph, args.ontology, args.genres_dir, args.spe_dir, args.chapters_dir)
        for e in report.errors:
            print(f"ERROR: {e}")
        for w in report.warnings:
            print(f"WARN: {w}")
        print(f"RESULT: {len(report.errors)} error(s), {len(report.warnings)} warning(s)")
        return 1 if report.errors else 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
