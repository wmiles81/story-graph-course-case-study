# Story Graph Foundation Slice Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Evolve the `story-graph` skill's validator to ontology v2 (genre-neutral core + optional SPE module, authority + epistemic model, manuscript-verified evidence spans) and add a Kùzu compiler that materializes the text graph into a property graph.

**Architecture:** One stdlib CLI file `assets/story_graph.py` holds the parser, the `validate` command, and the `compile` entry point. The Kùzu loader lives in a separate `assets/story_graph_kuzu.py` imported lazily only by `compile`, so `validate` and parsing never touch a third-party dependency. The authored `Story-Graph.md` stays the source of truth; the Kùzu database is a derived, rebuildable projection.

**Tech Stack:** Python 3.10 (stdlib only for parse/validate), pytest (dev/test), Kùzu (optional, `compile` only), Markdown graph + schema docs.

## Global Constraints

- **Runtime stdlib-only for parse + validate.** `assets/story_graph.py` imports only the standard library at module top level. `import kuzu` appears **only inside** the `compile` code path (lazy import), never at module top and never in `validate`.
- **Versioning rule (repo owner, unconditional).** Never overwrite. Fixed-call-chain files use *shift-rename*: move current content to its `_v1`/`-v1` slot, then write new content at the unsuffixed name (`story_graph.py`, `SKILL.md`, `reference/*.md`). Schema docs use *side-by-side*: `Story-Graph-Ontology-v2.md`, `Story-Graph-TEMPLATE-v2.md` live beside the v1 files, which are left untouched.
- **Exit codes:** `validate`/`compile` exit `0` when no ERRORs, `1` when any ERROR. Warnings never change the exit code. Print `ERROR: …` / `WARN: …` lines then a `RESULT: N error(s), M warning(s)` line.
- **Core section set (exact, in order):** `Local Vocabulary, Sources, Entities, Locations & Distances, Relationships, Propositions, Epistemic States, Open Loops & Setups, Evidence, Timeline, Logistics, Canon Commit Log`.
- **Module sections:** `spe` → `Physics State` (required only when `spe` is declared in the header `modules` field).
- **Controlled vocabularies:** source `type ∈ {manuscript, bible, outline, editorial, draft, ghost-draft}`; proposition `canon-status ∈ {true, false, undetermined, contested}`; epistemic `mode ∈ {knows, believes, believes-false, suspects, embargoed-until}`; setup `status` matches `^(UNFIRED|FIRED ch-\d+|DEFUSED ch-\d+)$`. Reserved epistemic holder id: `reader`.
- **All ids kebab-case**, unique across Entities / prop-ids / span-ids / setup ids.
- **Proving manuscript:** `series/books/book-3/phase-7-drafting/chapters/chNN.md` (`## Chapter N` headings).
- **Dev setup:** `pip install pytest` for tests; `pip install kuzu` for the compiler tasks. Tests that need Kùzu use `pytest.importorskip("kuzu")` and are skipped when it is absent.

---

## File Structure

- `story-graph/assets/story_graph_v1.py` — the current validator, preserved verbatim (created by renaming).
- `story-graph/assets/story_graph.py` — the v2 CLI: parser, `validate`, `compile` entry. Stdlib only at top level.
- `story-graph/assets/story_graph_kuzu.py` — Kùzu loader; `import kuzu` lives here.
- `story-graph/assets/Story-Graph-Ontology-v2.md` — v2 schema (side-by-side with v1).
- `story-graph/assets/Story-Graph-TEMPLATE-v2.md` — v2 blank graph (side-by-side).
- `story-graph/SKILL_v1.md` — preserved v1 skill prose (rename).
- `story-graph/SKILL.md` — v2 skill prose (new content at fixed name).
- `story-graph/tests/conftest.py` — pytest path setup + the `MINIMAL_V2` fixture.
- `story-graph/tests/test_structure.py`, `test_sources.py`, `test_propositions.py`, `test_epistemic.py`, `test_evidence.py`, `test_spans_source.py`, `test_openloops_logistics.py`, `test_cli.py`, `test_compile.py` — one test module per validator concern.
- `series/books/book-3/Story-Graph.md` — the Book-3 proof graph (created in Task 12).

The shared parsed representation every task consumes:

```python
# Graph is a plain dict:
# {
#   "header": {field: value, ...},          # from the header table
#   "modules": ["spe", ...],                # parsed from header "modules"
#   "canon_ch": int,                        # header current-canon-chapter
#   "sections": {"Entities": [rowdict, ...], ...},  # name -> list of row dicts
#   "order": ["Local Vocabulary", ...],     # section order as written
# }
```

---

### Task 1: Shift-rename to v2 + structure/header/modules checks

**Files:**
- Rename: `story-graph/assets/story_graph.py` → `story-graph/assets/story_graph_v1.py`
- Create: `story-graph/assets/story_graph.py`
- Create: `story-graph/tests/conftest.py`
- Test: `story-graph/tests/test_structure.py`

**Interfaces:**
- Produces: `parse_sections(text) -> (dict, list)`, `parse_table(lines) -> (list, list)`, `parse_header_fields(lines) -> dict`, `parse_graph(text) -> dict` (the Graph shape above), `class Report` with `.error(str)`, `.warn(str)`, `.errors`, `.warnings`, `KEBAB` regex, `CORE_SECTIONS`, `MODULE_SECTIONS`, `check_structure(graph, report)`, `check_header(graph, report) -> int`.

- [ ] **Step 1: Preserve v1 by renaming**

```bash
cd story-graph/assets
git mv story_graph.py story_graph_v1.py
```

- [ ] **Step 2: Create the test harness**

Create `story-graph/tests/conftest.py`:

