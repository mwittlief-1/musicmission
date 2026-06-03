# Core Cartenza Build Backlog

Lane goal: TestFlight iOS runtime that does not ship prebuilt missions as user content, can receive/import reviewed missions after install, plays them through MusicKit, and exports Atlas-ingestion-ready evidence.

## Non-Dependent Tasks

- [x] CWB-001 Split production mission content from debug/test fixtures.
  - Remove personal mission packs from the production TestFlight user path.
  - Keep sample missions available only to tests or explicit debug builds.
  - Add a check that release/TestFlight configuration does not default to bundled user missions.
  - Completed: release build excludes prebuilt mission JSON; debug/test fixtures remain available outside the normal tester path.

- [x] CWB-002 Introduce a `MissionProvider` boundary.
  - Support at least three provider modes: remote assignment placeholder, manual JSON import, debug fixtures.
  - Keep provider selection outside normal tester UI unless support needs it.
  - Completed: provider boundary now supports local reviewed import, debug fixture loading, and a Supabase-style remote client stub/config boundary.

- [x] CWB-003 Build the missionless first-run empty state.
  - States: no mission assigned, Apple Music not connected, Apple Music connected, survey available, waiting for assignment.
  - Do not imply Cartenza already knows the user's mission.
  - Completed: normal app startup can show an empty/no-assigned-mission state instead of a bundled mission library.

- [x] CWB-004 Add reviewed mission assignment/import path.
  - Accept mission JSON after install.
  - Store imported missions locally.
  - Reject or quarantine invalid mission payloads without crashing the app.
  - Completed: reviewed mission import stores local assignments and rejects invalid payloads through the app-import gate.

- [x] CWB-005 Add app-import gate for mission JSON.
  - Require stable `mission_id` and `item_id`.
  - Require concrete route items, expected signals, player-card copy, reaction chip sets, and useful search hints.
  - Reject unresolved placeholders unless the mission is explicitly a search-calibration/debug mission.
  - Completed: `MissionImportGate` enforces stable identifiers, concrete route items, unresolved MusicKit resolution at import, expected test signal, player-card hypothesis copy, and complete chip sets for the four primary signals.

- [x] CWB-006 Preserve Atlas-ingestion-ready evidence IDs.
  - Preserve `mission_id`, `item_id`, playback event IDs, reaction operation, selected chips, shown-unselected chips, notes, MusicKit resolution metadata, device context, export ID, and timestamps.
  - Completed: session export preserves mission/item identity, playback/reaction/note/chip/resolution/device/export/timestamp evidence and emits Atlas ingestion candidate IDs.

- [x] CWB-007 Map app events toward Atlas `Signal` source types.
  - Sources to cover: `mission`, `playback`, `note`, `review`, and later `survey`.
  - Treat app exports as Atlas ingestion candidates, not direct Atlas writes.
  - Completed: export candidate bundle maps resolution, playback, skip/no-signal, reaction, chip, note, and review evidence into ingestion candidates with no direct Atlas truth writes.

- [x] CWB-008 Harden local persistence without bundled mission assumptions.
  - Relaunch should restore assigned/imported missions, selected item, playback records, reactions, notes, review edits, and export history.
  - Completed: session persistence restores imported/assigned missions, selection, playback records, reactions, tags, notes, review edits, and saved export history.

- [x] CWB-009 Add reset/recover behavior for local Alpha data.
  - Include a tester-safe reset path for stuck sessions.
  - Avoid deleting evidence accidentally without confirmation.
  - Completed: tester reset path clears reviewed mission assignments and local sessions only after confirmation.

- [x] CWB-010 Hide diagnostics from the normal Alpha path.
  - Resolver status, export preview, raw JSON, and debug provider controls should be available for support but not dominate the listening flow.
  - Completed: diagnostics, raw JSON/Markdown preview, Apple Music probe, and survey/resolve debug surfaces are feature-gated out of the normal Release path.

- [x] CWB-011 Physical-device MusicKit QA checklist.
  - Full mission playback, pause/resume, seek, next/skip, auto-advance, unavailable item, wrong/ambiguous resolution, relaunch, export/share.
  - QA must distinguish physical iPhone evidence from simulator/stub evidence.
  - Completed: checklist added in `docs/app_dev/physical_device_musickit_qa_checklist.md`; physical-device execution remains a release QA activity.

- [x] CWB-012 Add TestFlight packaging checklist in repo.
  - Build/version increment discipline, signing, bundle ID, MusicKit capability, app icon placeholder, privacy/support fields, internal/external tester path.
  - Completed: packaging checklist added in `docs/app_dev/testflight_packaging_checklist.md`.

- [x] CWB-013 App-side Supabase client stub.
  - Add configuration shape and client boundary without hardcoding secrets.
  - If Supabase project is unavailable, use a local stub that consumes the golden packet response shape.
  - Completed: Supabase config/client boundary and local golden-packet stub were added without hardcoded secrets.

- [x] CWB-014 Wire mission response adapter tests.
  - Validate `mission.v0.2` payloads coming from the backend/golden-packet response.
  - Keep schema validity separate from app-import/product readiness.
  - Completed: adapter/import tests cover golden-packet response shape, strict app-import candidate readiness, and schema/product-readiness separation.

