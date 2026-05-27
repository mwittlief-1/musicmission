# Waymark Alpha Fast Survey Evidence Contract v0.1

Generated: 2026-05-21

Audience: App PM, App Engineering, Atlas PM, Atlas Engineering

Status: finalized for Alpha app handoff

## Purpose

Alpha Fast Survey emits a normalized append-only evidence ledger from Survey to Atlas. The app should capture visible user responses and export Survey Evidence Export v0.1 evidence atoms. The app should not pass raw page-construction payloads, Survey Builder debug state, simulator-private data, or Profile Writer prose to Atlas.

This contract is for trusted Alpha. It does not decide the final public onboarding flow.

## Page Count Recommendation

Recommended Alpha Fast Survey config: `A2_Al1_S1`

| Surface | Pages | Tiles |
|---|---:|---:|
| Artist | 2 | 24 |
| Album | 1 | 12 |
| Song | 1 | 12 |
| Total | 4 | 48 |

Rationale:

- `A2_Al1_S1` is the smallest tested cross-surface configuration.
- It is the current best fatigue-adjusted fallback in the deterministic page-count backtest.
- It gives Atlas artist, album, and song evidence instead of artist-only evidence.
- It keeps trusted Alpha onboarding feasible while preserving enough evidence diversity for concierge review.

Important qualification:

No tested page-count configuration cleared every pre-declared predictive threshold. `A2_Al1_S1` is therefore the Alpha Fast Survey recommendation, not the final public onboarding length. Use it as a constrained Alpha default, with optional concierge escalation when the evidence is visibly thin or contradictory.

## Response Enum Mapping

The app may use user-facing labels, but the exported internal values must remain stable.

| App-facing meaning | Export `reaction.raw_value` | `normalized_operation` | `taste_polarity` | `atlas_signal` | `evidence_strength_hint.hint` | Product rule |
|---|---|---|---|---|---|---|
| Favorite / Love | `love` | `positive_high` | `positive` | `strong_positive` | `strong_positive_basis` | Strong positive evidence, still scoped to the smallest justified object. |
| Like | `like` | `positive_medium` | `positive` | `positive` | `medium_positive_basis` | Positive evidence, usually not enough by itself for broad region promotion. |
| OK / Fine / Keep | `ok` | `waypoint_context` | `contextual` | `weak_positive_or_familiarity` | `waypoint_or_context_basis` | Waypoint, context, or familiarity evidence. Not landmark evidence. |
| Not for me | `dont_like` | `negative_scope_carefully` | `negative` | `negative_scope_carefully` | `negative_scope_basis` | Scoped negative evidence. Not a genre-wide dead end. |
| Don't know enough | `dont_know_enough` | `familiarity_uncertainty` | `none` | `familiarity_uncertainty` | `familiarity_uncertainty_basis` | Familiarity uncertainty. Must not become `preference_negative`. |

`evidence_strength_hint` is a Survey-side evidence-basis hint only. It is not final Atlas confidence. Atlas must calculate final confidence from its own accumulated evidence, conflict handling, and promotion model.

## Evidence Export Requirements

The app must emit Survey Evidence Export v0.1:

- `schema_version: "waymark.survey_evidence_export.v0.1"`
- `ledger_semantics.mode: "append_only"`
- one evidence atom per visible survey response
- typed `music_object_ref` for every response
- raw reaction plus normalized operation
- selected tags and shown-but-unselected tags, even if empty
- optional note, even if null
- page intent and candidate basis
- comparison set
- graph refs as refs/IDs only
- Apple exposure prior with `taste_truth: false`
- provenance and timestamps

Atlas may ingest only `atlas_ingestable.evidence_atoms`.

## Sample Evidence Export

Sample Fast Survey export:

`data/survey_simulation/survey_evidence_export/alpha_fast_survey_app_handoff/public_profile_01_A2_Al1_S1_survey_evidence_export.json`

Sample summary:

- config: `A2_Al1_S1`
- total tiles / evidence atoms: 48
- artist pages: 2
- album pages: 1
- song pages: 1
- ledger mode: `append_only`
- Apple `taste_truth` values: `[false]`
- `dont_know_enough` normalized operation: `familiarity_uncertainty`
- `evidence_strength_hint.is_final_atlas_confidence` values: `[false]`
- quarantined construction-only refs: 26

The 26 quarantined refs are not Atlas-ingestable. They point outside the selected Fast Survey export window and are retained only as construction-only exclusions.

## Hidden and Construction Data Exclusion Checklist

The following must not appear in `atlas_ingestable`:

### Hidden / Simulator-Private Data

- hidden fake profile ID
- fake profile display label
- hidden reaction corpus ID
- hidden corpus reactions outside visible survey responses
- hidden reason tags
- hidden archetype tiers
- hidden anti-affinities
- hidden lookup status
- simulator-private truth packets
- truth-scored evaluator data

### Survey Construction / Debug Data

- tile layout position
- tile ID
- page mode
- adaptive context
- generator-visible inputs
- raw ranking score blocks
- suppression warnings
- randomization seeds
- generation prompts
- adaptive target mixes
- Profile Writer prose
- raw model responses
- evaluator prose

### Derived Meaning That Atlas Must Own

- final Atlas confidence
- final role assignment
- landmark promotion
- region promotion
- dead-end confirmation
- mission generation copy
- graph family or archetype meanings unless visible meanings are explicitly present in the source packet
- Apple-derived taste truth

Allowed outside ingestion:

- `construction_only_excluded` may contain exclusion metadata and quarantined refs.
- Atlas must ignore `construction_only_excluded` for ingestion.

## Apple Exposure Rule

Apple Music data exports only as `apple_exposure_prior`.

Required:

```json
{
  "interpretation": "exposure_prior",
  "taste_truth": false
}
```

Allowed Apple dimensions:

- `exact_signal_weight`
- `exposure_score`
- `recency_score`
- `repetition_score`
- `library_commitment_score`
- `favorite_or_rating_score`
- `playlist_context_score`
- `album_completion_hint`
- `artist_depth_hint`

Do not export `probable_affinity_score` to Atlas.

## Response Reference Integrity Gate

Every Atlas-ingestable response reference must resolve to a visible response in the same Survey Evidence Export.

This applies to:

- each atom's own `evidence_ref`
- `comparison_set.peer_response_refs[]`
- `supporting_visible_response_refs[].evidence_ref`

Any unresolved or external response reference must either:

- fail validation if it appears under `atlas_ingestable`, or
- be quarantined under `construction_only_excluded.quarantined_response_refs`.

## Validation Command

Run from repo root:

```bash
.venv/bin/python scripts/validate_survey_evidence_export_v0_1.py \
  --export data/survey_simulation/survey_evidence_export/alpha_fast_survey_app_handoff/public_profile_01_A2_Al1_S1_survey_evidence_export.json \
  --report data/survey_simulation/survey_evidence_export/alpha_fast_survey_app_handoff/alpha_fast_survey_evidence_validation_report.md
```

Expected result:

```text
OK: Survey Evidence Export validates at data/survey_simulation/survey_evidence_export/alpha_fast_survey_app_handoff/public_profile_01_A2_Al1_S1_survey_evidence_export.json
```

Validation report:

`data/survey_simulation/survey_evidence_export/alpha_fast_survey_app_handoff/alpha_fast_survey_evidence_validation_report.md`

The current report proves:

- JSON Schema compliance
- no private/simulator/debug leakage
- raw page-construction payload exclusion
- typed music object refs
- append-only ledger semantics
- `evidence_strength_hint` as Survey-side hint, not Atlas confidence
- response-ref closure for Atlas-ingestable refs
- `dont_know_enough` as `familiarity_uncertainty`
- Apple Music as `exposure_prior`, not taste truth

## App Handoff Decision

For trusted Alpha, the app should implement `A2_Al1_S1` as the Fast Survey evidence-capture target and emit Survey Evidence Export v0.1 or a schema-compatible successor.

The app does not need LLM calls for export generation or validation. The export is deterministic and schema-validated.
