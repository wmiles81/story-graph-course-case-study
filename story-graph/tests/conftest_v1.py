import sys
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets"
sys.path.insert(0, str(ASSETS))

MINIMAL_V2 = """# Story Graph: Test

| field | value |
|---|---|
| ontology-version | 2 |
| modules | none |
| current-canon-chapter | 0 |

## Local Vocabulary
| edge | description |
|---|---|

## Sources
| source-id | type | authority | note |
|---|---|---|---|
| ms | manuscript | 100 | governing manuscript |

## Entities
| id | type | status | voice | note |
|---|---|---|---|---|
| jonah | Character | active | male | |
| library | Location | active | - | |

## Locations & Distances
| from | to | time | mode |
|---|---|---|---|

## Relationships
| from | edge | to | trend | since-ch | span | note |
|---|---|---|---|---|---|---|

## Propositions
| prop-id | statement | canon-status | governing-source | span |
|---|---|---|---|---|

## Epistemic States
| prop-id | holder | mode | since-ch | span |
|---|---|---|---|---|

## Open Loops & Setups
| id | planted-ch | expectation | must-fire-by | status | span |
|---|---|---|---|---|---|

## Evidence
| span-id | source-id | locator | quote | note |
|---|---|---|---|---|

## Timeline
| ch | story-time | elapsed | note |
|---|---|---|---|

## Logistics
| ch | entity | location | condition | span | note |
|---|---|---|---|---|---|

## Canon Commit Log
"""


def make_graph(**replacements):
    """Return MINIMAL_V2 with whole-section bodies replaced.
    replacements: section_name -> the full markdown for that section (incl. header)."""
    text = MINIMAL_V2
    for name, body in replacements.items():
        import re
        pattern = re.compile(r"(## " + re.escape(name) + r"\n).*?(?=\n## |\Z)", re.S)
        text = pattern.sub(body.rstrip() + "\n", text)
    return text
