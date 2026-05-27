# Waymark Mission Generation Harness - Context Matrix v0.4 Review Notes

Generated: 2026-05-19

## What Changed

- Added `context_matrix_v0_4_core` suite covering:
  - `nirvana_to_current`
  - `muse_boundary_check`
  - `taylor_persona_pop`
  - `modern_safe_risky`
  - `lithuanian_artists_frontier`
- Added context-mode aliases for matrix readability:
  - `thin_context` -> `thin`
  - `atlas_digest_only` -> `atlas_digest`
- Added a dedicated context matrix report writer.
- Added `--context-matrix-report` CLI support.
- Added automatic context-matrix reporting when one model is run across multiple context modes.
- Updated the README with the exact v0.4 live matrix command.

## Intended Live Matrix

```text
5 core requests
x 4 context modes
x gpt-5.4-mini
= 20 live runs
```

Prompt template:

```text
mission_generator_candidate_constrained_v0_1
```

Context modes:

```text
thin_context
atlas_digest_only
atlas_plus_features
atlas_plus_features_plus_candidates
```

## Live Run Result

The quota-failed v0.4 attempt from `20260519T195456Z` is obsolete as a quality read.

The successful v0.4 live matrix ran at `20260520T093346Z`.

Use this report:

```text
reports/context_matrix_20260520T093346Z.md
```

Headline result:

```text
Current minimum viable default context: atlas_plus_features_plus_candidates
Candidate-pool read: candidate-pool necessity is inconclusive from this run.
```

All 20 calls returned schema-valid JSON.

Full candidate-constrained context produced the only `product_pass_candidate` runs:

- `nirvana_to_current`
- `taylor_persona_pop`
- `lithuanian_artists_frontier`

Full context still produced review/fail results for:

- `muse_boundary_check`: review-needed because route shape used too many trap items.
- `modern_safe_risky`: product-fail because route item count was low and the safe/risky ratio skewed too risky.

Product read:

- Full context is the current safest default.
- Candidate pools look materially helpful, especially for frontier and bridge routes.
- Candidate pools are not sufficient by themselves for ratio/count-sensitive prompts.
- Thin context should not be used for serious mission generation.
- `atlas_digest` and `atlas_plus_features` can produce plausible review-needed missions, but unconstrained candidate choice remains a product risk.

## Review Focus

Reviewers should inspect:

- whether the context matrix report structure answers the v0.4 product questions;
- whether API/schema failures are clearly separated from product-quality failures;
- whether the requested fields are present in the report;
- whether the minimum-viable-context logic is conservative enough;
- whether the full-context failures should be fixed by prompt/schema changes or evaluator tolerance.

Do not use the older quota-failed report as model-quality or context-quality evidence.

## Rerun Command

```sh
python3 waymark-ai-tests/src/run_mission_generation_tests.py \
  --suite context_matrix_v0_4_core \
  --model gpt-5.4-mini \
  --prompt-template mission_generator_candidate_constrained_v0_1 \
  --context-mode thin_context,atlas_digest_only,atlas_plus_features,atlas_plus_features_plus_candidates \
  --runs 1 \
  --timeout-seconds 300 \
  --context-matrix-report
```

## Expected Next Product Read

The next product read should test:

- `listen_to_in_utero` as a simple album-route context check;
- three-run consistency on `modern_safe_risky` full context;
- three-run consistency on `muse_boundary_check` full context;
- a smaller candidate-pool compression test for `nirvana_to_current`, `taylor_persona_pop`, and `lithuanian_artists_frontier`.
