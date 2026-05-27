# TestFlight Alpha Operations Runbook v0.1

Generated: 2026-05-22

## Scope

Trusted Alpha, small tester group, iPhone-first, Apple Music required for real playback evidence.

## Preflight

- Confirm app build uses Release/TestFlight configuration.
- Confirm Release bundle does not include personal mission packs or sample mission JSON as user content.
- Confirm MusicKit entitlement works on physical iPhone.
- Confirm local reset/recover path exists.
- Confirm export/share path works.
- Confirm support channel is known to testers.
- Confirm privacy/support copy is approved.
- Confirm tester aliases are assigned.
- Confirm Sign in with Apple and Apple Music first-run copy is approved.
- Confirm evidence upload is disabled unless privacy/retention/deletion policy is approved.

## Backend Preflight

- Supabase project linked.
- Migration applied.
- Edge Function secrets set.
- `generate-first-mission-batch` deployed.
- `submit-alpha-evidence` deployed if evidence upload is enabled or being tested.
- `submit-alpha-diagnostic` deployed if PM/support diagnostics are enabled or being tested.
- App config includes `WaymarkSupabaseDiagnosticFunctionName=submit-alpha-diagnostic` if diagnostic upload is being tested.
- Supabase Auth Apple provider configured if account auth is enabled.
- Fixture smoke test passes.
- Live smoke test records one `alpha_generation_runs` row.
- Evidence upload smoke test records one `alpha_evidence_artifacts` row if upload is enabled.
- Diagnostic upload smoke test records one `alpha_client_diagnostic_artifacts` row if diagnostics are enabled.
- Core app config contains only app-safe URL/key/function fields.

## Tester Flow

1. Install TestFlight build.
2. Open app.
3. Accept privacy/terms.
4. Sign in with Apple and connect Apple Music.
5. Complete onboarding.
6. Complete required Survey intake.
7. Wait for first mission generation.
8. Resolve/play mission through MusicKit.
9. React with primary controls and optional chips/notes.
10. Finish or stop mission.
11. Confirm evidence sync status or use Share Evidence fallback if requested.

## Support Flow

If Apple Music fails:

- confirm subscription/catalog playback works outside app
- capture authorization state
- record storefront/device/iOS version
- use reset/retry only after preserving useful evidence

If mission generation fails:

- preserve status: `review_needed`, `blocked`, or `failed`
- collect run ID if available
- for `review_needed`, check whether `alpha_import_policy.app_import_allowed_for_trusted_alpha=true` and app mission validation passed
- do not import `blocked` or app-validation-failed mission payloads
- use local reviewed import fallback if needed
- run `node scripts/summarize_alpha_live_run.mjs --tester-alias <alias> --since <iso>` with service-role credentials available in the shell

If evidence upload fails:

- preserve local export files
- collect upload ID or client artifact ID if available
- confirm privacy consent was accepted
- use manual Share Evidence fallback

If playback resolves wrong version:

- capture resolved title/artist/album/catalog ID
- mark wrong-version in Mission Review if available
- preserve reaction only if tester reacted to what actually played

If app state is stuck:

- export/share evidence first when possible
- upload support diagnostics from Share Evidence first when Supabase auth is active; otherwise share the local diagnostics package
- use reset/recover path
- record app build and tester alias

## Live Smoke Triage

Use this matrix after each physical/TestFlight run.

| symptom | first check | likely owner |
| --- | --- | --- |
| Supabase Auth succeeds but generation has no rows | client request/config diagnostic, session JWT, function URL | Core / Infra |
| `review_needed` with app-valid missions | `alpha_import_policy`, review focus, candidate risk notes | Mission Generation / Infra / Canonical |
| `blocked` generation | generation/app validation errors | Mission Generation / Infra |
| zero imported missions after `app_import_candidate` | `mission_import_result` validation errors | Core |
| Survey has quarantined responses | `survey_page_selection_audit`, quarantine reason counts | Survey / Core / Atlas |
| missing Apple Music influence | `apple_music_signal_payload`, page-selection source mix | Core / Survey / Canonical |
| evidence upload has `user_id_present=false` | Supabase Auth session and JWT headers | Core / Infra |
| diagnostic artifact missing | app diagnostics upload path or `submit-alpha-diagnostic` deploy | Core / Infra |

## Rollback

Rollback options:

- pause TestFlight group
- ship new build with remote assignment disabled
- use local reviewed import only
- collect manual exports
- delete/revoke Supabase secrets if backend behavior is unsafe

## Do Not Do

- Do not ask testers to paste secrets.
- Do not ship bundled personal missions as user content.
- Do not treat generated missions as app-ready unless `status == app_import_candidate` or trusted Alpha `review_needed` policy returns app-valid missions with explicit review flags.
- Do not treat app evidence as promoted Atlas truth.
- Do not upload evidence automatically until privacy/retention/deletion/support policy is approved.
- Do not upload diagnostic artifacts automatically until privacy/retention/deletion/support policy is approved.
