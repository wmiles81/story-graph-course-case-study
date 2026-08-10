# Help System Rework Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rework the story-graph app's help drawer into a complete help system: full content coverage (app tabs, skill workflows, all 21 CLI subcommands), a credits section, and a true explorer left panel (collapsible sections, body-text search, maximize).

**Architecture:** No new architecture. The single-file stdlib server (`app/story_graph_app.py`) keeps serving `app/help/` (`manifest.json` + markdown tree). One new endpoint (`GET /help/search?q=`), client-side JS/CSS changes to the drawer, and new/updated markdown content. Spec: `docs/superpowers/specs/2026-08-02-help-system-rework-design.md`.

**Tech Stack:** Python 3.10+ stdlib only (no new deps), inline vanilla JS/CSS, pytest (tests in `story-graph/tests/`), Playwright MCP for browser verification.

## Global Constraints

- **No new dependencies.** Server is stdlib-only; client has no external JS. `kuzu` stays optional.
- **File versioning (user's global rule, unconditional).** Before first modification: `app/story_graph_app.py` → copy to `app/story_graph_app_v1.py`; `app/help/manifest.json` → copy to `app/help/manifest_v1.json`; `story-graph/tests/test_app.py` → copy to `story-graph/tests/test_app_v1.py`; `story-graph/tests/conftest.py` → copy to `story-graph/tests/conftest_v1.py`. Then edit the unsuffixed files in place (shift-rename form: unsuffixed = current). Existing help topic `.md` files edited in Task 8: copy prior text to `<name>_v2.md` first, manifest keeps pointing at the unsuffixed name (per approved spec §4). Never touch existing `_v#` files.
- **Help must work while the graph is compiling** — the `/help/search` endpoint must also be reachable from `Handler._starting`.
- **All content derived from real functionality** — every claim in a new topic traces to code or bundled skill docs, not invention.
- **Existing tests must stay green:** `python3 -m pytest story-graph/tests/ -q` (295+ tests). Run from repo root.
- The help server serves only files under `app/help/`; the search index reads only manifest-listed files.

---

### Task 1: Version snapshots + test-collection guard

The user's versioning rule requires `_v#` snapshots of every file this plan edits — but `test_app_v1.py` matches pytest's `test_*.py` discovery glob and would run stale duplicates, and `test_every_help_file_is_reachable_from_the_manifest` treats any unlisted `.md` under `help/` as an orphan, which `_v#` topic copies would trip. This task creates the snapshots and teaches the test suite that `_v#` files are history, in one commit so the suite is never broken in between.

**Files:**
- Create: `app/story_graph_app_v1.py`, `app/help/manifest_v1.json`, `story-graph/tests/test_app_v1.py`, `story-graph/tests/conftest_v1.py` (verbatim copies)
- Modify: `story-graph/tests/conftest.py` (top of file), `story-graph/tests/test_app.py:171-177`

**Interfaces:**
- Produces: the convention *`_v#`-suffixed files are ignored by pytest collection and by the help orphan test* — every later task relies on it.

- [ ] **Step 1: Make the four snapshot copies**

```bash
cp app/story_graph_app.py app/story_graph_app_v1.py
cp app/help/manifest.json app/help/manifest_v1.json
cp story-graph/tests/test_app.py story-graph/tests/test_app_v1.py
cp story-graph/tests/conftest.py story-graph/tests/conftest_v1.py
```

- [ ] **Step 2: Guard pytest collection.** Add near the top of `story-graph/tests/conftest.py` (module level, after existing imports):

```python
# _v# files are versioned history (user convention), never live code — don't collect.
collect_ignore_glob = ["*_v[0-9]*.py"]
```

- [ ] **Step 3: Amend the orphan test.** In `test_every_help_file_is_reachable_from_the_manifest` (test_app.py ~line 176), change the `on_disk` comprehension to skip versioned history:

```python
    import re
    on_disk = {str(p.relative_to(HELP)) for p in HELP.rglob("*.md")
               if not re.search(r"_v\d+$", p.stem)}
```

- [ ] **Step 4: Prove the guard works.** Create a throwaway `app/help/reference/glossary_v2.md` (any text), run:

```bash
python3 -m pytest story-graph/tests/test_app.py -q
```

Expected: PASS (orphan test ignores the `_v2` file; `test_app_v1.py` not collected — confirm with `python3 -m pytest story-graph/tests/ --collect-only -q | grep -c test_app_v1` → `0`). Then delete the throwaway file.

- [ ] **Step 5: Commit**

```bash
git add app/story_graph_app_v1.py app/help/manifest_v1.json story-graph/tests/test_app_v1.py story-graph/tests/conftest_v1.py story-graph/tests/conftest.py story-graph/tests/test_app.py
git commit -m "chore(help): version snapshots + teach tests that _v# files are history"
```

---

### Task 2: Server body-search index + `GET /help/search`

**Files:**
- Modify: `app/story_graph_app.py` — module level near `Handler._help` (~line 541), `Handler._get` routing (~line 537), `Handler._starting` (~line 566)
- Test: `story-graph/tests/test_app.py` (append)

**Interfaces:**
- Produces: `help_search(qtext: str) -> dict` module function returning `{"q": <echo>, "matches": [{"id": <topic-id>, "snippet": <str ≤160>}]}`; HTTP `GET /help/search?q=<text>` returning that JSON. Task 4 (client) consumes the HTTP shape.

- [ ] **Step 1: Write the failing tests** (append to `story-graph/tests/test_app.py`):

```python
def test_help_search_finds_body_text_and_returns_snippets():
    """Body search: a term that appears in topic bodies must surface those topics
    with a one-line snippet; blank and absent terms return nothing."""
    app = _app()
    res = app.help_search("kuzu")
    assert res["matches"], "at least one topic body mentions kuzu"
    for m in res["matches"]:
        assert m["id"] and m["snippet"] and len(m["snippet"]) <= 160
    assert app.help_search("")["matches"] == []
    assert app.help_search("z")["matches"] == []          # <2 chars: too noisy
    assert app.help_search("zzqx-not-present")["matches"] == []


def test_help_search_indexes_only_manifest_listed_files():
    """A _v# history file must never leak into search results."""
    import json
    app = _app()
    man = json.loads((HELP / "manifest.json").read_text(encoding="utf-8"))
    listed_ids = {t["id"] for s in man["sections"] for t in s["topics"]}
    for m in app.help_search("the")["matches"]:
        assert m["id"] in listed_ids
```

- [ ] **Step 2: Run to verify they fail**

```bash
python3 -m pytest story-graph/tests/test_app.py -k help_search -v
```

Expected: FAIL — `AttributeError: module ... has no attribute 'help_search'`.

- [ ] **Step 3: Implement.** In `app/story_graph_app.py`, module level (directly above `class Handler` or beside `_help`):

```python
_HELP_INDEX = None   # [(topic-id, body-text)] — manifest-listed topics only; static per process


def _help_index():
    global _HELP_INDEX
    if _HELP_INDEX is None:
        import json
        root = Path(__file__).resolve().parent / "help"
        idx = []
        try:
            man = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
            for sec in man.get("sections", []):
                for t in sec.get("topics", []):
                    if "file" not in t:
                        continue
                    try:
                        idx.append((t["id"], (root / t["file"]).read_text(encoding="utf-8")))
                    except OSError:
                        pass
        except (OSError, ValueError):
            pass
        _HELP_INDEX = idx
    return _HELP_INDEX


def help_search(qtext):
    """Case-insensitive substring search over topic bodies. Returns the line the
    first match sits on as a snippet — enough to decide whether to click."""
    q = (qtext or "").strip().lower()
    matches = []
    if len(q) >= 2:
        for tid, body in _help_index():
            i = body.lower().find(q)
            if i < 0:
                continue
            start = body.rfind("\n", 0, i) + 1
            end = body.find("\n", i)
            end = len(body) if end < 0 else end
            snippet = body[start:end].strip().lstrip("#>|-* ").strip()
            matches.append({"id": tid, "snippet": snippet[:160]})
    return {"q": qtext or "", "matches": matches}
```

In `Handler._get`, immediately BEFORE the existing `if u.path.startswith("/help/"):` line:

```python
        if u.path == "/help/search":
            return self._json(help_search(q.get("q", [""])[0]))
```

In `Handler._starting`, immediately BEFORE the existing `if path.startswith("/help/"):` line (note `_starting` only parsed the path, so parse the query here):

```python
        if path == "/help/search":
            from urllib.parse import parse_qs
            qs = parse_qs(urlparse(self.path).query)
            return self._json(help_search(qs.get("q", [""])[0]))
```

- [ ] **Step 4: Run the tests**

```bash
python3 -m pytest story-graph/tests/test_app.py -q
```

Expected: all PASS.

- [ ] **Step 5: Commit**

```bash
git add app/story_graph_app.py story-graph/tests/test_app.py
git commit -m "feat(help): body-text search index + GET /help/search endpoint"
```

---

### Task 3: Explorer left panel — collapsible sections

**Files:**
- Modify: `app/story_graph_app.py` — CSS `#helpnav .sec` (~line 735), JS `HELP` state (~line 1420), `helpNav()` (~line 1465)

**Interfaces:**
- Consumes: nothing new.
- Produces: `helpNav()` renders section headers with fold arrows; fold state in `localStorage` key `sgos.helpfold` as `{"<section-id>": true}` (true = closed). Task 4 re-renders through the same `helpNav()`.

- [ ] **Step 1: CSS.** Extend the `#helpnav .sec` rule block (after line 736) with:

```css
#helpnav .sec::before{content:'▾ ';opacity:.6}
#helpnav .sec.closed::before{content:'▸ '}
```

- [ ] **Step 2: JS state + render.** Below `const HELP_W_KEY='sgos.helpw';` (~line 1419) add:

```js
const HELP_FOLD_KEY='sgos.helpfold';
function foldState(){try{return JSON.parse(localStorage.getItem(HELP_FOLD_KEY)||'{}')}catch(_){return{}}}
```

Replace the body of `helpNav()` (lines 1465-1477) with:

```js
function helpNav(){
 const nav=document.getElementById('helpnav');if(!nav)return;
 const f=(document.getElementById('helpfilter').value||'').trim().toLowerCase();
 const fold=foldState();
 nav.innerHTML='';
 (HELP.manifest?.sections||[]).forEach(sec=>{
  const topics=(sec.topics||[]).filter(t=>!f||t.title.toLowerCase().includes(f)||sec.title.toLowerCase().includes(f));
  if(!topics.length)return;
  // A fold never hides the active topic, and filtering unfolds everything that matched.
  const closed=!f&&!topics.some(t=>t.id===HELP.active)&&fold[sec.id]===true;
  const h=$(`<div class="sec${closed?' closed':''}">${esc(sec.title)}</div>`);
  h.onclick=()=>{const s=foldState();s[sec.id]=!closed;localStorage.setItem(HELP_FOLD_KEY,JSON.stringify(s));helpNav()};
  nav.appendChild(h);
  if(closed)return;
  topics.forEach(t=>{
   const b=$(`<button class="tp${t.id===HELP.active?' on':''}">${esc(t.title)}</button>`);
   b.onclick=()=>helpShow(t.id);nav.appendChild(b)})});
 if(!nav.children.length)nav.appendChild($(`<div class="sec">no match</div>`));
}
```

(The pre-existing section-header `cursor:pointer;user-select:none` CSS already anticipates clickability — keep it.)

- [ ] **Step 3: Verify JS still parses**

```bash
python3 -m pytest story-graph/tests/test_app.py -k inline_frontend -v
```

Expected: PASS.

- [ ] **Step 4: Hand-check in the browser.** `python3 app/story_graph_app.py series/books/book-3/Story-Graph.md --port 8766`, open help (❓): click a section header → topics fold and the arrow flips; reload → still folded; open a topic in a folded section via search, clear search → its section is auto-expanded.

- [ ] **Step 5: Commit**

```bash
git add app/story_graph_app.py
git commit -m "feat(help): collapsible explorer sections with remembered fold state"
```

---

### Task 4: Client search integration (title + body, with snippets)

**Files:**
- Modify: `app/story_graph_app.py` — CSS near `#helpnav .tp` (~line 740), `HELP` state, `helpNav()` filter line, `helpInit` input listener (~line 1513)

**Interfaces:**
- Consumes: `GET /help/search?q=` from Task 2; `helpNav()` from Task 3.
- Produces: `HELP.body` — `{<topic-id>: <snippet>}` for the current query, merged into the tree render.

- [ ] **Step 1: CSS** (after the `#helpnav .tp.on` rule):

```css
#helpnav .snip{font:11px system-ui;color:var(--muted);padding:0 .8rem .3rem 1.4rem;
 white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
```

- [ ] **Step 2: JS.** Change the `HELP` state line to include the body-match map:

```js
let HELP={manifest:null,active:null,loaded:{},body:{}};
```

In `helpNav()` (Task 3 version), widen the topic filter to include body matches and render snippets — replace the `.filter(...)` line with:

```js
  const topics=(sec.topics||[]).filter(t=>!f||t.title.toLowerCase().includes(f)||sec.title.toLowerCase().includes(f)||HELP.body[t.id]!=null);
```

and inside `topics.forEach`, after `nav.appendChild(b)`, add:

```js
   if(f&&HELP.body[t.id]!=null&&!t.title.toLowerCase().includes(f))
    nav.appendChild($(`<div class="snip">${esc(HELP.body[t.id])}</div>`));
```

In `helpInit`, replace `document.getElementById('helpfilter').addEventListener('input',helpNav);` with a debounced body-search merge:

```js
 let srchT=0;
 document.getElementById('helpfilter').addEventListener('input',()=>{
  const q=(document.getElementById('helpfilter').value||'').trim();
  clearTimeout(srchT);HELP.body={};helpNav();
  if(q.length>=2)srchT=setTimeout(async()=>{
   try{
    const r=await fetch('/help/search?q='+encodeURIComponent(q),{cache:'no-store'});
    if(!r.ok)return;
    const j=await r.json();HELP.body={};
    (j.matches||[]).forEach(m=>{HELP.body[m.id]=m.snippet});
    helpNav();
   }catch(_){/* body search is best-effort; title filter already rendered */}
  },200);
 });
```

- [ ] **Step 3: Verify JS parses + suite green**

```bash
python3 -m pytest story-graph/tests/test_app.py -q
```

Expected: PASS.

- [ ] **Step 4: Hand-check.** In the running app, search a body-only term (e.g. `rebinding` — appears in safety topic bodies, no topic title). Expected: topic appears with a grey snippet line under it; clearing the box restores the full tree.

- [ ] **Step 5: Commit**

```bash
git add app/story_graph_app.py
git commit -m "feat(help): search matches topic bodies, shows snippets in the tree"
```

---

### Task 5: Wider default + maximize toggle

**Files:**
- Modify: `app/story_graph_app.py` — CSS `#helpdrawer` (~line 723), drawer header HTML (~line 757), `helpInit` (~line 1507)

**Interfaces:**
- Produces: maximized flag in `localStorage` key `sgos.helpmax` (`'1'`/`'0'`).

- [ ] **Step 1: CSS.** In the `#helpdrawer` rule change `var(--help-w,460px)` → `var(--help-w,560px)`, and add after the `#helpdrawer.open` rule:

```css
#helpdrawer.max{width:100vw!important;max-width:100vw}
#helpdrawer.max #helpgrip{display:none}
```

- [ ] **Step 2: HTML.** In the drawer header (line 757), add the maximize button before the close button:

```html
 <header><h2>Help</h2><button class="ghost" id="helpmax" title="Maximize / restore">⛶</button><button class="ghost" id="helpclose" title="Close (Esc)">✕</button></header>
```

- [ ] **Step 3: JS.** In `helpInit`, after the stored-width block (~line 1510), add:

```js
 const HELP_MAX_KEY='sgos.helpmax';
 if(localStorage.getItem(HELP_MAX_KEY)==='1')d.classList.add('max');
 document.getElementById('helpmax').onclick=()=>{
  d.classList.toggle('max');
  localStorage.setItem(HELP_MAX_KEY,d.classList.contains('max')?'1':'0')};
```

- [ ] **Step 4: Verify**

```bash
python3 -m pytest story-graph/tests/test_app.py -k inline_frontend -v
```

Expected: PASS. Hand-check: ⛶ toggles full-window; reload keeps the state; drag-resize still works when not maximized.

- [ ] **Step 5: Commit**

```bash
git add app/story_graph_app.py
git commit -m "feat(help): 560px default width and a maximize toggle"
```

---

### Task 6: Content — Skill Workflows section (5 topics)

**Files:**
- Create: `app/help/workflows/overview.md`, `workflows/seed-from-worksheet.md`, `workflows/reverse-engineer.md`, `workflows/catch-up-from-chapters.md`, `workflows/proposal-queue.md`
- Modify: `app/help/manifest.json` (append section)

**Interfaces:**
- Consumes: source material — `story-graph/SKILL.md`, `story-graph/reference/seed-from-worksheet.md`, `reference/reverse-engineer.md`, `reference/catch-up-from-chapters.md`, `reference/decisions.md`, and the propose/verify-proposal/apply-proposal/reject-proposal implementations in `story-graph/assets/story_graph.py`.

- [ ] **Step 1: Read the sources.** Read all five source files above before writing anything. Every topic must be *derived*: describe what the skill actually does in each mode — inputs, steps, outputs, safety rules — in help-voice (second person, present tense, like the existing `app/help/` topics). No invented behavior; when a mode guide and the code disagree, the code wins and the discrepancy is noted in the topic.

- [ ] **Step 2: Write the five topics.** Required shape per topic (each ≥ 80 chars of real content — the manifest test enforces this):
  - `overview.md` — "How the skill operates": the graph as canon ABox, ontology-v2 TBox, modules (`spe` vs `none`), the file-safety rule (never overwrite a graph), where the skill lives and how any project can use it.
  - `seed-from-worksheet.md` — when it applies (NPE YFD-RAW worksheet present), what gets extracted into which graph sections, what remains provisional.
  - `reverse-engineer.md` — building a graph from existing chapter prose (full or partial manuscript), evidence-span grounding, how ambiguity is recorded instead of guessed.
  - `catch-up-from-chapters.md` — folding finalized chapters into an existing graph: what is compared, what gets appended, how canon commits record the change.
  - `proposal-queue.md` — the propose → verify-proposal → apply-proposal / reject-proposal lifecycle: what a proposal is, what verification checks, what ratification changes in the graph.

- [ ] **Step 3: Manifest.** Append to the `sections` array in `app/help/manifest.json` (already snapshotted in Task 1; edit in place):

```json
{"id": "workflows", "title": "Skill Workflows", "topics": [
  {"id": "wf-overview", "title": "How the skill operates", "file": "workflows/overview.md"},
  {"id": "wf-seed", "title": "Seed from a worksheet", "file": "workflows/seed-from-worksheet.md"},
  {"id": "wf-reverse", "title": "Reverse-engineer from prose", "file": "workflows/reverse-engineer.md"},
  {"id": "wf-catch-up", "title": "Catch up from chapters", "file": "workflows/catch-up-from-chapters.md"},
  {"id": "wf-queue", "title": "The proposal queue", "file": "workflows/proposal-queue.md"}]}
```

- [ ] **Step 4: Run the manifest tests**

```bash
python3 -m pytest story-graph/tests/test_app.py -k "manifest or reachable" -v
```

Expected: PASS (files exist, non-empty, no orphans).

- [ ] **Step 5: Commit**

```bash
git add app/help/workflows/ app/help/manifest.json
git commit -m "docs(help): Skill Workflows section — five topics derived from the skill"
```

---

### Task 7: Content — Command Reference section (6 grouped topics, all 21 subcommands)

**Files:**
- Create: `app/help/commands/checking.md`, `commands/compile-query.md`, `commands/reports-analysis.md`, `commands/proposal-queue.md`, `commands/import-migration.md`, `commands/freeze-visualize.md`
- Modify: `app/help/manifest.json` (append section)
- Test: `story-graph/tests/test_app.py` (append)

**Interfaces:**
- Consumes: argparse definitions + implementations in `story-graph/assets/story_graph.py` (`python3 story-graph/assets/story_graph.py <cmd> --help` per command); existing quick table `app/help/reference/commands.md` stays as-is and is NOT duplicated — grouped topics go deeper (flags, one worked example each).

- [ ] **Step 1: Write the failing coverage test** (append to `story-graph/tests/test_app.py`):

```python
def test_command_reference_covers_all_21_subcommands():
    """Spec: every story_graph.py subcommand documented in the commands/ help topics."""
    cmds = ["validate", "compile", "query", "report", "import-legacy", "coverage",
            "queue", "freeze", "audit", "impact", "deviations", "visualize",
            "propose", "verify-proposal", "reject-proposal", "apply-proposal",
            "unresolved", "shapes", "irony", "conflicts", "decisions"]
    files = sorted((HELP / "commands").glob("*.md"))
    assert files, "commands/ help topics missing"
    text = "".join(p.read_text(encoding="utf-8") for p in files)
    missing = [c for c in cmds if f"`{c}" not in text]
    assert missing == [], f"subcommands undocumented in commands/: {missing}"
```

- [ ] **Step 2: Run to verify it fails**

```bash
python3 -m pytest story-graph/tests/test_app.py -k covers_all_21 -v
```

Expected: FAIL — `commands/ help topics missing`.

- [ ] **Step 3: Derive and write the six topics.** For each command run its `--help` and skim its implementation; document: what it does, key flags, when to reach for it, one real invocation with the Book 3 fixture path where sensible (e.g. `python3 story-graph/assets/story_graph.py validate series/books/book-3/Story-Graph.md`). Grouping (from the spec — may shift ±1 topic if a group reads badly, but every command must appear in exactly one topic):

| Topic file | Commands |
|---|---|
| `checking.md` | `validate`, `audit`, `deviations` |
| `compile-query.md` | `compile`, `query` |
| `reports-analysis.md` | `report`, `coverage`, `impact`, `shapes`, `irony`, `conflicts`, `unresolved`, `decisions` |
| `proposal-queue.md` | `propose`, `verify-proposal`, `reject-proposal`, `apply-proposal`, `queue` |
| `import-migration.md` | `import-legacy` |
| `freeze-visualize.md` | `freeze`, `visualize` |

Command names appear backtick-wrapped (the coverage test looks for `` `<cmd> `` prefixes).

