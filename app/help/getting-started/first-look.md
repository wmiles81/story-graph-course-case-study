# The six tabs in one minute

| Tab | What it answers |
|---|---|
| **Dashboard** | How big is this graph, and how much of it is ratified? |
| **Graph** | What is connected to what? *(the visualizer — the richest view)* |
| **Timeline** | What happens when, chapter by chapter? |
| **Query** | Ad-hoc Cypher over the compiled graph. |
| **Ask** | The same, in plain English — a model writes the Cypher. |
| **Reports** | The five standing reports: coverage, report, audit, deviations, queue. |

The header line always shows the book title, the current canon chapter, which modules are
declared, and whether Kùzu is on.

## Where to start

If the graph is new to you: **Dashboard** for the shape of it, then **Reports → coverage**
to see which layers are populated and which are empty. Coverage is the fastest way to learn
what a graph does and does not yet know.

If you are hunting a specific problem: **Reports → audit** (continuity detectors) or
**queue** (what is still unratified).

If you are exploring: **Graph**, with *size by* set to **unproven weight** — that draws the
claims that carry the most weight with no evidence behind them.
