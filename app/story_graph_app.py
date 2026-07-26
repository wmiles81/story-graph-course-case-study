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
import re
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

DB_LOCK = threading.Lock()   # one kuzu Connection shared by all request threads
READY = threading.Event()    # set once the initial load() finishes; gates request handling during startup

APP_DIR = Path(__file__).resolve().parent
ASSETS = APP_DIR.parent / "story-graph" / "assets"
sys.path.insert(0, str(ASSETS))
import story_graph as sg  # noqa: E402

STATE = {"path": None, "text": "", "graph": None, "chapters_dir": "", "conn": None, "kuzu_err": "",
         "provider": "", "model": "", "keys": {}, "mtime": None}
# keys: Ask-tab AI provider/model + in-memory keys (never written to disk).
# mtime: on-disk graph file's mtime as of the last load() — used for staleness polling.

# Provider-neutral, OpenAI-compatible endpoints. Local servers need no key; cloud reads env or an in-memory key.
PROVIDERS = [
    {"name": "openrouter", "label": "OpenRouter", "base": "https://openrouter.ai/api/v1", "env": "OPENROUTER_API_KEY", "local": False},
    {"name": "ollama", "label": "Ollama (local)", "base": "http://localhost:11434/v1", "env": "", "local": True},
    {"name": "lmstudio", "label": "LM Studio (local)", "base": "http://localhost:1234/v1", "env": "", "local": True},
]
_PROV = {p["name"]: p for p in PROVIDERS}


def _env_path():
    from pathlib import Path
    return Path(__file__).resolve().parent / ".env"


def _env_read():
    p = _env_path()
    out = {}
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            s = line.strip()
            if s and not s.startswith("#") and "=" in s:
                k, v = s.split("=", 1)
                out[k.strip()] = v.strip()
    return out


def _env_write(updates):
    """Upsert KEY=VALUE pairs into the local (gitignored) .env, preserving other lines."""
    import os as _os
    p = _env_path()
    keys = set(updates)
    kept = [ln for ln in (p.read_text(encoding="utf-8").splitlines() if p.exists() else [])
            if not ("=" in ln and not ln.strip().startswith("#") and ln.split("=", 1)[0].strip() in keys)]
    kept += [f"{k}={v}" for k, v in updates.items()]
    p.write_text("\n".join(kept) + "\n", encoding="utf-8")
    try:
        import os as _o; _o.chmod(p, 0o600)   # the file holds an API key
    except Exception:
        pass
    for k, v in updates.items():
        _os.environ[k] = v  # reflect immediately in this process


def _load_env():
    import os as _os
    for k, v in _env_read().items():
        _os.environ.setdefault(k, v)  # never override an env var set explicitly at launch


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
    import os as _os
    _load_env()  # restore keys + provider/model saved to the local .env
    STATE["provider"] = STATE.get("provider") or _os.environ.get("SGOS_PROVIDER", "")
    STATE["model"] = STATE.get("model") or _os.environ.get("SGOS_MODEL", "")
    STATE["path"] = graph_path
    STATE["chapters_dir"] = chapters_dir
    STATE["text"] = Path(graph_path).read_text(encoding="utf-8")
    STATE["mtime"] = Path(graph_path).stat().st_mtime
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


def api_status():
    """Cheap staleness probe (os.stat only, no re-parse) so the frontend can poll:
    stale = the on-disk graph file's mtime no longer matches what we last loaded."""
    path = STATE.get("path")
    mtime = STATE.get("mtime")
    if not path:
        return {"stale": False, "mtime": mtime}
    try:
        cur = Path(path).stat().st_mtime
    except OSError:
        return {"stale": False, "mtime": mtime}
    return {"stale": mtime is not None and cur != mtime, "mtime": mtime}


