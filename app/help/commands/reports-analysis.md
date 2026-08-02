# Reports & analysis

Eight commands that read the graph and tell you something about its shape or
its health, without writing anything back. Three need `kuzu`
(`pip install kuzu`) because they query the compiled model; five run on the
parsed markdown directly and are stdlib only.

## `report` — the digest

Needs `kuzu`. The short version of `audit`-adjacent state: dramatic irony
pairs and open loops, with overdue ones flagged, in one screen. Good as a
standing check during a session, before reaching for the narrower commands.

```bash
python3 story-graph/assets/story_graph.py report series/books/book-3/Story-Graph.md
```

## `coverage` — which layers are populated, how deep, what's missing

Stdlib only. A graph can validate cleanly and still be nearly useless — claims
recorded with nobody's knowledge attached, no relationships, no
believes-false anywhere. `coverage` counts rows per section and flags empty
ones (`<- empty`), so a thin graph shows up as a diagnostic instead of
something you discover by eyeballing a hairball later.

```bash
python3 story-graph/assets/story_graph.py coverage series/books/book-3/Story-Graph.md
```

## `impact` — what depends on a claim

Needs `kuzu`. Given a proposition id, lists the holders whose knowledge
depends on it, the evidence that establishes it, and who governs it — the
blast radius of retracting or rewriting that one claim.

```bash
python3 story-graph/assets/story_graph.py impact series/books/book-3/Story-Graph.md founding-scrolls-missing
```

## `shapes` — propositions that can become false later in the same book

Stdlib only. Two failure flavors, riskiest first: **state-shaped** claims that
can flip within the book but carry no time bound to say when, and
**unanchored** claims with no evidence locator and no epistemic since-chapter
— so nothing records whether they've even happened yet. A Proposition has no
built-in time bounds; this is what surfaces the ones that needed one.

```bash
python3 story-graph/assets/story_graph.py shapes series/books/book-3/Story-Graph.md
```

## `irony` — the reader knows a claim while a holder believes it false

Stdlib only. Lists every proposition marked `believes-false` for some holder
while the reader (or canon) knows it's true — the dramatic-irony pairs a
linear read can't surface on its own, because a character confidently wrong is
invisible until you go looking for it structurally.

```bash
python3 story-graph/assets/story_graph.py irony series/books/book-3/Story-Graph.md
```

## `conflicts` — claims that may not both be true, partitioned by chapter

Stdlib only. Finds proposition pairs about the same subject above a
content-word similarity floor, then splits them: **same chapter** pairs (no
event between them can reconcile the two — likeliest genuine contradictions),
**different chapters** (a state may simply have changed — look for the event),
and **undated** (no evidence locator or since-ch, so they can't be
partitioned at all).

Flags:
- `--overlap FLOAT` — content-word similarity floor (default 0.45). Raise it
  to cut false positives on a large cast; lower it if real conflicts are
  slipping through.

```bash
python3 story-graph/assets/story_graph.py conflicts series/books/book-3/Story-Graph.md --overlap 0.5
```

## `unresolved` — prose names no entity owns

Stdlib only. Scans the manuscript for capitalized names/descriptions that
never resolved to an entity id, split into probable **names** and
**descriptions**, plus a separate list of names two entities both claim.
`--chapters-dir` is required — there's no prose to scan without it.

Flags:
- `--chapters-dir DIR` — required.
- `--min N` — ignore names seen fewer than N times (default 2).
- `--ambiguous-min N` — also list names claimed by 2+ entities (default 2; 0
  disables the ambiguous list).

```bash
python3 story-graph/assets/story_graph.py unresolved series/books/book-3/Story-Graph.md \
  --chapters-dir series/books/book-3/chapters
```

## `decisions` — score the decision rules against the fixture corpus

Structural check by default: confirms every hard case has a scene, a trap, a
checkable expectation, and every category has a control — no model call. Pass
`--provider`/`--model` to actually run those cases through a model and score
its calls against the expected answers; `cases` defaults to the bundled
`story-graph/tests/decisions` corpus if omitted.

Flags:
- `cases` (positional, optional) — path to a decisions corpus; defaults to
  the bundled one.
- `--provider ollama|lmstudio|openrouter` — omit for the structural check only.
- `--model NAME`
- `--env PATH` — `.env` holding a provider key (default: none).

```bash
python3 story-graph/assets/story_graph.py decisions
```

Reach for `coverage` and `shapes` early, while a graph is thin. Reach for
`irony`, `conflicts`, and `unresolved` while reconciling graph against prose.
Reach for `report` and `impact` once the graph is populated and you're
checking specific claims.
