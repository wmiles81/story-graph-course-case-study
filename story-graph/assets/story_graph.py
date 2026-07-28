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

# SPE module (Physics State): vectors whose anchor is free-form prose, not a
# catalog id; and the pattern for extracting anchor ids from the SPE catalog.
FREEFORM_VECTORS = {"intimacy-ladder", "door-closed"}
ANCHOR_ID_RE = re.compile(r"^\s*-?\s*id:\s*[\"']?([A-Za-z0-9_-]+)", re.MULTILINE)


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


def _alias_cell(row):
    """Surface forms for an entity, as `;`-separated text.

    Prefers an explicit `aliases` column; falls back to the `note` column, which is
    where existing graphs put them. The fallback is guarded because a note is free
    text: `provisional — auto-registered from an assertion reference` splits into
    convincing nonsense, and nonsense aliases produce false collisions, which is worse
    than no checking at all. A segment only counts as an alias if it reads like a name.
    """
    explicit = (row.get("aliases") or "").strip()
    if explicit:
        return [s.strip() for s in explicit.split(";") if s.strip()]
    note = (row.get("note") or "").strip()
    if not note:
        return []
    parts = [s.strip() for s in note.split(";") if s.strip()]
    if any(len(p.split()) > 4 or "—" in p or p.endswith(".") for p in parts):
        return []          # prose, not an alias list
    return parts


def check_aliases(graph, entity_ids, report):
    """Identity resolution, mechanically. Cannot tell you that two names are one
    person — but it CAN tell you the graph has already claimed both readings at once,
    which is the state that silently corrupts everything downstream."""
    claimed = {}
    for r in graph["sections"].get("Entities", []):
        eid = r.get("id", "")
        if not eid:
            continue
        for a in _alias_cell(r):
            key = a.lower()
            if key == eid.lower():
                report.warn(f"Entities [{eid}]: alias '{a}' repeats the canonical id")
                continue
            if key in entity_ids or key.replace(" ", "-") in entity_ids:
                report.error(f"Entities [{eid}]: alias '{a}' is another entity's canonical id — "
                             f"one of them is wrong")
            claimed.setdefault(key, []).append(eid)
    for a, owners in sorted(claimed.items()):
        if len(owners) > 1:
            report.error(f"Entities: alias '{a}' is claimed by {len(owners)} entities "
                         f"({', '.join(sorted(owners))}) — either they are one entity recorded "
                         f"twice, or the alias belongs to only one of them")


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


def quote_found(haystack, needle):
    """Is this quote genuinely on the page?

    Exact substring first, then a whitespace-insensitive retry. A sentence that wraps
    across two lines in the markdown is the SAME sentence — failing it reports a
    fabrication where there is only a line break, which is both wrong and corrosive: a
    checker that cries wolf on formatting gets ignored on content.

    Only runs of whitespace are collapsed. No word, character or mark is ignored, so a
    quote that is not really in the prose still cannot pass.
    """
    needle = (needle or "").strip()
    if not needle:
        return False
    if needle in haystack:
        return True
    # Normalise WITHIN a paragraph, never across one. Collapsing the whole document made
    # a "quote" that jumped a scene break match — "The wolf knew the scent. * * * Rain
    # fell" is not a passage anyone could read on the page. Line wrapping was the only
    # thing that needed tolerating, and it never crosses a blank line.
    want = " ".join(needle.split())
    for block in re.split(r"\n\s*\n", haystack):
        if want in " ".join(block.split()):
            return True
    return False


# A basis quote has to be enough text to identify a passage. Without a floor, `the`
# satisfies the anti-fabrication check on any manuscript ever written — the gate looks
# like it is working and is testing nothing. Kept low enough for real short dialogue:
# "Not now. Not ever." is 18 characters and 4 words, and must still pass.
MIN_QUOTE_CHARS, MIN_QUOTE_WORDS = 12, 3


def quote_is_substantial(quote):
    q = (quote or "").strip()
    return len(q) >= MIN_QUOTE_CHARS and len(q.split()) >= MIN_QUOTE_WORDS


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
        if not quote_found(chapter.read_text(encoding="utf-8"), quote):
            report.error(f"Evidence [{sid}]: quote not found in {chapter.name} — graph-vs-source mismatch")


def check_span_relevance(graph, report):
    """Flag a receipt that shares NO content word with the claim it supposedly backs.

    This cannot tell you a quote proves a claim — that is a reading, and the whole point
    of decisions.md part 3. It can tell you the two are not even about the same thing,
    which is a different and entirely mechanical question.

    Deliberately set at ZERO shared words, not one or two. On this book that fires once;
    at "<= 1 word" it fires six times and starts flagging legitimate short spans. A
    checker that cries wolf gets ignored, and this one is worth listening to: the case it
    catches is "The Deep Stacks distort space and direction" backed by "Margot's
    flashlight cut a narrow cone through it".
    """
    try:
        import story_graph_candidates as sgc
    except ImportError:
        return                                     # candidate tooling absent; skip quietly
    quotes = {r.get("span-id"): (r.get("quote") or "")
              for r in graph["sections"].get("Evidence", []) if r.get("span-id")}
    for r in graph["sections"].get("Propositions", []):
        stmt = r.get("statement", "")
        st = sgc._tokens(stmt)
        if len(st) < 3:
            continue
        for sid in _span_ids(r.get("span", "")):
            q = quotes.get(sid)
            if q and not (st & sgc._tokens(q)):
                report.warn(f"Propositions [{r.get('prop-id')}]: span '{sid}' shares no "
                            f"content word with the claim — check it actually supports it")


def load_spe_anchors(spe_dir):
    """Return the set of anchor ids in <spe_dir>/narrative_state/anchors/*.yaml,
    or None when the catalog directory is absent (checks degrade to warnings)."""
    anchors_dir = Path(spe_dir) / "narrative_state" / "anchors"
    if not anchors_dir.is_dir():
        return None
    found = set()
    for f in anchors_dir.glob("*.yaml"):
        found |= set(ANCHOR_ID_RE.findall(f.read_text(encoding="utf-8")))
    return found


