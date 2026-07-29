# Proposed Analytical Layers v0.1

This proposal is intentionally narrow. Each layer exists only because it answers questions the current frozen graph cannot answer reliably.

## Layer A — Event and Plot-Thread Model

### Artifacts

- `EVENT-REGISTRY`
- `PLOT-THREAD-REGISTRY`
- `EVENT-THREAD-MEMBERSHIP`
- `PLOT-INTERSECTION-LEDGER`

### Questions answered

- Which events constitute each plot or subplot?
- Which scenes serve more than one thread?
- What does each event contribute to each thread?
- Where do threads intersect?
- What transfers at the intersection, and does it alter later outcomes?

## Layer B — Causal and Irreversibility Model

### Artifacts

- `CAUSAL-DEPENDENCY-LEDGER`
- `ENABLING-CONDITION-LEDGER`
- `NARRATIVE-IRREVERSIBILITY-LEDGER`

### Questions answered

- What had to be true before an event could occur?
- What merely enabled it?
- What changed because of it?
- Which options closed permanently?
- What would reversal cost?

## Layer C — World-Rule Model

### Artifacts

- `WORLD-RULE-REGISTRY`
- `WORLD-RULE-ASSERTIONS`
- `WORLD-RULE-EXCEPTION-LEDGER`

### Questions answered

- What rules does the story establish?
- Which are explicit, inferred, or merely believed?
- Where are exceptions explained?
- Which apparent exceptions are contradictions?

## Layer D — Reader and Epistemic Expansion

### Artifacts

- `READER-KNOWLEDGE-TIMELINE`
- `DRAMATIC-IRONY-WINDOWS`
- `CROSS-BOOK-KNOWLEDGE-CARRYOVER`

### Questions answered

- What does the reader know at each point?
- What does each character know, believe, suspect, or misunderstand?
- Where does the manuscript leak information early?
- What knowledge must carry into later books?

## Layer E — Spatial and Blocking Continuity

### Artifacts

- `LOCATION-TOPOLOGY`
- `SCENE-BLOCKING-LEDGER`
- `OBJECT-PLACEMENT-LEDGER`
- `SPATIAL-CONTINUITY-AUDIT`

### Questions answered

- Who is where, facing what, holding what, and able to reach whom?
- Are entrances, exits, movements, and repeated actions physically possible?
- Does object placement agree with custody?

## Layer F — Structural Sufficiency

### Artifacts

- `SCENE-STATE-CHANGE-AUDIT`
- `STRUCTURAL-SUFFICIENCY-AUDIT`
- `SUBPLOT-CONTRIBUTION-AUDIT`

### Questions answered

- What changes in each scene?
- Which scenes are redundant or inert?
- Where is setup missing, payoff missing, or a bridge absent?
- Does each subplot materially serve the story?

## Layer G — Series Continuity

### Artifacts

- `SERIES-ENTITY-REGISTRY`
- `BOOK-SERIES-IDENTITY-MAP`
- `SERIES-CHRONOLOGY`
- `SERIES-STATE-CARRYOVER`
- `SERIES-PROMISE-LIFECYCLE`
- `RETCON-CLARIFICATION-LEDGER`
- `SPOILER-SCOPE-MATRIX`
- `CROSS-BOOK-REVISION-IMPACT`

### Questions answered

- Is the same person, object, place, institution, or rule represented consistently across books?
- What state carries from one book into the next?
- Which promises remain open across volumes?
- Is a later statement a contradiction, clarification, reinterpretation, or deliberate retcon?
- What breaks elsewhere if one book changes?

## Discovery-only network measures

Centrality, betweenness, community detection, and clustering may be used to propose review targets. They never create canon by themselves. A highly connected node may be important, over-recorded, or merely a clerical hub. Computers remain tragically unable to distinguish those without context.
