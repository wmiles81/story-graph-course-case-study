import csv, os, hashlib, zipfile, collections
from pathlib import Path

base=Path('/mnt/data')
phase=base/'story_graph_deep_analysis_phase0'
inv=phase/'EXPANDED-REQUIREMENTS-INVENTORY-v0.1.csv'
rows=list(csv.DictReader(open(inv,encoding='utf-8-sig')))

# Evidence-backed classification after inspecting actual schemas and records.
# FULL = dedicated structure + populated data + evaluation/governance where relevant.
# PARTIAL = fields/data exist but no complete dedicated layer or evaluation.
# ABSENT = no meaningful schema support in Acts I-III.
# SERIES_PENDING = cannot verify cross-book behavior because only Book 3 corpus is loaded.
status={
'REQ-001':'FULL','REQ-002':'FULL','REQ-003':'FULL','REQ-004':'FULL','REQ-005':'SERIES_PENDING',
'REQ-006':'FULL','REQ-007':'PARTIAL','REQ-008':'FULL','REQ-009':'FULL','REQ-010':'PARTIAL',
'REQ-011':'SERIES_PENDING','REQ-012':'PARTIAL','REQ-013':'PARTIAL','REQ-014':'FULL','REQ-015':'SERIES_PENDING',
'REQ-016':'FULL','REQ-017':'SERIES_PENDING','REQ-018':'FULL','REQ-019':'FULL','REQ-020':'SERIES_PENDING',
'REQ-021':'ABSENT','REQ-022':'ABSENT','REQ-023':'ABSENT','REQ-024':'ABSENT','REQ-025':'ABSENT',
'REQ-026':'PARTIAL','REQ-027':'ABSENT','REQ-028':'PARTIAL','REQ-029':'ABSENT',
'REQ-030':'PARTIAL','REQ-031':'PARTIAL','REQ-032':'PARTIAL','REQ-033':'PARTIAL','REQ-034':'ABSENT',
'REQ-035':'PARTIAL','REQ-036':'ABSENT','REQ-037':'ABSENT','REQ-038':'PARTIAL',
'REQ-039':'PARTIAL','REQ-040':'PARTIAL','REQ-041':'PARTIAL','REQ-042':'ABSENT','REQ-043':'FULL','REQ-044':'PARTIAL','REQ-045':'ABSENT','REQ-046':'ABSENT','REQ-047':'ABSENT',
'REQ-048':'FULL','REQ-049':'SERIES_PENDING','REQ-050':'SERIES_PENDING','REQ-051':'PARTIAL','REQ-052':'SERIES_PENDING',
'REQ-053':'FULL','REQ-054':'FULL','REQ-055':'SERIES_PENDING','REQ-056':'PARTIAL','REQ-057':'PARTIAL','REQ-058':'FULL',
'REQ-059':'ABSENT','REQ-060':'ABSENT','REQ-061':'FULL','REQ-062':'FULL','REQ-063':'FULL',
'REQ-064':'SERIES_PENDING','REQ-065':'SERIES_PENDING','REQ-066':'SERIES_PENDING'
}

