# Data Directory Policy

Date: 2026-05-26

This directory is not a single bucket. It contains source-of-truth contracts, canonical graph material, deterministic fixtures, generated evidence, and local exports. Treat each subtree by the policy below.

Naming note: Cartenza is the current product name. Existing `waymark.*` schema IDs, historical archive filenames, and accepted fixtures remain legacy technical identifiers until a dedicated compatibility migration updates producers, consumers, validators, and tests together. New generated packet filenames should prefer `cartenza_` when no existing contract requires `waymark_`, and readers should tolerate legacy generated names during the transition.

## Source Of Truth

These paths are repo source-of-truth and should be tracked when changed intentionally:

| Path | Policy |
| --- | --- |
| `data/schemas/` | Canonical mission and reaction-session JSON schemas. |
| `data/product_contracts/` | Product and technical contracts for app, survey, Atlas, graph, MusicKit payloads, and mission generation. |
| `data/atlas_schema/atlas_schema_contract_v0_1.*` | Atlas schema source contract. |
| `data/atlas_schema/atlas_delta_v0_1.*` | Atlas delta source contract. |
| `data/atlas_schema/alpha_hardening/` | Active alpha hardening contracts and acceptance material. |
| `data/atlas_explainer/atlas_explainer_render_pack_runtime_schema_v0_1_1.*` | Runtime schema contract for app-facing Atlas explainer render packs. |
| `data/atlas_explainer/source_recovery_research_notes/` | Curated source-recovery provenance used by the Atlas explainer builder chain. |
| `data/atlas_explainer/AtlasExplainerPack_v0_2_3_RenderHardened/` | Latest alpha render-hardened Atlas explainer candidate handoff. Track as first-class product data while PM approval is pending. |
| `data/alpha_consumable_layer/alpha_v0/*contract*`, `*policy*`, `*guardrail*`, `*manifest*`, `*.schema.json`, and paired `*.md` contract docs | Alpha graph surface contracts, guardrails, resolver policy, and manifests. |
| `data/canonical_graph/family_*/` | Canonical graph family source material. |
| `data/canonical_graph/current/` | Active Canonical Graph v1 source-of-truth corpus for mission engine, tagging, linking, Atlas targets, Apple ID resolution, album sidecar planning, and album track sidecar resources. |
| `data/canonical_graph/canonical_graph_source_of_truth_manifest.json` | Root pointer to the active Canonical Graph source-of-truth corpus. |
| `data/canonical_graph/CURRENT_CANONICAL_GRAPH.md` | Human-readable current graph source-of-truth pointer and gate summary. |
| `data/canonical_graph/affinity_contracts/` | Active graphwide affinity tagging contracts, allowed tags, validation schema, and QA evidence. |
| `data/canonical_graph/policy_hardening/` | Canonical graph policy source material. |
| `data/canonical_graph/canonical_graph_import_runbook.md` | Canonical graph import runbook. |

## First-Class Fixtures

These paths are deterministic fixtures or golden packets. Track them when they are intentionally accepted as part of tests, app import, or contract validation:

| Path | Policy |
| --- | --- |
| `data/missions/` | App/test mission fixtures. |
| `data/alpha_packets/golden_alpha_packet_v0_1/` | Golden mission-generation/app-import packet. |
| `data/atlas_schema/examples/` | Atlas contract examples. |
| `data/atlas_explainer/render_pack_v0_1_hardened/` | Hardened Atlas explainer loader fixture used by validation tooling and loader tech review. |
| `data/canonical_graph/import_dry_run/` | Generated dry-run output promoted as a read-only fixture for legacy survey simulation and review tooling. |
| `data/canonical_graph/normalization_pass_2/` | Generated normalization output promoted as active alpha survey/app-resource input. |
| `data/closed_loop_simulation/*/closed_loop_manifest.json`, `*schema*.json`, and `closed_loop_acceptance_report.md` | Promoted closed-loop simulation contracts and acceptance summaries. Raw profile outputs remain generated evidence. |
| `data/deprecated_mission_fixtures/` | Retired mission fixtures kept as a small archive while app resource deletions are reviewed. Do not use for runtime wiring. |
| `data/survey_pilot/` | Survey pilot inputs and fixtures, pending deeper split if generated runs appear. |
| `data/survey_simulation/schemas/` | Survey simulator schemas. |
| `data/survey_simulation/fake_profiles/` | Survey simulator source profiles. |
| `data/survey_simulation/apple_payloads/` | Survey simulator Apple payload fixtures. |
| `data/survey_simulation/hidden_reaction_corpora/` | Simulator corpora used as controlled test inputs. |
| `data/survey_simulation/survey_evidence_export/` | Promoted Survey Evidence Export contracts, schemas, app/Atlas handoff samples, and validation reports. |
| `data/survey_simulation/llm_profile_review/api_requests/`, `prompts/`, `public_packets/`, and `schemas/` | Source templates, public inputs, and Structured Output schemas for the profile-review pilot. Generated API runs stay ignored. |

