# Plan v2: the decision layer

Supersedes [`ai-plan.md`](ai-plan.md), re-centred on the skill's **inclusion** and
**resolution** decisions rather than on the app. v1's principle and its stage 0–1
infrastructure survive unchanged; what changes is what the infrastructure is *for*, and
which stages matter.

**Stage 0 is complete** — `story_graph_llm.py` extracted, 86 tests green, engine verified
to make no network call.

## Why this revision

The claim in v1 was that the skill is AI-operated and the engine verifies it. True. But an
audit of what the skill actually *decides* found the decision layer is close to absent:

| Decision | Where it's specified today |
|---|---|
| Identity resolution (aliases, merge/split) | ~6 lines, `reference/reverse-engineer.md` only — **catch-up mode has none** |
| What makes a row **load-bearing** | nowhere. The term appears 8 times and gates whether a row needs a receipt |
| Conflict resolution between sources | the authority ranks exist in the ontology; no rule uses them |
| State change vs. contradiction | nowhere |
| Ambiguity as an outcome | mentioned once, in one mode |

The engine can check that a quote exists. It cannot check that the *right* rows were
created, that two names are one person, or that a claim earned its place. Those are the
decisions, they're where the tool's quality actually lives, and they're currently vibes.

## The reframe

> v1: AI proposes rows, code verifies quotes.
> **v2: the skill's decisions are written down, made testable, and narrowed by code before
> AI ever judges.**

Three properties to aim for, in order of how much they're worth:

1. **Explicit** — a rule an agent can follow the same way twice.
2. **Scored** — a corpus of hard cases with known-correct calls, so a change to the rules
   is measurable instead of hopeful.
3. **Narrowed** — deterministic code reduces the candidate set before a model sees it, so
   the model judges dozens of real questions rather than thousands of non-questions.

---

## Stage A — write the decisions down  ·  size: M  ·  no AI required

A new `reference/decisions.md`, loaded by **every** mode (seed, reverse-engineer,
catch-up, import), not one.

### Inclusion — what earns a row

**Define `load-bearing` operationally.** Proposal:

> A row is load-bearing if **contradicting it would force another row to change.**

That is a graph property, not a judgment — which means `story_graph.py` can *compute* it
(it already has the dependency traversal behind `impact`), and the skill's instruction
becomes "add a receipt where the graph says it's load-bearing" rather than "use your
judgment." This single definition is the highest-value item in the plan.

Then the emphasis ladder, from the reader-contract rule: **atmosphere · character
revelation · clue · setup · motif · red herring.** Only the last four create obligations,
so only they earn Open Loop rows — and the rule cuts both ways, flagging high-attention
detail that *didn't* get a row.

And the negative rule, stated as plainly as the positive one: what must **not** become a
row — inferred backstory, unnamed walk-ons, scenery that never returns, anything the
prose doesn't support. Anti-invention is currently a principle; it needs to be a checklist.

### Resolution — reconciling references and conflicts

- **Canonical id + alias table**, with *who uses which alias* (a POV-specific endearment
  is evidence about the speaker, not just a synonym). Promote to a real column; it's
  currently a free-text `note`.
- **The two symmetric failures**, stated together: never merge on a shared surname; never
  split on a differing surface form. Today only the first is written down.
- **Ambiguity is a valid outcome, not a failure.** An `ambiguity` row beats a confident
  guess, and the skill should say so everywhere rather than once.
- **Conflict → source authority.** The ranks already exist (manuscript 100 > bible >
  outline > editorial > draft > ghost-draft). The missing half is the rule that *uses*
  them, plus what to do at equal rank (contest it; don't pick).
- **State change is not contradiction.** "Jackson is alive" (ch03) and "Jackson is dead"
  (ch20) is a state transition; the same pair inside one chapter is a bug. This rule is
  what stands between stage D and a flood of false positives, and it does not exist yet.

## Stage B — make the decisions scorable  ·  size: M  ·  **the part that makes it engineering**

A decision layer you can't score is one you can only argue about. Build a fixture corpus —
`tests/decisions/*.md`, each a short scene plus the correct call and *why*:

```
case: surname-collision
scene: "Hart poured the coffee. Across the room, Ms. Hart pretended not to notice."
correct: two entities; do NOT merge; emit an ambiguity note naming both
trap: shared surname reads as one person
```

Seed it from the traps already known: surname collision, POV nickname, role reference
("the prosecutor"), relationship label ("his ex-wife"), state change vs. contradiction,
atmosphere masquerading as a clue, an inference with no textual basis.

Two harnesses over it:

- **Deterministic** (no model, runs in CI): alias-table consistency — no two entities
  claiming the same alias, no alias equal to another entity's canonical id, every
  ambiguity note naming ids that exist.
- **Scored** (opt-in, needs a provider): run the corpus, compare to expected, print
  correct/total per category. A prompt change becomes a number.

The scored harness is the deliverable that lets every later stage improve rather than
merely change.

## Stage C — narrow the candidates deterministically  ·  size: S each  ·  no AI

Code does the enumeration; the model only judges the residue.

- **`story_graph.py unresolved`** — every proper noun in the chapters that resolves to no
  entity id or alias. Pure text processing. Directly answers "who did I forget to model,"
  and turns identity resolution from an open-ended reading task into a finite list.
- **`story_graph.py conflicts`** — propositions about the same subject with opposing
  polarity, **partitioned by chapter range** so state changes sort separately from real
  contradictions. Deterministic candidate generation for stage D.

Both are useful on their own, ship without a model, and cut the token cost of everything
downstream.

## Stage D — the AI stages, re-pointed  ·  sizes as in v1

Unchanged in mechanism (v1 stage 1's proposal → verify → apply is still the spine),
but each is now an *application of the decision layer* rather than a freestanding prompt,
and each cites the rule it applied so a wrong row is traceable to a wrong rule:

| | Was | Now |
|---|---|---|
| `propose-evidence` | find quotes | find quotes **for rows the graph computes as load-bearing** |
| `propose-epistemic` | who knows what | same, with resolution rules deciding *who* the holder is |
| `audit-semantic` | find contradictions | judge only the pairs `conflicts` surfaces, using the state-change rule |
| `resolve-identity` | *(new)* | judge only the residue from `unresolved` |

## What drops

- **The app's Review tab** — demoted from v1 stage 4 to optional. A CLI review over
  proposal files is enough; the app is a viewer, and you've said that's not where the
  value is.
- **`propose-loops`** — parked until the emphasis ladder in stage A exists, because
  without it the prompt has nothing to reason from.

## Revised order

```
0  extract provider client     DONE  86 tests green, engine offline
A  decisions.md                M     define load-bearing, inclusion, resolution      no AI
B  decision corpus + scoring   M     makes A improvable instead of arguable          AI optional
C  unresolved / conflicts      S+S   deterministic candidate generation              no AI
1  proposal / verify / apply   M     the spine, unchanged from v1
D  propose-evidence            S     first AI stage, fully quote-verifiable
D  propose-epistemic           M     the payoff: holders 18% → 70%, irony > 0
D  audit-semantic              S     gated by C's conflict candidates
D  resolve-identity            S     gated by C's unresolved list
```

**A, B and C need no model at all** — the decision layer, its scoring harness, and the
candidate generators are all deterministic. That's a substantial amount of the value
available before a single token is spent, and it's the sequence that makes the AI stages
worth running when they arrive.
