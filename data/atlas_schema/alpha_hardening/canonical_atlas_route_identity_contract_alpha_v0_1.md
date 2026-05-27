# Canonical / Atlas Route Identity Contract Alpha v0.1

Generated: 2026-05-25

## Purpose

This contract supports the live generation recovery by pinning the route identity fields that Core, Infrastructure, Mission Generation, Canonical Graph, and Atlas should use to reject duplicate route items, reject non-candidate items, and keep display identity separate from canonical identity.

The immediate live blocker was:

```text
Supabase generated missions, but live validation allowed duplicate route item IDs, non-candidate route items, and repeated items across the 10-mission batch.
```

## Field Roles

| field | owner/source | role | validation use | not for |
| --- | --- | --- | --- | --- |
| `candidate_id` | Candidate Pool | Candidate membership identity. | Every generated `route.items[].candidate_id` must exactly match one supplied candidate `candidate_id`. Duplicate `candidate_id` within a mission or across a 10-mission batch is invalid unless explicitly allowed by a future repeat policy. | UI display, MusicKit search, Atlas role truth. |
| `dedupe_group` | Candidate Pool | Preferred route-level dedupe key. | Use as the stable route candidate key when available. Duplicate `dedupe_group` within a mission or across an active batch is invalid. | User-facing text. |
| `canonical_entity_id` | Canonical Graph | Canonical object identity. | Confirms graph object identity and backs `music_object_ref`; may also dedupe when `dedupe_group` is missing. | App item identity, UI display, user taste truth. |
| `canonical_object_type` | Canonical Graph | Canonical object type. | Distinguishes `song_recording` from `album`; track route candidates must map to `song_recording`. | App route item type by itself. |
| `object_type` | Candidate Pool route surface | App route object type. | Must be `track` or `album` in route-ready pools. | Atlas `music_object_ref.object_type` for tracks. |
| `route_item_type` | Candidate Pool route surface | App route item type. | Must equal `object_type`; must be `track` or `album`. | Canonical object type. |
| `route.items[].item_id` | Mission Generation adapter/Core app mission | App mission item identity. | Must be unique within one app mission and across imported active batch state. It is not proof that the item came from the candidate pool. | Candidate membership validation. |
| `display_name` / `display_label` | Candidate Pool | Candidate display title. | Preferred title source for generation and Survey/debug display. | Slug identity or dedupe by itself. |
| `credited_artist` | Candidate Pool | Candidate display artist credit. | Preferred artist display source and MusicKit search context. | Canonical role truth. |
| `music_kit_search_hint` | Candidate Pool / route item | Catalog search identity. | Search query support only; can help display-identity fallback. | Canonical merge, Atlas truth, or candidate membership. |
| `music_object_ref` | Canonical-to-Atlas adapter | Atlas-compatible identity/resolution context. | Typed canonical/user-local/external/unresolved reference for Atlas evidence and audit. | User-specific role truth or promotion. |

## Generated Route Item Requirements

Mission Generation output must obey all of these before any mission can become `app_import_candidate`:

- `route.items[].candidate_id` is required.
- `route.items[].candidate_id` must be present in the supplied candidate pool.
- `route.items[].item_id` must be unique within the mission.
- `route.items[].candidate_id` must be unique within the mission.
- `route.items[]` must not repeat display identity: normalized `item_type + artist + title`.
- Route items must be concrete `track` or `album` items, not artist-level route placeholders.
- The app mission adapter must preserve an unresolved Apple Music state until resolver work happens.

Batch-level generation must additionally reject or avoid repeats across the active 10-mission import target:

- prior imported `candidate_id`;
- prior imported `dedupe_group` or canonical route key;
- prior imported `route.items[].item_id`;
- prior normalized display identity.

## Candidate-Pool-Only Source Rule

Route items may not be invented from AtlasDigestView, MissionGenerationDigestView, Survey visible tiles, strong regions, generated prose, or canonical graph rows that were not supplied in the active candidate pool.

Allowed:

```text
MissionGenerationDigestView / AtlasDigestView -> user-specific context and constraints
candidate_pool.candidates or candidate_pool.pools.* -> concrete route items
```

Forbidden:

```text
digest strong region -> generated route item not in candidate pool
Survey tile -> route item not in candidate pool
model memory / known artist region -> route item not in candidate pool
canonical graph row -> route item not in candidate pool
```

If the model wants a musically plausible item outside the pool, the correct product state is `review_needed` or `blocked`, not `app_import_candidate`.

## Display-Name Contract

App-facing display should use these fields in order:

### Candidate Pool

- title: `display_label`, fallback `display_name`;
- artist: `credited_artist`;
- album, when present: candidate route metadata or `route_item` metadata;
- never prefer `candidate_id`, `canonical_entity_id`, `dedupe_group`, or normalized slugs as display copy.

### Generated Rich Mission Route

- title: `route.items[].display_metadata.title`;
- artist: `route.items[].display_metadata.artist`;
- album: `route.items[].display_metadata.album`;
- year: `route.items[].display_metadata.release_year`.

### App `mission.v0.2`

- title: `items[].title`;
- artist: `items[].artist`;
- album: `items[].album`;
- year: `items[].year`.

Internal slugs are allowed in diagnostics, validation reports, and support artifacts only.

## Atlas Evidence Boundary

This identity contract does not change Atlas truth rules:

- candidate-pool membership is graph/product metadata, not taste truth;
- successful import is operational evidence, not taste truth;
- generated mission result is not a `Signal` until the user interacts with the mission;
- diagnostics remain support-only unless explicitly classified as Atlas-ingestable evidence;
- no route item can promote a Landmark, Region, Frontier, Dead End, or Waypoint by itself.

## Validation Handoff

Core and Infrastructure should validate at least these sets:

```text
candidate_ids = all supplied candidate_pool candidate_id values
dedupe_groups = all supplied candidate_pool dedupe_group values
candidate_display_keys = normalized object_type + credited_artist + display_label/display_name
canonical_route_keys = canonical_object_type + canonical_entity_id
```

For each generated mission:

```text
route_candidate_id in candidate_ids
route_candidate_id unique within mission
route_item_id unique within mission
route_display_key unique within mission
route canonical/dedupe key unique when recoverable
```

For the 10-mission batch:

```text
candidate_id not repeated across imported missions
dedupe_group/canonical route key not repeated across imported missions
display identity not repeated across imported missions
```

Machine-readable companion:

`data/atlas_schema/alpha_hardening/canonical_atlas_route_identity_contract_alpha_v0_1.json`
