# Tile Log Metadata Contract Alpha v0

Version: `alpha_v0`

Status: `frozen_for_alpha_consumable_layer`

This contract preserves the minimum metadata needed to audit Survey display, first mission candidate selection, MusicKit resolution risk, and provisional Atlas evidence without exposing raw graph rows or hidden simulator truth.

## Displayed Tile Required Fields

Every displayed tile must log:

- `survey_session_id`
- `shown_page_id`
- `shown_page_history_ref`
- `candidate_id`
- `music_object_ref`
- `canonical_entity_id`
- `object_type`
- `display_label`
- `family_id`
- `archetype_ids`
- `survey_page_role`
- `survey_intent`
- `mission_candidate_role`
- `dedupe_group`
- `priority_score`
- `trigger_rule`
- `shown_page_number`
- `shown_position`
- `source_mix`
- `user_response`
- `familiarity_state`
- `timestamp`
- `apple_exposure_prior`
- `apple_payload_reason`
- `adaptive_reason`
- `positive_inference`
- `negative_inference`
- `do_not_infer`
- `quarantine_checked`
- `dedupe_checked`
- `version_checked`
- `music_kit_search_hint`
- `apple_music_resolution_policy`
- `version_risk_note`
- `source_contract_version`

## Generated Page Required Fields

Every generated page must log:

- `page_type`
- `page_number`
- `source_mix`
- `dedupe_checks_passed`
- `quarantine_checks_passed`
- `version_checks_passed`
- `family_distribution`
- `archetype_distribution`
- `candidate_count`
- `suppressed_candidate_count`
- `quarantined_candidate_count`
- `source_contract_version`

## Blocked Fields

Do not log or send through Alpha app/local candidate payloads:

- `hidden_simulator_truth`
- `fake_profile_reason_tags`
- `raw_apple_private_library_payload`
- `apple_auth_token`
- `raw_canonical_graph_row`
- `promoted_atlas_role`
- `final_atlas_confidence_claim`
- `graph_metadata_as_user_taste`
- `candidate_role_as_atlas_role`

## Survey Evidence Export Ingestion

Atlas and Canonical-adjacent ingestion should consume only:

```text
survey_evidence_export.atlas_ingestable.evidence_atoms
```

They must ignore:

```text
survey_evidence_export.construction_only_excluded
```

Any response not backed by the same session's displayed page history is construction-only/quarantined and not Atlas-ingestable.

## music_object_ref Policy

Every displayed tile should carry an Atlas-aligned `music_object_ref` matching:

```text
data/alpha_consumable_layer/alpha_v0/atlas_music_object_ref_alpha_v0.schema.json
```

Allowed `ref_source` values:

- `canonical_graph`
- `user_local`
- `external_catalog`
- `unresolved`

Allowed `object_type` values:

- `artist`
- `album`
- `song_recording`
- `composition_placeholder`

The reference is identity and resolution context only. It is not:

- user taste
- Atlas role truth
- confidence
- promotion state
- permission to mutate the canonical graph

## Response Semantics

Survey responses create:

- observed Signals
- provisional evidence
- possible future Atlas update inputs

Survey responses do not directly create:

- Landmarks
- Regions
- Frontiers
- Dead Ends
- Waypoints

`apple_exposure_prior.taste_truth` is always `false`.

`evidence_strength_hint` is Survey metadata only. It is not Atlas confidence.

`dont_know` maps to `familiarity_uncertainty`. It is not negative taste proof.

`selected_tags` are visible Signal evidence.

`shown_unselected_tags` are weak/non-selected context.

Skip or no-signal events are weak evidence and require review before interpretation.

## Audit Rule

The tile log must preserve enough metadata to answer:

```text
Why was this tile shown?
Which candidate surface did it come from?
Which quarantine/version/dedupe checks passed?
What was the user-visible response?
What should the system avoid inferring?
```
