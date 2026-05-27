# Apple Music Signal Payload v0.2 Alignment Dispatch - 2026-05-25

## Broadcast Note

Send this to Core Waymark Build and Survey Lineage:

```text
Please read docs/alpha_backlog/apple_music_signal_payload_v0_2_alignment_dispatch_2026_05_25.md. The Survey PM spec defines raw Apple Music Signal Payload v0.2 only. Align the Alpha app to capture and persist v0.2 Apple signal evidence, remove unsorted alphabetical library snapshots from Survey evidence, and add validation/fixtures. Do not implement Survey page construction, scoring, Atlas promotion, mission generation, or UI redesign as part of this dispatch.
```

## Owner Lanes

- Primary owner: Core Waymark Build
- Review/support: Survey Lineage
- Support if needed: Canonical Graph / Atlas for identity-field naming only
- Not required unless app upload semantics change: Supabase / Infrastructure

## Source Spec

The controlling product spec is the Survey PM-provided `Apple Music Signal Payload v0.2` dispatch shared on 2026-05-25.

This repo dispatch intentionally narrows implementation to raw Apple intake capture, persistence, fixture/schema validation, and migration. It does not define Survey page construction.

## Current Code Comparison

### Current payload model is v0.1 and flat

Current file: `MusicAtlasController/Models/AppleMusicSignalPayload.swift`

Current top-level model has:

- `schema_version`
- `captured_at`
- `authorization`
- `environment`
- `raw_endpoints`
- `library_artists_sample`
- `library_albums_sample`
- `library_songs_sample`
- `library_playlists_sample`
- `personal_recommendations`
- global `errors`
- `notes`

Missing from v0.2:

- `payload_id`
- `probe_version`
- top-level `storefront`
- `authorization.subscription_status`
- `authorization.token_status`
- source-scoped status/error sections
- `primary_signal_sources`
- `context_sources`
- `observed_resource_annotations`
- `catalog_hydration`
- `excluded_or_diagnostic_sources`
- `evidence_basis`
- `source_confidence`

### Current probe captures excluded alphabetical snapshots

Current file: `MusicAtlasController/Services/AppleMusicSignalProbeService.swift`

Current incompatible behavior:

- `fetchLibraryArtists()` uses `MusicLibraryRequest<Artist>()` with `request.limit = 50`.
- `fetchLibraryAlbums()` uses `MusicLibraryRequest<Album>()` with `request.limit = 50`.
- `fetchLibraryPlaylists()` uses unsorted `MusicLibraryRequest<Playlist>()`.
- `fetchLibrarySongs()` captures only one sorted song window: `playCount`, limit `100`.
- recently played, heavy rotation, and recently added are stored as raw endpoint JSON under `raw_endpoints`, not normalized v0.2 source sections.
- no Replay summary capture.
- no library-song last-played window.
- no library-song recently-added window.
- no library-album recently-added window.
- no playlist track sampling.
- no favorite/rating annotations.
- no catalog hydration list.
- no deterministic validator proving excluded sources cannot feed Survey evidence.

### Current Survey code consumes excluded snapshots

Current file: `MusicAtlasController/Services/AlphaDynamicSurveyPageProvider.swift`

Current incompatible behavior:

- `AlphaAppleEvidenceIndex` gives high artist strength to `payload.libraryArtistsSample`.
- It uses `payload.libraryAlbumsSample` as artist/album strength.
- It uses `payload.librarySongsSample` as song/artist/album strength.
- It uses personal recommendation albums directly.

This violates the v0.2 doctrine because unsorted library artists/albums/songs must not enter Survey evidence. Until the separate Survey page-construction spec lands, Core should persist v0.2 payload without consuming it for Survey page construction, or consume only explicitly allowed v0.2 primary/context sources behind a clearly named adapter.

### Current tests encode the old behavior

Current file: `MusicAtlasControllerTests/SurveyTests.swift`

Current incompatible tests:

- `testArtistPageOneUsesApplePayloadAndCanonicalGraphNotStaticPacket` builds a payload from `libraryArtistsSample` and expects Page 1 to use it.
- helper `makeApplePayload(artists:)` creates v0.1 payloads with `libraryArtistsSample`.

These tests must be migrated to v0.2 fixtures and validator expectations.

## Required Deliverables

- [x] APPLE-V02-001 Create spec markdown.
  - Path: `data/product_contracts/apple_music_signal_payload_v0_2.md` or equivalent.
  - Include product doctrine, source sections, caps, evidence-basis enum, source-confidence enum, exclusions, validation rules, and non-goals.

