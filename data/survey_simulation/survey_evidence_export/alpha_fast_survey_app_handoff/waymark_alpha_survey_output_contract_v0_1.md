# Waymark Alpha Survey Output Contract v0.1

Generated: 2026-05-21

Status: finalized for app handoff

Audience: App PM, App Engineering, Atlas PM, Atlas Engineering, Canonical Graph PM

## Purpose

Alpha Survey Output Contract v0.1 moves the Survey lane from simulator proof to app-renderable Survey output.

The app receives renderable survey page packets, captures one of five response states per visible tile, and emits a Survey Evidence Export v0.1-compatible append-only evidence payload for Atlas.

The app must not pass simulator-private truth, hidden corpus reactions, construction/debug state, raw scoring, or Profile Writer prose into Atlas ingestion.

Target Alpha flow:

```text
Survey Evidence Export
-> Signal
-> AtlasNode
-> provisional AtlasRoleAssignment
-> PossibleAtlasUpdateCandidate
-> AtlasDigestView
```

Survey owns the app-renderable page packet and Survey Evidence Export. Atlas owns Signal creation, AtlasNode persistence, provisional role assignment, possible update candidate creation, and digest view generation.

## Alpha 1 Required Intake

Product decision addendum `docs/app_dev/alpha_product_decision_addendum_2026_05_22.md` supersedes the earlier Alpha Fast Survey fallback.

Required Alpha 1 intake: `A4_Al2_S4`

| Surface | Pages | Tiles |
|---|---:|---:|
| Artist | 4 | 48 |
| Album | 2 | 24 |
| Song | 4 | 48 |
| Total | 10 | 120 |

Normal first-run Alpha intake has no optional early exit. Survey immediately follows onboarding and precedes Atlas/mission generation.

Required intake fixture:

`data/survey_simulation/survey_evidence_export/alpha1_required_intake/public_profile_01_A4_Al2_S4_alpha1_survey_page_packet.json`

## Legacy Alpha Fast Survey Fallback

Prior fallback for trusted Alpha: `A2_Al1_S1`

| Surface | Pages | Tiles |
|---|---:|---:|
| Artist | 2 | 24 |
| Album | 1 | 12 |
| Song | 1 | 12 |
| Total | 4 | 48 |

This is now a constrained fallback/test fixture, not the Alpha 1 required intake. It remains the smallest tested cross-surface configuration and the current best fatigue-adjusted fallback from the deterministic page-count backtest.

Known qualification:

No page-count configuration cleared every predictive threshold. If Alpha evidence is thin, contradictory, or low-confidence, the product should use concierge review rather than silently treating the Survey as complete.

The packet schema supports evaluated page-count configurations and render fixtures. Core should treat `A4_Al2_S4` as the required Alpha 1 first-run intake. `A2_Al1_S1` remains a legacy fallback/test fixture only.

## App-Renderable Page Packet

Schema:

`alpha_survey_page_packet_v0_1.schema.json`

Alpha 1 required intake sample:

`data/survey_simulation/survey_evidence_export/alpha1_required_intake/public_profile_01_A4_Al2_S4_alpha1_survey_page_packet.json`

Legacy fallback sample:

`public_profile_01_A2_Al1_S1_alpha_survey_page_packet.json`

The page packet contains:

- page identity and stage
- ordered render tiles
- typed `music_object_ref`
- display text
- page intent
- candidate basis
- approved graph surface reference
- graph refs as refs/IDs only
- Apple exposure prior
- response capture contract
- evidence export linkage

The page packet is app-renderable, not Atlas-ingestable. Atlas ingestion must use Survey Evidence Export v0.1.

Pre-response render fixtures may use `captured_state: null` and `normalized_operation: null`. Completed Survey output must capture one of the five response states before generating Atlas-ingestable evidence atoms.

## Response States

The app must preserve exactly five internal response states.

| Internal state | App label | Normalized operation | Atlas signal | Product interpretation |
|---|---|---|---|---|
| `love` | Love | `positive_high` | `strong_positive` | Strong positive evidence, scoped narrowly. |
| `like` | Like | `positive_medium` | `positive` | Positive evidence, not broad promotion by itself. |
| `ok` | OK | `waypoint_context` | `weak_positive_or_familiarity` | Context, utility, waypoint, or familiarity evidence. |
| `dont_like` | Not for me | `negative_scope_carefully` | `negative_scope_carefully` | Scoped negative evidence. |
| `dont_know_enough` | Don't know enough | `familiarity_uncertainty` | `familiarity_uncertainty` | Familiarity uncertainty, not preference-negative. |

UI labels can change later. Internal enum values should not change without a contract migration.

## Tags and Notes

Every render tile includes `response_capture`.

Required fields:

- `selected_tags`: array, may be empty
- `selected_tags_semantics`: `visible_signal_evidence`
- `shown_unselected_tags`: array, may be empty
- `shown_unselected_tags_semantics`: `weak_non_selected_context`
- `note`: string or null
- `allowed_states`: the five response states
- `captured_state`: sample/current response state
- `normalized_operation`: response-state normalization

