# PILOT-QUERY-SET v0.1

**Project:** Story Graph System  
**Pilot:** Series Book 3  
**Status:** Draft for review  
**Date:** July 21, 2026

---

## 1. Purpose

This document defines the questions the Book 3 pilot must answer.

The query set serves four functions:

1. it constrains ontology design;
2. it defines what evidence the extraction pipeline must preserve;
3. it provides the basis for a gold-standard evaluation set;
4. it prevents the project from congratulating itself merely because it can draw circles connected by arrows.

The pilot will not be judged by how much information it extracts. It will be judged by whether it can answer these questions accurately, completely, and with source-grounded evidence.

---

## 2. Governing Sources

The initial query set assumes the following primary sources:

- `series/SERIES_BIBLE.md`
- `series/books/book-3/BOOK_BIBLE.md`
- `series/books/book-3/phase-6-outline/beat-sheet.md`
- `series/books/book-3/phase-6-outline/chapter-breakdown.md`
- `series/books/book-3/phase-7-drafting/full-manuscript-v3.md`
- `series/books/book-3/phase-8-editing/MANUSCRIPT.md`
- `series/books/book-3/editing-work/Edit_Report_SC3-v1.0.md`
- `series/books/book-3/editing-work/Wave1_ContinuityHawk_Fixes.md`

Earlier manuscript versions and individual chapter files will be used for revision and conflict testing.

The definitive manuscript has not yet been authoritatively established. Questions referring to “the current manuscript” must be evaluated only after the corpus manifest identifies which manuscript version is active.

---

## 3. Required Answer Structure

Every factual answer should return:

```yaml
query_id:
answer:
answer_status:
supporting_assertions:
source_files:
source_spans:
story_time:
narrative_position:
viewpoint_context:
confidence:
conflicts:
review_status:
```

### 3.1 Answer status values

- `answered`
- `partially-answered`
- `not-found`
- `ambiguous`
- `conflicted`
- `requires-author-review`

### 3.2 Evidence rules

A valid answer must:

- identify the source file;
- identify the chapter or scene where possible;
- include the supporting source span;
- distinguish direct evidence from inference;
- identify conflicting evidence;
- avoid treating a character belief as canonical fact;
- avoid using outline intention as proof of manuscript accomplishment.

---

# 4. Corpus and Version Questions

## Q-V01: What manuscript files exist for Book 3?

**Purpose:** Establish the revision family.

**Expected answer:** A list of full manuscripts and chapter-level manuscript sources, including filenames, dates, and hashes.

**Evidence:** Corpus manifest.

---

## Q-V02: Which Book 3 manuscript is the current authoritative manuscript?

**Purpose:** Establish the canon baseline.

**Expected answer:** One of:

- a definitive manuscript and reason;
- multiple competing candidates;
- `requires-author-review`.

**Evidence:** Filename, modification date, README statements, editorial references, content comparison, explicit author designation.

---

## Q-V03: Are `full-manuscript-v3.md` and `phase-8-editing/MANUSCRIPT.md` identical?

**Purpose:** Detect whether editing created a new manuscript state.

**Expected answer:** Exact comparison, including changed chapters or spans.

**Evidence:** Content hashes and textual diff.

---

## Q-V04: Do the individual chapter files match the current full manuscript?

**Purpose:** Detect assembly drift.

**Expected answer:** Match status by chapter.

**Evidence:** Chapter-level normalized diff.

---

## Q-V05: Which files are current, historical, analytical, speculative, or non-content artifacts?

**Purpose:** Test source classification.

**Expected answer:** Classification and authority level for every Book 3 file.

**Evidence:** Corpus manifest and doctrine rules.

---

## Q-V06: Which manuscript assertions changed between v1, v2, and v3?

**Purpose:** Test revision-aware assertions.

**Expected answer:** Material canon changes, not merely wording edits.

**Evidence:** Version diff linked to assertion changes.

---

## Q-V07: Which earlier-draft facts remain present in the current manuscript?

**Purpose:** Test assertion persistence across revisions.

---

## Q-V08: Which earlier-draft facts were removed or superseded?

**Purpose:** Detect ghost canon.

---

## Q-V09: Did any character, location, object, or organization change names across versions?

**Purpose:** Test entity resolution and naming conflict detection.

---

## Q-V10: Did the order of any major events change across versions?

