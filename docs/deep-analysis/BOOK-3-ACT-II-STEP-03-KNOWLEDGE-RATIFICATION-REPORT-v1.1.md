# Book 3 Act II — Step 03 Knowledge-State Evidence Validation

## Purpose

Validate proposed knowledge-state records against normalized propositions, evidence-hardened assertions, and direct manuscript passages.

## Results

- Records evaluated: **24**
- Evidence-ratified: **22**
- Rejected as unsupported by the cited manuscript scene: **2**
- Remaining author decisions: **0**

## Automatic repairs

Five queue records used alternate wording for already registered propositions. They were mapped to canonical proposition language and verified directly against manuscript evidence.

One additional record, Jackson recognizing Jonah after the crash, was verified directly from the manuscript.

## Rejected records

### P-B03-000069

The provisional record claimed that the resistance identifies a surveillance or intelligence compromise in `B03-C15-S02`.

The bounded manuscript scene instead shows Magisterium occupation, civilian arrests, Sterling's admission, and rooftop escape planning. The claimed knowledge event does not occur there.

### P-B03-000077

The provisional record claimed that a rescued witness reveals Sterling's command site and next move in `B03-C17-S04`.

The bounded manuscript scene instead shows the Emitter-tower confrontation and Valerius ordering the rink purge. The claimed witness debrief does not occur there.

## Authority result

Passing records are labeled `SYSTEM_RATIFIED_EVIDENCE`.

The two unsupported records are labeled `REJECT_UNSUPPORTED_SOURCE`. This is an evidence decision, not an authorial interpretation decision, because the cited events are absent from the bounded source scenes.

## Outputs

- `BOOK-3-KNOWLEDGE-RATIFICATION-SYSTEM-PASS-v1.1.csv`
- `BOOK-3-KNOWLEDGE-RATIFICATION-REJECTED-v1.1.csv`
- `BOOK-3-SCENE-SUMMARY-SOURCE-EXCEPTIONS-ACT-II-v1.0.csv`

## Downstream impact

The two rejected records require correction of the scene ledger summaries and reevaluation of dependent continuity, promise, and query records before canon freeze.
