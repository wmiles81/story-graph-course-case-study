# Seed from a worksheet

Seed mode runs when an NPE worksheet — a file matching `*YFD-RAW*.md` or named
`master_story_document.md` — exists in the target folder and no `Story-Graph.md`
does yet. The worksheet already states the story's facts, so this mode is
transcription, not invention: it copies what the worksheet says into graph form
rather than inferring anything from prose.

## What gets extracted, and where

The skill copies the bundled blank template into the target folder as
`Story-Graph.md`, sets the header (title, `ontology-version | 2`, the `modules`
list the worksheet's RDL declares, `current-canon-chapter | 0`), then populates the
current-state tables from the worksheet:

- **Sources** — the worksheet itself (and any bible or editorial notes) registered
  with a type and an authority rank.
- **Entities** — every character, object, faction, and setting location, each typed
  and given a kebab-case id. Quantitative facts are first-class: every stated age,
  tenure, founding date, duration, distance, and amount is transcribed onto the
  owning row, and a quantity the story will predictably need but the worksheet
  doesn't state is recorded as `NOT ESTABLISHED — do not assert` — an explicit
  negative fact that blocks downstream invention instead of inviting it.
- **Locations & Distances** — travel edges between settings the story moves between.
- **Relationships** — the initial relationship edges, using core edge vocabulary or
  a story-specific edge declared in Local Vocabulary first.
- **Propositions** — premise-level claims the worksheet asserts, each pointing at a
  governing Source.
- **Epistemic States** — who knows, believes, believes-false, or suspects each
  proposition, including the reader.
- **Evidence** — the spans those claims cite, with a verbatim quote from the source
  document.
- **Open Loops & Setups** — obligatory scenes and planted setups the worksheet
  names, each with a `must-fire-by` chapter.

Timeline, Logistics, Physics State, and the Canon Commit Log are left empty — those
only fill in once chapters get committed, in catch-up mode.

## What stays provisional

The skill uses only what the worksheet actually establishes. If the schema wants
something the worksheet is silent on, the row is left blank rather than filled with
a guess. If a fact has to be added to keep the graph coherent, it's marked
provisional instead of backed by an invented quote — a provisional load-bearing row
warns on validation rather than erroring.

## After seeding

If finalized chapters already exist past chapter 0, seeding continues straight into
catch-up mode to fold them in, then the graph is validated against the manuscript's
chapter files so quotes get hard-verified rather than degrading to a warning.
