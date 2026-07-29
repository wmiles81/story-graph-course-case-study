# Story Graph Project Conversation

**Saved:** July 21, 2026

---

## User

Review the source documents and return a report on the viability of knowledge graphs in the writing of long form fiction, books or series. Identify any deficiencies in the resources.

---

## Assistant

# Report: Viability of Knowledge Graphs for Long-Form Fiction

## Executive conclusion

Knowledge graphs are **highly viable as the structured memory and analytical backbone of a long-form fiction system**, especially for novels that contain large casts, complicated timelines, mystery or suspense logic, recurring objects, inter-book continuity, and long-running character arcs.

They are much less useful as a direct mechanism for producing good prose.

That distinction matters. A graph can tell you that Lydia learned about the offshore account in Chapter 18, that Miles did not meet her until Chapter 21, and that the gun introduced in Book 1 has never been accounted for. It cannot, by itself, tell you whether their confrontation feels emotionally honest, whether the dialogue has subtext, or whether the scene is tedious despite satisfying every structural requirement.

My overall assessment:

| Application | Viability |
|---|---:|
| Series continuity and canon management | **Very high** |
| Timeline, location, object, and character-state tracking | **Very high** |
| Mystery clues, reveals, secrets, and knowledge-state analysis | **Very high** |
| Plot-thread and promise/payoff tracking | **High** |
| Relationship and emotional-arc monitoring | **High, with a purpose-built ontology** |
| Retrieval across manuscripts, notes, and prior books | **High** |
| Developmental analysis and revision support | **Moderate to high** |
| Theme, tone, subtext, and voice analysis | **Moderate at best** |
| Automatic prose generation | **Low as a graph-native function** |
| Evaluation of literary quality | **Low without additional models and human judgment** |

The source collection provides a strong technical foundation for graphs, ontology, retrieval, and agent access. It does **not yet provide a sufficient fiction-domain model**. The central deficiency is not the graph technology. It is the absence of a narrative ontology that understands that fiction consists not merely of people and events, but of **partial knowledge, unreliable assertions, changing emotional states, causality, scene function, narrative promises, viewpoint restrictions, and alternative versions of reality**.

## What the source documents establish well

The sources correctly distinguish among:

- the ontology, which defines what kinds of things and relationships may exist;
- the knowledge graph, which contains actual instances and assertions;
- the exchange or storage format, which determines how information is represented.

They also support a hybrid retrieval architecture:

- vector search for fuzzy, thematic, emotional, and paraphrased questions;
- graph traversal for exact relational, temporal, and multi-hop questions;
- source text verification for every important answer.

The documents also support incremental graph updates, MCP access, human review, schema induction, constrained extraction, and lightweight file-first author workflows.

## Strongest fiction use cases

### Canon and continuity

The graph can represent:

- characters and aliases;
- families;
- companies and organizations;
- locations and containment;
- possessions;
- injuries;
- physical traits;
- professions and roles;
- encounters;
- promises;
- secrets;
- evidence;
- relationships;
- deaths, births, marriages, and breakups;
- dates and chronology;
- series-level facts.

### Character knowledge and belief

A story needs several truth layers:

1. what is objectively true;
2. what the narrator claims;
3. what each character believes;
4. what each character knows;
5. what the reader knows;
6. what the reader is intended to suspect;
7. what remains unresolved.

### Clue, reveal, and suspense logic

The graph can track:

- what a clue evidences;
- who discovers it;
- when it becomes available;
- whether it is understood correctly;
- whether it is a red herring;
- what reveal or payoff it supports.

### Narrative promises and payoffs

Promises can include:

- threats;
- secrets;
- mystery questions;
- romantic vulnerabilities;
- symbolic objects;
- vows;
- debts;
- deadlines;
- anticipated confrontations.

### Relationship and emotional arcs

These require temporal, multidimensional state rather than simple static relationships.

### Series architecture

The graph can distinguish:

- series truth;
- book-local understanding;
- planned future canon;
- discarded draft ideas;
- marketing descriptions;
- reader-facing reveal status.

## Major deficiencies in the resources

1. Almost no direct treatment of fiction writing.
2. No narrative ontology.
3. Inadequate temporal modeling.
4. Weak handling of contradictory and perspectival truth.
5. No model of narrative causality.
6. Overemphasis on global graph visualization.
7. Insufficient evaluation methodology for fiction.
8. No serious treatment of manuscript versioning.
9. No strong separation between extraction and authorial authority.
10. Some resources are tangential or overbuilt for an author workflow.

