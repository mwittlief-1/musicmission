# Affinity Schema Amendment QA Report v0.3.1

## Decision encoded

PM approved v0.3 sparse pilot and v0.2.2 ontology/sparsity rules, with one required schema amendment before graph-wide tagging: separate core song affinity from route/membership context overlays.

## Artifact outputs

- `affinity_schema_boundary_amendment_v0_3_1.md`
- `affinity_tagging_output_schema_v0_3_1.json`
- `affinity_graphwide_tagging_instructions_v0_3_1.md`
- `affinity_tag_ontology_v0_2_2_schema_amended_v0_3_1.json`
- `affinity_sparse_pilot_split_schema_evidence_v0_3_1.json`
- `affinity_duplicate_context_review_candidates_v0_3_1.json`
- `affinity_duplicate_context_review_v0_3_1.md`
- `affinity_context_leak_review_flags_v0_3_1.json`
- `affinity_schema_amendment_QA_metrics_v0_3_1.json`

## Checks

| Check | Result |
|---|---:|
| Ontology dimensions preserved | PASS |
| Ontology tag count preserved | PASS |
| Core dimensions separated | PASS |
| Overlay dimensions separated | PASS |
| Sparse pilot converted to split schema | PASS |
| Duplicate/context candidates surfaced | PASS |
| Runtime ingestion authorized | NO |
| Graph-wide tagging executed | NO |

## Key metrics

```json
{
  "schema_amendment_version": "v0.3.1",
  "ontology_canonical_tag_count": 86,
  "ontology_dimension_count": 7,
  "core_dimensions": [
    "vocal_performance",
    "emotion_theme",
    "sonic_texture",
    "rhythm_body",
    "form_container"
  ],
  "overlay_dimensions": [
    "social_context",
    "routing_caution"
  ],
  "sparse_pilot_song_count_converted": 120,
  "duplicate_context_candidate_groups_in_graph": 29,
  "sparse_pilot_context_leak_flags": 6,
  "graph_wide_tagging_status": "schema_contract_prepared_not_executed",
  "runtime_ingestion_status": "not_approved"
}
```

## PM readout

This package fixes the next failure mode: context leak into core song truth. It does not rewrite the ontology, does not shrink the tag list, and does not ingest any tags into runtime.

Graph-wide tagging is now ready to be launched under the split-schema contract, subject to PM acceptance of this amendment.
