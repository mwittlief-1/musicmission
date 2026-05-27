# Waymark Alpha App State, Recovery, and Diagnostics Audit

Generated: 2026-05-25

Scope: read-only audit of current app state/navigation, reset/quarantine, mission generation recovery, and support diagnostics behavior after the TestFlight build 12 state-resume report.

Primary finding: build 12 most likely reopened into mission generation because the app is designed to resume first-run state when the persisted Alpha state version is still current. Build 11 bumped the Alpha state version to `alpha1_fresh_read_quarantine_2026_05_24_01`; build 12 kept that same version and only changed Survey/generation tolerance behavior. A TestFlight update preserves UserDefaults, Application Support, Documents, Keychain, and OS Music authorization, so a tester who had already completed terms, auth, onboarding, Survey, and had `generation_status != core_ready` would be routed back to the generation screen.

Important caveat: this audit reads the current working tree, not a checked-out build tag or App Store archive. The root-state behavior matches the build reports, but exact shipped bits should still be confirmed against the archived build if there is any doubt.

## 1. Root Navigation and State-Machine Map

Root navigation lives in `MusicAtlasController/Views/RootView.swift`.

### First-run storage keys

`RootView` uses `@AppStorage` under the prefix `waymark.alpha1.`:

- `waymark.alpha1.accepted_terms_version`
- `waymark.alpha1.onboarding_completed`
- `waymark.alpha1.survey_completed`
- `waymark.alpha1.generation_status`
- `waymark.alpha1.state_version`

The current constants are:

- `currentTermsVersion = alpha_terms_2026_05_23`
- `currentStateVersion = alpha1_fresh_read_quarantine_2026_05_24_01`

`generation_status` can be:

- `not_started`
- `waiting_for_assignment`
- `generation_failed`
- `core_ready`

### Root route order

The effective root route order is:

1. If `state_version != currentStateVersion`, show `.consent`.
2. Else if `accepted_terms_version != currentTermsVersion`, show `.consent`.
3. Else if Supabase auth is not authenticated or Apple Music auth is not authorized, show `.access`.
4. Else if onboarding is incomplete, show `.onboarding`.
5. Else if Survey is incomplete, show `.survey`.
6. Else if `generation_status != core_ready`, show `.generation`.
7. Else show the core tab shell.

The core tab shell starts at `.mission`; the selected tab is in SwiftUI `@State`, not durable persistence.

### Launch task order

On root `.task`, the app runs:

1. `applyAlphaStateVersionResetIfNeeded()`
2. `appModel.loadMissionLibrary()`
3. `appModel.refreshSupabaseAuthSessionIfPossible()`
4. `resumeAlphaGenerationIfNeeded()`

The versioned reset only runs if `waymark.alpha1.state_version` differs from `currentStateVersion`. If the state version already matches, no quarantine/reset runs on launch.

### Generation resume policy

`resumeAlphaGenerationIfNeeded()` auto-retries only when all of these are true:

- terms version accepted
- state version current
- onboarding complete
- Survey complete
- Supabase authenticated
- `generation_status == waiting_for_assignment`
- reviewed mission count is below `10`
- generation is not already loading

If `generation_status == generation_failed`, the app still routes to generation, but it does not auto-retry. After relaunch, the in-memory `firstMissionGenerationState` and `lastActionMessage` are lost, so the screen may not explain the previous failure clearly unless the tester remembers it.

## 2. Persistent Storage Inventory

### UserDefaults

Owner: `RootView`

Keys:

- `waymark.alpha1.accepted_terms_version`
- `waymark.alpha1.onboarding_completed`
- `waymark.alpha1.survey_completed`
- `waymark.alpha1.generation_status`
- `waymark.alpha1.state_version`

Navigation impact:

- This is the first-run/root state driver.
- `generation_status != core_ready` is sufficient to keep the tester out of the core app after Survey completion.
- Build-to-build cleanup depends on changing `currentStateVersion`.

Reset behavior:

- `purgeLegacyFirstRunUserDefaults()` removes keys with the `waymark.alpha1.` prefix.
- Support reset and version mismatch both call this purge.

Gap:

- There is no durable "last seen app build", "last reset build", "reset reason", or "root state snapshot" to explain why the current route was chosen.

### Supabase Auth Keychain

Owner: `SupabaseAuthService` / `SupabaseSessionKeychainStore`

Storage:

- Keychain service: `com.vytisstudios.MusicAtlasController.supabaseAuth`
- Account: `supabase_session_v0_1`
- Stored data: encoded Supabase access token, refresh token, expiry, token type, and user summary.

Navigation impact:

- A valid or refreshable session makes the `.access` gate pass for Waymark account auth.
- A TestFlight update does not clear Keychain.

Reset behavior:

- `resetAllLocalAlphaState(signOut: true)` calls `supabaseAuth.signOut()`, which clears the keychain item.

Gap:

- Diagnostics should report auth status, user ID presence, expiry, and refresh outcome, but never tokens.

### Apple Music Authorization

Owner: `MusicAuthorizationService`

Storage:

- OS-level MusicKit authorization, not an app JSON file.

Navigation impact:

- Root `.access` gate requires `musicAuthorization.snapshot.status == authorized`.
- TestFlight updates preserve OS authorization.

Reset behavior:

- App reset cannot revoke OS Music authorization.

Gap:

- The support package should capture authorization status plus subscription/storefront playback capability when available, so support can distinguish app auth from MusicKit/subscription issues.

### Survey State

Owner: `SurveyPersistenceStore` / `SurveyStore`

File:

- Application Support / `MusicAtlasController/waymark_survey_session_v0_1.json`

Contents:

- `survey_session_id`
- current step
- responses
- freeform signals
- advanced filter
- displayed pages
- Apple Music signal payload
- updated timestamp

Navigation impact:

- `RootView` does not inspect this file directly.
- `survey_completed` in UserDefaults decides whether root shows Survey or generation.
- Mission generation request building loads this file.

Reset behavior:

- `resetAllLocalAlphaState()` calls `SurveyPersistenceStore().reset()`.
- Version mismatch also quarantines the entire Application Support app root before resetting stores.

Gap:

- First-run Survey calls `prepareRequiredAlphaIntake()` with `resetExistingResponses: true` whenever the first-run Survey view is created. That means partial first-run Survey persistence is not really resumable; it is overwritten when the tester re-enters first-run Survey. This may be intentional for clean Alpha intake, but it should be documented and tested as a policy decision.

### Reviewed Mission Catalog

Owner: `ReviewedMissionStore` / `LocalMissionProvider`

File:

- Application Support / `MusicAtlasController/waymark_reviewed_missions_v0_1.json`

Contents:

- generated/imported mission assignments
- source
- import timestamp
- source run ID
- import note

Navigation impact:

- Core unlock requires `generation_status == core_ready`, but `retryGeneration()` only sets that when reviewed mission count is at least `10`.
- Generation retry and resume use reviewed mission count to decide whether more generation is required.

Reset behavior:

- `resetAllLocalAlphaState()` calls `missionProvider.resetReviewedAssignments()`.
- Version mismatch quarantines the app root.

Gap:

- The root gate can say "generation" based on UserDefaults even if catalog contents are inconsistent. A state snapshot should show both the flag and catalog count.

### Mission Session Library

Owner: `SessionPersistenceStore`

File:

- Application Support / `MusicAtlasController/waymark_session_library_v0_1.json`

Contents:

- active mission ID
- selected item ID
- per-item resolutions
- playback records
- reactions
- saved evidence exports
- updated timestamp

Navigation impact:

- Does not choose first-run stage.
- Once core is unlocked, `loadMissionLibrary()` restores active mission/session state.

Reset behavior:

- `resetAllLocalAlphaState()` calls `sessionPersistenceStore.reset()`.

Gap:

- Saved export references are stored here, while export files live under Documents. Quarantine moves Documents export roots, so the session library and files must stay in sync after reset.

### Client Diagnostics

Owner: `ClientDiagnosticArtifactStore`

Files:

- Documents / `MusicAtlasControllerExports/support_diagnostics/artifacts/*.json`
- Documents / `MusicAtlasControllerExports/support_diagnostics/packages/support_diagnostics_YYYYMMDD_HHMMSS/`
- Package index: `waymark_support_diagnostics_index.json`

Artifact types currently modeled:

- `apple_music_signal_payload`
- `survey_page_selection_audit`
- `survey_evidence_export`
- `mission_generation_request_packet`
- `mission_generation_result`
- `mission_import_result`
- `client_error_event`

Reset behavior:

- `resetAllLocalAlphaState()` calls `clientDiagnosticStore.reset()`.
- Version mismatch quarantine also moves the Documents export root.

Gap:

- Support diagnostics are reachable from `ExportPreviewView` / Account in core app, but not directly from the first-run generation failure screen. If the core app is locked, the tester may be unable to package/upload diagnostics before resetting.

### Evidence and Probe Exports

Owners:

- `ExportFileStore`
- `AppleMusicSignalProbeFileStore`

Files:

- Documents / `MusicAtlasControllerExports/dev/`
- Documents / `MusicAtlasControllerExports/acceptance/`
- Documents / `MusicAtlasControllerExports/apple_music_signal_probe/`

Reset behavior:

- Version mismatch/support reset quarantine moves the whole `MusicAtlasControllerExports` root.

Gap:

- Support reset warns via `lastActionMessage`, but the tester has no pre-reset confirmation that diagnostics/evidence were preserved or uploaded.

## 3. Why Build 12 Likely Resumed Mission Generation

Build 11 explicitly introduced a fresh-read quarantine by bumping `currentStateVersion` to `alpha1_fresh_read_quarantine_2026_05_24_01`, purging Alpha UserDefaults, quarantining local app/export roots, signing out Supabase, disabling failed-state auto-retry, adding `Start Fresh`, and gating core unlock on all `10` missions.

Build 12 did not bump the Alpha state version. Its build report lists Survey page selection fixes and generation tolerance for app-validation failures, but no new first-run state version or forced reset.

Therefore, if the tester installed build 12 over a build 11 session where:

- `waymark.alpha1.state_version == alpha1_fresh_read_quarantine_2026_05_24_01`
- terms were accepted
- Supabase auth was still valid or refreshable
- Apple Music authorization was still authorized
- onboarding was completed
- `survey_completed == true`
- `generation_status` was `waiting_for_assignment` or `generation_failed`
- reviewed mission count was below `10`

then `RootView.firstRunStage` would correctly return `.generation`. If the persisted status was `waiting_for_assignment`, build 12 would also auto-resume generation after auth refresh. If the status was `generation_failed`, it would not auto-retry, but it would still reopen to the generation screen because `generation_status != core_ready`.

This makes the observed build 12 behavior likely expected under the current state model, not evidence that build 11 quarantine is missing. The missing piece is a clear product/release policy: should every internal TestFlight build reset Alpha state, or only builds that bump `currentStateVersion`? Right now the code implements the second policy.

## 4. Recovery UX Gaps

### Generation failure details are not durable

`generation_status` persists, but the detailed failure text and `firstMissionGenerationState` are in memory. After relaunch, the tester can be routed back to generation without a durable explanation of the previous failure, run IDs, last client request ID, or next recommended action.

Impact:

- Tester sees "generation" again but support may not know what failed.
- Failed build 12 sessions can feel like they resumed into the same broken screen.

### Support diagnostics are not available in first-run generation

The diagnostic package UI lives under Share Evidence / Account / `ExportPreviewView`. In first-run generation, the core app is locked until 10 missions. The generation screen has Retry and Start Fresh, but no "Prepare Support Diagnostics", "Upload Diagnostics", or "Share Diagnostics" action.

Impact:

- The tester may reset before exporting the useful request/result/import/client-error chain.
- Support loses exactly the artifacts needed to diagnose generation failures.

### Start Fresh is disabled while generation is loading

`Start Fresh` is disabled when `generationState.isLoading`. If a network request hangs, the tester has no visible cancel/escape until the async call returns or the app is killed.

Impact:

- A stuck generation request can become a stuck UI.
- Killing/reopening may auto-resume if `generation_status == waiting_for_assignment`.

### Auto-resume has no update/build guard

Auto-resume is tied to `waiting_for_assignment`, not to whether the app was just updated, whether the prior request is stale, or whether the tester consented to another retry in the new build.

Impact:

- Useful for interrupted generation.
- Surprising after TestFlight updates when the expected smoke was a clean or paused state.

### Survey persistence policy is mixed

Survey state is persisted, but first-run Survey entry resets responses by default. After Survey completion, the root flow depends on UserDefaults and generation uses the persisted Survey session. Before completion, a tester who leaves/reopens first-run Survey may not actually resume the partial Survey.

Impact:

- This may be acceptable for required Alpha intake, but it should be explicit.
- Support diagnostics should be clear about whether a Survey session was resumed, reset, or superseded.

### Reset/quarantine is coarse and silent after success

