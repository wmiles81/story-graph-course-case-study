# Entities, names and descriptions

An entity is a `Character`, `Object`, `Location`, or `Faction`, with a kebab-case id that is
its canonical name: `margot-vance`, `founding-scrolls`, `level-b4`.

## Aliases are owned surface forms

A character is referred to many ways — first name, surname, full name, nickname, title,
role. "Evelyn Hart", "Evie", "Hart", "Ms. Hart" can all be one person.

Aliases are declared on the entity, `;`-separated, and they are **owned**: a surface form
belongs to exactly one entity, and two entities claiming the same one is a collision the
validator reports.

Resolution works in two ways, and the difference matters:

- **exact** — a whole surface form (the id read as words, or any declared alias)
- **component** — a single token of the **canonical id only**, never from an alias

An id is a name, so its parts are names for the thing: `margot-vance` legitimately yields
"Margot". An alias is a *phrase*, and a phrase's parts are not names for it. Without that
rule an object noted as "Valerius book" contributes the token `valerius`, and a character
named Valerius becomes unfindable — which is exactly what happened on a real manuscript
before the rule existed.

Possessive ids are excluded too: `keeper-s-label-gun` is the gun belonging to the Keeper,
not a surface form of "Keeper".

## Descriptions are not aliases

"the Vampire", "the Librarian", "the Alpha", "three Trolls" are **descriptions**, and they
must not go in the alias table.

An alias is a **rigid designator** — "Sheriff Harrow" is Jonah in every scene, forever. A
description is not: "the Vampire" reaches Aleksei only because he happens to be the one
vampire present, and in a room with two it names neither. Recording a description as an
alias asserts a permanent identity the prose never gave it.

The tool tells them apart mechanically. A common noun accepts a determiner and a proper name
rejects one — "the Vampire", "three Trolls", never "the Margot". On a real manuscript that
one test separates the two populations cleanly, with nothing in between.

## Traits — where a description resolves

A description resolves through an **attribute**, so entities carry an optional `traits`
cell: `vampire`, `alpha`, `librarian`, `troll`.

Traits are plain tokens, so one serves every descriptor built on it, and plurals reach the
singular — "Trolls" finds `troll`. Resolution is strict: exactly one bearer resolves, two is
reported **ambiguous** and left alone, because which one a scene means is a reading and a
wrong resolution is invisible once written.

**Traits are not surface forms.** A trait must never make a descriptor resolve as a name, or
the whole distinction collapses.

## The known limit

Multi-word candidates are deliberately left unclassified. English lets a proper name of an
institution or a place take a determiner exactly as a common noun does — "the Grey Guard",
"the Deep Stacks" — so no mechanical test separates them from "the Gunship". That one needs
a reader.
