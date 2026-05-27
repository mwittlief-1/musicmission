# Canonical Music Graph Backlog

Lane goal: Alpha-safe music-object substrate and candidate surfaces that downstream lanes can consume without raw graph leakage, quarantine leakage, unsafe version merges, or accidental user-taste claims.

## Non-Dependent Tasks

- [x] CMG-001 Freeze the Alpha graph surface manifest.
  - List approved files, version, source hashes, included families, excluded/context-only families, caution families, suppressed/quarantined counts, and known warnings.
  - Output: `data/alpha_consumable_layer/alpha_v0/alpha_graph_surface_manifest.json`
  - Output: `data/alpha_consumable_layer/alpha_v0/alpha_graph_surface_manifest.md`

- [x] CMG-002 Produce Atlas `music_object_ref` mapping guide.
  - Cover canonical artist, canonical album, canonical song recording, external catalog, user-local, unresolved, and composition-placeholder paths.
  - State when `composition_policy_status` or `recording_variant_type` is required.
  - Output: `data/alpha_consumable_layer/alpha_v0/atlas_music_object_ref_alpha_v0.schema.json`
  - Output: `data/alpha_consumable_layer/alpha_v0/graph_to_atlas_music_object_ref_alpha_v0.md`
  - Output: `data/alpha_consumable_layer/alpha_v0/atlas_music_object_ref_examples_alpha_v0.json`

- [x] CMG-003 Harden resolver/version policy sidecars.
  - Cover covers, source versions, live versions, remasters, clean/explicit variants, cast recordings, worship standards, traditional songs, classical works, and soundtrack/context entities.
  - Output: `data/alpha_consumable_layer/alpha_v0/resolver_version_policy_sidecar_alpha_v0.json`
  - Output: `data/alpha_consumable_layer/alpha_v0/resolver_version_policy_sidecar_alpha_v0.md`

- [x] CMG-004 Add machine-readable resolver policy fields where missing.
  - Fields should let App/MusicKit and Supabase block auto-resolution for manual-review or quarantined objects.
  - Output: `data/alpha_consumable_layer/alpha_v0/resolver_policy_machine_fields_alpha_v0.json`
  - Output: `data/alpha_consumable_layer/alpha_v0/resolver_policy_machine_fields_alpha_v0.md`

- [x] CMG-005 Candidate role/risk vocabulary alignment.
  - Align graph/candidate roles to Atlas `candidate_pool_behavior`: `anchor`, `bridge`, `probe`, `risky_probe`, `waypoint`, `trap`, `exclude`, `unknown`.
  - Preserve false-nearby and dead-end items as probes, not recommendations.
  - Output: `data/alpha_consumable_layer/alpha_v0/candidate_role_risk_vocabulary_alpha_v0.json`
  - Output: `data/alpha_consumable_layer/alpha_v0/candidate_role_risk_vocabulary_alpha_v0.md`

- [x] CMG-006 Tile-log metadata completeness validator.
  - Ensure candidate files preserve `candidate_id`, `canonical_entity_id`, `object_type`, `family_id`, `archetype_ids`, `survey_page_role`, `survey_intent`, `dedupe_group`, `priority_score`, `trigger_rule`, `positive_inference`, `negative_inference`, and `do_not_infer`.
  - Output: `data/alpha_consumable_layer/alpha_v0/tile_log_metadata_contract_alpha_v0.json`
  - Output: `data/alpha_consumable_layer/alpha_v0/tile_log_metadata_contract_alpha_v0.md`
  - Validator: `scripts/validate_alpha_consumable_layer_alpha_v0.mjs`

- [x] CMG-007 Quarantine/suppression enforcement validator.
  - Confirm suppressed/quarantined rows cannot enter survey display, default mission generation, candidate pool export, or Apple Music auto-resolution.
  - Output: `data/alpha_consumable_layer/alpha_v0/alpha_candidate_blocklist_alpha_v0.json`
  - Output: `data/alpha_consumable_layer/alpha_v0/alpha_consumable_layer_guardrails_alpha_v0.md`
  - Validator: `scripts/validate_alpha_consumable_layer_alpha_v0.mjs`

