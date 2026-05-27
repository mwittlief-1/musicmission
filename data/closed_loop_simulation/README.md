# Closed-Loop Simulation

This directory holds closed-loop mission-generation and Atlas-learning simulation evidence.

## Tracked

- `closed_loop_manifest.json`
- `closed_loop_mission_batch_schema_v0_1.json`
- `adaptive_second_batch_schema_v0_1.json`
- `closed_loop_acceptance_report.md`

These files are small contract and acceptance artifacts that describe the simulation shape, schema, status, and review result.

## Ignored By Default

- `profile_*/` directories.

Profile directories contain generated live/API run material: requests, responses, mission batches, validation output, hidden evaluator traces, and qualitative profile reviews. Keep them local or archive externally unless a maintainer promotes a specific fixture.
