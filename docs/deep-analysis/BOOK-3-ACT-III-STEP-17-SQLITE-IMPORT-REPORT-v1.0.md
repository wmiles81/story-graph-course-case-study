# Book 3 Act III — Step 17 SQLite Operational Database

## Database

`story_graph_os/data/story_graph.db`

## Imported tables

- canon and operational source tables: **18**
- proposal and audit tables: **3**
- indexes created: **13**

## Validation

- source-count checks: **18**
- passing count checks: **18**
- failing count checks: **0**
- SQLite integrity check: **ok**

## Governance

Frozen CSV artifacts remain the authoritative versioned source package.

SQLite is an operational projection.

Revision proposals, impacts, and events are stored separately from canon tables.

## Outputs

- `story_graph_os/data/story_graph.db`
- `BOOK-3-ACT-III-SQLITE-IMPORT-MANIFEST-v1.0.csv`
- `BOOK-3-ACT-III-SQLITE-IMPORT-VALIDATION-v1.0.csv`

## Next step

Build the Flask application, author dashboard, search, operational views, and revision-proposal workflow.
