# Book 3 Act II — Step 01 Ratification Inventory Report

## Purpose

This step identifies every existing ratification and adjudication queue, classifies the authority risk of each queue, and determines which records may proceed automatically without being mislabeled as author-approved interpretation.

## Inputs

- Entity ratification table
- Relationship ratification table
- Knowledge ratification table
- Timeline and logistics ratification table
- Chapter canon-commit ratification table
- Continuity issue adjudication table
- Open-loop adjudication table
- Narrative-physics adjudication table
- Review-deferred ratification policy
- Reconciled registries and provisional Story Graph

## Inventory

The principal queues contain 247 records:

- 67 entities
- 15 relationships
- 24 knowledge states
- 68 timeline and logistics records
- 30 chapter canon commits
- 26 continuity candidates
- 13 open loops
- 20 narrative-physics states

## Automatic-processing rule

Only records that are structural, directly evidenced, and noninterpretive may be ratified automatically.

The first automatic class is the entity registry because canonical identity, entity type, aliases, first appearance, and current status can be verified against the reconciled registry without deciding thematic meaning, emotional trend, ambiguity, or authorial intent.

The following remain evidence-review queues:

- relationship edges and trends;
- knowledge acquisition and embargo timing;
- inferred timeline wording;
- chapter canon-commit summaries;
- continuity classifications;
- promise and open-loop resolution;
- narrative-physics anchors.

## Authority rule

An automatic decision is recorded as `SYSTEM_RATIFIED_STRUCTURAL`, not `AUTHOR_RATIFIED`.

Author authority remains required for interpretive and canon-freeze decisions.

## Outputs

- `BOOK-3-ACT-II-RATIFICATION-INVENTORY-v1.0.csv`
- classification of each queue by automatic-processing eligibility
- authorization to begin structural entity ratification

## Next step

Run automated structural validation over all 67 entity records, produce an exception report, and ratify only records that pass every identity and reference check.
