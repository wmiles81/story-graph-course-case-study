# BOOK 3 SCENE-COVERAGE RECONCILIATION REPORT v1.1

## Result

The 21-scene discrepancy has been resolved.

- Previous parser scene count: **153**
- Previous master scene count: **132**
- Restored from the validated Chapters 7–9 batch: **16**
- Restored and directly revalidated from the Phase 8 manuscript: **5**
- Reconciled master scene count: **153**
- Reconciled scene-context count: **153**

The reconciled scene and context ledgers now both contain **153 rows**, giving one
current scene context per scene.

## Root causes

### Chapters 7–9

All sixteen scenes from Chapters 7–9 had already been validated in:

`BOOK-3-SCENE-LEDGER-CH07-09-VALIDATED-v0.1.csv`

They were omitted during the later master merge. They have been restored without
reinterpretation.

### Chapters 14–18

The fifth scene of each chapter existed in both the manuscript and parser skeleton,
but was omitted from the corresponding validated batch ledger:

- `B03-C14-S05`
- `B03-C15-S05`
- `B03-C16-S05`
- `B03-C17-S05`
- `B03-C18-S05`

Each was reviewed directly against the Phase 8 manuscript and received a new scene
ledger row and scene-context row.

## Additional finding

`B03-C18-S05` contains a repeated closing command in the manuscript. The repeated
paragraph has not been silently removed because this reconciliation preserves source
truth. It should be handled in a separate copyediting or manuscript-correction pass.

## Files produced

- `BOOK-3-SCENE-LEDGER-MASTER-RECONCILED-v1.1.csv`
- `BOOK-3-SCENE-CONTEXTS-MASTER-RECONCILED-v1.1.csv`
- `BOOK-3-SCENE-COVERAGE-RECONCILIATION-v1.1.csv`

## Gate status

**Scene coverage is now cleared.**

The next integrity work is:

1. unresolved entity references;
2. predicate normalization;
3. regeneration of the Story Graph integrity report against the reconciled ledgers.
