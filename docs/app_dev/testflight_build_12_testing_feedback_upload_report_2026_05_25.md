# TestFlight Build 12 Testing Feedback Upload Report

Generated: 2026-05-25

## Build

- App: Waymark / `com.vytisstudios.MusicAtlasController`
- Version: `0.2`
- Build: `12`
- Archive: `build/MusicAtlasController-0.2.12.xcarchive`
- TestFlight export options: `build/ExportOptions-TestFlight.plist`
- Upload posture: App Store Connect upload, internal TestFlight only

## Included Alpha Changes

- Survey page selection now receives the actual displayed page history, preventing later pages from repeating items already shown to the tester.
- Artist page one is capped to the required `12` tiles even with dense Apple Music signal matches.
- Current survey pages remain stable after a tap; answering an item no longer reshuffles the active grid.
- Exact rejected artists are suppressed from downstream album and song pages for Alpha intake.
- Song and album subtitles use display artist names instead of normalized internal keys.
- The Survey grid restores the short helper/title copy above the tiles.
- Mission generation skips app-validation failures, including duplicate generated item IDs, and continues trying to complete the `10`-mission Alpha batch.

## Verification

- Targeted `SurveyTests` suite passed after the survey selection fixes.
- Full simulator XCTest suite passed for `MusicAtlasController` on iPhone 17 / iOS 26.5.
- `git diff --check` passed for the touched app/test files.
- Release archive succeeded for build `12`.
- Archived app reports `Waymark` / version `0.2` / build `12`.
- Archived app has Supabase generation, evidence, and diagnostic function names present.
- Archived app contains schema/canonical/survey support JSON only; no bundled prebuilt mission pack was found.
- App Store Connect upload succeeded; Apple reported the uploaded package is processing.

## Next Smoke

After build `12` finishes processing in App Store Connect/TestFlight:

1. Install build `12` from TestFlight.
2. Confirm artist page one renders exactly `12` tiles with helper copy above the grid.
3. Tap artist page three/four items and confirm the grid does not reshuffle.
4. Confirm artist pages do not repeat prior artist tiles.
5. Dislike a clearly named artist and confirm exact albums/songs by that artist do not appear later.
6. Confirm song subtitles show display names such as `Dolly Parton`, not internal normalized keys.
7. Complete Survey and confirm mission generation progresses past any rejected/generated-invalid attempt toward `10` missions.
