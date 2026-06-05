# TestFlight Build 56 Mission Enrichment Runtime Upload Report

Date: 2026-06-05

Build: `0.3 (56)`

## Scope

Build 56 wires Mission Enrichment on top of the deterministic Survey/Atlas mission selector.

- `Regenerate missions` still selects the deterministic six Survey-derived Alpha missions first.
- The app then calls the new Supabase `enrich-mission` Edge Function once per selected mission.
- The enrichment overlay updates mission copy, route-item player copy, and per-song secondary reaction tags.
- Mission IDs, route item IDs, song order, Apple Music resolution metadata, and deterministic route identity are preserved.
- The existing regeneration progress bar now covers deterministic selection plus six enrichment completions.

## Supabase

- Deployed Edge Function: `enrich-mission`
- Project ref: `ewuffhezhgyskcfyzkvw`
- JWT verification: enabled in `supabase/config.toml`
- OpenAI execution remains server-side; the iOS app uses the Supabase publishable key/session bearer and does not contain the OpenAI key.

## Live Smoke

- Replay smoke against deployed `enrich-mission`: pass
- Real OpenAI smoke against deployed `enrich-mission`: pass
- Real smoke model reported by function: `gpt-5.4-mini`
- Real smoke latency: `8439 ms` function latency, `8757 ms` wall time
- Real smoke status: HTTP `200`, enrichment status `enriched`

The live smoke used a small two-item mission. Full six-mission regeneration should be expected to take materially longer because the app performs one enrichment call per deterministic mission after local selection.

## QA

- `npx -y -p typescript tsc --noEmit --target ES2022 --lib ES2022,DOM --strict supabase/functions/enrich-mission/index.ts`: pass
- `xcodebuild test -project MusicAtlasController.xcodeproj -scheme MusicAtlasController -destination 'platform=iOS Simulator,id=EB604B3F-7E42-470B-8D1E-156BAD202428' -only-testing:MusicAtlasControllerTests/MissionDecodingTests/testAppModelRegeneratesMissionsFromCurrentSurveyWithLocalSelector`: pass
- `xcodebuild build -project MusicAtlasController.xcodeproj -scheme MusicAtlasController -configuration Release -destination 'generic/platform=iOS'`: pass
- `git diff --check`: pass

The focused XCTest uses a local enrichment stub and verifies that regeneration calls enrichment six times, imports enriched mission titles, and exposes secondary tags in the player chip sets.

## Archive And Upload

- Archive: `build/MusicAtlasController-0.3.56.mission-enrichment.xcarchive`
- IPA: `build/TestFlightExport-0.3.56.mission-enrichment/MusicAtlasController.ipa`
- IPA size: `6812767` bytes
- App Store Connect Build Upload API upload: complete
- Build upload ID: `1bd05592-89ab-4923-9876-a44c683ce6ab`
- Build upload file ID: `b2eb5505-b1ef-4922-9071-0f16c3903d3a`
- App Store Connect build ID: `1bd05592-89ab-4923-9876-a44c683ce6ab`
- App Store Connect processing state: `VALID`
- Audience: `INTERNAL_ONLY`
- Uploaded date: `2026-06-05T12:07:37-07:00`

Generated local ASC upload artifacts are under `build/TestFlightUpload-0.3.56.mission-enrichment.*`. Pre-signed upload URLs were redacted before writing persisted ASC response artifacts.
