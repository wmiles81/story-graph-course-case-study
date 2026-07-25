import pytest
from conftest import MINIMAL_V2, make_graph
import story_graph as sg


def irony_graph():
    props = ("## Propositions\n| prop-id | statement | canon-status | governing-source | span |\n"
             "|---|---|---|---|---|\n| p1 | Wolf knows mate | true | ms | s1 |\n")
    epi = ("## Epistemic States\n| prop-id | holder | mode | since-ch | span |\n|---|---|---|---|---|\n"
           "| p1 | reader | knows | 1 | s1 |\n| p1 | jonah | believes-false | 1 | s1 |\n")
    ev = ("## Evidence\n| span-id | source-id | locator | quote | note |\n|---|---|---|---|---|\n"
          "| s1 | ms | ch01 | mate scent | |\n")
    return make_graph(Propositions=props, Evidence=ev, **{"Epistemic States": epi})


def test_impact_lists_holders_and_flags_irony():
    pytest.importorskip("kuzu")
    import story_graph_query as q
    out = q.run_impact(sg.parse_graph(irony_graph()), "p1")
    assert "jonah" in out and "reader" in out and "s1" in out
    assert "dramatic irony" in out.lower()


def test_impact_unknown_prop():
    pytest.importorskip("kuzu")
    import story_graph_query as q
    out = q.run_impact(sg.parse_graph(MINIMAL_V2), "nope")
    assert "not found" in out.lower() or "nothing depends" in out.lower()


def _dev_graph(quote):
    props = ("## Propositions\n| prop-id | statement | canon-status | governing-source | span |\n"
             "|---|---|---|---|---|\n| p1 | x | true | ms | s1 |\n")
    ev = ("## Evidence\n| span-id | source-id | locator | quote | note |\n|---|---|---|---|---|\n"
          f"| s1 | ms | ch01 | {quote} | |\n")
    return make_graph(Propositions=props, Evidence=ev)


def test_deviations_detects_rewritten_prose(tmp_path):
    g = tmp_path / "g.md"
    g.write_text(_dev_graph("a line that is not there"), encoding="utf-8")
    chdir = tmp_path / "chapters"
    chdir.mkdir()
    (chdir / "ch01.md").write_text("## Chapter 1\n\nThe prose was rewritten entirely.\n", encoding="utf-8")
    devs = sg.deviations(str(g), str(chdir))
    assert len(devs) == 1 and devs[0][0] == "s1"


def test_no_deviation_when_quote_matches(tmp_path):
    g = tmp_path / "g.md"
    g.write_text(_dev_graph("the exact line"), encoding="utf-8")
    chdir = tmp_path / "chapters"
    chdir.mkdir()
    (chdir / "ch01.md").write_text("## Chapter 1\n\nthe exact line is here.\n", encoding="utf-8")
    assert sg.deviations(str(g), str(chdir)) == []
