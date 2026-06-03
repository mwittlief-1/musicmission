# App Resources

This folder contains app-bundled resources for the Cartenza iOS alpha. A file belongs here only when the app or tests intentionally need it in the bundle.

## Production-Track Resources

- Canonical graph app exports: `canonical_artists.json`, `canonical_albums.json`, and `canonical_song_recordings.json`.
- Apple Music resolution support: `canonical_apple_music_catalog_index_v1.json`.
- Survey support: `canonical_song_affinity_tags_v0_1.json`, `survey_artist_candidates_v0_2.json`, `survey_album_candidates_v0_2.json`, and `survey_song_candidates_v0_2.json`.
- Alpha candidate support: `alpha_compact_candidate_pool_alpha_v0.json`, `alpha_candidate_blocklist_alpha_v0.json`, and related approved alpha candidate payloads.
- Atlas Explainer support: `atlas_explainer_render_packs_v0_2_3.json`.
- Compatibility schemas: `schema_mission_v0_2.json` and `schema_reaction_session_v0_2.json`.
- Runtime assets referenced by asset catalogs, such as the app icon set.

## Source Tracking

Generated JSON in this folder should have an upstream source, promotion note, or manifest under `data/`. Keep the upstream material and the app-bundled export in the same runtime/data-promotion slice when possible.

## Deprecated Or Local-Only

- Old personal or sample mission fixtures should not be restored into the production app bundle. Keep historical copies under `data/deprecated_mission_fixtures/` or test fixtures if they are still needed.
- Finder duplicate icon files such as `Icon-60@3x 2.png` are local artifacts and ignored by `.gitignore`.
- Do not drop raw diagnostics, review packets, build exports, or local Apple payload captures into this folder.