def check_physics(graph, spe_dir, report):
    """SPE module: validate the Physics State rows. `ch` must be an integer; for
    non-free-form vectors the `anchor` must be a catalog anchor id when the SPE
    catalog is available (else the rows are reported as unvalidated free-form)."""
    rows = graph["sections"].get("Physics State", [])
    anchors = load_spe_anchors(spe_dir) if spe_dir else None
    if anchors is None and rows:
        report.warn("Physics State: SPE anchor catalog not found — "
                    "anchor values are unvalidated free-form")
    for r in rows:
        ch = r.get("ch", "")
        if ch and not ch.isdigit():
            report.error(f"Physics State: ch must be an integer, got '{ch}'")
        if anchors is not None and r.get("vector", "") not in FREEFORM_VECTORS:
            a = r.get("anchor", "")
            if a and a not in anchors:
                report.error(f"Physics State: anchor '{a}' not in SPE narrative-state catalog")


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
    check_aliases(graph, entity_ids, report)
    span_ids = check_evidence(graph, sources, report)
    verify_spans(graph, sources, chapters_dir, report)
    prop_ids = check_propositions(graph, sources, span_ids, report)
    check_epistemic(graph, entity_ids, prop_ids, span_ids, report)
    check_open_loops(graph, canon_ch, span_ids, report)
    check_logistics(graph, entity_ids, location_ids, span_ids, report)
    check_span_relevance(graph, report)
    check_commit_log(graph, report)
    if "spe" in graph["modules"]:
        check_physics(graph, spe_dir, report)
    if graph["header"].get("canon-version"):
        prov = unratified(graph)
        if prov:
            report.warn(f"frozen canon '{graph['header']['canon-version']}' still contains "
                        f"{len(prov)} provisional (unratified) row(s)")
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


def query_graph(name, graph_path, target="", chapters_dir=""):
    report = validate(graph_path, chapters_dir=chapters_dir)
    if report.errors:
        return "", report
    try:
        import story_graph_query
    except ImportError:
        report.error("query requires the 'kuzu' package (pip install kuzu)")
        return "", report
    text = Path(graph_path).read_text(encoding="utf-8")
    graph = parse_graph(text)
    out = story_graph_query.run_query(name, graph, canon_ch=graph["canon_ch"], target=target)
    return out, report


def report_graph(graph_path, chapters_dir=""):
    report = validate(graph_path, chapters_dir=chapters_dir)
    if report.errors:
        return "", report
    try:
        import story_graph_query
    except ImportError:
        report.error("report requires the 'kuzu' package (pip install kuzu)")
        return "", report
    graph = parse_graph(Path(graph_path).read_text(encoding="utf-8"))
    return story_graph_query.run_report(graph, canon_ch=graph["canon_ch"]), report


def audit_graph(graph_path, chapters_dir="", adjudicated_path=""):
    report = validate(graph_path, chapters_dir=chapters_dir)
    if report.errors:
        return "", report
    try:
        import story_graph_query
    except ImportError:
        report.error("audit requires the 'kuzu' package (pip install kuzu)")
        return "", report
    graph = parse_graph(Path(graph_path).read_text(encoding="utf-8"))
    adj = set()
    if adjudicated_path and Path(adjudicated_path).is_file():
        adj = {ln.strip() for ln in Path(adjudicated_path).read_text(encoding="utf-8").splitlines()
               if ln.strip() and not ln.startswith("#")}
    out, _issues = story_graph_query.run_audit(graph, graph["canon_ch"], adj)
    return out, report


_VIZ_COLORS = {
    "entity:Character": "#0b7d84", "entity:Object": "#6b7280", "entity:Location": "#8a5cf6",
    "entity:Faction": "#b4531f", "proposition": "#0e7c86", "source": "#94708a",
    "holder": "#1f6f78", "reader": "#5a3fa6", "evidence": "#a94b1c",
}


def _viz_model(graph, prop_id=""):
    """Build (nodes, edges) for a graphical view: a proposition's neighbourhood
    when prop_id is given, else the whole entity/proposition/source graph."""
    S = graph["sections"]
    nodes, edges = {}, []

    def add(nid, kind):
        if nid and nid not in nodes:
            nodes[nid] = kind

    if prop_id:
        prow = next((r for r in S.get("Propositions", []) if r.get("prop-id") == prop_id), None)
        if not prow:
            return nodes, edges
        add(prop_id, "proposition")
        for r in S.get("Epistemic States", []):
            if r.get("prop-id") == prop_id and r.get("holder"):
                h = r["holder"]
                add(h, "reader" if h == "reader" else "holder")
                edges.append((h, prop_id, r.get("mode", "")))
        if prow.get("governing-source"):
            add(prow["governing-source"], "source")
            edges.append((prop_id, prow["governing-source"], "governed-by"))
        for sid in _span_ids(prow.get("span", "")):
            add(sid, "evidence")
            edges.append((sid, prop_id, "supports"))
        return nodes, edges

    for r in S.get("Entities", []):
        if r.get("id"):
            add(r["id"], "entity:" + (r.get("type") or "Entity"))
    for r in S.get("Propositions", []):
        pid = r.get("prop-id")
        if not pid:
            continue
        add(pid, "proposition")
        if r.get("governing-source"):
            add(r["governing-source"], "source")
            edges.append((pid, r["governing-source"], "governed-by"))
    for r in S.get("Relationships", []):
        if r.get("from") and r.get("to"):
            edges.append((r["from"], r["to"], r.get("edge", "")))
    for r in S.get("Epistemic States", []):
        if r.get("prop-id") and r.get("holder"):
            h = r["holder"]
            add(h, "reader" if h == "reader" else "holder")
            edges.append((h, r["prop-id"], r.get("mode", "")))
    return nodes, edges


