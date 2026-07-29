from __future__ import annotations

import html
import json
import os
import re
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server

APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "data" / "story_graph.db"
CANON_VERSION = "BOOK-3-CANON-v2.0"


def db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def esc(value: object) -> str:
    return html.escape("" if value is None else str(value))


def layout(title: str, body: str) -> str:
    nav = """
    <nav>
      <a href="/">Dashboard</a>
      <a href="/search">Search</a>
      <a href="/scenes">Scenes</a>
      <a href="/knowledge">Knowledge</a>
      <a href="/custody">Custody</a>
      <a href="/promises">Promises</a>
      <a href="/continuity">Continuity</a>
      <a href="/arcs">Arcs</a>
      <a href="/proposals">Revision Proposals</a>
    </nav>
    """
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} · Story Graph OS</title>
<link rel="stylesheet" href="/static/style.css">
</head>
<body>
<header>
  <div>
    <h1>Story Graph Operating System</h1>
    <p>Author workspace · {CANON_VERSION}</p>
  </div>
</header>
{nav}
<main>
{body}
</main>
<footer>Local prototype · Frozen canon is read-only · Revision proposals are isolated</footer>
</body>
</html>"""


def response(start_response, body: str, status: str = "200 OK", content_type: str = "text/html; charset=utf-8"):
    data = body.encode("utf-8")
    start_response(status, [
        ("Content-Type", content_type),
        ("Content-Length", str(len(data))),
    ])
    return [data]


def rows_to_table(rows: Iterable[sqlite3.Row], columns: list[str], empty: str = "No records found.") -> str:
    rows = list(rows)
    if not rows:
        return f'<p class="empty">{esc(empty)}</p>'
    head = "".join(f"<th>{esc(c.replace('_', ' ').title())}</th>" for c in columns)
    body = []
    for row in rows:
        cells = "".join(f"<td>{esc(row[c])}</td>" for c in columns)
        body.append(f"<tr>{cells}</tr>")
    return f'<div class="table-wrap"><table><thead><tr>{head}</tr></thead><tbody>{"".join(body)}</tbody></table></div>'


def dashboard() -> str:
    conn = db()
    counts = {}
    for table in ["scene_briefs", "entities", "knowledge_timeline", "custody_timeline",
                  "promise_board", "continuity_dashboard", "analytical_state_map",
                  "revision_proposals"]:
        counts[table] = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    active_promises = conn.execute(
        """SELECT COUNT(DISTINCT promise_id) FROM promise_board
           WHERE board_bucket IN ('INTRODUCED','ESCALATED','ACTIVE_OR_OTHER','REOPENED_OR_REVERSED','PARTIALLY_PAID')"""
    ).fetchone()[0]
    warnings = conn.execute(
        "SELECT COUNT(*) FROM continuity_dashboard WHERE dashboard_bucket='MODEL_LIMITATION_OR_REPAIR'"
    ).fetchone()[0]
    recent_scenes = conn.execute(
        """SELECT scene_id, chapter_index, pov, location, outcome
           FROM scene_briefs ORDER BY CAST(chapter_index AS INTEGER) DESC,
           CAST(scene_index_in_chapter AS INTEGER) DESC LIMIT 5"""
    ).fetchall()
    conn.close()
    cards = [
        ("Scenes", counts["scene_briefs"]),
        ("Entities", counts["entities"]),
        ("Knowledge states", counts["knowledge_timeline"]),
        ("Custody intervals", counts["custody_timeline"]),
        ("Active promises", active_promises),
        ("Timing/model annotations", warnings),
        ("Analytical states", counts["analytical_state_map"]),
        ("Revision proposals", counts["revision_proposals"]),
    ]
    card_html = "".join(
        f'<div class="card"><strong>{esc(value)}</strong><span>{esc(label)}</span></div>'
        for label, value in cards
    )
    recent = rows_to_table(recent_scenes, ["scene_id", "chapter_index", "pov", "location", "outcome"])
    return layout("Dashboard", f"""
<section class="hero">
  <h2>Author Command Center</h2>
  <p>Frozen canon stays frozen. Questions, evidence, and revision proposals live here.</p>
</section>
<section class="cards">{card_html}</section>
<section>
  <h2>Latest scenes</h2>
  {recent}
