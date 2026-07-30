# Query — Cypher console

Ad-hoc Cypher over the compiled graph. Requires Kùzu.

## Schema

**Node tables** — `Entity`, `Proposition`, `Source`, `Evidence`, `OpenLoop`, `Holder`

**Relationship tables** — `RELATES`, `EPISTEMIC`, `GOVERNED_BY`, `EVIDENCED_BY`, `SUPPORTS`

`Holder` is separate from `Entity` on purpose: the reserved holder `reader` is not an
entity in the story, but it holds stances exactly like one. That separation is what lets
you ask "what does the reader know that Jonah does not?" in a single query.

## Starting query

The console opens pre-filled with a query worth reading before you change it:

```cypher
MATCH (h:Holder)-[e:EPISTEMIC]->(p:Proposition)
RETURN h.id, e.mode, e.since_ch, p.id
ORDER BY e.since_ch
LIMIT 25
```

That is the epistemic layer in one statement — every stance anyone holds, in the order they
formed.

## Notes

Results render as a table with a row count. Errors come back as text from the engine rather
than being swallowed, so a binder error tells you which identifier is out of scope.

The **Ask** tab prefills this console with whatever Cypher the model produced, so a natural
language question that *nearly* worked can be repaired by hand rather than re-asked.
