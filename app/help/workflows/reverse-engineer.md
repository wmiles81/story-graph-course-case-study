# Reverse-engineer from prose

Reverse-engineer mode runs when there's no worksheet and no existing graph — a
manuscript written outside the worksheet pipeline. It works on a full or partial
manuscript, processing whatever chapters exist. This is the one mode that infers
rather than transcribes: it reads the chapters and derives the tables a worksheet
would otherwise have supplied.

## The governing rule

Every fact derived from prose is provisional. That mark isn't optional bookkeeping —
a provisional load-bearing row warns on validation instead of erroring, which is the
safety net that makes inference-from-prose viable at all. Skipping the mark on an
inferred fact is the one thing this mode exists to prevent.

## How it proceeds

The manuscript itself is registered as a Source first, so every quote pulled from it
becomes an Evidence row the validator can hard-verify against the real chapter files.
Then the skill reads every chapter in order, building entities (characters, objects,
locations, factions), relationships, propositions, epistemic states — including what
the reader is shown and when — and open loops, the same layers a worksheet would have
seeded, but inferred rather than copied.

Before going further, three deterministic checks run against the draft graph: which
named things in the prose have no entity yet, which propositions are state-shaped
rather than event-shaped (and so will contradict themselves later), and which claims
about the same subject might conflict. Fixing what they find now is cheaper than
after fifty rows cite the problem.

## Evidence-span grounding

Nothing is asserted without a receipt. A load-bearing claim — a proposition marked
true or false, an epistemic state, any open loop — must cite a verbatim Evidence
span pulled from the actual chapter text, or be marked provisional. This is what lets
the validator check inferred claims against real prose rather than trusting the
inference.

## How ambiguity is recorded

When a character reference can't be resolved with confidence — the same surname used
by two people, or a nickname that might belong to either of two candidates — the
skill records an ambiguity note naming both candidate ids and the ambiguous line,
rather than guessing. A wrong guess corrupts every downstream row that trusted it; a
recorded ambiguity costs one line and resolves itself once the prose disambiguates.

## What happens after

Once the tables are populated, the skill can optionally hand the remaining rows to a
model via the proposal queue (see that topic) before folding chapters into canon
through the same catch-up loop existing graphs use. The final report states plainly
that the graph was reverse-engineered, lists the ambiguities flagged, and — for a
partial manuscript — that later chapters may revise these facts.
