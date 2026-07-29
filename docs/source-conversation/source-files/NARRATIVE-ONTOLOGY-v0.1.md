# NARRATIVE-ONTOLOGY v0.1

**Project:** Story Graph System  
**Pilot:** Series Book 3  
**Status:** Draft for review  
**Date:** July 21, 2026

---

## 1. Purpose

This ontology defines the minimum shared vocabulary required to represent and analyze long-form fiction for the Book 3 pilot.

It is intentionally narrow.

The ontology exists to support specific pilot questions concerning:

- canon;
- chronology;
- scene structure;
- character knowledge and belief;
- causality and motivation;
- objects, clues, and evidence;
- promises and payoffs;
- character and relationship arcs;
- reader context;
- revision and source conflict.

It is not intended to encode every narratological theory, emotional nuance, symbolic interpretation, or genre convention ever proposed by a committee with a whiteboard.

---

## 2. Design Principles

### 2.1 Query-driven design

A class or relation belongs in the ontology only if it supports one or more approved pilot questions.

### 2.2 Evidence-first representation

Every factual assertion must be traceable to a source file and source span.

### 2.3 Context-sensitive truth

The ontology must distinguish among:

- story-world fact;
- character knowledge;
- character belief;
- false belief;
- lie;
- rumor;
- suspicion;
- reader knowledge;
- reader inference;
- authorial intention;
- analytical interpretation;
- revision-state fact.

### 2.4 Time-aware state

Facts may be true only during particular intervals.

### 2.5 Version-aware canon

Facts may differ across drafts, editions, outlines, and bibles without being treated as one undifferentiated contradiction.

### 2.6 Conservative inference

The system may propose interpretations, but it must not promote them to verified canon without evidence and review.

---

# 3. Ontology Layers

The ontology is organized into six layers.

1. **Document layer**  
   Sources, spans, versions, revisions.

2. **Narrative structure layer**  
   Series, books, chapters, scenes, beats.

3. **Story-world layer**  
   Characters, locations, organizations, objects, events.

4. **Epistemic and contextual layer**  
   Knowledge, belief, deception, reader exposure.

5. **Narratological layer**  
   promises, payoffs, scene functions, arcs, themes.

6. **Governance layer**  
   assertions, authority, review, conflict, supersession.

---

# 4. Core Classes

## 4.1 Document and Provenance Classes

### SourceDocument

A file or document used as evidence.

Examples:

- manuscript;
- series bible;
- book bible;
- outline;
- editorial report;
- marketing package;
- earlier draft.

Required properties:

- `source_id`
- `path`
- `source_class`
- `version`
- `authority_level`
- `content_hash`
- `review_status`

---

### SourceSpan

A bounded region of a source document supporting an assertion.

Required properties:

- `span_id`
- `source_document`
- `start_locator`
- `end_locator`
- `quoted_text`
- `span_hash`

Possible locators:

- chapter;
- scene;
- paragraph;
- line range;
- character offsets.

---

### Revision

A defined manuscript or source state.

Required properties:

- `revision_id`
- `source_document`
- `version_label`
- `created_or_modified`
- `status`

Allowed statuses:

- `historical`
- `current-candidate`
- `author-verified`
- `superseded`
- `rejected`

---

### Edition

A published or formally released state of a work.

Required properties:

- `edition_id`
- `book`
- `publication_status`
- `publication_date`

---

## 4.2 Narrative Structure Classes

### Series

A set of related books sharing continuity, characters, world, or thematic structure.

---

### Book

A complete narrative work within or outside a series.

Required properties:

- `book_id`
- `title`
- `series_position`
- `status`

---

### Chapter

A named or numbered structural division of a book.

Required properties:

- `chapter_id`
- `book`
- `chapter_order`
- `heading`

---

### Scene

A bounded unit of narrative action or state change.

Required properties:

- `scene_id`
- `chapter`
- `scene_order`
- `source_span`
- `review_status`

Recommended properties:

- `story_time`
- `narrative_order`
- `pov_character`
- `location`
- `scene_function`
- `goal`
- `opposition`
- `turn`
- `outcome`

---

### Beat

A smaller functional unit within a scene.

