# Apple Music Signal Payload v0.2

Status: frozen for Alpha raw Apple intake alignment, 2026-05-25.

## Purpose

`apple_music_signal_payload.v0.2` is a raw Apple Music evidence packet captured by the iOS app before Survey continues. It is not a Survey page-selection contract, not Atlas truth, and not mission-generation input by itself.

The packet exists so Product, Survey, Atlas, and Core can audit what the app actually received from Apple Music and later define explicit adapters from raw exposure evidence into Survey or Atlas candidates.

## Doctrine

- Capture source-scoped evidence, not inferred taste.
- Preserve every observed resource with `evidence_basis`, `source_confidence`, and stable identity fields.
- Do not use unsorted alphabetical library artist/album/song snapshots as Survey evidence.
- Treat `catalog_hydration` as identity support only.
- Keep probe errors source-scoped.
- Persist the v0.2 payload before Survey continues, but do not use it to rank Survey pages until Survey PM provides v0.2 adapter/scoring rules.

## Top-Level Shape

Required top-level fields:

- `schema_version`: must be `apple_music_signal_payload.v0.2`
- `payload_id`: unique capture identifier
- `probe_version`: must be `apple_probe.v0.2`
- `captured_at`: ISO-8601 timestamp
- `storefront`: Apple storefront when available
- `authorization`: authorization/subscription/token state and auth-scope errors
- `primary_signal_sources`: direct user behavior and library-commitment windows
- `context_sources`: playlist/replay context
- `observed_resource_annotations`: favorites/ratings when available
- `catalog_hydration`: identity-only catalog resource support
- `excluded_or_diagnostic_sources`: array of explicitly excluded support/debug captures

## Primary Signal Sources

Primary sources are the only v0.2 sections eligible for a future Survey adapter:

- `heavy_rotation`, cap 50, `evidence_basis = heavy_rotation`, `source_confidence = ranked_by_apple`
- `recently_played_tracks`, cap 50, `evidence_basis = recently_played`, `source_confidence = explicit_observed`
- `library_song_play_count`, cap 200, `evidence_basis = library_song_play_count`, `source_confidence = library_sorted`
- `library_song_last_played`, cap 100, `evidence_basis = library_song_last_played`, `source_confidence = library_sorted`
- `library_song_library_added`, cap 100, `evidence_basis = library_song_library_added`, `source_confidence = library_sorted`
- `library_album_library_added`, cap 100, `evidence_basis = library_album_library_added`, `source_confidence = library_sorted`
- `personal_recommendations`, cap 50, `evidence_basis = personal_recommendation`, `source_confidence = recommendation_context`

## Context Sources

Context sources may help interpret exposure but must not be treated as preference truth:

- `playlist_contexts`, cap 50
- `playlist_track_samples`, cap 25 per qualifying playlist and 250 total when implemented
- `replay_summary`, unavailable until Core verifies an app-side access path

## Observed Annotations

`observed_resource_annotations` is split into:

- `favorite_resources`
- `rated_resources`

If annotations cannot be captured through the current MusicKit surface, emit empty sections rather than inventing inferred preference.

## Catalog Hydration

`catalog_hydration.resources` contains deduped identity copies for observed resources. These resources must use:

- `evidence_basis = catalog_identity`
- `source_confidence = catalog_identity`

Catalog hydration supports matching only and must not be counted as user evidence.

## Evidence Basis Enum

- `heavy_rotation`
- `recently_played`
- `library_song_play_count`
- `library_song_last_played`
- `library_song_library_added`
- `library_album_library_added`
- `personal_recommendation`
- `playlist_context`
- `playlist_track_sample`
- `replay_summary`
- `favorite_annotation`
- `rating_annotation`
- `catalog_identity`
- `diagnostic_excluded`

## Source Confidence Enum

- `explicit_observed`
- `ranked_by_apple`
- `device_reported`
- `library_sorted`
- `recommendation_context`
- `playlist_context`
- `user_annotation`
- `catalog_identity`
- `diagnostic_excluded`
- `unavailable`

## Exclusions

The following must not appear in `primary_signal_sources` and must not influence Survey construction:

- `library_artists_sample`
- unsorted `library_albums_sample`
- unsorted `library_songs_sample`
- unsorted alphabetical `MusicLibraryRequest<Artist>()`
- unsorted alphabetical `MusicLibraryRequest<Album>()`
- unsorted alphabetical `MusicLibraryRequest<Song>()`

If support diagnostics keep markers for those old snapshots, they must live under `excluded_or_diagnostic_sources`, set `excluded_from_survey_evidence = true`, and use:

- `evidence_basis = diagnostic_excluded`
- `source_confidence = diagnostic_excluded`

## Validation Rules

- The payload must validate against `apple_music_signal_payload_v0_2.schema.json`.
- Every source section has `source_id`, `status`, `cap`, `items`, and `errors`.
- Every evidence item has `source_item_id`, `resource_type`, `display_name`, `evidence_basis`, `source_confidence`, and `observed_source_refs`.
- `diagnostic_excluded` items appear only under `excluded_or_diagnostic_sources`.
- `catalog_identity` items appear only under `catalog_hydration.resources`.
- At least one useful primary source should be captured before Survey continues when Apple Music is authorized.
- Probe errors are attached to the source that failed.
- Encode/decode round trips must be deterministic enough for persisted Survey sessions and diagnostic upload.

## Non-Goals

This contract does not define:

- Survey page construction
- payload-signature scoring
- Atlas promotion
- canonical matching rules
- LLM profile writing
- mission generation
- UI layout or copy
