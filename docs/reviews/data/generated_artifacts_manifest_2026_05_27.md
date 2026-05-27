# Generated Data Artifact Manifest - 2026-05-27

Scope: local generated/archive surfaces under `data/` that are intentionally ignored after repo cleanup classification.

This manifest records what was observed without promoting the artifacts into source-of-truth. No data files were moved or deleted as part of this manifest.

## Atlas Schema Ingestion Proof

Ignored by `.gitignore`: `data/atlas_schema/ingestion_proof/`

Observed size: about 31M across 133 files.

Observed top-level contents:

| Path | Size | Classification |
| --- | ---: | --- |
| `data/atlas_schema/ingestion_proof/a3_gpt_5_5_3x3/` | 7.1M | Generated ingestion proof evidence. |
| `data/atlas_schema/ingestion_proof/survey_to_atlas_digest_v0_1/` | 2.8M | Generated survey-to-Atlas digest proof evidence. |
| `data/atlas_schema/ingestion_proof/survey_evidence_export_v0_1/` | 17M | Generated proof evidence from Survey Evidence Export inputs. |
| `data/atlas_schema/ingestion_proof/alpha1_required_intake_survey_evidence_export_v0_1/` | 3.6M | Generated proof evidence for the alpha1 required intake path. |
| `data/atlas_schema/ingestion_proof/atlas_pm_contract_review_a3_ingestion_proof_2026-05-21.zip` | 284K | Generated review packet archive. |

Promotion rule: copy or move only specific accepted proof fixtures into `data/atlas_schema/examples/`, `data/atlas_schema/alpha_hardening/`, `data/product_contracts/`, or `docs/`, with a note explaining why the artifact became durable source.

## Survey Simulation Generated Outputs

Ignored by `.gitignore`: generated survey runs, reports, page-count backtests, selected LLM profile review API outputs, evidence bundles, private simulator material, and Finder duplicate files.

Observed generated/local surfaces:

| Path | Size | Files | Classification |
| --- | ---: | ---: | --- |
| `data/survey_simulation/runs/` | 6.0M | 341 | Generated simulator runs. |
| `data/survey_simulation/reports/` | 52K | 6 | Generated simulator reports. |
| `data/survey_simulation/page_count_backtest/` | 4.8M | 15 | Generated backtest output. |
| `data/survey_simulation/llm_profile_review/api_pilot/` | 1.1M | 10 | Generated LLM API pilot output. |
| `data/survey_simulation/llm_profile_review/api_pilot_3x3/` | 16M | 100 | Generated LLM API pilot output. |
| `data/survey_simulation/llm_profile_review/api_pilot_3x3_gpt_5_4_mini/` | 3.0M | 20 | Generated LLM API pilot output. |
| `data/survey_simulation/llm_profile_review/content_review/` | 116K | 4 | Generated content review output. |
| `data/survey_simulation/llm_profile_review/evidence_bundles/` | 17M | 106 | Generated review evidence bundles. |
| `data/survey_simulation/llm_profile_review/reports/` | 28K | 6 | Generated LLM review reports. |
| `data/survey_simulation/llm_profile_review/simulator_private/` | 288K | 2 | Private simulator/evaluator material. |

Tracked first-class survey simulation surfaces remain:

- `data/survey_simulation/schemas/`
- `data/survey_simulation/fake_profiles/`
- `data/survey_simulation/apple_payloads/`
- `data/survey_simulation/hidden_reaction_corpora/`
- `data/survey_simulation/survey_evidence_export/`
- `data/survey_simulation/llm_profile_review/api_requests/`
- `data/survey_simulation/llm_profile_review/prompts/`
- `data/survey_simulation/llm_profile_review/public_packets/`
- `data/survey_simulation/llm_profile_review/schemas/`

Observed ignored local duplicate files:

- `data/survey_simulation/hidden_reaction_corpora/hidden_corpus_04 2.json`
- `data/survey_simulation/reports/page_n_intelligence_dispatch_context 2.md`
- `data/survey_simulation/schemas/apple_payload.schema 2.json`
- `data/survey_simulation/schemas/fake_profile.schema 2.json`
- `data/survey_simulation/schemas/hidden_lookup_coverage.schema 2.json`
- `data/survey_simulation/schemas/hidden_reaction_corpus.schema 2.json`
- `data/survey_simulation/schemas/page_generation_log.schema 2.json`
- `data/survey_simulation/schemas/recorded_responses.schema 2.json`
- `data/survey_simulation/schemas/survey_page.schema 2.json`
- `data/survey_simulation/schemas/survey_run.schema 2.json`

Promotion rule: promote selected reports or generated examples into `docs/` or a fixture directory only after owner review. Raw API responses, private evaluator material, zipped packets, and timestamped simulator runs should stay external or ignored.
