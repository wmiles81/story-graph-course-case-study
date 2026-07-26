#!/usr/bin/env python3
"""Story Graph — local browser app (the Act-III "operating system").

A thin, single-user, localhost-only web face over the story-graph engine. It
serves one tabbed page with:
  - Dashboard : counts + quick facts (stdlib)
  - Graph     : an interactive node-link view (self-authored JS force renderer)
  - Query     : an ad-hoc Cypher console over the compiled Kùzu graph
  - Reports   : run report / audit / deviations / queue

No web framework (stdlib http.server). The only optional dependency is `kuzu`,
used for the Cypher console and the kuzu-backed reports; without it the app still
runs (dashboard, graph, deviations, queue) and says the Cypher tab is disabled.

Usage:
    python3 app/story_graph_app.py <Story-Graph.md> [--chapters-dir <dir>] [--port 8765]
"""
from __future__ import annotations

import argparse
import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
ASSETS = APP_DIR.parent / "story-graph" / "assets"
sys.path.insert(0, str(ASSETS))
import story_graph as sg  # noqa: E402

STATE = {"path": None, "text": "", "graph": None, "chapters_dir": "", "conn": None, "kuzu_err": "",
         "provider": "", "model": "", "keys": {}}  # Ask-tab AI: provider/model + in-memory keys (never written to disk)

# Provider-neutral, OpenAI-compatible endpoints. Local servers need no key; cloud reads env or an in-memory key.
PROVIDERS = [
    {"name": "openrouter", "label": "OpenRouter", "base": "https://openrouter.ai/api/v1", "env": "OPENROUTER_API_KEY", "local": False},
    {"name": "ollama", "label": "Ollama (local)", "base": "http://localhost:11434/v1", "env": "", "local": True},
    {"name": "lmstudio", "label": "LM Studio (local)", "base": "http://localhost:1234/v1", "env": "", "local": True},
]
_PROV = {p["name"]: p for p in PROVIDERS}


def _provider_key(name):
    import os as _os
    p = _PROV.get(name) or {}
    return STATE.get("keys", {}).get(name) or (_os.environ.get(p.get("env", "")) if p.get("env") else "")


_SSL_CTX = None


def _ssl_ctx():
    """A verifying SSL context that works on macOS python.org builds (which ship
    no CA bundle) by using certifi's when available."""
    global _SSL_CTX
    if _SSL_CTX is None:
        import ssl
        try:
            import certifi
            _SSL_CTX = ssl.create_default_context(cafile=certifi.where())
        except Exception:
            _SSL_CTX = ssl.create_default_context()
    return _SSL_CTX


def _oai(base, path, key, payload=None, timeout=60):
    """One OpenAI-compatible request (GET /models or POST /chat/completions)."""
    import urllib.request
    headers = {"Content-Type": "application/json"}
    if key:
        headers["Authorization"] = "Bearer " + key
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(base.rstrip("/") + path, data=data, headers=headers,
                                 method="POST" if data is not None else "GET")
    with urllib.request.urlopen(req, timeout=timeout, context=_ssl_ctx()) as r:  # context ignored for http://
        return json.loads(r.read().decode("utf-8"))


