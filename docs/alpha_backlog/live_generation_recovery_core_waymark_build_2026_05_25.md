# Core Waymark Build Dispatch - Live Generation Recovery - 2026-05-25

## Mission

Make the iOS Alpha generation flow resilient: import 10 valid missions, skip bad attempts, upload diagnostics, and never strand the tester.

## Read First

- `docs/alpha_backlog/live_generation_recovery_dispatch_2026_05_25.md`
- `docs/infra/waymark_alpha_live_diagnostic_evidence_review_2026_05_25.md`
- `docs/app_dev/waymark_alpha_app_state_recovery_diagnostics_audit_2026_05_25.md`

## P0 Tasks

- [ ] CWB-LGR-001 Wait for Infrastructure deploy before packaging.
  - Do not package a new TestFlight build until Infrastructure confirms live `generate-first-mission-batch` and `submit-alpha-diagnostic` are deployed.
  - Status: blocked on `CWB-LGR-I001`; no new TestFlight package produced in this pass.

- [x] CWB-LGR-002 Add batch memory to generation loop.
  - Track imported route `item_id`s across the 10-mission Alpha batch.
  - Send excluded/already-selected IDs to the backend if the request contract supports it.
  - Locally reject any generated mission that repeats an imported route item.
  - Continue trying until 10 valid missions import or retry budget is exhausted.
  - Completed: Core now accumulates imported route `item_id`s and display-identity keys, sends them as `already_selected_route_item_ids` / `already_selected_route_display_identity_keys` in the live request and prompt context, and rejects repeated IDs/identities before saving another generated assignment.

- [x] CWB-LGR-003 Make import failure recoverable.
  - Duplicate `item_id`, non-candidate, or app-import validation failures should be recorded and skipped.
  - A single bad attempt must not terminate the whole Alpha generation run.
  - Preserve diagnostics for skipped attempts.
  - Completed: app-validation failures, including duplicate in-mission items and cross-batch repeats, are recorded as `mission_import_result` diagnostics and skipped while the loop continues toward the 10-mission target. Non-candidate route items remain primarily a backend validator responsibility because app missions do not carry candidate IDs.

- [x] CWB-LGR-004 Improve generation progress UI.
  - Show visible movement while generating.
  - Include current count such as `Building mission 3 of 10`.
  - Keep `Stop Waiting`, `Retry`, `Start Fresh`, and `Upload Diagnostics` reachable on failure.
  - Completed: first-run generation already shows determinate progress, active mission count/attempt detail, `Stop Waiting`, retry, start-fresh, prepare/share diagnostics, and upload diagnostics controls.

- [x] CWB-LGR-005 Prove diagnostic upload from app.
  - Manual Upload Diagnostics should call `submit-alpha-diagnostic`.
  - It should include `client_state_snapshot`, generation request/result, import result, and client errors where available.
  - UI should show accepted/failed status in tester-safe language.
  - Completed app-side: manual diagnostics upload calls `submit-alpha-diagnostic` with the Supabase session bearer token and packages support diagnostics including `client_state_snapshot`, generation request/result, import result, and client errors when present. Live Supabase row proof remains blocked on Infrastructure deploy/smoke.

- [ ] CWB-LGR-006 Package next TestFlight build after P0 verification.
  - Increment build number.
  - Confirm first-run state migration gives a fresh read.
  - Run simulator tests and any available physical-device smoke before upload.

## Acceptance

- Build imports 10 locally valid missions or lands in a clear recoverable failure state.
- No duplicate route `item_id` enters local mission storage.
- Local diagnostics can explain every generation attempt and import skip.
- Manual Upload Diagnostics creates Supabase rows.
- Tester can always exit/retry/reset from generation failure.

## Blockers To Raise

| issue id | blocker | owner lane | needed for | current workaround | status |
| --- | --- | --- | --- | --- | --- |
| `CWB-LGR-I001` | Live backend deploy confirmation required before packaging, including stricter `generate-first-mission-batch`, `submit-alpha-diagnostic`, `client_state_snapshot` acceptance, and diagnostic row smoke. | Supabase / Infrastructure | CWB-LGR-001, CWB-LGR-005 live row proof, CWB-LGR-006 packaging, and device smoke. | Core code/tests are complete locally; continue local simulator validation and wait to package until Infra confirms live deploy. | open |

## Completion Note

- status: Core app-side recovery work complete except packaging/device smoke, which is blocked on live Infrastructure deploy confirmation.
- files changed:
  - `MusicAtlasController/Models/AppModel.swift`
  - `MusicAtlasController/Services/MissionLoader.swift`
  - `MusicAtlasController/Services/SurveyStore.swift`
  - `MusicAtlasControllerTests/MissionDecodingTests.swift`
  - `MusicAtlasControllerTests/SessionExporterTests.swift`
  - `docs/alpha_backlog/live_generation_recovery_core_waymark_build_2026_05_25.md`
- commands/tests run:
  - `git diff --check -- MusicAtlasController/Models/AppModel.swift MusicAtlasController/Services/MissionLoader.swift MusicAtlasController/Services/SurveyStore.swift MusicAtlasControllerTests/MissionDecodingTests.swift MusicAtlasControllerTests/SessionExporterTests.swift docs/alpha_backlog/live_generation_recovery_core_waymark_build_2026_05_25.md`
  - `COPYFILE_DISABLE=1 xcodebuild -scheme MusicAtlasController -configuration Debug -sdk iphonesimulator -destination 'platform=iOS Simulator,name=iPhone 17,OS=26.5' -derivedDataPath /tmp/musicmission-lgr-core-test/DerivedData test`
- live deploy or build number: no new build packaged; waiting on Supabase / Infrastructure deploy confirmation before CWB-LGR-006.
- remaining blockers:
  - `CWB-LGR-I001`: live backend deploy/smoke confirmation for stricter generation validation and diagnostic upload.
  - App-side non-candidate validation is limited until app mission payloads carry route `candidate_id` or backend rejects non-candidate output before adaptation.
- handoff needed from:
  - Supabase / Infrastructure: confirm live `generate-first-mission-batch` and `submit-alpha-diagnostic` deployment, `client_state_snapshot` acceptance, and at least one persisted `alpha_client_diagnostic_artifacts` row.
  - Mission Generation / Closed Loop: finalize the batch-memory field contract if it differs from Core's current `already_selected_route_item_ids` / `already_selected_route_display_identity_keys` shape.
