# Playback-Ready Candidate Pool Report Alpha v0

Generated: 2026-06-01T13:58:21.452Z

Status: `live_generation_recovery_playback_identity_ready_canonical_song_only_apple_resolved`

The canonical grid is the mission-item universe. Anything in the canonical graph with an Apple Music catalog ID is eligible for Survey consideration unless blocklisted. This compact pool is a playback-ready sample/slice, not the graph limit.

## Summary

| metric | count |
| --- | ---: |
| canonical_grid_items | 11710 |
| alpha_available_mission_items | 11497 |
| alpha_survey_eligible_grid_items | 11417 |
| alpha_survey_unavailable_no_apple_id | 291 |
| alpha_blocklisted_grid_rows | 2 |
| playback_candidate_rows_in_universe | 7417 |
| playback_candidate_rows_with_apple_id | 7206 |
| playback_candidate_rows_do_not_use_no_apple_id | 211 |
| compact_pool_candidates | 72 |
| playback_ready_sample_candidates | 72 |
| artist_candidates | 0 |
| track_candidates | 72 |
| album_candidates | 0 |
| apple_music_resolved_track_candidates | 72 |
| do_not_use_no_apple_id_candidates | 0 |
| waypoints | 12 |
| dead_end_checks | 12 |
| default_alpha_mission_eligible | 72 |
| hard_blocked | 0 |
| route_candidate_keys | 72 |
| route_batch_dedupe_keys | 72 |
| app_route_item_ids | 72 |
| route_display_identity_keys | 72 |

## Pool Counts

| pool | total | track | album | apple_music_resolved |
| --- | ---: | ---: | ---: | ---: |
| anchors | 12 | 12 | 0 | 12 |
| bridges | 12 | 12 | 0 | 12 |
| probes | 12 | 12 | 0 | 12 |
| boundary_probes | 12 | 12 | 0 | 12 |
| dead_end_checks | 12 | 12 | 0 | 12 |
| waypoints | 12 | 12 | 0 | 12 |

## Enforced Rules

- full canonical grid is available as the mission-item universe
- any canonical grid item with an Apple Music catalog ID is eligible for Survey consideration unless blocklisted
- compact pool is a playback-ready sample/slice, not the universe
- candidate object_type is track for this early Alpha sample pool
- track candidates reference canonical song_recording objects
- Apple Music catalog ID is present for every sample playback track
- do_not_use_no_apple_id rows are excluded from sample playback pool
- alpha blocklisted rows are retained in the universe but unavailable for product surfaces

## Remaining Boundary

- survey_selection: Survey may expand/adapt from canonical grid items with Apple IDs; curated survey files are approved defaults, not the full eligibility ceiling.
- music_kit_catalog_resolution: catalog IDs are present for sample playback items; app/Core still owns authorization/playback validation against MusicKit runtime responses
- atlas_promotion: not created by graph candidate pool or mission universe
- no_apple_id_status: unmatched graph items remain canonical/QA-visible but unavailable for Survey/playback until resolver work clears them
