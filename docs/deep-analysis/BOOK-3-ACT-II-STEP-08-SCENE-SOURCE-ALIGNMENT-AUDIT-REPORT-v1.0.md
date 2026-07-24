# Book 3 Act II — Step 08 Full Scene Source-Alignment Audit

## Purpose

Test all 153 reconciled scene summaries against the manuscript passages bounded by each scene's stored opening and closing lines.

## Method

The audit:

1. walked the scene ledger in narrative order;
2. located each scene's opening and closing lines in the governing manuscript;
3. extracted the bounded source passage;
4. compared content-bearing summary vocabulary with manuscript vocabulary;
5. flagged low-overlap records for direct source review.

Token overlap is used only as a triage signal. It does not prove that a summary is correct.

## Extraction results

- Ledger records: **153**
- Successfully bounded manuscript scenes: **153**
- Boundary failures: **0**
- Severe alignment risks: **25**
- Additional alignment-review candidates: **23**
- Median weighted token coverage: **0.379**

## Known failed summaries

The three scenes already corrected during Act II received these weighted-overlap scores:

- `B03-C15-S02`: **0.115** (SEVERE_SOURCE_ALIGNMENT_RISK)
- `B03-C17-S04`: **0.074** (SEVERE_SOURCE_ALIGNMENT_RISK)
- `B03-C18-S01`: **0.084** (SEVERE_SOURCE_ALIGNMENT_RISK)

## Interpretation

A low score does not automatically invalidate a scene summary. Some correct summaries use abstract language not repeated verbatim in prose.

However, severe low-overlap records are unsafe inputs for author ratification until directly checked against the bounded manuscript text.

## Outputs

- `BOOK-3-ACT-II-SCENE-SOURCE-ALIGNMENT-AUDIT-v1.0.csv`
- prioritized source-review queue for flagged scenes

## Next step

Directly inspect severe-risk scenes, correct demonstrably mismatched summaries, and then recalculate dependent ratification records before presenting the first author decision queue.
