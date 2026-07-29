# Book 3 Act II — Step 11 Scene Ratification-Candidate Merge

## Purpose

Merge all direct-manuscript Act II scene corrections into a new 153-row ratification candidate while preserving Act I history and explicit source lineage.

## Inputs

- `BOOK-3-SCENE-LEDGER-MASTER-RECONCILED-v1.1.csv`
- Chapters 13–18 Act II correction ledgers
- Step 10 false-positive dispositions
- governing Phase 8 manuscript
- original 153-scene boundary audit

## Merge result

- Total scenes: **{…}**
- Direct-manuscript replacements: **{…}**
- Unchanged Act I scene records retained: **{…}**
- Duplicate scene IDs: **{…}**
- Missing scene IDs: **0**

The candidate preserves original source boundaries, chapter ordering, hashes, and stable scene IDs. Corrected analytical fields are marked `ACT-II-DIRECT-MANUSCRIPT-CORRECTION`.

## Post-merge alignment rerun

- Median weighted token coverage: **{…}**
- Automatically flagged rows: **{…}**
- Flagged rows lacking prior direct review: **{…}**

Low-overlap flags on directly reconstructed scenes remain triage artifacts, not unresolved evidence problems. The two isolated false positives from Chapters 5 and 8 remain retained by direct review.

## Authority status

The new ledger is a **ratification candidate**, not yet the canon freeze.

Corrected scene rows qualify as `SYSTEM_RATIFIED_EVIDENCE_PENDING_FULL_DOWNSTREAM_REBUILD`. Their dependent assertions, promises, custody records, continuity findings, and queries must be regenerated before final promotion.

## Outputs

- `BOOK-3-SCENE-LEDGER-ACT-II-RATIFICATION-CANDIDATE-v1.0.csv`
- `BOOK-3-ACT-II-SCENE-SUPERSESSION-LINEAGE-v1.0.csv`
- `BOOK-3-ACT-II-RATIFICATION-CANDIDATE-ALIGNMENT-AUDIT-v1.0.csv`

## Next step

Rebuild scene-derived propositions and assertions for the 28 corrected scenes, reject stale Act I claims linked to superseded summaries, and generate the downstream change set.
