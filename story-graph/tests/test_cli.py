import subprocess, sys
from pathlib import Path
from conftest import MINIMAL_V2, make_graph
import story_graph as sg

ASSETS = Path(__file__).resolve().parent.parent / "assets"


def test_minimal_graph_validates_clean(tmp_path):
    g = tmp_path / "Story-Graph.md"
    g.write_text(MINIMAL_V2, encoding="utf-8")
    report = sg.validate(str(g))
    assert report.errors == [], report.errors


def test_dramatic_irony_graph_validates(tmp_path):
    props = ("## Propositions\n| prop-id | statement | canon-status | governing-source | span |\n"
             "|---|---|---|---|---|\n| jackson-alive | Jackson lives | true | ms | s1 |\n")
    epi = ("## Epistemic States\n| prop-id | holder | mode | since-ch | span |\n|---|---|---|---|---|\n"
           "| jackson-alive | reader | knows | 3 | s1 |\n| jackson-alive | jonah | believes-false | 3 | s1 |\n")
    ev = ("## Evidence\n| span-id | source-id | locator | quote | note |\n|---|---|---|---|---|\n"
          "| s1 | ms | ch3 | Jackson was alive | |\n")
    text = make_graph(Propositions=props, Evidence=ev, **{"Epistemic States": epi})
    g = tmp_path / "Story-Graph.md"
    g.write_text(text, encoding="utf-8")
    report = sg.validate(str(g))
    assert report.errors == [], report.errors


def test_cli_exit_code_on_error(tmp_path):
    g = tmp_path / "Story-Graph.md"
    g.write_text(MINIMAL_V2.replace("| ontology-version | 2 |", "| ontology-version | 1 |"), encoding="utf-8")
    proc = subprocess.run([sys.executable, str(ASSETS / "story_graph.py"), "validate", str(g)],
                          capture_output=True, text=True)
    assert proc.returncode == 1
    assert "RESULT:" in proc.stdout