```python
import sys
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets"
sys.path.insert(0, str(ASSETS))

MINIMAL_V2 = """# Story Graph: Test

| field | value |
|---|---|
| ontology-version | 2 |
| modules | none |
| current-canon-chapter | 0 |

## Local Vocabulary
| edge | description |
|---|---|

## Sources
| source-id | type | authority | note |
|---|---|---|---|
| ms | manuscript | 100 | governing manuscript |

## Entities
| id | type | status | voice | note |
|---|---|---|---|---|
| jonah | Character | active | male | |
| library | Location | active | - | |

## Locations & Distances
| from | to | time | mode |
|---|---|---|---|

## Relationships
| from | edge | to | trend | since-ch | span | note |
|---|---|---|---|---|---|---|

## Propositions
| prop-id | statement | canon-status | governing-source | span |
|---|---|---|---|---|

## Epistemic States
| prop-id | holder | mode | since-ch | span |
|---|---|---|---|---|

## Open Loops & Setups
| id | planted-ch | expectation | must-fire-by | status | span |
|---|---|---|---|---|---|

## Evidence
| span-id | source-id | locator | quote | note |
|---|---|---|---|---|

## Timeline
| ch | story-time | elapsed | note |
|---|---|---|---|

## Logistics
| ch | entity | location | condition | span | note |
|---|---|---|---|---|---|

## Canon Commit Log
"""


def make_graph(**replacements):
    """Return MINIMAL_V2 with whole-section bodies replaced.
    replacements: section_name -> the full markdown for that section (incl. header)."""
    text = MINIMAL_V2
    for name, body in replacements.items():
        import re
        pattern = re.compile(r"(## " + re.escape(name) + r"\n).*?(?=\n## |\Z)", re.S)
        text = pattern.sub(body.rstrip() + "\n", text)
    return text
```

- [ ] **Step 3: Write the failing test**

Create `story-graph/tests/test_structure.py`:

```python
from conftest import MINIMAL_V2, make_graph
import story_graph as sg


def run(text):
    graph = sg.parse_graph(text)
    report = sg.Report()
    sg.check_structure(graph, report)
    sg.check_header(graph, report)
    return report


def test_minimal_graph_has_clean_structure():
    report = run(MINIMAL_V2)
    assert report.errors == []


def test_missing_core_section_is_error():
    text = MINIMAL_V2.replace("## Evidence\n| span-id | source-id | locator | quote | note |\n|---|---|---|---|---|\n", "")
    report = run(text)
    assert any("Evidence" in e for e in report.errors)


def test_header_requires_ontology_version_two():
    text = MINIMAL_V2.replace("| ontology-version | 2 |", "| ontology-version | 1 |")
    report = run(text)
    assert any("ontology-version" in e for e in report.errors)
```

- [ ] **Step 4: Run the test to verify it fails**

Run: `cd story-graph && python3 -m pytest tests/test_structure.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'story_graph'` (file not created yet).

- [ ] **Step 5: Implement the v2 module skeleton**

Create `story-graph/assets/story_graph.py`:

```python
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
```

Also add a temporary `validate` stub so `main` imports cleanly (it is filled in Task 8):

```python
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
```

- [ ] **Step 6: Run the test to verify it passes**

Run: `cd story-graph && python3 -m pytest tests/test_structure.py -v`
Expected: 3 passed.

- [ ] **Step 7: Commit**

```bash
git add story-graph/assets/story_graph_v1.py story-graph/assets/story_graph.py story-graph/tests/conftest.py story-graph/tests/test_structure.py
git commit -m "feat(story-graph): v2 validator skeleton — structure, header, modules"
```

---

### Task 2: Sources registry + authority checks

**Files:**
- Modify: `story-graph/assets/story_graph.py`
- Test: `story-graph/tests/test_sources.py`

**Interfaces:**
- Consumes: `parse_graph`, `Report`, `KEBAB`, `SOURCE_TYPES`.
- Produces: `check_sources(graph, report) -> dict` returning `{source_id: {"type": str, "authority": int}}`; `check_authority(graph, sources, report)` (governing-source resolution, editorial bar, inversion WARN). These are called by `validate` in Task 8.

- [ ] **Step 1: Write the failing test**

Create `story-graph/tests/test_sources.py`:

```python
from conftest import make_graph
import story_graph as sg


def sources_report(body):
    graph = sg.parse_graph(make_graph(**{"Sources": body}))
    report = sg.Report()
    sg.check_sources(graph, report)
    return report


def test_valid_source_ok():
    body = ("## Sources\n| source-id | type | authority | note |\n|---|---|---|---|\n"
            "| ms | manuscript | 100 | |\n")
    assert sources_report(body).errors == []


def test_unknown_type_is_error():
    body = ("## Sources\n| source-id | type | authority | note |\n|---|---|---|---|\n"
            "| ms | screenplay | 100 | |\n")
    assert any("screenplay" in e for e in sources_report(body).errors)


def test_non_integer_authority_is_error():
    body = ("## Sources\n| source-id | type | authority | note |\n|---|---|---|---|\n"
            "| ms | manuscript | high | |\n")
    assert any("authority" in e for e in sources_report(body).errors)


def test_editorial_cannot_be_governing_source():
    props = ("## Propositions\n| prop-id | statement | canon-status | governing-source | span |\n"
             "|---|---|---|---|---|\n| p1 | x | true | ed | s1 |\n")
    srcs = ("## Sources\n| source-id | type | authority | note |\n|---|---|---|---|\n"
            "| ed | editorial | 10 | |\n")
    graph = sg.parse_graph(make_graph(Sources=srcs, Propositions=props))
    report = sg.Report()
    sources = sg.check_sources(graph, report)
    sg.check_authority(graph, sources, report)
    assert any("editorial" in e and "governing" in e for e in report.errors)
```

- [ ] **Step 2: Run to verify failure**

Run: `cd story-graph && python3 -m pytest tests/test_sources.py -v`
Expected: FAIL with `AttributeError: module 'story_graph' has no attribute 'check_sources'`.

- [ ] **Step 3: Implement the checks**

Add to `story_graph.py`:

```python
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
```

- [ ] **Step 4: Run to verify pass**