Use only when scene-level representation proves insufficient.

Required properties:

- `beat_id`
- `scene`
- `beat_order`
- `beat_function`

---

### NarrativeThread

A continuing line of story development.

Examples:

- central suspense investigation;
- romantic trust arc;
- family conflict;
- institutional conspiracy.

Required properties:

- `thread_id`
- `thread_type`
- `status`

Allowed statuses:

- `open`
- `active`
- `dormant`
- `resolved`
- `deferred`
- `abandoned`

---

## 4.3 Story-World Classes

### Entity

Abstract superclass for identifiable story-world things.

Subclasses:

- Character
- Location
- Organization
- Object

---

### Character

A person or person-like agent in the story world.

Required properties:

- `character_id`
- `canonical_name`

Recommended properties:

- `aliases`
- `role`
- `profession`
- `physical_traits`
- `status`

Allowed statuses:

- `alive`
- `dead`
- `missing`
- `unknown`
- `not-applicable`

---

### CharacterRole

A narrative or social role.

Examples:

- protagonist;
- antagonist;
- love interest;
- ally;
- suspect;
- witness;
- victim;
- mentor;
- family member.

This class should not be confused with profession or occupation.

---

### Location

A physical or virtual place where events occur.

Examples:

- town;
- house;
- archive;
- office;
- vehicle;
- online space.

Recommended properties:

- `location_id`
- `canonical_name`
- `location_type`
- `contains_location`

---

### Organization

A structured group or institution.

Examples:

- sheriff’s office;
- library;
- corporation;
- family business;
- criminal organization.

Recommended properties:

- `organization_id`
- `canonical_name`
- `organization_type`

---

### Object

A persistent material or digital item.

Examples:

- ledger;
- weapon;
- key;
- letter;
- photograph;
- phone;
- file;
- recording.

Recommended properties:

- `object_id`
- `canonical_name`
- `object_type`
- `physical_description`

---

### Event

A bounded occurrence that changes story state.

Examples:

- discovery;
- confrontation;
- injury;
- transfer;
- confession;
- attack;
- kiss;
- arrest;
- death.

Required properties:

- `event_id`
- `event_type`
- `scene`
- `story_time`

---

### Action

An intentional act performed by a character.

Action is a subclass of Event.

Recommended properties:

- `actor`
- `target`
- `instrument`
- `intended_outcome`

---

### State

A condition holding during a period.

Subclasses:

- CharacterState
- RelationshipState
- PossessionState
- LocationState
- KnowledgeState
- BeliefState
- ReaderKnowledgeState

Required properties:

- `valid_from`
- `valid_to`
- `confidence`
- `source_span`

---

### CharacterState

A temporally bounded condition of a character.

Possible dimensions:

- physical condition;
- emotional condition;
- role;
- goal;
- fear;
- obligation;
- injury status;
- social status.

---

### Relationship

A persistent connection between two or more characters or entities.

Examples:

- romantic;
- familial;
- professional;
- adversarial;
- institutional.

---

### RelationshipState

The condition of a relationship during a particular interval.

Possible dimensions:

- trust;
- attraction;
- intimacy;
- resentment;
- fear;
- commitment;
- dependence;
- power balance;
- concealment.

Values should initially be qualitative:

- `absent`
- `low`
- `rising`
- `high`
- `fractured`
- `restored`
- `uncertain`

Numeric scoring is deferred.

---

### PossessionState

Records who possesses, controls, stores, or has access to an object during an interval.

Required properties:

- `object`
- `holder`
- `possession_type`
- `valid_from`
- `valid_to`

Allowed possession types:

- `physical-possession`
- `ownership`
- `custody`
- `storage`
- `access`
- `control`
- `unknown`

---

### LocationState

Records where a character or object is located during an interval.

---

# 5. Epistemic and Context Classes

## 5.1 Proposition

A normalized statement capable of being known, believed, denied, concealed, or inferred.

Examples:

- the signature was forged;
- Victoria destroyed the ledger;
- the sheriff is being watched.

A proposition is not automatically true.

---

## 5.2 Assertion

A source-backed claim about a proposition or relationship.

Required properties:

- `assertion_id`
- `subject`
- `predicate`
- `object`
- `assertion_type`
- `canonical_status`
- `source_span`
- `authority_level`
- `confidence`
- `review_status`

---

## 5.3 KnowledgeState

Records that a character knows a proposition during an interval.

Required properties:

- `knower`
- `proposition`
- `valid_from`
- `source_of_knowledge`
- `confidence`

Allowed knowledge sources:

- `witnessed`
- `told`
- `read`
- `overheard`
- `discovered`
- `inferred-and-confirmed`
- `remembered`
- `unknown`

---

## 5.4 BeliefState

Records that a character believes a proposition.

Required properties:

- `believer`
- `proposition`
- `belief_status`
- `valid_from`
- `valid_to`

Allowed belief statuses:

- `believes`
- `suspects`
- `doubts`
- `rejects`
- `false-belief`
- `uncertain`

---

## 5.5 Lie

A communicative act in which a character states a proposition believed false by the speaker.

Lie is modeled as an Event linked to:

- speaker;
- audience;
- proposition;
- scene;
- motive where known.

---

## 5.6 Concealment

An intentional act of withholding a proposition, object, or event.

Concealment does not require a spoken falsehood.

---

## 5.7 Rumor

A proposition transmitted socially without established verification.

---

## 5.8 ReaderKnowledgeState

Records what is explicitly available to the reader at a narrative point.

Required properties:

- `proposition`
- `revealed_in`
- `certainty_level`

Allowed certainty levels:

- `explicit`
- `strongly-implied`
- `weakly-implied`
- `ambiguous`

---

## 5.9 ReaderInference

A proposition a reasonable reader may infer from available evidence.

Reader inference must remain separate from explicit reader knowledge.

---

## 5.10 Context

A bounded interpretive frame.

Subclasses:

- SceneContext
- CharacterContext
- ReaderContext
- RevisionContext
- BookContext
- SeriesContext

---

### SceneContext

Contains the active state relevant to a scene:

- POV;
- location;
- present characters;
- active goals;
- threats;
- objects;
- known facts;
- false beliefs;
- relationship states;
- open promises;
- reader asymmetry.

---

### CharacterContext

Contains what is salient and available to one character at a defined point.

---

### ReaderContext

Contains what is available to the reader at a defined narrative position.

---

### RevisionContext

Defines the source version in which an assertion is valid.

---

# 6. Suspense, Evidence, and Revelation Classes

## 6.1 Secret

A proposition intentionally withheld from one or more characters or the reader.

Required properties:

- `secret_id`
- `proposition`
- `known_by`
- `concealed_from`
- `status`

Allowed statuses:

- `hidden`
- `partially-revealed`
- `revealed`
- `misunderstood`

---

## 6.2 Clue

A perceivable fact, object, statement, or event that supports an inference.

Required properties:

- `clue_id`
- `source_span`
- `supports_proposition`
- `first_available_to_reader`
- `first_available_to_character`

---

## 6.3 Evidence

A clue or object with explicit investigative or argumentative significance.

Evidence may support or weaken a proposition.

---

## 6.4 RedHerring

A clue or interpretation that plausibly directs attention toward an incorrect proposition.

---

## 6.5 Reveal

An event in which a proposition becomes explicitly confirmed to a character or reader.

Required properties:

- `reveal_id`
- `proposition`
- `revealed_to`
- `scene`

---

# 7. Promise, Payoff, and Arc Classes

## 7.1 NarrativePromise

An expectation created by the text that implies future development or resolution.

Types:

- mystery question;
- threat;
- romantic tension;
- emotional vulnerability;
- skill deficit;
- symbolic object;
- vow;
- debt;
- deadline;
- anticipated confrontation;
- series-level setup.

Required properties:

- `promise_id`
- `promise_type`
- `introduced_in`
- `associated_thread`
- `status`

Allowed statuses:

- `introduced`
- `reinforced`
- `escalated`
- `partially-fulfilled`
- `fulfilled`
- `deferred`
- `abandoned`
- `unresolved`

---

## 7.2 Payoff

An event or state that fulfills, reverses, or resolves a narrative promise.

Required properties:

- `payoff_id`
- `promise`
- `scene`
- `payoff_type`

Allowed payoff types:

- `full`
- `partial`
- `reversal`
- `deferral`
- `negative-payoff`
- `ambiguous`

---

## 7.3 Arc

A structured pattern of state change.

Subclasses:

- CharacterArc
- RelationshipArc
- PlotArc
- SeriesArc

Required properties:

- `arc_id`
- `initial_state`
- `final_state`
- `status`

---

## 7.4 ArcTransition

A state change linked to a triggering event or decision.

Required properties:

- `arc`
- `from_state`
- `to_state`
- `trigger_event`
- `scene`

---

## 7.5 SceneFunction

A controlled vocabulary describing a scene’s narrative work.

Initial values:

- `setup`
- `inciting-disruption`
- `complication`
- `discovery`
- `investigation`
- `confrontation`
- `decision`
- `reversal`
- `romantic-escalation`
- `vulnerability`
- `rupture`
- `recovery`
- `revelation`
- `crisis`
- `climax`
- `resolution`
- `transition`

A scene may have multiple functions.

---

## 7.6 Theme

A recurring conceptual concern.

Theme is included only as an analytical class.

Examples:

- trust;
- betrayal;
- redemption;
- autonomy;
- justice.

Themes are never treated as hard canon.

---

## 7.7 Motif

A recurring image, object, phrase, setting, or action pattern associated with thematic or structural meaning.

---

# 8. Core Relations

## 8.1 Structural Relations

- `CONTAINS`
- `PART_OF`
- `PRECEDES_IN_NARRATION`
- `FOLLOWS_IN_NARRATION`
- `HAS_SCENE`
- `HAS_CHAPTER`
- `HAS_BEAT`
- `FOCALIZED_THROUGH`
- `NARRATED_IN`

---

## 8.2 Story-World Relations

- `APPEARS_IN`
- `OCCURS_AT`
- `OCCURS_BEFORE`
- `OCCURS_AFTER`
- `OCCURS_DURING`
- `PARTICIPATES_IN`
- `PERFORMS`
- `TARGETS`
- `USES`
- `OWNS`
- `POSSESSES`
- `TRANSFERS_TO`
- `LOCATED_AT`
- `MEMBER_OF`
- `RELATED_TO`
- `PARENT_OF`
- `SIBLING_OF`
- `ROMANTICALLY_INVOLVED_WITH`
- `WORKS_FOR`

---

## 8.3 Causal and Motivational Relations

- `CAUSES`
- `ENABLES`
- `TRIGGERS`
- `MOTIVATES`
- `PREVENTS`
- `COMPLICATES`
- `RESULTS_IN`
- `JUSTIFIES`
- `RATIONALIZED_AS`

Causal relations require either explicit evidence or human review.

---

## 8.4 Epistemic Relations

- `KNOWS`
- `BELIEVES`
- `FALSELY_BELIEVES`
- `SUSPECTS`
- `DOUBTS`
- `DENIES`
- `LEARNS_IN`
- `DISCOVERS`
- `WITNESSES`
- `TOLD_BY`
- `READS_IN`
- `OVERHEARS`
- `LIES_ABOUT`
- `CONCEALS`
- `CONCEALED_FROM`
- `REVEALED_TO_READER_IN`
- `INFERABLE_BY_READER_IN`

---

## 8.5 Suspense and Evidence Relations

- `SUPPORTS`
- `WEAKENS`
- `EVIDENCES`
- `MISLEADS_ABOUT`
- `POINTS_TO`
- `FABRICATED_BY`
- `ALTERED_BY`
- `DESTROYED_BY`
- `PLANTED_BY`
- `DISCOVERED_BY`
- `INTERPRETED_BY`
- `MISINTERPRETED_BY`

---

## 8.6 Promise and Arc Relations

- `INTRODUCES`
- `REINFORCES`
- `ESCALATES`
- `COMPLICATES_PROMISE`
- `REVERSES`
- `FULFILLS`
- `PARTIALLY_FULFILLS`
- `DEFERS`
- `ABANDONS`
- `ADVANCES_THREAD`
- `RESOLVES_THREAD`
- `PRESSURES`
- `TRANSFORMS`
- `REGRESSES`
- `DEMONSTRATES_CHANGE`

