# Propositions — the claims

A proposition is a claim about the story world, with a `canon-status`:

| Status | Means |
|---|---|
| `true` | established |
| `false` | established as untrue |
| `undetermined` | not yet settled |
| `contested` | sources disagree at equal authority |

A proposition carries **no holder**. "Jackson is alive" is separate from anyone's belief
about it — that is the point of the layering, and it is what makes dramatic irony
expressible at all.

## Write events, not states

This is the rule that does the most work.

> **"Jackson dies in the ch20 ambush"** — good.
> **"Jackson is dead"** — trouble.

A proposition has **no time bounds**. A state-shaped claim is true in one half of the book
and false in the other, with nothing in the row to say so. Every epistemic row that cites it
then inherits the ambiguity, and the graph starts reporting contradictions that are nobody's
mistake.

An event-shaped claim cannot contradict itself this way. "Jackson dies in ch20" is true
before ch20 too — it is a fact *about* ch20, not a description of the present.

The `shapes` command lists propositions that can become false later in the same book, ranked
by how many holders already believe them. Run it before a catch-up pass: rewriting one claim
now beats rewriting fifty rows that cite it later.

## depends-on — what rests on what

An optional column records that one claim needs another: read `X depends-on Y` as **if Y
were false, X would stop making sense.**

This is a one-hop declaration; the tool computes the transitive closure. Two traps:

- **Co-occurring in a scene is not dependency.** Two things happening together is not one
  resting on the other.
- **Same character is not dependency.** "Jonah defeats Kael" does not depend on "Kael works
  for the Council" — Jonah defeats him regardless of who employs him.

Direction is the part no checker can verify. Say "A, because B" aloud.

The payoff is ranking. `queue` orders by structural importance rather than popularity: a
claim underpinning a chain outranks one that merely has believers, because a believer can be
revised in place while a dependent claim has to be revisited or it quietly becomes false.