- [x] CWB-015 Survey renderer protocol, behind feature gate.
  - Build against fixture/app packet protocol while Survey finalizes app packet contract.
  - Keep Survey optional for the first TestFlight build until product decides visibility.
  - Completed: Survey page provider protocol and fixture provider were added; Survey is feature-gated out of Release pending product visibility decision.

- [x] CWB-016 Export envelope for Atlas ingestion candidates.
  - Add or document export shape that can carry session evidence into `Signal -> AtlasDigestView -> AtlasDelta`.
  - Include source app version/build and physical-device context.
  - Completed: `atlas_signal_candidate_bundle` export envelope includes source app version and physical-device context with candidate guardrails.

- [x] CWB-017 Alpha user flow smoke test.
  - No bundled missions -> connect Apple Music -> import/receive mission -> resolve/play -> react/chip/note -> relaunch -> export.
  - Completed: smoke-style XCTest covers missionless import, listen/reaction evidence, relaunch persistence, and export.

## Post-Brand Review Alpha 1 Tasks

Product decisions received 2026-05-22 reopen Core work for the guided first-run Alpha path.

- [x] CWB-018 Build first-run state machine.
  - Required order: privacy/terms -> Apple ID + Apple Music -> onboarding -> Survey -> generation wait -> core IA.
  - Persist completion state for consent, onboarding, Survey, generation, and first mission batch availability.
  - Completed: `RootView` now gates the app through consent, account/music access, onboarding, required Survey, generation status, then the core IA using local persistent Alpha 1 state.

- [x] CWB-019 Add privacy/terms gate.
  - First launch only unless terms version changes.
  - Must block Survey and evidence upload until accepted.
  - Completed: first launch now starts with a versioned Alpha acknowledgement gate before access, Survey, core IA, or upload paths. Copy is placeholder pending Release/Product approval.

- [x] CWB-020 Add Sign in with Apple + Apple Music connection step.
  - Present as one simple user action/screen.
  - Keep the implementation honest: Apple ID auth and MusicKit authorization are separate capabilities.
  - Persist session as long as possible and provide timed-out reauth state.
  - Completed: first-run access screen combines Sign in with Apple UI and Apple Music authorization in one guided step, with separate capability language. Live Supabase session exchange, Keychain persistence, timeout/reauth state, and session-JWT handoff were wired in CWB-029; a Release device build now archives, exports, and installs locally on the paired iPhone.

- [x] CWB-021 Add guided onboarding walkthrough and returning-user FAQ shell.
  - Use placeholder/copy slots until founder supplies final onboarding and FAQ copy.
  - FAQ belongs under My Account after onboarding.
  - Completed: guided onboarding shell added before Survey; returning-user FAQ/support lives under My Account.

- [x] CWB-022 Make Survey release-facing as required first-run intake.
  - Force 4 artist pages, 2 album pages, and 4 song pages for Alpha.
  - Do not expose Survey as a normal post-intake tab; move optional revisit/support entry to My Account.
  - Completed: first-run Survey is release-facing and forced through 4 artist, 2 album, and 4 song pages. Normal Release tabs do not expose Survey; My Account has a support revisit path.

- [x] CWB-023 Add post-Survey generation status surface.
  - Message that Cartenza is building the user's Atlas and first missions.
  - Preserve provisional/evidence language; do not imply promoted Atlas truth.
  - Completed: post-Survey generation surface says Cartenza is building the Atlas/first missions while preserving provisional evidence language and no promoted truth claim.

- [x] CWB-024 Reframe core IA after intake.
  - Normal path: mission batch -> player -> review -> Share Evidence/sync -> My Account.
  - Hide paste/import JSON and implementation language from normal testers when remote generation is live.
  - Completed: core tabs appear only after first-run intake and now include Mission, Player, Review, Evidence, and My Account. Manual import remains as support fallback until live remote generation is available.

- [ ] CWB-025 Rename and release-polish shell.
  - App display name: Cartenza.
  - Dark mode only for Alpha.
  - Portrait-only for Alpha iPhone builds.
  - Add app icon asset catalog once candidates are approved.
  - Partially completed: app display name is `Cartenza`, Alpha surfaces force dark mode, iPhone/iPad supported orientations are portrait-only with full-screen required, and an Alpha placeholder `AppIcon` asset catalog is bundled for TestFlight packaging. Final app icon art remains blocked on approved candidates.

- [x] CWB-026 Reframe Export as Share Evidence.
  - Remove schema/dev/acceptance language from the normal Alpha path.
  - Keep manual Share Evidence as fallback/support even if Supabase upload is added.
  - Completed: normal Evidence tab is titled Share Evidence and hides schema/dev/acceptance language unless debug panels are enabled. Manual Share Evidence remains available.

- [x] CWB-027 Add evidence upload client boundary.
  - Blocked until Infra provides endpoint/auth policy and Release approves privacy/retention copy.
  - Preserve local export/share fallback.
  - Completed: app-side `EvidenceUploadClient` boundary, config shape, request/result models, cadence enum, local no-upload stub, and live Supabase function client are in place. Automatic upload remains blocked by final privacy/retention/deletion/support policy; manual authenticated upload is available after Supabase sign-in.

