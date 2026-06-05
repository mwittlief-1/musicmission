# Mission Opportunity Selection Contracts v0.1

Status: PM accepted implementation-readiness slice plus offline synthetic selector prototype. Phase 1C adds target-sensitive generation and scoring over visible synthetic/profile fixtures only.

This package defines the schema layer for selecting ranked mission opportunities. It does not implement runtime selection, connect to live listener evidence, generate production missions, mutate canonical graph truth, or reuse Mission Construction Contract v0.2 as the selector schema.

## Contracts

- `schemas/mission_type_registry_v0_1.schema.json`
- `schemas/evidence_rollup_v0_1.schema.json`
- `schemas/mission_opportunity_blob_v0_1.schema.json`
- `schemas/selector_output_v0_1.schema.json`
- `schemas/hidden_oracle_evaluation_design_v0_1.schema.json`
- `schemas/hidden_oracle_rank_usefulness_analysis_v0_1.schema.json`

## TypeScript Types

- `types/mission_type_registry_v0_1.ts`
- `types/evidence_rollup_v0_1.ts`
- `types/mission_opportunity_blob_v0_1.ts`
- `types/selector_output_v0_1.ts`
- `types/hidden_oracle_evaluation_design_v0_1.ts`
- `types/hidden_oracle_rank_usefulness_analysis_v0_1.ts`
- `types/index.ts`

## Fixtures

Positive fixtures live in `fixtures/`.

Negative fixtures live in `fixtures/negative/` and are expected to fail validation or domain gates.

Prototype scenario fixtures:

- `fixtures/synthetic_selector_scenarios_v0_1.json`
- `fixtures/prototype_selector_output_synthetic_v0_1.json`
- `fixtures/prototype_selector_output_early_stop_synthetic_v0_1.json`
- `fixtures/profile_simulation/visible_profile_selector_inputs_v0_1.json`
- `fixtures/profile_simulation/hidden_profile_oracles_v0_1.json`
- `fixtures/profile_simulation/hidden_oracle_evaluation_design_v0_1.json`
- `fixtures/profile_simulation/hidden_oracle_rank_usefulness_analysis_v0_1.json`
- `fixtures/profile_simulation/public_profile_*_selector_output_v0_1.json`

Phase 1E expanded-scale evaluation outputs:

- `evaluations/phase1e_expanded_visible_evidence_scale/expanded_visible_profile_inputs_v0_1.json`
- `evaluations/phase1e_expanded_visible_evidence_scale/selector_outputs_by_profile_scale/`
- `evaluations/phase1e_expanded_visible_evidence_scale/hidden_oracle_rank_usefulness_by_profile_scale_v0_1.json`
- `evaluations/phase1e_expanded_visible_evidence_scale/expanded_visible_evidence_scale_summary_v0_1.json`
- `evaluations/phase1e_expanded_visible_evidence_scale/expanded_visible_evidence_scale_summary_v0_1.md`

Phase 1F offline song-pack smell-test outputs:

- `evaluations/phase1f_song_pack_smell_test/song_pack_simulation_results_v0_1.json`
- `evaluations/phase1f_song_pack_smell_test/song_pack_simulation_schema_v0_1.schema.json`
- `evaluations/phase1f_song_pack_smell_test/song_pack_simulation_summary_v0_1.md`
- `evaluations/phase1f_song_pack_smell_test/song_pack_simulation_guardrail_report_v0_1.md`
- `evaluations/phase1f_song_pack_smell_test/per_profile_pack_cards/`

Phase 1G mission-type construction-policy and LLM review outputs:

- `evaluations/phase1g_construction_policy_llm_review/phase1g_song_pack_results_v0_1.json`
- `evaluations/phase1g_construction_policy_llm_review/phase1g_song_pack_schema_v0_1.schema.json`
- `evaluations/phase1g_construction_policy_llm_review/phase1g_song_pack_summary_v0_1.md`
- `evaluations/phase1g_construction_policy_llm_review/phase1g_guardrail_report_v0_1.md`
- `evaluations/phase1g_construction_policy_llm_review/llm_sanity_review_packet_v0_1.md`
- `evaluations/phase1g_construction_policy_llm_review/llm_sanity_review_packet_v0_1.json`
- `evaluations/phase1g_construction_policy_llm_review/per_profile_pack_cards/`

## Offline Prototype

The prototype selector is `scripts/prototype_mission_opportunity_selector_v0_1.py`.

Coverage run:

```sh
.venv/bin/python scripts/prototype_mission_opportunity_selector_v0_1.py \
  --profile coverage \
  --output data/product_contracts/mission_opportunity_selection_v0_1/fixtures/prototype_selector_output_synthetic_v0_1.json
```

Early-stop run:

```sh
.venv/bin/python scripts/prototype_mission_opportunity_selector_v0_1.py \
  --profile early_stop \
  --output data/product_contracts/mission_opportunity_selection_v0_1/fixtures/prototype_selector_output_early_stop_synthetic_v0_1.json
```

The prototype reads only the mission type registry fixture and synthetic scenario rollup fixture. Profile runs read selector-visible fixture rollups only. It does not read app storage, canonical graph source-of-truth files, Apple Music, catalog APIs, runtime listener evidence, hidden oracle data, or production mission content.

Profile-oracle phase 1 fixture build:

```sh
.venv/bin/python scripts/build_mission_opportunity_profile_simulation_v0_1.py
```

This converts selected public fake-profile survey evidence exports into selector-visible fixtures and writes simulator-private hidden oracle data into a separate file. Selector outputs reference only `visible_profile_selector_inputs_v0_1.json`; the hidden oracle fixture is reserved for later post-selection evaluation and is marked `selector_may_read: false`.

Hidden-oracle evaluation design build:

```sh
.venv/bin/python scripts/build_hidden_oracle_evaluation_design_v0_1.py
```

This reads already-emitted profile selector outputs plus the hidden oracle fixture and writes an evaluator-only design fixture. It does not feed hidden oracle data back into selector input, construct mission contents, select candidate songs, connect runtime evidence, or generate production missions. The design fixture evaluates selected opportunity references only, with metrics for opportunity relevance, hidden-hit proxy, diagnostic value, boundary discovery, false-nearby detection, context detection, overfit prevention, survey decay, and expected learning usefulness.

Hidden-oracle rank-usefulness harness:

```sh
.venv/bin/python scripts/evaluate_hidden_oracle_rank_usefulness_v0_1.py
```

This reads the accepted post-selection evaluation design fixture and emits rank-vs-usefulness analysis over the top opportunity window. It reports top-1 usefulness, oracle-best rank, rank regret, Spearman rank alignment, NDCG, mission-type usefulness summaries, and profile-level tuning notes. It remains opportunity-ref only and still does not construct missions, select songs, or expose hidden oracle data to the selector.

Phase 1E expanded visible evidence scale simulation:

```sh
.venv/bin/python scripts/run_phase1e_expanded_visible_evidence_scale_v0_1.py
```

This builds deterministic selector-visible evidence sets for public profiles 01, 05, and 06 at 72, 150, 200, and 300 atoms across `profile_weighted_balanced`, `edge_heavy`, and `song_heavy` modes. The fixture builder may sample held-out corpus reactions into visible synthetic evidence, but selector runs read only the expanded visible fixture. Hidden oracle usefulness metrics are computed only after selector outputs exist and are not written back into selector input.

Phase 1F offline top-window song-pack smell test:

```sh
.venv/bin/python scripts/simulate_top_window_song_packs_v0_1.py
```

This reads Phase 1E selector outputs, constructs six-song offline review packs from the selector top window, then joins hidden-oracle reactions only after pack construction. The constructor uses a reaction-stripped song pool containing song IDs, titles, artist names, visible evidence tokens, and selector opportunity refs only. The output remains a synthetic smell-test artifact: it is not production mission content, does not emit final mission copy, does not update listener state, and does not write oracle results back into selector input.

