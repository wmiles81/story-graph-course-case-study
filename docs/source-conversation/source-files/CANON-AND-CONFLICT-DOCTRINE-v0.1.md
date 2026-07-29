# CANON-AND-CONFLICT-DOCTRINE v0.1

**Project:** Story Graph System  
**Applies to:** Book-level and series-level fiction analysis  
**Status:** Draft for review  
**Date:** July 21, 2026

---

## 1. Purpose

This doctrine defines how the Story Graph System determines, records, compares, and resolves conflicting claims across manuscripts, bibles, outlines, notes, editorial documents, marketing materials, and prior drafts.

Its purpose is not to force all sources into one artificial truth. Fiction development produces multiple legitimate kinds of truth:

- story-world fact;
- character belief;
- narrator claim;
- reader inference;
- authorial intention;
- historical draft state;
- analytical interpretation;
- marketing simplification.

The system must preserve these distinctions rather than flattening them into a single graph and then acting surprised when the heroine has three birthdays and two dead fathers.

---

## 2. Governing Principles

### 2.1 The manuscript is evidence, not merely content

The current author-approved manuscript is the primary source for what occurs on the page.

A planning document may state what was intended. An editorial report may state what appears inconsistent. A bible may state background canon. None automatically overrides the current manuscript where the manuscript explicitly depicts otherwise.

### 2.2 Canon is assertion-specific

Authority applies to individual claims, not only entire documents.

Examples:

- The manuscript governs whether a confrontation happened.
- The series bible may govern a birth date never stated in the manuscript.
- The book bible may govern an off-page family relationship.
- The marketing package governs the public title and subtitle.
- An editorial report may identify a continuity problem but does not create story-world fact.
- An outline governs planned structure only until the manuscript supersedes it.

### 2.3 Conflict is data

Contradictions are not deleted merely because one source appears stronger.

The system records:

- every conflicting assertion;
- the source of each assertion;
- its authority level;
- its applicable context;
- its current resolution status;
- the reason for resolution.

This preserves revision history and allows later audits.

### 2.4 No silent overwrite

A new assertion must not erase an earlier assertion without recording a supersession or conflict relationship.

### 2.5 Character truth is not canonical truth

A statement made or believed by a character may be:

- true;
- false;
- incomplete;
- deceptive;
- uncertain;
- misunderstood;
- metaphorical;
- emotionally distorted.

The system must not promote dialogue or interior thought directly to verified story-world fact.

### 2.6 Reader truth is separately modeled

What the reader knows, suspects, or is intended to infer is not identical to story-world canon or character knowledge.

### 2.7 Author approval is the final adjudication authority

Automated systems may detect, rank, and propose conflict resolutions. They may not declare unresolved narrative ambiguity solved without author approval.

---

## 3. Source Classes

Each source file must be assigned one primary source class.

### 3.1 Final Manuscript

Definition:

- the most recent author-approved manuscript;
- a published edition;
- an explicitly designated canonical text.

Typical authority:

- highest for on-page events, dialogue, scene order, and depicted state.

Limitations:

- may omit background details;
- may contain accidental continuity errors;
- may differ from intended but unrealized arc structure.

### 3.2 Canonical Bible

Definition:

- author-approved series bible;
- author-approved book bible;
- explicit canon registry.

Typical authority:

- high for background facts, relationships, ages, histories, institutions, and off-page canon.

Limitations:

- does not override explicit manuscript action unless the manuscript is itself under revision;
- may contain stale entries.

### 3.3 Structural Plan

Definition:

- approved outline;
- beat sheet;
- chapter breakdown;
- scene plan.

Typical authority:

- high for intended structure;
- medium or low for actual accomplishment.

Limitations:

- superseded by the manuscript when the manuscript diverges;
- should be used to compare promise versus execution, not to rewrite execution.

### 3.4 Development Draft

Definition:

- chapter draft;
- prior full manuscript;
- alternate scene;
- revision candidate.

Typical authority:

- valid only within its revision context.

Limitations:

- not current canon unless explicitly promoted;
- useful for lineage and change analysis.

### 3.5 Analytical Document

Definition:

- editorial letter;
- continuity report;
- character analysis;
- pacing analysis;
- developmental report;
- quality audit.

Typical authority:

- evidence about the manuscript;
- not direct story-world canon.

Limitations:

- interpretive;
- may contain mistaken readings;
- must cite manuscript evidence where possible.

