# TestFlight Build 48 Atlas Explainer v0.3 Upload Report

Date: 2026-06-04

## Build

- App version: `0.3`
- Build number: `48`
- Bundle ID: `com.vytisstudios.MusicAtlasController`
- Upload status: uploaded successfully; App Store Connect reported the package is processing.

## Changes In This Build

- Promotes `AtlasExplainerPack_v0_3_ProfileLadders` as the Alpha production Atlas Explainer copy.
- Bundles `atlas_explainer_render_packs_v0_3.json` with 120 v0.3 render packs.
- Preserves v0.2.3 canonical route refs as non-user-facing compatibility keys for existing mission/detail explainer matching.
- Keeps the approved Atlas Home readout and grouped `Likely Regions`, `Frontiers`, and `Open Questions` surface in place.
- Includes the current Survey repetition governors and low-signal Open Questions bucketing.

## Verification

- Passed `git diff --check`.
- Passed focused XCTest for `MusicAtlasControllerTests/SurveyTests`.
- Passed focused XCTest for `MusicAtlasControllerTests/AtlasHomeReadoutTests`.
- Passed focused XCTest for `MusicAtlasControllerTests/AtlasExplainerTests`.
- Verified archive metadata: `CFBundleShortVersionString=0.3`, `CFBundleVersion=48`, bundle ID `com.vytisstudios.MusicAtlasController`.
- Verified archived app contains `atlas_explainer_render_packs_v0_3.json` with `schema_version=0.3`, `source_package=AtlasExplainerPack_v0_3_ProfileLadders`, and 120 packs.
- Archive succeeded at `build/MusicAtlasController-0.3.48.atlas-explainer-v0-3.xcarchive`.
- TestFlight upload succeeded through `xcodebuild -exportArchive` with App Store Connect API-key auth and the manual `Cartenza TestFlight App Store` profile.

## Packaging Note

- The first automatic export attempt hit a cloud-signing profile/certificate mismatch.
- Retried with the existing manual TestFlight export profile and API-key auth; upload succeeded.

## Scope Notes

- No mission selection implementation.
- No mission context implementation.
- No post-mission learning summaries.
- No runtime model generation for Atlas Home or Atlas Explainer copy.
