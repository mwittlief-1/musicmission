# Waymark Mission Generator Rich v0.1

Source prompt: {{SOURCE_PROMPT}}

Request id: {{REQUEST_ID}}
Context mode: {{CONTEXT_MODE}}

You are producing a Waymark mission-generation test output, not a final backend response and not a playlist.

Mission design target:

The mission should feel like: "I know what you mean. Let's try this route. I think this might hit because of the way you react to X, but I am not sure yet, so let's test it."

Use the bounded context packet as controlling context. Do not rely on hidden memory or unprovided facts. If context is thin, preserve more uncertainty instead of filling gaps with confident genre logic.

Design steps:

1. Identify the mission archetype requested.
2. State a personalized hypothesis that can be proved wrong.
3. Name the major risk model: false-nearby traps, Dead Ends, Waypoint inflation, one-object exceptions, resolver uncertainty, or overgeneralization.
4. Build an ordered route where every item has a job:
   - anchor;
   - bridge;
   - probe;
   - trap or Dead End check;
   - checkpoint;
   - cooldown.
5. For every item, explain what a positive reaction would mean and what a negative reaction would mean.
6. Generate feedback chips for all four primary reaction operations:
   - `love`;
   - `like`;
   - `keep`;
   - `not_for_me`.
7. For trap or Dead End items, use special positive-reaction semantics:
   - `love` should mean unexpected exception, cultural furniture with surprising force, or reassess the dead end.
   - `like` should mean bounded exception, cultural furniture, or needs recurrence.
   - Do not interpret every positive trap response as a disguised negative.
8. Map chips to canonical feature ids when the feature registry is available. If no exact feature exists, use an empty string for `mapped_canonical_feature_id` and explain the meaning in `signal_meaning`.
9. Separate completion semantics:
   - primary reactions are required evidence;
   - chip selections are explanatory tags and do not substitute for a primary reaction.
10. Add review fields that make it easy to inspect failure modes before any app import or Atlas update.
11. Use `possible_atlas_update_candidates`, and make each possible update conditional on future reaction operations, recurrence, and human review. Set `review_required` to true. Any possible update above `Signal only` needs at least 2 future occurrences.

Hard guardrails:

- Muse does not imply Tool, A Perfect Circle, or generic prog-metal seriousness.
- Type O Negative does not imply broad gothic metal.
- LCD Soundsystem's This Is Happening does not imply generic dance-punk.
- The Decemberists do not imply generic indie-folk.
- Taylor Swift does not imply generic pop appetite. The fit is architecture, persona, bite, and hard pop construction.
- Jimmy Eat World's Bleed American does not imply broad emo/pop-punk approval.
- QOTSA and Kyuss are Waypoints until stronger evidence says otherwise.
- Current rock must avoid fake-hard, scene-posture, and post-grunge slop traps.
- Risky, trap, Dead End, and unknown frontier items should default to `review_state.needs_human_review = true`.
- A positive reaction to a trap may reveal an unexpected exception or cultural furniture. It is not automatically a failure of the listener or the mission.

Return only JSON conforming to the schema. Do not include Markdown outside the JSON.

Bounded context packet:

```json
{{CONTEXT_PACKET_JSON}}
```

Output schema:

```json
{{MISSION_OUTPUT_SCHEMA_JSON}}
```
