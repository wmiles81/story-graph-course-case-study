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


def _quotes_file(tmp_path, rows):
    import csv
    qp = tmp_path / "QUOTED.csv"
    with open(qp, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["assertion_id", "proposition_id", "source_quote", "valid_from_scene"])
        w.writeheader()
        for r in rows:
            w.writerow(r)
    return str(qp)


def _chapters(tmp_path, ch1_body):
    d = tmp_path / "chapters"
    d.mkdir()
    (d / "ch01.md").write_text("## Chapter 1\n\n" + ch1_body + "\n", encoding="utf-8")
    return str(d)


KNOWS = [{"assertion_id": "A-1", "proposition_id": "P-1", "subject_id": "Jonah", "predicate": "KNOWS",
          "object_id_or_value": "", "truth_status": "true", "canonical_status": "verified",
          "story_graph_destination": "Knowledge States", "valid_from_scene": "B09-C01-S01", "source_quote": ""}]
PROP1 = [{"proposition_id": "P-1", "normalized_proposition": "Scrolls missing", "status": "active"}]


def test_verified_quote_becomes_evidence_and_validates(tmp_path):
    d = legacy_dir(tmp_path, entities=BASE_ENTS, props=PROP1, asserts=KNOWS, scenes=BASE_SCENES)
    quote = "The gap was where the Scrolls should have been."
    chdir = _chapters(tmp_path, quote)
    qp = _quotes_file(tmp_path, [{"assertion_id": "A-1", "proposition_id": "P-1",
                                  "source_quote": quote, "valid_from_scene": "B09-C01-S01"}])
    md, report, stats = imp.build(d, "T", qp, chdir)
    assert stats["evidence_spans"] == 1
    assert f"| ev-p-1 | ms-book3 | ch01 | {quote} |" in md
    assert "| p-1 | Scrolls missing | true | ms-book3 | ev-p-1 |" in md
    g = tmp_path / "g.md"
    g.write_text(md, encoding="utf-8")
    rep = sg.validate(str(g), chapters_dir=chdir)
    assert rep.errors == [], rep.errors  # the verbatim quote hard-verifies against ch01


def test_unverifiable_quote_leaves_proposition_provisional(tmp_path):
    d = legacy_dir(tmp_path, entities=BASE_ENTS, props=PROP1, asserts=KNOWS, scenes=BASE_SCENES)
    chdir = _chapters(tmp_path, "Nothing relevant on this page.")
    qp = _quotes_file(tmp_path, [{"assertion_id": "A-1", "proposition_id": "P-1",
                                  "source_quote": "A paraphrase that is not in the prose.",
                                  "valid_from_scene": "B09-C01-S01"}])
    md, report, stats = imp.build(d, "T", qp, chdir)
    assert stats["evidence_spans"] == 0
    assert "| p-1 | Scrolls missing | true | ms-book3 | provisional |" in md