## Generated Or Archive Candidates

These paths are generated evidence or historical review material. Do not treat them as source-of-truth unless a specific file is promoted into a contract, fixture, or docs path:

| Path | Policy |
| --- | --- |
| `data/**/*.zip` | Generated packet/review/evidence bundles. Ignored by default; keep external or replace with a manifest. |
| `data/exports/` | Local app/device exports. Ignored except `.gitkeep` placeholders. |
| `data/atlas_schema/ingestion_proof/` | Generated ingestion proof evidence. Promote selected fixtures/docs explicitly if needed. |
| `data/atlas_schema/node_interpretation_smoke/` | Generated smoke evidence. |
| `data/atlas_schema/wwtsf_substrate_smoke/` | Generated smoke evidence. |
| `data/canonical_graph/depth_hardening_v0_1/` | Historical generated hardening pass. Ignored by default; archive externally unless a specific artifact is promoted. |
| `data/canonical_graph/depth_hardening_v0_2/` | Historical generated hardening pass that produced `current/`. Ignored by default to avoid tracking redundant pass C/pass D bulk. |
| `data/closed_loop_simulation/**/profile_*/` | Raw per-profile generated closed-loop API outputs, hidden evaluator traces, requests, responses, and qualitative profile reviews. Ignored by default; promote only selected fixtures. |
| `data/atlas_explainer/**/*.zip` and Finder duplicate `* 2*` paths | Generated packet archives and local duplicate expansions. Ignored by default. |
| `data/atlas_explainer/AtlasExplainerPack_v0_2_Checkpoint/`, `AtlasExplainerPack_v0_2_All_Archetypes/`, `AtlasExplainerPack_v0_2_1_SourceDeepened/`, and `AtlasExplainerPack_v0_2_2_SourceRecovery/` | Rebuildable intermediate Atlas explainer packages. Ignored by default; promote only if an older package becomes an active handoff or required fixture. |
| `data/atlas_explainer/**/indexes/schema_validation_report_*.md` | Generated local validation logs that embed absolute machine paths. Re-run validation locally when needed. |
| `data/mission_generation/**/[0-9][0-9][0-9][0-9]*Z*/` and timestamped request/response attempts | Generated run evidence. |
| `data/mission_generation/alpha_first_batch_route_ready_v0_1/` | Generated first-batch route-ready attempts, except promoted contracts/manifests. |
| `data/survey_simulation/runs/` | Generated simulator runs. |
| `data/survey_simulation/reports/` | Generated simulator reports. |
| `data/survey_simulation/page_count_backtest/` | Generated backtest output. |
| `data/survey_simulation/llm_profile_review/api_pilot*/`, `content_review/`, `evidence_bundles/`, `reports/`, and `simulator_private/` | Generated or private LLM review API outputs and evidence bundles. |
| `data/survey_simulation/**/* 2*` | Local Finder duplicate files. Ignored by default; remove locally after confirming the non-duplicate file exists. |
| `data/waymark_canonical_graph_chatgpt_review_packet_*/` | Extracted generated review packets. Ignored by default after manifesting under `docs/reviews/canonical_graph/`; promote only specific artifacts that remain active. |

## Promotion Rule

Generated files become first-class only when a maintainer moves or copies a specific artifact into one of these places with a short note explaining why:

- `data/product_contracts/`
- `data/schemas/`
- `data/atlas_schema/examples/`
- `data/alpha_packets/`
- `data/missions/`
- a harness `fixtures/` directory
- `docs/`

Exception: `data/canonical_graph/current/` is a promoted source-of-truth corpus generated from the accepted Canonical Graph Pass D freeze. Regenerate it only through the promotion script and keep the root source-of-truth manifest current.

Do not promote raw LLM request/response logs, zipped packets, local exports, or Xcode build artifacts into source-of-truth paths.
