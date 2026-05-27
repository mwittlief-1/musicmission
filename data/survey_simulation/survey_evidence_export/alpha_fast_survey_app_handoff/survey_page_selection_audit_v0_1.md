# Survey Page Selection Audit v0.1

Generated: 2026-05-24

Status: Alpha live-smoke diagnostic contract

Audience: Core app, Survey PM, Canonical Graph PM, Atlas PM, Mission Generation PM, Release QA

## Purpose

Survey Page Selection Audit v0.1 explains how each displayed Survey page was assembled during live Alpha without exposing hidden simulator truth, raw scoring internals, generation prompts, or tester-facing UI noise.

The audit is a PM/support diagnostic artifact. It is not Atlas-ingestable evidence. Atlas may ingest only Survey Evidence Export v0.1 evidence atoms.

## Required Boundary

The audit may include visible and sanitized construction context:

- page ID, step, stage, and page number
- displayed item IDs
- typed `music_object_ref`
- tile source mix
- candidate buckets/page intents
- candidate basis
- Apple exposure presence flag and sanitized exposure-prior summary
- approved graph surface refs and graph IDs
- prior visible response refs used by the selector
- dedupe and exclusion reasons expressed as categories, not raw ranking internals

The audit must exclude:

- hidden fake-profile truth
- hidden archetype tiers
- hidden corpus reactions
- hidden reason tags
- raw Apple Music payload
- raw candidate ranking scores
- adaptive target mix internals
- randomization seeds
- generator prompts
- Profile Writer output
- final Atlas confidence, roles, or promotion decisions

## Artifact Shape

Recommended top-level shape:

```json
{
  "schema_version": "waymark.survey_page_selection_audit.v0.1",
  "audit_id": "survey_page_selection_audit:<survey_session_id>",
  "survey_session_id": "survey_session:...",
  "created_at": "2026-05-24T00:00:00Z",
  "producer": "MusicAtlasController",
  "private_data_boundary": {
    "hidden_simulator_truth_excluded": true,
    "raw_apple_payload_excluded": true,
    "raw_ranking_scores_excluded": true,
    "atlas_truth_claims_excluded": true
  },
  "pages": [],
  "construction_only_excluded": {
    "atlas_ingestable": false,
    "excluded_categories": []
  }
}
```

## Page Record

Each page record should explain one displayed page:

```json
{
  "page_id": "artist_page_001",
  "step": "artist_page_1",
  "stage": "artist",
  "page_number": 1,
  "tile_count": 12,
  "displayed_item_ids": ["ALPHA_ARTIST_artist-fleetwood-mac"],
  "source_mix": {
    "apple_music_derived": 4,
    "broad_calibration": 3,
    "response_adjacent": 2,
    "rejection_probe": 1,
    "sleeper_probe": 1,
    "object_specific": 1
  },
  "candidate_bucket_mix": {
    "payload_signature_artist": 4,
    "archetype_confirmation_anchor": 3,
    "multi_archetype_junction": 2,
    "false_nearby_or_boundary_check": 1,
    "mass_popular_control": 1,
    "coverage_repair": 1
  },
  "prior_response_inputs": [],
  "tiles": [],
  "dedupe_summary": {
    "duplicate_item_ids_removed": 0,
    "duplicate_display_names_removed": 0,
    "prior_visible_items_removed": 0,
    "canonical_blocklist_removed": 0
  },
  "top_included_candidate_summaries": [],
  "top_excluded_candidate_summaries": []
}
```

## Tile Record

Each tile record should explain a visible tile:

```json
{
  "survey_item_id": "ALPHA_ARTIST_artist-fleetwood-mac",
  "response_id": "artist_page_001_resp_01",
  "evidence_ref": "artist_page_001:artist:01:Fleetwood Mac:love",
  "music_object_ref": {
    "object_type": "artist",
    "ref_source": "canonical_graph",
    "canonical_artist_id": "artist-fleetwood-mac",
    "display_name": "Fleetwood Mac",
    "resolution_state": "resolved"
  },
  "source": "apple_music_derived",
  "apple_exposure": {
    "is_present": true,
    "interpretation": "exposure_prior",
    "taste_truth": false
  },
  "page_intent": "payload_signature_artist",
  "candidate_basis": [
    "active_survey_selection",
    "payload_signature_artist_bucket",
    "payload_overrepresentation",
    "apple_exact_match"
  ],
  "graph_refs": {
    "family_numbers": [3],
    "archetype_ids": ["016", "022"],
    "roles": ["album_anchor", "anchor", "bridge", "gateway", "song_first"],
    "best_recognition_tier": "mass",
    "best_survey_tier": "core"
  },
  "approved_graph_surface_ref": {
    "source": "canonical_graph_survey_surface_v0_2",
    "candidate_id": "survey-f3-artist-artist-fleetwood-mac-016",
    "review_status": "approved",
    "survey_page_role": "page1_core",
    "survey_intent": "song_first_memory"
  }
}
```

## Included and Excluded Candidate Summaries

`top_included_candidate_summaries` may repeat the visible tiles in compact form for PM scanability.

`top_excluded_candidate_summaries` is optional in Alpha. If present, it must use only sanitized categories:

```json
{
  "music_object_ref": {
    "object_type": "artist",
    "ref_source": "canonical_graph",
    "canonical_artist_id": "artist-example",
    "display_name": "Example",
    "resolution_state": "resolved"
  },
  "exclusion_reason": "duplicate_display_name | prior_visible_item | canonical_blocklist | family_quota | archetype_quota | not_enough_page_capacity | not_response_relevant | deep_only_without_apple_or_prior_response",
  "candidate_basis": ["canonical_graph_runtime_surface"],
  "page_intent": "frontier",
  "atlas_ingestable": false
}
```

Do not include raw score values, rank positions, prompt text, hidden simulator labels, or hidden lookup state.

## Field Classification

| Field group | Classification | Atlas ingestion |
|---|---|---|
| `page_id`, `step`, `stage`, `page_number`, `displayed_item_ids` | PM diagnostic | no |
| `music_object_ref` | PM diagnostic / shared ref | no, unless repeated in Survey Evidence Export atom |
| `source_mix`, `candidate_bucket_mix`, `candidate_basis`, `page_intent` | PM diagnostic | no |
| `apple_exposure.is_present`, `apple_exposure.interpretation`, `taste_truth=false` | PM diagnostic exposure context | no |
| `prior_response_inputs` | PM diagnostic visible refs | no |
| `dedupe_summary`, `top_excluded_candidate_summaries` | construction-only excluded | no |
| Survey Evidence Export v0.1 `atlas_ingestable.evidence_atoms[]` | evidence ledger | yes |

## Live Smoke Usage

For a trusted Alpha support bundle, Core may upload this audit only after the same manual/consent gate used for diagnostic artifacts. Automatic upload remains blocked until Product/Release approves privacy, retention, deletion, and support copy.

The audit should be linked by:

- `survey_session_id`
- mission generation `client_request_id`
- Supabase generation run ID, when available
- Survey Evidence Export `export_id`

This creates the missing diagnostic chain:

```text
Apple Music signal
-> Survey page selection audit
-> Survey Evidence Export
-> mission request
-> generation result
-> app import result
```
