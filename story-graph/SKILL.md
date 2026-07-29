---
name: story-graph
description: Build, grow, and validate a canon knowledge graph (Story-Graph.md, ontology v2) for a manuscript — sources & authority, entities, relationships, holder-free propositions with epistemic states (knowledge/belief/reader awareness/embargoes), open loops & setups, evidence-backed spans, timeline, logistics, and an append-only canon commit log. Use when you need to produce, update, or query the structural state of a novel or series, in ANY project. Seeds from an NPE YFD-RAW worksheet when present; reverse-engineers the graph from chapter prose (full or partial manuscript) when no worksheet exists; catches up finalized chapters into an existing graph. Self-contained and portable — bundles its own template, ontology, and validator. Optionally compiles the graph into a queryable Kùzu property-graph database.
---

# Skill: Story Graph

Produce and maintain a `Story-Graph.md` — the canon knowledge graph (ABox) that
holds a manuscript's hidden state: who exists, who knows/believes what (and
since when, and with what evidence), what is planted and must fire, where
things are, and what changed each chapter. The graph conforms to the Story
Graph Ontology (TBox) bundled with this skill and is checked mechanically by
the bundled validator.

This skill is **self-contained and portable**. Everything it needs lives in
this skill folder — drop the folder into any project's `.claude/skills/` and
any workflow can invoke it. It does NOT depend on a host repo's
`Blueprints/` or `tools/` paths.

## Ontology v2

This skill authors **ontology v2** graphs (header `ontology-version | 2`).
v2 splits the graph into a genre-neutral **core** (12 sections, every graph,
any genre) and optional **modules** declared in the header `modules` field
(comma-separated, or `none`). Declaring a module adds its required
section(s) — today, `spe` adds a required **Physics State** section for
romance/NPE projects; a thriller or mystery graph declares `modules | none`
and never sees it. v2 also adds an authority + epistemic model (a `Sources`
registry, holder-free `Propositions`, and unified `Epistemic States` that
absorb belief and reader awareness) and manuscript-verified `Evidence` spans.
Read `assets/Story-Graph-Ontology-v2.md` before writing or editing a graph —
it is the authoritative schema this skill and its validator enforce.

A prior `ontology-version | 1` graph (`Story-Graph-Ontology-v1.md`,
`story_graph_v1.py`) remains supported for existing v1 projects; this skill's
default assets and validator target v2 only. Do not mix v1 and v2 sections in
one graph.

## Bundled assets (this skill's own files)

Resolve these relative to THIS skill's directory (the folder containing this
`SKILL.md`). Call it `<SKILL_DIR>`:

- `<SKILL_DIR>/assets/Story-Graph-TEMPLATE-v2.md` — the blank v2 graph to copy when seeding.
- `<SKILL_DIR>/assets/Story-Graph-Ontology-v2.md` — the v2 schema: header block, core/module sections, controlled vocabularies, table schemas, authority model, evidence-span rules, and the `compile` projection. Read it before writing the graph.
- `<SKILL_DIR>/assets/story_graph.py` — the stdlib-only validator, plus the `compile` entry point (lazily imports `story_graph_kuzu`).
- `<SKILL_DIR>/assets/story_graph_kuzu.py` — the Kùzu loader used only by `compile`; never imported by `validate`.
- `<SKILL_DIR>/assets/story_graph_llm.py` — provider-neutral chat client for optional AI subcommands. The validator/compiler **never** imports it; nothing in this skill's normal operation makes a network call.
- `<SKILL_DIR>/reference/decisions.md` — **inclusion & resolution rules. Read this in every mode**, alongside the one mode guide below.

## File-safety (unconditional)

NEVER overwrite or delete an existing graph. If a `Story-Graph.md` already
exists and you are about to replace rather than update it, stop and version the
old one first (copy to `Story-Graph_v1.md`, etc.). All edits to the current
graph are in-place table updates and append-only log entries — never a
destroy-and-rewrite. Use native file tools (Read/Write/Edit/Glob) only; the
sole permitted shell commands are the validator and compiler invocations
below.

## Inputs & target

Ask for (or infer) two things:

1. **Target folder** — where `Story-Graph.md` lives or will be created (the book
   or series folder). Default to the folder the user named or the graph they
   pointed at.