evidence={
'REQ-001':('BOOK-3-ASSERTIONS-CANON-FROZEN-v2.0.csv','source_document; source_span; source_quote; source_class; authority_level; confidence'),
'REQ-002':('BOOK-3-ASSERTIONS-CANON-FROZEN-v2.0.csv','source_document; source_span; source_quote; plus evidence fields in gold queries and knowledge view'),
'REQ-003':('BOOK-3-CANON-FREEZE-MANIFEST-v2.0.csv; BOOK-3-ACT-II-CANON-PROMOTION-LEDGER-v1.0.csv','versioned freeze and promotion records'),
'REQ-004':('BOOK-3-ENTITY-REGISTRY-CANON-FROZEN-v2.0.csv; BOOK-3-ACT-III-ENTITY-ALIAS-RESOLUTION-v1.0.csv','entity_id; entity_key; canonical_name; aliases; 202 alias rows'),
'REQ-005':('BOOK-3-ENTITY-REGISTRY-CANON-FROZEN-v2.0.csv','book-local stable IDs only; no loaded cross-book identity map'),
'REQ-006':('BOOK-3-SCENE-LEDGER-CANON-FROZEN-v2.0.csv','153 scene rows; stable scene_id; chapter/scene indexes; source hash and boundaries'),
'REQ-007':('BOOK-3-SCENE-LEDGER-CANON-FROZEN-v2.0.csv; BOOK-3-ASSERTIONS-CANON-FROZEN-v2.0.csv','major_events_candidate and event assertion types exist; no event_id registry'),
'REQ-008':('BOOK-3-PROPOSITION-REGISTRY-CANON-FROZEN-v2.0.csv; BOOK-3-ASSERTIONS-CANON-FROZEN-v2.0.csv','160 propositions separated from 196 assertions'),
'REQ-009':('BOOK-3-ASSERTIONS-CANON-FROZEN-v2.0.csv; BOOK-3-ACT-III-VIEW-KNOWLEDGE-TIMELINE-v1.0.csv','epistemic_status; validity range; reveal scene; viewpoint; evidence; 82 timeline rows'),
'REQ-010':('BOOK-3-ASSERTIONS-CANON-FROZEN-v2.0.csv','known, believed, inferred, concealed, unknown represented; suspicion and lie not separately populated'),
'REQ-011':('BOOK-3-ASSERTIONS-CANON-FROZEN-v2.0.csv','no cross-book carryover records'),
'REQ-012':('BOOK-3-ASSERTIONS-CANON-FROZEN-v2.0.csv; BOOK-3-READER-CONTEXTS-CH01-03-v0.1.csv','reader_context field and 2 reader-knowledge assertions; no full-book reader timeline'),
'REQ-013':('BOOK-3-SUSPENSE-ASYMMETRY-MAP-CH01-03-v0.1.csv; reader context artifacts','pilot evidence exists; no frozen full-book dramatic-irony layer'),
'REQ-014':('BOOK-3-SCENE-LEDGER-CANON-FROZEN-v2.0.csv; BOOK-3-TIMELINE-AUDIT-v1.0.csv','story_time_candidate; explicit markers; dedicated timeline audit'),
'REQ-015':('BOOK-3-SCENE-LEDGER-CANON-FROZEN-v2.0.csv','single-book chronology only'),
'REQ-016':('BOOK-3-CUSTODY-STATE-CANON-FROZEN-v2.0.csv; BOOK-3-ACT-III-VIEW-CUSTODY-TIMELINE-v1.0.csv','49 records with object, holder/location, range, change event, risk'),
'REQ-017':('BOOK-3-CUSTODY-STATE-CANON-FROZEN-v2.0.csv','no cross-book object identity/history loaded'),
'REQ-018':('BOOK-3-PROMISE-LIFECYCLE-CANON-FROZEN-v2.0.csv; promise board','69 lifecycle changes with introduced/active/fulfilled states'),
'REQ-019':('BOOK-3-PROMISE-LIFECYCLE-CANON-FROZEN-v2.0.csv','partially-fulfilled, substantially-fulfilled, fulfilled, deferred-to-next-book are distinct'),
'REQ-020':('BOOK-3-PROMISE-LIFECYCLE-CANON-FROZEN-v2.0.csv','one deferred-to-next-book signal, but no cross-book lifecycle'),
'REQ-021':('No dedicated artifact','no plot-thread registry in frozen or Act III schemas'),
'REQ-022':('No dedicated artifact','no scene/event-to-thread membership table'),
'REQ-023':('No dedicated artifact','no contribution type per thread membership'),
'REQ-024':('No dedicated artifact','no plot-intersection ledger'),
'REQ-025':('No dedicated artifact','no transfer semantics at intersections'),
'REQ-026':('BOOK-3-ASSERTIONS-CANON-FROZEN-v2.0.csv; dependency index','derived_from and graph dependencies exist, but not typed causal prerequisites'),
'REQ-027':('No dedicated artifact','enabling conditions not distinguished'),
'REQ-028':('BOOK-3-ACT-III-OPERATIONAL-DEPENDENCY-INDEX-v1.2.csv','3,228 dependency edges support propagation, but dependency is not consequence causality'),
'REQ-029':('No dedicated artifact','actual versus perceived causality not modeled'),
'REQ-030':('Proposition/assertion registries','rules can be stored as propositions, but no world-rule type/registry or rule audit'),
'REQ-031':('BOOK-3-ASSERTIONS-CANON-FROZEN-v2.0.csv','inferred epistemic status and confidence exist; no rule-specific inference model'),
'REQ-032':('BOOK-3-ASSERTIONS-CANON-FROZEN-v2.0.csv','belief represented generally; no rule-belief linkage'),
'REQ-033':('Continuity and assertion structures','could record exceptions/contradictions; no dedicated rule exception lifecycle'),
'REQ-034':('No dedicated artifact','no prior equilibrium, closed options, obligations, vulnerability, reversal-cost fields'),
'REQ-035':('BOOK-3-SCENE-LEDGER-CANON-FROZEN-v2.0.csv','location_candidate exists; no topology, containment, adjacency, route model'),
'REQ-036':('No dedicated artifact','entrances/exits/movement not systematically extracted'),
'REQ-037':('No dedicated artifact','posture/orientation/reachability not modeled'),
'REQ-038':('Custody and scene records','holder/location exists, but exact in-scene placement/accessibility is not systematic'),
'REQ-039':('BOOK-3-ANALYTICAL-STATE-CANON-FROZEN-v2.0.csv','25 states including character, identity, decision, emotional, leadership; sparse and analytical'),
'REQ-040':('BOOK-3-ANALYTICAL-STATE-CANON-FROZEN-v2.0.csv; assertions','relationship_arc/state and relationship assertions exist; no comprehensive transition ledger'),
'REQ-041':('Analytical state, custody, assertions','tactical/threat states and physical state artifacts exist, but no unified capability/injury/resource ledger'),
'REQ-042':('No dedicated artifact','scene brief has goal/turn/outcome but no evaluated state-change test'),
'REQ-043':('BOOK-3-PROMISE-LIFECYCLE-CANON-FROZEN-v2.0.csv; continuity audit','active and deferred promises expose setup without final payoff'),
'REQ-044':('Promise lifecycle and gold queries','some payoff validation possible, but no systematic payoff-without-setup audit'),
'REQ-045':('No dedicated artifact','missing bridges not systematically represented'),
'REQ-046':('No dedicated artifact','no repeated-function or redundant-beat audit'),
'REQ-047':('No dedicated artifact','no subplot-to-main-plot contribution model'),
'REQ-048':('BOOK-3-CONTINUITY-AUDIT-CANON-FROZEN-v2.0.csv','26 adjudicated issues with decision, classification, confirmed_error, reason, action'),
'REQ-049':('Continuity audit','single-book only; no cross-book assertion comparison'),
'REQ-050':('Act II supersession lineage exists','version corrections are tracked, but no cross-book retcon/clarification ledger'),
'REQ-051':('Assertions and continuity audit','unknown truth/epistemic values and author decision flags exist; no dedicated ambiguity lifecycle'),
'REQ-052':('No series corpus','reader context exists but no book-boundary spoiler matrix'),
'REQ-053':('BOOK-3-ACT-III-OPERATIONAL-DEPENDENCY-INDEX-v1.2.csv; scenario results','3,228 edges and tested two-depth impact scenarios'),
'REQ-054':('BOOK-3-ACT-III-OPERATIONAL-DEPENDENCY-INDEX-v1.2.csv; lexical repair report','stable-ID and lexical entity dependencies tested and repaired'),
'REQ-055':('Dependency system','only Book 3 targets loaded'),
'REQ-056':('BOOK-3-ACT-III-REVISION-IMPACT-CLASSIFICATION-v1.0.csv; scenario results','severity/review/test policy exists; no complete formal repair-ranking ledger'),
'REQ-057':('BOOK-3-GOLD-QUERY-EVALUATION-CANON-FROZEN-v2.0.csv; operational evaluation','180 canon questions and 39 operational tests, but none for absent new layers'),
'REQ-058':('BOOK-3-ACT-III-SAFE-FAILURE-TEST-CASES-v1.0.csv; results','10 adversarial/negative cases, all tested'),
'REQ-059':('Dependency graph only','no PageRank, HITS, degree, closeness, or betweenness results'),
'REQ-060':('No dedicated artifact','no community detection or clustering results'),
'REQ-061':('Six materialized views and 10-view inventory','scene, knowledge, custody, promise, continuity, analytical views; author-oriented rendering rules'),
'REQ-062':('Act I–III manifests, progress records, freeze manifest','chronological artifact registers and hashes exist'),
'REQ-063':('Author decision ledgers; author_decision_required fields; approval state machine','explicit decision gates and author authority'),
'REQ-064':('Analytical states','Book 3 arc states exist; no cross-volume arc'),
'REQ-065':('Relationship states','Book 3 only; no cross-volume relationship arc'),
'REQ-066':('One series-promise assertion / deferred promise','no cross-book thread registry or memberships')
}

