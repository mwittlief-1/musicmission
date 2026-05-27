# Alpha Follow-Up Dispatch Packet - 2026-05-25

## Status

Created after review of the latest lane updates on 2026-05-25.

This packet packages the remaining follow-ups needed before the next TestFlight Alpha build should be treated as generation-ready.

## Broadcast Note

Send this to lanes as they become available:

```text
Please read docs/alpha_backlog/alpha_followup_dispatch_packet_2026_05_25.md. Pick up the section for your lane, complete every non-dependent task, update the checkboxes/status notes in that file, and raise a blocker row only when another lane must change something before you can proceed. Do not package a new TestFlight build until Core + Infra acceptance checks in this packet are complete.
```

## Executive Call

Local contract hardening is moving in the right direction, but the next Alpha build still needs three closures:

- Core must align batch-memory field names with the backend contract.
- Core must preserve Canonical route identity fields into the live mission-generation request.
- Infra must prove authenticated live app/JWT generation and diagnostic persistence, not only local/offline acceptance.

Apple Music Signal Payload v0.2 work appears largely implemented, but Survey should continue treating v0.2 as raw capture/persistence only until a separate Survey page-construction spec is accepted.

## Cross-Lane Dependency Map

| id | dependency | owner | blocks | status |
| --- | --- | --- | --- | --- |
| `AFD-I001` | `prompt_context` batch-memory display-key field mismatch: Core sends `already_selected_route_display_identity_keys`; Supabase reads `already_selected_display_keys`. | Core Waymark Build, Mission Generation | reliable 10-mission cross-batch dedupe | fixed locally; live proof pending |
| `AFD-I002` | Canonical route identity fields exist in bundled JSON but are not preserved by `AlphaRouteCandidate` into `candidate_pool.candidates`. | Core Waymark Build | strong route-key validation, deterministic app item IDs | fixed locally; live proof pending |
| `AFD-I003` | App mission payload strips route `candidate_id` and route keys after backend validation. | Core Waymark Build, Mission Generation | local import diagnostics and post-import auditability | fixed locally; live proof pending |
| `AFD-I004` | Live Supabase needs authenticated app/JWT proof for generation + diagnostics. Current infra report is still offline acceptance. | Supabase / Infrastructure | packaging confidence | open |
| `AFD-I005` | Apple v0.2 raw capture is not a Survey scoring spec. Current Survey provider intentionally ignores Apple strengths. | Survey Lineage, Product | Apple-driven Survey adaptation | open |

## Core Waymark Build Follow-Ups

### Mission

Make the app request payload, local mission model, and diagnostic output preserve the route identities that Mission Generation and Supabase now expect.

### Tasks

- [x] `CWB-AFD-001` Align batch-memory field names.
  - Add `prompt_context.already_selected_display_keys` as the canonical display-key array.
  - Keep `already_selected_route_display_identity_keys` only as a backward-compatible alias if desired.
  - Update `MissionGenerationPromptContext` coding keys in `MusicAtlasController/Services/MissionLoader.swift`.
  - Update request diagnostics in `MusicAtlasController/Models/AppModel.swift`.
  - Acceptance: generated request JSON contains `prompt_context.already_selected_display_keys` when prior mission items exist.

- [x] `CWB-AFD-002` Preserve Canonical route identity fields in candidate-pool request rows.
  - Decode and output:
    - `app_route_item_id`
    - `route_candidate_key`
    - `route_batch_dedupe_key`
    - `route_display_identity_key`
  - Primary file: `MusicAtlasController/Services/SurveyStore.swift`.
  - Acceptance: `candidate_pool.candidates[]` sent to Supabase includes all four fields when present in `MusicAtlasController/Resources/alpha_compact_candidate_pool_alpha_v0.json`.

- [x] `CWB-AFD-003` Preserve route identity in imported app missions.
  - Extend app mission item model and decoding tests to carry backend-safe fields:
    - `candidate_id`
    - `route_candidate_key`
    - `route_batch_dedupe_key`
    - `route_display_identity_key`
  - Do not expose internal IDs in user-facing UI.
  - Acceptance: local `mission_import_result` diagnostics can show candidate/route identity for each imported item without relying on display strings.

- [x] `CWB-AFD-004` Add regression tests for the request and import contract.
  - Test request payload includes canonical batch-memory names and route identity fields.
  - Test import rejects duplicate route display identity and preserves route identity metadata.
  - Re-run the simulator test suite before packaging.
  - Status 2026-05-25: regression coverage added; `build`, `build-for-testing`, Supabase smoke, TypeScript compile, and Apple v0.2 fixture validation pass. Focused simulator execution was attempted but blocked by simulator launch `NSMachErrorDomain -308`; retry before packaging if the simulator is healthy.

