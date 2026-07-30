# What this is

Story Graph turns a manuscript into a **queryable model of its hidden state** — one
human-readable `Story-Graph.md` per book, checked mechanically against the actual prose.

Long-form fiction carries state that no word processor tracks: who knows what, who is
wrong about it, who owns which object, what was promised in chapter 3 and never paid off,
which claim quietly stops being true in chapter 20. That state is what breaks in revision,
and it breaks silently.

## The one idea

A **proposition** ("Jackson is alive") is kept separate from **who knows it**, **who
believes the opposite**, **what the reader knows**, and **the passage that proves it**.

Most continuity tools collapse those into one note. Keeping them apart is what lets the
graph answer questions a note cannot:

- Which characters are confidently wrong about something the reader already knows?
- What else has to change if this claim turns out to be false?
- Which load-bearing claim has no evidence behind it?

## The safety model

**AI proposes → deterministic code verifies → a human accepts.**

The engine makes no network calls and contains no model. Everything it reports is
rule-checking and graph traversal: same input, same output, offline.

An AI can invent a belief. It cannot invent a sentence that is genuinely on the page — so
a proposed row only sheds `provisional` when it cites a quote the validator finds in the
real chapter. Rows that assert a *reading* rather than a transcription are always marked
`NEEDS-HUMAN` and are never applied automatically.

See **How verification works** for the full chain.
