# The Story Graph Program: Five Acts from Pilot to Living Story Intelligence

## Purpose of the Five-Act Model

The Story Graph project is not a single extraction exercise. It is a staged program that begins with one source-grounded pilot and ends with a maintained, series-level story intelligence system.

Each act answers a different question:

- **Act I:** Can a complete novel be converted into a trustworthy, queryable model?
- **Act II:** Can the author review that model and turn provisional findings into ratified canon?
- **Act III:** Can the graph become a practical operating system for writing, editing, continuity, and marketing?
- **Act IV:** Can individual book graphs be joined into a controlled series graph without flattening book-specific truth?
- **Act V:** Can the system detect manuscript changes and update the graph safely, incrementally, and transparently?

The acts are cumulative. Later acts depend on the authority, evidence, identifiers, and validation practices established earlier. Skipping an act may produce something impressive-looking, but it will also produce the usual technological miracle: a system that answers quickly and cannot explain why it should be trusted.

---

# Act I — The Source-Grounded Pilot

## Central question

**Can one complete novel be transformed into a queryable Story Graph while preserving source authority, chronology, perspective, uncertainty, revision context, and evidence?**

Act I establishes the method. It is the research-and-construction act in which the project learns what must be represented, how records relate, where automated extraction fails, and what validation gates are necessary before graph output can be trusted.

## Objectives

Act I must:

1. define the questions the graph is expected to answer;
2. establish the authority hierarchy among manuscripts, outlines, bibles, reports, and earlier drafts;
3. identify the governing manuscript without pretending that “most recent” automatically means “canonical”;
4. segment the manuscript into stable scenes;
5. create canonical identifiers for scenes, entities, propositions, objects, promises, and arcs;
6. model facts separately from beliefs, lies, inferences, and reader knowledge;
7. track chronology, custody, causality, promises, payoffs, and character movement;
8. reconcile all extracted records against the manuscript;
9. generate a provisional graph;
10. test that graph with a formal query set.

## Major workstreams

### 1. Pilot specification

The pilot begins with the query families, not the database schema.

The system must answer questions about:

- canon and continuity;
- chronology and event order;
- character knowledge and false belief;
- reader knowledge and dramatic irony;
- causality and motivation;
- objects, evidence, and custody;
- promises, setups, and payoffs;
- character and relationship arcs;
- revision authority and superseded material.

These requirements determine the ontology and the data model.

### 2. Corpus and authority assessment

Every source is classified by type and authority.

The system distinguishes:

- governing manuscript;
- candidate manuscript;
- approved reference material;
- planning material;
- editorial analysis;
- superseded drafts;
- derived graph artifacts.

Authority is assertion-specific. A manuscript may govern what happened in a scene, while a series bible may govern an unstated birth date. An editorial report may identify a possible contradiction without becoming story-world truth.

### 3. Scene extraction and reconciliation

Scenes are the backbone of the graph because they provide stable containers for:

- viewpoint;
- location;
- story time;
- participating characters;
- goals and opposition;
- state changes;
- revelations;
- custody transfers;
- promises and payoffs;
- evidence spans.

Automated segmentation is treated as a draft, not an oracle. Chapter totals, scene IDs, source spans, and batch ledgers are reconciled before the master scene ledger is accepted.

### 4. Ontology and assertion design

The graph separates the thing being claimed from the person who knows or believes it.

For example:

- “Jackson is alive” is a proposition.
- “Margot knows Jackson is alive” is a knowledge state.
- “Jonah believes Jackson is dead” is a belief state.
- “The reader knows Jackson is alive” is a reader-context state.
- “An earlier draft said Jackson died” is revision evidence.

This separation prevents contradictions from being manufactured by poor modeling.

### 5. Specialized narrative ledgers

Act I builds dedicated structures for:

- entity identity and aliases;
- proposition registries;
- contextual assertions;
- chronology;
- knowledge and belief;
- object custody;
- promises and payoffs;
- character and relationship arcs;
- continuity candidates;
- source evidence;
- revision state.

The graph may expose these as connected views, but they remain semantically distinct.

### 6. Integrity, reconciliation, and evaluation

The first graph build is not accepted merely because it compiles.

Integrity checks test:

- scene coverage;
- context coverage;
- dangling entity references;
- invalid scene references;
- unresolved identifiers;
- duplicate or conflicting propositions;
- broken custody intervals;
- unsupported claims;
- missing evidence;
- unanswered gold queries.

A failed integrity gate is a required result, not an embarrassment to be hidden. It tells the project where its model and extraction pipeline remain incomplete.

## Deliverables

Act I produces:

- pilot specification;
- query set;
- canon and conflict doctrine;
- corpus manifest;
- manuscript authority assessment;
- scene ledger and scene contexts;
- entity registry;
- proposition registry;
- assertion ledger;
- knowledge, custody, promise, chronology, and arc ledgers;
- continuity audit;
- normalization maps;
- provisional Story Graph;
- browser report;
- gold-query evaluation;
- pilot completion assessment.

