# Seed mode — build the initial graph from a worksheet

Use when an NPE **YFD-RAW worksheet** (`*YFD-RAW*.md` or `master_story_document.md`)
exists but no `Story-Graph.md` does yet. The worksheet already states the story's
facts, so seeding is transcription, not invention.

## Steps

1. **Read the ontology first** — `<SKILL_DIR>/assets/Story-Graph-Ontology-v1.md`.
   It defines the exact section order, entity types, core edge vocabulary,
   trends, and per-table schemas you must obey.

2. **Copy the template.** Copy `<SKILL_DIR>/assets/Story-Graph-TEMPLATE.md` into
   the target folder as `Story-Graph.md` (native Write — never overwrite an
   existing file). Set:
   - the title line `# Story Graph: <Title>`
   - `genre-modules` — the ordered list declared in the worksheet RDL, or `none`
   - `current-canon-chapter: 0`
   - For a series-continuous graph, add the header blockquote legend of per-book
     chapter ranges (see the ontology's *Multi-Book Series Graphs*).

3. **Populate current-state tables from the worksheet** (leave Physics State,
   Timeline, Logistics, Private Beliefs, and the Canon Commit Log EMPTY — those
   fill at canon commits and via a Ghost Draft):

   - **Entities** — every character, object, faction, and setting location as a
     kebab-case `id`. Type each (`Character`/`Object`/`Location`/`Faction`).
     Give each Character a `voice` value (`female`/`male`/`-`). One-line `note`.
   - **Locations & Distances** — for each pair of settings the story moves
     between, a travel edge with `time` and `mode` (both endpoints must be
     `Location` entities).
   - **Relationships** — the initial relationship edges. Edges MUST come from
     the core edge vocabulary, a declared genre module, or the graph's own Local
     Vocabulary. If you need a story-specific edge, declare it in **Local
     Vocabulary** FIRST, then use it. Set `trend` and `since-ch`.
   - **Knowledge States** — premise-level facts, each a kebab-case `fact-id`,
     with `known-by` (`id (chN)`) and any `embargoed-from` (`id (until chN)`).
   - **Open Loops & Guns** — obligatory scenes and planted setups, each a
     kebab-case `id`, with `planted-ch`, `expectation`, `must-fire-by`, and
     `status` = `UNFIRED`.

4. **Do not invent.** Use only what the worksheet establishes. If the worksheet
   is silent on something the schema wants, leave it blank rather than fabricate;
   if you must add a fact to make the graph coherent, mark it provisional in the
   `note` and tell the user.

5. **Catch up, then validate.** If finalized chapters already exist above
   ch 0, continue into `catch-up-from-chapters.md`. Then run the validator
   (see SKILL.md → *Validation*).
