# Waymark Mission Generation API Test Harness v0.1

This harness evaluates whether a bounded OpenAI API context packet can generate Waymark missions from:

- a user prompt;
- a Matt Atlas digest;
- a Taste Feature Registry;
- an optional candidate music pool.

It is not the final backend, not a MusicKit resolver, and not an app import pipeline. Phase 1 is an experiment loop for mission quality.

## Structure

```text
waymark-ai-tests/
  fixtures/
    atlas_digests/
    feature_registry/
    mission_requests/
    candidate_pools/
    prompt_templates/
    schemas/
    pricing/
    expected/
  docs/
  outputs/
  reports/
  src/
```

Generated outputs are written to timestamped directories under `outputs/`. Summary reports are written under `reports/`.

## Setup

Use the repo virtualenv if desired, or run with system Python. The harness has no required package dependency. If `jsonschema` is installed, it uses full JSON Schema validation; otherwise it falls back to a built-in subset validator plus deterministic scoring checks.

```sh
cd waymark-ai-tests
cp .env.example .env
# edit .env and set OPENAI_API_KEY
```

## List Fixtures

From the repo root:

```sh
python3 waymark-ai-tests/src/run_mission_generation_tests.py --list requests
python3 waymark-ai-tests/src/run_mission_generation_tests.py --list suites
python3 waymark-ai-tests/src/run_mission_generation_tests.py --list prompts
python3 waymark-ai-tests/src/run_mission_generation_tests.py --list context_modes
python3 waymark-ai-tests/src/run_mission_generation_tests.py --list models
```

Generated Atlas ingestion context modes:

- `mission_generation_digest_view_plus_features_plus_candidates`: compact mission-facing adapter. Use this for live generated-Atlas mission tests.
- `generated_atlas_digest_view_plus_features_plus_candidates`: expanded digest/debug surface. It intentionally exposes more Atlas state and should not be the default mission-generation packet.

## Offline Smoke Test

Use `--mock` to verify fixture loading, payload writing, schema validation, scoring, and report generation without calling OpenAI:

```sh
python3 waymark-ai-tests/src/run_mission_generation_tests.py \
  --request nirvana_to_current \
  --prompt-template mission_generator_candidate_constrained_v0_1 \
  --context-mode atlas_plus_features_plus_candidates \
  --mock
```

Mock runs are schema/harness validation only. Do not use them as model-quality or product-quality evidence.

Use `--dry-run` to write API payloads only:

```sh
python3 waymark-ai-tests/src/run_mission_generation_tests.py \
  --request muse_boundary_check \
  --prompt-template mission_generator_rich_v0_1 \
  --context-mode atlas_plus_features \
  --dry-run
```

## Run One Live Test

```sh
python3 waymark-ai-tests/src/run_mission_generation_tests.py \
  --request nirvana_to_current \
  --prompt-template mission_generator_rich_v0_1 \
  --context-mode atlas_plus_features_plus_candidates \
  --model "$WAYMARK_OPENAI_MODEL"
```

The runner saves:

- `metadata.json`;
- `context_packet.json`;
- `request_payload.json`;
- `raw_model_output.json`;
- `parsed_output.json`;
- `validation_result.json`;
- `metrics.json`;
- `score_report.json`;
- `report.md`.

Run metadata includes `run_type`, schema validity, app-import readiness, product status, token usage when returned by the API, latency, and cost estimates.

## Model Matrix v0.3

Run the first-pass live model matrix:

```sh
python3 waymark-ai-tests/src/run_mission_generation_tests.py \
  --suite model_matrix_v0_3_core \
  --models gpt-5.4-nano,gpt-5.4-mini,gpt-5.4,gpt-5.5 \
  --prompt-template mission_generator_candidate_constrained_v0_1 \
  --context-mode atlas_plus_features_plus_candidates \
  --runs 1 \
  --timeout-seconds 300 \
  --model-matrix-report
```

Add `gpt-4.1` only when you need the legacy comparison baseline.

Then run a consistency pass after choosing the best default model, cheapest plausible model, and quality-ceiling model:

```sh
python3 waymark-ai-tests/src/run_mission_generation_tests.py \
  --suite model_matrix_v0_3_consistency \
  --models gpt-5.4-nano,gpt-5.4-mini,gpt-5.5 \
  --prompt-template mission_generator_candidate_constrained_v0_1 \
  --context-mode atlas_plus_features_plus_candidates \
  --runs 3 \
  --timeout-seconds 300 \
  --model-matrix-report
```

The suite-level model report is written to `reports/model_matrix_<timestamp>.md`.

## Context Matrix v0.4

Run the live context matrix for the current default model candidate:

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

