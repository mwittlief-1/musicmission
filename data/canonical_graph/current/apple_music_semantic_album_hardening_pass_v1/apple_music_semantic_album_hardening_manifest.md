# Apple Music Manual Album Review Pass v1

Generated: 2026-05-28T12:01:50.654Z

Status: `complete`

Storefront: `us`

## Policy

- Raw Apple payloads persisted: `false`
- Apple album and album track payloads are used only as transient validation and sidecar-track candidate pools.
- Durable output stores Apple catalog IDs, resource type, storefront, source refs, manual review provenance, and compact matching metadata only.

## Intent

This pass records an LLM-assisted semantic hardening slice over the remaining graph albums. It accepts same-artist or soundtrack/cast provenance matches whose Apple titles are semantically the same album, while holding out known wrong-band, missing-catalog, and weak compilation substitutes.

## Counts

- Approved albums: 35
- New links total: 188
- Deferred rows: 0

## New Links By Source Type

| key | count |
| --- | ---: |
| album_sidecar_track | 118 |
| album_sidecar_album | 35 |
| graph_album | 35 |

## New Links By Match Basis

| key | count |
| --- | ---: |
| semantic_album_hardening_track_auto_match | 118 |
| semantic_album_hardening_llm_assisted_approved | 70 |
