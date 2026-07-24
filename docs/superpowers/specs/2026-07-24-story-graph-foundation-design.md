# Story Graph — Foundation Slice Design

**Date:** 2026-07-24
**Status:** Approved design; ready for implementation planning
**Proving manuscript:** `series/books/book-3`

## 1. Purpose

Evolve the existing `story-graph` skill into a tool that helps writers maintain
the structural state of their books. This spec covers the **foundation slice**
only — the first of several sequenced sub-projects. It establishes the data
model, the two mechanical tools that operate on it (verify and materialize), and
the storage architecture that later slices build on.

The tool remains a **portable Claude Code skill**: an authored, human-readable,
git-diffable source file (`Story-Graph.md`) plus a stdlib validator, with a
graph database added only as a derived, rebuildable projection.

## 2. How we got here (decisions log)

- **Two prior instantiations exist.** A heavyweight ChatGPT pipeline (CSV ledgers
  → SQLite → `app.py` operating system, evidence-hardened, bespoke to Book 3),
  archived in `docs/source-conversation/`, `data/`, `packages/`. And the
  lightweight `story-graph/` skill (single `Story-Graph.md`, stdlib validator,
  portable). We build on the **skill**.
- The target is a **convergence**: keep the portable single-file skill as the
  vessel, but pull the pipeline's *rigor layers* into it. All five rigor layers
  (authority, canon lifecycle, epistemic separation, continuity audit,
  revision-impact) are in the eventual tool.
- The work is **decomposed** into sequenced sub-projects. This spec is the
  **foundation**; the rest are follow-on slices (Section 9).
- **Storage:** a DBMS is worth having, but source-of-record and query-engine are
  **separated**. Text stays the authored source of truth; the database is a
  derived projection. Back end: **Kùzu** (embedded property graph, Cypher, no
  server), behind a pluggable loader interface.

## 3. Scope

**In (foundation):**
- Ontology **v2**: a genre-neutral **core** plus optional declared **modules**
  (Section 4).
- **Authority + epistemic model** — layers 1 and 3 (Section 5).
- **Evidence spans** — D3 (Section 6).
- **Upgraded validator** — now graph-vs-source (Section 7).
- **Kùzu compiler** — materialize the source into a property graph (Section 8).

**Out (sequenced follow-on slices, not this spec):**
- Query/report CLI (**C**) — the natural next slice.
- Canon lifecycle / ratification (layer **2**).
- Continuity audit (layer **4**).
- Revision-impact analysis (layer **5**).
- Scene-level segmentation (the deprioritized "trust the inference" work, **B**).
- Any app/UI (curiosity only; later).
- SQLite / Neo4j back ends (loader stays pluggable; only Kùzu is built now).

## 4. Ontology v2 — the core/module cut (layer A)

The header bumps `ontology-version` to `2` and gains a `modules:` declaration.
The structural change: sections become either **core-required** (every graph,
any genre) or **module-provided** (present only when the header declares that
module). The validator's required-section set becomes *core + declared modules*.

Because Book 3 has no `Story-Graph.md` yet, there is no migration burden. Per the
repository owner's versioning rule, the new schema ships beside v1:
`Story-Graph-Ontology-v2.md` and `Story-Graph-TEMPLATE-v2.md` (side-by-side);
`SKILL.md`, `story_graph.py`, and the `reference/` files are owned by fixed
call-chains and follow the shift-rename form (current content moves to
`*_v1.*` / `*-v1.*`, new content takes the unsuffixed name).

### Core sections (required, in order)

| # | Section | Change from v1 |
|---|---|---|
| 1 | Local Vocabulary | unchanged |
| 2 | Sources | **new** — authority registry (layer 1) |
| 3 | Entities | unchanged |
| 4 | Locations & Distances | unchanged |
| 5 | Relationships | unchanged structure; edge vocab extended by modules |
| 6 | Propositions | **new** — holder-free claims (layer 3) |
| 7 | Epistemic States | **replaces** Knowledge States; absorbs belief + reader (layer 3) |
| 8 | Open Loops & Setups | **renamed** from "Open Loops & Guns" (genre-neutral) |
| 9 | Evidence | **new** — source spans (D3) |
| 10 | Timeline | unchanged |
| 11 | Logistics | gains a `span` column for changes |
| 12 | Canon Commit Log | unchanged (layer 2 enriches later) |

### SPE module (present only when `modules:` includes `spe`)

Contributes:
- **Physics State** section (SPE vectors + anchor-catalog validation).
- Romance/NPE **edge-vocabulary extensions** for Relationships.
- A `ghost-draft` **Source type**, so a private/ghost belief is simply an
  Epistemic State row whose span resolves to a Ghost Draft layer rather than
  prose. There is **no** separate "Private Beliefs (Ghost)" section — the belief
  *concept* is universal and lives in core Epistemic States; only its
  Ghost-Draft *sourcing* is module-specific.

A thriller author declares no module and never sees Physics State; a romance
author declares `spe` and does.

