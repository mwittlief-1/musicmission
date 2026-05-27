# Waymark Mission Generator Compact v0.1

Source prompt: {{SOURCE_PROMPT}}

Request id: {{REQUEST_ID}}
Context mode: {{CONTEXT_MODE}}

Generate one Waymark mission object. A mission is not a playlist. It is a structured listening route that tests a taste hypothesis and collects evidence.

Use only the bounded context packet below. Do not assume hidden project memory.

Core requirements:

- Return only valid JSON conforming to the supplied schema.
- Use stable primary reaction operations: `love`, `like`, `keep`, `not_for_me`.
- Every route item needs a route function, item hypothesis, expected positive signal, expected negative signal, expected features, MusicKit search hint, review state, and all four feedback chip sets.
- Each feedback chip must be tailored to the user, song, mission, expected signal, and reaction operation.
- Trap and Dead End items need special positive-reaction semantics: `love` or `like` should mean unexpected exception, cultural furniture, or reassess dead end. Do not force positive trap responses into negative interpretation.
- Completion must count primary reactions separately from chip selections.
- Use `possible_atlas_update_candidates`, not immediate Atlas updates. Every possible update must have `review_required: true` and trigger conditions tied to future primary reactions and review.
- Any possible update above `Signal only` needs recurrence: at least 2 future occurrences.
- Risky, trap, Dead End, and unknown frontier items should default to `review_state.needs_human_review = true`.
- Preserve uncertainty. Do not hallucinate catalog resolution. Use unresolved placeholders.
- Do not promote Waypoints to Landmarks.
- Do not turn one-object exceptions into broad genre claims.
- Avoid generic playlist output, generic feedback chips, and broad "sounds like" recommendations.

Bounded context packet:

```json
{{CONTEXT_PACKET_JSON}}
```

Output schema:

```json
{{MISSION_OUTPUT_SCHEMA_JSON}}
```
