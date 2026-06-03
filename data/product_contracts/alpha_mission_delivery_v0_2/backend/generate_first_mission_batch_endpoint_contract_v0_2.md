# Backend Endpoint Contract Draft v0.2

This is a contract/stub only. No Supabase function is implemented in this slice.

## Endpoint

`POST /functions/v1/generate-first-mission-batch`

## Input

- `tester_id`, `user_id` or `session_id`
- survey evidence export
- starter digest/profile substrate
- candidate pool or opportunity window
- requested mission batch size, default `3`
- allowed mission types
- contract versions
- safety constraints

## Output

- `run_id`
- `status`
- `missions[]`
- validation report
- `app_import_ready_count`
- `blocked_count`
- repair attempts
- error/fallback info

## Logging Requirements

- prompt/template version
- model/version/cost/latency when generation is added
- debug-safe input packet/run record
- output persistence
- validation status
- repair/retry status where implemented
- app-import readiness status

## First Batch Composition

Default batch size: 3 missions.

Suggested composition:

1. one low-risk context/gateway/nearby mission;
2. one boundary or bridge mission;
3. one deeper/archetype-depth mission if safety gates pass.
