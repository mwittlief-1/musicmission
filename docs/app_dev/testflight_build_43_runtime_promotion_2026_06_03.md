# TestFlight Build 43 Runtime Promotion

Date: 2026-06-03

Scope: classify the app/runtime files that produced Cartenza v0.3 build 43 and separate them from generated helper artifacts before opening broader alpha testing.

## Production Runtime Slice

Build 43 depends on:

- Xcode project membership and build number updates in `MusicAtlasController.xcodeproj/`.
- Runtime Swift under `MusicAtlasController/Models/`, `MusicAtlasController/Services/`, and `MusicAtlasController/Views/`.
- App bundle config in `MusicAtlasController/Support/Info.plist`.
- App-shipping resources under `MusicAtlasController/Resources/`.
- XCTest coverage and deterministic fixtures under `MusicAtlasControllerTests/`.
- Supabase diagnostic support for `mission_selection_audit` artifacts.

## App-Bundled Resources

These resources are production-track app inputs for build 43:

- `alpha_compact_candidate_pool_alpha_v0.json`
- `alpha_candidate_blocklist_alpha_v0.json`
- `app_import_ready_alpha_uat_fixtures_v0_2.json`
- `approved_alpha_app_import_candidates_v0_2.json`
- `atlas_explainer_render_packs_v0_2_3.json`
- `canonical_albums.json`
- `canonical_apple_music_catalog_index_v1.json`
- `canonical_artists.json`
- `canonical_song_affinity_tags_v0_1.json`
- `canonical_song_recordings.json`
- `schema_mission_v0_2.json`
- `schema_reaction_session_v0_2.json`
- `survey_album_candidates_v0_2.json`
- `survey_artist_candidates_v0_2.json`
- `survey_song_candidates_v0_2.json`

Old personal/sample mission resources are intentionally removed from the app bundle. The sample mission needed by tests now lives in `MusicAtlasControllerTests/Fixtures/`.

## Explicitly Not Promoted In This Slice

- `MusicAtlasController/Services/AlphaSurveyPagePacketProvider.swift` and `MusicAtlasController/Resources/alpha1_required_survey_page_packet_v0_1.json`: present on disk, but not members of the Xcode project and superseded by `AlphaDynamicSurveyPageProvider` for build 43.
- `supabase/functions/generate-first-mission-batch/index.ts`: modified old backend generation path. Leave for a dedicated backend deprecation/review slice.
- `data/canonical_graph/current/apple_music_*_pass_v1/` directories: generated hardening-pass evidence. Promote only specific outputs/manifests in a data-source slice.
- `derived_affinity_substrate_v0_1*/`: generated/helper substrate, not source-of-truth until promoted under documented `data/` paths.

## Remaining Cleanup Queue

1. Review and stage source-of-truth `data/canonical_graph/current/` updates separately from app-bundled resource exports.
2. Decide which Apple Music hardening pass outputs remain audit evidence versus promoted graph source material.
3. Mark or remove unused `AlphaSurveyPagePacketProvider` only after confirming no test, debug, or future fallback path still needs it.
4. Do a dedicated backend slice for deprecated mission-generation code and any remaining Supabase diagnostic migrations/functions.
