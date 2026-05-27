# A3 Mission Generation Repair Brief v0.1.3

## Purpose

The v0.1.2 mission-generation smoke run proved that the existing mission schema can be filled from AtlasDigestView + node interpretation + WWTSF substrate. It also exposed a beta-readiness gap: schema-valid missions can still contain unresolved route placeholders that look like playable route items.

This brief tightens the next mission-generation contract without changing the accepted v0.1.2 mission outputs.

## Controlling Finding

`mission_isolated_love_frontier_profile_06_A3.json` contains placeholder-style route items such as:

- `Hamilton-adjacent musical theater probe`
- `Disney-associated theatrical/film song probe`
- `Low-risk familiarity probe`
- `Scoped dead-end check`

These are valid route ideas, but they are not beta-ready mission items. A playable mission route needs concrete music objects, or it must explicitly mark the slot as unresolved candidate search.

## Required Repair

Mission generation must satisfy one of these two states for every route item:

1. **Concrete playable item**

   The item has a specific `artist`, `title`, and enough catalog context to support Apple Music search/import review. Album and year may remain uncertain if the search hint states that uncertainty.

2. **Explicit unresolved candidate-search slot**

   The item is not presented as playable. It is clearly marked as a candidate-search task that needs Candidate Pool Builder or human review before app import.

Placeholder route titles like `Disney-associated theatrical/film song probe` must not be treated as beta-ready mission items.

## Contract Additions

Add or enforce these evaluator checks before beta import:

- `route_items_are_concrete_or_unresolved_search_slots`
- `placeholder_titles_not_app_import_ready`
- `unresolved_candidate_search_slots_block_app_import`
- `candidate_search_status_is_explicit`

If any playable route item has a generic placeholder title, the mission may remain a useful development artifact but must set:

```text
product_status = product_review_needed
app_import_ready = false
```

If `product_status = product_fail`, `app_import_ready` must also be `false`.

## Route Item Semantics

For concrete playable items:

- `display_metadata.artist` must be a real artist or credited performer.
- `display_metadata.title` must be a real track or album title.
- `music_kit_search_hint.search_query` must be plausible as an Apple Music query.
- `preferred_version_notes` may carry uncertainty, but cannot substitute for a track identity.

For unresolved candidate-search slots:

- `item_type` should be `unresolved_candidate_search` or equivalent.
- `selection_role` may still describe route function: `anchor`, `bridge`, `probe`, `risky_probe`, `trap`, `waypoint`, or `checkpoint`.
- `music_kit_search_hint.resolution_status_placeholder` should be `needs_candidate_search`.
- `review_state.needs_human_review` must be `true`.
- `review_config.ready_for_app_import` must be `false`.

## Prompt Repair Requirement

The mission prompt should instruct the model:

```text
Do not invent placeholder route-item titles as if they are playable songs.
If a route needs a type of song but no concrete candidate is available in context, create an explicit unresolved candidate-search slot instead of a fake playable item.
Concrete route items require real artist/title metadata.
Unresolved search slots are useful for planning but are not app-import-ready.
```

## Pipeline Recommendation

Keep mission generation on `gpt-5.4-mini`.

Do not use `gpt-5.5` for mission generation until candidate object selection is cleaned up. The current issue is not primarily model intelligence; it is the handoff between mission planning and concrete candidate selection.

Next likely repair path:

1. Candidate Pool Builder resolves concrete candidate objects before mission generation.
2. Mission generation consumes candidate objects and may only choose from the pool in beta-ready mode.
3. If no candidate satisfies a needed route role, mission generation emits an unresolved candidate-search slot.
4. App import is blocked until every route slot is concrete and MusicKit-searchable.

## Status

This is a repair brief, not a rerun. Existing v0.1.2 mission outputs remain valid as development artifacts, but placeholder route items should not be considered beta-ready.
