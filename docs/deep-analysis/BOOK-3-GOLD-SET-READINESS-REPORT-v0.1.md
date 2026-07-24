# BOOK 3 GOLD-SET READINESS REPORT v0.1

## Executive result

The pilot is ready to begin formal gold-set evaluation, but not every planned query
category is equally mature.

- Planned gold questions: **180**
- Questions currently ready to author and score: **145**
- Questions still blocked by evidence or authority gaps: **35**
- Seed test cases created now: **25**

## Readiness by category

- **canon:** 40/40 ready (high confidence)
- **timeline:** 19/25 ready (moderate confidence)
- **character-knowledge:** 19/25 ready (moderate confidence)
- **object-custody:** 20/20 ready (high confidence)
- **causality:** 15/20 ready (moderate confidence)
- **promise-payoff:** 15/20 ready (moderate confidence)
- **contradiction:** 11/15 ready (moderate confidence)
- **revision-context:** 6/15 ready (low confidence)

## Strongest categories

The graph is currently strongest in:

- canon lookup;
- object custody;
- chapter ordering;
- explicit promise/payoff tracking;
- durable entity and relationship state.

## Weakest categories

The graph remains weakest in:

- exact elapsed-time questions;
- reader embargo timing;
- source-hardened character knowledge;
- revision-context comparison beyond the current authority hierarchy.

These are not failures of graph structure. They are evidence-hardening gaps.

## Existing batch tests

Existing master query-test rows: **49**

Observed status values:

- **answered:** 48
- **answered-with-inference:** 1

## Seed test set

A 24-question seed set has been created across all eight target categories. It is
designed to prove the evaluation harness before expanding to the full 180-question
gold set.

## Files produced

- `BOOK-3-GOLD-SET-READINESS-v0.1.csv`
- `BOOK-3-GOLD-QUERY-SET-SEED-v0.1.csv`
- `BOOK-3-GOLD-SET-READINESS-REPORT-v0.1.md`

## Next step

Run the 24-question seed set against the current review-deferred graph and record:

- answer;
- correctness;
- completeness;
- citation accuracy;
- temporal accuracy;
- perspective accuracy;
- confidence calibration.

After the harness works, expand the seed into the full 180-question gold set.
