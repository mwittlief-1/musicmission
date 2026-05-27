# Affinity Graph-Wide QA Contract v0.3.1

## Deterministic validation checks

Graph-wide tagging output is PM-reviewable only if all checks below pass or are explicitly flagged with reason-coded review fields.

## Hard fail checks

- 0 non-canonical tags
- 0 alias leakage
- 0 invented tags
- 0 unresolved required song IDs
- 0 schema-boundary violations
- 0 duplicate canonical song rows unless explicitly expected by graph identity model
- `social_context` and `routing_caution` never appear inside `canonical_song_affinity_tags`
- core dimensions never appear inside `membership_context_overlays`
- output validates against `schemas/affinity_tagging_output_schema_v0_3_1.json`

## Density checks

- Default average canonical affinity tags per song: 5–8
- 9–10 tags allowed only with explicit complexity justification
- Empty dimensions allowed
- Do not fill every dimension for shape

## Overlay checks

- `safe_gateway` is not used as a popularity default
- `context_dependent` is not used as a generic uncertainty tag
- At least 10–15% of eligible social-context overlays should be empty unless graph context proves otherwise
- Family/shared-listening surfaces must not rewrite core song features

## Blanket behavior checks

Detect and report repeated family-wide tag application patterns, especially:

- every country/roots song receiving the same story/heartbreak/shuffle pattern
- every punk/noise song receiving rebellion/distortion/alienation by default
- every family/shared-listening object receiving celebration/safe_gateway by default
- every famous song receiving overfamiliar_anchor or safe_gateway by default

## Duplicate/context checks

- Flag same title + same artist candidates
- Flag same composition with multiple recording IDs
- Flag legacy Waymark ID plus Cartenza ID coexistence
- Flag single/edit/live/version ambiguity
- Do not merge automatically

## Review reason codes

```text
recording_identity_unclear
tag_definition_ambiguous
missing_tag_candidate
social_context_unclear
routing_caution_unclear
over_tagged
under_tagged
duplicate_context_unclear
context_leak_risk
version_ambiguity
schema_boundary_risk
```

## Required QA metrics JSON

`affinity_graphwide_QA_metrics_v0_1.json` must include counts for song rows, membership overlays, families/archetypes covered, non-canonical tags, alias leakage, schema-boundary violations, average core tags per song, tag distribution, safe_gateway/context_dependent counts, empty social contexts, duplicate/context candidates, review flags, underused tags, and overused tags.
