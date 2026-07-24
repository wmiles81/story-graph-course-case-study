# Book 3 Act III — Step 10 Natural-Language Query Router

## Purpose

Define how free-form author and editor questions are converted into safe, typed Story Operating System queries.

## Results

- intent routes: **9**
- entity, alias, and synonym rows: **202**
- normalized story topics: **6**
- parse schema: **1**

## Resolution order

1. stable IDs;
2. exact canonical names;
3. exact aliases;
4. operational synonyms;
5. normalized topics;
6. fuzzy candidates;
7. safe clarification.

## Safety behavior

The router does not guess silently when:

- multiple entities share a surface form;
- a required scene scope is missing;
- a query depends on a rejected historical premise;
- a marketing claim exceeds the evidence;
- a revision target cannot be identified.

## Outputs

- `BOOK-3-ACT-III-NL-INTENT-ROUTING-RULES-v1.0.csv`
- `BOOK-3-ACT-III-ENTITY-ALIAS-RESOLUTION-v1.0.csv`
- `BOOK-3-ACT-III-TOPIC-NORMALIZATION-v1.0.csv`
- `BOOK-3-ACT-III-NL-QUERY-PARSE-SCHEMA-v1.0.json`

## Next step

Prototype query parsing and evidence assembly against representative author, editor, continuity, and marketing questions.
