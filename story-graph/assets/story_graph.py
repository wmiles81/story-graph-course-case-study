#!/usr/bin/env python3
"""Story Graph validator for the NPE Romance Architect.

Validates a per-story Story-Graph.md against the Story Graph Ontology:
structure, controlled vocabulary (core + imported genre modules + local),
referential integrity, canon logic, and continuity warnings.

Stdlib only. Exit 0 = no errors (warnings allowed); exit 1 = errors found.
Usage:
    python3 tools/story_graph.py validate <Story-Graph.md> \
        [--ontology Blueprints/Story-Graph-Ontology-v1.md] \
        [--genres-dir Blueprints/Genres] [--spe-dir SPE]
"""
import argparse
import re
import sys
from pathlib import Path

REQUIRED_SECTIONS = [
    "Local Vocabulary", "Entities", "Locations & Distances", "Relationships",
    "Knowledge States", "Open Loops & Guns", "Physics State", "Timeline",
    "Logistics", "Private Beliefs (Ghost)", "Canon Commit Log",
]
TRENDS = {"hardening", "softening", "stable", "volatile", "broken"}
ENTITY_TYPES = {"Character", "Object", "Location", "Faction"}
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
    """Split on '## ' headers. Returns ({name: lines}, [order]); preamble is 'HEADER'."""
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
    """First markdown table in lines -> (lowercased headers, [row dicts])."""
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


def check_structure(sections, order, report):
    present = [s for s in order if s in REQUIRED_SECTIONS]
    missing = [s for s in REQUIRED_SECTIONS if s not in order]
    for s in missing:
        report.error(f"missing section: '## {s}'")
    if not missing and present != REQUIRED_SECTIONS:
        report.error("sections out of canonical order "
                     f"(expected {REQUIRED_SECTIONS}, found {present})")
    for s in order:
        if s not in REQUIRED_SECTIONS:
            report.error(f"unknown section: '## {s}'")


def check_header(fields, report):
    for key in ("ontology-version", "genre-modules", "current-canon-chapter"):
        if key not in fields or not fields[key]:
            report.error(f"header block missing field: {key}")
    raw = fields.get("current-canon-chapter", "0")
    if not re.fullmatch(r"\d+", raw):
        report.error(f"current-canon-chapter must be an integer, got '{raw}'")
        return 0
    return int(raw)


def load_edge_vocab(md_path, section_name):
    try:
        text = md_path.read_text(encoding="utf-8")
    except OSError:
        return set()
    sections, _ = parse_sections(text)
    if section_name not in sections:
        return set()
    _, rows = parse_table(sections[section_name])
    return {r["edge"] for r in rows if r.get("edge")}


def resolve_genre_module(genres_dir, module_id):
    candidates = []
    if genres_dir.is_dir():
        for p in genres_dir.glob(f"{module_id}-v*.md"):
            m = re.search(r"-v(\d+)\.md$", p.name)
            if m:
                candidates.append((int(m.group(1)), p))
    return max(candidates)[1] if candidates else None


def load_vocabulary(ontology, genres_dir, declared, local_rows, report):
    vocab = load_edge_vocab(ontology, "Core Edge Vocabulary")
    if not vocab:
        report.error(f"could not load Core Edge Vocabulary from {ontology}")
    for module_id in declared:
        path = resolve_genre_module(genres_dir, module_id)
        if path is None:
            report.error(f"declared genre module not found: '{module_id}' in {genres_dir}")
            continue
        vocab |= load_edge_vocab(path, "Edge Vocabulary Extensions")
    vocab |= {r["edge"] for r in local_rows if r.get("edge")}
    return vocab


def check_relationships(rows, vocab, entity_ids, report):
    for r in rows:
        edge = r.get("edge", "")
        if edge and edge not in vocab:
            report.error(f"Relationships: edge '{edge}' not in core vocabulary, "
                         "declared genre modules, or Local Vocabulary (crosstalk?)")
        trend = r.get("trend", "")
        if trend and trend not in TRENDS:
            report.error(f"Relationships: unknown trend '{trend}'")
        for endpoint in ("from", "to"):
            eid = r.get(endpoint, "")
            if eid and eid not in entity_ids:
                report.error(f"Relationships: {endpoint} '{eid}' is not a declared entity")


def check_entities(rows, report):
    ids, locations = set(), set()
    for r in rows:
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


