# The proposal queue

Generated rows never touch the graph directly. Whatever produces them — a model
call, or an agent reading the manuscript in-session — writes a proposal file, and
the proposal reaches canon only by passing through this queue.

## What a proposal is

A proposal is a JSON file of candidate rows for one graph section at a time —
entities, evidence, or epistemic states, generated in that order, since a belief
can't name a holder the graph hasn't heard of yet. Nothing about generating a
proposal writes to the graph; the file on disk is the entire effect.

## Verify: what gets checked

`verify-proposal` runs a deterministic pass over every row — no model, no network —
and reports each as **PASS**, **FAIL** with a reason, or **NEEDS-HUMAN**. The checks:
the section and its columns exist, key columns are non-empty, every id resolves, the
chapter falls within canon, cited evidence spans are declared, the row isn't already
present, and the quote gate — any `basis.quote` on the row must appear verbatim in
its chapter. A model can invent a belief; it cannot invent a sentence that's actually
on the page. A separate consequence pass then validates the whole would-be graph and
rejects any row that would introduce an error the graph didn't already have.

**NEEDS-HUMAN is not a soft pass.** Rows in Epistemic States, Relationships, and Open
Loops & Setups are inferences — the quote is real, but what it means is a reading,
and no checker confirms a reading. They can never auto-ratify.

## Apply: what ratification changes

`apply-proposal` takes `--accept` naming row numbers, or `pass` (every row that
verified clean, deliberately excluding NEEDS-HUMAN rows), or `all` (every row that
didn't fail, including NEEDS-HUMAN ones — this prints a note naming how many
unreviewed rows it's taking, since that's a deliberate act, not a default). A row
that already failed verification cannot be applied; there's no `--force`. Applying
keeps the previous graph at the next free `_v<N>` slot, marks every new row
provisional, and appends one Canon Commit Log line naming the model and the proposal
file — so the graph always shows what was proposed, what the checker allowed, and
what was actually taken.

## Reject: recording what didn't survive

`reject-proposal` records rows you're turning down, with a reason, in a per-graph
review ledger — the graph itself is untouched. The next time a generator produces
the same claim, `verify-proposal` marks it `SEEN` and shows your prior reason, so a
re-run costs you only the genuinely new rows. The ledger is append-only and shared
across the graph's versions, so applying a later proposal — which rolls the graph to
a new `_v<N>` — never forgets a decision made before it.
