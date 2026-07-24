# Story Graph — Query/Report Slice (C) Implementation Plan

> **For agentic workers:** implement task-by-task, TDD. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Add `query` and `report` subcommands that answer writer-facing questions over the compiled Kùzu graph, with answers that carry their evidence receipts.

**Architecture:** A new `assets/story_graph_query.py` (imports kuzu, like the loader) compiles the text graph to a throwaway temp Kùzu db and runs a small set of named Cypher queries, returning formatted text. `story_graph.py` gains `query` and `report` subcommands that validate first, then dispatch. The loader gains a `SUPPORTS` edge (Evidence→Proposition and Evidence→OpenLoop) so a claim's receipts are a clean traversal.

**Tech Stack:** Python 3.10 (stdlib for parse/validate), Kùzu 0.11.3 (query/compile only), pytest.

## Global Constraints

- **stdlib boundary:** `parse`/`validate` stay stdlib-only. `kuzu` is imported only inside `story_graph_kuzu.py` and `story_graph_query.py`, and only reached via lazy imports in `compile`/`query`/`report`.
- **Single source of truth:** `query`/`report` never require a pre-built db — they compile the text graph to a temp dir each run. No stale database.
- **Validate-gate:** `query`/`report` refuse to run if the graph has validation ERRORs (same as `compile`).
- **Versioning (repo owner rule):** editing a fixed-call-chain file uses *shift-rename*. `SKILL.md` already has `SKILL_v1.md`; the next edit moves current `SKILL.md` → `SKILL_v2.md`, then writes new `SKILL.md`. `story_graph.py`/`story_graph_kuzu.py` are modified in place (they are code under test, not prose loaded by name — treat as normal source; the shift-rename rule targets prose/config loaded by fixed name). The ontology doc is side-by-side and already at v2; append the SUPPORTS note in place.
- **Kùzu result API (0.11.3):** `conn.execute(q, parameters={...})`; iterate with `while res.has_next(): res.get_next()`.
- **Proving manuscript:** `series/books/book-3/Story-Graph.md` + `series/books/book-3/phase-7-drafting/chapters/`.
- Tests needing kuzu use `pytest.importorskip("kuzu")`.

## File Structure

- `story-graph/assets/story_graph_kuzu.py` — add `SUPPORTS` rel table + edge creation from `span` columns.
- `story-graph/assets/story_graph_query.py` — NEW: `open_graph`, named queries, formatters, `run_query`, `run_report`.
- `story-graph/assets/story_graph.py` — add `query` + `report` subcommands and `query_graph`/`report_graph` entry funcs.
- `story-graph/tests/test_supports.py`, `test_query.py`, `test_report.py` — NEW test modules.
- `story-graph/SKILL.md` — document the two commands (shift-rename).

---

### Task C1: Loader — SUPPORTS edges (Evidence → Proposition / OpenLoop)

**Files:**
- Modify: `story-graph/assets/story_graph_kuzu.py`
- Test: `story-graph/tests/test_supports.py`

**Interfaces:**
- Produces: after `load_graph`, `MATCH (e:Evidence)-[:SUPPORTS]->(p:Proposition {id})` returns exactly the spans listed in that proposition's `span` column; same for OpenLoop.

- [ ] **Step 1: Write the failing test**

Create `story-graph/tests/test_supports.py`:

```python
import pytest
from conftest import make_graph
import story_graph as sg


def test_supports_edges_link_evidence_to_proposition(tmp_path):
    pytest.importorskip("kuzu")
    import kuzu, story_graph_kuzu as loader
    props = ("## Propositions\n| prop-id | statement | canon-status | governing-source | span |\n"
             "|---|---|---|---|---|\n| scrolls-gone | The scrolls are gone | true | ms | s1 |\n")
    ev = ("## Evidence\n| span-id | source-id | locator | quote | note |\n|---|---|---|---|---|\n"
          "| s1 | ms | ch02 | The gap was there | |\n| s2 | ms | ch01 | unrelated | |\n")
    graph = sg.parse_graph(make_graph(Propositions=props, Evidence=ev))
    db = str(tmp_path / "g.kuzu")
    loader.load_graph(graph, db)
    conn = kuzu.Connection(kuzu.Database(db))
    res = conn.execute("MATCH (e:Evidence)-[:SUPPORTS]->(p:Proposition {id:'scrolls-gone'}) RETURN e.id")
    got = []
    while res.has_next():
        got.append(res.get_next()[0])
    assert got == ["s1"]  # only the linked span, not s2
```

- [ ] **Step 2: Run to verify failure**

Run: `cd story-graph && python3 -m pytest tests/test_supports.py -v`
Expected: FAIL — no `SUPPORTS` rel table / no edge.

- [ ] **Step 3: Implement**

In `story_graph_kuzu.py`, add to `REL_DDL` (use a multi-pair rel table):

```python
    "CREATE REL TABLE SUPPORTS(FROM Evidence TO Proposition, FROM Evidence TO OpenLoop)",
```

Add a helper near `_int`:

```python
def _spans(cell):
    return [s.strip() for s in re.split(r"[,\s]+", cell or "")
            if s.strip() and s.strip().lower() != "provisional"]
```

After the Propositions loop (which creates Proposition nodes), add SUPPORTS edges — place this AFTER both Propositions and Evidence nodes exist (Evidence is created before Propositions in the current code, so add right after the Propositions loop):

```python
    for r in S.get("Propositions", []):
        for sid in _spans(r.get("span", "")):
            conn.execute(
                "MATCH (e:Evidence {id:$e}),(p:Proposition {id:$p}) CREATE (e)-[:SUPPORTS]->(p)",
                {"e": sid, "p": r["prop-id"]})
    for r in S.get("Open Loops & Setups", []):
        for sid in _spans(r.get("span", "")):
            conn.execute(
                "MATCH (e:Evidence {id:$e}),(o:OpenLoop {id:$o}) CREATE (e)-[:SUPPORTS]->(o)",
                {"e": sid, "o": r["id"]})
```

If kuzu 0.11.3 rejects the multi-pair `SUPPORTS` DDL, fall back to two rel tables `SUPPORTS_PROP(FROM Evidence TO Proposition)` and `SUPPORTS_LOOP(FROM Evidence TO OpenLoop)`, create edges into each, and update the test query accordingly — report the change.

- [ ] **Step 4: Run to verify pass**

Run: `cd story-graph && python3 -m pytest tests/test_supports.py -v`
Expected: PASS. Then FULL suite `python3 -m pytest tests/ -q` — still all green (the existing compile test must still pass with the new rel table).

- [ ] **Step 5: Commit**

```bash
git add story-graph/assets/story_graph_kuzu.py story-graph/tests/test_supports.py
git commit -m "feat(story-graph): SUPPORTS edges link evidence to claims"
```

---

### Task C2: Query module

**Files:**
- Create: `story-graph/assets/story_graph_query.py`
- Test: `story-graph/tests/test_query.py`

**Interfaces:**
- Produces: `open_graph(graph: dict) -> kuzu.Connection` (compiles to a temp db); `q_irony(conn) -> list`, `q_knows(conn, holder) -> list`, `q_open_loops(conn) -> list`, `q_receipts(conn, prop_id) -> list`; `run_query(name, graph, canon_ch, target="") -> str` (formatted text). Imported lazily by `story_graph.py`.

- [ ] **Step 1: Write the failing test**

Create `story-graph/tests/test_query.py`:

