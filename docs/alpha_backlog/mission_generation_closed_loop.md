# Mission Generation / Closed-Loop Learning Backlog

Lane goal: produce reviewed first-batch and adaptive second-batch mission artifacts from Atlas digest/delta context, preserve Mission-as-experiment semantics, and expose app-import candidates only after product, resolution, and evaluator gates pass.

## Non-Dependent Tasks

- [x] MGN-001 Publish Mission Generation PM Alpha brief.
  - Output: `data/product_contracts/alpha_briefs/Waymark Mission Generation and Closed-Loop Learning PM Alpha Brief v0.1.md`

- [x] MGN-002 Publish Mission Generation Alpha handoff contract.
  - Output: `data/product_contracts/mission_generation_alpha_handoff_v0_1.md`

- [x] MGN-003 Freeze first-batch portfolio semantics.
  - Output: `data/product_contracts/mission_generation_alpha_handoff_v0_1.md`
  - Backing artifact: `waymark-ai-tests/fixtures/prompt_templates/closed_loop_mission_batch_v0_1.md`

- [x] MGN-004 Freeze adaptive second-batch contract.
  - Output: `data/closed_loop_simulation/a3_first_batch_learning_v0_1_adaptive_contract_v0_1/adaptive_second_batch_schema_v0_1.json`
  - Summary: adaptive second-batch missions require `adaptation_action`, source refs, `source_atlas_delta_refs`, visible batch-one learning, hit/miss/no-signal semantics, and resolution suitability fields.

- [x] MGN-005 Validate live adaptive closed-loop proof.
  - Output: `data/closed_loop_simulation/a3_first_batch_learning_v0_1_adaptive_contract_v0_1/closed_loop_acceptance_report.md`
  - Output: `waymark-ai-tests/reports/adaptive_second_batch_report_20260521T175205Z.md`

- [x] MGN-006 Preserve hidden-truth exclusion in mission and Atlas-facing outputs.
  - Output: `data/closed_loop_simulation/a3_first_batch_learning_v0_1_adaptive_contract_v0_1/closed_loop_acceptance_report.md`
  - Note: hidden simulator traces are evaluator-only and excluded from Atlas-facing feedback, update, delta, and digest artifacts.

- [x] MGN-007 Define product status and app-import gate semantics.
  - Output: `data/product_contracts/mission_generation_alpha_handoff_v0_1.md`
  - Invariant: `product_fail -> app_import_ready=false`.

- [x] MGN-008 Document evaluator responsibilities.
  - Output: `data/product_contracts/mission_generation_alpha_handoff_v0_1.md`
  - Coverage: schema validity, mission structure, route readiness, conditional Atlas updates, false-nearby discipline, adaptive second-batch fields, AtlasDelta refs, and closed-loop suitability.

- [x] MGN-009 Record Alpha model posture.
  - Output: `data/product_contracts/mission_generation_alpha_handoff_v0_1.md`
  - Current posture: `gpt-5.4-mini` for bounded mission generation; `gpt-5.5` for fallback/adjudication.

- [x] MGN-010 Produce fully app-importable Alpha mission batch.
  - Candidate Pool retry target is now route-ready: `data/alpha_consumable_layer/alpha_v0/sample_compact_candidate_pool_alpha_v0.json`.
  - Result: live `gpt-5.4-mini` rerun using `MissionGenerationDigestView + route-ready alpha_v0 candidate pool` returned `status=app_import_candidate`.
  - Validation: rich mission schema valid, automated score `1.0`, Core `mission.v0.2` validation passed.
  - Output: `data/mission_generation/alpha_first_batch_route_ready_v0_1/public_profile_01_A3_Al1_S2/20260523T225550Z/`
  - Output: `data/mission_generation/alpha_first_batch_readiness_v0_1/alpha_v0_candidate_pool_route_readiness_report.md`
  - Previous blocker: `MGN-I004`, now `closed_by_app_import_candidate_generation`