## Recommended architecture

1. Source corpus
2. Document and chunk index
3. Narrative property graph
4. Narrative ontology and validation rules
5. Analytical services
6. Agent and writing integration

## Minimum viable fiction ontology

### Core entities

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
- Promise
- NarrativeThread
- SourceSpan
- Revision

### Core state objects

- CharacterState
- RelationshipState
- KnowledgeState
- PossessionState
- LocationState
- Assertion

### Core relationships

- CONTAINS
- APPEARS_IN
- OCCURS_AT
- OCCURS_BEFORE
- CAUSES
- MOTIVATES
- REVEALS
- CONCEALS
- KNOWS
- BELIEVES
- FALSELY_BELIEVES
- DISCOVERS
- WITNESSES
- POSSESSES
- TRANSFERS_TO
- INTRODUCES
- ESCALATES
- FULFILLS
- RESOLVES
- CONTRADICTS
- SUPERSEDES
- SUPPORTED_BY
- NARRATED_BY
- FOCALIZED_THROUGH

## Bottom line

A knowledge graph can become the **canonical story-state layer** beneath a serious long-form fiction environment.

It is especially strong for:

- continuity;
- chronology;
- character knowledge;
- mystery logic;
- series canon;
- object tracking;
- relationship progression;
- promises and payoffs;
- evidence-backed AI assistance.

It should not be mistaken for:

- the manuscript itself;
- a substitute for text retrieval;
- an automatic judge of literary quality;
- an engine that understands emotion merely because someone added an `EMOTIONALLY_CONNECTED_TO` edge.

The recommended direction is a **hybrid, revision-aware story graph** built around source evidence, temporal state, character-specific knowledge, narrative promises, and author-controlled canon.

---

## User

How would computational narratology or context graphs align with our current conversation?

---

## Assistant

Computational narratology and context graphs are not competing with the knowledge-graph approach we have been discussing. They fill the exact hole identified in the earlier report.

A conventional knowledge graph tells us **what exists and how things are related**.

Computational narratology tells us **how those things function as a story**.

A context graph tells us **which version of those facts is relevant from a particular viewpoint, time, scene, or analytical purpose**.

Put together, they turn a generic corpus graph into an actual **story intelligence system**.

## The alignment in one model

| Layer | Governing question | Example |
|---|---|---|
| Canonical story model | How is information represented? | A scene record has an ID, chapter, POV, location, and source span |
| Narrative ontology | What kinds of story things and relations exist? | Character, Event, Goal, Clue, Promise, Reveal, Cause |
| Story knowledge graph | What actually happens in this manuscript? | Emery finds the ledger in Scene 18 |
| Context and narratological graphs | What does that fact mean here, and to whom? | Emery knows; Theo does not; the reader suspects; the scene functions as a reversal |

Computational narratology operates over those layers. It is primarily an analytical and interpretive discipline, not another storage technology.

## What computational narratology adds

### Story versus discourse

It distinguishes:

- story order: when events occur in the fictional world;
- discourse order: when and how the text presents them.

### Narrative levels and viewpoint

It supports:

- narrator;
- focalizer or POV character;
- narrated character;
- embedded stories;
- memories;
- dreams;
- testimony;
- letters and recordings;
- unreliable narration.

### Plot structure

Scenes and events can be classified by function:

- setup;
- inciting disruption;
- complication;
- decision;
- reversal;
- revelation;
- confrontation;
- crisis;
- climax;
- denouement;
- payoff.

### Causal and motivational structure

The model can distinguish:

- CAUSES
- ENABLES
- MOTIVATES
- TRIGGERS
- PREVENTS
- COMPLICATES
- REVEALS
- MISLEADS_ABOUT
- JUSTIFIES
- IS_RATIONALIZED_AS

### Character arcs as state transitions

Instead of static traits, the model tracks state changes caused by events.

## What a context graph adds

A context graph represents the bounded situation in which facts, entities, states, and relationships are interpreted.

It answers:

- connected when;
- connected where;
- connected for whom;
- connected under which interpretation;
- connected in which manuscript version;
- connected for which analytical task.

### Scene context

For each scene:

- POV;
- location;
- present characters;
- active goals;
- threats;
- known facts;
- false beliefs;
- hidden facts;
- emotional states;
- relevant objects;
- open promises;
- reader knowledge.

### Character context