notes={
'FULL':'Dedicated populated artifact(s) and sufficient schema support exist for the stated Book 3 capability.',
'PARTIAL':'Acts I–III contain relevant fields or pilot data, but not a complete dedicated, full-book, evaluated layer.',
'ABSENT':'No meaningful dedicated schema or systematic evaluation exists in the inspected Acts I–III artifacts.',
'SERIES_PENDING':'The schema may contain hints, but cross-book coverage cannot be verified until additional books are loaded and identity-mapped.'
}

out=phase/'BOOK-AND-SERIES-COVERAGE-GAP-AUDIT-VERIFIED-v1.0.csv'
with open(out,'w',newline='',encoding='utf-8') as f:
    cols=['requirement_id','domain','requirement','scope','preliminary_coverage','verified_classification','evidence_artifact','evidence_schema_or_finding','verification_basis','next_action']
    w=csv.DictWriter(f,fieldnames=cols);w.writeheader()
    for r in rows:
        rid=r['requirement_id']; s=status[rid]; art,ev=evidence[rid]
        action={'FULL':'reuse and regression-test; do not rebuild','PARTIAL':'extend or normalize after bounded schema design','ABSENT':'design new analytical layer before extraction','SERIES_PENDING':'defer classification until next-book corpus and identity mapping are loaded'}[s]
        w.writerow({**r,'verified_classification':s,'evidence_artifact':art,'evidence_schema_or_finding':ev,'verification_basis':notes[s],'next_action':action})

