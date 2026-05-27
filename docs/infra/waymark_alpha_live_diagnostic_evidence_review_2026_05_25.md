# Waymark Alpha Live Diagnostic Evidence Review - 2026-05-25

## Scope

Reviewed the latest available live Supabase evidence for `trusted-alpha-001` after the tester reported that a diagnostic evidence report was shared from the app.

This review is a PM/support summary. It does not include raw Apple Music payloads, tokens, identity material, or full private diagnostic payloads.

## Artifact Search Result

- `alpha_client_diagnostic_artifacts` currently has no uploaded rows.
- Local Mac/iCloud/Downloads searches did not find a new `support_diagnostics_*` package or `waymark_support_diagnostics_index.json`.
- The connected iPhone is visible to Xcode as `Matt's iPhone (4)`, but is currently `unavailable`, so the app container could not be pulled from this machine.
- The only row in `alpha_evidence_artifacts` is the older `infra-live-smoke` evidence row from 2026-05-22.

Conclusion: the support diagnostic package was either shared to a target not present on this Mac, remained in the app container, or the app's manual upload path did not complete. Supabase does not currently contain the diagnostic artifacts needed for Apple Music payload -> page-selection lineage.

## Live Generation Window Reviewed

Latest trusted-alpha burst:

- Time window: `2026-05-25T11:41:10Z` through `2026-05-25T11:48:55Z`
- Source app build in request context: `12`
- Rows reviewed: `10`
- Survey summary in each request:
  - `78` total responses
  - `78` Atlas-ingestable responses
  - `0` quarantined responses
  - `10` displayed pages
  - `4` favorites
  - `28` likes
  - `20` not-for-me responses
  - `1` don't-know response
- Backend status:
  - `9` rows marked `app_import_candidate`
  - `1` row marked `review_needed`, but still described as app-valid for trusted Alpha policy
- Each row returned exactly `1` app mission.

## Key Findings

### 1. Live backend is still accepting duplicate route item IDs

Two of the latest ten returned missions contain duplicate `item_id` values within a single mission:

- `2026-05-25T11:42:46Z` / request `ios_first_batch_20A002FE-4A84-4A86-AA96-1822FC3D2433`
  - Duplicate: `ITEM_ALPHA_SONG_GETO_BOYS_MIND_PLAYING_TRICKS_ON_ME`
- `2026-05-25T11:47:16Z` / request `ios_first_batch_E267EB42-DDDA-4846-BAD2-36496D241571`
  - Duplicate: `ITEM_SURVEY_F2_SONG_RECORDING_QUESTION_MARK_AND_THE_MYSTERIANS_96_TEA`
  - Duplicate: `ITEM_SURVEY_F7_ALBUM_THE_ROOTS_THINGS_FALL_APART_051`

This directly matches the class of app failure reported on-device: `Mission import failed: duplicate item_id ...`.

### 2. The live validation payload is missing route identity diagnostics

The reviewed rows do not include populated `validation.route_identity` results. That means production Supabase has not yet deployed, or is not running, the stricter duplicate/non-candidate route identity validator from the local infrastructure recovery work.

The current live function is therefore still able to return `app_import_candidate` even when the app importer will reject the mission.

### 3. Candidate-pool constraint is not enforced tightly enough

Several returned missions include route items that are not in that request's supplied candidate pool by title/artist comparison.

Examples:

- Request `ios_first_batch_8D8C4468-F615-4F00-97B4-97DBD66180E0`
  - `6` route items returned
  - `6` route items did not match that request's candidate pool
- Request `ios_first_batch_1F2AF669-BAFA-4F30-8E05-B053728D9CC0`
  - `9` route items returned
  - `8` route items did not match that request's candidate pool
- Request `ios_first_batch_20A002FE-4A84-4A86-AA96-1822FC3D2433`
  - `8` route items returned
  - `7` route items did not match that request's candidate pool

The model appears to be drawing from the broader digest/known regions instead of staying constrained to `candidate_pool.candidates`.

### 4. Batch-level diversity is also not enforced

Because the app calls the Edge Function once per mission, the backend sees isolated requests with `batch_mission_index`, but it does not receive an accumulated exclusion list from earlier generated missions.

Across the latest ten returned missions, many item IDs recur across missions. Examples:

- `Mind Playing Tricks on Me` appeared `7` times.
- `It Was a Good Day` appeared `5` times.
- `Planet Her` appeared `4` times.
- `Maggot Brain` appeared `4` times.
- `Jungle Boogie` appeared `3` times.

Even if each individual mission were valid, the 10-mission batch is not currently protected against repeated route items.

## Interpretation

The live backend path is active, but the failure is no longer primarily "OpenAI did not return missions." Supabase is generating and storing rows. The technical failure is the import contract:

1. OpenAI can return duplicate route items.
2. OpenAI can return items outside the per-call candidate pool.
3. Live backend validation currently marks those outputs as importable.
4. The app importer correctly rejects at least some duplicate `item_id` cases.
5. The UI then strands the tester in generation failure recovery.

## Missing Evidence

Still missing from Supabase:

- `apple_music_signal_payload`
- `survey_page_selection_audit`
- `mission_generation_request_packet`
- `mission_generation_result`
- `mission_import_result`
- `client_error_event`
- `client_state_snapshot`

Without those artifacts, Supabase cannot yet reconstruct Apple Music payload -> Page 1 -> later pages -> survey completion. It can only reconstruct the generation side from `alpha_generation_runs`.

## Recommended Next Actions

1. Deploy the stricter local `generate-first-mission-batch` validator before the next TestFlight build or live smoke.
   - It should reject duplicate route `item_id`.
   - It should reject duplicate display identity.
   - It should reject non-candidate route items.
   - It should populate `validation.route_identity`.

2. Deploy the `submit-alpha-diagnostic` function and diagnostic type migration that accepts `client_state_snapshot`.

3. Upload/install the next app build only after the Supabase deploy, because build 13 expects the live backend to accept `client_state_snapshot` diagnostics.

4. Add batch-level memory.
   - Either generate all 10 missions in one backend request, or pass `excluded_item_ids` / `already_selected_route_items` on each loop iteration.
   - Backend should validate cross-mission uniqueness before returning a complete batch or before the app imports cumulative results.

5. Ask the tester to use "Upload Diagnostics" after authenticating, not just local share, for the next failure.
   - Current Supabase diagnostic row count is zero.
   - If local share is used, save/AirDrop the package to this Mac or iCloud Drive where it can sync.
