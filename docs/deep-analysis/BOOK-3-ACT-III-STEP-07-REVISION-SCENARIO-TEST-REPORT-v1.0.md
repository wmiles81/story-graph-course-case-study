# Book 3 Act III — Step 07 Controlled Revision Scenario Tests

## Purpose

Test whether the dependency index can identify the operational blast radius of different proposed changes without mutating canon.

## Scenarios

1. remove the Emitter sabotage scene event;
2. remove the service-pistol transfer;
3. rename Inquisitor Valerius while preserving identity.

## Results

- scenarios executed: **3**
- scenarios with detected dependencies: **2**
- scenario failures: **1**
- impact records generated: **13**
- directly invalidated evaluation questions: **2**

## Interpretation

The index successfully distinguishes:

- event-level blast radius;
- custody-specific consequences;
- identity and terminology consequences.

The results are conservative. A two-step traversal catches explicit reference dependencies but does not yet capture every semantic dependency implied only by prose meaning.

## Outputs

- `BOOK-3-ACT-III-REVISION-SCENARIO-RESULTS-v1.0.csv`
- `BOOK-3-ACT-III-REVISION-SCENARIO-IMPACTS-v1.0.csv`
- `BOOK-3-ACT-III-REVISION-SCENARIO-PACKET-v1.0.md`

## Next step

Build operational materialized views for scenes, knowledge, custody, promises, continuity, and analytical states so the dashboard can answer common questions without scanning every frozen file.
