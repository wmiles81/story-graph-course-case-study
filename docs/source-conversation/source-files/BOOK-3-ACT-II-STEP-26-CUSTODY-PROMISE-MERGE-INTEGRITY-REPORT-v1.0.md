# Book 3 Act II — Step 26 Custody and Promise Candidate Merge

## Purpose

Merge corrected Chapters 13–18 custody and promise records into new Act II candidates while preserving valid earlier and later history.

## Custody merge

- Act I custody rows: **{…}**
- stale rows removed: **{…}**
- rebuilt rows added: **{…}**
- custody candidate rows: **{…}**
- interval or terminal-state issues: **{…}**

## Promise merge

- Act I promise lifecycle rows: **{…}**
- late-batch rows removed: **{…}**
- rebuilt rows added: **{…}**
- promise candidate rows: **{…}**
- lifecycle integrity issues: **{…}**

## Integrity rules

Custody checks looked for:

- overlapping intervals;
- records beginning after destruction;
- contradictory terminal states.

Promise checks looked for:

- exact duplicate lifecycle rows;
- payoff before introduction;
- reactivation after fulfillment.

## Outputs

- `BOOK-3-CUSTODY-STATE-ACT-II-CANDIDATE-v1.0.csv`
- `BOOK-3-PROMISE-LIFECYCLE-ACT-II-CANDIDATE-v1.0.csv`
- `BOOK-3-ACT-II-CUSTODY-INTEGRITY-ISSUES-v1.0.csv`
- `BOOK-3-ACT-II-PROMISE-INTEGRITY-ISSUES-v1.0.csv`

## Next step

Resolve any mechanical integrity exceptions, merge non-epistemic state records into relationship and arc candidates, and recalculate continuity findings against the repaired scene, assertion, custody, and promise layers.
