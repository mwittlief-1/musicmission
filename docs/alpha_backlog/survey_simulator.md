# Survey Simulator Backlog

Lane goal: app-renderable survey packets and validated Survey Evidence Export that flow into Atlas Schema v0.1 without hidden simulator leakage or premature Atlas truth.

## Non-Dependent Tasks

- [x] SIM-001 Finalize Alpha Survey app packet contract.
  - Include page metadata, tile metadata, typed `music_object_ref`, response state, optional tags, optional notes/freeform, Apple exposure summary, and graph provenance.
  - Output: `data/survey_simulation/survey_evidence_export/alpha_fast_survey_app_handoff/waymark_alpha_survey_output_contract_v0_1.md`
  - Output: `data/survey_simulation/survey_evidence_export/alpha_fast_survey_app_handoff/alpha_survey_page_packet_v0_1.schema.json`

- [x] SIM-002 Produce app-renderable survey slate examples.
  - Include graph-only and Apple-biased examples.
  - Use approved Canonical Graph candidate surfaces only.
  - Keep hidden profile truth out.
  - Output: `data/survey_simulation/survey_evidence_export/alpha_fast_survey_app_handoff/examples/graph_only_artist_page_001_alpha_survey_slate_packet.json`
  - Output: `data/survey_simulation/survey_evidence_export/alpha_fast_survey_app_handoff/examples/apple_biased_artist_page_001_alpha_survey_slate_packet.json`
  - Output: `data/survey_simulation/survey_evidence_export/alpha_fast_survey_app_handoff/examples/README.md`

- [x] SIM-003 Preserve five response states and normalization.
  - `love`, `like`, `ok`, `dont_like`, `dont_know_enough`.
  - `dont_know_enough` maps to familiarity uncertainty, not dislike.
  - `ok` maps to waypoint/context evidence, not landmark-level preference.
  - Output: response mapping frozen in `data/survey_simulation/survey_evidence_export/alpha_fast_survey_app_handoff/waymark_alpha_survey_output_contract_v0_1.md`
  - Validator: `scripts/validate_alpha_survey_output_v0_1.py`

- [x] SIM-004 Define selected and shown-unselected tag semantics.
  - Selected tags become user-visible Signal evidence.
  - Shown-unselected tags remain weak/non-selected context.
  - Hidden reason tags never enter public/app packets.
  - Output: tag semantics enforced in `data/survey_simulation/survey_evidence_export/survey_evidence_export_v0_1.schema.json`
  - Output: Signal handoff semantics reflected in `data/atlas_schema/ingestion_proof/survey_evidence_export_v0_1/public_profile_01_A3_Al1_S2/signals.jsonl`

- [x] SIM-005 Define survey notes/freeform evidence.
  - Keep notes optional unless product decides otherwise.
  - Preserve notes as user-visible evidence suitable for later `Signal` or `UserVocabularyTerm` extraction.
  - Output: `data/survey_simulation/survey_evidence_export/alpha_fast_survey_app_handoff/alpha_survey_app_ui_notes_v0_1.md`

- [x] SIM-006 Apple exposure prior summary shape.
  - Keep Apple fields under exposure/import/familiarity context.
  - Include source-mix caps and audit fields.
  - Do not export tokens, private library dumps, or taste-truth claims.
  - Output: Apple prior shape in `data/survey_simulation/survey_evidence_export/survey_evidence_export_v0_1.md`
  - Validator: Apple `taste_truth=false` checks in `scripts/validate_survey_evidence_export_v0_1.py`

- [x] SIM-007 Survey Evidence Export builder from app-style responses.
  - Produce v0.1-compatible append-only evidence atoms from visible responses.
  - Preserve response refs and comparison sets.
  - Output: `scripts/build_survey_evidence_export_v0_1.py`
  - Output: `data/survey_simulation/survey_evidence_export/alpha_fast_survey_app_handoff/public_profile_01_A2_Al1_S1_survey_evidence_export.json`

- [x] SIM-008 Validator coverage.
  - Validate schema, no private leakage, append-only semantics, typed refs, response-ref closure, Apple-as-exposure, and `evidence_strength_hint` not final confidence.
  - Output: `scripts/validate_survey_evidence_export_v0_1.py`
  - Output: `scripts/validate_alpha_survey_output_v0_1.py`
  - Output: full harness coverage in `scripts/validate_survey_simulation.py`

