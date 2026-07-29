# Story Graph Operating System Prototype

A local, author-first web application built on the frozen Book 3 Story Graph.

## Requirements

- Python 3.10 or newer
- No third-party Python packages

## Run

From this directory:

```bash
python app.py
```

Open:

```text
http://127.0.0.1:8765
```

Set a different port:

```bash
STORY_GRAPH_PORT=9000 python app.py
```

## Included workflows

- Author dashboard
- Global canon search
- Scene briefs
- Character knowledge timeline
- Object custody timeline
- Promise and payoff board
- Continuity dashboard
- Analytical arc view
- Revision proposals with two-level dependency impact analysis

## Governance

- Frozen canon tables are read-only.
- Revision proposals are stored separately.
- The application does not promote or mutate canon.
- A future controlled-write version would require author approval, validation, versioning, and rollback.

## Database

`data/story_graph.db`

The database contains imported frozen canon, derived views, dependency edges, revision proposals, proposal impacts, and proposal events.
