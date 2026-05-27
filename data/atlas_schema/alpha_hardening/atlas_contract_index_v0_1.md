# Atlas Alpha Contract Index v0.1

Generated: 2026-05-21

## Purpose

This index is the Atlas lane's Alpha handoff map. It points downstream lanes to the current contracts, proof artifacts, validation commands, and guardrails without requiring them to inspect raw Survey packets or generated profile-writer artifacts.

## Controlling Contracts

| contract | path | use |
| --- | --- | --- |
| Atlas Schema Contract v0.1 | `data/atlas_schema/atlas_schema_contract_v0_1.md` | Product contract for the user interpretation layer. |
| Atlas JSON Schema v0.1 | `data/atlas_schema/atlas_schema_contract_v0_1.json` | JSON Schema for Atlas records and bundles. |
| AtlasDelta v0.1 | `data/atlas_schema/atlas_delta_v0_1.md` | "What changed?" object between Atlas states. |
| AtlasDelta JSON Schema | `data/atlas_schema/atlas_delta_v0_1.schema.json` | JSON Schema for Delta fixtures and future outputs. |
| MissionGenerationDigestView Alpha v0.1 | `data/mission_generation/mission_generation_digest_view_alpha_v0_1/mission_generation_digest_view_alpha_v0_1.md` | Compact Mission Generation read model from in-app Survey evidence. |
| MissionGenerationDigestView JSON Schema | `data/mission_generation/mission_generation_digest_view_alpha_v0_1/mission_generation_digest_view_alpha_v0_1.schema.json` | Supabase/OpenAI-friendly Mission Generation input schema. |
| Atlas Alpha 1 ingestion profile | `data/atlas_schema/alpha_hardening/atlas_alpha1_ingestion_profile_v0_1.json` | Machine-readable fixed Survey intake and upload/status guardrails after the 2026-05-22 product addendum. |
| Atlas Alpha 1 post-brand confirmations | `data/atlas_schema/alpha_hardening/atlas_alpha1_post_brand_review_confirmations_2026_05_22.md` | Product-facing confirmation for fixed intake, generation status wording, and uploaded evidence policy. |
| Atlas Live Smoke Diagnostic Contract | `data/atlas_schema/alpha_hardening/atlas_live_smoke_diagnostic_contract_v0_1.json` | Machine-readable classification for client diagnostic artifacts, link fields, and quarantine semantics without promoting Atlas truth. |
| Canonical/Atlas Route Identity Contract Alpha v0.1 | `data/atlas_schema/alpha_hardening/canonical_atlas_route_identity_contract_alpha_v0_1.md` | Live generation/import route identity, display, candidate-pool provenance, and Atlas evidence-boundary handoff. |

## Core Examples

| example | path |
| --- | --- |
| Landmark | `data/atlas_schema/examples/landmark.json` |
| Region | `data/atlas_schema/examples/region.json` |
| Frontier | `data/atlas_schema/examples/frontier.json` |
| Dead End | `data/atlas_schema/examples/dead_end.json` |
| Waypoint | `data/atlas_schema/examples/waypoint.json` |
| Signal | `data/atlas_schema/examples/signal.json` |
| Taste Feature | `data/atlas_schema/examples/taste_feature.json` |
| Survey-seeded update | `data/atlas_schema/examples/survey_seeded_update.json` |
| Mission Review possible update | `data/atlas_schema/examples/mission_review_possible_update.json` |
| AtlasDelta closed-loop profile 01 | `data/atlas_schema/examples/atlas_delta_closed_loop_profile_01.json` |
| AtlasDelta closed-loop profile 05 | `data/atlas_schema/examples/atlas_delta_closed_loop_profile_05.json` |
| AtlasDelta closed-loop profile 06 | `data/atlas_schema/examples/atlas_delta_closed_loop_profile_06.json` |
| MissionGenerationDigestView sample | `data/mission_generation/mission_generation_digest_view_alpha_v0_1/mission_generation_digest_view_alpha_v0_1.sample.json` |

## Proof Artifacts

| proof | path | note |
| --- | --- | --- |
| A3 ingestion proof | `data/atlas_schema/ingestion_proof/a3_gpt_5_5_3x3/` | Public A3 packet ingestion for profiles 01, 05, and 06. |
| Survey-to-AtlasDigestView proof | `data/atlas_schema/ingestion_proof/survey_to_atlas_digest_v0_1/` | Contract-shaped per-profile outputs from public packets. |
| Survey Evidence Export proof | `data/atlas_schema/ingestion_proof/survey_evidence_export_v0_1/` | Ingestion proof for the v0.1 Survey Evidence Export sample. |
| Node interpretation smoke | `data/atlas_schema/node_interpretation_smoke/a3_v0_1_1/` | Structured interpretation from slim packets only. |
| WWTSF substrate smoke | `data/atlas_schema/wwtsf_substrate_smoke/a3_v0_1_2/` | WWTSF substrate from Atlas read models, not raw Survey. |
| Closed-loop learning proof | `data/closed_loop_simulation/a3_first_batch_learning_v0_1_adaptive_contract_v0_1/` | Mission feedback to updated digest and AtlasDelta. |

## Validation Commands

One-command Atlas validation:

```bash
python3 scripts/validate_atlas_alpha_contracts.py
```

Route identity handoff validation:

```bash
python3 scripts/validate_canonical_atlas_route_identity_contract.py
```

Fixed-intake profile validation:

```bash
python3 scripts/validate_atlas_alpha1_intake_profile.py

python3 scripts/validate_atlas_alpha1_intake_profile.py \
  --survey-export path/to/A4_Al2_S4_survey_evidence_export.json
```

This runner separates:

- JSON syntax checks;
- JSON Schema checks;
- invariant checks;
- referential-integrity checks.

Targeted schema checks may still be run directly:

```bash
npx --yes ajv-cli@5 validate --strict=false --spec=draft2020 \
  -s data/atlas_schema/atlas_schema_contract_v0_1.json \
  -d 'data/atlas_schema/examples/*.json'

npx --yes ajv-cli@5 validate --strict=false --spec=draft2020 \
  -s data/atlas_schema/atlas_delta_v0_1.schema.json \
  -d 'data/atlas_schema/examples/atlas_delta_closed_loop_profile_*.json'

npx --yes ajv-cli@5 validate --strict=false --spec=draft2020 \
  -s data/mission_generation/mission_generation_digest_view_alpha_v0_1/mission_generation_digest_view_alpha_v0_1.schema.json \
  -d data/mission_generation/mission_generation_digest_view_alpha_v0_1/mission_generation_digest_view_alpha_v0_1.sample.json
```

## Non-Negotiable Read Rules

- `AtlasNode` represents the thing only.
- `AtlasRoleAssignment` owns user-specific role truth.
- `PossibleAtlasUpdateCandidate` is a proposal, not promotion.
- `Signal` is the durable evidence ledger.
- `AtlasDigestView` is the read surface for Mission Generation, Candidate Pool Builder, WWTSF, and app-facing summaries.
- `AtlasDelta` is deterministic change substrate, not final copy.
- Survey and Mission Review may write evidence and candidates, not promoted truth.
- Canonical Graph is read/reference-only from Atlas.
- Apple Music exposure is context, not taste truth.
- Hidden simulator truth and construction internals do not enter Atlas-ingestable or model-facing packets.
- Client diagnostics are support/audit artifacts unless they contain approved user-visible evidence atoms.
- Quarantined Survey responses remain diagnostics until repaired by a reviewed correction/superseding atom.
