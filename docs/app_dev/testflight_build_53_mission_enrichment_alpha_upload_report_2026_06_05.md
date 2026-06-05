# TestFlight Build 53 Mission Enrichment Alpha Upload Report - 2026-06-05

## Summary

Uploaded Cartenza iOS alpha `0.3 (53)` for internal TestFlight review.

This build packages the current production-alpha app tree after the Mission Enrichment v0.2 alpha-lock work. The IPA includes the current Atlas Home readout and Atlas Explainer v0.3 app resources. Mission Enrichment v0.2 remains a repo-side product contract/data packet in this lane; no Supabase Edge Function deploy was performed as part of this app upload.

## Validation

- `git diff --check` passed.
- Focused XCTest pass succeeded on `iPhone 17 Pro, iOS 26.5`:
  - `SurveyTests`
  - `AtlasHomeReadoutTests`
  - `AtlasExplainerTests`
  - `MissionDecodingTests`
- Mission Enrichment v0.2 fixture contract tests passed:
  - `.venv/bin/python data/product_contracts/mission_enrichment_v0_2/tests/fixture_contract_tests_v0_2.py`
- Supabase mission-generation smoke passed:
  - `npx tsx scripts/smoke_supabase_generate_first_mission_batch.mjs`
  - Result: `SUPABASE_FUNCTION_SMOKE_PASS`
- Archive metadata verified:
  - Bundle ID: `com.vytisstudios.MusicAtlasController`
  - Display name: `Cartenza`
  - Version: `0.3`
  - Build: `53`
  - Minimum iOS: `17.0`
  - Non-exempt encryption: `false`

## Archive And Export Notes

The first signed archive attempt under the repo-local `build/` path failed at CodeSign with `resource fork, Finder information, or similar detritus not allowed`. The staged app and source resource tree were carrying file-provider/provenance extended attributes.

The successful archive was created from a clean temporary build location:

- Archive path: `/private/tmp/cartenza_build_0_3_53_20260604_2145/MusicAtlasController-0.3.53.mission-enrichment-alpha.xcarchive`
- Export path: `/private/tmp/cartenza_build_0_3_53_20260604_2145/TestFlightExport-0.3.53.mission-enrichment-alpha`
- IPA: `/private/tmp/cartenza_build_0_3_53_20260604_2145/TestFlightExport-0.3.53.mission-enrichment-alpha/MusicAtlasController.ipa`

The final archive used `COPYFILE_DISABLE=1` and `/private/tmp` to avoid the file-provider metadata layer. Export succeeded with the existing internal TestFlight App Store Connect export options. Xcode still emitted the known App Store Connect `File exists` configuration warning seen on build 52, so upload was completed through the App Store Connect Build Upload API.

## Upload Result

- Build: `0.3 (53)`
- App Store Connect build ID: `35902aba-9954-4c1f-8d80-1850827a106b`
- Build upload file ID: `f902d9ff-3873-45c8-b21a-4b232d543764`
- Uploaded date: `2026-06-05T03:35:51-07:00`
- Processing state: `VALID`
- Audience: `INTERNAL_ONLY`
- Non-exempt encryption: `false`

Generated ASC upload artifacts are under `build/TestFlightUpload-0.3.53.mission-enrichment-alpha.*.json`. Pre-signed upload URLs were redacted before writing artifacts.
