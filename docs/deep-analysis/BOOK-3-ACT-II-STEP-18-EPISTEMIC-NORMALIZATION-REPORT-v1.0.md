# Book 3 Act II — Step 18 Epistemic Normalization

## Purpose

Convert the 28 corrected scenes' analytical `knowledge_gained` and `belief_changes` fields into a controlled queue of potential individual epistemic assertions.

## Inputs

- Chapters 13–18 direct-manuscript correction ledgers;
- `BOOK-3-ENTITY-REGISTRY-ACT-II-CANDIDATE-v1.1.csv`;
- Act II epistemic authority rules.

## Rules

A knowledge or belief assertion requires:

1. an identifiable holder;
2. a proposition distinct from the holder;
3. an epistemic state such as known, believed, suspected, or inferred;
4. an acquisition or validity scene;
5. manuscript evidence.

Collective phrases such as “the team learns” are not automatically expanded to every present character.

## Results

- Analytical epistemic statements processed: **59**
- Named-holder evidence candidates: **9**
- Source-review records: **50**
- Excluded no-claim records: **0**

## Classification counts

- ANALYTICAL_OR_UNASSIGNED: **1**
- COLLECTIVE_OR_GROUP_STATE: **10**
- MULTIPLE_NAMES_AMBIGUOUS_HOLDER: **39**
- NAMED_INDIVIDUAL_HOLDER: **3**
- NAMED_JOINT_HOLDER: **6**

## Authority status

Named-holder rows remain `CANDIDATE_PENDING_SOURCE_QUOTE`.

No knowledge or belief assertion has yet been promoted into the graph solely from an analytical scene-summary field.

## Outputs

- `BOOK-3-ACT-II-EPISTEMIC-NORMALIZATION-v1.0.csv`
- `BOOK-3-ACT-II-EPISTEMIC-EVIDENCE-CANDIDATES-v1.0.csv`
- `BOOK-3-ACT-II-EPISTEMIC-SOURCE-REVIEW-QUEUE-v1.0.csv`

## Next step

Verify named-holder candidates against bounded manuscript text, then directly inspect collective and ambiguous rows to determine which individuals actually acquire or change the relevant epistemic state.