def api_reload():
    """Re-parse the graph file from disk and rebuild the kuzu projection. Wrapped so
    a bad edit (parse error, missing file) can't crash the server: on failure this
    returns {"error": ...} instead of raising. Takes DB_LOCK so a concurrent Cypher
    query can't run against a kuzu connection that's being swapped out mid-reload."""
    try:
        with DB_LOCK:
            load(STATE["path"], STATE["chapters_dir"])
    except Exception as e:
        return {"error": f"reload failed: {e}"}
    return api_summary()


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
        with DB_LOCK:   # kuzu Connection is not safe for concurrent execute across threads
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
    if re.search(r"\b(create|merge|set|delete|drop|detach|copy|alter|install|load)\b", cypher, re.I):
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
        _env_write({"SGOS_PROVIDER": STATE["provider"]})
    if "model" in patch:
        STATE["model"] = (patch.get("model") or "").strip()
        _env_write({"SGOS_MODEL": STATE["model"]})
    if "api_key" in patch:
        prov = (patch.get("provider") or STATE.get("provider") or "").strip()
        key = (patch.get("api_key") or "").strip()
        p = _PROV.get(prov) or {}
        if prov and key:
            STATE.setdefault("keys", {})[prov] = key
            if p.get("env"):  # persist cloud keys to the gitignored .env so they survive restarts
                _env_write({p["env"]: key})
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
        # A handler exception used to kill the response mid-flight, which the browser
        # saw as a dead fetch and the UI as a tab stuck loading. Always answer.
        try:
            if not self._local_only():
                return
            if not READY.is_set():
                return self._starting()
            self._get()
        except Exception as e:
            try:
                self._json({"error": f"{type(e).__name__}: {e}"}, 500)
            except Exception:
                pass

    def _get(self):
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
        if u.path == "/api/status":
            return self._json(api_status())
        if u.path == "/api/graph":
            return self._json(api_graph(q.get("prop", [""])[0]))
        if u.path == "/api/timeline":
            return self._json(api_timeline())
        if u.path == "/api/report":
            return self._json(api_report(q.get("kind", ["report"])[0]))
        return self._json({"error": "not found"}, 404)

    def _starting(self):
        """While load() is still compiling the graph in a background thread: answer
        every request with a friendly 'starting up' reply instead of routing into
        _get() (which depends on STATE being fully populated)."""
        from urllib.parse import urlparse
        path = urlparse(self.path).path
        if path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
            return
        if path.startswith("/api/"):
            return self._json({"error": "starting up", "starting": True}, 503)
        return self._send(STARTING_PAGE, "text/html; charset=utf-8")

    def _local_only(self):
        """Reject cross-origin / DNS-rebinding requests: this server is for this
        machine's browser only, and its POSTs write .env and spend API credits."""
        host = (self.headers.get("Host") or "").split(":")[0]
        if host not in ("127.0.0.1", "localhost", "[::1]", "::1"):
            self._json({"error": "forbidden host"}, 403)
            return False
        origin = self.headers.get("Origin")
        if origin and not re.match(r"^https?://(127\.0\.0\.1|localhost|\[::1\])(:\d+)?$", origin):
            self._json({"error": "cross-origin request refused"}, 403)
            return False
        return True

    def do_POST(self):
        if not self._local_only():
            return
        if not READY.is_set():
            return self._json({"error": "starting up", "starting": True}, 503)
        try:
            length = int(self.headers.get("Content-Length") or 0)
            payload = json.loads(self.rfile.read(length) or "{}")
            if not isinstance(payload, dict):
                raise ValueError("body must be a JSON object")
        except Exception as e:
            return self._json({"error": f"bad request body: {e}"}, 400)
        try:
            return self._post(payload)
        except Exception as e:
            return self._json({"error": f"{type(e).__name__}: {e}"}, 500)

    def _post(self, payload):
        if self.path == "/api/cypher":
            return self._json(api_cypher(payload.get("cypher", "")))
        if self.path == "/api/ask":
            return self._json(api_ask(payload.get("question", "")))
        if self.path == "/api/settings":
            return self._json(api_settings_put(payload))
        if self.path == "/api/testkey":
            return self._json(api_testkey(payload.get("provider")))
        if self.path == "/api/reload":
            return self._json(api_reload())
        return self._json({"error": "not found"}, 404)


