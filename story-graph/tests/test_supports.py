import pytest
from conftest import make_graph
import story_graph as sg


def test_supports_edges_link_evidence_to_proposition(tmp_path):
    pytest.importorskip("kuzu")
    import kuzu, story_graph_kuzu as loader
    props = ("## Propositions\n| prop-id | statement | canon-status | governing-source | span |\n"
             "|---|---|---|---|---|\n| scrolls-gone | The scrolls are gone | true | ms | s1 |\n")
    ev = ("## Evidence\n| span-id | source-id | locator | quote | note |\n|---|---|---|---|---|\n"
          "| s1 | ms | ch02 | The gap was there | |\n| s2 | ms | ch01 | unrelated | |\n")
    graph = sg.parse_graph(make_graph(Propositions=props, Evidence=ev))
    db = str(tmp_path / "g.kuzu")
    loader.load_graph(graph, db)
    conn = kuzu.Connection(kuzu.Database(db))
    res = conn.execute("MATCH (e:Evidence)-[:SUPPORTS]->(p:Proposition {id:'scrolls-gone'}) RETURN e.id")
    got = []
    while res.has_next():
        got.append(res.get_next()[0])
    assert got == ["s1"]  # only the linked span, not s2
