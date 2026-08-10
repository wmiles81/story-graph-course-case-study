# Catch up from chapters

Catch-up mode runs when a `Story-Graph.md` already exists and chapters sit above its
`current-canon-chapter` high-water mark. It's the canon-commit loop: it walks each
uncommitted chapter in order and folds its deltas into the graph.

## What is compared

The skill reads the graph's header to find the current chapter mark, then discovers
chapters in the target folder — finalized chapters first, then drafts, then a generic
glob — and selects every chapter numbered higher than the mark, in ascending order.
Where a chapter has multiple versions, the highest wins. Two checks run before
committing a batch: which names in the new chapters have no entity yet, and which
existing propositions are state-shaped and liable to contradict themselves as the
new chapters land.

## What gets appended

For each chapter, in order, the skill reads it and extracts deltas, then updates the
current-state tables:

- **Relationships** that formed, changed, or broke.
- **Propositions** — new premise-level facts, or a status change on an existing one.
- **Epistemic States** — who learns, believes, or suspects what this chapter,
  including the reader — appended as new rows at the new chapter, never edited into
  history. An epistemic row can never be recorded before its proposition's embargo
  lifts; the validator treats that as an error.
- **Open Loops & Setups** — setups that fired or were defused, and new ones planted.
- **Entities** — new ones introduced, and status changes on existing ones.
- **Physics State** — under the `spe` module only, one row per moved vector or axis.
- **Timeline** — a row for the chapter's story-time and elapsed time.
- **Logistics** — where tracked entities are and their condition.

Every load-bearing addition carries an Evidence row: a real quote from that chapter,
cited back to the manuscript Source.

## Numbers reconcile at commit

Before a chapter's commit completes, every number in its text — ages, tenures,
dates, durations, distances, counts, amounts — is traced against the graph. A number
that matches passes; a new number the chapter itself sources gets registered with an
evidence span and is canon from that commit forward; a number that contradicts the
graph **stops the commit** for the author to resolve — the prose or the graph gets
fixed, never silently one over the other. Rows marked provisional against a chapter
must be confirmed or corrected when that chapter's Final commits; a commit that
leaves a due provisional unresolved is incomplete.

## How canon commits record the change

Once a chapter's deltas are folded in, `current-canon-chapter` advances to that
chapter number and exactly one line is appended to the Canon Commit Log describing
the deltas in plain language. Log entries must be strictly increasing by chapter. If
the chapters being committed are drafts rather than finals, the run is marked
provisional and the report says so — canon normally commits only at Final, and
nothing is invented to fill a gap; a gap is left and flagged instead.

The loop finishes with a validation pass against the chapter files, so this batch's
quotes are hard-verified rather than degrading to a warning.
