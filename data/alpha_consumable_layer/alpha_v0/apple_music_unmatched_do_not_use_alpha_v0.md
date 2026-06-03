# Apple Music Unmatched Do-Not-Use Alpha v0

Alpha contract version: `alpha_v0`

Generated: 2026-06-01T14:00:04.299Z

Status: `do_not_use_no_apple_id_status_applied`

Canonical graph rows stay in the graph. For Alpha playback and default Mission Generation, any song without an Apple Music catalog ID is marked `do_not_use_no_apple_id` until resolver work clears it.

## Summary

| metric | count |
| --- | ---: |
| canonical grid rows | 11710 |
| canonical grid rows with Apple ID | 11417 |
| canonical grid rows do_not_use_no_apple_id | 291 |
| active graph song rows | 7018 |
| active graph song rows with Apple ID | 6828 |
| active graph song rows do_not_use_no_apple_id | 190 |
| active graph recording rows | 399 |
| active graph playback rows | 7417 |
| active graph playback rows with Apple ID | 7206 |
| active graph playback rows do_not_use_no_apple_id | 211 |
| active survey song candidates | 1574 |
| active survey song candidates with Apple ID | 1500 |
| active survey song candidates do_not_use_no_apple_id | 74 |

## Product Rule

Rows without an Apple Music catalog ID may remain in the canonical mission universe for QA/resolver visibility but must not feed Survey display, Alpha playback, playback-route selection, Supabase active playback candidates, OpenAI playback payloads, or Apple Music auto-resolution.

The full canonical grid remains the mission-item universe; this file only gates unresolved playback rows.

## Blocked Surfaces

- default Mission Generation
- Supabase active candidates
- OpenAI prompt payloads
- app playback
- Apple Music auto-resolution

## First Survey-Surface Examples

| candidate_id | family | display | bucket |
| --- | ---: | --- | --- |
| survey-f2-song_recording-the-beatles-strawberry-fields-forever-013 | 2 | Strawberry Fields Forever | page1_core |
| survey-f2-song_recording-the-byrds-mr-tambourine-man-009 | 2 | Mr. Tambourine Man | page2_adaptive |
| survey-f2-song_recording-spencer-davis-group-gimme-some-lovin-008 | 2 | Gimme Some Lovin' | page2_adaptive |
| survey-f2-song_recording-manfred-mann-do-wah-diddy-diddy-008 | 2 | Do Wah Diddy Diddy | page2_adaptive |
| survey-f3-song_recording-song-refugee-1979-016 | 3 | Refugee | page2_adaptive |
| survey-f3-song_recording-song-owner-of-a-lonely-heart-1983-018 | 3 | Owner of a Lonely Heart | page2_adaptive |
| survey-f3-song_recording-song-i-keep-forgettin-1982-023 | 3 | I Keep Forgettin' | page3_deep |
| survey-f3-song_recording-song-shes-gone-1973-022 | 3 | She's Gone | page3_deep |
| survey-f3-song_recording-song-hanging-on-the-telephone-1976-021 | 3 | Hanging on the Telephone | page3_deep |
| survey-f3-song_recording-song-baby-come-back-1977-023 | 3 | Baby Come Back | page3_deep |
| survey-f3-song_recording-song-can-the-can-1973-020 | 3 | Can the Can | page3_deep |
| survey-f4-song_recording-f4-026-song-if-i-had-a-hammer-pete-seeger-and-lee-hays-peter-paul-and-mary-popularized-026 | 4 | If I Had a Hammer | page2_adaptive |
| survey-f4-song_recording-f4-024-song-both-sides-now-joni-mitchell-024 | 4 | Both Sides Now | page2_adaptive |
| survey-f4-song_recording-f4-025-song-brick-ben-folds-five-025 | 4 | Brick | page3_deep |
| survey-f4-song_recording-f4-024-song-me-and-bobby-mcgee-kris-kristofferson-024 | 4 | Me and Bobby McGee | page3_deep |
| survey-f4-song_recording-f4-026-song-there-but-for-fortune-phil-ochs-026 | 4 | There But for Fortune | page3_deep |
| survey-f4-song_recording-f4-026-song-deportee-woody-guthrie-026 | 4 | Deportee | page3_deep |
| survey-f4-song_recording-f4-027-song-gulf-coast-highway-nanci-griffith-027 | 4 | Gulf Coast Highway | page3_deep |
| survey-f4-song_recording-f4-028-song-too-far-to-care-old-97-s-028 | 4 | Too Far to Care | page3_deep |
| survey-f5-song_recording-garth-brooks-friends-in-low-places-034 | 5 | Friends in Low Places | page1_core |
| survey-f5-song_recording-kenny-rogers-and-dolly-parton-islands-in-the-stream-033 | 5 | Islands in the Stream | page2_adaptive |
| survey-f5-song_recording-lady-a-need-you-now-033 | 5 | Need You Now | page2_adaptive |
| survey-f5-song_recording-garth-brooks-the-dance-034 | 5 | The Dance | page2_adaptive |
| survey-f5-song_recording-kris-kristofferson-me-and-bobby-mcgee-032 | 5 | Me and Bobby McGee | page2_adaptive |
| survey-f5-song_recording-david-allan-coe-you-never-even-called-me-by-my-name-032 | 5 | You Never Even Called Me by My Name | page3_deep |
| survey-f6-song_recording-marvin-gaye-and-tammi-terrell-aint-no-mountain-high-enough-037 | 6 | Ain't No Mountain High Enough | page2_adaptive |
| survey-f6-song_recording-sylvester-you-make-me-feel-mighty-real-040 | 6 | You Make Me Feel (Mighty Real) | page3_deep |
| survey-f6-song_recording-erykah-badu-tyrone-live-043 | 6 | Tyrone | page3_deep |
| survey-f7-song_recording-afrika-bambaataa-and-soulsonic-force-planet-rock-045 | 7 | Planet Rock | page2_adaptive |
| survey-f7-song_recording-nwa-fuck-tha-police-047 | 7 | Fuck tha Police | page2_adaptive |