- [x] CMG-008 Dedupe group QA.
  - Validate no page/candidate slate can show duplicate canonical IDs or duplicate dedupe groups unless explicitly marked as a version/composition test.
  - Validator: `scripts/validate_alpha_consumable_layer_alpha_v0.mjs`
  - Coverage: active family/object/page buckets and compact candidate pool sample.

- [x] CMG-009 Family inclusion recommendation for trusted Alpha.
  - Provide recommended included, sandboxed, concierge-only, and excluded families with rationale.
  - Output: `data/alpha_consumable_layer/alpha_v0/family_inclusion_recommendation_alpha_v0.json`
  - Output: `data/alpha_consumable_layer/alpha_v0/family_inclusion_recommendation_alpha_v0.md`

- [x] CMG-010 Caution-family playbook.
  - Families 13, 14, and 16 need explicit language/version/work/worship handling guidance.
  - Families 15 and 17 remain context-only unless a deliberate context mission/survey exists.
  - Output: `data/alpha_consumable_layer/alpha_v0/caution_family_playbook_alpha_v0.md`

- [x] CMG-011 Canonical gap and unresolved object policy.
  - Define how downstream lanes should represent user objects not in the graph without mutating graph identity.
  - Output: `data/alpha_consumable_layer/alpha_v0/canonical_gap_unresolved_object_policy_alpha_v0.md`

- [x] CMG-012 Compact candidate pool export helper.
  - Produce or specify an export format for a per-user compact candidate pool, sourced only from approved surfaces and Survey/Atlas digest context.
  - Keep it small enough for Mission Generation; do not send the whole graph.
  - Helper: `scripts/build_alpha_compact_candidate_pool_alpha_v0.mjs`
  - Format: `data/alpha_consumable_layer/alpha_v0/compact_candidate_pool_export_format_alpha_v0.md`
  - Sample: `data/alpha_consumable_layer/alpha_v0/sample_compact_candidate_pool_alpha_v0.json`

- [x] CMG-013 QA exception ledger.
  - Preserve all known warnings and manual-review rows with downstream impact notes.
  - Output: `data/alpha_consumable_layer/alpha_v0/qa_exception_ledger_alpha_v0.json`
  - Output: `data/alpha_consumable_layer/alpha_v0/qa_exception_ledger_alpha_v0.md`

## Post-Brand Review Alpha 1 Tasks

- [x] CMG-014 Align graph surfaces to fixed Alpha 1 Survey intake.
  - Product decision: four artist screens, two album screens, four song screens, twelve tiles per screen.
  - Confirm Alpha v0 has enough approved `page1_core` and `page2_adaptive` candidates without raw rows, context-only families, or quarantined/suppressed rows.
  - Output: `data/alpha_consumable_layer/alpha_v0/alpha1_fixed_survey_intake_graph_support_alpha_v0.json`
  - Output: `data/alpha_consumable_layer/alpha_v0/alpha1_fixed_survey_intake_graph_support_alpha_v0.md`
  - Validator: `scripts/validate_alpha_consumable_layer_alpha_v0.mjs`

- [x] CMG-015 Define first mission handoff boundary after Survey completion.
  - Preserve graph metadata as reference-only candidate material for generated first missions.
  - Block context-only families, quarantined rows, suppressed rows, and unsafe MusicKit/manual-review rows from default first mission generation.
  - Output: `data/alpha_consumable_layer/alpha_v0/alpha1_first_mission_handoff_graph_contract_alpha_v0.json`
  - Output: `data/alpha_consumable_layer/alpha_v0/alpha1_first_mission_handoff_graph_contract_alpha_v0.md`
  - Validator: `scripts/validate_alpha_consumable_layer_alpha_v0.mjs`

- [x] CMG-016 Add graph-safe language guardrails for post-Survey generation.
  - Allow "building your Atlas" / "building your first missions" as product language only when downstream state remains provisional.
  - Block wording that implies graph metadata is user taste or that Survey directly creates Landmarks, Regions, or Dead Ends.
  - Output: `data/alpha_consumable_layer/alpha_v0/alpha1_user_facing_graph_language_guardrails_alpha_v0.md`