```python
import pytest
from conftest import make_graph
import story_graph as sg

IRONY = dict(
    Propositions=("## Propositions\n| prop-id | statement | canon-status | governing-source | span |\n"
                  "|---|---|---|---|---|\n| bond | Wolf knows its mate | true | ms | s1 |\n"),
    Evidence=("## Evidence\n| span-id | source-id | locator | quote | note |\n|---|---|---|---|---|\n"
              "| s1 | ms | ch01 | knew the scent of mate | |\n| s2 | ms | ch01 | Not ever | |\n"),
)
EPI = ("## Epistemic States\n| prop-id | holder | mode | since-ch | span |\n|---|---|---|---|---|\n"
       "| bond | reader | knows | 1 | s1 |\n| bond | jonah | believes-false | 1 | s2 |\n")


def graph_dict():
    ent = ("## Entities\n| id | type | status | voice | note |\n|---|---|---|---|---|\n"
           "| jonah | Character | active | male | |\n")
    return sg.parse_graph(make_graph(Entities=ent, **{"Epistemic States": EPI}, **IRONY))


def test_irony_query_pairs_reader_and_character():
    pytest.importorskip("kuzu")
    import story_graph_query as q
    conn = q.open_graph(graph_dict())
    rows = q.q_irony(conn)
    assert any(r for r in rows if r[0] == "bond" and r[2] == "jonah")


def test_receipts_returns_only_that_props_spans():
    pytest.importorskip("kuzu")
    import story_graph_query as q
    conn = q.open_graph(graph_dict())
    spans = sorted(r[0] for r in q.q_receipts(conn, "bond"))
    assert spans == ["s1"]


def test_run_query_irony_text_mentions_holders():
    pytest.importorskip("kuzu")
    import story_graph_query as q
    out = q.run_query("irony", graph_dict(), canon_ch=1)
    assert "reader" in out and "jonah" in out and "believes-false" in out
```

- [ ] **Step 2: Run to verify failure**

Run: `cd story-graph && python3 -m pytest tests/test_query.py -v`
Expected: FAIL — `story_graph_query` missing.

- [ ] **Step 3: Implement**

Create `story-graph/assets/story_graph_query.py`:

```python
"""Named queries over a compiled Story Graph. Imported lazily by `story_graph`
query/report. Imports kuzu (via the loader) — never reached by `validate`."""
from __future__ import annotations

import tempfile
from pathlib import Path

import kuzu


def _rows(conn, cy, params=None):
    res = conn.execute(cy, parameters=params or {})
    out = []
    while res.has_next():
        out.append(res.get_next())
    return out


def open_graph(graph: dict):
    import story_graph_kuzu
    d = tempfile.mkdtemp(prefix="sg-query-")
    dbpath = str(Path(d) / "g.kuzu")
    story_graph_kuzu.load_graph(graph, dbpath)
    return kuzu.Connection(kuzu.Database(dbpath))


def q_irony(conn):
    return _rows(conn,
        "MATCH (:Holder {id:'reader'})-[:EPISTEMIC {mode:'knows'}]->(p:Proposition) "
        "MATCH (h:Holder)-[e:EPISTEMIC {mode:'believes-false'}]->(p) "
        "RETURN p.id, p.statement, h.id, e.since_ch ORDER BY p.id")


def q_knows(conn, holder):
    return _rows(conn,
        "MATCH (h:Holder {id:$h})-[e:EPISTEMIC]->(p:Proposition) "
        "RETURN e.mode, e.since_ch, p.id, p.statement ORDER BY e.since_ch, p.id",
        {"h": holder})


def q_open_loops(conn):
    return _rows(conn,
        "MATCH (o:OpenLoop) RETURN o.id, o.status, o.planted_ch, o.must_fire_by, o.expectation "
        "ORDER BY o.planted_ch")


def q_receipts(conn, prop_id):
    return _rows(conn,
        "MATCH (e:Evidence)-[:SUPPORTS]->(p:Proposition {id:$p}) "
        "RETURN e.id, e.locator, e.quote ORDER BY e.locator, e.id", {"p": prop_id})


def _overdue(status, must_fire_by, canon_ch):
    return status == "UNFIRED" and str(must_fire_by).isdigit() and int(must_fire_by) <= canon_ch


def run_query(name, graph: dict, canon_ch=0, target=""):
    conn = open_graph(graph)
    lines = []
    if name == "irony":
        rows = q_irony(conn)
        if not rows:
            return "No dramatic irony: no proposition is known by the reader and believed-false by a character."
        lines.append("Dramatic irony — reader knows what a character denies:")
        for pid, stmt, who, since in rows:
            lines.append(f"  • {who} believes-false (since ch{since}): {stmt}")
    elif name == "knows":
        if not target:
            return "usage: query knows <graph> <holder>"
        rows = q_knows(conn, target)
        if not rows:
            return f"No knowledge states recorded for holder '{target}'."
        lines.append(f"What {target} holds:")
        for mode, since, pid, stmt in rows:
            lines.append(f"  ch{since:>2}  {mode:<15} {stmt}")
    elif name == "open-loops":
        rows = q_open_loops(conn)
        if not rows:
            return "No open loops or setups recorded."
        lines.append("Open loops & setups:")
        for oid, status, planted, must, exp in rows:
            flag = "  [OVERDUE]" if _overdue(status, must, canon_ch) else ""
            lines.append(f"  {oid} — {status} (planted ch{planted}, by ch{must}){flag}")
            lines.append(f"      {exp}")
    elif name == "receipts":
        if not target:
            return "usage: query receipts <graph> <prop-id>"
        rows = q_receipts(conn, target)
        if not rows:
            return f"No evidence spans support proposition '{target}'."
        lines.append(f"Evidence for '{target}':")
        for sid, loc, quote in rows:
            lines.append(f"  [{loc}] \"{quote}\"  ({sid})")
    else:
        return f"unknown query '{name}'. try: irony | knows | open-loops | receipts"
    return "\n".join(lines)


def run_report(graph: dict, canon_ch=0):
    conn = open_graph(graph)
    out = [f"STORY GRAPH REPORT — canon at chapter {canon_ch}", "=" * 48, ""]
    irony = q_irony(conn)
    out.append(f"Dramatic irony ({len(irony)}):")
    for pid, stmt, who, since in irony:
        out.append(f"  • reader knows / {who} believes-false: {stmt}")
    out.append("")
    loops = q_open_loops(conn)
    overdue = [o for o in loops if _overdue(o[1], o[3], canon_ch)]
    out.append(f"Open loops ({len(loops)}, overdue {len(overdue)}):")
    for oid, status, planted, must, exp in loops:
        flag = "  [OVERDUE]" if _overdue(status, must, canon_ch) else ""
        out.append(f"  {oid} — {status} (by ch{must}){flag}")
    return "\n".join(out)
```

- [ ] **Step 4: Run to verify pass**

Run: `cd story-graph && python3 -m pytest tests/test_query.py -v`
Expected: 3 passed (or skipped if kuzu absent — it is installed at 0.11.3, so PASS).

- [ ] **Step 5: Commit**

```bash
git add story-graph/assets/story_graph_query.py story-graph/tests/test_query.py
git commit -m "feat(story-graph): query module (irony/knows/open-loops/receipts)"
```

---

### Task C3: `query` subcommand

**Files:**
- Modify: `story-graph/assets/story_graph.py`
- Test: `story-graph/tests/test_query.py` (add CLI cases)

**Interfaces:**
- Produces: `query_graph(name, graph_path, target="", chapters_dir="") -> tuple[str, Report]`; a `query` argparse subcommand.

- [ ] **Step 1: Write the failing test**

Add to `story-graph/tests/test_query.py`:

```python
def test_query_refuses_on_validation_error(tmp_path):
    from conftest import MINIMAL_V2
    g = tmp_path / "Story-Graph.md"
    g.write_text(MINIMAL_V2.replace("| ontology-version | 2 |", "| ontology-version | 1 |"), encoding="utf-8")
    out, report = sg.query_graph("irony", str(g))
    assert report.errors and "irony" not in out.lower()
```