- [x] APPLE-V02-002 Create JSON schema.
  - Path: `data/product_contracts/apple_music_signal_payload_v0_2.schema.json` or equivalent.
  - Validate top-level shape, source sections, item identity fields, `evidence_basis`, `source_confidence`, caps where practical, and diagnostic-only exclusions.

- [x] APPLE-V02-003 Add Swift v0.2 model.
  - Preferred path: `MusicAtlasController/Models/AppleMusicSignalPayloadV02.swift`.
  - Keep the existing v0.1 type only if needed for migration/backward decode.
  - Include:
    - `schema_version = apple_music_signal_payload.v0.2`
    - `payload_id`
    - `captured_at`
    - `probe_version = apple_probe.v0.2`
    - `storefront`
    - authorization status/subscription/token/probe errors
    - primary signal sources
    - context sources
    - observed annotations
    - catalog hydration
    - excluded/diagnostic sources

- [x] APPLE-V02-004 Add probe v0.2 implementation.
  - Preferred path: `MusicAtlasController/Services/AppleMusicSignalProbeV02.swift`, or update the existing probe with a clearly named v0.2 boundary.
  - Normalize heavy rotation and recently played into v0.2 sections instead of only storing raw JSON.
  - Add sorted library song windows:
    - play-count cap `200`
    - last-played-device cap `100`
    - library-added cap `100`
  - Add library album recently-added window cap `100`.
  - Capture personal recommendations with flattened item cap `50`.
  - Capture playlist contexts cap `50`.
  - Capture playlist track samples only for qualifying playlists, cap `25` per playlist / `250` total.
  - Add Replay summary if available through the app's Apple Music access surface; if unavailable, emit source status `unavailable` with source-scoped errors.
  - Add favorite/rating annotations only for already-observed resources when feasible; otherwise emit source status/empty arrays.
  - Hydrate every unique observed resource enough for catalog matching.

- [x] APPLE-V02-005 Remove unsorted library snapshots from Survey evidence.
  - Delete or disable `MusicLibraryRequest<Artist>()` for Survey evidence.
  - Do not capture unsorted `MusicLibraryRequest<Album>()` as Survey evidence.
  - Do not capture unsorted `MusicLibraryRequest<Song>()` as Survey evidence.
  - If any alphabetical snapshots remain for support diagnostics, place them only in `excluded_or_diagnostic_sources` with `excluded_from_survey_evidence = true` and `evidence_basis = diagnostic_excluded`.

- [x] APPLE-V02-006 Update Survey integration boundary.
  - `SurveyStore` may persist v0.2 payload.
  - `AlphaDynamicSurveyPageProvider` must not read excluded v0.1 fields.
  - Until Survey PM supplies page-construction v0.2 scoring rules, use one of:
    - no Apple boost in Survey construction, while still persisting v0.2 payload, or
    - a small adapter that reads only explicitly allowed v0.2 primary/context signals and marks outputs as exposure priors.
  - Do not implement new Survey page selection logic in this dispatch.

- [x] APPLE-V02-007 Add validator.
  - Preferred path: `scripts/validate_apple_music_signal_payload_v0_2.mjs` or Swift test equivalent.
  - Validator must prove:
    - schema validates
    - every evidence item has `evidence_basis`
    - every non-catalog evidence item has `source_confidence`
    - unsorted library artist/album/song snapshots are absent from `primary_signal_sources`
    - `diagnostic_excluded` items appear only in `excluded_or_diagnostic_sources`
    - `catalog_identity` items are not treated as user evidence
    - every captured resource has stable identity fields
    - at least one useful source is captured before Survey continues
    - probe errors are source-scoped
    - payload persists/replays deterministically

- [x] APPLE-V02-008 Add fixture.
  - Preferred path: `MusicAtlasControllerTests/Fixtures/apple_music_signal_payload_v0_2_sample.json` or `data/fixtures/apple_music_signal_payload_v0_2_sample.json`.
  - Fixture should be generated from mocked Apple responses, not a real tester payload.
  - Include at least one source from:
    - heavy rotation
    - recently played
    - library song play-count
    - library song last-played-device
    - library song library-added
    - library album library-added
    - personal recommendation
    - catalog hydration
    - excluded diagnostic source marker

