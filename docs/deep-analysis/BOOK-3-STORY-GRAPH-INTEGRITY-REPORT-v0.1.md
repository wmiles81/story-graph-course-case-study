# BOOK 3 STORY GRAPH INTEGRITY REPORT v0.1

## Executive result

The integrity-cleanup pass is complete.

### Source totals

- Parser scene skeleton: **153 scenes**
- Validated master scene ledger: **132 scenes**
- Master scene contexts: **148 rows**
- Entity registry: **30 entities**
- Proposition registry: **122 propositions**
- Assertions: **131**
- Promise lifecycle events: **50**
- Custody states: **38**
- Arc states: **27**

### Primary coverage discrepancy

- Parser scenes absent from the validated master: **21**
- Validated-master scenes absent from parser skeleton: **0**

The difference between 153 parser scenes and 132 validated master scenes is therefore
not a cosmetic total mismatch. It is a concrete set of scene IDs that must be
reconciled before generating the canonical `BOOK-3-Story-Graph.md`.

### Integrity issues

- Total open issues: **141**
- Critical: **52**
- Major: **89**

## Issues by category

- **entity reference:** 31
- **predicate normalization:** 73
- **scene context:** 16
- **scene coverage:** 21

## Key findings

### 1. Scene coverage must be reconciled first

The parser and validated master do not represent the same scene set. Missing master
scenes cannot simply be discarded because the target Story Graph's Canon Commit Log
and Timeline depend on complete chapter coverage.

### 2. Scene-context cardinality is not yet clean

The target model expects one current scene context per scene. Missing, duplicated, or
orphaned context rows must be resolved.

### 3. Entity references are not fully normalized

The audit found references using registry-like IDs that do not resolve against the
current entity registry. These must be added, merged, or rewritten before validation.

### 4. Assertion predicates exceed the compact Story Graph ontology

This is expected. The analytical graph contains predicates that belong in:

- Knowledge States;
- Open Loops & Guns;
- Logistics;
- Canon Commit Log;
- evidence or issues sidecars.

They should not all become Relationship edges.

### 5. Promise lifecycle requires identity normalization

The migration needs one stable row per narrative promise, not one row per lifecycle
event. Possible duplicates must be collapsed or explicitly distinguished.

### 6. SPE now resolves the anchor-catalog warning

The SPE anchor catalog is present. Book 3's prose arc states, however, are not yet
canonical anchor IDs. They must be mapped deliberately rather than copied verbatim
into `Physics State`.

## Files produced

- `BOOK-3-STORY-GRAPH-INTEGRITY-REPORT-v0.1.md`
- `BOOK-3-STORY-GRAPH-INTEGRITY-ISSUES-v0.1.csv`
- `BOOK-3-PREDICATE-NORMALIZATION-v0.1.csv`
- `BOOK-3-ENTITY-REFERENCE-AUDIT-v0.1.csv`
- `BOOK-3-PROMISE-NORMALIZATION-v0.1.csv`
- `BOOK-3-SPE-ANCHOR-MAPPING-AUDIT-v0.1.csv`

## Gate decision

**Do not generate the canonical Book 3 Story Graph yet.**

The next controlled step is scene-coverage reconciliation, followed by entity and
context cleanup. Otherwise the new graph would be elegantly formatted and
structurally incomplete, which is one of software's more traditional achievements.
