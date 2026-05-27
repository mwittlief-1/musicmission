# Apple Music Signal Payload v0.2 Migration - 2026-05-25

## Summary

The Alpha app now treats Apple Music intake as a raw `apple_music_signal_payload.v0.2` evidence packet. The app persists the payload with the Survey session, but Survey page construction does not read Apple signal evidence until Survey PM supplies v0.2 adapter/scoring rules.

## Old Behavior Removed

- `MusicLibraryRequest<Artist>()` with `request.limit = 50` no longer feeds Survey evidence.
- Unsorted library album snapshots no longer feed Survey evidence.
- Unsorted library song snapshots no longer feed Survey evidence.
- The old flat `library_artists_sample`, `library_albums_sample`, and `library_songs_sample` fields are not emitted by the v0.2 payload.

If diagnostic markers for those sources are retained, they live under `excluded_or_diagnostic_sources` with:

- `excluded_from_survey_evidence = true`
- `evidence_basis = diagnostic_excluded`
- `source_confidence = diagnostic_excluded`

## Field Mapping

| v0.1 field | v0.2 disposition |
| --- | --- |
| `schema_version = apple_music_signal_probe.v0.1` | `schema_version = apple_music_signal_payload.v0.2` |
| `captured_at` | retained |
| missing `payload_id` | added |
| missing `probe_version` | added as `apple_probe.v0.2` |
| `authorization.music_authorization_status` | retained |
| missing `authorization.subscription_status` | added |
| missing `authorization.token_status` | added |
| global `errors` | replaced by source-scoped `errors` arrays and `authorization.errors` |
| `environment.storefront` | replaced by top-level `storefront` |
| `raw_endpoints` | normalized into source sections; raw endpoint JSON is not persisted as Survey evidence |
| `library_artists_sample` | removed from evidence; diagnostic marker only |
| `library_albums_sample` | replaced by sorted `primary_signal_sources.library_album_library_added` |
| `library_songs_sample` | replaced by sorted song windows |
| `library_playlists_sample` | moved to `context_sources.playlist_contexts` |
| `personal_recommendations` | moved to `primary_signal_sources.personal_recommendations` |

## New Evidence Windows

Artist exposure should later be derived from:

- Replay summary if an app-side access path becomes available
- heavy rotation
- recently played
- sorted library song play count
- sorted library song last played
- sorted library song library added
- sorted library album library added
- playlist contexts and playlist track samples
- personal recommendations
- observed annotations where available
- catalog hydration for identity matching only

## Survey Boundary

`SurveyStore` may persist the v0.2 payload. `AlphaDynamicSurveyPageProvider` intentionally ignores it for page ranking today. This prevents old alphabetical library snapshots from quietly becoming Survey evidence while the Survey PM adapter remains undefined.

## Validation

Validation assets:

- Contract: `data/product_contracts/apple_music_signal_payload_v0_2.md`
- JSON schema: `data/product_contracts/apple_music_signal_payload_v0_2.schema.json`
- Validator: `scripts/validate_apple_music_signal_payload_v0_2.mjs`
- Fixture: `MusicAtlasControllerTests/Fixtures/apple_music_signal_payload_v0_2_sample.json`

The validator fails payloads that place legacy alphabetical snapshots in `primary_signal_sources` or emit `diagnostic_excluded` outside `excluded_or_diagnostic_sources`.
