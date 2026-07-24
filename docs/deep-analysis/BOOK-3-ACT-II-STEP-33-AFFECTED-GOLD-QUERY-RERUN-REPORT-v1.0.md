# Book 3 Act II — Step 33 Affected Gold-Query Rerun

## Purpose

Rerun every gold or batch query invalidated by rejected propositions, superseded scene summaries, corrected custody, or repaired continuity state.

## Inputs

- `BOOK-3-ACT-II-INVALIDATED-QUERY-RESULTS-v1.0.csv`
- corrected Chapters 13–18 scene candidate;
- repaired proposition and assertion candidates;
- repaired custody and promise candidates;
- final Act II continuity candidate.

## Coverage

- invalidated source rows: **8**
- unique invalidated query IDs: **4**
- rerun or retirement records produced: **5**
- missing invalidated query IDs: **0**

## Results

- PASS_CORRECTED: **2**
- PASS_NEW: **1**
- RETIRED: **2**

## Query policy

A malformed question is not counted as a failed graph answer.

Queries whose premises depend on events or objects absent from the manuscript are:

1. marked `RETIRED_INVALID_QUERY`; or
2. rewritten into a manuscript-supported question and rerun.

Historical scores remain preserved for provenance but are excluded from the Act II denominator.

## Major corrections

- the new strategic problem is Magisterium occupation, not a hidden surveillance compromise;
- the immediate Chapters 16–18 target is the resort generator and Emitter, not Sterling's master archive;
- no compromised-tracker object exists;
- KV-0001 is dismissed as an invalid-premise continuity candidate.

## Outputs

- `BOOK-3-ACT-II-AFFECTED-GOLD-QUERY-RERUN-v1.0.csv`

## Next step

Recalculate the full evaluation denominator, preserving unaffected results and replacing or retiring invalidated questions, then generate the Act II evaluation summary.
