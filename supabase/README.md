# Cartenza Alpha Supabase

This folder is the thin Alpha backend for live first mission generation and provisional evidence intake. Its job is narrow:

- protect `OPENAI_API_KEY`;
- accept a compact Survey/Atlas generation packet;
- call OpenAI through the Responses API;
- log prompt/model/schema versions, latency, token usage, raw output, parsed output, and app-import status;
- adapt app-import candidates into `mission.v0.2`;
- accept consent-gated Alpha evidence artifacts through `submit-alpha-evidence`;
- accept consent-gated PM/support diagnostics through `submit-alpha-diagnostic`.

It is not the full Cartenza backend, Atlas authority, graph database, public account system, or sync layer.

## Setup

```sh
supabase login
supabase init # only if supabase/config.toml is missing
supabase link --project-ref <your-project-ref>
supabase db push
supabase secrets set OPENAI_API_KEY=<key>
supabase secrets set CARTENZA_OPENAI_MODEL=gpt-5.4-mini
supabase secrets set CARTENZA_OPENAI_REASONING_EFFORT=medium
supabase secrets set CARTENZA_OPENAI_MAX_OUTPUT_TOKENS=12000
supabase secrets set CARTENZA_GENERATION_PROMPT_VERSION=mission_generator_candidate_constrained_v0_1
supabase secrets set CARTENZA_ALPHA_REVIEW_NEEDED_APP_MISSION_POLICY=return_app_valid_missions
supabase functions deploy generate-first-mission-batch
supabase functions deploy submit-alpha-evidence
supabase functions deploy submit-alpha-diagnostic
```

The functions still accept legacy `WAYMARK_*` secrets during the Cartenza transition. Prefer `CARTENZA_*` for new local env files and new hosted secrets.

For local development:

```sh
cp supabase/functions/.env.example supabase/functions/.env.local
sed -i '' 's/CARTENZA_ALPHA_REPLAY_MODE=false/CARTENZA_ALPHA_REPLAY_MODE=true/' supabase/functions/.env.local
supabase functions serve generate-first-mission-batch --env-file supabase/functions/.env.local
supabase functions serve submit-alpha-evidence --env-file supabase/functions/.env.local
supabase functions serve submit-alpha-diagnostic --env-file supabase/functions/.env.local
```

Do not put OpenAI keys or Supabase service-role keys in the iOS app. The app should use only the Supabase project URL and a publishable/anon key if needed for function invocation.

## Endpoint

```text
POST /functions/v1/generate-first-mission-batch
```

Minimum request body:

```json
{
  "client_request_id": "ios-generated-stable-id",
  "tester_alias": "trusted-alpha-001",
  "requested_batch_size": 3,
  "survey_evidence_export": {},
  "mission_generation_digest_view": {},
  "candidate_pool": {},
  "prompt_context": {
    "alpha_scope": "first_batch"
  }
}
```

The function returns raw generation output plus `app_missions` when the app-import gate passes. For trusted Alpha, `CARTENZA_ALPHA_REVIEW_NEEDED_APP_MISSION_POLICY=return_app_valid_missions` may also return app-valid missions with `status=review_needed` and an `alpha_import_policy` envelope. The legacy `WAYMARK_ALPHA_REVIEW_NEEDED_APP_MISSION_POLICY` name is still accepted. The app must keep those review flags auditable and must never import `blocked` output.

## Evidence Upload Endpoint

```text
POST /functions/v1/submit-alpha-evidence
```

Minimum request body:

```json
{
  "client_artifact_id": "ios-generated-stable-id",
  "tester_alias": "trusted-alpha-001",
  "artifact_type": "reaction_session",
  "schema_version": "reaction_session.v0.2",
  "client_created_at": "2026-05-22T18:00:00Z",
  "source_app_version": "0.2",
  "source_app_build": "1",
  "upload_cadence": "after_saved_evidence",
  "consent": {
    "evidence_upload_allowed": true,
    "terms_version": "alpha_privacy_terms_v0_1",
    "accepted_at": "2026-05-22T17:50:00Z"
  },
  "payload": {}
}
```

Accepted artifact types:

- `survey_evidence_export`
- `mission_generation_digest_view`
- `reaction_session`
- `mission_review`
- `atlas_delta_candidate`

`submit-alpha-evidence` requires a JWT in hosted Supabase and stores artifacts with service-role credentials. It must not be enabled for automatic upload until privacy/terms, retention, deletion, and support access policies are approved.

## Diagnostic Upload Endpoint

```text
POST /functions/v1/submit-alpha-diagnostic
```

Minimum request body:

```json
{
  "client_artifact_id": "ios-generated-stable-id",
  "tester_alias": "trusted-alpha-001",
  "artifact_type": "mission_import_result",
  "schema_version": "waymark.alpha_client_diagnostic_artifact.v0.1",
  "survey_session_id": "ios-survey-session-id",
  "client_request_id": "ios-generation-request-id",
  "generation_run_id": "supabase-generation-run-uuid",
  "mission_id": "MIS_GENERATED_ALPHA_001",
  "source_app_version": "0.2",
  "source_app_build": "9",
  "redaction_level": "support_diagnostic",
  "upload_cadence": "manual_share",
  "client_created_at": "2026-05-24T18:00:00Z",
  "consent": {
    "diagnostic_upload_allowed": true,
    "terms_version": "alpha_privacy_terms_v0_1",
    "accepted_at": "2026-05-24T17:50:00Z"
  },
  "payload": {}
}
```

Accepted diagnostic artifact types:

- `apple_music_signal_payload`
- `survey_page_selection_audit`
- `survey_evidence_export`
- `mission_generation_request_packet`
- `mission_generation_result`
- `mission_import_result`
- `client_error_event`

Diagnostic artifacts persist to `alpha_client_diagnostic_artifacts`. They are PM/support evidence, not promoted Atlas truth, and must not contain tokens, service-role keys, Apple identity tokens, or hidden simulator truth.

## Offline Checks

These checks do not require a live Supabase account:

```sh
node scripts/build_supabase_function_fixtures.mjs
node scripts/smoke_supabase_generate_first_mission_batch.mjs
node scripts/check_supabase_alpha_infra.mjs
```

The acceptance script type-checks the Edge Function, validates replay fixtures, writes `supabase/alpha_infra_acceptance_report.md`, and reports whether Supabase/Deno CLI are installed.

## Fixture Replay

Replay fixtures live under:

```text
supabase/functions/generate-first-mission-batch/fixtures/
```

Replay requests include `replay_generation_output` and are accepted only when:

```text
CARTENZA_ALPHA_REPLAY_MODE=true
```

Never enable replay mode for the hosted Alpha function.
