# Story Graph Ontology v2

The TBox of the Story Graph canon system: what CAN exist in a Story Graph and
the rules that govern it. Each story's `Story-Graph.md` (the ABox) must
conform. The validator (`assets/story_graph.py`) enforces this document
mechanically.

**This supersedes `Story-Graph-Ontology-v1.md` for any graph whose header
declares `ontology-version | 2`.** Existing v1 graphs are unaffected and keep
using `Story-Graph-Ontology-v1.md` / `story_graph_v1.py` — v2 introduces a
genre-neutral core/module split, an authority + epistemic model, and
manuscript-verified evidence spans, none of which v1 graphs need to adopt.

## Header Block

Before the first `##` section, under the `# Story Graph: <Title>` line, a
table:

| field | value |
|---|---|
| ontology-version | 2 |
| modules | ordered list, comma-separated, or `none` |
| current-canon-chapter | integer; 0 = seeded, nothing committed |

- `ontology-version` must literally be `2` (checked by `check_header`).
- `modules` is the import statement: declaring `spe` pulls in the SPE module's
  additional required section (below). An undeclared module id is an error.
  `none` or an empty value means no modules are declared.
- `current-canon-chapter` must be a non-negative integer.

## Graph Sections

`Story-Graph.md` must contain, **in this exact order**, after the header
block, the 12 core sections plus any module-provided sections appended by a
declared module:

| # | Section | Notes |
|---|---|---|
| 1 | Local Vocabulary | story-specific edge types |
| 2 | Sources | authority registry (new in v2 — layer 1) |
| 3 | Entities | |
| 4 | Locations & Distances | |
| 5 | Relationships | edge vocab extendable by Local Vocabulary / modules |
| 6 | Propositions | holder-free claims (new in v2 — layer 3) |
| 7 | Epistemic States | replaces v1's Knowledge States; absorbs belief + reader |
| 8 | Open Loops & Setups | renamed from v1's "Open Loops & Guns" |
| 9 | Evidence | source spans (new in v2) |
| 10 | Timeline | |
| 11 | Logistics | gains a `span` column for condition changes |
| 12 | Canon Commit Log | append-only history |

Sections 1–11 are current-state tables (rows are edited as truth changes).
Section 12 is append-only history. Headers must never be renamed, reordered,
or removed within a graph's declared scope.

The validator rejects: any core section missing; any section present that is
neither core nor provided by a declared module; and — only once every core
section is present — core sections that are out of the canonical order shown
above.

### Module: `spe`

Declaring `spe` in the header `modules` field additionally **requires**:

| # | Section |
|---|---|
| 13 | Physics State |

A thriller/mystery author declares no module and never has to add Physics
State; a romance author using the SPE module declares `spe` and must add it
(its absence is a missing-required-section error).

**Physics State schema.** `ch | vector | subject | anchor | note` — one row per
vector that moved in a committed chapter. `ch` must be an integer. `vector` is
an SPE character vector (`trauma`, `mask`, `desire`, `agency`, per-pair
`charge`) or scene axis (`axis-internal`, `axis-relationship`, `axis-external`,
`axis-temporal`), plus the free-form vectors `intimacy-ladder` and
`door-closed`. For every non-free-form vector, `anchor` must be a catalog anchor
id from the host's SPE narrative-state catalog when it is supplied via
`--spe-dir` (`<spe-dir>/narrative_state/anchors/*.yaml`); an unknown anchor is an
**ERROR**. With no catalog supplied, the anchors are reported as unvalidated
free-form (a **WARN**). `intimacy-ladder` / `door-closed` anchors are always
free-form and never checked against the catalog.

A romance/NPE `ghost-draft` **Source type** is available in core
(see Controlled Vocabularies below) precisely so a private/ghost belief is
just an Epistemic State row whose span resolves to a Ghost Draft layer rather
than prose — there is no separate "Private Beliefs (Ghost)" section in v2.

