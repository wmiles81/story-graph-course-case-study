from conftest import make_graph
import story_graph as sg


def epi_report(body, entity_ids=frozenset({"jonah", "margot"}),
               prop_ids=frozenset({"jackson-alive"}), span_ids=frozenset({"s1"})):
    graph = sg.parse_graph(make_graph(**{"Epistemic States": body}))
    report = sg.Report()
    sg.check_epistemic(graph, set(entity_ids), set(prop_ids), set(span_ids), report)
    return report


HEAD = ("## Epistemic States\n| prop-id | holder | mode | since-ch | span |\n"
        "|---|---|---|---|---|\n")


def test_reader_is_valid_holder():
    body = HEAD + "| jackson-alive | reader | knows | 3 | s1 |\n"
    assert epi_report(body).errors == []


def test_unknown_holder_is_error():
    body = HEAD + "| jackson-alive | ghost | knows | 3 | s1 |\n"
    assert any("ghost" in e for e in epi_report(body).errors)


def test_bad_mode_is_error():
    body = HEAD + "| jackson-alive | jonah | assumes | 3 | s1 |\n"
    assert any("assumes" in e for e in epi_report(body).errors)


def test_knows_needs_span():
    body = HEAD + "| jackson-alive | jonah | knows | 3 |  |\n"
    assert any("span" in e for e in epi_report(body).errors)


def test_embargo_carried_forward():
    body = (HEAD
            + "| jackson-alive | margot | embargoed-until | 11 |  |\n"
            + "| jackson-alive | margot | knows | 5 | s1 |\n")
    assert any("embargo" in e.lower() for e in epi_report(body).errors)


def test_unknown_proposition_is_error():
    body = HEAD + "| nonexistent-prop | jonah | knows | 3 | s1 |\n"
    assert any("nonexistent-prop" in e for e in epi_report(body).errors)
