# Book 3 Act II — Step 03 Knowledge-State Evidence Validation

## Purpose

Validate each proposed knowledge-state record against the normalized proposition registry and the evidence-hardened assertion layer.

## Inputs

- `BOOK-3-KNOWLEDGE-RATIFICATION-v0.1.csv`
- `BOOK-3-PROPOSITION-REGISTRY-MASTER-v1.0.csv`
- `BOOK-3-ASSERTIONS-MASTER-EVIDENCE-HARDENED-v1.2.csv`
- `BOOK-3-KNOWLEDGE-EVIDENCE-HARDENING-v1.0.csv`

## Validation checks

Each record was checked for:

- exact normalized proposition match;
- evidence-hardened assertion;
- manuscript quotation;
- subject or knowledge holder;
- acquisition chapter;
- retained epistemic status.

## Results

- Records evaluated: **24**
- Evidence-ratified: **16**
- Exceptions requiring review: **8**

Passing records are labeled `SYSTEM_RATIFIED_EVIDENCE`. Beliefs remain beliefs; the validation does not promote them to objective story-world truth.

## Outputs

- `BOOK-3-KNOWLEDGE-RATIFICATION-SYSTEM-PASS-v1.0.csv`
- `BOOK-3-KNOWLEDGE-RATIFICATION-EXCEPTIONS-v1.0.csv`

## Next step

Inspect every exception, determine whether it is a mapping defect, holder mismatch, timing mismatch, or genuinely ambiguous knowledge state, and resolve all machine-correctable cases before presenting an author decision queue.
