# Story Graph Ontology v1

The TBox of the NPE Romance Architect canon system: what CAN exist in a Story Graph
and the rules that govern it. Each story's `Story-Graph.md` (the ABox) must conform.
The validator (`tools/story_graph.py`) enforces this document mechanically.

## Graph Sections

`Story-Graph.md` must contain, in this exact order, after the header block:

| # | section header |
|---|---|
| 1 | Local Vocabulary |
| 2 | Entities |
| 3 | Locations & Distances |
| 4 | Relationships |
| 5 | Knowledge States |
| 6 | Open Loops & Guns |
| 7 | Physics State |
| 8 | Timeline |
| 9 | Logistics |
| 10 | Private Beliefs (Ghost) |
| 11 | Canon Commit Log |

Headers must never be renamed, reordered, or removed. Sections 1–10 are
current-state tables (rows are edited as truth changes). Section 11 is
append-only history.

## Header Block

Before the first `##` section, under the `# Story Graph: <Title>` line, a table:

| field | value |
|---|---|
| ontology-version | 1 |
| genre-modules | ordered list, comma-separated, or `none` |
| current-canon-chapter | integer; 0 = seeded, nothing committed |

`genre-modules` is the import statement: commands load ONLY the core ontology
plus the listed modules from `Blueprints/Genres/`. Where two modules set the
same dial, the FIRST listed wins.

## Identifiers

All ids are kebab-case (`sophie`, `town-diner`, `pregnancy`), unique within the
graph across Entities, fact-ids, and gun ids. Every cross-reference must
resolve to a declared id.

## Entity Types

| type | meaning |
|---|---|
| Character | a person (or sentient being) |
| Object | a thing that can be tracked, moved, planted |
| Location | a place; the only type usable in travel edges and Logistics.location |
| Faction | a group, family, institution, community |

## Core Edge Vocabulary

Relationship edges must come from this table, a declared genre module's
extensions, or the graph's own Local Vocabulary section. Nothing else.

| edge | meaning |
|---|---|
| trusts | extends confidence to |
| distrusts | withholds confidence from |
| loves | romantic love toward |
| desires | wants romantically/physically |
| resents | holds a grievance against |
| estranged_from | relationship ruptured |
| allied_with | cooperates with |
| protects | guards the safety/interest of |
| owes | is indebted to |
| employs | work/power relationship over |
| family_of | kin relationship |
| rivals | competes with |
| mentors | guides/teaches |
| fears | is afraid of |
| deceives | actively misleads |

## Trends

| trend | meaning |
|---|---|
| hardening | the edge is intensifying |
| softening | the edge is weakening toward change |
| stable | no current movement |
| volatile | oscillating, unpredictable |
| broken | the edge has ruptured (kept for history) |

## Table Schemas

- **Local Vocabulary**: `edge | description` — story-specific edge types, declared before use.
- **Entities**: `id | type | status | voice | note` — type from Entity Types; `voice` is optional (`female` / `male` / `-`), used by the SPE voice-mechanics layer.
- **Locations & Distances**: `from | to | time | mode` — both endpoints must be Location entities. Edges are bidirectional.
- **Relationships**: `from | edge | to | trend | since-ch | note`.
- **Knowledge States**: `fact-id | description | known-by | embargoed-from` — known-by is a comma list of `id (chN)`; embargoed-from a comma list of `id (until chN)`. Learning a fact before its embargo chapter is a violation.
- **Open Loops & Guns**: `id | planted-ch | expectation | must-fire-by | status` — status is `UNFIRED`, `FIRED ch-N`, or `DEFUSED ch-N`.
- **Physics State**: `ch | vector | subject | anchor | note` — one row per vector per committed chapter. Vectors are the SPE character vectors (`trauma`, `mask`, `desire`, `agency`, per-pair `charge`) and scene axes (`axis-internal`, `axis-relationship`, `axis-external`, `axis-temporal`), plus `intimacy-ladder` (subject = the pair, anchor = rung description) and `door-closed` (subject = who, anchor = short label) rows where the chapter moved them. When the SPE anchor catalog (`SPE/narrative_state/anchors/`) is installed, `anchor` values for the character vectors and scene axes must be catalog anchor IDs; `intimacy-ladder`/`door-closed` anchors are free-form.
- **Timeline**: `ch | story-time | elapsed | note`.
- **Logistics**: `ch | entity | location | condition | note` — location must be a Location entity id or `-`.
- **Private Beliefs (Ghost)**: `holder | privately-believes | about | source` — source is MANDATORY and points to a Ghost Draft layer (e.g., `Ghost Draft L3`). Only `/ghost-draft` writes this section.
- **Canon Commit Log**: list items of the form `- ch N: <plain-language deltas>`, strictly increasing N.

## Multi-Book Series Graphs

A graph may cover an entire series rather than a single book: the series is
ONE cumulative canon sequence (shared setting, cast, and threads survive
across books). Chapter numbers run series-continuously — Book 2 chapter 1
continues after Book 1's final unit — because canon is cumulative and the
Canon Commit Log requires strictly increasing chapters. A series graph MUST
carry a chapter-convention legend in its header block (blockquote under the
field table) stating each book's chapter range, and every Canon Commit Log
entry notes its `(B# chN)` mapping. New books continue the sequence from the
current high-water mark.

## Update Rules (Canon Commit)

Canon changes ONLY when a chapter reaches Final (via `/polish-chapter`,
`/npe-full-gauntlet`, or `/commit-canon`). A canon commit: extract the
chapter's deltas → update all current-state tables except `## Private Beliefs (Ghost)` → set `current-canon-chapter` →
append one Canon Commit Log entry → run the validator. Errors must be fixed
before the commit is complete (max 3 attempts, then stop and report).
Warnings are reported to the author verbatim and never silently "fixed".
Drafts and plans never touch the graph.

## Genre Modules

Modules live at `Blueprints/Genres/<id>-v<N>.md` (highest N is current). Each
module may add edge vocabulary via its `## Edge Vocabulary Extensions` table.
Using an edge from a module the story did not declare is a validation error
(crosstalk). New genres are new files; the core ontology never changes for a
genre.