Run: `cd story-graph && python3 -m pytest tests/test_sources.py -v`
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add story-graph/assets/story_graph.py story-graph/tests/test_sources.py
git commit -m "feat(story-graph): Sources registry + authority checks"
```

---

### Task 3: Propositions

**Files:**
- Modify: `story-graph/assets/story_graph.py`
- Test: `story-graph/tests/test_propositions.py`

**Interfaces:**
- Consumes: `parse_graph`, `Report`, `KEBAB`, `CANON_STATUS`, `is_provisional`.
- Produces: `is_provisional(row) -> bool`; `check_propositions(graph, sources, span_ids, report) -> set` (returns prop-id set). Called by `validate` in Task 8 after `check_sources` and `check_evidence`.

- [ ] **Step 1: Write the failing test**

Create `story-graph/tests/test_propositions.py`:

```python
from conftest import make_graph
import story_graph as sg


def prop_report(body, span_ids=frozenset({"s1"})):
    graph = sg.parse_graph(make_graph(Propositions=body))
    report = sg.Report()
    sources = {"ms": {"type": "manuscript", "authority": 100}}
    sg.check_propositions(graph, sources, set(span_ids), report)
    return report


def test_true_prop_needs_span():
    body = ("## Propositions\n| prop-id | statement | canon-status | governing-source | span |\n"
            "|---|---|---|---|---|\n| jackson-alive | Jackson lives | true | ms |  |\n")
    assert any("span" in e for e in prop_report(body).errors)


def test_true_prop_with_span_ok():
    body = ("## Propositions\n| prop-id | statement | canon-status | governing-source | span |\n"
            "|---|---|---|---|---|\n| jackson-alive | Jackson lives | true | ms | s1 |\n")
    assert prop_report(body).errors == []


def test_bad_canon_status_is_error():
    body = ("## Propositions\n| prop-id | statement | canon-status | governing-source | span |\n"
            "|---|---|---|---|---|\n| p1 | x | maybe | ms | s1 |\n")
    assert any("canon-status" in e for e in prop_report(body).errors)


def test_provisional_true_prop_without_span_warns_not_errors():
    body = ("## Propositions\n| prop-id | statement | canon-status | governing-source | span |\n"
            "|---|---|---|---|---|\n| p1 | x | true | ms | provisional |\n")
    r = prop_report(body)
    assert r.errors == [] and any("provisional" in w for w in r.warnings)
```

- [ ] **Step 2: Run to verify failure**

Run: `cd story-graph && python3 -m pytest tests/test_propositions.py -v`
Expected: FAIL — `check_propositions` / `is_provisional` undefined.

- [ ] **Step 3: Implement**

Add to `story_graph.py`:

```python
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
```

- [ ] **Step 4: Run to verify pass**

Run: `cd story-graph && python3 -m pytest tests/test_propositions.py -v`
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add story-graph/assets/story_graph.py story-graph/tests/test_propositions.py
git commit -m "feat(story-graph): Propositions — ids, canon-status, span-required, provisional"
```

---

### Task 4: Epistemic States

**Files:**
- Modify: `story-graph/assets/story_graph.py`
- Test: `story-graph/tests/test_epistemic.py`

**Interfaces:**
- Consumes: `EPISTEMIC_MODES`, `RESERVED_HOLDERS`, `_check_span_required`, `_span_ids`.
- Produces: `check_epistemic(graph, entity_ids, prop_ids, span_ids, report)`.

- [ ] **Step 1: Write the failing test**

Create `story-graph/tests/test_epistemic.py`:

```python
from conftest import make_graph
import story_graph as sg


def epi_report(body, entity_ids=frozenset({"jonah", "margot"}),
               prop_ids=frozenset({"jackson-alive"}), span_ids=frozenset({"s1"})):
    graph = sg.parse_graph(make_graph(**{"Epistemic States": body}))
    report = sg.Report()
    sg.check_epistemic(graph, set(entity_ids), set(prop_ids), set(span_ids), report)
    return report


HEAD = ("## Epistemic States\n| prop-id | holder | mode | since-ch | span |\n"
        "|---|---|---|---|---|\n")


def test_reader_is_valid_holder():
    body = HEAD + "| jackson-alive | reader | knows | 3 | s1 |\n"
    assert epi_report(body).errors == []


def test_unknown_holder_is_error():
    body = HEAD + "| jackson-alive | ghost | knows | 3 | s1 |\n"
    assert any("ghost" in e for e in epi_report(body).errors)


def test_bad_mode_is_error():
    body = HEAD + "| jackson-alive | jonah | assumes | 3 | s1 |\n"
    assert any("assumes" in e for e in epi_report(body).errors)


def test_knows_needs_span():
    body = HEAD + "| jackson-alive | jonah | knows | 3 |  |\n"
    assert any("span" in e for e in epi_report(body).errors)


def test_embargo_carried_forward():
    body = (HEAD
            + "| jackson-alive | margot | embargoed-until | 11 |  |\n"
            + "| jackson-alive | margot | knows | 5 | s1 |\n")
    assert any("embargo" in e.lower() for e in epi_report(body).errors)


def test_unknown_proposition_is_error():
    body = HEAD + "| nonexistent-prop | jonah | knows | 3 | s1 |\n"
    assert any("nonexistent-prop" in e for e in epi_report(body).errors)
```

- [ ] **Step 2: Run to verify failure**

Run: `cd story-graph && python3 -m pytest tests/test_epistemic.py -v`
Expected: FAIL — `check_epistemic` undefined.

- [ ] **Step 3: Implement**

Add to `story_graph.py`:

```python
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
```

- [ ] **Step 4: Run to verify pass**

Run: `cd story-graph && python3 -m pytest tests/test_epistemic.py -v`
Expected: 6 passed.

- [ ] **Step 5: Commit**

```bash
git add story-graph/assets/story_graph.py story-graph/tests/test_epistemic.py
git commit -m "feat(story-graph): Epistemic States — holder/reader, mode, embargo, span"
```

---

### Task 5: Evidence section + span-id registry

**Files:**
- Modify: `story-graph/assets/story_graph.py`
- Test: `story-graph/tests/test_evidence.py`

**Interfaces:**
- Consumes: `KEBAB`, `Report`.
- Produces: `check_evidence(graph, sources, report) -> set` (returns the set of declared span-ids; validates each span references a real source and has a locator+quote for manuscript sources).