## Completion condition

Act I is complete when the graph is technically coherent, evidence-bearing, queryable, and evaluated.

It is **not yet canonical**.

Its correct terminal status is:

> **Technical pilot complete. Canon remains review-deferred provisional until author ratification.**

## Class lesson

Act I demonstrates that a Story Graph is not created by extracting names and relationships. It is created by preserving distinctions that prose allows readers to understand implicitly: who knows what, when it became true, who only believes it, what source supports it, and whether the author has approved it.

---

# Act II — Author Ratification and Canon Freeze

## Central question

**Can the provisional graph be reviewed by the author and converted into an explicitly approved canon baseline?**

Act II changes the authority of the system. Act I produces a technically defensible interpretation of the manuscript. Act II gives the author control over disputed interpretation, ambiguity, continuity judgment, and final canonical status.

## Objectives

Act II must:

1. expose every review-deferred record in a usable decision queue;
2. present the source evidence supporting each proposed graph record;
3. separate factual correction from interpretive disagreement;
4. allow intentional ambiguity to remain intentional;
5. record author decisions without overwriting the prior provisional state;
6. rebuild the graph from ratified decisions;
7. freeze a versioned canonical baseline for the book.

## Ratification categories

Each review item should support at least these outcomes:

- **Ratified:** accepted as canonical.
- **Corrected:** accepted after modification.
- **Rejected:** the extraction or inference is not valid.
- **Intentionally ambiguous:** the text supports uncertainty that should remain unresolved.
- **Deferred:** the author does not wish to decide yet.
- **Continuity issue confirmed:** the manuscript contains a real inconsistency.
- **Not a continuity issue:** the apparent conflict is explained by knowledge, time, perspective, or state change.

## Major workstreams

### 1. Ratification queue

The system gathers all records that require human authority, including:

- continuity candidates;
- uncertain scene boundaries;
- ambiguous chronology;
- inferred motivations;
- unresolved object custody;
- disputed promise resolution;
- character-knowledge exceptions;
- unsupported or weakly supported evidence excerpts;
- canonical claims derived from planning material;
- records produced by automated normalization.

Each queue item includes the graph claim, source evidence, surrounding context, affected downstream records, and recommended decision.

### 2. Evidence verification

Evidence is checked against the manuscript, not merely against previously generated ledgers.

The review interface should show:

- chapter and scene;
- source span;
- exact or bounded excerpt;
- proposed assertion;
- authority level;
- confidence;
- dependent queries and records.

This is especially important for knowledge-state claims, where a plausible paraphrase may not prove that a character actually learned something on-page.

### 3. Continuity adjudication

The author decides whether a candidate represents:

- an error;
- a deliberate reveal;
- a false belief;
- an unreliable statement;
- a revision artifact;
- a timeline compression;
- a valid state change;
- an unresolved mystery.

The adjudication record becomes part of the graph’s provenance.

### 4. Canon commit and version freeze

Ratified decisions are compiled into a canonical graph build.

The freeze should include:

- canon version identifier;
- governing manuscript version;
- date of ratification;
- accepted decision ledger;
- unresolved-item register;
- checksums or version hashes where practical;
- generated graph version;
- evaluation results;
- known limitations.

The freeze does not prevent later revision. It creates a stable baseline against which later revision can be measured.

## Deliverables

Act II produces:

- ratification policy;
- author review queue;
- evidence-verification queue;
- continuity adjudication ledger;
- canonical decision ledger;
- corrected source ledgers;
- ratified Story Graph;
- Book 3 canon baseline;
- canon-freeze report;
- unresolved ambiguity register.

## Completion condition

Act II is complete when the author has approved the baseline or explicitly deferred the remaining exceptions, and the system can distinguish:

- provisional records;
- rejected records;
- superseded records;
- ratified canon;
- unresolved ambiguity.

## Class lesson

Act II teaches that authorship is an authority layer, not a sentimental afterthought. A graph can analyze text, but it cannot silently appoint itself the final interpreter of the work.

---

# Act III — The Story Operating System

## Central question

**Can the ratified graph become a practical tool used during writing, revision, editing, and publishing?**

Act III turns the graph from an artifact into an operational environment. The user no longer visits it only to inspect what happened. The graph begins assisting active creative and production decisions.

## Objectives

Act III must:

1. provide natural-language and structured querying;
2. expose evidence with every answer;
3. support editorial and continuity workflows;
4. connect graph findings to manuscript locations;
5. support controlled corrections and proposed changes;
6. distinguish read-only analysis from canon-changing actions;
7. present story state visually and at useful levels of abstraction.

## Core capabilities

