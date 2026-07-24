import csv
from pathlib import Path
import story_graph as sg
import story_graph_import as imp


def _write(dirp, name, header, rows):
    p = Path(dirp) / name
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=header)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    return p


def legacy_dir(tmp_path, *, entities, props, asserts, scenes):
    _write(tmp_path, "BOOK-9-ENTITY-REGISTRY.csv",
           ["entity_id", "entity_type", "canonical_name", "aliases", "status"], entities)
    _write(tmp_path, "BOOK-9-PROPOSITION-REGISTRY.csv",
           ["proposition_id", "normalized_proposition", "status"], props)
    _write(tmp_path, "BOOK-9-ASSERTIONS.csv",
           ["assertion_id", "proposition_id", "subject_id", "predicate", "object_id_or_value",
            "truth_status", "canonical_status", "story_graph_destination", "valid_from_scene",
            "source_quote"], asserts)
    _write(tmp_path, "BOOK-9-SCENE-LEDGER.csv",
           ["scene_id", "chapter_index", "chapter_heading", "story_time_candidate",
            "major_events_candidate"], scenes)
    return str(tmp_path)


BASE_ENTS = [
    {"entity_id": "ENT-CHAR-1", "entity_type": "Character", "canonical_name": "Jonah Harrow", "aliases": "Jonah;the Sheriff", "status": "active"},
    {"entity_id": "ENT-CHAR-2", "entity_type": "Creature", "canonical_name": "Margot Vance", "aliases": "Margot", "status": "active"},
    {"entity_id": "ENT-GRP-1", "entity_type": "Group", "canonical_name": "Town Council", "aliases": "Council", "status": "active"},
    {"entity_id": "ENT-THR-1", "entity_type": "NarrativeThread", "canonical_name": "Mate-Bond Romance", "aliases": "", "status": "active"},
]
BASE_SCENES = [
    {"scene_id": "B09-C01-S01", "chapter_index": "1", "chapter_heading": "Chapter 1", "story_time_candidate": "night", "major_events_candidate": "opening"},
]


def test_entity_type_mapping_and_drops(tmp_path):
    d = legacy_dir(tmp_path, entities=BASE_ENTS, props=[], asserts=[], scenes=BASE_SCENES)
    md, report, stats = imp.build(d, "T")
    assert "| jonah-harrow | Character |" in md
    assert "| margot-vance | Character |" in md  # Creature -> Character
    assert "| town-council | Faction |" in md    # Group -> Faction
    assert "mate-bond-romance" not in md          # NarrativeThread dropped
    assert any("NarrativeThread" in c for c in [report])


def test_world_fact_captured_as_proposition_not_dropped(tmp_path):
    props = [{"proposition_id": "P-1", "normalized_proposition": "The library has impossible architecture", "status": "active"}]
    asserts = [{"assertion_id": "A-1", "proposition_id": "P-1", "subject_id": "CANON",
                "predicate": "HAS_PROPERTY", "object_id_or_value": "impossible-architecture",
                "truth_status": "true", "canonical_status": "verified",
                "story_graph_destination": "Logistics", "valid_from_scene": "B09-C01-S01", "source_quote": ""}]
    d = legacy_dir(tmp_path, entities=BASE_ENTS, props=props, asserts=asserts, scenes=BASE_SCENES)
    md, report, stats = imp.build(d, "T")
    assert "| p-1 | The library has impossible architecture |" in md   # present as proposition
    assert "captured as proposition" in report                          # reported as covered
    assert "CANON | HAS_PROPERTY" not in report or "dropped" not in report.split("captured as proposition")[0][-200:]


def test_epistemic_alias_and_token_resolution(tmp_path):
    props = [{"proposition_id": "P-1", "normalized_proposition": "Scrolls are missing", "status": "active"}]
    asserts = [{"assertion_id": "A-1", "proposition_id": "P-1", "subject_id": "Jonah",  # alias/token of Jonah Harrow
                "predicate": "KNOWS", "object_id_or_value": "", "truth_status": "true",
                "canonical_status": "verified", "story_graph_destination": "Knowledge States",
                "valid_from_scene": "B09-C02-S01", "source_quote": ""}]
    d = legacy_dir(tmp_path, entities=BASE_ENTS, props=props, asserts=asserts, scenes=BASE_SCENES)
    md, report, stats = imp.build(d, "T")
    assert "| p-1 | jonah-harrow | knows | 2 | provisional |" in md


def test_auto_register_agent_subject_as_provisional(tmp_path):
    props = [{"proposition_id": "P-1", "normalized_proposition": "The town resists", "status": "active"}]
    asserts = [{"assertion_id": "A-1", "proposition_id": "P-1", "subject_id": "Resistance",
                "predicate": "KNOWS", "object_id_or_value": "", "truth_status": "true",
                "canonical_status": "verified", "story_graph_destination": "Knowledge States",
                "valid_from_scene": "B09-C03-S01", "source_quote": ""}]
    d = legacy_dir(tmp_path, entities=BASE_ENTS, props=props, asserts=asserts, scenes=BASE_SCENES)
    md, report, stats = imp.build(d, "T")
    assert "| resistance | Faction |" in md            # auto-registered as provisional Faction
    assert "provisional" in md.split("resistance")[1][:80]
    assert "| p-1 | resistance | knows |" in md
    assert "auto-registered" in report


def test_output_validates_zero_errors(tmp_path):
    props = [{"proposition_id": "P-1", "normalized_proposition": "Scrolls are missing", "status": "active"},
             {"proposition_id": "P-2", "normalized_proposition": "The library has impossible architecture", "status": "active"}]
    asserts = [
        {"assertion_id": "A-1", "proposition_id": "P-1", "subject_id": "Jonah", "predicate": "KNOWS",
         "object_id_or_value": "", "truth_status": "true", "canonical_status": "verified",
         "story_graph_destination": "Knowledge States", "valid_from_scene": "B09-C01-S01", "source_quote": ""},
        {"assertion_id": "A-2", "proposition_id": "P-2", "subject_id": "CANON", "predicate": "HAS_PROPERTY",
         "object_id_or_value": "impossible-architecture", "truth_status": "true", "canonical_status": "verified",
         "story_graph_destination": "Logistics", "valid_from_scene": "B09-C01-S01", "source_quote": ""},
    ]
    d = legacy_dir(tmp_path, entities=BASE_ENTS, props=props, asserts=asserts, scenes=BASE_SCENES)
    md, report, stats = imp.build(d, "T")
    g = tmp_path / "Story-Graph.md"
    g.write_text(md, encoding="utf-8")
    rep = sg.validate(str(g))
    assert rep.errors == [], rep.errors


def test_ids_are_kebab_and_unique(tmp_path):
    ents = BASE_ENTS + [{"entity_id": "ENT-CHAR-9", "entity_type": "Character",
                         "canonical_name": "Jonah Harrow", "aliases": "", "status": "active"}]  # dup name
    d = legacy_dir(tmp_path, entities=ents, props=[], asserts=[], scenes=BASE_SCENES)
    md, report, stats = imp.build(d, "T")
    assert "| jonah-harrow | Character |" in md and "| jonah-harrow-2 | Character |" in md