def check_travel(rows, location_ids, report):
    pairs = set()
    for r in rows:
        a, b = r.get("from", ""), r.get("to", "")
        for endpoint in (a, b):
            if endpoint and endpoint not in location_ids:
                report.error(f"Locations & Distances: '{endpoint}' is not a Location entity")
        if a and b:
            pairs.add(frozenset({a, b}))
    return pairs


def check_logistics(rows, entity_ids, location_ids, report):
    for r in rows:
        eid, loc = r.get("entity", ""), r.get("location", "")
        if eid and eid not in entity_ids:
            report.error(f"Logistics: entity '{eid}' is not declared")
        if loc and loc != "-" and loc not in location_ids:
            report.error(f"Logistics: location '{loc}' is not a Location entity")


def check_ghost(rows, entity_ids, report):
    for r in rows:
        for field in ("holder", "about"):
            eid = r.get(field, "")
            if eid and eid not in entity_ids:
                report.error(f"Private Beliefs: {field} '{eid}' is not declared")
        if not r.get("source", "").strip():
            report.error("Private Beliefs: row missing mandatory source pointer "
                         f"(holder='{r.get('holder', '?')}')")


KNOWN_RE = re.compile(r"([a-z0-9-]+)\s*\(ch\s*(\d+)\)")
EMBARGO_RE = re.compile(r"([a-z0-9-]+)\s*\(until\s*ch\s*(\d+)\)")
GUN_STATUS_RE = re.compile(r"^(UNFIRED|FIRED ch-\d+|DEFUSED ch-\d+)$")
LOG_RE = re.compile(r"^-\s*ch\s*(\d+)\s*:")


def check_knowledge(rows, entity_ids, report):
    for r in rows:
        fact = r.get("fact-id", "?")
        known = {m.group(1): int(m.group(2))
                 for m in KNOWN_RE.finditer(r.get("known-by", ""))}
        embargo = {m.group(1): int(m.group(2))
                   for m in EMBARGO_RE.finditer(r.get("embargoed-from", ""))}
        for person in list(known) + list(embargo):
            if person not in entity_ids:
                report.error(f"Knowledge States [{fact}]: '{person}' is not a declared entity")
        for person, learned in known.items():
            if person in embargo and learned < embargo[person]:
                report.error(f"Knowledge States [{fact}]: embargo violation — "
                             f"'{person}' learned at ch{learned} but embargoed until ch{embargo[person]}")


def check_guns(rows, canon_ch, report):
    for r in rows:
        gid, status = r.get("id", "?"), r.get("status", "")
        if not GUN_STATUS_RE.fullmatch(status):
            report.error(f"Open Loops & Guns [{gid}]: invalid status '{status}'")
            continue
        planted_raw = r.get("planted-ch", "0") or "0"
        if not planted_raw.isdigit():
            report.error(f"Open Loops & Guns [{gid}]: planted-ch must be an integer, got '{planted_raw}'")
            continue
        planted = int(planted_raw)
        m = re.match(r"FIRED ch-(\d+)", status)
        if m and int(m.group(1)) < planted:
            report.error(f"Open Loops & Guns [{gid}]: fired at ch{m.group(1)} "
                         f"before planted at ch{planted}")
        must_by = r.get("must-fire-by", "")
        if status == "UNFIRED" and must_by.isdigit() and int(must_by) <= canon_ch:
            report.warn(f"Open Loops & Guns [{gid}]: OVERDUE — must fire by "
                        f"ch{must_by}, canon is at ch{canon_ch}, still UNFIRED")


def check_commit_log(lines, report):
    last = 0
    for line in lines:
        m = LOG_RE.match(line.strip())
        if not m:
            continue
        ch = int(m.group(1))
        if ch <= last:
            report.error(f"Canon Commit Log: chapter regression — ch{ch} after ch{last} "
                         "(entries must be strictly increasing)")
        last = ch


def check_coverage(physics_rows, timeline_rows, canon_ch, report):
    phys = {r.get("ch", "") for r in physics_rows}
    times = {r.get("ch", "") for r in timeline_rows}
    for ch in range(1, canon_ch + 1):
        if str(ch) not in phys:
            report.warn(f"Physics State: no rows for committed ch{ch}")
        if str(ch) not in times:
            report.warn(f"Timeline: no row for committed ch{ch}")


def check_geography(logistics_rows, travel_pairs, report):
    by_key = {}
    for r in logistics_rows:
        loc = r.get("location", "")
        if loc and loc != "-":
            by_key.setdefault((r.get("ch", ""), r.get("entity", "")), set()).add(loc)
    for (ch, entity), locs in sorted(by_key.items()):
        if len(locs) < 2:
            continue
        locs = sorted(locs)
        for i in range(len(locs)):
            for j in range(i + 1, len(locs)):
                if frozenset({locs[i], locs[j]}) not in travel_pairs:
                    report.warn(f"Logistics: '{entity}' is in both '{locs[i]}' and "
                                f"'{locs[j]}' in ch{ch} with no travel edge between them")


