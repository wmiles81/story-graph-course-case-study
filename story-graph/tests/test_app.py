import importlib.util
from pathlib import Path
import pytest
from conftest import MINIMAL_V2, make_graph

APP = Path(__file__).resolve().parents[2] / "app" / "story_graph_app.py"


def _app():
    spec = importlib.util.spec_from_file_location("sgapp", APP)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_app_summary_and_graph(tmp_path):
    app = _app()
    g = tmp_path / "g.md"
    g.write_text(MINIMAL_V2, encoding="utf-8")
    app.load(str(g))
    s = app.api_summary()
    assert s["counts"]["entities"] == 2 and "kuzu" in s
    assert isinstance(app.api_graph()["nodes"], list)


def test_app_cypher_and_bad_query(tmp_path):
    pytest.importorskip("kuzu")
    app = _app()
    props = ("## Propositions\n| prop-id | statement | canon-status | governing-source | span |\n"
             "|---|---|---|---|---|\n| p1 | x | true | ms | provisional |\n")
    g = tmp_path / "g.md"
    g.write_text(make_graph(Propositions=props), encoding="utf-8")
    app.load(str(g))
    r = app.api_cypher("MATCH (p:Proposition) RETURN p.id")
    assert r.get("columns") == ["p.id"] and len(r["rows"]) == 1
    assert "error" in app.api_cypher("NONSENSE QUERY")


def test_app_schema_and_ask_guards(tmp_path):
    app = _app()
    schema = app.api_schema()["schema"]
    assert "Proposition" in schema and "EPISTEMIC" in schema and "SUPPORTS" in schema
    # empty question is rejected before any SDK/kuzu need — deterministic
    assert "plain English" in app.api_ask("")["error"]


def test_app_settings_providers_roundtrip(tmp_path):
    app = _app()
    app._env_path = lambda: tmp_path / ".env"  # never touch the real .env during tests
    s = app.api_settings_get()
    names = {p["name"] for p in s["providers"]}
    assert {"openrouter", "ollama", "lmstudio"} <= names and "kuzu" in s
    app.api_settings_put({"provider": "openrouter", "model": "anthropic/claude-3.5-sonnet"})
    s2 = app.api_settings_get()
    assert s2["provider"] == "openrouter" and s2["model"] == "anthropic/claude-3.5-sonnet"
    app.api_settings_put({"provider": "openrouter", "api_key": "sk-or-x"})
    assert any(p["name"] == "openrouter" and p["key_set"] for p in app.api_settings_get()["providers"])
    # persisted to .env, restorable after a "restart"
    env = app._env_read()
    assert env["OPENROUTER_API_KEY"] == "sk-or-x" and env["SGOS_MODEL"] == "anthropic/claude-3.5-sonnet"
    # local provider probe fails fast (nothing listening) — both return dicts, no exception
    assert "models" in app.api_models("ollama")
    assert "ok" in app.api_testkey("ollama")
    assert app.api_models("bogus")["error"] == "unknown provider"
