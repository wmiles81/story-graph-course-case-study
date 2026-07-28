# Plan: adding AI to Story Graph

**Status:** proposed, not started. Stages 1–4 are specified to build from; stages 5–7 are preliminary and firm up once the harness in stages 1–3 has proven itself.

## The principle this whole plan defends

> AI proposes. Deterministic code verifies against the manuscript. A human accepts.

The engine's value is that it answers the same question the same way twice. So AI is confined to two edges — **ingest** (prose → candidate rows) and **interface** (English → Cypher, already shipped in the app's Ask tab) — and never sits between a question and its answer. `validate`, `compile`, `query`, `report`, `audit`, `impact`, `coverage`, `deviations` stay offline, stdlib, no model, no network. The README's claim survives, restated precisely: **the verification core uses no AI.**

Everything below is opt-in. Nothing changes for someone who never runs an AI subcommand.

## Where the code goes

<table class="editor-table" style="min-width: 75px;"><colgroup><col style="min-width: 25px;"><col style="min-width: 25px;"><col style="min-width: 25px;"></colgroup><tbody><tr><th colspan="1" rowspan="1"><p>Module</p></th><th colspan="1" rowspan="1"><p>Role</p></th><th colspan="1" rowspan="1"><p>AI?</p></th></tr><tr><td colspan="1" rowspan="1"><p><code>story-graph/assets/story_graph.py</code></p></td><td colspan="1" rowspan="1"><p>validator/compiler/CLI — untouched core</p></td><td colspan="1" rowspan="1"><p>never</p></td></tr><tr><td colspan="1" rowspan="1"><p><code>story-graph/assets/story_graph_llm.py</code></p></td><td colspan="1" rowspan="1"><p><strong>new</strong> — provider-neutral chat client, extracted from the app</p></td><td colspan="1" rowspan="1"><p>yes</p></td></tr><tr><td colspan="1" rowspan="1"><p><code>story-graph/assets/story_graph_propose.py</code></p></td><td colspan="1" rowspan="1"><p><strong>new</strong> — prompt templates + proposal generation</p></td><td colspan="1" rowspan="1"><p>yes</p></td></tr><tr><td colspan="1" rowspan="1"><p><code>story-graph/assets/story_graph_verify.py</code></p></td><td colspan="1" rowspan="1"><p><strong>new</strong> — deterministic gate over proposals</p></td><td colspan="1" rowspan="1"><p>never</p></td></tr><tr><td colspan="1" rowspan="1"><p><code>app/story_graph_app.py</code></p></td><td colspan="1" rowspan="1"><p>imports the extracted client instead of owning one</p></td><td colspan="1" rowspan="1"><p>yes (Ask, Review)</p></td></tr></tbody></table>

Same pattern already used for `kuzu`: lazy import, optional, absent means the core still runs. A missing provider key disables the AI subcommands and nothing else.

---

## Stage 0 — extract the provider client · size: S

`app/story_graph_app.py`  already has a working provider-neutral client that the user specified: OpenRouter + local Ollama (`:11434`) + LM Studio (`:1234`), OpenAI-compatible chat over stdlib  `urllib`, certifi SSL context,  `.env`  persistence.  **No SDK, no Anthropic-only path.**  Move it out so the CLI and the app share one implementation.

Move to `story_graph_llm.py`: `PROVIDERS`, `_env_path/_env_read/_env_write/_load_env`, `_provider_key`, `_ssl_ctx`, `_oai`, `_chat`, `_reachable`.

-   The app imports them; its public behaviour must not change.
    
-   **Done when:** the existing 78 tests still pass with zero edits to their assertions, and `test_app_settings_providers_roundtrip` still exercises the same round-trip.
    

## Stage 1 — the spine: proposal → verify → apply · size: M

This is the part that makes every later stage safe, and it must land before any prompt is written. **AI output is an artifact on disk, never an edit to the graph.**

### The artifact

`proposals/<kind>-<scope>.json`:

```json
{
  "kind": "epistemic",
  "graph": "series/books/book-3/imported/Story-Graph-from-act1.md",
  "generated": {
    "provider": "ollama", "model": "…", "prompt_version": "epistemic/1",
    "scope": "ch14", "chapter_sha256": "…", "temperature": 0
  },
  "rows": [{
    "section": "Epistemic States",
    "values": {"prop-id": "p-b03-000042", "holder": "margot-vance",
               "mode": "believes-false", "since-ch": "14", "span": "provisional"},
    "basis": {"locator": "ch14", "quote": "She would have known. She would have felt it."},
    "reasoning": "Margot asserts the negation of p-…042 as settled fact",
    "confidence": "high"
  }]
}
```

### `story_graph.py verify-proposal <file>` — deterministic, no model

