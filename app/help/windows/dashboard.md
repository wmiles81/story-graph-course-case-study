# Dashboard

A count card per section of the graph, plus **unratified (queue)** — how many rows are
still marked `provisional`.

Read the cards as a shape, not a score. A graph with 120 propositions and 6 epistemic
states is not "80% done"; it is a graph that has recorded *what is true* and not yet
recorded *who knows it*. Those are different layers and they fail differently.

The footer line tells you where the graph was loaded from and whether Kùzu is on. If Kùzu
is off it also tells you why — usually that it is not installed.

## What a healthy set of counts looks like

There is no target ratio, but two patterns are worth noticing:

- **Evidence far below Propositions** — most claims have no receipt. Run
  **Reports → coverage** to see which layers are thin, and `queue` to rank what to fix.
- **Epistemic States far below Propositions** — the graph knows the facts but not who
  holds them, which is the layer that makes dramatic irony visible. It is also the layer
  that is easiest to leave empty, because `knows` rows feel redundant with the prose.