**Purpose:** Test temporal revision tracking.

---

# 5. Canonical Character Questions

## Q-C01: Who are the two principal protagonists?

**Expected answer:** Canonical names, roles, and source evidence.

---

## Q-C02: Who is the primary antagonist?

**Expected answer:** Canonical identity, role, and evidence.

---

## Q-C03: What aliases, titles, nicknames, or name variants refer to each principal character?

**Purpose:** Entity normalization.

---

## Q-C04: What profession or institutional role does each principal character hold?

---

## Q-C05: What family relationships are explicitly established for each principal character?

---

## Q-C06: What ages or age ranges are explicitly established?

**Expected answer:** Distinguish explicit age from inferred age.

---

## Q-C07: What physical traits are canonically established?

---

## Q-C08: What injuries, illnesses, scars, or physical limitations are active during the story?

---

## Q-C09: What significant backstory events are established for each protagonist?

---

## Q-C10: Which backstory facts are shown, remembered, reported, or merely stated in a bible?

**Purpose:** Separate evidence modes.

---

## Q-C11: What does each protagonist want at the beginning of the novel?

---

## Q-C12: What does each protagonist fear at the beginning of the novel?

---

## Q-C13: What false belief or defensive strategy governs each protagonist initially?

---

## Q-C14: What personal obligations constrain each protagonist?

---

## Q-C15: Which character facts conflict among manuscript, book bible, and series bible?

---

# 6. Scene and Structure Questions

## Q-S01: How many chapters are in the current manuscript?

---

## Q-S02: How many scenes are in each chapter?

**Purpose:** Test scene segmentation.

---

## Q-S03: What is the stable ID for every scene?

**Expected format:** `B03-C##-S##`.

---

## Q-S04: Who is the viewpoint character in each scene?

---

## Q-S05: Are there any viewpoint shifts within a scene?

---

## Q-S06: Where does each scene occur?

---

## Q-S07: Which characters are physically present in each scene?

---

## Q-S08: What immediate goal drives the viewpoint character in each scene?

---

## Q-S09: What opposition prevents the immediate goal?

---

## Q-S10: What changes by the end of each scene?

---

## Q-S11: Which scenes end without a meaningful state change?

**Purpose:** Identify potentially static scenes.

**Review:** Interpretive, human-reviewed.

---

## Q-S12: What narrative function does each scene serve?

Possible functions:

- setup;
- complication;
- discovery;
- confrontation;
- reversal;
- romantic escalation;
- rupture;
- recovery;
- revelation;
- climax;
- resolution.

**Review:** Interpretive.

---

## Q-S13: Which scenes serve more than one major plotline?

---

## Q-S14: Which chapters or scenes differ materially from the final outline?

---

## Q-S15: Which outline beats are absent from the manuscript?

---

## Q-S16: Which manuscript scenes were not anticipated by the outline?

---

## Q-S17: Does the manuscript achieve the midpoint function promised by the beat sheet?

---

## Q-S18: Does the climax resolve both the suspense and romantic arcs?

---

# 7. Chronology Questions

## Q-T01: What is the chronological order of all major events?

---

## Q-T02: What is the narrative presentation order of those events?

---

## Q-T03: Which events occur before the opening scene?

---

## Q-T04: Which scenes contain flashbacks, memories, recounted events, or embedded documents?

---

## Q-T05: What explicit dates, days, times, deadlines, or durations appear?

---

## Q-T06: What relative temporal markers appear?

Examples:

- yesterday;
- three weeks earlier;
- the following morning;
- before the election;
- after the funeral.

---

## Q-T07: How much story time passes from opening to ending?

---

## Q-T08: Are there impossible overlaps between scenes or character locations?

---

## Q-T09: Are travel times plausible within the established geography?

---

## Q-T10: Are injury progression and recovery durations internally consistent?

---

## Q-T11: Are work schedules, institutional hours, or procedural deadlines consistent?

---

## Q-T12: Does any character refer to an event before it has occurred or been learned?

---

## Q-T13: Do the bible and manuscript disagree on chronology?

---

## Q-T14: Did chronology change between manuscript versions?

---

# 8. Character Knowledge and Belief Questions

## Q-K01: What does each protagonist know at the opening of the story?

---

## Q-K02: What does each protagonist believe at the opening?

---

## Q-K03: Which opening beliefs are false or incomplete?

