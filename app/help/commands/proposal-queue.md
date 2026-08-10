# The proposal queue (CLI)

The four proposal-lifecycle commands plus `queue` — the CLI side of the
workflow described in Skill Workflows → The proposal queue. All five are
stdlib only; no `kuzu` required.

## `propose` — write proposal files

Generates candidate rows for one graph section — `entities`, `evidence`,
`epistemic`, or `dependencies`, in that order, since a belief can't name a
holder the graph hasn't heard of yet. Writes a JSON proposal file; nothing
about proposing touches the graph.

Flags:
- `kind` (positional) — one of `entities | evidence | epistemic | dependencies`.
- `--chapters-dir DIR` — required.
- `--ask` — write the question to disk instead of calling a model; an agent
  reading the manuscript in-session answers it.
- `--answers DIR` — directory of `<kind>-<scope>.answer.json` files (paired
  with `--ask`).
- `--provider NAME`, `--model NAME` — only for a headless/batch run.
- `--out DIR` — where proposal files land (default `proposals`).
- `--cache PATH` — reuse replies across runs (recommended).
- `--limit N` — claims/candidates per call.
- `--chapters ch01,ch02` — restrict to specific chapter stems.
- `--env PATH` — `.env` holding a provider key.

```bash
python3 story-graph/assets/story_graph.py propose entities series/books/book-3/Story-Graph.md \
  --chapters-dir series/books/book-3/chapters --ask
```

## `verify-proposal` — gate every row against the manuscript and the ledger

Deterministic pass, no model, no network: checks the section and its columns
exist, key columns are non-empty, every id resolves, the chapter falls within
canon, cited evidence spans are declared, the row isn't already present, and
the quote gate — any `basis.quote` on a row must appear verbatim in its
chapter. Reports each row **PASS**, **FAIL** with a reason, or **NEEDS-HUMAN**
(an inference a checker can't confirm — the quote is real, what it means is a
reading).

Flags:
- `proposal` (positional) — the proposal file.
- `--graph PATH` — required.
- `--chapters-dir DIR`

```bash
python3 story-graph/assets/story_graph.py verify-proposal proposals/entities-book3.json \
  --graph series/books/book-3/Story-Graph.md --chapters-dir series/books/book-3/chapters
```

## `apply-proposal` — write only what you accept

Takes `--accept` naming row numbers, or `pass` (every row that verified
clean, excluding NEEDS-HUMAN), or `all` (every row that didn't fail,
including NEEDS-HUMAN — prints a note naming how many unreviewed rows it's
taking). A row that already failed verification cannot be applied; there's no
`--force`. Keeps the previous graph at the next free `_v<N>` slot, marks new
rows provisional, and appends one Canon Commit Log line.

Flags:
- `proposal` (positional)
- `--graph PATH` — required.
- `--chapters-dir DIR`
- `--accept ACCEPT` — required. Row numbers (`1,3,5`), `pass`, or `all`.

```bash
python3 story-graph/assets/story_graph.py apply-proposal proposals/entities-book3.json \
  --graph series/books/book-3/Story-Graph.md --accept pass
```

## `reject-proposal` — record a decision, with a reason, in the ledger

Records rows you're turning down, with a reason, in a per-graph review
ledger — the graph itself is untouched. The next time a generator produces
the same claim, `verify-proposal` marks it `SEEN` and shows the prior reason.

Flags:
- `proposal` (positional)
- `--graph PATH` — required.
- `--rows ROWS` — required. Row numbers you are rejecting.
- `--reason REASON` — shown when the row is proposed again.

```bash
python3 story-graph/assets/story_graph.py reject-proposal proposals/entities-book3.json \
  --graph series/books/book-3/Story-Graph.md --rows 4 --reason "already an alias, not a new entity"
```

## `queue` — what is still provisional, ranked structurally

Not part of the propose/verify/apply/reject lifecycle itself — it reads the
graph after the fact and ranks every unratified row by how much rests on it:
holders, evidence spans, dependents, dramatic irony, and overdue open-loop
obligation. 149 rows in file order tells you nothing about where to start;
`queue` does.

```bash
python3 story-graph/assets/story_graph.py queue series/books/book-3/Story-Graph.md
```