</section>
<section class="callout">
  <h2>Start with a question</h2>
  <form action="/search" method="get" class="search-form">
    <input name="q" placeholder="What does Margot know about Valerius by B03-C17-S03?">
    <button>Search canon</button>
  </form>
</section>
""")


def search_page(query: str) -> str:
    query = query.strip()
    if not query:
        return layout("Search", """
<h2>Search frozen canon</h2>
<form method="get" class="search-form">
<input name="q" placeholder="Search scenes, entities, promises, custody, continuity, or knowledge">
<button>Search</button>
</form>
""")
    conn = db()
    like = f"%{query}%"
    entities = conn.execute(
        """SELECT entity_id, canonical_name, entity_type, aliases, status
           FROM entities WHERE canonical_name LIKE ? OR aliases LIKE ? LIMIT 20""",
        (like, like)
    ).fetchall()
    scenes = conn.execute(
        """SELECT scene_id, chapter_index, pov, location, outcome
           FROM scene_briefs
           WHERE scene_id LIKE ? OR present_characters LIKE ? OR goal LIKE ?
              OR opposition LIKE ? OR outcome LIKE ? OR major_events LIKE ?
           LIMIT 30""", (like, like, like, like, like, like)
    ).fetchall()
    knowledge = conn.execute(
        """SELECT assertion_id, holder_name, epistemic_status, proposition, valid_from_scene
           FROM knowledge_timeline
           WHERE holder_name LIKE ? OR proposition LIKE ? LIMIT 30""",
        (like, like)
    ).fetchall()
    promises = conn.execute(
        """SELECT promise_id, scene, board_bucket, description
           FROM promise_board WHERE promise_id LIKE ? OR description LIKE ? LIMIT 30""",
        (like, like)
    ).fetchall()
    continuity = conn.execute(
        """SELECT issue_id, category, dashboard_bucket, decision, reason
           FROM continuity_dashboard
           WHERE issue_id LIKE ? OR reason LIKE ? OR graph_action LIKE ? LIMIT 30""",
        (like, like, like)
    ).fetchall()
    conn.close()
    body = f"""
<h2>Search</h2>
<form method="get" class="search-form">
<input name="q" value="{esc(query)}">
<button>Search</button>
</form>
<p class="meta">Results for <strong>{esc(query)}</strong></p>
<h3>Entities</h3>{rows_to_table(entities, ["entity_id","canonical_name","entity_type","aliases","status"])}
<h3>Scenes</h3>{rows_to_table(scenes, ["scene_id","chapter_index","pov","location","outcome"])}
<h3>Knowledge</h3>{rows_to_table(knowledge, ["assertion_id","holder_name","epistemic_status","proposition","valid_from_scene"])}
<h3>Promises</h3>{rows_to_table(promises, ["promise_id","scene","board_bucket","description"])}
<h3>Continuity</h3>{rows_to_table(continuity, ["issue_id","category","dashboard_bucket","decision","reason"])}
"""
    return layout("Search", body)


def scenes_page(scene_id: str | None = None) -> str:
    conn = db()
    if scene_id:
        row = conn.execute("SELECT * FROM scene_briefs WHERE scene_id=?", (scene_id,)).fetchone()
        conn.close()
        if not row:
            return layout("Scene", f"<h2>Scene not found</h2><p>{esc(scene_id)}</p>")
        fields = [
            ("Viewpoint", row["pov"]), ("Location", row["location"]),
            ("Present characters", row["present_characters"]), ("Goal", row["goal"]),
            ("Opposition", row["opposition"]), ("Turn", row["turn"]),
            ("Outcome", row["outcome"]), ("Major events", row["major_events"]),
            ("Assertions", row["linked_assertion_ids"]), ("Custody", row["linked_custody_ids"]),
            ("Promises", row["linked_promise_ids"]), ("Analytical states", row["linked_state_ids"]),
            ("Evaluation queries", row["linked_query_ids"]), ("Authority", row["authority"]),
        ]
        details = "".join(f"<dt>{esc(k)}</dt><dd>{esc(v)}</dd>" for k,v in fields)
        return layout(scene_id, f"""
