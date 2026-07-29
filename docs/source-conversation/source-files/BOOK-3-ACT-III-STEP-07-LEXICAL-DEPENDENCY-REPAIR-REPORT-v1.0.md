# Book 3 Act III — Step 07 Lexical Dependency Repair

## Failure detected

The first Valerius rename scenario returned no dependencies because many operational records mention canonical names in text fields rather than storing the entity ID.

## Repair

The dependency index now adds lexical entity-reference edges across:

- scenes;
- custody;
- promises;
- analytical states;
- continuity;
- evaluation questions and answers.

Generic role terms were excluded where they would create excessive false matches.

## Results

- lexical entity edges added: **{…}**
- total dependency edges after repair: **{…}**
- Valerius direct dependents: **{…}**
- Valerius impacts within two steps: **{…}**
- directly affected evaluation questions: **{…}**
- scenario result: **{…}**

## Limitation

Lexical edges are marked `lexical-confirmed`.

They prove a text reference exists. They do not by themselves prove that every wording change alters narrative meaning.

## Outputs

- `BOOK-3-ACT-III-OPERATIONAL-DEPENDENCY-INDEX-v1.2.csv`
- `BOOK-3-ACT-III-DEPENDENCY-SUMMARY-v1.2.csv`
- `BOOK-3-ACT-III-REVISION-SCENARIO-003-RERUN-v1.1.csv`

## Next step

Materialize the operational scene, knowledge, custody, promise, continuity, and analytical-state views from the repaired dependency index.
