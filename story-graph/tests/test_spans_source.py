from conftest import make_graph
import story_graph as sg


def setup_chapters(tmp_path):
    (tmp_path / "ch03.md").write_text("## Chapter 3\n\nJackson was alive after all.\n", encoding="utf-8")
    return str(tmp_path)


def verify(body, chapters_dir):
    sources = {"ms": {"type": "manuscript", "authority": 100}}
    graph = sg.parse_graph(make_graph(Evidence=body))
    report = sg.Report()
    sg.verify_spans(graph, sources, chapters_dir, report)
    return report


HEAD = ("## Evidence\n| span-id | source-id | locator | quote | note |\n"
        "|---|---|---|---|---|\n")


def test_quote_present_passes(tmp_path):
    d = setup_chapters(tmp_path)
    body = HEAD + "| s1 | ms | ch3 | Jackson was alive | |\n"
    assert verify(body, d).errors == []


def test_quote_absent_errors(tmp_path):
    d = setup_chapters(tmp_path)
    body = HEAD + "| s1 | ms | ch3 | Jackson was murdered | |\n"
    assert any("s1" in e and "not found" in e.lower() for e in verify(body, d).errors)


def test_no_chapters_dir_warns_not_errors(tmp_path):
    body = HEAD + "| s1 | ms | ch3 | anything | |\n"
    r = verify(body, "")
    assert r.errors == [] and any("could not verify" in w.lower() for w in r.warnings)