- [x] CWB-028 Apply approved Alpha orientation wireframes to SwiftUI.
  - Source: `docs/app_dev/mockups/alpha_orientation_flow_v0_1/index.html`.
  - Handoff: `docs/app_dev/mockups/alpha_orientation_flow_v0_1/IMPLEMENTATION_HANDOFF.md`.
  - Scope: first-run gates, onboarding, FAQ, required Survey, generation status, mission home/detail, Player, Review/edit evidence, My Account, Share Evidence backup.
  - Build now: layout, hierarchy, dark mobile-first styling, navigation, and local state behavior.
  - Still respect blockers for final legal/privacy copy, automatic upload policy, Supabase authenticated smoke, and final app icon art.
  - Completed: approved Alpha orientation wireframes were applied to the SwiftUI shell, first-run flow, mission home/detail, player action rail, mission review/edit evidence, account/FAQ, Survey labels, and Share Evidence backup entry. Final legal/privacy copy, automatic upload policy, Supabase authenticated smoke, and app icon art remain separate blockers.

- [ ] CWB-029 Wire live Supabase Auth, generation, and evidence calls.
  - Dispatch: `docs/app_dev/core_live_auth_generation_dispatch_2026_05_22.md`.
  - Replace local-only Apple ID completion with Sign in with Apple -> Supabase Auth session.
  - Add the Sign in with Apple app capability/entitlements if missing.
  - Use the Supabase session access token for `generate-first-mission-batch` and `submit-alpha-evidence`.
  - Trigger first mission generation after required Survey completion and import only `status=app_import_candidate`.
  - Keep automatic evidence upload disabled until privacy/retention/deletion/support policy is approved; manual Share Evidence Backup remains visible.
  - Device smoke target: a new iPhone/TestFlight build signs in through Supabase Auth, generation persists an `alpha_generation_runs` row, and evidence upload persists an `alpha_evidence_artifacts` row with `user_id_present=true`.
  - Partially completed: code-side live Supabase Auth, Keychain session persistence, session-JWT generation/evidence clients, post-Survey generation trigger, strict `app_import_candidate` import, manual authenticated evidence upload, Sign in with Apple entitlement, app-safe config keys, request header tests, one-time Alpha clean-state migration, and TestFlight export-compliance flag are implemented. Simulator tests pass. Release archive, local device export, local iPhone install, and App Store Connect/TestFlight upload pass. Authenticated on-device generation/evidence row smoke is still pending.

### CWB-029 Implementation Addendum

- files changed:
  - `MusicAtlasController.xcodeproj/project.pbxproj`
  - `MusicAtlasController/Models/AppModel.swift`
  - `MusicAtlasController/Services/MissionLoader.swift`
  - `MusicAtlasController/Services/SessionExporter.swift`
  - `MusicAtlasController/Services/SurveyStore.swift`
  - `MusicAtlasController/Support/Info.plist`
  - `MusicAtlasController/Support/MusicAtlasController.entitlements`
  - `MusicAtlasController/Resources/Assets.xcassets`
  - `MusicAtlasController/Views/ExportPreviewView.swift`
  - `MusicAtlasController/Views/RootView.swift`
  - `MusicAtlasControllerTests/MissionDecodingTests.swift`
  - `MusicAtlasControllerTests/SessionExporterTests.swift`
  - `docs/alpha_backlog/core_waymark_build.md`
- code guardrails enforced:
  - First-run account gate now checks a real Supabase Auth snapshot plus Apple Music authorization, not a local Apple-ID boolean.
  - Sign in with Apple request uses a raw nonce, SHA-256 Apple nonce, Apple identity token extraction, and Supabase `id_token` exchange.
  - Supabase session is persisted in Keychain and refreshed when possible.
  - `generate-first-mission-batch` and `submit-alpha-evidence` request builders send the publishable key plus `Authorization: Bearer <Supabase session access_token>`.
  - First mission generation triggers after required Survey completion and imports only through the existing `app_import_candidate` gate.
  - Automatic evidence upload remains disabled; the UI exposes manual upload only after a saved evidence package and authenticated Supabase session.
  - App config stores project URL/function names/tester alias in Info.plist and injects the publishable key via build setting.