- [ ] **Step 4: Manifest.** Append section:

```json
{"id": "commands", "title": "Command Reference", "topics": [
  {"id": "cmd-checking", "title": "Checking the graph", "file": "commands/checking.md"},
  {"id": "cmd-compile-query", "title": "Compiling & querying", "file": "commands/compile-query.md"},
  {"id": "cmd-reports", "title": "Reports & analysis", "file": "commands/reports-analysis.md"},
  {"id": "cmd-proposal-queue", "title": "The proposal queue (CLI)", "file": "commands/proposal-queue.md"},
  {"id": "cmd-import", "title": "Import & migration", "file": "commands/import-migration.md"},
  {"id": "cmd-freeze-viz", "title": "Freezing & visualizing", "file": "commands/freeze-visualize.md"}]}
```

- [ ] **Step 5: Run tests**

```bash
python3 -m pytest story-graph/tests/test_app.py -q
```

Expected: all PASS, including the new coverage test.

- [ ] **Step 6: Commit**

```bash
git add app/help/commands/ app/help/manifest.json story-graph/tests/test_app.py
git commit -m "docs(help): Command Reference — all 21 subcommands in six grouped topics, with coverage test"
```

---

### Task 8: Content — Credits & Acknowledgements

**Files:**
- Create: `app/help/credits/credits.md`
- Modify: `app/help/manifest.json` (append section)

