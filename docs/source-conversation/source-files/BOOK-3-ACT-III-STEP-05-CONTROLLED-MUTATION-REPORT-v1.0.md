# Book 3 Act III — Step 05 Controlled Mutation Vocabulary

## Purpose

Replace generic write access with named, validated, authority-aware actions.

## Results

- controlled actions defined: **{…}**
- approval states defined: **{…}**
- actions requiring author authority: **{…}**
- actions that create proposals only: **{…}**

## Governance

Every mutation specifies:

- valid target types;
- permitted roles;
- required inputs;
- preconditions;
- impact analysis;
- approval authority;
- versioning;
- tests;
- rollback behavior.

## Critical rule

Opening a continuity issue does not confirm an error.

Proposing a change does not modify canon.

Approving a change does not promote it until application and validation succeed.

## Outputs

- `BOOK-3-ACT-III-CONTROLLED-ACTION-VOCABULARY-v1.0.csv`
- `BOOK-3-ACT-III-CHANGE-APPROVAL-STATE-MACHINE-v1.0.csv`
- `BOOK-3-ACT-III-CHANGE-PROPOSAL-SCHEMA-v1.0.json`

## Next step

Build the operational dependency index from the frozen canon package and test it with controlled revision scenarios.
