# Affinity Retag Pilot v0.3 — Sparse Production Simulation Instructions

## Status

Use the v0.2.2 controlled ontology. This pass is **not runtime-ready** and **does not authorize graph-wide tagging**.

## Core rules

1. Use canonical tags only. Any alias in output fails QA.
2. Default target: **5–8 tags per song**.
3. 9–10 tags are allowed only for genuinely multi-context, bridge-heavy, or routing-sensitive songs.
4. Empty dimensions are allowed.
5. Do not fill every dimension just because the schema has every dimension.
6. Do not apply family-wide blanket tags.
7. Do not duplicate genre, family, scene, era, or recognition metadata as affinity tags.
8. `safe_gateway` is not a default; use only when the song actively helps sequence into a route.
9. `context_dependent` is not a default; use only when social/use-case context materially changes routing.
10. Keep `social_context` and `routing_caution` cleanly separated.

## Review fields

Use these review fields:

```json
{
  "identity_review_needed": false,
  "tag_review_needed": false,
  "selection_bucket_review_needed": false,
  "review_reason_codes": []
}
```

Allowed `review_reason_codes`:

```text
recording_identity_unclear
tag_definition_ambiguous
missing_tag_candidate
social_context_unclear
routing_caution_unclear
over_tagged
under_tagged
```

## Acceptance gate

- Average tags per song: 6–8.
- No alias leakage.
- No non-canonical tags.
- No family-wide blanket behavior.
- `safe_gateway` under control.
- `context_dependent` under control.
- At least 10–15% of songs may have empty `social_context`.
- Bridge clusters still emerge naturally.
- False-nearby candidates receive enough caution metadata.