- tests run:
  - `xcodebuild -scheme MusicAtlasController -configuration Debug -sdk iphonesimulator build`
  - `xcodebuild -scheme MusicAtlasController -configuration Debug -sdk iphonesimulator -destination 'platform=iOS Simulator,name=iPhone 17,OS=26.5' test`
  - `xcodebuild -scheme MusicAtlasController -configuration Release -destination 'generic/platform=iOS' -archivePath "$PWD/build/Waymark-Alpha1-20260522.xcarchive" -allowProvisioningUpdates archive`
  - `xcodebuild -exportArchive -archivePath "$PWD/build/Waymark-Alpha1-20260522.xcarchive" -exportPath "$PWD/build/DeviceSmokeExport" -exportOptionsPlist "$PWD/build/ExportOptions-DeviceSmoke.plist" -allowProvisioningUpdates`
  - `xcrun devicectl device install app --device FB8C134C-84DF-541F-BBE9-31412F792800 "$PWD/build/Waymark-Alpha1-20260522.xcarchive/Products/Applications/MusicAtlasController.app"`
  - `xcodebuild -exportArchive -archivePath "$PWD/build/Waymark-Alpha1-20260522.xcarchive" -exportPath "$PWD/build/TestFlightUpload" -exportOptionsPlist "$PWD/build/ExportOptions-TestFlight.plist" -allowProvisioningUpdates`
  - `xcodebuild -scheme MusicAtlasController -configuration Release -destination 'generic/platform=iOS' -archivePath "$PWD/build/Waymark-Alpha1-20260523.xcarchive" -allowProvisioningUpdates archive`
  - `xcodebuild -exportArchive -archivePath "$PWD/build/Waymark-Alpha1-20260523.xcarchive" -exportPath "$PWD/build/TestFlightUpload" -exportOptionsPlist "$PWD/build/ExportOptions-TestFlight.plist" -allowProvisioningUpdates`
  - `xcodebuild -scheme MusicAtlasController -configuration Release -destination 'generic/platform=iOS' -archivePath "$PWD/build/Waymark-Alpha1-20260523-b3.xcarchive" -allowProvisioningUpdates archive`
  - `xcodebuild -exportArchive -archivePath "$PWD/build/Waymark-Alpha1-20260523-b3.xcarchive" -exportPath "$PWD/build/TestFlightUpload" -exportOptionsPlist "$PWD/build/ExportOptions-TestFlight.plist" -allowProvisioningUpdates`
  - `plutil -lint MusicAtlasController/Support/Info.plist`
  - `xcodebuild -scheme MusicAtlasController -configuration Release -destination 'generic/platform=iOS' -archivePath "$PWD/build/Waymark-Alpha1-20260523-b4.xcarchive" -allowProvisioningUpdates archive`
  - `xcodebuild -exportArchive -archivePath "$PWD/build/Waymark-Alpha1-20260523-b4.xcarchive" -exportPath "$PWD/build/TestFlightUpload" -exportOptionsPlist "$PWD/build/ExportOptions-TestFlight.plist" -allowProvisioningUpdates`
- result:
  - Debug simulator build passed.
  - Full XCTest suite passed.
  - Release archive passed with Sign in with Apple entitlement in the refreshed profile.
  - Local device export passed and produced `build/DeviceSmokeExport/MusicAtlasController.ipa`.
  - Local install to Matt's paired iPhone passed; the device reports Waymark `0.2` build `2` installed.
  - Device launch from CLI was denied only because the iPhone was locked.
  - First TestFlight upload/export reached App Store Connect validation and failed on missing icon catalog / `CFBundleIconName` and iPad full-screen orientation packaging.
  - Added Alpha placeholder AppIcon asset catalog, `CFBundleIconName`, and `UIRequiresFullScreen`.
  - Rebuilt Release archive at `build/Waymark-Alpha1-20260523.xcarchive`.
  - App Store Connect/TestFlight upload succeeded; uploaded package is processing.
  - Build 3 added a one-time Alpha state migration that clears stale Survey, mission, session, export, and Supabase auth state on existing installs so testers restart at the first-run Survey path.
  - Build 3 also treats one imported `app_import_candidate` mission as a usable recovery state if later generation calls fail, while still targeting a 10-mission Alpha batch.
  - Build 4 added `ITSAppUsesNonExemptEncryption=false` and uploaded successfully to App Store Connect; uploaded package is processing.
- ready for Core app integration status:
  - `yes_code_complete_for_cwb_029`
  - `yes_release_archive_and_local_device_install_complete`
  - `yes_testflight_build_4_upload_succeeded`
  - `pending_authenticated_device_smoke_for_generation_and_evidence_rows`

### CWB-029 Fresh Intake / Partial Generation Recovery Addendum

- user-reported TestFlight findings addressed:
  - Existing install did not restart at Survey because prior Alpha state was still locally valid.
  - Mission generation could import one mission and then fail the overall generation run, leaving the tester blocked even though one reviewed mission was available.
- code behavior changed:
  - `RootView` now owns a versioned Alpha state migration. When `alpha1_clean_intake_2026_05_23_01` is not present, the app clears first-run flags and calls `resetAllLocalAlphaState(signOut: true)` before loading missions.
  - `resetAllLocalAlphaState` clears reviewed mission assignments, persisted sessions, saved exports, active mission/player state, Survey persistence, generation status, and the Supabase Keychain session.
  - `SurveyPersistenceStore.reset()` removes the local Survey response file.
  - Generation still targets 10 missions, but one valid imported `app_import_candidate` mission is now enough to enter the core app if a later generation step fails.
  - App Store export compliance now declares no non-exempt encryption with `ITSAppUsesNonExemptEncryption=false`.
- files changed:
  - `MusicAtlasController.xcodeproj/project.pbxproj`
  - `MusicAtlasController/Models/AppModel.swift`
  - `MusicAtlasController/Services/SurveyStore.swift`
  - `MusicAtlasController/Support/Info.plist`
  - `MusicAtlasController/Views/RootView.swift`
  - `docs/alpha_backlog/core_waymark_build.md`