- [x] SIM-009 Atlas ingestion fixture handoff.
  - Produce at least three sample survey exports with corresponding expected `Signal -> AtlasDigestView` ingestion outputs or links to existing proof outputs.
  - Output: `data/survey_simulation/survey_evidence_export/samples/public_profile_01_A3_Al1_S2_survey_evidence_export.json`
  - Output: `data/survey_simulation/survey_evidence_export/samples/public_profile_05_A3_Al1_S2_survey_evidence_export.json`
  - Output: `data/survey_simulation/survey_evidence_export/samples/public_profile_06_A3_Al1_S2_survey_evidence_export.json`
  - Output: `data/atlas_schema/ingestion_proof/survey_evidence_export_v0_1/manifest.json`

- [x] SIM-010 Page count strategy artifact.
  - Preserve current best fallback and uncertainty.
  - Do not overclaim the deterministic backtest.
  - Support configurable page counts in packet generation.
  - Output: `data/survey_simulation/page_count_backtest/recommended_minimum_config.md`
  - Output: configurable packet generation in `scripts/build_alpha_survey_page_packet_v0_1.py`

- [x] SIM-011 App/UI implementation notes.
  - Document tile count, artwork fields, response cycle, local persistence expectations, accessibility constraints, and failure states.
  - Output: `data/survey_simulation/survey_evidence_export/alpha_fast_survey_app_handoff/alpha_survey_app_ui_notes_v0_1.md`

- [x] SIM-012 Survey feel QA prompts.
  - Provide short trusted-tester prompts for whether the survey feels like Waymark calibration rather than a generic quiz.
  - Output: `data/survey_simulation/survey_evidence_export/alpha_fast_survey_app_handoff/alpha_survey_app_ui_notes_v0_1.md`

- [x] SIM-013 Construction-only exclusion report.
  - Make it clear which fields are app-facing, Atlas-ingestable, QA-only, and simulator-private.
  - Output: `data/survey_simulation/survey_evidence_export/alpha_fast_survey_app_handoff/alpha_survey_construction_exclusion_report_v0_1.md`

## Post-Brand Review Alpha 1 Tasks

Product decisions received 2026-05-22 make Survey required in Alpha 1.

- [x] SIM-014 Produce fixed Alpha intake configuration.
  - Required Alpha intake: 4 artist pages, 2 album pages, 4 song pages.
  - No optional early exit in the normal first-run flow.
  - Keep advanced/freeform support available only if Product explicitly includes it.
  - Output: `scripts/build_alpha1_required_intake_v0_1.py`
  - Output: `data/survey_simulation/survey_evidence_export/alpha1_required_intake/waymark_survey_output_packet_public_profile_01_A4_Al2_S4_alpha1_intake.json`
  - Output: `data/survey_simulation/survey_evidence_export/alpha1_required_intake/public_profile_01_A4_Al2_S4_alpha1_survey_page_packet.json`

- [x] SIM-015 Update app handoff notes for required intake.
  - Document page labels, progress copy, completion semantics, and how to avoid "taste truth" overclaims.
  - Make long-press/nuance expectations explicit or mark as post-Alpha polish.
  - Output: `data/survey_simulation/survey_evidence_export/alpha_fast_survey_app_handoff/waymark_alpha_survey_output_contract_v0_1.md`
  - Output: `data/survey_simulation/survey_evidence_export/alpha_fast_survey_app_handoff/alpha_survey_app_ui_notes_v0_1.md`

- [x] SIM-016 Validate Survey completion export for mission generation.
  - Ensure fixed intake Survey Evidence Export has all refs needed by Atlas and Mission Generation.
  - Preserve Apple exposure as exposure context, not taste truth.
  - Output: `data/survey_simulation/survey_evidence_export/alpha1_required_intake/public_profile_01_A4_Al2_S4_survey_evidence_export.json`
  - Output: `data/survey_simulation/survey_evidence_export/samples/public_profile_01_A4_Al2_S4_survey_evidence_export.json`
  - Output: `data/survey_simulation/survey_evidence_export/samples/public_profile_05_A4_Al2_S4_survey_evidence_export.json`
  - Output: `data/survey_simulation/survey_evidence_export/samples/public_profile_06_A4_Al2_S4_survey_evidence_export.json`
  - Output: `data/survey_simulation/survey_evidence_export/alpha1_required_intake/alpha1_required_intake_validation_report.md`
  - Output: `data/survey_simulation/survey_evidence_export/alpha1_required_intake/alpha1_required_intake_evidence_validation_report.md`
  - Output: `data/survey_simulation/survey_evidence_export/alpha1_required_intake/alpha1_required_intake_mission_generation_handoff_report.md`
  - Output: `data/atlas_schema/ingestion_proof/alpha1_required_intake_survey_evidence_export_v0_1/manifest.json`