For Alpha, selected and shown-unselected tags may be empty. The contract preserves the fields now so the app can add tag chips without changing the Atlas handoff shape.

Selected tags are visible Signal evidence. Shown-unselected tags are weak/non-selected context only; they are not negative tag evidence and must not be promoted as if the user selected them.

## Apple as Exposure Prior

Apple Music data must remain an exposure prior.

Required per tile:

```json
{
  "source": "apple_music",
  "interpretation": "exposure_prior",
  "taste_truth": false
}
```

Do not export Apple-derived `probable_affinity_score` to the app page packet or Atlas evidence export.

## Approved Graph Surface Use

Each tile must be backed by the approved Canonical Graph survey surface where available.

The app packet includes:

- `approved_graph_surface_ref.source`
- `approved_graph_surface_ref.review_status`
- `approved_graph_surface_ref.candidate_id`
- `approved_graph_surface_ref.survey_page_role`
- `approved_graph_surface_ref.survey_intent`
- `approved_graph_surface_ref.source_membership_id`

Graph meanings remain refs/IDs only unless visible meanings are explicitly present in the source packet or final Canonical family/label policy.

## Evidence Export Compatibility

For every visible app response, Survey must emit one Survey Evidence Export v0.1 evidence atom.

Required compatibility:

- `response_id` matches between app page packet and evidence atom
- `evidence_ref` matches between app page packet and evidence atom
- raw reaction matches captured state
- normalized operation matches response mapping
- Apple prior has `taste_truth: false`
- `construction_only_excluded` remains outside Atlas ingestion
- all Atlas-ingestable response refs resolve inside the same export
- `evidence_strength_hint` remains Survey metadata only, not final Atlas confidence
- selected tags become visible Signal evidence
- shown-unselected tags remain weak/non-selected context
- quarantined responses remain outside Atlas ingestion and carry a live-smoke taxonomy reason

Alpha 1 required intake evidence export:

`data/survey_simulation/survey_evidence_export/alpha1_required_intake/public_profile_01_A4_Al2_S4_survey_evidence_export.json`

Legacy fallback evidence export:

`public_profile_01_A2_Al1_S1_survey_evidence_export.json`

## Page-Selection Audit

Live Alpha smoke recovery adds a PM/support diagnostic artifact:

`survey_page_selection_audit_v0_1.md`

This audit explains displayed pages without becoming Atlas evidence. It may include visible page IDs, displayed item IDs, typed refs, page intent, candidate basis, source mix, Apple exposure flags, prior visible response refs, and sanitized dedupe/exclusion categories.

It must not include hidden simulator truth, raw Apple payload, raw ranking scores, adaptive target mix internals, randomization seeds, generation prompts, Profile Writer output, or Atlas truth claims.

Atlas must continue to ingest only Survey Evidence Export v0.1 `atlas_ingestable.evidence_atoms[]`.

## Quarantine Reason Taxonomy

Live quarantines must be explainable, not just counted. The allowed construction-only reasons are:

- `missing_displayed_page`
- `missing_tile_or_ref`
- `invalid_response_state`
- `duplicate_response`
- `schema_mismatch`
- `non_visible_construction_data`
- `apple_only_unmatched_object`

Validation reports must show total responses reviewed, Atlas-ingestable count, quarantined count, and quarantine reason counts.

## Hidden and Construction Data Exclusion Checklist

The app page packet and Atlas-ingestable evidence must exclude:

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
- raw model output
- evaluator output
- raw ranking scores
- suppression warnings
- generation prompts
- adaptive target mixes
- randomization seeds
- page construction debug payloads
- final Atlas confidence
- final Atlas role assignment
- final Atlas promotion decision

Allowed outside Atlas ingestion:

- `construction_only_excluded`
- quarantined unresolved/external response refs
- validation reports

## Validation Commands

Validate the Alpha 1 required app-renderable page packet against the evidence export:

```bash
.venv/bin/python scripts/validate_alpha_survey_output_v0_1.py \
  --page-packet data/survey_simulation/survey_evidence_export/alpha1_required_intake/public_profile_01_A4_Al2_S4_alpha1_survey_page_packet.json \
  --schema data/survey_simulation/survey_evidence_export/alpha_fast_survey_app_handoff/alpha_survey_page_packet_v0_1.schema.json \
  --evidence-export data/survey_simulation/survey_evidence_export/alpha1_required_intake/public_profile_01_A4_Al2_S4_survey_evidence_export.json \
  --report data/survey_simulation/survey_evidence_export/alpha1_required_intake/alpha1_required_intake_validation_report.md
```

Expected:

```text
OK: Alpha Survey Output validates at data/survey_simulation/survey_evidence_export/alpha1_required_intake/public_profile_01_A4_Al2_S4_alpha1_survey_page_packet.json
```

Validate the legacy fallback page packet against the evidence export:

```bash
.venv/bin/python scripts/validate_alpha_survey_output_v0_1.py
```

Expected:

```text
OK: Alpha Survey Output validates at data/survey_simulation/survey_evidence_export/alpha_fast_survey_app_handoff/public_profile_01_A2_Al1_S1_alpha_survey_page_packet.json
```

