# Atlas Readout Landing Contract v0.1

## Purpose

The Atlas Readout is the first post-survey "what we think so far" surface. It should help the user understand Cartenza's early signal without turning Survey responses into fixed identity claims.

This contract covers the offline prompt-test shape only. Runtime app rendering should consume a promoted display payload after validation and review.

## Input

The input is an `AtlasReadoutEvidenceBrief_v0_1` object with:

- Survey response counts and positive song counts.
- Strong signal clusters with plain labels, confidence, supporting examples, and scope notes.
- Positive song-affinity rollup with safe interpretations.
- Tensions and questions that should remain open.
- First mission batch summaries framed as tests.
- Copy guardrails and forbidden claims.

The model-facing payload may include raw IDs for traceability, but user-facing output must not expose them.

## Output

The output is an `AtlasReadoutOutput v0.1` object with:

- `readout_title`
- `readout_subtitle`
- `opening_read`
- `signal_cards`
- `song_shape_summary`
- `uncertainty_cards`
- `mission_bridge`
- `internal_quality_notes`

`internal_quality_notes` exists for validation review. It should be stripped from normal app UI.

## Required Guardrails

- Use early-signal language.
- Keep 90s alternative / grunge as a strong region, not a user identity.
- Keep classic album-rock and hooky alternative pop as supporting regions unless evidence changes.
- Use affinity tags as song-shape evidence, not personality diagnosis.
- Mention missions as tests that confirm, refine, probe, clarify, or reject early hypotheses.
- Treat Wipers unknown as an opening, not rejection.
- Treat The Decemberists negative as caution, not permanent exclusion.
- Do not expose mission IDs, cluster IDs, raw affinity tags, graph internals, Apple payload internals, OpenAI, or model behavior.

## Automatic Fail Conditions

An output fails before human review if it:

- returns invalid JSON;
- violates the output schema;
- says or implies "you are a grunge fan";
- claims Cartenza knows the user's taste;
- treats the readout as final;
- invents unsupported artists, songs, tags, missions, or conclusions;
- exposes raw IDs or internal mechanics;
- treats unknowns as rejection;
- makes unsupported lyric claims.

## Promotion Rule

No generated readout becomes app-facing until it has:

1. Valid JSON and schema compliance.
2. Zero automatic-fail conditions.
3. Rubric review scores captured in the result wrapper.
4. Product review selecting a specific candidate or edited derivative.
5. A separate app-handoff artifact that contains display copy only.
