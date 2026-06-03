# App Full Graph Survey Resources v1

Generated: 2026-06-02T18:16:55.753Z

Status: complete

## Source

- Source graph: `data/canonical_graph/current/graph_linking_node_set.json`
- Source inventory: `data/canonical_graph/current/canonical_graph_active_inventory.json`
- Apple catalog gate: `MusicAtlasController/Resources/canonical_apple_music_catalog_index_v1.json`

## Canonical App Resource Counts

| Resource | Count |
| --- | ---: |
| canonical_artists.json | 1876 |
| canonical_albums.json | 2113 |
| canonical_song_recordings.json | 7032 |

## Survey Membership Counts

| Surface | Count |
| --- | ---: |
| survey_artist_candidates_v0_2.json | 2036 |
| survey_album_candidates_v0_2.json | 2181 |
| survey_song_candidates_v0_2.json | 7216 |

## Canonical ID Sources

| Source | Count |
| --- | ---: |
| Catalog match key | 11048 |
| Inferred from graph identity | 1 |

## Skipped Graph Objects

| Reason | Count |
| --- | ---: |
| No Apple catalog entry | 277 |
| Unresolved risk | 0 |
| Unsupported type | 0 |
| Missing identity | 0 |

## Policy

Survey display resources are no longer capped by the legacy reduced survey candidate projection.
Any active current canonical graph artist, album, song, or recording may enter the app Survey resources when it has usable Apple catalog coverage and is not unresolved or blocklisted at runtime.
