# Start the app

```
python3 app/story_graph_app.py <path-to-Story-Graph.md>
```

The app opens on `localhost` and prints its address. While it compiles the graph you will
see a "Compiling the story graph…" page that refreshes itself; the real interface appears
when loading finishes.

## Local only, on purpose

The server refuses any request that does not originate from this machine's browser. It
rejects cross-origin and DNS-rebinding requests outright, because its POST endpoints write
your `.env` file and can spend API credits. It is not a server to expose.

## Kùzu is optional

`pip install kuzu` enables the embedded graph database, which powers three things:

| Feature | Without Kùzu |
|---|---|
| **Query** tab (Cypher) | disabled, with a notice |
| **Ask** tab | disabled — it compiles to Cypher |
| `audit` report | unavailable |

Everything else — dashboard, graph, timeline, the other reports — works without it. The
header shows `kuzu:on` or `kuzu:off` so you always know which mode you are in.

Kùzu is a database, not AI. Installing it adds no model and makes no network call.

## When the file changes underneath you

The app polls every five seconds and compares the graph file on disk against the copy it
loaded. If they differ, a bar appears above the main panel offering to reload. Editing the
graph in your editor and clicking reload is the normal working loop.
