# Family 1 Import Warnings

## Schema Drift Normalized

| area | warning |
|---|---|
| enum/field normalization | Non-enum role(s) `bridge_song` normalized/dropped for song row. |
| enum/field normalization | Non-enum role(s) `regional_anchor_album` normalized/dropped for album row. |

## Duplicate / Membership Semantics

| object class | duplicate canonical IDs across archetypes | import handling |
|---|---:|---|
| artists | 23 | Treat duplicate proposed artist IDs as one canonical artist with multiple archetype memberships. |
| albums | 6 | Treat duplicate proposed album IDs as one canonical album/compilation with multiple archetype memberships. |
| songs | 27 | Treat duplicate proposed song IDs as one recording with multiple archetype memberships unless a warning says versions must split. |

High-risk duplicate/version cases:

| risk | handling |
|---|---|
| `hound-dog` | Do not merge Big Mama Thornton and Elvis Presley recordings. |
| `the-twist` | Do not merge Hank Ballard and Chubby Checker recordings. |
| `shake-rattle-and-roll` | Do not merge Big Joe Turner and Bill Haley recordings. |
| `thats-all-right` | Do not merge Arthur Crudup and Elvis Presley recordings. |
| `blue-suede-shoes` | Preserve Carl Perkins and Elvis Presley recordings as separate survey objects if Elvis is later added in this title lane. |
| `barbara-ann` | Keep Regents original distinct from later Beach Boys cover if/when imported. |
| `sh-boom` | Define split rules for The Chords and The Crew-Cuts/pop-cover versions before title-based merging. |
| `love-potion-no-9` | Preserve The Clovers source version separately from later Searchers/British Invasion cover behavior. |
| `louie-louie` | Keep Kingsmen garage/frat-rock recording distinct from Richard Berry/source and other covers. |
| `the-wailers` | Disambiguate the Pacific Northwest Wailers from Bob Marley and the Wailers. |
| `jimmie-rodgers` | Use `jimmie-rodgers-pop` for the pop singer; do not merge with the country Jimmie Rodgers. |
| `gene-vincent` / Blue Caps | Decide whether to canonicalize early band recordings under `gene-vincent-and-his-blue-caps` or keep Gene Vincent with alias credits. |
| Link Wray / Wraymen / Ray Men | Normalize backing-band credits without creating duplicate Link Wray canonical artists. |
| The Crickets / Buddy Holly and the Crickets | Keep Buddy Holly solo, Crickets, and Buddy Holly and the Crickets alias rules explicit. |
| Jackie Brenston / Ike Turner | Store `Rocket 88` with Jackie Brenston and His Delta Cats while preserving Ike Turner/Kings of Rhythm credit aliases. |

Additional title-collision watchlist: `Bo Diddley`, `The Platters`, `The Raindrops`, `Santo & Johnny`, `Wipe Out`, `Pipeline`, `Telstar`, `California Sun`, `Take Good Care of My Baby`, `Please Mr. Postman`, and `Where Did Our Love Go`.

## Object-Type Warnings

- `compilation`, anthology, and label-comp rows are intentional gateway objects for this era.
- `album_exception` from source was normalized to `studio_album` plus `album_anchor` roles unless the row was explicitly a compilation/anthology/live object.
- Adult-pop/crooner contrast objects should be available for survey disambiguation but should not open a broad crooner family import from Family 1 alone.
- Later-family figures such as James Brown, Otis Redding, Ike & Tina Turner, The Sonics, and The Kingsmen should bridge forward without absorbing later canonical ownership.