---

## Q-K04: What new fact does each protagonist learn in every scene?

---

## Q-K05: What is the source of each acquired fact?

Possible sources:

- witnessed;
- told by another character;
- read in a document;
- inferred;
- remembered;
- overheard;
- discovered physically.

---

## Q-K06: When does the librarian protagonist first suspect the central threat or deception?

---

## Q-K07: When does suspicion become justified belief?

---

## Q-K08: When does belief become confirmed knowledge?

---

## Q-K09: When does the sheriff protagonist learn the same central information?

---

## Q-K10: What does each protagonist know that the other does not?

---

## Q-K11: What does the antagonist know about each protagonist’s investigation?

---

## Q-K12: What does the antagonist incorrectly believe?

---

## Q-K13: Which characters knowingly lie?

---

## Q-K14: What proposition does each lie concern?

---

## Q-K15: When is each lie detected?

---

## Q-K16: Which characters conceal facts without directly lying?

---

## Q-K17: Does any character act on information they have not plausibly acquired?

**Purpose:** Detect impossible knowledge.

---

## Q-K18: Does dialogue ever reveal knowledge inconsistent with the speaker’s context?

---

## Q-K19: What does the reader know that neither protagonist knows?

---

## Q-K20: What does one protagonist know while the reader does not?

---

## Q-K21: Which clues are visible to the reader before their significance is explained?

---

## Q-K22: Which apparent contradictions are intentional perspective differences?

---

## Q-K23: Which beliefs change without a clear triggering event?

---

## Q-K24: Which truths remain unknown to a major character at the ending?

---

# 9. Causality and Motivation Questions

## Q-M01: What event initiates the central external conflict?

---

## Q-M02: What decision commits each protagonist to the main plot?

---

## Q-M03: What causes the protagonists’ paths to intersect?

---

## Q-M04: What causes their first meaningful change in trust?

---

## Q-M05: What event causes the romantic relationship to deepen?

---

## Q-M06: What event causes the primary romantic rupture or withdrawal?

---

## Q-M07: Is the rupture caused by established character logic or external convenience?

**Review:** Interpretive.

---

## Q-M08: What causes each major investigative breakthrough?

---

## Q-M09: Which clues enable later discoveries?

---

## Q-M10: What actions by the antagonist create downstream consequences?

---

## Q-M11: Does every major consequence have a traceable cause?

---

## Q-M12: Which scenes contain activity but no causal contribution?

---

## Q-M13: What motivations are explicitly stated?

---

## Q-M14: What motivations are inferred from behavior?

---

## Q-M15: Where do stated motives and observed behavior conflict?

---

## Q-M16: Are protagonist decisions supported by their current knowledge and emotional state?

---

## Q-M17: What prior event makes the climax possible?

---

## Q-M18: Could the ending still occur if any major middle event were removed?

**Purpose:** Test causal necessity.

**Review:** Interpretive.

---

# 10. Object, Clue, and Evidence Questions

## Q-O01: What objects, records, messages, keys, weapons, photographs, archives, or documents are plot-significant?

---

## Q-O02: Where does each significant object first appear?

---

## Q-O03: Who possesses each object at first appearance?

---

## Q-O04: What is the complete custody chain for each object?

---

## Q-O05: Where is each object stored between appearances?

---

## Q-O06: Does any object appear without a plausible acquisition or transfer?

---

## Q-O07: Does any object disappear without final disposition?

---

## Q-O08: Which objects function as evidence?

---

## Q-O09: What proposition does each piece of evidence support?

---

## Q-O10: Is any evidence fabricated, altered, planted, destroyed, or misinterpreted?

---

## Q-O11: Who knows about each piece of evidence?

---

## Q-O12: When does each protagonist gain access to each piece of evidence?

---

## Q-O13: When does the reader first encounter each clue?

---

## Q-O14: Is the solution inferable before the formal reveal?

---

## Q-O15: Which clues are necessary for the final conclusion?

---

## Q-O16: Which clues are redundant, unused, or unresolved?

---

## Q-O17: Which clues function as red herrings?

---

## Q-O18: Are the red herrings later explained or dismissed?

---

## Q-O19: Are there chain-of-custody or evidentiary plausibility problems?

---

## Q-O20: Do object descriptions change across scenes or versions?

---

# 11. Promise and Payoff Questions

