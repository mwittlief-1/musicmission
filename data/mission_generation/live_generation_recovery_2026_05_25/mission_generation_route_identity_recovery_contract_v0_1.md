# Mission Generation Route Identity Recovery Contract v0.1

Generated: 2026-05-25

Status: `MISSION_GENERATION_CONTRACT_HARDENED_LOCAL`

## Purpose

This contract captures the Mission Generation lane response to the live Alpha smoke failure where Supabase generated app-import-candidate rows that still contained duplicate route item IDs, non-candidate route items, and repeated items across the ten-mission batch.

The product rule is simple:

```text
No mission is app-importable unless every playable route item is an exact, unique, supplied candidate-pool object.
```

## Candidate-Pool-Only Rule

When `candidate_pool.candidates` is non-empty:

- every `route.items[].candidate_id` must exactly match one supplied candidate row;
- artist/title similarity is not sufficient;
- Survey evidence, Atlas digest examples, strong-region summaries, user vocabulary, and candidate-pool behavior notes are context only;
- context objects cannot become route items unless the exact playable object appears in `candidate_pool.candidates`;
- if no valid candidate fits a needed route role, the model should return a blocked/retry reason and must not invent a playable item.

## Route Identity Rule

Within a mission, the route must not contain:

- duplicate `route.items[].item_id`;
- duplicate `route.items[].candidate_id`;
- duplicate normalized artist/title/type display identity.

Normalized display identity format:

```text
item_type:artist:title
```

## Ten-Mission Batch Memory

One-at-a-time generation calls should pass these backward-compatible arrays in `prompt_context`:

```json
{
  "already_selected_route_item_ids": [],
  "already_selected_candidate_ids": [],
  "already_selected_display_keys": [],
  "excluded_route_item_ids": [],
  "excluded_candidate_ids": []
}
```

If omitted, the request is treated as a single-mission call. If supplied, any reuse is a hard blocker.

## Failure Fixtures

Local fixture coverage now includes:

- `supabase/functions/generate-first-mission-batch/fixtures/duplicate_item_id/`
- `supabase/functions/generate-first-mission-batch/fixtures/non_candidate_item/`
- `supabase/functions/generate-first-mission-batch/fixtures/batch_memory_repeat/`

Expected result for each:

```text
status = blocked
app_missions_returned = false
```

## Failure Classification

If live generation produces a bad route item, classify it this way:

| failure | classification | owner follow-up |
| --- | --- | --- |
| Missing or non-pool `candidate_id` | validator gap if imported; prompt drift if generated but blocked | Supabase validator / Mission prompt |
| Duplicate item/candidate/display identity inside mission | validator gap if imported; prompt drift if generated but blocked | Supabase validator / Mission prompt |
| Repeated route item across ten-mission batch without batch memory supplied | request/context gap | Core/Infrastructure batch-memory handoff |
| Repeated route item despite batch memory supplied | validator gap if imported; prompt drift if blocked | Supabase validator / Mission prompt |
| Candidate pool lacks enough route-ready alternatives for requested slot | candidate-pool construction issue | Canonical/Candidate Pool |

## App Import Rule

`app_import_candidate` and `app_import_candidate_with_review_flags` are allowed only when route identity and exact candidate membership pass.

`review_needed`, `blocked`, and `failed` responses must not be imported.
