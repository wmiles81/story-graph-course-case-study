# BOOK 3 PILOT-SLICE ASSESSMENT v0.1

**Project:** Story Graph System  
**Pilot scope:** Book 3, Chapters 1–3  
**Status:** Scale-readiness assessment  
**Date:** July 21, 2026

---

## 1. Executive Decision

The Chapters 1–3 pilot slice is **ready to scale cautiously to the full Book 3 manuscript**, but not by simply repeating the current process scene by scene without refinement.

The model has proven that it can represent and query:

- source authority and revision context;
- scene segmentation;
- canonical facts;
- character knowledge and belief;
- reader knowledge;
- dramatic irony;
- suspense asymmetry;
- promises and payoffs;
- object and evidence custody;
- qualitative arc movement;
- analytical claims kept separate from canon.

That is enough to justify expansion.

However, the pilot also exposed several issues that must be addressed before scaling to all 30 chapters:

1. scene segmentation should be validated in batches;
2. source quotes need deterministic extraction and spot-checking;
3. character-context snapshots need a repeatable update method;
4. promise/payoff records need lifecycle rules to prevent duplication;
5. object custody requires interval handling rather than isolated events;
6. analytical fields need controlled confidence and review states;
7. a lightweight query layer is now warranted;
8. the current CSV model needs a stable ID registry.

The conclusion is therefore:

> **Proceed to full-book expansion using a staged, batch-validated pipeline. Do not yet move to a production graph database.**

---

## 2. Pilot Artifacts Completed

The first pilot slice produced the following governing and analytical artifacts.

### 2.1 Governance and planning

- `STORY-GRAPH-PILOT-SPEC-v0.1.md`
- `CANON-AND-CONFLICT-DOCTRINE-v0.1.md`
- `PILOT-QUERY-SET-v0.1.md`
- `CORPUS-MANIFEST-BOOK-3-v0.1.csv`
- `BOOK-3-CORPUS-MANIFEST-FINDINGS-v0.1.md`

### 2.2 Manuscript authority and revision

- `BOOK-3-MANUSCRIPT-AUTHORITY-ASSESSMENT-v0.1.md`
- `BOOK-3-MANUSCRIPT-CHAPTER-DIFF-v0.1.csv`
- revision diff files for v1 → v2 → v3 → Phase 8

### 2.3 Narrative structure

- `BOOK-3-SCENE-LEDGER-v0.1.csv`
- `BOOK-3-SCENE-LEDGER-BUILD-REPORT-v0.1.md`
- `BOOK-3-SCENE-LEDGER-CH01-03-VALIDATED-v0.1.csv`

### 2.4 Ontology and assertion model

- `NARRATIVE-ONTOLOGY-v0.1.md`
- `ASSERTION-CONTEXT-MODEL-v0.1.md`
- `BOOK-3-PROPOSITIONS-CH01-03-v0.1.csv`
- `BOOK-3-ASSERTIONS-CH01-03-v0.1.csv`
- `BOOK-3-ASSERTIONS-CH01-03-QUOTED-v0.2.csv`
- `BOOK-3-SCENE-CONTEXTS-CH01-03-v0.1.csv`

### 2.5 Context, suspense, promises, custody, and arcs

- `BOOK-3-CHARACTER-CONTEXTS-CH01-03-v0.1.csv`
- `BOOK-3-KNOWLEDGE-PROGRESSION-TESTS-CH01-03-v0.1.csv`
- `BOOK-3-READER-CONTEXTS-CH01-03-v0.1.csv`
- `BOOK-3-SUSPENSE-ASYMMETRY-MAP-CH01-03-v0.1.csv`
- `BOOK-3-PROMISE-PAYOFF-LEDGER-CH01-03-v0.1.csv`
- `BOOK-3-OBJECT-EVIDENCE-CUSTODY-CH01-03-v0.1.csv`
- `BOOK-3-ARC-STATE-BASELINE-CH01-03-v0.1.csv`

### 2.6 Query and evaluation

- `BOOK-3-PILOT-QUERY-RESULTS-CH01-03-v0.1.csv`
- `BOOK-3-PILOT-QUERY-TEST-REPORT-v0.1.md`
- supporting test files for knowledge, promise/payoff, custody, and arcs.

---

## 3. What the Pilot Proved

## 3.1 The ontology is sufficient for the current scope

The ontology handled the first 15 scenes without requiring emergency expansion.

It successfully represented:

- Characters
- Scenes
- Locations
- Objects
- Events
- KnowledgeState
- BeliefState
- RelationshipState
- PossessionState
- Secret
- Clue
- NarrativePromise
- Payoff
- NarrativeThread
- Revision
- Assertion
- SourceSpan

No new core class is required before expansion.

Possible future refinements, such as treating the library as an agent, should wait until later chapters prove that location-level modeling is insufficient.

---

## 3.2 Context graphs provide genuine analytical value

The pilot showed that context modeling is not decorative metadata.

It enabled the system to distinguish:

- what Jonah knows;
- what Margot knows;
- what Jonah believes;
- what Margot conceals;
- what the reader knows;
- what remains unknown to everyone;
- what is canon;
- what is analytical interpretation.

This is the central success of the pilot.

A flat graph could store that the Scrolls are missing. The context model can additionally store:

- when Margot knows;
- when Jonah knows;
- when the reader knows;
- who still does not know;
- whether current custody is known;
- which revision establishes the fact.

That is the difference between a graph of facts and a graph of story state.

---

## 3.3 The CSV model is adequate for the pilot stage

The first eight pilot queries were answered directly from CSV records.

The system did not need Neo4j, RDF, SPARQL, or a GraphRAG framework to prove the model.

This is important because it means the conceptual model can be tested independently of infrastructure.

The current data volume for one book remains manageable in:

- CSV;
- Markdown;
- Python;
- lightweight indexing.

A graph database may become useful later for multi-hop and series-level queries, but it is not yet required.

---

## 3.4 The model prevents common fiction-analysis errors

The pilot correctly avoided:

- treating Jonah's mate recognition as objective canon;
- inventing a possessor for the missing Scrolls;
- treating reader knowledge as character knowledge;
- treating analytical cooperation claims as verified fact;
- treating entering B2 as fulfillment of reaching B4;
- treating outline intention as manuscript accomplishment;
- flattening secrecy and ignorance into contradiction.

These are exactly the failure modes a generic knowledge graph would be prone to.

---

## 3.5 Qualitative arc states are sufficient

The pilot did not require numerical trust or attraction scores.

Qualitative state descriptions plus concrete behavioral evidence were enough to track:

- Jonah's movement from authority to partnership;
- Margot's movement from secrecy toward reliance;
- relationship progression from professional distance to mutual rescue and voluntary closeness.

Numeric scoring should remain deferred until a real analytical need appears.

---

## 4. What the Pilot Did Not Yet Prove

The pilot does not yet establish that the system can reliably handle:

- the entire 30-chapter manuscript;
- later-stage reversals and revelations;
- multiple suspects and red herrings;
- full causal chains;
- long-distance promise/payoff tracking;
- injury persistence over many chapters;
- cross-book continuity;
- contradictory backstory across multiple books;
- final arc fulfillment;
- series-level deferred promises;
- large-scale automated extraction accuracy;
- ontology migration;
- graph-database performance.

The first three chapters are structurally rich, but they are still an opening sample. Openings introduce. Middles complicate. Endings expose every lazy assumption made earlier and demand payment with interest.

---

## 5. Required Changes Before Full-Book Expansion

## 5.1 Stable entity registry

Create:

`BOOK-3-ENTITY-REGISTRY-v0.1.csv`

Required fields:

```text
entity_id
entity_type
canonical_name
aliases
first_appearance
source_document
review_status
notes
```

This prevents duplicate entities and name drift during later extraction.

---

## 5.2 Stable proposition registry

The proposition list must become append-only and normalized.

Create:

`BOOK-3-PROPOSITION-REGISTRY-v0.1.csv`

Rules:

- one proposition ID per normalized claim;
- no duplicate paraphrases;
- contradictions represented as separate propositions;
- proposition text independent of subject knowledge state.

---

## 5.3 Batch scene validation

Do not validate all remaining 27 chapters in one pass.

Recommended batches:

- Chapters 4–6
- Chapters 7–9
- Chapters 10–12
- Chapters 13–15
- Chapters 16–18
- Chapters 19–21
- Chapters 22–24
- Chapters 25–27
- Chapters 28–30

Each batch should be reviewed before the next begins.

This creates checkpoints for:

- ontology drift;
- scene segmentation errors;
- entity duplication;
- promise proliferation;
- context-state inconsistency.

---

## 5.4 Deterministic evidence locators

Every assertion should receive:

- source file;
- chapter;
- scene;
- paragraph index;
- sentence index;
- compact source quote;
- source hash.

Automatic quote selection should be spot-checked.

The current quote extraction is useful but not yet reliable enough to serve as final evidence without review.

---

## 5.5 Interval-based state handling

Current records often use only `valid_from_scene`.

Full-book scaling requires `valid_to_scene` or explicit termination events for:

- knowledge;
- belief;
- possession;
- injury;
- relationship state;
- location;
- promises;
- concealment.

Otherwise old states will linger forever like guests who missed several social cues.

---

## 5.6 Promise lifecycle controls

Each promise should support:

- introduction;
- reinforcement;
- escalation;
- partial payoff;
- reversal;
- full payoff;
- deferral;
- abandonment;
- supersession.

Duplicate promise records should be merged into one lifecycle.

The system should flag:

- no activity for a configured scene interval;
- payoff without setup;
- promise without resolution;
- series-level deferral without explicit scope.

---

## 5.7 Context snapshot cadence

Character and reader contexts should not necessarily be materialized after every scene.

Recommended cadence:

- every chapter end;
- every major reveal;
- every major relationship turn;
- every custody change;
- every false-belief correction;
- every climax-stage transition.

This balances analytical usefulness against record explosion.

---

## 5.8 Confidence and review discipline

Use:

- `high`
- `medium`
- `low`

Review states:

- `machine-proposed`
- `human-verified`
- `human-corrected`
- `needs-adjudication`
- `rejected`

Interpretive fields should default to `machine-proposed` or `human-curated`, never `verified canon`.

---

## 5.9 Query harness

Create a small Python or notebook query harness able to answer:

- scene lookup;
- knowledge-at-scene;
- object custody;
- promise lifecycle;
- arc transition;
- reader asymmetry;
- contradiction lookup.

This remains simpler and more testable than prematurely adopting a graph database.

---

## 6. Scale Plan

## Phase A: Prepare registries

Create:

1. `BOOK-3-ENTITY-REGISTRY-v0.1.csv`
2. `BOOK-3-PROPOSITION-REGISTRY-v0.1.csv`
3. `BOOK-3-RELATION-VOCABULARY-v0.1.csv`
4. `BOOK-3-REVISION-REGISTRY-v0.1.csv`

---

## Phase B: Validate Chapters 4–6

For the next batch:

- validate scene boundaries;
- populate scene ledger;
- add entities;
- add propositions;
- add assertions;
- update character contexts;
- update reader context;
- update promises;
- update custody;
- update arc states;
- run batch queries.

---

## Phase C: Review ontology drift

After Chapter 6, ask:

- Did any new entity class appear?
- Did any relation prove inadequate?
- Did any state require a new interval rule?
- Did any query fail?
- Did any record type become redundant?

Only then revise ontology v0.2.

---

## Phase D: Continue in three-chapter batches

Repeat through Chapter 30.

At the end of each act or major structural region, generate:

- continuity report;
- knowledge audit;
- promise/payoff report;
- custody report;
- arc report;
- suspense asymmetry report.

---

## Phase E: Full-book synthesis

After all chapters are validated:

1. consolidate duplicate propositions;
2. close state intervals;
3. resolve promise statuses;
4. build final knowledge timelines;
5. build final custody chains;
6. compare promised versus accomplished arcs;
7. compare manuscript against outline and bibles;
8. run the full pilot query set;
9. calculate accuracy against a gold sample;
10. decide whether to adopt a graph database.

---

## 7. Database Decision Gate

Do not select the permanent graph store until one of these conditions is met:

- multi-hop queries become awkward in CSV;
- series-level entity merging becomes expensive;
- path analysis becomes necessary;
- graph traversal becomes a performance bottleneck;
- incremental updates require formal graph operations;
- visualization needs exceed current reporting.

Likely future candidates:

- Kùzu for embedded local graph work;
- Neo4j for mature property-graph tooling;
- PostgreSQL with relational and vector support;
- RDF/OWL only if formal interoperability or reasoning proves necessary.

The pilot currently favors a property-graph-style model, but implementation remains open.

---

## 8. Readiness Scorecard

| Area | Status | Readiness |
|---|---|---:|
| Source authority | Proven | High |
| Revision handling | Proven in sample | High |
| Scene segmentation | Proven in sample | Medium-high |
| Canon extraction | Proven in sample | High |
| Knowledge and belief | Proven in sample | High |
| Reader context | Proven in sample | High |
| Suspense asymmetry | Proven in sample | High |
| Promise/payoff | Proven in sample | Medium-high |
| Object custody | Proven in sample | High |
| Arc modeling | Proven in sample | Medium-high |
| Evidence quoting | Partially proven | Medium |
| Automated extraction | Not proven at scale | Low |
| Full-book continuity | Not yet tested | Low |
| Series continuity | Not yet tested | Low |
| Database need | Not established | Deferred |

---

## 9. Final Recommendation

Proceed with full-book expansion.

Use a three-chapter batch cycle with explicit review checkpoints.

Before Chapters 4–6, create the four registries:

1. entity;
2. proposition;
3. relation vocabulary;
4. revision.

Do not yet adopt a graph database.

The pilot model is conceptually sound. The next risk is no longer architecture. It is operational consistency across hundreds of records, which is where otherwise elegant systems go to die under a pile of slightly different spellings.

---

## 10. Immediate Next Action

Create:

`BOOK-3-ENTITY-REGISTRY-v0.1.csv`

Seed it with all entities identified in Chapters 1–3, including:

- Jonah Harrow;
- Margot Vance;
- Grishka;
- Aleksei Petrov;
- Marcy;
- Meredith;
- Snowfall Creek Public Library;
- The Howling Moon;
- Preservation Section;
- Deep Stacks;
- Level B1;
- Level B2;
- Founding Scrolls;
- grandmother's journal;
- Deep Stacks key;
- flashlight;
- bibliovore;
- lexivore;
- unknown B2 entity.

Then create the proposition, relation, and revision registries before validating Chapters 4–6.