- [x] CMG-017 Update frozen manifest and validation coverage.
  - Add Alpha 1 intake and first-mission handoff artifacts to the frozen `alpha_v0` consumable layer.
  - Preserve `alpha_v0` as the contract version; this is an Alpha 1 alignment layer, not a canonical hard lock.
  - Output: `data/alpha_consumable_layer/alpha_v0/alpha_graph_surface_manifest.json`
  - Output: `data/alpha_consumable_layer/alpha_v0/alpha_graph_surface_manifest.md`
  - Output: `data/alpha_consumable_layer/alpha_v0/alpha_consumable_layer_validation_report.md`

- [x] CMG-018 Update app/local candidate pool contract with Alpha 1 intake references.
  - Connect the frozen first-mission candidate pool contract to the Alpha 1 fixed Survey intake and handoff artifacts.
  - Output: `data/product_contracts/app_local_candidate_pool_contract_alpha_v0.md`

- [x] CMG-019 Resolve incoming Mission Generation blocker `MGN-I004`.
  - Replace artist-only compact route pools with concrete `track` / `album` route candidates.
  - Fill `waypoints` and `dead_end_checks` with approved route-ready objects.
  - Preserve canonical `song_recording` / `album` refs under `music_object_ref` while exposing Core/Mission `object_type = track|album`.
  - Output: `data/alpha_consumable_layer/alpha_v0/sample_compact_candidate_pool_alpha_v0.json`
  - Output: `data/alpha_consumable_layer/alpha_v0/route_ready_candidate_pool_report_alpha_v0.json`
  - Output: `data/alpha_consumable_layer/alpha_v0/route_ready_candidate_pool_report_alpha_v0.md`
  - Builder: `scripts/build_alpha_compact_candidate_pool_alpha_v0.mjs`
  - Validator: `scripts/validate_alpha_consumable_layer_alpha_v0.mjs`

- [x] CMG-020 Align Canonical contracts to Survey runtime shown-page evidence.
  - Survey owns live page selection and freezing; Canonical owns stable candidate surfaces and typed refs.
  - Atlas/Canonical-adjacent ingestion consumes only `survey_evidence_export.atlas_ingestable.evidence_atoms`.
  - `construction_only_excluded` is ignored for Atlas ingestion.
  - Preserve `dont_know -> familiarity_uncertainty`, Apple exposure is not taste truth, and Survey `evidence_strength_hint` is not Atlas confidence.
  - Output: `data/alpha_consumable_layer/alpha_v0/survey_runtime_ingestion_alignment_alpha_v0.json`
  - Output: `data/alpha_consumable_layer/alpha_v0/survey_runtime_ingestion_alignment_alpha_v0.md`
  - Output updates: `data/alpha_consumable_layer/alpha_v0/tile_log_metadata_contract_alpha_v0.json`
  - Output updates: `data/alpha_consumable_layer/alpha_v0/tile_log_metadata_contract_alpha_v0.md`
  - Validator: `scripts/validate_alpha_consumable_layer_alpha_v0.mjs`

## Live Alpha Smoke Recovery Tasks

Source: `docs/alpha_backlog/alpha_live_smoke_recovery_2026_05_24.md`.

- [x] CMG-021 Add candidate safety/review metadata needed to reduce false `review_needed`.
  - Audit route-ready candidate pool fields used by Mission Generation and Supabase review gates.
  - Ensure each route-ready candidate has enough metadata to distinguish Alpha-safe, review-needed, context-only, quarantined, suppressed, resolver-risk, and manual-review rows.
  - Output a candidate review-risk report showing which route-ready candidates can safely feed default Alpha mission generation.
  - Output: `data/alpha_consumable_layer/alpha_v0/candidate_review_risk_report_alpha_v0.json`
  - Output: `data/alpha_consumable_layer/alpha_v0/candidate_review_risk_report_alpha_v0.md`
  - Output updates: `data/alpha_consumable_layer/alpha_v0/sample_compact_candidate_pool_alpha_v0.json`
  - Output updates: `data/alpha_consumable_layer/alpha_v0/route_ready_candidate_pool_report_alpha_v0.json`
  - Output updates: `data/alpha_consumable_layer/alpha_v0/route_ready_candidate_pool_report_alpha_v0.md`
  - Builder updates: `scripts/build_alpha_compact_candidate_pool_alpha_v0.mjs`
  - Recovery builder: `scripts/build_alpha_live_smoke_recovery_graph_artifacts_alpha_v0.mjs`
  - Validator: `scripts/validate_alpha_consumable_layer_alpha_v0.mjs`