## 5. Authority + epistemic model (layers 1 and 3)

### Epistemic separation (layer 3)

v1 conflated "what is true" with "who knows it," and exiled belief to a genre
section. v2 splits truth from stance and unifies knowledge, belief, and reader
awareness into **one holder-keyed table**.

**Propositions** — the claims themselves, holder-free:

```
| prop-id | statement | canon-status | governing-source | span |
```

- `canon-status ∈ {true, false, undetermined, contested}`.
- `governing-source` → a `source-id` (Section: Sources).
- `span` → a `span-id` establishing it (required for `true`/`false`; Section 6).

**Epistemic States** — who stands in what relation to each proposition:

```
| prop-id | holder | mode | since-ch | span |
```

- `holder` → an entity id **or the reserved id `reader`**.
- `mode ∈ {knows, believes, believes-false, suspects, embargoed-until}`.
- `span` → span-id(s) backing the claim (required except for `embargoed-until`).

Worked Book-3 example (proposition `jackson-alive`, "Jackson survived the fire",
`canon-status: true`):

| prop-id | holder | mode | since-ch | span |
|---|---|---|---|---|
| jackson-alive | jonah | believes-false | 3 | s-ch3-jonah |
| jackson-alive | margot | knows | 11 | s-ch11-margot |
| jackson-alive | reader | knows | 3 | s-ch3-reveal |

Dramatic irony falls out mechanically: the reader `knows` at ch3 while Jonah
`believes-false` and Margot does not learn until ch11. `embargoed-until` carries
v1's embargo check forward (no `knows` row may precede the embargo chapter).

### Authority model (layer 1)

Authority is **assertion-specific** — the manuscript governs on-page events, the
bible governs unstated facts, an editorial report flags but never asserts.

**Sources** — the registry:

```
| source-id | type | authority | note |
```

- `type ∈ {manuscript, bible, outline, editorial, draft, ghost-draft}`.
- `authority` = integer rank; **higher = more authoritative**.

Assertion-specificity is expressed by each proposition naming its own
`governing-source`. The rank is **not** a global truth-order; it is a **sanity
rail**: the validator WARNs when a proposition is governed by a low-rank source
while a higher-rank source asserts a conflicting value. Unstated facts create no
conflict (the manuscript simply does not speak), so the bible legitimately
governs them. An `editorial` source may be referenced but is **barred from being
a `governing-source`** (it flags, never asserts).

## 6. Evidence spans (D3)

Spans get their own core section — readable rows, reusable spans, and a clean
projection to the property graph (an Evidence node, `EVIDENCED_BY` /
`SUPPORTS` edges).

**Evidence**:

```
| span-id | source-id | locator | quote | note |
```

- `source-id` → the Sources registry (this is what ties a span to its authority
  and type).
- `locator` → for a `manuscript` source, the chapter file (`ch12`); for
  `bible`/`outline`/`ghost-draft`, a heading/anchor in that document.
- `quote` → a **verbatim substring** the validator locates in the referenced
  file. For manuscript sources it must appear or it is an **ERROR**.

Load-bearing rows carry a `span` column of one or more `span-id`s:

| Row | Span required? |
|---|---|
| Epistemic State `knows` / `believes-false` / `suspects` | **yes** (incl. `reader`) |
| Epistemic State `embargoed-until` | no (a constraint, not an on-page fact) |
| Proposition `canon-status` true/false | **yes** |
| Open Loop / Setup — planted / fired / defused | **yes** |
| Logistics — object location/condition **change** | **yes** |
| Relationships — edge forms / breaks | optional (recommended) |
| Physics State (SPE module) | n/a — sourced via SPE anchors |

**Anti-invention / strictness tiers.** A `manuscript` quote is hard-verified
(absent → ERROR). A `bible`/`outline`/`ghost-draft` quote is resolved but soft
(unresolved → WARN). A reverse-engineered or not-yet-on-page fact is allowed only
if marked **provisional**; a quote is never fabricated to satisfy a span, and an
unsupported load-bearing row that is not marked provisional is an ERROR.

## 7. Validator upgrade — `story_graph.py validate`

Keeps every existing v1 check (kebab ids and uniqueness across
Entities/prop-ids/span-ids/setup-ids, relationship edge vocab, embargo logic,
setup-status regex, commit-log monotonicity, coverage/geography warnings, SPE
anchors when the `spe` module and catalog are present). Adds:

1. **Modular required sections.** Required set = core + declared modules; Physics
   State required only under `spe`; section-order check updated for v2.
