# TestFlight Build 49 Atlas Explainer Feedback Upload Report

Date: 2026-06-04

## Build

- App: Cartenza / `MusicAtlasController`
- Version: `0.3`
- Build: `49`
- Bundle ID: `com.vytisstudios.MusicAtlasController`
- Archive path: `build/MusicAtlasController-0.3.49.atlas-explainer-feedback.xcarchive`
- Export path: `build/TestFlightUpload-0.3.49.atlas-explainer-feedback-manual`

## Scope

This build promotes the feedback-updated Atlas Explainer v0.3 render-pack resource for TestFlight review.

Included:

- `MusicAtlasController/Resources/atlas_explainer_render_packs_v0_3.json`
- `schema_version: 0.3`
- `source_package: AtlasExplainerPack_v0_3_ProfileLadders`
- `pack_count: 120`
- compatibility graph refs merged from `atlas_explainer_render_packs_v0_2_3.json`

Not included:

- mission selection implementation
- mission context implementation
- post-mission learning summaries
- runtime model generation for explainer copy
- founder-specific data

## Resource Checks

- Current app resource hash differs from build 48 archived resource hash, confirming this upload contains the later feedback-updated explainer package.
- Build 49 archived resource hash matches the current app resource hash exactly.
- Core v0.3 module check passed:
  - `packs_len: 120`
  - `core_missing_count: 0`
  - `packs_missing_legacy_route_refs: 0`
  - `dead_end_false_nearby_caution_module` remains intentionally empty across 120 packs and hidden by the current UI.

## Validation

Passed:

```sh
git diff --check
```

Passed:

```sh
xcodebuild test \
  -project MusicAtlasController.xcodeproj \
  -scheme MusicAtlasController \
  -destination 'platform=iOS Simulator,id=2A4C112F-958E-4CEB-8D2A-C2D42F88D6E5' \
  -only-testing:MusicAtlasControllerTests/SurveyTests \
  -only-testing:MusicAtlasControllerTests/AtlasHomeReadoutTests \
  -only-testing:MusicAtlasControllerTests/AtlasExplainerTests
```

Focused test log:

- `build/TestFlightUpload-0.3.49.atlas-explainer-feedback.focused-test.log`

## Archive Verification

Archive succeeded.

Verified archived app metadata:

- `CFBundleShortVersionString: 0.3`
- `CFBundleVersion: 49`
- `CFBundleIdentifier: com.vytisstudios.MusicAtlasController`
- `ITSAppUsesNonExemptEncryption: false`

Archive log:

- `build/TestFlightUpload-0.3.49.atlas-explainer-feedback.archive.log`

Note: archive logs are local-only build evidence and may include private build-setting expansion from the local xcconfig. Keep them under ignored `build/`.

## Upload

Upload succeeded via manual App Store signing profile and App Store Connect API-key authentication.

App Store Connect status from `xcodebuild -exportArchive`:

- `Uploaded package is processing.`
- `Upload succeeded.`
- `** EXPORT SUCCEEDED **`

Upload log:

- `build/TestFlightUpload-0.3.49.atlas-explainer-feedback.upload-manual-api-key.log`
