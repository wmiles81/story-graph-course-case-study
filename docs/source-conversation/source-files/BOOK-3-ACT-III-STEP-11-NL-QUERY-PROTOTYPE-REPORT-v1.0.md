# Book 3 Act III — Step 11 Natural-Language Query Prototype

## Purpose

Exercise intent routing, alias resolution, topic normalization, evidence assembly, and safe failure behavior against representative user questions.

## Prototype coverage

- sample questions: **{…}**
- intent families exercised: **{…}**
- unsupported-premise corrections: **{…}**
- ambiguity cases: **{…}**

## Behaviors demonstrated

- direct scene brief;
- holder-specific knowledge with an as-of scene;
- custody tracking;
- promise lifecycle;
- continuity disposition;
- analytical arc response;
- revision-impact routing;
- marketing routing;
- unsupported-premise correction;
- alias resolution.

## Limitation

This is a deterministic prototype, not a full semantic parser.

Its purpose is to validate contracts, failure behavior, evidence assembly, and normalization requirements before implementation in a conversational runtime.

## Outputs

- `BOOK-3-ACT-III-NL-QUERY-PROTOTYPE-PARSES-v1.0.csv`
- `BOOK-3-ACT-III-NL-QUERY-PROTOTYPE-RESPONSES-v1.0.csv`
- `BOOK-3-ACT-III-NL-QUERY-PROTOTYPE-PACKET-v1.0.md`

## Next step

Test ambiguity, not-found, unsupported-premise, spoiler-sensitive, and insufficient-scope cases as explicit safe-failure scenarios.
