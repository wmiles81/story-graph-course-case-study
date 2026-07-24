# BOOK 3 ENTITY AND PREDICATE NORMALIZATION REPORT v1.1

## Result

The entity-reference and predicate-normalization pass is complete.

### Entity registry

- Base and delta registry rows merged: **46**
- New late-book entities added: **21**
- Reconciled entity-registry rows: **67**
- Custody references rewritten: **23**
- Unresolved registry-like references after normalization: **0**

### Predicate routing

- Distinct analytical predicates: **73**
- Assertions routed to Story Graph sections: **131**
- Original predicates preserved: **yes**

## Important design decision

The analytical predicates were not flattened into the Story Graph `Relationships`
table.

Instead, they were routed by function:

- epistemic predicates to **Knowledge States**;
- custody and state predicates to **Logistics**;
- obligation predicates to **Open Loops & Guns**;
- durable interpersonal predicates to **Relationships**;
- event predicates to the **Canon Commit Log**;
- anything still ambiguous to the evidence sidecar.

This preserves the richer analytical model while keeping the compact Story Graph
ontology intelligible.

## Entity decisions

### Existing entity recovered

`ENT-OBJ-0010`, the Original Integration Treaty, already existed in the validated
Chapters 7–9 registry delta. The earlier audit called it unresolved only because it
checked the base registry instead of the merged registry.

### Newly registered entities

Late-book objects and creatures now have canonical IDs, including:

- Margot's glasses;
- the revolver and Mossberg shotgun;
- evidence copies and detainee records;
- the Dragon-Killer Ballista;
- the Fire Elemental and Siege Golem;
- the AM transmitter;
- the dragon's-blood cure;
- the Iron Horse schematic and Emitter;
- the Valerius containment book;
- Jackson Harrow and his old sheriff badge.

### Provisional entity retained

The compromised tracking source remains provisional because the current graph does
not identify the precise physical object or mechanism with enough confidence.

## Files produced

- `BOOK-3-ENTITY-REGISTRY-MASTER-RECONCILED-v1.1.csv`
- `BOOK-3-CUSTODY-STATE-MASTER-RECONCILED-v1.1.csv`
- `BOOK-3-ENTITY-ID-NORMALIZATION-MAP-v1.1.csv`
- `BOOK-3-PREDICATE-NORMALIZATION-RULES-v1.1.csv`
- `BOOK-3-ASSERTIONS-MASTER-ROUTED-v1.1.csv`

## Gate status

**Entity references and predicate routing are cleared for draft Story Graph generation.**

The next step is to regenerate the integrity report against:

- 153 reconciled scenes;
- 153 reconciled scene contexts;
- the reconciled entity registry;
- the reconciled custody ledger;
- the routed assertion table.

If that pass is clean enough, the first provisional `BOOK-3-Story-Graph.md` can be
generated and validated.
