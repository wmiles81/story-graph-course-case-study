# Story Graph Fiction Case Study

A source-grounded, worked case study showing how a complete novel becomes a queryable model of canon, chronology, knowledge, belief, custody, promises, plot threads, intersections, and revision authority.

The repository has two halves. The **case study** is the historical pilot that produced the method. The **tool** is what the method became: a portable skill that turns a manuscript into a checkable graph and verifies every inferred claim against the actual prose.

## The tool — [`story-graph/`](story-graph/)

Drop the folder into any project's `.claude/skills/` and it works there. One human-readable `Story-Graph.md` per book, mechanically checked, optionally compiled into a graph database.

```
python3 story-graph/assets/story_graph.py validate <graph> --chapters-dir <chapters>
```

The safety model is the point: **AI proposes, deterministic code verifies, a human accepts.** The engine makes no network calls and contains no model. An AI can invent a belief; it cannot invent a sentence that is genuinely on the page — so a proposed row only sheds `provisional` when it cites a quote the validator finds in the real chapter. Rows asserting a *reading* rather than a transcription are always `NEEDS-HUMAN` and never auto-applied.

21 subcommands, 295 tests. See [`story-graph/README.md`](story-graph/README.md) for the full tour and [`story-graph/assets/Story-Graph-Ontology-v2.md`](story-graph/assets/Story-Graph-Ontology-v2.md) for the authoritative schema.

## Structure

- `story-graph/` — **the skill**: ontology, validator/CLI, per-mode guides, decision rulebook, tests
- `app/` — a browsable operating-system view (dashboard, interactive graph, belief timeline, Cypher console)
- `docs/act-1/` — governing method and Act I analysis reports
- `data/act-1/` — reconciled scene, context, entity, proposition, assertion, and predicate artifacts
- `docs/deep-analysis/` — later event, thread, and intersection reports
- `data/deep-analysis/` — candidate event and analytical ledgers
- `docs/ai-plan_v2.md` — the plan that built the decision layer, with measured outcomes and what is deliberately unfinished
- `packages/` — preserved ZIP packages in production order where available
- `notion/` — page links and publishing notes

The manuscripts themselves are not in this repository: `series/` is gitignored because this repo is public. Tests that need a real graph ship a synthetic fixture instead ([`story-graph/tests/fixtures/`](story-graph/tests/fixtures/)), so a fresh clone runs the suite green.

## Canon status

Act I artifacts are preserved as historical pilot outputs. Later author-ratified canon supersedes them where explicitly recorded. Nothing in this repository should silently overwrite accepted canon.

## Student Notion pages

- Act I — The Source-Grounded Pilot: https://app.notion.com/p/3a55d3ff7a19812eb316f7876c53d420
- Student Edition: https://app.notion.com/p/3a75d3ff7a1981daaa62ed67e64d23c4