Validate the Alpha 1 required Survey Evidence Export v0.1 directly:

```bash
.venv/bin/python scripts/validate_survey_evidence_export_v0_1.py \
  --export data/survey_simulation/survey_evidence_export/alpha1_required_intake/public_profile_01_A4_Al2_S4_survey_evidence_export.json \
  --report data/survey_simulation/survey_evidence_export/alpha1_required_intake/alpha1_required_intake_evidence_validation_report.md
```

Expected:

```text
OK: Survey Evidence Export validates at data/survey_simulation/survey_evidence_export/alpha1_required_intake/public_profile_01_A4_Al2_S4_survey_evidence_export.json
```

Validate the legacy fallback Survey Evidence Export v0.1 directly:

```bash
.venv/bin/python scripts/validate_survey_evidence_export_v0_1.py \
  --export data/survey_simulation/survey_evidence_export/alpha_fast_survey_app_handoff/public_profile_01_A2_Al1_S1_survey_evidence_export.json \
  --report data/survey_simulation/survey_evidence_export/alpha_fast_survey_app_handoff/alpha_fast_survey_evidence_validation_report.md
```

Expected:

```text
OK: Survey Evidence Export validates at data/survey_simulation/survey_evidence_export/alpha_fast_survey_app_handoff/public_profile_01_A2_Al1_S1_survey_evidence_export.json
```

Validation reports:

- `data/survey_simulation/survey_evidence_export/alpha1_required_intake/alpha1_required_intake_validation_report.md`
- `data/survey_simulation/survey_evidence_export/alpha1_required_intake/alpha1_required_intake_evidence_validation_report.md`
- `data/survey_simulation/survey_evidence_export/alpha1_required_intake/alpha1_required_intake_mission_generation_handoff_report.md`
- `alpha_survey_output_validation_report.md`
- `alpha_fast_survey_evidence_validation_report.md`
- `alpha_survey_app_ui_notes_v0_1.md`
- `alpha_survey_construction_exclusion_report_v0_1.md`
- `survey_page_selection_audit_v0_1.md`
- `live_adaptive_survey_qa_report_2026_05_24.md`
- `examples/graph_only_artist_page_001_alpha_survey_slate_packet.json`
- `examples/apple_biased_artist_page_001_alpha_survey_slate_packet.json`
- `examples/public_profile_05_A3_Al1_S2_alpha_survey_page_packet.json`
- `examples/public_profile_06_A3_Al1_S2_alpha_survey_page_packet.json`

## Current Handoff Files

- `waymark_alpha_survey_output_contract_v0_1.md`
- `alpha_survey_page_packet_v0_1.schema.json`
- `data/survey_simulation/survey_evidence_export/alpha1_required_intake/waymark_survey_output_packet_public_profile_01_A4_Al2_S4_alpha1_intake.json`
- `data/survey_simulation/survey_evidence_export/alpha1_required_intake/public_profile_01_A4_Al2_S4_alpha1_survey_page_packet.json`
- `data/survey_simulation/survey_evidence_export/alpha1_required_intake/public_profile_01_A4_Al2_S4_survey_evidence_export.json`
- `data/survey_simulation/survey_evidence_export/alpha1_required_intake/alpha1_required_intake_validation_report.md`
- `data/survey_simulation/survey_evidence_export/alpha1_required_intake/alpha1_required_intake_evidence_validation_report.md`
- `data/survey_simulation/survey_evidence_export/alpha1_required_intake/alpha1_required_intake_mission_generation_handoff_report.md`
- `public_profile_01_A2_Al1_S1_alpha_survey_page_packet.json`
- `public_profile_01_A2_Al1_S1_survey_evidence_export.json`
- `alpha_survey_output_validation_report.md`
- `alpha_fast_survey_evidence_validation_report.md`
- `survey_page_selection_audit_v0_1.md`
- `live_adaptive_survey_qa_report_2026_05_24.md`

## Validated Status

The current handoff validates:

- app page packet schema compliance
- all five response states preserved
- selected/shown-unselected tag arrays present
- note field present
- Apple as exposure prior with `taste_truth: false`
- approved graph survey surface backing for each tile
- no hidden/private simulator truth
- no construction/debug leakage
- one Evidence Export v0.1 atom per visible response
- response and reaction compatibility between page packet and evidence export
- quarantine reason taxonomy and reason counts in validation reports

## Only Remaining Product Blockers

This contract should not block on more simulator proof.

The only product blockers are:

1. Live Supabase/account access:
   Core/Infrastructure must decide and configure live upload/sync. Survey can provide local validated payloads now.

2. Final privacy/terms and onboarding/FAQ copy:
   Product/Release/Core must finalize copy before silent upload or production tester flow.

3. Final Canonical family/label policy:
   Canonical Graph PM must decide whether family/archetype meanings become visible in Alpha or remain refs/IDs only.

4. Downstream ingestion semantics beyond the proven provisional flow:
   The proven target is `Survey Evidence Export -> Signal -> AtlasNode -> provisional AtlasRoleAssignment -> PossibleAtlasUpdateCandidate -> AtlasDigestView`. Atlas owns final confidence, promotion, correction, and superseding semantics.
