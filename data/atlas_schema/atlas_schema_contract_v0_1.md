# Atlas Schema Contract v0.1

Generated: 2026-05-20

Working title:

```text
Waymark Atlas Schema Contract v0.1: User Interpretation Layer
```

## Status

This is a provisional contract for Survey, Mission Generation, Candidate Pool Builder, Mission Review, and Atlas UI integration.

It defines the user-specific interpretation layer above the canonical music graph. It is not a canonical music graph schema and must not be used as a path for canonical graph mutation.

Source inputs:

- `data/product_contracts/graph_staging_contract.md`
- `data/product_contracts/atlas_schema_build_brief.md`
- `data/product_contracts/cross_team_consistency_review.md`
- `data/canonical_graph/policy_hardening/schema_policy_review.md`
- `data/canonical_graph/policy_hardening/canonical_identity_policy.md`
- `data/canonical_graph/policy_hardening/composition_recording_policy.md`

## Core Boundary

```text
Canonical graph = shared music-object substrate
Atlas schema = user-specific interpretation layer
```

Atlas records should reference canonical graph objects when available, but Atlas must also represent objects that are not in the canonical graph.

Supported reference sources:

- `canonical_graph`
- `user_local`
- `external_catalog`
- `unresolved`

Supported music object types:

- `artist`
- `album`
- `song_recording`
- `composition_placeholder`

Survey, Mission Generation, and Mission Review may create or update user-specific Atlas records, Signals, and possible update candidates. They must not create, update, merge, or delete canonical graph entities.

## Non-Negotiable Rules

1. `AtlasNode` represents the thing. It does not own authoritative role truth.
2. `AtlasRoleAssignment` is the authoritative source for role truth.
3. `road` and `lineage` are not ordinary Atlas roles in v0.1.
4. Roads are route/grouping structures.
5. Lineage is represented as edges or network views.
6. Survey writes evidence and provisional candidates, not final Landmark/Region/Frontier/Dead End/Waypoint truth.
7. Mission Generation writes hypotheses and digest-consumable suggestions, not promoted Atlas facts.
8. Mission Review writes Signals and `PossibleAtlasUpdateCandidate` records, not automatic promotions.
9. Candidate Pool Builder consumes `AtlasRoleAssignment` and `AtlasDigestView`, not raw `AtlasNode` role-like summaries.
10. Signals must remain auditable to user-visible survey, mission, note, reaction, tag, skip, playback, import, or review events.

## Machine-Readable Contract

The JSON Schema companion is:

```text
data/atlas_schema/atlas_schema_contract_v0_1.json
```

Example records are under:

```text
data/atlas_schema/examples/
```

The JSON Schema accepts either one Atlas record or an `atlas_example_bundle` containing multiple related records.

## Shared Music Object Reference

Atlas uses a typed `music_object_ref` rather than a single string ID.

Required shape:

```json
{
  "object_type": "artist | album | song_recording | composition_placeholder",
  "ref_source": "canonical_graph | user_local | external_catalog | unresolved",
  "canonical_artist_id": null,
  "canonical_album_id": null,
  "canonical_song_recording_id": null,
  "composition_placeholder_id": null,
  "user_music_object_id": null,
  "external_catalog_refs": {},
  "display_name": "",
  "credited_artist_name": null,
  "credit_context": null,
  "resolution_state": "resolved | needs_resolution | intentionally_user_local",
  "composition_policy_status": "resolved | needs_review | not_applicable | no_review_needed | composition_first_required | split_confirmed",
  "recording_variant_type": null
}
```

Reference rules:

- Canonical artist refs require `canonical_artist_id`.
- Canonical album refs require `canonical_album_id`.
- Canonical song recording refs require `canonical_song_recording_id`.
- User-local refs require `user_music_object_id`.
- External catalog refs require at least one external catalog identifier.
- Unresolved refs must use `resolution_state=needs_resolution`.
- Composition placeholders require `composition_placeholder_id`.

Identity policy:

- Canonical identity is not the same as display credit.
- `display_name`, `credited_artist_name`, and `credit_context` preserve the listener-facing credit context.
- Group and solo entities remain distinct unless a canonical alias policy explicitly links them.
- Collaborations, featured artists, cast recordings, church brands, producer projects, and Various Artists contexts should be preserved through credit context rather than forced into one artist identity.

