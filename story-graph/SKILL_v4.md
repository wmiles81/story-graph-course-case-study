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
| No worksheet, no graph | **Reverse-engineer** | Follow `reference/reverse-engineer.md` |
| A `Story-Graph.md` already exists | **Catch-up** | Follow `reference/catch-up-from-chapters.md` |
| Always, as the last step | **Validate** | See *Validation* below |

Load the one reference file for the branch you're on; don't read all three.

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
python3 "<SKILL_DIR>/assets/story_graph.py" import-legacy <legacy-dir> --out <Story-Graph.md> [--report <coverage.md>] [--title "..."]
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
