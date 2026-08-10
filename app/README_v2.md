# Story Graph OS — local browser app

A single-user, **localhost-only** web face over the `story-graph` engine — the
Act-III "operating system" the five-act program describes, rebuilt on the
ontology-v2 model and Kùzu. It's a *separate optional layer*: the portable
`story-graph/` skill stays the stdlib engine; this app is a UI you launch when
you want to browse, query, and visualize.

## Run

```
python3 app/story_graph_app.py <Story-Graph.md> [--chapters-dir <dir>] [--port 8765]
# then open http://127.0.0.1:8765
```

- **Python 3.10+**, no web framework (stdlib `http.server`).
- **`pip install kuzu`** is optional but recommended — it powers the ad-hoc
  Cypher console and the `report`/`audit` panels. Without it the app still runs
  (Dashboard, Graph, `deviations`, `queue`) and says the Cypher tab is disabled.
- The **Ask** tab (plain-English → Cypher) is **provider-neutral and needs no
  SDK** — it speaks the OpenAI-compatible chat API over stdlib HTTP. Point it at a
  **local** server (Ollama on `:11434`, LM Studio on `:1234` — no key) or at
  **OpenRouter** (paste a key). Configure provider + model in ⚙️ Settings → AI
  Model. `OPENROUTER_API_KEY` in the environment is picked up automatically.
- Pass `--chapters-dir` to enable the `deviations` report (graph-vs-source drift).

First load compiles the graph into a throwaway Kùzu database, so startup takes a
few seconds on a large graph (e.g. a full-book import); small graphs are instant.

## Tabs

- **Dashboard** — counts (entities / propositions / epistemic states / evidence /
  open loops / sources) and the ratification-queue size.
- **Graph** — an interactive node-link view (self-authored force layout, drag to
  rearrange, **zoom slider** to enlarge and read edge labels; the whole plot fits
  on load). Focus box narrows to one proposition's neighbourhood. No external JS
  library — inline and self-contained.
  - **Size by** — node *area* can encode a magnitude, so the shape of the graph
    answers a question instead of just being a picture. Switching metric resizes
    in place (the layout never re-runs, so you keep your bearings), and the legend
    names the top scorer and how many nodes sit at the floor:

    | Mode | Bigger means | Reads as |
    |---|---|---|
    | `connections` | more edges *in the visible graph* — so the edge-type filter rebalances it | structural hubs |
    | `believers` | more minds hold a stance on this claim (for a character, more claims they hold) | where the story's knowledge actually lives |
    | `receipts` | more verbatim evidence spans back this claim | what's proven vs. asserted |
    | `unproven weight` | more rests on a claim with **no** evidence span (propositions only) | what to go verify first |
    | `contested` | more holders on the smaller side of a real disagreement | the dramatic-irony surface |

    A metric with no data is reported honestly rather than hidden — `contested`
    reading "nothing here scores above zero" means no `believes-false` states
    exist yet, which is a finding about the graph, not a bug in the view.
  - Nodes with no edges are parked in a grid to the side rather than left in the
    simulation, where their mutual repulsion would blow the connected graph into
    an unreadable dot.
- **Timeline** — belief-over-time: each character a lane, chapters left→right,
  every epistemic state a coloured dot.
- **Query** — an ad-hoc **Cypher** console over the compiled graph. Node tables:
  `Entity, Proposition, Source, Evidence, OpenLoop, Holder`. Rel tables:
  `RELATES, EPISTEMIC, GOVERNED_BY, EVIDENCED_BY, SUPPORTS`.
- **Ask** — for people without Cypher: type a question in plain English, the model
  you picked (local or OpenRouter) turns it into a read-only Cypher query (the
  schema above is given to the model and shown in a collapsible panel), runs it,
  and shows both the generated query and the results. Configure the provider/model
  in Settings.
- **Reports** — run `report`, `audit`, `deviations`, `queue` and read the output.

## Help (❓ top-right, or press `?`)

A drawer slides in from the right with the full documentation — 33 topics across
9 sections: Getting Started, The Windows (one per tab), How Story Graph Works,
The Decisions, the Safety Model, Reference, Skill Workflows, Command Reference,
and Credits & Acknowledgements.

- **Search** — the filter box does more than match titles: it also searches
  topic bodies server-side (`GET /help/search`) and surfaces a grey snippet of
  the matching passage under any topic whose title doesn't contain the term, so
  a topic is findable by what it says, not just what it's called.
- **Collapsible sections** — click a section header to fold it; the state is
  remembered per browser (`localStorage`, key `sgos.helpfold`) and survives a
  reload. Opening a topic inside a folded section — including via search —
  expands that section automatically, and a section holding the currently open
  topic can't be folded out from under it.
- **Resize and maximize** — drag the drawer's left edge to resize (560px wide by
  default, remembered across sessions); the **⛶** button next to the drawer
  title toggles a full-viewport maximized view for long reading sessions
  (remembered separately via `sgos.helpmax`). `Esc` closes the drawer.

Content lives in [`help/`](help/) as `manifest.json` plus a markdown tree, served by
the app itself — editing a topic is editing a file, with no rebuild. Help is also
served *while the graph is still compiling*, since that is exactly when there is
time to read it. The Credits & Acknowledgements section documents the tool's
intellectual sources, provenance, and infrastructure (Python, Kùzu, OpenDyslexic,
the Ask tab's LLM providers) in the same drawer.

## Settings (⚙️ top-right)

A settings dialog adapted from the Novel Machine authoring UI. Esc or click
outside to close.

- **Display** — accessibility & reading preferences, applied instantly and saved
  in the browser (`localStorage`): contrast, text size (whole-UI scale), letter
  spacing, line height, a readable-font toggle (OpenDyslexic if installed),
  reduce-motion, and a 12px minimum-text-size floor.
- **AI Model** — provider-neutral config for the Ask tab: pick a **provider**
  (OpenRouter · Ollama · LM Studio — the dot shows local reachability), then a
  **model** (Browse the provider's live catalogue, or type an id for a local
  model), and `Test` the connection. Your provider/model choice and any cloud key
  are saved to a local **`.env`** (gitignored) so they **persist across restarts**;
  local providers need no key. A pre-set `OPENROUTER_API_KEY` in the environment is
  also picked up.
- **About** — the loaded graph, canon chapter, modules, and Kùzu status.

(The source dialog also has novel-pipeline Flows and an OpenRouter Corpus tab;
those route a 30-agent authoring pipeline and have no analog in a story-graph
tool, so they're intentionally not carried over.)

## Boundaries

Binds to `127.0.0.1` only; no auth, no multi-user, no write-back to the graph
(the app reads `Story-Graph.md` and a rebuildable Kùzu projection of it). Edit
canon in the `Story-Graph.md` file with the skill; restart the app to see it.
The generated Cypher is validated read-only before running. One network
exception: the **Ask** tab sends your question and the graph *schema* (table
names, not your data) to your chosen provider. Point it at a local Ollama / LM
Studio server and even that stays on your machine; OpenRouter is the only cloud
hop, and only if you choose it.
