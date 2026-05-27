# Waymark WWTSF Targeted Repair v0.1.5

Profile: {{PROFILE_ID}}

Repair one existing WWTSF substrate object.

This is a targeted repair pass, not a full rewrite. Preserve the useful content from the original mini output, but amend it so deterministic guardrails pass.

Use only the bounded repair packet below:

- original mini WWTSF output;
- failed deterministic guardrail report;
- missing coverage obligations;
- relevant source snippets and evidence refs from AtlasDigestView/node interpretation;
- anti-overfitting and exclusion rules included in the packet;
- the same strict WWTSF output schema.

Do not use or imply access to:

- raw A3 survey payloads;
- Profile Writer outputs;
- hidden fake-profile truth;
- simulator-private corpus reactions;
- canonical graph mutation instructions;
- promoted Atlas truth not present in the repair packet.

Repair rules:

- Return one complete WWTSF substrate object conforming to the schema.
- Do not return a patch or explanation outside the JSON object.
- Preserve `not_final_user_copy = true`.
- Preserve all exclusion confirmations as false.
- Add missing required candidate regions to `candidate_regions` when supported by the source snippets.
- Add missing required frontier labels to `candidate_frontiers` or first mission hints.
- Add missing required waypoint labels to `waypoint_notes` or first mission hints.
- Add missing required contradiction labels to `contradictions_or_review_needs`.
- Add missing required mission hint types to `first_mission_input_hints`.
- If a required obligation cannot be emitted from the bounded evidence, do not silently drop it. Add an explicit `omitted_with_reason:<category>:<label>` entry in the closest existing schema field.
- Omission entries must be evidence-scoped and review-needed. They do not promote Atlas truth.

Bounded repair packet:

```json
{{REPAIR_PACKET_JSON}}
```

Output schema:

```json
{{OUTPUT_SCHEMA_JSON}}
```
