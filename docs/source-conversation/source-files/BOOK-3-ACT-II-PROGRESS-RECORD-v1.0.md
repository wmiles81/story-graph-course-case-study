# Act II — Author Ratification and Canon Freeze

## Purpose

Act II converts the technically coherent but provisional Book 3 Story Graph into an author-controlled canon baseline.

Act I proved that the manuscript could be transformed into a queryable model of scenes, entities, chronology, knowledge, belief, custody, causality, promises, payoffs, and revision authority. Act II tests the harder question:

> Can that model be checked against the manuscript, corrected where necessary, separated into evidence-resolvable and author-dependent decisions, and frozen as a defensible canonical version?

This document is the running progress record for Act II. It is updated as each step is completed. Historical Act I artifacts remain preserved. Act II does not silently overwrite them. Corrections are recorded through supersession, recalculation, and new versioned artifacts.

---

## Authority Rules

Act II uses four distinct decision states.

### `SYSTEM_RATIFIED_STRUCTURAL`

The record matches a reconciled structural registry exactly.

This status may be assigned automatically to identifiers, canonical names, entity types, aliases, first appearances, and other noninterpretive structural facts.

It does **not** mean the author has approved characterization, theme, motive, or narrative interpretation.

### `SYSTEM_RATIFIED_EVIDENCE`

The record is directly supported by bounded manuscript evidence and survives source, holder, timing, and epistemic checks.

A belief remains a belief. A suspicion remains a suspicion. Evidence ratification does not promote a character's belief into objective story-world truth.

### `REJECT_UNSUPPORTED_SOURCE`

The proposed record is absent from, or contradicted by, its cited manuscript passage.

Rejected records remain visible in the provenance trail but are excluded from the future canon build.

### `AUTHOR_DECISION_REQUIRED`

The manuscript permits more than one defensible interpretation, or the decision depends on intended ambiguity, authorial preference, thematic meaning, or continuity judgment.

Act II stops only when such a decision is necessary.

---

# Step 1 — Ratification Corpus Inventory

## Goal

Identify all existing ratification and adjudication queues, count their records, classify their authority risk, and determine which classes may proceed automatically.

## Inputs

- entity ratification queue;
- relationship ratification queue;
- knowledge ratification queue;
- timeline and logistics ratification queue;
- chapter canon-commit ratification queue;
- continuity issue adjudication queue;
- open-loop adjudication queue;
- narrative-physics adjudication queue;
- review-deferred ratification policy;
- reconciled Story Graph artifacts.

## Results

The principal Act II queues contain **247 records**:

- 67 entities;
- 15 relationships;
- 24 knowledge states;
- 68 timeline and logistics records;
- 30 chapter canon commits;
- 26 continuity candidates;
- 13 open loops;
- 20 narrative-physics states.

## Decision

Only structural identity records were authorized for the first automatic ratification pass.

Relationship trends, knowledge timing, chronology wording, chapter summaries, continuity classifications, open-loop resolution, and narrative-physics labels remained subject to evidence review.

## Outputs

- `BOOK-3-ACT-II-RATIFICATION-INVENTORY-v1.0.csv`
- `BOOK-3-ACT-II-STEP-01-RATIFICATION-INVENTORY-REPORT-v1.0.md`

## Lesson

A queue labeled “recommended approve” is still a recommendation, not author consent. Ratification has to preserve the difference between machine confidence and authority.

---

# Step 2 — Structural Entity Ratification

## Goal

Validate all entity-ratification records against the reconciled master entity registry.

## Checks

Each entity was checked for:

- canonical entity ID;
- canonical name;
- entity type;
- aliases;
- first appearance;
- current status.

## Results

- Records evaluated: **67**
- Structurally ratified: **67**
- Exceptions: **0**

Every passing record was labeled `SYSTEM_RATIFIED_STRUCTURAL`.

## Outputs

- `BOOK-3-ENTITY-RATIFICATION-SYSTEM-PASS-v1.0.csv`
- `BOOK-3-ENTITY-RATIFICATION-EXCEPTIONS-v1.0.csv`
- `BOOK-3-ACT-II-STEP-02-ENTITY-RATIFICATION-REPORT-v1.0.md`

