# Family 1 Gap Summary

Scope: Early Rock, Oldies, Doo-Wop, Pre-Beatles Pop.

Source package: `/Users/matt_wittlief_home/Library/Mobile Documents/com~apple~CloudDocs/waymark_family_1_latest_corpus_for_codex_2026-05-19.md`

Note: no Family 1 zip was found in the iCloud root; the latest one-file Family 1 corpus was used as the controlling source package.

## Import Shape

| Object class | Existing seed rows | Added missing-obvious rows | Total normalized rows |
|---|---:|---:|---:|
| Artists | 175 | 72 | 247 |
| Albums | 90 | 34 | 124 |
| Songs | 298 | 79 | 377 |

## Archetype Coverage

| archetype_id | archetype | artists | albums | songs | structural note |
|---|---|---:|---:|---:|---|
| 001 | Early Rock & Roll Foundations | 35 | 21 | 65 | Broad central foundation now robust; main risk is source-version handling overwhelming Page 1. |
| 002 | Rockabilly / Primitive Guitar / Proto-Garage | 33 | 16 | 53 | Adequate and intentionally smaller; keep collector rockabilly mostly Page 3. |
| 003 | Doo-Wop / Vocal Group Oldies | 37 | 15 | 51 | Strong song-first doo-wop coverage; album surface should stay compilation-led. |
| 004 | Teen Idol / Early Pop-Rock Radio | 34 | 16 | 52 | Strong teen-idol/radio-pop coverage; adult-pop boundary must remain capped. |
| 005 | Brill Building / Girl Group / Early 60s Pop Craft | 34 | 18 | 49 | Girl-group/Brill coverage improved; Motown and pop-soul overlap needs membership handling. |
| 006 | Early Soul-Pop / R&B Crossover | 39 | 19 | 55 | Robust early soul-pop/R&B bridge; later soul/funk ownership remains the lock blocker. |
| 007 | Surf / Instrumental / Early Guitar Pop | 35 | 19 | 52 | Instrumental/surf/hot-rod coverage improved; artist rows should not overtake song-first logic. |

## Filled Gaps

| Gap area | Added coverage | Reason |
|---|---|---|
| Pre-1954 R&B, gospel, and jump-blues roots | Sister Rosetta Tharpe, Jackie Brenston, Big Joe Turner, Big Mama Thornton, Louis Jordan, Wynonie Harris, Arthur Crudup | Keeps the origin layer from being reduced to later white-rock hit versions. |
| Raw rockabilly and primitive guitar Page 2 | Warren Smith, Ronnie Self, The Rock-A-Teens, The Phantom, Collins Kids | Adds boundary/contrast objects without making the archetype collector-only. |
| Doo-wop song-first long tail | Orioles, Harptones, Channels, Jive Five, Capris, Mello-Kings, Randy & The Rainbows | Matches the era where song recognition often exceeds artist recognition. |
| Teen-idol and adult-pop boundary | Pat Boone, Johnny Mathis, Little Peggy March, Kathy Young, Johnny Burnette solo | Helps Survey Page 2 separate clean-pop preference from rock/R&B preference. |
| Girl-group / Brill / Spector ecosystem | Chantels, Bobbettes, Dee Dee Sharp, Raindrops, Ikettes, Velvelettes, Spector/girl-group anthologies | Adds craft, dance-craze, and label-comp gateways. |
| Early soul-pop / R&B crossover | Ruth Brown, Hank Ballard, Arthur Alexander, James Brown, Bobby Bland, Irma Thomas, Ike & Tina, Otis | Strengthens bridge paths into later soul families while keeping Family 1 early-period scope. |
| Surf / instrumental / hot-rod one-hits | Santo & Johnny, Johnny and the Hurricanes, Tornados, Rivieras, Routers, Revels, Atlantics | Restores normal-user instrumental memory and soundtrack/frat-rock bridge value. |

## Boundary Risks

| Risk | Handling |
|---|---|
| Source versions vs mass versions | `Hound Dog`, `Shake, Rattle and Roll`, `The Twist`, `That's All Right`, and `Rocket 88` are recording-specific rows, not title merges. |
| Artist duplicates across archetypes | Repeated IDs are archetype memberships; importer should create one canonical entity plus membership rows. |
| Compilations and anthologies | Doo-wop, girl-group, surf, and R&B source-code lanes need compilation gateways as canonical survey objects. |
| Adult-pop sprawl | Pat Boone, Johnny Mathis, and similar rows are contrast/boundary rows, not a license to import the whole crooner canon. |
| Later-family ownership | James Brown, Otis Redding, Ike & Tina, Beach/surf, garage, and proto-soul objects should bridge forward without claiming later-family totality. |

## Recommendation

Family 1 is staging-ready for an importer dry run. Do not hard-lock until the importer confirms canonical entity plus archetype-membership semantics, version-aware recording handling, and alias/split rules for the named merge risks.