Phase 1G mission-type construction-policy hardening plus LLM review packet:

```sh
.venv/bin/python scripts/simulate_phase1g_construction_policy_llm_review_v0_1.py
```

This tests Alpha v0.2-style six-song packs for `archetype_depth_test`, `artist_depth_test`, `album_container_test`, `boundary_test`, `bridge_test`, and `context_dependence_test` at the 200-atom evidence scale. Six songs are recorded as an Alpha test size only; future product stress testing should cover 8-12 song packs. Each mission type owns a native construction policy, and the harness compares it against experience-balanced and diagnostic-biased policies. High-risk negative probes are not globally required. The LLM packet is review-only and contains no production mission copy.

## Prototype Scoring Formula

The Phase 1C prototype treats mission type value as a prior and lets target-specific fit/readiness/learning dominate ordering among floor-passing opportunities:

```text
mission_type_value =
  mission_type.score_floor * 0.46 * mission_type_value_input

mission_fit_score =
  0.34 * target_fit_input

readiness_score =
  0.20 * readiness_input

learning_value_score =
  0.30 * learning_value_input

risk_penalty =
  0.10 * risk_input

repetition_penalty =
  0.04 * repetition_input

complexity_penalty =
  0.04 * complexity_input

raw_score =
  mission_type_value
+ mission_fit_score
+ readiness_score
+ learning_value_score
- risk_penalty
- repetition_penalty
- complexity_penalty

final_opportunity_score =
  min(max(raw_score, 0), mission_type.score_ceiling)
```

The mission type registry still supplies approved floors, ceilings, bands, caps, and scoring metadata. The executable Phase 1C formula intentionally reduces direct value-band dominance so a lower-ceiling opportunity with excellent visible target fit can beat a higher-ceiling opportunity with weak target fit.

The candidate is emitted only when `floor_passed = true` and `final_opportunity_score >= mission_type.score_floor`. Candidate generation is conditional on visible target rollups, and non-generation reasons are recorded in selector audit output.

`score_components.raw_score` records the pre-ceiling weighted value. The selector output schema directly references `mission_opportunity_blob_v0_1.schema.json` for `ranked_opportunities`; the paired validator also keeps explicit domain gates for opportunity-only output, duplicate-control audit fields, profile differentiation checks, and hidden-oracle separation.

## Target Identity Integrity

Generated opportunities derive `target_object_ref`, `target_object_ids`, `required_graph_object_refs`, graph context target refs, floor rollup refs, and source signal target refs from the same target-level rollup. Candidate variants may suffix IDs such as `_candidate_02`, but validators strip those suffixes and require provenance back to the same base rollup target. Pair opportunities must preserve both pair endpoints from the pair rollup.

## Hidden Oracle Evaluation Boundary

Hidden oracle data is never selector input. The selector reads only `visible_profile_selector_inputs_v0_1.json` and emitted selector outputs remain opportunity-only. The hidden-oracle evaluation design is a post-selection review artifact for future simulation: it can compare selected opportunity refs against simulator-private taste truth after selection, but candidate-song selection and mission construction remain out of scope.

## Validation

Use the repo virtualenv so `jsonschema` is available:

```sh
.venv/bin/python scripts/validate_mission_opportunity_selection_v0_1.py
.venv/bin/python data/product_contracts/mission_opportunity_selection_v0_1/tests/fixture_contract_tests_v0_1.py
```

## Locked Boundaries

- Survey `ok` is no signal and must not contribute preference or non-failure evidence.
- Mission/song-review `ok` is weak non-failure evidence, not positive preference.
- Output is ranked opportunity blobs only, not mission content.
- Runtime use, production mission generation, canonical graph mutation, and listener preference inference from affinity similarity remain blocked.
