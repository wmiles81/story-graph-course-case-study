# BOOK 3 CHAPTERS 1–3 SCENE VALIDATION REPORT v0.1

**Source:** `series/books/book-3/phase-8-editing/MANUSCRIPT.md`  
**Validated scenes:** 15  
**Chapters:** 1–3  
**Status:** Manual pilot validation

---

## 1. Segmentation Result

The formatting-based scene ledger correctly identified five scene units in each of the first three chapters.

| Chapter | POV | Scenes | Segmentation result |
|---|---|---:|---|
| Chapter 1 | Jonah Harrow | 5 | Confirmed |
| Chapter 2 | Margot Vance | 5 | Confirmed |
| Chapter 3 | Jonah Harrow | 5 | Confirmed |

No additional unmarked scene boundary was required in these chapters.

---

## 2. Major Story-State Progression

### Chapter 1

1. Jonah resolves a routine supernatural bar fight.
2. His wolf detects an approaching danger.
3. He traces the disturbance to the library and recognizes Margot's mate scent.
4. He discovers Margot containing animated books in an impossible basement.
5. The library seals itself, trapping them.

### Chapter 2

1. Margot partially reveals the library's wards and hidden knowledge.
2. She discovers the Founding Scrolls are missing.
3. She explains the lethal importance of the Scrolls and the twelve-hour Purge Protocol.
4. Meredith identifies Level B4 as the route to recovery.
5. Margot and Jonah enter the Deep Stacks together.

### Chapter 3

1. They enter B1 and learn the Deep Stacks distort space and contain active books.
2. Jonah protects Margot from a flying book and encounters a bibliovore.
3. A lexivore emerges as Jonah struggles with mate recognition.
4. They defeat or evade it through Margot's tactical use of books and light.
5. They enter B2 holding hands and explicitly commit to proceeding together.

---

## 3. Knowledge-State Milestones

- Jonah first knows the library contains active old magic in Chapter 1, Scene 4.
- Jonah learns Margot has a hidden custodial role in Chapter 1, Scene 5 and Chapter 2, Scene 1.
- Margot confirms the Founding Scrolls are missing in Chapter 2, Scene 2.
- Jonah learns the Scrolls contain dangerous truths about the town in Chapter 2, Scene 3.
- Both learn the library will erase itself in twelve hours in Chapter 2, Scene 3.
- Both learn recovery requires reaching Level B4 in Chapter 2, Scene 4.
- Jonah learns specific Deep Stacks hazards progressively through Chapter 3.

No impossible-knowledge defect was identified in Chapters 1–3.

---

## 4. Object and Custody Milestones

- The biting book is controlled by Margot after Chapter 1, Scene 5.
- Margot conceals and retains her grandmother's journal in Chapter 2, Scene 1.
- The three Founding Scrolls are confirmed missing in Chapter 2, Scene 2; current custody is unknown.
- Margot retains the Deep Stacks key and flashlight.
- A flying book passes from shelf to Jonah to a bibliovore in Chapter 3, Scene 2.
- Several books are sacrificed to the lexivore in Chapter 3, Scene 4.

The missing Scrolls create the first critical custody gap.

---

## 5. Promise and Payoff Milestones

Promises introduced:

- supernatural law-enforcement premise;
- approaching magical danger;
- library mystery;
- mate-bond romance;
- Margot's hidden Keeper role;
- missing Founding Scrolls;
- dangerous truth about Snowfall Creek's founding;
- twelve-hour survival countdown;
- descent through four unstable levels;
- escalating romantic partnership.

Early payoffs:

- Jonah's sensed wrongness resolves into the library crisis.
- The sealed doors are explained by the Purge Protocol.
- The mission to reach B4 becomes active.
- Margot's warning that the lower stacks are dangerous is demonstrated by bibliovore and lexivore encounters.
- The initial trust promise advances into explicit cooperation and handholding.

---

## 6. Ontology Findings

The v0.1 ontology adequately represents the first fifteen scenes.

Classes exercised:

- Character
- Scene
- Location
- Object
- Event
- Action
- KnowledgeState
- BeliefState
- RelationshipState
- PossessionState
- Secret
- Clue
- NarrativePromise
- Payoff
- NarrativeThread

Relations exercised:

- APPEARS_IN
- OCCURS_AT
- KNOWS
- BELIEVES
- DISCOVERS
- POSSESSES
- TRANSFERS_TO
- CAUSES
- ENABLES
- INTRODUCES
- ESCALATES
- FULFILLS
- FOCALIZED_THROUGH

No new ontology class is required yet.

A likely future refinement is a controlled class for **Environmental or Institutional Agent**, because the library itself acts with apparent agency. For now, the library may be represented as a Location participating in Events. Creating a sentient-building class after three chapters would be premature enthusiasm.

---

## 7. Confidence and Limitations

High confidence:

- chapter and scene boundaries;
- POV;
- principal locations;
- present major characters;
- explicit events;
- explicit knowledge acquisition;
- direct object transfers.

Medium confidence:

- scene goal and opposition;
- relationship-state changes;
- narrative promises;
- partial payoffs;
- causal interpretation.

The validated ledger remains a pilot artifact. Interpretive fields should not yet be treated as author-verified canon.

---

## 8. Next Action

Create `ASSERTION-CONTEXT-MODEL-v0.1.md`, then convert Chapters 1–3 into normalized assertion records.

This will test whether the ontology can represent:

- the missing Scrolls as canonical fact;
- Jonah's mate belief separately from author-verified truth;
- Margot's concealed knowledge;
- the twelve-hour deadline;
- object custody;
- reader knowledge;
- revision and source provenance.
