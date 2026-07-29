# STORY-GRAPH-PILOT-SPEC v0.1

**Project:** Story Graph System  
**Pilot corpus:** Series Book 3  
**Status:** Draft for review  
**Date:** July 21, 2026

---

## 1. Purpose

This pilot will determine whether a context-sensitive computational narrative graph can reliably represent and analyze one complete long-form fiction manuscript.

The pilot is intended to prove that the system can:

1. construct a source-grounded scene model;
2. distinguish canon from planning, analysis, and superseded material;
3. track chronology, character knowledge, belief, and deception;
4. trace objects, clues, evidence, promises, and payoffs;
5. assess character and relationship arc fulfillment;
6. answer structured questions with verifiable source support;
7. preserve revision context rather than flattening all documents into one supposed truth.

The pilot is not intended to establish the final production architecture, final database platform, complete series ontology, or fully automated literary judgment.

---

## 2. Pilot Book

Book 3 is selected as the provisional pilot because it has a comparatively small and well-organized supporting corpus while still containing enough narrative complexity to test romance, suspense, continuity, causality, and character development.

### 2.1 Governing source candidates

The initial pilot corpus will be drawn from:

- `series/SERIES_BIBLE.md`
- `series/books/book-3/BOOK_BIBLE.md`
- `series/books/book-3/phase-6-outline/beat-sheet.md`
- `series/books/book-3/phase-6-outline/chapter-breakdown.md`
- `series/books/book-3/phase-7-drafting/full-manuscript-v3.md`
- `series/books/book-3/editing-work/Edit_Report_SC3-v1.0.md`
- `series/books/book-3/editing-work/Wave1_ContinuityHawk_Fixes.md`

### 2.2 Secondary comparison sources

These may be used only for version comparison or diagnostic testing:

- `series/books/book-3/phase-7-drafting/full-manuscript-v1.md`
- `series/books/book-3/phase-7-drafting/full-manuscript-v2.md`
- `series/books/book-3/phase-8-editing/MANUSCRIPT.md`
- `series/books/book-3/phase-8-editing/EDITORIAL_LETTER.md`
- `series/books/book-3/phase-8-editing/QUALITY_REPORT.md`
- individual chapter files under `phase-7-drafting/chapters/`

### 2.3 Initially excluded material

The following are excluded from canon extraction during the first pass:

- market analysis;
- comparison titles;
- concept pitches;
- early discovery notes;
- character ideation documents;
- world-building notes not confirmed by later canon;
- scripts and utility files;
- `.DS_Store` and `__MACOSX` artifacts;
- editing commentary treated as though it were story fact;
- superseded manuscript versions treated as current canon.

Excluded files may later be used to test conflict detection and revision lineage.

---

## 3. Pilot Questions

The system must eventually answer questions from the following classes.

### 3.1 Canon and continuity

- Who are the principal characters?
- What facts about each principal character are explicitly established?
- Which locations, organizations, and recurring objects are canonically present?
- Which facts differ among the series bible, book bible, outline, and manuscript?
- Are names, ages, professions, injuries, family relationships, or histories inconsistent?
- Does any character appear in a location without a plausible transition?
- Does any physical or relational state change without explanation?

### 3.2 Chronology

- What is the chronological order of major events?
- What is the narrative presentation order?
- Which scenes contain flashbacks, memories, summaries, or embedded accounts?
- What dates, durations, deadlines, and travel intervals are established?
- Are any temporal relationships impossible or contradictory?

### 3.3 Character knowledge and belief

- What does each major character know at the beginning and end of each scene?
- What do they believe but not know?
- Which beliefs are false?
- Which facts are concealed from them?
- Which statements are lies, rumors, suspicions, or inferences?
- Does a character ever act on information they have not acquired?
- What does the reader know that the viewpoint character does not?

### 3.4 Causality and motivation

- What causes each major plot turn?
- Which events merely precede another event, and which actually cause or enable it?
- What motivates each decisive action?
- Are important decisions supported by prior knowledge, desire, fear, or pressure?
- Which scenes fail to create downstream consequences?

### 3.5 Objects, clues, and evidence

- What important objects, records, weapons, messages, or documents appear?
- Who possesses each item at each point?
- When and how does custody change?
- Which clues support the final reveal?
- When does each clue become available to the protagonist and reader?
- Which clues are misunderstood, concealed, fabricated, or ignored?

### 3.6 Promises and payoffs

- What narrative questions, threats, secrets, romantic tensions, and expectations are introduced?
- Where is each promise reinforced or escalated?
- Where is it partially fulfilled, reversed, deferred, or resolved?
- Which promises receive no payoff?
- Which payoffs lack sufficient setup?

### 3.7 Character and relationship arcs

- What initial states are established for the protagonists?
- What fears, needs, wounds, goals, and false beliefs drive them?
- Which events pressure those states?
- Which decisions demonstrate growth or regression?
- How do trust, intimacy, attraction, resentment, fear, and commitment change?
- Does the ending demonstrate the transformation promised by the opening?

