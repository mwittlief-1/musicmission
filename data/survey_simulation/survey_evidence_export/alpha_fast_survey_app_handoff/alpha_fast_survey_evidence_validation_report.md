# Survey Evidence Export v0.1 Validation Report

- Export: `data/survey_simulation/survey_evidence_export/alpha_fast_survey_app_handoff/public_profile_01_A2_Al1_S1_survey_evidence_export.json`
- Status: `passed`
- Total responses reviewed: `74`
- Atlas-ingestable responses: `48`
- Quarantined responses: `26`

## Checks

- JSON Schema compliance
- private/simulator/debug leakage guard
- raw page-construction payload exclusion
- typed music object refs
- append-only ledger semantics
- `evidence_strength_hint` as Survey-side hint, not Atlas confidence
- selected tags as visible Signal evidence
- shown-unselected tags as weak/non-selected context
- response-ref closure for Atlas-ingestable refs
- `dont_know_enough` as `familiarity_uncertainty`
- Apple Music as `exposure_prior`, not taste truth
- quarantine reason taxonomy and counts

## Quarantine Reason Counts

- `missing_displayed_page`: `26`

No validation errors found.
