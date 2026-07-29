# Book 3 Act II — Step 17 Normalization Application and Integrity Rerun

## Purpose

Apply all Step 16 subject-normalization decisions to the Act II entity and assertion candidates, route analysis-only records out of the story-world graph, split compound assertions, and rerun integrity.

## Inputs

- `BOOK-3-ENTITY-REGISTRY-ACT-II-CANDIDATE-v1.0.csv`
- `BOOK-3-ASSERTIONS-ACT-II-CANDIDATE-v1.0.csv`
- `BOOK-3-ENTITY-REGISTRY-ACT-II-REFERENCE-ADDITIONS-v1.1.csv`
- `BOOK-3-ACT-II-DANGLING-REFERENCE-NORMALIZATION-v1.0.csv`

## Applied changes

- analysis-only assertions routed to sidecar: **{…}**
- assertion subject normalizations or rewrites: **{…}**
- compound assertion expansions: **{…}**
- Step 16 entities added to registry: **{…}**

## Candidate totals

- Act II entity candidate v1.1: **{…}**
- Act II assertion candidate v1.1: **{…}**

## Integrity results

- unresolved entity references: **{…}**
- duplicate assertion IDs: **{…}**
- exact duplicate assertion records: **{…}**

## Relationship rewrite

The compound subject `Jonah Harrow and Margot Vance` was replaced with a directed assertion:

`ENT-CHAR-0001 IN_RELATIONSHIP_WITH ENT-CHAR-0002`

The scene and source context remain attached to the assertion. This avoids treating a pair of characters as a single entity.

## Authority result

The story-world assertion candidate now contains only canonical entity subjects, permitted nonentity subjects, and valid entity-object references.

Analytical interpretations remain available in a dedicated sidecar rather than masquerading as story-world facts.

## Outputs

- `BOOK-3-ENTITY-REGISTRY-ACT-II-CANDIDATE-v1.1.csv`
- `BOOK-3-ASSERTIONS-ACT-II-CANDIDATE-v1.1.csv`
- `BOOK-3-ACT-II-ANALYSIS-ASSERTION-SIDECAR-v1.0.csv`
- `BOOK-3-ACT-II-ASSERTION-REWRITE-LINEAGE-v1.0.csv`
- `BOOK-3-ACT-II-ASSERTION-INTEGRITY-RERUN-v1.1.csv`

## Next step

Normalize the 28 corrected-scene knowledge and belief summaries into individual epistemic claims, retaining only claims with identifiable holders and manuscript-supported acquisition context.