def _chat(provider, model, system, user, max_tokens=2048):
    p = _PROV[provider]
    payload = {"model": model, "max_tokens": max_tokens,
               "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
    d = _oai(p["base"], "/chat/completions", _provider_key(provider), payload, timeout=90)
    return d["choices"][0]["message"]["content"]


def _reachable(name):
    p = _PROV.get(name)
    if not p:
        return False
    if not p["local"]:
        return bool(_provider_key(name))
    try:
        _oai(p["base"], "/models", "", None, timeout=1.5)
        return True
    except Exception:
        return False


def _jsonable(v):
    if isinstance(v, (str, int, float, bool)) or v is None:
        return v
    return str(v)


def load(graph_path, chapters_dir=""):
    STATE["path"] = graph_path
    STATE["chapters_dir"] = chapters_dir
    STATE["text"] = Path(graph_path).read_text(encoding="utf-8")
    STATE["graph"] = sg.parse_graph(STATE["text"])
    STATE["conn"] = None
    STATE["kuzu_err"] = ""
    try:
        import tempfile
        import story_graph_kuzu
        import kuzu
        db = str(Path(tempfile.mkdtemp(prefix="sg-app-")) / "g.kuzu")
        story_graph_kuzu.load_graph(STATE["graph"], db)
        STATE["conn"] = kuzu.Connection(kuzu.Database(db))
    except Exception as e:  # kuzu missing or compile failed
        STATE["kuzu_err"] = str(e)


def api_summary():
    g = STATE["graph"]
    S = g["sections"]
    def n(name):
        return len(S.get(name, []))
    commits = sum(1 for ln in g.get("_raw", {}).get("Canon Commit Log", [])
                  if ln.strip().startswith("- "))
    counts = {                                     # the full tracked inventory, in ontology order
        "sources": n("Sources"),
        "entities": n("Entities"),
        "locations & distances": n("Locations & Distances"),
        "relationships": n("Relationships"),
        "propositions": n("Propositions"),
        "epistemic states": n("Epistemic States"),
        "open loops & setups": n("Open Loops & Setups"),
        "evidence spans": n("Evidence"),
        "timeline rows": n("Timeline"),
        "logistics rows": n("Logistics"),
        "canon commits": commits,
        "local vocab": n("Local Vocabulary"),
    }
    if "spe" in g["modules"]:
        counts["physics state"] = n("Physics State")
    return {
        "title": STATE["text"].splitlines()[0].lstrip("# ").strip() if STATE["text"] else "Story Graph",
        "path": STATE["path"],
        "canon_chapter": g["canon_ch"],
        "modules": g["modules"],
        "kuzu": STATE["conn"] is not None,
        "kuzu_err": STATE["kuzu_err"],
        "counts": counts,
        "unratified": len(sg.unratified(g)),
    }


def api_graph(prop=""):
    nodes, edges = sg._viz_model(STATE["graph"], prop)
    return {
        "nodes": [{"id": nid, "kind": kind, "color": sg._VIZ_COLORS.get(kind, "#888")}
                  for nid, kind in nodes.items()],
        "edges": [{"from": u, "to": v, "label": lab} for u, v, lab in edges],
    }


def api_timeline():
    S = STATE["graph"]["sections"]
    stmt = {r.get("prop-id"): r.get("statement", "") for r in S.get("Propositions", [])}
    items, holders, maxch = [], set(), 1
    for r in S.get("Epistemic States", []):
        h, pid, ch = r.get("holder", ""), r.get("prop-id", ""), r.get("since-ch", "")
        if not h or not pid or not ch.isdigit():
            continue
        c = int(ch)
        holders.add(h)
        maxch = max(maxch, c)
        items.append({"chapter": c, "character": h, "stance": r.get("mode", ""),
                      "belief": stmt.get(pid, pid)})
    return {"holders": sorted(holders), "max_chapter": maxch, "items": items}


def api_cypher(cypher):
    if STATE["conn"] is None:
        return {"error": f"Cypher needs kuzu (pip install kuzu). {STATE['kuzu_err']}".strip()}
    try:
        res = STATE["conn"].execute(cypher)
        cols = res.get_column_names()
        rows = []
        while res.has_next():
            rows.append([_jsonable(v) for v in res.get_next()])
        return {"columns": cols, "rows": rows}
    except Exception as e:
        return {"error": str(e)}


def api_report(kind):
    g, path, ch = STATE["graph"], STATE["path"], STATE["chapters_dir"]
    if kind == "queue":
        rows = sg.unratified(g)
        return {"text": "Ratification queue is empty." if not rows else
                "\n".join(f"[{sec}] {lab}" for sec, lab in rows)}
    if kind == "deviations":
        if not ch:
            return {"text": "deviations needs --chapters-dir at app startup."}
        devs = sg.deviations(path, ch)
        return {"text": "No deviations — evidence still matches the prose." if not devs else
                "\n".join(f"[{loc}] {sid} (supports '{p}') — {r}" for sid, p, loc, r in devs)}
    if kind in ("report", "audit"):
        if STATE["conn"] is None:
            return {"text": f"{kind} needs kuzu (pip install kuzu)."}
        import story_graph_query
        if kind == "report":
            return {"text": story_graph_query.run_report(g, g["canon_ch"])}
        out, _ = story_graph_query.run_audit(g, g["canon_ch"])
        return {"text": out}
    return {"error": "unknown report"}


CYPHER_SCHEMA = """NODE TABLES
  Entity(id, type, status)            characters / objects / locations / factions
  Proposition(id, statement, canon_status)   canon_status: true|false|undetermined|contested
  Source(id, type, authority)         type: manuscript|bible|outline|editorial|draft|ghost-draft
  Evidence(id, locator, quote)        locator like 'ch01'
  OpenLoop(id, status, planted_ch, must_fire_by, expectation)   status: UNFIRED|FIRED
  Holder(id)                          who holds a belief; includes the reserved 'reader'
REL TABLES
  (Entity)-[RELATES {edge, since_ch}]->(Entity)          edge: trusts, protects, deceives, loves, ...
  (Holder)-[EPISTEMIC {mode, since_ch}]->(Proposition)   mode: knows, believes, believes-false, suspects, embargoed-until
  (Proposition)-[GOVERNED_BY]->(Source)
  (Evidence)-[SUPPORTS]->(Proposition)
  (Evidence)-[EVIDENCED_BY]->(OpenLoop)
NOTES
  since_ch is a STRING chapter number; order numerically with CAST(x AS INT64).
  Dramatic irony = the reader knows a proposition a character believes-false.
  All ids are lowercase kebab-case slugs — entities like 'jonah-harrow' / 'margot-vance',
  the reserved holder 'reader', propositions like 'p-b03-000007'. When the user names
  someone loosely ("Jonah", "Margot"), NEVER use equality on a display name — match the
  slug case-insensitively: WHERE toLower(e.id) CONTAINS 'jonah'  (not  e.id = 'Jonah')."""


def api_schema():
    return {"schema": CYPHER_SCHEMA}


def api_ask(question):
    """Natural-language question -> Claude -> a read-only Cypher query -> results.
    Uses the official Anthropic SDK (optional, like kuzu). Model claude-opus-5;
    override with ANTHROPIC_MODEL. Degrades with a clear message if unavailable."""
    if not (question or "").strip():
        return {"error": "Ask a question in plain English."}
    if STATE["conn"] is None:
        return {"error": "Cypher needs kuzu (pip install kuzu) and a compiled graph."}
    provider, model = STATE.get("provider"), STATE.get("model")
    if not provider or not model:
        return {"error": "Pick a provider and model in ⚙️ Settings → AI Model "
                         "(OpenRouter, or a local Ollama / LM Studio server)."}
    system = (
        "You translate a question about a novel's canon 'story graph' into ONE read-only Kùzu "
        "Cypher query. Use ONLY these tables and properties:\n\n" + CYPHER_SCHEMA +
        "\n\nReturn a single MATCH query — never CREATE/MERGE/SET/DELETE. Prefer RETURNing "
        "readable fields (entity/proposition ids and p.statement). Respond with ONLY a JSON "
        'object and nothing else: {"cypher": "<the query>", "explanation": "<one sentence>"}.')
    try:
        text = _chat(provider, model, system, question).strip()
    except Exception as e:
        label = (_PROV.get(provider) or {}).get("label", provider)
        return {"error": f"{label} call failed: {e}"}
    if text.startswith("```"):
        text = text.strip("`")
        text = text[text.find("{"):]
    try:
        obj = json.loads(text[text.find("{"): text.rfind("}") + 1])
    except Exception:
        return {"error": "the model did not return valid JSON", "raw": text[:400]}
    cypher = (obj.get("cypher") or "").strip()
    explanation = obj.get("explanation", "")
    if any(w in cypher.lower() for w in (" create ", " merge ", " set ", " delete ", " drop ", "detach ")):
        return {"cypher": cypher, "explanation": explanation, "error": "refusing to run a non-read-only query"}
    result = api_cypher(cypher)
    result["cypher"] = cypher
    result["explanation"] = explanation
    return result


def api_settings_get():
    provs = [{"name": p["name"], "label": p["label"], "local": p["local"],
              "key_set": bool(_provider_key(p["name"])), "reachable": _reachable(p["name"])}
             for p in PROVIDERS]
    return {"provider": STATE.get("provider") or "", "model": STATE.get("model") or "",
            "providers": provs, "kuzu": STATE["conn"] is not None}


def api_settings_put(patch):
    if "provider" in patch:
        STATE["provider"] = (patch.get("provider") or "").strip()
    if "model" in patch:
        STATE["model"] = (patch.get("model") or "").strip()
    if "api_key" in patch:  # held in memory only; never written to disk
        prov = (patch.get("provider") or STATE.get("provider") or "").strip()
        if prov:
            STATE.setdefault("keys", {})[prov] = (patch.get("api_key") or "").strip()
    return api_settings_get()


def api_models(provider):
    p = _PROV.get(provider)
    if not p:
        return {"error": "unknown provider", "models": []}
    if not p["local"] and not _provider_key(provider):
        return {"error": f"Add a key for {p['label']} first.", "models": []}
    try:
        d = _oai(p["base"], "/models", _provider_key(provider), None, timeout=20)
        ids = sorted({m.get("id") for m in (d.get("data") or []) if m.get("id")})
        return {"models": ids}
    except Exception as e:
        return {"error": str(e)[:200], "models": []}


def api_testkey(provider=None):
    prov = provider or STATE.get("provider")
    p = _PROV.get(prov)
    if not p:
        return {"ok": False, "detail": "Pick a provider first."}
    try:
        d = _oai(p["base"], "/models", _provider_key(prov), None, timeout=15)
        return {"ok": True, "detail": f"{p['label']} reachable · {len(d.get('data') or [])} models"}
    except Exception as e:
        return {"ok": False, "detail": str(e)[:200]}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, body, ctype="application/json", status=200):
        data = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _json(self, obj, status=200):
        self._send(json.dumps(obj), "application/json; charset=utf-8", status)

    def do_GET(self):
        from urllib.parse import urlparse, parse_qs
        u = urlparse(self.path)
        q = parse_qs(u.query)
        if u.path == "/":
            return self._send(PAGE, "text/html; charset=utf-8")
        if u.path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
            return
        if u.path == "/api/schema":
            return self._json(api_schema())
        if u.path == "/api/settings":
            return self._json(api_settings_get())
        if u.path == "/api/models":
            return self._json(api_models(q.get("provider", [""])[0]))
        if u.path == "/api/summary":
            return self._json(api_summary())
        if u.path == "/api/graph":
            return self._json(api_graph(q.get("prop", [""])[0]))
        if u.path == "/api/timeline":
            return self._json(api_timeline())
        if u.path == "/api/report":
            return self._json(api_report(q.get("kind", ["report"])[0]))
        return self._json({"error": "not found"}, 404)

    def do_POST(self):
        length = int(self.headers.get("Content-Length") or 0)
        payload = json.loads(self.rfile.read(length) or "{}")
        if self.path == "/api/cypher":
            return self._json(api_cypher(payload.get("cypher", "")))
        if self.path == "/api/ask":
            return self._json(api_ask(payload.get("question", "")))
        if self.path == "/api/settings":
            return self._json(api_settings_put(payload))
        if self.path == "/api/testkey":
            return self._json(api_testkey(payload.get("provider")))
        return self._json({"error": "not found"}, 404)


