# Apple Music Direct Song Hardening Pass v1

Generated: 2026-05-28T20:38:56.363Z

Status: `complete`

Storefront: `us`

Source scope: `songs`

## Policy

- Raw Apple payloads persisted: `false`
- Apple catalog requests are transient song searches only.
- Durable output stores Apple catalog IDs, resource type, storefront, source refs, and compact matching metadata only.
- Apple track names, album names, artist names from search responses, artwork, previews, lyrics, and Music User Tokens are not persisted.

## Acceptance Rule

This pass encodes the review calibration that medium/high direct song candidates are acceptable when the identity evidence is title/artist strong:

- exact normalized title + exact normalized artist
- edition-stripped core title + exact normalized artist
- exact/core title + compatible artist only with tight release-year support

Obvious mix/live/cover/demo/karaoke/instrumental/remix version terms stay deferred.

## Counts

- Jobs considered: 863
- New links total: 553
- Deferred rows: 310

## New Links By Match Basis

| key | count |
| --- | ---: |
| direct_song_hardening_exact_title_artist_auto_match | 470 |
| direct_song_hardening_core_title_artist_year_auto_match | 46 |
| direct_song_hardening_exact_title_compatible_artist_year_auto_match | 23 |
| direct_song_hardening_core_title_artist_auto_match | 11 |
| direct_song_hardening_core_title_compatible_artist_year_auto_match | 3 |

## Deferred By Reason

| key | count |
| --- | ---: |
| direct_song_search_no_auto_match | 284 |
| direct_song_search_no_results | 15 |
| direct_song_search_version_term_needs_review | 11 |
