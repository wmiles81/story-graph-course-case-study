import importlib.util
from pathlib import Path
import pytest
from conftest import MINIMAL_V2, make_graph

APP = Path(__file__).resolve().parents[2] / "app" / "story_graph_app.py"


def _app():
    spec = importlib.util.spec_from_file_location("sgapp", APP)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_app_summary_and_graph(tmp_path):
    app = _app()
    g = tmp_path / "g.md"
    g.write_text(MINIMAL_V2, encoding="utf-8")
    app.load(str(g))
    s = app.api_summary()
    assert s["counts"]["entities"] == 2 and "kuzu" in s
    assert isinstance(app.api_graph()["nodes"], list)


def test_graph_nodes_carry_sizing_metrics(tmp_path):
    """Node size encodes receipts / believers / contested, so every node must ship
    those magnitudes — and `contested` must stay 0 unless holders actually disagree."""
    app = _app()
    props = ("## Propositions\n| prop-id | statement | canon-status | governing-source | span |\n"
             "|---|---|---|---|---|\n"
             "| p1 | jackson is alive | contested | ms | ev1 ev2 |\n"
             "| p2 | nobody argues about this | true | ms | provisional |\n")
    evid = ("## Evidence\n| span-id | source-id | locator | quote | note |\n|---|---|---|---|---|\n"
            "| ev1 | ms | ch01 | a | |\n| ev2 | ms | ch02 | b | |\n")
    epi = ("## Epistemic States\n| prop-id | holder | mode | since-ch | span |\n|---|---|---|---|---|\n"
           "| p1 | reader | knows | 1 | provisional |\n"
           "| p1 | jonah | believes-false | 1 | provisional |\n"
           "| p2 | jonah | knows | 1 | provisional |\n"
           "| p2 | reader | knows | 1 | provisional |\n")
    g = tmp_path / "g.md"
    g.write_text(make_graph(Propositions=props, Evidence=evid, **{"Epistemic States": epi}),
                 encoding="utf-8")
    app.load(str(g))
    m = {n["id"]: n["m"] for n in app.api_graph()["nodes"]}
    assert m["p1"] == {"ev": 2, "bel": 2, "con": 1}     # two receipts, two holders, one disagreement
    assert m["p2"]["ev"] == 0 and m["p2"]["bel"] == 2
    assert m["p2"]["con"] == 0, "agreement is not contested"
    assert m["jonah"]["bel"] == 2                        # holds a stance on both claims
    assert m["library"] == {"ev": 0, "bel": 0, "con": 0}  # never scores, but always present


def test_app_cypher_and_bad_query(tmp_path):
    pytest.importorskip("kuzu")
    app = _app()
    props = ("## Propositions\n| prop-id | statement | canon-status | governing-source | span |\n"
             "|---|---|---|---|---|\n| p1 | x | true | ms | provisional |\n")
    g = tmp_path / "g.md"
    g.write_text(make_graph(Propositions=props), encoding="utf-8")
    app.load(str(g))
    r = app.api_cypher("MATCH (p:Proposition) RETURN p.id")
    assert r.get("columns") == ["p.id"] and len(r["rows"]) == 1
    assert "error" in app.api_cypher("NONSENSE QUERY")


def test_app_schema_and_ask_guards(tmp_path):
    app = _app()
    schema = app.api_schema()["schema"]
    assert "Proposition" in schema and "EPISTEMIC" in schema and "SUPPORTS" in schema
    # empty question is rejected before any SDK/kuzu need — deterministic
    assert "plain English" in app.api_ask("")["error"]


