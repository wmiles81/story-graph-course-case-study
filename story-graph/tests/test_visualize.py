from conftest import make_graph
import story_graph as sg


def test_visualize_whole_graph_emits_html(tmp_path):
    props = ("## Propositions\n| prop-id | statement | canon-status | governing-source | span |\n"
             "|---|---|---|---|---|\n| p1 | x | true | ms | provisional |\n")
    epi = ("## Epistemic States\n| prop-id | holder | mode | since-ch | span |\n|---|---|---|---|---|\n"
           "| p1 | jonah | knows | 1 | provisional |\n")
    g = tmp_path / "g.md"
    g.write_text(make_graph(Propositions=props, **{"Epistemic States": epi}), encoding="utf-8")
    out = tmp_path / "g.html"
    n, e = sg.visualize_graph(str(g), str(out))
    doc = out.read_text(encoding="utf-8")
    assert "<svg" in doc and "jonah" in doc and "p1" in doc
    assert n >= 2 and e >= 1


def test_visualize_prop_focus_excludes_others(tmp_path):
    props = ("## Propositions\n| prop-id | statement | canon-status | governing-source | span |\n"
             "|---|---|---|---|---|\n| p1 | x | true | ms | s1 |\n| p2 | y | true | ms | provisional |\n")
    epi = ("## Epistemic States\n| prop-id | holder | mode | since-ch | span |\n|---|---|---|---|---|\n"
           "| p1 | reader | knows | 1 | s1 |\n")
    ev = ("## Evidence\n| span-id | source-id | locator | quote | note |\n|---|---|---|---|---|\n"
          "| s1 | ms | ch01 | q | |\n")
    g = tmp_path / "g.md"
    g.write_text(make_graph(Propositions=props, Evidence=ev, **{"Epistemic States": epi}), encoding="utf-8")
    out = tmp_path / "g.html"
    sg.visualize_graph(str(g), str(out), prop_id="p1")
    doc = out.read_text(encoding="utf-8")
    assert "p1" in doc and "reader" in doc and "s1" in doc and "ms" in doc
    assert "p2" not in doc