- [ ] **Step 2: Run to verify failure**

Run: `cd story-graph && python3 -m pytest tests/test_query.py::test_query_refuses_on_validation_error -v`
Expected: FAIL — `query_graph` undefined.

- [ ] **Step 3: Implement**

Add to `story_graph.py`:

```python
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
```

In `main`, register after the `compile` parser:

```python
    qp = sub.add_parser("query")
    qp.add_argument("name")
    qp.add_argument("graph")
    qp.add_argument("target", nargs="?", default="")
    qp.add_argument("--chapters-dir", default="")
```

and add the branch after the `compile` branch:

```python
    if args.command == "query":
        out, report = query_graph(args.name, args.graph, args.target, args.chapters_dir)
        if report.errors:
            for e in report.errors:
                print(f"ERROR: {e}")
            return 1
        print(out)
        return 0
```

- [ ] **Step 4: Run to verify pass**

Run: `cd story-graph && python3 -m pytest tests/test_query.py -v` then FULL `python3 -m pytest tests/ -q`.
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add story-graph/assets/story_graph.py story-graph/tests/test_query.py
git commit -m "feat(story-graph): query subcommand (validate-gated)"
```

---

### Task C4: `report` subcommand

**Files:**
- Modify: `story-graph/assets/story_graph.py`
- Test: `story-graph/tests/test_report.py`

**Interfaces:**
- Produces: `report_graph(graph_path, chapters_dir="") -> tuple[str, Report]`; a `report` argparse subcommand.

- [ ] **Step 1: Write the failing test**

Create `story-graph/tests/test_report.py`:

```python
import pytest
from conftest import make_graph
import story_graph as sg


def test_report_lists_irony_and_open_loops(tmp_path):
    pytest.importorskip("kuzu")
    props = ("## Propositions\n| prop-id | statement | canon-status | governing-source | span |\n"
             "|---|---|---|---|---|\n| bond | Wolf knows mate | true | ms | s1 |\n")
    ev = ("## Evidence\n| span-id | source-id | locator | quote | note |\n|---|---|---|---|---|\n"
          "| s1 | ms | ch01 | mate | |\n| s2 | ms | ch01 | not ever | |\n")
    epi = ("## Epistemic States\n| prop-id | holder | mode | since-ch | span |\n|---|---|---|---|---|\n"
           "| bond | reader | knows | 1 | s1 |\n| bond | jonah | believes-false | 1 | s2 |\n")
    loops = ("## Open Loops & Setups\n| id | planted-ch | expectation | must-fire-by | status | span |\n"
             "|---|---|---|---|---|---|\n| purge | 2 | stop the purge | 30 | UNFIRED | s2 |\n")
    ent = "## Entities\n| id | type | status | voice | note |\n|---|---|---|---|---|\n| jonah | Character | active | male | |\n"
    text = make_graph(Entities=ent, Propositions=props, Evidence=ev, **{"Epistemic States": epi}, **{"Open Loops & Setups": loops})
    g = tmp_path / "Story-Graph.md"
    g.write_text(text, encoding="utf-8")
    out, report = sg.report_graph(str(g))
    assert report.errors == []
    assert "Dramatic irony" in out and "purge" in out
```

- [ ] **Step 2: Run to verify failure**

Run: `cd story-graph && python3 -m pytest tests/test_report.py -v`
Expected: FAIL — `report_graph` undefined.

- [ ] **Step 3: Implement**

Add to `story_graph.py`:

```python
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
```

Register in `main` after the `query` parser:

```python
    rp = sub.add_parser("report")
    rp.add_argument("graph")
    rp.add_argument("--chapters-dir", default="")
