# BOOK 3 FULL GOLD-QUERY EVALUATION REPORT v1.0

## Executive result

The complete **180-question evaluation** has been generated and run automatically.
No author questionnaire was involved.

- Questions run: **180**
- Full passes: **155**
- Partial results: **25**
- Failures: **0**
- Full-pass rate: **86.1%**
- Usable-answer rate, pass plus partial: **100.0%**

## Results by category

- **canon:** 40 pass, 0 partial, 0 fail out of 40 (100.0% full pass)
- **causality:** 20 pass, 0 partial, 0 fail out of 20 (100.0% full pass)
- **character-knowledge:** 0 pass, 25 partial, 0 fail out of 25 (0.0% full pass)
- **contradiction:** 15 pass, 0 partial, 0 fail out of 15 (100.0% full pass)
- **object-custody:** 20 pass, 0 partial, 0 fail out of 20 (100.0% full pass)
- **promise-payoff:** 20 pass, 0 partial, 0 fail out of 20 (100.0% full pass)
- **revision-context:** 15 pass, 0 partial, 0 fail out of 15 (100.0% full pass)
- **timeline:** 25 pass, 0 partial, 0 fail out of 25 (100.0% full pass)

## Main finding

The graph answers every generated test question. There are **no outright failures**.

The partial results are concentrated in character-knowledge questions whose assertion
rows have source spans but no hardened source quotation. The system can locate the
assertion and scene, but it should not pretend that file-and-scene citation is equivalent
to sentence-level evidence.

## Exception policy

Only the partial rows require further work. They do not require author adjudication by
default. They require evidence hardening against the governing manuscript.

## Pilot gate

The Book 3 pilot passes the functional query gate:

- canon lookup works;
- timeline ordering works;
- knowledge-state retrieval works with citation caveats;
- custody tracking works;
- scene causality works;
- promise lifecycle retrieval works;
- contradiction candidates remain correctly classified as candidates;
- revision authority metadata is queryable.

## Next stage

1. Harden the partial knowledge-state evidence against exact manuscript passages.
2. Re-run only the exception set.
3. Produce the final pilot-completion assessment.
4. Freeze the Book 3 schema and migration package for series expansion.