- [x] MGN-011 Wire backend generation/import handoff.
  - Offline response/audit contract exists.
  - Supabase live generation smoke is reported passing in `docs/alpha_backlog/supabase_infrastructure.md`.
  - Remaining live app invocation work belongs to Core/Infra auth/session wiring, not Mission Generation contract shape.
  - Raised issue `MGN-I003` is closed by Infrastructure live-smoke completion.

## Post-Brand Review Alpha 1 Tasks

Product decisions received 2026-05-22 make the first mission batch a post-Survey generated artifact.

- [x] MGN-012 Define Survey-completion first-batch trigger contract.
  - Consume AtlasDigest/Survey Evidence-derived context only.
  - Do not consume hidden simulator truth or raw construction logs.
  - Output: `data/product_contracts/survey_completion_first_batch_generation_contract_alpha_v0_1.md`

- [x] MGN-013 Produce one generated first mission batch suitable for Alpha first-run.
  - Batch should become available after Survey completion.
  - Preserve statuses: generated, review-needed, blocked, app-import-candidate.
  - Completed: first generated post-Survey Alpha mission batch candidate uses `MissionGenerationDigestView` plus the route-ready `alpha_v0` candidate pool.
  - Output: `data/mission_generation/alpha_first_batch_route_ready_v0_1/public_profile_01_A3_Al1_S2/20260523T225550Z/`
  - Existing integration fixture remains valid: `data/alpha_packets/golden_alpha_packet_v0_1/`
  - Previous blocker: `MGN-I004`, now `closed_by_app_import_candidate_generation`

- [x] MGN-014 Coordinate backend response for automatic assignment/import.
  - Output must map cleanly through Core's app-import gate.
  - No generated mission ships bundled in the app.
  - Output: `data/product_contracts/survey_completion_first_batch_generation_contract_alpha_v0_1.md`
  - Backing artifacts: `supabase/functions/generate-first-mission-batch/index.ts`, `docs/infra/supabase_adapter_reconciliation_v0_1.md`, `data/alpha_packets/golden_alpha_packet_v0_1/response/supabase_generate_first_mission_batch_response.json`

## Live Alpha Smoke Recovery Tasks

Source: `docs/alpha_backlog/alpha_live_smoke_recovery_2026_05_24.md`.

- [x] MGN-015 Define trusted Alpha handling for `review_needed` outputs.
  - Distinguish hard safety/validation blockers from product-review notes that are acceptable for trusted internal Alpha.
  - Proposed statuses:
    - `blocked`: never import.
    - `review_needed`: generated route is structurally valid but product review flags exist.
    - `app_import_candidate`: importable without extra flags.
    - optional Alpha-only `app_import_candidate_with_review_flags`: importable if Core/app validation passes and review flags are stored.
  - Coordinate exact response semantics with Supabase and Core before implementation.
  - Output: update the mission generation handoff contract and backend adapter notes.
  - Completed: `data/mission_generation/live_alpha_smoke_recovery_v0_1/mission_generation_live_alpha_smoke_recovery_contract_v0_1.md`
  - Updated: `data/product_contracts/mission_generation_alpha_handoff_v0_1.md`
  - Updated: `data/product_contracts/survey_completion_first_batch_generation_contract_alpha_v0_1.md`
  - Updated: `docs/infra/supabase_adapter_reconciliation_v0_1.md`

- [!] MGN-016 Repair prompt/evaluator behavior causing false review gates.
  - Use live audit examples from build `9` to identify why risky/default selections triggered manual review.
  - Adjust prompt, candidate constraints, or evaluator wording so Alpha-eligible route-ready candidates clear the app-import gate more consistently.
  - Preserve the hard block for unsafe, unresolved, schema-invalid, or graph-quarantined outputs.
  - Acceptance: replay fixtures include at least one former `review_needed` case that now either returns a safer app-import candidate or a precise non-import reason.
  - Non-dependent work completed: prompt guidance now says route-ready risky/frontier/trap/dead-end/waypoint review flags do not by themselves require `ready_for_app_import=false`.
  - Updated: `waymark-ai-tests/fixtures/prompt_templates/mission_generator_candidate_constrained_v0_1.md`
  - Updated: `scripts/run_alpha_first_batch_generation_v0_1.py`
  - Updated: `supabase/functions/generate-first-mission-batch/index.ts`
  - Blocked portion: build `9` live audit examples are not present in the repo, so replay-based acceptance is blocked by `MGN-I005`.

