# Live Adaptive Survey QA Report

Date: 2026-05-24

Status: ready for live Alpha smoke recovery handoff

## Purpose

This report ties the TestFlight finding back to the Survey lane contract and local app behavior:

- Apple payload can influence Artist Page 1.
- Page 2 does not repeat visible disliked Apple seed objects.
- Prior responses can pivot later pages toward adjacent, bridge, boundary, contrast, or familiarity probes.
- App-renderable page packets remain compatible with `waymark.alpha_survey_page_packet.v0.1`.
- Apple exposure remains `taste_truth=false`.

## QA Cases

| Case | Coverage | Validation |
|---|---|---|
| Apple payload present but incomplete | Page 1 can include exact Apple-derived artists while filling the rest from approved canonical graph surfaces. | `SurveyTests.testArtistPageOneUsesApplePayloadAndCanonicalGraphNotStaticPacket` |
| Prior negative responses to visible Apple cluster | Page 2 excludes those prior visible items and includes rejection/adjacent probes rather than repeating them. | `SurveyTests.testArtistPageTwoDoesNotRepeatDislikedAppleSeedObjects` |
| Page 2 no repeats | Required intake pages do not repeat IDs within object type. | `SurveyTests.testRequiredAlphaSurveyPagesDoNotRepeatWithinObjectType` |
| Canonical display blocklist | Canonical `alpha_candidate_blocklist_alpha_v0` entries are removed from Survey display. | `SurveyTests.testAlphaSurveyProviderFiltersCanonicalAlphaBlocklist` |
| Evidence export closure | Visible responses become Atlas-ingestable atoms; unshown responses are quarantined outside Atlas ingestion with a reason. | `SurveyTests.testSurveyEvidenceExportUsesDisplayedPagesAndQuarantinesUnshownResponses` |
| Apple is exposure only | App packet and Survey Evidence Export preserve `taste_truth=false`. | `validate_alpha_survey_output_v0_1.py`, `validate_survey_evidence_export_v0_1.py` |

## Current App Runtime Notes

The Alpha app runtime uses Canonical approved survey surfaces and local Survey responses to assemble the fixed `A4_Al2_S4` flow. It is not using the old static personal PoC packet for Page 1.

Deep/frontier candidates may appear when they are exact Apple payload matches or when prior visible responses make them relevant. They should not enter generic fallback pages solely because they exist in `page3_deep`.

## Validation Commands

```bash
.venv/bin/python scripts/validate_alpha_survey_output_v0_1.py \
  --page-packet data/survey_simulation/survey_evidence_export/alpha1_required_intake/public_profile_01_A4_Al2_S4_alpha1_survey_page_packet.json \
  --schema data/survey_simulation/survey_evidence_export/alpha_fast_survey_app_handoff/alpha_survey_page_packet_v0_1.schema.json \
  --evidence-export data/survey_simulation/survey_evidence_export/alpha1_required_intake/public_profile_01_A4_Al2_S4_survey_evidence_export.json \
  --report data/survey_simulation/survey_evidence_export/alpha1_required_intake/alpha1_required_intake_validation_report.md
```

```bash
.venv/bin/python scripts/validate_survey_evidence_export_v0_1.py \
  --export data/survey_simulation/survey_evidence_export/alpha1_required_intake/public_profile_01_A4_Al2_S4_survey_evidence_export.json \
  --report data/survey_simulation/survey_evidence_export/alpha1_required_intake/alpha1_required_intake_evidence_validation_report.md
```

```bash
xcodebuild test -project MusicAtlasController.xcodeproj \
  -scheme MusicAtlasController \
  -destination 'platform=iOS Simulator,name=iPhone 17,OS=26.5' \
  -only-testing:MusicAtlasControllerTests/SurveyTests
```

## Non-Goals

- This report does not authorize automatic diagnostic upload.
- This report does not promote Survey evidence into final Atlas truth.
- This report does not expose raw Apple Music payload or hidden simulator truth.
- This report does not change Mission Generation review gates.
