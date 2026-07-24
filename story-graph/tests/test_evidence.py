from conftest import make_graph
import story_graph as sg


def ev_report(body, sources=None):
    sources = sources or {"ms": {"type": "manuscript", "authority": 100}}
    graph = sg.parse_graph(make_graph(Evidence=body))
    report = sg.Report()
    span_ids = sg.check_evidence(graph, sources, report)
    return span_ids, report


HEAD = ("## Evidence\n| span-id | source-id | locator | quote | note |\n"
        "|---|---|---|---|---|\n")


def test_valid_span_registered():
    body = HEAD + '| s1 | ms | ch3 | Jackson was alive | |\n'
    span_ids, report = ev_report(body)
    assert "s1" in span_ids and report.errors == []


def test_span_with_unknown_source_is_error():
    body = HEAD + '| s1 | nope | ch3 | text | |\n'
    _, report = ev_report(body)
    assert any("nope" in e for e in report.errors)


def test_manuscript_span_without_quote_is_error():
    body = HEAD + '| s1 | ms | ch3 |  | |\n'
    _, report = ev_report(body)
    assert any("quote" in e for e in report.errors)


def test_duplicate_span_id_is_error():
    body = HEAD + '| s1 | ms | ch3 | a | |\n| s1 | ms | ch4 | b | |\n'
    _, report = ev_report(body)
    assert any("duplicate" in e for e in report.errors)