- [x] MGN-017 Tighten 10-mission batch semantics.
  - Define diversity/portfolio expectations across ten one-at-a-time generation calls.
  - Ensure prompt context fields such as batch mission index, total, prior imported mission IDs, and seed/diversity directive are sufficient to avoid ten near-duplicates.
  - Decide whether backend should support true batch output later; do not block Alpha on that if one-at-a-time calls are reliable.
  - Completed: `data/mission_generation/live_alpha_smoke_recovery_v0_1/mission_generation_live_alpha_smoke_recovery_contract_v0_1.md`
  - Recommendation: one-at-a-time generation remains acceptable for Alpha, with `target_imported_missions=10` and configurable `max_generation_attempts=14`.
  - Required prompt context fields are documented: batch index/total, attempt index/ceiling, batch seed, portfolio slot, mission objective, prior imported mission IDs/candidate IDs, prior attempt summaries, and prior review-needed reasons.

## Dependency Tripwires

Raise an issue when:

- Candidate Pool Builder cannot provide concrete candidate pool or route resolution metadata needed to move from `product_review_needed` to `app_import_candidate`.
- Core app import requires mission fields different from the rich mission-generation output and no adapter contract exists.
- Supabase generation responses cannot preserve product status, app-import readiness, schema validation, model/cost/latency, prompt version, and audit refs.
- Atlas promotion thresholds are requested for generated mission updates.
- Product asks Mission Generation to run inside the iOS app for Alpha.
- Product asks generated first missions to appear before Survey evidence exists.

## Do Not Do Yet

- Do not ship generated or prebuilt missions as bundled TestFlight user content.
- Do not generate missions locally in the iOS app.
- Do not auto-promote Atlas updates.
- Do not treat schema-valid as app-import-ready.
- Do not use hidden simulator truth, raw survey construction logs, Profile Writer output, or generator-private traces as Atlas evidence.
- Do not feed raw canonical graph rows directly into mission generation.

## Raised Issues

| issue id | blocker | owner lane | needed for | current workaround | status |
| --- | --- | --- | --- | --- | --- |
| `MGN-I001` | Need compact concrete candidate-pool export with resolution metadata and app-import-eligible candidate roles. | Canonical Music Graph / Candidate Pool | Fully app-importable Alpha mission batches and reduced unresolved placeholders. | Resolved through `MGN-I004`: current `alpha_v0` pool has route-ready track/album objects and remains graph metadata, not taste truth. | closed_by_MGN-I004 |
| `MGN-I002` | Need final adapter contract from rich mission-generation output to app `mission.v0.2` payload and import gate. | Core Waymark Build | Reviewed mission assignment/import into TestFlight app. | Core `MissionImportGate`, `LocalMissionProvider`, Supabase response import tests, and Supabase adapter reconciliation are available. | closed_offline |
| `MGN-I003` | Live Supabase project access, function secrets, deploy, and live smoke test were unavailable from this lane. | Supabase / Infrastructure | Remote generation/import path and reproducible Alpha audit trail. | Infrastructure now reports linked project, deployed function, persisted audit row, and live generation smoke pass. | closed_by_infra_live_smoke |
| `MGN-I004` | The `alpha_v0` sample compact candidate pool previously contained only artist-level candidates in populated pools; app import requires concrete track/album route items or a resolver step before mission import. | Canonical Music Graph / Candidate Pool | Post-Survey first mission batch that can clear Core's `mission.v0.2` app-import gate without pseudo-playable placeholders. | Canonical/Candidate Pool now provides `72` route-ready track/album candidates. Mission Generation rerun at `data/mission_generation/alpha_first_batch_route_ready_v0_1/public_profile_01_A3_Al1_S2/20260523T225550Z/` returned `app_import_candidate` and passed Core `mission.v0.2` validation. | closed_by_app_import_candidate_generation |
| `MGN-I005` | Build `9` live generation/import audit examples are not available in the repo, including the exact `review_needed` request/result/import diagnostics that triggered the live smoke blocker. | Core Waymark Build / Supabase Infrastructure | Replaying a former live `review_needed` case to prove the prompt/evaluator repair either returns a safer app-import candidate or a precise non-import reason. | Mission Generation updated the policy/prompt language from the recovery packet and can use generic `review_needed` fixtures until linked live audit artifacts are exported. | open |

