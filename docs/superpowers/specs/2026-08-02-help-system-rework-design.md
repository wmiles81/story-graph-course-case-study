# Help System Rework — Design

**Date:** 2026-08-02
**Status:** Approved approach; spec for implementation planning
**Component:** `app/story_graph_app.py` help drawer + `app/help/` content tree

## Goal

Rework the existing in-app help drawer (❓, added in commit 1408692) into a
usable, complete help system: full content coverage of the tool's real
functionality (app tabs, skill workflows, CLI subcommands), a credits and
acknowledgements section, and a true explorer-style left panel. No new app,
no new architecture — the drawer, the stdlib server, and the
`manifest.json` + markdown tree stay.

The requested layout — search box first, explorer panel left, detail panel
right — already exists structurally (`#helpfilter`, `#helpnav`, `#helpdoc`).
The work is content coverage, credits, and explorer usability.

## 1. Content plan

Three new sections appended to `app/help/manifest.json`. Every topic is a
markdown file whose content is derived from the real implementation — read
the code, document what it does — not from aspirational descriptions.
"Derived initially": a one-time derivation, hand-maintained afterward like
the existing topics.

### Skill Workflows (`workflows/`) — 5 topics

Derived from `story-graph/SKILL.md` and `story-graph/reference/`:

1. **How the skill operates** — the graph as canon ABox, the ontology-v2
   TBox, modules, file-safety rules.
2. **Seed from a worksheet** — the NPE YFD-RAW seeding mode
   (`reference/seed-from-worksheet.md`).
3. **Reverse-engineer from prose** — building a graph from an existing
   manuscript (`reference/reverse-engineer.md`).
4. **Catch up from chapters** — folding finalized chapters into an existing
   graph (`reference/catch-up-from-chapters.md`).
5. **The proposal queue** — propose → verify-proposal → apply/reject
   lifecycle and what ratification means.

### Command Reference (`commands/`) — ~6 grouped topics

The 21 `story_graph.py` subcommands (`validate, compile, query, report,
import-legacy, coverage, queue, freeze, audit, impact, deviations,
visualize, propose, verify-proposal, reject-proposal, apply-proposal,
unresolved, shapes, irony, conflicts, decisions`) grouped by function
rather than 21 stub pages:

| Topic | Commands |
|---|---|
| Checking the graph | `validate`, `audit`, `deviations` |
| Compiling & querying | `compile`, `query` |
| Reports & analysis | `report`, `coverage`, `impact`, `shapes`, `irony`, `conflicts`, `unresolved`, `decisions` |
| The proposal queue | `propose`, `verify-proposal`, `reject-proposal`, `apply-proposal`, `queue` |
| Import & migration | `import-legacy` |
| Freezing & visualizing | `freeze`, `visualize` |

Each command's entry is derived from its argparse definition and
implementation in `story-graph/assets/story_graph.py`, and includes one
real invocation example. (Exact grouping may shift ±1 topic during
implementation if a group reads badly; the constraint is: every subcommand
documented, no stub pages.)

### Credits & Acknowledgements (`credits/`) — 1 topic

Three parts, real facts only:

- **Intellectual sources** — SSTorytime (Mark Burgess's semantic-spacetime
  project), cited in the source conversation as formative to the graph
  model, plus any other resources the archived conversation
  (`docs/source-conversation/`) credits as shaping the design. The
  implementer sweeps the transcript for citations before writing this
  topic.
- **Provenance** — the five-act program and this tool's design originated
  in the archived ChatGPT conversation; no named human course creator
  exists in the record, so provenance is stated as such.
- **Infrastructure** — the real stack: Python (stdlib server, no web
  framework), Kùzu (embedded graph database), OpenDyslexic (optional
  readable font), and the optional Ask-tab providers Ollama, LM Studio,
  and OpenRouter. Explicitly not AWS or MySQL — the tool uses neither.

### Existing 21 topics

A verification pass against current code: fix drift (behavior that changed
since the topic was written), do not rewrite. Any topic file that changes
gets a side-by-side version copy first (see §4).

## 2. Explorer upgrade (left panel)

- **Collapsible sections.** Section headers in `#helpnav` toggle
  fold/unfold. Expanded/collapsed state persists in `localStorage`. The
  section containing the active topic auto-expands. With ~9 sections and
  ~33 topics this is what keeps the tree scannable.
- **Content search.** The search box remains the first element in the
  drawer. Today it filters titles only; it gains body search: the server
  builds an in-memory index (topic id → lowercased body text) at startup
  and serves `GET /help/search?q=` returning matched topic ids plus a
  one-line snippet around the first match. The client merges title matches
  (instant, local) with body matches (debounced fetch) and shows body-match
  snippets under the topic title in the tree. Plain substring match,
  case-insensitive; no ranking, no stemming — YAGNI.
- **Width & maximize.** Default drawer width goes from 460px to ~560px
  (still user-resizable by dragging the left edge; that stays). A new
  maximize toggle (⛶) in the drawer header expands to full-window and
  back. Both the width and the maximized flag persist in `localStorage`.

## 3. Architecture (unchanged)

Same single-file stdlib server. Content stays `manifest.json` + markdown
tree under `app/help/`, served by the existing `_help` route; editing a
topic remains editing a file, no build step. Help continues to be served
while the graph is still compiling. The only server change is the search
index + `GET /help/search` endpoint. No new dependencies, no external JS.

## 4. File-versioning compliance (global rule)

- `app/story_graph_app.py` and `app/help/manifest.json` are call-chain-owned
  names → **shift-rename**: move the current file to its next free `_v#`
  slot, then write the new content at the unsuffixed name.
- Existing help topic `.md` files that change in the verification pass →
  **side-by-side**: copy the prior text to `<name>_v2.md`, manifest keeps
  pointing at the live unsuffixed filename.
- Brand-new files (new topics, new sections' directories) are simply new.
- The help server must not pick up `_v#` files as topics (it serves only
  files named in the manifest, so this holds automatically; the search
  index likewise indexes only manifest-listed files).

## 5. Verification

Launch `python3 app/story_graph_app.py series/books/book-3/Story-Graph.md`
against the Book 3 fixture and drive the drawer with Playwright:

1. Open help; confirm the three new sections appear in the tree.
2. Search a term that appears only in a topic body (not any title);
   confirm the topic surfaces with a snippet.
3. Collapse a section, reload the page, confirm it stays collapsed;
   confirm the active topic's section auto-expands.
4. Open one Command Reference topic and the Credits topic; confirm
   rendering.
5. Toggle maximize; screenshot normal and maximized states and look at
   both screenshots.

Plus a non-browser check: a small test (or one-shot script) asserting
every manifest entry resolves to an existing file and every one of the 21
subcommands appears somewhere in the Command Reference topics.

## Out of scope

Automated doc generation from argparse; full-text ranking/stemming; a
standalone help app; rewriting existing topics that aren't drifted;
cross-topic hyperlink graph; help authoring UI.