## Lesson

Stable identity is one of the few graph layers that can often be ratified automatically. Even here, the status must state what was actually proven: registry consistency, not literary interpretation.

---

# Step 3 — Knowledge-State Evidence Validation

## Goal

Validate each proposed knowledge-state record against normalized propositions, evidence-hardened assertions, source scenes, manuscript quotations, knowledge holders, and acquisition timing.

## Inputs

- `BOOK-3-KNOWLEDGE-RATIFICATION-v0.1.csv`
- `BOOK-3-PROPOSITION-REGISTRY-MASTER-v1.0.csv`
- `BOOK-3-ASSERTIONS-MASTER-EVIDENCE-HARDENED-v1.2.csv`
- `BOOK-3-KNOWLEDGE-EVIDENCE-HARDENING-v1.0.csv`
- governing manuscript passages.

## Initial automatic pass

- Records evaluated: **24**
- Exact evidence matches: **16**
- Exceptions requiring direct review: **8**

The eight exceptions were inspected individually rather than sent immediately to the author.

## Final result

- Evidence-ratified: **22**
- Rejected as unsupported: **2**
- Author decisions required: **0**

## Rejected claims

### `P-B03-000069`

**Provisional claim:** The resistance identifies a surveillance or intelligence compromise in `B03-C15-S02`.

**Manuscript finding:** The scene shows Magisterium occupation, civilian arrests, Sterling's admission that the site will be sanitized, and the protagonists choosing a rooftop escape route.

The cited scene does not identify a surveillance source.

### `P-B03-000077`

**Provisional claim:** A rescued witness reveals Sterling's command site and next move in `B03-C17-S04`.

**Manuscript finding:** The scene shows Margot, Aleksei, and Henderson captive beside the Emitter Tower while Valerius orders the ice-rink purge. Margot begins the chemical sabotage operation.

No witness debrief occurs.

## Outputs

- `BOOK-3-KNOWLEDGE-RATIFICATION-SYSTEM-PASS-v1.1.csv`
- `BOOK-3-KNOWLEDGE-RATIFICATION-REJECTED-v1.1.csv`
- `BOOK-3-SCENE-SUMMARY-SOURCE-EXCEPTIONS-ACT-II-v1.0.csv`
- `BOOK-3-ACT-II-STEP-03-KNOWLEDGE-RATIFICATION-REPORT-v1.1.md`

## Lesson

Evidence hardening is only as trustworthy as the scene summary beneath it. A quotation attached to a mislabeled scene can make an invalid claim look impressively documented.

---

# Step 4 — Dependency Audit

## Goal

Trace every downstream record dependent on the two rejected knowledge claims.

## Results

The two unsupported claims had propagated into:

- **63 dependent rows**
- across **44 historical files**

Affected record classes included:

- scene summaries;
- assertions;
- continuity candidates;
- promise records;
- custody notes;
- batch query tests;
- gold-query evaluation results.

## Preservation policy

Historical Act I artifacts were not edited in place.

Every affected record received an Act II disposition:

- reject or rebuild assertion;
- supersede scene summary or context;
- dismiss or recalculate continuity issue;
- recalculate promise dependency;
- verify custody independently;
- invalidate and rerun query result.

## Outputs

- `BOOK-3-ACT-II-DEPENDENCY-AUDIT-v1.0.csv`
- `BOOK-3-ACT-II-STEP-04-DEPENDENCY-AUDIT-REPORT-v1.0.md`

## Lesson

A wrong graph claim is rarely isolated. Once it is accepted as a premise, it quietly colonizes summaries, continuity checks, promise tracking, and evaluation results. Databases are very efficient at preserving mistakes.

---

# Step 5 — Direct-Manuscript Scene Correction

## Goal

Replace the two unsupported scene summaries with records derived directly from their bounded manuscript passages.

## Corrected scene: `B03-C15-S02`

The corrected scene records:

- Magisterium martial law;
- separation and detention of humans and supernatural residents;
- the assault on Mrs. Gable;
- Sterling's admission that the Magisterium sanitizes sites where treaties fail;
- the decision to escape across the roof.