<a class="back" href="/scenes">← All scenes</a>
<h2>{esc(scene_id)}</h2>
<dl class="detail-grid">{details}</dl>
<a class="button-link" href="/proposals/new?target_type=scene&target_id={esc(scene_id)}">Propose revision</a>
""")
    rows = conn.execute(
        """SELECT scene_id, chapter_index, scene_index_in_chapter, pov, location, outcome
           FROM scene_briefs ORDER BY CAST(chapter_index AS INTEGER), CAST(scene_index_in_chapter AS INTEGER)"""
    ).fetchall()
    conn.close()
    links = []
    for r in rows:
        links.append(
            f'<tr><td><a href="/scenes?id={esc(r["scene_id"])}">{esc(r["scene_id"])}</a></td>'
            f'<td>{esc(r["chapter_index"])}</td><td>{esc(r["pov"])}</td>'
            f'<td>{esc(r["location"])}</td><td>{esc(r["outcome"])}</td></tr>'
        )
    return layout("Scenes", f"""
<h2>Scene Browser</h2>
<div class="table-wrap"><table><thead><tr><th>Scene</th><th>Chapter</th><th>POV</th><th>Location</th><th>Outcome</th></tr></thead>
<tbody>{''.join(links)}</tbody></table></div>
""")


def knowledge_page(holder: str = "") -> str:
    conn = db()
    params = []
    where = ""
    if holder:
        where = "WHERE holder_name LIKE ? OR holder_id=?"
        params = [f"%{holder}%", holder]
    rows = conn.execute(
        f"""SELECT holder_name, epistemic_status, proposition, valid_from_scene,
                   valid_to_scene, assertion_id
            FROM knowledge_timeline {where}
            ORDER BY holder_name, valid_from_scene LIMIT 500""", params
    ).fetchall()
    holders = conn.execute(
        "SELECT DISTINCT holder_name FROM knowledge_timeline ORDER BY holder_name"
    ).fetchall()
    conn.close()
    options = '<option value="">All holders</option>' + "".join(
        f'<option {"selected" if h["holder_name"]==holder else ""}>{esc(h["holder_name"])}</option>'
        for h in holders
    )
    return layout("Knowledge", f"""
<h2>Character Knowledge Timeline</h2>
<form method="get" class="filter-form"><select name="holder">{options}</select><button>Filter</button></form>
<p class="warning">A character's presence in a scene does not prove knowledge. These records require holder-specific evidence.</p>
{rows_to_table(rows, ["holder_name","epistemic_status","proposition","valid_from_scene","valid_to_scene","assertion_id"])}
""")


def custody_page(object_id: str = "") -> str:
    conn = db()
    params = []
    where = ""
    if object_id:
        where = "WHERE object_id=? OR object_name LIKE ?"
        params = [object_id, f"%{object_id}%"]
    rows = conn.execute(
        f"""SELECT object_name, holder_or_location, custody_type, start_scene,
                   end_scene, change_event, continuity_risk, terminal, record_id
            FROM custody_timeline {where}
            ORDER BY object_name, start_scene LIMIT 500""", params
    ).fetchall()
    conn.close()
    return layout("Custody", f"""
<h2>Object Custody Timeline</h2>
<form method="get" class="search-form"><input name="object" value="{esc(object_id)}" placeholder="Treaty, pistol, Emitter..."><button>Filter</button></form>
{rows_to_table(rows, ["object_name","holder_or_location","custody_type","start_scene","end_scene","change_event","continuity_risk","terminal","record_id"])}
""")


def promises_page(bucket: str = "") -> str:
    conn = db()
    where = "WHERE board_bucket=?" if bucket else ""
    rows = conn.execute(
        f"""SELECT promise_id, board_bucket, scene, change_type, status, description
            FROM promise_board {where}
            ORDER BY promise_id, scene""", ([bucket] if bucket else [])
    ).fetchall()
    buckets = conn.execute("SELECT DISTINCT board_bucket FROM promise_board ORDER BY board_bucket").fetchall()
    conn.close()
    options = '<option value="">All states</option>' + "".join(
        f'<option {"selected" if b["board_bucket"]==bucket else ""}>{esc(b["board_bucket"])}</option>'
        for b in buckets
    )
    return layout("Promises", f"""
