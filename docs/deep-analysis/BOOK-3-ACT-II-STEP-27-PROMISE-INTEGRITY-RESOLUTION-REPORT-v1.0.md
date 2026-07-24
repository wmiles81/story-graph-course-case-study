# Book 3 Act II — Step 27 Promise Integrity Exception Resolution

## Purpose

Adjudicate the eight promise lifecycle flags produced by the Step 26 merge.

## Findings

The flags represented three ledger problems, not eight manuscript failures:

- five established promises lacked their earlier setup rows in the master lifecycle;
- two Act II payoff rows duplicated existing promises under new IDs;
- one Act II payoff needed its earlier setup restored.

## Corrections

### Missing setup rows restored

- partnership and trust arc (`PR-B03-0011`);
- Margot as Jonah's anchor (`PR-B03-0025`);
- breaking quarantine information control (`PR-B03-0029`);
- Margot's Charter-based authority against Valerius (`PR-B03-0035`);
- durable romantic and domestic future (`PR-B03-0036`);
- Jonah's fear that the Pack abandoned him (`PR-ACTII-0001`).

### Duplicate IDs merged

- `PR-ACTII-0002` merged into romance promise `PR-B03-0003`;
- `PR-ACTII-0003` merged into founding-truth promise `PR-B03-0006`.

## Rerun result

- promise rows in candidate v1.1: **58**
- remaining lifecycle issues: **8**
- author decisions required: **0**

## Outputs

- `BOOK-3-PROMISE-LIFECYCLE-ACT-II-CANDIDATE-v1.1.csv`
- `BOOK-3-ACT-II-PROMISE-INTEGRITY-DISPOSITIONS-v1.0.csv`
- `BOOK-3-ACT-II-PROMISE-INTEGRITY-RERUN-v1.1.csv`

## Next step

Merge non-epistemic state records into relationship, arc, decision, allegiance, threat, and tactical candidate ledgers, then recalculate continuity candidates against all repaired layers.