2. **Graph scope** — single book, or a series-continuous cumulative graph. For a
   series graph, follow the ontology's *Multi-Book Series Graphs* rules (header
   legend of per-book chapter ranges; every log entry carries its `(B# chN)`
   mapping).

## Mode detection (automatic — no flags)

Inspect the target folder, then take the matching path. Modes compose: a fresh
run typically does a seed/reverse-engineer pass, THEN a catch-up pass, THEN
validate, in one invocation.

| Detected | Mode | Do this |
|---|---|---|
| A worksheet (`*YFD-RAW*.md` or `master_story_document.md`) exists, no graph yet | **Seed** | Follow `reference/seed-from-worksheet.md` |
| Legacy canon CSVs (entity / proposition / assertion registries) exist, no graph | **Import-legacy** | Run `import-legacy` (see *Importing legacy canon*), then Catch-up + Validate |
| No worksheet, no legacy ledgers, no graph | **Reverse-engineer** | Follow `reference/reverse-engineer.md` |
| A `Story-Graph.md` already exists | **Catch-up** | Follow `reference/catch-up-from-chapters.md` |
| Always, as the last step | **Validate** | See *Validation* below |

Load the one reference file for the branch you're on; don't read all three.

**Always also load `reference/decisions.md`.** The mode guides say how to fill each
section; `decisions.md` says what earns a row and how to resolve references that
conflict — and those are the two calls the validator cannot make for you. In
particular, read it before you write your first Proposition: which rows are
*load-bearing* (and so must cite an evidence span or be marked `provisional`) is a
rule the validator **enforces**, and discovering it from an ERROR is the slow way.

### Seed vs. reverse-engineer

- **Seed** is exact: the worksheet already contains the entities,
  relationships, sources, propositions, and epistemic states, so transcribe
  them into the graph.
- **Reverse-engineer** is inference: with no worksheet, read the chapters and
  derive the same tables from the prose. Works on a **full or partial**
  manuscript — process whatever chapters exist. Every fact inferred from prose
  (not stated in a worksheet) is marked **provisional** per the anti-invention
  rule; note in the graph when it is incomplete. A provisional load-bearing
  row without an evidence span WARNs instead of ERRORing — see the ontology's
  *Evidence Span Rules*.

## Chapter discovery (portable)

Find chapters in the target folder in this order; use the first that yields files:

1. `**/Final-Chapters/Chapter*_Final*.md` (finalized canon; highest `_v#` wins per chapter)
2. `**/Draft-Chapters/Chapter*Draft*.md` (drafts — mark commits provisional)
3. A generic chapter glob (`**/Chapter*.md`, or files the caller points at)
4. A path the caller passes explicitly

Order chapters numerically. For a partial manuscript, set
`current-canon-chapter` to the highest chapter actually processed and say so in
the report. The same directory is what you pass as `--chapters-dir` to the
validator so `manuscript`-sourced Evidence quotes get hard-verified against
actual prose rather than degrading to a WARN.

## Validation (always last)

Run the bundled validator. It is a permitted shell command in this skill:

```
python3 "<SKILL_DIR>/assets/story_graph.py" validate "<target>/Story-Graph.md" \
    [--chapters-dir "<target's chapters directory>"] \
    [--spe-dir "<host SPE dir>"]
```

- `--chapters-dir` is **opt-in but strongly recommended**: without it,
  manuscript Evidence quotes cannot be hard-verified and the check degrades to
  a WARN (`could not verify manuscript quote`) instead of an ERROR on a
  mismatch. Pass it whenever the manuscript's chapter files are available.
