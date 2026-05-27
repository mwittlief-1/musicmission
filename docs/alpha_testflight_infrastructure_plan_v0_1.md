# Waymark Alpha TestFlight Infrastructure Plan v0.1

Date: 2026-05-21

## Goal

Get Waymark into a trusted TestFlight Alpha with one guarded first-run loop:

```text
Apple Music connect
-> in-app Survey
-> Survey evidence export
-> starter MissionGenerationDigestView
-> Supabase Edge Function
-> OpenAI first mission generation
-> app-import-ready mission.v0.2
-> MusicKit playback
-> reactions, notes, review, export/upload
```

The backend stays thin. Supabase protects the OpenAI key, logs generation runs, validates output, gates app import, and stores alpha artifacts. It does not become the full Atlas, full graph authority, account system, or multi-device sync layer.

## Current Repo Read

Green or near-green:

- SwiftUI iOS app exists in `MusicAtlasController.xcodeproj`.
- Automatic signing is configured with team `7XQQ46X8QQ`.
- Bundle ID is `com.vytisstudios.MusicAtlasController`.
- App version is `0.2`, build `1`.
- `NSAppleMusicUsageDescription` is present.
- Apple Music authorization, live search/resolution, and playback services exist.
- Mission library loading, mission detail, resolver, player, Mission Review, local persistence, JSON/Markdown export, and physical-device acceptance export paths exist.
- Survey UI exists with artist, album, song, optional advanced passes, five-state response cycle, local persistence, nuance tags, and freeform scaffolding.
- Mission generation harness exists under `waymark-ai-tests/` with Responses API request construction, structured output, model/cost/latency logging, schema validation, and app-import readiness scoring.
- Atlas harness exists under `waymark-atlas-tests/` and now emits `mission_generation_digest_view.json`.

Verification run:

- `xcodebuild test -scheme MusicAtlasController -project MusicAtlasController.xcodeproj -destination 'platform=iOS Simulator,name=iPhone 17,OS=26.5'` passed on 2026-05-21.
- `npx -y -p typescript -p @types/deno tsc --noEmit --target ES2022 --lib ES2022,DOM --strict supabase/functions/generate-first-mission-batch/index.ts` passed on 2026-05-21.
- Supabase CLI and Deno CLI are not installed locally yet, so `supabase functions serve` and deploy verification remain pending.

Yellow or red for TestFlight Alpha:

- The app does not yet have a Supabase client or first-mission generation call.
- Survey responses persist locally but do not yet emit the final in-app Survey Evidence Export contract.
- Starter AtlasDigestView / MissionGenerationDigestView construction is proven in harness, not wired into the app.
- Mission generation output schema is `waymark.mission_output.v0.1`, while the app imports `mission.v0.2`.
- No deployed Supabase project, tables, secrets, Edge Function, or audit trail exists yet.
- No TestFlight app record/build pipeline checklist is tracked in repo yet.
- TestFlight privacy/trust language is still a release dependency.

## Apple Developer Account Tasks

Required before TestFlight:

- Confirm Apple Developer Program membership is active.
- Accept the latest agreements in App Store Connect Business if prompted; Apple blocks new app records until the Account Holder signs current agreements.
- Register or confirm the explicit App ID for `com.vytisstudios.MusicAtlasController`, unless we decide to rename the bundle before alpha.
- Enable MusicKit on that App ID in Certificates, Identifiers & Profiles.
- Make sure Xcode automatic signing produces a provisioning profile that includes the MusicKit capability.
- Create the App Store Connect app record before uploading the first build.
- Fill TestFlight beta app description, feedback email, test info, and export-compliance answers.
- Decide internal-only first pass vs external trusted testers. External TestFlight requires beta review on the first build assigned to an external group.

Tester requirements:

- Testers need the TestFlight app.
- Testers need an Apple Account that can accept TestFlight invitations.
- For the full playback gate, testers need an Apple Music-capable device/account state, normally including Apple Music app access and catalog playback rights.