## Live Alpha Smoke Recovery Tasks

Source: `docs/alpha_backlog/alpha_live_smoke_recovery_2026_05_24.md`.

- [x] SIM-017 Define Survey page-selection audit artifact.
  - Contract should explain every displayed page without leaking hidden simulator truth or raw prompt/scoring internals.
  - Include page ID, step, displayed item IDs, typed music refs, source mix, candidate buckets, Apple exposure flags, page intent, candidate basis, top included/excluded candidate summaries, prior-response inputs, and dedupe reasons.
  - Mark fields as app-facing, PM diagnostic, Atlas-ingestable, or construction-only excluded.
  - Output: contract under `data/survey_simulation/survey_evidence_export/alpha_fast_survey_app_handoff/`.
  - Output: `data/survey_simulation/survey_evidence_export/alpha_fast_survey_app_handoff/survey_page_selection_audit_v0_1.md`
  - Output: app-side audit builder in `MusicAtlasController/Services/SurveyStore.swift`
  - Test: `MusicAtlasControllerTests/SurveyTests.swift::testSurveyPageSelectionAuditExplainsDisplayedPagesWithoutAtlasIngestion`

- [x] SIM-018 Add quarantine reason taxonomy for live Survey responses.
  - Explain quarantined responses as one of: missing displayed page, missing tile/ref, invalid response state, duplicate response, schema mismatch, non-visible construction data, or Apple-only unmatched object.
  - Update validators/fixtures so live `3` quarantined response cases can be triaged rather than counted only.
  - Acceptance: Survey Evidence Export validation reports total responses, Atlas-ingestable count, quarantined count, and reason counts.
  - Output: taxonomy in `data/survey_simulation/survey_evidence_export/survey_evidence_export_v0_1.md`
  - Output: schema enum in `data/survey_simulation/survey_evidence_export/survey_evidence_export_v0_1.schema.json`
  - Output: validator counts in `scripts/validate_survey_evidence_export_v0_1.py`
  - Output: builder taxonomy in `scripts/build_survey_evidence_export_v0_1.py`
  - Output: live triage fixture `data/survey_simulation/survey_evidence_export/alpha_fast_survey_app_handoff/examples/live_three_quarantine_cases_survey_evidence_export.json`
  - Output: live triage validation report `data/survey_simulation/survey_evidence_export/alpha_fast_survey_app_handoff/examples/live_three_quarantine_cases_validation_report.md`
  - Test: `MusicAtlasControllerTests/SurveyTests.swift::testSurveyEvidenceExportUsesDisplayedPagesAndQuarantinesUnshownResponses`

- [x] SIM-019 Add live adaptive Survey QA cases from the TestFlight finding.
  - Include Apple payload present but incomplete, prior negative responses to a visible cluster, no repeats on page 2, and pivot to contrast/boundary/bridge/familiarity probes.
  - Validate that page packets remain compatible with `waymark.alpha_survey_page_packet.v0.1`.
  - Validate Apple exposure stays `taste_truth=false`.
  - Output: `data/survey_simulation/survey_evidence_export/alpha_fast_survey_app_handoff/live_adaptive_survey_qa_report_2026_05_24.md`
  - Output: refreshed public Survey Evidence Export samples with quarantine taxonomy.
  - Test: `MusicAtlasControllerTests/SurveyTests.swift::testArtistPageOneUsesApplePayloadAndCanonicalGraphNotStaticPacket`
  - Test: `MusicAtlasControllerTests/SurveyTests.swift::testArtistPageTwoDoesNotRepeatDislikedAppleSeedObjects`

## Dependency Tripwires

Raise an issue when:

- App/Core needs final visual interaction choices, onboarding copy, or required-intake copy that Survey cannot decide alone.
- Canonical Graph changes family inclusion, graph label visibility, candidate file shape, or quarantine policy.
- Atlas requires correction/superseding atom behavior after first export.
- Product asks Survey to create promoted Atlas roles or final user taste claims.
- Apple Import/Privacy changes available payload fields or consent language.

