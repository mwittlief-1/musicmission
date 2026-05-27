# Survey Completion to First Mission Batch App Wiring Audit v0.1

Date: 2026-05-21

## Scope

This audit covers the remaining iOS app work to connect:

```text
Survey completion
-> Survey Evidence Export
-> starter MissionGenerationDigestView
-> Supabase generate-first-mission-batch
-> returned app-import-ready mission.v0.2
-> local mission persistence
-> TestFlight-safe first mission flow
```

This is app-side scope. It does not assign backend, Atlas, Survey intelligence, Candidate Pool, or Mission Generation ownership except where the iOS app needs a contract boundary.

## Current State Read

Already present in the app:

- Survey UI with welcome, Apple Music connect, artist grid, optional third artist page, album grid, song grid, advanced survey, freeform notes, and readout.
- Survey responses persist locally in `waymark_survey_session_v0_1.json`.
- Survey response model includes item kind, state, nuances, note, and updated timestamp.
- Survey fixture items include source, objective, rationale, title/subtitle, artwork seed, and optional artwork URL.
- Mission library loads bundled `mission.v0.2` JSON.
- Mission session state persists locally in `waymark_session_library_v0_1.json`.
- MusicKit authorization, search, playback, mission review, and export are implemented.
- Supabase scaffold exists under `supabase/`.
- Edge Function `generate-first-mission-batch` exists and adapts valid `waymark.mission_output.v0.1` into app `mission.v0.2` when the app-import gate passes.

Not yet present in the app:

- No Survey Evidence Export builder.
- No app-side `MissionGenerationDigestView` builder.
- No Supabase Swift package or URLSession client.
- No app config for Supabase URL/key/function name/tester alias.
- No "Generate First Missions" app action.
- No generated mission response model.
- No import path for non-bundled missions.
- No persisted generated mission library.
- No generation run persistence/retry state.
- No reset/recovery surface for Survey + generated mission state.
- No TestFlight-safe first-run shell that hides internal Resolve/Export diagnostics.

## Task List: Survey Evidence Export

Goal: convert completed in-app Survey state into the visible append-only evidence ledger expected by Atlas/Mission Generation.

Required tasks:

- Add `SurveyEvidenceExport` models matching `waymark.survey_evidence_export.v0.1`.
- Add `SurveyEvidenceExportBuilder` service that consumes:
  - `SurveyStore.responses`;
  - `SurveyStore.freeformSignals`;
  - visible `SurveyItem` metadata from `SurveyFixtureLibrary`;
  - Apple Music authorization/storefront context if available;
  - app/device/version context where useful.
- Generate stable IDs:
  - `export_id`;
  - `evidence_atom_id`;
  - `evidence_ref`;
  - `response_id`;
  - page/source refs.
- Map app survey states to export reactions:
  - `favorite` -> `love`;
  - `like` -> `like`;
  - `fine` -> `ok`;
  - `not_for_me` -> `dont_like`;
  - `dont_know` -> `dont_know_enough`.
- Map export reactions to normalized operations:
  - `love` -> `positive_high`;
  - `like` -> `positive_medium`;
  - `ok` -> `waypoint_context`;
  - `dont_like` -> `negative_scope_carefully`;
  - `dont_know_enough` -> `familiarity_uncertainty`.
- Convert every visible Survey item into a typed `music_object_ref`.
- Preserve object type:
  - artist;
  - album;
  - song recording.
- Preserve `ref_source` honestly:
  - `canonical_graph` only if the app has a real canonical ID;
  - otherwise `user_local`, `external_catalog`, or `unresolved`.
- Include selected nuances as `selected_tags`.
- Include visible alternatives as `shown_unselected_tags` if the app can reconstruct what was offered.
- Include notes only when user-visible and user-authored.
- Include page context using app-visible fields:
  - page/stage;
  - page intent;
  - item source;
  - batch objective;
  - comparison set where available.
- Include Apple exposure prior only as exposure/familiarity context, never as taste truth.
- Exclude private or construction-only data:
  - no hidden simulator truth;
  - no raw ranking scores;
  - no fake profile labels;
  - no prompt construction;
  - no page randomization internals;
  - no Profile Writer prose.
- Build response ref index and validate every `atlas_ingestable` ref resolves within the export.
- Add local JSON preview/save support for dev diagnostics.

Recommended tasks:

- Add `SurveyEvidenceExportValidator` domain checks in Swift:
  - schema version present;
  - at least one evidence atom;
  - no unresolved response refs;
  - `dont_know_enough` is not negative;
  - Apple prior has `taste_truth = false`;
  - all atoms have typed refs.
- Add unit tests for reaction mapping, no-private-data guarantees, and response-ref integrity.
- Add sample export fixture from a deterministic in-app survey state.

