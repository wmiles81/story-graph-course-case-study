# ASSERTION-CONTEXT-MODEL v0.1

**Project:** Story Graph System  
**Pilot:** Series Book 3  
**Status:** Draft for review  
**Date:** July 21, 2026

## 1. Purpose

This model defines how the Story Graph System stores claims without confusing canonical fact, character knowledge, belief, false belief, lie, suspicion, reader knowledge, analytical interpretation, and revision-specific truth.

A proposition is a normalized claim. An assertion connects that proposition to a subject, context, source, authority, and review state.

## 2. Assertion record

```yaml
assertion_id:
proposition_id:
subject_id:
predicate:
object_id_or_value:
assertion_type:
canonical_status:
truth_status:
epistemic_status:
story_time:
valid_from_scene:
valid_to_scene:
narrative_reveal_scene:
viewpoint_context:
reader_context:
revision_context:
source_document:
source_span:
source_quote:
source_class:
authority_level:
confidence:
review_status:
supersedes:
contradicts:
derived_from:
notes:
```

## 3. Context objects

### Scene context

```yaml
scene_context_id:
scene_id:
pov_character:
location:
present_characters:
active_goals:
active_threats:
known_propositions:
believed_propositions:
false_beliefs:
concealed_propositions:
objects_present:
relationship_states:
open_promises:
reader_advantage:
reader_disadvantage:
revision_context:
source_document:
review_status:
```

### Character context

```yaml
character_context_id:
character_id:
as_of_scene:
known_propositions:
believed_propositions:
suspicions:
false_beliefs:
goals:
fears:
secrets:
obligations:
physical_state:
relationship_states:
salient_recent_events:
```

### Reader context

```yaml
reader_context_id:
as_of_scene:
explicit_propositions:
implied_propositions:
visible_clues:
likely_suspicions:
red_herrings:
open_questions:
dramatic_irony:
withheld_information:
```

### Revision context

```yaml
revision_context_id:
source_document:
content_hash:
version_label:
status:
supersedes_revision:
superseded_by_revision:
active_for_pilot:
```

## 4. Rules

- A character cannot know a proposition before a qualifying acquisition event.
- Reader knowledge does not imply character knowledge.
- Character belief does not equal canon.
- A lie requires evidence that the speaker believed the claim false.
- Every verified assertion requires source provenance.
- Facts from different revisions remain revision-scoped.
- Analytical interpretations remain analytical unless author-approved.
- Unknown custody remains unknown. The graph is not permitted to improvise evidence.

## 5. Pilot storage

The pilot will use:

- `BOOK-3-PROPOSITIONS-CH01-03-v0.1.csv`
- `BOOK-3-ASSERTIONS-CH01-03-v0.1.csv`
- `BOOK-3-SCENE-CONTEXTS-CH01-03-v0.1.csv`

Database selection remains deferred until these records prove adequate for the approved queries.