```

and the branch after the `query` branch:

```python
    if args.command == "report":
        out, report = report_graph(args.graph, args.chapters_dir)
        if report.errors:
            for e in report.errors:
                print(f"ERROR: {e}")
            return 1
        print(out)
        return 0
```

- [ ] **Step 4: Run to verify pass**

Run: `cd story-graph && python3 -m pytest tests/ -q`
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add story-graph/assets/story_graph.py story-graph/tests/test_report.py
git commit -m "feat(story-graph): report subcommand (digest)"
```

---

### Task C5: Docs

**Files:**
- Shift-rename: `story-graph/SKILL.md` → `story-graph/SKILL_v2.md`; Create new `story-graph/SKILL.md`
- Modify: `story-graph/assets/Story-Graph-Ontology-v2.md`

- [ ] **Step 1: Shift-rename SKILL.md and add query/report**

```bash
cd story-graph && git mv SKILL.md SKILL_v2.md
```

Write a new `story-graph/SKILL.md` identical to `SKILL_v2.md` plus a "Querying" section documenting:
`python3 "<SKILL_DIR>/assets/story_graph.py" query <irony|knows|open-loops|receipts> "<graph>" [target] [--chapters-dir <dir>]`
and
`python3 "<SKILL_DIR>/assets/story_graph.py" report "<graph>" [--chapters-dir <dir>]`,
noting both need `pip install kuzu`, both validate first and refuse on ERRORs, and answers carry evidence receipts. `knows` takes a holder id (or `reader`); `receipts` takes a prop-id.

- [ ] **Step 2: Note SUPPORTS in the ontology**

In `Story-Graph-Ontology-v2.md`, in the compile-projection section, add `SUPPORTS(Evidence → Proposition | OpenLoop)` to the rel-table list with a one-line description (materialized from load-bearing `span` columns).

- [ ] **Step 3: Verify tests unaffected + commit**

Run: `cd story-graph && python3 -m pytest tests/ -q` (still all pass).

```bash
git add story-graph/SKILL.md story-graph/SKILL_v2.md story-graph/assets/Story-Graph-Ontology-v2.md
git commit -m "docs(story-graph): document query/report commands + SUPPORTS edge"
```

---

### Task C6: Book-3 proof

- [ ] **Step 1: Run the four queries against the real graph**

```bash
G=series/books/book-3/Story-Graph.md
CH=series/books/book-3/phase-7-drafting/chapters
python3 story-graph/assets/story_graph.py query irony "$G" --chapters-dir "$CH"
python3 story-graph/assets/story_graph.py query knows "$G" jonah-harrow --chapters-dir "$CH"
python3 story-graph/assets/story_graph.py query open-loops "$G" --chapters-dir "$CH"
python3 story-graph/assets/story_graph.py query receipts "$G" founding-scrolls-missing --chapters-dir "$CH"
```
Expected: irony names jonah-harrow/reader on the mate-bond; receipts for `founding-scrolls-missing` returns ONLY `s-scrolls-gone` (proving the SUPPORTS fix — no cross-claim quotes).

- [ ] **Step 2: Run the report**

```bash
python3 story-graph/assets/story_graph.py report "$G" --chapters-dir "$CH"
```
Expected: irony count 1, open loops 1 (purge, not overdue at ch3).

- [ ] **Step 3: Record + no commit needed** (proof is runtime; nothing to write). Report outputs to the user.

---

## Self-Review

- SUPPORTS edge → C1; query engine → C2; CLI query → C3; report → C4; docs (incl. versioning) → C5; proof (incl. the receipts-precision fix demonstrated) → C6. ✓
- stdlib boundary preserved: kuzu only in `story_graph_kuzu.py` + `story_graph_query.py`, reached lazily. ✓
- Types: `open_graph`→conn used by all `q_*`; `run_query(name, graph, canon_ch, target)` + `run_report(graph, canon_ch)` match their callers `query_graph`/`report_graph`. ✓
- No placeholders. ✓
