# Survey Evidence Export v0.1 Validation Report

- Export: `data/survey_simulation/survey_evidence_export/samples/public_profile_01_A3_Al1_S2_survey_evidence_export.json`
- Status: `passed`

## Checks

- JSON Schema compliance
- private/simulator/debug leakage guard
- raw page-construction payload exclusion
- typed music object refs
- append-only ledger semantics
- `evidence_strength_hint` as Survey-side hint, not Atlas confidence
- response-ref closure for Atlas-ingestable refs
- `dont_know_enough` as `familiarity_uncertainty`
- Apple Music as `exposure_prior`, not taste truth

No validation errors found.
