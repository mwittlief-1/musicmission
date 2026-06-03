# Apple Music Album Graph Decision Pass v1

Generated: 2026-05-28T18:48:36.492Z

Status: `complete`

Storefront: `us`

## Intent

Record user-reviewed album availability decisions from the latest 20-row unmatched slice. This pass separates direct same-target Apple links from graph replacement nodes and from albums that should remain preserved but Apple-unresolvable.

## Policy

- Preserve original graph target for unresolvable albums: `true`
- Replacement model: `add_new_graph_node_with_relationship_to_original_target`
- Raw Apple payloads persisted: `false`

## Counts

- Decisions: 20
- Direct links: 2
- Replacement nodes staged: 14
- Unresolvable without replacement: 4
- New links: 18

## New Links By Source Type

| key | count |
| --- | ---: |
| graph_replacement_album | 14 |
| album_sidecar_album | 2 |
| graph_album | 2 |

## Decisions By Status

| key | count |
| --- | ---: |
| apple_music_unresolvable | 18 |
| resolved_direct | 2 |
