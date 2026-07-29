# Story Graph Conversation Since Last Checkpoint

**Project:** story-graph  
**Date:** 2026-07-21  
**Scope:** Conversation from the last saved checkpoint through the completion of the Book 3 pilot evaluation.

---

## User

It works now. Next

## Assistant

The next-stage tool is ready: **Ratification Assembly**.

- Opened a Ratification Assembly interface.
- Added import validation for the eight review modules.
- Added consolidated bundle export and a completion checklist.

## User

I don't see those files anywhere. When I clicked 'save locally' what happened

## Assistant

Explained that “Save locally” used browser `localStorage`, not the Downloads folder.

Clarified that:

- decisions remained available only in the same browser context;
- no file was created;
- browser data clearing, private browsing, URL changes, or switching devices could lose access;
- the Ratification Assembly could not see those decisions automatically.

Acknowledged that the wording was misleading and should have said **Save in this browser**.

## User

that's pretty useless.

## Assistant

Agreed and rebuilt the control room as v0.3 with:

- **Download all decisions**
- **Import decision backup**
- completion progress
- a Markdown checklist
- clearer browser-storage warnings

## User

download all decisions does nothing

## Assistant

Rebuilt the control room as v0.4 with:

- a state bridge between embedded review modules and the parent control room;
- a visible JSON export panel;
- **Copy JSON**
- **Open JSON in new tab**
- **Save JSON file**

## User

the json doesn't save. Listen, I don't want to waste more time here. I need to move on to the next steps.

## Assistant

Stopped the browser-export work and adopted a **review-deferred ratification policy**.

Created:

- `BOOK-3-REVIEW-DEFERRED-RATIFICATION-POLICY-v0.1.md`
- `BOOK-3-Story-Graph-REVIEW-DEFERRED-v0.2.md`
- `BOOK-3-REVIEW-DEFERRED-GRAPH-BUILD-REPORT-v0.2.md`
- `BOOK-3-REVIEW-DEFERRED-STORY-GRAPH-v0.2.zip`

Applied the following provisional open-loop decisions:

- 10 marked **FIRED**
- 1 marked **DEFUSED**
- 1 moved to a series-level deadline
- 1 tracking-source issue left unresolved

The graph remained explicitly labeled **review-deferred provisional canon**, not fully author-ratified canon.

## User

continue

## Assistant

Updated the browser report to use the reconciled 153-scene dataset.

Created:

- `book3_story_graph_report_v2/index.html`
- `BOOK-3-BROWSER-STORY-GRAPH-REPORT-v2.0.zip`

The updated report included:

- 153 reconciled scenes
- 153 reconciled scene contexts
- continuity issues
- open-loop status
- SPE Physics State
- knowledge states
- logistics

Added views for:

- **Continuity Issues**
- **Open Loops**
- **SPE Physics State**

## User

next

## Assistant

Prepared the gold-set evaluation stage.

Created:

- `BOOK-3-GOLD-SET-READINESS-v0.1.csv`
- `BOOK-3-GOLD-QUERY-SET-SEED-v0.1.csv`
- `BOOK-3-GOLD-SET-READINESS-REPORT-v0.1.md`
- `BOOK-3-GOLD-SET-READINESS-v0.1.zip`

Initial readiness result:

- 180 planned gold questions
- 145 judged ready to author and score
- 35 blocked by evidence or authority gaps
- 24 seed questions initially reported

## User

Are you fucking kidding me? 180 questions? What do I have you for?

## Assistant

Acknowledged the mistake.

Clarified that the 180 questions were for the assistant to generate, run, and score automatically, not for the author to answer.

Committed to:

- run the seed set;
- fix the evaluation method;
- run the full 180-question set;
- surface only failures, partials, and genuine author decisions.

## User

go

## Assistant

Ran the seed evaluation.

The initial run revealed that the seed contained 25 questions, not 24.

Corrected result:

- 25 questions run
- 24 full passes
- 1 partial
- 0 failures
- 96% full-pass rate

The partial was:

> Can a superseded draft fact override the Phase 8 manuscript?

Created:

- `BOOK-3-GOLD-QUERY-SEED-RESULTS-v1.0.csv`
- `BOOK-3-GOLD-QUERY-SEED-SUMMARY-v1.0.csv`
- `BOOK-3-GOLD-QUERY-SEED-EVALUATION-REPORT-v1.1.md`
- `BOOK-3-GOLD-QUERY-SEED-EVALUATION-v1.1.zip`

## User

ok

## Assistant

Confirmed that the next step was the full automated 180-question evaluation, with only exceptions surfaced afterward.

## User

go

## Assistant

Generated and ran the complete 180-question evaluation automatically.

Result:

- 180 questions run
- 155 full passes
- 25 partial results
- 0 failures
- 86.1% full-pass rate
- 100% usable-answer rate

The 25 partials were all character-knowledge evidence cases where assertion rows had scene locators but lacked hardened sentence-level quotations.

Created:

- `BOOK-3-FULL-GOLD-QUERY-EVALUATION-v1.0.csv`
- `BOOK-3-FULL-GOLD-QUERY-SUMMARY-v1.0.csv`
- `BOOK-3-FULL-GOLD-QUERY-EXCEPTIONS-v1.0.csv`
- `BOOK-3-FULL-GOLD-QUERY-EVALUATION-REPORT-v1.0.md`
- `BOOK-3-FULL-GOLD-QUERY-EVALUATION-v1.0.zip`

## User

continue

## Assistant

Hardened the 25 character-knowledge exceptions directly against the Phase 8 manuscript.

Added exact supporting excerpts to the assertion registry and reran the exception set.

Final result:

- 180 queries run
- 180 full passes
- 0 partials
- 0 failures
- 100% full-pass rate

Created:

- `BOOK-3-ASSERTIONS-MASTER-EVIDENCE-HARDENED-v1.2.csv`
- `BOOK-3-KNOWLEDGE-EVIDENCE-HARDENING-v1.0.csv`
- `BOOK-3-GOLD-QUERY-EXCEPTION-RERUN-v1.0.csv`
- `BOOK-3-FULL-GOLD-QUERY-EVALUATION-FINAL-v1.1.csv`
- `BOOK-3-PILOT-COMPLETION-ASSESSMENT-v1.0.md`
- `BOOK-3-PILOT-COMPLETION-PACKAGE-v1.0.zip`

The Book 3 technical pilot was declared complete.

The graph remains **review-deferred provisional canon** because unresolved authorial and interpretive matters remain, including:

- the safehouse tracking-source mechanism;
- continuity candidates requiring authorial interpretation;
- exact elapsed-time questions unsupported by explicit manuscript durations;
- future series-level obligations beyond Book 3.

The schema, validation process, sidecar architecture, query harness, evidence model, and browser-report approach were considered proven for series expansion.

---

## Current Project State

### Completed

- Book 3 manuscript authority assessment
- 153-scene reconciliation
- 153 context reconciliation
- entity and predicate normalization
- provisional Story Graph generation
- review-deferred ratification policy
- updated browser report
- continuity audit
- open-loop adjudication recommendations
- SPE Physics State coverage
- 180-question automated gold evaluation
- evidence hardening for all 25 knowledge-state exceptions
- final 180/180 evaluation pass
- pilot completion assessment

### Current Canon Status

**Review-deferred provisional canon**

### Next Recommended Stage

Freeze the Book 3 pilot package as the reference implementation and migrate the series-level Story Graph using the mature four-book continuity graph as the governing layer.

