# Apple Music Song Source Album Reconciliation Pass v1

Generated: 2026-05-29T03:54:50.256Z

Status: `complete`

Storefront: `us`

## Policy

- Raw Apple payloads persisted: `false`
- Apple catalog requests are sparse and transient: `sparse_album_tracks_transient_only`
- Durable output stores Apple catalog IDs, resource type, storefront, source refs, and compact matching metadata only.
- Apple track names/artists fetched for matching are not written to output artifacts.

## Intent

This pass reconciles unresolved first-pass graph song/recording rows against two album-backed sources:

1. Album sidecar tracks that already have Apple song IDs from any current pass.
2. Sparse track listings fetched transiently from already-resolved graph album and graph replacement album IDs.

## Counts

- Graph song/recording review rows considered: 289
- Sidecar track candidates with Apple IDs: 4220
- Resolved album contexts: 4237
- Resolved album IDs fetched: 2120
- Transient resolved-album track candidates: 57298
- New links total: 80
- Deferred rows: 209

## New Links By Candidate Source

| key | count |
| --- | ---: |
| resolved_graph_album_track | 63 |
| linked_sidecar_track | 13 |
| resolved_graph_replacement_album_track | 4 |

## New Links By Match Basis

| key | count |
| --- | ---: |
| song_source_album_resolved_graph_album_track_exact_title_artist_context_year | 22 |
| song_source_album_resolved_graph_album_track_exact_title_artist_unique_no_year | 20 |
| song_source_album_resolved_graph_album_track_exact_title_compatible_artist_context_year | 15 |
| song_source_album_linked_sidecar_track_exact_title_artist_context_year | 9 |
| song_source_album_resolved_graph_album_track_exact_title_compatible_artist_unique_no_year | 6 |
| song_source_album_linked_sidecar_track_exact_title_artist_unique_no_year | 3 |
| song_source_album_resolved_graph_replacement_album_track_exact_title_artist_unique_no_year | 3 |
| song_source_album_resolved_graph_replacement_album_track_exact_title_artist_context_year | 1 |
| song_source_album_linked_sidecar_track_exact_title_compatible_artist_unique_no_year | 1 |

## Deferred By Reason

| key | count |
| --- | ---: |
| song_source_album_no_unique_track_match | 208 |
| song_source_album_ambiguous_track_match | 1 |