- [ ] **Step 1: Write the failing test**

Create `story-graph/tests/test_evidence.py`:

```python
from conftest import make_graph
import story_graph as sg


def ev_report(body, sources=None):
    sources = sources or {"ms": {"type": "manuscript", "authority": 100}}
    graph = sg.parse_graph(make_graph(Evidence=body))
    report = sg.Report()
    span_ids = sg.check_evidence(graph, sources, report)
    return span_ids, report


HEAD = ("## Evidence\n| span-id | source-id | locator | quote | note |\n"
        "|---|---|---|---|---|\n")


def test_valid_span_registered():
    body = HEAD + '| s1 | ms | ch3 | Jackson was alive | |\n'
    span_ids, report = ev_report(body)
    assert "s1" in span_ids and report.errors == []


def test_span_with_unknown_source_is_error():
    body = HEAD + '| s1 | nope | ch3 | text | |\n'
    _, report = ev_report(body)
    assert any("nope" in e for e in report.errors)


def test_manuscript_span_without_quote_is_error():
    body = HEAD + '| s1 | ms | ch3 |  | |\n'
    _, report = ev_report(body)
    assert any("quote" in e for e in report.errors)


def test_duplicate_span_id_is_error():
    body = HEAD + '| s1 | ms | ch3 | a | |\n| s1 | ms | ch4 | b | |\n'
    _, report = ev_report(body)
    assert any("duplicate" in e for e in report.errors)
```

- [ ] **Step 2: Run to verify failure**

Run: `cd story-graph && python3 -m pytest tests/test_evidence.py -v`
Expected: FAIL — `check_evidence` undefined.

- [ ] **Step 3: Implement**

Add to `story_graph.py`:

```python
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
```

- [ ] **Step 4: Run to verify pass**

Run: `cd story-graph && python3 -m pytest tests/test_evidence.py -v`
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add story-graph/assets/story_graph.py story-graph/tests/test_evidence.py
git commit -m "feat(story-graph): Evidence section + span-id registry"
```

---

### Task 6: Graph-vs-source verification (`--chapters-dir`)

**Files:**
- Modify: `story-graph/assets/story_graph.py`
- Test: `story-graph/tests/test_spans_source.py`

**Interfaces:**
- Consumes: `sources`, `Report`.
- Produces: `verify_spans(graph, sources, chapters_dir, report)` — for each Evidence row whose source is `manuscript`, resolve `locator` to `<chapters_dir>/<locator>.md` (also try zero-padded 2-digit), assert the quote is a substring → ERROR if absent; if `chapters_dir` is empty/missing, WARN-degrade instead.

- [ ] **Step 1: Write the failing test**

Create `story-graph/tests/test_spans_source.py`:

```python
from conftest import make_graph
import story_graph as sg


def setup_chapters(tmp_path):
    (tmp_path / "ch03.md").write_text("## Chapter 3\n\nJackson was alive after all.\n", encoding="utf-8")
    return str(tmp_path)


def verify(body, chapters_dir):
    sources = {"ms": {"type": "manuscript", "authority": 100}}
    graph = sg.parse_graph(make_graph(Evidence=body))
    report = sg.Report()
    sg.verify_spans(graph, sources, chapters_dir, report)
    return report


HEAD = ("## Evidence\n| span-id | source-id | locator | quote | note |\n"
        "|---|---|---|---|---|\n")


def test_quote_present_passes(tmp_path):
    d = setup_chapters(tmp_path)
    body = HEAD + "| s1 | ms | ch3 | Jackson was alive | |\n"
    assert verify(body, d).errors == []


def test_quote_absent_errors(tmp_path):
    d = setup_chapters(tmp_path)
    body = HEAD + "| s1 | ms | ch3 | Jackson was murdered | |\n"
    assert any("s1" in e and "not found" in e.lower() for e in verify(body, d).errors)


def test_no_chapters_dir_warns_not_errors(tmp_path):
    body = HEAD + "| s1 | ms | ch3 | anything | |\n"
    r = verify(body, "")
    assert r.errors == [] and any("could not verify" in w.lower() for w in r.warnings)
```

- [ ] **Step 2: Run to verify failure**

Run: `cd story-graph && python3 -m pytest tests/test_spans_source.py -v`
Expected: FAIL — `verify_spans` undefined.

- [ ] **Step 3: Implement**

Add to `story_graph.py`:

```python
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
```

- [ ] **Step 4: Run to verify pass**

Run: `cd story-graph && python3 -m pytest tests/test_spans_source.py -v`
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add story-graph/assets/story_graph.py story-graph/tests/test_spans_source.py
git commit -m "feat(story-graph): graph-vs-source span verification with chapters-dir"
```

---

### Task 7: Open Loops & Setups, Entities, Logistics, and carried-over checks

**Files:**
- Modify: `story-graph/assets/story_graph.py`
- Test: `story-graph/tests/test_openloops_logistics.py`

**Interfaces:**
- Consumes: `SETUP_STATUS_RE`, `ENTITY_TYPES`, `TRENDS`, `_check_span_required`.
- Produces: `check_entities(graph, report) -> (set, set)` (entity_ids, location_ids); `check_open_loops(graph, canon_ch, span_ids, report)`; `check_logistics(graph, entity_ids, location_ids, span_ids, report)`; `check_commit_log(graph, report)`.

- [ ] **Step 1: Write the failing test**

Create `story-graph/tests/test_openloops_logistics.py`:

```python
from conftest import make_graph
import story_graph as sg


def test_entities_typed_and_kebab():
    body = ("## Entities\n| id | type | status | voice | note |\n|---|---|---|---|---|\n"
            "| Bad_Id | Character | active | male | |\n| ok | Sprite | active | - | |\n")
    graph = sg.parse_graph(make_graph(Entities=body))
    report = sg.Report()
    sg.check_entities(graph, report)
    assert any("kebab" in e for e in report.errors)
    assert any("Sprite" in e for e in report.errors)


def test_setup_status_regex():
    body = ("## Open Loops & Setups\n| id | planted-ch | expectation | must-fire-by | status | span |\n"
            "|---|---|---|---|---|---|\n| pistol | 2 | fired later | 20 | LOADED | s1 |\n")
    graph = sg.parse_graph(make_graph(**{"Open Loops & Setups": body}))
    report = sg.Report()
    sg.check_open_loops(graph, 5, {"s1"}, report)
    assert any("LOADED" in e for e in report.errors)


def test_overdue_setup_warns():
    body = ("## Open Loops & Setups\n| id | planted-ch | expectation | must-fire-by | status | span |\n"
            "|---|---|---|---|---|---|\n| pistol | 2 | must fire | 4 | UNFIRED | s1 |\n")
    graph = sg.parse_graph(make_graph(**{"Open Loops & Setups": body}))
    report = sg.Report()
    sg.check_open_loops(graph, 5, {"s1"}, report)
    assert any("OVERDUE" in w for w in report.warnings)


def test_commit_log_monotonic():
    body = "## Canon Commit Log\n- ch 3: a\n- ch 2: b\n"
    graph = sg.parse_graph(make_graph(**{"Canon Commit Log": body}))
    report = sg.Report()
    sg.check_commit_log(graph, report)
    assert any("regression" in e for e in report.errors)
```

- [ ] **Step 2: Run to verify failure**

Run: `cd story-graph && python3 -m pytest tests/test_openloops_logistics.py -v`
Expected: FAIL — functions undefined.

- [ ] **Step 3: Implement**

Add to `story_graph.py`:

```python
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
```

Add the raw-lines helper (the commit log is prose, not a table) near `parse_graph`:

```python
def _raw_section_lines(graph, name):
    return graph.get("_raw", {}).get(name, [])
```

And capture raw section lines in `parse_graph` by adding, before the return:

```python
    graph_raw = {name: sections.get(name, []) for name in order}
```

then include `"_raw": graph_raw` in the returned dict.

- [ ] **Step 4: Run to verify pass**

Run: `cd story-graph && python3 -m pytest tests/test_openloops_logistics.py -v`
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add story-graph/assets/story_graph.py story-graph/tests/test_openloops_logistics.py
git commit -m "feat(story-graph): entities, setups (renamed), logistics spans, commit log"
```

---

### Task 8: Wire the full `validate` orchestrator + end-to-end CLI test

**Files:**
- Modify: `story-graph/assets/story_graph.py` (replace the Task 1 `validate` stub)
- Test: `story-graph/tests/test_cli.py`

**Interfaces:**
- Consumes: every `check_*` and `verify_spans` above.
- Produces: final `validate(graph_path, ontology, genres_dir, spe_dir, chapters_dir) -> Report`; unchanged `main` CLI from Task 1.

- [ ] **Step 1: Write the failing test**

Create `story-graph/tests/test_cli.py`:

```python
import subprocess, sys
from pathlib import Path
from conftest import MINIMAL_V2, make_graph
import story_graph as sg

ASSETS = Path(__file__).resolve().parent.parent / "assets"


def test_minimal_graph_validates_clean(tmp_path):
    g = tmp_path / "Story-Graph.md"
    g.write_text(MINIMAL_V2, encoding="utf-8")
    report = sg.validate(str(g))
    assert report.errors == [], report.errors


def test_dramatic_irony_graph_validates(tmp_path):
    props = ("## Propositions\n| prop-id | statement | canon-status | governing-source | span |\n"
             "|---|---|---|---|---|\n| jackson-alive | Jackson lives | true | ms | s1 |\n")
    epi = ("## Epistemic States\n| prop-id | holder | mode | since-ch | span |\n|---|---|---|---|---|\n"
           "| jackson-alive | reader | knows | 3 | s1 |\n| jackson-alive | jonah | believes-false | 3 | s1 |\n")
    ev = ("## Evidence\n| span-id | source-id | locator | quote | note |\n|---|---|---|---|---|\n"
          "| s1 | ms | ch3 | Jackson was alive | |\n")
    text = make_graph(Propositions=props, Evidence=ev, **{"Epistemic States": epi})
    g = tmp_path / "Story-Graph.md"
    g.write_text(text, encoding="utf-8")
    report = sg.validate(str(g))
    assert report.errors == [], report.errors


def test_cli_exit_code_on_error(tmp_path):
    g = tmp_path / "Story-Graph.md"
    g.write_text(MINIMAL_V2.replace("| ontology-version | 2 |", "| ontology-version | 1 |"), encoding="utf-8")
    proc = subprocess.run([sys.executable, str(ASSETS / "story_graph.py"), "validate", str(g)],
                          capture_output=True, text=True)
    assert proc.returncode == 1
    assert "RESULT:" in proc.stdout
```

- [ ] **Step 2: Run to verify failure**

Run: `cd story-graph && python3 -m pytest tests/test_cli.py -v`
Expected: FAIL — `test_dramatic_irony_graph_validates` fails because the stub `validate` does not run the new checks.

- [ ] **Step 3: Replace the `validate` stub with the full orchestrator**

In `story_graph.py`, replace the Task 1 `validate` function body with:

```python
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
```

- [ ] **Step 4: Run the whole suite**

Run: `cd story-graph && python3 -m pytest tests/ -v`
Expected: all tests pass (structure, sources, propositions, epistemic, evidence, spans_source, openloops_logistics, cli).

- [ ] **Step 5: Commit**

```bash
git add story-graph/assets/story_graph.py story-graph/tests/test_cli.py
git commit -m "feat(story-graph): wire full v2 validate orchestrator + CLI e2e"
```

---

### Task 9: Kùzu loader module

**Files:**
- Create: `story-graph/assets/story_graph_kuzu.py`
- Test: `story-graph/tests/test_compile.py` (loader portion)

**Interfaces:**
- Consumes: a parsed `graph` dict (from `story_graph.parse_graph`).
- Produces: `load_graph(graph: dict, out_path: str) -> None` — creates node/rel tables and inserts rows into a Kùzu database at `out_path`.

- [ ] **Step 1: Write the failing test (skips without kuzu)**

Create `story-graph/tests/test_compile.py`:

```python
import pytest
from conftest import make_graph
import story_graph as sg


