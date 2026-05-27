# Survey Evidence Export v0.1 Validation Report

- Export: `data/survey_simulation/survey_evidence_export/alpha_fast_survey_app_handoff/examples/live_three_quarantine_cases_survey_evidence_export.json`
- Status: `passed`
- Total responses reviewed: `123`
- Atlas-ingestable responses: `120`
- Quarantined responses: `3`

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

- `apple_only_unmatched_object`: `1`
- `missing_displayed_page`: `1`
- `missing_tile_or_ref`: `1`

No validation errors found.
