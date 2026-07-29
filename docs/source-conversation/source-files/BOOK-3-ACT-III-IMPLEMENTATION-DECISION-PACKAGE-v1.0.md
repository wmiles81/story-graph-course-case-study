# Book 3 Act III — Product Implementation Decision Package

## Current status

The Story Operating System is fully specified and prototyped at the data-contract level.

Completed:

- role model;
- operating requirements;
- query contract;
- evidence schema;
- dashboard specification;
- revision-impact contract;
- controlled action vocabulary;
- 3,228-edge dependency index;
- six materialized operational views;
- natural-language query prototype;
- safe-failure rules;
- runtime service and event contracts;
- 39/39 operational tests;
- 10/10 safe-failure tests;
- complete requirements traceability.

The remaining question is what software product to build.

---

## Decision 1 — Product surface

### Recommended

**LOCAL WEB APP**

A dedicated browser application best supports:

- dashboard layouts;
- evidence expansion;
- dependency inspection;
- revision-impact workflows;
- role-oriented navigation;
- later controlled mutations.

Notion remains useful for class documentation but is awkward as the primary runtime for graph traversal and versioned operational state.

### Options

- NOTION FIRST
- LOCAL WEB APP
- VS CODE EXTENSION
- HYBRID

---

## Decision 2 — Primary first role

### Recommended

**AUTHOR**

Build the first workflow around:

- natural-language canon questions;
- scene briefs;
- active promises;
- character and relationship arcs;
- continuity warnings;
- revision-impact proposals.

Continuity and editorial views can follow from the same underlying contracts.

### Options

- AUTHOR
- CONTINUITY EDITOR
- DEVELOPMENTAL EDITOR
- MULTI-ROLE

---

## Decision 3 — Version 1 mutation scope

### Recommended

**READ ONLY PLUS PROPOSALS**

Version 1 should allow:

- query;
- inspection;
- revision proposals;
- impact reports;
- invalidated-test discovery.

It should not directly mutate frozen canon.

Controlled canon writes add approval workflows, regeneration, validation, versioning, and rollback. Those belong after the read and proposal workflows prove usable.

### Options

- READ ONLY
- READ ONLY PLUS PROPOSALS
- CONTROLLED CANON WRITES

---

## Decision 4 — Operational storage

### Recommended

**SQLITE**

SQLite provides:

- local deployment;
- strong joins;
- indexed lookup;
- simple backups;
- structured migrations;
- no server administration;
- a clear path to PostgreSQL later.

The source CSV files remain immutable freeze artifacts and import into SQLite as operational tables.

### Options

- CSV FILES
- SQLITE
- POSTGRESQL
- GRAPH DATABASE

A native graph database remains possible later, but the current ontology includes intervals, evidence, authority, and lifecycle records that are easier to govern initially in relational tables.

---

## Decision 5 — Act III implementation depth

### Recommended

**BUILD WORKING PROTOTYPE**

The current package is already sufficient as a formal specification. Continuing Act III should now produce an operational application rather than another stack of documents describing one.

### Options

- SPECIFICATION COMPLETE
- BUILD WORKING PROTOTYPE
- BUILD CLASS DEMO

---

# Recommended approval block

1. Product surface: **LOCAL WEB APP**
2. Primary role: **AUTHOR**
3. Mutation scope: **READ ONLY PLUS PROPOSALS**
4. Storage: **SQLITE**
5. Implementation depth: **BUILD WORKING PROTOTYPE**

With those approvals, the next automatic work becomes:

1. application architecture;
2. SQLite schema and import pipeline;
3. author dashboard;
4. query and evidence service;
5. scene, knowledge, custody, promise, and continuity views;
6. revision-impact proposal workflow;
7. application-level tests;
8. class demonstration package.
