# AtlasDelta v0.1

## Purpose

`AtlasDelta` is the canonical Waymark object for explaining what changed between one Atlas state and the next.

It answers:

> What did Waymark learn from new Signals and PossibleAtlasUpdateCandidates?

`AtlasDelta` is not Atlas truth by itself. It is a deterministic summary derived from:

- `Signal`
- `AtlasRoleAssignment`
- `PossibleAtlasUpdateCandidate`
- prior `AtlasDigestView`
- updated `AtlasDigestView`

LLM copy rendering may later consume `AtlasDelta`, but the delta object itself should be deterministic first.

## Supported Product Surfaces

`AtlasDelta` should support:

- Survey completion summary
- Mission completion "What Waymark Learned"
- Today next-route explanation
- Atlas Home recent learning
- second-batch mission adaptation
- confidence and scope visualization

## Required Fields

- `atlas_delta_id`
- `user_id`
- `fixture_profile_id`
- `source_event_type`: `survey | mission_batch | open_road | review`
- `source_event_id`
- `prior_digest_ref`
- `updated_digest_ref`
- `strengthened_roles`
- `weakened_roles`
- `new_candidate_landmarks`
- `new_candidate_frontiers`
- `new_dead_end_hypotheses`
- `new_waypoints`
- `contradictions`
- `unresolved_questions`
- `paused_paths`
- `promotion_recommendations`
- `promotion_blockers`
- `demotion_recommendations`
- `confidence_changes`
- `scope_changes`
- `next_mission_implications`
- `user_facing_summary_inputs`

`user_id` may be `null` for fixtures when `fixture_profile_id` is present. Production records should use `user_id`.

## Hard Rules

1. `AtlasDelta` is not promoted Atlas truth.
2. `AtlasDelta` must not mutate the canonical graph.
3. `AtlasDelta` must preserve evidence refs back to Signals or update candidates.
4. `AtlasDelta` summarizes changes derived from Signals, AtlasRoleAssignments, and PossibleAtlasUpdateCandidates.
5. Promotion and demotion recommendations are recommendations only; they do not change Atlas truth unless a separate review/promotion policy writes the actual Atlas records.
6. User-facing summary inputs are source material, not final WWTSF copy.

## Field Semantics

### Strengthened and Weakened Roles

`strengthened_roles` and `weakened_roles` describe confidence movement around provisional roles.

They should include:

- target ref
- role
- confidence delta
- promotion state
- review requirement
- evidence refs
- `atlas_truth_changed=false`

### New Candidate Buckets

The `new_candidate_*` arrays summarize newly created or newly reinforced candidate role hypotheses.

These are not promoted Landmarks, Frontiers, Dead Ends, or Waypoints. They remain candidates until an explicit promotion policy or human review acts.

### Contradictions

Contradictions preserve positive and negative evidence refs separately and include a scope warning. A contradiction should usually create a review/test recommendation, not a broad claim.

### Paused Paths

`paused_paths` explains routes that should not be advanced yet because evidence is skipped, flat, negative, signal-only, contradictory, or too thin.

### Promotion Blockers

`promotion_blockers` makes uncertainty visible. Common blockers:

- recurrence required
- human review required
- contradiction unresolved
- object scope too narrow
- family/archetype labels unavailable

### Confidence and Scope Changes

`confidence_changes` powers confidence visualization.

`scope_changes` powers object-scope visualization. It should distinguish:

- artist-level
- album-level
- recording-level
- mission-item scope
- unresolved/search-required scope

### Next Mission Implications

`next_mission_implications` tells Mission Generation what to do next without creating mission objects.

Examples:

- probe strengthened Frontier candidates
- use confirmed Waypoints as bridges
- test Dead End hypotheses cautiously
- resolve unresolved questions

### User-Facing Summary Inputs

`user_facing_summary_inputs` gives WWTSF or Atlas Home rendering useful source bullets.

It must include `not_final_copy=true`.

## Example Fixtures

- `data/atlas_schema/examples/atlas_delta_closed_loop_profile_01.json`
- `data/atlas_schema/examples/atlas_delta_closed_loop_profile_05.json`
- `data/atlas_schema/examples/atlas_delta_closed_loop_profile_06.json`
