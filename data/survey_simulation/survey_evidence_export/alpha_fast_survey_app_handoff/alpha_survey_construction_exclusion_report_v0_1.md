# Alpha Survey Construction Exclusion Report v0.1

Generated: 2026-05-21

Status: validated Survey-lane boundary report

## Purpose

This report separates app-facing fields, Atlas-ingestable fields, QA-only fields, and simulator-private fields for Alpha Survey output.

The governing rule is simple: Survey sends visible evidence atoms to Atlas, not construction payloads or private simulator truth.

## App-Facing Packet

Allowed in `waymark.alpha_survey_page_packet.v0.1`:

- page identity and stage
- ordered render tiles
- typed `music_object_ref`
- display text
- page intent
- candidate basis
- approved graph surface refs
- graph refs/IDs already present in the visible source packet
- Apple exposure prior with `taste_truth: false`
- five-state response contract
- selected tags as visible Signal evidence
- shown-unselected tags as weak/non-selected context
- optional note field
- planned evidence-export linkage

The app packet is renderable, not Atlas-ingestable.

## Atlas-Ingestable Payload

Allowed in Survey Evidence Export v0.1 `atlas_ingestable`:

- one evidence atom per visible response
- typed `music_object_ref`
- raw reaction and normalized operation
- `evidence_strength_hint` as Survey metadata only
- selected tags with `visible_signal_evidence` semantics
- shown-but-unselected tags with `weak_non_selected_context` semantics
- optional user note
- page context
- comparison set refs
- supporting visible response refs
- graph refs/IDs only
- Apple exposure prior with `taste_truth: false`
- provenance and timestamps

Target flow:

```text
Survey Evidence Export
-> Signal
-> AtlasNode
-> provisional AtlasRoleAssignment
-> PossibleAtlasUpdateCandidate
-> AtlasDigestView
```

## QA-Only / Non-Ingestable

Allowed only outside Atlas ingestion:

- validation reports
- construction-only exclusion summaries
- quarantined unresolved response refs with taxonomy reasons
- render fixture manifests
- schema validation outputs
- local harness acceptance reports

These may be useful for engineering and PM review, but they are not user evidence.

Quarantine reason taxonomy:

- `missing_displayed_page`
- `missing_tile_or_ref`
- `invalid_response_state`
- `duplicate_response`
- `schema_mismatch`
- `non_visible_construction_data`
- `apple_only_unmatched_object`

Validation reports must summarize total responses, Atlas-ingestable responses, quarantined responses, and reason counts.

## Simulator-Private / Excluded

Must not enter app-facing packets or Atlas-ingestable evidence:

- fake profile ID
- fake profile display label
- hidden reaction corpus ID
- hidden corpus reactions outside visible responses
- hidden reason tags
- hidden archetype tiers
- hidden anti-affinities
- hidden lookup status
- simulator-private truth packets
- Profile Writer prose
- evaluator output
- raw model output
- raw ranking score blocks
- suppression warnings
- generation prompts
- adaptive target mixes
- randomization seeds
- page construction debug payloads
- final Atlas confidence
- final Atlas role assignment
- final Atlas promotion decision

## Validated Checks

The validators enforce:

- JSON Schema compliance
- typed music object refs
- approved graph surface backing for app-renderable tiles
- no hidden/private/debug field leakage
- Apple as exposure prior, never taste truth
- `dont_know_enough` as familiarity uncertainty, not negative taste
- `evidence_strength_hint` as Survey metadata only
- selected tags as visible Signal evidence
- shown-unselected tags as weak/non-selected context
- response-ref closure for Atlas-ingestable refs
- construction-only exclusions outside Atlas ingestion
- quarantine reason taxonomy for non-ingestable response refs

Validation commands:

```bash
.venv/bin/python scripts/validate_alpha_survey_output_v0_1.py
.venv/bin/python scripts/validate_survey_evidence_export_v0_1.py
.venv/bin/python scripts/validate_survey_simulation.py
```