def test_load_graph_builds_queryable_db(tmp_path):
    kuzu = pytest.importorskip("kuzu")
    import story_graph_kuzu as loader
    props = ("## Propositions\n| prop-id | statement | canon-status | governing-source | span |\n"
             "|---|---|---|---|---|\n| jackson-alive | Jackson lives | true | ms | s1 |\n")
    epi = ("## Epistemic States\n| prop-id | holder | mode | since-ch | span |\n|---|---|---|---|---|\n"
           "| jackson-alive | reader | knows | 3 | s1 |\n| jackson-alive | jonah | believes-false | 3 | s1 |\n")
    ev = ("## Evidence\n| span-id | source-id | locator | quote | note |\n|---|---|---|---|---|\n"
          "| s1 | ms | ch3 | Jackson was alive | |\n")
    graph = sg.parse_graph(make_graph(Propositions=props, Evidence=ev, **{"Epistemic States": epi}))
    db_path = str(tmp_path / "g.kuzu")
    loader.load_graph(graph, db_path)
    conn = kuzu.Connection(kuzu.Database(db_path))
    res = conn.execute("MATCH (:Proposition)<-[e:EPISTEMIC]-(h) WHERE e.mode='believes-false' RETURN count(*)")
    assert res.get_next()[0] == 1
```

- [ ] **Step 2: Run to verify it skips or fails**

Run: `cd story-graph && python3 -m pytest tests/test_compile.py -v`
Expected: SKIPPED if kuzu absent; if `pip install kuzu` was run, FAIL with `ModuleNotFoundError: story_graph_kuzu`.

- [ ] **Step 3: Implement the loader**

Create `story-graph/assets/story_graph_kuzu.py`:

```python
"""Kùzu loader for a parsed Story Graph. Imported lazily by `story_graph compile`.
This is the ONLY module that imports kuzu."""
from __future__ import annotations

import re
import shutil
from pathlib import Path

import kuzu

NODE_DDL = [
    "CREATE NODE TABLE Entity(id STRING, type STRING, status STRING, voice STRING, note STRING, PRIMARY KEY(id))",
    "CREATE NODE TABLE Proposition(id STRING, statement STRING, canon_status STRING, PRIMARY KEY(id))",
    "CREATE NODE TABLE Source(id STRING, type STRING, authority INT64, note STRING, PRIMARY KEY(id))",
    "CREATE NODE TABLE Evidence(id STRING, locator STRING, quote STRING, note STRING, PRIMARY KEY(id))",
    "CREATE NODE TABLE OpenLoop(id STRING, planted_ch INT64, expectation STRING, must_fire_by STRING, status STRING, PRIMARY KEY(id))",
    "CREATE NODE TABLE Holder(id STRING, PRIMARY KEY(id))",
]
REL_DDL = [
    "CREATE REL TABLE RELATES(FROM Entity TO Entity, edge STRING, trend STRING, since_ch STRING)",
    "CREATE REL TABLE EPISTEMIC(FROM Holder TO Proposition, mode STRING, since_ch STRING, span_ids STRING)",
    "CREATE REL TABLE GOVERNED_BY(FROM Proposition TO Source)",
    "CREATE REL TABLE EVIDENCED_BY(FROM Evidence TO Source)",
]


def _int(v, default=0):
    return int(v) if re.fullmatch(r"-?\d+", (v or "").strip() or "") else default


def load_graph(graph: dict, out_path: str) -> None:
    p = Path(out_path)
    if p.exists():
        shutil.rmtree(p, ignore_errors=True) if p.is_dir() else p.unlink()
    db = kuzu.Database(out_path)
    conn = kuzu.Connection(db)
    for ddl in NODE_DDL + REL_DDL:
        conn.execute(ddl)

    S = graph["sections"]
    holders = set()

    for r in S.get("Entities", []):
        if r.get("id"):
            conn.execute("CREATE (:Entity {id:$id, type:$type, status:$status, voice:$voice, note:$note})",
                         {"id": r["id"], "type": r.get("type", ""), "status": r.get("status", ""),
                          "voice": r.get("voice", ""), "note": r.get("note", "")})
    for r in S.get("Sources", []):
        if r.get("source-id"):
            conn.execute("CREATE (:Source {id:$id, type:$type, authority:$a, note:$note})",
                         {"id": r["source-id"], "type": r.get("type", ""),
                          "a": _int(r.get("authority")), "note": r.get("note", "")})
    for r in S.get("Evidence", []):
        if r.get("span-id"):
            conn.execute("CREATE (:Evidence {id:$id, locator:$loc, quote:$q, note:$note})",
                         {"id": r["span-id"], "loc": r.get("locator", ""), "q": r.get("quote", ""),
                          "note": r.get("note", "")})
            if r.get("source-id"):
                conn.execute("MATCH (e:Evidence {id:$e}),(s:Source {id:$s}) CREATE (e)-[:EVIDENCED_BY]->(s)",
                             {"e": r["span-id"], "s": r["source-id"]})
    for r in S.get("Propositions", []):
        if r.get("prop-id"):
            conn.execute("CREATE (:Proposition {id:$id, statement:$st, canon_status:$cs})",
                         {"id": r["prop-id"], "st": r.get("statement", ""), "cs": r.get("canon-status", "")})
            if r.get("governing-source"):
                conn.execute("MATCH (p:Proposition {id:$p}),(s:Source {id:$s}) CREATE (p)-[:GOVERNED_BY]->(s)",
                             {"p": r["prop-id"], "s": r["governing-source"]})
    for r in S.get("Open Loops & Setups", []):
        if r.get("id"):
            conn.execute("CREATE (:OpenLoop {id:$id, planted_ch:$pc, expectation:$ex, must_fire_by:$mf, status:$stt})",
                         {"id": r["id"], "pc": _int(r.get("planted-ch")), "ex": r.get("expectation", ""),
                          "mf": r.get("must-fire-by", ""), "stt": r.get("status", "")})
    for r in S.get("Epistemic States", []):
        h = r.get("holder", "")
        if h and h not in holders:
            conn.execute("CREATE (:Holder {id:$id})", {"id": h})
            holders.add(h)
    for r in S.get("Epistemic States", []):
        if r.get("prop-id") and r.get("holder"):
            conn.execute(
                "MATCH (h:Holder {id:$h}),(p:Proposition {id:$p}) "
                "CREATE (h)-[:EPISTEMIC {mode:$m, since_ch:$sc, span_ids:$sp}]->(p)",
                {"h": r["holder"], "p": r["prop-id"], "m": r.get("mode", ""),
                 "sc": r.get("since-ch", ""), "sp": r.get("span", "")})
    for r in S.get("Relationships", []):
        if r.get("from") and r.get("to"):
            conn.execute(
                "MATCH (a:Entity {id:$a}),(b:Entity {id:$b}) "
                "CREATE (a)-[:RELATES {edge:$e, trend:$t, since_ch:$sc}]->(b)",
                {"a": r["from"], "b": r["to"], "e": r.get("edge", ""),
                 "t": r.get("trend", ""), "sc": r.get("since-ch", "")})
