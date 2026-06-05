# TestFlight Build 47 Atlas Home Groups Upload Report

Date: 2026-06-03

## Build

- App version: `0.3`
- Build number: `47`
- Bundle ID: `com.vytisstudios.MusicAtlasController`
- Upload status: uploaded successfully; App Store Connect reported the package is processing.

## Changes In This Build

- Groups Atlas Home archetype explainers into `Likely Regions`, `Frontiers`, and `Open Questions`.
- Caps the Atlas Home archetype explainer surface at 10 cards.
- Uses persisted Survey-scored archetypes when available, with deterministic Alpha fallback when no score exists.
- Keeps the approved `What We're Seeing So Far` Atlas Home readout in place.

## Verification

- Passed focused XCTest for `MusicAtlasControllerTests/AtlasExplainerTests`.
- Passed focused XCTest for `MusicAtlasControllerTests/AtlasHomeReadoutTests`.
- Verified project/plist lint and `git diff --check` for touched paths.
- Archive succeeded at `build/MusicAtlasController-0.3.47.atlas-home-groups.xcarchive`.
- TestFlight upload succeeded through `xcodebuild -exportArchive` with App Store Connect API-key auth.

## Packaging Note

- Added an app-target packaging phase to strip extended attributes from the generated app bundle before codesign.
- Set `ENABLE_USER_SCRIPT_SANDBOXING = NO` on the app target so that packaging phase can clean the bundle path used by codesign.

## Scope Notes

- No mission selection implementation.
- No mission context implementation.
- No post-mission learning summaries.
- No runtime model generation for Atlas Home.
