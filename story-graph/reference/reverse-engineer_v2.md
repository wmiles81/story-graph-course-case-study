# Reverse-engineer mode — build the v2 graph from prose alone

Use when there is **no worksheet and no graph** — a manuscript that was written
outside the NPE pipeline. You will infer the same tables a worksheet would have
seeded, by reading the chapters. Works on a **full OR partial** manuscript:
process whatever chapters exist.

This is the one mode that INFERS rather than transcribes. The governing rule:
**every fact you derive from prose is provisional.** Do not present inference as
established canon. A provisional load-bearing row without an evidence span
WARNs instead of ERRORing (see the ontology's *Evidence Span Rules*) — that is
the mechanical safety net for this mode, but it does not excuse skipping the
`provisional` mark.

## Steps

1. **Read the ontology** (`<SKILL_DIR>/assets/Story-Graph-Ontology-v2.md`) — you
   must produce exactly its sections (core, in order, plus any declared
   module's), ids, and controlled vocabularies.

2. **Copy the template** into the target folder as `Story-Graph.md` (native
   Write; never overwrite). Set the title from the manuscript,
   `ontology-version | 2`, `modules | none` (unless the manuscript is clearly
   using a module's material, e.g. SPE Physics State, in which case declare
   `spe`), `current-canon-chapter | 0`.

3. **Register the manuscript as a Source first.** Add one row to **Sources**:
   a kebab-case `source-id` (e.g. `ms`), `type: manuscript`, and an
   `authority` rank. Every quote you pull from prose in step 5 becomes an
   **Evidence** row citing this source, which is what lets the validator
   hard-verify your quotes against the actual chapter files.

4. **First pass — read every available chapter in order** and build a working
   cast/place/thread list. Resolve character references carefully:
   - Treat first name, surname, nickname, title, and role as possibly the SAME
     person (`Evelyn` / `Ms. Hart` / `the prosecutor`). Assign ONE kebab-case id
     per real person and record surface aliases in the `note`.
   - Do NOT merge two people just because they share a surname, nor split one
     person across two ids. When genuinely unsure, create ONE id and note the
     ambiguity in its `note` rather than silently guessing.

5. **Populate the current-state tables by inference**, adding an **Evidence**
   row (with a real quote) for every load-bearing claim as you go:
   - **Entities** — each distinct person (`Character`), tracked thing (`Object`),
     place (`Location`), and group (`Faction`). Infer `voice` for characters
     where the prose makes it clear; else `-`. Put aliases and your confidence in
     `note`.
   - **Locations & Distances** — travel edges only where the prose actually
     establishes a route/time between two `Location` entities; leave unknown
     `time` blank rather than invent.
   - **Relationships** — edges you can support from the text, drawn from core
     edge vocabulary (declare any needed story-specific edge in Local
     Vocabulary first). Set `trend` from the arc so far and `since-ch` to where
     the edge first reads as true; cite the passage in `span` where you can.
   - **Propositions** — the premise-level facts the prose establishes as
     `true` (or `false`, `undetermined`, `contested`), each with a
     `governing-source` of the manuscript Source and a `span` to the Evidence
     row quoting the passage.
   - **Epistemic States** — who knows/believes/suspects each Proposition and
     since which chapter, including the reader's own knowledge state
     (`holder: reader`) wherever the prose reveals something to the reader
     before or after a character learns it — this is exactly where dramatic
     irony becomes mechanically visible. Record embargoes
     (`mode: embargoed-until`) only where the text shows a fact deliberately
     withheld until a later chapter.
   - **Open Loops & Setups** — planted-but-unresolved elements (a described object,
     a threat, a secret, an unanswered question). `status = UNFIRED` if unpaid by
     the last chapter you have; `FIRED ch-N` where you saw it pay off. For a
     partial manuscript, leave still-open setups `UNFIRED`. Cite the planting
     passage in `span`.

6. **Then run the canon-commit loop** over the same chapters to fill the
   history-bearing tables — follow `catch-up-from-chapters.md` from
   `current-canon-chapter: 0`: Timeline, Logistics, Physics State (only under
   the `spe` module), and one Canon Commit Log line per chapter. (You are
   effectively seeding and committing in a single pass.)

7. **Mark provisional + incomplete.**
   - Set `current-canon-chapter` to the highest chapter you actually processed.
   - In the report, state plainly that the graph was reverse-engineered from
     prose, list any ambiguities you flagged, and — if the manuscript is partial
     — that later chapters may revise these facts.

8. **Validate** (SKILL.md → *Validation*), passing `--chapters-dir` so your
   pulled quotes are hard-verified against the real chapter files rather than
   degrading to a WARN. Fix ERRORs (≤3 attempts); report WARNs verbatim. Many
   provisional-fact WARNs on a reverse-engineered graph are expected and
   correct — report them, don't fabricate spans to silence them.




## Claim
A: The Purge Protocol will erase the library and everyone inside after twelve hours.
B: The Founding Scrolls are discovered missing from the vault in ch02.

## Expect
- depends: a-needs-b       ← my call
