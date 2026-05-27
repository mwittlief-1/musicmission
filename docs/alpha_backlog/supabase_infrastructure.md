# Supabase / Infrastructure Backlog

Lane goal: thin Alpha backend that protects the OpenAI key, logs generation runs, adapts validated missions for app import, and leaves room for evidence upload without becoming the full Atlas/account/sync system.

## Non-Dependent Tasks

- [x] INF-001 Keep Supabase local config reproducible.
  - Maintain `supabase/config.toml`, migrations, function source, and `.env.example`.
  - Audit 2026-05-22: local scaffold exists at `supabase/config.toml`, `supabase/migrations/20260521160000_alpha_generation_logs.sql`, `supabase/functions/generate-first-mission-batch/index.ts`, and `supabase/functions/.env.example`.

- [x] INF-002 Install/check local tooling.
  - Supabase CLI.
  - Deno CLI or compatible type-check path.
  - Document exact versions once installed.
  - Completed: `supabase/alpha_infra_acceptance_report.md` documents Supabase CLI and Deno CLI as not installed; Node/npx are available; Edge Function type-check uses `npx` fallback.

- [x] INF-003 Link Supabase project.
  - Requires project ref from product/account owner.
  - After link, document project name/ref in a non-secret local note or setup doc.
  - Completed: linked project `ewuffhezhgyskcfyzkvw`; see `docs/infra/supabase_live_deploy_report_2026_05_22.md`.

- [x] INF-004 Apply Alpha generation log migration.
  - Apply `supabase/migrations/20260521160000_alpha_generation_logs.sql`.
  - Apply `supabase/migrations/20260522190000_alpha1_auth_and_evidence_upload.sql`.
  - Confirm RLS and service-role write behavior.
  - Completed: both migrations are applied remotely.

- [x] INF-005 Set Edge Function secrets.
  - `OPENAI_API_KEY`
  - `WAYMARK_OPENAI_MODEL`
  - `WAYMARK_OPENAI_REASONING_EFFORT`
  - `WAYMARK_OPENAI_MAX_OUTPUT_TOKENS`
  - `WAYMARK_GENERATION_PROMPT_VERSION`
  - Completed: CLI verification on 2026-05-22 confirms `OPENAI_API_KEY` is present. Live generation uses `WAYMARK_OPENAI_REASONING_EFFORT=none` and `WAYMARK_OPENAI_MAX_OUTPUT_TOKENS=24000`.

- [x] INF-006 Deploy `generate-first-mission-batch`.
  - Confirm request validation, OpenAI call, structured output parsing, logging, and response shape.
  - Completed: function is deployed and active. Live OpenAI smoke passed on 2026-05-22 with run `a2be5f2c-8f18-4e93-9d0e-98b17091fec0`, status `app_import_candidate`, one valid app mission, and persisted `alpha_generation_runs` audit row.

- [x] INF-007 Reconcile Edge Function adapter with golden packet builder.
  - The app mission adapter in Supabase should match the generated golden packet shape or document intentional differences.
  - Completed: `docs/infra/supabase_adapter_reconciliation_v0_1.md`.

- [x] INF-008 Add function contract fixtures.
  - Use golden packet request/response as fixtures.
  - Include blocked, review-needed, and app-import-candidate examples.
  - Completed: `supabase/functions/generate-first-mission-batch/fixtures/` with app-import-candidate, review-needed, blocked, and invalid-input cases.

- [x] INF-009 Add local function smoke test.
  - Validate no OpenAI call path with fixture replay.
  - Validate live OpenAI path only when secrets are present.
  - Completed: `scripts/smoke_supabase_generate_first_mission_batch.mjs`; replay mode is gated by `WAYMARK_ALPHA_REPLAY_MODE=true`.

- [x] INF-010 Log generation audit fields.
  - Raw request hash, prompt version, model, token usage, latency, parsed output, validation status, app-import status, and error message.
  - Completed: migration/function now include `adapter_version`, `input_packet_sha256`, `openai_request`, raw response, parsed generation, app missions, validation, token usage, latency, and error message.

- [x] INF-011 Decide evidence upload path.
  - Either keep manual export/share for first TestFlight or add a second Edge Function for evidence upload.
  - Do not silently invent full sync/account architecture.
  - Completed recommendation: keep manual export/share for first TestFlight; see `docs/infra/alpha_evidence_upload_recommendation_v0_1.md`.