---

## 4. Required Outputs

The pilot must produce the following six primary reports.

### 4.1 Canonical Fact Sheet

A verified record of:

- principal and supporting characters;
- aliases and name variants;
- professions and roles;
- family relationships;
- physical traits and injuries;
- locations;
- organizations;
- important objects;
- major backstory facts;
- unresolved conflicts among sources.

### 4.2 Scene Ledger

One record per scene containing:

- stable scene ID;
- book and chapter;
- scene order;
- story time;
- narrative order;
- location;
- viewpoint character;
- present characters;
- immediate goal;
- opposition;
- scene turn;
- outcome;
- major events;
- knowledge gained;
- belief changes;
- relationship changes;
- object transfers;
- promises introduced, advanced, or fulfilled;
- source span.

### 4.3 Character Knowledge Audit

For each major character and scene:

- known facts;
- believed facts;
- false beliefs;
- suspicions;
- lies told;
- facts concealed;
- source of knowledge;
- knowledge changes;
- impossible-knowledge warnings.

### 4.4 Object and Evidence Custody Report

For each important item:

- first appearance;
- physical description;
- possession history;
- location history;
- transfers;
- discoveries;
- uses;
- evidentiary significance;
- final disposition;
- custody gaps or contradictions.

### 4.5 Promise and Payoff Ledger

For each narrative promise:

- promise type;
- introduction;
- associated characters;
- expected outcome;
- escalation points;
- reversals;
- payoff;
- fulfillment status;
- strength of setup;
- source evidence.

### 4.6 Arc Fulfillment Report

For each major character and relationship:

- promised initial state;
- explicit and implied needs;
- pressure events;
- decisive choices;
- regressions;
- turning points;
- final state;
- evidence of transformation;
- promised versus accomplished comparison.

---

## 5. Source Authority Model

The pilot will use the following provisional trust hierarchy.

### Level 1: Final manuscript canon

The most recent author-approved full manuscript governs what occurs on the page.

### Level 2: Author-approved canonical reference

The current series bible and book bible govern facts not contradicted by the final manuscript.

### Level 3: Current structural plan

The final outline and chapter breakdown describe intended structure but do not override what the manuscript actually accomplishes.

### Level 4: Analytical interpretation

Editorial letters, continuity reports, and diagnostics are evidence about the manuscript, not canon within the story world.

### Level 5: Historical or speculative material

Earlier drafts, exploratory notes, market files, and concept documents are retained for lineage and comparison but are not current canon.

Authority may be assertion-specific. A book bible may govern an unmentioned birthday. The manuscript governs an event shown on page. An editorial report may correctly identify a contradiction but does not itself become story-world truth.

---

## 6. Canonical Assertion Record

The minimum unit of stored narrative knowledge will be an assertion.

```yaml
assertion_id:
subject:
predicate:
object:
assertion_type:
canonical_status:
valid_from:
valid_to:
story_time:
narrative_reveal:
viewpoint_context:
source_file:
source_span:
source_class:
authority_level:
confidence:
review_status:
supersedes:
contradicts:
notes:
```

### 6.1 Canonical status values

- `verified`
- `probable`
- `proposed`
- `character-belief`
- `false-belief`
- `lie`
- `rumor`
- `reader-inference`
- `superseded`
- `contradicted`
- `unresolved`

### 6.2 Review status values

- `unreviewed`
- `machine-accepted`
- `human-verified`
- `human-corrected`
- `rejected`
- `needs-adjudication`

No unreviewed interpretive assertion may be promoted automatically to verified canon.

---

## 7. Minimum Narrative Ontology

### 7.1 Core entity classes

- Series
- Book
- Chapter
- Scene
- Character
- Location
- Object
- Organization
- Event
- Secret
- Clue
- Evidence
- Promise
- NarrativeThread
- Assertion
- SourceSpan
- Revision

### 7.2 Core state classes

- CharacterState
- RelationshipState
- KnowledgeState
- BeliefState
- PossessionState
- LocationState
- ReaderKnowledgeState

### 7.3 Core relations

- `CONTAINS`
- `APPEARS_IN`
- `OCCURS_AT`
- `OCCURS_BEFORE`
- `OCCURS_DURING`
- `CAUSES`
- `ENABLES`
- `MOTIVATES`
- `PREVENTS`
- `REVEALS`
- `CONCEALS`
- `KNOWS`
- `BELIEVES`
- `FALSELY_BELIEVES`
- `SUSPECTS`
- `LIES_ABOUT`
- `DISCOVERS`
- `WITNESSES`
- `POSSESSES`
- `TRANSFERS_TO`
- `INTRODUCES`
- `ESCALATES`
- `FULFILLS`
- `RESOLVES`
- `CONTRADICTS`
- `SUPERSEDES`
- `SUPPORTED_BY`
- `FOCALIZED_THROUGH`
- `REVEALED_TO_READER_IN`

