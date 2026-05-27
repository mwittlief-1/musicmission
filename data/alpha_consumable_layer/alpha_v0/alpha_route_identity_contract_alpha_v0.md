# Alpha Route Identity Contract

Version: `alpha_v0`

Status: `live_generation_recovery_identity_contract`

This contract defines the Canonical Graph route identity fields for live Alpha mission generation/import recovery. It exists so Mission Generation, Supabase validation, Core import, and support diagnostics can validate route items without guessing from display strings.

## Core Rule

Mission route items must come from the supplied candidate pool.

Digest regions, Survey signals, Atlas hints, Apple exposure, or model knowledge may influence why a candidate is selected, but they must not create a playable route item unless that item is present in the candidate pool.

## Required Identity Fields

| field | meaning | validator use |
| --- | --- | --- |
| `candidate_id` | Exact candidate-pool membership ID. | Required membership check. `route.items[].candidate_id` must match the supplied pool. |
| `route_candidate_key` | Canonical playable identity: `route:{track|album}:{song_recording|album}:{canonical_entity_id}`. | Preferred duplicate and batch-repeat key when present. |
| `route_batch_dedupe_key` | Graph dedupe identity, normally copied from `dedupe_group`. | Preferred cross-mission exclusion key when present. |
| `app_route_item_id` | Deterministic app-safe item ID for `route.items[].item_id`. | Core import identity and item ID duplicate validation. |
| `canonical_entity_id` | Canonical object ID. | Secondary integrity check with `canonical_object_type`. |
| `dedupe_group` | Survey/candidate-surface dedupe identity. | Fallback duplicate key if `route_batch_dedupe_key` is missing. |
| `route_display_identity_key` | Normalized item type + artist + title. | Fallback diagnostic key and batch-repeat guard; display text is not primary identity. |

## Display Contract

Preferred app-facing fields:

- `display_name`: route title.
- `display_label`: graph/survey-compatible title, same value as `display_name` for Alpha route candidates.
- `credited_artist`: route artist credit.
- `music_object_ref.display_name`: Atlas/reference title.
- `music_object_ref.credited_artist_name`: reference artist credit for song recordings.

Internal IDs and slugs are not preferred UI labels:

- `candidate_id`
- `canonical_entity_id`
- `route_candidate_key`
- `route_batch_dedupe_key`
- `dedupe_group`
- `source_membership_id`

## Mission Output Copy Rules

Mission Generation should copy these fields from the chosen candidate:

- `route.items[].candidate_id` = `candidate_id`
- `route.items[].item_id` = `app_route_item_id`
- `route.items[].route_candidate_key` = `route_candidate_key`, when the mission schema allows it
- `route.items[].route_batch_dedupe_key` = `route_batch_dedupe_key`, when the mission schema allows it
- `route.items[].display_metadata.title` = `display_name`
- `route.items[].display_metadata.artist` = `credited_artist`

If a mission schema cannot yet carry `route_candidate_key` or `route_batch_dedupe_key`, validators should still enforce `candidate_id`, `item_id`, and display identity while treating the missing stronger keys as a schema-follow-up for Mission/Core.

## Validation Policy

Block a single mission from app import when any of these occur:

- duplicate `route.items[].item_id`
- duplicate `route.items[].candidate_id`
- duplicate `route.items[].route_candidate_key`, when present
- duplicate `route.items[].route_batch_dedupe_key`, when present
- missing `route.items[].candidate_id`
- `route.items[].candidate_id` not found in the supplied candidate pool
- duplicate route display identity when stronger keys are missing

Block or regenerate across the 10-mission batch when any of these repeat:

- `app_route_item_id`
- `candidate_id`
- `route_candidate_key`
- `route_batch_dedupe_key`
- `route_display_identity_key` when stronger keys differ or are missing

Do not hard-block solely because a candidate has review flags such as `alpha_safe_with_review_flags`, `generate_allowed_store_review_flags`, or high risk on an intentional `risky_probe` / `trap`. Those flags should be preserved for audit and review.

## Candidate-Pool-Only Rule

Route items may not be fabricated from:

- digest strong regions
- Survey-visible tiles
- Atlas role hints
- Apple Music exposure payloads
- model memory
- raw graph rows

Those sources may explain candidate selection. They do not supply playable mission route objects.

## Atlas Boundary

Route identity fields are operational references only. They do not create user taste, Atlas roles, Landmarks, Regions, Frontiers, Dead Ends, or Waypoints.

Valid mission import is still not taste evidence by itself. Listening/review signals decide what becomes Atlas evidence.
