# Book 3 Act III — Step 12 Safe Failure and Ambiguity Handling

## Purpose

Test whether the Story Operating System fails safely when a question is ambiguous, underspecified, unsupported, spoiler-sensitive, or asks for unauthorized mutation.

## Coverage

- cases: **10**
- PASS: **10**
- FAIL: **0**

## Behaviors validated

- candidate return for ambiguous titles;
- as-of-scene protection for knowledge queries;
- unsupported-premise correction;
- honest not-found response;
- explicit model limitations;
- analytical-canon labeling;
- spoiler warnings;
- proposal rather than unauthorized mutation;
- warning-versus-error distinction;
- approved copyedit equivalence.

## Result

The safe-failure contract passes all defined cases.

## Outputs

- `BOOK-3-ACT-III-SAFE-FAILURE-TEST-CASES-v1.0.csv`
- `BOOK-3-ACT-III-SAFE-FAILURE-TEST-RESULTS-v1.0.csv`

## Next step

Define the runtime dashboard and service data contracts that connect query parsing, materialized views, evidence assembly, revision impact, and controlled actions.
