# Book 3 Act III — Step 04 Revision-Impact Contract

## Purpose

Define how the Story Operating System evaluates a proposed manuscript or canon change before any mutation occurs.

## Impact classes

- impact classes defined: **{…}**
- dependency traversal rules: **{…}**

## Required impact output

Every proposal must identify:

- direct target;
- direct affected records;
- downstream dependencies;
- invalidated tests;
- warnings;
- authority requirement;
- recommendation;
- versioning and supersession requirements.

## Safety rule

No proposal may be approved without an impact report.

A declared copyedit is not assumed semantically harmless. It must pass an equivalence check or be escalated.

## Outputs

- `BOOK-3-ACT-III-REVISION-IMPACT-CLASSIFICATION-v1.0.csv`
- `BOOK-3-ACT-III-DEPENDENCY-TRAVERSAL-RULES-v1.0.csv`
- `BOOK-3-ACT-III-REVISION-IMPACT-REPORT-SCHEMA-v1.0.json`

## Next step

Define the controlled-action vocabulary and approval state machine used to turn an impact-reviewed proposal into a versioned canon update.
