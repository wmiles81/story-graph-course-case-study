# Book 3 Act III — Step 16 Implementation Decisions

## Approved product direction

- Product surface: **Local web app**
- Primary role: **Author**
- Mutation scope: **Read only plus proposals**
- Storage: **SQLite**
- Depth: **Working prototype**

## Architecture consequence

The prototype will use:

- Python;
- Flask;
- SQLite;
- server-rendered HTML;
- local-only deployment;
- immutable frozen CSV inputs;
- revision proposals stored separately from canon.

## Non-goals for version one

- direct canon mutation;
- multi-user authentication;
- cloud deployment;
- native graph database;
- automatic author approval.

## Outputs

- `BOOK-3-ACT-III-AUTHOR-DECISION-LEDGER-v1.0.csv`
- `BOOK-3-ACT-III-PROTOTYPE-ARCHITECTURE-v1.0.json`

## Next step

Build the SQLite schema and import pipeline from the frozen canon and Act III operational views.
