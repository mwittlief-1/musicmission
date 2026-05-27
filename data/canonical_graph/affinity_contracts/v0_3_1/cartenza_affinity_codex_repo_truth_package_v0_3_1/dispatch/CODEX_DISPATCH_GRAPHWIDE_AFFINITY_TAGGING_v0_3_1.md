# Codex Dispatch — Cartenza Graph-Wide Affinity Tagging Runtime Exercise v0.3.1

## Status

Do not begin graph-wide tagging until the canonical graph expansion exercises are complete and PM explicitly identifies the completed graph export as the controlling source.

```text
Affinity ontology v0.2.2: APPROVED
Sparse tagging rules v0.3: APPROVED
Schema boundary amendment v0.3.1: APPROVED
Graph-wide tagging: PREPARED BUT BLOCKED PENDING GRAPH EXPANSION
Runtime ingestion: NOT APPROVED
```

## Mission

Run a graph-wide Cartenza Affinity Tagging exercise against the completed canonical graph. The output should enrich songs and membership contexts so future mission generation can build smarter routes across songs, recordings, albums, artists, archetypes, families, survey surfaces, mission routes, and Atlas education surfaces.

This is not a recommendation task. Treat the user as generic Jane Doe. Do not use founder or Matt-specific taste data.

## Required contract files

- `schemas/affinity_tagging_output_schema_v0_3_1.json`
- `ontology/affinity_tag_ontology_v0_2_2_schema_amended_v0_3_1.json`
- `allowed_tags/allowed_canonical_tags_by_dimension_v0_3_1.json`
- `allowed_tags/APPROVED_CANONICAL_RUNTIME_TAGS_v0_3_1.md`
- `instructions/affinity_graphwide_tagging_instructions_v0_3_1.md`
- `schema_boundary/affinity_schema_boundary_amendment_v0_3_1.md`
- `validation/affinity_graphwide_QA_contract_v0_3_1.md`

## Source of truth

Use the final completed canonical graph export named by PM after graph expansion. Expected inputs include canonical graph manifest, canonical_song_recordings, song_archetype_memberships, canonical artists/albums/compositions/recording versions, entity relationships, normalized family files, survey candidates, archetype readiness, family readiness, boundary questions, and dead-end probes.

## Core schema rule

`canonical_song_affinity_tags` may use only these dimensions:

```text
vocal_performance
emotion_theme
sonic_texture
rhythm_body
form_container
```

`membership_context_overlays` may use only these dimensions:

```text
social_context
routing_caution
```

Do not let family/archetype/survey/mission context rewrite intrinsic song truth.

## Allowed tags

Only canonical tags listed in `allowed_tags/allowed_canonical_tags_by_dimension_v0_3_1.json` may appear in output. Alias leakage is a hard QA failure.

## Sparsity rule

Default target: 5–8 tags per song. Empty dimensions are allowed. Do not fill to the cap. Use 9–10 tags only when a song is genuinely multi-context, bridge-heavy, or routing-sensitive.

## Execution phases

1. Readiness check.
2. Duplicate/context diagnostics.
3. Shard plan.
4. Controlled graph-wide tagging.
5. Deterministic QA validation.
6. Cluster analysis.
7. PM review packet.

## Required outputs

```text
affinity_graphwide_readiness_report_v0_1.md
affinity_duplicate_context_review_graphwide_v0_1.md
affinity_duplicate_context_review_graphwide_v0_1.json
affinity_graphwide_shard_plan_v0_1.md
affinity_graphwide_shard_manifest_v0_1.json
affinity_song_tags_graphwide_shard_*.json
affinity_song_tags_graphwide_v0_1.json
affinity_graphwide_QA_report_v0_1.md
affinity_graphwide_QA_metrics_v0_1.json
affinity_graphwide_cluster_findings_v0_1.md
affinity_graphwide_schema_notes_v0_1.md
affinity_graphwide_tagging_PM_review_packet_v0_1.zip
```

## Stop/RFI conditions

Stop and RFI if the completed graph export is missing/inconsistent; song IDs or membership IDs are unstable; ontology/schema files are missing or unexpectedly modified; aliases or invented tags appear; average tags per song drifts above 8 without justification; social/routing tags leak into core song affinity; duplicate/context ambiguity creates unstable canonical song truth; or shared-listening surfaces rewrite intrinsic profiles.

## Final instruction

Produce the PM review packet only. Do not ingest runtime data. Runtime ingestion is a separate PM decision.
