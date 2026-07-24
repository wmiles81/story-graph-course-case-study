# Book 3 Act III — Step 06 Operational Dependency Index, Repaired

## Initial result

- dependency edges: **1724**
- indexed targets: **479**
- initial dangling targets: **4**

## Repair

All four apparent dangling targets were rejected historical propositions referenced by continuity audit records.

They were reclassified from active `proposition` targets to:

`historical_rejected_proposition`

This preserves provenance without implying the propositions remain in active canon.

## Final result

- active-canon dangling targets: **0**
- historical rejected references preserved: **4**

## Outputs

- `BOOK-3-ACT-III-OPERATIONAL-DEPENDENCY-INDEX-v1.1.csv`
- `BOOK-3-ACT-III-DEPENDENCY-SUMMARY-v1.1.csv`
- `BOOK-3-ACT-III-DEPENDENCY-INDEX-REPAIRS-v1.0.csv`
- `BOOK-3-ACT-III-DEPENDENCY-INDEX-ISSUES-v1.1.csv`

## Next step

Run controlled revision scenarios against the repaired dependency index.
