# Book 3 Act III — Steps 18–19 Working Prototype

## Application

A runnable local Story Graph Operating System prototype has been created.

## Technology

- Python standard library
- WSGI local server
- SQLite
- server-rendered HTML
- embedded CSS
- no third-party packages

Flask was removed from the architecture because it was unavailable in the runtime and unnecessary for the prototype.

## Included workflows

- author dashboard;
- global canon search;
- scene browser and scene briefs;
- character knowledge timeline;
- object custody timeline;
- promise and payoff board;
- continuity dashboard;
- analytical arc view;
- revision proposal form;
- two-level dependency impact generation;
- isolated proposal and audit storage.

## Governance

- frozen canon tables remain unchanged;
- revision proposals are stored separately;
- proposal creation produces impact records;
- no direct canon mutation exists;
- the proposal test verifies canon row counts remain unchanged.

## Application tests

- tests: **9**
- PASS: **9**
- FAIL: **0**

## Run

```bash
cd story_graph_os
python app.py
```

Open:

```text
http://127.0.0.1:8765
```

## Package

`story-graph-os-prototype-v0.1.0.zip`

## Outputs

- `story_graph_os/app.py`
- `story_graph_os/test_app.py`
- `story_graph_os/static/style.css`
- `story_graph_os/data/story_graph.db`
- `story_graph_os/README.md`
- `BOOK-3-ACT-III-WEB-APP-TEST-RESULTS-v1.0.csv`
- `BOOK-3-ACT-III-WEB-APP-MANIFEST-v1.0.csv`
- `story-graph-os-prototype-v0.1.0.zip`

## Next step

Run the application-level operational evaluation and prepare the author demonstration workflow.
