# Waymark Mission Generation Harness - Model + Cost + Fine-Tune v0.3 Review Notes

Generated: 2026-05-19

## What Changed

- Added `gpt-5.4-nano` and `gpt-5.4` to the configurable model list.
- Added `fixtures/pricing/openai_pricing_v0_3.json` and per-run cost estimates.
- Added cached-input token capture when returned by the API.
- Added input/cached/output/total cost fields, cost status, calculation version, pricing table version/date, and pricing source.
- Added clearer report separation for schema validity, product status, and app-import readiness.
- Added `docs/fine_tuning_strategy_v0_1.md`.

## Live Runs Included

- v0.3 first pass: `20260519T170427Z`
  - 5 requests x 4 models x 1 run.
  - Report: `reports/model_matrix_20260519T170427Z.md`
- v0.3 consistency pass: `20260519T175330Z`
  - 2 requests x 3 models x 3 runs.
  - Report: `reports/model_matrix_20260519T175330Z.md`

## Current Routing Read

- Default full mission generation: `gpt-5.4-mini`
- Cheap/simple substeps to test: `gpt-5.4-nano`
- Hard mission fallback: `gpt-5.4`
- Quality ceiling / ambiguous high-value missions: `gpt-5.5`
- Legacy baseline: `gpt-4.1`

## Product Takeaways

- `gpt-5.4-mini` is the current best default: low cost, low latency, and stable on the consistency pass.
- `gpt-5.4-nano` is not reliable for full mission generation. It repeatedly produced invalid JSON or product failures, but remains worth testing for narrow substeps.
- `gpt-5.4` produced strong best-case missions but was less stable in the consistency pass.
- `gpt-5.5` remains useful as a quality ceiling reference, but its cost/latency and intermittent transport failure do not justify default routing.
- Fine-tuning remains deferred. The near-term priority is structured context, candidate constraints, evaluator repair, and model routing.

## Next Test

Run a context-mode matrix using `gpt-5.4-mini`:

1. thin context;
2. Atlas digest only;
3. Atlas digest + Feature Registry;
4. Atlas digest + Feature Registry + Candidate Pool.

Use the same five core requests to determine how much context the mini model actually needs and where overgeneralization returns.
