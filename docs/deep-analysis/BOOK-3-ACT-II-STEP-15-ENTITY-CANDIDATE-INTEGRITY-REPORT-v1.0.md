# Book 3 Act II — Step 15 Repaired Entity Candidate and Reference Integrity

## Purpose

Build the repaired Act II entity-registry candidate and test every surviving or rebuilt assertion for dangling entity references.

## Entity candidate

- Act I entities: **67**
- Unsupported entities removed: **5**
- Direct-manuscript entities added: **18**
- Act II candidate entities: **80**
- Duplicate entity IDs: **0**
- Duplicate canonical names: **0**

## Assertion candidate

- Act I assertions retained: **111**
- Stale Act I assertions removed: **20**
- Rebuilt scene-event assertions added: **28**
- Candidate assertions: **139**

## Reference audit

Each assertion subject was checked against:

- canonical entity IDs;
- canonical names;
- aliases;
- allowed nonentity subjects such as `CANON`.

Object values beginning with `ENT-` were checked against the repaired registry IDs.

## Results

- Assertions audited: **139**
- Assertions with unresolved entity references: **17**

Unresolved rows remain outside the canon-freeze candidate until their subject or object references are normalized.

## Outputs

- `BOOK-3-ENTITY-REGISTRY-ACT-II-CANDIDATE-v1.0.csv`
- `BOOK-3-ASSERTIONS-ACT-II-CANDIDATE-v1.0.csv`
- `BOOK-3-ACT-II-ASSERTION-ENTITY-REFERENCE-AUDIT-v1.0.csv`
- `BOOK-3-ACT-II-DANGLING-ENTITY-REFERENCES-v1.0.csv`

## Next step

Resolve any remaining dangling references, then normalize the knowledge and belief rebuild queue into individual epistemic assertions using repaired entity identifiers.
