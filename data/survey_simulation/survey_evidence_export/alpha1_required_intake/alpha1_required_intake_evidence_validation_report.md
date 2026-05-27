# Survey Evidence Export v0.1 Validation Report

- Export: `data/survey_simulation/survey_evidence_export/alpha1_required_intake/public_profile_01_A4_Al2_S4_survey_evidence_export.json`
- Status: `passed`
- Total responses reviewed: `120`
- Atlas-ingestable responses: `120`
- Quarantined responses: `0`

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

- none

No validation errors found.
