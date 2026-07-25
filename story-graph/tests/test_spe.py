from conftest import MINIMAL_V2
import story_graph as sg

PH = "\n## Physics State\n| ch | vector | subject | anchor | note |\n|---|---|---|---|---|\n"


def spe_graph(rows="", with_physics=True):
    g = MINIMAL_V2.replace("| modules | none |", "| modules | spe |")
    if with_physics:
        g += PH + rows
    return g


def make_anchors(tmp_path, ids=("calm", "breaking", "cold")):
    d = tmp_path / "narrative_state" / "anchors"
    d.mkdir(parents=True)
    (d / "anchors.yaml").write_text("\n".join(f"  - id: {i}" for i in ids), encoding="utf-8")
    return str(tmp_path)


def _check(text, spe_dir=""):
    graph = sg.parse_graph(text)
    report = sg.Report()
    sg.check_physics(graph, spe_dir, report)
    return report


def test_anchor_in_catalog_ok(tmp_path):
    r = _check(spe_graph("| 1 | trauma | jonah | calm | eased |\n"), make_anchors(tmp_path))
    assert r.errors == []


def test_anchor_not_in_catalog_errors(tmp_path):
    r = _check(spe_graph("| 1 | trauma | jonah | euphoric | x |\n"), make_anchors(tmp_path))
    assert any("euphoric" in e for e in r.errors)


def test_freeform_vector_skips_anchor_check(tmp_path):
    r = _check(spe_graph("| 1 | intimacy-ladder | jonah-margot | rung-3-first-touch | x |\n"),
               make_anchors(tmp_path))
    assert r.errors == []


def test_no_catalog_warns_not_errors():
    r = _check(spe_graph("| 1 | trauma | jonah | calm | x |\n"), "")
    assert r.errors == [] and any("catalog not found" in w for w in r.warnings)


def test_ch_must_be_integer(tmp_path):
    r = _check(spe_graph("| one | trauma | jonah | calm | x |\n"), make_anchors(tmp_path))
    assert any("integer" in e for e in r.errors)


def test_validate_runs_physics_under_spe(tmp_path):
    g = spe_graph("| 1 | trauma | jonah | euphoric | x |\n")
    p = tmp_path / "g.md"
    p.write_text(g, encoding="utf-8")
    rep = sg.validate(str(p), spe_dir=make_anchors(tmp_path))
    assert any("euphoric" in e for e in rep.errors)


def test_spe_graph_requires_physics_section(tmp_path):
    p = tmp_path / "g.md"
    p.write_text(spe_graph("", with_physics=False), encoding="utf-8")
    rep = sg.validate(str(p))
    assert any("Physics State" in e for e in rep.errors)


def test_none_graph_never_triggers_physics(tmp_path):
    p = tmp_path / "g.md"
    p.write_text(MINIMAL_V2, encoding="utf-8")
    rep = sg.validate(str(p))
    assert not any("Physics State" in m for m in rep.errors + rep.warnings)
