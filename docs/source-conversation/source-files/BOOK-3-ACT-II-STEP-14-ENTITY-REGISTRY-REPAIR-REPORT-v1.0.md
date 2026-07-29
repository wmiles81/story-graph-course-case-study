# Book 3 Act II — Step 14 Entity Registry Repair

## Purpose

Test whether the structurally consistent Act I entity registry actually represents the governing manuscript, then add missing manuscript entities and reject entities produced solely by contaminated scene summaries.

## Trigger

The epistemic rebuild could not assign valid entity IDs to Henderson, Iron-Jaw, or Inquisitor Valerius because those recurring characters were absent from the reconciled registry.

At the same time, the registry contained objects created by unsupported late-batch summaries.

## Result

- Missing manuscript entities added: **{…}**
- Unsupported Act I entities rejected: **{…}**

## Additions

### Characters

- Henderson
- Iron-Jaw
- Inquisitor Valerius
- Mrs. Gable
- Sarah
- Silas Blackwood

### Group

- Federal Magisterium

### Locations

- Aspen Ridge Resort
- Civic Center
- Town Hall
- Snowfall Creek High School
- Snowfall Creek Ice Rink
- High-School Football Field

### Objects

- Magisterium Emitter Tower
- Margot's Zippo Lighter
- Chemical Sabotage Duffel
- Jonah's Service Pistol
- Magisterium Gunship

## Rejected entities

- `ENT-OBJ-0014` Treaty Evidence Copies
- `ENT-OBJ-0015` Compromised Tracking Source
- `ENT-OBJ-0016` Detainee Files and Transfer Records
- `ENT-OBJ-0017` Rescued Witness Testimony
- `ENT-OBJ-0018` Sterling's Master Archive Records

Each rejected entity traces to a scene record replaced during Act II and lacks support in the governing manuscript.

## Correction to Step 2 interpretation

The Step 2 result remains mechanically true: all 67 ratification rows matched the 67-row registry.

It is no longer sufficient as evidence that the registry itself was complete or source-valid.

The proper interpretation is now:

> The Act I ratification table was internally consistent with the Act I registry, but the registry required manuscript-level repair.

## Authority status

Additions are labeled `act-ii-direct-manuscript-addition`.

Rejections are labeled `REJECT_UNSUPPORTED_SOURCE`.

No author interpretation was required because the decisions concern presence or absence of named manuscript entities and source-bound objects.

## Outputs

- `BOOK-3-ENTITY-REGISTRY-ACT-II-ADDITIONS-v1.0.csv`
- `BOOK-3-ENTITY-REGISTRY-ACT-II-REJECTIONS-v1.0.csv`

## Next step

Construct the Act II entity-registry candidate, rerun dangling-reference checks, and resume knowledge and belief normalization using the repaired identifiers.
