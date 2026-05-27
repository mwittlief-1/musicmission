# Alpha Backlog Audit 2026-05-22

Audit time: 2026-05-22, America/Indiana/Indianapolis.

## Summary

Most lane backlogs are complete or complete-with-caveats. Supabase / Infrastructure has now completed all offline/non-account-dependent work. Remaining infrastructure work is blocked by live Supabase project access and secrets. Mission Generation still has retry work for app-importable mission batches.

Current checklist counts:

| lane | complete | open | issue/blocked | in progress |
| --- | ---: | ---: | ---: | ---: |
| Core Waymark Build | 17 | 0 | 0 | 0 |
| Canonical Music Graph | 13 | 0 | 0 | 0 |
| Survey Simulator | 13 | 0 | 0 | 0 |
| Atlas Schema | 14 | 0 | 0 | 0 |
| Mission Generation / Closed-Loop | 9 | 0 | 1 | 1 |
| Supabase / Infrastructure | 10 | 0 | 4 | 0 |

## Immediate Dispatch

Send this to the agents:

```text
Backlog audit is at docs/alpha_backlog/backlog_audit_2026_05_22.md. Supabase/Infrastructure completed offline infra work and is blocked only on live Supabase project access/secrets/deploy. Mission Generation should retry MGN-010 using the new Canonical alpha_v0 candidate pool and Core import adapter. Core, Canonical, Survey, and Atlas should do verification/handoff cleanup only unless they find a concrete issue raised by another lane.
```

## Remaining Work By Lane

### Supabase / Infrastructure

Offline work complete; live deploy blocked.

Completed:

- `INF-001` local scaffold exists:
  - `supabase/config.toml`
  - `supabase/migrations/20260521160000_alpha_generation_logs.sql`
  - `supabase/functions/generate-first-mission-batch/index.ts`
  - `supabase/functions/.env.example`

Completed offline tasks:

- `INF-002` local tooling checked and documented
- `INF-007` Edge Function adapter reconciled with golden packet builder
- `INF-008` function contract fixtures added
- `INF-009` local fixture smoke test added
- `INF-010` generation audit fields added/checked
- `INF-011` evidence upload recommendation documented
- `INF-012` app configuration contract documented
- `INF-013` backend acceptance script added and run
- `INF-014` TestFlight operational runbook documented

Tasks that likely need account/secrets:

- `INF-003` link Supabase project
- `INF-004` apply migration
- `INF-005` set Edge Function secrets
- `INF-006` deploy `generate-first-mission-batch`

Issue to raise if needed:

| issue id | blocker | owner lane | needed for | current workaround | status |
| --- | --- | --- | --- | --- | --- |
| `INF-I001` | Supabase project ref, anon key, service-role deployment access, OpenAI API key, or function secrets unavailable. | Product / Infrastructure account owner | Live backend deployment and Core remote assignment. | Offline acceptance, fixture replay, type-check, app config contract, and local golden-packet stub. | open |

### Mission Generation / Closed-Loop

Active retry lane.

Remaining:

- `MGN-010` is now `in progress / ready to retry`, not fully blocked.
- Use Canonical artifact: `data/alpha_consumable_layer/alpha_v0/sample_compact_candidate_pool_alpha_v0.json`.
- Use Core adapter/import target: `MissionImportGate`, `LocalMissionProvider`, and Supabase batch-response import tests.
- Goal: produce at least one fully app-importable Alpha mission batch artifact, then validate it against Core's `mission.v0.2` import gate.

Still blocked:

- `MGN-011` backend generation/import handoff remains blocked on Supabase audit envelope/deployment.

Expected output:

- app-importable mission batch artifact
- validation/evaluator report
- explicit statement whether `MGN-I001` and `MGN-I002` can be closed or need more specific replacement issues

### Core Waymark Build

No new feature backlog remains from the current file.

Verification/handoff tasks:

- Confirm code compiles after the latest modified files.
- Re-run simulator tests.
- Resolve duplicate/unintended file `MusicAtlasController/Views/MissionListView 2.swift` if it is accidental.
- Confirm Release bundle scan still excludes sample/personal mission JSON.
- Await Supabase live config and Product release/privacy decisions.

Current remaining caveats:

- real Supabase project URL, anon key, Edge Function URL, and auth policy
- final Survey visibility in first TestFlight
- privacy, retention, deletion, and support copy
- final app name, icon, bundle ID rename, and tester group policy
- final Atlas ingestion field names beyond `atlas_signal_candidate_bundle.v0.1`

### Canonical Music Graph

No active non-dependent backlog remains.

Available support:

- respond to Mission Generation if `sample_compact_candidate_pool_alpha_v0.json` lacks a required field
- respond to Core if resolver policy fields are insufficient
- keep `alpha_v0` surfaces stable unless a downstream issue requires a patch

### Survey Simulator

No active non-dependent backlog remains.

Available support:

- respond if Core needs app packet field clarification
- respond if Product decides Survey is visible in first TestFlight
- keep Survey Evidence Export v0.1 and app packet examples stable

### Atlas Schema

No active non-dependent backlog remains.

Available support:

- respond if Core or Supabase need exact app evidence `Signal` ingestion fields
- respond if Mission Generation needs additional `AtlasDigestView` fields
- keep promotion/demotion automation out of scope unless Product explicitly asks for a policy pass

## Product / Human Decisions Still Open

These are not good autonomous-agent tasks unless the user gives the decision:

- Supabase project/account/secrets
- first TestFlight Survey visibility
- evidence upload vs manual export for first TestFlight
- privacy/retention/deletion/support copy
- final app name, app icon, bundle rename, tester group policy
- whether any `AtlasDelta.user_facing_summary_inputs` appears in the app
- promotion/demotion thresholds beyond manual/reviewed Alpha policy

## Suggested Agent Assignments

1. Supabase / Infrastructure: wait for live Supabase project access/secrets, then run INF-003 through INF-006 and a live smoke test.
2. Mission Generation: retry MGN-010 against Canonical `alpha_v0` candidate pool and Core import gate. Do not wait for Supabase.
3. Core Waymark Build: run verification, clean duplicate files if accidental, and prepare for Supabase config handoff.
4. Canonical Music Graph: stand by for MGN field-gap issues.
5. Survey Simulator: stand by for Core app packet clarification or Product visibility decision.
6. Atlas Schema: stand by for exact ingestion/read-model field questions.
