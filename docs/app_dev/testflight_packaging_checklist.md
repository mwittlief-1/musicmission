# TestFlight Packaging Checklist

Purpose: keep the Alpha app shippable without leaking debug fixtures, private mission packs, or unfinished backend assumptions into tester-facing flows.

Related readiness docs:

- `docs/app_dev/alpha_product_decision_addendum_2026_05_22.md`
- `docs/app_dev/testflight_non_code_readiness_checklist_v0_1.md`
- `docs/app_dev/user_facing_screen_spec_v0_1.md`

## Build Settings

- Increment marketing version and build number before archive.
- Use the approved bundle ID and signing team.
- Confirm Apple Music capability and `NSAppleMusicUsageDescription`.
- Confirm Release excludes bundled mission JSON user content.
- Confirm Survey and diagnostics tabs are controlled by `AppFeatureFlags`.
- Confirm mission assignments arrive through reviewed import/assignment only.

## App Store Connect

- Add or update app icon placeholder before external testing.
- Fill privacy, support, and contact fields before external TestFlight.
- Add internal tester group first.
- Add external tester group only after physical-device QA passes.
- Use clear tester instructions for Apple Music subscription/account requirements.

## Preflight Commands

```sh
xcodebuild test -scheme MusicAtlasController -destination 'platform=iOS Simulator,name=iPhone 17'
xcodebuild -scheme MusicAtlasController -configuration Release -destination 'platform=iOS Simulator,name=iPhone 17' clean build
find ~/Library/Developer/Xcode/DerivedData -path '*Release-iphonesimulator/MusicAtlasController.app/*' \( -name 'sample_mission*.json' -o -name 'waymark_matt_10_personal_missions_v0_1.json' \) -print
```

The final command should return no bundled mission files for the Release app.

## Alpha Guardrails

- Do not ship personal mission packs as user-facing content.
- Do not generate missions locally in the app.
- Do not write promoted Atlas state from the app.
- Do not treat Apple Music exposure as taste truth.
- Do not treat skip/no-signal as automatic dislike.
- Keep raw JSON, Apple Music signal probe, and resolver diagnostics out of the normal tester path unless support explicitly needs them.

## Release Notes Checklist

- State that this is a trusted Alpha.
- Mention Apple Music is required.
- Mention missions are assigned/imported after install.
- Mention evidence may be exported/shared for product calibration.
- Include reset/recovery instructions for stuck local state.