cnt=collections.Counter(status.values())
report=phase/'COVERAGE-VERIFICATION-REPORT-v1.0.md'
changes=[]
for r in rows:
    prelim={'Existing':'FULL','Partial':'PARTIAL','Absent':'ABSENT'}.get(r['preliminary_coverage'],r['preliminary_coverage'])
    if prelim!=status[r['requirement_id']]: changes.append((r['requirement_id'],r['requirement'],prelim,status[r['requirement_id']]))
report.write_text(f'''# Coverage Verification Report v1.0

**Date:** 2026-07-23  
**Scope:** 66 requirements from the expanded Book and Series inventory  
**Evidence basis:** actual frozen Act II CSV schemas and records, plus Act III operational, dependency, query, evaluation, and safe-failure artifacts

## Result

- VERIFIED FULL: {cnt['FULL']}
- VERIFIED PARTIAL: {cnt['PARTIAL']}
- VERIFIED ABSENT: {cnt['ABSENT']}
- SERIES PENDING: {cnt['SERIES_PENDING']}
- Total: {sum(cnt.values())}

## Important correction to the preliminary audit

The first audit used three broad labels and treated many series requirements as absent. The verified audit introduces **SERIES_PENDING** because a single-book corpus cannot prove or disprove cross-book continuity support. That is not semantic hair-splitting; it prevents us from declaring a failure before the required evidence exists.

## Schema findings

### Strong existing foundations

- Assertion-level provenance and authority are fully represented.
- Proposition and assertion are structurally separate.
- Scene identity and source boundaries are stable across 153 scenes.
- Character epistemic state has validity ranges, reveal scenes, viewpoint context, evidence, and authority.
- Custody and promise lifecycles are dedicated populated layers.
- Promise statuses already distinguish partial, substantial, final, failed/reopened, and deferred closure.
- Continuity findings are adjudicated rather than merely detected.
- Revision impact uses 3,228 dependency edges and includes repaired lexical dependencies.
- Gold evaluation and negative/safe-failure testing are real, not aspirational checkboxes wearing a tie.

### Partial rather than absent

Several capabilities originally labeled absent have genuine footholds:

- reader knowledge exists in `reader_context`, reader-knowledge assertions, and the Chapter 1–3 reader-context pilot;
- event information exists in scene `major_events_candidate` and event assertion types, but lacks stable event identity;
- world rules can be expressed as propositions/assertions, but no rule-specific registry or exception lifecycle exists;
- character and relationship states exist, but are sparse analytical records rather than comprehensive transition histories;
- causality has `derived_from` and dependency edges, but dependency must not be mistaken for causal proof;
- location and custody fields support limited spatial reasoning, but not topology or blocking.

### Confirmed missing layers

The inspected schemas do not contain dedicated support for:

- plot-thread registry, many-to-many membership, contribution, or intersections;
- enabling conditions and perceived-versus-actual causality;
- narrative irreversibility and reversal cost;
- entrances, exits, blocking, posture, orientation, and reachability;
- scene state-change, missing-bridge, redundancy, or subplot-contribution audits;
- graph centrality or community-detection results.

## Classification changes from the preliminary audit

{chr(10).join(f'- `{rid}` {name}: **{a} → {b}**' for rid,name,a,b in changes) if changes else '- None'}

## Gate decision

**Gate 0 is not yet ready for approval.** The coverage classifications are now verified, but the next step is to revise the proposed analytical-layer plan so that it:

1. reuses the full layers without rebuilding them;
2. extends partial layers from their actual columns;
3. creates only the confirmed missing layers;
4. reserves series-pending requirements for the first additional book ingestion.

No new manuscript extraction has begun.
''',encoding='utf-8')

