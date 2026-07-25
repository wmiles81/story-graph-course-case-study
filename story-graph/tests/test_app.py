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
