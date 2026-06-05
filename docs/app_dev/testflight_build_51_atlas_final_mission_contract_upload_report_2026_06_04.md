# TestFlight Build 51 Upload Report

Date: 2026-06-04

## Result

- App: Cartenza
- Bundle ID: `com.vytisstudios.MusicAtlasController`
- Marketing version: `0.3`
- Build: `51`
- Archive: `build/MusicAtlasController-0.3.51.atlas-final-mission-contract.xcarchive`
- IPA export: `build/TestFlightExport-0.3.51.atlas-final-mission-contract/MusicAtlasController.ipa`
- App Store Connect delivery UUID / build ID: `f385a64a-e3a0-4f94-a4c3-d0a5df51c845`
- App Store Connect processing state after upload: `VALID`

## Included Alpha Runtime Scope

- Promotes the latest Atlas explainer alpha copy/render work in the app build.
- Confirms the bundled Atlas explainer render pack reports `schema_version: 0.3` and `pack_count: 120`.
- Keeps the existing Atlas lane scope; no new Mission selection or Mission context UI was implemented in this upload slice.

## Mission Enrichment Note

The Mission Enrichment v0.2 package under `data/product_contracts/mission_enrichment_v0_2/` is present and its local fixture contract tests pass. Its own lock/report docs still classify it as an offline/local contract package, not iOS or Supabase runtime-integrated. This TestFlight IPA therefore carries the current app runtime plus the latest repo state, but does not by itself deploy backend Mission Enrichment runtime behavior.

## Validation

- Mission Enrichment v0.2 fixture contract tests: pass
- Supabase generate-first-mission-batch smoke: pass
- Focused iOS tests: pass
  - `SurveyTests`
  - `AtlasHomeReadoutTests`
  - `AtlasExplainerTests`
  - `MissionDecodingTests`
- Release archive: pass
- Manual IPA export: pass
- Legacy `altool --upload-app` upload: pass
- App Store Connect build lookup after upload: build `51`, processing state `VALID`

## Upload Notes

The current Xcode `ContentDelivery.framework` upload path failed during app metadata lookup with `NSPOSIXErrorDomain Code=17 "File exists"`. A local App Store Connect API check succeeded, confirming account/API access. Upload was completed through the legacy `altool --upload-app` path with explicit TestFlight metadata.