- tests/builds run:
  - `xcodebuild -scheme MusicAtlasController -configuration Debug -sdk iphonesimulator build`
  - `xcodebuild -scheme MusicAtlasController -configuration Debug -sdk iphonesimulator -destination 'platform=iOS Simulator,name=iPhone 17,OS=26.5' test`
  - `plutil -lint MusicAtlasController/Support/Info.plist`
  - Release archive/export/upload for build 3.
  - Release archive/export/upload for build 4.
- result:
  - TestFlight build 4 was superseded by later Alpha recovery builds.
  - Expected first launch after update: old Alpha-local state is forgotten, user is signed out, and the app starts at the first-run acknowledgement/access/Survey flow.
  - Expected generation recovery in build 4: if Supabase creates/imports at least one app-importable mission and a subsequent generation request fails, the app should allow testing with the available mission instead of blocking the core app. This was superseded by build 11, which keeps the core app locked until all 10 Alpha missions are available and exposes Retry / Start Fresh instead.

### Build 11 Fresh-Read Quarantine Addendum

- user-reported TestFlight finding addressed:
  - Existing install opened directly into mission generation because the prior Alpha state version was still considered valid.
  - Mission generation could fail repeatedly with no route out of the generation screen.
  - One imported mission could still be treated as enough to unlock the core app, despite the Alpha target being 10 generated missions.
- code behavior changed:
  - `RootView` now bumps the Alpha state version to `alpha1_fresh_read_quarantine_2026_05_24_01`.
  - Alpha first-run `UserDefaults` keys under `waymark.alpha1.` are purged when the state version changes or support reset is tapped.
  - `resetAllLocalAlphaState(signOut: true)` quarantines known local app roots before clearing stores.
  - Generation failure is persisted as `generation_failed`, so relaunch does not automatically re-enter a failed retry loop.
  - `GenerationStatusView` exposes `Start Fresh` during generation/recovery.
  - First-run core unlock now requires the full 10-mission batch.
- tests/builds run:
  - `plutil -lint MusicAtlasController/Support/Info.plist`
  - `git diff --check -- MusicAtlasController/Views/RootView.swift MusicAtlasController/Models/AppModel.swift MusicAtlasControllerTests/SessionExporterTests.swift MusicAtlasController/Support/Info.plist MusicAtlasController.xcodeproj/project.pbxproj`
  - `COPYFILE_DISABLE=1 xcodebuild -scheme MusicAtlasController -configuration Debug -sdk iphonesimulator -destination 'platform=iOS Simulator,name=iPhone 17,OS=26.5' -derivedDataPath /tmp/musicmission-fresh-read-build-11/DerivedData test`
  - Release archive/export/upload for build 11.
- result:
  - TestFlight build 11 uploaded successfully and is the next physical smoke candidate after App Store Connect processing completes.
  - Expected first launch after update: old local Alpha files are quarantined, the tester is signed out, and the app starts at Alpha Access.
  - Expected generation behavior: the app keeps targeting 10 missions, shows progress/retry/reset controls, and does not unlock the core app until 10 app-ready missions are available.

## Live Alpha Smoke Recovery Tasks

Source: `docs/alpha_backlog/alpha_live_smoke_recovery_2026_05_24.md`.

- [x] CWB-030 Make post-Survey generation resilient to review-gated attempts.
  - Continue mission generation attempts after an isolated `review_needed` response until the app imports `10` missions, reaches a hard failure, or hits a bounded max-attempt ceiling.
  - Preserve the existing rule that only app-valid missions can enter the local mission library.
  - Record skipped/review-gated run IDs and statuses in local diagnostic state for upload/export.
  - Acceptance: one `app_import_candidate`, then one `review_needed`, then another `app_import_candidate` produces at least two imported missions and does not strand the tester on the generation screen.
  - Completed: post-Survey generation now runs a bounded multi-attempt loop, records request/result/import/error diagnostics, continues past isolated review-gated attempts, imports only locally app-valid missions, and still rejects blocked/non-app-valid responses.

- [x] CWB-031 Add client diagnostic artifact capture and manual upload/export.
  - Capture support-only artifacts for:
    - `apple_music_signal_payload`
    - `survey_page_selection_audit`
    - `survey_evidence_export`
    - `mission_generation_request_packet`
    - `mission_generation_result`
    - `mission_import_result`
    - `client_error_event`
  - Link artifacts by tester alias, Supabase user ID when available, survey session ID, client request ID, generation run ID, mission ID, app version, and build.
  - Keep artifacts hidden from normal tester UI; expose only through Share Evidence / support diagnostics.
  - Do not enable automatic upload until final privacy/retention/deletion/support policy is approved.
  - Completed: app-local support diagnostic artifacts and package export are available through Share Evidence support diagnostics. Manual authenticated diagnostic upload is wired to Supabase; automatic upload remains blocked on CWB-I002/CWB-I004 policy guardrails.

- [x] CWB-032 Persist Survey runtime audit data needed for PM reconstruction.
  - For each displayed page, persist page ID, step, tile IDs, typed refs, source mix, Apple exposure flags, candidate basis, page intent, prior-response summary inputs, and visible history.
  - Exclude hidden simulator truth, raw scorer internals, prompts, and private construction-only tags.
  - Acceptance: a local diagnostic export can explain why every displayed tile appeared and why every response is Atlas-ingestable or quarantined.
  - Completed: Survey diagnostic export now emits a page-selection audit with displayed tiles, typed refs, source/objective mix, Apple exposure priors, candidate basis, page intent, prior-response summary, visible history, and quarantined response counts while excluding hidden scorer internals/prompts.