<h2>Promise and Payoff Board</h2>
<form method="get" class="filter-form"><select name="bucket">{options}</select><button>Filter</button></form>
{rows_to_table(rows, ["promise_id","board_bucket","scene","change_type","status","description"])}
""")


def continuity_page(bucket: str = "") -> str:
    conn = db()
    where = "WHERE dashboard_bucket=?" if bucket else ""
    rows = conn.execute(
        f"""SELECT issue_id, category, dashboard_bucket, decision, classification,
                   confirmed_error, reason, graph_action
            FROM continuity_dashboard {where} ORDER BY issue_id""", ([bucket] if bucket else [])
    ).fetchall()
    buckets = conn.execute("SELECT DISTINCT dashboard_bucket FROM continuity_dashboard ORDER BY dashboard_bucket").fetchall()
    conn.close()
    options = '<option value="">All classifications</option>' + "".join(
        f'<option {"selected" if b["dashboard_bucket"]==bucket else ""}>{esc(b["dashboard_bucket"])}</option>'
        for b in buckets
    )
    return layout("Continuity", f"""
<h2>Continuity Dashboard</h2>
<form method="get" class="filter-form"><select name="bucket">{options}</select><button>Filter</button></form>
<p class="warning">Warnings and model limitations are not confirmed manuscript errors.</p>
{rows_to_table(rows, ["issue_id","category","dashboard_bucket","decision","classification","confirmed_error","reason","graph_action"])}
""")


def arcs_page(holder: str = "") -> str:
    conn = db()
    params = []
    where = ""
    if holder:
        where = "WHERE holder_labels LIKE ? OR holder_ids LIKE ?"
        params = [f"%{holder}%", f"%{holder}%"]
    rows = conn.execute(
        f"""SELECT scene_id, state_type, holder_labels, description, authority, interpretive, state_id
            FROM analytical_state_map {where} ORDER BY scene_id""", params
    ).fetchall()
    conn.close()
    return layout("Arcs", f"""
<h2>Character and Relationship Arc Map</h2>
<form method="get" class="search-form"><input name="holder" value="{esc(holder)}" placeholder="Jonah, Margot, relationship..."><button>Filter</button></form>
<p class="warning">These are author-approved analytical canon, not literal manuscript statements.</p>
{rows_to_table(rows, ["scene_id","state_type","holder_labels","description","authority","interpretive","state_id"])}
""")


def impact_for(conn: sqlite3.Connection, target_type: str, target_id: str) -> list[dict]:
    frontier = [(target_type, target_id, 0)]
    seen = {(target_type, target_id)}
    impacts = []
    while frontier:
        ttype, tid, depth = frontier.pop(0)
        if depth >= 2:
            continue
        rows = conn.execute(
            """SELECT source_type, source_id, relationship, certainty, target_type, target_id
               FROM dependency_index WHERE target_type=? AND target_id=?""",
            (ttype, tid)
        ).fetchall()
        for row in rows:
            item = dict(row)
            item["depth"] = depth + 1
            impacts.append(item)
            node = (row["source_type"], row["source_id"])
            if node not in seen:
                seen.add(node)
                frontier.append((node[0], node[1], depth + 1))
    return impacts


def proposals_page() -> str:
    conn = db()
    rows = conn.execute(
        """SELECT proposal_id, created_at, status, action_id, target_type, target_id,
                  proposed_change, reason FROM revision_proposals ORDER BY created_at DESC"""
    ).fetchall()
    conn.close()
    return layout("Revision Proposals", f"""
<div class="title-row"><h2>Revision Proposals</h2><a class="button-link" href="/proposals/new">New proposal</a></div>
<p>Proposals may generate impact reports. They cannot alter frozen canon.</p>
{rows_to_table(rows, ["proposal_id","created_at","status","action_id","target_type","target_id","proposed_change","reason"])}
""")


def proposal_form(params: dict[str, list[str]]) -> str:
    target_type = params.get("target_type", ["scene"])[0]
    target_id = params.get("target_id", [""])[0]
    return layout("New Revision Proposal", f"""
