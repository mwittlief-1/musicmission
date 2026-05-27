# Supabase App Configuration Contract v0.1

Generated: 2026-05-22

## Purpose

This contract tells Core Waymark what configuration the iOS app may receive for the Alpha backend.

The app must never receive:

- `OPENAI_API_KEY`
- Supabase service-role key
- Supabase database password
- function secret values

## App-Safe Fields

```json
{
  "schema_version": "waymark.supabase_app_config.v0.1",
  "environment": "local_fixture | alpha",
  "supabase_project_url": "https://PROJECT_REF.supabase.co",
  "supabase_anon_key": "publishable_or_anon_key",
  "generate_first_mission_batch_function": "generate-first-mission-batch",
  "submit_alpha_evidence_function": "submit-alpha-evidence",
  "submit_alpha_diagnostic_function": "submit-alpha-diagnostic",
  "function_url": "https://PROJECT_REF.supabase.co/functions/v1/generate-first-mission-batch",
  "evidence_function_url": "https://PROJECT_REF.supabase.co/functions/v1/submit-alpha-evidence",
  "diagnostic_function_url": "https://PROJECT_REF.supabase.co/functions/v1/submit-alpha-diagnostic",
  "requires_jwt": true,
  "auth_provider": "apple",
  "tester_alias": "trusted-alpha-001",
  "evidence_upload_cadence": "manual_share | after_saved_evidence | scheduled",
  "request_timeout_seconds": 120,
  "fallback_mode": "local_golden_packet_stub"
}
```

## Local Fixture Mode

Until the live Supabase project exists, Core should use:

```json
{
  "schema_version": "waymark.supabase_app_config.v0.1",
  "environment": "local_fixture",
  "supabase_project_url": null,
  "supabase_anon_key": null,
  "generate_first_mission_batch_function": "generate-first-mission-batch",
  "submit_alpha_evidence_function": "submit-alpha-evidence",
  "submit_alpha_diagnostic_function": "submit-alpha-diagnostic",
  "function_url": null,
  "evidence_function_url": null,
  "diagnostic_function_url": null,
  "requires_jwt": false,
  "auth_provider": null,
  "tester_alias": "trusted-alpha-local",
  "evidence_upload_cadence": "manual_share",
  "request_timeout_seconds": 30,
  "fallback_mode": "local_golden_packet_stub"
}
```

The local fixture path should consume:

```text
data/alpha_packets/golden_alpha_packet_v0_1/response/supabase_generate_first_mission_batch_response.json
```

## Live Alpha Mode

Live Alpha mode requires Product/Infrastructure to provide:

- Supabase project URL
- app-safe anon/publishable key
- function JWT/auth policy
- Sign in with Apple / Supabase Auth provider configuration
- tester alias policy
- evidence upload cadence
- support path for failed generation

## Request Policy

The app may call:

```text
POST /functions/v1/generate-first-mission-batch
```

The app request should include:

- `client_request_id`
- `tester_alias`
- `requested_batch_size`
- `survey_evidence_export`
- `mission_generation_digest_view`
- `candidate_pool`
- `prompt_context`

The app must not include:

- hidden simulator truth
- raw private Apple library dump
- OpenAI secrets
- Supabase service-role credentials
- promoted Atlas claims

## Response Policy

The app may import missions only when:

```text
status == "app_import_candidate"
app_missions is non-empty
```

Trusted Alpha may also import review-gated missions only when the backend response includes:

```text
status == "review_needed"
alpha_import_policy.app_import_allowed_for_trusted_alpha == true
alpha_import_policy.app_missions_returned == true
app_missions is non-empty
```

The app must preserve review flags and upload/export a `mission_import_result` diagnostic for any review-gated import.

The app must not import missions when:

```text
status == "blocked"
status == "failed"
```

For non-import statuses, the app should preserve a support/export artifact and show a tester-safe failure state.

## Evidence Upload Policy

The app may call:

```text
POST /functions/v1/submit-alpha-evidence
```

Only after:

- privacy/terms consent is accepted
- `consent.evidence_upload_allowed == true`
- the request includes the accepted terms version and timestamp
- the artifact is provisional evidence, not promoted Atlas truth

Manual Share Evidence remains the fallback path.

## Diagnostic Upload Policy

The app may call:

```text
POST /functions/v1/submit-alpha-diagnostic
```

Only after:

- privacy/terms consent is accepted
- `consent.diagnostic_upload_allowed == true`
- the request includes the accepted terms version and timestamp
- the artifact is PM/support diagnostic material, not promoted Atlas truth

Manual Share Evidence / support diagnostics remain the fallback path. Automatic diagnostic upload is blocked until privacy/retention/deletion/support policy is approved.

Core config key: `WaymarkSupabaseDiagnosticFunctionName=submit-alpha-diagnostic`.
