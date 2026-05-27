# TestFlight Build 10 Upload Report

Generated: 2026-05-24

Status: superseded by build `11`; use `docs/app_dev/testflight_build_11_fresh_read_upload_report_2026_05_24.md` for the next smoke.

## Build

- App: Waymark / `com.vytisstudios.MusicAtlasController`
- Version: `0.2`
- Build: `10`
- Archive: `build/MusicAtlasController-0.2.10.xcarchive`
- TestFlight export options: `build/ExportOptions-TestFlight.plist`
- Upload posture: App Store Connect upload, internal TestFlight only

## Included Alpha Changes

- Manual support diagnostic upload to `submit-alpha-diagnostic`.
- Support Diagnostics remains manual and support-gated.
- Automatic evidence/diagnostic upload remains disabled pending final privacy, retention, deletion, and support policy.
- Existing Alpha generation recovery remains in place: app-valid `review_needed` missions may import for trusted Alpha; `blocked` output is still rejected.

## Verification

- Full simulator XCTest suite passed before packaging.
- Release archive succeeded for build `10`.
- Archived app has `WaymarkSupabaseDiagnosticFunctionName=submit-alpha-diagnostic`.
- Archived app has the Supabase publishable key configured.
- Archived app contains schema/canonical/survey support JSON only; no bundled prebuilt mission pack was found.
- App Store Connect upload succeeded; Apple reported the uploaded package is processing.

## Next Smoke

After build `10` finishes processing in App Store Connect/TestFlight:

1. Install build `10` from TestFlight.
2. Sign in with Apple and authorize Apple Music.
3. Complete required onboarding and Survey intake.
4. Confirm generation attempts toward `10` Alpha missions.
5. Enter the core app with imported missions.
6. Open My Account -> Share Evidence Backup.
7. Prepare Support Diagnostics.
8. Upload Diagnostics to Waymark.
9. Confirm `alpha_client_diagnostic_artifacts` rows are present with `user_id_present=true`.
