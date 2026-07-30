# Resolving references

## The two symmetric failures

- **Never merge on a shared surname.** "Hart poured the coffee. Across the room, Ms. Hart
  pretended not to notice." — two people.
- **Never split on a differing surface form.** "Evie", "Ms. Hart" and "the prosecutor" can
  be one person.

Only the first is usually remembered. Both are errors, and the second is harder to see
because nothing looks wrong.

## Ambiguity is a valid outcome

An ambiguity note beats a confident guess. Everywhere the tool must choose between two
readings without evidence, it reports instead of picking:

- a name two entities both claim → **ambiguous**
- a trait two entities both carry → **ambiguous**
- sources disagreeing at equal authority → **contested**

A wrong resolution is invisible once written. That asymmetry justifies the caution.

## Conflict resolution

Higher source authority governs. At equal authority, contest it — do not choose.

## State change is not contradiction

"Jackson is alive" (ch03) and "Jackson is dead" (ch20) is a **state transition**. The same
pair *inside one chapter* is a bug.

This is why `conflicts` partitions candidate pairs by chapter: a state change and a
contradiction look identical in structure, and only the chapter tells them apart.
