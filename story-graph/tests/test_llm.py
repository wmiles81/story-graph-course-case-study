"""The shared provider-neutral client (docs/ai-plan.md, stage 0).

No test here may touch the network: every request goes through a substituted
urlopen, and the one case that must make no request at all asserts that.
"""
import json
import os
import urllib.request

import pytest
import story_graph_llm as llm


class _Resp:
    def __init__(self, payload):
        self._b = json.dumps(payload).encode()

    def read(self):
        return self._b

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class _Calls(list):
    """Captured requests, plus the canned reply the next one gets."""
    reply = None


@pytest.fixture
def calls(monkeypatch):
    """Capture every outbound request instead of making it."""
    seen = _Calls()
    seen.reply = {"value": {}}

    def fake(req, timeout=None, context=None):
        seen.append({"url": req.full_url, "method": req.get_method(),
                     "headers": {k.lower(): v for k, v in req.header_items()},
                     "body": json.loads(req.data.decode()) if req.data else None,
                     "timeout": timeout})
        return _Resp(seen.reply["value"])

    monkeypatch.setattr(urllib.request, "urlopen", fake)
    return seen


def test_provider_registry_is_local_first_and_vendor_neutral():
    names = [p["name"] for p in llm.PROVIDERS]
    assert {"openrouter", "ollama", "lmstudio"} == set(names)
    local = {p["name"] for p in llm.PROVIDERS if p["local"]}
    assert local == {"ollama", "lmstudio"}, "both local servers must stay usable without a key"
    assert all(not p["env"] for p in llm.PROVIDERS if p["local"]), "a local provider must need no key"
    assert llm.provider("nope") is None


def test_env_roundtrip_preserves_unrelated_lines_and_locks_the_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("# comment\nUNRELATED=keep\nOPENROUTER_API_KEY=old\n", encoding="utf-8")
    llm.env_write(p, {"OPENROUTER_API_KEY": "new", "SGOS_MODEL": "m/1"})
    got = llm.env_read(p)
    assert got["OPENROUTER_API_KEY"] == "new" and got["SGOS_MODEL"] == "m/1"
    assert got["UNRELATED"] == "keep", "an unrelated key must survive an upsert"
    assert "# comment" in p.read_text(encoding="utf-8")
    assert oct(p.stat().st_mode)[-3:] == "600", "the file can hold an API key"
    assert os.environ["SGOS_MODEL"] == "m/1", "written values apply to this process immediately"
    assert llm.env_read(tmp_path / "absent.env") == {}


def test_load_env_never_overrides_an_explicit_variable(tmp_path, monkeypatch):
    p = tmp_path / ".env"
    p.write_text("SG_TEST_A=from-file\nSG_TEST_B=from-file\n", encoding="utf-8")
    monkeypatch.setenv("SG_TEST_A", "from-launch")
    monkeypatch.delenv("SG_TEST_B", raising=False)
    llm.load_env(p)
    assert os.environ["SG_TEST_A"] == "from-launch", "a var set at launch must win over the file"
    assert os.environ["SG_TEST_B"] == "from-file"


def test_oai_shapes_the_request(calls):
    calls.reply["value"] = {"data": [{"id": "m1"}, {"id": "m2"}, {"no": "id"}]}
    llm.oai("http://x/v1/", "/models")                     # trailing slash must not double up
    assert calls[-1]["url"] == "http://x/v1/models" and calls[-1]["method"] == "GET"
    assert "authorization" not in calls[-1]["headers"], "no key -> no Authorization header"
    llm.oai("http://x/v1", "/chat/completions", "sk-1", {"a": 1})
    assert calls[-1]["method"] == "POST" and calls[-1]["body"] == {"a": 1}
    assert calls[-1]["headers"]["authorization"] == "Bearer sk-1"
    assert llm.models("ollama") == ["m1", "m2"]
    assert llm.models("bogus") == []


def test_chat_sends_openai_shape_and_returns_the_text(calls):
    calls.reply["value"] = {"choices": [{"message": {"content": "hello"}}]}
    out = llm.chat("ollama", "llama3", "SYS", "USER", max_tokens=64, key="")
    assert out == "hello"
    body = calls[-1]["body"]
    assert body["model"] == "llama3" and body["max_tokens"] == 64
    # Sent, not merely recorded: proposal files claimed temperature 0 in their provenance
    # while every request went out at the provider's default.
    assert body["temperature"] == 0
    assert body["messages"] == [{"role": "system", "content": "SYS"},
                                {"role": "user", "content": "USER"}]
    assert set(body) == {"model", "max_tokens", "temperature", "messages"}, \
        "no vendor-specific fields"
    assert calls[-1]["url"].startswith("http://localhost:11434/v1")


def test_reachability_costs_a_cloud_provider_no_request(calls):
    """A cloud provider's reachability is 'do we have a key' — probing it would spend
    a request (and leak that the app is running) on a question we can answer locally."""
    assert llm.reachable("openrouter", "sk-1") is True
    assert llm.reachable("openrouter", "") is False
    assert calls == [], "no network call may be made to decide cloud reachability"
    calls.reply["value"] = {"data": []}
    assert llm.reachable("ollama") is True and len(calls) == 1
    assert calls[-1]["timeout"] == 1.5, "an absent local server must fail fast, not hang"
    assert llm.reachable("bogus") is False


def test_local_probe_failure_is_not_an_exception(monkeypatch):
    def boom(*a, **k):
        raise OSError("connection refused")
    monkeypatch.setattr(urllib.request, "urlopen", boom)
    assert llm.reachable("ollama") is False


def test_engine_stays_offline():
    """The deterministic core must never pull in the client — that is the whole basis
    for saying validate/compile/query/audit make no network calls."""
    import subprocess
    import sys
    from pathlib import Path
    assets = Path(llm.__file__).resolve().parent
    r = subprocess.run(
        [sys.executable, "-c",
         "import sys; sys.path.insert(0, %r); import story_graph; "
         "print('story_graph_llm' in sys.modules)" % str(assets)],
        capture_output=True, text=True)
    assert r.stdout.strip() == "False", r.stderr