- [ ] `CWB-AFD-005` Package only after Infra live proof.
  - Build number is currently `13`; do not upload a new TestFlight build until `INF-AFD-001` through `INF-AFD-004` are complete or consciously waived.

### Handoff Needed

- Mission Generation: confirm whether `already_selected_route_display_identity_keys` should remain as an alias or be removed after Core sends `already_selected_display_keys`.
- Infra: provide live run/diagnostic proof before packaging.

## Mission Generation Follow-Ups

### Mission

Close the contract around route identity names, app mission adaptation, and batch-memory enforcement.

### Tasks

- [x] `MGN-AFD-001` Finalize batch-memory aliases.
  - Current product contracts use `prompt_context.already_selected_display_keys`.
  - Supabase validator reads `already_selected_display_keys`.
  - Core currently sends `already_selected_route_display_identity_keys`.
  - Decide whether the backend accepts both names for Alpha or Core migrates fully to the shorter canonical name.

- [x] `MGN-AFD-002` Update Supabase adapter output to carry route identity fields.
  - In `supabase/functions/generate-first-mission-batch/index.ts`, ensure `toAppMissionItem` copies safe internal identity fields into app mission items when present.
  - Required fields:
    - `candidate_id`
    - `route_candidate_key`
    - `route_batch_dedupe_key`
    - `route_display_identity_key`
  - Acceptance: app missions returned by replay fixtures retain these fields.

- [x] `MGN-AFD-003` Add route-key fixture coverage.
  - Add or extend a replay fixture where candidate rows include `app_route_item_id`, `route_candidate_key`, `route_batch_dedupe_key`, and `route_display_identity_key`.
  - Expected behavior: generated route item copies/uses those fields; adapted app mission retains diagnostic-safe route identity.

- [x] `MGN-AFD-004` Keep local validator green.
  - Run:
    - `node scripts/smoke_supabase_generate_first_mission_batch.mjs`
    - `npx -y -p typescript tsc --noEmit --target ES2022 --lib ES2022,DOM --strict supabase/functions/generate-first-mission-batch/index.ts`
  - Status 2026-05-25: both commands pass locally.

## Supabase / Infrastructure Follow-Ups

### Mission

Prove the live backend path with authenticated requests and persisted diagnostics.

### Current State

`scripts/check_supabase_alpha_infra.mjs` passes and reports live functions active, but the generated report still labels the result `offline_acceptance_pass`. That is not enough by itself to bless TestFlight packaging.

### Tasks

- [ ] `INF-AFD-001` Run authenticated live generation smoke.
  - Use the live project `ewuffhezhgyskcfyzkvw`.
  - Exercise `generate-first-mission-batch` with an authenticated Alpha user/JWT, not only local replay validation.
  - Acceptance: a new `alpha_generation_runs` row exists for the smoke and includes `validation.route_identity`.
  - Status 2026-05-25: hosted anon-JWT live smoke passed on function version `14` with run `6b1fc23f-426b-4590-9410-c786466af741`, `status = app_import_candidate`, `app_missions = 1`, and populated `validation.route_identity`. Real app Sign in with Apple/Supabase user-session smoke remains open.

- [ ] `INF-AFD-002` Prove duplicate/non-candidate/batch-memory blockers live.
  - Live validation should block:
    - duplicate route `item_id`
    - duplicate route display identity
    - missing route `candidate_id`
    - route `candidate_id` outside `candidate_pool.candidates`
    - repeat from `prompt_context.already_selected_display_keys`
  - Acceptance: live rows show `status = blocked` with redacted validation summaries.

- [ ] `INF-AFD-003` Prove diagnostic upload persistence.
  - Use `submit-alpha-diagnostic` with an authenticated app/JWT path.
  - Acceptance: `alpha_client_diagnostic_artifacts` has a new row for a benign diagnostic fixture or app-produced package.
  - Do not expose service-role keys, Apple identity tokens, raw Apple payloads, or private tester data in docs.
  - Status 2026-05-25: hosted anon-JWT diagnostic smoke passed on function version `3` after applying migration `20260525120000_alpha_client_state_snapshot_diagnostics.sql`; upload `28d24335-6b4e-48f0-b2ec-6b25969dbac9` persisted `client_state_snapshot`. Real app-authenticated diagnostic smoke with `user_id_present = true` remains open.

