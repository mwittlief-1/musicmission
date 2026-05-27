# Live Alpha Safe Smoke Report - 2026-05-25

## Summary

Core and hosted Supabase smoke checks are green for the current route-identity contract. The remaining proof before calling the next TestFlight build fully app-authenticated is a physical/TestFlight run using the app's real Supabase Auth session from Sign in with Apple.

## Deployed During This Pass

- `generate-first-mission-batch`
  - Deployed to project `ewuffhezhgyskcfyzkvw`.
  - Live function version after deploy: `14`.
  - Includes route identity fields in the OpenAI response schema and app mission adapter.
- `submit-alpha-diagnostic`
  - Deployed to project `ewuffhezhgyskcfyzkvw`.
  - Live function version after deploy: `3`.
- Migration applied:
  - `20260525120000_alpha_client_state_snapshot_diagnostics.sql`
  - Adds `client_state_snapshot` to the live diagnostic artifact type constraint.

## Live Smoke Results

### Generation

- Tester alias: `trusted-alpha-001-safe-smoke`
- Run ID: `6b1fc23f-426b-4590-9410-c786466af741`
- Request ID: `safe-live-generation-20260525181805`
- Result: `app_import_candidate`
- App missions returned: `1`
- App mission validation: passed
- Generation validation: passed
- Route identity validation:
  - `route_item_count`: `4`
  - `candidate_pool_count`: `10`
  - `checked_candidate_membership`: `true`
  - duplicate route item IDs: none
  - duplicate candidate IDs: none
  - duplicate display identity keys: none
  - non-candidate IDs: none

### Diagnostic Upload

- Tester alias: `trusted-alpha-001-safe-smoke`
- Upload ID: `28d24335-6b4e-48f0-b2ec-6b25969dbac9`
- Artifact type: `client_state_snapshot`
- Result: `accepted`
- `user_id_present`: `false`

## Verification Commands

```bash
node scripts/smoke_supabase_generate_first_mission_batch.mjs
npx -y -p typescript tsc --noEmit --target ES2022 --lib ES2022,DOM --strict supabase/functions/generate-first-mission-batch/index.ts
npx -y -p typescript tsc --noEmit --target ES2022 --lib ES2022,DOM --strict supabase/functions/submit-alpha-diagnostic/index.ts
npx -y supabase functions list --project-ref ewuffhezhgyskcfyzkvw
npx -y supabase migration list --linked
SUPABASE_URL=... SUPABASE_SERVICE_ROLE_KEY=... node scripts/summarize_alpha_live_run.mjs --tester-alias trusted-alpha-001-safe-smoke --since 2026-05-25T18:10:00.000Z
```

## Remaining App-Authenticated Smoke

The live checks above used the project anon JWT from the CLI. They prove hosted function deployment, persistence, route identity validation, and diagnostic artifact acceptance. They do not prove the app's real Supabase Auth session from Sign in with Apple.

Remaining check:

1. Install/run the next TestFlight or device build.
2. Sign in with Apple in the app.
3. Complete Survey and trigger first mission generation.
4. Upload support diagnostics or generate a `client_state_snapshot`.
5. Confirm the resulting rows show app-authenticated behavior, especially diagnostic `user_id_present = true`.

## Packaging Guidance

The backend is safe enough for the next app-authenticated smoke. Treat TestFlight packaging as allowed for smoke purposes, but do not claim full app-authenticated acceptance until a real app session produces persisted generation and diagnostic rows.