Composition policy:

- Atlas song refs are recording-first when using `canonical_song_recording_id`.
- Same title is never enough to merge.
- Covers, source versions, live versions, remixes, clean/explicit versions, cast recordings, soundtrack pop recordings, hymns, standards, and traditional songs require explicit variant or composition policy status.
- Use `composition_placeholder` when the user signal points to a work/standard/songbook object that is not yet represented by a canonical composition layer.

## Shared Lifecycle Fields

Every persistent object that can become user state uses distinct lifecycle fields:

```text
status: active | suppressed | archived | provisional
review_state: unreviewed | needs_review | reviewed | rejected
promotion_state: proposed | candidate | promoted | demoted | blocked
```

These fields must not be collapsed into one generic truthiness flag.

## Shared Confidence Fields

Confidence uses a shared shape:

```json
{
  "confidence_score": 0.0,
  "confidence_band": "low | medium | high",
  "confidence_basis": "direct_user_reaction | repeated_user_behavior | explicit_user_note | survey_pattern | mission_review | import_context | editorial_seed | generated_hypothesis | mixed",
  "confidence_summary": "Short explanation."
}
```

`signal_strength` and `interpretation_confidence` remain separate on `Signal`.

Example: a skip is a real event but usually weak taste evidence. A user note may be low-volume but high interpretive value.

## Persistent Objects

### AtlasNode

Represents a thing that Atlas may render or reason about.

Supported `node_type` values:

- `artist`
- `album`
- `song_recording`
- `composition_placeholder`
- `scene`
- `era`
- `genre_lane`
- `taste_feature`
- `user_defined_concept`
- `mission_derived_concept`

An `AtlasNode` may reference a canonical or non-canonical music object through `music_object_ref`, or it may be a non-music concept with `music_object_ref=null`.

`AtlasNode` must not contain authoritative roles. UI role chips must be derived from `AtlasRoleAssignment`.

### AtlasRoleAssignment

Represents how a node functions for a user in a scope.

Authoritative v0.1 role values:

- `landmark`
- `region`
- `frontier`
- `dead_end`
- `waypoint`
- `unknown`
- `signal_only`

Candidate Pool Builder behavior is explicitly separate:

- `anchor`
- `bridge`
- `probe`
- `risky_probe`
- `waypoint`
- `trap`
- `exclude`
- `unknown`

This lets a role such as `frontier` map to a candidate-pool `probe` or `risky_probe` without making the role enum carry routing semantics.

### Road

A route or grouping structure for Atlas and Mission Generation.

A Road may connect landmarks, waypoints, frontiers, and dead ends through node refs and role assignment refs. It is not an Atlas role.

### LineageEdge

An edge/network record over Atlas and canonical-referenced nodes.

Supported edge types include:

- `influence`
- `source_recording`
- `cover_of`
- `adjacent_scene`
- `false_nearby`
- `shared_composition`
- `credit_relation`
- `user_perceived_lineage`
- `generated_hypothesis`

Lineage is an edge view, not a role assignment.

### TasteFeature

Global feature registry record.

Examples:

- `body_force`
- `hooks_under_pressure`
- `album_world`
- `hard_persona_pop`
- `fake_hard`
- `no_blood`
- `waypoint_not_landmark`

Global features are reusable definitions. They are not user-specific truth by themselves.

### UserTasteFeatureState

User-specific state for a global Taste Feature.

Example: `body_force` may be globally defined, while one user has high-confidence affinity for it based on Nirvana, Local H, and Muse-like references.

### Signal

Durable evidence ledger.

Sources:

- `survey`
- `mission`
- `open_road`
- `import`
- `note`
- `review`
- `playback`

Signals must store only observed user-visible tags and notes. Simulator-private hidden reason tags, hidden corpus lookups, and fake-user ground truth must not enter production-facing Signals.

Survey ingestion may also attach optional visible provenance fields:

- `raw_reaction`
- `normalized_signal`
- `shown_unselected_tags`
- `source_context`
- `page_context`
- `apple_exposure_context`
- `integrity_state`
- `debug_provenance`

`apple_exposure_context` is exposure/import/familiarity context only. It is not taste truth and must not be used by itself to promote Atlas roles.

