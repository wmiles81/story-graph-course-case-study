# Act IV — The Series Graph Progress Record

## Purpose

Act IV federates independently versioned book graphs into a series-level Story Graph.

Act I proved that a novel could be modeled.

Act II ratified and froze one book's canon.

Act III turned the frozen graph into an operational author tool.

Act IV asks:

> How do multiple book graphs combine without losing book-specific truth, spoiler boundaries, revision history, or series continuity?

## Governing Baseline

### Book 3

- Canon version: `BOOK-3-CANON-v2.0`
- Status: author-ratified and source-grounded
- Operational system: Story Graph OS Prototype v0.1.0
- Scenes: 153
- Entities: 91
- Propositions: 160
- Assertions: 196
- Custody records: 49
- Promise lifecycle rows: 69
- Analytical states: 25
- Continuity adjudications: 26

## Act IV Core Problems

### 1. Cross-book entity identity

The same person, place, organization, object, or rule may appear under:

- different names;
- different aliases;
- different statuses;
- different roles;
- different levels of reader knowledge;
- changed or retconned attributes.

Act IV must determine when two book-level entities are:

- the same series entity;
- distinct entities with similar names;
- variants or manifestations;
- intentionally ambiguous;
- superseded by a retcon.

### 2. Series chronology

Book order is not necessarily story-time order.

The Series Graph must represent:

- publication order;
- narrative order;
- story-time order;
- flashbacks;
- overlapping books;
- prequels;
- epilogues;
- time jumps;
- uncertain dates.

### 3. Spoiler-aware querying

A series-level answer must respect the reader's scope.

Examples:

- What is known after Book 1?
- What may marketing copy reveal before Book 3?
- When does the reader first learn a hidden identity?
- Which facts are safe for a Book 2 recap?

### 4. Cross-book knowledge

A character may learn a fact in one book and act on it in another.

The graph must preserve:

- holder;
- acquisition scene;
- book;
- persistence;
- forgetting or concealment;
- false belief;
- reader knowledge;
- series reveal order.

### 5. Series promises and payoffs

Some promises begin and end within one book.

Others:

- span several books;
- change ownership;
- appear dormant;
- receive partial payoffs;
- become retconned;
- are deliberately deferred.

### 6. World-rule inheritance

A book may:

- establish a rule;
- apply it;
- reveal an exception;
- contradict it;
- revise it;
- expose a character's false understanding of it.

The Series Graph must separate genuine world-rule change from newly revealed context.

### 7. Retcons and revision authority

Later books may clarify or replace earlier canon.

Act IV must record:

- original fact;
- later correction;
- whether the change is in-world revelation or authorial retcon;
- affected books;
- affected scenes;
- reader-facing implications;
- continuity consequences.

## Operating Principles

### Book graphs remain independently versioned

Federation does not erase book-level canon.

### Series entities do not replace local entities

Each book retains local IDs and local context.

Series IDs provide cross-book identity and navigation.

### Spoiler scope is a first-class field

Every series query requires an allowed book or reveal ceiling.

### Later knowledge does not leak backward

A fact revealed in Book 4 cannot answer a Book 1-scoped query.

### Retcons are explicit records

No later fact silently overwrites earlier published canon.

### Series-level analysis remains distinct from manuscript fact

Cross-book arc interpretation and series promises use governed analytical layers.

---

# Planned Workstreams

## Workstream A — Federation Ontology

Define:

- series;
- book;
- edition;
- book-local entity;
- series entity;
- identity mapping;
- series proposition;
- series assertion;
- spoiler scope;
- retcon;
- cross-book promise;
- world rule.

## Workstream B — Cross-Book Identity Resolution

Create rules for:

- exact identity;
- alias identity;
- uncertain identity;
- split identity;
- merged identity;
- role succession;
- manifestation or form;
- intentional ambiguity.

## Workstream C — Series Chronology

Model:

- publication order;
- narrative order;
- story-time intervals;
- overlap;
- uncertainty;
- relative chronology.

## Workstream D — Spoiler-Aware Querying

Create query contracts for:

- book-limited canon;
- recap-safe facts;
- marketing-safe claims;
- reader knowledge by book;
- character knowledge by book;
- series-wide truth.

## Workstream E — Series Promises and World Rules

Federate:

- unresolved promises;
- inherited stakes;
- recurring objects;
- series antagonists;
- world rules;
- exceptions;
- long arcs.

## Workstream F — Retcon Governance

Define:

- clarification;
- revelation;
- contradiction;
- intentional retcon;
- accidental continuity error;
- edition-level correction.

## Workstream G — Series Graph Prototype

Extend the Story Graph Operating System with:

- book selector;
- series scope;
- spoiler ceiling;
- cross-book entity view;
- series timeline;
- series promise board;
- retcon ledger.

---

# Initial Deliverables

1. Act IV federation requirements
2. series ontology
3. book-to-series identity mapping contract
4. spoiler-scope model
5. series chronology contract
6. retcon and world-rule governance
7. cross-book promise model
8. Series Graph operational views
9. series evaluation suite
10. implementation assessment

---

# Current Status

Act IV has started.

## Next Step

Inventory the available book-level graphs and define the minimum federation contract that allows Book 3 to participate in a future multi-book series graph without altering its frozen canon.
