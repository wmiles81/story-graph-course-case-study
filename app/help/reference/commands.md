# Command reference

`python3 story-graph/assets/story_graph.py <command> …` — 21 subcommands, stdlib only.
`compile` / `query` / `audit` / `impact` additionally want `pip install kuzu`.

## Build & maintain

| Command | Does |
|---|---|
| `validate` | Structural + vocabulary checks, and graph-vs-source quote verification with `--chapters-dir`. |
| `compile` | Build the Kùzu database from the markdown. |
| `import-legacy` | Convert a v1 / legacy graph to ontology v2. Pure code, no AI. |
| `freeze` | Stamp a versioned canon baseline. |

## Query & report

| Command | Does |
|---|---|
| `query` | Canned queries: irony, knows, open-loops, receipts. |
| `report` | The digest. |
| `coverage` | Which layers are populated, how deep, what is missing. |
| `queue` | What is still provisional, ranked structurally. |
| `audit` | Continuity detectors. |
| `impact` | What depends on a claim. |
| `deviations` | Where the prose drifted from canon. |
| `visualize` | Self-contained node-link HTML page. |

## Find problems

| Command | Does |
|---|---|
| `unresolved` | Prose names no entity owns, split into probable **names** and **descriptions**, plus names two entities both claim. |
| `conflicts` | Claims that may not both be true, partitioned by chapter. |
| `shapes` | Propositions that can become false later in the same book. |
| `irony` | The reader knows a claim while a holder believes it false. |
| `decisions` | Score the decision rules against the fixture corpus of hard cases. |

## Propose from prose

| Command | Does |
|---|---|
| `propose entities\|evidence\|epistemic\|dependencies` | Write proposal files. `--ask` writes the question to disk and calls no model. |
| `verify-proposal` | Gate every row against the manuscript and the ledger. |
| `apply-proposal` | Write only what you accept (`--accept pass\|all\|1,3,5`). |
| `reject-proposal` | Record a decision, with a reason, in the append-only ledger. |