- [ ] CWB-033 Produce next device-smoke report from live build.
  - Run the next physical/TestFlight pass after `CWB-030` and `CWB-031`.
  - Record build number, auth status, Survey counts, quarantined response count/reasons, generation attempt count, imported mission count, run IDs, upload IDs, and any visible UX issue.
  - Output: append a device-smoke addendum to this file or create a dated report under `docs/app_dev/`.

## Dependency Tripwires

Raise an issue when:

- Survey UI implementation needs final Survey app packet fields.
- App copy requires privacy, trust, retention, deletion, or support policy.
- First-run auth requires Sign in with Apple capability, Supabase auth policy, or account session contract.
- A UI wants to show `AtlasDelta.user_facing_summary_inputs` as user-facing copy.
- Supabase client needs real project URL, anon key, Edge Function URL, or auth policy.
- Evidence upload needs endpoint, upload cadence, tester identity, privacy/retention/deletion policy, or support access policy.
- App evidence export needs final Atlas ingestion field names beyond the v0.1 contract.
- Release packaging needs final app name, icon, bundle ID rename, or tester group policy.

## Do Not Do Yet

- Do not ship personal mission packs as TestFlight user content.
- Do not generate missions locally in the app.
- Do not write promoted Atlas state from the app.
- Do not treat skip/no-signal as automatic dislike.
- Do not let debug fixtures appear as a normal tester mission library.

## Raised Issues

| issue id | blocker | owner lane | needed for | current workaround | status |
| --- | --- | --- | --- | --- | --- |
| CWB-I002 | Final privacy, terms, retention, deletion, and support copy is not approved. | Brand / Design / Release | External TestFlight consent gate and any automatic evidence upload. | Placeholder Alpha acknowledgement blocks first-run until accepted; manual Share Evidence remains fallback. | open |
| CWB-I003 | App-side Supabase Auth is wired and TestFlight build 11 is uploaded, but authenticated on-device smoke still needs to run through Sign in with Apple, generation, evidence upload, and diagnostic upload. | Core / Release QA | Durable account identity, timeout/reauth behavior, authenticated generation, evidence upload identity, diagnostic upload identity, CWB-029/CWB-033 device smoke. | Simulator build/tests pass. Release archive and App Store Connect upload pass. TestFlight build 11 includes fresh-read quarantine, failed-generation escape/reset, full 10-mission unlock gating, and manual support diagnostic upload; install it when processing completes and verify Supabase rows. | open |
| CWB-I004 | Evidence upload endpoint and app live client are wired, but automatic upload policy is still not approved. Authenticated manual upload needs physical-device smoke. | Release Policy + Core QA | CWB-027 live evidence upload/sync and app-authenticated evidence smoke. | Manual Share Evidence remains fallback. App manual upload sends the Supabase session JWT after device sign-in; automatic upload remains disabled. | open |
| CWB-I005 | Final Cartenza app icon candidates are not approved. | Brand / Design / Release | CWB-025 external polish. | Display name, dark mode, portrait-only restrictions, and an Alpha placeholder AppIcon catalog are implemented. Replace placeholder with approved art before broader external polish. | open |
| CWB-I006 | TestFlight upload/export was blocked until App Store Connect had an app record for bundle ID `com.vytisstudios.MusicAtlasController`. | Release / Apple Account Owner | TestFlight distribution for CWB-029 smoke. | Resolved 2026-05-23: App Store Connect/TestFlight upload succeeded after app record/account access was available and icon/orientation packaging was fixed. | closed |
| CWB-I007 | Release Survey was still backed by the legacy fixture provider; Core needed Apple-exposure-biased, canonical-graph-backed, Page N+1 adaptive Survey behavior without fabricated app-side taste guesses. | Survey Simulator + Canonical Music Graph + Core | Replace TestFlight Survey fixtures with Apple-exposure-biased, canonical-graph-backed, Page N+1 adaptive Survey packets. | Resolved by bundled Alpha canonical graph/survey surfaces plus `AlphaDynamicSurveyPageProvider`. The provider uses Apple exposure as prior, falls back to canonical graph, dedupes prior visible items, and adapts from prior responses. Caveat: dynamic ranking currently lives in app code for Alpha; keep a future product/architecture decision open on moving this to a Survey service. | closed_for_alpha |
| CWB-I008 | Manual app-side diagnostic upload is wired to the Supabase `submit-alpha-diagnostic` endpoint, but authenticated physical-device smoke still needs to prove rows land with `user_id_present=true`. | Core QA / Infra | CWB-031 backend-side PM reconstruction without ShareLink files. | Support diagnostics can still be generated locally from Share Evidence and shared manually. Automatic upload remains blocked by CWB-I002/CWB-I004 policy guardrails. | open |

Post-brand pass raised the concrete cross-lane blockers above. Existing dependency tripwires still apply.

