# Book 3 Event Normalization Pilot Report v0.1

**Scope:** Chapters 1–3  
**Source:** Frozen Book 3 scene ledger and linked assertion/proposition canon  
**Candidate events:** 49  
**Scenes covered:** 15  
**Validation:** 7/7 checks passed

## Method

Each semicolon-delimited item in `major_events_candidate` was treated as one provisional event candidate. Candidates inherit the scene location and outcome context, resolve participants against the frozen entity registry, and link to assertions/propositions anchored to the same scene.

## What this pilot proves

- stable event IDs can be added without replacing scene IDs;
- candidate events can link cleanly to the existing graph;
- lineage to the scene ledger is explicit;
- candidates remain non-canonical until reviewed.

## What this pilot does not prove

- that every semicolon-delimited phrase is the correct event granularity;
- that all participants listed as present actively participate in each event;
- that scene outcome text is always the event's changed state;
- that same-scene assertions necessarily belong to every event in that scene;
- that no event spans multiple scenes.

## Required review before scaling

1. Split or merge event candidates where scene-ledger phrasing is too coarse or too fine.
2. Remove merely present characters from participant lists.
3. Replace scene-wide proposition/assertion links with event-specific links.
4. Identify multi-scene events.
5. Ratify the event-type vocabulary.

No accepted canon was modified.
