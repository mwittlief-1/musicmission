# Waymark Alpha Mission Generation Failure Trace

Date: 2026-05-25

Scope: diagnostic trace only. No code changes were made as part of this investigation.

## 1. End-to-End Generation Pipeline Map

1. Survey completion triggers first-batch generation in the app.
   - `AppModel.generateFirstMissionBatchAfterSurveyCompletion()` targets `10` imported missions and stops after `16` generation attempts.
   - Build 12 generates one mission per request: `requestedBatchSize: 1`, with `batch_mission_index`, `batch_mission_total`, and a fresh `batch_seed`.

2. The app builds the generation packet.
   - `SurveyEvidenceExportBuilder.makeFirstMissionGenerationRequest(...)` emits:
     - `survey_evidence_export`
     - `mission_generation_digest_view`
     - `candidate_pool`
     - `prompt_context`
   - The Survey Evidence Export only admits responses that can be matched to visible displayed pages; unmatched responses are quarantined in the export.
   - The MissionGenerationDigestView groups survey responses into landmarks, strong regions, waypoints, dead ends, unknowns, and first-batch portfolio hints.
   - The candidate pool adds `mission_intent`, `mission_request`, `survey_response_focus`, and selected route-ready candidates.

3. Candidate selection uses the bundled Alpha compact pool.
   - Local pool: `MusicAtlasController/Resources/alpha_compact_candidate_pool_alpha_v0.json`.
   - Observed local shape: `72` route-ready candidates, `12` each in `anchors`, `bridges`, `probes`, `boundary_probes`, `dead_end_checks`, and `waypoints`.
   - Local check found `72` total candidate IDs and `72` unique candidate IDs.
   - The known failing candidate, `survey-f7-song_recording-2pac-feat-dr-dre-california-love-047`, appears once in the local pool under `anchors`.

4. The app posts to Supabase.
   - `LiveSupabaseMissionGenerationClient.makeURLRequest(...)` sends the packet to `/functions/v1/generate-first-mission-batch` using the app-safe publishable key plus the Supabase session bearer.

5. The Edge Function logs and constructs the OpenAI request.
   - `generate-first-mission-batch/index.ts` creates an `alpha_generation_runs` row with `input_packet_sha256`, `input_packet`, `prompt_version`, model, schema versions, and adapter version.
   - The function stores `openai_request`, calls the Responses API, stores `raw_openai_response`, extracts output text, parses JSON, validates the rich mission output, adapts it to `mission.v0.2`, validates the adapted app mission, and returns `app_missions` only when policy allows.

6. Backend validation and status derivation.
   - Rich generation validation checks only required high-level fields and per-item artist/title/chip presence.
   - App mission validation checks schema version, mission ID format, non-empty items, item ID format, and unresolved Apple Music status.
   - `review_needed` may still return app-valid missions if `WAYMARK_ALPHA_REVIEW_NEEDED_APP_MISSION_POLICY=return_app_valid_missions`.

7. App import gate.
   - `LocalMissionProvider.importSupabaseMissionBatchResponseData(...)` accepts only `app_import_candidate` or `review_needed`, requires non-empty `app_missions`, then calls `MissionImportGate.validateAppImportCandidate(...)`.
   - The app import gate is stricter than the Edge app mission validator. It rejects duplicate `item_id`, pre-resolved items, blank artist/title, missing expected signal, missing player-card hypothesis, and missing feedback chips.
   - On `invalidMission`, Build 12 records a `mission_import_result` diagnostic with `local_import_status: validation_failed` and continues generation until the max-attempt ceiling.

## 2. Latest Observed Failure Signatures

- TestFlight build 12 can complete Survey, but mission generation repeatedly fails before reaching the 10-mission imported batch.
- Prior observed duplicate app route item ID:
  - `ITEM_SURVEY_F7_SONG_RECORDING_2PAC_FEAT_DR_DRE_CALIFORNIA_LOVE_047`
