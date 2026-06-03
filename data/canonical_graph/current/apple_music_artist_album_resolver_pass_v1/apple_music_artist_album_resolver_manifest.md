# Apple Music Artist Album Resolver Pass v1

Generated: 2026-05-28T03:01:45.524Z

Status: `complete`

Storefront: `us`

## Policy

- Raw Apple payloads persisted: `false`
- Apple artist album and album track payloads are used only as transient candidate pools.
- Durable output stores Apple catalog IDs, resource type, storefront, source refs, match status, and matching metadata only.

## Intent

This pass targets graph albums still missing Apple album IDs after prior album search and album-variant passes. It scopes candidate albums by resolved Apple artist IDs, prefers original-like albums over remasters, and prefers remasters over expanded/deluxe editions when a same-title candidate exists.

## Counts

- Album jobs completed: 178
- New links total: 335
- Deferred rows: 144

## New Links By Source Type

| key | count |
| --- | ---: |
| album_sidecar_track | 267 |
| album_sidecar_album | 34 |
| graph_album | 34 |

## New Links By Match Basis

| key | count |
| --- | ---: |
| artist_album_resolver_track_auto_match | 267 |
| artist_album_list_title_year_auto_match | 34 |
| artist_album_list_title_containment_auto_match | 16 |
| artist_album_list_tracklist_auto_match | 10 |
| artist_album_list_censored_title_tracklist_auto_match | 8 |

## Album Links By Edition Class

| key | count |
| --- | ---: |
| original_like | 38 |
| expanded | 16 |
| remaster | 12 |
| ep | 2 |

## Deferred By Reason

| key | count |
| --- | ---: |
| artist_album_resolver_no_safe_album_match | 137 |
| artist_album_resolver_no_artist_id | 7 |