<h2>New Revision Proposal</h2>
<form method="post" class="proposal-form">
<label>Action
<select name="action_id">
<option>ACTION-PROPOSE-SCENE-REVISION</option>
<option>ACTION-CORRECT-CANON-RECORD</option>
<option>ACTION-REPAIR-CUSTODY-INTERVAL</option>
<option>ACTION-CLOSE-PROMISE</option>
<option>ACTION-REOPEN-PROMISE</option>
</select></label>
<label>Target type<input name="target_type" value="{esc(target_type)}" required></label>
<label>Target ID<input name="target_id" value="{esc(target_id)}" required></label>
<label>Proposed change<textarea name="proposed_change" required></textarea></label>
<label>Reason<textarea name="reason" required></textarea></label>
<button>Create proposal and analyze impact</button>
</form>
""")


def create_proposal(params: dict[str, list[str]]) -> tuple[str, str]:
    required = ["action_id","target_type","target_id","proposed_change","reason"]
    values = {k: params.get(k, [""])[0].strip() for k in required}
    if any(not values[k] for k in required):
        return "400 Bad Request", layout("Proposal Error", "<h2>Missing required proposal fields.</h2>")
    proposal_id = "PROP-" + uuid.uuid4().hex[:10].upper()
    now = datetime.now(timezone.utc).isoformat()
    conn = db()
    impacts = impact_for(conn, values["target_type"], values["target_id"])
    conn.execute(
        """INSERT INTO revision_proposals
           (proposal_id, created_at, status, action_id, target_type, target_id,
            proposed_change, reason, canon_version)
           VALUES (?, ?, 'READY_FOR_REVIEW', ?, ?, ?, ?, ?, ?)""",
        (proposal_id, now, values["action_id"], values["target_type"],
         values["target_id"], values["proposed_change"], values["reason"], CANON_VERSION)
    )
    for impact in impacts:
        conn.execute(
            """INSERT INTO proposal_impacts
               (proposal_id, depth, impacted_type, impacted_id, relationship, certainty)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (proposal_id, impact["depth"], impact["source_type"], impact["source_id"],
             impact["relationship"], impact["certainty"])
        )
    event = {
        "proposal_id": proposal_id,
        "target": [values["target_type"], values["target_id"]],
        "impact_count": len(impacts),
    }
    conn.execute(
        """INSERT INTO proposal_events (proposal_id, event_type, created_at, payload_json)
           VALUES (?, 'IMPACT_READY', ?, ?)""",
        (proposal_id, now, json.dumps(event))
    )
    conn.commit()
    conn.close()
    return "303 See Other", ""


def static_file(path: str):
    if path != "/static/style.css":
        return None
    css_path = APP_DIR / "static" / "style.css"
    return css_path.read_text(encoding="utf-8")


def application(environ, start_response):
    path = environ.get("PATH_INFO", "/")
    method = environ.get("REQUEST_METHOD", "GET")
    query = parse_qs(environ.get("QUERY_STRING", ""), keep_blank_values=True)

    css = static_file(path)
    if css is not None:
        return response(start_response, css, content_type="text/css; charset=utf-8")

    if path == "/" and method == "GET":
        return response(start_response, dashboard())
    if path == "/search" and method == "GET":
        return response(start_response, search_page(query.get("q", [""])[0]))
    if path == "/scenes" and method == "GET":
        return response(start_response, scenes_page(query.get("id", [None])[0]))
    if path == "/knowledge" and method == "GET":
        return response(start_response, knowledge_page(query.get("holder", [""])[0]))
    if path == "/custody" and method == "GET":
        return response(start_response, custody_page(query.get("object", [""])[0]))
    if path == "/promises" and method == "GET":
        return response(start_response, promises_page(query.get("bucket", [""])[0]))
    if path == "/continuity" and method == "GET":
        return response(start_response, continuity_page(query.get("bucket", [""])[0]))
    if path == "/arcs" and method == "GET":
        return response(start_response, arcs_page(query.get("holder", [""])[0]))
    if path == "/proposals" and method == "GET":
        return response(start_response, proposals_page())
    if path == "/proposals/new" and method == "GET":
        return response(start_response, proposal_form(query))
    if path == "/proposals/new" and method == "POST":
        try:
            length = int(environ.get("CONTENT_LENGTH") or "0")
        except ValueError:
            length = 0
        params = parse_qs(environ["wsgi.input"].read(length).decode("utf-8"), keep_blank_values=True)
        status, body = create_proposal(params)
        if status.startswith("303"):
            start_response(status, [("Location", "/proposals")])
            return [b""]
        return response(start_response, body, status=status)

    return response(start_response, layout("Not Found", "<h2>Not found</h2>"), status="404 Not Found")


if __name__ == "__main__":
    host = os.environ.get("STORY_GRAPH_HOST", "127.0.0.1")
    port = int(os.environ.get("STORY_GRAPH_PORT", "8765"))
    print(f"Story Graph OS running at http://{host}:{port}")
    with make_server(host, port, application) as server:
        server.serve_forever()