## Do Not Do Yet

- Do not write promoted Atlas nodes.
- Do not let Mission consume raw survey construction logs.
- Do not export hidden fake-user truth, hidden reason tags, lookup state, evaluator outputs, or generator-visible inputs.
- Do not treat Apple exposure as taste truth.
- Do not treat `evidence_strength_hint` as Atlas confidence.

## Raised Issues

| issue id | blocker | owner lane | needed for | current workaround | status |
| --- | --- | --- | --- | --- | --- |

No concrete cross-lane issue was raised by Survey Simulator in this pass.

## Completion Report

When this lane pauses, add:

- files changed:
  - `data/survey_simulation/survey_evidence_export/alpha_fast_survey_app_handoff/waymark_alpha_survey_output_contract_v0_1.md`
  - `data/survey_simulation/survey_evidence_export/alpha_fast_survey_app_handoff/alpha_survey_page_packet_v0_1.schema.json`
  - `data/survey_simulation/survey_evidence_export/alpha_fast_survey_app_handoff/alpha_survey_app_ui_notes_v0_1.md`
  - `data/survey_simulation/survey_evidence_export/alpha_fast_survey_app_handoff/alpha_survey_construction_exclusion_report_v0_1.md`
  - `data/survey_simulation/survey_evidence_export/alpha_fast_survey_app_handoff/survey_page_selection_audit_v0_1.md`
  - `data/survey_simulation/survey_evidence_export/alpha_fast_survey_app_handoff/live_adaptive_survey_qa_report_2026_05_24.md`
  - `data/survey_simulation/survey_evidence_export/alpha_fast_survey_app_handoff/examples/`
  - `data/survey_simulation/survey_evidence_export/alpha1_required_intake/`
  - `data/survey_simulation/survey_evidence_export/survey_evidence_export_v0_1.md`
  - `data/survey_simulation/survey_evidence_export/survey_evidence_export_v0_1.schema.json`
  - `data/survey_simulation/survey_evidence_export/atlas_tech_owner_handoff/survey_evidence_export_v0_1.schema.json`
  - `data/survey_simulation/survey_evidence_export/atlas_tech_owner_handoff/public_profile_01_A3_Al1_S2_validation_report.md`
  - `data/survey_simulation/survey_evidence_export/samples/`
  - `data/atlas_schema/ingestion_proof/survey_evidence_export_v0_1/`
  - `data/atlas_schema/ingestion_proof/alpha1_required_intake_survey_evidence_export_v0_1/`
  - `scripts/build_alpha1_required_intake_v0_1.py`
  - `scripts/build_alpha_survey_page_packet_v0_1.py`
  - `scripts/build_alpha_survey_slate_examples_v0_1.py`
  - `scripts/build_survey_evidence_export_v0_1.py`
  - `scripts/validate_alpha_survey_output_v0_1.py`
  - `scripts/validate_survey_evidence_export_v0_1.py`
  - `scripts/validate_survey_simulation.py`
  - `MusicAtlasController/Services/SurveyStore.swift`
  - `MusicAtlasControllerTests/SurveyTests.swift`
