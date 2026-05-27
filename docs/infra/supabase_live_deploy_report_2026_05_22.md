# Supabase Live Deploy Report

Date: 2026-05-22

Project ref: `ewuffhezhgyskcfyzkvw`

Project URL: `https://ewuffhezhgyskcfyzkvw.supabase.co`

## Completed

- Linked local Supabase workspace to project `ewuffhezhgyskcfyzkvw`.
- Applied migrations:
  - `20260521160000_alpha_generation_logs.sql`
  - `20260522190000_alpha1_auth_and_evidence_upload.sql`
- Deployed Edge Functions:
  - `generate-first-mission-batch`
  - `submit-alpha-evidence`
- Set Waymark function configuration secrets:
  - `OPENAI_API_KEY`
  - `WAYMARK_OPENAI_MODEL`
  - `WAYMARK_OPENAI_REASONING_EFFORT`
  - `WAYMARK_OPENAI_MAX_OUTPUT_TOKENS`
  - `WAYMARK_GENERATION_PROMPT_VERSION`
  - `WAYMARK_MISSION_OUTPUT_SCHEMA_VERSION`
  - `WAYMARK_APP_MISSION_SCHEMA_VERSION`
  - `WAYMARK_APP_MISSION_ADAPTER_VERSION`
  - `WAYMARK_ALPHA_REPLAY_MODE`
  - `WAYMARK_ALPHA_EVIDENCE_TERMS_VERSION`
- Confirmed platform Supabase secrets exist by name/digest:
  - `SUPABASE_URL`
  - `SUPABASE_ANON_KEY`
  - `SUPABASE_PUBLISHABLE_KEYS`
  - `SUPABASE_SERVICE_ROLE_KEY`
  - `SUPABASE_SECRET_KEYS`
- Confirmed migration list shows both local migrations applied remotely.
- Confirmed function list shows both functions active.
- Confirmed local Supabase CLI auth was restored on 2026-05-22.
- Confirmed `OPENAI_API_KEY` is present in Edge Function secrets by that exact name as of the 2026-05-22 CLI check.
- Tuned live generation config to `WAYMARK_OPENAI_REASONING_EFFORT=none` and `WAYMARK_OPENAI_MAX_OUTPUT_TOKENS=24000` after the first live generation smoke exhausted the prior output budget in reasoning.
- Patched and redeployed `generate-first-mission-batch` so generation run updates use PATCH, raw OpenAI responses are persisted before parsing, and the JSON schema requires at least two feedback chips per reaction operation.

## Validation

Offline validation:

```text
node scripts/smoke_supabase_generate_first_mission_batch.mjs
SUPABASE_FUNCTION_SMOKE_PASS

node scripts/check_supabase_alpha_infra.mjs
SUPABASE_ALPHA_INFRA_CHECK_PASS
```

Remote migration list:

```text
Local          | Remote
20260521160000 | 20260521160000
20260522190000 | 20260522190000
```

Remote functions:

```text
generate-first-mission-batch | ACTIVE | version 7
submit-alpha-evidence        | ACTIVE | version 5
```

Live evidence upload smoke:

```text
function: submit-alpha-evidence
auth: anon JWT
upload_id: 2cfef693-bda4-45f3-ac13-4c846337c254
client_artifact_id: live-smoke-evidence-20260522T190951Z
status: accepted
persisted row: yes
user_id_present: false
```

Live generation smoke:

```text
function: generate-first-mission-batch
auth: anon JWT
run_id: a2be5f2c-8f18-4e93-9d0e-98b17091fec0
status: app_import_candidate
app_mission_count: 1
generation_valid: true
app_mission_valid: true
latency_ms: 42251
model: gpt-5.4-mini
token_usage: 111501 input, 6492 output, 117993 total
```

## Still Needed

- Verify Supabase Auth Sign in with Apple provider by completing an authenticated app/JWT smoke with a real Supabase Auth user. Product reports the Apple provider accepted the generated client-secret JWT on 2026-05-22.
- Provide Core with app-safe config:
  - project URL
  - publishable/anon key
  - function names
  - evidence upload cadence policy
- Run app-authenticated live smoke tests:
  - `generate-first-mission-batch` writes one `alpha_generation_runs` row using the app's real Supabase Auth session.
  - `submit-alpha-evidence` writes one `alpha_evidence_artifacts` row with `user_id_present=true`.
- Revoke the temporary Supabase personal access token used for deployment after no more CLI deploy work is needed.

## Do Not Enable Yet

- Automatic evidence upload remains blocked until privacy/terms, retention, deletion, and support access policy are approved.
- Generated missions must still be imported only when `status == app_import_candidate`, unless the trusted Alpha `review_needed` policy returns app-valid missions with explicit review flags and Core preserves the audit trail.

## 2026-05-24 Live Smoke Recovery Addendum

Context: physical/TestFlight runs proved that Survey and generation reach Supabase, but several structurally valid generations returned `review_needed` and blocked the app from building the intended 10-mission Alpha batch. The app also lacked a complete client-side audit chain for Apple Music -> Survey -> generation -> import.

Changes applied:

- Added migration `20260524170000_alpha_client_diagnostics.sql`.
- Added `alpha_client_diagnostic_artifacts` for PM/support diagnostics.
- Added and deployed `submit-alpha-diagnostic`.
- Added `WAYMARK_ALPHA_REVIEW_NEEDED_APP_MISSION_POLICY=return_app_valid_missions`.
- Redeployed `generate-first-mission-batch`.
- `generate-first-mission-batch` now returns an `alpha_import_policy` envelope and can return app-valid `review_needed` missions for trusted Alpha without changing the original `status`.
- Added `scripts/summarize_alpha_live_run.mjs` for tester-alias/time-window audit summaries.

Latest validation:

```text
node scripts/check_supabase_alpha_infra.mjs
SUPABASE_ALPHA_INFRA_CHECK_PASS
```

Remote functions after deploy:

```text
generate-first-mission-batch | ACTIVE | version 12
submit-alpha-evidence        | ACTIVE | version 5
submit-alpha-diagnostic      | ACTIVE | version 2
```

Still needed:

- Core must decide/implement how to consume trusted Alpha `review_needed` responses with `alpha_import_policy.app_import_allowed_for_trusted_alpha=true`.
- Core must upload `mission_import_result` and related diagnostic artifacts for app-side import outcomes.
- App-authenticated evidence/diagnostic smoke with `user_id_present=true` remains pending.
- Automatic evidence or diagnostic upload remains blocked until privacy/retention/deletion/support policy is approved.
