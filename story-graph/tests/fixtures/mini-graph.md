# Story Graph: The Eleven Months (synthetic test fixture)

| field | value |
|---|---|
| ontology-version | 2 |
| modules | none |
| current-canon-chapter | 3 |

## Local Vocabulary
| edge | description |
|---|---|
| deceives | knowingly gives the target a false account |
| trusts | relies on the target's word or judgment against risk |
| audits | holds a formal remit to examine the target's records |

## Sources
| source-id | type | authority | note |
|---|---|---|---|
| ms | manuscript | 100 | governing manuscript |

## Entities
| id | type | status | voice | note |
|---|---|---|---|---|
| delia-foss | Character | active | - | Delia; Ms. Foss |
| emmett-rourke | Character | active | - | Emmett |
| priya-raman | Character | active | - | Priya |
| records-room | Location | active | - | the reading room |
| sub-basement | Location | active | - |  |

## Locations & Distances
| from | to | time | mode |
|---|---|---|---|
| records-room | sub-basement | 2m | stairs |

## Relationships
| from | edge | to | trend | since-ch | span | note |
|---|---|---|---|---|---|---|
| emmett-rourke | deceives | delia-foss | hardening | 1 | ev-05 | paid to lie about the night shifts |
| delia-foss | trusts | emmett-rourke | broken | 1 | provisional | holds until ch03 |
| priya-raman | audits | records-room | stable | 2 | ev-04 |  |

## Propositions
| prop-id | statement | canon-status | governing-source | span | depends-on |
|---|---|---|---|---|---|
| p1 | Halloran countersigns the ledger in March and again in April | true | ms | ev-01 |  |
| p2 | Emmett tells Delia the March entries were left incomplete on purpose | true | ms | ev-02 | p1 |
| p3 | Delia states that the vault key never left her | true | ms | ev-03 |  |
| p4 | Priya reports eleven months of countersignatures missing | true | ms | ev-04 | p1 |
| p5 | Emmett lies to Delia about working the night shifts | true | ms | ev-05 |  |
| p6 | Somebody moved the boxes of records into the sub-basement | true | ms | ev-06 | p4 |
| p7 | Delia learns Halloran is a real person after all | true | ms | ev-07 | p1 |

## Epistemic States
| prop-id | holder | mode | since-ch | span |
|---|---|---|---|---|
| p1 | reader | knows | 1 | ev-01 |
| p1 | delia-foss | knows | 1 | ev-01 |
| p2 | reader | knows | 1 | ev-02 |
| p2 | emmett-rourke | knows | 1 | ev-02 |
| p3 | reader | knows | 2 | ev-03 |
| p3 | priya-raman | suspects | 2 | provisional |
| p4 | reader | knows | 2 | ev-04 |
| p4 | delia-foss | knows | 2 | ev-04 |
| p5 | reader | knows | 3 | ev-05 |
| p5 | delia-foss | believes-false | 1 | provisional |
| p6 | reader | knows | 3 | ev-06 |
| p7 | reader | knows | 3 | ev-07 |
| p7 | delia-foss | knows | 3 | ev-07 |

## Open Loops & Setups
| id | planted-ch | expectation | must-fire-by | status | span |
|---|---|---|---|---|---|
| ol-halloran | 1 | the reader learns who Halloran is and why he countersigned | 3 | FIRED ch-3 | ev-07 |
| ol-eleven-months | 2 | the eleven missing months are located | 3 | FIRED ch-3 | ev-06 |

## Evidence
| span-id | source-id | locator | quote | note |
|---|---|---|---|---|
| ev-01 | ms | ch01 | countersigned by Halloran in March | |
| ev-02 | ms | ch01 | The March entries are... incomplete on purpose | ellipsis must not read as a sentence end |
| ev-03 | ms | ch02 | The vault key never left me | short dialogue, under the old length floor |
| ev-04 | ms | ch02 | We're missing eleven months of countersignatures | |
| ev-05 | ms | ch03 | Emmett Rourke had lied about the night shifts | |
| ev-06 | ms | ch03 | Somebody had simply moved the boxes | |
| ev-07 | ms | ch03 | So Halloran was a real person after all | |

## Timeline
| ch | story-time | elapsed | note |
|---|---|---|---|
| 1 | Wednesday, 06:30 | - | rain since Tuesday |
| 2 | Thursday, morning | 1d | Priya arrives |
| 3 | Thursday, later | same day | the sub-basement |

## Logistics
| ch | entity | location | condition | span | note |
|---|---|---|---|---|---|
| 1 | delia-foss | records-room | working | ev-01 | |
| 2 | priya-raman | records-room | auditing | ev-04 | |
| 3 | emmett-rourke | sub-basement | confessing | ev-05 | |

## Canon Commit Log
- ch01 — committed (synthetic fixture)
- ch02 — committed (synthetic fixture)
- ch03 — committed (synthetic fixture)
