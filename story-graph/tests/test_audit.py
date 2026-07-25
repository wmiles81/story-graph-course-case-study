import pytest
from conftest import make_graph
import story_graph as sg


def audit_text():
    props = ("## Propositions\n| prop-id | statement | canon-status | governing-source | span |\n"
             "|---|---|---|---|---|\n| p1 | Fact established later | true | ms | s1 |\n"
             "| p2 | An orphan claim | undetermined | ms |  |\n")
    epi = ("## Epistemic States\n| prop-id | holder | mode | since-ch | span |\n|---|---|---|---|---|\n"
           "| p1 | jonah | knows | 1 | s1 |\n")
    ev = ("## Evidence\n| span-id | source-id | locator | quote | note |\n|---|---|---|---|---|\n"
          "| s1 | ms | ch03 | some passage | |\n")
    loops = ("## Open Loops & Setups\n| id | planted-ch | expectation | must-fire-by | status | span |\n"
             "|---|---|---|---|---|---|\n| setup1 | 1 | must fire | 2 | UNFIRED | provisional |\n")
    return make_graph(Propositions=props, Evidence=ev,
                      **{"Epistemic States": epi}, **{"Open Loops & Setups": loops})


def _run(canon_ch=5, adj=frozenset()):
    pytest.importorskip("kuzu")
    import story_graph_query as q
    return q.run_audit(sg.parse_graph(audit_text()), canon_ch, adj)


def test_audit_flags_knows_before_evidence():
    _out, issues = _run()
    keys = {f"{d}:{k}" for d, k, _ in issues}
    assert "knows-before-evidence:jonah:p1" in keys


def test_audit_flags_orphan_and_overdue():
    _out, issues = _run()
    keys = {f"{d}:{k}" for d, k, _ in issues}
    assert "orphan-proposition:p2" in keys
    assert "overdue-setup:setup1" in keys


def test_adjudication_suppresses_one_issue():
    _out, issues = _run(adj={"knows-before-evidence:jonah:p1"})
    keys = {f"{d}:{k}" for d, k, _ in issues}
    assert "knows-before-evidence:jonah:p1" not in keys
    assert "orphan-proposition:p2" in keys
