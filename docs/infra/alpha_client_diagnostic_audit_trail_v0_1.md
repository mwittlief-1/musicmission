# Alpha Client Diagnostic Audit Trail v0.1

Date: 2026-05-24

Status: implementation guidance for `CWB-031`, `INF-020`, `SIM-017`, and `ATL-018`.

## Goal

Give Product/PM and engineering a reconstructable live Alpha chain:

```text
Apple Music payload
-> Survey page construction
-> Survey responses / evidence export
-> mission generation request
-> backend generation result
-> app import result
-> mission/reaction evidence upload
```

This is a diagnostics/support layer. It is not Atlas truth, not a public account/sync layer, and not user-facing product copy.

## Upload Posture

- Manual support upload is acceptable after the Alpha acknowledgement/privacy gate.
- Automatic upload remains blocked until final privacy, retention, deletion, and support access policy is approved.
- The normal tester UI should not show raw payloads, schemas, run IDs, candidate scores, or import errors.
- Support diagnostics may appear behind an existing diagnostic/debug flag or under Share Evidence.

## Common Envelope

Every diagnostic artifact should include these fields when available:

```json
{
  "schema_version": "waymark.alpha_client_diagnostic_artifact.v0.1",
  "artifact_id": "client-generated-stable-id",
  "artifact_type": "mission_import_result",
  "tester_alias": "alpha_tester_alias",
  "supabase_user_id": "optional-auth-user-id",
  "survey_session_id": "optional-survey-session-id",
  "client_request_id": "optional-generation-client-request-id",
  "generation_run_id": "optional-supabase-run-id",
  "mission_id": "optional-mission-id",
  "source_app_version": "0.2",
  "source_app_build": "9",
  "client_created_at": "ISO-8601",
  "redaction_level": "support_diagnostic",
  "payload_sha256": "sha256-of-payload",
  "payload": {}
}
```

Required link fields depend on artifact type. Missing optional fields should be explicit `null` or omitted consistently; do not invent fake IDs.

## Artifact Types

### `apple_music_signal_payload`

Purpose: prove what Apple Music signal was available before Survey page 1.

Minimum payload:

- storefront/subscription/device context
- capped library artist/album/song/playlist samples
- capped recommendation groups
- capped raw endpoint snapshots
- capture timestamp and source caps
- consent/diagnostic disclosure version

Rules:

- Do not upload tokens or authorization headers.
- Treat Apple Music as exposure/familiarity context only.
- Do not mark Apple Music presence as taste truth.

### `survey_page_selection_audit`

Purpose: explain why each Survey tile appeared.

Minimum payload:

- survey session ID
- page ID, step, object type, page index
- displayed tiles with typed refs and display labels
- source mix and approved graph surface refs
- Apple exposure prior summary per tile where applicable
- candidate basis, page intent, dedupe group, and family/archetype refs
- prior visible response summary used for page N+1
- included/excluded candidate summaries and exclusion reasons
- construction-only exclusion declaration

Rules:

- Do not include hidden simulator truth.
- Do not include raw scoring internals unless Survey/PM marks them support-safe.
- Do not expose generator prompts or private construction traces.

### `survey_evidence_export`

Purpose: preserve the exact Atlas-ingestable Survey Evidence Export used for generation.

Minimum payload:

- the same `waymark.survey_evidence_export.v0.1` object sent to generation
- total response count
- Atlas-ingestable response count
- quarantined response count and reason counts

Rules:

- This is the primary Survey evidence artifact.
- Quarantined responses stay visible for diagnostics but do not become Signals.

### `mission_generation_request_packet`

Purpose: prove exactly what the app sent to Supabase.

Minimum payload:

- client request ID
- requested batch size
- batch mission index/total/seed when present
- Survey Evidence Export hash and inline payload or stored artifact ref
- MissionGenerationDigestView hash and inline payload or stored artifact ref
- candidate pool hash/ref if present
- prompt context

Rules:

- Keep OpenAI/service-role secrets out.
- If payload size becomes large, store hashes plus artifact refs instead of duplicating everything.

### `mission_generation_result`

Purpose: mirror the backend response as seen by the app.

Minimum payload:

- client request ID
- generation run ID
- status and app import status
- prompt/model/adapter/schema versions
- validation summary
- app mission count returned
- generated mission IDs when returned
- backend latency/token summary if returned

Rules:

- Preserve `review_needed` and `blocked` statuses even when no app missions are imported.
- Link to `alpha_generation_runs.id` when available.

### `mission_import_result`

Purpose: explain what the app accepted, skipped, or rejected.

Minimum payload:

- generation run ID
- generation status
- local import status: `imported`, `skipped_review_needed`, `blocked`, `validation_failed`, `missing_app_missions`, `client_error`
- imported mission IDs and item counts
- local validation errors
- local mission catalog count after import

Rules:

- This artifact is the missing client-side half of the current audit trail.
- It must record review-gated attempts even when the app continues generating.

### `client_error_event`

Purpose: capture failures before or after the Supabase function.

Minimum payload:

- error domain and code/category
- visible user state where safe
- auth/session status summary
- function/config name where relevant
- associated request/run IDs when available
- app version/build

Rules:

- Do not store tokens, secrets, raw Apple identity tokens, or keychain material.

## Supabase Storage Recommendation

Fastest safe path:

- Add a dedicated `alpha_client_diagnostic_artifacts` table, or extend `alpha_evidence_artifacts` only if the check constraints and naming remain clear.
- Prefer a dedicated table if implementation cost is low; it keeps diagnostics separate from formal evidence artifacts.
- Reuse Edge Function auth/session checks and service-role writes.
- Add indexes on tester alias, user ID, survey session ID, client request ID, generation run ID, artifact type, and created-at.

## PM Query Target

Given tester alias + time window, PM should be able to answer:

- Which app build ran?
- Was Supabase auth present?
- What Apple Music payload was captured?
- Which Survey pages and tiles appeared?
- How many Survey responses were exported, ingested, or quarantined?
- What did the app send to generation?
- Which backend runs returned `app_import_candidate`, `review_needed`, `blocked`, or `failed`?
- Which missions imported locally?
- Which mission/reaction evidence uploaded?
- Which client-side error stopped or degraded the flow?
