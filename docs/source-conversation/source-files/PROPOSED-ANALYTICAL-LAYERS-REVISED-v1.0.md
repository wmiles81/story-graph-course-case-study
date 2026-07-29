# Revised Analytical-Layer Plan v1.0

**Program:** Story Graph Deep Analysis & Series Continuity  
**Date:** 2026-07-23  
**Basis:** Verified Act I–III schema audit  
**Status:** Proposed execution design for Gate 0 approval

## Governing distinction

The analytical work is divided into four modes:

1. **Reuse** — the capability already exists with a dedicated populated artifact and sufficient schema.
2. **Extension** — usable data and structure already exist, but the capability needs additional semantics, normalization, coverage, or evaluation.
3. **New construction** — no dedicated artifact exists; a bounded analytical layer must be designed before extraction.
4. **Series-pending validation** — Book 3 provides a foundation, but implementation status cannot be tested until at least one additional book is loaded.

This distinction prevents a particularly human form of progress: rebuilding working things because a new document used different nouns.

---

# Mode 1 — Reuse

## Rule

Do not replace or duplicate these structures. Preserve their stable IDs, authority rules, evidence fields, version history, and author-ratified status. Add regression tests or new views only when required by later layers.

## Reused foundations

### Authority, evidence, and canon governance

Reuse:

- `BOOK-3-ASSERTIONS-CANON-FROZEN-v2.0.csv`
- `BOOK-3-CANON-FREEZE-MANIFEST-v2.0.csv`
- `BOOK-3-ACT-II-CANON-PROMOTION-LEDGER-v1.0.csv`
- author decision ledgers
- artifact manifests and chronological progress records

Capabilities:

- assertion-specific authority;
- exact evidence spans and source quotations;
- immutable accepted versions;
- explicit author decision gates;
- chronological artifact governance.

### Narrative identity and source structure

Reuse:

- `BOOK-3-SCENE-LEDGER-CANON-FROZEN-v2.0.csv`
- `BOOK-3-ENTITY-REGISTRY-CANON-FROZEN-v2.0.csv`
- `BOOK-3-ACT-III-ENTITY-ALIAS-RESOLUTION-v1.0.csv`
- `BOOK-3-PROPOSITION-REGISTRY-CANON-FROZEN-v2.0.csv`
- `BOOK-3-ASSERTIONS-CANON-FROZEN-v2.0.csv`

Capabilities:

- verified scene segmentation;
- stable entity identity within Book 3;
- proposition/assertion separation;
- character knowledge timeline.

### Chronology, custody, promises, and continuity

Reuse:

- Book 3 scene chronology and timeline audit;
- custody canon and custody timeline view;
- promise-lifecycle canon and promise board;
- continuity audit;
- dependency index, including lexical dependencies.

Capabilities:

- book chronology;
- object custody;
- setup, promise, partial payoff, final closure, reopening, and deferral;
- setup-without-payoff detection;
- contradiction detection;
- dependency and impact traversal.

### Operational evaluation and presentation

Reuse:

- materialized author views;
- safe-failure tests;
- operational evaluation;
- negative and adversarial tests.

## Reuse acceptance test

A reused capability is accepted when:

- its current schema answers the requirement;
- its records remain linked to stable source evidence;
- its regression questions still pass after new layers are added;
- no new table duplicates its semantic responsibility.

---

# Mode 2 — Extension

## Rule

Extend from existing stable IDs and evidence-bearing records. New fields or ledgers must reference existing scene, entity, proposition, assertion, custody, promise, continuity, or dependency IDs wherever possible.

## Extension Package A — Event normalization

### Existing basis

- scene ledger;
- assertions;
- propositions;
- dependency index.

### Extend to add

- stable `event_id`;
- event boundaries within or across scenes;
- event type;
- participants;
- changed state;
- event evidence span;
- event-to-assertion links.

### Do not rebuild

- scenes;
- propositions;
- assertions.

## Extension Package B — Epistemic and reader-state expansion

