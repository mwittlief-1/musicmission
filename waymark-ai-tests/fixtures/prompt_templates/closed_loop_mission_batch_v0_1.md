# Waymark Closed-Loop Mission Batch Generator v0.1

Profile: {{PROFILE_ID}}
Batch stage: {{BATCH_STAGE}}

Generate exactly six Waymark mission objects as a coherent portfolio.

Use the existing mission object contract for each mission. A Mission is not a playlist. It is a structured listening route designed to gather useful Atlas evidence.

Use only the bounded context packet below:

- AtlasDigestView / updated AtlasDigestView read model
- AtlasDelta entries supplied for adaptive second batch
- node interpretation smoke output
- WWTSF substrate
- Atlas update summaries supplied in the packet
- prior mission feedback summaries supplied in the packet
- selected evidence refs already present in those artifacts
- anti-overfitting rules

Do not use:

- raw A3 survey payloads
- Profile Writer outputs
- hidden fake-profile truth
- simulator-private corpus reactions
- hidden evaluator traces
- canonical graph mutation instructions
- promoted Atlas truth not present in the packet

Portfolio requirement:

Generate one mission for each functional slot:

1. `safe_anchor`
2. `nearby_road`
3. `frontier`
4. `dead_end_or_contradiction_check`
5. `waypoint_useful_not_canon`
6. `wildcard_delight`

The six missions must be meaningfully different. Do not create six variants of the same route.

Route item requirement:

Use 2-3 route items per mission for this closed-loop simulation. Prefer concise but specific field values so the full six-mission portfolio fits in one structured response.

Every route item must be either:

- a concrete searchable song or album with real `artist`, `title`, `album` when known, year when known, and a plausible Apple Music search query;
- or an explicit unresolved candidate-search slot.

If unresolved, stay schema-compatible by using `item_type = "track"`, but make the status explicit:

- `display_metadata.title` begins with `candidate_search_required:`
- `music_kit_search_hint.search_query` begins with `candidate_search_required:`
- `music_kit_search_hint.resolution_status_placeholder = "unresolved"`
- `review_state.needs_human_review = true`
- `review_state.uncertainty_flags` includes `candidate_search_required`

Do not present pseudo-items as playable tracks. Bad example: `Disney-associated theatrical/film song probe`. Good example: `candidate_search_required: Disney theatrical / film song frontier probe`.

Mission requirements:

- Include title, archetype, brief, hypothesis, why_now, route, expected signal per route item, feedback chips, risk model, completion criteria, review config, completion summary inputs, and possible Atlas update candidates.
- Use stable feedback chip reaction operations: `love`, `like`, `keep`, `not_for_me`.
- `possible_atlas_update_candidates` must be mission-scoped and conditional on future reactions.
- Risky, trap, Dead End, Frontier, unknown, and contradiction items should default to review-needed.
- Preserve uncertainty and provisional state.
- Do not promote Atlas truth.
- Do not mutate canonical graph.

For second-batch generation:

- Do not generate a mission unless it can point to at least one `source_atlas_delta_refs` value from `atlas_delta_after_batch_1.deltas[*].delta_id`.
- The mission must make the learning visible: “Waymark noticed X, Atlas changed in Y way, so this mission now tests Z.”
- For every mission, copy `source_atlas_delta_refs`, `source_signal_refs`, and `source_update_candidate_refs` from `adaptive_second_batch_reference_table.rows`.
- `source_signal_refs` must use only `signal:mission:...` refs from the referenced AtlasDelta rows. Do not use `signal:survey:...` refs.
- `source_update_candidate_refs` must use only `possible_update:signal:mission:...` refs from the referenced AtlasDelta rows.
- Every mission must choose exactly one `adaptation_action`: `deepen`, `pivot`, `retire_pause`, `contradiction_check`, or `dead_end_confirmation`.
- When a referenced AtlasDelta has `recommended_adaptation_action`, the mission's `adaptation_action` should usually match it. Do not silently convert a `retire_pause` delta into a `deepen`, `pivot`, or generic contradiction mission.
- If the reference table includes a `retire_pause` delta, at least one second-batch mission must use `adaptation_action = "retire_pause"` and say what Waymark is pausing, retiring, narrowing, or no longer spending effort on.
- Every mission must explain `what_batch_1_taught`, `what_changed_since_prior_batch`, and `what_this_mission_is_not_doing_anymore`.
- Every mission must define hit/miss/no-signal semantics through `success_condition`, `failure_condition`, `no_signal_interpretation`, and `expected_next_atlas_update`.
- At least two missions must visibly adapt because of batch-one learning.
- Include at least one mission that deepens a stronger path when deltas support it.
- Include at least one mission that pauses, retires, narrows, or deprioritizes a weak/no-signal path when deltas support it.
- Include a contradiction or dead-end confirmation mission when deltas indicate negative, conflict, trap, or false-nearby evidence.
- Preserve uncertainty where evidence remains thin.

Resolution-quality rule for second-batch generation:

- No second-batch mission should include more than one unresolved/candidate-search placeholder unless `mission_type = "resolution_search_calibration"`.
- If route items cannot be resolved cleanly, substitute a resolved control, downgrade the mission to search/discovery setup, or mark it unsuitable for closed-loop learning.
- Set `resolution_quality_status` and `closed_loop_learning_suitability` honestly. Do not mark a mission `suitable` if `resolution_quality_status = "too_many_placeholders"`.

Adaptive contract:

```json
{{ADAPTIVE_CONTRACT_JSON}}
```

Mission portfolio:

```json
{{MISSION_PORTFOLIO_JSON}}
```

Bounded context packet:

```json
{{CONTEXT_PACKET_JSON}}
```
