# Book 3 Act III — Prototype Dashboard Specification

## Global shell

### Header

- Book and canon version
- governing manuscript
- current role
- current chapter or scene scope
- unresolved warning count
- pending proposal count
- last freeze manifest

### Global search

Search accepts:

- natural-language question;
- stable entity ID;
- stable scene ID;
- promise ID;
- continuity issue ID;
- object name;
- character name or alias.

### Global answer pattern

1. direct answer;
2. authority badge;
3. scene or interval scope;
4. limitations;
5. expandable evidence;
6. related views;
7. controlled actions, when permitted.

---

## Author Command Center

### Top row

- Current canon version
- Active promises
- Open proposals
- Timing annotations
- Latest affected-test result

### Main panels

#### Current chapter

Shows scenes, viewpoint, goals, turns, outcomes, active objects, knowledge changes, and promises.

#### Active promises

Shows every introduced but unfulfilled promise, ordered by age and narrative importance.

#### Character state

Shows latest approved relationship, identity, leadership, allegiance, and emotional states.

#### Continuity watch

Shows only unresolved annotations or newly introduced risks.

#### Revision queue

Shows proposed changes and downstream impact summaries.

---

## Scene Brief

The scene brief is the basic operational unit.

### Required blocks

- Scene identity
- Source boundaries
- Viewpoint and present characters
- Goal
- Opposition
- Turn
- Outcome
- Major events
- Knowledge gained
- Belief or interpretation changes
- Object transfers
- Promises introduced, advanced, or paid
- Analytical state changes
- Linked continuity annotations
- Evidence

---

## Character Knowledge Timeline

### Timeline row

- Scene
- Proposition
- Epistemic state
- Acquisition method
- Confidence
- Valid-to scene
- Reader knowledge difference
- Evidence

### Critical behavior

The view must support:

> What does Margot know about Valerius as of B03-C17-S02?

It must not answer using later scenes.

---

## Object Custody Timeline

### Timeline row

- Object
- Holder or location
- Custody type
- Start scene
- End scene
- Transfer event
- Terminal state
- Risk flag

The interface must display shared and uncertain custody without coercing them into false certainty.

---

## Promise Board

Columns:

- Introduced
- Active
- Escalated
- Partially paid
- Fulfilled
- Closed unused contingency
- Deferred to series

A promise card includes:

- promise ID;
- description;
- introduction scene;
- latest lifecycle scene;
- current status;
- age in scenes;
- affected characters;
- evidence;
- controlled actions.

---

## Revision Impact Workbench

### Input

- target scene or entity;
- proposed change;
- intended reason;
- requested authority level.

### Output

- direct records changed;
- dependent records possibly changed;
- invalidated tests;
- continuity risks;
- unresolved author choices;
- proposed new versions;
- approval action.

No change is applied from this screen until the impact report exists.