STARTING_PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta http-equiv="refresh" content="2">
<title>Story Graph OS — starting…</title>
<style>
:root{--bg:#eef1f5;--ink:#151c26;--muted:#586573}
@media(prefers-color-scheme:dark){:root{--bg:#0c121a;--ink:#e7edf4;--muted:#93a1b3}}
body{margin:0;background:var(--bg);color:var(--ink);font:15px system-ui,-apple-system,'Segoe UI',sans-serif;display:flex;align-items:center;justify-content:center;height:100vh}
div{text-align:center} p.hint{color:var(--muted);font-size:.85rem}
</style></head><body><div><p>Compiling the story graph…</p><p class="hint">This page refreshes automatically every 2 seconds.</p></div></body></html>"""


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
.gwrap{position:relative}
.gtools{display:flex;gap:.5rem;align-items:center;padding:.5rem .6rem;border-bottom:1px solid var(--line);flex-wrap:wrap}
.gtools .ghost{padding:.3rem .6rem}
.gsearch{flex:1;min-width:140px;font:13px ui-monospace,monospace;background:var(--bg);color:var(--ink);border:1px solid var(--line);border-radius:8px;padding:.4rem .6rem}
.gstage{position:relative;overflow:hidden}
.gstage svg{width:100%;height:100%;cursor:grab;touch-action:none}
.gstage svg:active{cursor:grabbing}
circle.gmatch{stroke:var(--accent);stroke-width:2px}
circle.ghover{stroke:var(--ink);stroke-width:2px}
.gpanel{position:absolute;top:10px;right:10px;width:230px;max-height:calc(100% - 20px);overflow:auto;background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:.7rem .8rem;box-shadow:0 6px 24px rgba(0,0,0,.3);font-size:13px}
.gpanel-id{font:600 13px ui-monospace,monospace;word-break:break-all;padding-right:1.2rem}
.gpanel-count{color:var(--muted);font-size:11px;border-top:1px solid var(--line);padding-top:.35rem;margin-top:.2rem}
.gpanel-list{display:flex;flex-direction:column;margin:.25rem 0}
.gpanel-focus{width:100%;margin-top:.4rem;background:var(--accent);color:#fff;border:0;border-radius:7px;padding:.35rem;font:12px system-ui;cursor:pointer}
.gpanel-x{position:absolute;top:4px;right:8px}
.gpanel-head{display:flex;justify-content:space-between;align-items:center;gap:.5rem}
.gpanel-head b{font:600 13px ui-monospace,monospace;word-break:break-all}
.gpanel-x{background:none;border:0;color:var(--muted);font-size:1.3rem;line-height:1;cursor:pointer;padding:0 .2rem}
.gpanel-kind{color:var(--muted);font-size:.78rem;margin:.15rem 0 .6rem;text-transform:uppercase;letter-spacing:.03em}
.gpanel-nbrs{display:flex;flex-direction:column;gap:.3rem;margin-top:.3rem}
.gpanel-link{color:var(--accent);text-decoration:none;font:12.5px ui-monospace,monospace;cursor:pointer}
.gpanel-link:hover{text-decoration:underline}
#offline{position:fixed;left:0;right:0;bottom:0;background:var(--irony,#b4531f);color:#fff;padding:.6rem 1rem;font:13px system-ui;display:flex;gap:.75rem;align-items:center;justify-content:center;z-index:99}
#offline button{background:#fff;border:0;border-radius:6px;padding:.25rem .6rem;cursor:pointer}
#stalebar{background:var(--panel);border:1px solid var(--irony);border-radius:10px;padding:.6rem 1rem}
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
// Never throws: every failure comes back as {error} so a caller can render it
// instead of leaving a tab stuck on "loading…" (a restarted backend used to do exactly that).
const api=async(p,o,timeoutMs)=>{
 const ac=new AbortController();
 const to=setTimeout(()=>ac.abort(),timeoutMs||45000);
 try{
  const res=await fetch(p,{...o,signal:ac.signal});
  let d=null;
  try{ d=await res.json() }catch(_){ d=null }
  if(!res.ok)return {error:(d&&d.error)||`server error ${res.status}`,_http:res.status};
  if(d===null)return {error:'server sent a malformed response'};
  banner(false);return d;
 }catch(e){
  if(e.name==='AbortError')return {error:'timed out waiting for a response. Try again.',_timeout:true};
  banner(true);
  return {error:'Cannot reach the server — it may have been restarted. Reload the page.',_offline:true};
 }finally{
  clearTimeout(to);
 }};
function banner(show){let b=document.getElementById('offline');
 if(show&&!b){b=$(`<div id="offline">Backend unreachable — the server may have restarted. <button class="ghost" onclick="location.reload()">Reload</button></div>`);document.body.appendChild(b)}
 else if(!show&&b)b.remove();}
// Polls /api/status every 5s; shows a dismissible bar atop #main when the graph file
// on disk changed since we loaded it, with a button to POST /api/reload.
let STALE_DISMISSED=false;
async function staleCheck(){
 const s=await api('/api/status');if(s.error)return;
 const bar=document.getElementById('stalebar');
 if(!s.stale){if(bar)bar.remove();STALE_DISMISSED=false;return}
 if(STALE_DISMISSED||bar)return;
 const b=$(`<div id="stalebar" class="row"><span>The graph file changed on disk.</span><button class="go">Reload graph</button><button class="ghost">Dismiss</button></div>`);
 const main=document.getElementById('main');main.insertBefore(b,main.firstChild);
 const [rbtn,dbtn]=b.querySelectorAll('button');
 rbtn.onclick=async()=>{rbtn.textContent='reloading…';rbtn.disabled=true;
  const r=await api('/api/reload',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'});
  if(r.error){rbtn.textContent='Reload graph';rbtn.disabled=false;b.querySelector('span').textContent='Reload failed: '+r.error;return}
  b.remove();STALE_DISMISSED=false;await head();await render();};
 dbtn.onclick=()=>{b.remove();STALE_DISMISSED=true};
}
let TAB='dashboard';
const TABS=['dashboard','graph','timeline','query','ask','reports'];
// Escapes quotes too — values from the provider catalog land in HTML attributes (value="…").
const esc=(s)=>String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');
function nav(){const n=document.getElementById('nav');n.innerHTML='';TABS.forEach(t=>{const b=document.createElement('button');b.textContent=t[0].toUpperCase()+t.slice(1);b.className=t===TAB?'on':'';b.onclick=()=>{TAB=t;render().then(staleCheck)};n.appendChild(b)})}
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
 const hint=$(`<p class="hint"></p>`);m.appendChild(hint);
 const mount=$(`<div></div>`);m.appendChild(mount);
 async function go(){const p=document.getElementById('focus').value.trim();const d=await api('/api/graph?prop='+encodeURIComponent(p));
  leg.innerHTML='';[...new Set(d.nodes.map(n=>n.kind))].forEach(k=>{const c=(d.nodes.find(n=>n.kind===k)||{}).color;leg.appendChild($(`<span><i style="background:${c}"></i>${k}</span>`))});
  if(!d.nodes.length){hint.textContent='No such proposition. Leave the box blank for the whole graph.';mount.innerHTML='';return}
  hint.textContent=`${d.nodes.length} nodes · ${d.edges.length} edges · drag a node to move it · drag empty space to pan · wheel to zoom · click a node for details`;
  draw(d,mount)}
 document.getElementById('fbtn').onclick=go;
 document.getElementById('focus').addEventListener('keydown',e=>{if(e.key==='Enter')go()});
 go();}
// Graph renderer: the force layout runs once per dataset (d={nodes,edges}). Everything drawn lives
// inside one <g>; wheel/pan/hover/search/select afterward only ever touch that <g>'s transform or
// element attributes — never re-simulate — so interaction stays smooth even at ~200 nodes.
// `full` (internal, threaded through recursive calls) is the true root dataset, so "Focus" on a
// neighbourhood can always offer a "Show all" back to the original graph, however deep the focus.
function draw(d,mount,full){full=full||d;mount.innerHTML='';
 const wrap=$(`<div class="frame gwrap"><div class="gtools"><input class="gsearch" placeholder="search nodes…" aria-label="Search nodes"><span class="gcount hint" aria-live="polite"></span><span style="flex:1"></span>${full!==d?'<button class="ghost" id="gall">Show all</button>':''}<button class="ghost" id="gzo" title="Zoom out">−</button><button class="ghost" id="gzi" title="Zoom in">+</button><button class="ghost" id="gzf" title="Fit to view">Fit</button></div><div class="gstage"><svg tabindex="0" role="img" aria-label="Story graph with ${d.nodes.length} nodes"></svg><div class="gpanel" hidden></div></div></div>`);
 mount.appendChild(wrap);
 const svg=wrap.querySelector('svg'),stage=wrap.querySelector('.gstage'),panel=wrap.querySelector('.gpanel');
 const sinput=wrap.querySelector('.gsearch'),countEl=wrap.querySelector('.gcount');
 const NS='http://www.w3.org/2000/svg',W=stage.clientWidth||900,H=560;
 stage.style.height=H+'px';svg.setAttribute('viewBox',`0 0 ${W} ${H}`);

 const N=d.nodes.map(n=>({...n,x:W/2+Math.cos(Math.random()*6.28)*180,y:H/2+Math.sin(Math.random()*6.28)*140}));
 const idx=Object.fromEntries(N.map((n,i)=>[n.id,i]));
 const E=d.edges.filter(e=>e.from in idx&&e.to in idx).map(e=>({s:idx[e.from],t:idx[e.to],label:e.label}));
 const neigh=N.map(()=>new Set());E.forEach(e=>{neigh[e.s].add(e.t);neigh[e.t].add(e.s)});
 const k=0.9*Math.sqrt(W*H/Math.max(1,N.length));
 for(let it=0;it<300;it++){for(const a of N){a.fx=0;a.fy=0}
  for(let i=0;i<N.length;i++)for(let j=i+1;j<N.length;j++){let dx=N[i].x-N[j].x,dy=N[i].y-N[j].y,dd=Math.hypot(dx,dy)||.01,f=k*k/dd;N[i].fx+=dx/dd*f;N[i].fy+=dy/dd*f;N[j].fx-=dx/dd*f;N[j].fy-=dy/dd*f}
  for(const e of E){let a=N[e.s],b=N[e.t],dx=a.x-b.x,dy=a.y-b.y,dd=Math.hypot(dx,dy)||.01,f=dd*dd/k;a.fx-=dx/dd*f;a.fy-=dy/dd*f;b.fx+=dx/dd*f;b.fy+=dy/dd*f}
  for(const a of N){a.fx+=(W/2-a.x)*.03;a.fy+=(H/2-a.y)*.03;const dl=Math.hypot(a.fx,a.fy)||.01,t=Math.max(1.5,W*0.05*(1-it/300));a.x+=a.fx/dl*Math.min(dl,t);a.y+=a.fy/dl*Math.min(dl,t)}}

 // Pan/zoom state lives only in this transform — "fit" (below) picks k/x/y to frame whatever the
 // layout produced, however far disconnected components have spread, instead of distorting node
 // coordinates to force them into a fixed box.
 const view={x:0,y:0,k:1},MINK=.12,MAXK=8;
 let hoverIdx=-1,selIdx=-1;const srch={active:false,matches:new Set()};

 const g=document.createElementNS(NS,'g');svg.appendChild(g);
 const linesG=document.createElementNS(NS,'g'),elabG=document.createElementNS(NS,'g'),nodesG=document.createElementNS(NS,'g'),nlabG=document.createElementNS(NS,'g');
 g.appendChild(linesG);g.appendChild(elabG);g.appendChild(nodesG);g.appendChild(nlabG);
 const ring=document.createElementNS(NS,'circle');ring.setAttribute('r',13);ring.setAttribute('fill','none');ring.setAttribute('stroke','var(--accent)');ring.setAttribute('stroke-width','2.5');ring.setAttribute('vector-effect','non-scaling-stroke');ring.style.display='none';ring.style.pointerEvents='none';g.appendChild(ring);

 const lines=[],elabels=[],circles=[],nlabels=[];
 E.forEach((e,ei)=>{const l=document.createElementNS(NS,'line');l.setAttribute('x1',N[e.s].x);l.setAttribute('y1',N[e.s].y);l.setAttribute('x2',N[e.t].x);l.setAttribute('y2',N[e.t].y);l.setAttribute('stroke','var(--line)');l.setAttribute('stroke-width','1.5');l.setAttribute('vector-effect','non-scaling-stroke');linesG.appendChild(l);lines[ei]=l;
  if(e.label){const tx=document.createElementNS(NS,'text');tx.setAttribute('class','elab');tx.setAttribute('x',(N[e.s].x+N[e.t].x)/2);tx.setAttribute('y',(N[e.s].y+N[e.t].y)/2-4);tx.textContent=e.label;elabG.appendChild(tx);elabels[ei]=tx}else elabels[ei]=null});
 N.forEach((n,i)=>{const c=document.createElementNS(NS,'circle');c.setAttribute('cx',n.x);c.setAttribute('cy',n.y);c.setAttribute('r',8);c.setAttribute('fill',n.color);c.dataset.i=i;
  const ti=document.createElementNS(NS,'title');ti.textContent=`${n.id} (${n.kind})`;c.appendChild(ti);
  c.addEventListener('pointerenter',()=>{hoverIdx=i;paintDim();updateLOD()});
  c.addEventListener('pointerleave',()=>{hoverIdx=-1;paintDim();updateLOD()});
  nodesG.appendChild(c);circles[i]=c;
  const t=document.createElementNS(NS,'text');t.setAttribute('class','nlab');t.setAttribute('x',n.x+11);t.setAttribute('y',n.y+4);t.textContent=n.id;nlabG.appendChild(t);nlabels[i]=t});

 // ── node details: click a node for its kind + neighbours, with Focus ──
 const closePanel=()=>{panel.style.display='none';selIdx=-1;ring.style.display='none';paintDim();updateLOD()};
 function selectNode(i){selIdx=i;const n=N[i];
  ring.setAttribute('cx',N[i].x);ring.setAttribute('cy',N[i].y);ring.style.display='';
  const nb=[];E.forEach(e=>{if(e.s===i)nb.push([N[e.t].id,e.t,e.label,'→']);else if(e.t===i)nb.push([N[e.s].id,e.s,e.label,'←'])});
  panel.innerHTML=`<button class="gpanel-x" title="Close (Esc)">×</button>`+
   `<div class="gpanel-id">${esc(n.id)}</div><div class="gpanel-kind">${esc(n.kind||'')}</div>`+
   `<div class="gpanel-count">${nb.length} neighbour${nb.length===1?'':'s'}</div>`;
  panel.querySelector('.gpanel-x').onclick=closePanel;
  const list=document.createElement('div');list.className='gpanel-list';
  nb.slice(0,60).forEach(([id,idx,lab,dir])=>{const b=document.createElement('button');b.className='gpanel-link';
   b.textContent=dir+' '+id+(lab?'  ·  '+lab:'');b.onclick=()=>selectNode(idx);list.appendChild(b)});
  panel.appendChild(list);
  if(nb.length){const f=document.createElement('button');f.className='gpanel-focus';f.textContent='Focus on this node';
   f.onclick=()=>{const keep=new Set([i]);E.forEach(e=>{if(e.s===i)keep.add(e.t);if(e.t===i)keep.add(e.s)});
    const nodes=[...keep].map(k=>({id:N[k].id,kind:N[k].kind,color:N[k].color}));
    const edges=E.filter(e=>keep.has(e.s)&&keep.has(e.t)).map(e=>({from:N[e.s].id,to:N[e.t].id,label:e.label}));
    draw({nodes,edges},mount,full)};
   panel.appendChild(f)}
  panel.style.display='block';paintDim();updateLOD();}
 circles.forEach((c,i)=>c.addEventListener('click',ev=>{ev.stopPropagation();if(!c.dataset.moved)selectNode(i);delete c.dataset.moved}));
 svg.addEventListener('click',ev=>{if(ev.target===svg)closePanel()});
 mount.addEventListener('keydown',ev=>{if(ev.key==='Escape')closePanel()});
 document.addEventListener('keydown',function onEsc(ev){if(ev.key==='Escape'&&document.body.contains(panel))closePanel();
  else if(!document.body.contains(panel))document.removeEventListener('keydown',onEsc)});

 function moveNode(i){circles[i].setAttribute('cx',N[i].x);circles[i].setAttribute('cy',N[i].y);
  nlabels[i].setAttribute('x',N[i].x+11);nlabels[i].setAttribute('y',N[i].y+4);
  if(i===selIdx){ring.setAttribute('cx',N[i].x);ring.setAttribute('cy',N[i].y)}
  E.forEach((e,ei)=>{if(e.s===i){lines[ei].setAttribute('x1',N[i].x);lines[ei].setAttribute('y1',N[i].y)}
   if(e.t===i){lines[ei].setAttribute('x2',N[i].x);lines[ei].setAttribute('y2',N[i].y)}
   if((e.s===i||e.t===i)&&elabels[ei]){elabels[ei].setAttribute('x',(N[e.s].x+N[e.t].x)/2);elabels[ei].setAttribute('y',(N[e.s].y+N[e.t].y)/2-4)}})}

 // Hover/search dim everything except what's relevant — "the rest" gets quieter, nothing disappears.
 function paintDim(){N.forEach((n,i)=>{const inc=hoverIdx>=0&&(i===hoverIdx||neigh[hoverIdx].has(i));
   const op=hoverIdx>=0?(inc?1:.18):(srch.active?(srch.matches.has(i)?1:.15):1);
   circles[i].style.opacity=op;nlabels[i].style.opacity=op;
   circles[i].classList.toggle('gmatch',srch.active&&srch.matches.has(i));
   circles[i].classList.toggle('ghover',i===hoverIdx)});
  E.forEach((e,ei)=>{const inc=hoverIdx>=0&&(e.s===hoverIdx||e.t===hoverIdx);
   const op=hoverIdx>=0?(inc?1:.12):(srch.active?((srch.matches.has(e.s)||srch.matches.has(e.t))?.85:.08):1);
   lines[ei].style.opacity=op;if(elabels[ei])elabels[ei].style.opacity=op})}
 // Level-of-detail: labels are mush at ~200 nodes, so they're opt-in — small graphs, high zoom, or
 // the thing you're actually pointing at (plus its neighbours) always get to show their label.
 function updateLOD(){const smallN=N.length<=40,zin=view.k>=1.6;
  N.forEach((n,i)=>{const show=smallN||zin||i===hoverIdx||i===selIdx||(hoverIdx>=0&&neigh[hoverIdx].has(i))||(selIdx>=0&&neigh[selIdx].has(i))||(srch.active&&srch.matches.has(i));
   nlabels[i].style.display=show?'':'none'});
  const smallE=E.length<=25,zinE=view.k>=2.2;
  E.forEach((e,ei)=>{if(!elabels[ei])return;const show=smallE||zinE||(hoverIdx>=0&&(e.s===hoverIdx||e.t===hoverIdx))||(selIdx>=0&&(e.s===selIdx||e.t===selIdx));
   elabels[ei].style.display=show?'':'none'})}
 function applyTransform(){g.setAttribute('transform',`translate(${view.x},${view.y}) scale(${view.k})`);updateLOD()}
 function fitView(){if(!N.length){view.x=0;view.y=0;view.k=1;return applyTransform()}
  const xs=N.map(n=>n.x),ys=N.map(n=>n.y),mnx=Math.min(...xs),mxx=Math.max(...xs),mny=Math.min(...ys),mxy=Math.max(...ys),pad=40;
  view.k=Math.max(MINK,Math.min(MAXK,Math.min((W-2*pad)/(mxx-mnx||1),(H-2*pad)/(mxy-mny||1))));
  view.x=W/2-(mnx+mxx)/2*view.k;view.y=H/2-(mny+mxy)/2*view.k;applyTransform()}
 function zoomAt(sx,sy,factor){const wx=(sx-view.x)/view.k,wy=(sy-view.y)/view.k;
  view.k=Math.max(MINK,Math.min(MAXK,view.k*factor));view.x=sx-wx*view.k;view.y=sy-wy*view.k;applyTransform()}

 function setSelected(i){selIdx=i;
  if(i<0){panel.hidden=true;ring.style.display='none';updateLOD();return}
  ring.style.display='';ring.setAttribute('cx',N[i].x);ring.setAttribute('cy',N[i].y);
  const nbrs=[...neigh[i]].map(j=>N[j]).sort((a,b)=>a.id<b.id?-1:1);
  panel.hidden=false;panel.innerHTML='';
  const head=$(`<div class="gpanel-head"><b>${esc(N[i].id)}</b><button class="gpanel-x" title="Close (Esc)">×</button></div>`);
  head.querySelector('.gpanel-x').onclick=()=>setSelected(-1);panel.appendChild(head);
  panel.appendChild($(`<div class="gpanel-kind">${esc(N[i].kind)}</div>`));
  const foc=$(`<button class="ghost">Focus</button>`);foc.onclick=()=>focusOn(i);panel.appendChild(foc);
  panel.appendChild($(`<div class="hint" style="margin:.6rem 0 .3rem">${nbrs.length} neighbour${nbrs.length===1?'':'s'}</div>`));
  const list=$(`<div class="gpanel-nbrs"></div>`);panel.appendChild(list);
  nbrs.forEach(nb=>{const a=$(`<a class="gpanel-link">${esc(nb.id)}</a>`);a.onclick=()=>setSelected(idx[nb.id]);list.appendChild(a)});
  updateLOD()}
 function focusOn(i){const keep=new Set([i,...neigh[i]]);
  const subN=[...keep].map(j=>({id:N[j].id,kind:N[j].kind,color:N[j].color}));
  const subE=E.filter(e=>keep.has(e.s)&&keep.has(e.t)).map(e=>({from:N[e.s].id,to:N[e.t].id,label:e.label}));
  draw({nodes:subN,edges:subE},mount,full)}

 function runSearch(q){q=q.trim().toLowerCase();
  if(!q){srch.active=false;srch.matches=new Set();countEl.textContent=''}
  else{srch.active=true;srch.matches=new Set(N.map((n,i)=>i).filter(i=>N[i].id.toLowerCase().includes(q)));
   countEl.textContent=srch.matches.size+' match'+(srch.matches.size===1?'':'es')}
  paintDim();updateLOD()}
 sinput.addEventListener('input',()=>runSearch(sinput.value));
 sinput.addEventListener('keydown',e=>{if(e.key==='Enter'){const first=[...srch.matches][0];
  if(first!=null){view.x=W/2-N[first].x*view.k;view.y=H/2-N[first].y*view.k;applyTransform();setSelected(first)}}});
 wrap.addEventListener('keydown',e=>{if(e.key==='Escape')setSelected(-1)});

 wrap.querySelector('#gzo').onclick=()=>zoomAt(W/2,H/2,1/1.4);
 wrap.querySelector('#gzi').onclick=()=>zoomAt(W/2,H/2,1.4);
 wrap.querySelector('#gzf').onclick=fitView;
 const allBtn=wrap.querySelector('#gall');if(allBtn)allBtn.onclick=()=>draw(full,mount);

 // Wheel (and trackpad pinch, which arrives as wheel+ctrlKey) zooms toward the cursor; the transform
 // is the only thing that changes, so this never touches the layout.
 svg.addEventListener('wheel',ev=>{ev.preventDefault();
  const r=svg.getBoundingClientRect(),sx=(ev.clientX-r.left)*(W/r.width),sy=(ev.clientY-r.top)*(H/r.height);
  zoomAt(sx,sy,Math.exp(-Math.max(-80,Math.min(80,ev.deltaY))*.0025))},{passive:false});

 // A pointerdown on a node drags that node (unchanged from before); anywhere else starts a pan.
 // pointerup decides click-vs-drag from `moved`, not from re-reading ev.target — once pointer capture
 // is set, ev.target on later events is the svg itself, not whatever is visually underneath it.
 let dragI=null,panStart=null,downPt=null,moved=false;
 svg.addEventListener('pointerdown',ev=>{downPt={x:ev.clientX,y:ev.clientY};moved=false;
  const hit=(ev.target.dataset&&ev.target.dataset.i!=null)?+ev.target.dataset.i:null;
  dragI=hit;if(hit==null)panStart={x:ev.clientX,y:ev.clientY,vx:view.x,vy:view.y};
  try{svg.setPointerCapture(ev.pointerId)}catch(_){}});
 svg.addEventListener('pointermove',ev=>{if(downPt&&!moved&&Math.hypot(ev.clientX-downPt.x,ev.clientY-downPt.y)>4)moved=true;
  const r=svg.getBoundingClientRect();
  if(dragI!=null){const sx=(ev.clientX-r.left)*(W/r.width),sy=(ev.clientY-r.top)*(H/r.height);
   N[dragI].x=(sx-view.x)/view.k;N[dragI].y=(sy-view.y)/view.k;moveNode(dragI)}
  else if(panStart){view.x=panStart.vx+(ev.clientX-panStart.x)*(W/r.width);view.y=panStart.vy+(ev.clientY-panStart.y)*(H/r.height);applyTransform()}});
 svg.addEventListener('pointerup',()=>{if(!moved)setSelected(dragI!=null?dragI:-1);
  dragI=null;panStart=null;downPt=null});
 svg.addEventListener('pointercancel',()=>{dragI=null;panStart=null;downPt=null});

 fitView();}
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
// Ask state survives tab switches — question, last result, chosen view + column mapping.
let ASK={q:'',r:null,view:'table',mode:'auto',src:0,tgt:-1,lbl:-1};
const ASK_PAL=['#0b7d84','#8a5cf6','#b4531f','#0e7c86','#94708a','#5a3fa6'];
// Columns whose values annotate an edge rather than being a node in their own right.
function askLabelCols(r){
 const n=r.columns.length, rows=r.rows;
 const byName=new Set(), byCard=new Set();
 r.columns.forEach((c,i)=>{
  const idish=/(^|\.|_)id$/i.test(c)||/statement|name|title/i.test(c);   // ids & text are always nodes
  if(!idish&&/mode|edge|type|label|rel\b|relation|trend|status|since|_ch\b|chapter/i.test(c)){byName.add(i);return}
  if(idish)return;
  const vals=new Set(rows.map(rw=>String(rw[i]??'')));                    // low-cardinality repeats read as labels
  if(rows.length>=4&&vals.size<=Math.max(2,Math.floor(rows.length/3)))byCard.add(i);});
 let out=new Set([...byName,...byCard]);
 if(n-out.size<2)out=new Set(byName);      // too aggressive: keep only name-based labels
 if(n-out.size<2)out=new Set();            // still not two node columns: draw everything
 return out;
}
function askGraphData(r){
 const n=r.columns.length, nodes={},edges=[],seen=new Set();
 const addNode=(v,i)=>{if(v&&!(v in nodes))nodes[v]={id:v,kind:r.columns[i],color:ASK_PAL[i%ASK_PAL.length]}};
 const addEdge=(a,b,lab)=>{const k=a+''+b+''+lab;if(a&&b&&a!==b&&!seen.has(k)){seen.add(k);edges.push({from:a,to:b,label:lab})}};
 if(ASK.mode==='auto'&&n>=2){
  // Full-row graph: chain every node column left→right; label columns annotate the next edge.
  const lblCols=askLabelCols(r);
  r.rows.forEach(rw=>{
   let prev=null,previ=-1,pend='';
   r.columns.forEach((c,i)=>{
    const v=rw[i]==null?'':String(rw[i]);
    if(lblCols.has(i)){pend=pend?pend+' · '+v:v;return}
    addNode(v,i);
    if(prev)addEdge(prev,v,pend);
    pend='';prev=v;previ=i;});
  });
 }else{
  const src=Math.min(ASK.src,n-1), tgt=(ASK.tgt<0?n-1:Math.min(ASK.tgt,n-1)), lbl=ASK.lbl;
  r.rows.forEach(rw=>{
   const a=rw[src]==null?'':String(rw[src]), b=rw[tgt]==null?'':String(rw[tgt]);
   addNode(a,src);if(b!==a)addNode(b,tgt);
   addEdge(a,b,(lbl>=0&&lbl<n)?String(rw[lbl]??''):'');});
 }
 return {nodes:Object.values(nodes),edges};
}
function askRender(out){
 out.innerHTML='';const r=ASK.r;
 if(!r)return;
 if(r.cypher)out.appendChild($(`<p class="hint"><b>Generated Cypher</b> — ${esc(r.explanation||'')}</p>`)),out.appendChild($(`<pre>${esc(r.cypher)}</pre>`));
 if(r.error){out.appendChild($(`<p class="err">${esc(r.error)}</p>`));if(r.raw)out.appendChild($(`<pre>${esc(r.raw)}</pre>`));return}
 // view toggle
 const bar=$(`<div class="row"></div>`);
 [['table','Table'],['graph','Graph']].forEach(([k,l])=>{const b=$(`<button class="${ASK.view===k?'go':'ghost'}">${l}</button>`);b.onclick=()=>{ASK.view=k;askRender(out)};bar.appendChild(b)});
 out.appendChild(bar);
 if(ASK.view==='table'){
  let h='<table><thead><tr>'+r.columns.map(c=>`<th>${esc(c)}</th>`).join('')+'</tr></thead><tbody>';
  h+=r.rows.map(rw=>'<tr>'+rw.map(v=>`<td>${v==null?'':esc(String(v))}</td>`).join('')+'</tr>').join('');
  h+='</tbody></table>';out.appendChild($(`<div>${h}</div>`));
  out.appendChild($(`<p class="hint">${r.rows.length} row(s)</p>`));
  return;
 }
 // graph view: full-row auto graph by default; Custom exposes source → target (+ edge label) pickers
 if(!r.rows.length){out.appendChild($(`<p class="hint">No rows to draw.</p>`));return}
 const map=$(`<div class="row" style="flex-wrap:wrap;gap:.5rem"></div>`);
 [['auto','Full row'],['custom','Custom']].forEach(([k,l])=>{const b=$(`<button class="${ASK.mode===k?'go':'ghost'}">${l}</button>`);b.onclick=()=>{ASK.mode=k;askRender(out)};map.appendChild(b)});
 if(ASK.mode==='custom'){
  const mk=(label,field,allowNone)=>{const sel=$(`<select class="sm-field"></select>`);
   if(allowNone){const o=document.createElement('option');o.value='-1';o.textContent='(none)';sel.appendChild(o)}
   r.columns.forEach((c,i)=>{const o=document.createElement('option');o.value=String(i);o.textContent=c;sel.appendChild(o)});
   const cur=field==='tgt'&&ASK.tgt<0?r.columns.length-1:ASK[field];
   sel.value=String(cur);sel.onchange=()=>{ASK[field]=+sel.value;askRender(out)};
   const w=$(`<span class="hint" style="display:inline-flex;align-items:center;gap:.35rem">${label}</span>`);w.appendChild(sel);return w};
  map.appendChild(mk('nodes from','src',false));map.appendChild(mk('→','tgt',false));map.appendChild(mk('edge label','lbl',true));
 }else{
  map.appendChild($(`<span class="hint">every column becomes nodes, chained left→right; label-like columns (mode, since-ch…) annotate the edges</span>`));
 }
 out.appendChild(map);
 const d=askGraphData(r);
 const mount=$(`<div></div>`);out.appendChild(mount);
 out.appendChild($(`<p class="hint">${d.nodes.length} nodes · ${d.edges.length} edges · drag a node to move it · drag empty space to pan · wheel to zoom · click a node for details</p>`));
 draw(d,mount);
}
async function ask(m){m.innerHTML='';
 m.appendChild($(`<p class="hint">Ask in plain English — the model you set in <b>⚙️ Settings → AI Model</b> (OpenRouter, or a local Ollama / LM Studio server) turns it into a Cypher query, runs it, and shows both. Results stay until your next question; flip to <b>Graph</b> to see them as a node-link.</p>`));
 const ta=$(`<textarea placeholder="e.g. what does Jonah know?"></textarea>`);ta.value=ASK.q||'What does Jonah know?';m.appendChild(ta);
 const row=$(`<div class="row"></div>`);const btn=$(`<button class="go">Ask</button>`);row.appendChild(btn);m.appendChild(row);
 const out=$(`<div></div>`);m.appendChild(out);
 askRender(out);   // restore the previous result on tab return
 const sch=await api('/api/schema');
 m.appendChild($(`<details style="margin-top:1rem"><summary class="hint">Cypher rules — the schema the AI is given</summary><pre>${esc(sch.schema||'')}</pre></details>`));
 btn.onclick=async()=>{ASK.q=ta.value;out.innerHTML='<p class="hint">asking…</p>';
  // 95s: comfortably past the backend's own 90s provider-call timeout (_chat/_oai), so a slow
  // but successful provider round-trip doesn't get reported as "timed out" by the frontend first.
  const r=await api('/api/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:ta.value})},95000);
  ASK.r=r;ASK.mode='auto';ASK.src=0;ASK.tgt=-1;ASK.lbl=-1;   // reset mapping for the new result shape
  askRender(out)};}
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
 body.appendChild($(`<p class="hint">The AI behind the <b>Ask</b> tab. Pick a provider, then a model — your choice and any key are saved to a local <code>.env</code> (gitignored) so they persist across restarts. Local providers (Ollama, LM Studio) need no key — the dot shows reachability.</p>`));
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
head().then(render).then(staleCheck);
setInterval(staleCheck,5000);
</script></body></html>"""


def main(argv=None):
    p = argparse.ArgumentParser(prog="story_graph_app")
    p.add_argument("graph")
    p.add_argument("--chapters-dir", default="")
    p.add_argument("--port", type=int, default=8765)
    p.add_argument("--host", default="127.0.0.1")
    a = p.parse_args(argv)
    try:
        server = ThreadingHTTPServer((a.host, a.port), Handler)   # bind first, before any 'open' message
    except OSError as e:
        if getattr(e, "errno", None) in (48, 98, 10048):          # EADDRINUSE: mac / linux / windows
            print(f"Port {a.port} is already in use — another server is running there.")
            print(f"  See it:  lsof -nP -iTCP:{a.port} -sTCP:LISTEN")
            print(f"  Fix it:  rerun with a free port,  --port {a.port + 1}   (or stop that process)")
            return 1
        raise
    print(f"Story Graph OS — loading {a.graph} …")
    print(f"  open http://{a.host}:{a.port}   (Ctrl-C to stop; page auto-refreshes until the graph finishes compiling)")

    def _load_then_ready():
        # Runs while the socket is already listening (bound above), so requests that
        # arrive during the slow compile get a friendly "starting up" reply instead
        # of a connection refusal — see READY / Handler._starting().
        load(a.graph, a.chapters_dir)
        kz = "kuzu ON" if STATE["conn"] else f"kuzu OFF ({STATE['kuzu_err'] or 'not installed'})"
        print(f"Story Graph OS ready — {STATE['path']} — {kz}")
        READY.set()

    threading.Thread(target=_load_then_ready, daemon=True).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
    return 0


if __name__ == "__main__":
    sys.exit(main())
