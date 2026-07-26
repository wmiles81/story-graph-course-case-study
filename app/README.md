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
- **`pip install anthropic`** (+ `ANTHROPIC_API_KEY`, or `ant auth login`) is
  optional — it powers the **Ask** tab (plain-English → Cypher). Without it the
  Ask tab shows a message; nothing else is affected. Uses `claude-opus-5` by
  default (override with the `ANTHROPIC_MODEL` env var).
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
- **Timeline** — belief-over-time: each character a lane, chapters left→right,
  every epistemic state a coloured dot.
- **Query** — an ad-hoc **Cypher** console over the compiled graph. Node tables:
  `Entity, Proposition, Source, Evidence, OpenLoop, Holder`. Rel tables:
  `RELATES, EPISTEMIC, GOVERNED_BY, EVIDENCED_BY, SUPPORTS`.
- **Ask** — for people without Cypher: type a question in plain English, Claude
  turns it into a read-only Cypher query (the schema above is given to the model
  and shown in a collapsible panel), runs it, and shows both the generated query
  and the results. Needs `anthropic` + a key (see Run).
- **Reports** — run `report`, `audit`, `deviations`, `queue` and read the output.

## Settings (⚙️ top-right)

A settings dialog adapted from the Novel Machine authoring UI. Esc or click
outside to close.

- **Display** — accessibility & reading preferences, applied instantly and saved
  in the browser (`localStorage`): contrast, text size (whole-UI scale), letter
  spacing, line height, a readable-font toggle (OpenDyslexic if installed),
  reduce-motion, and a 12px minimum-text-size floor.
- **AI Model** — configure the Ask tab's Anthropic model (dropdown) and API key.
  The key is held **in memory for the session only — never written to disk**;
  `Test` sends a one-token ping to confirm it reaches the model. Falls back to
  `ANTHROPIC_API_KEY` / `ant auth login` when no key is entered.
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
names, not your data) to the Anthropic API; every other tab is fully local.