### Existing basis

- assertion epistemic fields;
- character knowledge timeline;
- early reader-context and suspense-asymmetry artifacts.

### Extend to add

- normalized mental-state vocabulary for belief, suspicion, inference, lie, uncertainty, ignorance, and knowledge;
- reader knowledge by narrative position;
- dramatic-irony windows;
- premature disclosure and delayed-revelation findings.

### Do not infer

- knowledge from scene presence;
- reader knowledge from author notes not present in the manuscript.

## Extension Package C — Causality

### Existing basis

- assertions;
- dependency index;
- revision-impact edges.

### Extend to add

- causal prerequisite;
- direct cause;
- enabling condition where newly constructed below applies;
- consequence;
- causal confidence;
- perceived-causality holder;
- evidence and counterevidence.

The existing dependency index remains a revision and reference graph. It must not be relabeled wholesale as a causal graph.

## Extension Package D — World rules

### Existing basis

- propositions;
- assertions;
- confidence, authority, and epistemic fields;
- continuity findings.

### Extend to add

- rule identity;
- rule domain;
- explicit versus inferred status;
- character belief about rule;
- exception;
- violation;
- clarification;
- confidence and evidence.

The world-rule registry becomes a typed projection over existing claims where possible, not an independent competing canon.

## Extension Package E — Spatial foundations

### Existing basis

- scene locations;
- custody records;
- scene evidence.

### Extend to add

- location hierarchy and adjacency;
- object placement;
- access constraints;
- source-supported movement anchors.

Detailed blocking is new construction and remains separate below.

## Extension Package F — Character, relationship, capability, and vulnerability states

### Existing basis

- analytical-state canon;
- assertions;
- custody;
- continuity records.

### Extend to add

- typed before/after state;
- transition trigger;
- duration or persistence;
- capability availability;
- injury and recovery;
- resource gain/loss;
- vulnerability introduced or resolved.

Analytical states remain analytical canon unless separately supported as story-world facts.

## Extension Package G — Structural, ambiguity, repair, and evaluation coverage

Extend:

- payoff-without-setup checks from promise lifecycle;
- unresolved ambiguity from assertions and continuity;
- repair ranking from revision-impact classifications;
- gold questions for every new or extended layer.

---

# Mode 3 — New Construction

## Rule

These capabilities have no dedicated Act I–III artifact. Each requires a schema proposal, evidence contract, sample rows, gold questions, and author-decision policy before full extraction.

## New Layer 1 — Plot-thread model

Create:

- `PLOT-THREAD-REGISTRY`
- `EVENT-THREAD-MEMBERSHIP`
- `THREAD-CONTRIBUTION-LEDGER`

Required semantics:

- main plot, subplot, relationship arc, mystery, antagonist plan, internal arc, and series thread where relevant;
- many-to-many membership;
- contribution type;
- contribution strength;
- source evidence;
- disputed membership.

Depends on:

- event normalization.

## New Layer 2 — Plot intersections

Create:

- `PLOT-INTERSECTION-LEDGER`

Required semantics:

- participating threads;
- intersection event or scene;
- transferred information, resource, pressure, relationship, capability, obligation, or consequence;
- later effect;
- evidence;
- whether the intersection is material or merely co-located.

Depends on:

- plot-thread model;
- causal extension.

## New Layer 3 — Enabling conditions and perceived causality

Create or add as bounded causal records:

- enabling conditions;
- false causal assumptions;
- character-perceived causality;
- corrected causal understanding.

This may be implemented as additional typed rows in the causal ledger rather than separate tables, provided the distinctions remain queryable.

## New Layer 4 — Narrative irreversibility

Create:

- `NARRATIVE-IRREVERSIBILITY-LEDGER`

Required semantics:

- prior equilibrium;
- triggering action;
- new state;
- options closed;
- obligations created;
- vulnerabilities created;
- reversal path;
- reversal cost;
- persistence;
- evidence;
- author-intent gate.

Depends on:

- event normalization;
- causal extension;
- state-transition extension.

## New Layer 5 — Spatial blocking

Create:

- `SCENE-BLOCKING-LEDGER`
- `SPATIAL-CONTINUITY-AUDIT`

Required semantics:

- entrance and exit;
- movement;
- posture;
- orientation;
- reachability;
- visibility;
- object placement;
- impossible or duplicated action;
- evidence and confidence.

Depends on:

- spatial foundation extension;
- custody reuse.

## New Layer 6 — Structural sufficiency

Create:

- `SCENE-STATE-CHANGE-AUDIT`
- `MISSING-BRIDGE-AUDIT`
- `REDUNDANT-BEAT-AUDIT`
- `SUBPLOT-CONTRIBUTION-AUDIT`

Required distinction:

- causal function;
- emotional function;
- thematic function;
- character function;
- atmospheric or experiential function.

A scene is not inert merely because it does not move the external plot. Literature has survived several centuries despite not being a project-management board.

Depends on:

- state extensions;
- plot-thread model;
- causal model;
- promise lifecycle.

## New Layer 7 — Discovery-only network analysis

Create derived reports, not canon tables:

- centrality report;
- bridge-node report;
- community or clustering candidates;
- orphan and weakly connected structures.

Rules:

- centrality does not equal narrative importance;
- clustering proposes review targets;
- no network measure creates canon or continuity findings by itself.

---

# Mode 4 — Series-Pending Validation

## Rule

Design the validation protocol now, but do not claim implementation, absence, or success until another book is loaded.

## Series validation package

Prepare specifications for:

- `SERIES-ENTITY-REGISTRY`
- `BOOK-SERIES-IDENTITY-MAP`
- `SERIES-CHRONOLOGY`
- `CROSS-BOOK-KNOWLEDGE-CARRYOVER`
- `SERIES-OBJECT-HISTORY`
- `SERIES-PROMISE-LIFECYCLE`
- `CROSS-BOOK-CONTINUITY-AUDIT`
- `RETCON-CLARIFICATION-LEDGER`
- `SPOILER-SCOPE-MATRIX`
- `CROSS-BOOK-REVISION-IMPACT`
- `SERIES-CHARACTER-ARC`
- `SERIES-RELATIONSHIP-ARC`
- `SERIES-PLOT-THREAD-REGISTRY`

## Validation sequence when the next book arrives

1. Register the new manuscript and authority.
2. Extract book-local scenes, entities, propositions, assertions, chronology, custody, promises, and states.
3. Propose cross-book identity mappings.
4. Author-ratify ambiguous identity mappings.
5. Build chronology constraints and state carryover.
6. Test inherited knowledge, possession, injuries, capabilities, obligations, and relationships.
7. Compare world rules and continuity claims.
8. Classify differences as contradiction, clarification, reinterpretation, correction, intentional retcon, or unresolved ambiguity.
9. Establish spoiler boundaries.
10. Run cross-book revision-impact scenarios.
11. Reclassify each `SERIES_PENDING` requirement as full, partial, or absent.

## Series gate

No series requirement exits pending status merely because a schema exists. It must be populated and tested against at least two books.

---

# Revised dependency order

1. Preserve and regression-test reused foundations.
2. Extend event identity and state semantics.
3. Construct plot-thread membership.
4. Extend causality and construct intersections.
5. Extend world rules and reader knowledge.
6. Extend spatial foundations and construct blocking analysis.
7. Construct irreversibility.
8. Construct structural sufficiency.
9. Run discovery-only network analysis.
10. Add gold questions and cross-layer integrity tests.
11. Load another book and execute series-pending validation.

---

# Gate 0 approval criteria

The plan is ready to proceed when the author approves:

- the four work modes;
- the prohibition against rebuilding full capabilities;
- the extension packages;
- the seven new-construction layers;
- the rule that series capabilities remain pending until tested with another book;
- the revised dependency order.

No new manuscript extraction begins before Gate 0 approval.
