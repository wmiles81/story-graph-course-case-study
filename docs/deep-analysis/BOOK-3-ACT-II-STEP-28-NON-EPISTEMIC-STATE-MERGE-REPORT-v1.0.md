# Book 3 Act II — Step 28 Non-Epistemic State Merge

## Purpose

Merge all corrected-scene records that were removed from the epistemic layer into a normalized state candidate.

## Inputs

- `BOOK-3-ACT-II-NON-EPISTEMIC-STATE-ROUTING-v1.0.csv`
- `BOOK-3-ACT-II-DECISION-STATE-ADDITIONS-v1.0.csv`
- `BOOK-3-ACT-II-ARC-STATE-ADDITIONS-v1.0.csv`

## Results

- state records created: **25**
- duplicate state IDs: **0**
- exact duplicate states: **0**
- missing scene references: **0**

## State counts

- allegiance_state: **1**
- character_arc: **9**
- collective_arc: **1**
- decision_and_arc: **1**
- decision_state: **3**
- identity_arc: **1**
- leadership_arc: **1**
- mixed_state: **1**
- other_state: **1**
- relationship_arc: **2**
- relationship_state: **1**
- scene_emotional_state: **1**
- tactical_state: **1**
- threat_state: **1**

## Semantic result

The following are now represented outside the knowledge graph:

- operational choices;
- romantic commitment;
- leadership progression;
- identity and vulnerability shifts;
- alliance and allegiance changes;
- threat escalation;
- tactical reframing;
- emotional transitions.

## Outputs

- `BOOK-3-NON-EPISTEMIC-STATE-ACT-II-CANDIDATE-v1.0.csv`
- `BOOK-3-ACT-II-NON-EPISTEMIC-STATE-INTEGRITY-ISSUES-v1.0.csv`

## Next step

Recalculate continuity candidates against the repaired scene, assertion, epistemic, custody, promise, and state candidates.