def _viz_layout(nodes, edges, w=960, h=680, iters=600, seed=7, pad_l=56, pad_r=170, pad_v=48):
    """Fruchterman-Reingold with centering gravity, settled WITHOUT edge-clamping
    (clamping makes nodes hug the border), then scaled/translated to fit the
    viewport with padding — extra on the right so labels don't clip."""
    import math
    import random
    ns = list(nodes)
    if not ns:
        return {}
    rnd = random.Random(seed)
    cx, cy = w / 2, h / 2
    r0 = min(w, h) * 0.32
    pos = {n: [cx + r0 * math.cos(2 * math.pi * i / len(ns)) + rnd.uniform(-6, 6),
               cy + r0 * math.sin(2 * math.pi * i / len(ns)) + rnd.uniform(-6, 6)]
           for i, n in enumerate(ns)}
    k = 0.9 * math.sqrt(w * h / len(ns))
    for it in range(iters):
        disp = {n: [0.0, 0.0] for n in ns}
        for i in range(len(ns)):
            for j in range(i + 1, len(ns)):
                a, b = ns[i], ns[j]
                dx, dy = pos[a][0] - pos[b][0], pos[a][1] - pos[b][1]
                d = math.hypot(dx, dy) or 0.01
                f = k * k / d
                disp[a][0] += dx / d * f; disp[a][1] += dy / d * f
                disp[b][0] -= dx / d * f; disp[b][1] -= dy / d * f
        for u, v, _lab in edges:
            if u not in pos or v not in pos:
                continue
            dx, dy = pos[u][0] - pos[v][0], pos[u][1] - pos[v][1]
            d = math.hypot(dx, dy) or 0.01
            f = d * d / k
            disp[u][0] -= dx / d * f; disp[u][1] -= dy / d * f
            disp[v][0] += dx / d * f; disp[v][1] += dy / d * f
        for n in ns:                      # centering gravity keeps isolated nodes in frame
            disp[n][0] += (cx - pos[n][0]) * 0.03
            disp[n][1] += (cy - pos[n][1]) * 0.03
        t = max(1.5, w * 0.06 * (1 - it / iters))
        for n in ns:
            dl = math.hypot(*disp[n]) or 0.01
            pos[n][0] += disp[n][0] / dl * min(dl, t)
            pos[n][1] += disp[n][1] / dl * min(dl, t)
    xs = [p[0] for p in pos.values()]
    ys = [p[1] for p in pos.values()]
    sx = (w - pad_l - pad_r) / ((max(xs) - min(xs)) or 1)
    sy = (h - 2 * pad_v) / ((max(ys) - min(ys)) or 1)
    s = min(sx, sy)
    ox = pad_l + ((w - pad_l - pad_r) - (max(xs) - min(xs)) * s) / 2
    oy = pad_v + ((h - 2 * pad_v) - (max(ys) - min(ys)) * s) / 2
    for n in pos:
        pos[n][0] = ox + (pos[n][0] - min(xs)) * s
        pos[n][1] = oy + (pos[n][1] - min(ys)) * s
    return pos


def _viz_html(title, nodes, edges, pos, w=960, h=680):
    import html as _html
    show_labels = len(edges) <= 30
    parts = [f'<line x1="{pos[u][0]:.1f}" y1="{pos[u][1]:.1f}" x2="{pos[v][0]:.1f}" '
             f'y2="{pos[v][1]:.1f}" stroke="var(--edge)" stroke-width="1.2"/>'
             for u, v, _lab in edges if u in pos and v in pos]
    if show_labels:
        for u, v, lab in edges:
            if lab and u in pos and v in pos:
                mx, my = (pos[u][0] + pos[v][0]) / 2, (pos[u][1] + pos[v][1]) / 2
                parts.append(f'<text x="{mx:.1f}" y="{my:.1f}" class="elab">{_html.escape(lab)}</text>')
    for nid, kind in nodes.items():
        x, y = pos[nid]
        color = _VIZ_COLORS.get(kind, "#888")
        if x > w * 0.66:
            lbl = f'<text x="{x - 10:.1f}" y="{y + 4:.1f}" class="nlab" text-anchor="end">{_html.escape(nid)}</text>'
        else:
            lbl = f'<text x="{x + 10:.1f}" y="{y + 4:.1f}" class="nlab">{_html.escape(nid)}</text>'
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="{color}"/>{lbl}')
    legend = " ".join(
        f'<span><i style="background:{c}"></i>{_html.escape(k)}</span>'
        for k, c in _VIZ_COLORS.items())
    return f"""<!doctype html><meta charset="utf-8"><title>{_html.escape(title)}</title>
<style>
:root{{--bg:#eef1f5;--ink:#151c26;--edge:#c2ccd6;--panel:#f7f8fb}}
@media(prefers-color-scheme:dark){{:root{{--bg:#0c121a;--ink:#e7edf4;--edge:#2a3a49;--panel:#141c26}}}}
body{{margin:0;background:var(--bg);color:var(--ink);font:14px system-ui,-apple-system,sans-serif}}
header{{padding:14px 18px}} h1{{font-size:1.1rem;margin:0}}
.legend{{display:flex;flex-wrap:wrap;gap:.4rem 1rem;padding:0 18px 10px;font:11px ui-monospace,monospace;color:var(--ink)}}
.legend i{{display:inline-block;width:.7rem;height:.7rem;border-radius:3px;margin-right:.35rem;vertical-align:middle}}
.wrap{{overflow:auto;padding:0 12px 18px}}
svg{{background:var(--panel);border:1px solid var(--edge);border-radius:10px;max-width:100%;height:auto}}
.nlab{{font:10px ui-monospace,monospace;fill:var(--ink)}} .elab{{font:9px ui-monospace,monospace;fill:#8a97a5;text-anchor:middle}}
</style>
<header><h1>{_html.escape(title)}</h1></header>
<div class="legend">{legend}</div>
<div class="wrap"><svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">{''.join(parts)}</svg></div>
"""


