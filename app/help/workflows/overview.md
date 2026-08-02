# How the skill operates

The graphs this app reads are produced by a Claude Code skill called `story-graph`,
not by this app. The app is a viewer and query surface; the skill is the thing that
reads a manuscript (or a worksheet) and writes the `Story-Graph.md` file.

## Where it lives

The skill is self-contained and portable: everything it needs — template, ontology,
validator — lives in its own folder. Drop that folder into any project's
`.claude/skills/` directory and any workflow in that project can invoke it. It does
not depend on this repo's paths, so the same skill can build a graph for a book that
has nothing to do with this codebase.

## The graph as canon ABox, the ontology as TBox

`Story-Graph.md` is the **ABox** — the assertions: which entities exist, what each one
is claimed to be true, who knows or believes what. The bundled `Story-Graph-Ontology-v2.md`
is the **TBox** — the schema those assertions must conform to: section order, entity
types, controlled edge vocabularies, per-table columns. The skill and its validator both
read the ontology before writing or checking a graph; a graph that doesn't match its
shape is invalid, not just untidy.

## Modules

The ontology splits into a genre-neutral core (present in every graph, any genre) and
optional modules declared in the graph's header `modules` field. Today there is one:
`spe`, which adds a required Physics State section for romance/NPE projects tracking
character-vector and scene-axis movement. A thriller or mystery graph declares
`modules | none` and never sees that section. The skill only loads a module a project
has actually declared — it never adds one uninvited.

## The file-safety rule

Never overwrite or delete an existing graph. If `Story-Graph.md` already exists and a
run is about to replace rather than update it, the skill stops and versions the old
file first (`Story-Graph_v1.md`, and so on). All edits to the current graph are
in-place table updates and append-only log entries — never a destroy-and-rewrite. The
skill uses native file tools to write or edit the graph file; the only shell commands
it uses for that are the validator and compiler invocations. Proposals, queries, and
reports (see The Proposal Queue) are separate, read-only or queue-mediated commands —
this rule is scoped to editing the graph file itself, not to everything the skill runs.

## The five workflows

Everything else in this section documents one thing the skill does: seed a graph from
a worksheet, reverse-engineer one from prose, catch up an existing graph from newly
finalized chapters, and run generated rows through the proposal queue before they
become canon.
