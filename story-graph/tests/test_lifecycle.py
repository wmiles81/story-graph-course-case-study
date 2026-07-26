from conftest import MINIMAL_V2, make_graph
import story_graph as sg

PROV_PROP = ("## Propositions\n| prop-id | statement | canon-status | governing-source | span |\n"
             "|---|---|---|---|---|\n| p1 | Scrolls missing | true | ms | provisional |\n")


def prov_graph():
    return make_graph(Propositions=PROV_PROP)


def test_queue_lists_provisional_rows():
    rows = sg.unratified(sg.parse_graph(prov_graph()))
    assert ("Propositions", "p1") in rows


def test_queue_empty_on_clean_graph():
    assert sg.unratified(sg.parse_graph(MINIMAL_V2)) == []


def test_freeze_refuses_with_provisional(tmp_path):
    g = tmp_path / "g.md"
    g.write_text(prov_graph(), encoding="utf-8")
    out = tmp_path / "frozen.md"
    rep = sg.freeze_graph(str(g), "BOOK-CANON-v1.0", str(out))
    assert rep.errors and not out.exists()


def test_freeze_force_stamps_version_and_warns(tmp_path):
    g = tmp_path / "g.md"
    g.write_text(prov_graph(), encoding="utf-8")
    out = tmp_path / "frozen.md"
    rep = sg.freeze_graph(str(g), "BOOK-CANON-v1.0", str(out), force=True, at="2026-07-25")
    assert rep.errors == [] and out.exists()
    txt = out.read_text(encoding="utf-8")
    assert "| canon-version | BOOK-CANON-v1.0 |" in txt and "| frozen-at | 2026-07-25 |" in txt
    assert "FROZEN BOOK-CANON-v1.0" in txt
    # a frozen graph that still has provisional rows warns on validate
    rep2 = sg.validate(str(out))
    assert any("frozen canon" in w for w in rep2.warnings)


def test_freeze_clean_graph_succeeds_without_force(tmp_path):
    g = tmp_path / "g.md"
    g.write_text(MINIMAL_V2, encoding="utf-8")
    out = tmp_path / "frozen.md"
    rep = sg.freeze_graph(str(g), "CANON-v1.0", str(out), at="2026-07-25")
    assert rep.errors == [] and out.exists()
    assert sg.validate(str(out)).errors == []


def test_coverage_flags_thin_layers():
    """Coverage must name the gaps a validating-but-shallow graph has, so they are
    reported rather than discovered by squinting at a hairball."""
    props = ("## Propositions\n| prop-id | statement | canon-status | governing-source | span |\n"
             "|---|---|---|---|---|\n"
             "| p1 | a | true | ms | provisional |\n| p2 | b | true | ms | provisional |\n"
             "| p3 | c | true | ms | provisional |\n")
    epi = ("## Epistemic States\n| prop-id | holder | mode | since-ch | span |\n|---|---|---|---|---|\n"
           "| p1 | jonah | knows | 1 | provisional |\n")
    out = sg.coverage_report(sg.parse_graph(make_graph(Propositions=props, **{"Epistemic States": epi})), "T")
    assert "COVERAGE — T" in out
    assert "1/3" in out                                # only one of three has a holder
    assert "No believes-false states" in out          # irony impossible
    assert "have no holder" in out                     # thin epistemic layer
    assert "Relationships is effectively empty" in out or "Relationships" in out


def test_coverage_clean_graph_has_fewer_flags():
    out = sg.coverage_report(sg.parse_graph(MINIMAL_V2), "T")
    assert "LAYER POPULATION" in out and "EPISTEMIC DEPTH" in out
