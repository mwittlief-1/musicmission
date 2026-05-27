# Atlas Schema Backlog

Lane goal: harden Atlas Schema v0.1 into practical ingestion, read-model, and delta contracts that unblock Survey, Core, Canonical Graph, Mission Generation, WWTSF, and Supabase without automating promotion.

## Non-Dependent Tasks

- [x] ATL-001 Publish contract index.
  - Point downstream lanes to `atlas_schema_contract_v0_1.md`, JSON schema, examples, ingestion proofs, `AtlasDelta`, and validation commands.
  - Output: `data/atlas_schema/alpha_hardening/atlas_contract_index_v0_1.md`

- [x] ATL-002 Add validation runner.
  - One command should validate schema examples, ingestion bundles, and delta examples.
  - Keep JSON syntax, JSON Schema, and invariant checks separate.
  - Output: `scripts/validate_atlas_alpha_contracts.py`
  - Command: `python3 scripts/validate_atlas_alpha_contracts.py`

- [x] ATL-003 Service-level referential integrity prototype.
  - Check signal IDs, role assignment IDs, node refs, update candidate refs, digest refs, and canonical IDs where graph artifacts are available.
  - Output: `scripts/validate_atlas_alpha_contracts.py`
  - Note: runner checks Signal, RoleAssignment, PossibleAtlasUpdateCandidate, DigestView refs, and typed `music_object_ref` canonical/user-local/external/unresolved requirements.

- [x] ATL-004 App mission evidence ingestion mapping.
  - Define how Core app exports become `Signal` records for mission, playback, note, review, and resolution evidence.
  - Include skip/no-signal policy as provisional if final policy is not approved.
  - Output: `data/atlas_schema/alpha_hardening/atlas_alpha_hardening_contracts_v0_1.md` section "App Mission Evidence Ingestion Mapping"

- [x] ATL-005 Survey Evidence Export acceptance criteria.
  - Freeze what makes a Survey Evidence Export ingestible.
  - Include `evidence_strength_hint`, comparison sets, Apple exposure context, response refs, selected tags, shown-unselected tags, and quarantined refs.
  - Output: `data/atlas_schema/alpha_hardening/atlas_alpha_hardening_contracts_v0_1.md` section "Survey Evidence Export Acceptance Criteria"

- [x] ATL-006 `PossibleAtlasUpdateCandidate` patch-shape hardening.
  - Add typed common payload shapes for Survey-seeded updates and Mission Review updates while preserving extensibility.
  - Output: `data/atlas_schema/alpha_hardening/atlas_alpha_hardening_contracts_v0_1.md` section "PossibleAtlasUpdateCandidate Patch Shapes"

- [x] ATL-007 Correction/superseding atom policy draft.
  - Define how append-only Survey or app evidence can be corrected without mutation.
  - Output: `data/atlas_schema/alpha_hardening/atlas_alpha_hardening_contracts_v0_1.md` section "Correction / Superseding Atom Policy"

- [x] ATL-008 Manual promotion/demotion policy draft.
  - Keep automation out of scope.
  - Define what a human/reviewed path would need to move `candidate` to `promoted`, `demoted`, or `blocked`.
  - Output: `data/atlas_schema/alpha_hardening/atlas_alpha_hardening_contracts_v0_1.md` section "Manual Promotion / Demotion Policy Draft"

- [x] ATL-009 Mission feedback to `AtlasDelta` proof.
  - Use existing closed-loop outputs to show `reaction session -> Signals -> update candidates -> updated digest -> AtlasDelta`.
  - Output: `data/atlas_schema/alpha_hardening/atlas_alpha_hardening_contracts_v0_1.md` section "Mission Feedback to AtlasDelta Proof"

- [x] ATL-010 App-facing starter read model.
  - Define what the app can safely show before final Atlas UI: candidate roles, uncertainty, recent learning, or nothing.
  - Output: `data/atlas_schema/alpha_hardening/atlas_alpha_hardening_contracts_v0_1.md` section "App-Facing Starter Read Model"

