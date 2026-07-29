# Story Graph Project Conversation — Continuation

**Saved:** July 21, 2026  
**Range:** From the previous Markdown save point through the current turn

---

## User

Can we save this to my Notion page “Knowledge Graphs for Fiction”?

---

## Assistant

Saved to your Notion page **Knowledge Graphs for Fiction**.

---

## User

Notion has reconnected.

---

## Assistant

I’ll reconnect the dots and append the saved conversation to that page.

---

## Assistant

Saved to your Notion page **Knowledge Graphs for Fiction**.

---

## User

Let’s proceed... planning next?

---

## Assistant

Planning is next, but not more grand architecture. We have enough architecture. The next task is to convert it into a **controlled pilot specification**.

# Immediate next stage: Pilot Planning

## Step 1: Define the pilot’s purpose

The pilot should prove that the system can take one completed novel and produce a reliable, source-grounded story model capable of answering:

- continuity questions;
- character-knowledge questions;
- timeline questions;
- object and evidence custody questions;
- promise/payoff questions;
- character and relationship arc questions.

The pilot is not intended to prove that we can ingest the entire series, generate beautiful graphs, or automate literary judgment.

## Step 2: Choose the pilot book

Book 3 was recommended as the first pilot because:

- it has the smallest apparent supporting corpus;
- it contains enough narrative complexity to test romance, suspense, character knowledge, and continuity;
- it reduces the amount of development debris to classify before reaching analytical work;
- Book 1 can later serve as the stress test.

The pilot should use only:

1. the series bible;
2. one book bible;
3. one final manuscript;
4. the final outline, if one exists;
5. selected analytical documents only when needed for comparison.

## Step 3: Create the pilot requirements document

The next governing document should be:

`STORY-GRAPH-PILOT-SPEC-v0.1.md`

It should define:

- scope;
- source files;
- non-goals;
- core questions;
- required outputs;
- accuracy targets;
- evidence requirements.

## Step 4: Establish the authority model

Five trust levels were proposed:

1. Published or final canon
2. Author-approved canonical reference
3. Current development authority
4. Analytical interpretation
5. Historical or speculative material

## Step 5: Define the canonical assertion record

```yaml
assertion_id:
subject:
predicate:
object:
assertion_type:
canonical_status:
valid_from:
valid_to:
narrative_reveal:
source_file:
source_span:
source_class:
authority_level:
confidence:
review_status:
notes:
```

## Step 6: Build the first query set

The initial queries should cover:

- canon;
- knowledge;
- timeline;
- suspense;
- romance;
- promises and payoffs.

## Step 7: Produce the corpus manifest

The manifest should include:

```text
file_id
path
book
filename
extension
source_class
development_phase
version
date
authority_level
duplicate_group
included_in_pilot
reason
```

## Recommended work order

1. `STORY-GRAPH-PILOT-SPEC-v0.1.md`
2. `CANON-AND-CONFLICT-DOCTRINE-v0.1.md`
3. `PILOT-QUERY-SET-v0.1.md`
4. `CORPUS-MANIFEST.csv`

After review, begin the manually verified scene ledger.

---

## User

Good. Continue.

---

## Assistant

Created:

`STORY-GRAPH-PILOT-SPEC-v0.1.md`

The document established:

- pilot purpose;
- provisional use of Book 3;
- governing source candidates;
- included and excluded file classes;
- required analytical outputs;
- source-authority model;
- canonical assertion format;
- minimum narrative ontology;
- context model;
- extraction plan;
- retrieval plan;
- evaluation plan;
- success criteria;
- next action.

The file was made available as:

`/mnt/data/STORY-GRAPH-PILOT-SPEC-v0.1.md`

---

## User

Continue.

---

## Assistant

Created:

`CANON-AND-CONFLICT-DOCTRINE-v0.1.md`

The doctrine defined:

- governing principles for canon;
- source classes;
- authority levels;
- assertion types;
- canonical status values;
- conflict types;
- conflict detection rules;
- precedence rules;
- resolution outcomes;
- provenance requirements;
- review requirements;
- revision doctrine;
- series-level doctrine;
- conflict-report format;
- success criteria.

The file was made available as:

`/mnt/data/CANON-AND-CONFLICT-DOCTRINE-v0.1.md`

---

## User

Continue.

---

## Assistant

Created:

`PILOT-QUERY-SET-v0.1.md`

The query set defined testable questions across:

- corpus and version identity;
- canonical characters;
- scenes and structure;
- chronology;
- character knowledge and belief;
- causality and motivation;
- objects, clues, and evidence;
- promises and payoffs;
- relationships and arcs;
- reader context and suspense;
- cross-source conflicts;
- series-level continuity;
- negative and adversarial tests.

It also defined:

- required answer structure;
- answer status values;
- evidence rules;
- query priorities;
- gold-set selection;
- acceptance rules.

The file was made available as:

`/mnt/data/PILOT-QUERY-SET-v0.1.md`

---

## User

Continue.

---

## Assistant

Created:

`CORPUS-MANIFEST-BOOK-3-v0.1.csv`

and:

`BOOK-3-CORPUS-MANIFEST-FINDINGS-v0.1.md`

The manifest classified 56 files by:

- file ID;
- path;
- source class;
- version;
- authority level;
- duplicate or revision family;
- pilot inclusion;
- canonical relevance;
- review status.

The findings report recorded the provisional conclusion that:

- `full-manuscript-v3.md`
- and `phase-8-editing/MANUSCRIPT.md`

remain competing authoritative candidates until comparison establishes the active manuscript.

The files were made available as:

- `/mnt/data/CORPUS-MANIFEST-BOOK-3-v0.1.csv`
- `/mnt/data/BOOK-3-CORPUS-MANIFEST-FINDINGS-v0.1.md`

---

## User

Continue.

---

## Assistant

Compared four manuscript states:

- `full-manuscript-v1.md`
- `full-manuscript-v2.md`
- `full-manuscript-v3.md`
- `phase-8-editing/MANUSCRIPT.md`

Created:

- `BOOK-3-MANUSCRIPT-AUTHORITY-ASSESSMENT-v0.1.md`
- `BOOK-3-MANUSCRIPT-CHAPTER-DIFF-v0.1.csv`
- `full-manuscript-v1_TO_full-manuscript-v2.diff`
- `full-manuscript-v2_TO_full-manuscript-v3.diff`
- `full-manuscript-v3_TO_phase-8-manuscript.diff`

The provisional decision was:

> Use `phase-8-editing/MANUSCRIPT.md` as the current manuscript candidate.

`full-manuscript-v3.md` remains the immediate predecessor.

The Phase 8 manuscript is marked as a current candidate, not yet as author-verified canon.

---

## User

Continue.

---

## Assistant

Created:

- `BOOK-3-SCENE-LEDGER-v0.1.csv`
- `BOOK-3-SCENE-LEDGER-BUILD-REPORT-v0.1.md`

The parser detected:

- 30 chapters;
- 153 formatted scenes.

The scene ledger is a segmentation skeleton containing:

- stable scene IDs;
- chapter placement;
- source hashes;
- word counts;
- opening and closing lines;
- placeholder analytical fields.

It intentionally does not yet claim:

- POV;
- location;
- causality;
- knowledge shifts;
- relationship shifts;
- promise or payoff interpretation.

The next planned step was:

1. create `NARRATIVE-ONTOLOGY-v0.1.md`;
2. manually validate the first three chapters against the scene ledger;
3. only then automate deeper extraction.

---

## User

From the last save point, capture the conversation to a Markdown file.