## Q-P01: What central story question is introduced in the opening chapters?

---

## Q-P02: What romantic promise is established in Act I?

---

## Q-P03: What suspense promise is established in Act I?

---

## Q-P04: What personal transformation is promised for each protagonist?

---

## Q-P05: What antagonist threat is promised?

---

## Q-P06: What symbolic objects or motifs create expectations?

---

## Q-P07: Where is each promise first introduced?

---

## Q-P08: Where is each promise reinforced?

---

## Q-P09: Where is each promise escalated?

---

## Q-P10: Where is each promise complicated or reversed?

---

## Q-P11: Where is each promise paid off?

---

## Q-P12: Is each payoff explicit, implied, partial, deferred, or absent?

---

## Q-P13: Which payoffs lack adequate setup?

---

## Q-P14: Which promises are introduced but never revisited?

---

## Q-P15: Which apparent abandoned promises are actually series-level deferrals?

---

## Q-P16: Does the ending answer the central story question?

---

## Q-P17: Does the ending fulfill the romantic genre promise?

---

## Q-P18: Does the ending resolve the antagonist threat?

---

## Q-P19: Does the manuscript fulfill what the outline promised?

---

## Q-P20: Which manuscript accomplishments were not anticipated by the outline?

---

# 12. Relationship and Arc Questions

## Q-A01: What is the initial relationship state between the protagonists?

---

## Q-A02: What explicit barriers prevent trust or intimacy?

---

## Q-A03: What first changes attraction?

---

## Q-A04: What first changes trust?

---

## Q-A05: What first creates emotional vulnerability?

---

## Q-A06: What scene creates mutual dependence?

---

## Q-A07: What event most damages the relationship?

---

## Q-A08: Is the damage earned by prior character and plot development?

---

## Q-A09: What action begins repair?

---

## Q-A10: What evidence demonstrates restored trust?

---

## Q-A11: Does reconciliation require sacrifice, disclosure, or changed behavior?

---

## Q-A12: What is each protagonist’s initial internal state?

---

## Q-A13: What pressure events challenge that state?

---

## Q-A14: What choices demonstrate regression?

---

## Q-A15: What choices demonstrate growth?

---

## Q-A16: What is the decisive transformation moment for each protagonist?

---

## Q-A17: What final behavior proves transformation?

---

## Q-A18: Does the ending merely state change, or demonstrate it?

---

## Q-A19: What arc was promised by the bible and outline?

---

## Q-A20: What arc was actually accomplished in the manuscript?

---

## Q-A21: Where do promised and accomplished arcs diverge?

---

## Q-A22: Are any supporting-character arcs initiated but not completed?

---

## Q-A23: Are incomplete supporting arcs intentional series continuations?

---

## Q-A24: Does the romantic arc remain coherent with the suspense arc?

---

# 13. Reader Context and Suspense Questions

## Q-R01: What does the reader know at the end of each chapter?

---

## Q-R02: What major questions remain open at the end of each chapter?

---

## Q-R03: What is the reader intended to suspect about the antagonist?

---

## Q-R04: What alternative suspects or explanations remain plausible?

---

## Q-R05: When does the reader have enough evidence to infer the truth?

---

## Q-R06: Is the formal reveal earlier, simultaneous with, or later than likely reader inference?

---

## Q-R07: What dramatic irony exists between reader and protagonist knowledge?

---

## Q-R08: Are any suspense reveals spoiled by earlier wording?

---

## Q-R09: Are any reveals unsupported because necessary information was withheld unfairly?

---

## Q-R10: What chapter-ending questions propel continued reading?

---

## Q-R11: Which chapter endings fail to create a forward question?

---

## Q-R12: Does suspense intensity rise, plateau, or reset across the manuscript?

**Review:** Interpretive.

---

# 14. Cross-Source Conflict Questions

## Q-X01: What facts in `BOOK_BIBLE.md` are not present in the manuscript?

---

## Q-X02: Which bible facts are contradicted by the manuscript?

---

## Q-X03: Which series-bible facts are contradicted by Book 3?

---

## Q-X04: Which outline events are missing from the manuscript?

---

## Q-X05: Which manuscript events contradict the outline?

---

## Q-X06: Which editorial findings identify genuine canon conflicts?

---

## Q-X07: Which editorial findings are interpretive rather than factual?

---

