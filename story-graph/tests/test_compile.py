import pytest
from conftest import make_graph
import story_graph as sg


def test_load_graph_builds_queryable_db(tmp_path):
    kuzu = pytest.importorskip("kuzu")
    import story_graph_kuzu as loader
    props = ("## Propositions\n| prop-id | statement | canon-status | governing-source | span |\n"
             "|---|---|---|---|---|\n| jackson-alive | Jackson lives | true | ms | s1 |\n")
    epi = ("## Epistemic States\n| prop-id | holder | mode | since-ch | span |\n|---|---|---|---|---|\n"
           "| jackson-alive | reader | knows | 3 | s1 |\n| jackson-alive | jonah | believes-false | 3 | s1 |\n")
    ev = ("## Evidence\n| span-id | source-id | locator | quote | note |\n|---|---|---|---|---|\n"
          "| s1 | ms | ch3 | Jackson was alive | |\n")
    graph = sg.parse_graph(make_graph(Propositions=props, Evidence=ev, **{"Epistemic States": epi}))
    db_path = str(tmp_path / "g.kuzu")
    loader.load_graph(graph, db_path)
    conn = kuzu.Connection(kuzu.Database(db_path))
    res = conn.execute("MATCH (:Proposition)<-[e:EPISTEMIC]-(h) WHERE e.mode='believes-false' RETURN count(*)")
    assert res.get_next()[0] == 1
