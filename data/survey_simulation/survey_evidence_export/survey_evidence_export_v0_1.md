# Survey Evidence Export v0.1

## Purpose

Survey Evidence Export v0.1 is the normalized append-only evidence ledger from Survey to Atlas. It exports visible survey evidence atoms, not raw page construction payloads.

Atlas should ingest this export when it needs to seed or update taste evidence from completed survey responses. It should not ingest Survey Builder debug state, simulator-private fake-user truth, LLM Profile Writer prose, or ranking internals.

The proven Alpha flow is:

```text
Survey Evidence Export
-> Signal
-> AtlasNode
-> provisional AtlasRoleAssignment
-> PossibleAtlasUpdateCandidate
-> AtlasDigestView
```

Survey Evidence Export is the Survey side of that flow only. Atlas owns Signal creation, AtlasNode persistence, provisional role assignment policy, possible update candidate creation, and digest generation.

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

`evidence_strength_hint` is a Survey-side evidence-basis hint. It is not final Atlas confidence. During Atlas ingestion it may be preserved only as Survey metadata on the resulting Signal or audit record; it must not become `Signal.confidence`, `AtlasNode.confidence`, `AtlasRoleAssignment.confidence`, or a promotion threshold by itself.

The hint summarizes the evidence basis visible to Survey, using reaction operation and visible page context only. Atlas must calculate final confidence from its own model, accumulated evidence, conflict resolution, object specificity rules, and historical ledger state.

Required guardrails:

- `evidence_strength_hint.source` is always `survey`.
- `evidence_strength_hint.is_final_atlas_confidence` is always `false`.
- The hint must not contain hidden fake-profile data, hidden corpus data, simulator lookup state, raw scores, or final Atlas promotion decisions.

## Tag Semantics

Survey exports two tag lanes with different evidence meaning:

| Export field | Required semantics | Atlas treatment |
|---|---|---|
| `tags.selected` | `visible_signal_evidence` | Visible user-selected Signal evidence. |
| `tags.shown_but_unselected` | `weak_non_selected_context` | Weak context that a tag was shown but not selected. |

Selected tags are part of the visible Signal evidence. Shown-but-unselected tags are not negative tag evidence and must not be treated as user-selected claims. A tag cannot appear in both lanes for the same evidence atom.

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

## Quarantine Reason Taxonomy

Quarantined responses are construction-only diagnostics. They explain why a response did not become an Atlas-ingestable evidence atom. Atlas must ignore these rows for ingestion, but PM/Core/Release QA can use them to reconstruct live smoke failures.

Allowed quarantine reasons:

| Reason | Meaning |
|---|---|
| `missing_displayed_page` | The response or supporting ref points to a page that is not present in the displayed-page record for this export. |
| `missing_tile_or_ref` | The page exists, but the response item, tile ref, evidence ref, or response ID does not resolve to a visible tile/ref. |
| `invalid_response_state` | The response state is outside the five-state Survey enum. |
| `duplicate_response` | Multiple response records claim the same Atlas-ingestable response ID or visible evidence ref. |
| `schema_mismatch` | The response payload shape cannot be interpreted under Survey Evidence Export v0.1. |
| `non_visible_construction_data` | The item is construction/debug state rather than a visible user-facing response. |
| `apple_only_unmatched_object` | The object came from Apple context but did not resolve to a visible Survey tile/ref. |

Validation reports must include:

- total responses reviewed
- Atlas-ingestable response count
- quarantined response count
- quarantine reason counts

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
- quarantined response refs use the live-smoke reason taxonomy and are reported by reason count
