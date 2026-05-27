# Supabase / Infrastructure Dispatch - Live Generation Recovery - 2026-05-25

## Mission

Make live Supabase stop returning missions the app will reject, and make diagnostic upload visible in Supabase.

## Read First

- `docs/alpha_backlog/live_generation_recovery_dispatch_2026_05_25.md`
- `docs/infra/waymark_alpha_live_diagnostic_evidence_review_2026_05_25.md`
- `docs/infra/waymark_alpha_generation_recovery_implementation_2026_05_25.md`

## P0 Tasks

- [ ] INF-LGR-001 Deploy stricter `generate-first-mission-batch`.
  - Use current local function source.
  - Live validation must reject duplicate route `item_id`.
  - Live validation must reject duplicate display identity.
  - Live validation must reject route items outside `candidate_pool.candidates`.
  - Live rows must include populated `validation.route_identity`.

- [ ] INF-LGR-002 Deploy diagnostics support.
  - Apply the migration that allows `client_state_snapshot`.
  - Deploy `submit-alpha-diagnostic`.
  - Confirm the live function accepts all current diagnostic artifact types.

- [ ] INF-LGR-003 Run backend acceptance.
  - Run function smoke tests.
  - Run syntax/type checks available in the repo.
  - Run `scripts/summarize_alpha_live_run.mjs` against `trusted-alpha-001` after live verification.

- [ ] INF-LGR-004 Prove diagnostic persistence.
  - Preferred: upload one benign fixture or app-produced diagnostic through the live function.
  - Confirm `alpha_client_diagnostic_artifacts` has at least one new row.
  - Do not expose service-role keys or raw private payloads.

- [ ] INF-LGR-005 Document live deploy result.
  - Add a short deploy note under `docs/infra/`.
  - Include function versions, migration status, smoke result, and whether diagnostic rows are present.

## Acceptance

- A duplicate route-item fixture is blocked before app import.
- A non-candidate route-item fixture is blocked before app import.
- Live `alpha_generation_runs.validation.route_identity` is populated for new runs.
- `submit-alpha-diagnostic` accepts `client_state_snapshot`.
- `alpha_client_diagnostic_artifacts` contains a new live row after the smoke.

## Blockers To Raise

| issue id | blocker | owner lane | needed for | current workaround | status |
| --- | --- | --- | --- | --- | --- |
| `INF-LGR-I001` |  |  |  |  | open |

## Completion Note

- status:
- files changed:
- commands/tests run:
- live deploy or build number:
- remaining blockers:
- handoff needed from:
