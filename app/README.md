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
- Pass `--chapters-dir` to enable the `deviations` report (graph-vs-source drift).

First load compiles the graph into a throwaway Kùzu database, so startup takes a
few seconds on a large graph (e.g. a full-book import); small graphs are instant.

## Tabs

- **Dashboard** — counts (entities / propositions / epistemic states / evidence /
  open loops / sources) and the ratification-queue size.
- **Graph** — an interactive node-link view (self-authored force layout, drag to
  rearrange). No external JS library — inline and self-contained.
- **Query** — an ad-hoc **Cypher** console over the compiled graph. Node tables:
  `Entity, Proposition, Source, Evidence, OpenLoop, Holder`. Rel tables:
  `RELATES, EPISTEMIC, GOVERNED_BY, EVIDENCED_BY, SUPPORTS`.
- **Reports** — run `report`, `audit`, `deviations`, `queue` and read the output.

## Boundaries

Binds to `127.0.0.1` only; no auth, no multi-user, no write-back to the graph
(the app reads `Story-Graph.md` and a rebuildable Kùzu projection of it). Edit
canon in the `Story-Graph.md` file with the skill; restart the app to see it.
