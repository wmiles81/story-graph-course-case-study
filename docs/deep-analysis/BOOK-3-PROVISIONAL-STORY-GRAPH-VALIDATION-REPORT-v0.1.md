# BOOK 3 PROVISIONAL STORY GRAPH VALIDATION REPORT v0.1

## Mode

**Reverse-engineer + migration + validation**

The graph was generated from:

- the Phase 8 manuscript candidate;
- the reconciled 153-scene ledger;
- the reconciled 153 scene-context rows;
- the reconciled entity and custody registries;
- the routed assertion table;
- the promise lifecycle and arc-state tables;
- the installed SPE anchor catalog.

## Scope

- Single-book graph
- Chapters processed: **1–30**
- `current-canon-chapter`: **30**
- Authority: **provisional**, pending author ratification

## Validator result

- **Errors: 0**
- **Warnings: 33**
- Validation attempts used: **2 of 3 permitted**

The first pass found undeclared analytical holders and three physical-state logistics
objects. Those structural errors were corrected without changing story facts.

## Warnings, verbatim

- `Open Loops & Guns [pr-b03-0007]: OVERDUE — must fire by ch30, canon is at ch30, still UNFIRED`
- `Open Loops & Guns [pr-b03-0014]: OVERDUE — must fire by ch30, canon is at ch30, still UNFIRED`
- `Open Loops & Guns [pr-b03-0016]: OVERDUE — must fire by ch30, canon is at ch30, still UNFIRED`
- `Open Loops & Guns [pr-b03-0018]: OVERDUE — must fire by ch30, canon is at ch30, still UNFIRED`
- `Open Loops & Guns [pr-b03-0019]: OVERDUE — must fire by ch30, canon is at ch30, still UNFIRED`
- `Open Loops & Guns [pr-b03-0020]: OVERDUE — must fire by ch30, canon is at ch30, still UNFIRED`
- `Open Loops & Guns [pr-b03-0021]: OVERDUE — must fire by ch30, canon is at ch30, still UNFIRED`
- `Open Loops & Guns [pr-b03-0022]: OVERDUE — must fire by ch30, canon is at ch30, still UNFIRED`
- `Open Loops & Guns [pr-b03-0023]: OVERDUE — must fire by ch30, canon is at ch30, still UNFIRED`
- `Open Loops & Guns [pr-b03-0024]: OVERDUE — must fire by ch30, canon is at ch30, still UNFIRED`
- `Open Loops & Guns [pr-b03-0026]: OVERDUE — must fire by ch30, canon is at ch30, still UNFIRED`
- `Open Loops & Guns [pr-b03-0028]: OVERDUE — must fire by ch30, canon is at ch30, still UNFIRED`
- `Open Loops & Guns [pr-series-0001]: OVERDUE — must fire by ch30, canon is at ch30, still UNFIRED`
- `Physics State: no rows for committed ch2`
- `Physics State: no rows for committed ch3`
- `Physics State: no rows for committed ch5`
- `Physics State: no rows for committed ch7`
- `Physics State: no rows for committed ch8`
- `Physics State: no rows for committed ch10`
- `Physics State: no rows for committed ch11`
- `Physics State: no rows for committed ch12`
- `Physics State: no rows for committed ch13`
- `Physics State: no rows for committed ch16`
- `Physics State: no rows for committed ch17`
- `Physics State: no rows for committed ch19`
- `Physics State: no rows for committed ch20`
- `Physics State: no rows for committed ch21`
- `Physics State: no rows for committed ch22`
- `Physics State: no rows for committed ch23`
- `Physics State: no rows for committed ch24`
- `Physics State: no rows for committed ch25`
- `Physics State: no rows for committed ch26`
- `Physics State: no rows for committed ch28`

## Interpretation of warnings

### Open-loop warnings

Thirteen promise rows remain marked `UNFIRED` at Chapter 30. These warnings are
useful. They indicate one of three possibilities:

1. the promise is genuinely unresolved;
2. the lifecycle table failed to record its payoff;
3. it is a series-level obligation that should have a later deadline.

They were not silently changed merely to achieve a clean validator screen.

### Physics-state warnings

The graph contains Physics State rows only where the current analytical model
recorded a meaningful state transition. The validator warns because twenty chapters
lack any Physics State row.

This is a coverage warning, not a schema failure. Filling those chapters responsibly
requires a chapter-by-chapter SPE pass rather than copying the nearest neighboring
anchor.

## Files in the package

- `BOOK-3-Story-Graph-PROVISIONAL-v0.1.md`
- `BOOK-3-Story-Graph-Evidence-v0.1.csv`
- `BOOK-3-Story-Graph-Reader-Context-v0.1.csv`
- `BOOK-3-Story-Graph-Issues-v0.1.csv`
- `BOOK-3-Story-Graph-Migration-Trace-v0.1.csv`
- `BOOK-3-PROVISIONAL-STORY-GRAPH-VALIDATION-REPORT-v0.1.md`

## Current conclusion

The first Book 3 Story Graph now conforms mechanically to Story Graph Ontology v1
and validates against the installed SPE catalog with **zero errors**.

It is not yet author-ratified canon. The most valuable next pass is not cosmetic
warning removal. It is adjudication of the thirteen open-loop warnings and completion
of the missing chapter-level Physics State readings.