```

Note for the implementer: Kùzu's Python DDL/Cypher has shifted across releases. After `pip install kuzu`, run the Task 9 test and adjust the DDL strings / `execute` parameter style to match the installed version if it errors (e.g., `CREATE NODE TABLE` syntax, `get_next()` vs `get_as_df()`). The schema (tables, columns, rel directions) is fixed; only surface syntax may need alignment.

- [ ] **Step 4: Run the test (with kuzu installed)**

Run: `cd story-graph && pip install kuzu && python3 -m pytest tests/test_compile.py -v`
Expected: PASS (the dramatic-irony `believes-false` edge is counted as 1).

- [ ] **Step 5: Commit**

```bash
git add story-graph/assets/story_graph_kuzu.py story-graph/tests/test_compile.py
git commit -m "feat(story-graph): Kùzu loader (isolated dependency)"
```

---

### Task 10: `compile` subcommand (validate-gate + load)

**Files:**
- Modify: `story-graph/assets/story_graph.py`
- Test: `story-graph/tests/test_compile.py` (add CLI-gate cases)

**Interfaces:**
- Consumes: `validate`, `parse_graph`, lazy `story_graph_kuzu.load_graph`.
- Produces: `compile_graph(graph_path, out_path, ontology, chapters_dir) -> Report`; a `compile` argparse subcommand in `main`.

- [ ] **Step 1: Write the failing test**

Add to `story-graph/tests/test_compile.py`:

```python
def test_compile_refuses_on_error(tmp_path):
    # invalid ontology-version -> validation error -> compile must refuse (no kuzu needed)
    from conftest import MINIMAL_V2
    g = tmp_path / "Story-Graph.md"
    g.write_text(MINIMAL_V2.replace("| ontology-version | 2 |", "| ontology-version | 1 |"), encoding="utf-8")
    report = sg.compile_graph(str(g), str(tmp_path / "out.kuzu"), "", "")
    assert any("refus" in e.lower() or "ontology-version" in e for e in report.errors)
    assert not (tmp_path / "out.kuzu").exists()
```

- [ ] **Step 2: Run to verify failure**

Run: `cd story-graph && python3 -m pytest tests/test_compile.py::test_compile_refuses_on_error -v`
Expected: FAIL — `compile_graph` undefined.

- [ ] **Step 3: Implement**

Add to `story_graph.py`:

```python
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
```

Extend `main` to register the subcommand (add after the `validate` parser setup, before `args = parser.parse_args(argv)`):

```python
    c = sub.add_parser("compile")
    c.add_argument("graph")
    c.add_argument("--out", required=True)
    c.add_argument("--ontology", default="")
    c.add_argument("--chapters-dir", default="")
