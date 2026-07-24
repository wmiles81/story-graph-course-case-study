# BOOK 3 PILOT QUERY TEST REPORT v0.1

**Scope:** Chapters 1–3
**Assertions tested:** 25
**Queries executed:** 8

## Results

### QT-001: When does Jonah learn the Founding Scrolls are missing?

**Answer:** Jonah learns this in Scene B03-C02-S02.

**Status:** `answered`

**Evidence:**
- `A-B03-000009` — scene `B03-C02-S02` — “"I'm not, I'm just—" His hand closed around her elbow, steadying her, and the touch was so unexpected—so *warm* in the cold of the basement—that she forgot to panic about the missing Scrolls and started panicking about something else entirely.”

### QT-002: What does Margot conceal from Jonah?

**Answer:** Margot conceals her grandmother's journal from Jonah in Scene B03-C02-S01.

**Status:** `answered`

**Evidence:**
- `A-B03-000019` — scene `B03-C02-S01` — “Some of the books... remember things they shouldn't." "Books don't remember things." "These ones do." She reached for a leather-bound journal that had fallen open on the floor, its pages covered in handwriting that looked like it had been dipped in rust.”

### QT-003: What does the reader know by the end of Chapter 2?

**Answer:** By the end of Chapter 2, the reader explicitly knows the Founding Scrolls are missing and that the Purge Protocol imposes a twelve-hour deadline.

**Status:** `answered`

**Evidence:**
- `A-B03-000010` — scene `B03-C02-S02` — “"I'm not, I'm just—" His hand closed around her elbow, steadying her, and the touch was so unexpected—so *warm* in the cold of the basement—that she forgot to panic about the missing Scrolls and started panicking about something else entirely.”
- `A-B03-000015` — scene `B03-C02-S03` — “"In twelve hours," she said, "the library will seal itself permanently.”

### QT-004: What important object has unknown custody?

**Answer:** The Founding Scrolls have unknown custody from Scene B03-C02-S02 onward.

**Status:** `answered`

**Evidence:**
- `A-B03-000020` — scene `B03-C02-S02` — “The gap was where the Founding Scrolls should have been.”

### QT-005: Which claim is analytical rather than canonical?

**Answer:** The claim that Margot and Jonah must cooperate to survive the descent is stored as an analytical interpretation, not verified story-world fact.

**Status:** `answered`

**Evidence:**
- `A-B03-000024` — scene `B03-C02-S05` — “They reached the basement—familiar now, almost comforting in its chaos of fallen books and scattered salt—and Margot led them past the mess, past the shelves, past the gap where the Founding Scrolls should have been.”

### QT-006: Is Jonah's mate recognition confirmed as objective canon?

**Answer:** No. It is represented as Jonah's belief because his wolf identifies Margot as mate, while objective confirmation remains unresolved.

**Status:** `answered`

**Evidence:**
- `A-B03-000003` — scene `B03-C01-S03` — “The way the wolf knew the scent of *mate*.”

### QT-007: When does the reader first learn about the twelve-hour deadline?

**Answer:** Scene B03-C02-S03.

**Status:** `answered`

**Evidence:**
- `A-B03-000015` — scene `B03-C02-S03` — “"In twelve hours," she said, "the library will seal itself permanently.”

### QT-008: Does Jonah know the Level B4 solution before Scene B03-C02-S04?

**Answer:** No evidence in the pilot records shows that Jonah knows it before Scene B03-C02-S04.

**Status:** `answered`

**Evidence:**
- `A-B03-000017` — scene `B03-C02-S04` — “The Founding Scrolls are no longer within the containment field." "I *know*." "Protocol requires complete sterilization.”

**Notes:** Negative answer based on valid_from_scene.

## Evaluation

- All eight pilot queries were answerable from the CSV model.
- The system correctly separated canon, character knowledge, reader knowledge, belief, concealment, unknown custody, and analytical interpretation.
- Negative temporal reasoning worked for the Level B4 question by checking the assertion's `valid_from_scene`.
- The CSV representation remains sufficient for this pilot slice.

## Important limitation

Source quotations were selected automatically from the correct scene and should be human spot-checked before being treated as final evidentiary citations. This is still better than inventing a quote, the traditional shortcut favored by unreliable software and certain memoirists.

## Immediate next action

Create character-context snapshots for Jonah and Margot at the end of Chapters 1, 2, and 3, then test knowledge-state progression and dramatic irony queries.