## First Graphwide Examples

| candidate_identity_key | display | family |
| --- | --- | --- |
| song|eddie cochran|something else | Eddie Cochran - Something Else | Early Rock, Oldies, Doo-Wop, Pre-Beatles Pop |
| song|cookies|don t say nothin bad | The Cookies - Don't Say Nothin' Bad | Early Rock, Oldies, Doo-Wop, Pre-Beatles Pop |
| song|sunrays|i live for the sun | The Sunrays - I Live for the Sun | Early Rock, Oldies, Doo-Wop, Pre-Beatles Pop |
| song|nerves|hanging on the telephone | The Nerves - Hanging on the Telephone | Classic Rock, Album Rock, Progressive Rock |
| song|traditional revival circuit object|house of the rising sun | Traditional / revival circuit object - House of the Rising Sun | Singer-Songwriter, Folk, Americana, Adult Songcraft |
| song|jayhawks|waiting for a superman | The Jayhawks - Waiting for a Superman | Singer-Songwriter, Folk, Americana, Adult Songcraft |
| song|woody guthrie|deportee | Woody Guthrie - Deportee | Singer-Songwriter, Folk, Americana, Adult Songcraft |
| song|old 97 s|too far to care | Old 97's - Too Far to Care | Singer-Songwriter, Folk, Americana, Adult Songcraft |
| song|garth brooks|friends in low places | Garth Brooks - Friends in Low Places | Country |
| song|garth brooks|dance | Garth Brooks - The Dance | Country |
| song|erykah badu|tyrone | Erykah Badu - Tyrone | Soul, Funk, Disco, R&B Foundations |
| song|salt n pepa|push it | Salt-N-Pepa - Push It | Hip-Hop |
| song|n w a|fuck tha police | N.W.A - Fuck tha Police | Hip-Hop |
| song|future|fuck up some commas | Future - Fuck Up Some Commas | Hip-Hop |
| song|x ray spex|oh bondage up yours | X-Ray Spex - Oh Bondage Up Yours! | Punk, Hardcore, Post-Punk, New Wave |
| song|liz phair|fuck and run | Liz Phair - Fuck and Run | Alternative, Indie, Grunge, Emo |
| song|lil louis|french kiss | Lil Louis - French Kiss | Electronic, Dance, Club, Industrial, Experimental Pop |
| song|nightcrawlers|push the feeling on | Nightcrawlers - Push the Feeling On | Electronic, Dance, Club, Industrial, Experimental Pop |
| song|robin s|show me love | Robin S. - Show Me Love | Electronic, Dance, Club, Industrial, Experimental Pop |
| song|basic channel|phylyps trak ii | Basic Channel - Phylyps Trak II | Electronic, Dance, Club, Industrial, Experimental Pop |
| song|orbital|halcyon on and on | Orbital - Halcyon On and On | Electronic, Dance, Club, Industrial, Experimental Pop |
| song|underground resistance|jupiter jazz | Underground Resistance - Jupiter Jazz | Electronic, Dance, Club, Industrial, Experimental Pop |
| song||me and giuliani down by the school yard | !!! - Me and Giuliani Down by the School Yard | Electronic, Dance, Club, Industrial, Experimental Pop |
| song|grupo frontera|no se va | Grupo Frontera - No Se Va | Latin, Caribbean, Global Pop |
| song|soggy bottom boys|man of constant sorrow | The Soggy Bottom Boys - Man of Constant Sorrow | Soundtrack, Theater, Musicals, Family Context |
| song|matt redman|10 000 reasons bless the lord | Matt Redman - 10,000 Reasons (Bless the Lord) | Christian, Worship, Gospel |
| song|trans siberian orchestra|christmas eve sarajevo 12 24 | Trans-Siberian Orchestra - Christmas Eve/Sarajevo 12/24 | Nostalgia, Novelty, Context, Shared Listening |
| song|garth brooks|friends in low places | Garth Brooks - Friends in Low Places | Nostalgia, Novelty, Context, Shared Listening |
| song|los del rio|macarena | Los Del Rio - Macarena | Nostalgia, Novelty, Context, Shared Listening |
| song|lion king cast|hakuna matata | The Lion King Cast - Hakuna Matata | Nostalgia, Novelty, Context, Shared Listening |