Per row, emits `PASS` / `FAIL <reason>` / `NEEDS-HUMAN`:

<table class="editor-table" style="min-width: 50px;"><colgroup><col style="min-width: 25px;"><col style="min-width: 25px;"></colgroup><tbody><tr><th colspan="1" rowspan="1"><p>Check</p></th><th colspan="1" rowspan="1"><p>Rule</p></th></tr><tr><td colspan="1" rowspan="1"><p>schema</p></td><td colspan="1" rowspan="1"><p>required columns for that section are present and well-typed</p></td></tr><tr><td colspan="1" rowspan="1"><p>id resolution</p></td><td colspan="1" rowspan="1"><p><code>prop-id</code> exists; <code>holder</code> is a known entity or <code>reader</code></p></td></tr><tr><td colspan="1" rowspan="1"><p>range</p></td><td colspan="1" rowspan="1"><p><code>since-ch</code> is an integer ≤ <code>current-canon-chapter</code></p></td></tr><tr><td colspan="1" rowspan="1"><p><strong>quote gate</strong></p></td><td colspan="1" rowspan="1"><p><code>basis.quote</code> appears <strong>verbatim</strong> in <code>chapters/&lt;locator&gt;</code> — reuses the existing <code>validate --chapters-dir</code> grep</p></td></tr><tr><td colspan="1" rowspan="1"><p>duplicate</p></td><td colspan="1" rowspan="1"><p>the row isn't already in the graph</p></td></tr><tr><td colspan="1" rowspan="1"><p>consequence</p></td><td colspan="1" rowspan="1"><p>re-runs existing detectors (<code>knows-before-evidence</code>, orphan props) against graph <strong>+</strong> proposed rows</p></td></tr></tbody></table>

The quote gate is the anti-hallucination mechanism, and it is not negotiable: a model can invent a belief, but it cannot invent a sentence that is genuinely on the page.

### `story_graph.py apply-proposal <file> --accept <row-ids>`

Writes only accepted rows, every one marked `provisional`, and appends one Canon Commit Log line naming the model and the artifact:

```
- ch14: +6 epistemic states (proposed by <model>, 8 rows, 7 verified, 6 accepted)
  [proposals/epistemic-ch14.json]
```

That line is the audit trail — you can always ask what the model said, what the checker allowed, and what you actually took.

**Done when:** a hand-written proposal file with one good row and four deliberately broken ones (bad prop-id, future chapter, fabricated quote, duplicate) yields exactly one `PASS`, and `apply` writes exactly that row plus one commit-log entry.

## Stage 2 — `propose-evidence` (ratification) · size: S · **the shakedown**

Target: **source-verified propositions 13/122 (10%) → 60%+**

For each provisional proposition, find the sentence in the chapters that proves it.

I still consider the epistemic gap the highest-value one — this goes first only because it's the cheapest way to prove the harness. Its verification is *completely* mechanical: the quote either grep-matches the chapter or it doesn't. If the pipeline is going to fail, it fails here, visibly and harmlessly, before it's pointed at anything unverifiable.

-   Input per call: one chapter + the propositions whose `span` is `provisional`.
    
-   Output: `Evidence` rows + the `span` back-reference on the proposition.
    
-   **Done when:** `coverage` reports source-verified ≥ 60%, with zero rows accepted whose quote isn't findable.
    

## Stage 3 — `propose-epistemic` · size: M · **the payoff**

Targets, straight off today's `coverage`:

<table class="editor-table" style="min-width: 75px;"><colgroup><col style="min-width: 25px;"><col style="min-width: 25px;"><col style="min-width: 25px;"></colgroup><tbody><tr><th colspan="1" rowspan="1"><p>Metric</p></th><th colspan="1" rowspan="1"><p>Now</p></th><th colspan="1" rowspan="1"><p>Target</p></th></tr><tr><td colspan="1" rowspan="1"><p>propositions with a holder</p></td><td colspan="1" rowspan="1"><p>22/122 (18%)</p></td><td colspan="1" rowspan="1"><p>70%+</p></td></tr><tr><td colspan="1" rowspan="1"><p><code>believes-false</code> states</p></td><td colspan="1" rowspan="1"><p><strong>0</strong></p></td><td colspan="1" rowspan="1"><p>non-zero</p></td></tr><tr><td colspan="1" rowspan="1"><p>dramatic irony pairs</p></td><td colspan="1" rowspan="1"><p><strong>0</strong></p></td><td colspan="1" rowspan="1"><p>non-zero</p></td></tr><tr><td colspan="1" rowspan="1"><p>distinct holders</p></td><td colspan="1" rowspan="1"><p>7</p></td><td colspan="1" rowspan="1"><p>15+</p></td></tr></tbody></table>

