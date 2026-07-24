import pytest
from conftest import make_graph
import story_graph as sg


def test_report_lists_irony_and_open_loops(tmp_path):
    pytest.importorskip("kuzu")
    props = ("## Propositions\n| prop-id | statement | canon-status | governing-source | span |\n"
             "|---|---|---|---|---|\n| bond | Wolf knows mate | true | ms | s1 |\n")
    ev = ("## Evidence\n| span-id | source-id | locator | quote | note |\n|---|---|---|---|---|\n"
          "| s1 | ms | ch01 | mate | |\n| s2 | ms | ch01 | not ever | |\n")
    epi = ("## Epistemic States\n| prop-id | holder | mode | since-ch | span |\n|---|---|---|---|---|\n"
           "| bond | reader | knows | 1 | s1 |\n| bond | jonah | believes-false | 1 | s2 |\n")
    loops = ("## Open Loops & Setups\n| id | planted-ch | expectation | must-fire-by | status | span |\n"
             "|---|---|---|---|---|---|\n| purge | 2 | stop the purge | 30 | UNFIRED | s2 |\n")
    ent = "## Entities\n| id | type | status | voice | note |\n|---|---|---|---|---|\n| jonah | Character | active | male | |\n"
    text = make_graph(Entities=ent, Propositions=props, Evidence=ev, **{"Epistemic States": epi}, **{"Open Loops & Setups": loops})
    g = tmp_path / "Story-Graph.md"
    g.write_text(text, encoding="utf-8")
    out, report = sg.report_graph(str(g))
    assert report.errors == []
    assert "Dramatic irony" in out and "purge" in out
