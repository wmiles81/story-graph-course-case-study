# The layered model

A graph is one markdown file of tables, in a fixed order. Each table is a **layer**, and the
layering is the design — every layer answers a different kind of question, and keeping them
apart is what stops the graph manufacturing contradictions that are nobody's mistake.

| Layer | Holds |
|---|---|
| **Local Vocabulary** | story-specific relationship edge types, declared before use |
| **Sources** | who or what has authority, and its rank |
| **Entities** | characters, objects, locations, factions — and their `traits` |
| **Locations & Distances** | travel routes and times |
| **Relationships** | typed edges between entities, with a trend |
| **Propositions** | the claims about the story world |
| **Epistemic States** | who knows / believes / believes-false / suspects each claim, and when |
| **Open Loops & Setups** | planted-but-unresolved elements |
| **Evidence** | verbatim source spans, hard-verified against the chapters |
| **Timeline** | chronology per chapter |
| **Logistics** | where tracked entities are, and their condition |
| **Canon Commit Log** | append-only, per-chapter history of what changed |
| **Physics State** *(module `spe`)* | character-vector / scene-axis movement per chapter |

## Why the separation matters

Consider "Jackson is alive."

Collapsed into one note, that is a single fact that flips when he turns out to be alive, and
every scene written on the old assumption silently rots.

Layered, it is four independent things:

- a **Proposition** — the claim itself
- several **Epistemic States** — the reader learns it in ch28; Jonah believed the opposite
  from ch1 until ch28; the town never learns at all
- an **Evidence** span — the sentence that proves it
- possibly a **dependency** — other claims that only make sense if it holds

Change one and you can see exactly which of the others must move. That is the whole
argument for the format.

## Everything cites, or admits it does not

A row that carries weight either points at a verbatim quote from the manuscript, or is
marked `provisional`. There is no third state, and `validate` enforces it. A `provisional`
row is not a failure — it is an honest one. What the format refuses is a claim that *looks*
established and is not.
