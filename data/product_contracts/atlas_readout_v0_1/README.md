# Cartenza Atlas Readout v0.1

Status: prompt-test and app-handoff contract design. Offline only.

This package defines the first post-survey Atlas Landing readout prompt test. It is not runtime generation wiring, and raw model completions from the 25-run experiment should not be bundled into the app.

## Included

- Shared evidence brief fixture: [fixtures/atlas_readout_evidence_brief_sample_v0_1.json](fixtures/atlas_readout_evidence_brief_sample_v0_1.json)
- Landing contract: [atlas_readout_landing_contract_v0_1.md](atlas_readout_landing_contract_v0_1.md)
- Evidence brief schema: [schemas/atlas_readout_evidence_brief_v0_1.schema.json](schemas/atlas_readout_evidence_brief_v0_1.schema.json)
- Output schema: [schemas/atlas_readout_output_v0_1.schema.json](schemas/atlas_readout_output_v0_1.schema.json)
- Prompt-test result wrapper schema: [schemas/atlas_readout_prompt_test_result_v0_1.schema.json](schemas/atlas_readout_prompt_test_result_v0_1.schema.json)
- Shared system prompt: [prompts/system_prompt_v0_1.md](prompts/system_prompt_v0_1.md)
- Prompt formats: [prompts/formats_v0_1.json](prompts/formats_v0_1.json)
- Variant instructions: [prompts/variant_instructions_v0_1.json](prompts/variant_instructions_v0_1.json)
- Run matrix: [prompts/run_matrix_v0_1.json](prompts/run_matrix_v0_1.json)

## Boundary

Allowed:

- Offline prompt testing against the shared evidence brief.
- Deterministic validation of JSON shape, length limits, guardrails, and automatic-fail conditions.
- Human or evaluator scoring against the rubric.
- Promotion of one reviewed display payload into a separate app-facing artifact after product acceptance.

Not allowed:

- Shipping raw prompt formats, raw completions, model metadata, evaluator notes, or the full 25-run experiment in the app bundle.
- Calling OpenAI from the iOS runtime for this Alpha readout.
- Exposing internal quality notes, raw graph IDs, mission IDs, Apple payload internals, or model behavior to users.
- Treating this first readout as final taste truth.

## Run Shape

The v0.1 test targets 25 completions:

- 5 prompt formats.
- 5 variant instructions per format.
- 1 shared input payload.
- 1 shared output schema.

Each result should be wrapped with hashes, validation status, rubric scores, and a gate decision before review.

Recommended generated-output root:

```sh
data/product_contracts/atlas_readout_v0_1/evaluations/prompt_test_v0_1/
```

Generated outputs should stay untracked unless a maintainer explicitly promotes a summary or selected display payload.

## App Handoff

The app should consume a promoted `AtlasReadoutDisplayModel`, not this prompt-test package. The display model should include only:

- title, subtitle, and opening read;
- signal cards;
- song-shape summary;
- uncertainty cards;
- mission bridge teasers.

`internal_quality_notes` belongs in validation artifacts or support diagnostics only, not normal UI.
