# Family 2 Gap Summary

Scope: Beatles, British Invasion, 60s Pop-Rock.

## Import Shape

| Object class | Existing seed rows | Added missing-obvious rows | Total normalized rows |
|---|---:|---:|---:|
| Artists | 10 | 14 | 24 |
| Albums | 27 | 12 | 39 |
| Songs | 28 | 26 | 54 |

## Filled Gaps

| Gap area | Added coverage | Reason |
|---|---|---|
| Beatles album spine | `a-hard-days-night`, `rubber-soul`, `revolver`, `sgt-peppers-lonely-hearts-club-band` | Source had Beatles artist and psych album objects but missed the invasion-to-album-era progression. |
| Core British Invasion singles | `i-want-to-hold-your-hand`, `a-hard-days-night`, `satisfaction`, `paint-it-black`, `my-generation`, `you-really-got-me` | These are mass-recognition entry points that should not be inferred only from artist rows. |
| British Invasion secondary anchors | The Animals, The Zombies, The Yardbirds, The Dave Clark Five, Herman's Hermits | Adds bridge, contrast, and false-nearby structure around the core four. |
| Folk-rock / harmony-pop anchors | Simon & Garfunkel, The Mamas & the Papas, The Beach Boys, `bookends`, `turn-turn-turn`, `mrs-robinson` | Source had songs and albums but omitted obvious artist-level anchors. |
| Psych and heavy-psych artist anchors | The Jimi Hendrix Experience, Cream, The Doors, Love, Jefferson Airplane-adjacent rows | Source emphasized albums; added artist rows keep navigation from becoming album-only. |
| Art-damaged bridge | The Velvet Underground, `tommy`, `the-who-sell-out`, `the-kinks-are-the-village-green-preservation-society` | Strengthens bridge paths to punk, art rock, new wave, and later alternative lineages. |
| Contrast / false-nearby handling | Herman's Hermits, Dave Clark Five, Procol Harum, Status Quo, Tommy James and the Shondells | Keeps popular 60s pop-rock neighbors visible without overpromoting them as family anchors. |

## Boundary Risks

| Risk | Handling |
|---|---|
| Beach Boys can belong to surf, baroque pop, and psych-pop families. | Kept `pet-sounds` and `good-vibrations` as Family 2 anchors; artist row is a bridge, not exclusive ownership. |
| Dylan and Simon & Garfunkel can belong to folk/singer-songwriter families. | Kept only 60s folk-rock crossover objects and marked bridge roles. |
| Hendrix, Cream, Doors, Who, and Stones can flow into classic rock / hard rock families. | Family 2 rows emphasize 1960s psych, invasion, and album-era transformation. |
| Garage canon is compilation-led and one-hit-heavy. | Preserved `nuggets` as compilation gateway and song-first garage rows rather than inflating artist rows. |
| Distinct versions of shared songs can be collapsed accidentally. | `gloria` is scoped to The Shadows of Knight; import warnings flag that it must not merge with Them/Van Morrison versions. |

## Recommendation

Ready for importer dry-run after schema validation. Do not lock until the source duplicate rows and shorthand terms noted in `corrections_to_source_report.md` and `import_warnings.md` are accepted.

## Second-Pass Cross-Check Addendum

Reviewed `/Users/matt_wittlief_home/Library/Mobile Documents/com~apple~CloudDocs/F2-2.md` after the initial artifact build. Accepted additions: 19 artists, 13 albums, 18 songs. New total rows: 167.

Merge policy: accepted missing-obvious and high-survey-value objects; deferred collector-depth, unstable boundary, and low-recognition rows to later consolidation rather than importing them now.