Approved wireframe update 2026-05-22: Product/Founder approved the HTML mockups at `docs/app_dev/mockups/alpha_orientation_flow_v0_1/index.html` for Alpha 1 Swift implementation. CWB-028 is now the primary non-dependent UI implementation task for Core/UI.

## Completion Report

- files changed:
  - `.gitignore`
  - `MusicAtlasController.xcodeproj/project.pbxproj`
  - `MusicAtlasController/Models/AppModel.swift`
  - `MusicAtlasController/Models/Mission.swift`
  - `MusicAtlasController/Models/ReactionSession.swift`
  - `MusicAtlasController/Models/Survey.swift`
  - `MusicAtlasController/Resources/schema_reaction_session_v0_2.json`
  - `MusicAtlasController/Services/MissionLoader.swift`
  - `MusicAtlasController/Services/SessionExporter.swift`
  - `MusicAtlasController/Services/SessionPersistenceStore.swift`
  - `MusicAtlasController/Services/SurveyStore.swift`
  - `MusicAtlasController/Views/ExportPreviewView.swift`
  - `MusicAtlasController/Views/MissionListView.swift`
  - `MusicAtlasController/Views/RootView.swift`
  - `MusicAtlasControllerTests/MissionDecodingTests.swift`
  - `MusicAtlasControllerTests/SessionExporterTests.swift`
  - `docs/app_dev/physical_device_musickit_qa_checklist.md`
  - `docs/app_dev/testflight_packaging_checklist.md`
  - `docs/alpha_backlog/core_waymark_build.md`
- tests run:
  - `jq empty MusicAtlasController/Resources/schema_reaction_session_v0_2.json`
  - `xcodebuild test -scheme MusicAtlasController -destination 'platform=iOS Simulator,name=iPhone 17'`
  - `xcodebuild -scheme MusicAtlasController -configuration Release -destination 'platform=iOS Simulator,name=iPhone 17' clean build`
  - Release app bundle scan for `sample_mission*.json` and `waymark_matt_10_personal_missions_v0_1.json` returned no files.
- device QA performed:
  - Not executed in this pass. Physical-device checklist was added; simulator tests and Release build/package checks passed.
- additional hygiene:
  - Verified `MusicAtlasController/Views/MissionListView 2.swift` was an untracked accidental duplicate of the older mission list screen, not referenced by the Xcode project, and removed it.
- remaining blockers:
  - Real Supabase project URL, anon key, Edge Function URL, and auth policy remain Infra/Product dependencies before live remote assignment.
  - Final Survey app packet field names and first-TestFlight Survey visibility remain Survey/Product dependencies.
  - Final privacy, retention, deletion, and support copy remain Release/Product dependencies.
  - Final app name, icon, bundle ID rename, and tester group policy remain Release/Design dependencies.
  - Final Atlas ingestion field names beyond the `atlas_signal_candidate_bundle.v0.1` app contract remain Atlas lane dependencies.
- ready for Core app integration status: `yes_with_caveats`

## CWB-029 Device Smoke Follow-Up Addendum

- user-reported device findings addressed:
  - Required first-run Survey intake now clears any persisted prior responses/freeform carryover before starting at Artist Grid 1.
  - Post-Survey generation now fills the Alpha batch toward 10 missions instead of accepting a single imported mission as complete.
  - Generation screen now shows an active spinner plus determinate mission-count progress while Supabase generation is running.
  - Existing installs with fewer than 10 reviewed/generated missions resume the generation step after auth/session refresh.
  - Normal Release UI hides MusicKit environment checks, manual import/reset controls, and resolver status badges from the tester path; playback still auto-resolves with MusicKit when needed.
- files changed:
  - `MusicAtlasController/Models/AppModel.swift`
  - `MusicAtlasController/Services/MissionLoader.swift`
  - `MusicAtlasController/Services/SurveyStore.swift`
  - `MusicAtlasController/Views/RootView.swift`
  - `MusicAtlasController/Views/MissionListView.swift`
  - `MusicAtlasController/Views/MissionDetailView.swift`
  - `MusicAtlasController/Views/MusicAuthorizationPanel.swift`
  - `MusicAtlasControllerTests/SurveyTests.swift`
- tests run:
  - `xcodebuild test -scheme MusicAtlasController -destination 'platform=iOS Simulator,name=iPhone 17'`
  - `xcodebuild build -scheme MusicAtlasController -configuration Release -destination 'generic/platform=iOS Simulator'`
- remaining caveat:
  - The live Edge Function still generates one mission per request; the app fills the 10-mission Alpha batch by issuing one generation request per missing slot.

## Post-Brand Alpha 1 Completion Addendum

- files changed:
  - `MusicAtlasController/Models/Survey.swift`
  - `MusicAtlasController/Services/SessionExporter.swift`
  - `MusicAtlasController/Services/SurveyFixtureLibrary.swift`
  - `MusicAtlasController/Services/SurveyStore.swift`
  - `MusicAtlasController/Support/Info.plist`
  - `MusicAtlasController/Views/ExportPreviewView.swift`
  - `MusicAtlasController/Views/RootView.swift`
  - `MusicAtlasController/Views/SurveyView.swift`
  - `MusicAtlasControllerTests/SurveyTests.swift`
  - `docs/alpha_backlog/core_waymark_build.md`
