---
name: story-graph
description: Build, grow, and validate a canon knowledge graph (Story-Graph.md) for a manuscript — entities, relationships, knowledge/embargoes, guns, timeline, logistics, and an append-only canon commit log. Use when you need to produce or update a Story Graph for a novel or series, in ANY project. Seeds from an NPE YFD-RAW worksheet when present; reverse-engineers the graph from chapter prose (full or partial manuscript) when no worksheet exists; catches up finalized chapters into an existing graph. Self-contained and portable — bundles its own template, ontology, and validator.
---

# Skill: Story Graph

Produce and maintain a `Story-Graph.md` — the canon knowledge graph (ABox) that
holds a manuscript's hidden state: who exists, who knows what, what is planted
and must fire, where things are, and what changed each chapter. The graph
conforms to the Story Graph Ontology (TBox) bundled with this skill and is
checked mechanically by the bundled validator.

This skill is **self-contained and portable**. Everything it needs lives in this
skill folder — drop the folder into any project's `.claude/skills/` and any
workflow can invoke it. It does NOT depend on a host repo's `Blueprints/` or
`tools/` paths.

## Bundled assets (this skill's own files)

Resolve these relative to THIS skill's directory (the folder containing this
`SKILL.md`). Call it `<SKILL_DIR>`:

- `<SKILL_DIR>/assets/Story-Graph-TEMPLATE.md` — the blank graph to copy when seeding.
- `<SKILL_DIR>/assets/Story-Graph-Ontology-v1.md` — the schema: sections, entity types, core edge vocabulary, trends, table schemas, canon-commit rules. Read it before writing the graph.
- `<SKILL_DIR>/assets/story_graph.py` — the stdlib-only validator.

## File-safety (unconditional)

NEVER overwrite or delete an existing graph. If a `Story-Graph.md` already
exists and you are about to replace rather than update it, stop and version the
old one first (copy to `Story-Graph_v1.md`, etc.). All edits to the current
graph are in-place table updates and append-only log entries — never a
destroy-and-rewrite. Use native file tools (Read/Write/Edit/Glob) only; the
sole permitted shell command is the validator invocation below.

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

- **Seed** is exact: the worksheet already contains the entities, relationships,
  guns, and knowledge, so transcribe them into the graph.
- **Reverse-engineer** is inference: with no worksheet, read the chapters and
  derive the same tables from the prose. Works on a **full or partial**
  manuscript — process whatever chapters exist. Every fact inferred from prose
  (not stated in a worksheet) is marked **provisional** per the anti-invention
  rule; note in the graph when it is incomplete.

## Chapter discovery (portable)

Find chapters in the target folder in this order; use the first that yields files:

1. `**/Final-Chapters/Chapter*_Final*.md` (finalized canon; highest `_v#` wins per chapter)
2. `**/Draft-Chapters/Chapter*Draft*.md` (drafts — mark commits provisional)
3. A generic chapter glob (`**/Chapter*.md`, or files the caller points at)
4. A path the caller passes explicitly

Order chapters numerically. For a partial manuscript, set
`current-canon-chapter` to the highest chapter actually processed and say so in
the report.

## Validation (always last)

Run the bundled validator. It is the ONLY permitted shell command in this skill:

```
python3 "<SKILL_DIR>/assets/story_graph.py" validate "<target>/Story-Graph.md" \
    --ontology "<SKILL_DIR>/assets/Story-Graph-Ontology-v1.md" \
    [--genres-dir "<host genres dir>"] [--spe-dir "<host SPE dir>"]
```

- `--genres-dir` and `--spe-dir` are **opt-in**: pass them ONLY if the host
  project actually has those directories (e.g. `Blueprints/Genres`, `SPE`).
  Omit them otherwise — the validator degrades gracefully (genre-module and
  SPE-anchor checks are simply skipped, or downgraded to warnings).
- Fix ERRORs (max 3 attempts), then stop and show the user the remaining
  failures. Report WARNs **verbatim** — never silently change a story fact to
  clear a warning.
- If `python3` is unavailable, say so once and continue (the graph is still
  written; it just wasn't machine-checked).

## Genre modules (optional)

If the host project declares genre modules (in a worksheet RDL or an existing
graph header) AND has a genres directory, honor them: load ONLY the declared
modules, use their extended edge vocabulary, and pass `--genres-dir`. With no
genres directory, keep `genre-modules: none` and use core edge vocabulary plus
the graph's own Local Vocabulary. NEVER load an undeclared genre module.

## Report

Tell the user: mode(s) taken, whether it seeded or reverse-engineered, chapters
processed, final `current-canon-chapter`, validator result (errors fixed,
warnings verbatim), and — for reverse-engineered graphs — that facts are
provisional and where they were inferred from.
