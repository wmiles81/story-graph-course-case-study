# Source conversation

The complete ChatGPT conversation that produced this repository, archived here so the case study
can be read against its own working record rather than only its finished artifacts.

**Share URL:** https://chatgpt.com/share/6a63afc3-51e8-83e8-bea6-e190a5196eff

| Field | Value |
| --- | --- |
| Title | Knowledge Graphs in Fiction |
| Conversation ID | `6a63afc3-51e8-83e8-bea6-e190a5196eff` |
| Model | `gpt-5-6-thinking` |
| Span | 21–23 July 2026 |
| Author prompts | 174 |
| Model turns | 1,342 |
| Tool turns | 1,065 |
| Total rendered turns | 2,581 |
| Archived | 24 July 2026 |

## What is here

| Path | What it is |
| --- | --- |
| [`FULL-TRANSCRIPT.md`](FULL-TRANSCRIPT.md) | The whole conversation in one file, 3.2 MB. Too large for GitHub's inline renderer — open it locally or use the parts below. |
| [`transcript-parts/`](transcript-parts/) | The same transcript split into six browsable parts of roughly 550 KB, with previous/next navigation. |
| [`TRANSCRIPT-INDEX.md`](TRANSCRIPT-INDEX.md) | Every author prompt in order, each linked to the part and turn that contains it. The fastest way in. |
| [`SOURCE-FILES.md`](SOURCE-FILES.md) | Manifest of the files that went into the conversation and the files it wrote. |
| [`source-files/`](source-files/) | 122 files reconstructed verbatim from the conversation's own file-write calls. |
| `conversation.json.gz` | The raw structured record as served by the share link, gzipped. Everything above derives from this. |

## How to read it

Turns are numbered `[0001]`–`[2581]` and labelled with the role exactly as recorded. Four kinds appear:

- **user** — the author's prompts.
- **assistant** — model replies. Internal reasoning is preserved but collapsed behind a
  `model reasoning` disclosure so it does not crowd the readable thread.
- **tool** — the Python, container, and Notion connector calls the model made. These are kept because
  they are the actual construction record: the CSV ledgers in [`../../data/`](../../data/) and the ZIP
  packages in [`../../packages/`](../../packages/) were produced by the code in these turns.
- **system** — session scaffolding, retained where non-empty.

Early `file_search` turns read `The output of this plugin was redacted` — that redaction is in the
shared conversation itself, not an artifact of this archive.

## Provenance and fidelity

The archive was built from the share page's own embedded conversation payload, not from screen-scraped
HTML, so message text is byte-identical to what the share link serves. Nothing was summarised,
reordered, or omitted except empty system turns.

Two things a share link cannot provide:

- **Uploaded file contents.** The 18 attachments listed in [`SOURCE-FILES.md`](SOURCE-FILES.md) are
  recorded by name, type, size, and first appearance. Their payloads are not exposed to an
  unauthenticated share view and are not recoverable from this URL.
- **Computed artifacts.** Files built by computation rather than written as literal text — chiefly the
  CSV ledgers — are not in [`source-files/`](source-files/). They already exist in
  [`../../data/`](../../data/) and [`../../packages/`](../../packages/); the code that produced them is
  in the transcript.

A third caveat applies inside [`source-files/`](source-files/) itself. Many of those documents were
written from templates whose counts, totals, and timestamps were computed as the code ran. A static
reconstruction cannot resolve a value that was never in the source text, so each unresolved slot reads
`{…}`. 51 of the 122 files are complete; the other 71 are templated in this way, and
[`SOURCE-FILES.md`](SOURCE-FILES.md) flags every one and links to the published artifact that carries
the real figures where one exists.

Of the 122 reconstructed files, 86 are also published elsewhere in this repository and 36 appear here
for the first time — chiefly the Act III and Act IV progress records, the narrative ontology draft,
the analytical-layer proposals, the five-act program, and the prototype dashboard application. 29 of
those 36 are complete reconstructions.

## Relationship to the rest of the repository

This directory is a historical record. It does not supersede anything. Where a file here differs from
its published counterpart in [`../act-1/`](../act-1/), [`../deep-analysis/`](../deep-analysis/), or
[`../../data/`](../../data/), the published artifact governs, consistent with the canon rule in the
repository README.