### 1. Query layer

The operating system should answer questions such as:

- What does Margot know at the start of Chapter 17?
- When does Jonah learn the Treaty upload failed?
- Who possesses each copy of the evidence after Chapter 12?
- Which promises remain open after Chapter 24?
- Which scenes depend on Sterling believing Jonah is dead?
- Where does the relationship arc materially change?
- Which claims are supported only by inference?
- What changed between two manuscript versions?

Answers should include evidence, confidence, authority, and relevant scene links.

### 2. Continuity workspace

The system should generate targeted views for:

- timeline conflicts;
- impossible travel;
- object custody gaps;
- knowledge-before-reveal errors;
- unexplained relationship changes;
- unresolved promises;
- inconsistent injuries or physical states;
- naming and identity inconsistencies.

The workspace should allow an editor to classify, comment on, defer, or resolve each issue.

### 3. Revision planning

Before changing the manuscript, an author should be able to test consequences.

Examples:

- What breaks if Chapter 12 moves after Chapter 14?
- Which characters must now know about the ledger earlier?
- Which later scenes depend on the current location of the revolver?
- Which promises would close too early?
- Which marketing claims would become inaccurate?

This is impact analysis for story revision.

### 4. Arc and promise intelligence

The system should visualize:

- character pressure over time;
- internal and external arc movement;
- relationship progression;
- promise opening, reinforcement, delay, and payoff;
- unresolved or weakly delivered expectations;
- long sections with no meaningful state change.

This is not a substitute for artistic judgment. It is an instrument panel for noticing where judgment is needed.

### 5. Marketing alignment

The graph can compare the manuscript against:

- trope claims;
- blurbs;
- advertising language;
- series positioning;
- reader promises;
- content warnings.

It can flag claims that are unsupported, overstated, or accidentally spoil major turns.

### 6. Controlled write actions

The system should never casually edit canon.

Write actions should support:

- proposed correction;
- author-approved correction;
- new revision branch;
- superseding a prior assertion;
- adding a planned but noncanonical note;
- recording a future-book dependency.

Every write action needs provenance and rollback.

## Deliverables

Act III produces:

- query interface;
- evidence viewer;
- continuity dashboard;
- promise/payoff tracker;
- custody tracker;
- character-knowledge viewer;
- arc visualizations;
- revision impact analyzer;
- marketing alignment report;
- controlled graph-edit workflow;
- user and role permissions.

## Completion condition

Act III is complete when the graph is used during ordinary story work and its answers are faster and more reliable than manually searching the manuscript and scattered notes.

## Class lesson

Act III demonstrates the difference between a database and an operating system. A database stores records. An operating system supports decisions, workflows, consequences, and controlled change.

---

# Act IV — The Series Graph

## Central question

**Can multiple book-level graphs be connected into a series-wide model without erasing the boundaries, spoilers, revisions, and authority of individual books?**

Act IV expands the scope from one novel to the larger fictional universe.

## Objectives

Act IV must:

1. preserve each book as an independently versioned graph;
2. identify entities shared across books;
3. track cross-book chronology;
4. model series-level promises and arcs;
5. preserve book-specific reader knowledge;
6. distinguish recurring canon from book-local events;
7. detect contradictions introduced by later volumes;
8. support sequel planning without contaminating published-book canon.

## Major workstreams

### 1. Cross-book identity

The same character, location, organization, object, or event may appear under different names or descriptions across books.

The series graph needs:

- stable series-level IDs;
- book-local aliases;
- first appearance;
- current status;
- role changes;
- identity reveals;
- spoiler boundaries.

A hidden identity must not be exposed to a Book 1 reader merely because the Series Graph knows the answer from Book 4.

### 2. Series chronology

The system tracks:

- absolute and relative dates;
- overlapping events;
- flashbacks;
- gaps between books;
- character ages;
- travel;
- institutional history;
- historical events referenced across volumes.

Chronology should support both story-world order and publication/reveal order.

### 3. Cross-book knowledge and spoilers

Knowledge is indexed by character, reader context, book, chapter, and edition.

The system must answer:

- What does this character know by the end of Book 2?
- What may a reader safely be told before reading Book 3?
- Which marketing copy reveals a Book 1 secret?
- Which sequel scene assumes knowledge never shown on-page?

### 4. Series promises and arcs

Some promises open in one book and resolve later.

The graph tracks:

- unresolved antagonist threats;
- recurring mysteries;
- family secrets;
- political or organizational conflicts;
- long-form romantic or relational arcs;
- world-rule questions;
- sequel hooks;
- series-end obligations.

This allows the author to compare promises made with promises actually delivered.

### 5. World rules and institutions

Repeated world rules should be modeled explicitly:

- supernatural rules;
- technology constraints;
- legal or political systems;
- organizational hierarchy;
- magic costs;
- biological limitations;
- economic and geographic facts.