```

and add this branch in `main` after the `validate` branch:

```python
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
```

- [ ] **Step 4: Run to verify pass**

Run: `cd story-graph && python3 -m pytest tests/test_compile.py -v`
Expected: `test_compile_refuses_on_error` passes; the loader test passes or skips depending on kuzu.

- [ ] **Step 5: Commit**

```bash
git add story-graph/assets/story_graph.py story-graph/tests/test_compile.py
git commit -m "feat(story-graph): compile subcommand with validate-gate"
```

---

### Task 11: Ontology v2 doc, template v2, and SKILL.md v2

**Files:**
- Create: `story-graph/assets/Story-Graph-Ontology-v2.md`
- Create: `story-graph/assets/Story-Graph-TEMPLATE-v2.md`
- Rename: `story-graph/SKILL.md` → `story-graph/SKILL_v1.md`; Create new `story-graph/SKILL.md`
- Rename each `story-graph/reference/*.md` → `*_v1.md`; Create updated versions referencing v2 sections/commands

**Interfaces:** documentation only; no code interfaces.

- [ ] **Step 1: Write the v2 template**

Create `story-graph/assets/Story-Graph-TEMPLATE-v2.md` as the exact `MINIMAL_V2` section skeleton from `conftest.py` (same 12 core sections, empty tables, header `ontology-version | 2`, `modules | none`, `current-canon-chapter | 0`), titled `# Story Graph: [STORY_TITLE]`.

- [ ] **Step 2: Write the v2 ontology**

Create `story-graph/assets/Story-Graph-Ontology-v2.md` documenting, to match the code exactly: the header block (`ontology-version: 2`, `modules`, `current-canon-chapter`); the 12 core sections in order + the `spe` module's `Physics State`; every controlled vocabulary in "Global Constraints" above; the per-table schemas (Sources, Propositions, Epistemic States, Evidence, Open Loops & Setups, Logistics-with-span) with column lists copied from the fixture; the authority model (assertion-specific `governing-source`, editorial bar, inversion as WARN); the evidence-span rules (load-bearing set, manuscript hard-verify, provisional exemption); and the `compile` projection (node/rel tables from `story_graph_kuzu.py`). State that it supersedes v1 for v2 graphs; v1 remains for v1 graphs.

- [ ] **Step 3: Shift-rename and rewrite SKILL.md**

```bash
cd story-graph && git mv SKILL.md SKILL_v1.md
```

Create a new `story-graph/SKILL.md` that keeps v1's mode-detection and file-safety prose but: points the bundled-asset paths at `Story-Graph-Ontology-v2.md` / `Story-Graph-TEMPLATE-v2.md`; documents the `modules` header field and the core/module split; documents the two commands —
`python3 "<SKILL_DIR>/assets/story_graph.py" validate "<graph>" [--chapters-dir <dir>] [--spe-dir <dir>]`
and
`python3 "<SKILL_DIR>/assets/story_graph.py" compile "<graph>" --out <db> [--chapters-dir <dir>]` —
and states that `validate` is stdlib-only while `compile` needs `pip install kuzu`.

- [ ] **Step 4: Shift-rename and update reference files**

```bash
cd story-graph/reference && git mv seed-from-worksheet.md seed-from-worksheet_v1.md && git mv reverse-engineer.md reverse-engineer_v1.md && git mv catch-up-from-chapters.md catch-up-from-chapters_v1.md
```

Recreate each at its unsuffixed name updated for v2: the new core sections (Sources, Propositions, Epistemic States, Evidence), the renamed "Open Loops & Setups", populating evidence spans for load-bearing rows, and marking inferred facts `provisional`.

- [ ] **Step 5: Commit**

```bash
git add story-graph/
git commit -m "docs(story-graph): ontology v2, template v2, SKILL.md v2, reference updates"
```

---

### Task 12: Book-3 proof

**Files:**
- Create: `series/books/book-3/Story-Graph.md`

**Interfaces:** none (acceptance test of the whole slice).

- [ ] **Step 1: Read chapters 1–3 and pull real quotes**

Run: `sed -n '1,80p' series/books/book-3/phase-7-drafting/chapters/ch01.md` (and ch02, ch03). Choose 2–3 short verbatim sentences that establish a fact, a character's (mis)belief, and a planted setup. Record their exact text and chapter for the Evidence table.

- [ ] **Step 2: Author the v2 graph**

Create `series/books/book-3/Story-Graph.md` by copying `Story-Graph-TEMPLATE-v2.md` and filling: a `manuscript` Source; the real entities; ≥1 Proposition with a manuscript span; ≥1 Epistemic State pair demonstrating dramatic irony (`reader knows` vs a character `believes-false`); ≥1 Open Loop/Setup with a span; and the Evidence rows holding the verbatim quotes from Step 1. Set `current-canon-chapter | 3`.

- [ ] **Step 3: Validate against the real chapters (must pass)**

Run:
```bash
python3 story-graph/assets/story_graph.py validate \
  series/books/book-3/Story-Graph.md \
  --chapters-dir series/books/book-3/phase-7-drafting/chapters
```
Expected: `RESULT: 0 error(s), …`. Fix authored rows until clean.

- [ ] **Step 4: Prove graph-vs-source catches a bad quote**

Temporarily change one Evidence `quote` to text not in its chapter, re-run Step 3, and confirm an `ERROR: Evidence [...]: quote not found`. Then revert the edit.

- [ ] **Step 5: Compile and run the two Cypher sanity checks**

Run:
```bash
pip install kuzu
python3 story-graph/assets/story_graph.py compile \
  series/books/book-3/Story-Graph.md --out /tmp/book3.kuzu \
  --chapters-dir series/books/book-3/phase-7-drafting/chapters
python3 - <<'PY'
import kuzu
c = kuzu.Connection(kuzu.Database("/tmp/book3.kuzu"))
irony = c.execute("MATCH (h:Holder {id:'reader'})-[e:EPISTEMIC]->(p:Proposition) "
                  "WHERE e.mode='knows' RETURN p.id")
print("reader-knows:", [r for r in irony])
PY
```
Expected: the dramatic-irony query returns the proposition; a second query for `OpenLoop` rows lists the planted setup. This confirms A, layers 1+3, D3, and the compiler on real prose.

- [ ] **Step 6: Commit**

```bash
git add series/books/book-3/Story-Graph.md
git commit -m "test(story-graph): Book-3 chapters 1-3 foundation proof graph"
```

---

## Self-Review

**Spec coverage:**
- A (core/module cut) → Tasks 1 (structure/modules), 11 (ontology doc). ✓
- Authority (layer 1) → Task 2. ✓
- Epistemic separation (layer 3): Propositions + unified Epistemic States incl. `reader` → Tasks 3, 4. ✓
- Evidence spans (D3): section + registry → Task 5; manuscript verification → Task 6; load-bearing enforcement → Tasks 3, 4, 7. ✓
- Validator upgrade (graph-vs-source, authority, epistemic, modular) → Tasks 1–8. ✓
- Kùzu compiler (pluggable/isolated, validate-gate, refuse-on-error) → Tasks 9, 10. ✓
- Versioning rule (shift-rename code/SKILL/reference; side-by-side schema) → Tasks 1, 11. ✓
- stdlib boundary / dependency quarantine → Tasks 1 (top-level stdlib), 9–10 (kuzu isolated + lazy). ✓
- Proof against Book 3 → Task 12. ✓
- Out-of-scope layers (C, 2, 4, 5) → correctly absent.

**Placeholder scan:** No "TBD/TODO"; the Task 9 note is a version-alignment instruction, not a content gap; Task 11/12 doc steps specify exact content, files, and commands.

**Type consistency:** `parse_graph` returns the documented dict everywhere; `check_evidence` returns `span_ids` consumed by `check_propositions`/`check_epistemic`/`check_open_loops`/`check_logistics`; `check_sources` returns the `{id: {type, authority}}` dict consumed by `check_authority`/`check_evidence`/`verify_spans`; `_check_span_required`/`_span_ids`/`is_provisional` defined in Task 3 and reused in Tasks 4, 7; `load_graph(graph, out_path)` signature matches its Task 10 caller. ✓