The quarantine moves Application Support `MusicAtlasController` and Documents `MusicAtlasControllerExports`, then separately resets stores and signs out. This is good for freshness, but the tester does not see a detailed pre/post inventory or have a guided "export diagnostics first" choice in the first-run failure path.

Impact:

- Recovery is possible, but supportability depends on user behavior.
- Reset can erase the easy path to local diagnostics unless package/share/upload is surfaced first.

## 5. Diagnostic Package and Upload Recommendations

### The support package should include

Keep the existing artifact types, but add one new state-focused artifact or equivalent payload:

- `client_state_snapshot`
  - app version/build
  - current Alpha state version and terms version
  - all `waymark.alpha1.*` values
  - computed root stage
  - generation status flag
  - in-memory generation state/progress when available
  - reviewed mission count and mission IDs
  - active mission ID and session-library counts
  - Survey session ID, current step, response counts, displayed page IDs, quarantined response counts
  - Supabase auth status, user ID presence, expiry, refresh outcome, configured function names, but no tokens/keys
  - Apple Music authorization, storefront, subscription/playback capability when available
  - diagnostic/evidence file inventory with filenames, sizes, timestamps, and payload hashes
  - last action message and last visible support error
  - reset/quarantine history when available

Continue to include:

- `apple_music_signal_payload`
- `survey_page_selection_audit`
- `survey_evidence_export`
- `mission_generation_request_packet`
- `mission_generation_result`
- `mission_import_result`
- `client_error_event`

Mission-generation diagnostics should retain:

- client request ID
- generation run ID
- backend status
- app import status
- local import status
- validation errors
- imported mission IDs/counts
- local catalog count after each attempt
- attempt number, target count, and batch slot
- failure category and whether retry is safe

### Manual versus automatic upload

Current policy should remain:

- Automatically upload nothing until privacy, retention, deletion, and support access policy approves it.
- Let testers manually upload support diagnostics after explicit consent and an authenticated Supabase session.
- Always keep local Share diagnostics as the fallback when auth/config/upload fails.

Recommended future policy after approval:

- Auto-upload minimal operational diagnostics for app-initiated remote work:
  - `client_error_event`
  - `mission_import_result`
  - `mission_generation_result` summary
  - compact `client_state_snapshot`
  - request packet hashes/refs, not full raw payloads by default
- Keep full raw/support-heavy artifacts manual unless product/legal approves automatic collection:
  - full `apple_music_signal_payload`
  - full `survey_page_selection_audit`
  - full `survey_evidence_export`
  - full `mission_generation_request_packet`
  - full raw generation response with app mission payloads
  - local evidence exports
- Evidence/reaction uploads should stay manual until evidence-specific policy approval. They are not the same as support diagnostics.

Backend posture:

- `submit-alpha-diagnostic` already accepts the seven current artifact types, requires consent, validates schema/payload, writes through service-role credentials, and reports `user_id_present`.
- Infra should add `client_state_snapshot` to the allowed artifact types if Core implements it as a first-class artifact.

## 6. Concrete Implementation Tickets

### Core Waymark Build

#### CWB-034: Make Alpha state reset policy explicit per build

Problem:

- Build 12 resumed because the state version stayed current. That is code-correct but smoke-expectation ambiguous.

Acceptance:

- Add a documented state policy: "reset on every internal smoke build" versus "reset only on state-version bump".
- Persist `last_seen_build`, `last_reset_build`, `reset_reason`, and `state_version`.
- On app update, decide deterministically whether to preserve, quarantine, or ask support/tester.
- Update build report template to say whether installing over a prior build should preserve or reset first-run state.

#### CWB-035: Add durable first-run state snapshot

Problem:

- Root route decisions are distributed across UserDefaults, Keychain auth snapshot, OS Music auth, Survey files, and mission catalog files.

Acceptance:

- Add a local `client_state_snapshot` diagnostic artifact.
- Include root-stage inputs, computed root stage, mission count, Survey summary, auth/music status, app build, and file inventory.
- Generate it on demand and when generation fails.
- Do not include tokens, Apple identity tokens, anon keys, service-role keys, or raw private credentials.

#### CWB-036: Surface diagnostics in first-run generation recovery

Problem:

- If generation fails before core unlock, Share Evidence / Support Diagnostics is not reachable from Account.

Acceptance:

- Generation screen includes:
  - Prepare Support Diagnostics
  - Share Support Diagnostics
  - Upload Diagnostics to Waymark when authenticated
  - Retry Mission Generation
  - Start Fresh after diagnostics