- [ ] `INF-AFD-004` Update deploy/acceptance docs.
  - Update or replace `supabase/alpha_infra_acceptance_report.md` so the result distinguishes:
    - offline/local acceptance
    - live function active check
    - authenticated live smoke
    - diagnostic persistence proof
  - Add a short note under `docs/infra/` with timestamp, function versions, migration status, and smoke result.
  - Status 2026-05-25: added `docs/infra/live_alpha_safe_smoke_report_2026_05_25.md` for the hosted safe-smoke pass and remaining app-authenticated proof.

## Survey Lineage Follow-Ups

### Mission

Keep Survey behavior stable while separating raw Apple capture from future Survey scoring decisions.

### Tasks

- [ ] `SURV-AFD-001` Treat Apple v0.2 as raw intake only until scoring spec lands.
  - Current `AlphaAppleEvidenceIndex` ignores payload strengths; keep this explicit unless Product approves a v0.2 scoring adapter.
  - Update user/support wording if needed so testers do not expect Apple-driven adaptation yet.

- [ ] `SURV-AFD-002` Close the read-only lineage report into implementation tickets.
  - Source: `docs/app_dev/waymark_alpha_intake_lineage_report_2026_05_25.md`.
  - Prioritize:
    - first-run Survey reset on refresh
    - Apple payload recapture clearing displayed pages
    - invalidated future responses influencing regenerated pages
    - missing selected-vs-excluded candidate trace
    - song `payloadSignature` bucket mismatch

- [ ] `SURV-AFD-003` Add page-selection trace only after reset/stability bugs are handled.
  - Desired trace: selected candidates, near-misses, exclusion reasons, score vector, quota pass, fallback pass, Apple match path, and invalidation event.
  - Keep raw Apple payload private/support-only.

## Apple Music Signal Payload v0.2 Follow-Ups

### Mission

Close documentation/status on v0.2 raw capture work and avoid accidental Survey-scoring scope creep.

### Tasks

- [x] `APPLE-AFD-001` Update `docs/alpha_backlog/apple_music_signal_payload_v0_2_alignment_dispatch_2026_05_25.md`.
  - Mark completed deliverables that now exist:
    - spec markdown
    - JSON schema
    - Swift model
    - probe implementation
    - fixture
    - validator
    - migration note
    - tests
  - Leave explicit blockers for Replay/physical-device verification and future Survey scoring spec.

- [x] `APPLE-AFD-002` Keep validator green.
  - Run:
    - `node scripts/validate_apple_music_signal_payload_v0_2.mjs`
  - Acceptance: sample fixture validates and diagnostic-excluded sources stay out of primary signal sources.
  - Status 2026-05-25: sample fixture validation passes.

## Packaging Gate

The next TestFlight build can proceed when:

- [x] Core request payload includes canonical batch-memory names and route identity fields.
- [x] Supabase adapter/app mission payload preserves route identity metadata.
- [x] Local Supabase smoke and TypeScript checks pass.
- [x] Local iOS simulator tests pass or any failure/hang is documented with a packaging decision.
- [ ] Infra proves authenticated live generation and diagnostic upload persistence.
- [ ] Product accepts that Apple v0.2 is raw capture only for this build, with Survey scoring to follow separately.

## Review Commands Already Run

These passed during the consolidation review:

```bash
python3 scripts/validate_canonical_atlas_route_identity_contract.py
node scripts/validate_alpha_consumable_layer_alpha_v0.mjs
node scripts/smoke_supabase_generate_first_mission_batch.mjs
npx -y -p typescript tsc --noEmit --target ES2022 --lib ES2022,DOM --strict supabase/functions/generate-first-mission-batch/index.ts
node scripts/check_supabase_alpha_infra.mjs
node scripts/validate_apple_music_signal_payload_v0_2.mjs
plutil -lint MusicAtlasController/Support/Info.plist
git diff --check
COPYFILE_DISABLE=1 xcodebuild -scheme MusicAtlasController -configuration Debug -sdk iphonesimulator -destination 'generic/platform=iOS Simulator' -derivedDataPath /tmp/musicmission-afd-build build
COPYFILE_DISABLE=1 xcodebuild -scheme MusicAtlasController -configuration Debug -sdk iphonesimulator -destination 'generic/platform=iOS Simulator' -derivedDataPath /tmp/musicmission-afd-build-for-testing build-for-testing
```

One simulator test run was inconclusive during review because the test bundle compiled, then simulator launch hung and ended with `NSMachErrorDomain -308` after manual cleanup. Core should rerun executable simulator tests before packaging if the simulator is healthy, or explicitly waive with the green build-for-testing result.
