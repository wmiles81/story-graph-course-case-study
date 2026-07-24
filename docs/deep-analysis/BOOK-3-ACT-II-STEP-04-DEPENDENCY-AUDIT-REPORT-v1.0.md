# Book 3 Act II — Step 04 Dependency Audit and Supersession Plan

## Purpose

Trace every downstream record that depends on the two knowledge claims rejected during direct manuscript verification.

## Rejected source claims

- `P-B03-000069` — resistance identifies a surveillance or intelligence compromise in `B03-C15-S02`
- `P-B03-000077` — rescued witness reveals Sterling's command site and next move in `B03-C17-S04`

## Inputs

- all Book 3 CSV artifacts in the Act I workspace;
- Step 03 knowledge-ratification results;
- direct manuscript findings for the two cited scenes.

## Results

- Dependent CSV records found: **63**
- Files affected: **44**

Affected classes include scene summaries, assertions, continuity candidates, promise records, query tests, custody notes, and gold-evaluation outputs.

## Preservation policy

Historical Act I artifacts are not edited in place.

Each affected record receives a superseding Act II disposition:

- reject or rebuild unsupported assertions;
- supersede inaccurate scene summaries;
- dismiss or recalculate dependent continuity candidates;
- recalculate promise and query dependencies;
- rerun affected evaluation questions;
- verify any custody record independently before retaining it.

## Disposition counts

- DISMISS_OR_RECALCULATE_ISSUE: **5**
- RECALCULATE_BATCH_QUERY: **4**
- RECALCULATE_PROMISE_DEPENDENCY: **4**
- RECALCULATE_QUERY_RESULT: **4**
- REJECT_OR_REBUILD_ASSERTION: **8**
- REVIEW_DEPENDENCY: **17**
- SUPERSEDE_SCENE_SUMMARY_OR_CONTEXT: **18**
- VERIFY_CUSTODY_NOTE_INDEPENDENTLY: **3**

## Outputs

- `BOOK-3-ACT-II-DEPENDENCY-AUDIT-v1.0.csv`
- supersession and recalculation plan for every affected downstream record

## Next step

Build corrected scene records for `B03-C15-S02` and `B03-C17-S04` directly from their bounded manuscript passages, then generate a formal supersession ledger for dependent records.
