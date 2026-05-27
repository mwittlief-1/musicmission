# TestFlight Build 14 Feedback Triage - 2026-05-25

## Source

Founder physical-device TestFlight run, app version `0.2`, build `14`.

Reported behavior:

- Survey first screen said Apple Music did not provide enough context and fell back to Canonical Graph.
- Survey felt reasonably responsive/adaptive overall, but not perfect.
- A few repeats still appeared.
- Mission generation failed on timeout again.

## Immediate Read

Build 14 moved the system forward: client diagnostics were uploaded, Survey completed enough to produce request artifacts, and the failure is now primarily timeout behavior rather than the earlier duplicate-item import failure.

The Apple Music message is probably misleading. Current code intentionally treats Apple Music Signal Payload v0.2 as raw intake/persistence only and clears Survey scoring strengths until the separate Survey scoring adapter exists:

- `MusicAtlasController/Services/AlphaDynamicSurveyPageProvider.swift`
  - `updateAppleMusicSignalPayload(_:)` sets `appleEvidence = AlphaAppleEvidenceIndex.empty`.
  - `AlphaAppleEvidenceIndex.init(payload:)` ignores the payload.

Therefore, "not enough context from Apple Music" does not necessarily mean capture failed. It likely means the Survey scorer has no usable Apple-derived strengths by design.

## Live Evidence Seen

Supabase diagnostics show build `14` artifacts uploaded for tester alias `trusted-alpha-001` around `2026-05-25T20:56Z`, including:

- `apple_music_signal_payload`
- `survey_page_selection_audit`
- `survey_evidence_export`
- `mission_generation_request_packet`
- `client_state_snapshot`
- `client_error_event`

The latest observed request packet had:

```text
client_request_id = ios_first_batch_193794D3-A945-48E6-91EE-B776720251C1
```

The direct live generation-runs query hit a temporary Supabase connection/auth circuit breaker, so the backend completion row still needs to be checked after the circuit breaker cools down.

## Likely Root Causes

### 1. Mission Timeout

The app hard-times each Supabase generation call at `75` seconds:

```swift
AlphaMissionGenerationConfig.requestTimeoutSeconds = 75
```

The Edge Function performs a synchronous OpenAI Responses API call before returning to the app. If OpenAI completes after 75 seconds, the app records a timeout even if Supabase later finishes and updates `alpha_generation_runs`.

This is now the highest-priority Alpha blocker.

### 2. Apple Context Message

The app captures Apple Music v0.2 payloads but does not use them for Survey scoring yet. The UI should not imply Apple Music was too thin unless the raw payload actually lacks useful captured sections.

### 3. Survey Repeats

Repeats remain possible if they are not exact item-ID repeats or if invalidated future responses/page cache state affects later page generation. This overlaps the existing lineage report gaps:

- missing full selected-vs-excluded trace
- invalidated future responses influencing regenerated pages
- exact-key/artist metadata suppression limits

## Dispatch: Core Waymark Build

- [ ] `CWB-B14-001` Increase or replace the app-side generation timeout.
  - Fast Alpha patch: raise `requestTimeoutSeconds` from `75` to `180` or `240`.
  - Better patch: do not treat a single request timeout as terminal if the backend may still complete; show a retry/poll state that can recover by `client_request_id`.
  - Acceptance: physical-device generation can wait long enough for one mission attempt without dropping immediately to failure.

- [ ] `CWB-B14-002` Record timeout diagnostics with `client_request_id`.
  - Current `recordClientErrorDiagnostic` can accept `clientRequestID`, but the generation hard-failure catch records the error without threading the active request ID.
  - Acceptance: timeout `client_error_event` links to the exact generation request that timed out.

- [ ] `CWB-B14-003` Add post-timeout recovery.
  - If a timeout occurs, keep the request ID visible in diagnostics and provide a "Check for Completed Mission" / retry path.
  - Acceptance: app can import a completed backend run if the response was late rather than failed.

- [ ] `CWB-B14-004` Adjust Apple Music fallback copy.
  - Do not say Apple Music lacked context unless the v0.2 payload actually has no useful captured primary/context sections.
  - If Survey scoring is intentionally Canonical-only, say that in tester-safe language.

## Dispatch: Supabase / Infrastructure

- [ ] `INF-B14-001` Query live generation rows after circuit breaker clears.
  - Look up `client_request_id = ios_first_batch_193794D3-A945-48E6-91EE-B776720251C1`.
  - Report only redacted fields:
    - `status`
    - `app_import_status`
    - `latency_ms`
    - `token_usage`
    - `error_message`
    - `validation.route_identity`
    - `created_at`
    - `updated_at`

- [ ] `INF-B14-002` Determine whether timeout is client-only or backend failure.
  - If `alpha_generation_runs` eventually reached `app_import_candidate`, the app timeout is too short/recovery is missing.
  - If the row stayed `generating` or `failed`, inspect function/OpenAI error path and live Edge runtime limits.

- [ ] `INF-B14-003` Reduce generation latency.
  - Verify live secrets for:
    - `WAYMARK_OPENAI_MODEL`
    - `WAYMARK_OPENAI_MAX_OUTPUT_TOKENS`
    - `WAYMARK_OPENAI_REASONING_EFFORT`
  - Do not print secret values if any are sensitive; model/config names are fine.
  - Consider lower max output tokens, compact prompt payload, or a faster mission-specific prompt.

- [ ] `INF-B14-004` Consider async generation architecture if p95 remains over app timeout.
  - Minimal Alpha async pattern:
    - app submits request
    - function stores run and returns `202/run_id`
    - backend worker/OpenAI completion updates row
    - app polls by `client_request_id`/`run_id`
  - This is not required if raising timeout and reducing latency stabilizes Alpha.

## Dispatch: Survey Lineage

- [ ] `SURV-B14-001` Clarify Apple v0.2 scoring boundary.
  - Current behavior: raw Apple payload is captured and persisted, but Survey scoring ignores it.
  - Decide whether Alpha should:
    - keep Canonical-only scoring for now, with honest copy; or
    - implement a small allowed v0.2 adapter using only primary sources.

- [ ] `SURV-B14-002` Investigate repeats using uploaded `survey_page_selection_audit`.
  - Compare repeated items by:
    - exact item ID
    - display identity
    - canonical entity ID
    - artist/display fallback key
  - Classify repeats as true bug, permissible artist recurrence, alias/identity mismatch, or invalidation/cache artifact.

- [ ] `SURV-B14-003` Add repeat guard beyond item ID where needed.
  - Candidate guards:
    - normalized display identity
    - canonical object ID
    - artist + title key for songs/albums
    - prior disliked artist suppression

## Next Operator Steps

1. Wait for Supabase connection circuit breaker to clear.
2. Query the build 14 `client_request_id` generation row.
3. If backend finished after 75 seconds, patch Core timeout/recovery first.
4. If backend failed or stayed generating, patch Infra/OpenAI generation path first.
5. Update Survey copy so the Apple fallback message reflects reality.