## Identifiers

All ids are kebab-case (`^[a-z0-9]+(-[a-z0-9]+)*$`), unique within the graph
across: Entities `id`, Sources `source-id`, Propositions `prop-id`, Evidence
`span-id`, and Open Loops & Setups `id`. Every cross-reference must resolve to
a declared id (or, for Epistemic States `holder`, the reserved id `reader`).

## Controlled Vocabularies

These are enforced verbatim by the validator; using any other value is an
error.

| Vocabulary | Values |
|---|---|
| Source `type` | `manuscript`, `bible`, `outline`, `editorial`, `draft`, `ghost-draft` |
| Proposition `canon-status` | `true`, `false`, `undetermined`, `contested` |
| Epistemic State `mode` | `knows`, `believes`, `believes-false`, `suspects`, `embargoed-until` |
| Entity `type` | `Character`, `Object`, `Location`, `Faction` |
| Relationship `trend` | `hardening`, `softening`, `stable`, `volatile`, `broken` |
| Open Loop/Setup `status` | matches `^(UNFIRED|FIRED ch-\d+|DEFUSED ch-\d+)$` |
| Reserved Epistemic `holder` | `reader` (always valid even though not an Entity) |

`TRENDS` is defined by the validator but not currently cross-checked against
Relationships rows (no `trend`-vocabulary error is raised); it documents the
intended values for authors and is enforced structurally by convention, not
mechanically, in this slice.

## Table Schemas

Column lists below are exact — they are what `Story-Graph-TEMPLATE-v2.md`
ships and what the validator's row-parser expects as header cells (matched
case-insensitively).

- **Local Vocabulary**: `edge | description` — story-specific edge types,
  declared before use.
- **Sources**: `source-id | type | authority | note` — `type` from the
  Source-type vocabulary above; `authority` an integer rank (higher = more
  authoritative; see *Authority Model* below).
- **Entities**: `id | type | status | voice | note` — `type` from the Entity
  Types vocabulary; `voice` optional (`female` / `male` / `-`).
- **Locations & Distances**: `from | to | time | mode` — both endpoints must
  be `Location` entities.
- **Relationships**: `from | edge | to | trend | since-ch | span | note` — a
  `span` column (optional; recommended when an edge forms or breaks) was
  added in v2.
- **Propositions**: `prop-id | statement | canon-status | governing-source |
  span` — `canon-status` from the vocabulary above; `governing-source` a
  `source-id`; `span` a `span-id` (required when `canon-status` is `true` or
  `false`; see *Evidence Span Rules*).
- **Epistemic States**: `prop-id | holder | mode | since-ch | span` —
  `prop-id` must resolve to a declared Proposition; `holder` an Entity id or
  the reserved id `reader`; `mode` from the vocabulary above; `span` required
  for `knows` / `believes` / `believes-false` / `suspects` (not for
  `embargoed-until`).
  An optional **`until-ch`** column closes a stance. Without it a stance runs to
  the end of the book, so a belief that is later corrected cannot be stated:
  "Jonah believed it false, then learned better in ch20" had to be recorded as
  two rows that then read as a contradiction. That is an arc, not an error, and
  warning about it suppressed the most valuable mode — a manuscript can reach
  173 `knows` rows and 6 `believes-false` purely because the informative mode was
  the one that complained. `until-ch` must be greater than `since-ch`, and the
  contradiction check compares windows rather than modes: disjoint stances pass
  silently, only a real overlap is flagged. Dramatic irony becomes computable
  from it — the reader knowing a claim while a holder is `believes-false` over an
  overlapping window (`story_graph.py irony`). The column is optional and tables
  are parsed by column name, so a graph that omits it is unaffected and every
  stance in it is open.
- **Open Loops & Setups**: `id | planted-ch | expectation | must-fire-by |
  status | span` — `status` matches the setup-status regex; `span` always
  required (see *Evidence Span Rules*).
