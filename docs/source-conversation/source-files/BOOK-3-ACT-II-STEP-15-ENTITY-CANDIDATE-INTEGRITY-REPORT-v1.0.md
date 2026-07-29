# Book 3 Act II — Step 15 Repaired Entity Candidate and Reference Integrity

## Purpose

Build the repaired Act II entity-registry candidate and test every surviving or rebuilt assertion for dangling entity references.

## Entity candidate

- Act I entities: **{…}**
- Unsupported entities removed: **{…}**
- Direct-manuscript entities added: **{…}**
- Act II candidate entities: **{…}**
- Duplicate entity IDs: **{…}**
- Duplicate canonical names: **{…}**

## Assertion candidate

- Act I assertions retained: **{…}**
- Stale Act I assertions removed: **{…}**
- Rebuilt scene-event assertions added: **{…}**
- Candidate assertions: **{…}**

## Reference audit

Each assertion subject was checked against:

- canonical entity IDs;
- canonical names;
- aliases;
- allowed nonentity subjects such as `CANON`.

Object values beginning with `ENT-` were checked against the repaired registry IDs.

## Results

- Assertions audited: **{…}**
- Assertions with unresolved entity references: **{…}**

Unresolved rows remain outside the canon-freeze candidate until their subject or object references are normalized.

## Outputs

- `BOOK-3-ENTITY-REGISTRY-ACT-II-CANDIDATE-v1.0.csv`
- `BOOK-3-ASSERTIONS-ACT-II-CANDIDATE-v1.0.csv`
- `BOOK-3-ACT-II-ASSERTION-ENTITY-REFERENCE-AUDIT-v1.0.csv`
- `BOOK-3-ACT-II-DANGLING-ENTITY-REFERENCES-v1.0.csv`

## Next step

Resolve any remaining dangling references, then normalize the knowledge and belief rebuild queue into individual epistemic assertions using repaired entity identifiers.