PAGE = r"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Story Graph OS</title>
<style>
:root{--bg:#eef1f5;--ink:#151c26;--muted:#586573;--panel:#f7f8fb;--line:#d5dce4;--accent:#0b7d84;--truth:#0e7c86;--irony:#b4531f}
@media(prefers-color-scheme:dark){:root{--bg:#0c121a;--ink:#e7edf4;--muted:#93a1b3;--panel:#141c26;--line:#243140;--accent:#37cfc7;--truth:#37cfc7;--irony:#e0894b}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 system-ui,-apple-system,'Segoe UI',sans-serif}
header{padding:14px 20px;border-bottom:1px solid var(--line);display:flex;align-items:baseline;gap:14px;flex-wrap:wrap}
h1{font:600 1.15rem 'Iowan Old Style',Palatino,Georgia,serif;margin:0}
.meta{font:12px ui-monospace,'SF Mono',monospace;color:var(--muted)}
nav{display:flex;gap:2px;padding:8px 16px;border-bottom:1px solid var(--line);flex-wrap:wrap}
nav button{font:13px system-ui;background:none;border:1px solid transparent;color:var(--muted);padding:.4rem .8rem;border-radius:8px;cursor:pointer}
nav button.on{background:var(--panel);border-color:var(--line);color:var(--ink)}
main{padding:18px 20px;max-width:1100px}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:.7rem;margin:.5rem 0 1rem}
.card{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:.9rem 1rem}
.card b{display:block;font:600 1.6rem 'Iowan Old Style',serif} .card span{color:var(--muted);font-size:.82rem}
.frame{background:var(--panel);border:1px solid var(--line);border-radius:12px;overflow:hidden}
svg{display:block;touch-action:none}
input[type=range]{accent-color:var(--accent)}
circle{cursor:grab} text{font:11px ui-monospace,monospace;fill:var(--ink);pointer-events:none}
.elab{fill:var(--muted);font-size:10px;text-anchor:middle}
.tlab{font:11px ui-monospace,monospace;fill:var(--muted)}
textarea{width:100%;height:90px;font:13px ui-monospace,monospace;background:var(--panel);color:var(--ink);border:1px solid var(--line);border-radius:10px;padding:.6rem}
.row{display:flex;gap:.6rem;align-items:center;margin:.5rem 0}
button.go{background:var(--accent);color:#fff;border:0;border-radius:8px;padding:.5rem .9rem;font:600 13px system-ui;cursor:pointer}
button.ghost{background:var(--panel);border:1px solid var(--line);color:var(--ink);border-radius:8px;padding:.45rem .8rem;cursor:pointer;font:13px system-ui}
table{border-collapse:collapse;width:100%;font:13px ui-monospace,monospace;margin-top:.6rem}
th,td{border:1px solid var(--line);padding:.35rem .5rem;text-align:left} th{background:var(--panel)}
pre{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:1rem;overflow:auto;white-space:pre-wrap;font:12.5px ui-monospace,monospace}
.err{color:var(--irony)} .hint{color:var(--muted);font-size:.85rem}
.legend{display:flex;flex-wrap:wrap;gap:.4rem 1rem;padding:.6rem 1rem;font:11px ui-monospace,monospace;color:var(--muted)}
.legend i{display:inline-block;width:.7rem;height:.7rem;border-radius:3px;margin-right:.35rem;vertical-align:-1px}
#gear{margin-left:auto;font:13px system-ui;background:var(--panel);border:1px solid var(--line);color:var(--ink);border-radius:8px;padding:.4rem .7rem;cursor:pointer}
.sm-overlay{position:fixed;inset:0;background:rgba(0,0,0,.45);display:flex;align-items:flex-start;justify-content:center;padding:6vh 16px;z-index:50}
.sm-modal{background:var(--bg);border:1px solid var(--line);border-radius:14px;width:min(680px,100%);max-height:86vh;overflow:auto;box-shadow:0 12px 48px rgba(0,0,0,.45)}
.sm-head{display:flex;align-items:center;justify-content:space-between;padding:16px 20px;border-bottom:1px solid var(--line)}
.sm-title-label{font:600 1.05rem 'Iowan Old Style',Georgia,serif} .sm-title-sub{color:var(--muted);font-size:.8rem;margin-left:.5rem}
.sm-close{background:none;border:0;color:var(--muted);font-size:1.4rem;line-height:1;cursor:pointer}
.sm-tabs{display:flex;gap:2px;padding:8px 14px;border-bottom:1px solid var(--line);flex-wrap:wrap}
.sm-tab{font:13px system-ui;background:none;border:1px solid transparent;color:var(--muted);padding:.4rem .8rem;border-radius:8px;cursor:pointer}
.sm-tab.on{background:var(--panel);border-color:var(--line);color:var(--ink)}
.sm-body{padding:16px 20px}
.sm-row{display:flex;flex-direction:column;gap:.25rem;padding:.75rem 0;border-bottom:1px solid var(--line)}
.sm-row-head{display:flex;align-items:center;justify-content:space-between;gap:1rem;flex-wrap:wrap}
.sm-label{font-weight:600} .sm-sub{color:var(--muted);font-size:.82rem}
.sm-seg{display:inline-flex;border:1px solid var(--line);border-radius:8px;overflow:hidden}
.sm-seg button{background:var(--panel);border:0;border-left:1px solid var(--line);color:var(--muted);padding:.35rem .7rem;cursor:pointer;font:13px system-ui}
.sm-seg button:first-child{border-left:0} .sm-seg button.on{background:var(--accent);color:#fff}
.sm-switch{display:inline-flex;align-items:center;gap:.5rem;background:var(--panel);border:1px solid var(--line);border-radius:999px;padding:.25rem .65rem;cursor:pointer;color:var(--muted);font:12px system-ui}
.sm-switch.on{color:var(--ink);border-color:var(--accent)}
.sm-switch i{width:.8rem;height:.8rem;border-radius:50%;background:var(--muted)} .sm-switch.on i{background:var(--accent)}
.sm-field{font:13px ui-monospace,monospace;background:var(--panel);color:var(--ink);border:1px solid var(--line);border-radius:8px;padding:.5rem .6rem}
.sm-ok{color:var(--truth)} .sm-bad{color:var(--irony)}
body{zoom:var(--a11y-scale,1);letter-spacing:var(--a11y-ls,normal);line-height:var(--a11y-lh,1.55)}
body.a11y-contrast{--bg:#000;--ink:#fff;--muted:#dcdcdc;--line:#7c7c7c;--panel:#0d0d0d}
body.a11y-dyslexia,body.a11y-dyslexia *{font-family:'OpenDyslexic','Comic Sans MS',Verdana,Tahoma,sans-serif!important;letter-spacing:.02em}
body.a11y-motion *{transition:none!important;animation:none!important}
body.a11y-minfont .hint,body.a11y-minfont .tlab,body.a11y-minfont .elab,body.a11y-minfont .nlab,body.a11y-minfont .meta{font-size:12px!important}
</style></head><body>
<header><h1>Story Graph OS</h1><span class="meta" id="hd"></span><button id="gear" title="Settings (display, AI model)">⚙️ Settings</button></header>
<nav id="nav"></nav>
<main id="main"></main>
<script>
const $=(h)=>{const d=document.createElement('div');d.innerHTML=h;return d.firstElementChild};
const api=async(p,o)=>(await fetch(p,o)).json();
let TAB='dashboard';
const TABS=['dashboard','graph','timeline','query','ask','reports'];
const esc=(s)=>String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
function nav(){const n=document.getElementById('nav');n.innerHTML='';TABS.forEach(t=>{const b=document.createElement('button');b.textContent=t[0].toUpperCase()+t.slice(1);b.className=t===TAB?'on':'';b.onclick=()=>{TAB=t;render()};n.appendChild(b)})}
async function render(){nav();const m=document.getElementById('main');m.innerHTML='<p class="hint">loading…</p>';
 if(TAB==='dashboard')return dashboard(m);
 if(TAB==='graph')return graph(m);
 if(TAB==='timeline')return timeline(m);
 if(TAB==='query')return query(m);
 if(TAB==='ask')return ask(m);
 if(TAB==='reports')return reports(m);}
async function head(){const s=await api('/api/summary');document.getElementById('hd').textContent=`${s.title} · canon ch${s.canon_chapter} · modules: ${s.modules.length?s.modules.join(','):'none'} · kuzu:${s.kuzu?'on':'off'}`;return s}
async function dashboard(m){const s=await api('/api/summary');m.innerHTML='';const cards=document.createElement('div');cards.className='cards';
 const entries=Object.entries(s.counts).concat([['unratified (queue)',s.unratified]]);
 entries.forEach(([k,v])=>{cards.appendChild($(`<div class="card"><b>${v}</b><span>${k}</span></div>`))});
 m.appendChild(cards);
 m.appendChild($(`<p class="hint">Graph loaded from <code>${s.path}</code>. ${s.kuzu?'Kùzu is on — Cypher + audit available.':'Kùzu is off — Cypher/audit disabled ('+ (s.kuzu_err||'kuzu not installed') +').'}</p>`));}
async function graph(m){m.innerHTML='';
 const bar=$(`<div class="row"><input id="focus" placeholder="focus on a proposition id (blank = whole graph)" style="flex:1;font:13px ui-monospace,monospace;background:var(--panel);color:var(--ink);border:1px solid var(--line);border-radius:8px;padding:.45rem .6rem"><button class="go" id="fbtn">Draw</button></div>`);m.appendChild(bar);
 const leg=$(`<div class="legend"></div>`);m.appendChild(leg);
 const zrow=$(`<div class="row"><label class="hint" style="min-width:3rem">zoom</label><input id="zoom" type="range" min="100" max="500" value="100" style="flex:1"><span class="hint" id="zlab">fit</span></div>`);m.appendChild(zrow);
 const frame=$(`<div class="frame" style="overflow:auto;max-height:72vh"><svg id="gv" style="width:100%;height:560px"></svg></div>`);m.appendChild(frame);
 const hint=$(`<p class="hint"></p>`);m.appendChild(hint);
 const applyZoom=()=>{const z=+document.getElementById('zoom').value,gv=document.getElementById('gv');gv.style.width=z+'%';gv.style.height=(560*z/100)+'px';document.getElementById('zlab').textContent=z==100?'fit':z/100+'×'};
 document.getElementById('zoom').oninput=applyZoom;
 async function go(){const p=document.getElementById('focus').value.trim();const d=await api('/api/graph?prop='+encodeURIComponent(p));
  leg.innerHTML='';[...new Set(d.nodes.map(n=>n.kind))].forEach(k=>{const c=(d.nodes.find(n=>n.kind===k)||{}).color;leg.appendChild($(`<span><i style="background:${c}"></i>${k}</span>`))});
  hint.textContent=`${d.nodes.length} nodes · ${d.edges.length} edges · drag nodes to rearrange · slide zoom to read labels`;
  if(!d.nodes.length){hint.textContent='No such proposition. Leave the box blank for the whole graph.';return}
  applyZoom();draw(d)}
 document.getElementById('fbtn').onclick=go;
 document.getElementById('focus').addEventListener('keydown',e=>{if(e.key==='Enter')go()});
 go();}
function draw(d){const svg=document.getElementById('gv');const W=svg.clientWidth||900,H=560;
 const N=d.nodes.map(n=>({...n,x:W/2+Math.cos(Math.random()*6.28)*180,y:H/2+Math.sin(Math.random()*6.28)*140,vx:0,vy:0}));
 const idx=Object.fromEntries(N.map((n,i)=>[n.id,i]));
 const E=d.edges.filter(e=>e.from in idx&&e.to in idx).map(e=>({s:idx[e.from],t:idx[e.to],label:e.label}));
 const k=0.9*Math.sqrt(W*H/Math.max(1,N.length));
 for(let it=0;it<300;it++){for(const a of N){a.fx=0;a.fy=0}
  for(let i=0;i<N.length;i++)for(let j=i+1;j<N.length;j++){let dx=N[i].x-N[j].x,dy=N[i].y-N[j].y,dd=Math.hypot(dx,dy)||.01,f=k*k/dd;N[i].fx+=dx/dd*f;N[i].fy+=dy/dd*f;N[j].fx-=dx/dd*f;N[j].fy-=dy/dd*f}
  for(const e of E){let a=N[e.s],b=N[e.t],dx=a.x-b.x,dy=a.y-b.y,dd=Math.hypot(dx,dy)||.01,f=dd*dd/k;a.fx-=dx/dd*f;a.fy-=dy/dd*f;b.fx+=dx/dd*f;b.fy+=dy/dd*f}
  for(const a of N){a.fx+=(W/2-a.x)*.03;a.fy+=(H/2-a.y)*.03;const dl=Math.hypot(a.fx,a.fy)||.01,t=Math.max(1.5,W*0.05*(1-it/300));a.x+=a.fx/dl*Math.min(dl,t);a.y+=a.fy/dl*Math.min(dl,t)}}
 const NS='http://www.w3.org/2000/svg';svg.setAttribute('viewBox',`0 0 ${W} ${H}`);svg.innerHTML='';
 for(const e of E){const l=document.createElementNS(NS,'line');l.setAttribute('x1',N[e.s].x);l.setAttribute('y1',N[e.s].y);l.setAttribute('x2',N[e.t].x);l.setAttribute('y2',N[e.t].y);l.setAttribute('stroke','var(--line)');l.setAttribute('stroke-width','1.5');l.dataset.s=e.s;l.dataset.t=e.t;svg.appendChild(l)}
 for(const e of E){if(!e.label)continue;const tx=document.createElementNS(NS,'text');tx.setAttribute('class','elab');tx.setAttribute('x',(N[e.s].x+N[e.t].x)/2);tx.setAttribute('y',(N[e.s].y+N[e.t].y)/2-4);tx.textContent=e.label;tx.dataset.es=e.s;tx.dataset.et=e.t;svg.appendChild(tx)}
 N.forEach((n,i)=>{const c=document.createElementNS(NS,'circle');c.setAttribute('cx',n.x);c.setAttribute('cy',n.y);c.setAttribute('r',8);c.setAttribute('fill',n.color);c.dataset.i=i;svg.appendChild(c);
  const t=document.createElementNS(NS,'text');t.setAttribute('x',n.x+11);t.setAttribute('y',n.y+4);t.textContent=n.id;t.dataset.ti=i;svg.appendChild(t)});
 function moveNode(i){
  svg.querySelectorAll('circle').forEach(c=>{if(+c.dataset.i===i){c.setAttribute('cx',N[i].x);c.setAttribute('cy',N[i].y)}});
  svg.querySelectorAll('text[data-ti]').forEach(t=>{if(+t.dataset.ti===i){t.setAttribute('x',N[i].x+11);t.setAttribute('y',N[i].y+4)}});
  svg.querySelectorAll('line').forEach(l=>{if(+l.dataset.s===i){l.setAttribute('x1',N[i].x);l.setAttribute('y1',N[i].y)}if(+l.dataset.t===i){l.setAttribute('x2',N[i].x);l.setAttribute('y2',N[i].y)}});
  svg.querySelectorAll('text[data-es]').forEach(t=>{const s=+t.dataset.es,e=+t.dataset.et;if(s===i||e===i){t.setAttribute('x',(N[s].x+N[e].x)/2);t.setAttribute('y',(N[s].y+N[e].y)/2-4)}});}
 let drag=null;svg.onpointerdown=ev=>{if(ev.target.dataset.i!=null){drag=+ev.target.dataset.i;svg.setPointerCapture(ev.pointerId)}};
 svg.onpointermove=ev=>{if(drag==null)return;const r=svg.getBoundingClientRect();N[drag].x=(ev.clientX-r.left)*(W/r.width);N[drag].y=(ev.clientY-r.top)*(H/r.height);moveNode(drag)};
 svg.onpointerup=()=>{drag=null};}
async function timeline(m){m.innerHTML='';const d=await api('/api/timeline');
 if(!d.items.length){m.innerHTML='<p class="hint">No epistemic states with chapter numbers to plot.</p>';return}
 const ST={knows:'#0e9488',believes:'#3b6ea5','believes-false':'#c0632a',suspects:'#7a5cba','embargoed-until':'#8a97a5'};
 const leg=$(`<div class="legend"></div>`);Object.entries(ST).forEach(([k,c])=>leg.appendChild($(`<span><i style="background:${c}"></i>${k}</span>`)));m.appendChild(leg);
 const Hs=d.holders,maxc=Math.max(1,d.max_chapter),lane=46,L=170,T=32,R=26,B=16;
 const W=Math.max(680,L+R+maxc*52),height=T+Hs.length*lane+B;
 const x=c=>L+(maxc===1?0:(c-1)/(maxc-1))*(W-L-R),y=i=>T+i*lane+lane/2;
 let s='';
 Hs.forEach((h,i)=>{s+=`<line x1="${L}" y1="${y(i)}" x2="${W-R}" y2="${y(i)}" stroke="var(--line)"/><text x="${L-12}" y="${y(i)+4}" text-anchor="end" class="tlab">${esc(h)}</text>`});
 for(let c=1;c<=maxc;c++){if(maxc>18&&c%2===0)continue;s+=`<line x1="${x(c)}" y1="${T-4}" x2="${x(c)}" y2="${height-B}" stroke="var(--line)" opacity=".4"/><text x="${x(c)}" y="${T-12}" text-anchor="middle" class="tlab">${c}</text>`}
 const cnt={};d.items.forEach(it=>{const key=it.character+'|'+it.chapter,n=(cnt[key]=(cnt[key]||0)+1)-1,hi=Hs.indexOf(it.character);
  const cx=x(it.chapter)+(n%3-1)*8,cy=y(hi)+(Math.floor(n/3))*10-((Math.floor(n/3))?4:0);
  s+=`<circle cx="${cx.toFixed(1)}" cy="${cy.toFixed(1)}" r="6" fill="${ST[it.stance]||'#8a97a5'}" style="cursor:pointer" data-b="${encodeURIComponent(it.character+' — '+it.stance+' · ch'+it.chapter+': '+it.belief)}"><title>${esc(it.character+' — '+it.stance+' (ch'+it.chapter+')\n'+it.belief)}</title></circle>`});
 const frame=$(`<div class="frame" style="overflow:auto"><svg viewBox="0 0 ${W} ${height}" style="min-width:${W}px;height:${height}px">${s}</svg></div>`);m.appendChild(frame);
 const cap=$(`<p class="hint">Time runs left→right (chapter); each row is a character. Hover a dot for the belief, or click to pin it here.</p>`);m.appendChild(cap);
 frame.querySelectorAll('circle').forEach(c=>{c.onclick=()=>{cap.textContent=decodeURIComponent(c.dataset.b)}});}
async function ask(m){m.innerHTML='';
 m.appendChild($(`<p class="hint">Ask in plain English — the model you set in <b>⚙️ Settings → AI Model</b> (OpenRouter, or a local Ollama / LM Studio server) turns it into a Cypher query, runs it, and shows both. No API key needed for local models.</p>`));
 const ta=$(`<textarea placeholder="e.g. which propositions does the reader know that a character believes are false?">Which propositions does the reader know that a character believes are false?</textarea>`);m.appendChild(ta);
 const row=$(`<div class="row"></div>`);const btn=$(`<button class="go">Ask</button>`);row.appendChild(btn);m.appendChild(row);
 const out=$(`<div></div>`);m.appendChild(out);
 const sch=await api('/api/schema');
 m.appendChild($(`<details style="margin-top:1rem"><summary class="hint">Cypher rules — the schema the AI is given</summary><pre>${esc(sch.schema||'')}</pre></details>`));
 btn.onclick=async()=>{out.innerHTML='<p class="hint">asking Claude…</p>';
  const r=await api('/api/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:ta.value})});
  let h='';
  if(r.cypher)h+=`<p class="hint"><b>Generated Cypher</b> — ${esc(r.explanation||'')}</p><pre>${esc(r.cypher)}</pre>`;
  if(r.error){h+=`<p class="err">${esc(r.error)}</p>`+(r.raw?`<pre>${esc(r.raw)}</pre>`:'');out.innerHTML=h;return}
  h+='<table><thead><tr>'+r.columns.map(c=>`<th>${esc(c)}</th>`).join('')+'</tr></thead><tbody>';
  h+=r.rows.map(rw=>'<tr>'+rw.map(v=>`<td>${v==null?'':esc(String(v))}</td>`).join('')+'</tr>').join('');
  h+='</tbody></table><p class="hint">'+r.rows.length+' row(s)</p>';out.innerHTML=h};}
async function query(m){m.innerHTML='';const s=await api('/api/summary');
 m.appendChild($(`<p class="hint">Ad-hoc Cypher over the compiled graph. Node tables: Entity, Proposition, Source, Evidence, OpenLoop, Holder. Rel tables: RELATES, EPISTEMIC, GOVERNED_BY, EVIDENCED_BY, SUPPORTS.</p>`));
 const ta=$(`<textarea>MATCH (h:Holder)-[e:EPISTEMIC]->(p:Proposition) RETURN h.id, e.mode, e.since_ch, p.id ORDER BY e.since_ch LIMIT 25</textarea>`);m.appendChild(ta);
 const rowdiv=$(`<div class="row"></div>`);const btn=$(`<button class="go">Run</button>`);rowdiv.appendChild(btn);m.appendChild(rowdiv);
 const out=$(`<div></div>`);m.appendChild(out);
 if(!s.kuzu){out.innerHTML='<p class="err">Kùzu is off — install it (pip install kuzu) and restart to enable the console.</p>';btn.disabled=true;return}
 btn.onclick=async()=>{out.innerHTML='<p class="hint">running…</p>';const r=await api('/api/cypher',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({cypher:ta.value})});
  if(r.error){out.innerHTML=`<p class="err">${r.error}</p>`;return}
  let h='<table><thead><tr>'+r.columns.map(c=>`<th>${c}</th>`).join('')+'</tr></thead><tbody>';
  h+=r.rows.map(row=>'<tr>'+row.map(v=>`<td>${v==null?'':String(v)}</td>`).join('')+'</tr>').join('');
  h+='</tbody></table><p class="hint">'+r.rows.length+' row(s)</p>';out.innerHTML=h};}
async function reports(m){m.innerHTML='';const bar=$(`<div class="row"></div>`);
 ['report','audit','deviations','queue'].forEach(k=>{const b=$(`<button class="ghost">${k}</button>`);b.onclick=async()=>{pre.textContent='running…';const r=await api('/api/report?kind='+k);pre.textContent=r.text||r.error||''};bar.appendChild(b)});
 m.appendChild(bar);const pre=$(`<pre>Pick a report above.</pre>`);m.appendChild(pre);}
// ---- Settings modal (adapted from the Novel Machine authoring UI) ----
const A11Y_KEY='sgos.a11y';
const a11yRead=()=>{try{return JSON.parse(localStorage.getItem(A11Y_KEY))||{}}catch(_){return{}}};
const a11ySave=a=>localStorage.setItem(A11Y_KEY,JSON.stringify(a));
function a11yApply(a){const r=document.documentElement,b=document.body;
 r.style.setProperty('--a11y-scale',({s:.9,m:1,l:1.15,xl:1.35})[a.textSize||'m']);
 r.style.setProperty('--a11y-ls',({normal:'normal',wide:'.03em',xwide:'.06em'})[a.letterSpacing||'normal']);
 r.style.setProperty('--a11y-lh',({normal:'1.55',relaxed:'1.75',loose:'2'})[a.lineHeight||'normal']);
 b.classList.toggle('a11y-contrast',a.contrast==='high');
 b.classList.toggle('a11y-dyslexia',!!a.dyslexia);
 b.classList.toggle('a11y-motion',!!a.reduceMotion);
 b.classList.toggle('a11y-minfont',!!a.minFont);}
let SETTINGS_TAB='display';
function openSettings(){
 const ov=$(`<div class="sm-overlay"></div>`),modal=$(`<div class="sm-modal"></div>`);ov.appendChild(modal);
 const close=()=>{ov.remove();document.removeEventListener('keydown',onKey)};
 const onKey=e=>{if(e.key==='Escape')close()};document.addEventListener('keydown',onKey);
 ov.addEventListener('mousedown',e=>{if(e.target===ov)close()});
 modal.innerHTML=`<div class="sm-head"><div><span class="sm-title-label">Settings</span><span class="sm-title-sub">display &amp; AI model</span></div><button class="sm-close" title="Close (Esc)">×</button></div><div class="sm-tabs"></div><div class="sm-body"></div>`;
 modal.querySelector('.sm-close').onclick=close;
 const tabs=modal.querySelector('.sm-tabs'),body=modal.querySelector('.sm-body');
 const T=[['display','Display'],['model','AI Model'],['about','About']];
 const paint=()=>{tabs.innerHTML='';T.forEach(([k,l])=>{const btn=$(`<button class="sm-tab${k===SETTINGS_TAB?' on':''}">${l}</button>`);btn.onclick=()=>{SETTINGS_TAB=k;paint()};tabs.appendChild(btn)});
  body.innerHTML='';(SETTINGS_TAB==='display'?smDisplay:SETTINGS_TAB==='model'?smModel:smAbout)(body)};
 document.body.appendChild(ov);paint();
}
function smDisplay(body){const a=a11yRead();
 const commit=p=>{Object.assign(a,p);a11yApply(a);a11ySave(a);smDisplay(body)};
 const seg=(f,opts,def)=>{const s=$(`<div class="sm-seg"></div>`);opts.forEach(([id,lbl])=>{const btn=$(`<button class="${(a[f]||def)===id?'on':''}">${lbl}</button>`);btn.onclick=()=>commit({[f]:id});s.appendChild(btn)});return s};
 const toggle=f=>{const on=!!a[f],btn=$(`<button class="sm-switch${on?' on':''}"><i></i>${on?'On':'Off'}</button>`);btn.onclick=()=>commit({[f]:!on});return btn};
 const row=(label,sub,ctrl)=>{const r=$(`<div class="sm-row"><div class="sm-row-head"><span class="sm-label">${label}</span></div>${sub?`<span class="sm-sub">${sub}</span>`:''}</div>`);r.querySelector('.sm-row-head').appendChild(ctrl);return r};
 body.appendChild($(`<p class="hint">Display &amp; reading preferences. Applied immediately and saved on this device.</p>`));
 body.appendChild(row('Contrast','High contrast maximizes text/background separation.',seg('contrast',[['normal','Normal'],['high','High']],'normal')));
 body.appendChild(row('Text size','Scales the whole interface.',seg('textSize',[['s','S'],['m','M'],['l','L'],['xl','XL']],'m')));
 body.appendChild(row('Letter spacing','Extra space between letters can aid readability.',seg('letterSpacing',[['normal','Normal'],['wide','Wide'],['xwide','Extra']],'normal')));
 body.appendChild(row('Line height','More space between lines of text.',seg('lineHeight',[['normal','Normal'],['relaxed','Relaxed'],['loose','Loose']],'normal')));
 body.appendChild(row('Readable font','A legible sans (OpenDyslexic if the font is installed).',toggle('dyslexia')));
 body.appendChild(row('Reduce motion','Minimize animations and transitions.',toggle('reduceMotion')));
 body.appendChild(row('Minimum text size','Keep interface text at least 12px.',toggle('minFont')));
}
async function smModel(body){
 const s=await api('/api/settings');
 const post=(patch)=>api('/api/settings',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(patch)});
 body.appendChild($(`<p class="hint">The AI behind the <b>Ask</b> tab. Pick a provider, then a model. Keys are held in memory for this session only — never written to disk. Local providers (Ollama, LM Studio) need no key — the dot shows reachability.</p>`));
 // provider
 const prow=$(`<div class="sm-row"><div class="sm-row-head"><span class="sm-label">Provider</span></div></div>`);
 const psel=$(`<select class="sm-field"></select>`);
 const o0=document.createElement('option');o0.value='';o0.textContent='— provider —';psel.appendChild(o0);
 s.providers.forEach(p=>{const o=document.createElement('option');o.value=p.name;o.textContent=p.label+(p.local?(p.reachable?' ●':' ○'):(p.key_set?' ✓':''));if(p.name===s.provider)o.selected=true;psel.appendChild(o)});
 psel.onchange=async()=>{await post({provider:psel.value,model:''});smModel(body)};
 prow.querySelector('.sm-row-head').appendChild(psel);body.appendChild(prow);
 const cur=s.providers.find(p=>p.name===s.provider);
 // key (cloud only)
 if(cur && !cur.local){
  const krow=$(`<div class="sm-row"><div class="sm-row-head"><span class="sm-label">${cur.label} key</span><span class="sm-sub">${cur.key_set?'active':'not set'}</span></div></div>`);
  const kw=$(`<div class="row"></div>`),kin=$(`<input class="sm-field" style="flex:1" type="password" placeholder="${cur.key_set?'•••• (blank keeps current)':'API key'}" autocomplete="off">`);
  const ksave=$(`<button class="go">Save</button>`),kstat=$(`<span class="sm-sub"></span>`);
  kw.appendChild(kin);kw.appendChild(ksave);krow.appendChild(kw);krow.appendChild(kstat);
  ksave.onclick=async()=>{if(!kin.value.trim())return;kstat.textContent='saving…';await post({provider:cur.name,api_key:kin.value.trim()});smModel(body)};
  body.appendChild(krow);
 }
 // model
 const mrow=$(`<div class="sm-row"><div class="sm-row-head"><span class="sm-label">Model</span><span class="sm-sub" id="mstat">${s.model?'current: '+esc(s.model):'none set'}</span></div></div>`);
 const mw=$(`<div class="row"></div>`),mfield=$(`<input class="sm-field" style="flex:1" placeholder="model id (or Browse)" value="${esc(s.model||'')}">`);
 const mbrowse=$(`<button class="ghost">Browse…</button>`),mset=$(`<button class="go">Set</button>`),mtest=$(`<button class="ghost">Test</button>`);
 mw.appendChild(mfield);mw.appendChild(mbrowse);mw.appendChild(mset);mw.appendChild(mtest);mrow.appendChild(mw);
 const mlist=$(`<div></div>`);mrow.appendChild(mlist);body.appendChild(mrow);
 const mstat=mrow.querySelector('#mstat');
 mset.onclick=async()=>{await post({provider:s.provider,model:mfield.value.trim()});mstat.innerHTML='<span class="sm-ok">✓ set</span>'};
 mtest.onclick=async()=>{mstat.textContent='testing…';const r=await api('/api/testkey',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({provider:s.provider})});mstat.innerHTML=r.ok?`<span class="sm-ok">✓ ${esc(r.detail)}</span>`:`<span class="sm-bad">✗ ${esc(r.detail)}</span>`};
 mbrowse.onclick=async()=>{if(!s.provider){mstat.innerHTML='<span class="sm-bad">pick a provider first</span>';return}
  mlist.innerHTML='<p class="hint">loading models…</p>';const r=await api('/api/models?provider='+encodeURIComponent(s.provider));
  if(r.error){mlist.innerHTML=`<p class="hint"><span class="sm-bad">${esc(r.error)}</span></p>`;return}
  const box=$(`<div style="max-height:220px;overflow:auto;border:1px solid var(--line);border-radius:8px;margin-top:.5rem"></div>`);
  const filt=$(`<input class="sm-field" style="width:100%;border:0;border-bottom:1px solid var(--line);border-radius:0" placeholder="filter ${r.models.length} models…">`);box.appendChild(filt);
  const ul=$(`<div></div>`);box.appendChild(ul);
  const paint=(qq)=>{ul.innerHTML='';r.models.filter(mm=>!qq||mm.toLowerCase().includes(qq)).slice(0,400).forEach(mm=>{const b=$(`<button class="ghost" style="display:block;width:100%;text-align:left;border:0;border-bottom:1px solid var(--line);border-radius:0;font:12px ui-monospace,monospace">${esc(mm)}</button>`);b.onclick=async()=>{mfield.value=mm;await post({provider:s.provider,model:mm});mstat.innerHTML='<span class="sm-ok">✓ '+esc(mm)+'</span>';mlist.innerHTML=''};ul.appendChild(b)})};
  filt.oninput=()=>paint(filt.value.trim().toLowerCase());paint('');mlist.innerHTML='';mlist.appendChild(box)};
}
async function smAbout(body){const s=await api('/api/summary');
 body.appendChild($(`<p class="hint">Story Graph OS — a local browser face over the story-graph engine.</p>`));
 body.appendChild($(`<pre>graph:   ${esc(s.path||'')}\ncanon:   chapter ${s.canon_chapter}\nmodules: ${s.modules.join(', ')||'none'}\nkuzu:    ${s.kuzu?'on':'off'}</pre>`));
 body.appendChild($(`<p class="hint">Settings dialog adapted from the Novel Machine authoring UI — its accessibility controls plus provider-neutral, OpenAI-compatible model routing (OpenRouter + local Ollama / LM Studio). That app's per-agent novel-pipeline Flows have no analog here.</p>`));
}
a11yApply(a11yRead());
document.getElementById('gear').onclick=openSettings;
head().then(render);
</script></body></html>"""


def main(argv=None):
    p = argparse.ArgumentParser(prog="story_graph_app")
    p.add_argument("graph")
    p.add_argument("--chapters-dir", default="")
    p.add_argument("--port", type=int, default=8765)
    p.add_argument("--host", default="127.0.0.1")
    a = p.parse_args(argv)
    load(a.graph, a.chapters_dir)
    kz = "kuzu ON" if STATE["conn"] else f"kuzu OFF ({STATE['kuzu_err'] or 'not installed'})"
    try:
        server = ThreadingHTTPServer((a.host, a.port), Handler)   # bind first, before any 'open' message
    except OSError as e:
        if getattr(e, "errno", None) in (48, 98, 10048):          # EADDRINUSE: mac / linux / windows
            print(f"Port {a.port} is already in use — another server is running there.")
            print(f"  See it:  lsof -nP -iTCP:{a.port} -sTCP:LISTEN")
            print(f"  Fix it:  rerun with a free port,  --port {a.port + 1}   (or stop that process)")
            return 1
        raise
    print(f"Story Graph OS — {STATE['path']} — {kz}")
    print(f"  open http://{a.host}:{a.port}   (Ctrl-C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
    return 0


if __name__ == "__main__":
    sys.exit(main())