- **Evidence**: `span-id | source-id | locator | quote | note` —
  `source-id` must resolve to a declared Source; `locator` is a chapter id
  (`ch3`) for a `manuscript` source, or a heading/anchor for other source
  types; `quote` a verbatim substring, mandatory when `source-id` resolves to
  a `manuscript` source.
- **Timeline**: `ch | story-time | elapsed | note`.
- **Logistics**: `ch | entity | location | condition | span | note` —
  `entity` must be a declared Entity id; `location` must be `-` or a
  `Location` entity id; `span` required whenever `condition` records a change
  (non-empty and not `-`).
- **Canon Commit Log**: list items of the form `- ch N: <plain-language
  deltas>`; `N` must strictly increase entry to entry (a regression is an
  error).
- **Physics State** (`spe` module only): `ch | vector | subject | anchor |
  note` — carried forward unchanged from the v1 ontology; row-level content is
  not yet validated by the v2 validator (see *Module: spe* above).

## Authority Model (layer 1)

Authority is **assertion-specific**: the manuscript governs on-page events,
the bible governs unstated facts, an editorial report flags but never
asserts. This is expressed by each Proposition naming its own
`governing-source` rather than by a single global truth-order.

The validator's `check_authority` enforces, mechanically, today:

1. **Resolution.** A Proposition's `governing-source` must name a declared
   `source-id` — a dangling reference is an **ERROR**.
2. **Editorial bar.** A source whose `type` is `editorial` may be referenced
   elsewhere, but **cannot be a `governing-source`** — using one is an
   **ERROR** (`"editorial source '<id>' cannot be a governing-source (it
   flags, never asserts)"`), because an editorial report flags a concern, it
   does not assert canon.

`authority` (the integer rank on each Source) is read and stored by the
validator but is **not yet cross-checked as an inversion sanity rail** in this
slice — the design intent (a low-rank governing-source WARNs when a
higher-rank source asserts a conflicting value) is recorded here as the
target behavior for a follow-on layer (layer 4, continuity audit), not as
something `story_graph.py` currently checks. Authoring a graph with an
apparent authority inversion today produces no validator WARN; only the two
ERROR conditions above are live.

## Evidence Span Rules (D3)

**Evidence** is its own core section: `span-id | source-id | locator | quote
| note`. `span-id`s are unique, kebab-case, and reused across any load-bearing
row via a `span` column (space/comma-separated list of `span-id`s; the literal
token `provisional` in a `span` cell is stripped and does not count as an id).

Load-bearing rows and whether the validator requires a `span`:

| Row | Span required? (as implemented) |
|---|---|
| Epistemic State `knows` / `believes` / `believes-false` / `suspects` | **yes** (holder may be `reader`) |
| Epistemic State `embargoed-until` | no — it is a constraint, not an on-page fact |
| Proposition `canon-status` `true` / `false` | **yes** |
| Open Loop / Setup (any status) | **yes**, unconditionally |
| Logistics — `condition` records a change (non-empty, not `-`) | **yes** |
| Relationships | not enforced by the validator (recommended, not required) |
| Physics State (`spe` module) | not applicable — content unvalidated this slice |

A load-bearing row with no `span` is an **ERROR**
(`"load-bearing row has no evidence span (mark 'provisional' if intended)"`)
**unless** the row is marked **provisional** — `is_provisional` treats a row
as provisional if the word `provisional` (any case) appears in *any* of its
cell values — in which case it is a **WARN**
(`"provisional — no evidence span, claim is unverified"`) instead. A `span`
value naming an id that is not a declared Evidence `span-id` is always an
**ERROR**, provisional or not.

**Anti-invention / strictness tiers (graph-vs-source verification,
`verify_spans`).** For every Evidence row whose `source-id` resolves to a
`manuscript` source:

