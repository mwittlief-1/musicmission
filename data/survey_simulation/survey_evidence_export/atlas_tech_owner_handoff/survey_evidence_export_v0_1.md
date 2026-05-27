# Survey Evidence Export v0.1

## Purpose

Survey Evidence Export v0.1 is the normalized append-only evidence ledger from Survey to Atlas. It exports visible survey evidence atoms, not raw page construction payloads.

Atlas should ingest this export when it needs to seed or update taste evidence from completed survey responses. It should not ingest Survey Builder debug state, simulator-private fake-user truth, LLM Profile Writer prose, or ranking internals.

## Contract Shape

The export is a JSON document with five major areas:

1. `source`
   Identifies the public profile, Apple payload, survey run, page-count config, source packet fingerprint, and source public packet hash.

2. `private_data_boundary`
   Declares that simulator-private data, Profile Writer prose, raw page-construction payloads, raw ranking scores, and graph meanings unavailable to the visible packet are excluded.

3. `ledger_semantics`
   Declares append-only behavior. Survey must not rewrite existing evidence atoms; corrections or replacements should be appended as later evidence or correction atoms.

4. `atlas_ingestable`
   Contains only evidence atoms and a response reference index. This is the only section Atlas may consume.

5. `construction_only_excluded`
   Records non-ingestable exclusions and quarantined unresolved response refs. Atlas must ignore this section.

## Evidence Atom

Each `atlas_ingestable.evidence_atoms[]` item represents one visible survey response:

- typed `music_object_ref`
- raw reaction
- normalized reaction operation
- `evidence_strength_hint`
- selected tags
- shown-but-unselected tags
- optional note
- page intent
- comparison set
- candidate basis
- graph refs
- Apple exposure prior
- provenance
- timestamps

The atom intentionally does not include:

- tile position
- tile ID
- page layout mechanics
- randomization seeds
- generation prompts
- adaptive target mixes
- raw candidate ranking scores
- suppression/debug warnings
- hidden fake-profile truth
- hidden corpus reactions
- simulator lookup state
- Profile Writer prose
- graph meanings unavailable to the visible packet

## Append-Only Ledger Semantics

Survey Evidence Export is append-only. Evidence atoms are immutable once emitted. If Survey later needs to correct, supersede, or retract evidence, it should append a new correction/superseding atom rather than rewriting the original atom.

Atlas may derive current state from the full ledger, but the export itself is not a mutable state snapshot.

## Evidence Strength Hint

`evidence_strength_hint` is a Survey-side evidence-basis hint. It is not final Atlas confidence.

The hint summarizes the evidence basis visible to Survey, using reaction operation and visible page context only. Atlas must calculate final confidence from its own model, accumulated evidence, conflict resolution, object specificity rules, and historical ledger state.

Required guardrails:

- `evidence_strength_hint.source` is always `survey`.
- `evidence_strength_hint.is_final_atlas_confidence` is always `false`.
- The hint must not contain hidden fake-profile data, hidden corpus data, simulator lookup state, raw scores, or final Atlas promotion decisions.

## Reaction Normalization

Survey reactions are normalized before Atlas ingestion:

| Raw reaction | Normalized operation | Atlas interpretation |
|---|---|---|
| `love` | `positive_high` | Strong positive evidence, scoped to the smallest justified object. |
| `like` | `positive_medium` | Positive evidence, usually not enough for a broad landmark by itself. |
| `ok` | `waypoint_context` | Useful/contextual/waypoint evidence, not landmark evidence. |
| `dont_like` | `negative_scope_carefully` | Negative evidence with careful scope control. |
| `dont_know_enough` | `familiarity_uncertainty` | Familiarity uncertainty, not negative taste evidence. |

`dont_know_enough` must never be transformed into negative taste evidence by this export.

## Apple Exposure Prior

Apple Music fields are exported under `apple_exposure_prior`. Their interpretation is always `exposure_prior`, and `taste_truth` is always `false`.

Allowed Apple exposure dimensions:

- `exact_signal_weight`
- `exposure_score`
- `recency_score`
- `repetition_score`
- `library_commitment_score`
- `favorite_or_rating_score`
- `playlist_context_score`
- `album_completion_hint`
- `artist_depth_hint`

The export intentionally excludes taste-like Apple conclusions such as broad preference truth. Apple can say what a user was likely exposed to; it does not prove what the user loves.

## Graph References

Graph context is exported only as visible refs already present in the public packet:

- `family_numbers`
- `archetype_ids`
- `roles`
- `best_recognition_tier`
- `best_survey_tier`

The export does not invent or attach graph family/archetype meanings unless those meanings are present in the visible source packet.

## Response Reference Integrity

Hard gate:

Every Atlas-ingestable response reference must resolve to a visible response in the same Survey Evidence Export.

This applies to:

- `supporting_visible_response_refs[].evidence_ref`
- `comparison_set.peer_response_refs[]`
- each atom’s own `evidence_ref`

Any unresolved or external response ref must either:

- fail validation, if it appears inside `atlas_ingestable`, or
- be moved to `construction_only_excluded.quarantined_response_refs`, which Atlas must not ingest.

## Sample

The v0.1 fixture is:

`samples/public_profile_01_A3_Al1_S2_survey_evidence_export.json`

It is generated from the public blind packet:

`data/survey_simulation/llm_profile_review/api_pilot_3x3/public_packets/waymark_survey_output_packet_public_profile_01_A3_Al1_S2.json`

The sample contains 72 visible response atoms:

- 3 artist pages
- 1 album page
- 2 song pages

## Validation

Run:

```bash
.venv/bin/python scripts/validate_survey_evidence_export_v0_1.py
```

The validator checks:

- JSON Schema compliance
- no forbidden private/simulator/Profile Writer fields
- no raw page construction payload fields
- no raw ranking score objects
- typed music object refs
- `dont_know_enough` maps to `familiarity_uncertainty`
- Apple priors remain `exposure_prior` with `taste_truth: false`
- all Atlas-ingestable response refs resolve inside the same export
- unresolved refs are quarantined outside Atlas ingestion
