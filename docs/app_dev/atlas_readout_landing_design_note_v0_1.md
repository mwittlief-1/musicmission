# Cartenza Atlas Readout Landing Design Note v0.1

Date: 2026-06-03

## Goal

Design the first post-survey Atlas Landing readout so Cartenza can tell an external Alpha user what it sees so far, why the first missions exist, and what is still uncertain.

The readout should feel specific and musically literate, but it must stay humble: early signal, not final taste truth.

## Current App Flow

The existing first-run flow already has a lightweight Survey readout. After the required Survey pages, `SurveyStore.advance()` reaches `.readout`, and `SurveyView` shows "What We Think So Far." Tapping "Build My Atlas" calls `RootView.completeSurvey()`, which marks Survey complete and immediately starts first mission generation.

There are two viable insertion paths:

- Lowest-risk Alpha slice: replace or expand the existing `SurveyView` readout. This preserves the current first-run state machine.
- Cleaner product slice: add a new `FirstRunStage.atlasReadout` between `.survey` and `.generation`. This decouples "Survey is complete" from "the user has seen the Atlas readout and asked Cartenza to build missions."

Recommendation for the external Alpha candidate: use the cleaner product slice if schedule allows. The readout is a real landing page and should own the transition from Survey evidence into mission tests.

## Data Model

Use two separate models:

- `AtlasReadoutEvidenceBrief`: structured evidence for generation or deterministic copy assembly.
- `AtlasReadoutDisplayModel`: UI-safe display copy only.

Do not render raw prompt-test output directly. Strip `internal_quality_notes` from the normal UI payload.

The app can build early evidence from existing Survey state:

- response counts from `SurveyStore.summary`;
- visible evidence and mission digest from Survey evidence export helpers;
- first mission batch summary from deterministic opportunity mission generation;
- affinity rollup from positive song responses joined to `canonical_song_affinity_tags_v0_1.json`.

The affinity join is the main missing runtime ingredient. Current Survey items do not expose affinity tags directly, so this needs a small service or builder rather than ad hoc string matching in the view.

## Prompt Test Contract

The offline v0.1 prompt test now lives under:

`data/product_contracts/atlas_readout_v0_1/`

It includes:

- shared evidence brief fixture;
- evidence and output schemas;
- prompt formats A-E;
- variant instructions 01-05;
- 25-run matrix;
- result wrapper schema for validation and scoring.

Generated runs should stay under an ignored `evaluations/prompt_test_v0_1/` workspace unless a maintainer promotes a summary. The app bundle should receive only a selected, reviewed display payload or deterministic local builder output.

## UI Shape

Recommended first-run readout screen:

- Title and subtitle.
- Opening read, 70-120 words.
- 3-5 signal cards ordered by evidence strength.
- Song-shape summary from affinity tags.
- 2-4 uncertainty cards.
- Mission bridge section with 3-6 mission teasers.
- Primary CTA: "Build first missions" or equivalent.

The screen should keep cards compact. Confidence labels should be plain text such as "High early signal" or "Medium early signal," not internal score badges.

## Guardrails

- Never say the user is a grunge fan or any fixed identity.
- Never say Cartenza knows the user's taste.
- Never call the Atlas final.
- Do not expose mission IDs, cluster IDs, raw tag strings, Apple payload internals, OpenAI, or graph mechanics.
- Unknown means opening, not rejection.
- Negative signal means caution, not permanent dead end.
- Emotional tags must stay cautious: "an early emotional pattern around..." rather than lyric or personality claims.

## Recommended Implementation Slices

1. Keep the prompt-test contract offline and add a validator/runner script.
2. Add `AtlasReadoutDisplayModel` and a static fixture-driven preview view for UI layout.
3. Add `FirstRunStage.atlasReadout` and move mission generation behind the readout CTA.
4. Add an evidence brief builder and affinity rollup tests.
5. Promote one reviewed readout candidate or deterministic readout builder for external Alpha.

## Test Plan

- JSON schema validation for prompt-test artifacts.
- Guardrail validator for raw IDs, forbidden claims, invented examples, and final-truth language.
- Unit tests for evidence brief counts, positive song-affinity rollup, uncertainty handling, and mission teaser sanitization.
- Existing mission-generation tests should continue to pass.
- Release build should confirm fixture controls remain hidden unless explicitly enabled.
