# Book 3 Act II — Step 13 Proposition and Assertion Rebuild

## Purpose

Rebuild the minimum proposition and assertion layer required by the 28 directly corrected Chapters 13–18 scenes, while preventing stale Act I analytical claims from remaining active merely because they already had IDs.

## Inputs

- six Chapters 13–18 Act II correction ledgers;
- `BOOK-3-PROPOSITION-REGISTRY-MASTER-v1.0.csv`;
- `BOOK-3-ASSERTIONS-MASTER-EVIDENCE-HARDENED-v1.2.csv`;
- governing Phase 8 manuscript;
- Act II source-authority rules.

## Stale-record audit

- Act I propositions first asserted in corrected scenes: **{…}**
- Act I assertions governed by corrected scenes: **{…}**
- Total historical records marked for supersession: **{…}**

These records are preserved as historical Act I outputs. They are no longer eligible for the Act II canon candidate unless independently rebuilt from manuscript evidence.

## Conservative rebuild

- New scene-outcome propositions: **{…}**
- New canon event assertions: **{…}**
- Knowledge and belief rows routed to normalization review: **{…}**

The rebuild deliberately creates only one conservative objective-event proposition per corrected scene.

It does not automatically convert the scene's analytical `knowledge_gained` or `belief_changes` fields into graph assertions. Those fields may refer to:

- one named character;
- several characters;
- the reader;
- a belief rather than a fact;
- an inference;
- a change in confidence rather than new knowledge.

Promoting them without normalization would recreate the epistemic errors Act II is meant to remove.

## Authority status

New event records are labeled:

- proposition: `system-rebuilt-from-direct-manuscript-scene`;
- assertion: `act-ii-direct-scene-evidence-candidate`;
- canonical status: `provisional`.

They are eligible for the Act II candidate graph after integrity and dependency checks, but they are not author-ratified canon.

## Outputs

- `BOOK-3-PROPOSITION-REGISTRY-ACT-II-SCENE-REBUILD-v1.0.csv`
- `BOOK-3-ASSERTIONS-ACT-II-SCENE-REBUILD-v1.0.csv`
- `BOOK-3-ACT-II-KNOWLEDGE-BELIEF-REBUILD-QUEUE-v1.0.csv`
- `BOOK-3-ACT-II-STALE-PROPOSITION-ASSERTION-LEDGER-v1.0.csv`

## Next step

Normalize the 28 knowledge and belief rows into individual epistemic claims, reject group statements that cannot be assigned safely, and propagate corrected object, promise, chronology, and relationship state from the rebuilt scenes.