- `--spe-dir` is accepted for parity with the rest of the skill's CLI surface;
  the v2 validator does not currently use it to check Physics State content
  (see the ontology's *Module: spe* note). Omit it if there is no SPE anchor
  catalog.
- Fix ERRORs (max 3 attempts), then stop and show the user the remaining
  failures. Report WARNs **verbatim** — never silently change a story fact to
  clear a warning.
- If `python3` is unavailable, say so once and continue (the graph is still
  written; it just wasn't machine-checked).

## Compiling to a queryable graph (optional)

Once a graph validates clean, it can be materialized into a Kùzu property-graph
database — a derived, rebuildable projection for Cypher queries. The
authored `Story-Graph.md` stays the source of truth; never hand-edit the
compiled database.

```
python3 "<SKILL_DIR>/assets/story_graph.py" compile "<target>/Story-Graph.md" \
    --out "<path to .kuzu db>" \
    [--chapters-dir "<target's chapters directory>"]
```

- `compile` runs `validate` first and **refuses to write anything if the
  graph has any ERRORs** — fix them, then re-run `compile`.
- `compile` needs the optional `kuzu` package: `pip install kuzu`. If it is
  not installed, `compile` reports this once and writes nothing; `validate`
  is unaffected either way (it never imports `kuzu`).
- Only tell the user to run `compile` when they actually want a queryable
  database (e.g. to answer a dramatic-irony or overdue-setups question over
  Cypher) — it is not part of the default seed/catch-up/validate loop.

## Querying

Once a graph validates clean, it can be asked writer-facing questions directly
— no separate `compile` step needed first: `query` and `report` compile the
text graph to a throwaway temp Kùzu database on each run, so there is never a
stale database to manage.

```
python3 "<SKILL_DIR>/assets/story_graph.py" query <irony|knows|open-loops|receipts> "<graph>" [target] [--chapters-dir <dir>]
python3 "<SKILL_DIR>/assets/story_graph.py" report "<graph>" [--chapters-dir <dir>]
```

- Both need the optional `kuzu` package: `pip install kuzu`.
- Both run `validate` first and **refuse to run if the graph has any
  ERRORs** — fix them, then re-run.
- Every answer carries its evidence receipts (source locator + quote), not
  just a bare claim.
- `irony` — propositions the reader `knows` that some character
  `believes-false`; no target argument.
- `knows` — what a holder currently holds, ordered by when each belief was
  formed; target is a holder id (a character's Entity id, or `reader`).
- `open-loops` — open loops & setups, flagged `[OVERDUE]` when unfired past
  their `must-fire-by` chapter relative to `current-canon-chapter`.
- `receipts` — the Evidence spans that support one proposition; target is a
  `prop-id`. Returns only that proposition's own spans (via the `SUPPORTS`
  edge), never another claim's quotes.
- `report` runs all of the above and prints a single summary: irony count,
  open-loop count (with overdue count), for the graph as a whole.

## Importing legacy canon

If a book was already modelled in an older CSV-ledger pipeline, `import-legacy`
converts that canon into a v2 `Story-Graph.md` in one pass, plus a coverage
report of what it could not faithfully carry over.

```
python3 "<SKILL_DIR>/assets/story_graph.py" import-legacy <legacy-dir> --out <Story-Graph.md> [--report <coverage.md>] [--title "..."] [--quotes <quoted-assertions.csv> --chapters-dir <chapters>]
```

- Reads the legacy ledgers found in `<legacy-dir>` (stdlib only): entity
  registry, proposition registry, routed assertions (with a
  `story_graph_destination` column), and scene ledger — matched by filename.
- Entity references are resolved by canonical name, then alias, then token
  overlap. A still-unresolved proper-noun **agent** (the subject of a
  knowledge/relationship assertion) is auto-registered as a `provisional`
  entity and disclosed in the coverage report; value strings and events are
  never turned into entities (anti-invention).
- CANON/world-level facts are reported as already captured by their proposition
  rather than dropped.
- Load-bearing rows are marked `provisional` when the legacy data has no
  verbatim `source_quote`, so the output validates with warnings, not errors.
- The coverage report lists everything covered-elsewhere, dropped, or degraded,
  plus layers these ledgers never contained (events, plot threads, promise
  lifecycle). Always `validate` the output; `compile`/`query` it like any graph.

## Canon lifecycle, audit & revision

Once a graph is built and validating, these commands operate on it. `queue` and
`deviations` are stdlib; `audit` and `impact` run Cypher over the compiled graph
and need `pip install kuzu`. `freeze` writes a new stamped file and never mutates
the source graph.

**Ratification & freeze (canon lifecycle):**
```
python3 "<SKILL_DIR>/assets/story_graph.py" queue "<graph>"
python3 "<SKILL_DIR>/assets/story_graph.py" freeze "<graph>" --version <CANON-ID> --out <frozen.md> [--force] [--at YYYY-MM-DD]
```
- `queue` — the ratification queue: every load-bearing row still marked
  `provisional`, grouped by section. Work it toward empty (add evidence, or
  accept a row by removing its `provisional` mark) before freezing.
- `freeze` — validate, then stamp a versioned baseline (`canon-version` /
  `frozen-at` in the header) into a NEW file. Refuses if provisional rows remain
  unless `--force`. A frozen graph that still holds provisional rows warns on
  `validate`.

**Coverage (is the graph actually populated?):**
```
python3 "<SKILL_DIR>/assets/story_graph.py" coverage "<graph>"
```
Reports which ontology layers are populated and how deeply — rows per layer,
what share of propositions have a holder, how many are held by 2+ holders
(shared knowledge), dramatic-irony pairs, source-verified share, and how
concentrated the edges are on one node — then FLAGS the gaps. Run it first on any
inherited or imported graph: a graph can validate perfectly and still record
claims with nobody's knowledge attached and no entity relationships, which no
amount of querying will reveal. The flags name the fix (usually catch-up mode).

**Continuity audit:**
```
python3 "<SKILL_DIR>/assets/story_graph.py" audit "<graph>" [--chapters-dir <dir>] [--adjudicated <file>]
```
Reports continuity candidates, grouped: a character who `knows` a fact before its
evidence chapter; an `UNFIRED` setup past its must-fire-by; and orphan
propositions (no holder, no evidence). Each has a stable `key` — list keys in the
`--adjudicated` sidecar to suppress issues you've explained.

**Revision impact & drift:**
```
python3 "<SKILL_DIR>/assets/story_graph.py" impact "<graph>" <prop-id>
python3 "<SKILL_DIR>/assets/story_graph.py" deviations "<graph>" --chapters-dir <dir>
```
- `impact` — what depends on a proposition: the holders whose knowledge rests on
  it, the evidence establishing it, and whether it anchors dramatic irony
  (moving or cutting it collapses that irony).
- `deviations` — manuscript-verified Evidence quotes that no longer appear in
  their chapter: canon claims the current prose has drifted from. Rewrite a scene
  and its claims light up. Exits non-zero when drift is found.

## Visualizing the graph

Two ways to see the graph, not just read it as text.

**Built-in — a self-contained HTML page (stdlib, no dependencies):**
```
python3 "<SKILL_DIR>/assets/story_graph.py" visualize "<graph>" --out <graph.html> [--prop <prop-id>]
```
Renders a node-link diagram (a deterministic force layout emitted as inline SVG,
coloured by node kind, light/dark aware) that opens in any browser. With `--prop`
it draws just that proposition's neighbourhood — holders, evidence, governing
source — the visual companion to `impact`; without it, the whole
entity/proposition/source graph.

**Kùzu Explorer — interactive Cypher + graph viz (third-party, Docker):**
A `compile --out db.kuzu` database is a standard Kùzu database, so Kùzu's official
browser UI can open it for interactive exploration and graphical Cypher:
```
python3 "<SKILL_DIR>/assets/story_graph.py" compile "<graph>" --out /abs/path/book.kuzu
docker run --rm -p 8000:8000 -v /abs/path/book.kuzu:/database -e MODE=READ_ONLY kuzudb/explorer:latest
# then open http://localhost:8000
```
Use the `kuzudb/explorer` image tag matching your installed Kùzu version — the
on-disk format is version-specific (Kùzu 0.11.x here). `MODE=READ_ONLY` is
recommended: the compiled DB is a rebuildable projection of `Story-Graph.md`, so
there is no reason to let the UI write back to it.

## Generating rows from prose

**You are the judge.** If you are reading this manuscript in an editor, you are the
strongest model available and you are already here — routing this to a smaller model over
HTTP is a downgrade, not a design.

```bash
# 1. ask: writes the questions to disk, calls nothing
python3 <SKILL_DIR>/assets/story_graph.py propose epistemic <graph> --chapters-dir <d> --ask --out q/

# 2. read q/epistemic-ch01.question.json, decide, save q/epistemic-ch01.answer.json

# 3. turn your answers into proposal rows
python3 <SKILL_DIR>/assets/story_graph.py propose epistemic <graph> --chapters-dir <d> --answers q/ --out proposals/
```

Run the kinds in order — `entities`, then `evidence`, then `epistemic` — because a belief
cannot name a holder the graph has never heard of.

**You never write a quote.** Each question gives you numbered sentences taken from the
chapter; you answer with a NUMBER and code attaches the sentence. That is what makes a
fabricated quote impossible rather than merely detectable — asked for free text, a small
model fabricated 23 of 23; asked for an index, none.

**Answer 0, or omit the claim, whenever no listed sentence shows the stance.** A sentence
on the same topic is not evidence. This is the discipline the whole thing depends on, and
it is the first thing a weak judge abandons.

`--provider/--model` still exists for headless or batch runs. It is the weakest link when
the model is small, and it is not the main path.

## Proposals: how generated rows reach canon

**A generated row is a file on disk, never an edit to the graph.** Anything produced by
a model goes through this gate first — the gate is deterministic and calls no model.

```bash
python3 <SKILL_DIR>/assets/story_graph.py verify-proposal <p.json> --graph <g> --chapters-dir <d>
python3 <SKILL_DIR>/assets/story_graph.py apply-proposal  <p.json> --graph <g> --chapters-dir <d> --accept 1,4,7
```

Each row gets `PASS`, `FAIL <reason>`, or `NEEDS-HUMAN`. The checks: the section and
columns exist, key columns are non-empty, every id resolves, the chapter is within canon,
cited spans are declared, the row isn't already present — and **the quote gate**: the
row's `basis.quote` must appear *verbatim* in its chapter. A model can invent a belief;
it cannot invent a sentence that is on the page.

Then a consequence pass validates the whole would-be graph and rejects any row that
introduces an error the graph didn't already have.

**`NEEDS-HUMAN` is not a soft pass.** Rows in `Epistemic States`, `Relationships` and
`Open Loops & Setups` are *inferences*: the quote is real, but what it MEANS is a
reading, and no checker confirms a reading. They can never auto-ratify. `--accept pass`
deliberately excludes them; naming their row numbers is the deliberate act.

Applying keeps the previous graph at the next free `_v<N>` slot, marks every new row
`provisional`, and appends one Canon Commit Log line naming the model and the proposal
file — so you can always ask what was proposed, what the checker allowed, and what you
took. There is no `--force`.

## Checking the shape of your claims

```bash
python3 <SKILL_DIR>/assets/story_graph.py shapes <graph>
```

Lists propositions that can become FALSE later in the same book — `"The Founding Scrolls
are missing"`, `"Margot is inside the library"` — ranked by how many holders already
believe them. A Proposition has no time bounds, so these generate contradictions that are
nobody's mistake: the claim was true when written and false by the end.

Run it before a catch-up pass. A state-shaped claim poisons every epistemic row that
touches it, and rewriting one after fifty rows cite it is far more work than rewriting it
now. The fix is always the same shape — say the event that made it true:

  `"The Founding Scrolls are missing."` -> `"The Founding Scrolls are taken from the vault before ch02."`

Rewriting a statement is a canon change, so the tool reports and does not edit.

## Saying what a claim rests on

Propositions take an optional `depends-on` column listing the prop-ids this claim needs in
order to be true. `queue` then ranks by what would have to be REVISITED if a claim moved,
not by how many characters happen to hold an opinion about it — weight is transitive, so a
claim underpinning a chain outranks a popular one.

Read it as "this needs that": the Purge Protocol fires *because* the Scrolls left
containment, so the Purge claim depends on the discovery claim. Getting the direction
backwards inverts the whole ranking and nothing can catch it for you.

The column is optional and backward compatible — a graph without it scores exactly as
before. Ids must resolve and the edges must not form a cycle; both are validation errors.

## Series graphs (one canon across books)

A series graph numbers chapters continuously — Book 2 chapter 1 is series ch31 if Book 1
ran to 30 — so it MUST carry a chapter-convention legend in the header, one blockquote
line per book:

```
> B1 ch1-30 — series/books/book-1/phase-7-drafting/chapters
> B2 ch31-50 — series/books/book-2/phase-7-drafting/chapters
```

`validate` reads it, so a series graph needs **no `--chapters-dir`**: each Evidence
locator resolves to the right book's directory, whatever that book names its files. The
ranges must ascend, must not overlap, and must point at directories that exist — a legend
that lies sends the quote checker to the wrong book, which is worse than none.

Without the legend a series graph is silently unverifiable, so a Canon Commit Log carrying
`(B# chN)` mappings with no legend is an ERROR rather than a warning.

## Review is cumulative

```bash
python3 <SKILL_DIR>/assets/story_graph.py reject-proposal <p.json> --graph <g> \
    --rows 3,7 --reason "the quote shows anger, not belief"
```

Every accept and every rejection is appended to `<graph>-review.jsonl` beside the graph.
`verify-proposal` then marks a row you have already decided as `SEEN`, and tells you how
many rows are **genuinely new** — so re-running a generator costs you the new rows to read,
not all of them again.

Record the REASON. When the same claim comes back with a different quote, the row is shown
with your reason attached rather than hidden: "this stance is wrong" should stay decided,
but "that quote doesn't support it" deserves another look, and only you know which you
meant.

The ledger is append-only and shared across the graph's versions, so applying a proposal —
which rolls the graph to a new `_v<N>` — never forgets what you decided before it.

## Finding what's missing (deterministic)

Two candidate generators. Neither uses a model, neither writes to the graph, and both
are tuned for recall — a missed candidate is invisible, a spurious one costs a glance.

```bash
# proper nouns in the prose with no entity behind them, most frequent first
python3 <SKILL_DIR>/assets/story_graph.py unresolved <graph> --chapters-dir <dir> [--min 4]

# claims about the same subject, partitioned by chapter
python3 <SKILL_DIR>/assets/story_graph.py conflicts <graph> [--overlap 0.45]
```

**Run `unresolved` at the start of every catch-up pass.** It turns "who did I forget to
model?" from a re-read of the manuscript into a finite ranked list. A name near the top
with no entity row is usually a character the graph never caught up on.

`conflicts` partitions on purpose (see `reference/decisions.md` 2.4): **same chapter is
a bug; different chapters is usually plot.** A pair it cannot date lands in UNDATED and
tells you nothing — so the report prints what fraction of propositions resolve to a
chapter at all, because that number caps what the command can say.

Neither output is a verdict. `unresolved` also surfaces capitalised common nouns, and
`conflicts` also surfaces claims that are merely compatible.

## Scoring the decisions (optional)

`reference/decisions.md` states the inclusion & resolution rules; `decisions` measures
whether they're followed, so a change to the rules produces a number instead of an
argument.

```bash
# structural check only — no model, no network, safe in CI
python3 <SKILL_DIR>/assets/story_graph.py decisions

# scored against a model you choose (local needs no key)
python3 <SKILL_DIR>/assets/story_graph.py decisions --provider ollama --model <id>
```

Each case in `tests/decisions/` is a short scene, the correct call, and the trap it
sets. **Every category carries both polarities on purpose** — without a control, a
degenerate strategy ("always ambiguous", "always propose a row") scores well while
deciding nothing. A format failure is reported as `FMT`, separately from a wrong
decision, and retried once; the two are different failures and conflating them makes
the score unreadable.

Note what this does *not* do: it scores judgement against a fixture, not against your
manuscript. A high score means the rules are being applied consistently, not that the
resulting graph is right.

## Genre modules (optional)

If the host project declares genre modules (in a worksheet RDL or an existing
graph header) AND has a genres directory, honor them: load ONLY the declared
modules, use their extended edge vocabulary. With no genres directory, keep
`modules: none` (or `spe` only if the project is a romance/NPE project using
Physics State) and use core edge vocabulary plus the graph's own Local
Vocabulary. NEVER load an undeclared module.

## Report

Tell the user: mode(s) taken, whether it seeded or reverse-engineered, chapters
processed, final `current-canon-chapter`, validator result (errors fixed,
warnings verbatim), whether the graph was compiled, and — for
reverse-engineered graphs — that facts are provisional and where they were
inferred from.
