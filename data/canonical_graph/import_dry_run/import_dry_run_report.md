# Canonical Graph Import Dry Run

Generated: 2026-05-20

## Status

- Validation errors: 0
- Validation warnings: 9
- Composition/title review rows: 24
- Imported family files: 18
- Expected full corpus: 18 families
- Families remaining: 0

## Family Inputs

| family | scope | artists | albums | songs | total rows |
|---:|---|---:|---:|---:|---:|
| 1 | Early Rock, Oldies, Doo-Wop, Pre-Beatles Pop | 247 | 124 | 377 | 748 |
| 2 | Beatles, British Invasion, 60s Pop-Rock | 43 | 52 | 72 | 167 |
| 3 | Classic Rock, Album Rock, Progressive Rock | 136 | 117 | 150 | 403 |
| 4 | Singer-Songwriter, Folk, Americana, Adult Songcraft | 113 | 85 | 126 | 324 |
| 5 | Country | 88 | 56 | 89 | 233 |
| 6 | Soul, Funk, Disco, R&B Foundations | 107 | 71 | 139 | 317 |
| 7 | Hip-Hop | 97 | 104 | 174 | 375 |
| 8 | Punk, Hardcore, Post-Punk, New Wave | 92 | 81 | 96 | 269 |
| 9 | Metal and Heavy Music | 129 | 139 | 170 | 438 |
| 10 | Alternative, Indie, Grunge, Emo | 98 | 89 | 128 | 315 |
| 11 | Electronic, Dance, Club, Industrial, Experimental Pop | 103 | 70 | 89 | 262 |
| 12 | Pop Monoculture and Persona Pop | 54 | 36 | 50 | 140 |
| 13 | Latin, Caribbean, Global Pop | 84 | 54 | 82 | 220 |
| 14 | Jazz, Standards, Vocal, Classical-Adjacent | 41 | 32 | 43 | 116 |
| 15 | Soundtrack, Theater, Musicals, Family Context | 39 | 33 | 47 | 119 |
| 16 | Christian, Worship, Gospel | 39 | 29 | 44 | 112 |
| 17 | Nostalgia, Novelty, Context, Shared Listening | 35 | 22 | 42 | 99 |
| 18 | Modern Rock, Current Discovery, Internet-Native Scenes | 67 | 51 | 65 | 183 |

## Emitted Tables

| table | rows |
|---|---:|
| canonical_artists.json | 1499 |
| canonical_albums.json | 1207 |
| canonical_song_recordings.json | 1917 |
| artist_archetype_memberships.json | 1612 |
| album_archetype_memberships.json | 1245 |
| song_archetype_memberships.json | 1983 |

## Duplicate Membership Signal

| source rows | duplicate canonical IDs | note |
|---|---:|---|
| artists | 107 | Expected when one artist belongs to multiple archetypes/families. |
| albums | 38 | Expected for shared album gateways. |
| songs | 65 | Expected for shared recordings; title collisions still require review. |

## Warnings

- family 4 song f4-026-song-we-shall-overcome-pete-seeger-et-al-traditional: release_year is `None`
- family 4 song f4-026-song-house-of-the-rising-sun-traditional-revival-circuit-object: release_year is `None`
- artist `kool-and-the-gang` has multiple display/source names: Kool & The Gang; Kool & the Gang
- artist `martha-and-the-vandellas` has multiple display/source names: Martha & the Vandellas; Martha and the Vandellas
- artist `simon-and-garfunkel` has multiple display/source names: Simon & Garfunkel; Simon and Garfunkel
- artist `smokey-robinson-and-the-miracles` has multiple display/source names: Smokey Robinson & The Miracles; Smokey Robinson and the Miracles
- album `the-sonics-here-are-the-sonics` has multiple display/source names: Here Are The Sonics; Here Are the Sonics
- song_recording `martha-and-the-vandellas-dancing-in-the-street` has conflicting `artist_names` values: Martha & the Vandellas; Martha and the Vandellas
- song_recording `shania-twain-man-i-feel-like-a-woman` has conflicting `release_years` values: 1997; 1999

## Errors

- None.

## Next Dispatch Guidance

- Use the emitted canonical entity tables and membership tables as the import contract for the remaining 0 families.
- Do not import family rows directly as unique entities; always route through canonical entity IDs plus membership rows.
- Keep the composition review queue as a human QA queue, not an automatic merge list.