## Completion Report

- files changed:
  - `data/product_contracts/mission_generation_alpha_handoff_v0_1.md`
  - `data/product_contracts/survey_completion_first_batch_generation_contract_alpha_v0_1.md`
  - `data/mission_generation/alpha_first_batch_readiness_v0_1/alpha_v0_candidate_pool_route_readiness_report.md`
  - `data/mission_generation/alpha_first_batch_readiness_v0_1/alpha_v0_candidate_pool_route_readiness_report.json`
  - `data/mission_generation/live_alpha_smoke_recovery_v0_1/mission_generation_live_alpha_smoke_recovery_contract_v0_1.md`
  - `waymark-ai-tests/fixtures/prompt_templates/mission_generator_candidate_constrained_v0_1.md`
  - `scripts/run_alpha_first_batch_generation_v0_1.py`
  - `supabase/functions/generate-first-mission-batch/index.ts`
  - `docs/infra/supabase_adapter_reconciliation_v0_1.md`
  - `docs/alpha_backlog/mission_generation_closed_loop.md`
  - `docs/alpha_backlog/README.md`
- validators run:
  - `node scripts/validate_alpha_consumable_layer_alpha_v0.mjs`
  - Result: passed; Candidate Pool route-ready export validates with 72 route-ready track/album candidates.
  - `python3 -m json.tool data/mission_generation/alpha_first_batch_readiness_v0_1/alpha_v0_candidate_pool_route_readiness_report.json`
  - Result: passed.
  - `python3 -m compileall -q waymark-ai-tests/src`
  - `.venv/bin/python scripts/validate_mission_json.py data/alpha_packets/golden_alpha_packet_v0_1/app_import/app_mission_v0_2.json`
  - `.venv/bin/python scripts/validate_survey_evidence_export_v0_1.py --export data/alpha_packets/golden_alpha_packet_v0_1/inputs/survey_evidence_export.json`
  - `node scripts/smoke_supabase_generate_first_mission_batch.mjs`
  - `python3 -m py_compile scripts/run_alpha_first_batch_generation_v0_1.py`
  - `npx -y -p typescript -p @types/deno tsc --noEmit --target ES2022 --lib ES2022,DOM --strict supabase/functions/generate-first-mission-batch/index.ts`
  - `git diff --check -- docs/alpha_backlog/mission_generation_closed_loop.md data/product_contracts/mission_generation_alpha_handoff_v0_1.md data/product_contracts/survey_completion_first_batch_generation_contract_alpha_v0_1.md docs/infra/supabase_adapter_reconciliation_v0_1.md data/mission_generation/live_alpha_smoke_recovery_v0_1/mission_generation_live_alpha_smoke_recovery_contract_v0_1.md waymark-ai-tests/fixtures/prompt_templates/mission_generator_candidate_constrained_v0_1.md scripts/run_alpha_first_batch_generation_v0_1.py scripts/smoke_supabase_generate_first_mission_batch.mjs supabase/functions/generate-first-mission-batch/index.ts`
- latest live proof:
  - `data/closed_loop_simulation/a3_first_batch_learning_v0_1_adaptive_contract_v0_1/closed_loop_acceptance_report.md`
- remaining blockers:
  - No active Candidate Pool blocker. Mission Generation live rerun passed and produced an app-import candidate artifact.
  - `MGN-I005` remains open: live build `9` `review_needed` audit examples are needed from Core/Supabase to complete replay-based false-review-gate acceptance.
- ready for Core app integration status: `yes_with_caveats`