---

## 8.7 Governance Relations

- `SUPPORTED_BY`
- `ASSERTED_IN`
- `VALID_IN_REVISION`
- `SUPERSEDES`
- `CONTRADICTS`
- `RESOLVES_CONFLICT_WITH`
- `MERGED_WITH`
- `SAME_ENTITY_AS`
- `ALIAS_OF`
- `REQUIRES_REVIEW`

---

# 9. Relation Constraints

## 9.1 `KNOWS`

Domain:

- Character

Range:

- Proposition

Requirements:

- valid-time interval;
- source of knowledge;
- source evidence;
- no inference from reader knowledge alone.

---

## 9.2 `BELIEVES`

Domain:

- Character

Range:

- Proposition

Requirements:

- belief status;
- valid-time interval;
- source evidence or analytical confidence.

---

## 9.3 `POSSESSES`

Domain:

- Character, Organization, Location

Range:

- Object

Requirements:

- possession type;
- valid-time interval.

---

## 9.4 `CAUSES`

Domain:

- Event, Action, State

Range:

- Event, State

Requirements:

- direct textual support or human review.

Mere chronological adjacency is insufficient.

---

## 9.5 `FULFILLS`

Domain:

- Event, Scene, State

Range:

- NarrativePromise

Requirements:

- prior promise introduction;
- payoff classification;
- human review for interpretive cases.

---

## 9.6 `CONTRADICTS`

Domain and range:

- Assertion

Requirements:

- overlapping context;
- incompatible proposition;
- conflict type.

---

# 10. Assertion Model

Every relationship or property capable of dispute should be represented through an assertion record.

```yaml
assertion_id:
subject:
predicate:
object:
assertion_type:
canonical_status:
story_time:
valid_from:
valid_to:
narrative_position:
viewpoint_context:
reader_context:
revision_context:
source_span:
authority_level:
confidence:
review_status:
supersedes:
contradicts:
notes:
```

---

# 11. Controlled Vocabularies

## 11.1 Assertion Type

- `story-world-fact`
- `on-page-event`
- `character-knowledge`
- `character-belief`
- `false-belief`
- `lie`
- `rumor`
- `suspicion`
- `reader-knowledge`
- `reader-inference`
- `authorial-intention`
- `analytical-interpretation`
- `marketing-representation`
- `revision-state-fact`

---

## 11.2 Canonical Status

- `verified`
- `probable`
- `proposed`
- `unresolved`
- `character-belief`
- `false-belief`
- `lie`
- `rumor`
- `suspicion`
- `reader-knowledge`
- `reader-inference`
- `authorial-intention`
- `analytical`
- `marketing-only`
- `superseded`
- `contradicted`
- `rejected`

---

## 11.3 Review Status

- `unreviewed`
- `machine-accepted`
- `human-verified`
- `human-corrected`
- `rejected`
- `needs-adjudication`

---

## 11.4 Confidence

Recommended initial scale:

- `high`
- `medium`
- `low`

Numeric probability is deferred until calibration data exists.

---

# 12. Validation Rules

The pilot should enforce the following rules.

## 12.1 Structural Validation

- Every Scene belongs to exactly one Chapter.
- Every Chapter belongs to exactly one Book.
- Every Scene has a source span.
- Scene IDs are unique.
- Narrative order is unique within a book.

---

## 12.2 Epistemic Validation

- A Character cannot `KNOW` a proposition before a qualifying knowledge event.
- Reader knowledge does not imply character knowledge.
- Character dialogue does not automatically create story-world fact.
- False belief must reference a proposition contradicted by stronger evidence.
- A lie requires evidence that the speaker believed the statement false.

---

## 12.3 Temporal Validation

- State intervals must have valid ordering.
- Possession intervals for one object may overlap only when shared access or joint custody is explicit.
- An event cannot cause an earlier event unless the relation is retrospective or explanatory and marked accordingly.
- A dead character cannot participate in present chronology without an allowed narrative mode.

Allowed modes:

- flashback;
- memory;
- dream;
- recording;
- hallucination;
- supernatural presence;
- mistaken death;
- recovered archival material.

---

## 12.4 Promise Validation

- Every Payoff must reference at least one prior NarrativePromise.
- Every fulfilled promise must have a payoff scene.
- Every deferred promise must identify the intended future scope where known.
- An abandoned promise requires review.

---

## 12.5 Governance Validation

- No verified assertion lacks source provenance or explicit author declaration.
- No superseded assertion remains active in the same revision context.
- Contradictory assertions must produce a conflict record.
- Marketing-only assertions cannot override manuscript canon.
- Analytical interpretations cannot be promoted automatically to verified story-world fact.

---

# 13. Pilot Query Coverage Matrix

| Query area | Primary classes | Primary relations |
|---|---|---|
| Canon | Character, Location, Organization, Object, Assertion | SUPPORTED_BY, CONTRADICTS, SUPERSEDES |
| Scene structure | Book, Chapter, Scene, Beat | CONTAINS, FOCALIZED_THROUGH |
| Chronology | Event, State, Scene | OCCURS_BEFORE, OCCURS_DURING |
| Character knowledge | Proposition, KnowledgeState, BeliefState | KNOWS, BELIEVES, LEARNS_IN |
| Causality | Event, Action, State | CAUSES, ENABLES, MOTIVATES |
| Object custody | Object, PossessionState, LocationState | POSSESSES, TRANSFERS_TO, LOCATED_AT |
| Clues and evidence | Clue, Evidence, RedHerring, Reveal | SUPPORTS, MISLEADS_ABOUT, REVEALED_TO_READER_IN |
| Promise/payoff | NarrativePromise, Payoff, NarrativeThread | INTRODUCES, ESCALATES, FULFILLS |
| Character arc | CharacterState, CharacterArc, ArcTransition | PRESSURES, TRANSFORMS, REGRESSES |
| Relationship arc | RelationshipState, RelationshipArc | DEMONSTRATES_CHANGE, REVERSES |
| Revision conflict | Revision, Assertion, SourceDocument | VALID_IN_REVISION, SUPERSEDES, CONTRADICTS |

---

# 14. Deferred Concepts

The following are intentionally deferred from v0.1.

- formal genre ontology;
- detailed dialogue-act taxonomy;
- sentiment scoring;
- numeric emotional trajectories;
- symbolic interpretation as canon;
- full thematic inference;
- prose-style ontology;
- narratee modeling;
- free indirect discourse classification;
- formal possible-world semantics;
- comprehensive speech-act logic;
- automatic scene necessity scoring;
- universal beat-sheet mappings.

These may be added only when pilot evidence shows they are needed.

---

# 15. Implementation Neutrality

This ontology does not require:

- RDF;
- OWL;
- Neo4j;
- Kùzu;
- PostgreSQL;
- JSON-LD;
- any specific GraphRAG framework.

It can be represented initially in:

- Markdown;
- CSV;
- JSON;
- a property graph;
- a relational prototype.

The storage choice should follow validated query needs, not the other way around. Civilization has already built enough databases in search of a problem.

---

# 16. Review Questions

Before approval, verify:

1. Does every class support at least one pilot query?
2. Are story-world fact and character belief cleanly separated?
3. Can the model represent reader knowledge independently?
4. Can facts vary across time and revision?
5. Can lies and concealment be represented without corrupting canon?
6. Can promises and payoffs be traced?
7. Can object custody be reconstructed?
8. Can causality remain distinct from sequence?
9. Can interpretive claims remain reviewable rather than canonical?
10. Is any class present merely because it sounds sophisticated?

---

# 17. Immediate Next Action

Manually validate the first three chapters of `phase-8-editing/MANUSCRIPT.md` against `BOOK-3-SCENE-LEDGER-v0.1.csv`.

The validation pass should confirm:

- chapter boundaries;
- scene boundaries;
- POV;
- location;
- present characters;
- major events;
- explicit knowledge changes;
- object transfers;
- obvious promises and payoffs.

The result should be:

`BOOK-3-SCENE-LEDGER-CH01-03-VALIDATED-v0.1.csv`
