#!/usr/bin/env python3
"""Provider-neutral chat client shared by the story-graph tools.

`story_graph.py` — the validator/compiler/CLI — never imports this. Nothing here is
needed to run `validate`, `compile`, `query`, `report`, `audit`, `impact`, `coverage`
or `deviations`; those stay deterministic, offline and stdlib. This module exists so
that the browser app and (later) the AI subcommands share ONE client rather than two
drifting copies, and so provider neutrality is enforced in a single place:

  * OpenAI-compatible chat over stdlib ``urllib`` — no vendor SDK, no vendor-specific
    request shape.
  * OpenRouter for cloud, Ollama (:11434) and LM Studio (:1234) for local. A local
    server needs no key and no network egress.

Every function takes what it needs as an argument. There is deliberately no module
state and no implicit ``.env`` location: the app keeps its key in ``app/.env`` while a
CLI run may sit in a different working directory, and two callers must not fight over
one global.
"""
from __future__ import annotations

import json

# Provider-neutral, OpenAI-compatible endpoints. Local servers need no key.
PROVIDERS = [
    {"name": "openrouter", "label": "OpenRouter", "base": "https://openrouter.ai/api/v1",
     "env": "OPENROUTER_API_KEY", "local": False},
    {"name": "ollama", "label": "Ollama (local)", "base": "http://localhost:11434/v1",
     "env": "", "local": True},
    {"name": "lmstudio", "label": "LM Studio (local)", "base": "http://localhost:1234/v1",
     "env": "", "local": True},
]
_PROV = {p["name"]: p for p in PROVIDERS}


def provider(name):
    """The provider record, or None. Callers treat None as 'unknown provider'."""
    return _PROV.get(name)


# --------------------------------------------------------------------------- .env


def env_read(path):
    """Parse a KEY=VALUE .env into a dict. Missing file -> {}."""
    out = {}
    if path and path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            s = line.strip()
            if s and not s.startswith("#") and "=" in s:
                k, v = s.split("=", 1)
                out[k.strip()] = v.strip()
    return out


def env_write(path, updates):
    """Upsert KEY=VALUE pairs, preserving every other line, and reflect them in this
    process immediately. The file is chmod 0600 because it can hold an API key."""
    import os
    keys = set(updates)
    kept = [ln for ln in (path.read_text(encoding="utf-8").splitlines() if path.exists() else [])
            if not ("=" in ln and not ln.strip().startswith("#") and ln.split("=", 1)[0].strip() in keys)]
    kept += [f"{k}={v}" for k, v in updates.items()]
    path.write_text("\n".join(kept) + "\n", encoding="utf-8")
    try:
        os.chmod(path, 0o600)
    except Exception:
        pass
    for k, v in updates.items():
        os.environ[k] = v


def load_env(path):
    """Seed os.environ from the .env without ever overriding a variable that was set
    explicitly at launch — an env var on the command line must win over a stale file."""
    import os
    for k, v in env_read(path).items():
        os.environ.setdefault(k, v)


# ------------------------------------------------------------------------ transport

_SSL_CTX = None


def ssl_ctx():
    """A verifying SSL context that also works on macOS python.org builds, which ship
    no CA bundle — without certifi those raise CERTIFICATE_VERIFY_FAILED on any HTTPS
    call, which reads like a bad API key and is not one."""
    global _SSL_CTX
    if _SSL_CTX is None:
        import ssl
        try:
            import certifi
            _SSL_CTX = ssl.create_default_context(cafile=certifi.where())
        except Exception:
            _SSL_CTX = ssl.create_default_context()
    return _SSL_CTX


def oai(base, path, key="", payload=None, timeout=60):
    """One OpenAI-compatible request. POST when a payload is given, else GET."""
    import urllib.request
    headers = {"Content-Type": "application/json"}
    if key:
        headers["Authorization"] = "Bearer " + key
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(base.rstrip("/") + path, data=data, headers=headers,
                                 method="POST" if data is not None else "GET")
    with urllib.request.urlopen(req, timeout=timeout, context=ssl_ctx()) as r:  # context ignored for http://
        return json.loads(r.read().decode("utf-8"))


def chat(name, model, system, user, max_tokens=2048, key=""):
    """One chat completion. Returns the assistant's text."""
    p = _PROV[name]
    payload = {"model": model, "max_tokens": max_tokens,
               "messages": [{"role": "system", "content": system},
                            {"role": "user", "content": user}]}
    d = oai(p["base"], "/chat/completions", key, payload, timeout=90)
    return d["choices"][0]["message"]["content"]


def models(name, key=""):
    """The provider's live model catalogue as a list of ids."""
    p = _PROV.get(name)
    if not p:
        return []
    d = oai(p["base"], "/models", key, None, timeout=20)
    return [m.get("id", "") for m in d.get("data", []) if m.get("id")]


def reachable(name, key=""):
    """Can we actually use this provider right now? A cloud provider needs a key; a
    local one needs something listening, which we probe with a short timeout so an
    absent local server costs the caller a moment rather than a hang."""
    p = _PROV.get(name)
    if not p:
        return False
    if not p["local"]:
        return bool(key)
    try:
        oai(p["base"], "/models", "", None, timeout=1.5)
        return True
    except Exception:
        return False
