from conftest import make_graph
import story_graph as sg


def test_entities_typed_and_kebab():
    body = ("## Entities\n| id | type | status | voice | note |\n|---|---|---|---|---|\n"
            "| Bad_Id | Character | active | male | |\n| ok | Sprite | active | - | |\n")
    graph = sg.parse_graph(make_graph(Entities=body))
    report = sg.Report()
    sg.check_entities(graph, report)
    assert any("kebab" in e for e in report.errors)
    assert any("Sprite" in e for e in report.errors)


def test_setup_status_regex():
    body = ("## Open Loops & Setups\n| id | planted-ch | expectation | must-fire-by | status | span |\n"
            "|---|---|---|---|---|---|\n| pistol | 2 | fired later | 20 | LOADED | s1 |\n")
    graph = sg.parse_graph(make_graph(**{"Open Loops & Setups": body}))
    report = sg.Report()
    sg.check_open_loops(graph, 5, {"s1"}, report)
    assert any("LOADED" in e for e in report.errors)


def test_overdue_setup_warns():
    body = ("## Open Loops & Setups\n| id | planted-ch | expectation | must-fire-by | status | span |\n"
            "|---|---|---|---|---|---|\n| pistol | 2 | must fire | 4 | UNFIRED | s1 |\n")
    graph = sg.parse_graph(make_graph(**{"Open Loops & Setups": body}))
    report = sg.Report()
    sg.check_open_loops(graph, 5, {"s1"}, report)
    assert any("OVERDUE" in w for w in report.warnings)


def test_commit_log_monotonic():
    body = "## Canon Commit Log\n- ch 3: a\n- ch 2: b\n"
    graph = sg.parse_graph(make_graph(**{"Canon Commit Log": body}))
    report = sg.Report()
    sg.check_commit_log(graph, report)
    assert any("regression" in e for e in report.errors)
