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