def test_app_settings_providers_roundtrip(tmp_path):
    app = _app()
    app._env_path = lambda: tmp_path / ".env"  # never touch the real .env during tests
    s = app.api_settings_get()
    names = {p["name"] for p in s["providers"]}
    assert {"openrouter", "ollama", "lmstudio"} <= names and "kuzu" in s
    app.api_settings_put({"provider": "openrouter", "model": "anthropic/claude-3.5-sonnet"})
    s2 = app.api_settings_get()
    assert s2["provider"] == "openrouter" and s2["model"] == "anthropic/claude-3.5-sonnet"
    app.api_settings_put({"provider": "openrouter", "api_key": "sk-or-x"})
    assert any(p["name"] == "openrouter" and p["key_set"] for p in app.api_settings_get()["providers"])
    # persisted to .env, restorable after a "restart"
    env = app._env_read()
    assert env["OPENROUTER_API_KEY"] == "sk-or-x" and env["SGOS_MODEL"] == "anthropic/claude-3.5-sonnet"
    # local provider probe fails fast (nothing listening) — both return dicts, no exception
    assert "models" in app.api_models("ollama")
    assert "ok" in app.api_testkey("ollama")
    assert app.api_models("bogus")["error"] == "unknown provider"


def test_inline_frontend_js_is_syntactically_valid(tmp_path):
    """The whole UI is one inline <script>; a syntax error there kills the entire
    app silently (blank page, no tabs). Catch it in CI rather than in the browser."""
    import re, shutil, subprocess
    node = shutil.which("node")
    if not node:
        pytest.skip("node not available to syntax-check the inline JS")
    src = APP.read_text(encoding="utf-8")
    i = src.index('PAGE = r"""')
    page = src[i + len('PAGE = r"""'): src.index('"""', i + 12)]
    m = re.search(r"<script>(.*)</script>", page, re.S)
    assert m, "no inline <script> found in PAGE"
    js = tmp_path / "page.js"
    js.write_text(m.group(1), encoding="utf-8")
    r = subprocess.run([node, "--check", str(js)], capture_output=True, text=True)
    assert r.returncode == 0, f"inline JS syntax error:\n{r.stderr}"


def test_ask_repairs_invalid_cypher_once(tmp_path):
    """An invalid generated query must be fed back to the model once and repaired,
    not surfaced as a raw binder error (the user hit exactly this)."""
    pytest.importorskip("kuzu")
    import json as _json
    app = _app()
    app._env_path = lambda: tmp_path / ".env"
    g = tmp_path / "g.md"
    props = ("## Propositions\n| prop-id | statement | canon-status | governing-source | span |\n"
             "|---|---|---|---|---|\n| p1 | x | true | ms | provisional |\n")
    epi = ("## Epistemic States\n| prop-id | holder | mode | since-ch | span |\n|---|---|---|---|---|\n"
           "| p1 | reader | knows | 1 | provisional |\n")
    g.write_text(make_graph(Propositions=props, **{"Epistemic States": epi}), encoding="utf-8")
    app.load(str(g))
    app.STATE.update(provider="ollama", model="fake")

    bad = ("MATCH (h:Holder)-[e:EPISTEMIC]->(p:Proposition) RETURN DISTINCT p.id AS pid "
           "ORDER BY CAST(e.since_ch AS INT64)")          # e is out of scope after DISTINCT
    good = "MATCH (h:Holder)-[e:EPISTEMIC]->(p:Proposition) RETURN h.id AS holder, p.id AS pid"
    calls = []

    def fake_chat(provider, model, system, user, max_tokens=2048):
        calls.append(user)
        return _json.dumps({"cypher": bad if len(calls) == 1 else good, "explanation": "s"})

    app._chat = fake_chat
    r = app.api_ask("who knows what?")
    assert len(calls) == 2, "should retry exactly once"
    assert "Engine error" in calls[1], "the retry must include the engine's error"
    assert r.get("repaired") is True and "error" not in r
    assert r["rows"] and r["columns"] == ["holder", "pid"]


# ----------------------------------------------------------------- the help drawer

HELP = APP.parent / "help"


def test_every_manifest_topic_exists_and_is_not_empty():
    """A help system whose links 404 is worse than none — it teaches you not to open it."""
    import json
    man = json.loads((HELP / "manifest.json").read_text(encoding="utf-8"))
    missing, empty = [], []
    n = 0
    for sec in man["sections"]:
        for t in sec["topics"]:
            if "file" not in t:
                continue
            n += 1
            f = HELP / t["file"]
            if not f.is_file():
                missing.append(t["file"])
            elif len(f.read_text(encoding="utf-8").strip()) < 80:
                empty.append(t["file"])
    assert n >= 15, f"only {n} topics — the manifest looks truncated"
    assert missing == [], f"manifest points at files that do not exist: {missing}"
    assert empty == [], f"topics with almost no content: {empty}"