- tests run:
  - `plutil -p MusicAtlasController/Support/Info.plist`
  - `jq empty MusicAtlasController/Resources/schema_reaction_session_v0_2.json`
  - `xcodebuild test -scheme MusicAtlasController -destination 'platform=iOS Simulator,name=iPhone 17'`
  - `xcodebuild -scheme MusicAtlasController -configuration Release -destination 'platform=iOS Simulator,name=iPhone 17' clean build`
  - Release app bundle scan for `sample_mission*.json` and `waymark_matt_10_personal_missions_v0_1.json` returned no files.
  - Release app `Info.plist` check confirmed `CFBundleDisplayName=Cartenza`, `UIUserInterfaceStyle=Dark`, and portrait-only supported orientations.
- device QA performed:
  - Not executed in this pass.
- guardrails enforced in code:
  - First-run blocks Survey/core IA until Alpha acknowledgement is accepted.
  - Required Survey intake is 4 artist pages, 2 album pages, and 4 song pages.
  - Core IA appears only after first-run Survey reaches generation status.
  - Normal Release path keeps Survey out of the top-level tab shell after intake.
  - Share Evidence hides schema/dev/acceptance language from normal Alpha users.
  - App display name is `Cartenza`.
  - Alpha runtime is dark-mode-only and portrait-only through Info.plist/root styling.
  - No prebuilt mission Release guardrail remains intact.
- remaining blockers:
  - CWB-I002 final privacy/terms/retention/deletion/support copy.
  - CWB-I003 live account/auth capability and Supabase account policy.
  - CWB-I004 live evidence upload endpoint/auth/cadence/policy.
  - CWB-I005 approved app icon candidates.

## CWB-028 Completion Addendum

- files changed:
  - `MusicAtlasController/Models/Survey.swift`
  - `MusicAtlasController/Views/RootView.swift`
  - `MusicAtlasController/Views/MissionListView.swift`
  - `MusicAtlasController/Views/MissionDetailView.swift`
  - `MusicAtlasController/Views/NowTestingView.swift`
  - `MusicAtlasController/Views/MissionReviewView.swift`
  - `MusicAtlasController/Views/SurveyView.swift`
  - `docs/alpha_backlog/core_waymark_build.md`
- tests run:
  - `xcodebuild test -scheme MusicAtlasController -destination 'platform=iOS Simulator,name=iPhone 17'`
  - `xcodebuild -scheme MusicAtlasController -configuration Release -destination 'platform=iOS Simulator,name=iPhone 17' clean build`
  - Release app bundle scan for `sample_mission*.json` and `waymark_matt_10_personal_missions_v0_1.json` returned no files.
- guardrails enforced in code:
  - Release core tabs keep Survey, Resolve, and raw Evidence/debug panels out of the normal tester path.
  - Share Evidence backup remains reachable from My Account.
  - Player support-only Resolve Issue action is debug-only.
  - Survey display labels now use the approved Alpha rhythm: `Don't Know`, `Ok`, `Like`, `Love`, `No`.
  - First-run onboarding uses the approved six-page orientation hierarchy and provisional-evidence language.
- remaining blockers:
  - CWB-I002 final privacy/terms/retention/deletion/support copy.
  - CWB-I003 live account/auth capability and Supabase account policy.
  - CWB-I004 evidence upload endpoint/auth/cadence/privacy policy.
  - CWB-I005 final app icon candidates.
- ready for Core app integration status: `yes_with_caveats`

## Live Alpha Smoke Recovery Addendum

- files changed:
  - `MusicAtlasController/Models/AppModel.swift`
  - `MusicAtlasController/Models/Survey.swift`
  - `MusicAtlasController/Services/MissionLoader.swift`
  - `MusicAtlasController/Services/SessionExporter.swift`
  - `MusicAtlasController/Services/SurveyStore.swift`
  - `MusicAtlasController/Views/ExportPreviewView.swift`
  - `MusicAtlasControllerTests/MissionDecodingTests.swift`
  - `MusicAtlasControllerTests/SurveyTests.swift`
  - `docs/alpha_backlog/core_waymark_build.md`
- guardrails enforced in code:
  - `blocked` generation responses are still rejected and cannot enter the local mission library.
  - `review_needed` responses are only imported if they contain locally app-valid missions; otherwise they are skipped and recorded as review-gated diagnostics.
  - App diagnostic artifacts are local support exports or manual authenticated Supabase uploads, not automatic uploads and not Atlas truth.
  - Survey page audits exclude hidden simulator truth, raw scorer internals, prompts, and private construction-only tags.
- tests run:
  - `COPYFILE_DISABLE=1 xcodebuild -scheme MusicAtlasController -configuration Debug -sdk iphonesimulator -destination 'platform=iOS Simulator,name=iPhone 17,OS=26.5' -derivedDataPath /tmp/musicmission-codex-test/build/DerivedData test`
- result:
  - Full simulator XCTest pass succeeded from a clean temp copy.
  - CWB-030, CWB-031, and CWB-032 are code-complete for app-local Alpha support.
  - CWB-033 remains pending until the next physical/TestFlight smoke pass.
- ready for Core app integration status: `yes_with_caveats`
