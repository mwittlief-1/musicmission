# Next Dispatch Prompts

Generated: 2026-05-20

## Survey Simulation Harness Dispatch

Use this in a new Codex chat:

```text
We are building Waymark's Survey Simulation Harness.

Read these files first:
- data/product_contracts/graph_staging_contract.md
- data/product_contracts/survey_simulator_build_brief.md
- data/product_contracts/cross_team_consistency_review.md
- data/canonical_graph/import_dry_run/canonical_graph_manifest.json
- data/canonical_graph/import_dry_run/import_dry_run_report.md

Build the v0.1 survey simulator as a read-only consumer of the staging canonical graph.

Do not mutate canonical graph data.
Do not expose hidden fake-user data to the Survey Builder or predictor.
Keep hidden reason tags out of visible transcripts.
Use typed music_object_ref values rather than vague object IDs.

First implementation slice:
1. Create data/survey_simulation/ structure.
2. Define fake profile, Apple payload, hidden corpus, survey run, page, and response JSON shapes.
3. Create validators.
4. Create 10 seed fake profiles with sparse hidden reaction corpora.
5. Implement graph-only and Apple-biased Artist Page 1.
6. Simulate responses via hidden corpus lookup.
7. Export survey_run.json, survey_transcript.md, page_generation_log.json, recorded_responses.json, apple_payload_used.json, and hidden_lookup_coverage_report.md.
8. Produce simulation_acceptance_report.md.

Stop before LLM prediction backtest unless the first slice validates cleanly.
```

## Atlas Schema Contract Dispatch

Use this in a separate new Codex chat:

```text
We are building Waymark's Atlas Schema Contract v0.1: User Interpretation Layer.

Read these files first:
- data/product_contracts/graph_staging_contract.md
- data/product_contracts/atlas_schema_build_brief.md
- data/product_contracts/cross_team_consistency_review.md
- data/canonical_graph/policy_hardening/schema_policy_review.md
- data/canonical_graph/policy_hardening/canonical_identity_policy.md
- data/canonical_graph/policy_hardening/composition_recording_policy.md

Produce a provisional Atlas schema contract and examples.

The Atlas must reference canonical graph objects when available, but must also support user-local, external-catalog, unresolved, and composition-placeholder music objects.

Do not treat AtlasNode roles as authoritative. Role truth belongs in AtlasRoleAssignment.
Do not let Survey or Mission Generation mutate the canonical graph.
Do not let Mission Review auto-promote generated hypotheses into Atlas truth.

Primary outputs:
- data/atlas_schema/atlas_schema_contract_v0_1.md
- data/atlas_schema/atlas_schema_contract_v0_1.json
- data/atlas_schema/examples/landmark.json
- data/atlas_schema/examples/region.json
- data/atlas_schema/examples/frontier.json
- data/atlas_schema/examples/dead_end.json
- data/atlas_schema/examples/waypoint.json
- data/atlas_schema/examples/signal.json
- data/atlas_schema/examples/taste_feature.json
- data/atlas_schema/examples/survey_seeded_update.json
- data/atlas_schema/examples/mission_review_possible_update.json
- data/atlas_schema/atlas_schema_acceptance_report.md
```
