# Cartenza WWTSF Substrate Generator v0.1.2

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
