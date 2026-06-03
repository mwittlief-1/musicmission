# Compact Candidate Pool Export Format Alpha v0

Version: `alpha_v0`

Status: `frozen_for_alpha_consumable_layer`

Helper:

```text
scripts/build_alpha_compact_candidate_pool_alpha_v0.mjs
```

Sample output:

```text
data/alpha_consumable_layer/alpha_v0/sample_compact_candidate_pool_alpha_v0.json
```

Alpha 1 first mission handoff:

```text
data/alpha_consumable_layer/alpha_v0/alpha1_first_mission_handoff_graph_contract_alpha_v0.json
data/alpha_consumable_layer/alpha_v0/alpha1_first_mission_handoff_graph_contract_alpha_v0.md
```

Route identity contract:

```text
data/alpha_consumable_layer/alpha_v0/alpha_route_identity_contract_alpha_v0.json
data/alpha_consumable_layer/alpha_v0/alpha_route_identity_contract_alpha_v0.md
```

## Purpose

The compact candidate pool gives Mission Generation a small, curated, role-labeled set of playback-ready candidates for handoff tests and compact prompt payloads. It is sourced from approved Alpha graph surfaces and should be further filtered/ranked by user Survey and Atlas evidence.

It is not the canonical mission-item universe. The full mission universe is:

```text
data/alpha_consumable_layer/alpha_v0/canonical_mission_item_universe_alpha_v0.json
```

Do not send the whole graph to OpenAI.

MGN-I004 guardrail: playback route pools must contain concrete `track` candidates for early Alpha default playback. Artist-only candidates must not be used as pseudo-playable playback items. Album candidates remain reference/context material unless a later album-route contract explicitly enables them.

Playable `track` candidates must have a resolved Apple Music catalog ID. Canonical songs without an Apple ID remain in the graph but are marked `do_not_use_no_apple_id` for Alpha playback and default Mission Generation.

## Pool Buckets

Allowed pool buckets:

- `anchors`
- `bridges`
- `probes`
- `boundary_probes`
- `dead_end_checks`
- `waypoints`

Each candidate includes:

- `candidate_id`
- `route_candidate_key`
- `route_batch_dedupe_key`
- `route_display_identity_key`
- `app_route_item_id`
- `candidate_role`
- `music_object_ref`
- `canonical_entity_id`
- `object_type`
- `canonical_object_type`
- `route_item_type`
- `playable_route_ready`
- `artist_level_candidate`
- `route_item`
- `display_label`
- `display_name`
- `credited_artist`
- `family_id`
- `archetype_ids`
- `survey_page_role`
- `survey_intent`
- `mission_candidate_role`
- `candidate_pool_behavior`
- `dedupe_group`
- `priority_score`
- `why_selected`
- `expected_signal`
- `risk_class`
- `candidate_safety_state`
- `review_gate_status`
- `review_gate_action`
- `default_alpha_mission_eligible`
- `hard_block`
- `blocked_reason`
- `quarantine_status`
- `suppression_status`
- `resolver_risk_class`
- `review_risk_flags`
- `context_only`
- `manual_review_required`
- `familiarity_assumption`
- `positive_inference`
- `negative_inference`
- `do_not_infer`
- `music_kit_search_hint`
- `music_kit_resolution_status`
- `apple_music_catalog_status`
- `apple_music_catalog_id`
- `apple_music_catalog_url`
- `apple_music_catalog_match_status`
- `apple_music_catalog_match_basis`
- `apple_music_resolution_policy`
- `version_risk_note`
- `source_file`
- `source_contract_version`
- `source_membership_id`
- `source_evidence_refs`
- `source_evidence_summary`
- `atlas_role_refs`
- `atlas_role_ref_status`
- `review_status`
- `eligible_for_supabase`
- `eligible_for_openai`

For route candidates:

- `object_type` is `track` for early Alpha default playback.
- `candidate_id` is the exact candidate-pool membership ID.
- `app_route_item_id` is the app-safe deterministic ID Mission Generation should copy to `route.items[].item_id`.
- `route_candidate_key` is the canonical playable route identity.
- `route_batch_dedupe_key` is the mission/batch uniqueness key.
- `route_display_identity_key` is fallback diagnostic identity only.
- `canonical_object_type` preserves the graph source type, normally `song_recording` in the default pool.
- `track` candidates carry `music_object_ref.object_type = song_recording`.
- `album` candidates remain reference/context material until a future album-route contract enables them.
- `music_kit_resolution_status = catalog_id_resolved` means the candidate already has an Apple Music catalog ID in the app catalog index.
- `apple_music_catalog_status = resolved` and a non-empty `apple_music_catalog_id` are required for the early Alpha default pool.
- `do_not_use_no_apple_id` rows are retained for graph/QA/manual resolver work but excluded from playback routes and default Mission Generation.
- `candidate_safety_state = alpha_safe_with_review_flags` means store/review the flags, not automatically block generation.
- `review_gate_action = generate_allowed_store_review_flags` means Mission Generation/Supabase should preserve caution metadata while continuing attempts.

Route items must be selected from the supplied candidate pool. Digest regions, Survey responses, Atlas hints, Apple exposure, and model memory may shape selection but must not create non-candidate route items.

Review-risk report:

```text
data/alpha_consumable_layer/alpha_v0/candidate_review_risk_report_alpha_v0.json
data/alpha_consumable_layer/alpha_v0/candidate_review_risk_report_alpha_v0.md
```

## Export Rule

The helper blocks:

- artist-level candidates from route pools
- context-only families
- quarantined rows
- suppressed rows
- Alpha blocklist rows
- manual-review recording rows
- missing or unsafe recording-version sidecars
- rows without a resolved Apple Music catalog ID
- duplicate dedupe groups in one export
- duplicate route display identities in one export

## Mission Boundary

Mission Generation should treat this pool as candidate material only. It must not infer Atlas roles or user taste from graph membership.

For Alpha 1, this pool is consumed only after the required fixed Survey intake has produced provisional evidence. Survey/Atlas evidence selects and ranks from the pool; graph membership alone does not create first missions.
