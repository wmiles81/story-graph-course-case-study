# Reverse-engineer mode — build the v2 graph from prose alone

Use when there is **no worksheet and no graph** — a manuscript written outside the NPE
pipeline. You infer the tables a worksheet would have seeded, by reading the chapters.
Works on a **full OR partial** manuscript: process whatever chapters exist.

This is the one mode that INFERS rather than transcribes. The governing rule: **every fact
you derive from prose is provisional.** A provisional load-bearing row without an evidence
span WARNs instead of ERRORing — that is the safety net for this mode, not permission to
skip the `provisional` mark.

**Read `decisions.md` first.** It holds what earns a row and how to resolve references
that conflict; this guide holds the ORDER you do things in and which command to reach for.
Where they overlap, `decisions.md` is authoritative and this file points at it rather than
restating a weaker version.

## Steps

1. **Read the ontology** (`<SKILL_DIR>/assets/Story-Graph-Ontology-v2.md`) — you must
   produce exactly its sections (core, in order, plus any declared module's), ids, and
   controlled vocabularies.

2. **Copy the template** into the target folder as `Story-Graph.md` (native Write; never
   overwrite). Set the title from the manuscript, `ontology-version | 2`,
   `modules | none` (unless the manuscript clearly uses a module's material, e.g. SPE
   Physics State — then declare `spe`), `current-canon-chapter | 0`.

   Covering a whole series in one graph? Chapters number continuously across books and the
   header MUST carry a chapter-convention legend — see SKILL.md → *Series graphs*.

3. **Register the manuscript as a Source first.** One row in **Sources**: kebab-case
   `source-id` (e.g. `ms`), `type: manuscript`, an `authority` rank. Every quote you pull
   becomes an **Evidence** row citing this source, which is what lets the validator
   hard-verify your quotes against the real chapter files.

4. **First pass — read every chapter in order** and build a working cast/place/thread
   list. Resolve references per `decisions.md` 2.1–2.2; the two failures are symmetric and
   only the first is usually remembered — never merge on a shared surname, never split on
   a differing surface form, and record an ambiguity rather than guessing.

   Write aliases as a **`;`-separated list** in the entity's `note` (or an explicit
   `aliases` column): `Jonah; Sheriff Harrow`. That exact shape is what `validate` parses
   to catch two entities claiming one alias — free text in `note` is skipped, so an alias
   written as prose is an alias nothing checks.

5. **Populate the current-state tables by inference.** Which rows need a receipt is a rule
   the validator ENFORCES, not a matter of taste — see `decisions.md` 1.1 before writing
   your first Proposition.

   - **Entities** — each distinct person (`Character`), tracked thing (`Object`), place
     (`Location`), group (`Faction`). Infer `voice` where the prose is clear, else `-`.
   - **Locations & Distances** — travel edges only where the prose establishes a route or
     time between two `Location` entities; leave unknown `time` blank rather than invent.
   - **Relationships** — edges you can support from the text, from core edge vocabulary
     (declare any story-specific edge in Local Vocabulary first). `trend` from the arc so
     far, `since-ch` where the edge first reads as true, `span` where you can cite it.
   - **Propositions** — the claims the prose establishes. Two rules do most of the work
     here: a sentence earns a row only if a later chapter could contradict it
     (`decisions.md` 1.2), and **write events, not states** (2.4) — "Jackson dies in the
     ch20 ambush", never "Jackson is dead". A state-shaped claim flips mid-book and
     poisons every epistemic row that touches it.
   - **Epistemic States** — who knows / believes / believes-false / suspects each
     Proposition and since when, INCLUDING the reader (`holder: reader`). `believes-false`
     is the one most often missed and the most valuable: a character confidently wrong
     about something the reader knows is dramatic irony, and it is invisible unless
     recorded. Record `embargoed-until` only where the text shows a fact deliberately
     withheld.
   - **Open Loops & Setups** — planted-but-unresolved elements. Give each its **own id**,
     not the id of the proposition that planted it, and **always set `must-fire-by`**,
     even as a guess (`decisions.md` 1.4): a promise with no due date can never be
     reported broken, which makes the whole layer decorative.

6. **Run the deterministic checks before you go further.** Each turns an open-ended
   re-read into a finite list, and fixing what they find now is far cheaper than after
   fifty rows cite it:

   ```
   story_graph.py unresolved <graph> --chapters-dir <d>   # who you did not model
   story_graph.py shapes     <graph>                      # claims that cannot be pinned in time
   story_graph.py conflicts  <graph>                      # claims that may not both be true
   ```

7. **Optionally, propose the rest with a model.** You are reading this manuscript, so you
   are the best judge available — `propose <kind> --ask` writes the question to disk and
   calls nothing. Run `entities`, then `evidence`, then `epistemic`: a belief cannot name
   a holder the graph has never heard of. Every row lands as `NEEDS-HUMAN` and reaches the
   graph only through `verify-proposal` → `apply-proposal`; record what you turn down with
   `reject-proposal --reason`, so a re-run shows you what is new instead of everything
   again. See SKILL.md → *Generating rows from prose*.

8. **Then run the canon-commit loop** over the same chapters to fill the history-bearing
   tables — follow `catch-up-from-chapters.md` from `current-canon-chapter: 0`: Timeline,
   Logistics, Physics State (only under `spe`), and one Canon Commit Log line per chapter.
   You are effectively seeding and committing in a single pass.

9. **Record what rests on what** (optional, `decisions.md` 2.5). Where one claim needs
   another to be true, name it in the Proposition's `depends-on` column. `queue` then
   ranks the backlog by what would have to be revisited rather than by how many characters
   hold an opinion. Direction is the part no checker can verify: say "A, because B" aloud,
   and remember that co-occurring in one scene is not dependency.

10. **Mark provisional + incomplete.**
    - Set `current-canon-chapter` to the highest chapter you actually processed.
    - In the report, say plainly that the graph was reverse-engineered from prose, list
      the ambiguities you flagged, and — for a partial manuscript — that later chapters
      may revise these facts.

11. **Validate** (SKILL.md → *Validation*), passing `--chapters-dir` so your quotes are
    hard-verified against the real chapter files rather than degrading to a WARN. A series
    graph needs no `--chapters-dir`; its legend resolves each locator to the right book.
    Fix ERRORs (≤3 attempts); report WARNs verbatim. Many provisional-fact WARNs on a
    reverse-engineered graph are expected and correct — report them, never fabricate a
    span to silence one.
