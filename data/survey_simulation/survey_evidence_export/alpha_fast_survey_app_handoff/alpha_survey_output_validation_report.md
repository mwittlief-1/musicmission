# Alpha Survey Output v0.1 Validation Report

- Page packet: `data/survey_simulation/survey_evidence_export/alpha_fast_survey_app_handoff/public_profile_01_A2_Al1_S1_alpha_survey_page_packet.json`
- Evidence export: `data/survey_simulation/survey_evidence_export/alpha_fast_survey_app_handoff/public_profile_01_A2_Al1_S1_survey_evidence_export.json`
- Status: `passed`

## Checks

- app page packet JSON Schema compliance
- five response states preserved
- selected/shown-unselected tag arrays and note field present
- selected tags marked as visible Signal evidence
- shown-unselected tags marked as weak/non-selected context
- Apple data exported as exposure prior with `taste_truth: false`
- approved canonical graph survey surface backing for each tile
- private simulator truth and construction/debug data excluded
- one Survey Evidence Export v0.1 atom per visible app response
- target Atlas flow preserved from export to digest
- response/reaction/linkage compatibility between app packet and evidence export

No validation errors found.
