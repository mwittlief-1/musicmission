# Apple Music Offline Reconciliation Pass v1

Generated: 2026-05-28T01:24:21.720Z

Status: `complete`

Storefront: `us`

## Policy

- Raw Apple payloads persisted: `false`
- No Apple API calls are made by this pass.
- Durable output stores Apple catalog IDs, resource type, storefront, source refs, match status, and matching metadata only.

## Intent

This pass reconciles first-pass graph song/recording review rows against album-sidecar tracks that already received Apple song IDs in prior passes.

## Counts

- Sidecar track candidates with Apple IDs: 23403
- Graph song/recording review rows considered: 1198
- New links total: 143
- Deferred rows: 1055

## New Links By Match Basis

| key | count |
| --- | ---: |
| offline_sidecar_exact_title_effective_artist_year | 138 |
| offline_sidecar_exact_title_compatible_artist_year | 5 |

## Links By Prior Review Reason

| key | count |
| --- | ---: |
| apple_song_search_no_auto_match | 84 |
| apple_song_search_needs_review_version_risk | 36 |
| apple_song_search_no_results | 23 |

## Deferred By Reason

| key | count |
| --- | ---: |
| offline_sidecar_no_unique_track_match | 1054 |
| offline_sidecar_ambiguous_track_match | 1 |
