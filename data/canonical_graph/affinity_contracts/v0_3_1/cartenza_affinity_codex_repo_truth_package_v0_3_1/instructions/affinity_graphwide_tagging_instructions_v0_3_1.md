# Affinity Graph-Wide Tagging Instructions v0.3.1

## Purpose

Run graph-wide song affinity tagging using the approved v0.2.2 ontology and v0.3 sparse tagging rules, with the v0.3.1 schema boundary: canonical song affinity tags are separate from membership / route-context overlays.

This is a tagging contract, not runtime ingestion approval.

## Inputs

Use the current canonical graph export as source of truth:

- `canonical_song_recordings.json`
- `song_archetype_memberships.json`
- `canonical_artists.json`
- `canonical_albums.json`
- family normalized files where needed
- `affinity_tag_ontology_v0_2_2_schema_amended_v0_3_1.json`
- `affinity_tagging_output_schema_v0_3_1.json`

Do not use Matt-specific taste files or founder preference evidence. Treat the product user generically as Jane Doe.

## Required output files for graph-wide pass

1. `affinity_graphwide_song_tags_v0_3_1.json`
2. `affinity_graphwide_duplicate_context_review_v0_3_1.md`
3. `affinity_graphwide_cluster_findings_v0_3_1.md`
4. `affinity_graphwide_QA_report_v0_3_1.md`
5. `affinity_graphwide_QA_metrics_v0_3_1.json`

## Output shape

Each song object must use this split:

```json
{
  "canonical_song_recording_id": "",
  "song_title": "",
  "artist_names": [],
  "release_years": [],
  "canonical_song_affinity_tags": {
    "vocal_performance": {"primary": [], "secondary": []},
    "emotion_theme": {"primary": [], "secondary": []},
    "sonic_texture": {"primary": [], "secondary": []},
    "rhythm_body": {"primary": [], "secondary": []},
    "form_container": {"primary": [], "secondary": []}
  },
  "membership_context_overlays": [
    {
      "membership_id": "",
      "family_number": null,
      "archetype_id": "",
      "membership_roles": [],
      "social_context": {"primary": [], "secondary": []},
      "routing_caution": {"primary": [], "secondary": []},
      "overlay_notes": ""
    }
  ],
  "duplicate_context_review": {
    "needed": false,
    "reason_codes": []
  },
  "review": {
    "identity_review_needed": false,
    "core_tag_review_needed": false,
    "overlay_review_needed": false,
    "selection_bucket_review_needed": false,
    "review_reason_codes": [],
    "review_reason": ""
  },
  "tagging_notes": "",
  "source_confidence": "high"
}
```

## Sparsity rules

Default target:

```text
3–5 core tags per song across the five core dimensions.
0–3 overlay tags per membership/context overlay.
5–8 combined tags only when overlay context is meaningful.
Fewer than 5 total tags is allowed for simple songs or context-light memberships.
9–10 combined tags are allowed only for genuinely multi-context, bridge-heavy, or routing-sensitive songs.
```

Do not fill to shape. Empty dimensions are allowed.

## Core-vs-overlay rules

### Canonical song affinity tags

Use for intrinsic musical features only:

- vocal stance/performance
- central emotion/theme
- sound-world/texture
- movement/groove/energy shape
- form/container

These must be stable across memberships unless the graph is actually representing different recordings/versions.

### Membership context overlays

Use for contextual behavior:

- karaoke/shared listening
- wedding/holiday/family/worship/party/social use
- safe gateway behavior
- overfamiliarity
- false-nearby risk
- context dependence
- framing requirements
- boundary/whiplash caution

## Duplicate/context review rule

Flag review when:

- same `composition_key` and release year appears under multiple `canonical_song_recording_id`s;
- same title/artist appears in multiple families/archetypes;
- the graph appears to represent the same recording once as a music-history object and once as a social/context object;
- the same real-world recording would otherwise receive materially different core affinity tags.

Use reason codes:

```text
same_composition_multiple_ids
same_recording_multiple_contexts
context_surface_duplicate
version_identity_unclear
core_overlay_conflict
membership_overlay_needed
canonical_merge_candidate
intentional_distinct_version
```

## Hard fail checks

The output fails QA if:

- aliases appear instead of canonical tags;
- non-canonical tags appear;
- social_context or routing_caution appears inside canonical_song_affinity_tags;
- family/archetype context rewrites core tags;
- safe_gateway becomes a default filler tag;
- context_dependent becomes a default filler tag;
- duplicate/context candidates are not flagged;
- average tag density returns to v0.1/v0.2 over-tagging behavior.

## Acceptance gate for graph-wide tagging pass

```text
All canonical_song_recording_ids resolve against graph.
All membership overlays resolve against song_archetype_memberships where available.
No alias leakage.
No non-canonical tags.
Average combined tags/song: target 5–8, but simple/context-light songs may be below 5.
safe_gateway and context_dependent remain bounded and justified.
At least 10–15% of songs may have empty social_context overlays.
Duplicate/context candidates are surfaced, not silently flattened.
Bridge clusters emerge from core + overlay data without family blanket tagging.
False-nearby candidates receive overlay caution metadata without corrupting core song truth.
```