- [x] INF-012 App configuration contract.
  - Provide URL/key/config fields Core needs.
  - No service-role keys in app.
  - Completed: `docs/infra/supabase_app_config_contract_v0_1.md`.

- [x] INF-013 Backend acceptance script.
  - One command should type-check functions and, when linked, verify migration/function deployment status.
  - Completed: `scripts/check_supabase_alpha_infra.mjs`; offline acceptance passed and report was written to `supabase/alpha_infra_acceptance_report.md`.

- [x] INF-014 TestFlight operational runbook.
  - Internal build, tester onboarding, support channel, evidence collection, known failure handling, rollback.
  - Completed: `docs/infra/testflight_alpha_operations_runbook_v0_1.md`.

## Post-Brand Review Alpha 1 Tasks

Product decisions received 2026-05-22 add first-run auth, Survey-triggered generation, and likely evidence upload/sync.

- [x] INF-015 Design Sign in with Apple / Supabase auth posture.
  - Keep scope thin: Alpha identity/session, not full public account system.
  - Document app-safe config and token/session persistence expectations.
  - Output: `docs/infra/supabase_alpha1_auth_generation_evidence_contract_v0_1.md`.
  - Output: `supabase/migrations/20260522190000_alpha1_auth_and_evidence_upload.sql`.

- [x] INF-016 Wire Survey completion -> first mission batch generation contract.
  - Input should be Survey Evidence Export / AtlasDigest-compatible context, not raw simulator/private construction data.
  - Output must preserve product status and app-import readiness.
  - Output: `docs/infra/supabase_alpha1_auth_generation_evidence_contract_v0_1.md`.
  - Existing function contract remains `supabase/functions/generate-first-mission-batch/index.ts`.

- [x] INF-017 Design evidence upload/sync endpoint.
  - Product prefers automatic or scheduled Supabase upload if safe.
  - Do not enable until privacy/terms, retention, deletion, and support access policies are approved.
  - Keep manual Share Evidence fallback.
  - Output: `supabase/functions/submit-alpha-evidence/index.ts`.
  - Output: `supabase/functions/submit-alpha-evidence/fixtures/`.
  - Output: `docs/infra/supabase_alpha1_auth_generation_evidence_contract_v0_1.md`.

- [x] INF-018 Extend migration/table inventory for Alpha identity and evidence upload if needed.
  - Avoid turning Supabase into full Atlas/account/sync architecture.
  - Preserve append-only/provisional evidence semantics.
  - Output: `supabase/migrations/20260522190000_alpha1_auth_and_evidence_upload.sql`.

- [x] INF-019 Deploy `submit-alpha-evidence`.
  - Confirm JWT requirement, consent validation, service-role write, and `alpha_evidence_artifacts` persistence.
  - Completed: function is deployed and active. Live anon-JWT smoke passed on 2026-05-22 with upload `2cfef693-bda4-45f3-ac13-4c846337c254`, status `accepted`, and persisted `alpha_evidence_artifacts` row. Real Apple-auth user session smoke is still required before app identity is considered complete. Automatic upload remains blocked until privacy/retention policy approval.

## Live Alpha Smoke Recovery Tasks

Source: `docs/alpha_backlog/alpha_live_smoke_recovery_2026_05_24.md`.

- [x] INF-020 Add Supabase-backed client diagnostic artifact support.
  - Either extend `alpha_evidence_artifacts` safely or add a dedicated `alpha_client_diagnostic_artifacts` table.
  - Support artifact types:
    - `apple_music_signal_payload`
    - `survey_page_selection_audit`
    - `survey_evidence_export`
    - `mission_generation_request_packet`
    - `mission_generation_result`
    - `mission_import_result`
    - `client_error_event`
  - Store link fields where supplied: tester alias, auth user ID, survey session ID, client request ID, generation run ID, mission ID, app version, build, client timestamp, payload hash, and redaction level.
  - Keep service-role writes inside Edge Functions; do not expose direct table writes from the app.
  - Manual/consent-gated upload is allowed; automatic upload remains blocked pending privacy/retention/deletion/support approval.
  - Completed: added migration `20260524170000_alpha_client_diagnostics.sql`, deployed `submit-alpha-diagnostic`, added fixtures, added typecheck/smoke coverage, and documented the diagnostic contract.