- If `--chapters-dir` was not passed, the check **degrades to WARN**
  (`"could not verify manuscript quote (no --chapters-dir)"`) — parsing and
  the rest of validation still run.
- If `--chapters-dir` was passed but no matching chapter file is found (the
  validator tries `<chapters_dir>/<locator>.md`, and if `locator` matches
  `ch\d+`, also the zero-padded `ch<NN>.md`), it **WARNs**
  (`"could not verify — chapter file for '<locator>' not found"`).
- If the chapter file is found and the `quote` is **not** a substring of it,
  this is a hard **ERROR**
  (`"quote not found in <file> — graph-vs-source mismatch"`).

A `bible` / `outline` / `draft` / `ghost-draft` source's Evidence rows are
never graph-vs-source verified (only `manuscript` sources are); a
`manuscript` Evidence row with an empty `quote` is already an ERROR from
`check_evidence` and is skipped by `verify_spans` to avoid a duplicate report.
A reverse-engineered or not-yet-on-page fact should be marked **provisional**
rather than backed by a fabricated quote; an unsupported load-bearing row that
is not marked provisional is an ERROR, never silently accepted.

## Proposition Dependencies (optional)

A Proposition may carry an optional `depends-on` column: a space- or comma-separated list
of prop-ids this claim needs in order to be true. Read it as **"this needs that"** — the
Purge Protocol fires because the Scrolls left containment, so the Purge claim depends on
the discovery claim.

The column is **optional and backward compatible**: every table here is parsed by column
NAME, so a graph written before this existed keeps validating unchanged and scores exactly
as it did. No version bump, no migration.

It exists because dependency is the difference between a claim being *popular* and being
*load-bearing*. Ranking by holders alone made a foundational claim nobody had an opinion
about indistinguishable from an inert one — 49 of 122 propositions in a real graph scored
zero. `blast_radius` walks these edges transitively, so a claim underpinning a chain
outranks a claim with more believers.

Validated: every id must resolve to a declared proposition, a claim may not depend on
itself, and the edges must not form a cycle — while a cycle exists, "what rests on this"
has no answer.

## Multi-Book Series Graphs

Carried forward unchanged from v1: a graph may cover an entire series as one
cumulative canon sequence, with series-continuous chapter numbering and a
chapter-convention legend in the header block. See
`Story-Graph-Ontology-v1.md` § *Multi-Book Series Graphs* for the full
mechanism — v2 does not change it.

**Legend format** (v2 makes the previously-unspecified shape concrete, because
the validator now reads it). One blockquote line per book, in the header above
the first `##` section:

```
> B1 ch1-30 — series/books/book-1/phase-7-drafting/chapters
> B2 ch31-50 — series/books/book-2/phase-7-drafting/chapters
```

The label is free text; the range and the path are what the tool uses, and the
path is relative to the graph file. Ranges must ascend and must not overlap,
and each must point at a real directory — a legend that lies sends the quote
checker to the wrong book, which is worse than no legend at all.

Chapters are addressed by their SERIES number: with the legend above, `ch31`
is Book 2's chapter 1. `validate` resolves each Evidence locator through the
legend, so a series graph needs no `--chapters-dir`, and a quote cited at a
Book 2 locator cannot be satisfied by prose that only exists in Book 1.

A Canon Commit Log carrying `(B# chN)` mappings without a legend is an ERROR:
it declares itself a series graph while making its own evidence unverifiable.

## Update Rules (Canon Commit)

Canon changes only when a chapter reaches Final. A canon commit: extract the
chapter's deltas → update all current-state tables (Entities, Relationships,
Propositions, Epistemic States, Open Loops & Setups, Timeline, Logistics, and
Physics State under `spe`) → set `current-canon-chapter` → append one Canon
Commit Log entry (`- ch N: <deltas>`, strictly increasing `N`) → run the
validator. ERRORs must be fixed before the commit is complete (max 3 attempts,
then stop and report); WARNs are reported verbatim and never silently
"fixed". Drafts and plans never touch the graph.

