# Mission Enrichment v0.2 Alpha Provisional Lock

Date: 2026-06-04

Decision owner: CEO/Product

Status: Provisionally locked for alpha contract and output behavior. Not app/backend integrated.

## Decision

Mission Enrichment v0.2 is provisionally accepted as the alpha baseline for enriching deterministic Cartenza missions with app-facing mission copy, route-item setup copy, and ranked secondary reaction chip candidates.

This lock supersedes the earlier runtime-candidate posture for the v0.2 contract package. v0.1 remains superseded.

## Locked Scope

- `MissionEnrichmentInput_v0_2` and `MissionEnrichmentOutput_v0_2` schemas.
- Secondary reaction tag registry v0.2.
- Deterministic secondary-tag prefilter behavior.
- Prompt guardrails, including validation-critical rules for linked song affinity tags, linked user alignment hints, and display-safe Atlas target labels.
- Validator rules for mission identity/order preservation, tag validity, applicability gates, copy safety, and raw ID/tag leakage.
- Build 45 compatibility for `gateway_test` and route roles `bridge`, `context`, and `comparator`.
- Alpha behavior for missing song-affinity sidecar rows: leave song affinity arrays empty rather than inventing tags.

## Acceptance Evidence

Product reviewed the six Build 45 Mission Enrichment outputs and judged them good enough to provisionally lock for alpha.

Combined validated output packet:

- `runs/build45_six_mission_enrichment_v0_2_combined_validated_20260604T173100Z/combined_summary.md`
- `runs/build45_six_mission_enrichment_v0_2_combined_validated_20260604T173100Z/combined_validated_outputs.json`

Validation summary:

- Mission count: 6
- Route item count: 36
- Live OpenAI outputs accepted into combined packet: 6
- Local v0.2 validation passed: all 6
- Model used for accepted output packet: `gpt-4.1`
- Combined accepted-output token usage: 83,190 total tokens
- Combined accepted-output estimated API cost: `$0.414006`

Mission IDs accepted:

- `MIS_ALPHA_SURVEY_OPPORTUNITY_DEPTH_01`
- `MIS_ALPHA_SURVEY_OPPORTUNITY_DEPTH_02`
- `MIS_ALPHA_SURVEY_OPPORTUNITY_BRIDGE_01`
- `MIS_ALPHA_SURVEY_OPPORTUNITY_BOUNDARY_01`
- `MIS_ALPHA_SURVEY_OPPORTUNITY_CONTEXT_01`
- `MIS_ALPHA_SURVEY_OPPORTUNITY_GATEWAY_01`

## Data Findings

- The Supabase diagnostic packet captured mission IDs only; it did not include route bodies.
- The local Build 45 share packet v2 supplied the complete mission bodies and 36 route items.
- Song-level affinity tags were present for 33 of 36 route items.
- Missing affinity rows were left empty rather than inferred:
  - `Bastards of Young`
  - `The One I Love`
  - `I Will Dare`

## Integration Boundaries

This lock does not authorize broad runtime rewiring by itself.

Still out of scope for this lock:

- iOS app integration.
- Supabase runtime integration.
- Atlas mutation or persistence.
- Production OpenAI execution configuration.
- Mission selection changes.
- Backfilling missing song-affinity rows.

## Follow-Ups Before Runtime Integration

1. Decide deployed OpenAI model and runtime configuration path.
2. Wire Mission Enrichment after deterministic mission selection only.
3. Preserve validator checks in the runtime or CI path before app display.
4. Decide whether `artist_context_available` is the canonical app/backend hook for artist-context gating.
5. Capture mission bodies and route items in future Supabase diagnostics.
6. Decide whether to backfill the three missing Build 45 sidecar rows before wider alpha use.

## Product Note

The lock is provisional: it authorizes alpha use of this contract and output behavior while preserving room for copy, chip-label, and registry tuning after real tester feedback.