- [x] INF-021 Add trusted Alpha import tolerance for review-gated-but-app-valid missions.
  - Coordinate with Mission Generation and Core before changing response semantics.
  - Recommended Alpha behavior: when rich generation and adapted app mission validation pass but `review_config.ready_for_app_import` is false, optionally return app missions with explicit review flags under an Alpha-only setting.
  - Preserve hard `blocked` for schema-invalid output, app-mission validation failure, missing concrete route items, unsafe MusicKit/manual-review rows, or function errors.
  - Persist original `status`, `app_import_status`, review notes, and reason codes in `alpha_generation_runs`.
  - Completed: `generate-first-mission-batch` now builds/validates adapted app missions for structurally valid `review_needed` output and returns them only when `WAYMARK_ALPHA_REVIEW_NEEDED_APP_MISSION_POLICY=return_app_valid_missions`. The response and persisted validation include an `alpha_import_policy` envelope with review flags and reason codes. `blocked` output still returns no app missions.

- [x] INF-022 Add live audit view/query/script for one tester run.
  - Produce a PM-readable summary that joins generation rows, diagnostic artifacts, evidence upload rows, run IDs, import status, validation errors, candidate counts, token usage, latency, and build metadata.
  - Output can be a SQL view, documented query, or script under `scripts/`.
  - Acceptance: given tester alias and time window, Product can reconstruct Apple signal -> Survey -> generation -> import without opening the iPhone container.
  - Completed: `scripts/summarize_alpha_live_run.mjs` reads `alpha_generation_runs`, `alpha_client_diagnostic_artifacts`, and `alpha_evidence_artifacts` by tester alias/time window and prints a PM-readable summary.

- [x] INF-023 Refresh operations runbook for live smoke triage.
  - Add standard checks for `review_needed`, zero app missions, partial mission import, quarantined Survey responses, missing user ID, missing diagnostic artifact, and failed upload.
  - Include clear owner handoff: Core bug, Survey bug, Mission Generation gate, Canonical candidate issue, Atlas ingest issue, or Product/privacy blocker.
  - Completed: `docs/infra/testflight_alpha_operations_runbook_v0_1.md` now includes diagnostic deployment checks, live smoke triage, review-needed handling, and owner routing.

## Dependency Tripwires

Raise an issue when:

- Supabase account/project does not exist or project ref is unavailable.
- OpenAI API key or model policy is unavailable.
- Core app requires auth/user identity beyond anonymous trusted Alpha alias.
- Atlas asks backend to become the full persistence layer.
- Privacy/Release policy blocks evidence upload or model packet storage.
- Product asks for automatic upload before consent/retention/deletion policy is approved.
- Mission Generation changes output schema or app-import gate semantics.

## Do Not Do Yet

- Do not store service-role secrets in app code.
- Do not build full account/sync architecture unless explicitly approved.
- Do not return app missions when generation status is blocked. For `review_needed`, return app missions only if the trusted Alpha import-tolerance policy is explicitly implemented with app validation and review flags.
- Do not treat schema-valid generation as app-import-ready without product gate.
- Do not store hidden simulator truth in backend Alpha tables.

## Raised Issues

| issue id | blocker | owner lane | needed for | current workaround | status |
| --- | --- | --- | --- | --- | --- |
| `INF-I001` | Supabase Auth Apple provider end-to-end verification with a real user session and final privacy/retention policy for automatic upload remain unavailable. | Product / Infrastructure account owner | Durable user identity, app-session evidence upload, Core reauth behavior, and enabling automatic upload. | Migrations applied, functions deployed, secrets set, offline fixture/typecheck acceptance passes, live generation smoke passes, and live evidence upload smoke passes with anon JWT. | open |

## Completion Report

When this lane pauses, add:

- files changed:
  - `supabase/README.md`
  - `supabase/config.toml`
  - `supabase/functions/.env.example`
  - `supabase/functions/generate-first-mission-batch/index.ts`
  - `supabase/functions/generate-first-mission-batch/fixtures/`
  - `supabase/functions/submit-alpha-evidence/index.ts`
  - `supabase/functions/submit-alpha-evidence/fixtures/`
  - `supabase/functions/submit-alpha-diagnostic/index.ts`
  - `supabase/functions/submit-alpha-diagnostic/fixtures/`
  - `supabase/migrations/20260521160000_alpha_generation_logs.sql`
  - `supabase/migrations/20260522190000_alpha1_auth_and_evidence_upload.sql`
  - `supabase/migrations/20260524170000_alpha_client_diagnostics.sql`
  - `supabase/alpha_infra_acceptance_report.md`
  - `scripts/build_supabase_function_fixtures.mjs`
  - `scripts/smoke_supabase_generate_first_mission_batch.mjs`
  - `scripts/check_supabase_alpha_infra.mjs`
  - `scripts/summarize_alpha_live_run.mjs`
  - `docs/infra/supabase_adapter_reconciliation_v0_1.md`
  - `docs/infra/supabase_app_config_contract_v0_1.md`
  - `docs/infra/supabase_alpha1_auth_generation_evidence_contract_v0_1.md`
  - `docs/infra/alpha_client_diagnostic_audit_trail_v0_1.md`
  - `docs/infra/supabase_live_deploy_report_2026_05_22.md`
  - `docs/infra/alpha_evidence_upload_recommendation_v0_1.md`
  - `docs/infra/testflight_alpha_operations_runbook_v0_1.md`
  - `docs/alpha_backlog/supabase_infrastructure.md`
- commands run:
  - `npx -y supabase projects list` failed because `SUPABASE_ACCESS_TOKEN` / `supabase login` is not available locally.
  - `npx -y supabase link --project-ref ewuffhezhgyskcfyzkvw`
  - `npx -y supabase db push`
  - `npx -y supabase functions deploy generate-first-mission-batch`
  - `npx -y supabase functions deploy submit-alpha-evidence`
  - `npx -y supabase functions deploy submit-alpha-diagnostic --project-ref ewuffhezhgyskcfyzkvw`
  - `npx -y supabase secrets set ...` for non-sensitive Waymark function config
  - `npx -y supabase secrets set WAYMARK_ALPHA_REVIEW_NEEDED_APP_MISSION_POLICY=return_app_valid_missions WAYMARK_ALPHA_DIAGNOSTIC_TERMS_VERSION=alpha_privacy_terms_v0_1`
  - `npx -y supabase functions list`
  - `npx -y supabase secrets list`
  - `npx -y supabase migration list`
  - `node scripts/build_supabase_function_fixtures.mjs`
  - `node scripts/smoke_supabase_generate_first_mission_batch.mjs`
  - `npx -y -p typescript -p @types/deno tsc --noEmit --target ES2022 --lib ES2022,DOM --strict supabase/functions/submit-alpha-evidence/index.ts`
  - `npx -y -p typescript -p @types/deno tsc --noEmit --target ES2022 --lib ES2022,DOM --strict supabase/functions/generate-first-mission-batch/index.ts`
  - `npx -y -p typescript -p @types/deno tsc --noEmit --target ES2022 --lib ES2022,DOM --strict supabase/functions/submit-alpha-diagnostic/index.ts`
  - `node --check scripts/summarize_alpha_live_run.mjs`
  - `node scripts/check_supabase_alpha_infra.mjs`
  - indirect through acceptance script: `node scripts/smoke_supabase_generate_first_mission_batch.mjs`
  - indirect through acceptance script: `npx -y -p typescript -p @types/deno tsc --noEmit --target ES2022 --lib ES2022,DOM --strict supabase/functions/generate-first-mission-batch/index.ts`
  - indirect through acceptance script: `npx -y -p typescript -p @types/deno tsc --noEmit --target ES2022 --lib ES2022,DOM --strict supabase/functions/submit-alpha-evidence/index.ts`
  - indirect through acceptance script: `npx -y -p typescript -p @types/deno tsc --noEmit --target ES2022 --lib ES2022,DOM --strict supabase/functions/submit-alpha-diagnostic/index.ts`
- deploy status:
  - Offline acceptance passed.
  - Supabase CLI via npx is available (`2.101.0`); global Supabase CLI is not installed.
  - Live Supabase project is linked locally.
  - Migrations applied.
  - Waymark function settings, `OPENAI_API_KEY`, and `WAYMARK_ALPHA_REVIEW_NEEDED_APP_MISSION_POLICY=return_app_valid_missions` are set.
  - `generate-first-mission-batch` deployed and active; latest deploy includes trusted Alpha `review_needed` app-valid mission return policy and `alpha_import_policy` response/audit envelope.
  - `submit-alpha-evidence` deployed and active; live anon-JWT persistence smoke passed.
  - `submit-alpha-diagnostic` deployed and active.
  - Product reports Supabase Auth Apple provider accepted the generated client-secret JWT; end-to-end auth smoke is still required.
- remaining blockers:
  - `INF-I001`
- ready for Core app integration status: `yes_with_caveats`
