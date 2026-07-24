# Book 3 Act III — Step 03 Operational View Design

## Purpose

Define the working surfaces through which authors and editors use the frozen graph without browsing raw data files.

## Results

- operational views defined: **10**
- role-to-view assignments: **18**
- views with author-controlled mutation: **4**
- fully read-only views: **2**

## Core views

- Author Command Center
- Scene Brief
- Character Knowledge Timeline
- Object Custody Timeline
- Promise and Payoff Board
- Character and Relationship Arc Map
- Continuity Dashboard
- Revision Impact Workbench
- Copyedit and Terminology Review
- Marketing Claim Validator

## Design rule

The views do not own duplicated canon data.

They query the same frozen records and render them differently according to role, task, and authority.

## Outputs

- `BOOK-3-ACT-III-OPERATIONAL-VIEW-INVENTORY-v1.0.csv`
- `BOOK-3-ACT-III-ROLE-VIEW-MATRIX-v1.0.csv`
- `BOOK-3-ACT-III-PROTOTYPE-DASHBOARD-SPEC-v1.0.md`

## Next step

Define the revision-impact contract and dependency traversal rules used before any canon or manuscript change.
