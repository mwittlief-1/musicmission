# Waymark Mission Generation Alpha Handoff v0.1

Generated: 2026-05-21

Status: `ALPHA_READY_WITH_REVIEW_AND_RESOLUTION_GATES`

## Purpose

This handoff defines what the Mission Generation / Closed-Loop Learning lane can safely provide to Alpha planning, Core app import, Supabase generation, Atlas ingestion, and Candidate Pool Builder.

It is a product contract summary, not a final backend architecture.

## Controlling Artifacts

| artifact | purpose |
| --- | --- |
| `data/product_contracts/alpha_briefs/Waymark Mission Generation and Closed-Loop Learning PM Alpha Brief v0.1.md` | PM lane overview and Alpha readiness view. |
| `waymark-ai-tests/fixtures/schemas/mission_output_schema_v0_1.json` | Current rich mission-generation schema used by AI harness. |
| `waymark-ai-tests/fixtures/prompt_templates/closed_loop_mission_batch_v0_1.md` | Current closed-loop first/second batch generation prompt. |
| `waymark-ai-tests/src/waymark_ai_tests/closed_loop_simulation.py` | Current closed-loop harness and adaptive second-batch evaluator. |
| `data/closed_loop_simulation/a3_first_batch_learning_v0_1_adaptive_contract_v0_1/adaptive_second_batch_schema_v0_1.json` | Strict adaptive second-batch schema extension. |
| `data/closed_loop_simulation/a3_first_batch_learning_v0_1_adaptive_contract_v0_1/closed_loop_acceptance_report.md` | Latest live adaptive run acceptance report. |
| `waymark-ai-tests/reports/adaptive_second_batch_report_20260521T175205Z.md` | Latest live adaptive second-batch report. |
| `data/mission_generation/atlas_substrate_a3_v0_1_2/mission_generation_repair_brief_v0_1_3.md` | Route item resolution repair brief. |
| `data/product_contracts/app_local_candidate_pool_contract_alpha_v0.md` | Alpha candidate-pool source and guardrail contract. |
| `data/product_contracts/survey_completion_first_batch_generation_contract_alpha_v0_1.md` | Post-brand Survey-completion first-batch trigger and backend response contract. |
| `data/mission_generation/alpha_first_batch_readiness_v0_1/alpha_v0_candidate_pool_route_readiness_report.md` | Current retry result against the Canonical `alpha_v0` candidate pool and Core app-import gate. |
| `data/mission_generation/alpha_first_batch_route_ready_v0_1/public_profile_01_A3_Al1_S2/20260523T225550Z/` | First live route-ready Alpha generation run that passed rich mission schema, evaluator checks, and Core `mission.v0.2` validation. |
| `data/mission_generation/live_alpha_smoke_recovery_v0_1/mission_generation_live_alpha_smoke_recovery_contract_v0_1.md` | Trusted Alpha recovery policy for `review_needed`, review flags, and ten-mission attempt semantics. |
| `docs/alpha_backlog/live_generation_recovery_mission_generation_2026_05_25.md` | Live recovery hardening for candidate-pool-only generation, route identity uniqueness, and ten-mission batch memory. |

## Alpha Product Boundary

Mission Generation may produce:

- first-batch mission portfolios;
- adaptive second-batch mission portfolios;
- mission hypotheses;
- ordered routes;
- expected signals;
- reaction-specific chips;
- review readiness fields;
- mission-scoped possible Atlas update candidates;
- app-import candidate payloads only after the import gate passes.

Mission Generation must not produce:

- promoted Atlas truth;
- canonical graph mutation;
- hidden simulator evidence;
- final WWTSF copy;
- app-visible missions that contain pseudo-playable placeholders.

## First-Batch Contract

First-batch missions should be a portfolio, not six variants of the same idea.

Expected portfolio slots:

- `safe_anchor`
- `nearby_road`
- `frontier`
- `dead_end_or_contradiction_check`
- `waypoint_useful_not_canon`
- `wildcard_delight`

First batch only needs to be credible, varied, explainable, safe enough, and instrumented well enough to learn. It is not expected to perfectly understand a user after onboarding.

## Adaptive Second-Batch Contract

Second-batch missions must be visibly caused by Atlas changes from batch one.

Required adaptive fields:

- `mission_type`
- `adaptation_action`
- `source_signal_refs`
- `source_update_candidate_refs`
- `source_atlas_delta_refs`
- `what_batch_1_taught`
- `why_this_mission_now`
- `what_changed_since_prior_batch`
- `what_this_mission_is_not_doing_anymore`
- `success_condition`
- `failure_condition`
- `no_signal_interpretation`
- `expected_next_atlas_update`
- `resolution_quality_status`
- `closed_loop_learning_suitability`

Allowed `adaptation_action` values:

- `deepen`
- `pivot`
- `retire_pause`
- `contradiction_check`
- `dead_end_confirmation`

Hard rule:

```text
No adaptive second-batch mission is product-pass unless it references at least one source_atlas_delta_refs entry.
```

