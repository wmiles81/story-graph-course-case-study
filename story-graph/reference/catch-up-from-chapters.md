# Catch-up mode — commit finalized chapters into the v2 graph

Use when a `Story-Graph.md` already exists and chapters sit above its
`current-canon-chapter` high-water mark. This is the canon-commit loop: it walks
each uncommitted chapter in order and folds its deltas into the graph.

## Steps

1. **Read the ontology** (`<SKILL_DIR>/assets/Story-Graph-Ontology-v2.md`),
   especially *Update Rules (Canon Commit)*, *Evidence Span Rules*, and the
   per-table schemas.

2. **Find the frontier.** Read the graph's header `current-canon-chapter` (call
   it `C`). Discover chapters (see SKILL.md → *Chapter discovery*). Select every
   chapter with number `> C`, in ascending order. Highest version per chapter
   wins (`_Final_v2.md` over `_Final.md`).

3. **Commit each chapter in order.** For chapter `N`, read it and extract deltas,
   then update the current-state tables — adding an **Evidence** row (real
   quote from chapter `N`, `source-id` the manuscript Source) for every
   load-bearing claim you add or change:
   - **Relationships** — edges that formed, hardened/softened, broke, or
     reversed (update `trend`, `since-ch`; add new edges — declare any new edge
     in Local Vocabulary first). Cite a `span` where the change is on-page.
   - **Propositions** — new premise-level facts this chapter establishes, or a
     `canon-status` change (e.g. `undetermined` → `true`) on an existing one;
     each `true`/`false` proposition needs a `span`.
   - **Epistemic States** — who learns/believes/suspects what this chapter,
     including reader awareness (`holder: reader`) if the prose reveals
     something to the reader this chapter. Append new rows rather than
     editing history — a character's epistemic state is a new row at the new
     `since-ch`, not an edit of the old one. Respect embargoes — never record
     a `knows` row at a chapter before its `embargoed-until` chapter; that is
     an ERROR.
   - **Open Loops & Setups** — setups that fired (`FIRED ch-N`) or were defused
     (`DEFUSED ch-N`); new setups planted this chapter (`UNFIRED`). Every row
     needs a `span`.
   - **Entities** — new entities introduced; status changes (e.g. `active` →
     `deceased`, `departed`).
   - **Physics State** (`spe` module only) — one row per moved vector/axis for
     chapter `N` (see Ontology-v2's *Module: `spe`* Physics State schema). If the
     host supplies an SPE anchor catalog (`--spe-dir`), use catalog anchor ids
     from it — an unknown anchor is a validation ERROR; with no catalog the
     anchors are best-effort free-form (a WARN). `intimacy-ladder` /
     `door-closed` anchors are always free-form.
   - **Timeline** — a row for chapter `N`: `story-time`, `elapsed`, `note`.
   - **Logistics** — where tracked entities are and their condition. Any
     `condition` value that records a change needs a `span`.

4. **Advance and log.** Set `current-canon-chapter: N`. Append ONE line to the
   Canon Commit Log: `- ch N: <plain-language deltas>` (for a series graph, add
   the `(B# chN)` mapping). Log chapters must be strictly increasing.

5. **Provisional sourcing.** If the chapters are drafts (not Finals), mark the
   run provisional and say so in the report — canon normally commits only at
   Final. Never invent a fact to fill a gap; leave it and flag it. A
   provisional load-bearing row without a span WARNs rather than ERRORs, but
   still needs the `provisional` mark to get that treatment.

6. **Validate** once the loop is done (SKILL.md → *Validation*), passing
   `--chapters-dir` so this chapter's quotes are hard-verified. Fix ERRORs
   (≤3 attempts); report WARNs verbatim.
