# Cartenza WWTSF Guarded Substrate Generator v0.1.5

Profile: {{PROFILE_ID}}

Generate one WWTSF substrate object.

WWTSF means "What We Think So Far."

This is not final app copy. It is structured source material for downstream user-facing copy and mission generation.

Use only the bounded context packet below:

- AtlasDigestView
- node interpretation smoke output
- selected signal/evidence refs already present in those artifacts
- anti-overfitting rules
- role assignment policy notes
- deterministic coverage obligations

Do not use or imply access to:

- raw A3 survey payloads
- Profile Writer outputs
- hidden fake-profile truth
- simulator-private corpus reactions
- canonical graph mutation instructions
- promoted Atlas truth not present in the substrate

Product rules:

- Survey evidence is evidence, not verdict.
- Apple exposure is familiarity/import context, not taste truth.
- Unknown / dont_know_enough is not negative evidence.
- One click does not create a permanent Landmark.
- A loved isolated node may be a Frontier, not a Landmark.
- A loved dense node may reinforce a Landmark or Region.
- A loved node in a mixed/negative neighborhood may be a bridge, contradiction, or one-object exception.
- Dead Ends are hypotheses unless strongly supported.
- Waypoints are useful/contextual, not canon.
- All claims need scope and confidence.

Coverage obligation rules:

- Preserve every required functional category in `coverage_obligations`.
- Required candidate regions must appear in `candidate_regions`, unless impossible from the bounded evidence.
- Required frontier labels must appear in `candidate_frontiers` or a clearly frontier-oriented first mission hint.
- Required waypoint labels must appear in `waypoint_notes` or a clearly waypoint/bridge-oriented first mission hint.
- Required contradiction labels must appear in `contradictions_or_review_needs`.
- Required mission hint types must be represented by `first_mission_input_hints`.
- The number of first mission hints must be at least `minimum_hint_count`.
- If a required category cannot be emitted from the bounded evidence, do not silently drop it. Add an explicit `omitted_with_reason:<category>:<label>` entry in the closest existing schema field:
  - use `contradictions_or_review_needs` with `issue_type = "other"` for omitted category/object coverage;
  - use `first_mission_input_hints` with `prompt_seed` beginning `omitted_with_reason:<hint_type>` for omitted hint coverage.
- Omission entries are review-needed and must explain the evidence limitation. They are not product passes, but they are better than silent drops.

Output rules:

- Set `not_final_user_copy = true`.
- Set all exclusion confirmations to false as required by the schema.
- Do not create final mission objects.
- Do not generate polished final user-facing prose.
- Do not promote Atlas roles.
- Do not mutate canonical graph.
- Do not collapse contradictions into broad claims.
- Do not infer family/archetype labels if unavailable.
- Keep summaries concrete and evidence-scoped.
- Use evidence refs that point to source digest, node interpretation, signal ids, possible update candidates, or policy notes already present in the bounded context packet.

Bounded context packet:

```json
{{CONTEXT_PACKET_JSON}}
```

Output schema:

```json
{{OUTPUT_SCHEMA_JSON}}
```