def test_every_help_file_is_reachable_from_the_manifest():
    """The other direction: a topic nobody can navigate to may as well not be written."""
    import json
    man = json.loads((HELP / "manifest.json").read_text(encoding="utf-8"))
    listed = {t["file"] for sec in man["sections"] for t in sec["topics"] if "file" in t}
    on_disk = {str(p.relative_to(HELP)) for p in HELP.rglob("*.md")}
    assert on_disk - listed == set(), f"orphaned help files: {sorted(on_disk - listed)}"


def test_help_is_served_and_cannot_escape_its_directory(tmp_path):
    """`_help` is the one route that maps a URL onto the filesystem."""
    app = _app()

    class FakeHandler:
        _help = app.Handler._help
        sent = None
        def _send(self, body, ctype="application/json", status=200):
            self.sent = (body, ctype, status)
        def _json(self, obj, status=200):
            self.sent = (obj, "json", status)

    h = FakeHandler()
    h._help("manifest.json")
    assert h.sent[1].startswith("application/json") and '"sections"' in h.sent[0]

    h._help("reference/glossary.md")
    assert h.sent[1].startswith("text/markdown") and "Alias" in h.sent[0]

    for escape in ("../story_graph_app.py", "../../README.md", "nope.md",
                   "../../../etc/passwd"):
        h._help(escape)
        assert h.sent[2] == 404, f"{escape} was not refused: {h.sent[:2]}"


def test_the_drawer_is_wired_into_the_page():
    """The markup and the handlers the drawer needs, so a rename cannot silently
    orphan the Help button."""
    src = APP.read_text(encoding="utf-8")
    for needed in ('id="helpdrawer"', 'id="helpbtn"', 'id="helpgrip"', 'id="helpnav"',
                   'id="helpdoc"', 'id="helpfilter"', 'id="helpclose"',
                   "function mdRender(", "function helpOpen(", "function helpClose(",
                   "--help-w", "ew-resize", "translateX(101%)"):
        assert needed in src, f"help drawer is missing {needed}"


def test_the_help_markdown_renderer_escapes_and_renders(tmp_path):
    """Runs the ACTUAL renderer out of the page, not a copy of it."""
    import re, shutil, subprocess
    node = shutil.which("node")
    if not node:
        pytest.skip("node not available")
    src = APP.read_text(encoding="utf-8")
    fn = src[src.index("function mdRender("):src.index("async function helpText(")]
    js = tmp_path / "md.js"
    js.write_text(fn + """
const out = [];
const t=(n,md,f)=>out.push([n, !!f(mdRender(md))]);
t('escapes html in prose', 'A <script>alert(1)</script> tag.',
  h=>h.includes('&lt;script&gt;') && !h.includes('<script>'));
t('escapes html in a fence', '```\\n<script>x</script>\\n```',
  h=>h.includes('&lt;script&gt;') && !/<script>/.test(h));
t('renders a table', '| a | b |\\n|---|---|\\n| 1 | 2 |',
  h=>/<table><thead>/.test(h) && /<td>1<\\/td>/.test(h));
t('drops the separator row', '| a |\\n|---|\\n| 1 |', h=>!/<td>-+<\\/td>/.test(h));
t('no sentinel leaks', '```\\ncode\\n```\\n\\ntext', h=>!/@@CB\\d+@@/.test(h));
t('bold and italic', '**b** and *i*', h=>/<strong>b<\\/strong>/.test(h)&&/<em>i<\\/em>/.test(h));
console.log(JSON.stringify(out));
""", encoding="utf-8")
    r = subprocess.run([node, str(js)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    import json
    results = json.loads(r.stdout)
    failed = [n for n, ok in results if not ok]
    assert failed == [], f"renderer failures: {failed}"