## App-Import Gate

Schema-valid is not app-import-ready.

A generated mission can be app-import candidate only when:

- product status is not `product_fail`;
- every route item has stable `mission_id` and `item_id`;
- every route item copies an exact `candidate_id` from the supplied route-ready `candidate_pool.candidates`;
- each playable route item has concrete artist/title/search metadata;
- every route item has unique `item_id`, unique `candidate_id`, and unique artist/title/type display identity inside the mission;
- each one-at-a-time first-batch call avoids route items listed in batch-memory fields supplied by `prompt_context`;
- unresolved candidate-search slots are absent, unless the mission is explicitly a search-calibration/debug mission;
- expected signals and feedback chip sets are present;
- `possible_atlas_update_candidates` are mission-scoped and conditional;
- risky/frontier/trap/contradiction items are review-needed by default;
- hidden simulator/private fields are absent;
- the app-side adapter can map the rich mission object into the current app mission schema.

Block app import when:

- route item title is a pseudo-playable placeholder;
- `resolution_quality_status = too_many_placeholders`;
- `closed_loop_learning_suitability = unsuitable`;
- product status is `product_fail`;
- `source_atlas_delta_refs` is empty for adaptive second batch;
- the payload implies promoted Atlas truth.

## Product Status Semantics

| status | meaning |
| --- | --- |
| `product_fail` | Do not import or show as a user mission. Repair or discard. |
| `product_review_needed` | Useful development/concierge artifact, but needs human review or resolution before app import. |
| `product_pass_candidate` | Product-meaningful mission output; still not app-import unless route and adapter gates pass. |
| `app_import_candidate` | Cleared for app assignment/import path after adapter validation. |
| `app_import_candidate_with_review_flags` | Alpha-only status for missions that clear adapter/Core import gates while carrying auditable product review notes. |

Invariant:

```text
product_fail -> app_import_ready=false
```

## Trusted Alpha Recovery Semantics

Live Alpha smoke testing showed that `review_needed` is too strict when it hard-stops a trusted tester after an otherwise app-valid generation. Mission Generation now distinguishes hard blockers from Alpha-tolerable review flags.

Hard blockers still prevent app import:

- rich mission schema invalid;
- app `mission.v0.2` adaptation invalid;
- Core import gate failure;
- pseudo-playable route titles or artist-only placeholders;
- selected route items not present in the route-ready candidate pool;
- missing or non-pool `route.items[].candidate_id`;
- duplicate `route.items[].item_id`;
- duplicate `route.items[].candidate_id`;
- duplicate route artist/title/type display identity;
- route items repeated from supplied first-batch memory/exclusion fields;
- graph/candidate quarantine or unsafe review status;
- hidden simulator truth, raw graph rows, raw Survey construction logs, or Profile Writer output;
- generated output implying promoted Atlas truth or canonical graph mutation.

Alpha-tolerable review flags may travel with an imported mission only when Core/app validation passes:

- risky, frontier, trap, dead-end, waypoint, or contradiction items explicitly marked review-needed;
- release-year inference or version notes marked as uncertainty;
- trap/dead-end positives use bounded exception, cultural-furniture, or reassess semantics;
- possible Atlas updates are conditional, mission-scoped, recurrence-gated, and review-required.

Prompt/evaluator rule:

```text
Do not set review_config.ready_for_app_import=false solely because route-ready risky/frontier/trap/waypoint items carry review flags. Set it false only for hard blockers or unresolved product questions that make the mission unsuitable for listening.
```

Recommended trusted Alpha statuses:

| status | app missions allowed | Mission Generation meaning |
| --- | --- | --- |
| `blocked` | no | Hard blocker or validation failure. |
| `review_needed` | no | Structurally useful but not app-importable without repair/review. |
| `app_import_candidate` | yes | App-valid and no extra Alpha review flags. |
| `app_import_candidate_with_review_flags` | yes, Alpha only | App-valid with auditable review notes. |

`app_import_candidate_with_review_flags` requires Supabase/Core implementation before live use. Until implemented, Mission Generation should still bias prompts toward cleaner `app_import_candidate` outputs when all hard gates pass.

## Ten-Mission First-Batch Semantics

Alpha first batch targets ten imported missions, not ten generation calls.

Recommended recovery default:

```text
target_imported_missions = 10
max_generation_attempts = 14
```

Generation should continue after isolated `review_needed` attempts until ten missions import, a hard failure appears, or the max-attempt ceiling is reached.

Each one-at-a-time generation call should receive:

- `batch_mission_index`;
- `batch_mission_total`;
- `attempt_index`;
- `max_generation_attempts`;
- `batch_seed`;
- `mission_portfolio_slot`;
- `mission_archetype`;
- `mission_objective`;
- `diversity_directive`;
- `prior_imported_mission_ids`;
- `prior_imported_candidate_ids`;
- `already_selected_route_item_ids`;
- `already_selected_candidate_ids`;
- `already_selected_display_keys`;
- `excluded_route_item_ids`;
- `excluded_candidate_ids`;
- `prior_attempt_summaries`;
- `prior_review_needed_reasons`.

