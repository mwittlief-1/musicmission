# Waymark Mission Generation Harness - Model Matrix v0.2 Review Notes

Generated: 2026-05-19

## What Changed

- Added multi-model runner support with `--models`.
- Added per-run `run_type`, product-readiness status, token usage, latency, and optional cost-estimate hook.
- Added suite-level `reports/model_matrix_<timestamp>.md`.
- Added `model_matrix_first_pass` and `model_matrix_consistency_candidates` suites.
- Added stricter checks for hypothesis-as-evidence, Atlas escalation, candidate-role discipline, route shape, trap semantics, and structurally useless chips.
- Refined false-nearby scoring so cautionary mentions like "not Tool" are not treated as promoted recommendations.
- Added `--timeout-seconds`; strict-schema live calls often exceed 120 seconds.

## Live Runs Included

- First-pass model matrix: `20260519T152703Z`
  - 5 requests x 3 models x 1 run.
  - Rescored report: `reports/model_matrix_20260519T152703Z_rescored.md`
- Consistency pass: `20260519T161221Z`
  - 2 requests x 2 models x 3 runs.
  - Rescored report: `reports/model_matrix_20260519T161221Z_rescored.md`

## Current Read

- `gpt-5.4-mini` is the best commercial default candidate so far: much lower latency and strong enough structured output under candidate-constrained context.
- `gpt-5.5` remains the quality-ceiling candidate, but it was slower and had one intermittent frontier warning miss plus one first-pass transport failure.
- `gpt-4.1` is no longer the best baseline under the tightened evaluator; it repeatedly failed conditional Atlas-update checks.

## Review Focus

- Manually review Muse boundary runs for whether trap items are used as boundary checks rather than recommendations.
- Manually review Lithuanian frontier runs for uncertainty preservation and catalog-resolution caution.
- Decide whether the strict route-shape check should allow more than two trap items when the route is explicitly a boundary map.
- Decide whether `gpt-5.4-mini` route-count failures should be handled by prompt tightening or a stronger route-planning step.
