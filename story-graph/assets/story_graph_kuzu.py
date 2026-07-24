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