Batch-memory field placement:

```text
prompt_context.already_selected_route_item_ids: string[]
prompt_context.already_selected_candidate_ids: string[]
prompt_context.already_selected_display_keys: string[]  # normalized as item_type:artist:title
prompt_context.excluded_route_item_ids: string[]
prompt_context.excluded_candidate_ids: string[]
```

Backward compatibility:

```text
If these arrays are omitted, the call behaves as a one-mission generation request. If supplied, any reuse is a hard import blocker.
```

Candidate-pool-only rule:

```text
MissionGenerationDigestView, Survey evidence, Atlas examples, strong-region summaries, and user vocabulary are context only. They can explain why a route should exist, but they cannot supply playable route items unless the exact object is also present in candidate_pool.candidates.
```

Minimum ten-mission portfolio coverage:

- at least two safe/anchor missions;
- at least two nearby-road or bridge missions;
- at least two frontier probes;
- at least one contradiction or dead-end check;
- at least one waypoint/useful-not-canon route;
- at least one wildcard/delight route;
- one flexible slot from the strongest available Atlas/candidate signal.

## Evaluator Responsibilities

The Mission Generation evaluator must check:

- valid JSON;
- schema conformance;
- no empty route;
- route item readiness;
- all four primary chip sets;
- MusicKit/search hints;
- no duplicate route items unless explicitly allowed;
- no duplicate route item IDs, candidate IDs, or display identities;
- expected archetype or portfolio slot coverage;
- candidate-constrained mode compliance when applicable;
- exact route-item candidate membership, not artist/title similarity fallback;
- no route item repeats from supplied batch memory;
- known dead-end warnings;
- false-nearby discipline;
- Waypoint vs Landmark distinction;
- completion/review semantics;
- conditional Atlas updates;
- trap positive chips use exception/reassess semantics;
- adaptive second-batch fields;
- `source_atlas_delta_refs`;
- signal/update refs;
- visible batch-one learning;
- hit/miss/no-signal semantics;
- resolution quality and closed-loop learning suitability.

## Latest Proof Snapshot

Latest live adaptive run:

```text
data/closed_loop_simulation/a3_first_batch_learning_v0_1_adaptive_contract_v0_1/
```

Result:

- profiles: `profile_01_A3`, `profile_05_A3`, `profile_06_A3`
- model: `gpt-5.4-mini`
- first batch: schema-valid for all profiles
- adaptive second batch: schema-valid and adaptive-evaluator-valid for all profiles
- visibly adaptive missions: `6/6` per profile
- total estimated cost: about `$0.76`
- total token usage: `358,311`
- hidden provenance leak check: no hidden simulator provenance in Atlas-facing feedback, update, delta, or digest artifacts

Interpretation:

`gpt-5.4-mini` is viable for trusted Alpha mission generation when bounded by digest context, candidate constraints, strict schema, exact ref copy tables, and evaluator gates.

## Current Alpha Recommendation

Use reviewed/concierge-backed generation for trusted Alpha.

Default model:

```text
gpt-5.4-mini
```

Fallback/adjudication:

```text
gpt-5.5
```

Do not generate missions inside the iOS app for Alpha. The app should receive reviewed/importable mission payloads after install or through a backend assignment/import path.

## Post-Brand Alpha 1 Update

Product decision date:

```text
2026-05-22
```

First mission generation now starts after required Survey completion. Mission Generation should consume Survey Evidence Export / MissionGenerationDigestView context, not bundled mission content.

Current handoff state:

- Survey-completion trigger contract is defined.
- Supabase/Core response and import target are defined.
- Infrastructure reports live Supabase generation smoke passed; Core still needs to invoke it with the real app session after Survey.
- Existing golden packet validates the import pipeline.
- A fully app-importable post-brand first-batch artifact now exists from `MissionGenerationDigestView + route-ready alpha_v0 candidate pool`.

Latest passing artifact:

```text
data/mission_generation/alpha_first_batch_route_ready_v0_1/public_profile_01_A3_Al1_S2/20260523T225550Z/
```

Result:

- model: `gpt-5.4-mini`
- product status: `app_import_candidate`
- rich mission schema valid: `true`
- automated score: `1.0`
- Core `mission.v0.2` validation: `passed`
- route items: concrete `track` candidates from `sample_compact_candidate_pool_alpha_v0.json`
- no manual app-import override applied

`MGN-I004` is closed by the route-ready candidate pool and live app-import candidate generation.

## Open Handoff Dependencies

1. Core/Infrastructure must finish app-session invocation of the live generation endpoint after Survey completion.
2. Survey should provide the fixed Alpha 1 `A4_Al2_S4` Survey Evidence Export so this path can be rerun against the final intake shape.
3. Atlas must keep promotion/demotion manual or review-gated for Alpha.

Until these resolve, Mission Generation can provide app-import candidate artifacts and evaluator reports, but the app-session live assignment path remains a Core/Infrastructure dependency.
