# TestFlight Build 55 Local Regeneration Upload Report - 2026-06-05

## Summary

Uploaded Cartenza iOS alpha `0.3 (55)` for internal TestFlight review.

This build supersedes `0.3 (54)` for alpha testing. It restores the manual Regenerate Missions path to the deterministic Survey/Atlas opportunity selector and documents the legacy full OpenAI mission-generation path as deprecated for production-alpha mission creation.

## Runtime Change

- `Regenerate Missions` now reads saved Survey evidence, runs the local deterministic Survey/Atlas opportunity selector, validates a six-mission import preview, and only then replaces the current reviewed mission batch.
- The regenerate path no longer requires Supabase generation configuration, no longer asks for a generation access token, and no longer calls `generate-first-mission-batch`.
- The legacy `supabase/functions/generate-first-mission-batch` path remains in the repo for possible backend review/replay, but is not the app launch or manual regeneration path.

## Expected Latency

Based on simulator tests for this specific restored deterministic path:

- Focused regeneration test: `33.645s` on the earlier run.
- Focused regeneration retest after cleanup: `51.199s`.
- Full `MissionDecodingTests` class run: local regeneration test case `53.684s`.

Expected manual regeneration latency for the deterministic selector is therefore roughly `35-55s` for the full six-mission batch on the current simulator/test machine. This is local app/data processing, not OpenAI or Supabase generation latency.

Mission Enrichment v0.2 is a separate overlay contract. Earlier live OpenAI enrichment tests were roughly `41-52s` per mission in the final four-call run, so six serial enrichment calls would still be minutes unless the runtime batches or parallelizes them.

## Validation

- `git diff --check`: pass
- Focused XCTest:
  - `MissionDecodingTests.testAppModelRegeneratesMissionsFromCurrentSurveyWithLocalSelector`: pass
- Full mission/import XCTest class:
  - `MusicAtlasControllerTests/MissionDecodingTests`: pass
- Release archive succeeded with manual App Store signing:
  - Signing identity: `Apple Distribution: Matt Wittlief (7XQQ46X8QQ)`
  - Provisioning profile: `Cartenza TestFlight App Store`
- Archived app metadata verified:
  - Bundle ID: `com.vytisstudios.MusicAtlasController`
  - Version: `0.3`
  - Build: `55`
  - Supabase project URL present
  - Diagnostic function name: `submit-alpha-diagnostic`
  - Both Supabase anon-key compatibility plist entries present and non-empty
  - No old sample/personal mission JSON files found in the app bundle
- IPA export succeeded through the existing internal TestFlight export options.
- App Store Connect Build Upload API upload completed.

## Upload Result

- Build: `0.3 (55)`
- App Store Connect build/upload ID: `8e7bbcc4-eb25-4382-9666-894a8dd57f1e`
- Build upload file ID: `911e301b-e44c-48ef-8bf3-66571dfa1eea`
- Processing state: `VALID`
- Upload state: `COMPLETE`
- Audience: `INTERNAL_ONLY`

Generated local ASC upload artifacts are under `build/TestFlightUpload-0.3.55.local-regeneration.*`. Pre-signed upload URLs were redacted before writing persisted ASC response artifacts.
