# Compiling & querying

The markdown graph is the source of truth; `kuzu` is a disposable index built
from it. `compile` builds that index, `query` reads canned answers out of it.
Both need `pip install kuzu` — everything upstream of them (validate, propose,
verify-proposal, apply-proposal) is stdlib only.

## `compile` — build the Kùzu database from the markdown

Runs `validate` first and refuses to build on a graph with errors. Writes a
Kùzu database directory, not a single file — point `--out` at a directory
path, not a filename. Rebuild it after every edit to the graph markdown; the
database is a derived artifact, never hand-edited, never the thing you commit
as canon.

Flags:
- `--out DIR` — required. Where the compiled database goes.
- `--ontology PATH` — accepted, currently has no effect on the build.
- `--chapters-dir DIR` — passed through to the `validate` pre-check.

```bash
python3 story-graph/assets/story_graph.py compile series/books/book-3/Story-Graph.md \
  --out /tmp/book3.kuzu
```

## `query` — canned queries: irony, knows, open-loops, receipts

Runs one named, parameterized query against the compiled model. It compiles
the graph in-process each time (no need to run `compile` first) — the `--out`
directory from `compile` isn't required by `query`, which builds its own
throwaway connection from the markdown. The four names:

- `irony` — every proposition the reader knows that a holder currently
  believes false. No target needed.
- `knows <holder>` — everything a given holder (an entity id, or `reader`)
  currently knows or believes, in chapter order. Target is the holder id.
- `open-loops` — every Open Loops & Setups row, flagging any past its
  `must-fire-by` chapter as `[OVERDUE]`. No target needed.
- `receipts <prop-id>` — every evidence span that supports one proposition,
  with locator and quote. Target is the proposition id.

`knows` and `receipts` fail with a usage message if you omit the target —
`irony` and `open-loops` ignore it if you pass one.

```bash
python3 story-graph/assets/story_graph.py query knows series/books/book-3/Story-Graph.md jonah-harrow
```

```bash
python3 story-graph/assets/story_graph.py query receipts series/books/book-3/Story-Graph.md founding-scrolls-missing
```

Reach for `compile` when you want a durable database to point other Kùzu
tooling at. Reach for `query` for a one-line answer during a working session —
it's the fastest of the kuzu-backed commands because there's no `--out` to
manage.
