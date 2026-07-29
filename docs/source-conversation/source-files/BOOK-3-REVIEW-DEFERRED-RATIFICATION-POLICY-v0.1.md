# BOOK 3 REVIEW-DEFERRED RATIFICATION POLICY v0.1

## Purpose

Move the Story Graph project forward without requiring completion of the browser-based
ratification interfaces.

## Decision rule

The current provisional graph remains authoritative for technical work, but not fully
author-ratified canon.

### Automatically accepted as provisional

- all mechanically valid entity rows;
- all core relationship rows;
- all existing timeline rows;
- all existing logistics rows;
- all existing canon-commit rows;
- all SPE recommendations for missing chapters;
- all open-loop recommendations except those explicitly marked REVIEW;
- all continuity recommendations that classify an item as model/data quality rather
  than a confirmed manuscript error.

### Remain explicitly unresolved

- `pr-b03-0019` safehouse tracking-source mechanism;
- any continuity issue requiring direct source adjudication;
- any entity still labeled provisional;
- any knowledge-state row supported only by machine-selected evidence;
- any timing row lacking explicit elapsed-time proof.

## Canon status

The resulting graph status is:

`review-deferred provisional canon`

This means it may be used for:

- continued system development;
- validation;
- query testing;
- browser reporting;
- Book 4/series migration design;
- continuity analysis.

It may not be represented as fully author-ratified canon.

## Next project stage

1. Generate Story Graph v0.2 under this policy.
2. Run final structural validation.
3. Update the browser report to use the reconciled 153-scene graph.
4. Add Issues and Open Loops views.
5. Run the planned gold query set.
6. Produce a pilot-completion assessment.
