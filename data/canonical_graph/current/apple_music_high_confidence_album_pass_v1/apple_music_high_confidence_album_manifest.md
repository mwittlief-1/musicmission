# Apple Music High Confidence Album Pass v1

Generated: 2026-05-28T04:25:17.112Z

Status: `complete`

Storefront: `us`

## Policy

- Raw Apple payloads persisted: `false`
- Apple album and album track payloads are used only as transient candidate pools.
- Durable output stores Apple catalog IDs, resource type, storefront, source refs, match status, and compact matching metadata only.

## Intent

This pass targets graph albums still missing Apple album IDs after the conservative search, variant, offline, and artist-album passes. It deliberately accepts high-confidence remaster, expanded, censored-title, live-title, and alternate-title matches when title normalization and/or tracklist evidence is strong. For soundtrack, cast, and Various Artists-style album containers, album artist name mismatch is not treated as a blocker when title and tracklist evidence are strong.

## Counts

- Album jobs completed: 144
- New links total: 501
- Deferred rows: 104

## New Links By Source Type

| key | count |
| --- | ---: |
| album_sidecar_track | 421 |
| album_sidecar_album | 40 |
| graph_album | 40 |

## New Links By Match Basis

| key | count |
| --- | ---: |
| high_confidence_album_track_auto_match | 421 |
| high_confidence_title_tracklist_auto_match | 34 |
| high_confidence_curated_seed_tracklist_auto_match | 20 |
| high_confidence_alternate_title_tracklist_auto_match | 12 |
| high_confidence_title_variant_tracklist_auto_match | 6 |
| high_confidence_soundtrack_title_tracklist_auto_match | 6 |
| high_confidence_edition_variant_tracklist_auto_match | 2 |

## Album Links By Edition Class

| key | count |
| --- | ---: |
| original_like | 56 |
| expanded | 14 |
| remaster | 10 |

## Deferred By Reason

| key | count |
| --- | ---: |
| high_confidence_album_no_safe_match | 104 |