The context matrix report is written to `reports/context_matrix_<timestamp>.md` and compares schema validity, product status, app-import readiness, automated score, human-review need, overgeneralization failures, candidate-choice failures, chip usefulness, Atlas-update caution, token usage, estimated cost, and latency.

If all live calls fail before model output is produced, the report marks the matrix as `none_api_failure`. Treat that as an API/billing/quota result only, not as evidence about context quality.

## Cost Estimates

The default pricing table lives at `fixtures/pricing/openai_pricing_v0_3.json`. It is manually maintained and can be overridden with:

```sh
WAYMARK_MODEL_PRICING_FILE=path/to/openai_pricing.json
```

or:

```sh
WAYMARK_MODEL_PRICING_JSON='{"models":{"example-model":{"input_per_1m":1,"cached_input_per_1m":0.1,"output_per_1m":5}}}'
```

Each live run records input tokens, cached input tokens if the API returns them, output tokens, total tokens, input/cached/output/total cost estimates, cost status, pricing table version/date, and latency. Cost estimates are for model-comparison and planning. Dashboard reconciliation may differ due to cached tokens, service tier, retries, failed calls, or account-level aggregation.

## Model Routing Hypothesis

- Default full mission generation: `gpt-5.4-mini`
- Cheap/simple substeps to test: `gpt-5.4-nano`
- Hard mission fallback: `gpt-5.4`
- Quality ceiling / ambiguous high-value missions: `gpt-5.5`
- Legacy baseline: `gpt-4.1`

Fine-tuning remains deferred; see `docs/fine_tuning_strategy_v0_1.md`.

## Suggested First Matrix

This is the initial low-cost matrix from the dispatch:

```sh
python3 waymark-ai-tests/src/run_mission_generation_tests.py \
  --suite suggested_first_five \
  --prompt-template mission_generator_compact_v0_1,mission_generator_rich_v0_1 \
  --context-mode thin,atlas_digest,atlas_plus_features_plus_candidates \
  --runs 1
```

Then run consistency checks on the hardest cases:

```sh
python3 waymark-ai-tests/src/run_mission_generation_tests.py \
  --suite consistency_hard_cases \
  --prompt-template mission_generator_candidate_constrained_v0_1 \
  --context-mode atlas_plus_features_plus_candidates \
  --runs 3
```

## Context Modes

- `thin`: request fixture plus thin Atlas digest.
- `atlas_digest`: request fixture plus full Atlas digest.
- `atlas_plus_features`: full Atlas digest plus Taste Feature Registry.
- `atlas_plus_features_plus_candidates`: full Atlas digest plus registry plus candidate pool.
- `generated_atlas_digest_view`: generated AtlasDigestView fixture from `waymark-atlas-tests`.
- `generated_atlas_digest_view_plus_features`: generated AtlasDigestView fixture plus Taste Feature Registry.
- `generated_atlas_digest_view_plus_features_plus_candidates`: generated AtlasDigestView fixture plus registry plus candidate pool.

Aliases are supported for context matrix readability: `thin_context` maps to `thin`, and `atlas_digest_only` maps to `atlas_digest`.

## Prompt Templates

- `mission_generator_compact_v0_1`: short generation instructions.
- `mission_generator_rich_v0_1`: more explicit mission-design process and guardrails.
- `mission_generator_candidate_constrained_v0_1`: hard-constrains route items to candidate pools when present.

## Automated Checks

The scoring report currently checks:

- valid JSON;
- schema conformance;
- non-empty route;
- route item count in expected range;
- all four chip sets on every item;
- at least two chips per reaction operation;
- MusicKit search hints;
- duplicate songs;
- expected archetype;
- candidate-constrained pool compliance;
- 70/30 risk mix where requested;
- fixed-year constraints where requested;
- required Dead End warning terms;
- false-nearby trap promotion;
- structurally useless chip labels;
- Waypoint versus Landmark distinction.
- completion semantics that count primary reactions separately from chip selections;
- conditional `possible_atlas_update_candidates` with future-reaction trigger conditions;
- review-needed defaults for risky, trap, Dead End, and frontier-unknown items;
- trap love/like chips that use unexpected-exception, cultural-furniture, or reassess-dead-end semantics.
- hypothesis text that treats generated premise as evidence;
- Atlas escalation guardrails for non-Signal updates;
- candidate-role discipline;
- archetype-specific route shape.

The report also includes a manual 0-3 rubric for mission quality, route logic, Atlas use, uncertainty, chip quality, evidence usefulness, and MusicKit plausibility.

## Phase 2 Hooks

The fixture shape leaves room for:

- live MusicKit resolution checks;
- candidate pool generation from library/catalog data;
- LLM-as-judge scoring;
- side-by-side diff UI;
- token/cost reporting;
- golden-output regression tests;
- Atlas update simulation after synthetic reactions.
