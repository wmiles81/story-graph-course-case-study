from conftest import MINIMAL_V2, make_graph
import story_graph as sg


def run(text):
    graph = sg.parse_graph(text)
    report = sg.Report()
    sg.check_structure(graph, report)
    sg.check_header(graph, report)
    return report


def test_minimal_graph_has_clean_structure():
    report = run(MINIMAL_V2)
    assert report.errors == []


def test_missing_core_section_is_error():
    text = MINIMAL_V2.replace("## Evidence\n| span-id | source-id | locator | quote | note |\n|---|---|---|---|---|\n", "")
    report = run(text)
    assert any("Evidence" in e for e in report.errors)


def test_header_requires_ontology_version_two():
    text = MINIMAL_V2.replace("| ontology-version | 2 |", "| ontology-version | 1 |")
    report = run(text)
    assert any("ontology-version" in e for e in report.errors)