### 3.6 Ideation Document

Definition:

- brainstorm;
- concept note;
- discarded plot option;
- exploratory character sketch;
- title or trope generation file.

Typical authority:

- proposed only.

Limitations:

- never treated as current canon without explicit promotion.

### 3.7 Marketing Document

Definition:

- blurb;
- ad copy;
- metadata;
- cover copy;
- promotional summary.

Typical authority:

- high for approved public-facing wording;
- low for precise story-world facts.

Limitations:

- may simplify, compress, conceal, or dramatize.

### 3.8 External Research

Definition:

- factual reference;
- genre research;
- legal, medical, technical, historical, or cultural source.

Typical authority:

- supports real-world plausibility;
- does not itself establish fictional canon.

---

## 4. Authority Levels

Each assertion receives an authority level from 0 through 5.

| Level | Name | Meaning |
|---|---|---|
| 5 | Author-verified canon | Explicitly approved by the author |
| 4 | Strong canonical evidence | Directly depicted in final manuscript or current bible |
| 3 | Current development authority | Current outline, current draft, or unresolved manuscript evidence |
| 2 | Analytical interpretation | Supported reading or diagnostic claim |
| 1 | Historical or speculative | Prior draft, brainstorm, alternate possibility |
| 0 | Rejected or invalid | Explicitly discarded, disproven, or erroneous |

Authority level alone does not settle conflict. Context and assertion type also matter.

---

## 5. Assertion Types

Every assertion must declare one of the following types.

### 5.1 Story-World Fact

A proposition asserted as objectively true within the fictional world.

Example:

`The ledger is hidden in the archive.`

### 5.2 On-Page Event

An event explicitly depicted in the manuscript.

Example:

`Emery opens the locked drawer in Scene 18.`

### 5.3 Character Knowledge

A fact a character knows with sufficient justification.

Example:

`Emery knows the signature was forged.`

### 5.4 Character Belief

A proposition a character accepts but may not know.

Example:

`Theo believes Emery destroyed the evidence.`

### 5.5 False Belief

A character belief contradicted by canonical evidence.

### 5.6 Lie

A proposition stated by a character who knows or believes it to be false.

### 5.7 Rumor

A socially transmitted proposition without established reliability.

### 5.8 Suspicion

A tentative character hypothesis.

### 5.9 Reader Knowledge

A proposition explicitly available to the reader by a given narrative point.

### 5.10 Reader Inference

A proposition the reader may reasonably infer but which is not explicitly confirmed.

### 5.11 Authorial Intention

A planned or declared narrative goal.

Example:

`The midpoint should permanently alter trust between the leads.`

### 5.12 Analytical Interpretation

A claim about function, structure, arc, theme, pacing, causality, or reader effect.

### 5.13 Marketing Representation

A public-facing simplification or framing.

### 5.14 Revision-State Fact

A proposition true only in a specified draft or version.

---

## 6. Canonical Status Values

Every assertion receives one canonical status.

- `verified`
- `probable`
- `proposed`
- `unresolved`
- `character-belief`
- `false-belief`
- `lie`
- `rumor`
- `suspicion`
- `reader-knowledge`
- `reader-inference`
- `authorial-intention`
- `analytical`
- `marketing-only`
- `superseded`
- `contradicted`
- `rejected`

---

## 7. Conflict Types

The system must classify conflicts rather than treating all disagreement alike.

### 7.1 Direct Contradiction

Two assertions cannot both be true in the same context.

Example:

- `Ava is thirty-two.`
- `Ava is thirty-six.`

### 7.2 Temporal Conflict

Two assertions may both be true, but their timing is incompatible.

Example:

- the injury occurs before the gala;
- a later source places the injury after the gala.

### 7.3 Version Conflict

Different drafts contain different facts.

This is not necessarily an error if each assertion is correctly scoped to its version.

### 7.4 Perspective Conflict

Characters hold incompatible beliefs.

This is often intentional and must not be “resolved” into one belief.

### 7.5 Canon versus Intention Conflict

The outline promises something the manuscript does not accomplish.

This is a developmental finding, not necessarily a continuity error.

### 7.6 Bible versus Manuscript Conflict

A reference document and the manuscript disagree.

The manuscript usually governs on-page action; the bible may govern unstated background.

### 7.7 Internal Manuscript Conflict

