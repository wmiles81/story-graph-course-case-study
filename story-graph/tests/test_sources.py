from conftest import make_graph
import story_graph as sg


def sources_report(body):
    graph = sg.parse_graph(make_graph(**{"Sources": body}))
    report = sg.Report()
    sg.check_sources(graph, report)
    return report


def test_valid_source_ok():
    body = ("## Sources\n| source-id | type | authority | note |\n|---|---|---|---|\n"
            "| ms | manuscript | 100 | |\n")
    assert sources_report(body).errors == []


def test_unknown_type_is_error():
    body = ("## Sources\n| source-id | type | authority | note |\n|---|---|---|---|\n"
            "| ms | screenplay | 100 | |\n")
    assert any("screenplay" in e for e in sources_report(body).errors)


def test_non_integer_authority_is_error():
    body = ("## Sources\n| source-id | type | authority | note |\n|---|---|---|---|\n"
            "| ms | manuscript | high | |\n")
    assert any("authority" in e for e in sources_report(body).errors)


def test_editorial_cannot_be_governing_source():
    props = ("## Propositions\n| prop-id | statement | canon-status | governing-source | span |\n"
             "|---|---|---|---|---|\n| p1 | x | true | ed | s1 |\n")
    srcs = ("## Sources\n| source-id | type | authority | note |\n|---|---|---|---|\n"
            "| ed | editorial | 10 | |\n")
    graph = sg.parse_graph(make_graph(Sources=srcs, Propositions=props))
    report = sg.Report()
    sources = sg.check_sources(graph, report)
    sg.check_authority(graph, sources, report)
    assert any("editorial" in e and "governing" in e for e in report.errors)
