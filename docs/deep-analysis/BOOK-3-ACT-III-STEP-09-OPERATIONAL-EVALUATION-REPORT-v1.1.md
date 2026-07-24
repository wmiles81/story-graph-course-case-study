# Book 3 Act III — Step 09 Operational Evaluation, Rerun

## Initial result

- tests: **39**
- pass: **37**
- fail: **2**

## Failure analysis

Both failures were evaluation-fixture defects:

1. The Margot test searched for the generic word `chemical`, while the canonical proposition used the more precise terms `ammonia`, `bleach`, and `exothermic`.
2. The Aleksei test used the display label `Aleksei`, while the operational view correctly used the canonical name `Aleksei Petrov`.

No canon or materialized-view correction was required.

## Final result

- tests: **39**
- PASS: **39**
- FAIL: **0**
- pass rate: **100.0%**

## Lesson

Operational tests must resolve aliases and semantic terminology rather than assuming one display string or keyword.

The natural-language query layer must therefore normalize:

- canonical names;
- aliases;
- topic synonyms;
- stable IDs.

## Outputs

- `BOOK-3-ACT-III-OPERATIONAL-EVALUATION-RESULTS-v1.1.csv`
- `BOOK-3-ACT-III-OPERATIONAL-EVALUATION-SUMMARY-v1.1.csv`

## Next step

Define and prototype the natural-language operational query layer, including intent routing, entity and alias resolution, topic normalization, evidence assembly, and safe failure behavior.
