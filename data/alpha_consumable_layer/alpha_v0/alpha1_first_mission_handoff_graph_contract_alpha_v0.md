# Alpha 1 First Mission Handoff Graph Contract

Version: `alpha_v0`

Status: `approved_graph_handoff_contract_for_generated_first_missions`

This contract defines what the Canonical Music Graph lane can hand to Survey, Atlas, Core, Supabase, and Mission Generation after the required Alpha 1 Survey intake completes.

It does not define Atlas promotion semantics. It does not generate missions by itself. It supplies reference-safe candidate material and guardrails.

MGN-I004 resolution:

```text
Mission Generation must receive concrete route-ready `track` / `album` candidates.
Artist-level candidates are blocked from route pools.
The graph pool may still use canonical song-recording or album refs under `music_object_ref`.
```

## Handoff Shape

The first mission handoff should be built from:

```text
Survey tile logs
Survey evidence export / Signal packet
Atlas digest, when available
compact candidate pool generated from alpha_v0 surfaces
```

The compact candidate pool helper remains:

```text
scripts/build_alpha_compact_candidate_pool_alpha_v0.mjs
```

The sample output remains:

```text
data/alpha_consumable_layer/alpha_v0/sample_compact_candidate_pool_alpha_v0.json
```

Route identity contract:

```text
data/alpha_consumable_layer/alpha_v0/alpha_route_identity_contract_alpha_v0.json
data/alpha_consumable_layer/alpha_v0/alpha_route_identity_contract_alpha_v0.md
```

## Required Candidate Fields

Mission Generation needs these graph-provided candidate fields:

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
- `trigger_rule`
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

Route-ready rule:

- `candidate_id` is the exact candidate-pool membership ID and must be copied to `route.items[].candidate_id`
- `app_route_item_id` is the deterministic app-safe item ID and should be copied to `route.items[].item_id`
- `route_candidate_key` is the canonical playable identity and should be unique within a mission and across the generated 10-mission batch
- `route_batch_dedupe_key` is the batch-level dedupe identity and should be unique within a mission and across the generated 10-mission batch
- `route_display_identity_key` is a fallback duplicate guard and should not repeat within a mission or batch when stronger keys differ or are missing
- `object_type = track` must carry `music_object_ref.object_type = song_recording`
- `object_type = album` must carry `music_object_ref.object_type = album`
- `playable_route_ready` must be `true`
- `artist_level_candidate` must be `false`
- `credited_artist` and `music_kit_search_hint` must be present
- `alpha_safe_with_review_flags` is not a hard block by itself
- `generate_allowed_store_review_flags` means preserve the flags and continue Alpha generation attempts

Mission Generation must not fabricate route items from digest strong regions, Survey-visible tiles, Atlas hints, Apple exposure, model memory, or raw graph rows. Those sources may explain selection, but route items must come from the supplied candidate pool.

## Candidate Behaviors

Graph candidates should use the shared behavior vocabulary:

- `anchor`
- `bridge`
- `probe`
- `risky_probe`
- `waypoint`
- `trap`
- `exclude`
- `unknown`

Mission Generation may use:

- `anchor` as a route start or comparison point
- `bridge` as a cross-lane exploration item
- `probe` as a test item
- `risky_probe` only with caution language and clear learning purpose
- `waypoint` as useful connective or context material
- `trap` only as a dead-end check, never as a normal recommendation

Mission Generation must not use:

- `exclude`
- `unknown`
- artist-level route candidates
- pseudo-playable route items
- blocked candidates
- quarantined rows
- suppressed rows
- manual-review recording rows
- context-only family rows unless a deliberate context mission is approved

## Handoff Guardrails

The graph lane guarantees only that a candidate is eligible graph material under `alpha_v0`.

The graph lane does not claim:

- the user likes the candidate
- the candidate should become an Atlas Landmark
- the candidate belongs in a Region
- the candidate is a confirmed Dead End
- the candidate should be auto-resolved through Apple Music if resolver policy says manual review

Survey/Atlas evidence must decide what the candidate means for this user.

## Family Handling

Default first mission generation may use survey-ready families:

```text
1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 18
```

Default first mission generation must not use context-only families:

```text
15, 17
```

Caution families remain allowed only when resolver/version/work rules are honored:

```text
11 electronic/version caution
13 language/remix/collaboration caution
14 work/recording caution
16 worship-standard/church-brand caution
```

## Supabase/OpenAI Safety

Safe for Supabase when:

- candidate comes from approved `alpha_v0` surfaces
- `eligible_for_supabase == true`
- no quarantine/blocklist/manual-review policy applies
- `music_object_ref` validates
- tile log metadata is preserved

Safe for OpenAI when:

- payload is compact
- payload contains reference-safe graph metadata only
- raw graph rows are excluded
- hidden simulation truth is excluded
- quarantined/manual-review rows are excluded
- graph metadata is explicitly marked as not user taste

## Post-Survey Generation Status

During the Core "generating" screen, graph state may support phrases like:

- "preparing candidate roads"
- "checking version-safe music matches"
- "building a first mission candidate set"

Avoid implying that graph metadata has already created promoted Atlas truth.

## Blockers

No current Canonical Music Graph blocker prevents Core from integrating the Alpha 1 first mission handoff.

Final blockers remain owned elsewhere:

- Atlas owns promotion/demotion thresholds and final `Signal -> AtlasRoleAssignment` behavior.
- Supabase/Infrastructure owns live account/project access and upload endpoints.
- Brand/Design/Release owns final privacy, terms, onboarding, and FAQ copy.
