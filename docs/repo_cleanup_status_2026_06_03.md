# Repo Cleanup Status - 2026-06-03

Scope: production-track cleanup checkpoint after the Cartenza v0.3 build 43 Survey policy upload.

This is a stewardship note, not a deletion plan. The worktree contains staged and unstaged runtime changes from active alpha development. Do not move, revert, or delete app/runtime files from this checkpoint without a focused runtime validation pass.

## Current Posture

- Build 43 is the current TestFlight production-track alpha surface.
- The app runtime surface is active in `MusicAtlasController/`, `MusicAtlasControllerTests/`, and `MusicAtlasController.xcodeproj/`.
- The Canonical Graph, Apple Music catalog index, album sidecar, Survey candidate resources, and song affinity tag sidecar are production-track data inputs when they are bundled under `MusicAtlasController/Resources/`.
- `data/canonical_graph/current/` is the source-of-truth graph corpus behind those bundled resources.
- `data/product_contracts/` holds accepted or candidate product/technical contracts and should remain visible.
- `build/`, `review_packets/`, local diagnostics, local exports, and timestamped generated pass directories remain local/generated unless explicitly promoted.

## Production-Track Runtime Surface

These paths should be treated as production-track alpha code or app-shipping resources:

| Path | Classification | Stewardship action |
| --- | --- | --- |
| `MusicAtlasController.xcodeproj/` | Runtime source | Keep build number, resource membership, and signing changes with the app runtime slice that needed them. |
| `MusicAtlasController/Models/` | Runtime source | Track model changes with the feature or data contract that requires them. |
| `MusicAtlasController/Services/` | Runtime source | Active services include MusicKit probing, canonical catalog lookup, Survey generation, persistence, export, mission loading, and Atlas explainer loading. |
| `MusicAtlasController/Views/` | Runtime source | Active app UI surfaces. Keep branding/user-facing copy aligned to Cartenza. |
| `MusicAtlasController/Resources/` | Runtime app resources | Only app-shipping JSON/assets belong here. Each generated JSON should have an upstream source or manifest under `data/`. |
| `MusicAtlasControllerTests/` | Test/source fixture | Keep focused tests with the runtime behavior they protect. |
| `supabase/functions/submit-alpha-diagnostic/` | Runtime backend | Active diagnostic upload path for alpha support. |
| `supabase/migrations/` | Runtime backend | Track migrations only when they are intended for the alpha backend. |

## Production-Track App Resources

Current resource classes that belong in `MusicAtlasController/Resources/` when intentionally wired:

- `canonical_artists.json`, `canonical_albums.json`, and `canonical_song_recordings.json`: app-facing Canonical Graph resource exports.
- `canonical_apple_music_catalog_index_v1.json`: app-facing Apple Music resolution index.
- `canonical_song_affinity_tags_v0_1.json`: app-facing song tag sidecar for Survey song selection.
- `survey_artist_candidates_v0_2.json`, `survey_album_candidates_v0_2.json`, and `survey_song_candidates_v0_2.json`: compatibility/debug priors, not the full Survey eligibility ceiling.
- `alpha_compact_candidate_pool_alpha_v0.json` and blocklist resources: alpha graph/mission candidate support inputs.
- `atlas_explainer_render_packs_v0_2_3.json`: approved Atlas explainer render-pack input.
- `schema_mission_v0_2.json` and `schema_reaction_session_v0_2.json`: runtime/schema compatibility resources while consumers still reference v0.2.

When adding or updating any resource here, update the source manifest or promotion note in `data/` and keep the Xcode project resource membership in the same runtime slice.

## Legacy Or Deprecated Product Paths

These are not deletion instructions. They are guardrails to prevent old alpha behavior from silently returning.

| Surface | Status | Guardrail |
| --- | --- | --- |
| Legacy Waymark names | Compatibility legacy | Keep schema IDs, env vars, package names, persisted keys, and historical filenames until a dedicated migration updates consumers and tests. |
| Old bundled personal/sample mission fixtures | Deprecated runtime inputs | Do not restore deleted personal/sample mission resources into the production app bundle. If a historical fixture is needed, keep it under `data/deprecated_mission_fixtures/` or a test fixture path. |
| Supabase/OpenAI first-mission generation as app launch path | Deprecated for current alpha mission creation | Do not wire the app back to dynamic runtime LLM mission generation. Current alpha mission work should use the approved deterministic graph/Survey/mission-selection contracts unless the owner explicitly reopens the backend path. |
| Legacy `survey_*_candidates_v*.json` surfaces | Compatibility/debug priors | These files may seed or debug Survey behavior, but active canonical graph objects with Apple Music resolution are eligible beyond these lists. |
| Founder-specific taste packets or personal missions | Forbidden runtime/demo data | Do not ship, seed, screenshot, or use founder-specific taste data for outside alpha testers. |

## Generated, Helper, Or Archive Surfaces

These paths should stay ignored/local or be represented by a small manifest unless promoted:

| Path | Classification | Action |
| --- | --- | --- |
| `build/` | Local build/cache output | Keep local only. Delete archives only after dSYM/archive retention is confirmed elsewhere. |
| `review_packets/` | Generated review/archive packets | Keep ignored. Promote selected Markdown summaries into `docs/reviews/` only when accepted as evidence. |
| `data/**/*.zip` | Candidate for external/archive storage | Keep external or manifest-only unless explicitly accepted. |
| `derived_affinity_substrate_v0_1*/` | Generated/helper substrate | Do not treat as source-of-truth until promoted under `data/product_contracts/` or `data/canonical_graph/` with a manifest. |
| `data/canonical_graph/current/apple_music_*_pass_v1/` | Generated hardening pass evidence | Keep as review/audit evidence unless a specific output is promoted into the current graph or app resources. |
| `MusicAtlasController/Resources/Assets.xcassets/AppIcon.appiconset/* 2.png` | Local Finder duplicate app icon assets | Ignore and do not commit. The canonical icon filenames are the non-duplicate files referenced by `Contents.json`. |
| `tmp/` | Local scratch | Ignore and do not commit. |

## Recommended Cleanup Sequence

1. Stabilize and commit the current production-track runtime slice separately from repo cleanup.
2. In that runtime slice, stage only the app files, app resources, tests, source manifests, and scripts that produced build 43 behavior.
3. In a separate data-promotion slice, review `data/canonical_graph/current/`, Apple Music pass outputs, album sidecar updates, and derived affinity artifacts for source-of-truth versus generated evidence.
4. In a deprecation slice, add explicit code comments or docs references only where old paths remain callable and could accidentally be reintroduced.
5. In a generated-artifact slice, replace bulky review packets with manifests or external archive pointers.

## Stop Conditions

Stop before acting when:

- A file is app-shipping and its Xcode resource membership is unclear.
- A data artifact could be canonical graph source-of-truth or merely pass evidence.
- A legacy Waymark identifier might be read by persisted state, Supabase config, a schema, or a test fixture.
- A build archive/dSYM might be needed for TestFlight crash symbolication.
