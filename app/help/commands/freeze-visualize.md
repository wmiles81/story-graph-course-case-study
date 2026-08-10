# Freezing & visualizing

Two commands that produce a snapshot of the graph as it stands — one a
versioned canon baseline, the other a picture. Both stdlib only.

## `freeze` — stamp a versioned canon baseline

Validates first and refuses to freeze if that fails. Then checks for
unratified (provisional) load-bearing rows and refuses to freeze with them
still open, unless `--force`. Writes the stamped graph to `--out`; the source
graph is left untouched. Use this at the end of an editing pass, once
everything provisional has been resolved, to lock in a version you can point
readers or later chapters at with confidence.

Flags:
- `--version VERSION` — required. The version label to stamp.
- `--out PATH` — required. Where the frozen graph is written.
- `--force` — freeze anyway, recording unresolved provisional rows as
  unresolved rather than blocking.
- `--at DATE` — freeze date (default: today).

```bash
python3 story-graph/assets/story_graph.py freeze series/books/book-3/Story-Graph.md \
  --version v1.0 --out series/books/book-3/Story-Graph-v1.0-frozen.md
```

## `visualize` — self-contained node-link HTML page

Builds a single HTML file with an embedded force-directed layout of the
graph — open it in a browser, no server needed. Pass `--prop` to center the
view on one proposition and its immediate neighborhood instead of the whole
graph; useful once a graph is too dense to read as a single hairball.

Flags:
- `--out PATH` — required. Where the HTML file is written.
- `--prop PROP-ID` — optional. Center on one proposition's neighborhood.

```bash
python3 story-graph/assets/story_graph.py visualize series/books/book-3/Story-Graph.md \
  --out /tmp/book3-graph.html
```

```bash
python3 story-graph/assets/story_graph.py visualize series/books/book-3/Story-Graph.md \
  --out /tmp/book3-scrolls.html --prop founding-scrolls-missing
```