**Interfaces:**
- Consumes: citation sweep of `docs/source-conversation/` (`FULL-TRANSCRIPT.md`, `SOURCE-FILES.md`, `transcript-parts/`).

- [ ] **Step 1: Sweep the source conversation for cited IP.**

```bash
grep -rioE "sstorytime|burgess|cited from [^.]+|based on [^.]+" docs/source-conversation/ | sort -u | head -40
```

Also skim `docs/source-conversation/SOURCE-FILES.md` for named external resources. Collect every external project/person the conversation credits as shaping the design (SSTorytime / Mark Burgess is confirmed present; include others only if actually cited).

- [ ] **Step 2: Write `credits/credits.md`** with exactly three parts (real facts only, per approved spec):
  - **Intellectual sources** — each cited resource: name, author where known, one line on what it contributed to the design.
  - **Provenance** — the five-act program and this tool's design originated in an archived ChatGPT conversation (`docs/source-conversation/` in the repository); no named human course creator exists in the record, stated as such.
  - **Infrastructure** — Python (stdlib server, no web framework), Kùzu (embedded graph database powering Cypher/audit), OpenDyslexic (optional readable font), and the optional Ask-tab providers Ollama, LM Studio, OpenRouter. Explicitly no AWS/MySQL — the tool uses neither.

- [ ] **Step 3: Manifest.** Append section:

```json
{"id": "credits", "title": "Credits & Acknowledgements", "topics": [
  {"id": "credits", "title": "Credits & acknowledgements", "file": "credits/credits.md"}]}
```

- [ ] **Step 4: Run manifest tests**

```bash
python3 -m pytest story-graph/tests/test_app.py -k "manifest or reachable" -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add app/help/credits/ app/help/manifest.json
git commit -m "docs(help): credits — intellectual sources, provenance, real infrastructure"
```

---

### Task 9: Drift pass over the existing 21 topics

**Files:**
- Possibly modify: any of the 21 existing `.md` files under `app/help/` (each edited file first copied to `<name>_v2.md`)

**Interfaces:**
- Consumes: current implementations — each `windows/*.md` topic checked against its tab's code in `app/story_graph_app.py`; `reference/commands.md` against `story_graph.py --help`; `getting-started/*` against the actual startup flow.

- [ ] **Step 1: Verify each topic against the code it describes.** For each of the 21 existing topics, read the topic and the code it documents; note only *drift* (behavior that changed — e.g. the help drawer's own topic `windows/settings.md` or any topic describing the drawer must now mention search-in-bodies, folding, and maximize). Do not rewrite prose that is still accurate.

- [ ] **Step 2: For each drifted file:** copy the prior text to `<name>_v2.md` (side-by-side history per approved spec §4 — e.g. `cp app/help/windows/graph.md app/help/windows/graph_v2.md`), then fix the unsuffixed file in place. Untouched topics get no version copy.

- [ ] **Step 3: Run the full app test file**

```bash
python3 -m pytest story-graph/tests/test_app.py -q
```

Expected: PASS (Task 1's amendment keeps `_v2.md` files out of the orphan check).

- [ ] **Step 4: Commit**

```bash
git add app/help/
git commit -m "docs(help): drift pass — existing topics re-verified against current code"
```

---

### Task 10: End-to-end verification + README

**Files:**
- Create: `app/README_v2.md` (updated app README — side-by-side, `_v#` = newest per repo convention)
- No code changes expected; fixes loop back to the owning task.

- [ ] **Step 1: Full test suite**

```bash
python3 -m pytest story-graph/tests/ -q
```

Expected: all PASS (295+ pre-existing + the new help tests).

- [ ] **Step 2: Launch against the fixture**

```bash
python3 app/story_graph_app.py series/books/book-3/Story-Graph.md --port 8765
```

- [ ] **Step 3: Drive with Playwright MCP** (browser_navigate to `http://127.0.0.1:8765`, then):
  1. Open help (❓). Confirm the tree shows 9 sections including *Skill Workflows*, *Command Reference*, *Credits & Acknowledgements*.
  2. Type a body-only term (one that appears in no topic title — pick from a topic body, e.g. `rebinding`). Confirm the owning topic surfaces with a grey snippet.
  3. Collapse a section; reload the page; reopen help — still collapsed. Open a topic inside it via search; clear the search — its section is expanded.
  4. Open one Command Reference topic and the Credits topic; confirm both render (tables, code spans).
  5. Toggle ⛶; screenshot normal and maximized; **look at both screenshots** — a blank panel is a failure.
- [ ] **Step 4: Write `app/README_v2.md`** — the current `app/README.md` content updated for the reworked help: new sections list, body search, folding, maximize, credits topic. (Original `app/README.md` stays untouched at its name per the side-by-side convention.)

- [ ] **Step 5: Commit**

```bash
git add app/README_v2.md
git commit -m "docs(app): README_v2 — help system rework (coverage, search, explorer, credits)"
```
