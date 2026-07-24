from conftest import make_graph
import story_graph as sg


def prop_report(body, span_ids=frozenset({"s1"})):
    graph = sg.parse_graph(make_graph(Propositions=body))
    report = sg.Report()
    sources = {"ms": {"type": "manuscript", "authority": 100}}
    sg.check_propositions(graph, sources, set(span_ids), report)
    return report


def test_true_prop_needs_span():
    body = ("## Propositions\n| prop-id | statement | canon-status | governing-source | span |\n"
            "|---|---|---|---|---|\n| jackson-alive | Jackson lives | true | ms |  |\n")
    assert any("span" in e for e in prop_report(body).errors)


def test_true_prop_with_span_ok():
    body = ("## Propositions\n| prop-id | statement | canon-status | governing-source | span |\n"
            "|---|---|---|---|---|\n| jackson-alive | Jackson lives | true | ms | s1 |\n")
    assert prop_report(body).errors == []


def test_bad_canon_status_is_error():
    body = ("## Propositions\n| prop-id | statement | canon-status | governing-source | span |\n"
            "|---|---|---|---|---|\n| p1 | x | maybe | ms | s1 |\n")
    assert any("canon-status" in e for e in prop_report(body).errors)


def test_provisional_true_prop_without_span_warns_not_errors():
    body = ("## Propositions\n| prop-id | statement | canon-status | governing-source | span |\n"
            "|---|---|---|---|---|\n| p1 | x | true | ms | provisional |\n")
    r = prop_report(body)
    assert r.errors == [] and any("provisional" in w for w in r.warnings)