Per chapter, given the entity roster and existing propositions, ask for who **knows / believes / believes-false / suspects** what, since which chapter — including `reader`. The prompt asks explicitly for the negative case, because that's the missing layer: *who here believes the opposite of what's true, and what line shows it?*

### The unsolved problem, and the mitigation

A proposition is verifiable — its quote is on the page. **A belief is an inference**, and no grep confirms it. This is the one place the existing safety model doesn't transfer, and pretending otherwise would put unverifiable rows into a graph whose whole value is that its rows are checkable.

Mitigation, in order:

1.  Every epistemic row must cite the passage the inference **rests on**, and that passage is quote-gated like any other. The model can't invent the evidence even where it can err on the reading.
    
2.  Epistemic rows verify to `NEEDS-HUMAN`**, never** `PASS`**.** They cannot auto-ratify. A new ratification tier — `inferred` — sits below `provisional`.
    
3.  The consequence check runs `knows-before-evidence` over graph + proposal, so a belief dated before the scene that could have caused it is rejected mechanically.
    

**Done when:** the targets above are met *and* the `contested` sizing mode in the app stops rendering 189/189 nodes at the floor.

## Stage 4 — Review tab in the app · size: M

Where the human-in-the-loop actually lives. Loads a proposal file and renders one row per line: the proposed row, its verdict, its cited quote **with surrounding chapter context**, and the model's reasoning — accept / reject / edit per row, then write the accepted subset via `apply-proposal`.

Reviewing 100 candidate rows in a terminal is how you end up accepting all of them unread. This stage is what keeps stage 3 honest.

---

## Preliminary — the three read-only advisors

These never write to the graph; they emit questions and findings for a human. That makes them low-risk and cheap to add once the harness exists, and it's why they're specified loosely here: their shape should follow what stages 1–3 teach us.

### Stage 5 — `audit-semantic` (contradiction detection) · size: S

The class of error no validator will ever catch: *"Margot has never been to the basement"* and *"Margot remembered the basement's smell"* are contradictory in meaning and identical in structure. Batch the propositions (122 fits one prompt; larger graphs block by entity or chapter) and ask which pairs can't both be true. Output is a **question list**, never a row. Open design point: how to suppress the pairs a human has already dismissed.

### Stage 6 — `triage-deviations` · size: S

`deviations` already reports where a stored quote no longer matches the prose, and stops there. Feed each mismatch plus the current chapter text to the model and have it classify — *intentional revision* / *accidental drift* / *transcription error* — and propose the replacement span. Fully verifiable: the proposed new quote goes through the same quote gate. Probably the highest ratio of usefulness to effort in the whole plan.

### Stage 7 — `propose-loops` (promise & payoff) · size: S

Currently 10 open loops, all recorded by hand. Split the work by what each side is good at: the **model judges emphasis** ("this got unusual narrative attention"), and **code confirms the fact** ("and it never recurs after ch07" is a search). Neither half is trusted with the other's job. Open design point: what "unusual attention" means in a prompt without it degrading to "mentioned more than twice."

---

## Cross-cutting requirements

**Provider neutrality is a hard requirement.** Every stage runs against local Ollama or LM Studio with no key and no network egress, or OpenRouter if the user chooses it. No stage may depend on a single vendor's SDK or a cloud-only feature.

**Cost control.** Chapter-at-a-time, and cache by `(chapter_sha256, prompt_version, model)` — re-running after an unrelated edit costs nothing. A 30-chapter book is 30 calls per stage, not 30 × rows.

**Reproducibility.** Temperature 0 where the provider supports it. The proposal file records provider, model, prompt version, and input hash, so any accepted row can be traced back to exactly what produced it.

**Tests never hit the network.** Substitute a fake `_chat` — the pattern already proven in `test_ask_repairs_invalid_cypher_once`. Every stage needs at least: a happy path, a fabricated-quote rejection, and a malformed-JSON-from-the-model recovery.

**One measurement of success, not a vibe.** `coverage` already prints every number this plan moves. Capture it before stage 2 and after each stage; the flags it raises are the acceptance criteria.

## Suggested order

```
0  extract provider client      S   no behaviour change, 78 tests still green
1  proposal / verify / apply    M   the spine — nothing lands before this
2  propose-evidence             S   shakedown on the fully-verifiable task    10% → 60%
3  propose-epistemic            M   the payoff                                18% → 70%, irony > 0
4  Review tab                   M   makes stage 3 reviewable in practice
5  audit-semantic               S   read-only
6  triage-deviations            S   read-only
7  propose-loops                S   read-only
```

Stop after any stage and the tool is still coherent — that's the point of the ordering. Stages 0–1 are pure infrastructure and can be built and tested with no model at all.