`debug_provenance` may retain QA/replay fields such as ranking scores or page-generator inputs, but these fields are not user-facing Atlas interpretation state.

### UserVocabularyTerm

Stores user language that can later become chips or Atlas copy.

Examples:

- "has body"
- "fake hard"
- "too clean"
- "album world"

### PossibleAtlasUpdateCandidate

Stores possible changes before they become Atlas state.

Survey and Mission Review write candidates here to prevent generated or thin-evidence hypotheses from becoming accidental Atlas truth.

Required safeguards:

- `canonical_graph_mutation_allowed=false`
- `generated_hypothesis_only=true` when produced by Mission Generation or Mission Review hypothesis flow
- Survey/Mission-created candidates may only use `promotion_state=proposed`, `candidate`, or `blocked`
- Mission Review candidates require `review_requirement.required=true`

### AtlasDigestView

Mission Generation should consume digest views rather than raw Atlas tables.

Digest views include:

- relevant Landmarks
- relevant Regions
- relevant Frontiers
- relevant Dead Ends
- relevant Waypoints
- user Taste Feature states
- user vocabulary terms
- anti-overfitting rules
- recent signals
- unresolved questions
- mission-relevant constraints
- suggested candidate roles

Survey-ingestion digest views may include optional compact summaries for WWTSF and first mission generation:

- `candidate_landmarks`
- `candidate_regions`
- `candidate_frontiers`
- `candidate_dead_end_hypotheses`
- `candidate_waypoints`
- `recent_signals`
- `signal_summaries`
- `candidate_pool_behavior_hints`
- `contradictions`
- `user_taste_feature_states`
- `user_taste_feature_summaries`
- `user_vocabulary_terms`
- `starter_atlas_state`
- `mission_generation_inputs`
- `wwtsf_inputs`
- `evidence_audit`
- `future_correction`
- `debug_provenance`

## Write Paths

### Survey Event -> Provisional Atlas State

Survey may create:

- `Signal`
- `UserVocabularyTerm`
- provisional `AtlasNode` when needed
- provisional `AtlasRoleAssignment` candidate when evidence threshold policy allows
- `PossibleAtlasUpdateCandidate`

Survey must not create promoted Landmarks, Regions, Frontiers, Dead Ends, or Waypoints without a later threshold/review policy.

### Mission Generation -> Hypothesis/Digest Use

Mission Generation may consume:

- `AtlasDigestView`
- `AtlasRoleAssignment`
- recent `Signal`
- relevant `UserTasteFeatureState`
- user vocabulary terms

Mission Generation may produce:

- suggested candidate roles in a digest or mission brief
- generated hypothesis Signals only when tied to user-facing mission output
- `PossibleAtlasUpdateCandidate` records if a proposal needs persistence

Mission Generation must not mutate canonical graph objects or promoted Atlas truth.

### Mission Review -> Evidence-Backed Update Candidate

Mission Review may create:

- `Signal`
- candidate role changes
- confidence deltas
- recurrence requirements
- review requirements
- promote/demote/block recommendations

Mission Review must not auto-promote generated hypotheses into Atlas truth.

## Example Files

Required examples:

- `data/atlas_schema/examples/landmark.json`
- `data/atlas_schema/examples/region.json`
- `data/atlas_schema/examples/frontier.json`
- `data/atlas_schema/examples/dead_end.json`
- `data/atlas_schema/examples/waypoint.json`
- `data/atlas_schema/examples/signal.json`
- `data/atlas_schema/examples/taste_feature.json`
- `data/atlas_schema/examples/survey_seeded_update.json`
- `data/atlas_schema/examples/mission_review_possible_update.json`

The examples intentionally include canonical, user-local, external-catalog, unresolved, and composition-placeholder references.

## Acceptance Criteria Mapping

This contract supports:

1. Survey-created starter Atlas state without final verdicts through `Signal`, provisional nodes, and possible update candidates.
2. Mission Generation consumption through `AtlasDigestView`.
3. Candidate Pool Builder queries through `AtlasRoleAssignment.candidate_pool_behavior`.
4. Mission Review evidence capture through `Signal` and `PossibleAtlasUpdateCandidate`.
5. Atlas UI rendering for Landmark, Region, Frontier, Dead End, and Waypoint cards from node plus role assignment bundles.
6. Evidence auditability through signal IDs on stateful records and update candidates.