Open product boundary:

- The app can produce visible evidence atoms now, but it cannot honestly attach canonical graph IDs unless Survey candidate fixtures provide them. Survey PM / Canonical Graph must decide whether app Survey items will ship with canonical refs or only display-local refs for Alpha.

## Task List: MissionGenerationDigestView Construction

Goal: give the generation endpoint a compact mission-facing digest without requiring the iOS app to become Atlas.

Required tasks:

- Add `MissionGenerationDigestView` models for `waymark.mission_generation_digest_view.v0.1`.
- Add `MissionGenerationDigestBuilder` service that consumes the Survey Evidence Export and produces a starter digest.
- Keep this builder deliberately shallow:
  - summarize visible positives;
  - summarize waypoints/contextual likes;
  - summarize likely dead ends;
  - summarize unknowns;
  - summarize user vocabulary from notes/nuances;
  - preserve anti-overfitting rules;
  - preserve unresolved questions.
- Do not create promoted Atlas truth in the app.
- Mark all role-like outputs as provisional or starter summaries.
- Include read policy:
  - mission generation reads this compact adapter;
  - no canonical graph mutation;
  - possible updates are review-gated;
  - app-generated digest is low-confidence starter state.
- Include fields required by the existing harness shape:
  - `schema_version`;
  - `record_type`;
  - `digest_id`;
  - `source_digest_id` or source export ID;
  - `user_id` or tester alias;
  - `generated_at`;
  - `mission_context`;
  - `core_taste_summary`;
  - `landmarks`;
  - `regions`;
  - `frontiers`;
  - `dead_ends`;
  - `waypoints`;
  - `unknowns`;
  - `taste_feature_states`;
  - `user_vocabulary_terms`;
  - `anti_overfitting_rules`;
  - `unresolved_questions`;
  - `recent_signal_summaries`;
  - `candidate_pool_behavior`;
  - `suggested_candidate_roles`;
  - `review_gated_interpretation_summary`.
- Add deterministic digest snapshots for tests.

Recommended tasks:

- Keep full Atlas ingestion on the backend/harness side for Alpha if possible.
- If app-generated digest is too thin, have the app send Survey Evidence Export and let Supabase/Atlas infrastructure construct the richer digest server-side.
- Add a `digest_quality` or `digest_completeness` marker so backend can decide whether to generate, return review-needed, or fall back to concierge review.

Open product boundary:

- If Alpha requires real Atlas-level role assignment from Survey, the app should not hand-roll it. The app can build a starter digest, but Atlas PM should own true role assignment and confidence semantics.

## Task List: Supabase Client and Config

Goal: let the iOS app invoke `generate-first-mission-batch` without exposing OpenAI or service-role secrets.

Current backend facts:

- Supabase function: `generate-first-mission-batch`.
- Config currently has `verify_jwt = true`.
- Function persists to `alpha_generation_runs` if Supabase service credentials are available in Edge Function environment.
- App must send:
  - `survey_evidence_export`;
  - `mission_generation_digest_view`;
  - optional `candidate_pool`;
  - `prompt_context`;
  - `client_request_id`;
  - `tester_alias`;
  - `requested_batch_size`.

Required tasks:

- Decide client approach:
  - option A: add `supabase-swift` via Swift Package Manager;
  - option B: use plain `URLSession` for a single Edge Function call.
- For fastest Alpha, `URLSession` is sufficient if no Supabase Auth/session features are needed.
- Add `WaymarkBackendConfig`:
  - Supabase project URL;
  - publishable/anon key;
  - function name;
  - tester alias;
  - requested batch size;
  - environment label: local/dev/staging/prod.
- Do not store OpenAI key, Supabase service-role key, or secret key in the app.
- Store Supabase publishable/anon key in a non-secret config file or xcconfig appropriate for TestFlight.
- Add `WaymarkGenerationClient` protocol.
- Add live client implementation.
- Add stub client implementation for simulator/tests.
- Include required headers for Edge Function invocation:
  - `Authorization: Bearer <publishable-or-user-token>`;
  - `apikey: <publishable-or-anon-key>`;
  - `Content-Type: application/json`.
- If `verify_jwt = true` remains, confirm anon/publishable key invocation is accepted for this Alpha function, or add a real Supabase Auth session.
- Add network timeout, cancellation, retry, and error mapping.
- Add response decoding for:
  - `run_id`;
  - `status`;
  - `prompt_version`;
  - `model`;
  - schema versions;
  - `app_missions`;
  - validation details;
  - usage;
  - latency.
- Add clear client error states:
  - not configured;
  - invalid request;
  - unauthorized;
  - generation failed;
  - review needed;
  - blocked;
  - no app-import candidates returned.

Recommended tasks:

- Add build-time guard that prevents TestFlight archive if Supabase config is missing.
- Add a local `localhost`/Supabase functions serve config for simulator.
- Add a backend health/check action in Diagnostics, not in the main user flow.
- Persist last generation request and response for support/debug.

Official-doc constraints to preserve:

- Supabase Swift initializes with project URL and project key.
- Swift Edge Function invocation requires an Authorization header.
- Edge Function secrets/service keys belong in Supabase Edge Functions, not the iOS app.

## Task List: First Mission Generation Request

Goal: connect Survey readout to backend generation safely.

Required tasks:

- Add `GenerateFirstMissionBatchRequest` model.
- Add stable `client_request_id` generation:
  - stable per Survey completion attempt;
  - reused on retry to avoid duplicate backend rows.
- Include `tester_alias`.
- Include `requested_batch_size`, likely 3 for first Alpha.
- Include Survey Evidence Export.
- Include MissionGenerationDigestView.
- Include candidate pool:
  - `{}` if none is available;
  - or a bundled/remote candidate pool if Candidate Pool PM provides one.
- Include prompt context:
  - `alpha_scope = first_batch`;
  - storefront if known;
  - app version/build;
  - survey completion timestamp;
  - MusicKit authorization/subscription summary if relevant.
- Add `GenerationRunState`:
  - idle;
  - building input;
  - submitting;
  - generating;
  - app import candidate;
  - review needed;
  - blocked;
  - failed.

Recommended tasks:

- Persist request packet before sending.
- Persist response packet after receiving.
- Save local run log with `run_id`, status, timestamp, and schema versions.
- Add debug export/share for the request and response.

Open product boundary:

- If candidate pool is empty, the current backend can generate but may fail the app-import gate. Product should decide whether Alpha accepts "review needed" as a normal result or whether app should require a candidate pool before calling.

## Task List: Returned Mission Import

Goal: import returned `mission.v0.2` missions into the app as playable mission candidates.

Current gap:

- `MissionLoader` only loads bundled mission resources.
- `Mission` and `MissionItem` are `Decodable`, not `Codable`.
- App mission library is currently derived from bundled JSON plus persisted session state; it does not store generated mission definitions.

Required tasks:

- Make mission models encodable where needed, or add separate persisted generated mission wrapper.
- Add `GeneratedMissionStore`.
- Persist generated mission definitions separately from session evidence.
- Add mission source metadata:
  - bundled;
  - generated;
  - imported;
  - concierge;
  - dev/stub.
- Add `MissionLibraryStore` or extend `MissionLoader` to merge:
  - bundled missions;
  - persisted generated missions;
  - optional imported JSON files.
- Add import validation:
  - `schema_version == mission.v0.2`;
  - valid `mission_id`;
  - stable item IDs;
  - at least one item;
  - every item starts unresolved;
  - route item has artist/title;
  - feedback chip sets are present for four primary operations;
  - generated placeholders are not presented as playable tracks.
- Add generated mission dedupe by mission ID and/or source run ID.
- On successful import, add mission(s) to available mission list.
- Select first generated mission by default after successful generation.
- Preserve generated mission source/run metadata for export and support.

Recommended tasks:

- Support replacing a generated mission if backend returns a corrected mission for the same run.
- Add "View generated missions" and "Use bundled fallback mission" affordances.
- Add test fixture for a Supabase response with app missions and import it through the store.

Open product boundary:

- The Edge Function currently adapts one generated output into a single app mission. The request says first mission batch. Decide whether the function should return multiple generated mission outputs or whether "batch" initially means one selected first mission plus backend logs.

## Task List: Persistence

Goal: app can survive relaunch throughout Survey -> generation -> mission execution.

Required tasks:

- Persist Survey session as currently implemented, but add completion metadata:
  - completed_at;
  - export_id;
  - generation eligibility;
  - last generated run ID.
- Persist Survey Evidence Export artifacts.
- Persist MissionGenerationDigestView artifacts.
- Persist generation request/response state.
- Persist generated mission definitions.
- Persist active generated mission session using current mission session persistence.
- Persist imported mission source metadata.
- Persist failed/review-needed generation states so user can resume or retry.
- Ensure app relaunch after each phase restores the right screen/state:
  - in-progress Survey;
  - Survey complete/readout;
  - generation pending/failed/review-needed;
  - generated mission ready;
  - active mission in progress.

Recommended tasks:

- Use a single `AlphaAppStateStore` index file that references artifact files rather than one giant blob.
- Keep durable artifacts in Application Support, not Documents, except explicit user exports.
- Add versioned persistence migrations or graceful reset when schema changes.
- Add tests for relaunch restoration at each boundary.

## Task List: Reset and Recovery

Goal: trusted Alpha users and the team can recover from bad local state without reinstalling.

