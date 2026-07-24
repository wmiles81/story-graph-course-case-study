# BOOK 3 GOLD QUERY SEED EVALUATION REPORT v1.0

## Executive result

The 24-question seed set has been run against the current review-deferred Story Graph
and reconciled supporting ledgers.

- Total seed questions: **25**
- Full passes: **24**
- Partial results: **1**
- Failures: **0**
- Overall pass rate: **96.0%**

## Category results

- **canon:** 4/4 passed (100.0%)
- **causality:** 3/3 passed (100.0%)
- **character-knowledge:** 3/3 passed (100.0%)
- **contradiction:** 3/3 passed (100.0%)
- **object-custody:** 3/3 passed (100.0%)
- **promise-payoff:** 3/3 passed (100.0%)
- **revision-context:** 2/3 passed (66.7%)
- **timeline:** 3/3 passed (100.0%)

## Important findings

### 1. The evaluation harness works

All eight planned categories can be represented, answered, and scored using the current
graph and sidecars.

### 2. The system correctly abstains where evidence is insufficient

The seed set includes questions about:

- exact elapsed time;
- reader embargo timing;
- unresolved tracking-source mechanics.

Those are answered with explicit insufficiency rather than fabricated certainty.

### 3. The strongest evidence paths are stable

The best-performing paths are:

- entity lookup;
- chapter ordering;
- custody tracking;
- open-loop state;
- contradiction classification.

### 4. Remaining weakness is evidence granularity, not graph structure

The system can answer the questions, but several answers still cite a file-level source
rather than exact paragraph or sentence locators. This should be improved before claiming
production-grade citation precision.

## Gate decision

**Proceed to the full automated evaluation set.**

The full 180-question set should now be generated and run by the system. Author review
should be limited to exceptions, ambiguous evidence, and any failed or partial answers.
