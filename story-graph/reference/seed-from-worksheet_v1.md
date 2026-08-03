# Seed mode — build the initial v2 graph from a worksheet

Use when an NPE **YFD-RAW worksheet** (`*YFD-RAW*.md` or `master_story_document.md`)
exists but no `Story-Graph.md` does yet. The worksheet already states the story's
facts, so seeding is transcription, not invention.

**Read `decisions.md` alongside this.** Seeding is transcription, so most of its
judgement calls do not arise — but two do, because a worksheet does not make them for you:
resolving one person's several names to one id (2.1–2.2), and writing claims as EVENTS
rather than states (2.4). A worksheet routinely says "Jackson is alive"; the graph wants
the event that made it true, or it will contradict itself by the last act.

## Steps

1. **Read the ontology first** — `<SKILL_DIR>/assets/Story-Graph-Ontology-v2.md`.
   It defines the exact section order (core + declared modules), entity
   types, controlled vocabularies, and per-table schemas you must obey.

2. **Copy the template.** Copy `<SKILL_DIR>/assets/Story-Graph-TEMPLATE-v2.md`
   into the target folder as `Story-Graph.md` (native Write — never overwrite
   an existing file). Set:
   - the title line `# Story Graph: <Title>`
   - `ontology-version | 2`
   - `modules` — the ordered list declared in the worksheet RDL (e.g. `spe`
     for a romance/NPE project), or `none`
   - `current-canon-chapter | 0`
   - For a series-continuous graph, add the header blockquote legend of per-book
     chapter ranges (see the ontology's *Multi-Book Series Graphs*).

3. **Populate current-state tables from the worksheet** (leave Timeline,
   Logistics, Physics State (`spe` module only), and the Canon Commit Log
   EMPTY — those fill at canon commits):

   - **Sources** — register the worksheet/bible/outline itself (and any
     editorial notes) as `source-id`s with a `type` from the vocabulary
     (`manuscript`, `bible`, `outline`, `editorial`, `draft`, `ghost-draft`)
     and an `authority` rank (higher = more authoritative for the facts it
     governs).
   - **Entities** — every character, object, faction, and setting location as a
     kebab-case `id`. Type each (`Character`/`Object`/`Location`/`Faction`).
     Give each Character a `voice` value (`female`/`male`/`-`). One-line `note`.
   - **Locations & Distances** — for each pair of settings the story moves
     between, a travel edge with `time` and `mode` (both endpoints must be
     `Location` entities).
   - **Relationships** — the initial relationship edges. Edges MUST come from
     the core edge vocabulary, a declared module's extensions, or the graph's own Local
     Vocabulary. If you need a story-specific edge, declare it in **Local
     Vocabulary** FIRST, then use it. Set `trend` and `since-ch`; add a `span`
     if the worksheet cites a specific passage that establishes the edge.
   - **Propositions** — premise-level claims the worksheet asserts, each a
     kebab-case `prop-id`, a `statement`, a `canon-status` (usually `true` for
     established worksheet facts), and a `governing-source` pointing at the
     worksheet/bible Source. A `true`/`false` proposition needs a `span` — add
     the corresponding **Evidence** row (see below) first.
   - **Epistemic States** — who stands in what relation to each Proposition:
     one row per `(prop-id, holder)` pair, `holder` an Entity id or the
     reserved id `reader`, `mode` from `knows` / `believes` /
     `believes-false` / `suspects` / `embargoed-until`. This is where v1's
     Knowledge States *and* reader dramatic-irony tracking both live now.
     Every mode except `embargoed-until` needs a `span`.
   - **Evidence** — one row per `span-id` your Propositions/Epistemic
     States/Open Loops cite: `source-id` (the worksheet/bible Source),
     `locator` (a heading/anchor in that document), and `quote` (a verbatim
     substring — required whenever `source-id` is a `manuscript` source;
     recommended for other types too so the claim is auditable).
   - **Open Loops & Setups** — obligatory scenes and planted setups, each a
     kebab-case `id`, with `planted-ch`, `expectation`, `must-fire-by`, and
     `status` = `UNFIRED`, plus a `span` citing where it was planted.

4. **Do not invent.** Use only what the worksheet establishes. If the worksheet
   is silent on something the schema wants, leave it blank rather than fabricate;
   if you must add a fact to make the graph coherent, mark the row
   **provisional** (the word "provisional" in any cell of that row) rather
   than fabricate a quote — a provisional load-bearing row without a span
   WARNs instead of ERRORing.

5. **Catch up, then validate.** If finalized chapters already exist above
   ch 0, continue into `catch-up-from-chapters.md`. Then run the validator
   (see SKILL.md → *Validation*), passing `--chapters-dir` so any
   `manuscript`-sourced Evidence quotes are hard-verified.
