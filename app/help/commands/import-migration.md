# Import & migration

## `import-legacy` — convert a v1 / legacy graph to ontology v2

Pure code, no AI: reads a legacy-format graph directory and mechanically
restructures it into the current ontology v2 shape. Reach for this once, when
bringing an older graph into a project that otherwise runs on v2 — not part
of the normal validate/compile/propose loop.

Flags:
- `legacy_dir` (positional) — the legacy graph directory to convert.
- `--out PATH` — required. Where the converted v2 graph is written.
- `--report PATH` — optional coverage/conversion report to write alongside it.
- `--title TEXT` — title for the converted graph (default
  `"Imported Legacy Canon"`).
- `--quotes PATH` — optional quote-verification source for the conversion.
- `--chapters-dir DIR` — chapters directory, passed through where the
  conversion needs manuscript text.

```bash
python3 story-graph/assets/story_graph.py import-legacy data/act-1 \
  --out /tmp/book3-v2.md --title "Snowfall Creek — Book 3 (imported)"
```

`legacy_dir` is a directory holding `*ENTITY-REGISTRY*.csv`,
`*PROPOSITION-REGISTRY*.csv`, `*ASSERTIONS*.csv`, and `*SCENE-LEDGER*.csv` —
the v1 CSV registries, not a v2 markdown graph.

Run `validate` on the output afterward — conversion produces a v2-shaped
graph, it doesn't guarantee the result is clean.
