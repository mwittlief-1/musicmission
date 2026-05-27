# Cartenza Atlas Ingestion + Digest Harness v0.1

This harness proves the Atlas schema can sit between:

```text
Survey onboarding -> Atlas seed state -> AtlasDigestView -> Mission Generation / Candidate Pool Builder
Mission Review -> Signals + PossibleAtlasUpdateCandidate -> Atlas state refinement
```

It uses synthetic fixtures first. The transform layer is intentionally deterministic so real Survey Simulation, iOS Survey, Mission Review, or Listen/Player exports can replace the fixtures later by matching input schema versions.

The directory and Python package names still use the former Waymark identifier for compatibility. See `../docs/brand_migration_cartenza.md` before renaming technical paths.

## Structure

```text
waymark-atlas-tests/
  fixtures/
    survey_outputs/
    mission_review_outputs/
    canonical_refs/
    expected_atlas_records/
  src/
  outputs/
  reports/
```

## Run

From the repo root:

```sh
.venv/bin/python waymark-atlas-tests/src/run_atlas_ingestion_tests.py
```

The runner:

- ingests all synthetic Survey fixtures;
- ingests all synthetic Mission Review fixtures;
- writes contract-valid Atlas records;
- validates records against `data/atlas_schema/atlas_schema_contract_v0_1.json`;
- runs product invariants;
- emits a contract `AtlasDigestView`;
- emits an expanded mission/candidate-builder digest;
- emits a compact `MissionGenerationDigestView` adapter that strips copyable Atlas update IDs;
- exports the expanded digest to `waymark-ai-tests/fixtures/atlas_digests/generated_atlas_digest_view_v0_1.json`;
- exports the compact mission digest to `waymark-ai-tests/fixtures/atlas_digests/mission_generation_digest_view_v0_1.json`;
- runs a dry-run mission harness smoke test using `mission_generation_digest_view_plus_features_plus_candidates`.

Use a Python environment with `jsonschema` installed for full Atlas Schema Contract validation. The repo `.venv` currently provides this. System Python can run the harness, but if `jsonschema` is unavailable the validator reports a fallback subset check rather than the full contract.

## Outputs

Each run writes a timestamped directory under `outputs/`:

- `generated_atlas_records.json`
- `survey_ingestion_records.json`
- `mission_review_ingestion_records.json`
- `atlas_digest_view.json`
- `atlas_digest_view_expanded.json`
- `mission_generation_digest_view.json`
- `validation_result.json`
- `mission_smoke_outputs/`

Reports are written to:

```text
reports/atlas_ingestion_report_<timestamp>.md
```

## Invariants

The validator checks:

- no canonical graph mutation;
- `AtlasNode` has no authoritative role;
- Survey does not auto-promote weak evidence;
- Mission Review does not auto-promote;
- role/update candidates are auditable to Signals;
- `signal_strength` remains separate from `interpretation_confidence`;
- candidate-pool behavior is present for future Candidate Pool Builder use;
- composition-placeholder support validates;
- vocabulary terms are not automatically canon;
- the digest emits mission-usable summaries.

## Mission Harness Integration

After a run, these generated context modes are available in `waymark-ai-tests`:

```text
mission_generation_digest_view_plus_features_plus_candidates
generated_atlas_digest_view_plus_features_plus_candidates
```

Use `mission_generation_digest_view_plus_features_plus_candidates` for live mission-generation tests. The older `generated_atlas_digest_view_plus_features_plus_candidates` mode intentionally exposes the expanded digest and is mainly for debugging.

Smoke test manually:

```sh
python3 waymark-ai-tests/src/run_mission_generation_tests.py \
  --request nirvana_to_current \
  --prompt-template mission_generator_candidate_constrained_v0_1 \
  --context-mode mission_generation_digest_view_plus_features_plus_candidates \
  --model gpt-5.4-mini \
  --dry-run
```

This smoke test does not call OpenAI. It only verifies that Mission Generation can receive the generated digest packet with landmarks, frontiers, dead ends, waypoints, taste features, vocabulary, anti-overfitting rules, and candidate-pool behavior cues.

## Not Included

This harness does not implement final promotion formulas, full Candidate Pool Builder, MusicKit resolution, backend persistence, account state, or Atlas graph visualization.