The same manuscript asserts incompatible facts.

This is a likely continuity defect unless explained by perspective, deception, memory, or chronology.

### 7.8 Naming Conflict

An entity appears under variant names, aliases, spellings, titles, or accidental renaming.

### 7.9 Granularity Conflict

Two sources describe the same fact at different levels of detail.

Example:

- `She works in medicine.`
- `She is an attending cardiologist.`

These may be compatible rather than contradictory.

### 7.10 Interpretive Conflict

Two analyses disagree about scene function, character motivation, or thematic effect.

These remain competing interpretations unless authorially adjudicated.

---

## 8. Conflict Detection Rules

A conflict candidate should be raised when assertions:

1. share the same normalized subject and predicate;
2. have incompatible objects;
3. overlap in valid time or revision context;
4. apply to the same narrative level;
5. exceed the configured confidence threshold.

The system should not raise a direct contradiction when:

- the assertions belong to different manuscript versions;
- one is a character belief and one is story-world fact;
- one is marketing language and one is literal canon;
- the values can be reconciled by hierarchy or granularity;
- valid-time intervals do not overlap;
- the difference is an intentional alias.

---

## 9. Conflict Resolution Precedence

When two assertions genuinely conflict in the same context, apply the following sequence.

### Rule 1: Prefer explicit author adjudication

An author-approved canon decision overrides lower-authority sources.

### Rule 2: Prefer the latest approved manuscript for depicted events

For what occurs on-page, the latest approved manuscript prevails unless the author marks it as erroneous.

### Rule 3: Prefer the canonical bible for unstated background facts

Use the current bible when the manuscript is silent.

### Rule 4: Prefer specific evidence over general summary

A directly depicted event outweighs a generalized description.

### Rule 5: Prefer later approved revision over earlier revision

Only within the same authority class and where the later version is confirmed as current.

### Rule 6: Preserve unresolved ambiguity

Do not fabricate certainty when evidence remains insufficient.

### Rule 7: Do not resolve intentional perspective differences

Character disagreement remains part of the narrative model.

### Rule 8: Escalate material canon conflicts

Human review is mandatory when a conflict affects:

- identity;
- chronology;
- parentage;
- death or survival;
- central mystery logic;
- romantic exclusivity;
- major evidence;
- crime responsibility;
- series-level continuity;
- ending state.

---

## 10. Resolution Outcomes

Each conflict must end in one of these states.

### 10.1 Resolved: Source A Prevails

The stronger assertion becomes active canon. The losing assertion remains stored as superseded or contradicted.

### 10.2 Resolved: Source B Prevails

Same treatment in the opposite direction.

### 10.3 Resolved: Context Split

Both assertions remain valid under different contexts.

Examples:

- different versions;
- different time intervals;
- different character beliefs;
- different editions.

### 10.4 Resolved: Entity Merge

The apparent conflict was caused by duplicate entity identity.

### 10.5 Resolved: Granularity Reconciliation

The assertions are compatible at different levels of specificity.

### 10.6 Unresolved

Evidence is insufficient or author review is pending.

### 10.7 Intentional Contradiction

The contradiction is narratively purposeful.

Examples:

- unreliable narration;
- deception;
- disputed testimony;
- mistaken memory.

---

## 11. Provenance Requirements

Every canonical or interpretive assertion must include:

```yaml
assertion_id:
subject:
predicate:
object:
assertion_type:
canonical_status:
source_file:
source_span:
source_class:
source_version:
authority_level:
story_time:
valid_from:
valid_to:
viewpoint_context:
reader_context:
confidence:
review_status:
created_by:
reviewed_by:
supersedes:
contradicts:
resolution_reason:
```

No assertion may be marked `verified` without source provenance or explicit author declaration.

---

## 12. Review Requirements

### 12.1 Automatic acceptance allowed

Only for high-confidence, low-ambiguity facts such as:

- explicit character appearance;
- explicit location;
- chapter and scene membership;
- direct object possession;
- directly stated family relation;
- explicit temporal marker.

### 12.2 Human review required

For:

- contradictory canon;
- inferred causality;
- character motive;
- deception;
- false belief;
- promise/payoff identification;
- arc interpretation;
- thematic classification;
- ambiguous pronoun resolution affecting canon;
- cross-book identity merges;
- series-level retcons.

### 12.3 Author-only approval required

For:

- declaring a retcon;
- changing published canon;
- resolving intentional ambiguity;
- promoting ideation into canon;
- rejecting manuscript evidence as erroneous;
- determining the authoritative future-series plan.

---

## 13. Revision Doctrine

### 13.1 Every significant source has a version identity

At minimum:

- file path;
- content hash;
- modified date;
- declared version;
- manuscript status.

### 13.2 Revision does not delete history

When a fact changes:

- the old assertion becomes `superseded`;
- the new assertion points to the prior assertion;
- the reason for change is recorded where known.

### 13.3 Changed source spans invalidate dependent assertions

When manuscript text changes, all assertions derived from affected spans must be re-evaluated.

### 13.4 Unchanged assertions may persist

Assertions tied to unchanged source spans remain active, subject to conflict checks.

### 13.5 Published canon is immutable by default

Later changes are treated as:

- revised-edition canon;
- explicit retcon;
- alternate edition;
- author correction.

They do not silently alter the historical published state.

---

## 14. Series-Level Doctrine

### 14.1 Book-local facts may become series canon

A fact established in one book remains binding unless:

- explicitly retconned;
- revealed as false belief or deception;
- limited to a character perspective;
- contradicted and authorially corrected.

### 14.2 Later books do not automatically override earlier books

A later contradiction may represent:

- a deliberate reveal;
- a retcon;
- an error;
- an unreliable earlier account;
- changed circumstances.

The system must classify before resolving.

### 14.3 Series bibles are not self-executing law

A bible entry inconsistent with published text must be flagged for adjudication.

### 14.4 Future-plan material remains proposed

Planned Book 4 material cannot be used as though already canonical in Book 1 analysis.

---

## 15. Examples

### Example A: Age conflict

**Book bible:** Mara is thirty-four.  
**Manuscript:** Mara says, “I turned thirty-six last month.”

Treatment:

- If the dialogue is sincere and unchallenged, raise a direct conflict.
- Manuscript receives stronger authority for on-page fact.
- Bible assertion becomes `contradicted` pending review.
- Do not automatically assume dialogue is accurate if deception or sarcasm is plausible.

### Example B: Character belief versus truth

**Theo believes:** Emery destroyed the ledger.  
**Canonical event:** Victoria destroyed the ledger.

Treatment:

- no canon conflict;
- store Theo’s assertion as `false-belief`;
- store the canonical event separately;
- record when Theo’s belief changes.

### Example C: Outline versus manuscript

**Outline:** The midpoint kiss resolves distrust.  
**Manuscript:** Distrust worsens after the kiss.

Treatment:

- no continuity conflict;
- record a canon-versus-intention divergence;
- surface it in the arc fulfillment report.

### Example D: Earlier draft versus final manuscript

**Draft 1:** The evidence is a photograph.  
**Final manuscript:** The evidence is an audio recording.

Treatment:

- scope each assertion to its version;
- final manuscript assertion becomes active canon;
- earlier assertion becomes `superseded`;
- no unresolved contradiction remains.

### Example E: Marketing compression

**Blurb:** She discovers her husband’s betrayal.  
**Manuscript:** She suspects the betrayal, gathers evidence, and confirms it much later.

Treatment:

- marketing assertion remains `marketing-only`;
- do not use it to determine the scene where knowledge becomes certain.

---

## 16. Conflict Report Format

Each conflict report entry should contain:

```yaml
conflict_id:
conflict_type:
subject:
predicate:
assertion_a:
assertion_b:
source_a:
source_b:
authority_a:
authority_b:
context_overlap:
materiality:
recommended_resolution:
resolution_status:
author_review_required:
notes:
```

Materiality values:

- `critical`
- `major`
- `moderate`
- `minor`
- `cosmetic`

---

## 17. Success Criteria

This doctrine succeeds when the system can:

1. distinguish genuine canon conflicts from perspective differences;
2. preserve historical versions without polluting current canon;
3. identify manuscript-versus-bible discrepancies;
4. avoid treating analysis and marketing copy as story fact;
5. explain why one assertion prevailed;
6. cite the exact source evidence;
7. leave ambiguity unresolved when necessary;
8. support author adjudication without forcing premature decisions.

---

## 18. Immediate Next Action

Create `PILOT-QUERY-SET-v0.1.md` for Book 3.

The query set will operationalize this doctrine by defining the exact questions the pilot must answer and the expected evidence required for each answer.