- If upload is unavailable, explain local share fallback.
- Reset path prompts to prepare/upload/share diagnostics first when useful.

#### CWB-037: Persist generation failure summary

Problem:

- `generation_failed` persists but the detailed failure does not.

Acceptance:

- Persist last generation failure category, message, client request ID, generation run ID if known, attempt count, imported count, and timestamp.
- On relaunch, generation screen shows the previous failure and next action.
- Failed state does not auto-retry unless tester taps Retry.

#### CWB-038: Add cancel/timeout escape from generation loading

Problem:

- `Start Fresh` is disabled while loading, and a hung network task can strand the tester.

Acceptance:

- Add request timeout and visible stuck-state recovery.
- Add Cancel Generation or Stop Waiting.
- After cancel, persist `generation_failed` or a new `generation_cancelled` state with diagnostics.
- Do not auto-resume cancelled generation without user action.

#### CWB-039: Turn root navigation into a tested reducer

Problem:

- Root behavior is currently implicit in SwiftUI computed properties and `@AppStorage`.

Acceptance:

- Extract a pure root-state evaluator with inputs for alpha defaults, auth snapshot, Music authorization, mission count, and generation status.
- Add tests for:
  - fresh install
  - update with old state version
  - build 11 to build 12 in-progress generation
  - failed generation relaunch
  - partial mission catalog
  - auth expired/recovered
  - core unlock only at 10 missions

#### CWB-040: Clarify first-run Survey resume/reset behavior

Problem:

- Survey persists partial state, but first-run intake resets on view entry.

Acceptance:

- Decide whether first-run Survey should resume partial progress or intentionally restart.
- If restart is intended, record that reset reason in diagnostics.
- If resume is intended, call `prepareRequiredAlphaIntake(resetExistingResponses: false)` or equivalent after first entry.
- Add tests for partial Survey relaunch and support reset.

#### CWB-041: Add local state inventory to support reset

Problem:

- Reset/quarantine moves roots, but support cannot easily see what was moved, cleared, or left intact.

Acceptance:

- Before reset, capture a state inventory artifact.
- After reset, capture reset result: moved paths, cleared stores, sign-out result, remaining files, and new `state_version`.
- UI should say whether diagnostics were preserved/shared/uploaded before reset.

### Supabase Infrastructure

#### INF-024: Add `client_state_snapshot` diagnostic support

Problem:

- The current backend allowlist lacks a root/app-state diagnostic artifact type.

Acceptance:

- Add `client_state_snapshot` to `submit-alpha-diagnostic`, migration check constraints, fixtures, typecheck/smoke coverage, and docs.
- Index by tester alias, user ID, source app build, survey session ID, and received timestamp.

#### INF-025: PM live-run summary should highlight root-state causes

Problem:

- PM can inspect generation/evidence/diagnostics, but state-resume causes need to be obvious.

Acceptance:

- Extend `scripts/summarize_alpha_live_run.mjs` or equivalent summary to show:
  - root stage
  - Alpha state version
  - generation status flag
  - mission count
  - last failure/cancel summary
  - auth user presence
  - build transition if available

#### INF-026: Define automatic diagnostic upload contract

Problem:

- Current policy blocks automatic uploads, but future Core behavior needs a precise allowlist.

Acceptance:

- Produce an approved policy matrix by artifact type:
  - never auto
  - auto after explicit Alpha consent
  - manual support only
  - evidence policy required
- Include retention/deletion/support-access requirements.
- Keep diagnostic uploads separate from evidence uploads and Atlas truth.

#### INF-027: Validate partial and unauthenticated support paths

Problem:

- The app can only upload diagnostics when authenticated; local share is fallback.

Acceptance:

- Confirm support runbook covers:
  - authenticated diagnostic upload
  - local package share when auth is missing
  - package upload failure
  - no generation run ID
  - no user ID
  - repeated package upload / duplicate client artifact IDs

## Bottom Line

Build 12 reopening into mission generation is most likely a consequence of preserved, current Alpha first-run state, not a failed build 11 quarantine. The state machine says: current state version plus completed terms/auth/onboarding/Survey plus non-core-ready generation equals generation screen. The urgent hardening work is not just another reset; it is making the state policy explicit, preserving a durable explanation of root decisions, and putting diagnostics/export/upload directly on the failure path before testers reset.