def visualize_graph(graph_path, out_path, prop_id=""):
    text = Path(graph_path).read_text(encoding="utf-8")
    graph = parse_graph(text)
    title = text.splitlines()[0].lstrip("# ").strip() if text.strip() else "Story Graph"
    if prop_id:
        title += f" — impact of {prop_id}"
    nodes, edges = _viz_model(graph, prop_id)
    pos = _viz_layout(nodes, edges)
    Path(out_path).write_text(_viz_html(title, nodes, edges, pos), encoding="utf-8")
    return len(nodes), len(edges)


def impact_graph(graph_path, prop_id, chapters_dir=""):
    report = validate(graph_path, chapters_dir=chapters_dir)
    if report.errors:
        return "", report
    try:
        import story_graph_query
    except ImportError:
        report.error("impact requires the 'kuzu' package (pip install kuzu)")
        return "", report
    graph = parse_graph(Path(graph_path).read_text(encoding="utf-8"))
    return story_graph_query.run_impact(graph, prop_id), report


def deviations(graph_path, chapters_dir):
    """Canon claims whose manuscript evidence no longer matches the current prose
    — the graph-vs-source check re-framed as revision drift. Stdlib only."""
    graph = parse_graph(Path(graph_path).read_text(encoding="utf-8"))
    src_type = {r.get("source-id"): r.get("type") for r in graph["sections"].get("Sources", [])}
    span_prop = {}
    for r in graph["sections"].get("Propositions", []):
        for sid in _span_ids(r.get("span", "")):
            span_prop.setdefault(sid, r.get("prop-id", "?"))
    devs = []
    for r in graph["sections"].get("Evidence", []):
        sid, srcid = r.get("span-id", ""), r.get("source-id", "")
        if src_type.get(srcid) != "manuscript":
            continue
        quote = (r.get("quote") or "").strip()
        if not quote:
            continue
        chapter = _resolve_chapter(chapters_dir, r.get("locator", ""))
        if chapter is None:
            devs.append((sid, span_prop.get(sid, "?"), r.get("locator", ""), "chapter file not found"))
        elif not quote_found(chapter.read_text(encoding="utf-8"), quote):
            devs.append((sid, span_prop.get(sid, "?"), chapter.name, "evidence no longer matches the prose"))
    return devs