Current Apple docs checked:

- [TestFlight overview](https://developer.apple.com/help/app-store-connect/test-a-beta-version/testflight-overview/)
- [Add a new app record](https://developer.apple.com/help/app-store-connect/create-an-app-record/add-a-new-app)
- [Enable MusicKit for an App ID](https://developer.apple.com/help/account/services/musickit/)

## Supabase Alpha Tasks

Required before the backend can serve the app:

- Create a Supabase project.
- Install/login/link the Supabase CLI locally.
- Apply `supabase/migrations/20260521160000_alpha_generation_logs.sql`.
- Set Edge Function secrets:
  - `OPENAI_API_KEY`
  - `WAYMARK_OPENAI_MODEL`
  - `WAYMARK_OPENAI_REASONING_EFFORT`
  - `WAYMARK_OPENAI_MAX_OUTPUT_TOKENS`
  - `WAYMARK_GENERATION_PROMPT_VERSION`
- Deploy `generate-first-mission-batch`.
- Confirm generation rows are written to `alpha_generation_runs`.
- Confirm raw OpenAI output, parsed mission output, app mission adapter output, token usage, latency, and app-import status are logged.
- Decide whether alpha evidence uploads go through a second Edge Function or remain export/share for the first TestFlight build.

Current Supabase docs checked:

- [Edge Functions quickstart](https://supabase.com/docs/guides/functions/quickstart)
- [Edge Function environment variables and secrets](https://supabase.com/docs/guides/functions/secrets)

## Thin Backend Contract

Initial endpoint:

```text
POST /functions/v1/generate-first-mission-batch
```

Request body:

```json
{
  "client_request_id": "ios-generated-stable-id",
  "tester_alias": "trusted-alpha-001",
  "requested_batch_size": 3,
  "survey_evidence_export": {},
  "mission_generation_digest_view": {},
  "candidate_pool": {},
  "prompt_context": {
    "alpha_scope": "first_batch",
    "storefront": "us"
  }
}
```

Response body:

```json
{
  "run_id": "uuid",
  "status": "app_import_candidate",
  "prompt_version": "mission_generator_candidate_constrained_v0_1",
  "model": "gpt-5.4-mini",
  "mission_output_schema_version": "waymark.mission_output.v0.1",
  "app_mission_schema_version": "mission.v0.2",
  "generation": {},
  "app_missions": [],
  "validation": {},
  "usage": {},
  "latency_ms": 1234
}
```

Gate rule:

- If generated output is invalid, return `status = "blocked"`.
- If generated output is valid but `review_config.ready_for_app_import != true`, return `status = "review_needed"`.
- Only return `app_missions` when the adapted `mission.v0.2` output is app-import eligible.

## Alpha Acceptance Gates

Gate A: In-app Survey evidence persists and exports with visible refs.

Gate B: App creates a compact MissionGenerationDigestView or equivalent packet.

Gate C: App calls Supabase, Supabase calls OpenAI securely, and a run is logged.

Gate D: Generated mission output validates and adapts to `mission.v0.2`.

Gate E: A real iPhone plays a full mission through MusicKit.

Gate F: Survey, mission, resolution, playback, reaction, notes, and review state survive app relaunch.

Gate G: Team receives an export or backend record that maps evidence to mission items and possible Atlas updates.

Gate H: Tester sees a starter read, route rationale, or "what Waymark learned" moment without promoted Atlas overclaims.

## Recommended First Execution Order

1. Finish Supabase project setup and deploy this scaffold.
2. Add the app-side generation client and config.
3. Add in-app Survey Evidence Export builder.
4. Add app-local MissionGenerationDigestView builder or adapter from the harness contract.
5. Add mission output adapter tests for `waymark.mission_output.v0.1 -> mission.v0.2`.
6. Wire Survey readout to "Generate First Missions."
7. Run simulator tests, then physical-device MusicKit mission QA.
8. Archive/upload build to App Store Connect.
9. Start internal TestFlight first, then external trusted testers after beta review.
