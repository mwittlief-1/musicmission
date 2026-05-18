# Data Contracts v0.2

## Contract decisions

### Initial mission size

The included sample mission has 4 items. v0.2 does not require resolving every item.

### Initial success bar

Acceptance requires at least 1 item to be resolved and played on a physical iPhone.

### `reconciliation_status`

`reconciliation_status` belongs at the **top level** of `reaction_session.json`, not inside `mission_summary`.

Default value:

```json
"reconciliation_status": "not_reconciled"
```

Allowed values:

```json
["not_reconciled", "reconciliation_candidate", "reconciled", "ignored"]
```

## Mission JSON shape

Mission files use schema: `schema_mission_v0_2.json`.

Required top-level fields:

- `schema_version`
- `mission_id`
- `mission_title`
- `mission_version`
- `created_at`
- `mission_type`
- `recommended_format`
- `hypothesis`
- `inflation_warning`
- `success_bar`
- `items`

Each mission item requires:

- `item_id`
- `sequence`
- `item_type`
- `artist`
- `title`
- `apple_music_resolution.status`

Supported item types:

- `track`
- `album`

Supported resolution statuses:

- `unresolved`
- `resolved`
- `ambiguous`
- `skipped`
- `unavailable_region`
- `unavailable_subscription`
- `failed`

For `resolved`, catalog metadata is required by schema.

For unresolved/skipped/unavailable/failed statuses, a reason is required.

## Reaction session JSON shape

Reaction sessions use schema: `schema_reaction_session_v0_2.json`.

Required top-level fields:

- `schema_version`
- `session_id`
- `mission_id`
- `mission_version`
- `created_at`
- `started_at`
- `reconciliation_status`
- `device_context`
- `music_context`
- `item_results`
- `export`

Each item result requires:

- `mission_item_id`
- `item_type`
- `artist`
- `title`
- `resolution.status`
- `playback.status`
- `reaction.reaction_value`
- `reaction.reacted_at`
- `reaction.notes.text`
- `timestamps.created_at`
- `timestamps.updated_at`

## Reaction values

Allowed values:

- `hit`
- `partial`
- `ok_shelf`
- `miss`
- `slop`
- `skipped`
- `unresolved`

## Playback statuses

Allowed values:

- `not_attempted`
- `queued`
- `playing`
- `played`
- `skipped`
- `failed`

## Storefront / region handling

Every resolution object should store the storefront/region used for search or playback if known. If a track cannot be found or played in the user storefront, mark it as `unavailable_region` or `unresolved` with a reason. The mission does not fail merely because some items are unavailable.

## Export file naming

Suggested names:

```text
exports/reaction_session_YYYYMMDD_HHMMSS.json
exports/discovery_log_YYYYMMDD_HHMMSS.md
```

## Validation rule

The app should refuse to mark a session export as complete unless:

- JSON validates against schema.
- At least one item result has `resolution.status = "resolved"`.
- At least one item result has playback status `played` or `playing` during acceptance.
- At least one item result has a non-empty reaction note for the acceptance test.
