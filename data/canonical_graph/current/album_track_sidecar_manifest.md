# Album Track Sidecar v1

Generated on 2026-05-26.

## Scope

Built from `data/canonical_graph/depth_hardening_v0_2/pass_d/album_sidecar_seed_albums_v1.json`, with accepted post-freeze Family 10 Radiohead/Oasis additions from `data/canonical_graph/current/album_sidecar_seed_albums.json`.

- Source album membership rows: 2234
- Unique album identity rows: 2167
- Album identity rows in this sidecar: 2167

## Resolution Summary

- Apple resolved album identities: 2117
- MusicBrainz fallback resolved album identities: 1822
- Unresolved album identities: 0
- Total sidecar tracks: 29667

Source policy: Apple iTunes Search API is preferred for Apple-compatible collection/track IDs; MusicBrainz WS/2 is used as structured fallback for albums missing from Apple search. Post-freeze Family 10 hotfix albums use accepted Apple Music catalog album IDs and sparse Apple Music catalog track relationships.

## Apple ID Backfill

Backfilled on 2026-05-29 from accepted Apple Music link artifacts.

- Raw Apple payloads persisted: false
- Album rows with Apple collection IDs after backfill: 2117
- Track rows with Apple track IDs after backfill: 28595
- Track rows total: 29667
- Album ID conflicts: 0
- Track ID conflicts: 0

See `album_track_sidecar_apple_id_backfill_manifest.md` for the backfill ledger.

## Apple Tracklist Authority

Rebuilt on 2026-05-29 from Apple Music catalog album track relationships for albums with accepted Apple album IDs. Post-freeze Family 10 album rows patched on 2026-06-01T23:45:08.892Z.

- Raw Apple payloads persisted: false
- Albums with Apple collection IDs: 2117
- Albums without Apple collection IDs: 50
- Apple-resolved albums rebuilt from Apple tracklists: 2117
- Apple-resolved albums rebuilt with zero Apple song tracks: 1
- Current sidecar track rows total: 29667
- Track rows with Apple song IDs: 28595
- Track rows missing Apple song IDs: 1072
- Missing Apple song IDs on Apple-resolved albums: 0
- Missing Apple song IDs on albums without Apple album IDs: 1072

For Apple-resolved albums, Apple Music catalog song tracks are now the sidecar track-row authority. Music-video relationship entries are dropped, and Apple music-video IDs are not persisted.

See `apple_music_sidecar_tracklist_authority_pass_v1/apple_music_sidecar_tracklist_authority_manifest.md` for the authority-pass ledger. See `apple_music_family10_album_sidecar_patch_v1/apple_music_family10_album_sidecar_patch_manifest.md` for the post-freeze Family 10 patch ledger.

## Artifacts

- `album_track_sidecar.json`: nested album nodes with memberships, catalog match, and track list.
- `album_track_sidecar_album_resolution.csv`: one row per unique album identity and its resolution status.
- `album_track_sidecar_tracks.csv`: one row per sidecar track for graph/song-depth expansion.
- `album_track_sidecar_manifest.md`: this report.

## Unresolved Preview

No unresolved album identities.
