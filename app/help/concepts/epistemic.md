# Epistemic states — who knows what

The layer that makes hidden state visible. Each row is one holder's stance on one
proposition, from a chapter, optionally until a chapter.

| Mode | Means |
|---|---|
| `knows` | holds it as true, correctly |
| `believes` | holds it as true |
| `believes-false` | holds the opposite — confidently wrong |
| `suspects` | partial, unconfirmed |
| `embargoed-until` | deliberately withheld until a chapter (a constraint, not an on-page fact) |

## The reader is a holder

`reader` is a reserved holder, valid even though it is not an entity. Recording what the
**audience** knows is what makes dramatic irony computable rather than remembered.

## Stances have an end

`since-ch` opens a stance; the optional `until-ch` closes it.

Without an end, a stance runs to the end of the book — and "Jonah believed it false, then
learned better in ch20" becomes inexpressible. You can only write both rows, and the graph
then reads them as a contradiction.

That is not a contradiction. It is a **character arc**, and it is the ordinary shape of
dramatic irony. Flagging it as an error is why the informative mode goes unused: a manuscript
can accumulate 173 `knows` rows against 6 `believes-false` purely because the useful one
produced warnings.

So the contradiction check compares **windows**, not modes. Two stances whose chapter ranges
are disjoint are a correction and pass silently; only a real overlap is flagged.

## Dramatic irony

Once stances carry windows, irony is pure traversal: **the reader knows a claim while a
holder believes it false, over an overlapping window.** The `irony` command lists them.

`believes-false` is the mode most often missed and the most valuable. A character
confidently wrong about something the reader knows is invisible to a linear read — that is
precisely why it needs recording.

## A caution about `knows`

`knows` is the cheap mode. "Jonah knows the Grey Guard arrived" mostly restates the plot,
and a graph made almost entirely of `knows` rows tells you little you could not get by
reading. The value concentrates in where someone is **wrong**.
