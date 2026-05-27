# TestFlight Build 11 Fresh-Read Upload Report

Generated: 2026-05-24

## Build

- App: Waymark / `com.vytisstudios.MusicAtlasController`
- Version: `0.2`
- Build: `11`
- Archive: `build/MusicAtlasController-0.2.11.xcarchive`
- TestFlight export options: `build/ExportOptions-TestFlight.plist`
- Upload posture: App Store Connect upload, internal TestFlight only

## Included Alpha Changes

- Forced a new first-run state version: `alpha1_fresh_read_quarantine_2026_05_24_01`.
- On first launch after update, stale Alpha first-run flags are purged, local Alpha data roots are quarantined, and the Supabase session is signed out.
- Quarantined local roots:
  - Application Support: `MusicAtlasController`
  - Documents exports: `MusicAtlasControllerExports`
- Mission generation no longer auto-retries after a failed generation state on relaunch.
- The generation screen now has a `Start Fresh` escape action.
- The first-run core app gate now requires the full `10`-mission Alpha batch instead of treating one imported mission as complete enough.
- The generation primary action shows `Waiting for 10 Missions` until the batch is complete.

## Verification

- `plutil -lint MusicAtlasController/Support/Info.plist` passed.
- `git diff --check` passed for the touched app/test files.
- Full simulator XCTest suite passed after the fresh-read/quarantine changes.
- Full simulator XCTest suite passed again after the 10-mission gate change.
- Release archive succeeded for build `11`.
- Archived app has `WaymarkSupabaseDiagnosticFunctionName=submit-alpha-diagnostic`.
- Archived app contains schema/canonical/survey support JSON only; no bundled prebuilt mission pack was found.
- App Store Connect upload succeeded; Apple reported the uploaded package is processing.

## Next Smoke

After build `11` finishes processing in App Store Connect/TestFlight:

1. Install build `11` from TestFlight over the current app.
2. Confirm first open starts at Alpha Access, not mission generation.
3. Accept Alpha terms, sign in with Apple, and authorize Apple Music.
4. Complete onboarding and the required Survey intake.
5. Confirm generation attempts toward exactly `10` Alpha missions.
6. Confirm the generation screen shows progress plus Retry / Start Fresh when needed.
7. Confirm the core app unlocks only after the `10`-mission batch is available.
8. Run one mission far enough to create playback/reaction evidence.
9. Upload Support Diagnostics and confirm Supabase diagnostic rows.
