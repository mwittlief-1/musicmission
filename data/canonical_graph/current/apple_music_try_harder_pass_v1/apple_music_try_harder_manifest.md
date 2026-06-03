# Apple Music Try Harder Pass v1

Generated: 2026-05-27T23:17:31.392Z

Status: `complete`

Storefront: `us`

## Policy

- Raw Apple payloads persisted: `false`
- Durable output stores Apple catalog IDs, resource type, storefront, source refs, match status, and scoring metadata only.
- Artwork, previews, lyrics, MusicKit content, raw catalog responses, and Music User Tokens are not persisted.

## Intent

This pass avoids manual review by using safer additional context:

- album-scoped Apple Music track relationships for sidecar track IDs
- tracklist overlap for album rows that the first pass deferred
- sidecar-derived Apple track IDs to bridge deferred graph song/recording rows

## Counts

- Prior links total: 14156
- New links total: 19790
- Deferred rows: 2687
- Album search jobs completed cumulative: 492
- Album track jobs completed cumulative: 1607
- Album search jobs completed current invocation: 8
- Album track jobs completed current invocation: 4

## New Links By Source Type

| key | count |
| --- | ---: |
| album_sidecar_track | 17906 |
| album_sidecar_album | 1607 |
| graph_album | 277 |

## New Links By Match Basis

| key | count |
| --- | ---: |
| album_track_try_harder_position_title_duration_auto_match | 15554 |
| album_sidecar_inherited_graph_album_apple_album_search_title_artist_year_auto_match | 1324 |
| album_track_try_harder_position_duration_auto_match | 1198 |
| album_track_try_harder_position_title_core_duration_auto_match | 929 |
| album_sidecar_try_harder_inherited_graph_album_tracklist_match | 277 |
| album_try_harder_search_tracklist_auto_match | 277 |
| album_track_try_harder_position_title_auto_match | 209 |
| album_track_try_harder_position_title_core_auto_match | 16 |
| album_sidecar_inherited_graph_album_apple_album_search_title_artist_auto_match | 6 |

## Deferred By Reason

| key | count |
| --- | ---: |
| album_track_try_harder_no_safe_match | 2472 |
| album_try_harder_no_safe_tracklist_match | 215 |
