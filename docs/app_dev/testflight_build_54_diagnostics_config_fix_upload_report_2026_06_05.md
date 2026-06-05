# TestFlight Build 54 Diagnostics Config Fix Upload Report - 2026-06-05

## Summary

Uploaded Cartenza iOS alpha `0.3 (54)` for internal TestFlight review.

This build supersedes `0.3 (53)` for alpha testing. It contains no app logic changes beyond the Xcode build-number bump from `53` to `54`; the purpose is to repair the release packaging configuration that left the shipped Supabase anon-key fields empty in build 53.

## Root Cause

The support diagnostics index shared from the device showed local support-package generation was still working, including mission-generation request/result artifacts. The remote upload/regenerate path was failing because build `0.3 (53)` was archived without the Supabase anon key injected into the app bundle.

Observed archive metadata:

- Build `0.3 (52)`: `CartenzaSupabaseAnonKey` length `208`; `WaymarkSupabaseAnonKey` length `208`
- Build `0.3 (53)`: `CartenzaSupabaseAnonKey` length `0`; `WaymarkSupabaseAnonKey` length `0`
- Build `0.3 (54)`: `CartenzaSupabaseAnonKey` length `208`; `WaymarkSupabaseAnonKey` length `208`

Build 53 was archived from a temporary packaging path to avoid local extended-attribute signing failures, but that path bypassed the release-local Supabase key injection used by prior archives. Build 54 was archived with the key explicitly present and verified in the archived app plist before export.

## Validation

- Xcode archive succeeded with manual App Store signing:
  - Signing identity: `Apple Distribution: Matt Wittlief (7XQQ46X8QQ)`
  - Provisioning profile: `Cartenza TestFlight App Store`
- Archived app metadata verified:
  - Bundle ID: `com.vytisstudios.MusicAtlasController`
  - Version: `0.3`
  - Build: `54`
  - Supabase project URL present
  - Diagnostic function name: `submit-alpha-diagnostic`
  - Mission-generation function name: `generate-first-mission-batch`
  - Both Supabase anon-key compatibility plist entries present and non-empty
- IPA export succeeded through the existing internal TestFlight export options.
- App Store Connect Build Upload API upload completed.

## Upload Result

- Build: `0.3 (54)`
- App Store Connect build ID: `e7c4448e-f565-481d-8638-f49e57dd8520`
- Build upload file ID: `e67c8c09-58cb-4b66-b8fd-c50e676b31d4`
- Uploaded date: `2026-06-05T06:10:41-07:00`
- Processing state: `VALID`
- Audience: `INTERNAL_ONLY`
- Non-exempt encryption: `false`

Generated local ASC upload artifacts are under `build/TestFlightUpload-0.3.54.diagnostics-config-fix.*.json`. Pre-signed upload URLs were redacted before writing artifacts.
