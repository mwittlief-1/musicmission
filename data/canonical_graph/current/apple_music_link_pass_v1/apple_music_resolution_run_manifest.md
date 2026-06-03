# Apple Music Link Pass v1

Generated: 2026-05-27T21:45:41.270Z

Status: `complete`

Storefront: `us`

## Policy

- Raw Apple payloads persisted: `false`
- Durable output stores Apple catalog IDs, resource type, storefront, source refs, match status, and scoring metadata only.
- Artwork, previews, lyrics, MusicKit content, raw catalog responses, and Music User Tokens are not persisted.

## Inputs

- `data/canonical_graph/current/graph_linking_node_set.json`
- `data/canonical_graph/current/album_track_sidecar_album_resolution.csv`
- `data/canonical_graph/current/album_track_sidecar_tracks.csv`

## Counts

- Graph nodes total: 11309
- Graph jobs completed cumulative: 11309
- Graph jobs remaining: 0
- Sidecar seed links: 4560
- Links total: 14156
- Manual review rows: 1713

## Links By Source Type

| key | count |
| --- | ---: |
| graph_song | 5770 |
| album_sidecar_track | 4220 |
| graph_artist_anchor | 1875 |
| graph_album | 1670 |
| album_sidecar_album | 340 |
| graph_recording | 281 |

## Links By Match Basis

| key | count |
| --- | ---: |
| apple_song_search_title_artist_year_auto_match | 5489 |
| existing_sidecar_apple_track_id_catalog_validation | 4220 |
| apple_artist_search_top_exact_normalized | 1867 |
| apple_album_search_title_artist_year_auto_match | 1324 |
| graph_song_matched_unique_sidecar_track_artist_title_year | 366 |
| existing_sidecar_apple_collection_id_catalog_validation | 340 |
| graph_album_matched_existing_sidecar_apple_collection_id | 340 |
| apple_song_search_title_artist_auto_match | 115 |
| graph_song_matched_unique_sidecar_track_artist_title_without_year | 81 |
| apple_artist_search_exact_normalized_in_top5 | 8 |
| apple_album_search_title_artist_auto_match | 6 |

## Reviews By Reason

| key | count |
| --- | ---: |
| apple_song_search_no_auto_match | 707 |
| apple_album_search_no_auto_match | 474 |
| apple_song_search_needs_review_version_risk | 404 |
| apple_song_search_no_results | 86 |
| apple_artist_search_no_exact_normalized_result | 19 |
| apple_album_search_no_results | 18 |
| apple_artist_search_no_results | 4 |
| sidecar_track_artist_title_year_ambiguous | 1 |

## Manual Review Preview

| type | artist | title | year | reason |
| --- | --- | --- | --- | --- |
| album | 2Baba | Grass 2 Grace | 2006 | apple_album_search_no_auto_match |
| album | 50 Cent | Get Rich or Die Tryin' | 2003 | apple_album_search_no_auto_match |
| album | 6LACK | Free 6lack | 2016 | apple_album_search_no_auto_match |
| album | 7 Seconds | The Crew | 1984 | apple_album_search_no_auto_match |
| album | A$AP Rocky | Long.Live.A$AP | 2013 | apple_album_search_no_auto_match |
| album | A-ha | Hunting High and Low | 1985 | apple_album_search_no_auto_match |
| album | A Tribe Called Quest | People's Instinctive Travels and the Paths of Rhythm | 1990 | apple_album_search_no_auto_match |
| album | ABBA | Arrival | 1976 | apple_album_search_no_auto_match |
| album | Adam and the Ants | Kings of the Wild Frontier | 1980 | apple_album_search_no_auto_match |
| album | The Adverts | Crossing the Red Sea with The Adverts | 1978 | apple_album_search_no_auto_match |
| album | Alan Silvestri | Back to the Future | 1985 | apple_album_search_no_auto_match |
| album | Alanis Morissette | Jagged Little Pill | 1995 | apple_album_search_no_auto_match |
| album | Ali Farka Toure and Ry Cooder | Talking Timbuktu | 1994 | apple_album_search_no_auto_match |
| album | Alice in Chains | Dirt | 1992 | apple_album_search_no_auto_match |
| album | The Allman Brothers Band | At Fillmore East | 1971 | apple_album_search_no_auto_match |
| album | Andrae Crouch | Live in London | 1978 | apple_album_search_no_auto_match |
| album | Angel Witch | Angel Witch | 1980 | apple_album_search_no_auto_match |
| album | The Animals | The Animals | 1964 | apple_album_search_no_auto_match |
| album | Archers of Loaf | Icky Mettle | 1993 | apple_album_search_no_auto_match |
| album | Aretha Franklin | Amazing Grace | 1972 | apple_album_search_no_auto_match |
