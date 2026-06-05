# TestFlight Build 52 Regenerate Missions Upload Report - 2026-06-04

## Summary

Uploaded Cartenza iOS alpha `0.3 (52)` for internal TestFlight review.

This build adds a manual mission-regeneration control on both Mission and Account surfaces. The action sends the saved Survey evidence through the configured Cartenza mission-generation client and replaces the reviewed mission batch only after a new batch imports successfully.

## App Changes

- Added `regenerateMissionBatchFromCurrentSurvey()` to `AppModel`.
- Added a reusable Mission regeneration panel to the Mission screen and Account support section.
- Regeneration uses persisted Survey evidence, current Supabase mission-generation configuration, and existing mission import gates.
- Existing mission assignments remain in place if generation fails before replacement.
- A successful replacement clears local mission-session progress and selects the first regenerated mission.

## Validation

- `git diff --check` passed.
- Focused XCTest pass succeeded:
  - `SurveyTests`
  - `AtlasHomeReadoutTests`
  - `AtlasExplainerTests`
  - `MissionDecodingTests`
- New coverage: `MissionDecodingTests.testAppModelRegeneratesMissionsFromCurrentSurveyThroughMissionClient`.
- Archive metadata verified:
  - Bundle ID: `com.vytisstudios.MusicAtlasController`
  - Version: `0.3`
  - Build: `52`

## Upload Notes

`xcrun altool` failed with `NSPOSIXErrorDomain Code=17 "File exists"` for both `--upload-app` and `--upload-package`, including a fresh temp directory. Plain `curl` App Store Connect API calls succeeded, so the IPA was uploaded through the App Store Connect Build Upload API.

Build upload result:

- Build: `0.3 (52)`
- App Store Connect build ID: `7ca3fb4b-216f-4ad1-ad8b-82e807f031bd`
- Uploaded date: `2026-06-04T16:35:56-07:00`
- Processing state: `VALID`
- Audience: `INTERNAL_ONLY`
- Non-exempt encryption: `false`

No Supabase Edge Function deploy was performed in this app-build lane; the regeneration control uses the currently configured remote mission-generation endpoint at runtime.