For a character at a specific story moment:

- what they know;
- what they believe;
- whom they trust;
- what they want;
- what they fear;
- what they hide;
- what they incorrectly assume.

### Reader context

Tracks:

- facts explicitly revealed;
- clues visible but uninterpreted;
- facts implied;
- likely suspicions;
- red herrings;
- unanswered questions;
- dramatic irony;
- withheld information.

### Revision context

Tracks whether a fact is valid in:

- outline;
- first draft;
- current draft;
- published edition;
- revised edition;
- proposed future canon;
- marketing summary.

## Context is not merely metadata

Context should usually be represented as first-class assertions or named subgraphs, not as an ever-growing pile of tags.

This supports:

- lies;
- misunderstanding;
- unreliable narration;
- secrecy;
- memory;
- revelation;
- revision history.

## Division of responsibility

```text
Knowledge graph = story memory
Computational narratology = story analysis
Context graph = story perspective
```

## Revised architecture

1. Source and provenance layer
2. Canonical narrative representation
3. Story-world graph
4. Assertion and context graph
5. Computational narratology layer
6. Hybrid retrieval layer
7. Analytical and agent layer

## Concrete analytical products

- continuity report;
- scene-context card;
- promise and payoff matrix;
- suspense asymmetry map;
- arc fulfillment report.

## Recommended conceptual position

A strong name for the system is:

> **A context-sensitive computational narrative graph**

A more accessible name is:

> **A Story Graph System**

Its internal structure combines:

- a canonical story representation;
- a narrative ontology;
- a story-world knowledge graph;
- temporal context graphs;
- epistemic graphs for knowledge and belief;
- computational narratology analyzers;
- hybrid textual retrieval;
- source-grounded agent access.

The alignment is:

> **Knowledge graphs capture the pieces, context graphs capture the situated state, and computational narratology captures the story those pieces create.**

---

## User

I added this, probably too early, to eventually test some of our outputs. For now, please create a plan to proceed.

---

## Assistant

You did add it early, but not uselessly early. The archive is valuable now as a **test corpus and requirements probe**, not yet as material to ingest wholesale into a polished graph.

The archive contains four books, a series bible, and extensive phase-by-phase development material. It is ideal for testing canon conflict, version drift, context selection, and narrative extraction, provided we proceed in controlled stages.

# Recommended plan

## Phase 0: Define the questions before the graph

Establish 40–60 representative queries across:

- canon and continuity;
- character knowledge;
- plot and causality;
- promises and payoffs;
- character and relationship arcs;
- series continuity.

These become acceptance tests.

## Phase 1: Corpus inventory and source classification

Create a manifest for every file with:

- path;
- book;
- development phase;
- source type;
- likely authority;
- version or timestamp;
- duplicate family;
- manuscript status;
- intended use;
- inclusion status.

Suggested source classes:

| Source class | Typical authority |
|---|---|
| Published or final manuscript | Highest story evidence |
| Current full manuscript | High |
| Approved series bible | High for declared canon |
| Current book bible | High but subordinate to manuscript where conflict exists |
| Final outline | Medium |
| Chapter drafts | Version-dependent |
| Editing and diagnostic reports | Analytical, not canon |
| Brainstorming and concept files | Proposed, not canon |
| Superseded versions and backups | Historical only |
| Marketing documents | Reader-facing interpretation, not necessarily literal canon |

### Deliverable

A machine-readable `corpus_manifest`.

## Phase 2: Establish the source-of-truth hierarchy

Define formal conflict rules.

Each assertion should carry:

```text
source_file
source_span
source_class
book
version
authority_level
assertion_type
review_status
confidence
```

### Deliverable

A written canon and conflict doctrine.

## Phase 3: Select a narrow pilot

Use:

- the series bible;
- one book bible;
- one final manuscript;
- optionally one outline.

Do not begin with the whole series.

### Deliverable

A pilot corpus of 10–30 carefully chosen files.

## Phase 4: Build a canonical scene ledger manually

Each scene record should include:

```text
scene_id
book
chapter
scene_order
story_time
location
POV
present_characters
scene_goal
opposition
turn
outcome
major_events
knowledge_gained
belief_changes
relationship_changes
objects_transferred
promises_introduced
promises_advanced
promises_paid_off
source_span
```

### Deliverable

A manually reviewed scene ledger for one complete book.

## Phase 5: Define the minimum narrative ontology