- Build 12 release notes say generation now skips app-validation failures, including duplicate generated item IDs, and continues attempting the batch.
- Existing offline Supabase smoke still passes:
  - `node scripts/smoke_supabase_generate_first_mission_batch.mjs`
  - Result: `SUPABASE_FUNCTION_SMOKE_PASS`
- Local shell does not currently expose `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, or `OPENAI_API_KEY`, and the Supabase CLI is not in `PATH`, so this trace could not inspect live `alpha_generation_runs` rows directly.

## 3. Exact Failure Point Hypothesis With Evidence

Primary hypothesis:

The immediate failure point is app-side import validation, triggered by duplicate route item IDs in an app mission that the backend can currently classify as app-valid. The upstream cause is OpenAI repeating the same route item or route item ID inside one generated mission, combined with missing duplicate/candidate uniqueness checks in the Edge Function validation contract.

Evidence:

- The candidate pool is not the direct duplicate source for the cited `California Love` ID. The local compact pool has unique candidate IDs, and `California Love` appears once.
- The app import gate explicitly rejects duplicate item IDs with `duplicate item_id <id>`.
- The Edge `validateAppMission(...)` does not check uniqueness across `mission.items[].item_id`.
- The rich generation validator does not check uniqueness across `route.items[].item_id`, `route.items[].candidate_id`, or canonical/dedupe IDs.
- `schema_mission_v0_2.json` constrains item ID format but does not express item ID uniqueness.
- The prompt/context says `allow_duplicate_songs: false`, but the hard backend validator does not enforce it.
- The app is probably interpreting the response correctly. A duplicate route item would make mission playback/reaction state ambiguous because `MissionItem.id == itemID`.

Secondary contributing hypotheses:

- Prompt construction does not pass prior imported candidate IDs, prior failed duplicate IDs, or prior attempt summaries. Each retry receives a mission index and fresh seed, but no explicit memory of the failed duplicate.
- The Edge adapter uses `appID("ITEM", item.item_id, ...)`, so if the model repeats the same rich `route.items[].item_id`, the adapted app mission preserves the duplicate.
- Candidate membership is not enforced by the Edge validator. A model could use non-candidates or repeat a candidate even though the prompt forbids it.
- The app candidate-pool exact-repeat filter uses a broad `itemLookup` exclusion and falls back to the original pool when filtering empties a pool. That means visible-Survey-repeat policy is documented in the packet but is not a hard guarantee in all pool slots.

Less likely based on local evidence:

- Review gating alone. Build 12 app code accepts `review_needed` when app missions are returned and app validation passes.
- Candidate pool duplicate content. Local checks show unique candidate IDs in the compact pool.
- Supabase request construction missing core objects. The live client sends `survey_evidence_export`, `mission_generation_digest_view`, `candidate_pool`, and `prompt_context`.

## 4. Missing Logs / Audit Rows

Live access missing from this shell:

- Recent `alpha_generation_runs` for build 12 could not be queried because service-role credentials were not present locally.
- Recent `alpha_client_diagnostic_artifacts` could not be queried for uploaded `mission_import_result` rows.
- Supabase CLI access was also unavailable from `PATH`.

Audit gaps that make the current failure slower to prove:

- `alpha_generation_runs` does not store top-level `source_app_version`, `source_app_build`, `batch_mission_index`, `batch_mission_total`, `batch_seed`, or a sanitized `attempt_index`.
- Backend validation does not persist a normalized route summary with:
  - route item IDs
  - candidate IDs
  - duplicate item ID list
  - duplicate candidate ID list
  - non-candidate route item list
  - route index sequence check
- `scripts/summarize_alpha_live_run.mjs` summarizes statuses and counts, but not duplicate validation errors, app mission item IDs, candidate IDs, or local import validation errors.
- Client `mission_generation_result` diagnostics currently store `raw_response` inside the support artifact. That is useful for support, but PM summaries should also have a redacted shape-only view.
- Client diagnostics are manual/support-upload gated. If the tester did not upload diagnostics after the failure, the backend has the generation side but not the app-side import rejection side.
- There is no checked-in `duplicate_item_id` Edge fixture proving that the backend currently lets duplicate adapted item IDs through while the app rejects them.

## 5. Recommended Technical Fixes

### Infra

- Add backend hard validation for duplicate rich `route.items[].item_id`, duplicate `candidate_id`, duplicate adapted `items[].item_id`, and repeated canonical/dedupe groups.
- Add candidate membership validation: every generated `candidate_id` should exist in `candidate_pool.candidates`.
- Add a sanitized validation summary to `alpha_generation_runs.validation`, including duplicate IDs and candidate-membership failures.
- Extend `summarize_alpha_live_run.mjs` to print redacted duplicate/candidate validation summaries and client `mission_import_result.local_validation_errors`.
- Add a replay fixture `supabase/functions/generate-first-mission-batch/fixtures/duplicate_item_id/` with an expected blocked contract.

### Atlas Schema

- Promote route identity invariants into the candidate/generation handoff:
  - unique candidate per route
  - unique dedupe group per route unless explicitly allowed
  - route item must be track/album and route-ready
  - visible Survey repeats must be explicitly labeled if ever allowed
- Add stable `route_candidate_key` or `dedupe_group` requirements to the app-facing candidate dictionaries so validators do not have to infer identity from display strings.

### Core

- Keep the app import duplicate rejection. It is the correct final safety gate.
- Include duplicate item IDs and, when safe, duplicate candidate IDs in `mission_import_result.local_validation_errors`.
- Upload support diagnostics immediately after a generation failure only when consent/upload policy permits; otherwise make the manual package path obvious to support.
- Consider passing prior imported mission IDs/candidate IDs and prior failed duplicate IDs into each subsequent generation attempt.

### Prompt / Generation

- Add explicit output rules:
  - every `route.items[].item_id` must be unique
  - every `route.items[].candidate_id` must be unique
  - do not repeat a candidate, title/artist pair, canonical entity, or dedupe group inside a mission
  - item IDs should be route-position-stable or candidate-derived with uniqueness checked before returning
- Include prior attempt summaries in retry prompts:
  - failed duplicate item IDs
  - imported candidate IDs
  - imported mission archetypes/portfolio slots
  - review-needed or blocked reasons
- Treat duplicate route/candidate identity as a hard blocker, not a review-needed condition.

## 6. Minimal Reproduction / Verification Commands

Current happy-path fixture smoke:

```bash
node scripts/smoke_supabase_generate_first_mission_batch.mjs
```

Check the current compact pool for candidate duplicates:

```bash
jq -r '[.pools[][].candidate_id] | length as $n | unique | length as $u | "candidate_ids total=\($n) unique=\($u) dupes=\($n-$u)"' MusicAtlasController/Resources/alpha_compact_candidate_pool_alpha_v0.json
```

Check a saved generation response for duplicate app item IDs:

```bash
jq -r '.app_missions[]?.items[]?.item_id' path/to/generation_response.json | sort | uniq -d
```

Check a saved generation response for duplicate rich route item IDs:

```bash
jq -r '.generation.route.items[]?.item_id' path/to/generation_response.json | sort | uniq -d
```

If live service-role access is available in a local shell, use the redacted summary script:

```bash
SUPABASE_URL=... SUPABASE_SERVICE_ROLE_KEY=... \
node scripts/summarize_alpha_live_run.mjs --tester-alias trusted-alpha-001 --since 2026-05-25T00:00:00.000Z
```

Recommended missing fixture:

```text
supabase/functions/generate-first-mission-batch/fixtures/duplicate_item_id/request.json
```

Expected behavior for that fixture after repair: backend status `blocked`, `app_missions` empty, validation error naming the duplicate route/app item ID.