It explicitly records that no surveillance source is identified.

## Corrected scene: `B03-C17-S04`

The corrected scene records:

- Margot, Aleksei, and Henderson captive beside the Emitter;
- Valerius ordering the ice-rink purge;
- Henderson's prepared chemical bag;
- Margot recognizing the sabotage opportunity;
- Margot throwing her lighter onto the bag.

It explicitly records that no medical debrief or command-site revelation occurs.

## Outputs

- `BOOK-3-SCENE-LEDGER-ACT-II-CORRECTIONS-v1.0.csv`
- `BOOK-3-ACT-II-SUPERSESSION-LEDGER-v1.0.csv`
- `BOOK-3-ACT-II-STEP-05-SCENE-CORRECTION-REPORT-v1.0.md`

## Lesson

A source correction should not merely say the old record was wrong. It should provide the bounded replacement, identify what changed, and preserve the old record as superseded history.

---

# Step 6 — Continuity and Promise Recalculation

## Goal

Remove continuity and promise records created solely by unsupported source claims and identify evaluation rows requiring rerun.

## Dispositions

### `KV-0001`

Dismissed because the underlying proposition `P-B03-000069` is unsupported. No premature-knowledge contradiction remains.

### `PR-0006`

Dismissed as a duplicate issue derived from an invalid promise.

### `PR-B03-0019`

Rejected because the manuscript does not plant a promise to identify and neutralize a surveillance compromise.

## Evaluation impact

- Query or evaluation rows invalidated for rerun: **8**

The historical results were marked superseded rather than automatically converted from pass to fail.

## Outputs

- `BOOK-3-ACT-II-CONTINUITY-PROMISE-DISPOSITIONS-v1.0.csv`
- `BOOK-3-ACT-II-INVALIDATED-QUERY-RESULTS-v1.0.csv`
- `BOOK-3-ACT-II-STEP-06-CONTINUITY-RECALCULATION-REPORT-v1.0.md`

## Lesson

Continuity tools cannot compensate for false premises. Before adjudicating whether two facts conflict, confirm that both facts actually exist.

---

# Step 7 — Corrected Query Rerun and Chapter 18 Repair

## Goal

Rerun invalidated questions against corrected records and investigate a newly exposed Chapter 18 premise.

## New source finding

The Act I record for `B03-C18-S01` described:

- a resistance planning room;
- rescued witnesses;
- maps;
- selection of Sterling's master archive as the final target.

The bounded manuscript scene instead shows:

- Jonah feeling the Emitter suppression end;
- the Wolf and his magic returning;
- retained silver being expelled;
- rapid healing;
- violent transformation;
- Jonah recognizing Henderson as a pack-friend;
- Jonah entering the ventilation system to hunt.

A manuscript-wide search found no support for a Sterling “master archive” target.

## Proposition disposition

- `P-B03-000078` — `REJECT_UNSUPPORTED_SOURCE`

## Query rerun result

- 3 corrected or replacement questions passed;
- 2 malformed questions were retired.

Retired questions are excluded from the future canon-freeze denominator.

## Outputs

- `BOOK-3-SCENE-LEDGER-ACT-II-C18-CORRECTION-v1.0.csv`
- `BOOK-3-ACT-II-CORRECTED-QUERY-RERUN-v1.0.csv`
- `BOOK-3-ACT-II-SUPERSESSION-LEDGER-ADDENDUM-v1.1.csv`
- `BOOK-3-ACT-II-STEP-07-QUERY-RERUN-AND-C18-CORRECTION-REPORT-v1.0.md`

## Lesson

Gold queries can themselves contain bad premises. Evaluation is not trustworthy merely because every question received a confident answer.

---

# Step 8 — Full Scene Source-Alignment Audit

## Goal

Test all 153 reconciled scene summaries against the manuscript passages bounded by each scene's stored opening and closing lines.

## Method

The audit:

1. walked the scene ledger in narrative order;
2. located every opening and closing line in the governing manuscript;
3. extracted each bounded scene passage;
4. compared content-bearing summary vocabulary with the manuscript text;
5. flagged low-overlap records for direct review.

