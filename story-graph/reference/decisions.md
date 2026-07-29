# Decisions: inclusion & resolution

Load this in **every** mode — seed, reverse-engineer, catch-up, import. Those guides say
*how* to fill each section; this one says *what earns a row* and *how to reconcile
references that conflict*. Those two decisions are where a story graph is made good or
useless, and they are the decisions the validator cannot make for you.

Two things the tool cannot check, ever:

- that the **right** rows exist (it only checks the rows you wrote)
- that two names are **one person** (it only checks that ids resolve)

Everything below exists because of those two sentences.

---

# Part 1 — Inclusion: what earns a row

## 1.1 The receipt gate — what "load-bearing" actually means

`load-bearing` is enforced, not advisory. A load-bearing row must cite an Evidence span
or be marked `provisional`; otherwise `validate` **errors**. Know which rows those are
before you write them, not after the validator complains:

| Section | Needs a receipt when | Exempt |
|---|---|---|
| **Propositions** | `canon-status` is `true` or `false` | `undetermined`, `contested` |
| **Epistemic States** | mode is `knows` / `believes` / `believes-false` / `suspects` | `embargoed-until` |
| **Open Loops & Setups** | always | — |
| Entities · Relationships · Timeline · Logistics · Locations | never | all |

Two consequences worth internalising:

- **`undetermined` is the honest default.** A claim you can't yet source is `undetermined`
  and costs nothing. Marking it `true` without a quote is the error.
- **`provisional` is a promise, not an escape hatch.** It says *"a human still has to look
  at this"*, and `queue` will keep showing it until someone does.

## 1.2 Does this even earn a proposition?

One test:

> **Could a later chapter contradict it?**

If no, it is prose, not a claim, and it does not belong in the graph.

| Sentence | Row? | Why |
|---|---|---|
| "The library smelled of old paper and dust." | no | atmosphere; nothing can contradict it |
| "The library contains active old magic." | **yes** | a later chapter could deny it |
| "Rows of shelves disappeared into the darkness." | no | scenery |
| "The basement contains impossible architecture." | **yes** | load-bearing world rule |
| "She had never been to the basement." | **yes** | and note it is *state-shaped* — see 2.4 |

Recording atmosphere is not harmless. Every inert row dilutes the queue, the coverage
numbers, and the graph you have to read.

## 1.3 The emphasis ladder — what earns an Open Loop

Narrative attention creates obligation. Sort each emphasised element into one of:

**atmosphere · character revelation · clue · setup · motif · red herring**

The last four create a reader expectation and earn an Open Loop row. The first two do not.

The rule runs **both ways**, and the second direction is the one that gets skipped:

- a row for atmosphere is noise
- an element given vivid, repeated, or loaded attention and given **no** row is a missed
  promise — the exact failure the ledger exists to catch

## 1.4 `must-fire-by` is not optional

In the Book 3 fixture, **10 of 10 open loops have an empty `must-fire-by`**. Nothing can
ever be reported overdue, so the entire setup layer is decorative — it records that a
promise was made and can never report that it was broken.

- Every Open Loop gets a `must-fire-by`, **even if it is a guess**. A wrong deadline is
  revisable; a missing one is unfalsifiable.
- Leave it empty **only** for a payoff deliberately deferred past this book, and say so in
  the note, naming the book.
- Give the loop **its own id**. Reusing the id of the proposition that planted it conflates
  the claim with the obligation it created; they have different lifetimes and only one of
  them can be "fired".

## 1.5 What must NOT become a row

The anti-invention rule, as a checklist. Do not create:

- backstory the prose does not state (a job, a relative, a former marriage)
- named walk-ons who never matter again
- scenery that never returns
- a belief you inferred with no line you can point at
- a distance, travel time, or elapsed duration you estimated rather than read

When the story genuinely needs one of these, write it **and** mark it `provisional`, so it
enters the queue rather than the canon. Inventing quietly is the one failure that makes
every other number in the graph a lie.

---

# Part 2 — Resolution: reconciling references and conflicts

## 2.1 One person, many surfaces

