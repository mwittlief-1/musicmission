# Apple Music Recording Hardening Pass v1

Generated: 2026-05-29T00:05:31.573Z

Status: `complete`

Storefront: `us`

## Policy

- Raw Apple payloads persisted: `false`
- Apple catalog requests are transient song searches only.
- Durable output stores Apple catalog IDs, resource type, storefront, source refs, and compact match metadata only.
- Apple track names, album names, artist names from search responses, artwork, previews, lyrics, and Music User Tokens are not persisted.

## Acceptance Rule

This pass targets residual `graph_recording` rows. It accepts only strong recording identity evidence:

- exact/core/compact title plus exact primary artist
- exact/core/compact title plus multi-participant overlap for cast/collaboration recordings
- compatible title only when supported by artist and soundtrack/cast context

It defers tribute, cover, karaoke, arrangement, dub/remix mismatch, and weak title/artist evidence.

## Counts

- Jobs considered: 102
- New links total: 81
- Deferred rows: 21

## New Links By Match Basis

| key | count |
| --- | ---: |
| recording_hardening_exact_title_primary_artist_exact_auto_match | 53 |
| recording_hardening_compatible_title_context_auto_match | 14 |
| recording_hardening_exact_title_participant_overlap_auto_match | 9 |
| recording_hardening_core_title_primary_artist_exact_auto_match | 4 |
| recording_hardening_compact_title_primary_artist_exact_auto_match | 1 |

## Deferred By Reason

| key | count |
| --- | ---: |
| recording_hardening_no_auto_match | 20 |
| recording_hardening_version_term_needs_review | 1 |