Token overlap was used only as triage. It is not proof of correctness.

## Results

- Ledger records: **153**
- Successfully bounded manuscript scenes: **153**
- Boundary failures: **0**
- Severe source-alignment risks: **25**
- Additional review candidates: **23**
- Median weighted token coverage: **0.379**

## Known failed records

The three already corrected scenes received severe-risk scores:

- `B03-C15-S02`: 0.115
- `B03-C17-S04`: 0.074
- `B03-C18-S01`: 0.084

## Pattern discovered

The severe-risk records clustered in:

- `B03-C05-S04`;
- `B03-C08-S04`;
- all stored scene summaries from Chapters 13–18.

This indicated a batch-level source-alignment failure rather than a handful of random errors.

## Outputs

- `BOOK-3-ACT-II-SCENE-SOURCE-ALIGNMENT-AUDIT-v1.0.csv`
- `BOOK-3-ACT-II-STEP-08-SCENE-SOURCE-ALIGNMENT-AUDIT-REPORT-v1.0.md`

## Lesson

A master ledger can be complete in row count and still be wrong in content. Coverage, alignment, and authority are separate validation dimensions.

---

# Step 9 — Direct Reconstruction of Chapters 13–16

## Goal

Reconstruct the severe-risk chapter batches directly from bounded manuscript passages.

## Chapter 13

Three corrected scenes were created:

1. Jonah returns from full-wolf form and admits Margot's voice brought him back.
2. Jonah and Margot enter the Troll Undercity, learn the town has risen, and receive the Civic Center route.
3. They traverse the geothermal tunnel, consummate their relationship, and recommit to confronting Sterling.

### Output

- `BOOK-3-SCENE-LEDGER-ACT-II-C13-CORRECTIONS-v1.0.csv`

## Chapter 14

Five corrected scenes were created:

1. reconnaissance from the Civic Center roof;
2. maintenance-bridge and skylight breach;
3. confrontation with Sterling and Jonah's silver gunshot wound;
4. Aleksei's rescue and transfer of the public-disclosure task to Margot;
5. public Treaty revelation, town unity, declaration of love, and arrival of the Magisterium.

### Output

- `BOOK-3-SCENE-LEDGER-ACT-II-C14-CORRECTIONS-v1.0.csv`

## Chapter 15

Five corrected scenes were created:

1. Magisterium arrival and activation of the anti-magic field;
2. martial-law occupation and rooftop escape decision;
3. sniper attack and identification of the ventilation route;
4. movement through ducts to Henderson's lead-shielded refuge;
5. Jonah's emergency treatment and creation of the resistance strategy.

### Output

- `BOOK-3-SCENE-LEDGER-ACT-II-C15-CORRECTIONS-v1.0.csv`

## Chapter 16

Five corrected scenes were created:

1. Jonah wakes without access to the Wolf;
2. Jonah and Aleksei infer the Emitter's location and extinction-level stakes;
3. Margot returns and Jonah resumes strategic leadership;
4. the team designs the ski-resort operation and Margot accepts field command;
5. equipment, Treaty custody, firearm transfer, and departure of the strike team.

### Output

- `BOOK-3-SCENE-LEDGER-ACT-II-C16-CORRECTIONS-v1.0.csv`

## Lesson

The source-alignment audit did more than locate bad summaries. It revealed that the late-middle extraction batch had been populated by scenes from a different narrative sequence. Direct bounded reconstruction became safer than trying to repair individual fields.

---

# Current Status

## Completed

- ratification corpus inventory;
- structural entity ratification;
- knowledge-state evidence validation;
- rejection of three unsupported propositions;
- dependency audit;
- direct correction of three individual scenes;
- continuity and promise recalculation;
- query rerun;
- full 153-scene source-alignment audit;
- direct reconstruction of Chapters 13–16.

## In progress

- write the Chapter 17 correction ledger;
- complete the remaining Chapter 18 corrections;
- inspect `B03-C05-S04` and `B03-C08-S04`;
- propagate all corrected scenes through assertions, knowledge, chronology, custody, promises, arcs, continuity candidates, and queries;
- rerun the affected evaluation subset;
- classify remaining records into evidence-resolvable and author-dependent queues;
- create the author decision package;
- freeze the ratified canon baseline after author decisions.

