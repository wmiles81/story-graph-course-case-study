# Credits & acknowledgements

This tool did not arrive from nowhere. This page states, plainly, what shaped it and what
it runs on — no flattery, no invented attributions.

## Intellectual sources

**SSTorytime** — Mark Burgess's semantic-spacetime research project. Cited repeatedly in
the source conversation for the idea that a single relational graph is not enough for
human understanding: useful interpretation needs sequence, contextual disambiguation,
sections, and multiple curated views over the same underlying data, plus an "orbit"
concept where a selected item expands into its immediate neighborhood. That argument is
why Story Graph exposes several coordinated windows (Dashboard, Graph, Timeline, Query,
Ask, Reports) over one model instead of a single "the graph" view.

**"Build Your Knowledge Graph with myKG and Connect It to Claude Desktop"** — one of the
reference documents the author uploaded to the source conversation; specific authorship
is not recorded there. Cited for two design patterns actually used in this tool: exposing
safe, read-oriented tools for an AI assistant to query story state (the shape of the
**Ask** tab), and updating a graph incrementally rather than rebuilding it from scratch,
with answers always checked back against the source text — the same principle behind this
tool's provisional/verified row lifecycle.

Other uploaded reference documents (on ontology induction, hybrid retrieval, and
graph/CDM terminology) informed the surrounding research discussion but are not tied to a
specific feature of the shipped tool, so they are not itemized here as design sources.

## Provenance

Story Graph's design — including the five-act program that shaped how Book 3 was
processed — originated in a single long ChatGPT conversation, archived in this repository
under `docs/source-conversation/` (`README.md`, `SOURCE-FILES.md`, `FULL-TRANSCRIPT.md`,
and `transcript-parts/`). There is no named human course creator in that record. Where
this help text says "the design," it means decisions made across that conversation, not
by an individual credited by name.

## Infrastructure

The real stack, nothing more:

- **Python** — the server is stdlib only; no web framework.
- **Kùzu** — the optional embedded graph database that powers the Cypher console and the
  audit reports. The app runs without it, in a reduced mode; see **Start the app**.
- **OpenDyslexic** — the optional dyslexia-friendly font offered in Settings, with a
  fallback stack when it isn't installed.
- **Ollama**, **LM Studio**, **OpenRouter** — the optional providers behind the **Ask**
  tab's plain-English-to-Cypher translation. All three are optional; none is required to
  use the rest of the tool.

There is no cloud backend here — no AWS, no MySQL; everything above runs on your machine.
