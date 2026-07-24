# BOOK 3 CONTINUITY AUDIT REPORT v1.0

## Executive result

**Confirmed continuity errors:** 0

**Candidate issues requiring manuscript adjudication:** 26

This audit does not treat every state change as a contradiction. Several apparent conflicts are intentionally resolved by later revelation or elapsed story time, including:

- the Scrolls appearing stolen and later being revealed as hidden;
- Jackson being presumed dead and later found alive;
- Valerius acting as antagonist before being archived as a book.

Those are valid narrative reversals, not continuity defects.

## Candidate issue counts

### By category

- **knowledge continuity:** 7
- **object custody:** 4
- **promise continuity:** 13
- **timeline:** 2

### By severity

- **major-risk:** 4
- **moderate-risk:** 1
- **review:** 21

## Most important findings

### 1. Timeline precision remains insufficient

The graph tracks the Purge Protocol and the Iron Horse collision deadline, but it does not consistently encode elapsed minutes or hours. The sequences are narratively ordered, yet the model cannot prove that every deadline is physically feasible.

### 2. Custody intervals need closure

Several objects have open-ended custody states followed by later holders or locations. These may be perfectly correct transfers, but the interval model does not always close the earlier state explicitly.

### 3. Knowledge audit produced candidates, not confirmed violations

The current assertion table and scene summaries were sufficient to identify possible premature-knowledge cases. None can be responsibly labeled an error without checking the exact manuscript passage.

### 4. Promise lifecycle normalization is incomplete

Some promise IDs lack an explicit terminal state in the lifecycle table. This may reflect bookkeeping gaps rather than abandoned story promises.

## Important limitation

Much of the Chapters 4–30 analytical layer was created through structured, machine-assisted interpretation. The audit therefore evaluates the current graph model first and the manuscript second.

A true gold-standard continuity audit now requires:

1. opening each candidate issue at the cited scenes;
2. checking the exact manuscript language;
3. marking each candidate as confirmed, dismissed, or resolved-by-context;
4. attaching paragraph and sentence locators;
5. updating the browser report with an Issues view.

## Files produced

- `BOOK-3-CONTINUITY-ISSUES-v1.0.csv`
- `BOOK-3-CONTRADICTION-PAIRS-v1.0.csv`
- `BOOK-3-KNOWLEDGE-VIOLATIONS-v1.0.csv`
- `BOOK-3-TIMELINE-AUDIT-v1.0.csv`

## Current defensible conclusion

The automated graph-level audit found **no confirmed continuity error yet**.

It found **26 candidate issues or model-quality gaps** requiring direct manuscript adjudication.

This is progress, not absolution. The manuscript has merely reached the stage where accusations need evidence.
