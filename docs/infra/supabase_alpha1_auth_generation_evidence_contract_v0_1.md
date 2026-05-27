# Supabase Alpha 1 Auth, Generation, And Evidence Contract v0.1

Generated: 2026-05-22

## Purpose

Define the thin Supabase responsibilities for Alpha 1 after the product decision addendum:

1. First-run account continuity through Sign in with Apple / Supabase Auth.
2. Survey completion handoff into first mission batch generation.
3. Consent-gated provisional evidence upload.
4. Consent-gated PM/support diagnostic upload for live Alpha reconstruction.

Supabase remains a thin Alpha backend. It is not the public account system, full Atlas authority, graph database, or permanent sync layer.

## App-Safe Configuration

The app may receive:

```json
{
  "schema_version": "waymark.supabase_app_config.v0.2",
  "environment": "alpha",
  "supabase_project_url": "https://PROJECT_REF.supabase.co",
  "supabase_anon_key": "publishable_or_anon_key",
  "requires_jwt": true,
  "auth_provider": "apple",
  "generate_first_mission_batch_function": "generate-first-mission-batch",
  "submit_alpha_evidence_function": "submit-alpha-evidence",
  "submit_alpha_diagnostic_function": "submit-alpha-diagnostic",
  "tester_alias": "trusted-alpha-001",
  "evidence_upload_cadence": "manual_share | after_saved_evidence | scheduled",
  "fallback_mode": "local_golden_packet_stub"
}
```

The app must never receive:

- `OPENAI_API_KEY`
- Supabase service-role key
- database password
- function secrets
- raw OpenAI request/response logs outside support artifacts

## Auth Posture

Product wants a single easy action that signs in with Apple ID and connects Apple Music. Engineering should keep the implementation honest:

- Sign in with Apple / Supabase Auth provides account/session continuity.
- MusicKit authorization provides Apple Music access.
- The product surface may present these as one guided step, but failure states should distinguish account auth from Apple Music access.

Supabase Auth setup required outside code:

- Enable Apple provider in Supabase Auth.
- Configure Apple Services ID / Bundle ID / redirect URLs.
- Confirm the iOS app has the Sign in with Apple capability.
- Confirm hosted Edge Functions require JWTs.

`alpha_tester_profiles` is the thin Alpha profile table keyed by `auth.users.id`. It tracks tester alias and first-run milestone timestamps without becoming a public profile system.

## Survey Completion To First Mission Generation

Endpoint:

```text
POST /functions/v1/generate-first-mission-batch
```

Minimum request:

```json
{
  "client_request_id": "ios-generated-stable-id",
  "tester_alias": "trusted-alpha-001",
  "requested_batch_size": 3,
  "survey_evidence_export": {},
  "mission_generation_digest_view": {},
  "candidate_pool": {},
  "prompt_context": {
    "alpha_scope": "first_batch_after_required_survey",
    "survey_page_count": {
      "artist": 4,
      "album": 2,
      "song": 4
    }
  }
}
```

Rules:

- Input must come from visible Survey Evidence Export and Atlas/MissionGenerationDigest-compatible context.
- Do not send hidden simulator truth, private construction logs, raw Apple library dumps, or promoted Atlas claims.
- The function returns clean app missions when `status == app_import_candidate`.
- Trusted Alpha may set `WAYMARK_ALPHA_REVIEW_NEEDED_APP_MISSION_POLICY=return_app_valid_missions`; in that mode `review_needed` can return app-valid missions with an `alpha_import_policy` envelope and explicit review flags.
- `blocked` and `failed` responses must not be imported by the app.
- The original backend `status`, review focus, validation summary, and run ID must remain auditable even if the app imports a review-gated mission for trusted Alpha.

## Evidence Upload

Endpoint:

```text
POST /functions/v1/submit-alpha-evidence
```

Minimum request:

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

Rules:

- Evidence upload is disabled until privacy/terms, retention, deletion, and support access policy are approved.
- Hosted endpoint requires a Supabase JWT.
- Edge Function writes with service-role credentials.
- App evidence remains provisional and append-only.
- Manual Share Evidence remains fallback/support even if upload is enabled.

## Diagnostic Upload

Endpoint:

```text
POST /functions/v1/submit-alpha-diagnostic
```

Accepted diagnostic artifact types:

- `apple_music_signal_payload`
- `survey_page_selection_audit`
- `survey_evidence_export`
- `mission_generation_request_packet`
- `mission_generation_result`
- `mission_import_result`
- `client_error_event`

Rules:

- Diagnostic upload is manual/support-gated until privacy/terms, retention, deletion, and support access policy are approved.
- Hosted endpoint requires a Supabase JWT.
- Edge Function writes with service-role credentials.
- Diagnostic artifacts are PM/support reconstruction aids, not promoted Atlas truth.
- Diagnostic payloads must not include auth tokens, service-role keys, Apple identity tokens, or hidden simulator truth.

## Database Objects

Existing:

- `alpha_generation_runs`
- `alpha_evidence_artifacts`
- `alpha_client_diagnostic_artifacts`

Added for Alpha 1:

- `alpha_tester_profiles`
- `alpha_evidence_artifacts.user_id`
- `alpha_evidence_artifacts.upload_status`
- `alpha_evidence_artifacts.upload_cadence`
- `alpha_evidence_artifacts.consent_terms_version`
- `alpha_evidence_artifacts.consent_accepted_at`
- `alpha_evidence_artifacts.source_app_version`
- `alpha_evidence_artifacts.source_app_build`
- `alpha_evidence_artifacts.client_artifact_sha256`
- `alpha_evidence_artifacts.payload_sha256`
- `alpha_evidence_artifacts.received_at`
- `alpha_evidence_artifacts.deleted_at`
- `alpha_client_diagnostic_artifacts.survey_session_id`
- `alpha_client_diagnostic_artifacts.client_request_id`
- `alpha_client_diagnostic_artifacts.generation_run_id`
- `alpha_client_diagnostic_artifacts.mission_id`
- `alpha_client_diagnostic_artifacts.redaction_level`
- `alpha_client_diagnostic_artifacts.payload_sha256`

## Live Deployment Checklist

Requires Supabase account access:

```sh
npx -y supabase login
npx -y supabase link --project-ref <project-ref>
npx -y supabase db push
npx -y supabase secrets set OPENAI_API_KEY=<key>
npx -y supabase secrets set WAYMARK_OPENAI_MODEL=gpt-5.4-mini
npx -y supabase secrets set WAYMARK_OPENAI_REASONING_EFFORT=medium
npx -y supabase secrets set WAYMARK_OPENAI_MAX_OUTPUT_TOKENS=12000
npx -y supabase secrets set WAYMARK_GENERATION_PROMPT_VERSION=mission_generator_candidate_constrained_v0_1
npx -y supabase secrets set WAYMARK_ALPHA_REVIEW_NEEDED_APP_MISSION_POLICY=return_app_valid_missions
npx -y supabase secrets set SUPABASE_SERVICE_ROLE_KEY=<service-role-key>
npx -y supabase functions deploy generate-first-mission-batch
npx -y supabase functions deploy submit-alpha-evidence
npx -y supabase functions deploy submit-alpha-diagnostic
```

Current local blocker if not already authenticated:

```text
SUPABASE_ACCESS_TOKEN or supabase login is required before project list/link/deploy checks can run.
```