- [x] CMG-022 Add diagnostic refs for Survey page-selection audit.
  - Provide stable refs/labels that Core/Survey can include in `survey_page_selection_audit` without exposing raw graph rows.
  - Include dedupe group, approved surface ref, candidate basis, family/archetype, caution flag, and graph provenance summary where safe.
  - Acceptance: Survey/Core can explain why a tile was displayed using Canonical refs only, not hidden simulator truth or raw graph internals.
  - Output: `data/alpha_consumable_layer/alpha_v0/survey_page_selection_audit_refs_alpha_v0.json`
  - Output: `data/alpha_consumable_layer/alpha_v0/survey_page_selection_audit_refs_alpha_v0.md`
  - Recovery builder: `scripts/build_alpha_live_smoke_recovery_graph_artifacts_alpha_v0.mjs`
  - Validator: `scripts/validate_alpha_consumable_layer_alpha_v0.mjs`

## Dependency Tripwires

Raise an issue when:

- Survey changes page count, page role names, or reaction semantics in a way that changes graph candidate role requirements.
- Survey changes Evidence Export path names or stops emitting same-session displayed page history.
- App/MusicKit needs resolver telemetry fields not present in graph sidecars.
- Atlas importer requires referential integrity checks or object-ref fields not derivable from current graph artifacts.
- Product asks for public family/archetype labels beyond IDs/roles.
- Mission Generation wants graph rows outside the approved Alpha surfaces.

## Do Not Do Yet

- Do not hard-lock the full canonical graph.
- Do not use raw graph rows for Fast Survey or default first missions.
- Do not merge by title alone.
- Do not let graph roles become Atlas role truth.
- Do not auto-resolve quarantined/manual-review rows.
- Do not treat Apple payload as canonical identity or taste.

## Raised Issues

| issue id | blocker | owner lane | needed for | current workaround | status |
| --- | --- | --- | --- | --- | --- |

No raised cross-lane issues in this pass. Atlas `music_object_ref` details were sufficient for Alpha alignment; promotion semantics remain intentionally outside this lane.

## Completion Report

When this lane pauses, add:

- files changed:
  - `data/alpha_consumable_layer/alpha_v0/alpha_graph_surface_manifest.json`
  - `data/alpha_consumable_layer/alpha_v0/alpha_graph_surface_manifest.md`
  - `data/alpha_consumable_layer/alpha_v0/alpha_candidate_blocklist_alpha_v0.json`
  - `data/alpha_consumable_layer/alpha_v0/alpha_consumable_layer_guardrails_alpha_v0.md`
  - `data/alpha_consumable_layer/alpha_v0/alpha_consumable_layer_validation_report.md`
  - `data/alpha_consumable_layer/alpha_v0/atlas_music_object_ref_alpha_v0.schema.json`
  - `data/alpha_consumable_layer/alpha_v0/atlas_music_object_ref_examples_alpha_v0.json`
  - `data/alpha_consumable_layer/alpha_v0/graph_to_atlas_music_object_ref_alpha_v0.md`
  - `data/alpha_consumable_layer/alpha_v0/candidate_role_risk_vocabulary_alpha_v0.json`
  - `data/alpha_consumable_layer/alpha_v0/candidate_role_risk_vocabulary_alpha_v0.md`
  - `data/alpha_consumable_layer/alpha_v0/resolver_version_policy_sidecar_alpha_v0.json`
  - `data/alpha_consumable_layer/alpha_v0/resolver_version_policy_sidecar_alpha_v0.md`
  - `data/alpha_consumable_layer/alpha_v0/resolver_policy_machine_fields_alpha_v0.json`
  - `data/alpha_consumable_layer/alpha_v0/resolver_policy_machine_fields_alpha_v0.md`
  - `data/alpha_consumable_layer/alpha_v0/tile_log_metadata_contract_alpha_v0.json`
  - `data/alpha_consumable_layer/alpha_v0/tile_log_metadata_contract_alpha_v0.md`
  - `data/alpha_consumable_layer/alpha_v0/survey_runtime_ingestion_alignment_alpha_v0.json`
  - `data/alpha_consumable_layer/alpha_v0/survey_runtime_ingestion_alignment_alpha_v0.md`
  - `data/alpha_consumable_layer/alpha_v0/family_inclusion_recommendation_alpha_v0.json`
  - `data/alpha_consumable_layer/alpha_v0/family_inclusion_recommendation_alpha_v0.md`
  - `data/alpha_consumable_layer/alpha_v0/caution_family_playbook_alpha_v0.md`
  - `data/alpha_consumable_layer/alpha_v0/canonical_gap_unresolved_object_policy_alpha_v0.md`
  - `data/alpha_consumable_layer/alpha_v0/compact_candidate_pool_export_format_alpha_v0.md`
  - `data/alpha_consumable_layer/alpha_v0/sample_compact_candidate_pool_alpha_v0.json`
  - `data/alpha_consumable_layer/alpha_v0/route_ready_candidate_pool_report_alpha_v0.json`
  - `data/alpha_consumable_layer/alpha_v0/route_ready_candidate_pool_report_alpha_v0.md`
  - `data/alpha_consumable_layer/alpha_v0/candidate_review_risk_report_alpha_v0.json`
  - `data/alpha_consumable_layer/alpha_v0/candidate_review_risk_report_alpha_v0.md`
  - `data/alpha_consumable_layer/alpha_v0/survey_page_selection_audit_refs_alpha_v0.json`
  - `data/alpha_consumable_layer/alpha_v0/survey_page_selection_audit_refs_alpha_v0.md`
  - `data/alpha_consumable_layer/alpha_v0/alpha1_fixed_survey_intake_graph_support_alpha_v0.json`
  - `data/alpha_consumable_layer/alpha_v0/alpha1_fixed_survey_intake_graph_support_alpha_v0.md`
  - `data/alpha_consumable_layer/alpha_v0/alpha1_first_mission_handoff_graph_contract_alpha_v0.json`
  - `data/alpha_consumable_layer/alpha_v0/alpha1_first_mission_handoff_graph_contract_alpha_v0.md`
  - `data/alpha_consumable_layer/alpha_v0/alpha1_user_facing_graph_language_guardrails_alpha_v0.md`
  - `data/alpha_consumable_layer/alpha_v0/qa_exception_ledger_alpha_v0.json`
  - `data/alpha_consumable_layer/alpha_v0/qa_exception_ledger_alpha_v0.md`
  - `data/product_contracts/app_local_candidate_pool_contract_alpha_v0.md`
  - `scripts/validate_alpha_consumable_layer_alpha_v0.mjs`
  - `scripts/build_alpha_compact_candidate_pool_alpha_v0.mjs`
  - `scripts/build_alpha_live_smoke_recovery_graph_artifacts_alpha_v0.mjs`
  - `docs/alpha_backlog/canonical_music_graph.md`
- validators run:
  - `node scripts/validate_alpha_consumable_layer_alpha_v0.mjs`
  - Result: `ALPHA_CONSUMABLE_LAYER_VALIDATION_PASS`
- approved Alpha surface version:
  - `alpha_v0`
- remaining blockers:
  - None for this lane's non-dependent Alpha consumable-layer tasks.
  - Atlas promotion/demotion thresholds remain owned by Atlas/Product and are intentionally not required for this lane.
- ready for Core app integration status: `yes_with_caveats`
  - Caveats: Core must consume only `alpha_v0` surfaces/helpers, enforce validator-backed quarantine/suppression/dedupe/version gates, and treat `music_object_ref` plus graph metadata as reference-only evidence context, never user taste or Atlas promotion.
