# Checking the graph

Three commands that ask "is this graph telling the truth" from different angles:
`validate` checks the file against its own rules, `audit` checks the claims
against each other, `deviations` checks the graph against the current prose.

## `validate` — structural and vocabulary checks, with optional quote verification

Runs first inside almost every other command — `compile`, `report`, `audit`,
`impact`, `coverage`, `queue`, and `freeze` all call it before doing anything
else, so a broken graph never reaches a downstream tool. On its own it checks
required sections and header fields exist, every reference resolves (sources,
entities, propositions, span ids), evidence spans are declared where a row
claims one, aliases and open loops are well-formed, and the Canon Commit Log is
append-only.

Flags:
- `--chapters-dir DIR` — turns on the quote gate: every `basis.quote` on a row
  must appear verbatim in the chapter file it cites. Without this flag,
  validate only checks structure, not truth against prose.
- `--spe-dir DIR` — when the graph declares the `spe` module, checks claims
  against physics anchors in that directory.
- `--ontology PATH`, `--genres-dir DIR` — accepted for forward compatibility;
  neither currently changes what gets checked.

Stdlib only — no `kuzu` needed.

```bash
python3 story-graph/assets/story_graph.py validate series/books/book-3/Story-Graph.md \
  --chapters-dir series/books/book-3/chapters
```

## `audit` — continuity detectors

Runs `validate` first, then a second pass purpose-built to catch the bugs
structural checking can't see: a holder knowing a proposition before its own
supporting evidence appears, and stances on the same proposition whose time
windows overlap when they shouldn't (a state-shaped claim can't be true and
false for the same holder in the same stretch of story). Needs `kuzu`
(`pip install kuzu`) — it queries the compiled graph, not the raw markdown.

Flags:
- `--chapters-dir DIR` — passed through to the `validate` pre-check.
- `--adjudicated PATH` — a file of ids the audit should treat as reviewed and
  skip re-flagging.

```bash
python3 story-graph/assets/story_graph.py audit series/books/book-3/Story-Graph.md
```

## `deviations` — where the prose drifted from canon

The graph-vs-source check re-framed as a revision-drift report: for every
proposition with a cited quote, does that quote still appear in the current
chapter text? A book gets rewritten; the graph doesn't automatically follow.
This is what catches a claim whose evidence quote no longer exists on the
page. Stdlib only — no `kuzu` needed. `--chapters-dir` is required, not
optional, since there's nothing to compare against without it.

```bash
python3 story-graph/assets/story_graph.py deviations series/books/book-3/Story-Graph.md \
  --chapters-dir series/books/book-3/chapters
```

Reach for `validate` after any hand-edit of the graph file. Reach for `audit`
after applying a batch of proposals, when you want a second pass that reasons
across rows rather than checking each one in isolation. Reach for `deviations`
after a prose revision pass, before trusting the graph's evidence citations
again.