def coverage_report(graph, title=""):
    """Which layers of the ontology are actually populated, and how deeply.

    A graph can validate cleanly and still be nearly useless: claims recorded but
    nobody's knowledge attached, no entity relationships, no believes-false. This
    is the diagnostic that says so, instead of leaving it to be discovered by
    eyeballing a hairball. Stdlib only.
    """
    S = graph["sections"]
    def rows(name):
        return S.get(name, [])
    n = {name: len(rows(name)) for name in
         ("Sources", "Entities", "Locations & Distances", "Relationships", "Propositions",
          "Epistemic States", "Open Loops & Setups", "Evidence", "Timeline", "Logistics",
          "Local Vocabulary")}
    commits = sum(1 for ln in graph.get("_raw", {}).get("Canon Commit Log", [])
                  if ln.strip().startswith("- "))

    props = [r.get("prop-id") for r in rows("Propositions") if r.get("prop-id")]
    holders_of = {}
    modes = {}
    for r in rows("Epistemic States"):
        pid, h, m = r.get("prop-id"), r.get("holder"), (r.get("mode") or "")
        if pid and h:
            holders_of.setdefault(pid, set()).add(h)
            modes[m] = modes.get(m, 0) + 1
    attached = len(holders_of)
    shared = sum(1 for v in holders_of.values() if len(v) > 1)
    all_holders = {h for v in holders_of.values() for h in v}
    reader_knows = {r.get("prop-id") for r in rows("Epistemic States")
                    if r.get("holder") == "reader" and r.get("mode") == "knows"}
    disbelieved = {r.get("prop-id") for r in rows("Epistemic States")
                   if r.get("mode") == "believes-false"}
    irony = len(reader_knows & disbelieved)

    verified = sum(1 for r in rows("Propositions")
                   if _span_ids(r.get("span", "")) and not is_provisional(r))
    provisional = len(unratified(graph))

    # edge shape: how concentrated is the graph on one node?
    deg = {}
    for r in rows("Propositions"):
        gs = r.get("governing-source")
        if gs:
            deg[gs] = deg.get(gs, 0) + 1
    for r in rows("Epistemic States"):
        for k in (r.get("holder"), r.get("prop-id")):
            if k:
                deg[k] = deg.get(k, 0) + 1
    for r in rows("Relationships"):
        for k in (r.get("from"), r.get("to")):
            if k:
                deg[k] = deg.get(k, 0) + 1
    total_edges = sum(1 for r in rows("Propositions") if r.get("governing-source")) \
        + n["Epistemic States"] + n["Relationships"]
    hub, hub_deg = (max(deg.items(), key=lambda kv: kv[1]) if deg else ("—", 0))

    def pct(a, b):
        return f"{(100 * a // b) if b else 0}%"

    L = [f"COVERAGE — {title or 'story graph'} (canon ch{graph['canon_ch']})",
         "=" * 56, "LAYER POPULATION"]
    for name in ("Sources", "Entities", "Locations & Distances", "Relationships", "Propositions",
                 "Epistemic States", "Open Loops & Setups", "Evidence", "Timeline", "Logistics"):
        mark = "   <- empty" if n[name] == 0 else ""
        L.append(f"  {name:<24}{n[name]:>5}{mark}")
    L.append(f"  {'Canon commits':<24}{commits:>5}")

    L += ["", "EPISTEMIC DEPTH",
          f"  propositions with a holder   {attached:>4}/{len(props)}  ({pct(attached, len(props))})",
          f"  held by 2+ holders (shared)  {shared:>4}",
          f"  distinct holders             {len(all_holders):>4}",
          f"  dramatic irony pairs         {irony:>4}",
          "  modes: " + (", ".join(f"{k}={v}" for k, v in sorted(modes.items())) or "none")]

    L += ["", "EVIDENCE & RATIFICATION",
          f"  source-verified propositions {verified:>4}/{len(props)}  ({pct(verified, len(props))})",
          f"  provisional load-bearing rows{provisional:>5}"]

    L += ["", "SHAPE",
          f"  busiest node  {hub}  {hub_deg} edges of {total_edges} ({pct(hub_deg, total_edges)})"]

    flags = []
    if n["Entities"] >= 5 and n["Relationships"] <= max(2, n["Entities"] // 20):
        flags.append(f"Relationships is effectively empty ({n['Relationships']} edge(s) across "
                     f"{n['Entities']} entities) — entity relationships cannot appear in queries.")
    if props and attached * 100 // len(props) < 50:
        flags.append(f"{100 - (attached * 100 // len(props))}% of propositions have no holder — "
                     "who-knows-what is largely unrecorded.")
    if not disbelieved:
        flags.append("No believes-false states — dramatic irony cannot be derived.")
    if props and verified * 100 // len(props) < 25:
        flags.append(f"Only {pct(verified, len(props))} of propositions cite a verified source span.")
    if total_edges and hub_deg * 100 // total_edges > 60:
        flags.append(f"{pct(hub_deg, total_edges)} of all edges land on one node ({hub}) — the graph "
                     "is hub-dominated, so real structure is hard to see; filter that edge type out.")
    if n["Locations & Distances"] == 0 and n["Entities"]:
        flags.append("No locations/distances — travel-time logistics cannot be checked.")
    if flags:
        L += ["", "FLAGS"]
        L += [f"  ! {f}" for f in flags]
        L += ["  -> populate thin layers with the catch-up mode "
              "(reference/catch-up-from-chapters.md)."]
    else:
        L += ["", "No coverage gaps flagged."]
    return "\n".join(L)


def unratified(graph):
    """Load-bearing rows still marked `provisional` — the ratification queue."""
    out = []
    for sec in ("Propositions", "Epistemic States", "Open Loops & Setups", "Logistics"):
        for r in graph["sections"].get(sec, []):
            if not is_provisional(r):
                continue
            if sec == "Epistemic States":
                lab = f"{r.get('prop-id','?')}/{r.get('holder','?')}"
            elif sec == "Logistics":
                lab = f"ch{r.get('ch','?')}/{r.get('entity','?')}"
            else:
                lab = r.get("prop-id") or r.get("id") or "?"
            out.append((sec, lab))
    return out


def _next_version_path(path):
    """The next free `_v<N>` slot beside a file. The project never overwrites: applying a
    proposal keeps the pre-application graph, so a bad batch is one `mv` from undone."""
    p = Path(path)
    stem = re.sub(r"_v\d+$", "", p.stem)
    n = 1
    while (p.parent / f"{stem}_v{n}{p.suffix}").exists():
        n += 1
    return str(p.parent / f"{stem}_v{n}{p.suffix}")


def blast_radius(graph):
    """Per-proposition dependency weight: what has to be revisited if this claim moves
    or flips. Stdlib; no kuzu.

    Mind the ceiling, because it bounds every use of this: ontology v2 has no
    proposition -> proposition edge, so the walk is ONE HOP and cannot go transitive.
    A claim that quietly underpins another claim scores as weightless here. That gap is
    the reason "load-bearing" can't be computed as a dependency today — see
    reference/decisions.md.
    """
    S = graph["sections"]
    out = {}

    def cell(pid):
        return out.setdefault(pid, {"holders": 0, "evidence": 0, "irony": False, "score": 0})

    for r in S.get("Propositions", []):
        pid = r.get("prop-id")
        if pid:
            cell(pid)["evidence"] += len(_span_ids(r.get("span", "")))
    modes = {}
    for r in S.get("Epistemic States", []):
        pid = r.get("prop-id")
        if not pid:
            continue
        cell(pid)["holders"] += 1
        modes.setdefault(pid, set()).add(r.get("mode") or "")
    for pid, ms in modes.items():
        if "believes-false" in ms and ({"knows", "believes"} & ms):
            cell(pid)["irony"] = True
    for c in out.values():
        # irony is weighted because breaking it is the failure a reader actually feels,
        # and it is the one that no later validation pass will catch for you.
        c["score"] = c["holders"] + c["evidence"] + (3 if c["irony"] else 0)
    return out


def unratified_ranked(graph):
    """The ratification queue as a work plan rather than a list: heaviest first, each
    row saying what rests on it. 149 rows in file order tells you nothing about where
    to start."""
    bl = blast_radius(graph)
    canon = graph.get("canon_ch") or 0
    try:
        canon = int(canon)
    except (TypeError, ValueError):
        canon = 0
    overdue = {}
    for r in graph["sections"].get("Open Loops & Setups", []):
        gid, by = r.get("id"), (r.get("must-fire-by") or "").strip()
        if gid and by.isdigit() and canon and int(by) <= canon:
            overdue[gid] = canon - int(by)

    out = []
    for sec, lab in unratified(graph):
        pid = lab.split("/")[0] if sec == "Epistemic States" else lab
        c = bl.get(pid) or {}
        why = []
        if c.get("holders"):
            why.append(f"{c['holders']} holder{'' if c['holders'] == 1 else 's'}")
        if c.get("evidence"):
            why.append(f"{c['evidence']} span{'' if c['evidence'] == 1 else 's'}")
        if c.get("irony"):
            why.append("dramatic irony")
        score = c.get("score", 0)
        if lab in overdue:
            # An open loop carries obligation weight, not dependency weight. Without this
            # every overdue setup sorts last, which is exactly backwards for a work plan.
            score = max(score, 5 + overdue[lab])
            why.append(f"overdue by {overdue[lab]} ch")
        out.append((sec, lab, score, ", ".join(why) or "nothing depends on it yet"))
    out.sort(key=lambda t: (-t[2], t[0], t[1]))
    return out


def freeze_graph(graph_path, version, out_path, force=False, at=""):
    """Stamp a versioned canon baseline. Validates first; refuses if any
    provisional (unratified) rows remain unless --force. Writes the stamped
    graph to out_path; the source graph is left untouched."""
    report = validate(graph_path)
    if report.errors:
        report.error("refusing to freeze: fix validation ERRORs first")
        return report
    text = Path(graph_path).read_text(encoding="utf-8")
    graph = parse_graph(text)
    prov = unratified(graph)
    if prov and not force:
        report.error(f"refusing to freeze: {len(prov)} unratified (provisional) load-bearing row(s) "
                     "remain — resolve them, or pass --force to freeze with them recorded as unresolved")
        return report
    if not at:
        from datetime import date
        at = date.today().isoformat()
    stamped, done = [], False
    for ln in text.splitlines():
        stamped.append(ln)
        if not done and re.match(r"\|\s*current-canon-chapter\s*\|", ln):
            stamped.append(f"| canon-version | {version} |")
            stamped.append(f"| frozen-at | {at} |")
            done = True
    stamped.append(f"- FROZEN {version} @ {at} (unresolved provisional rows: {len(prov)})")
    Path(out_path).write_text("\n".join(stamped) + "\n", encoding="utf-8")
    report.warn(f"froze '{version}' at {at}; unresolved provisional rows: {len(prov)}")
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
    qp = sub.add_parser("query")
    qp.add_argument("name")
    qp.add_argument("graph")
    qp.add_argument("target", nargs="?", default="")
    qp.add_argument("--chapters-dir", default="")
    rp = sub.add_parser("report")
    rp.add_argument("graph")
    rp.add_argument("--chapters-dir", default="")
    ip = sub.add_parser("import-legacy")
    ip.add_argument("legacy_dir")
    ip.add_argument("--out", required=True)
    ip.add_argument("--report", default="")
    ip.add_argument("--title", default="Imported Legacy Canon")
    ip.add_argument("--quotes", default="")
    ip.add_argument("--chapters-dir", default="")
    cv = sub.add_parser("coverage")
    cv.add_argument("graph")
    qq = sub.add_parser("queue")
    qq.add_argument("graph")
    fz = sub.add_parser("freeze")
    fz.add_argument("graph")
    fz.add_argument("--version", required=True)
    fz.add_argument("--out", required=True)
    fz.add_argument("--force", action="store_true")
    fz.add_argument("--at", default="")
    au = sub.add_parser("audit")
    au.add_argument("graph")
    au.add_argument("--chapters-dir", default="")
    au.add_argument("--adjudicated", default="")
    im = sub.add_parser("impact")
    im.add_argument("graph")
    im.add_argument("prop")
    im.add_argument("--chapters-dir", default="")
    dv = sub.add_parser("deviations")
    dv.add_argument("graph")
    dv.add_argument("--chapters-dir", required=True)
    vz = sub.add_parser("visualize")
    vz.add_argument("graph")
    vz.add_argument("--out", required=True)
    vz.add_argument("--prop", default="")
    pr = sub.add_parser("propose")
    pr.add_argument("kind", choices=["entities", "evidence", "epistemic"])
    pr.add_argument("graph")
    pr.add_argument("--chapters-dir", required=True)
    pr.add_argument("--ask", action="store_true",
                    help="write the question to disk instead of calling a model — the agent "
                         "reading this manuscript answers it in-session")
    pr.add_argument("--answers", default="", help="directory of <kind>-<scope>.answer.json")
    pr.add_argument("--provider", default="", help="only for a headless/batch run")
    pr.add_argument("--model", default="")
    pr.add_argument("--out", default="proposals")
    pr.add_argument("--cache", default="", help="reuse replies across runs (recommended)")
    pr.add_argument("--limit", type=int, default=18, help="claims/candidates per call")
    pr.add_argument("--chapters", default="", help="comma-separated chapter stems, e.g. ch01,ch02")
    pr.add_argument("--env", default="", help=".env holding a provider key")
    vp = sub.add_parser("verify-proposal")
    vp.add_argument("proposal")
    vp.add_argument("--graph", required=True)
    vp.add_argument("--chapters-dir", default="")
    ap = sub.add_parser("apply-proposal")
    ap.add_argument("proposal")
    ap.add_argument("--graph", required=True)
    ap.add_argument("--chapters-dir", default="")
    ap.add_argument("--accept", required=True, help="row numbers (1,3,5), 'pass', or 'all'")
    ur = sub.add_parser("unresolved")
    ur.add_argument("graph")
    ur.add_argument("--chapters-dir", required=True)
    ur.add_argument("--min", type=int, default=2, help="ignore names seen fewer times (default 2)")
    cf = sub.add_parser("conflicts")
    cf.add_argument("graph")
    cf.add_argument("--overlap", type=float, default=0.45, help="content-word similarity floor (default 0.45)")
    dc = sub.add_parser("decisions")
    dc.add_argument("cases", nargs="?", default="")
    dc.add_argument("--provider", default="", help="ollama | lmstudio | openrouter; omit for the structural check only")
    dc.add_argument("--model", default="")
    dc.add_argument("--env", default="", help=".env holding a provider key (default: none)")
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
    if args.command == "query":
        out, report = query_graph(args.name, args.graph, args.target, args.chapters_dir)
        if report.errors:
            for e in report.errors:
                print(f"ERROR: {e}")
            return 1
        print(out)
        return 0
    if args.command == "report":
        out, report = report_graph(args.graph, args.chapters_dir)
        if report.errors:
            for e in report.errors:
                print(f"ERROR: {e}")
            return 1
        print(out)
        return 0
    if args.command == "import-legacy":
        import story_graph_import
        md, coverage, stats = story_graph_import.build(args.legacy_dir, args.title, args.quotes, args.chapters_dir)
        Path(args.out).write_text(md, encoding="utf-8")
        if args.report:
            Path(args.report).write_text(coverage, encoding="utf-8")
        print(f"RESULT: wrote {args.out}; " + ", ".join(f"{k}={v}" for k, v in stats.items()))
        return 0
    if args.command == "coverage":
        text = Path(args.graph).read_text(encoding="utf-8")
        title = text.splitlines()[0].lstrip("# ").strip() if text.strip() else ""
        print(coverage_report(parse_graph(text), title))
        return 0
    if args.command == "propose":
        import story_graph_propose as sgpr
        chat, calls = None, [0]
        if not args.ask and not args.answers:
            # Only a headless run needs an external provider. In an editor the agent
            # reading the manuscript is the strongest judge available and is already here;
            # routing this out to a smaller model over HTTP is a downgrade, not a design.
            import os
            import story_graph_llm as llm
            if not args.provider or not args.model:
                print("ERROR: choose one — --ask (answer it yourself), --answers <dir>, "
                      "or --provider/--model for a headless run")
                return 1
            if args.env:
                llm.load_env(Path(args.env))
            p = llm.provider(args.provider)
            if p is None:
                print(f"ERROR: unknown provider '{args.provider}'")
                return 1
            key = os.environ.get(p["env"], "") if p["env"] else ""
            if not p["local"] and not key:
                print(f"ERROR: {args.provider} needs a key (set {p['env']} or pass --env)")
                return 1

            def chat(system, user):
                calls[0] += 1
                return llm.chat(args.provider, args.model, system, user, max_tokens=12000, key=key)

        mode = "ask" if args.ask else ("answers" if args.answers else
                                       f"{args.model} via {args.provider}")
        print(f"PROPOSE {args.kind} — {mode}")
        written = sgpr.generate(args.kind, args.graph, args.chapters_dir, chat,
                                model=args.model or "agent", provider=args.provider or "in-session",
                                out_dir=args.out, cache_dir=args.cache, limit=args.limit,
                                ask=args.ask, answers_dir=args.answers,
                                chapters=[c for c in args.chapters.split(",") if c.strip()] or None)
        print(f"RESULT: {len(written)} file(s)" + (f", {calls[0]} model call(s)" if chat else ""))
        if args.ask:
            print("Answer each question file and save it beside as <kind>-<scope>.answer.json,\n"
                  f"then: propose {args.kind} <graph> --chapters-dir <d> --answers {args.out}")
        else:
            print("Nothing has touched the graph. Next: verify-proposal, then apply-proposal.")
        return 0
    if args.command in ("verify-proposal", "apply-proposal"):
        import story_graph_proposals as sgp     # lazy: nothing else needs it
        prop = sgp.load(args.proposal)
        prop["_file"] = args.proposal
        verdicts = sgp.verify(prop, args.graph, args.chapters_dir)
        if args.command == "verify-proposal":
            print(sgp.verify_report(verdicts, prop,
                                    parse_graph(Path(args.graph).read_text(encoding='utf-8'))))
            return 1 if any(v == sgp.FAIL for _, v, _ in verdicts) else 0
        ok = {i for i, v, _ in verdicts if v != sgp.FAIL}
        if args.accept == "pass":
            accept = sorted(i for i, v, _ in verdicts if v == sgp.PASS)
        elif args.accept == "all":
            accept = sorted(ok)
            humans = [i for i, v, _ in verdicts if v == sgp.HUMAN]
            if humans:
                # 'all' is a convenience, and convenience is how a review gets skipped.
                # Say plainly what it is taking, since NEEDS-HUMAN is the whole safeguard.
                print(f"NOTE: --accept all is taking {len(humans)} NEEDS-HUMAN row(s) "
                      f"({', '.join(map(str, humans))}) that nobody has reviewed. "
                      f"Use --accept pass, or name the rows, to review them first.")
        else:
            bad_tokens = [x for x in re.split(r"[,\s]+", args.accept) if x.strip()
                          and not re.fullmatch(r"\d+", x.strip())]
            if bad_tokens:
                print(f"ERROR: --accept takes row numbers, 'pass' or 'all'; "
                      f"could not read {', '.join(repr(t) for t in bad_tokens)}")
                return 1
            accept = sorted({int(x) for x in re.split(r"[,\s]+", args.accept) if x.strip()})
            # An out-of-range index would index into the rows list and either explode or,
            # with 0 or a negative, silently apply a DIFFERENT row than the one named.
            n = len(prop["rows"])
            out_of_range = [i for i in accept if i < 1 or i > n]
            if out_of_range:
                print(f"ERROR: row number(s) {out_of_range} are outside this proposal "
                      f"(it has {n} row{'' if n == 1 else 's'}, numbered 1-{n})")
                return 1
        rejected = [i for i in accept if i not in ok]
        if rejected:
            # Applying a row the checker rejected is the one thing this gate exists to
            # prevent; there is deliberately no --force.
            print(f"ERROR: row(s) {rejected} failed verification and cannot be applied")
            return 1
        if not accept:
            print("Nothing accepted; the graph was not touched.")
            return 0
        # An update that ratifies a claim cites an Evidence row proposed alongside it.
        # Accepting the update but rejecting that row — which is exactly what happens when
        # a reviewer rejects bad evidence — would point the claim at a span that does not
        # exist. Verification passed both together, so only apply can catch this.
        provided = {(prop["rows"][i - 1].get("values") or {}).get("span-id")
                    for i in accept if prop["rows"][i - 1].get("section") == "Evidence"}
        graph_now = parse_graph(Path(args.graph).read_text(encoding="utf-8"))
        declared = {r.get("span-id") for r in graph_now["sections"].get("Evidence", [])}
        orphaned = []
        for i in accept:
            row = prop["rows"][i - 1]
            if (row.get("op") or "add") != "set":
                continue
            for s in _span_ids((row.get("set") or {}).get("span", "")):
                if s not in provided and s not in declared:
                    orphaned.append((i, s))
        if orphaned:
            for i, s in orphaned:
                print(f"ERROR: row {i} cites span '{s}', which is neither in the graph nor "
                      f"among the rows you accepted — accept the Evidence row too, or drop this one")
            return 1
        text = Path(args.graph).read_text(encoding="utf-8")
        merged = sgp.apply_rows(text, prop, accept, parse_graph(text))
        merged = sgp.append_commit(merged, sgp.commit_line(prop, verdicts, accept))
        # Validate the RESULT before it becomes the user's file. Writing first and
        # checking afterwards left a broken graph on disk whenever the merge went wrong,
        # and told them so only after the damage. The user's canonical record is the one
        # file in this project that must never be worse for having run a command.
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            probe = Path(td) / Path(args.graph).name
            probe.write_text(merged, encoding="utf-8")
            rep = validate(str(probe), chapters_dir=args.chapters_dir)
        if rep.errors:
            print(f"ERROR: the result would not validate — {args.graph} is unchanged.")
            for e in rep.errors[:5]:
                print(f"  {e}")
            return 1
        prior = _next_version_path(args.graph)
        Path(prior).write_text(text, encoding="utf-8")   # never overwrite: keep the old one
        Path(args.graph).write_text(merged, encoding="utf-8")
        print(f"RESULT: applied {len(accept)} row(s) to {args.graph}; previous version kept at "
              f"{Path(prior).name}; validate reports 0 error(s)")
        return 0
    if args.command in ("unresolved", "conflicts"):
        import story_graph_candidates as sgc     # lazy: nothing else needs it
        graph = parse_graph(Path(args.graph).read_text(encoding="utf-8"))
        if args.command == "unresolved":
            rows = sgc.unresolved(graph, args.chapters_dir, _alias_cell, args.min)
            print(sgc.unresolved_report(rows, args.min))
        else:
            same, cross, undated = sgc.conflicts(graph, args.overlap)
            props = [r for r in graph["sections"].get("Propositions", []) if r.get("prop-id")]
            print(sgc.conflicts_report(same, cross, undated,
                                       dated=len(sgc._prop_chapter(graph)), total=len(props)))
        return 0
    if args.command == "decisions":
        import story_graph_decisions as sgd     # lazy: nothing else needs it
        cases = args.cases or str(Path(__file__).resolve().parent.parent / "tests" / "decisions")
        chat = None
        if args.provider:
            if not args.model:
                print("ERROR: --provider needs --model")
                return 1
            import story_graph_llm as llm
            if args.env:
                llm.load_env(Path(args.env))
            import os
            p = llm.provider(args.provider)
            if p is None:
                print(f"ERROR: unknown provider '{args.provider}'")
                return 1
            key = os.environ.get(p["env"], "") if p["env"] else ""

            def chat(system, user):
                return llm.chat(args.provider, args.model, system, user, key=key)
        text, (pts, tot) = sgd.run(cases, chat)
        print(text)
        # A structural problem fails the build; a low score is information, not an error —
        # the corpus exists to be scored against, including badly.
        return 1 if "STRUCTURE — " in text and "problem" in text else 0
    if args.command == "queue":
        graph = parse_graph(Path(args.graph).read_text(encoding="utf-8"))
        rows = unratified_ranked(graph)
        if not rows:
            print("Ratification queue empty — no provisional load-bearing rows.")
            return 0
        print(f"Ratification queue — {len(rows)} unratified (provisional) row(s), heaviest first:")
        for sec, lab, score, why in rows:
            print(f"  [{score:>3}] [{sec}] {lab} — {why}")
        print("\nWeight is a ONE-HOP count (holders + spans, +3 for irony, or how overdue a setup is).\n"
              "Ontology v2 has no proposition->proposition edge, so a claim that silently\n"
              "underpins another claim scores 0 here. See reference/decisions.md.")
        return 0
    if args.command == "freeze":
        report = freeze_graph(args.graph, args.version, args.out, args.force, args.at)
        for e in report.errors:
            print(f"ERROR: {e}")
        for w in report.warnings:
            print(f"WARN: {w}")
        print(f"RESULT: {'frozen -> ' + args.out if not report.errors else 'not frozen'}; "
              f"{len(report.errors)} error(s)")
        return 1 if report.errors else 0
    if args.command == "audit":
        out, report = audit_graph(args.graph, args.chapters_dir, args.adjudicated)
        if report.errors:
            for e in report.errors:
                print(f"ERROR: {e}")
            return 1
        print(out)
        return 0
    if args.command == "impact":
        out, report = impact_graph(args.graph, args.prop, args.chapters_dir)
        if report.errors:
            for e in report.errors:
                print(f"ERROR: {e}")
            return 1
        print(out)
        return 0
    if args.command == "deviations":
        devs = deviations(args.graph, args.chapters_dir)
        if not devs:
            print("No deviations — all manuscript evidence still matches the prose.")
            return 0
        print(f"DEVIATIONS — {len(devs)} canon claim(s) drifted from the current manuscript:")
        for sid, prop, loc, reason in devs:
            print(f"  [{loc}] {sid} (supports '{prop}') — {reason}")
        return 1
    if args.command == "visualize":
        n, e = visualize_graph(args.graph, args.out, args.prop)
        print(f"RESULT: wrote {args.out}; {n} node(s), {e} edge(s)")
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