2. **Graph-vs-source verification (D3).** New input `--chapters-dir` (inferred
   from the target folder or a header field). For each Evidence row with a
   `manuscript` source, read `chNN.md` and assert the `quote` is a substring →
   **ERROR** if absent. If the chapters dir is absent, manuscript-span checks
   **degrade to WARN** (same opt-in pattern as today's `--spe-dir`). Parsing
   stays stdlib; this only reads text files.
3. **Authority checks (layer 1).** Every `source-id` / `governing-source`
   reference must resolve (dangling → ERROR). An `editorial` source used as a
   `governing-source` → ERROR. Authority inversion → WARN sanity rail (full
   conflict detection deferred to layer 4).
4. **Epistemic checks (layer 3).** `holder` is a declared entity or reserved
   `reader`; `mode` in vocabulary; embargo carried forward (a `knows` before
   `embargoed-until` → ERROR); a load-bearing row missing its `span` and not
   marked provisional → ERROR; `believes-false` vs. a prop's `canon-status`
   mismatch → WARN (kept soft; often legitimate).

Exit codes unchanged: `0` = no errors, `1` = errors; ERROR/WARN reported
verbatim; ERRORs fixed within the skill's existing 3-attempt loop, then stop and
report.

## 8. Kùzu compiler — `story_graph.py compile`

Source-of-record stays the text file; the database is a **derived, rebuildable
projection**. Nobody hand-edits it.

### Property-graph schema

**Node tables:** `Entity{id,type,status,voice,note}`,
`Proposition{id,statement,canon_status}`, `Source{id,type,authority,note}`,
`Evidence{id,locator,quote,note}`,
`OpenLoop{id,planted_ch,expectation,must_fire_by,status}`,
`Chapter{ch,story_time,elapsed}`. `reader` is a single reserved node. SPE-module
rows (Physics State) add their own tables only when declared.

**Rel tables:**
- `RELATES(Entity)-[edge,trend,since_ch,span_ids]->(Entity)` — one typed rel with
  `edge` as a property (mirrors the markdown; avoids a table per edge type);
  `span_ids` optional.
- `TRAVELS(Location)-[time,mode]-(Location)`.
- `EPISTEMIC(holder)-[mode,since_ch,span_ids]->(Proposition)`.
- `GOVERNED_BY(Proposition)->(Source)`.
- `EVIDENCED_BY(Evidence)->(Source)`.
- `LOCATED(Entity)-[ch,condition,span_ids]->(Location)`.

**Where evidence attaches.** A property graph cannot attach an edge to an edge,
so load-bearing *relationships* (EPISTEMIC, LOCATED, and optionally RELATES)
carry their supporting span-ids as a `span_ids` list **property** on the rel.
`SUPPORTS(Evidence)->(node)` edges are created only where the supported item is a
node — `Proposition` and `OpenLoop`. Either way the Evidence node exists and is
reachable; only the attachment mechanism differs by shape.

### Command

`story_graph.py compile <graph> --out <db> [--chapters-dir …]`: parse the source
(reusing the validator's parser), run `validate` first and **refuse to compile a
graph with ERRORs**, then create the core + declared-module tables and insert.
The result is what the C slice will query with Cypher.

**Dependency quarantine.** `kuzu` is used **only** by `compile`. Parsing and
`validate` stay stdlib-only; if `kuzu` is absent, `compile` says so once and
exits, and the rest of the skill is unaffected. This preserves the portable
validator while giving the graph engine where it matters.

## 9. Follow-on slices (not this spec)

Sequenced, each its own spec → plan → build:

1. **C — Query/report** (`story_graph.py query` / `report`): Cypher over the Kùzu
   projection; answers carry their evidence spans (receipts).
2. **Layer 2 — Canon lifecycle:** provisional → ratified → frozen, an author
   ratification step, and a versioned freeze, enriching the Commit Log.
3. **Layer 4 — Continuity audit:** mechanical continuity-candidate detection plus
   an adjudication record.
4. **Layer 5 — Revision-impact:** dependency traversal — "what breaks if I move
   ch12" — as Cypher over the projection.

## 10. Proof against Book 3

1. Hand-author a v2 `Story-Graph.md` over `ch01–03.md` with real quotes.
2. `validate --chapters-dir series/books/book-3/phase-7-drafting/chapters` must
   pass real spans and **ERROR on a deliberately wrong quote**.
3. `compile` must build a Kùzu db that answers two raw Cypher sanity checks: a
   dramatic-irony query (reader `knows` while a character `believes-false`) and
   overdue setups.

That exercises A, layers 1 + 3, D3, and the compiler on real prose.

## 11. Implementation constraints

- **Versioning (repo owner's rule).** Side-by-side for the schema
  (`Story-Graph-Ontology-v2.md`, `Story-Graph-TEMPLATE-v2.md`); shift-rename for
  fixed-call-chain files (`SKILL.md`, `story_graph.py`, `reference/*`): move the
  current content to its `_v1` / `-v1` slot, write new content at the unsuffixed
  name. Never overwrite; never destroy-and-rewrite a `Story-Graph.md`.
- **Stdlib boundary.** Parsing + `validate` import only the standard library.
  `kuzu` is confined to `compile`.
- **Portability.** The skill remains drop-in for any project; module
  directories (`--genres-dir`, `--spe-dir`) and `--chapters-dir` are opt-in and
  degrade gracefully when absent.
