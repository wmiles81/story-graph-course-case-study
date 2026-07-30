# Ask — plain English

Type a question; the model set in **⚙️ Settings → AI Model** turns it into Cypher, runs it,
and shows you **both** the answer and the query.

Showing the query is not decoration. It is the only way to know whether the answer means
what you think it means — a query that returns 12 rows because it silently dropped a join
looks exactly like one that returns 12 rows because there are 12.

## Self-repair

If the generated Cypher is invalid, the app feeds the engine's error back to the model once
and retries. A repaired result is marked as such. This exists because the common failure is
not a wrong idea but a scope slip — an identifier used after `DISTINCT`, say — and the
engine's own error message is enough to fix it.

## Providers

Set in **Settings**: OpenRouter, or a local **Ollama** / **LM Studio** server. Local
providers keep the manuscript on your machine.

## The schema is disclosed

The **Cypher rules** disclosure at the bottom shows the exact schema text the model is
given. If Ask keeps misunderstanding your data, read it — the fix is usually that the model
was never told about a section you assumed it knew.

## Results persist

Your result stays until the next question, and flipping to the **Graph** tab shows the same
result as a node-link diagram.