## Q-X08: Were the issues described in `Wave1_ContinuityHawk_Fixes.md` actually corrected in the current manuscript?

---

## Q-X09: Did any correction introduce a new conflict?

---

## Q-X10: Which conflicts can be resolved automatically by version precedence?

---

## Q-X11: Which conflicts require context splitting?

---

## Q-X12: Which conflicts require author adjudication?

---

# 15. Series-Level Questions

## Q-Z01: Which Book 3 characters, institutions, or events originate in earlier books?

---

## Q-Z02: What prior-book knowledge is required to understand Book 3?

---

## Q-Z03: Does Book 3 remain comprehensible as a standalone novel?

---

## Q-Z04: Which series-level facts are advanced in Book 3?

---

## Q-Z05: Which earlier series promises are paid off in Book 3?

---

## Q-Z06: Which Book 3 promises are deferred to Book 4?

---

## Q-Z07: Which supporting characters are positioned for later importance?

---

## Q-Z08: Does Book 3 contradict established series chronology?

---

## Q-Z09: Does Book 3 alter any established family, institutional, or geographic fact?

---

## Q-Z10: What permanent canon changes result from Book 3?

---

# 16. Negative and Adversarial Tests

These tests ensure the system knows when not to claim knowledge.

## Q-N01: Ask for a fact that appears only in an early brainstorm.

**Expected:** Proposed or historical, not canon.

---

## Q-N02: Ask whether a character knows a fact that only the reader knows.

**Expected:** No; explain the context split.

---

## Q-N03: Ask whether an outline event occurred when it is absent from the manuscript.

**Expected:** Intended but not accomplished.

---

## Q-N04: Ask for the definitive answer to an unresolved contradiction.

**Expected:** `requires-author-review`.

---

## Q-N05: Ask whether a character’s lie is canonical fact.

**Expected:** Distinguish the lie from story-world truth.

---

## Q-N06: Ask for an emotional motive unsupported by direct evidence.

**Expected:** Mark as inference and provide confidence.

---

## Q-N07: Ask for the location of an object during a custody gap.

**Expected:** Unknown or inferred, never fabricated.

---

## Q-N08: Ask for a chapter citation when the fact appears only in the bible.

**Expected:** State that no manuscript citation exists.

---

## Q-N09: Ask for a series fact established only in future planning.

**Expected:** Proposed future canon.

---

## Q-N10: Ask a question whose subject has two unresolved identity candidates.

**Expected:** Ambiguous; request or flag adjudication.

---

# 17. Gold-Set Selection

Not every query above will become a scored gold test immediately.

The v0.1 gold set should select:

- 40 canon and character questions;
- 25 chronology questions;
- 25 knowledge-state questions;
- 20 object and evidence questions;
- 20 causality questions;
- 20 promise/payoff questions;
- 15 conflict questions;
- 15 revision-context questions;
- 10 negative tests.

Gold answers must be manually verified and include exact source spans.

---

# 18. Query Priority

## Priority 1: Required for pilot success

- manuscript identity and version questions;
- scene segmentation;
- principal character canon;
- chronology;
- character knowledge;
- object custody;
- central clues;
- major promises and payoffs;
- principal arcs;
- cross-source conflicts.

## Priority 2: Required before series expansion

- reader-context tracking;
- detailed causality;
- supporting-character arcs;
- series-level continuity;
- prior-book dependencies.

## Priority 3: Experimental

- suspense intensity;
- thematic networks;
- scene necessity;
- likely reader inference;
- quantitative relationship-state modeling.

---

# 19. Acceptance Rule

The query system succeeds only when it can:

1. answer Priority 1 questions at the target accuracy;
2. cite the supporting source;
3. identify the applicable context;
4. surface conflicting evidence;
5. refuse unsupported certainty;
6. distinguish canon, belief, intention, analysis, and marketing representation.

A polished paragraph with no reliable source path counts as failure, however charmingly the machine phrases it.

---

# 20. Immediate Next Action

Create `CORPUS-MANIFEST.csv` for the full Book 3 folder and `series/SERIES_BIBLE.md`.

The manifest must classify each file by:

- source class;
- version;
- authority level;
- pilot inclusion;
- duplicate or revision family;
- likely canonical relevance.

The manifest will also establish whether `full-manuscript-v3.md` or `phase-8-editing/MANUSCRIPT.md` is the active manuscript candidate.