## The `compile` Projection

`story_graph.py compile <graph> --out <db> [--chapters-dir …]` runs `validate`
first and **refuses to compile a graph with any ERRORs**
(`"refusing to compile: fix validation ERRORs first"`, nothing written). If
validation is clean, it lazily imports `story_graph_kuzu` (erroring once,
cleanly, with `"compile requires the 'kuzu' package (pip install kuzu);
nothing was written"` if `kuzu` is not installed) and materializes the parsed
graph into a Kùzu property-graph database at `--out`. The source `.md` file
stays the source of truth; the database is a derived, rebuildable projection
— nobody hand-edits it.

**Node tables** (as created by `story_graph_kuzu.NODE_DDL`):

| Node table | Columns |
|---|---|
| `Entity` | `id` (PK), `type`, `status`, `voice`, `note` |
| `Proposition` | `id` (PK), `statement`, `canon_status` |
| `Source` | `id` (PK), `type`, `authority` (INT64), `note` |
| `Evidence` | `id` (PK), `locator`, `quote`, `note` |
| `OpenLoop` | `id` (PK), `planted_ch` (INT64), `expectation`, `must_fire_by`, `status` |
| `Holder` | `id` (PK) — one node per distinct Epistemic-State `holder`, including `reader` |

**Rel tables** (as created by `story_graph_kuzu.REL_DDL`):

| Rel table | Shape | Properties |
|---|---|---|
| `RELATES` | `(Entity)->(Entity)` | `edge`, `trend`, `since_ch` |
| `EPISTEMIC` | `(Holder)->(Proposition)` | `mode`, `since_ch`, `span_ids` (the row's `span` cell, as text) |
| `GOVERNED_BY` | `(Proposition)->(Source)` | — (created only when the Proposition has a `governing-source`) |
| `EVIDENCED_BY` | `(Evidence)->(Source)` | — (created only when the Evidence row has a `source-id`) |
| `SUPPORTS` | `(Evidence)->(Proposition \| OpenLoop)` | — (materialized from load-bearing `span` columns so a claim's evidence is a direct traversal) |

**Current scope of the loader.** Only `Entities`, `Sources`, `Evidence`,
`Propositions`, `Open Loops & Setups`, `Epistemic States`, and `Relationships`
rows are materialized. `Locations & Distances`, `Timeline`, and `Logistics`
rows are parsed by `parse_graph` but **not yet loaded** into the compiled
database in this foundation slice (no `Chapter`, `TRAVELS`, or `LOCATED`
tables exist yet) — that is deferred to a follow-on slice. `RELATES` does not
currently carry the Relationships row's `span` cell as a property, even though
the source table has one. Evidence↔Proposition/OpenLoop attachment in this
slice runs through `EPISTEMIC.span_ids` and `GOVERNED_BY`/`EVIDENCED_BY`
rather than a dedicated `SUPPORTS(Evidence)->(node)` edge.

## Validator Command Reference

```
python3 story_graph.py validate <graph> [--chapters-dir <dir>] [--spe-dir <dir>] [--ontology <path>] [--genres-dir <dir>]
python3 story_graph.py compile  <graph> --out <db> [--chapters-dir <dir>] [--ontology <path>]
```

`validate` is stdlib-only (never imports `kuzu`); `compile` needs `pip
install kuzu`. `--ontology`, `--genres-dir`, and `--spe-dir` are accepted on
the CLI for surface parity with the rest of the skill but are not yet read by
any v2 check — only `--chapters-dir` currently changes validator behavior (it
gates graph-vs-source manuscript verification, per *Evidence Span Rules*
above). Exit code `0` = no ERRORs, `1` = any ERROR; WARNs never change the
exit code. Output is `ERROR: …` / `WARN: …` lines followed by
`RESULT: N error(s), M warning(s)`.
