# Apple Music Album Variant Pass v1

Generated: 2026-05-28T01:24:04.495Z

Status: `complete`

Storefront: `us`

## Policy

- Raw Apple payloads persisted: `false`
- Apple requests use sparse album and song fields for transient matching.
- Durable output stores Apple catalog IDs, resource type, storefront, source refs, match status, and matching metadata only.

## Intent

This pass targets albums still missing Apple album IDs after the earlier passes, with specific handling for remastered editions, compilation title mismatches, and source titles that include the artist name.

## Counts

- Album jobs completed: 215
- New links total: 685
- Deferred rows: 178

## New Links By Source Type

| key | count |
| --- | ---: |
| album_sidecar_track | 611 |
| album_sidecar_album | 37 |
| graph_album | 37 |

## New Links By Match Basis

| key | count |
| --- | ---: |
| album_variant_track_auto_match | 611 |
| album_variant_remaster_or_title_core_tracklist_auto_match | 54 |
| album_variant_artist_name_stripped_title_auto_match | 18 |
| album_variant_compilation_tracklist_auto_match | 2 |

## Deferred By Reason

| key | count |
| --- | ---: |
| album_variant_no_safe_match | 178 |
