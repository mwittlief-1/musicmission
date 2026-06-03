# Apple Music Graph Song Iterative Hardening Pass v1

Generated: 2026-05-29T03:56:14.799Z

Status: `complete`

Storefront: `us`

## Policy

- Raw Apple payloads persisted: `false`
- Apple catalog requests are sparse and transient: `sparse_album_tracks_and_song_search_transient_only`
- Durable output stores Apple catalog IDs, resource type, storefront, source refs, and compact matching metadata only.
- Apple track names/artists/albums fetched for matching are not written to output artifacts.

## Intent

This pass targets currently unresolved `graph_song` rows after the prior Apple Music song passes.

It runs two stages:

1. Album sidecar tracks that already have Apple song IDs from any current pass.
2. Sparse track listings fetched transiently from already-resolved graph album and graph replacement album IDs.
3. Direct Apple Music song search with stronger title normalization, artist alias handling, compilation tolerance, and soundtrack/cast/score leniency.

## Counts

- Graph song rows before pass: 269
- Graph song rows considered: 269
- Sidecar track candidates with Apple IDs: 4220
- Resolved album contexts: 4237
- Resolved album IDs fetched: 2120
- Transient resolved-album track candidates: 57298
- New links total: 90
- Deferred rows: 179

## New Links By Candidate Source

| key | count |
| --- | ---: |
| direct_catalog_song_search | 65 |
| resolved_graph_album_track | 22 |
| linked_sidecar_track | 3 |

## New Links By Match Basis

| key | count |
| --- | ---: |
| iterative_song_hardening_core_title_primary_artist_exact_auto_match | 51 |
| song_source_album_resolved_graph_album_track_core_title_artist_context_year | 14 |
| iterative_song_hardening_compatible_title_context_auto_match | 5 |
| iterative_song_hardening_exact_title_primary_artist_exact_auto_match | 5 |
| song_source_album_resolved_graph_album_track_core_title_compatible_artist_context_year | 3 |
| song_source_album_resolved_graph_album_track_exact_title_artist_unique_no_year | 3 |
| song_source_album_linked_sidecar_track_core_title_artist_context_year | 2 |
| song_source_album_resolved_graph_album_track_exact_title_artist_context_year | 1 |
| song_source_album_linked_sidecar_track_core_title_compatible_artist_context_year | 1 |
| iterative_song_hardening_core_title_participant_overlap_auto_match | 1 |
| iterative_song_hardening_exact_title_soundtrack_cast_context_auto_match | 1 |
| song_source_album_resolved_graph_album_track_exact_title_compatible_artist_unique_no_year | 1 |
| iterative_song_hardening_exact_title_participant_overlap_auto_match | 1 |
| iterative_song_hardening_compact_title_primary_artist_exact_auto_match | 1 |

## Deferred By Reason

| key | count |
| --- | ---: |
| iterative_song_hardening_no_auto_match | 119 |
| iterative_song_hardening_version_term_needs_review | 26 |
| iterative_song_hardening_ambiguous_close_candidate | 18 |
| iterative_song_hardening_no_results | 13 |
| iterative_song_hardening_context_term_needs_review | 3 |
