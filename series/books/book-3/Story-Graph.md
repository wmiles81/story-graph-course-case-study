# Story Graph: Snowfall Creek — Book 3

| field | value |
|---|---|
| ontology-version | 2 |
| modules | none |
| current-canon-chapter | 3 |

## Local Vocabulary
| edge | description |
|---|---|
| protects | one entity moves to physically defend or shield another |

## Sources
| source-id | type | authority | note |
|---|---|---|---|
| ms-book3 | manuscript | 100 | governing manuscript |

## Entities
| id | type | status | voice | note |
|---|---|---|---|---|
| jonah-harrow | Character | active | male | werewolf Sheriff of Snowfall Creek |
| margot-vance | Character | active | female | town librarian; secret Keeper of the Vault |
| founding-scrolls | Object | active | - | pre-Integration documents hidden by the Vance family |
| snowfall-creek-library | Location | active | - | Victorian library built over the warded Vault/Deep Stacks |

## Locations & Distances
| from | to | time | mode |
|---|---|---|---|

## Relationships
| from | edge | to | trend | since-ch | span | note |
|---|---|---|---|---|---|---|
| jonah-harrow | protects | margot-vance | hardening | 1 | | forming bond as they descend into the Deep Stacks together |

## Propositions
| prop-id | statement | canon-status | governing-source | span |
|---|---|---|---|---|
| founding-scrolls-missing | The Founding Scrolls have been stolen from the library's Preservation Section vault | true | ms-book3 | s-scrolls-gone |
| jonah-margot-mate-bond | Jonah's wolf has recognized Margot's scent as its mate | true | ms-book3 | s-mate-scent |

## Epistemic States
| prop-id | holder | mode | since-ch | span |
|---|---|---|---|---|
| jonah-margot-mate-bond | reader | knows | 1 | s-mate-scent |
| jonah-margot-mate-bond | jonah-harrow | believes-false | 1 | s-jonah-denial |

## Open Loops & Setups
| id | planted-ch | expectation | must-fire-by | status | span |
|---|---|---|---|---|---|
| purge-protocol-countdown | 2 | Jonah and Margot must recover the Founding Scrolls (or otherwise stop the Purge Protocol) before the library's chronological-deletion countdown reaches zero, or the building and everyone in it will be erased | 30 | UNFIRED | s-purge-countdown |

## Evidence
| span-id | source-id | locator | quote | note |
|---|---|---|---|---|
| s-scrolls-gone | ms-book3 | ch02 | The gap was where the Founding Scrolls should have been. | Margot discovers the theft while re-shelving books after the storm |
| s-mate-scent | ms-book3 | ch01 | The way the wolf knew the scent of *mate*. | reader-visible confirmation of the mate-bond, before Jonah admits it |
| s-jonah-denial | ms-book3 | ch01 | Not now. Not ever. | Jonah consciously suppresses/denies what his wolf already knows |
| s-purge-countdown | ms-book3 | ch02 | Chronological deletion will commence in eleven hours and fifty-eight minutes. | Meredith hologram announces the ticking-clock threat |

## Timeline
| ch | story-time | elapsed | note |
|---|---|---|---|
| 1 | Friday night | - | Jonah breaks up a bar fight, then follows the wrongness to the library and finds Margot mid-ritual |
| 2 | same night, minutes later | minutes | Founding Scrolls found missing; Purge Protocol triggers, sealing the library |
| 3 | same night, continuing | minutes | Jonah and Margot descend into the Deep Stacks (Level B1 → B2), fleeing a lexivore |

## Logistics
| ch | entity | location | condition | span | note |
|---|---|---|---|---|---|

## Canon Commit Log
- ch 1: Jonah discovers Margot performing forbidden magic in the library basement; his wolf recognizes her scent as its mate, which he denies.
- ch 2: The Founding Scrolls are discovered missing from the Vault, triggering the library's Purge Protocol countdown.
- ch 3: Jonah and Margot descend into the Deep Stacks, evade a lexivore, and press on toward Level B2 to search for the Scrolls before the deadline.
