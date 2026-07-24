import pytest
from conftest import make_graph
import story_graph as sg

IRONY = dict(
    Propositions=("## Propositions\n| prop-id | statement | canon-status | governing-source | span |\n"
                  "|---|---|---|---|---|\n| bond | Wolf knows its mate | true | ms | s1 |\n"),
    Evidence=("## Evidence\n| span-id | source-id | locator | quote | note |\n|---|---|---|---|---|\n"
              "| s1 | ms | ch01 | knew the scent of mate | |\n| s2 | ms | ch01 | Not ever | |\n"),
)
EPI = ("## Epistemic States\n| prop-id | holder | mode | since-ch | span |\n|---|---|---|---|---|\n"
       "| bond | reader | knows | 1 | s1 |\n| bond | jonah | believes-false | 1 | s2 |\n")


def graph_dict():
    ent = ("## Entities\n| id | type | status | voice | note |\n|---|---|---|---|---|\n"
           "| jonah | Character | active | male | |\n")
    return sg.parse_graph(make_graph(Entities=ent, **{"Epistemic States": EPI}, **IRONY))


def test_irony_query_pairs_reader_and_character():
    pytest.importorskip("kuzu")
    import story_graph_query as q
    conn = q.open_graph(graph_dict())
    rows = q.q_irony(conn)
    assert any(r for r in rows if r[0] == "bond" and r[2] == "jonah")


def test_receipts_returns_only_that_props_spans():
    pytest.importorskip("kuzu")
    import story_graph_query as q
    conn = q.open_graph(graph_dict())
    spans = sorted(r[0] for r in q.q_receipts(conn, "bond"))
    assert spans == ["s1"]


def test_run_query_irony_text_mentions_holders():
    pytest.importorskip("kuzu")
    import story_graph_query as q
    out = q.run_query("irony", graph_dict(), canon_ch=1)
    assert "reader" in out and "jonah" in out and "believes-false" in out
