# Graph — the visualizer

The richest view in the app. A force-directed node-link diagram of the whole graph, or of
one proposition's neighbourhood.

## Interactions

| Action | Result |
|---|---|
| **Drag a node** | Move it. It stays pinned where you put it, across redraws. |
| **Drag empty space** | Pan the whole canvas. |
| **Wheel** | Zoom. |
| **Click a node** | Show its details. |
| **Shift-click** or **double-click** | Explore that node's set — refocus the graph on its neighbourhood. |
| **Search box** | Highlight nodes whose label matches as you type. |

The force layout runs **once per dataset**. Everything after that — zoom, pan, hover,
search, selection — only changes a transform or an attribute, and never re-simulates. That
is why the view stays smooth at a couple of hundred nodes, and why a node you dragged does
not spring back.

## Focus

The box at the top takes a **proposition id**. Leave it blank for the whole graph; enter an
id to draw only that claim and what it touches. However deep you focus, **Show all** returns
you to the original graph rather than one level up.

## Size by — what node area encodes

This is the control worth learning. Each option asks a different question of the same graph.

| Option | Bigger means |
|---|---|
| **uniform** | every node the same size |
| **connections** | more edges in the *visible* graph — structural hubs |
| **believers** | more minds hold a stance on this claim (for a character: more claims they hold) |
| **receipts** | more verbatim evidence spans back this claim |
| **unproven weight** | more rests on a claim that has **no** evidence span *(propositions only)* |
| **contested** | more holders on the smaller side of a real disagreement — the dramatic-irony surface |

Two of these are doing something subtler than the rest:

**Connections** is measured on the edges *actually drawn*, so hiding an edge type
rebalances it. The others are story facts sent by the server and do not move.

**Unproven weight** deliberately scores propositions only. An entity or a source has no
receipts by construction, so scoring them would just redraw the same hubs and bury the
claims you actually need to check.

## Hiding edge types

Toggle any edge type off and the graph redraws without it. The setting persists across
redraws, so you can focus, explore, and come back without rebuilding your view. Hiding
edges also changes what **connections** sizing reports, which is often the point — hide
`EPISTEMIC` and the remaining hubs are the structural ones.

## Legend

The legend lists every node kind currently drawn, with its colour. It is generated from the
data, so a kind that is absent from this graph is absent from the legend.
