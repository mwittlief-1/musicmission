# Alpha 1 Fixed Survey Intake Graph Support

Version: `alpha_v0`

Status: `approved_graph_support_for_alpha1_fixed_intake`

Product decision source:

```text
docs/app_dev/alpha_product_decision_addendum_2026_05_22.md
```

This artifact aligns the frozen Alpha graph surfaces with the Alpha 1 first-run Survey decision:

```text
4 artist screens
2 album screens
4 song screens
12 tiles per screen
```

It does not create a new canonical database version. It confirms that the existing `alpha_v0` consumable layer has enough approved, deduped, non-quarantined material for the fixed intake shape.

## Ownership Boundary

Graph owns:

- approved candidate surface availability
- candidate eligibility guardrails
- quarantine and suppression enforcement
- reference-only graph metadata
- MusicKit/version-risk notes

Survey owns:

- live page selection
- shown page freezing
- displayed page history
- final page composition
- adaptive trigger sequencing
- reaction language
- tile UI behavior
- Survey evidence export assembly

Core owns:

- first-run state machine
- page display and logging
- local persistence
- post-Survey generation screen

Atlas owns:

- Signal ingestion
- AtlasDigestView
- promotion/demotion semantics
- Landmark, Region, Frontier, Dead End, and Waypoint creation rules

Mission Generation owns:

- first mission batch generation
- candidate ranking from Survey/Atlas evidence
- mission review interpretation

## Intake Capacity

| object surface | required pages | required tiles | allowed buckets | available candidates | status |
| --- | ---: | ---: | --- | ---: | --- |
| artist | 4 | 48 | `page1_core`, `page2_adaptive` | 957 | pass |
| album | 2 | 24 | `page1_core`, `page2_adaptive` | 871 | pass |
| song recording | 4 | 48 | `page1_core`, `page2_adaptive` | 972 | pass |

Default bucket guidance:

- Artist page 1: `page1_core`
- Artist pages 2-4: `page2_adaptive`
- Album page 1: `page1_core`
- Album page 2: `page2_adaptive`
- Song page 1: `page1_core`
- Song pages 2-4: `page2_adaptive`

Survey can override ordering inside those buckets, but it must not pull raw graph rows or suppressed/quarantined rows.

## Allowed Inputs

Fixed-intake page generation may use only:

```text
data/canonical_graph/normalization_pass_2/survey_artist_candidates_v0_2.json
data/canonical_graph/normalization_pass_2/survey_album_candidates_v0_2.json
data/canonical_graph/normalization_pass_2/survey_song_candidates_v0_2.json
data/canonical_graph/normalization_pass_2/family_survey_readiness_v0_2.json
data/canonical_graph/normalization_pass_2/archetype_readiness_v0_2.json
data/canonical_graph/normalization_pass_2/canonical_quarantine_queue.json
data/canonical_graph/normalization_pass_2/canonical_recording_versions.json
data/alpha_consumable_layer/alpha_v0/alpha_candidate_blocklist_alpha_v0.json
data/alpha_consumable_layer/alpha_v0/resolver_policy_machine_fields_alpha_v0.json
data/alpha_consumable_layer/alpha_v0/tile_log_metadata_contract_alpha_v0.json
```

Blocked inputs:

- raw family rows
- raw canonical entity tables
- merge review queues
- composition review queues
- hidden simulation truth
- raw Apple Music payloads
- suppressed/quarantined candidate rows

## Eligibility Rules

Fast intake candidates must satisfy all of these:

- `review_status == approved`
- `quarantine_reasons` is empty
- candidate is not in `alpha_candidate_blocklist_alpha_v0.json`
- typed entity ref is not in `canonical_quarantine_queue.json`
- family is `survey_ready`
- family has `fast_survey_allowed == true`
- family is not context-only
- `survey_page_role` matches the source bucket

Song recordings must also satisfy:

- matching row exists in `canonical_recording_versions.json`
- recording `review_status == approved`
- recording `survey_safe == true`
- `apple_music_resolution_policy != manual_review_required`

Family 15 and Family 17 remain blocked from default Fast Survey intake because they are context-only.

## Required Tile Metadata

Every displayed tile must preserve:

- `survey_session_id`
- `shown_page_id`
- `shown_page_history_ref`
- `candidate_id`
- `canonical_entity_id`
- `object_type`
- `family_id`
- `archetype_ids`
- `survey_page_role`
- `survey_intent`
- `dedupe_group`
- `priority_score`
- `trigger_rule`
- `shown_page_number`
- `shown_position`
- `user_response`
- `familiarity_state`
- `timestamp`
- `apple_exposure_prior`
- `apple_payload_reason`, if any
- `adaptive_reason`, if any
- `positive_inference`
- `negative_inference`
- `do_not_infer`

These fields are evidence context. They are not Atlas promotion claims.

## Survey Evidence Export Ingestion

Canonical/Atlas ingestion should consume only:

```text
survey_evidence_export.atlas_ingestable.evidence_atoms
```

It must ignore:

```text
survey_evidence_export.construction_only_excluded
```

Responses without same-session displayed page history are construction-only/quarantined and not Atlas-ingestable.

## Dedupe Rules

Within a generated page:

- no duplicate `candidate_id`
- no duplicate `canonical_entity_id`
- no duplicate `dedupe_group`

Across the fixed intake:

- avoid repeated `dedupe_group` by default
- repeat only when Survey explicitly marks the tile as a version/composition test

## Truth Rules

- Graph metadata is not user taste.
- Apple payload metadata is not user taste.
- Apple payload metadata is not canonical identity truth.
- `apple_exposure_prior.taste_truth` is always `false`.
- `evidence_strength_hint` is Survey metadata only, not Atlas confidence.
- `dont_know` maps to `familiarity_uncertainty`, not negative taste.
- Survey response creates provisional evidence only.
- Survey response does not directly create a Landmark, Region, Frontier, Dead End, or Waypoint.
- False-nearby and boundary rows are probes, not conclusions.

## Safe-Send Position

Supabase: safe only for approved candidate rows and tile-log evidence that pass this contract.

OpenAI: safe only for compact candidate pools or tile-log context packets. Do not send raw graph rows.

Core app integration: ready with guardrails.
