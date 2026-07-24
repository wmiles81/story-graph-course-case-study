# Catch-up mode — commit finalized chapters into the graph

Use when a `Story-Graph.md` already exists and chapters sit above its
`current-canon-chapter` high-water mark. This is the canon-commit loop: it walks
each uncommitted chapter in order and folds its deltas into the graph.

## Steps

1. **Read the ontology** (`<SKILL_DIR>/assets/Story-Graph-Ontology-v1.md`),
   especially *Update Rules (Canon Commit)* and the per-table schemas.

2. **Find the frontier.** Read the graph's header `current-canon-chapter` (call
   it `C`). Discover chapters (see SKILL.md → *Chapter discovery*). Select every
   chapter with number `> C`, in ascending order. Highest version per chapter
   wins (`_Final_v2.md` over `_Final.md`).

3. **Commit each chapter in order.** For chapter `N`, read it and extract deltas,
   then update the current-state tables:
   - **Relationships** — edges that formed, hardened/softened, broke, or
     reversed (update `trend`, `since-ch`; add new edges — declare any new edge
     in Local Vocabulary first).
   - **Knowledge States** — facts learned (append `id (chN)` to `known-by`); new
     facts get a new `fact-id`. Respect embargoes — never record someone
     learning a fact before its `until chN`.
   - **Open Loops & Guns** — setups that fired (`FIRED ch-N`) or were defused
     (`DEFUSED ch-N`); new setups planted this chapter (`UNFIRED`).
   - **Entities** — new entities introduced; status changes (e.g. `active` →
     `deceased`, `departed`).
   - **Physics State** — one row per moved vector/axis for chapter `N` (see the
     ontology's Physics State schema). If the host has an SPE anchor catalog, use
     catalog anchor IDs; otherwise use best-effort free-form and let the
     validator warn.
   - **Timeline** — a row for chapter `N`: `story-time`, `elapsed`, `note`.
   - **Logistics** — where tracked entities are and their condition, when it
     matters for continuity.
   - Do **not** touch **Private Beliefs (Ghost)** — only a Ghost Draft writes it.

4. **Advance and log.** Set `current-canon-chapter: N`. Append ONE line to the
   Canon Commit Log: `- ch N: <plain-language deltas>` (for a series graph, add
   the `(B# chN)` mapping). Log chapters must be strictly increasing.

5. **Provisional sourcing.** If the chapters are drafts (not Finals), mark the
   run provisional and say so in the report — canon normally commits only at
   Final. Never invent a fact to fill a gap; leave it and flag it.

6. **Validate** once the loop is done (SKILL.md → *Validation*). Fix ERRORs
   (≤3 attempts); report WARNs verbatim.