Required tasks:

- Add a Diagnostics or More screen reset section.
- Add reset actions:
  - reset Survey only;
  - reset generated missions only;
  - reset active mission session only;
  - reset all local Alpha data.
- Add confirmation dialogs for destructive resets.
- Add "Export diagnostics before reset" option.
- Add "Retry generation" using the same `client_request_id` or a new one, depending on user action.
- Add "Use bundled fallback mission" when generation fails.
- Add "Mark generation as needs team review" when backend returns `review_needed` or `blocked`.
- Add support for backend response recovery:
  - if app crashes after response but before import, import from persisted response on relaunch;
  - if request was sent but response lost, allow manual retry/recovery.

Recommended tasks:

- Add lightweight local data inventory display:
  - survey signals count;
  - export IDs;
  - generation run IDs;
  - generated mission count;
  - active mission ID.
- Add support bundle export for trusted Alpha debugging.

## Task List: TestFlight-Safe UI Flow

Goal: a trusted tester can complete Survey and reach a first generated mission without seeing the current internal-tool tab structure.

Required tasks:

- Add a TestFlight-safe shell or mode.
- Replace or hide the current six-tab internal layout for Alpha users.
- Recommended top-level Alpha flow:

```text
Welcome / Connect Apple Music
-> Survey
-> What We Think So Far
-> Generate First Missions
-> Mission Ready
-> Player
-> Mission Review
-> Share/Submit Evidence
```

- Add clear states after Survey readout:
  - "Generate first missions";
  - "Generating";
  - "Mission ready";
  - "Needs team review";
  - "Use starter mission";
  - "Try again".
- Keep Resolve and Export available under More/Diagnostics for support.
- Keep Apple Music authorization status visible only when needed.
- After successful generation/import, navigate to Mission Detail or Player.
- If generation returns `review_needed`, show a calm Alpha-safe message:
  - "This route needs review before we play it."
  - provide bundled fallback or support/export path.
- If network fails, preserve Survey and show retry/fallback.
- If Supabase config is missing in a TestFlight build, show a controlled configuration error rather than crashing.
- Add "Review Past Missions" only if generated mission persistence is ready.

Recommended tasks:

- Add a feature flag:
  - `internalDevTabs`;
  - `alphaFlow`.
- Add visual distinction between user flow and diagnostics.
- Add concise "what happens next" copy at the Survey readout.
- Add progress affordance without overclaiming:
  - "Building a first route from your Survey signals."
  - avoid "final taste profile" language.

## Test Coverage Needed

Unit tests:

- Survey state -> Survey Evidence Export mapping.
- Reaction normalization.
- Nuance/tag serialization.
- `dont_know` guardrail.
- Apple exposure prior is not taste truth.
- MissionGenerationDigestView construction from known survey fixture.
- Generation request encoding.
- Supabase response decoding.
- `review_needed` and `blocked` error mapping.
- Returned mission import validation.
- Generated mission persistence and reload.
- Reset behavior.

Integration tests:

- Complete deterministic Survey -> build export -> build digest -> stub generation response -> import mission.
- Relaunch after Survey complete.
- Relaunch after generation response persisted.
- Relaunch after generated mission imported.
- Failure path with backend `review_needed`.
- Failure path with no Supabase config.

Physical-device QA:

- Complete Survey on iPhone.
- Generate/import mission through deployed Supabase.
- Resolve generated mission items through MusicKit.
- Play a full generated mission.
- Close and reopen mid-Survey, post-generation, and mid-mission.
- Export/share final evidence.

## Main Dependencies

App-side work depends on:

- Final Survey Evidence Export contract acceptance.
- Decision on whether app Survey items include canonical refs.
- Decision on app-generated starter digest vs backend-built digest.
- Supabase project URL and publishable/anon key.
- Confirmation of `verify_jwt` strategy for Edge Function invocation.
- Deployed `generate-first-mission-batch` function.
- Candidate Pool availability or accepted empty-pool fallback.
- Backend guarantee that only app-import-ready `mission.v0.2` missions appear in `app_missions`.
- Product decision on TestFlight Alpha shell vs internal tabs.

## App-Side Readiness Bar

This wiring is ready for trusted Alpha when:

- Survey can complete and survive relaunch.
- Survey can emit a valid visible evidence export.
- App can build or receive a valid MissionGenerationDigestView.
- App can call Supabase without exposing secret keys.
- Backend response is persisted before import.
- App imports only valid `mission.v0.2` app-import candidates.
- Generated missions appear in the mission library and can become active.
- Tester has a fallback path when generation is review-needed, blocked, offline, or misconfigured.
- Local reset/recovery exists.
- TestFlight shell guides user from Survey to first mission without internal diagnostics getting in the way.
