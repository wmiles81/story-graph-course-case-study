# How verification works

The chain, end to end:

```
1. code enumerates candidates      deterministic — no model
2. code numbers real sentences     the shortlist
3. the judge picks an index        a model, or you
4. code fills in the quote         from the numbered sentence
5. the gate verifies               quote must exist in the chapter
6. a human accepts                 NEEDS-HUMAN rows never auto-apply
7. the decision is logged          append-only review ledger
```

## Index-not-quote

Step 3 is the load-bearing one. The judge never *writes* a quote — it picks a **number** from
a list of real sentences that code extracted, and code fills in the text.

Fabrication is therefore not merely detected, it is **structurally impossible**. There is no
channel through which invented prose can enter the graph.

## Why a gate as well

Because the index is not the only way to be wrong. The gate independently checks that:

- the quote exists in the named chapter, exactly or paragraph-normalised
- the quote is substantial — not a three-word fragment
- the cited span is declared, or declared earlier in the same proposal
- no cell contains a `|` or a newline that would silently re-column the table
- a dependency edge does not close a cycle
- the chapter is not beyond `current-canon-chapter`

That last class matters more than it sounds. A `|` inside a cell used to re-column a row and
then validate clean — corruption that passes its own checker.

## What the engine does not do

No network calls. No model. No hidden state. `validate`, `compile`, `query`, `report`,
`audit`, `impact`, `visualize`, `unresolved`, `conflicts`, `shapes`, `irony` are all
rule-checking and traversal: same input, same output, offline.

The optional `propose` commands are the only ones that can involve a model — and
`propose … --ask` writes the question to disk and calls nothing at all, so the agent already
reading your manuscript can answer it.
