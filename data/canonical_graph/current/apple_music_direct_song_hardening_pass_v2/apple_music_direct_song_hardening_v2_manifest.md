# Apple Music Direct Song Hardening Pass v2

Generated: 2026-05-28T22:13:54.620Z

Status: `complete`

Storefront: `us`

## Policy

- Raw Apple payloads persisted: `false`
- Apple catalog requests are transient song searches only.
- Durable output stores Apple catalog IDs, resource type, storefront, source refs, and compact match metadata only.
- Apple track names, album names, artist names from search responses, artwork, previews, lyrics, and Music User Tokens are not persisted.

## Acceptance Rule

This pass targets residual graph songs deferred by v1. It adds:

- multi-artist, featured-artist, and compact artist normalization
- title compacting for punctuation/stylization/censored-text differences
- collaboration participant matching when title identity is strong

It still defers obvious live/remix/dub/karaoke/cover/demo/instrumental version traps unless the graph title itself requests that version.

## Counts

- Jobs considered: 310
- New links total: 51
- Deferred rows: 259

## New Links By Match Basis

| key | count |
| --- | ---: |
| direct_song_hardening_v2_exact_title_primary_artist_exact_auto_match | 31 |
| direct_song_hardening_v2_compact_title_primary_artist_exact_auto_match | 9 |
| direct_song_hardening_v2_exact_title_primary_artist_present_in_candidate_participants_auto_match | 8 |
| direct_song_hardening_v2_core_title_primary_artist_exact_auto_match | 1 |
| direct_song_hardening_v2_exact_title_candidate_primary_present_in_expected_participants_auto_match | 1 |
| direct_song_hardening_v2_exact_title_collaboration_participant_auto_match | 1 |

## Deferred By Reason

| key | count |
| --- | ---: |
| direct_song_hardening_v2_no_auto_match | 227 |
| direct_song_hardening_v2_no_results | 15 |
| direct_song_hardening_v2_version_term_needs_review | 10 |
| direct_song_hardening_v2_context_term_needs_review | 7 |
