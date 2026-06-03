# Apple Music Sidecar Track Album-Bound Pass v1

Generated: 2026-05-29T03:28:04.727Z

Status: `complete`

## Policy

- Raw Apple payloads persisted: `false`
- Apple requests are limited to sparse track lists for sidecar albums that already have an Apple album ID.
- Output persists Apple song IDs and match evidence only; fetched Apple track titles/artists/album names are not written.

## Counts

| Metric | Count |
| --- | ---: |
| Album jobs | 608 |
| Missing sidecar track rows in scope | 2943 |
| Track links accepted | 738 |
| Deferred rows | 2205 |

## Deferred By Reason

| Value | Count |
| --- | ---: |
| `album_bound_track_no_safe_match` | 2205 |