## Current stopping condition

No author decision is currently required.

Act II will continue automatically until the evidence and reconstruction work is exhausted and the remaining queue contains genuinely interpretive or authority-sensitive decisions.

---

# Running Act II Artifact Index

## Step 1

- `BOOK-3-ACT-II-RATIFICATION-INVENTORY-v1.0.csv`
- `BOOK-3-ACT-II-STEP-01-RATIFICATION-INVENTORY-REPORT-v1.0.md`

## Step 2

- `BOOK-3-ENTITY-RATIFICATION-SYSTEM-PASS-v1.0.csv`
- `BOOK-3-ENTITY-RATIFICATION-EXCEPTIONS-v1.0.csv`
- `BOOK-3-ACT-II-STEP-02-ENTITY-RATIFICATION-REPORT-v1.0.md`

## Step 3

- `BOOK-3-KNOWLEDGE-RATIFICATION-SYSTEM-PASS-v1.1.csv`
- `BOOK-3-KNOWLEDGE-RATIFICATION-REJECTED-v1.1.csv`
- `BOOK-3-SCENE-SUMMARY-SOURCE-EXCEPTIONS-ACT-II-v1.0.csv`
- `BOOK-3-ACT-II-STEP-03-KNOWLEDGE-RATIFICATION-REPORT-v1.1.md`

## Step 4

- `BOOK-3-ACT-II-DEPENDENCY-AUDIT-v1.0.csv`
- `BOOK-3-ACT-II-STEP-04-DEPENDENCY-AUDIT-REPORT-v1.0.md`

## Step 5

- `BOOK-3-SCENE-LEDGER-ACT-II-CORRECTIONS-v1.0.csv`
- `BOOK-3-ACT-II-SUPERSESSION-LEDGER-v1.0.csv`
- `BOOK-3-ACT-II-STEP-05-SCENE-CORRECTION-REPORT-v1.0.md`

## Step 6

- `BOOK-3-ACT-II-CONTINUITY-PROMISE-DISPOSITIONS-v1.0.csv`
- `BOOK-3-ACT-II-INVALIDATED-QUERY-RESULTS-v1.0.csv`
- `BOOK-3-ACT-II-STEP-06-CONTINUITY-RECALCULATION-REPORT-v1.0.md`

## Step 7

- `BOOK-3-SCENE-LEDGER-ACT-II-C18-CORRECTION-v1.0.csv`
- `BOOK-3-ACT-II-CORRECTED-QUERY-RERUN-v1.0.csv`
- `BOOK-3-ACT-II-SUPERSESSION-LEDGER-ADDENDUM-v1.1.csv`
- `BOOK-3-ACT-II-STEP-07-QUERY-RERUN-AND-C18-CORRECTION-REPORT-v1.0.md`

## Step 8

- `BOOK-3-ACT-II-SCENE-SOURCE-ALIGNMENT-AUDIT-v1.0.csv`
- `BOOK-3-ACT-II-STEP-08-SCENE-SOURCE-ALIGNMENT-AUDIT-REPORT-v1.0.md`

## Step 9

- `BOOK-3-SCENE-LEDGER-ACT-II-C13-CORRECTIONS-v1.0.csv`
- `BOOK-3-SCENE-LEDGER-ACT-II-C14-CORRECTIONS-v1.0.csv`
- `BOOK-3-SCENE-LEDGER-ACT-II-C15-CORRECTIONS-v1.0.csv`
- `BOOK-3-SCENE-LEDGER-ACT-II-C16-CORRECTIONS-v1.0.csv`

---

## Update Policy

This document is a living Act II progress record.

Each later update should add:

- the step number and purpose;
- exact inputs;
- method;
- verified results;
- rejected or superseded records;
- downstream consequences;
- produced artifacts;
- current author-decision status.

The document should not be rewritten to make the process appear cleaner than it was. The failures are part of the class material because they show where graph validation, evidence hardening, and automated evaluation can fail while still producing plausible-looking outputs.