ANCHOR_ID_RE = re.compile(r"^\s*-?\s*id:\s*[\"']?([A-Za-z0-9_-]+)", re.MULTILINE)


def load_spe_anchors(spe_dir):
    anchors_dir = Path(spe_dir) / "narrative_state" / "anchors"
    if not anchors_dir.is_dir():
        return None
    found = set()
    for f in anchors_dir.glob("*.yaml"):
        found |= set(ANCHOR_ID_RE.findall(f.read_text(encoding="utf-8")))
    return found


FREEFORM_VECTORS = {"intimacy-ladder", "door-closed"}


def check_anchors(physics_rows, anchors, report):
    if anchors is None:
        if physics_rows:
            report.warn("Physics State: SPE anchor catalog not found — "
                        "anchor values are unvalidated free-form")
        return
    for r in physics_rows:
        if r.get("vector", "") in FREEFORM_VECTORS:
            continue
        a = r.get("anchor", "")
        if a and a not in anchors:
            report.error(f"Physics State: anchor '{a}' not in SPE narrative-state catalog")


def check_ids(rows, section, column, reserved_ids, report):
    seen = set()
    for r in rows:
        rid = r.get(column, "")
        if not rid:
            continue
        if rid in seen:
            report.error(f"{section}: duplicate {column} '{rid}'")
        if not KEBAB.fullmatch(rid):
            report.error(f"{section}: {column} '{rid}' is not kebab-case")
        if rid in reserved_ids:
            report.error(f"{section}: {column} '{rid}' collides with an existing entity id")
        seen.add(rid)


def validate(graph_path, ontology, genres_dir, spe_dir):
    report = Report()
    try:
        text = Path(graph_path).read_text(encoding="utf-8")
    except OSError as e:
        report.error(f"cannot read graph file: {e}")
        return report
    sections, order = parse_sections(text)
    check_structure(sections, order, report)
    fields = parse_header_fields(sections.get("HEADER", []))
    canon_ch = check_header(fields, report)

    declared_raw = fields.get("genre-modules", "none")
    declared = [] if declared_raw.strip() in ("none", "") else \
        [m.strip() for m in declared_raw.split(",") if m.strip()]

    def rows(name):
        return parse_table(sections.get(name, []))[1]

    vocab = load_vocabulary(Path(ontology), Path(genres_dir), declared,
                            rows("Local Vocabulary"), report)
    entity_ids, location_ids = check_entities(rows("Entities"), report)
    check_ids(rows("Knowledge States"), "Knowledge States", "fact-id", entity_ids, report)
    check_ids(rows("Open Loops & Guns"), "Open Loops & Guns", "id", entity_ids, report)
    travel_pairs = check_travel(rows("Locations & Distances"), location_ids, report)
    check_relationships(rows("Relationships"), vocab, entity_ids, report)
    check_knowledge(rows("Knowledge States"), entity_ids, report)
    check_guns(rows("Open Loops & Guns"), canon_ch, report)
    check_logistics(rows("Logistics"), entity_ids, location_ids, report)
    check_ghost(rows("Private Beliefs (Ghost)"), entity_ids, report)
    check_commit_log(sections.get("Canon Commit Log", []), report)
    check_coverage(rows("Physics State"), rows("Timeline"), canon_ch, report)
    check_geography(rows("Logistics"), travel_pairs, report)
    check_anchors(rows("Physics State"), load_spe_anchors(Path(spe_dir)), report)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(prog="story_graph")
    sub = parser.add_subparsers(dest="command", required=True)
    v = sub.add_parser("validate", help="validate a Story-Graph.md")
    v.add_argument("graph")
    v.add_argument("--ontology", default="Blueprints/Story-Graph-Ontology-v1.md")
    v.add_argument("--genres-dir", default="Blueprints/Genres")
    v.add_argument("--spe-dir", default="SPE")
    args = parser.parse_args(argv)

    report = validate(args.graph, args.ontology, args.genres_dir, args.spe_dir)
    for e in report.errors:
        print(f"ERROR: {e}")
    for w in report.warnings:
        print(f"WARN: {w}")
    print(f"RESULT: {len(report.errors)} error(s), {len(report.warnings)} warning(s)")
    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main())
