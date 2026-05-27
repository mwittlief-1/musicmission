# Waymark Mission Generator Candidate-Constrained v0.1

Source prompt: {{SOURCE_PROMPT}}

Request id: {{REQUEST_ID}}
Context mode: {{CONTEXT_MODE}}

Generate one Waymark mission object using the bounded context packet below.

Candidate constraint:

- If `candidate_pool.candidates` is non-empty, every route item must come from `candidate_pool.candidates`.
- Copy the selected fixture row's `candidate_id` exactly into the route item `candidate_id`.
- Artist/title similarity is not enough. A route item without an exact `candidate_id` from `candidate_pool.candidates` is invalid even if the song appears in the digest, Survey evidence, or user vocabulary.
- Digest/Atlas/strong-region examples are context only. They are not route-item sources unless the exact object also appears in `candidate_pool.candidates`.
- If no valid pool candidate fits the requested route role, do not invent a substitute. Add a blocked/retry explanation in `risk_model.uncertainty_notes` and keep `review_config.ready_for_app_import = false`.
- Do not invent artists, songs, albums, years, countries, or MusicKit search hints when a candidate pool is present.
- You may exclude trap candidates.
- You may include trap candidates only when the route item is explicitly a boundary or Dead End check, with `selection_role` set to `trap` and `risk_class` set to `trap` or `dead_end_check`.
- Trap items are not forced misses. If the user chooses `love` or `like` on a trap, the chips must mean unexpected exception, cultural furniture, bounded exception, or reassess dead end.
- Trap positive chips must not say or imply that a positive response still proves a negative interpretation.
- If the candidate pool is empty, state the lack of candidates in `risk_model.uncertainty_notes` and generate the best bounded mission possible.
- Respect `mission_request.expected_route_item_count` when present. Stay within that min/max range unless the candidate pool is too small, and explain any exception in `risk_model.uncertainty_notes`.

Mission requirements:

- A mission is not a playlist. Every item must serve the route.
- Use stable reaction operations: `love`, `like`, `keep`, `not_for_me`.
- Every route item must have a unique `item_id`, unique `candidate_id`, and unique artist/title/type display identity within the mission.
- If `prompt_context.already_selected_route_item_ids`, `prompt_context.already_selected_candidate_ids`, `prompt_context.already_selected_display_keys`, `prompt_context.excluded_route_item_ids`, or `prompt_context.excluded_candidate_ids` are supplied, do not select those objects again. If the remaining pool cannot satisfy the route, output a blocked/retry explanation instead of repeating.
- Each item must include all four feedback chip sets, each with at least two chips.
- Feedback chips must use user vocabulary naturally when appropriate: body, bite, blood, architecture, album-world, false-nearby, no slop, Waypoint not Landmark.
- Preserve uncertainty. Do not claim Apple Music resolution has happened.
- Completion must count primary reactions separately from chip selections. Chip selections refine signal meaning; they do not replace primary reactions.
- Use `possible_atlas_update_candidates` cautiously and keep most fresh evidence as `Signal only` or `Frontier` until recurrence.
- Output `possible_atlas_update_candidates` must be mission-scoped proposals tied to selected route items or the route-level evidence this mission would collect.
- Do not copy, re-emit, or rename existing `atlas_digest.possible_atlas_update_candidates` from the context packet. Treat those context candidates as read-only Atlas state, not as mission output.
- Prefer selected route item `candidate_id` values for mission output update `candidate_id` fields when a candidate pool is present.
- If an output update uses a selected route item `candidate_id`, its rationale, role, and trigger conditions must refer to that same route item, not another selected song.
- Do not propose Dead End updates for non-trap/non-dead-end route items.
- Every possible Atlas update candidate must include `review_required: true` and trigger conditions tied to future primary reactions and human review.
- Any possible Atlas role above `Signal only` must require at least 2 future occurrences.
- Risky, trap, Dead End, and unknown frontier items should default to `review_state.needs_human_review = true`.
- Trusted Alpha readiness distinction: item-level review flags are not the same thing as app-import failure.
- Do not set `review_config.ready_for_app_import = false` solely because a route-ready risky, frontier, trap, Dead End, Waypoint, or contradiction item correctly carries review flags.
- Set `review_config.ready_for_app_import = false` only for hard blockers: schema uncertainty, non-candidate route items, pseudo-playable placeholders, unresolved search slots, unsafe/quarantined candidates, hidden/private source leakage, or Atlas/canonical overclaiming.
- If a mission is playable and app-import-safe but carries review flags, keep those flags explicit in `review_config.review_focus`, item `review_state`, and `risk_model.uncertainty_notes`.

Scoring hazards to avoid:

- Generic playlist language.
- Generic chips like "catchy", "good", "boring", or "not for me" without signal meaning.
- Ignoring known Dead Ends.
- Treating Waypoints as Landmarks.
- Treating one-object exceptions as genre appetites.
- Missing the user's vocabulary and taste logic.

Return only JSON conforming to the schema.

Bounded context packet:

```json
{{CONTEXT_PACKET_JSON}}
```

Output schema:

```json
{{MISSION_OUTPUT_SCHEMA_JSON}}
```
