# The provisional lifecycle

Every inferred fact enters the graph marked `provisional`, and that mark is the graph's
honesty about its own confidence.

```
proposed  →  verified against the prose  →  accepted by a human  →  ratified  →  frozen
```

## Shedding provisional

A row loses `provisional` when it cites an evidence span the validator can find in the real
chapter. Not when someone is confident; when the quote checks out.

## NEEDS-HUMAN

Some rows can never be auto-ratified no matter how good the quote, because they assert a
**reading** rather than a transcription:

- Epistemic States — what someone believes
- Relationships — what an edge between two people means
- Open Loops — that something is a promise
- Entities — that a name is a Character rather than a Location
- Evidence — that *this* quote supports *that* claim

The quote is real; what it *means* is a judgement. Those rows are flagged `NEEDS-HUMAN` and
wait for you.

## The review ledger

Every accept and reject is appended to `<graph>-review.jsonl` with your reason. On the next
run:

- an **identical row** you already decided is skipped outright
- a **claim you rejected before**, re-proposed with different support, is *hinted* rather
  than blocked — because the new support may be sound

That distinction is deliberate and it earns its keep. A rejection of "X depends on Y" should
not silently block "X depends on Z", which may be a completely different and correct claim.

## Freezing

`freeze` stamps a versioned canon baseline. Rows still provisional at that point are
recorded as such, so a frozen baseline never pretends to more certainty than it has.