Every reference resolves to one canonical kebab-case id. The same person may appear as:

first name · surname · full name · nickname · title · role · relationship label · a
POV-specific endearment or insult

> "Evelyn Hart" · "Evelyn" · "Hart" · "Evie" · "Ms. Hart" · "the prosecutor" · "his ex-wife"

Record the aliases **and who uses each one**. Who calls her "Evie" is evidence about the
speaker, not merely a synonym — and it is the thing that tells you a POV character's
stance without a single line of interiority.

**The two failures are symmetric, and only the first is usually remembered:**

- **Never merge on a shared surname.** "Hart" and "Ms. Hart" in one scene may be two people.
- **Never split on a differing surface form.** "Evie" and "the prosecutor" may be one.

## 2.2 Ambiguity is a valid outcome

When you cannot resolve a reference, an **ambiguity note is the correct answer** — not a
confident guess, and not silence. Name both candidate ids and the line that is ambiguous.

A guess that turns out wrong corrupts every downstream row that trusted it. A recorded
ambiguity costs one line and resolves itself the moment the prose disambiguates.

## 2.3 Conflict → source authority

Two sources disagree. The ranks already exist in the Sources table:

```
manuscript 100  >  bible  >  outline  >  editorial  >  draft  >  ghost-draft
```

- **Higher rank wins.** The loser's proposition becomes `canon-status: false`, or is
  retired — with a Canon Commit Log line saying which source overrode which and why.
- **Equal rank does not get picked.** Mark it `contested` and leave it. `contested` is
  exempt from the receipt gate precisely so an unresolved conflict can be recorded
  honestly rather than resolved by coin-flip.
- Never silently drop the losing row. A conflict that leaves no trace will be
  re-discovered and re-argued.

## 2.4 State change is not contradiction

"Jackson is alive" (ch03) and "Jackson is dead" (ch20) are **not** a contradiction. They
are one state transition. The same pair inside a single chapter **is** a bug.

Ontology v2 gives a Proposition a `canon-status` but **no time bounds**, so it cannot
express "true until ch20" on its own. Therefore:

> **Prefer event-shaped propositions to state-shaped ones.**

| Avoid (state-shaped) | Prefer (event-shaped) |
|---|---|
| "Jackson is dead." | "Jackson dies in the ch20 ambush." |
| "Margot has never been to the basement." | "Margot first enters the basement in ch14." |
| "Jonah and Margot are estranged." | "Jonah and Margot break contact after ch07." |

An event-shaped proposition is **permanently** true once it happens, so it never has to be
flipped, and a later chapter cannot contradict it without contradicting the manuscript.
State-shaped claims need constant maintenance and generate false contradictions.

**This rule is now checked.** `story_graph.py shapes <graph>` lists every state-shaped
proposition, riskiest first — those something already believes, because that is where the
contradiction is already reachable. `validate` separately warns when one holder ends up
both knowing a claim and believing it false, which is the state-shaped trap having sprung.

The cost of ignoring it, measured: a full-book epistemic pass proposed
`reader believes-false: "The Founding Scrolls are missing"` for chapters 21, 22, 28 and 29
— **correct at those chapters**, because by ch29 the Scrolls are recovered. The generator
was right and the claim was unrepresentable. Two other detectors converge on the same five
claims: `conflicts` pairs "Jackson Harrow is alive and being used as an Alpha-class battery"
with "Jackson Harrow is freed from the Alpha battery tank", and cannot partition them,
because neither is anchored to a chapter.

Where a state genuinely matters at a moment in time, that is what **Logistics** (per
chapter: entity, location, condition) and **Relationships** (with a `trend`) are for.
Use them instead of a state-shaped proposition.

## 2.5 Say what a claim rests on

`queue` ranks the ratification backlog by dependency weight — holders, evidence spans,
+3 where the claim carries dramatic irony, and **2 per claim that rests on it**.

Record that last part yourself, in the optional `depends-on` column on Propositions:

| prop-id | statement | … | depends-on |
|---|---|---|---|
| p-000007 | The Scrolls are discovered missing from the vault in ch02. | … | |
| p-000009 | The Purge Protocol will erase the library after twelve hours. | … | p-000007 |
| p-000010 | Returning the Scrolls through B4 can stop the Purge Protocol. | … | p-000009 |

Read it as **"this claim needs that one to be true"**. The direction is easy to reverse and
the tool cannot catch you doing it, so say it aloud when you write the row: the Purge fires
*because* the Scrolls left containment, so p-000009 depends on p-000007.

Weight is transitive. p-000007 above carries three dependents, one of them two hops away,
and that took it from score 3 to 10 — past a claim with four believers and an irony bonus.
Which is the point: **a believer can be revised in place, but a dependent claim has to be
revisited or it quietly becomes false.**

Without this column a foundational claim nobody has an opinion about scores zero, exactly
like an inert one. On Book 3 that was 49 of 122 propositions.

### Getting the direction right

Two tests, and neither uses the order the claims were handed to you in:

**Say it aloud.** "A, because B" and "B, because A". Exactly one is true.

> "The Purge fires *because* the Scrolls left containment." ✓
> "The Scrolls left containment *because* the Purge fires." ✗

**Delete one and see what collapses.** Remove the foundation and the dependent claim stops
making sense; remove the dependent and the foundation is untouched.

> Delete "Margot possesses the journal" → "Margot conceals the journal" is nonsense.
> Delete "Margot conceals the journal" → "Margot possesses the journal" is unaffected.

Chronology is a hint, not the rule. It usually agrees — you are freed *after* being
captured — but the narrative often shows the dependent claim first, because the
concealment is the interesting part and the possession is assumed.

The commonest error is neither direction: **co-occurrence is not dependency.** Two claims
in one scene, about one town, in one chapter, still need nothing from each other. A judge
hunting for a link will find one, so require the "because" sentence to be true out loud
before writing the edge.

**A claim that reads as a standing rule cannot carry a dependency reliably.** "The Purge
Protocol will erase the library after twelve hours" is either a mechanism the library has
always had — depending on nothing — or this particular running countdown, which depends on
the Scrolls leaving containment. Two competent readers split on it, and no test above
resolves the ambiguity, because the ambiguity is in the CLAIM. That is the same defect
`shapes` exists to catch: fix the sentence rather than argue about the edge.

Two rules the validator enforces: every id must resolve, and the edges must not form a
cycle. While a cycle exists, "what rests on this" has no answer.

# Part 3 — What is checked vs. what you must decide

> **The single most expensive misunderstanding available here** is reading the left
> column as "verified". A generated batch once produced 24 Evidence rows that *all*
> passed every mechanical check — every quote genuinely on the page — while only about
> one in twelve actually **proved** its claim. The winner: *"Jonah saves Margot from
> hypothermia through emergency skin-to-skin warming"*, backed by *"'What,' Jonah Harrow
> said slowly, 'the hell is going on?'"*
>
> A green check means **the quote is real**. It has never meant the claim is right.

| The tool checks mechanically | Only you can decide |
|---|---|
| the quote exists verbatim in the chapter | whether the quote actually *supports* the claim |
| every id resolves to a declared row | whether two ids are the same person |
| load-bearing rows cite a span or say `provisional` | whether the row should exist at all |
| a `knows` doesn't precede its evidence | whether a belief is a genuine reading of the scene |
| canon-status is a legal value | which of two conflicting sources is right |
| an embargo isn't violated | whether an emphasised detail created a promise |

The left column is why the graph is trustworthy. The right column is why it needs you.

---

## Open ontology question

Making "load-bearing" a genuine dependency measure — *contradicting this row would force
another row to change* — needs a **proposition → proposition edge** that ontology v2 does
not have. Without it `blast_radius` stops at one hop and a foundational claim with no
holders is indistinguishable from an inert one.

Adding a `depends-on` column to Propositions would fix it, at the cost of an ontology
version bump and a migration for existing graphs. Not decided; flagged here so the
limitation is visible wherever the weight is used.
