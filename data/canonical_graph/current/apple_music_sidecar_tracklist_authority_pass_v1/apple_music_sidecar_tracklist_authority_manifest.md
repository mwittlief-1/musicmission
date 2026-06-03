# Apple Music Sidecar Tracklist Authority Pass v1

Generated: 2026-06-01T23:45:08.892Z

Status: `complete`

## Policy

- Raw Apple payloads persisted: `false`
- Apple requests are limited to sparse album track lists for sidecar albums that already have an accepted Apple album ID.
- For Apple-resolved albums, Apple Music catalog song tracks replace prior sidecar track rows.
- Music-video relationship entries are dropped and no Apple music-video IDs are persisted.
- Albums without Apple album IDs are left unchanged.
- Artwork, previews, lyrics, raw catalog payloads, and user tokens are not persisted.

## Counts

| Metric | Count |
| --- | ---: |
| Album jobs | 2112 |
| Albums rebuilt from Apple tracklists | 2112 |
| Albums rebuilt with zero Apple song tracks | 1 |
| Previous track rows in Apple-album scope | 28610 |
| Previous missing track IDs in Apple-album scope | 72 |
| Apple track rows written in scope | 28538 |
| Sidecar albums total | 2167 |
| Sidecar albums with Apple album ID | 2117 |
| Sidecar albums without Apple album ID | 50 |
| Sidecar track rows total | 29667 |
| Sidecar track rows with Apple track ID | 28595 |
| Sidecar track rows missing Apple track ID | 1072 |
| Missing track IDs on Apple-resolved albums | 0 |
| Missing track IDs on albums without Apple ID | 1072 |

## Post-Freeze Patch

- Patch run: `apple_music_family10_album_sidecar_patch_v1`
- Albums added to sidecar: 5
- Apple track rows added in patch scope: 57
