# Cartenza Affinity Codex Repo Truth Package v0.3.1

## Purpose

This package is the Codex handoff for the future graph-wide Cartenza Affinity Tagging runtime exercise. It is intended to be added to the repo as the authoritative product/data contract for mass affinity assignment once the canonical graph expansion work is complete.

This package does **not** contain runtime-ingested affinity output and does **not** authorize graph-wide tagging by itself. It prepares the schema, ontology, allowed tags, validation gates, metadata, and dispatch instructions Codex should use when PM later authorizes the mass run.

## PM lock status

```text
Affinity ontology v0.2.2: APPROVED
Sparse tagging rules v0.3: APPROVED
Schema boundary amendment v0.3.1: APPROVED
Graph-wide tagging: PREPARED BUT BLOCKED PENDING GRAPH EXPANSION
Runtime ingestion: NOT APPROVED
```

## Controlling rules

1. Use the completed canonical graph export as source of truth once graph expansion is done.
2. Use only canonical runtime tags in `allowed_tags/allowed_canonical_tags_by_dimension_v0_3_1.json`.
3. Do not invent tags.
4. Do not use aliases in output.
5. Do not use Matt/founder taste calibration evidence.
6. Treat the app user as generic Jane Doe.
7. Separate intrinsic song truth from membership/route context overlays.
8. Do not ingest generated tags into runtime until PM approves.

## Core schema boundary

`canonical_song_affinity_tags` may use only:

```text
vocal_performance
emotion_theme
sonic_texture
rhythm_body
form_container
```

`membership_context_overlays` may use only:

```text
social_context
routing_caution
```

## Primary files for Codex

- `dispatch/CODEX_DISPATCH_GRAPHWIDE_AFFINITY_TAGGING_v0_3_1.md`
- `schemas/affinity_tagging_output_schema_v0_3_1.json`
- `ontology/affinity_tag_ontology_v0_2_2_schema_amended_v0_3_1.json`
- `allowed_tags/allowed_canonical_tags_by_dimension_v0_3_1.json`
- `allowed_tags/APPROVED_CANONICAL_RUNTIME_TAGS_v0_3_1.md`
- `instructions/affinity_graphwide_tagging_instructions_v0_3_1.md`
- `validation/affinity_graphwide_QA_contract_v0_3_1.md`
- `metadata/affinity_repo_truth_manifest_v0_3_1.json`

## Suggested repo location

```text
data/canonical_graph/affinity_contracts/v0_3_1/
```
