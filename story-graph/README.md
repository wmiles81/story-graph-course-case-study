# Story Graph

A portable skill that turns a manuscript into a **queryable model of its hidden
state** — one human-readable `Story-Graph.md` per book, checked mechanically and
(optionally) compiled into a graph database. Drop the folder into any project's
`.claude/skills/` and it works there.

`SKILL.md` is the agent-facing instruction set; this README is the human
overview. The authoritative schema is [`assets/Story-Graph-Ontology-v2.md`](assets/Story-Graph-Ontology-v2.md).

## What it tracks

Every graph is these sections, in order. This is the whole inventory:

| Section | What it holds |
|---|---|
| **Local Vocabulary** | story-specific relationship edge types, declared before use |
| **Sources** | who/what has authority (manuscript · bible · outline · editorial · draft · ghost-draft) and its rank |
| **Entities** | characters, objects, locations, factions — plus optional `traits` (`vampire`, `alpha`), the attribute a *description* resolves through |
| **Locations & Distances** | travel routes and times between locations |
| **Relationships** | typed edges between entities (trusts, protects, deceives, loves…) with a trend |
| **Propositions** | the claims about the story world, each with a canon-status (true / false / undetermined / contested), and optionally what the claim `depends-on` |
| **Epistemic States** | who **knows / believes / believes-false / suspects** each proposition, from which chapter and optionally **until** which — including the **reader**, so dramatic irony is computable — and embargoes |
| **Open Loops & Setups** | planted-but-unresolved elements (Chekhov's guns): where planted, what's expected, must-fire-by, status |
| **Evidence** | the verbatim source spans backing load-bearing claims — hard-verified against the actual chapters |
| **Timeline** | chronology per chapter (story-time, elapsed) |
| **Logistics** | where tracked entities are and their condition, per chapter |
| **Canon Commit Log** | the append-only, per-chapter history of what changed |
| **Physics State** *(with the `spe` module)* | SPE character-vector / scene-axis movement per chapter, against the anchor catalog |

The separation is the point: a **proposition** ("Jackson is alive") is kept apart
from **who knows it**, **who believes the opposite**, **what the reader knows**,
and **the passage that proves it** — so contradictions aren't manufactured by
sloppy modelling, and a claim can always show its receipt.

## Does it use AI?

**The tool uses none.** `story_graph.py` and its siblings are deterministic
Python plus an embedded graph database — no LLM calls, no network, no model.
Every command (`validate`, `compile`, `query`, `audit`, `impact`, `visualize`,
`import-legacy`, …) is rule-checking, graph traversal, and rendering: same input,
same output, offline. (`kuzu` is a database, not AI.)

**The skill is AI-operated.** `SKILL.md` is a structured prompt — it tells an
agent how to *author* the graph from prose: inferring entities, propositions, and
who-knows-what when reverse-engineering or catching up chapters, and resolving
that "Evie" / "Ms. Hart" / "the prosecutor" are one person. Seeding from a
worksheet is transcription; `import-legacy` is pure code with no AI at all.

**The split is the safety model.** The AI *proposes* — and every inferred fact is
marked `provisional` under an anti-invention rule. The deterministic code
*verifies*: an inferred claim only sheds `provisional` when it cites a verbatim
quote the validator can find in the actual chapter (`validate --chapters-dir`).
An AI can hallucinate a belief; it cannot hallucinate a sentence that is
genuinely on the page. **AI reads and proposes; the tool verifies against the
manuscript and answers deterministically** — which is why the resulting graph is
auditable and reproducible.

## What you can do with it

Run `story_graph.py` (stdlib; `compile`/`query`/`audit`/`impact` also want `pip install kuzu`):

- **Build & maintain** — `validate` (incl. graph-vs-source quote checks), plus the
  seed / reverse-engineer / catch-up / `import-legacy` modes in `reference/`.
- **Query** — `query` (irony · knows · open-loops · receipts), `report`, and
  ad-hoc **Cypher** over the compiled graph.
- **Diagnose** — `coverage` (which layers are populated, how deep, and what's missing).
- **Propose from prose** *(optional; a model, or the agent already reading the manuscript —
  `propose … --ask` writes the question to disk and calls nothing)* —
  `propose entities|evidence|epistemic|dependencies`
  reads the chapters and writes **proposal files**; `verify-proposal` then gates every row
  against the manuscript and `apply-proposal` writes only what you accept. The model never
  writes a quote — code numbers real sentences and the model picks one, so a fabricated
  quote has no way in. Rows that assert a *reading* (a belief, an entity's type, that a
  quote proves a claim) are always `NEEDS-HUMAN`, never auto-applied.
- **Review once** — `reject-proposal` records a decision (with your reason) in an
  append-only `<graph>-review.jsonl`; `verify-proposal` then skips what you have already
  decided and tells you how many rows are genuinely new. Re-running a generator costs you
  the new rows, not all of them again.
- **Check claim shape** — `shapes` lists propositions that can become false later in the
  same book ("The Founding Scrolls are missing"), ranked by how many holders already
  believe them. A Proposition has no time bounds, so these manufacture contradictions that
  are nobody's mistake. Run it before a catch-up pass; rewriting one claim now beats
  rewriting fifty rows that cite it later.
- **Find what's missing** — `unresolved` lists prose names that no entity owns (who you
  forgot to model), and `conflicts` lists claims about the same subject **partitioned by
  chapter**, because a state change and a contradiction look identical in structure and only
  the chapter tells them apart. Both are deterministic and recall-first: code enumerates,
  you judge.

  `unresolved` also separates **names from descriptions**, because they need opposite
  treatment. A common noun accepts a determiner and a proper name rejects one — "the
  Vampire", "three Trolls", never "the Margot" — and that one test splits them cleanly
  (measured on a real manuscript: descriptions 0.47–0.93, names 0.00–0.01). A description is
  **not an alias**: an alias is a rigid designator ("Sheriff Harrow" is Jonah in every
  scene), while "the Vampire" reaches Aleksei only because he *is* one. Give the bearer a
  `traits` cell and the descriptor resolves; two bearers is reported as ambiguous and left
  alone, because which one a scene means is a reading. Multi-word candidates are left
  unclassified on purpose — English lets "the Grey Guard" and "the Deep Stacks" take a
  determiner exactly as a common noun does, so no mechanical test separates them.
- **Find the irony** — `irony` lists every claim the reader knows while a character believes
  it false, over overlapping chapter windows. This needs the optional `until-ch`: without an
  end, a stance runs forever, so "he was wrong, then learned better" was inexpressible and
  showed up as a contradiction instead. Flagging an arc as an error is why the informative
  mode goes unused — a manuscript can accumulate 173 `knows` rows against 6 `believes-false`
  purely because the useful one produced warnings.
- **Decide consistently** — [`reference/decisions.md`](reference/decisions.md) is the
  inclusion & resolution rulebook (what earns a row; how to resolve one person's many
  names; when a conflict is a state change rather than a contradiction). `decisions`
  scores those calls against a fixture corpus of hard cases, so a change to the rules
  produces a number instead of an opinion. `validate` also checks alias consistency
  mechanically — it can't tell you two names are one person, but it will tell you the
  graph has claimed both readings at once.
- **Say what rests on what** — an optional `depends-on` column on Propositions records
  that one claim needs another. `queue` then ranks by structural importance rather than
  popularity: a claim underpinning a chain outranks one that merely has believers, because
  a believer can be revised in place while a dependent claim has to be revisited or it
  quietly becomes false.
- **Ratify** — `queue` (what's still provisional) and `freeze` (stamp a versioned canon baseline).
- **Audit & revise** — `audit` (continuity detectors), `impact` (what depends on a claim), `deviations` (where the prose has drifted from canon).
- **Visualize** — `visualize` writes a self-contained node-link HTML page.

For a browsable operating-system view (dashboard, interactive graph, belief
timeline, Cypher console, reports) see the separate app in [`../app/`](../app/).

## Layout

- `SKILL.md` — the instructions an agent follows (mode detection, commands, rules).
- `assets/` — the ontology (`-v2`), the blank template, and `story_graph.py` (validator/compiler/CLI).
- `reference/` — the per-mode guides (seed, reverse-engineer, catch-up) and
  [`decisions.md`](reference/decisions.md), the inclusion & resolution rulebook every mode loads.
- `tests/` — 295 mechanical checks, plus `fixtures/`: a synthetic graph and three short
  chapters so the graph-level tests run on a clone. The real manuscripts are gitignored,
  and a fixture that only exists on one machine makes a suite look green while testing
  nothing.

A `_v#` suffix means one of two opposite things, so check before deleting one. Under
**side-by-side** the unsuffixed file is the original and `_v#` is the newer revision —
`assets/story_graph_v1.py` is the still-supported validator for `ontology-version | 1`
graphs, not history. Under **shift-rename** (a name a framework loads, like `SKILL.md`)
the unsuffixed file is current and `_v#` are prior versions. Git now holds that history,
so prior versions are no longer kept in the tree.
