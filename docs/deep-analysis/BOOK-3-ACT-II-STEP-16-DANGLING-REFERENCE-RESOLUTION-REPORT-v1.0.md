# Book 3 Act II — Step 16 Dangling-Reference Resolution

## Purpose

Resolve all 17 assertion subjects that failed the repaired entity-reference audit.

## Classification

### Analysis-sidecar records

Three assertions use `ANALYST` as their subject. They are analytical interpretations rather than story-world entity claims and are routed out of the canonical assertion graph.

### Missing manuscript entities

Nine canonical entities were added:

- Jonah's Wolf
- Wild Hunt Protocol
- Grey Guard
- Snowfall Creek Defense Coalition
- Civilian Witness Convoy
- Iron Horse
- Iron Horse Assault Team
- Federal Government
- Cian

### Informal or compound subjects

Remaining subjects were normalized or rewritten:

- Federal forces → Federal Magisterium
- Snowfall Creek Archives → Snowfall Creek Public Library
- Grey Guard Hunters → Grey Guard
- Aleksei and Sarah → two individual assertions
- Jonah Harrow and Margot Vance → a directed relationship assertion

## Results

- Unresolved assertion references entering the step: **17**
- Routed to analysis sidecar: **3**
- Normalized to canonical entities: **12**
- Compound assertions split or rewritten: **2**
- Unresolved reference decisions remaining: **0**
- Author decisions required: **0**

## Outputs

- `BOOK-3-ENTITY-REGISTRY-ACT-II-REFERENCE-ADDITIONS-v1.1.csv`
- `BOOK-3-ACT-II-DANGLING-REFERENCE-NORMALIZATION-v1.0.csv`

## Next step

Apply the normalization map to the entity and assertion candidates, rerun integrity, and then create individual knowledge and belief assertions from the corrected scene queue.