- [x] ATL-011 `AtlasDelta.user_facing_summary_inputs` guardrail.
  - Clarify that these are source bullets, not final copy.
  - Provide an app-safe hidden/default-off stance until Product decides display.
  - Output: `data/atlas_schema/alpha_hardening/atlas_alpha_hardening_contracts_v0_1.md` section "AtlasDelta User-Facing Summary Guardrail"

- [x] ATL-012 Privacy/deletion inventory.
  - List Signals, notes, Apple exposure context, Atlas interpretations, model packets, deltas, and exports as data classes for Release/Trust/Privacy.
  - Output: `data/atlas_schema/alpha_hardening/atlas_alpha_hardening_contracts_v0_1.md` section "Privacy / Deletion Inventory"

- [x] ATL-013 Candidate Pool Builder read-path guide.
  - Show how to consume `AtlasRoleAssignment.candidate_pool_behavior` and `AtlasDigestView` without raw Atlas table dependence.
  - Output: `data/atlas_schema/alpha_hardening/atlas_alpha_hardening_contracts_v0_1.md` section "Candidate Pool Builder Read Path Guide"

- [x] ATL-014 WWTSF substrate guidance.
  - Document current model posture: GPT-5.5 fallback required where mini guardrails do not pass.
  - Keep WWTSF substrate separate from final user-facing copy.
  - Output: `data/atlas_schema/alpha_hardening/atlas_alpha_hardening_contracts_v0_1.md` section "WWTSF Substrate Guidance"

## Post-Brand Review Alpha 1 Tasks

Product decisions received 2026-05-22 add required Survey intake, generation status copy, and likely evidence upload.

- [!] ATL-015 Confirm fixed Survey intake ingestion profile.
  - 4 artist pages, 2 album pages, 4 song pages.
  - Survey output remains evidence, not final Atlas truth.
  - Atlas-side output: `data/atlas_schema/alpha_hardening/atlas_alpha1_ingestion_profile_v0_1.json`
  - Atlas-side confirmation: `data/atlas_schema/alpha_hardening/atlas_alpha1_post_brand_review_confirmations_2026_05_22.md`
  - Validator: `scripts/validate_atlas_alpha1_intake_profile.py`
  - MissionGenerationDigestView builder: `scripts/build_mission_generation_digest_from_atlas.py`
  - Current fixture proof: `data/mission_generation/mission_generation_digest_view_alpha_v0_1/generated_from_survey_evidence_export/`
  - Status: Atlas fixed-intake profile, validation gate, and Atlas-to-MissionGenerationDigestView handoff are complete for existing normalized `A3_Al1_S2` exports; full fixed-intake ingestion proof is blocked until Survey provides an `A4_Al2_S4` Survey Evidence Export fixture. See `ATL-I001`.

- [x] ATL-016 Review "building your Atlas" wording guardrails.
  - Allow progress/status copy without implying promoted/durable taste truth.
  - Provide safe alternatives if needed.
  - Output: `data/atlas_schema/alpha_hardening/atlas_alpha1_post_brand_review_confirmations_2026_05_22.md` section "ATL-016: \"Building Your Atlas\" Wording Guardrails"

- [x] ATL-017 Confirm uploaded app evidence policy.
  - Evidence upload/sync remains append-only and provisional.
  - Deletion/reset inventory must support privacy copy.
  - Output: `data/atlas_schema/alpha_hardening/atlas_alpha1_post_brand_review_confirmations_2026_05_22.md` section "ATL-017: Uploaded App Evidence Policy"
  - Note: final privacy/terms copy is still required before upload is enabled, but the Atlas data policy is defined without needing final copy.

## Live Alpha Smoke Recovery Tasks

Source: `docs/alpha_backlog/alpha_live_smoke_recovery_2026_05_24.md`.

- [x] ATL-018 Classify client diagnostic artifacts without promoting Atlas truth.
  - Define which diagnostic artifacts can become Atlas-ingestable evidence and which must remain PM/support-only.
  - Cover:
    - `apple_music_signal_payload`
    - `survey_page_selection_audit`
    - `survey_evidence_export`
    - `mission_generation_request_packet`
    - `mission_generation_result`
    - `mission_import_result`
    - `client_error_event`
  - Preserve the rule that Apple Music exposure, candidate scoring, generation prompts, and import failures are not user taste truth.
  - Output: add a diagnostics classification section to the Atlas alpha hardening contract.
  - Output: `data/atlas_schema/alpha_hardening/atlas_alpha_hardening_contracts_v0_1.md` sections "Live Alpha Diagnostic Artifact Classification" and "Live Alpha Audit Link Semantics"
  - Output: `data/atlas_schema/alpha_hardening/atlas_live_smoke_diagnostic_contract_v0_1.json`

- [x] ATL-019 Define audit link semantics across Survey, generation, import, and evidence.
  - Provide required/recommended link fields for `survey_session_id`, `client_request_id`, `generation_run_id`, `mission_id`, `evidence_ref`, app version/build, and tester alias.
  - Explain how quarantined Survey responses should remain visible for diagnostics without becoming `Signal` records.
  - Acceptance: Core/Infra can store linked diagnostics, while Atlas ingestion continues to consume only approved evidence atoms.
  - Output: `data/atlas_schema/alpha_hardening/atlas_alpha_hardening_contracts_v0_1.md` section "Live Alpha Audit Link Semantics"
  - Output: `data/atlas_schema/alpha_hardening/atlas_live_smoke_diagnostic_contract_v0_1.json`

## Dependency Tripwires

Raise an issue when:

- Core export shape lacks fields required for app evidence `Signal` records.
- Survey export changes evidence atom or response-ref behavior.
- Canonical Graph cannot provide a needed canonical ID or composition/version field.
- Product asks for automatic promotion thresholds.
- Release/Privacy must approve data retention, deletion, or external model packet handling.
- Mission Generation needs more digest fields than `AtlasDigestView` v0.1 provides.
- Product wants user-facing Atlas summary copy beyond approved provisional status language.

## Do Not Do Yet

- Do not auto-promote Survey or Mission Review outputs.
- Do not mutate canonical graph.
- Do not put authoritative role truth on `AtlasNode`.
- Do not turn `AtlasDelta` into final copy.
- Do not let Apple exposure context promote roles by itself.

## Raised Issues

| issue id | blocker | owner lane | needed for | current workaround | status |
| --- | --- | --- | --- | --- | --- |
| `ATL-I001` | Need fixed Alpha 1 Survey Evidence Export fixture with 4 artist pages, 2 album pages, and 4 song pages (`A4_Al2_S4`). Current normalized fixtures are `A3_Al1_S2`, and the validator confirms they do not satisfy fixed intake counts. | Survey Simulator | Full fixed-intake Atlas ingestion proof and first-batch MissionGenerationDigestView validation against the Alpha 1 intake shape. | Atlas published the fixed-intake profile and validator; existing `A3_Al1_S2` exports remain useful for schema/invariant proof only. | open |

## Completion Report

When this lane pauses, add:

- files changed:
  - `data/atlas_schema/alpha_hardening/atlas_contract_index_v0_1.md`
  - `data/atlas_schema/alpha_hardening/atlas_alpha_hardening_contracts_v0_1.md`
  - `data/atlas_schema/alpha_hardening/atlas_alpha1_ingestion_profile_v0_1.json`
  - `data/atlas_schema/alpha_hardening/atlas_alpha1_post_brand_review_confirmations_2026_05_22.md`
  - `data/atlas_schema/alpha_hardening/atlas_live_smoke_diagnostic_contract_v0_1.json`
  - `data/mission_generation/mission_generation_digest_view_alpha_v0_1/mission_generation_digest_view_alpha_v0_1.md`
  - `data/mission_generation/mission_generation_digest_view_alpha_v0_1/mission_generation_digest_view_alpha_v0_1.schema.json`
  - `data/mission_generation/mission_generation_digest_view_alpha_v0_1/mission_generation_digest_view_alpha_v0_1.sample.json`
  - `data/mission_generation/mission_generation_digest_view_alpha_v0_1/generated_from_survey_evidence_export/`
  - `scripts/build_mission_generation_digest_from_atlas.py`
  - `scripts/validate_atlas_alpha_contracts.py`
  - `scripts/validate_atlas_alpha1_intake_profile.py`
  - `docs/alpha_backlog/atlas_schema.md`
- validators run:
  - `python3 -m json.tool data/atlas_schema/alpha_hardening/atlas_live_smoke_diagnostic_contract_v0_1.json`
  - Result: passed.
  - `python3 scripts/build_mission_generation_digest_from_atlas.py`
  - Result: passed; generated 3 compact MissionGenerationDigestView packets from existing Atlas ingestion outputs. Output sizes: profile 01 = 48,433 bytes; profile 05 = 48,946 bytes; profile 06 = 41,814 bytes.
  - `npx --yes ajv-cli@5 validate --strict=false --spec=draft2020 -s data/mission_generation/mission_generation_digest_view_alpha_v0_1/mission_generation_digest_view_alpha_v0_1.schema.json -d data/mission_generation/mission_generation_digest_view_alpha_v0_1/generated_from_survey_evidence_export/mission_generation_digest_view_public_profile_01_A3_Al1_S2.json -d data/mission_generation/mission_generation_digest_view_alpha_v0_1/generated_from_survey_evidence_export/mission_generation_digest_view_public_profile_05_A3_Al1_S2.json -d data/mission_generation/mission_generation_digest_view_alpha_v0_1/generated_from_survey_evidence_export/mission_generation_digest_view_public_profile_06_A3_Al1_S2.json`
  - Result: passed; all 3 generated MissionGenerationDigestView packets are schema-valid.
  - `python3 scripts/validate_atlas_alpha_contracts.py`
  - Result: passed; 129 JSON files checked; 25 Atlas schema targets; 3 AtlasDelta schema targets; 4 MissionGenerationDigestView schema targets; invariant checks passed; referential integrity prototype checks passed.
  - `python3 scripts/validate_atlas_alpha_contracts.py --skip-schema`
  - Result: passed; 110 JSON files checked; invariant checks passed; referential integrity prototype checks passed.
  - `python3 scripts/validate_atlas_alpha1_intake_profile.py`
  - Result: passed for Atlas fixed-intake profile; no fixed Survey Evidence Export supplied.
  - `python3 scripts/validate_atlas_alpha1_intake_profile.py --survey-export data/survey_simulation/survey_evidence_export/samples/public_profile_01_A3_Al1_S2_survey_evidence_export.json`
  - Result: expected mismatch; current fixture is 3 artist / 1 album / 2 song, not Alpha 1 fixed 4 / 2 / 4.
  - `PYTHONPYCACHEPREFIX=/private/tmp/musicmission_pycache python3 -m py_compile scripts/build_mission_generation_digest_from_atlas.py scripts/validate_atlas_alpha_contracts.py scripts/validate_atlas_alpha1_intake_profile.py`
  - Result: passed.
- contract version:
  - Atlas Schema Contract v0.1 plus Alpha hardening v0.1 and Alpha 1 post-brand confirmation 2026-05-22.
- remaining blockers:
  - `ATL-I001`: fixed `A4_Al2_S4` Survey Evidence Export fixture needed from Survey Simulator for full Alpha 1 fixed-intake ingestion proof.
  - Final privacy/terms copy is required before enabling upload, but Atlas upload policy is defined and unblocked.
- ready for Core app integration status: `yes_with_caveats`
