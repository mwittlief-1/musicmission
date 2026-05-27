# Route-Ready Candidate Pool Report Alpha v0

Generated: 2026-05-25T12:52:08.142Z

Status: `live_generation_recovery_route_identity_ready`

Input blocker:

```text
live_generation_duplicate_non_candidate_route_items_2026_05_25
```

Candidate pool:

```text
data/alpha_consumable_layer/alpha_v0/sample_compact_candidate_pool_alpha_v0.json
```

Route identity contract:

```text
data/alpha_consumable_layer/alpha_v0/alpha_route_identity_contract_alpha_v0.json
```

## Summary

| metric | count |
| --- | ---: |
| total candidates | 72 |
| route-ready candidates | 72 |
| artist candidates | 0 |
| track candidates | 50 |
| album candidates | 22 |
| waypoints | 12 |
| dead-end checks | 12 |
| default Alpha mission eligible | 72 |
| hard blocked | 0 |
| unique route_candidate_key values | 72 |
| unique route_batch_dedupe_key values | 72 |
| unique app_route_item_id values | 72 |
| unique route_display_identity_key values | 72 |

## Pool Counts

| pool | total | track | album |
| --- | ---: | ---: | ---: |
| anchors | 12 | 12 | 0 |
| bridges | 12 | 12 | 0 |
| probes | 12 | 3 | 9 |
| boundary_probes | 12 | 12 | 0 |
| dead_end_checks | 12 | 11 | 1 |
| waypoints | 12 | 0 | 12 |

## Route Identity Policy

- Route items must come from the supplied candidate pool.
- `candidate_id` is the exact membership key.
- `app_route_item_id` is the app-safe `route.items[].item_id` seed Mission Generation should copy.
- `route_candidate_key` and `route_batch_dedupe_key` are the preferred non-display duplicate and batch-repeat keys.
- `route_display_identity_key` is a fallback duplicate and batch-repeat guard when stronger keys differ or are missing.
- Digest regions, Survey-visible tiles, Atlas hints, Apple exposure, model memory, and raw graph rows must not create non-candidate route items.

## Enforced Requirements

- candidate object_type is track or album
- track candidates reference canonical song_recording objects
- album candidates reference canonical album objects
- artist_level_candidate is false
- playable_route_ready is true
- credited_artist is present
- music_kit_search_hint is present
- source_evidence_refs are present
- route_candidate_key is present and unique in the export
- route_batch_dedupe_key is present and unique in the export
- app_route_item_id is present and unique in the export
- route_display_identity_key is present and unique in the export
- route_item carries the same candidate_id, app_route_item_id, route_candidate_key, route_batch_dedupe_key, and route_display_identity_key
- waypoints pool is non-empty
- dead_end_checks pool is non-empty
- quarantined and manual-review rows are excluded

## Remaining Boundary

MusicKit catalog resolution is still required before playback.

The graph candidate pool still does not create Atlas promotion. Mission Generation must copy candidate identity fields and validate rich mission output plus Core `mission.v0.2` before returning `status = app_import_candidate`.