### Initial entity types

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
- Promise
- NarrativeThread
- Assertion
- SourceSpan
- Revision

### Initial state types

- CharacterState
- RelationshipState
- KnowledgeState
- PossessionState
- ReaderKnowledgeState

### Initial relationships

- CONTAINS
- APPEARS_IN
- OCCURS_AT
- OCCURS_BEFORE
- CAUSES
- MOTIVATES
- REVEALS
- CONCEALS
- KNOWS
- BELIEVES
- FALSELY_BELIEVES
- DISCOVERS
- WITNESSES
- POSSESSES
- TRANSFERS_TO
- INTRODUCES
- ESCALATES
- FULFILLS
- RESOLVES
- CONTRADICTS
- SUPERSEDES
- SUPPORTED_BY
- FOCALIZED_THROUGH

### Deliverable

Narrative ontology version 0.1.

## Phase 6: Add first-class context and assertion modeling

Create context views for:

- scene context;
- character context;
- reader context;
- revision context;
- book context;
- series context.

### Deliverable

A formal context model supporting:

- canonically true;
- believed by character;
- suspected by character;
- stated as a lie;
- revealed to reader;
- withheld from reader;
- true only in an earlier draft.

## Phase 7: Build the extraction pipeline

### Pass 1: Structural extraction

- books;
- chapters;
- scenes;
- characters;
- locations;
- objects;
- direct relationships;
- temporal markers;
- POV;
- source spans.

### Pass 2: Event extraction

- actions;
- decisions;
- discoveries;
- transfers;
- injuries;
- arrivals and departures;
- explicit causal links.

### Pass 3: Epistemic extraction

- knowledge;
- belief;
- suspicion;
- deception;
- concealment;
- reader exposure.

### Pass 4: Narratological interpretation

- scene function;
- promise introduction;
- escalation;
- reversal;
- payoff;
- character-state change;
- relationship-state change;
- thematic relevance.

### Deliverable

A repeatable extraction pipeline with source citation and confidence.

## Phase 8: Build a hybrid retrieval layer

Use:

1. lexical search;
2. vector search;
3. graph traversal.

### Deliverable

A query router.

## Phase 9: Create the first analytical outputs

1. Canon conflict report
2. Character knowledge audit
3. Promise/payoff ledger
4. Object and evidence custody report
5. Character and relationship arc report
6. Series continuity report

## Phase 10: Evaluation

Create a gold test set:

- 40 canon questions;
- 25 timeline questions;
- 25 character-knowledge questions;
- 20 object-custody questions;
- 20 causal questions;
- 20 promise/payoff questions;
- 15 contradiction tests;
- 15 revision-context tests.

Measure:

- correctness;
- completeness;
- citation accuracy;
- temporal accuracy;
- perspective accuracy;
- confidence calibration;
- false contradiction rate;
- missed contradiction rate.

## Phase 11: Incremental revision support

1. Detect changed files and scenes.
2. Invalidate assertions tied to changed spans.
3. Re-extract only affected material.
4. Compare old and new assertions.
5. Flag canon-impacting changes.
6. Re-run dependent reports.
7. Preserve superseded assertions.

## Phase 12: Expand book by book

After the pilot succeeds:

1. Add one additional book.
2. Resolve cross-book identities.
3. Introduce series-level threads.
4. Compare the books.
5. Refine the ontology only where required.
6. Add Books 3 and 4 sequentially.
7. Process historical and analytical files last.

## Practical sequence

1. Inventory the archive fully.
2. Classify files by source type and authority.
3. Write the canon/conflict doctrine.
4. Select one pilot book and governing files.
5. Create the gold scene ledger.
6. Define ontology v0.1.
7. Define the assertion/context model.
8. Build conservative extraction.
9. Produce the six initial reports.
10. Evaluate against the gold set.
11. Refine before expanding.

## What not to do yet

Do not yet:

- load the entire archive into GraphRAG;
- build an elaborate global visualization;
- commit to a database before the query model is proven;
- formalize every narratological concept;
- assign numeric emotion scores as hard truth;
- allow an LLM to write directly into canonical records;
- treat analyses, outlines, manuscripts, and marketing files as equally authoritative.

## First milestone

> **For one book, produce a source-grounded scene graph that can correctly answer continuity, knowledge-state, object-custody, promise/payoff, and arc questions at an agreed accuracy level.**

Only after that succeeds should the project become a series graph.

---

## User

Before we get too large, can we save this conversation to a markdown file?
