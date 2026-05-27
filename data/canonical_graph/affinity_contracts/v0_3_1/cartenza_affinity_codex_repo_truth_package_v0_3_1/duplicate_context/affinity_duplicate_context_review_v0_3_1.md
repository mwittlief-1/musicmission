# Duplicate and Context-Surface Review v0.3.1

## Purpose

This review supports the schema amendment by identifying graph records where the same composition/year appears under multiple canonical song IDs. These are the cases most likely to need canonical core affinity consistency plus separate membership overlays.

## Summary

- Candidate duplicate/context groups: **29**
- Sparse pilot context-leak flags: **6**
- Review method: grouped `canonical_song_recordings.json` by `composition_key + release_years`.

Some groups may be intentional source-version distinctions. The graph-wide tagging worker must not merge or rewrite graph IDs. It should flag review and keep core song affinity stable when the underlying recording/composition is effectively the same.

## Top duplicate/context candidates

| Composition key | Title | Artist surface | Count | Families | Canonical IDs |
|---|---:|---|---:|---|---|
| `don-t-know-why` | Don't Know Why | Norah Jones / Norah Jones | 3 | [4, 14] | `f4-025-song-don-t-know-why-norah-jones, f4-029-song-don-t-know-why-norah-jones, norah-jones-don-t-know-why` |
| `angel-from-montgomery` | Angel from Montgomery | John Prine / John Prine | 2 | [4, 5] | `f4-027-song-angel-from-montgomery-john-prine, john-prine-angel-from-montgomery` |
| `blowin-in-the-wind` | Blowin' in the Wind | Bob Dylan / Bob Dylan | 2 | [4] | `f4-024-song-blowin-in-the-wind-bob-dylan, f4-026-song-blowin-in-the-wind-bob-dylan` |
| `bohemian-rhapsody` | Bohemian Rhapsody | Queen / Queen | 2 | [3, 17] | `queen-bohemian-rhapsody, song-bohemian-rhapsody-1975` |
| `boulder-to-birmingham` | Boulder to Birmingham | Emmylou Harris / Emmylou Harris | 2 | [4, 5] | `emmylou-harris-boulder-to-birmingham, f4-027-song-boulder-to-birmingham-emmylou-harris` |
| `copperhead-road` | Copperhead Road | Steve Earle / Steve Earle | 2 | [4, 5] | `f4-027-song-copperhead-road-steve-earle, steve-earle-copperhead-road` |
| `cover-me-up` | Cover Me Up | Jason Isbell / Jason Isbell | 2 | [4, 5] | `f4-027-song-cover-me-up-jason-isbell, jason-isbell-cover-me-up` |
| `desperados-waiting-for-a-train` | Desperados Waiting for a Train | Guy Clark / Guy Clark | 2 | [4, 5] | `f4-027-song-desperados-waiting-for-a-train-guy-clark, guy-clark-desperados-waiting-for-a-train` |
| `don-t-stop-believin` | Don't Stop Believin' | Journey / Journey | 2 | [3, 17] | `journey-dont-stop-believin, song-don-t-stop-believin-1981` |
| `fallin` | Fallin' | Alicia Keys / Alicia Keys | 2 | [4, 6] | `alicia-keys-fallin, f4-025-song-fallin-alicia-keys` |
| `fire-and-rain` | Fire and Rain | James Taylor / James Taylor | 2 | [3, 4] | `f4-024-song-fire-and-rain-james-taylor, song-fire-and-rain-1970` |
| `i-ll-take-you-there` | I'll Take You There | Staple Singers / The Staple Singers | 2 | [6, 16] | `staple-singers-ill-take-you-there, the-staple-singers-i-ll-take-you-there` |
| `if-we-were-vampires` | If We Were Vampires | Jason Isbell and the 400 Unit / Jason Isbell and the 400 Unit | 2 | [4, 5] | `f4-027-song-if-we-were-vampires-jason-isbell-and-the-400-unit, jason-isbell-and-the-400-unit-if-we-were-vampires` |
| `iron-man` | Iron Man | Black Sabbath / Black Sabbath | 2 | [3, 9] | `black-sabbath-iron-man, song-iron-man-1970` |
| `it-s-too-late` | It's Too Late | Carole King / Carole King | 2 | [3, 4] | `f4-025-song-it-s-too-late-carole-king, song-its-too-late-1971` |
| `just-what-i-needed` | Just What I Needed | The Cars / The Cars | 2 | [3, 8] | `song-just-what-i-needed-1978, the-cars-just-what-i-needed` |
| `love-shack` | Love Shack | The B-52's / The B-52s | 2 | [8, 17] | `the-b-52-s-love-shack, the-b-52s-love-shack` |
| `pancho-and-lefty` | Pancho and Lefty | Townes Van Zandt / Townes Van Zandt | 2 | [4, 5] | `f4-027-song-pancho-and-lefty-townes-van-zandt, townes-van-zandt-pancho-and-lefty` |
| `paranoid` | Paranoid | Black Sabbath / Black Sabbath | 2 | [3, 9] | `black-sabbath-paranoid, song-paranoid-1970` |
| `piano-man` | Piano Man | Billy Joel / Billy Joel | 2 | [3, 4] | `f4-025-song-piano-man-billy-joel, song-piano-man-1973` |
| `radio-free-europe` | Radio Free Europe | R.E.M. / R.E.M. | 2 | [8, 10] | `r-e-m-radio-free-europe, rem-radio-free-europe` |
| `shake-rattle-and-roll` | Shake, Rattle and Roll | Big Joe Turner / Bill Haley & His Comets | 2 | [1] | `big-joe-turner-shake-rattle-and-roll, bill-haley-and-his-comets-shake-rattle-and-roll` |
| `something-in-the-orange` | Something in the Orange | Zach Bryan / Zach Bryan | 2 | [4, 5] | `f4-027-song-something-in-the-orange-zach-bryan, zach-bryan-something-in-the-orange` |
| `sunday-mornin-comin-down` | Sunday Mornin' Comin' Down | Kris Kristofferson / Kris Kristofferson | 2 | [4, 5] | `f4-027-song-sunday-mornin-comin-down-kris-kristofferson, kris-kristofferson-sunday-mornin-comin-down` |
| `the-one-i-love` | The One I Love | R.E.M. / R.E.M. | 2 | [8, 10] | `r-e-m-the-one-i-love, rem-the-one-i-love` |
| `time-in-a-bottle` | Time in a Bottle | Jim Croce / Jim Croce | 2 | [3, 4] | `f4-024-song-time-in-a-bottle-jim-croce, song-time-in-a-bottle-1972` |
| `turn-turn-turn` | Turn! Turn! Turn! | The Byrds / Pete Seeger / The Byrds | 2 | [2, 4] | `f4-026-song-turn-turn-turn-the-byrds-pete-seeger, the-byrds-turn-turn-turn` |
| `we-don-t-talk-about-bruno` | We Don't Talk About Bruno | Carolina Gaitan, Mauro Castillo, Adassa, Rhenzy Feliz, Diane Guerrero, Stephanie Beatriz and Encanto Cast / Encanto Cast | 2 | [15, 17] | `carolina-gaitan-mauro-castillo-adassa-rhenzy-feliz-diane-guerrero-stephanie-beatriz-and-encanto-cast-we-don-t-talk-about-bruno, encanto-cast-we-dont-talk-about-bruno` |
| `your-song` | Your Song | Elton John / Elton John | 2 | [3, 4] | `f4-025-song-your-song-elton-john, song-your-song-1970` |

## PM-named context leak examples from sparse pilot

### `queen-bohemian-rhapsody` / `song-bohemian-rhapsody-1975`

The two graph surfaces share composition and year but appeared in different family/context surfaces. Core song affinity should not become different just because one surface is shared-listening/karaoke. Karaoke behavior belongs in membership overlays.

### `raffi-baby-beluga`

Family/shared-listening context should not force implausible intrinsic tags. If the song is mainly a family/children/shared-listening object, those traits belong in overlay fields; core tags should be sparse and literal.

## Required handling in graph-wide pass

1. Do not merge canonical IDs.
2. Do not invent IDs.
3. Do not make different intrinsic profiles for the same underlying song/recording unless the graph clearly represents different versions.
4. Put social/routing behavior in membership overlays.
5. Flag candidate groups in `affinity_graphwide_duplicate_context_review_v0_3_1.md`.