- validators run:
  - `python3 -m compileall scripts/build_survey_evidence_export_v0_1.py scripts/validate_survey_evidence_export_v0_1.py`
  - `.venv/bin/python scripts/validate_alpha_survey_output_v0_1.py`
  - `.venv/bin/python scripts/validate_alpha_survey_output_v0_1.py --page-packet data/survey_simulation/survey_evidence_export/alpha1_required_intake/public_profile_01_A4_Al2_S4_alpha1_survey_page_packet.json --schema data/survey_simulation/survey_evidence_export/alpha_fast_survey_app_handoff/alpha_survey_page_packet_v0_1.schema.json --evidence-export data/survey_simulation/survey_evidence_export/alpha1_required_intake/public_profile_01_A4_Al2_S4_survey_evidence_export.json --report data/survey_simulation/survey_evidence_export/alpha1_required_intake/alpha1_required_intake_validation_report.md`
  - `.venv/bin/python scripts/validate_survey_evidence_export_v0_1.py --export data/survey_simulation/survey_evidence_export/alpha1_required_intake/public_profile_01_A4_Al2_S4_survey_evidence_export.json --report data/survey_simulation/survey_evidence_export/alpha1_required_intake/alpha1_required_intake_evidence_validation_report.md`
  - `.venv/bin/python scripts/validate_survey_evidence_export_v0_1.py --export data/survey_simulation/survey_evidence_export/alpha_fast_survey_app_handoff/public_profile_01_A2_Al1_S1_survey_evidence_export.json --report data/survey_simulation/survey_evidence_export/alpha_fast_survey_app_handoff/alpha_fast_survey_evidence_validation_report.md`
  - `.venv/bin/python scripts/validate_survey_evidence_export_v0_1.py --export data/survey_simulation/survey_evidence_export/alpha_fast_survey_app_handoff/examples/live_three_quarantine_cases_survey_evidence_export.json --report data/survey_simulation/survey_evidence_export/alpha_fast_survey_app_handoff/examples/live_three_quarantine_cases_validation_report.md`
  - `.venv/bin/python scripts/validate_survey_evidence_export_v0_1.py --export data/survey_simulation/survey_evidence_export/atlas_tech_owner_handoff/public_profile_01_A3_Al1_S2_survey_evidence_export.json --report data/survey_simulation/survey_evidence_export/atlas_tech_owner_handoff/public_profile_01_A3_Al1_S2_validation_report.md`
  - `jsonschema Draft202012Validator against data/survey_simulation/survey_evidence_export/atlas_tech_owner_handoff/survey_evidence_export_v0_1.schema.json`
  - `.venv/bin/python scripts/validate_survey_evidence_export_v0_1.py`
  - `.venv/bin/python scripts/ingest_survey_evidence_export_to_atlas.py --input-dir data/survey_simulation/survey_evidence_export/alpha1_required_intake --output-root data/atlas_schema/ingestion_proof/alpha1_required_intake_survey_evidence_export_v0_1`
  - `.venv/bin/python scripts/ingest_survey_evidence_export_to_atlas.py`
  - `.venv/bin/python scripts/validate_survey_simulation.py`
  - `xcodebuild test -project MusicAtlasController.xcodeproj -scheme MusicAtlasController -destination 'platform=iOS Simulator,name=iPhone 17,OS=26.5' -only-testing:MusicAtlasControllerTests/SurveyTests`
- app-ready packet examples:
  - `data/survey_simulation/survey_evidence_export/alpha1_required_intake/public_profile_01_A4_Al2_S4_alpha1_survey_page_packet.json`
  - `data/survey_simulation/survey_evidence_export/samples/public_profile_01_A4_Al2_S4_survey_evidence_export.json`
  - `data/survey_simulation/survey_evidence_export/samples/public_profile_05_A4_Al2_S4_survey_evidence_export.json`
  - `data/survey_simulation/survey_evidence_export/samples/public_profile_06_A4_Al2_S4_survey_evidence_export.json`
  - `data/survey_simulation/survey_evidence_export/alpha_fast_survey_app_handoff/public_profile_01_A2_Al1_S1_alpha_survey_page_packet.json`
  - `data/survey_simulation/survey_evidence_export/alpha_fast_survey_app_handoff/examples/graph_only_artist_page_001_alpha_survey_slate_packet.json`
  - `data/survey_simulation/survey_evidence_export/alpha_fast_survey_app_handoff/examples/apple_biased_artist_page_001_alpha_survey_slate_packet.json`
  - `data/survey_simulation/survey_evidence_export/alpha_fast_survey_app_handoff/examples/public_profile_05_A3_Al1_S2_alpha_survey_page_packet.json`
  - `data/survey_simulation/survey_evidence_export/alpha_fast_survey_app_handoff/examples/public_profile_06_A3_Al1_S2_alpha_survey_page_packet.json`
- remaining blockers:
  - No Survey-lane blocker raised. Cross-lane dependencies remain tracked in the master README: live Supabase/account access, final privacy/terms copy, final onboarding/FAQ copy, final Canonical family/label visibility, and Atlas promotion/correction semantics beyond the proven provisional flow.
- ready for Core app integration status: `yes_with_caveats`
  - Caveats: Core can integrate the fixed A4/Al2/S4 packet and produce Survey Evidence Export v0.1-compatible payloads now; upload/sync and final tester copy remain cross-lane dependencies. Atlas must retain provisional/candidate semantics downstream.