The ontology will remain deliberately narrow. New classes and relations must be justified by one or more pilot questions.

---

## 8. Context Model

The pilot must support the following contexts.

### 8.1 Scene context

- viewpoint;
- location;
- present characters;
- active goals;
- active threats;
- current emotional state;
- relevant prior events;
- objects present;
- open promises;
- reader advantage or disadvantage.

### 8.2 Character context

- known facts;
- beliefs;
- false beliefs;
- suspicions;
- goals;
- fears;
- secrets;
- obligations;
- relationship states;
- recently salient events.

### 8.3 Reader context

- explicitly revealed facts;
- implied facts;
- visible clues;
- likely suspicions;
- red herrings;
- unanswered questions;
- dramatic irony;
- withheld information.

### 8.4 Revision context

- source version;
- active or superseded status;
- draft-only facts;
- current canon;
- proposed future canon;
- published canon;
- conflict lineage.

---

## 9. Extraction Plan

### Pass 1: Structural extraction

Extract:

- book, chapter, and scene boundaries;
- viewpoint;
- characters;
- locations;
- organizations;
- named objects;
- explicit temporal markers;
- source spans.

### Pass 2: Event extraction

Extract:

- actions;
- decisions;
- discoveries;
- arrivals and departures;
- injuries;
- object transfers;
- explicit causal statements;
- state changes.

### Pass 3: Epistemic extraction

Extract or propose:

- knowledge;
- belief;
- suspicion;
- deception;
- concealment;
- misunderstanding;
- reader exposure.

### Pass 4: Narratological interpretation

Propose for review:

- scene function;
- narrative promise;
- escalation;
- reversal;
- payoff;
- character-state transition;
- relationship-state transition;
- thematic contribution.

Hard facts may be accepted automatically only when confidence is high and the evidence span is explicit. Interpretive claims remain reviewable.

---

## 10. Retrieval Plan

The pilot will combine:

1. lexical retrieval for exact names, objects, phrases, and identifiers;
2. vector retrieval for thematic, emotional, and paraphrased material;
3. graph traversal for precise relational, temporal, and multi-hop questions;
4. source-text verification before final answers are reported.

The pilot will not commit to a final graph database until the query and output requirements are validated.

---

## 11. Evaluation Plan

### 11.1 Gold question set

The pilot evaluation set will contain at least:

- 40 canon questions;
- 25 chronology questions;
- 25 character-knowledge questions;
- 20 object-custody questions;
- 20 causality questions;
- 20 promise/payoff questions;
- 15 contradiction tests;
- 15 revision-context tests.

### 11.2 Evaluation dimensions

Each answer will be scored for:

- correctness;
- completeness;
- source citation accuracy;
- temporal accuracy;
- perspective accuracy;
- confidence calibration;
- false contradiction rate;
- missed contradiction rate.

### 11.3 Initial targets

| Area | Target |
|---|---:|
| Character identification | 98% |
| Location identification | 98% |
| Scene segmentation | 95% |
| Explicit event extraction | 95% |
| Object custody | 95% |
| Timeline ordering | 95% |
| Character knowledge | 90% |
| Promise/payoff identification | 85% |
| Interpretive arc analysis | Human-reviewed |

---

## 12. Deliverables

The pilot will proceed through these artifacts:

1. `STORY-GRAPH-PILOT-SPEC-v0.1.md`
2. `CANON-AND-CONFLICT-DOCTRINE-v0.1.md`
3. `PILOT-QUERY-SET-v0.1.md`
4. `CORPUS-MANIFEST.csv`
5. `BOOK-3-SCENE-LEDGER-v0.1.csv`
6. `NARRATIVE-ONTOLOGY-v0.1.md`
7. `ASSERTION-CONTEXT-MODEL-v0.1.md`
8. `PILOT-EVALUATION-SET-v0.1.csv`
9. six initial analytical reports.

---

## 13. Non-Goals

The pilot will not yet:

- ingest the entire series;
- treat all source documents as equally authoritative;
- build a production GraphRAG platform;
- select a permanent database solely by fashion or vendor enthusiasm;
- create a global force-directed graph as the primary interface;
- automate final literary judgments;
- assign hard numerical emotion scores;
- allow an LLM to write directly into verified canon;
- formalize every theory of narrative structure.

---

## 14. Success Criterion

The pilot succeeds when, for one complete book, the system produces a source-grounded scene graph that can reliably answer continuity, chronology, knowledge-state, object-custody, promise/payoff, and arc questions at the agreed accuracy levels.

Only after this threshold is met will the project expand to cross-book series analysis.

---

## 15. Immediate Next Action

Create `CANON-AND-CONFLICT-DOCTRINE-v0.1.md`, then generate the Book 3 corpus manifest and identify the definitive manuscript version through evidence rather than filename optimism.
