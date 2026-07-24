# Reverse-engineer mode — build the graph from prose alone

Use when there is **no worksheet and no graph** — a manuscript that was written
outside the NPE pipeline. You will infer the same tables a worksheet would have
seeded, by reading the chapters. Works on a **full OR partial** manuscript:
process whatever chapters exist.

This is the one mode that INFERS rather than transcribes. The governing rule:
**every fact you derive from prose is provisional.** Do not present inference as
established canon.

## Steps

1. **Read the ontology** (`<SKILL_DIR>/assets/Story-Graph-Ontology-v1.md`) — you
   must produce exactly its sections, ids, and vocabulary.

2. **Copy the template** into the target folder as `Story-Graph.md` (native
   Write; never overwrite). Set the title from the manuscript, `genre-modules:
   none` (unless the host clearly declares modules AND has a genres dir),
   `current-canon-chapter: 0`.

3. **First pass — read every available chapter in order** and build a working
   cast/place/thread list. Resolve character references carefully:
   - Treat first name, surname, nickname, title, and role as possibly the SAME
     person (`Evelyn` / `Ms. Hart` / `the prosecutor`). Assign ONE kebab-case id
     per real person and record surface aliases in the `note`.
   - Do NOT merge two people just because they share a surname, nor split one
     person across two ids. When genuinely unsure, create ONE id and note the
     ambiguity in its `note` rather than silently guessing.

4. **Populate the current-state tables by inference:**
   - **Entities** — each distinct person (`Character`), tracked thing (`Object`),
     place (`Location`), and group (`Faction`). Infer `voice` for characters
     where the prose makes it clear; else `-`. Put aliases and your confidence in
     `note`.
   - **Locations & Distances** — travel edges only where the prose actually
     establishes a route/time between two `Location` entities; leave unknown
     `time` blank rather than invent.
   - **Relationships** — edges you can support from the text, drawn from core
     edge vocabulary (declare any needed story-specific edge in Local Vocabulary
     first). Set `trend` from the arc so far and `since-ch` to where the edge
     first reads as true.
   - **Knowledge States** — who knows what, with the chapter they learned it;
     record embargoes only where the text shows a fact deliberately withheld.
   - **Open Loops & Guns** — planted-but-unresolved elements (a described object,
     a threat, a secret, an unanswered question). `status = UNFIRED` if unpaid by
     the last chapter you have; `FIRED ch-N` where you saw it pay off. For a
     partial manuscript, leave still-open guns `UNFIRED`.

5. **Then run the canon-commit loop** over the same chapters to fill the
   history-bearing tables — follow `catch-up-from-chapters.md` from
   `current-canon-chapter: 0`: Physics State, Timeline, Logistics, and one Canon
   Commit Log line per chapter. (You are effectively seeding and committing in a
   single pass.)

6. **Mark provisional + incomplete.**
   - Set `current-canon-chapter` to the highest chapter you actually processed.
   - In the report, state plainly that the graph was reverse-engineered from
     prose, list any ambiguities you flagged, and — if the manuscript is partial
     — that later chapters may revise these facts.

7. **Validate** (SKILL.md → *Validation*). Fix ERRORs (≤3 attempts); report
   WARNs verbatim. Many warnings on a reverse-engineered graph are expected
   (e.g. missing Physics anchors without an SPE catalog) — report, don't
   fabricate to silence them.
