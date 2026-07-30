# Evidence and sources

## Evidence

A span is `span-id | source-id | locator | quote | note`. For a manuscript source the
`locator` is a chapter id (`ch07`) and the `quote` is a **verbatim substring** of that
chapter.

`validate --chapters-dir` hard-verifies every quote against the real chapter file. This is
the hinge of the whole safety model: a model can invent a belief, but it cannot invent a
sentence that is genuinely on the page.

Matching is exact first, then paragraph-bounded with whitespace normalised — so a quote that
survived a re-wrap still verifies, while a quote that was never written does not. A quote
must also be substantial; a three-letter fragment is not a receipt.

The validator additionally warns when a span shares **no content word** with the claim it
supports. It cannot confirm that a quote *proves* a claim — that is a reading — but it can
say the two are not about the same thing, which is mechanical.

## Sources and authority

| Type | Typical rank |
|---|---|
| `manuscript` | highest — the prose itself |
| `bible` | series canon |
| `outline` | plan |
| `editorial` | notes |
| `draft` | superseded prose |
| `ghost-draft` | discarded |

When sources disagree, the higher authority governs. At **equal** authority the claim
becomes `contested` — the tool does not pick. A silent pick is how the wrong version of a
fact ends up canon.

## Open Loops & Setups

Planted-but-unresolved elements — Chekhov's guns. Each has its own id (not the id of the
proposition that planted it), where it was planted, what is expected, a **`must-fire-by`**
chapter, and a status.

Always set `must-fire-by`, even as a guess. A promise with no due date can never be reported
broken, which makes the whole layer decorative.
