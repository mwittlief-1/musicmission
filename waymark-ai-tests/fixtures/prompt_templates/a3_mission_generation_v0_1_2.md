# Cartenza A3 Mission Generation v0.1.2

Profile: {{PROFILE_ID}}
Scenario id: {{SCENARIO_ID}}
Mission archetype: {{MISSION_ARCHETYPE}}

Generate one Cartenza mission object using the existing approved mission schema.

This mission consumes Atlas substrate and WWTSF substrate as context. WWTSF is not final user copy; use it as structured source material only.

Use only the bounded context packet below:

- AtlasDigestView
- node interpretation smoke output
- WWTSF substrate
- selected evidence refs already present in those artifacts
- anti-overfitting rules

Do not use:

- raw A3 survey payloads
- Profile Writer outputs
- hidden fake-profile truth
- simulator-private corpus reactions
- canonical graph mutation instructions
- promoted Atlas truth not present in the substrate

Mission requirements:

- A mission is not a playlist.
- Preserve uncertainty and provisional state.
- Include hypothesis, why_now, route, route-item expected signals, reaction-specific feedback chips, review config, completion criteria, and possible Atlas update candidates.
- Use stable primary reaction operations: `love`, `like`, `keep`, `not_for_me`.
- Do not promote Atlas truth.
- Do not mutate canonical graph.
- Do not treat WWTSF bullets as final truth.
- `possible_atlas_update_candidates` must be mission-scoped and conditional on future primary reactions.
- Risky, trap, Dead End, Frontier, unknown, and contradiction items should default to review-needed.
- If you use known objects from the substrate, keep object scope clear: artist, album, song, cluster, or unresolved lane.
- MusicKit/search hints should be plausible placeholders. Do not claim resolution happened.

Scenario objective:

```text
{{SCENARIO_OBJECTIVE}}
```

Scenario constraints:

```json
{{SCENARIO_CONSTRAINTS_JSON}}
```

Bounded context packet:

```json
{{CONTEXT_PACKET_JSON}}
```

Output schema:

```json
{{OUTPUT_SCHEMA_JSON}}
```
