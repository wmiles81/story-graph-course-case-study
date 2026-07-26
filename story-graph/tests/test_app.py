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


def test_app_settings_roundtrip():
    app = _app()
    s = app.api_settings_get()
    assert s["model"] and isinstance(s["models"], list) and "kuzu" in s and "anthropic" in s
    app.api_settings_put({"model": "claude-sonnet-5"})
    assert app.api_settings_get()["model"] == "claude-sonnet-5"
    app.api_settings_put({"api_key": "sk-ant-x"})
    assert app.api_settings_get()["key_set"] and app.api_settings_get()["key_source"] == "app"
    assert "ok" in app.api_testkey()  # degrades to {ok:False,...} without the SDK
