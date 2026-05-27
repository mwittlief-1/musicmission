# Waymark Alpha Generation Recovery Implementation

Generated: 2026-05-25

Scope: implementation follow-up to:

- `docs/infra/waymark_alpha_generation_failure_trace_2026_05_25.md`
- `docs/app_dev/waymark_alpha_app_state_recovery_diagnostics_audit_2026_05_25.md`

Survey lineage is intentionally excluded because it is being investigated separately.

## Lane Summary

### Infra

Implemented:

- `generate-first-mission-batch` now treats route identity errors as backend validation blockers:
  - duplicate `route.items[].item_id`
  - duplicate `route.items[].candidate_id`
  - duplicate route artist/title/type identity
  - missing route `candidate_id`
  - route `candidate_id` not found in the supplied candidate pool
- Adapted app missions now also fail backend validation on duplicate app `items[].item_id`.
- Generation responses and `alpha_generation_runs.validation` now include a redacted `route_identity` summary.
- Prompt/system instructions now state that duplicate route identity is a hard import blocker.
- Added a `duplicate_item_id` replay fixture for the Supabase generation smoke.
- Extended `scripts/smoke_supabase_generate_first_mission_batch.mjs` to verify duplicate route identity blocks.
- Extended `scripts/summarize_alpha_live_run.mjs` to surface route identity failures and client import/state diagnostics.

Live deployment status:

- Not deployed from this shell. `supabase` CLI and Supabase service credentials are not present in the local environment.
- Required live actions: apply `supabase/migrations/20260525120000_alpha_client_state_snapshot_diagnostics.sql` and deploy `supabase/functions/generate-first-mission-batch` plus `supabase/functions/submit-alpha-diagnostic`.

### Core Waymark Build

Implemented:

- Bumped the Alpha first-run state version to `alpha1_generation_guard_diagnostics_2026_05_25_01`, so the next installed build forces a clean Alpha reset instead of resuming the build 11/12 generation state.
- Added `client_state_snapshot` as a first-class diagnostic artifact type.
- Support diagnostics packages now include a client state snapshot with:
  - app version/build
  - root-stage inputs
  - generation state/progress/counts
  - Survey session summary
  - Supabase/Music auth status without tokens
  - local session/package/upload status
- The locked first-run generation screen now exposes:
  - Prepare Support Diagnostics
  - Share Support Diagnostics
  - Upload Diagnostics to Waymark
  - Stop Waiting
  - Start Fresh even while generation is loading
- Generation requests now have a timeout guard.
- Cancelled generation records a failure state and prepares diagnostics.
- The last generation failure message is persisted in `waymark.alpha1.generation_failure_message` so relaunches can explain the previous failure.

### Supabase Diagnostics

Implemented:

- `submit-alpha-diagnostic` now allows `client_state_snapshot`.
- Added `client_state_snapshot` fixture coverage.
- Added a migration that updates the diagnostic artifact type check constraint for existing Supabase projects.

### Atlas / Prompt Contract

Partially implemented in Infra/prompt guardrails:

- Hard uniqueness rules are now included in the live Edge prompt contract.
- Backend validation now enforces candidate membership and route identity uniqueness.

Still recommended for Atlas lane:

- Promote route identity invariants into the formal mission-generation handoff contract.
- Add stable `route_candidate_key` / `dedupe_group` fields to candidate dictionaries so validators can avoid display-string inference.

## Verification

Passed:

```bash
node scripts/smoke_supabase_generate_first_mission_batch.mjs
```

Passed:

```bash
COPYFILE_DISABLE=1 xcodebuild -scheme MusicAtlasController -configuration Debug -sdk iphonesimulator -destination 'platform=iOS Simulator,name=iPhone 17,OS=26.5' -derivedDataPath /tmp/musicmission-generation-recovery/DerivedData test
```

Passed:

```bash
plutil -lint MusicAtlasController/Support/Info.plist
```

Passed:

```bash
git diff --check -- supabase/functions/generate-first-mission-batch/index.ts supabase/functions/submit-alpha-diagnostic/index.ts scripts/smoke_supabase_generate_first_mission_batch.mjs scripts/summarize_alpha_live_run.mjs MusicAtlasController/Models/AppModel.swift MusicAtlasController/Views/RootView.swift MusicAtlasController/Services/SessionExporter.swift supabase/migrations/20260524170000_alpha_client_diagnostics.sql supabase/migrations/20260525120000_alpha_client_state_snapshot_diagnostics.sql
```

## Open Deployment Step

Before this can fix live mission generation in TestFlight, the Supabase backend must be updated:

```bash
supabase db push
supabase functions deploy generate-first-mission-batch
supabase functions deploy submit-alpha-diagnostic
```

Use the project `ewuffhezhgyskcfyzkvw` and keep secrets out of logs.

## Build 13 Readiness

The app bundle is set to version `0.2`, build `13`.

Build 13 should be uploaded only after or alongside the Supabase deploy, because the app can now produce `client_state_snapshot` diagnostics and the live backend must accept that artifact type.