- [x] APPLE-V02-009 Update tests.
  - Replace v0.1 `libraryArtistsSample` Survey tests with v0.2 validator/persistence tests.
  - Add a negative test proving alphabetical `library_artists_sample` cannot influence Survey evidence.
  - Add deterministic encode/decode test for v0.2 payload.
  - Add Survey flow smoke proving v0.2 payload can be persisted before Survey continues.

- [x] APPLE-V02-010 Add migration note.
  - Preferred path: `docs/app_dev/apple_music_signal_payload_v0_2_migration_2026_05_25.md`.
  - Document old field -> new field decisions.
  - Explicitly call out removed behavior:
    - `MusicLibraryRequest<Artist>() request.limit = 50` as Survey evidence
    - unsorted library album snapshot as Survey evidence
    - unsorted library song snapshot as Survey evidence
  - Explain that artist exposure should later be derived from Replay, heavy rotation, recently played, sorted song windows, sorted album-added windows, playlist samples, recommendations, and annotations.

## Acceptance Criteria

- v0.2 spec markdown exists.
- v0.2 JSON schema exists.
- Swift model or equivalent exists.
- Probe implementation emits `schema_version = apple_music_signal_payload.v0.2`.
- The old 50-library-artist snapshot no longer feeds Survey evidence.
- Sample fixture exists and passes validation.
- Validator fails payloads that place alphabetical library snapshots in primary signal sources.
- Migration note exists.
- Existing Survey flow can persist a v0.2 payload without depending on it for page construction.

## Non-Goals

Do not implement in this dispatch:

- Survey page selection
- payload-signature scoring
- Artist Page 1 changes
- Atlas evidence export changes
- canonical graph matching changes
- Profile Writer prompt changes
- LLM taste assessment
- recommendation logic
- mission generation
- UI redesign

## Open Questions / Blockers

| issue id | blocker | owner lane | needed for | current workaround | status |
| --- | --- | --- | --- | --- | --- |
| `APPLE-V02-I001` | Replay API availability and exact app-side access path may need physical-device/API verification. | Core Waymark Build | Replay summary source implementation. | Emit `replay_summary.status = unavailable` with source-scoped error until verified. | open |
| `APPLE-V02-I002` | Survey PM has not provided v0.2 page-construction/scoring rules. | Survey Lineage / Product | Safe use of v0.2 payload for Survey grids. | Persist v0.2 payload and avoid Apple-derived Survey boosts, or only use explicitly allowed source adapter with tests. | open |

## Completion Note

- status: Core alignment complete for the raw Apple Music Signal Payload v0.2 contract. The app now captures/persists v0.2 raw evidence and Survey construction no longer consumes old v0.1 alphabetical library snapshots.
- files changed: `MusicAtlasController/Models/AppleMusicSignalPayload.swift`, `MusicAtlasController/Services/AppleMusicSignalProbeService.swift`, `MusicAtlasController/Services/AlphaDynamicSurveyPageProvider.swift`, `MusicAtlasController/Views/AppleMusicSignalProbeView.swift`, `MusicAtlasControllerTests/SurveyTests.swift`, `MusicAtlasControllerTests/Fixtures/apple_music_signal_payload_v0_2_sample.json`, `data/product_contracts/apple_music_signal_payload_v0_2.md`, `data/product_contracts/apple_music_signal_payload_v0_2.schema.json`, `scripts/validate_apple_music_signal_payload_v0_2.mjs`, `docs/app_dev/apple_music_signal_payload_v0_2_migration_2026_05_25.md`.
- commands/tests run:
  - `node scripts/validate_apple_music_signal_payload_v0_2.mjs MusicAtlasControllerTests/Fixtures/apple_music_signal_payload_v0_2_sample.json` passed.
  - Negative validator smoke with forbidden `primary_signal_sources.library_artists_sample` failed as expected.
  - `xcodebuild -scheme MusicAtlasController -configuration Debug -sdk iphonesimulator -destination 'generic/platform=iOS Simulator' -derivedDataPath /tmp/musicmission-apple-v02-build build` passed.
  - Full simulator XCTest compile succeeded, but the simulator launch failed with `NSMachErrorDomain Code=-308`; no code compile failure was observed.
- remaining blockers: `APPLE-V02-I001` Replay source access remains unavailable pending Apple/device verification; `APPLE-V02-I002` Survey v0.2 page-construction/scoring rules remain owned by Survey Lineage/Product.
- handoff needed from: Survey Lineage for v0.2 scoring/page-construction rules before any Apple evidence is used to shape Survey pages; Core/Apple-device QA for Replay availability.