# Schema inventory snapshot
schema=phase/'ACT-I-III-SCHEMA-INVENTORY-v1.0.csv'
patterns=list(base.glob('BOOK-3-*-CANON-FROZEN-v2.0.csv'))+list(base.glob('BOOK-3-ACT-III-*.csv'))
with open(schema,'w',newline='',encoding='utf-8') as f:
    w=csv.writer(f);w.writerow(['filename','row_count','columns','sha256'])
    for p in sorted(patterns):
        with open(p,encoding='utf-8-sig',newline='') as fh:
            rr=csv.reader(fh);h=next(rr); n=sum(1 for _ in rr)
        w.writerow([p.name,n,' | '.join(h),hashlib.sha256(p.read_bytes()).hexdigest()])

# Updated progress
prog=phase/'DEEP-ANALYSIS-PROGRESS-RECORD-v0.2.md'
prog.write_text(f'''# Deep Analysis Progress Record v0.2

**Status:** Phase 0 coverage verification complete; layer-plan revision pending

## Completed

- Inspected all nine frozen canon CSV schemas and records.
- Inspected Act III query, view, dependency, revision-impact, evaluation, safe-failure, traceability, and governance CSVs.
- Verified all 66 preliminary coverage classifications.
- Created an evidence-level audit naming the supporting artifact and fields for every requirement.
- Separated true absence from series requirements that cannot yet be evaluated.

## Verified totals

- Full: {cnt['FULL']}
- Partial: {cnt['PARTIAL']}
- Absent: {cnt['ABSENT']}
- Series pending: {cnt['SERIES_PENDING']}

## Next action

Revise `PROPOSED-ANALYTICAL-LAYERS-v0.1.md` into v1.0 using the verified reuse/extend/create boundaries. Do not begin extraction before that revision is reviewed.
''',encoding='utf-8')

# manifest and package
files=[out,report,schema,prog]
man=phase/'COVERAGE-VERIFICATION-MANIFEST-v1.0.csv'
with open(man,'w',newline='',encoding='utf-8') as f:
    w=csv.writer(f);w.writerow(['filename','size_bytes','sha256'])
    for p in files: w.writerow([p.name,p.stat().st_size,hashlib.sha256(p.read_bytes()).hexdigest()])
files.append(man)
zip_path=base/'STORY-GRAPH-COVERAGE-VERIFICATION-v1.0.zip'
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
    for p in files: z.write(p,arcname=p.name)
print(cnt)
print('changes',len(changes))
print(out,report,schema,prog,zip_path,sep='\n')