Exceptions are stored with context rather than being forced into false uniformity.

### 6. Book isolation and series inheritance

Each book inherits appropriate series facts but retains its own authority and perspective.

A later retcon should not silently rewrite the historical graph. It should create:

- prior canonical state;
- revised canonical state;
- effective book or edition;
- explanation;
- affected records.

## Deliverables

Act IV produces:

- series entity registry;
- cross-book identity map;
- series chronology;
- spoiler-aware knowledge graph;
- series promise ledger;
- recurring object and location registry;
- world-rule registry;
- cross-book continuity audit;
- sequel-planning dashboard;
- series browser.

## Completion condition

Act IV is complete when the system can answer series-level questions while still reconstructing exactly what was true, known, believed, and revealed at any point in any individual book.

## Class lesson

Act IV teaches that a series graph is not merely several book graphs poured into a larger bucket. It is a federated model with inheritance, boundaries, historical state, and spoiler control.

---

# Act V — Automated Manuscript Change Intelligence

## Central question

**Can the Story Graph respond to manuscript revision by identifying meaningful changes, calculating their consequences, and updating only what has actually changed?**

Act V creates the maintained system. Instead of rebuilding the graph after every revision, the system performs controlled change detection and produces a reviewable delta.

## Objectives

Act V must:

1. compare manuscript versions structurally and semantically;
2. identify added, removed, split, merged, moved, and rewritten scenes;
3. detect changed facts and state transitions;
4. calculate downstream effects;
5. preserve prior graph versions;
6. require review for authority-sensitive changes;
7. regenerate only affected records and evaluations;
8. explain every proposed update.

## Change-detection layers

### 1. Textual change

The system identifies:

- inserted and deleted passages;
- changed names, dates, numbers, and locations;
- altered dialogue;
- rewritten descriptions;
- moved paragraphs.

Textual difference is evidence, but not yet narrative interpretation.

### 2. Structural change

The system detects:

- scenes added or removed;
- scenes split or merged;
- chapter moves;
- viewpoint changes;
- reordered events;
- changed scene boundaries.

Stable IDs and lineage records help the system decide whether a scene is revised, moved, or replaced.

### 3. Semantic change

The system determines whether revision changed:

- what happened;
- who caused it;
- who witnessed it;
- who learned it;
- what a character believes;
- object custody;
- chronology;
- relationship state;
- promise status;
- arc movement;
- world rules.

### 4. Dependency analysis

A changed assertion may affect many later records.

For example, changing when Margot learns a secret may affect:

- later dialogue;
- dramatic irony;
- continuity checks;
- motivation;
- query answers;
- scene summaries;
- marketing descriptions;
- sequel assumptions.

The system produces a dependency report rather than quietly propagating changes.

### 5. Delta review

Each proposed update should be classified as:

- safe automatic update;
- likely update requiring confirmation;
- authority-sensitive change;
- ambiguous change;
- potential continuity break;
- intentional retcon candidate.

The author or editor reviews only the affected area, not the entire graph.

### 6. Incremental evaluation

Queries connected to changed records are rerun automatically.

The system reports:

- previously passing queries now failing;
- changed answers;
- evidence spans that no longer exist;
- newly unsupported claims;
- continuity candidates introduced or resolved;
- marketing claims affected by revision.

## Deliverables

Act V produces:

- manuscript diff engine;
- scene-lineage map;
- semantic delta ledger;
- dependency graph;
- revision review queue;
- incremental graph builder;
- targeted evaluation rerun;
- revision impact report;
- version comparison browser;
- rollback and provenance system.

## Completion condition

Act V is complete when manuscript revision no longer requires a full manual reconstruction of story state, and every graph change can be traced to a source revision and an explicit authority decision.

## Class lesson

Act V demonstrates the final transformation: the Story Graph becomes living infrastructure. It remembers not only the story, but how the story changed, why the graph changed with it, and which consequences still require human judgment.

---

# How the Acts Relate

The five acts form a maturity sequence:

1. **Act I proves representation.**
2. **Act II establishes authority.**
3. **Act III enables daily use.**
4. **Act IV expands scope.**
5. **Act V maintains the system through change.**

The progression can also be described as:

> **Extract → Ratify → Operate → Federate → Maintain**

No act makes the author unnecessary. The purpose of the system is the opposite. It reduces clerical memory burden so the author can make better creative decisions with clearer evidence and fewer accidental contradictions.

# Current Position

The Book 3 project has completed **Act I** as a technical pilot.

The next formal stage is:

> **Act II, Phase 10 — Author Ratification and Canon Freeze**

That phase should begin with the review-deferred decision queue, evidence verification, continuity adjudication, and the remaining artifact-migration cleanup. The graph should not be promoted from provisional authority to canonical authority until those decisions are recorded.
