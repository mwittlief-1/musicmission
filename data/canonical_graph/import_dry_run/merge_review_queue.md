# Merge Review Queue

This queue is generated from title collisions and import-warning snippets. It is intentionally conservative.

## Same-Title Song Recording Review

| composition_key | song_title | artists | canonical_song_recording_ids | reason |
|---|---|---|---|---|
| alison | Alison | Elvis Costello; Slowdive | elvis-costello-alison; slowdive-alison | Same normalized song title appears across multiple artists; review composition versus recording split. |
| blind | Blind | Hercules & Love Affair; Korn | hercules-and-love-affair-blind; korn-blind | Same normalized song title appears across multiple artists; review composition versus recording split. |
| cum-on-feel-the-noize | Cum On Feel the Noize | Quiet Riot; Slade | quiet-riot-cum-on-feel-the-noize; song-cum-on-feel-the-noize-1973 | Same normalized song title appears across multiple artists; review composition versus recording split. |
| cupid | Cupid | FIFTY FIFTY; Sam Cooke | fifty-fifty-cupid; sam-cooke-cupid | Same normalized song title appears across multiple artists; review composition versus recording split. |
| doomsday | Doomsday | Architects; MF DOOM | architects-doomsday; mf-doom-doomsday | Same normalized song title appears across multiple artists; review composition versus recording split. |
| gee | Gee | Girls' Generation; The Crows | girls-generation-gee; the-crows-gee | Same normalized song title appears across multiple artists; review composition versus recording split. |
| gloria | Gloria | Patti Smith; The Cadillacs; The Shadows of Knight; Them | patti-smith-gloria; the-cadillacs-gloria; the-shadows-of-knight-gloria; them-gloria | Same normalized song title appears across multiple artists; review composition versus recording split. |
| god-only-knows | God Only Knows | The Beach Boys; for KING & COUNTRY | for-king-and-country-god-only-knows; the-beach-boys-god-only-knows | Same normalized song title appears across multiple artists; review composition versus recording split. |
| hound-dog | Hound Dog | Big Mama Thornton; Elvis Presley | big-mama-thornton-hound-dog; elvis-presley-hound-dog | Same normalized song title appears across multiple artists; review composition versus recording split. |
| house-of-the-rising-sun | House of the Rising Sun | The Animals; Traditional / revival circuit object | f4-026-song-house-of-the-rising-sun-traditional-revival-circuit-object; the-animals-house-of-the-rising-sun | Same normalized song title appears across multiple artists; review composition versus recording split. |
| i-ll-take-you-there | I'll Take You There | Staple Singers; The Staple Singers | staple-singers-ill-take-you-there; the-staple-singers-i-ll-take-you-there | Same normalized song title appears across multiple artists; review composition versus recording split. |
| lonely-boy | Lonely Boy | Paul Anka; The Black Keys | paul-anka-lonely-boy; the-black-keys-lonely-boy | Same normalized song title appears across multiple artists; review composition versus recording split. |
| love-shack | Love Shack | The B-52's; The B-52s | the-b-52-s-love-shack; the-b-52s-love-shack | Same normalized song title appears across multiple artists; review composition versus recording split. |
| oblivion | Oblivion | Grimes; Mastodon | grimes-oblivion; mastodon-oblivion | Same normalized song title appears across multiple artists; review composition versus recording split. |
| only-you | Only You | The Platters; Yazoo | the-platters-only-you; yazoo-only-you | Same normalized song title appears across multiple artists; review composition versus recording split. |
| push-it | Push It | Salt-N-Pepa; Static-X | salt-n-pepa-push-it; static-x-push-it | Same normalized song title appears across multiple artists; review composition versus recording split. |
| shake-rattle-and-roll | Shake, Rattle and Roll | Big Joe Turner; Bill Haley & His Comets | big-joe-turner-shake-rattle-and-roll; bill-haley-and-his-comets-shake-rattle-and-roll | Same normalized song title appears across multiple artists; review composition versus recording split. |
| stay | Stay | Lisa Loeb; Maurice Williams and the Zodiacs | f4-029-song-stay-lisa-loeb; maurice-williams-and-the-zodiacs-stay | Same normalized song title appears across multiple artists; review composition versus recording split. |
| that-s-all-right | That's All Right | Arthur "Big Boy" Crudup; Elvis Presley | arthur-big-boy-crudup-thats-all-right; elvis-presley-thats-all-right | Same normalized song title appears across multiple artists; review composition versus recording split. |
| the-twist | The Twist | Chubby Checker; Hank Ballard & The Midnighters | chubby-checker-the-twist; hank-ballard-and-the-midnighters-the-twist | Same normalized song title appears across multiple artists; review composition versus recording split. |
| turn-turn-turn | Turn! Turn! Turn! | The Byrds; The Byrds / Pete Seeger | f4-026-song-turn-turn-turn-the-byrds-pete-seeger; the-byrds-turn-turn-turn | Same normalized song title appears across multiple artists; review composition versus recording split. |
| walk-this-way | Walk This Way | Aerosmith; Run-DMC | run-dmc-walk-this-way; song-walk-this-way-1975 | Same normalized song title appears across multiple artists; review composition versus recording split. |
| we-don-t-talk-about-bruno | We Don't Talk About Bruno | Carolina Gaitan, Mauro Castillo, Adassa, Rhenzy Feliz, Diane Guerrero, Stephanie Beatriz and Encanto Cast; Encanto Cast | carolina-gaitan-mauro-castillo-adassa-rhenzy-feliz-diane-guerrero-stephanie-beatriz-and-encanto-cast-we-don-t-talk-about-bruno; encanto-cast-we-dont-talk-about-bruno | Same normalized song title appears across multiple artists; review composition versus recording split. |
| zombie | Zombie | Fela Kuti; The Cranberries | fela-kuti-zombie; the-cranberries-zombie | Same normalized song title appears across multiple artists; review composition versus recording split. |

## Warning Snippets

| family | source | line | note |
|---:|---|---:|---|
| 1 | `data/canonical_graph/family_1/import_warnings.md` | 16 | \| songs \| 27 \| Treat duplicate proposed song IDs as one recording with multiple archetype memberships unless a warning says versions must split. \| |
| 1 | `data/canonical_graph/family_1/import_warnings.md` | 18 | High-risk duplicate/version cases: |
| 1 | `data/canonical_graph/family_1/import_warnings.md` | 22 | \| `hound-dog` \| Do not merge Big Mama Thornton and Elvis Presley recordings. \| |
| 1 | `data/canonical_graph/family_1/import_warnings.md` | 23 | \| `the-twist` \| Do not merge Hank Ballard and Chubby Checker recordings. \| |
| 1 | `data/canonical_graph/family_1/import_warnings.md` | 24 | \| `shake-rattle-and-roll` \| Do not merge Big Joe Turner and Bill Haley recordings. \| |
| 1 | `data/canonical_graph/family_1/import_warnings.md` | 25 | \| `thats-all-right` \| Do not merge Arthur Crudup and Elvis Presley recordings. \| |
| 1 | `data/canonical_graph/family_1/import_warnings.md` | 27 | \| `barbara-ann` \| Keep Regents original distinct from later Beach Boys cover if/when imported. \| |
| 1 | `data/canonical_graph/family_1/import_warnings.md` | 28 | \| `sh-boom` \| Define split rules for The Chords and The Crew-Cuts/pop-cover versions before title-based merging. \| |
| 1 | `data/canonical_graph/family_1/import_warnings.md` | 29 | \| `love-potion-no-9` \| Preserve The Clovers source version separately from later Searchers/British Invasion cover behavior. \| |
| 1 | `data/canonical_graph/family_1/import_warnings.md` | 30 | \| `louie-louie` \| Keep Kingsmen garage/frat-rock recording distinct from Richard Berry/source and other covers. \| |
| 1 | `data/canonical_graph/family_1/import_warnings.md` | 31 | \| `the-wailers` \| Disambiguate the Pacific Northwest Wailers from Bob Marley and the Wailers. \| |
| 1 | `data/canonical_graph/family_1/import_warnings.md` | 32 | \| `jimmie-rodgers` \| Use `jimmie-rodgers-pop` for the pop singer; do not merge with the country Jimmie Rodgers. \| |
| 1 | `data/canonical_graph/family_1/import_warnings.md` | 33 | \| `gene-vincent` / Blue Caps \| Decide whether to canonicalize early band recordings under `gene-vincent-and-his-blue-caps` or keep Gene Vincent with alias credits. \| |
| 1 | `data/canonical_graph/family_1/import_warnings.md` | 35 | \| The Crickets / Buddy Holly and the Crickets \| Keep Buddy Holly solo, Crickets, and Buddy Holly and the Crickets alias rules explicit. \| |
| 1 | `data/canonical_graph/family_1/import_warnings.md` | 36 | \| Jackie Brenston / Ike Turner \| Store `Rocket 88` with Jackie Brenston and His Delta Cats while preserving Ike Turner/Kings of Rhythm credit aliases. \| |
| 10 | `data/canonical_graph/family_10/import_warnings.md` | 28 | \| `green-day-good-riddance-time-of-your-life` \| Acoustic/context use should not split away from Green Day recording without version evidence. \| |
| 11 | `data/canonical_graph/family_11/import_warnings.md` | 7 | ## Merge / Alias / Version Risks |
| 11 | `data/canonical_graph/family_11/import_warnings.md` | 10 | - Producer aliases and project names require explicit alias tables: Larry Heard/Mr. Fingers/Fingers Inc., Juan Atkins/Model 500/Cybotron, Kevin Saunderson/Inner City. |
| 11 | `data/canonical_graph/family_11/import_warnings.md` | 11 | - Club rows often need mix/edit specificity; single titles can refer to radio edits, original mixes, remixes, live/DJ-set versions, or viral clips. |
| 11 | `data/canonical_graph/family_11/import_warnings.md` | 31 | - Lock still requires source-aligned row review, Page 1/Page 2 ordering, and merge-table confirmation for aliases, covers, remixes, collaborations, live recordings, and language/version variants. |
| 12 | `data/canonical_graph/family_12/import_warnings.md` | 16 | \| songs \| 0 \| Treat duplicate proposed song IDs as one recording unless a warning says versions must split. \| |
| 12 | `data/canonical_graph/family_12/import_warnings.md` | 22 | \| `beyonce` solo vs group-era credits \| Do not merge Destiny-era recordings into solo Beyonce without explicit alias/member handling. \| |
| 13 | `data/canonical_graph/family_13/import_warnings.md` | 7 | ## Merge / Alias / Version Risks |
| 13 | `data/canonical_graph/family_13/import_warnings.md` | 10 | - Language versions, remixes, and collaboration credits are high-risk in Family 13: `Despacito`, `Bailando`, `Danza Kuduro`, `Love Nwantiti`, `AMG`, `Bebe Dame`, and `7 Seconds` need recording-level care. |
| 13 | `data/canonical_graph/family_13/import_warnings.md` | 12 | - Afrobeat, Afrobeats, Afropiano, African pop, and global-roots rows must remain distinct enough for adaptive survey interpretation. |
| 13 | `data/canonical_graph/family_13/import_warnings.md` | 14 | - World-fusion rows such as Deep Forest require sampling/ethics/version review before import lock. |
| 13 | `data/canonical_graph/family_13/import_warnings.md` | 31 | - Lock still requires source-aligned row review, Page 1/Page 2 ordering, and merge-table confirmation for aliases, covers, remixes, collaborations, live recordings, and language/version variants. |
| 14 | `data/canonical_graph/family_14/import_warnings.md` | 12 | ## Merge / Alias / Version Risks |
| 14 | `data/canonical_graph/family_14/import_warnings.md` | 14 | - Louis Armstrong: Jazz, standards, New Orleans, and pop-memory memberships should remain distinct. |
| 14 | `data/canonical_graph/family_14/import_warnings.md` | 35 | - My Favorite Things - John Coltrane: Preserve Coltrane recording distinct from musical-theater composition. |
| 14 | `data/canonical_graph/family_14/import_warnings.md` | 37 | - Nessun dorma - Luciano Pavarotti: Opera aria/composition must remain distinct from Pavarotti recording. |
| 14 | `data/canonical_graph/family_14/import_warnings.md` | 38 | - Cello Suite No. 1: Prelude - Yo-Yo Ma: Composition vs recording distinction required. |
| 14 | `data/canonical_graph/family_14/import_warnings.md` | 44 | - The Girl from Ipanema - Stan Getz and Astrud Gilberto: Bossa nova, jazz, and lounge rows should remain distinct. |
| 14 | `data/canonical_graph/family_14/import_warnings.md` | 54 | - Largest remaining gap: The largest remaining gap is recording-level standard attribution: many songs need composition, definitive recording, and holiday/context split rules before hard lock. |
| 14 | `data/canonical_graph/family_14/import_warnings.md` | 55 | - Duplicate object IDs across families should be interpreted as multi-membership unless a warning says the display names or source versions conflict. |
| 15 | `data/canonical_graph/family_15/import_warnings.md` | 12 | ## Merge / Alias / Version Risks |
| 15 | `data/canonical_graph/family_15/import_warnings.md` | 14 | - Claude-Michel Schonberg: Composer/show-first object; do not merge with cast recordings. |
| 15 | `data/canonical_graph/family_15/import_warnings.md` | 27 | - Ludwig Goransson: Score and hip-hop/R&B soundtrack album rows should remain distinct. |
| 15 | `data/canonical_graph/family_15/import_warnings.md` | 33 | - Guardians of the Galaxy: Awesome Mix Vol. 1 - Various Artists: Compilation soundtrack made of older songs; do not merge with original release albums. |
| 15 | `data/canonical_graph/family_15/import_warnings.md` | 36 | - Black Panther - Ludwig Goransson: Score album distinct from Kendrick Lamar-curated soundtrack album. |
| 15 | `data/canonical_graph/family_15/import_warnings.md` | 38 | - I Will Always Love You - Whitney Houston: Preserve Whitney Houston recording distinct from Dolly Parton original. |
| 15 | `data/canonical_graph/family_15/import_warnings.md` | 43 | - We Don't Talk About Bruno - Carolina Gaitan, Mauro Castillo, Adassa, Rhenzy Feliz, Diane Guerrero, Stephanie Beatriz and Encanto Cast: Ensemble cast credit is version-specific and should not merge to one artist. |
| 15 | `data/canonical_graph/family_15/import_warnings.md` | 44 | - Remember Me - Benjamin Bratt: Coco has multiple in-film versions; preserve recording context. |
| 15 | `data/canonical_graph/family_15/import_warnings.md` | 48 | - Man of Constant Sorrow - The Soggy Bottom Boys: Film-fictional group and traditional/roots song attribution need review. |
| 15 | `data/canonical_graph/family_15/import_warnings.md` | 50 | - James Bond Theme - John Barry Orchestra: Bond theme authorship and performance credits require manual review. |
| 15 | `data/canonical_graph/family_15/import_warnings.md` | 55 | - Duplicate object IDs across families should be interpreted as multi-membership unless a warning says the display names or source versions conflict. |
| 16 | `data/canonical_graph/family_16/import_warnings.md` | 12 | ## Merge / Alias / Version Risks |
| 16 | `data/canonical_graph/family_16/import_warnings.md` | 14 | - Sister Rosetta Tharpe: Gospel, early rock and roll, and blues memberships should remain linked but distinct. |
| 16 | `data/canonical_graph/family_16/import_warnings.md` | 19 | - Passion: Conference/live worship brand needs distinct entity handling. |
| 16 | `data/canonical_graph/family_16/import_warnings.md` | 22 | - In Christ Alone - Keith and Kristyn Getty: Modern hymn/songbook row; many church versions exist. |
| 16 | `data/canonical_graph/family_16/import_warnings.md` | 24 | - People - Hillsong United: Hillsong Worship, Hillsong United, and church-brand rows should remain distinct. |
| 16 | `data/canonical_graph/family_16/import_warnings.md` | 25 | - Amazing Grace - Aretha Franklin: Composition vs Aretha live recording must remain distinct. |
| 16 | `data/canonical_graph/family_16/import_warnings.md` | 26 | - Soon and Very Soon - Andrae Crouch: Gospel standard has many church and choir versions. |
| 16 | `data/canonical_graph/family_16/import_warnings.md` | 28 | - Break Every Chain - Tasha Cobbs Leonard: Worship standard and live gospel recording should remain distinct. |
| 16 | `data/canonical_graph/family_16/import_warnings.md` | 29 | - God's Not Dead (Like a Lion) - Newsboys: Newsboys cover/version should not merge with original Daniel Bashta worship song. |
| 16 | `data/canonical_graph/family_16/import_warnings.md` | 31 | - Shout to the Lord - Darlene Zschech: Church-songbook standard with many Hillsong and congregation versions. |
| 16 | `data/canonical_graph/family_16/import_warnings.md` | 33 | - In Christ Alone - Keith and Kristyn Getty: Modern hymn should be standard-first and version-aware. |
| 16 | `data/canonical_graph/family_16/import_warnings.md` | 35 | - Jireh - Elevation Worship and Maverick City Music featuring Chandler Moore and Naomi Raine: Collaboration and featured-vocal credits need manual handling. |
| 16 | `data/canonical_graph/family_16/import_warnings.md` | 37 | - Build My Life - Pat Barrett: Modern worship standard with many artist and church versions. |
| 16 | `data/canonical_graph/family_16/import_warnings.md` | 42 | - Largest remaining gap: The largest remaining gap is worship standard/version policy: live, church-brand, songwriter, and congregational versions need explicit import split rules. |
| 16 | `data/canonical_graph/family_16/import_warnings.md` | 43 | - Duplicate object IDs across families should be interpreted as multi-membership unless a warning says the display names or source versions conflict. |
| 17 | `data/canonical_graph/family_17/import_warnings.md` | 16 | \| songs \| 0 \| Treat duplicate proposed song IDs as one recording unless a warning says versions must split. \| |
| 17 | `data/canonical_graph/family_17/import_warnings.md` | 26 | \| Traditional/kids repertoire \| Composition-level objects need non-artist canonical handling where performer is not meaningful. \| |
| 18 | `data/canonical_graph/family_18/import_warnings.md` | 12 | ## Merge / Alias / Version Risks |
| 18 | `data/canonical_graph/family_18/import_warnings.md` | 14 | - Turnstile: Hardcore, alternative, and current-rock memberships should remain distinct. |
| 18 | `data/canonical_graph/family_18/import_warnings.md` | 28 | - Beggin' - Maneskin: Preserve Maneskin recording distinct from Four Seasons original. |
| 18 | `data/canonical_graph/family_18/import_warnings.md` | 38 | - Duplicate object IDs across families should be interpreted as multi-membership unless a warning says the display names or source versions conflict. |
| 2 | `data/canonical_graph/family_2/import_warnings.md` | 21 | \| `the-shadows-of-knight-gloria` \| Cover/version-specific row; do not merge with Them's `Gloria`. \| |
| 2 | `data/canonical_graph/family_2/import_warnings.md` | 23 | \| `the-animals-house-of-the-rising-sun` \| Arrangement/recording-specific row; do not merge with traditional-song records. \| |
| 2 | `data/canonical_graph/family_2/import_warnings.md` | 47 | Normalized prior `artist_seeded`, `artist_added`, `artist_not_added`, and `artist_ambiguous_or_traditional` song status shorthand into the requested `artist_survey_worthy`, `song_survey_first`, and `song_survey_only` enum. |
| 3 | `data/canonical_graph/family_3/import_warnings.md` | 26 | \| ambiguous_versions \| Live vs studio versions and cover-adjacent later memories are not merged. \| Requires downstream version-aware matching. \| |
| 4 | `data/canonical_graph/family_4/import_warnings.md` | 9 | \| date_normalization \| 1940/1944, 20th c., traditional, 1998/2000 US breakthrough \| release_year uses an integer where defensible and null where attribution/date is traditional or unstable; row warnings preserve ambiguity. \| |
| 4 | `data/canonical_graph/family_4/import_warnings.md` | 10 | \| collaboration_and_version_risk \| Wilco with Billy Bragg, Pete Seeger et al. / traditional, Pete Seeger and Lee Hays; Peter Paul and Mary popularized, Jason Isbell and the 400 Unit \| Artist name retained as supplied when needed; import should not collapse collaborations into solo artist rows without manual confirmation. \| |
| 4 | `data/canonical_graph/family_4/import_warnings.md` | 11 | \| duplicate_cross_archetype_objects \| Carole King, Bob Dylan, John Prine, Norah Jones, Tapestry, The Freewheelin Bob Dylan, Come Away with Me, Blowin in the Wind, Dont Know Why \| Kept as separate archetype placements with distinct proposed IDs. Consolidation should happen only at a later canonical entity layer. \| |
| 4 | `data/canonical_graph/family_4/import_warnings.md` | 20 | Normalized prior `artist_seeded`, `artist_added`, `artist_not_added`, and `artist_ambiguous_or_traditional` song status shorthand into the requested `artist_survey_worthy`, `song_survey_first`, and `song_survey_only` enum. |
| 5 | `data/canonical_graph/family_5/import_warnings.md` | 7 | ## Merge / Alias / Version Risks |
| 5 | `data/canonical_graph/family_5/import_warnings.md` | 11 | - `Wagon Wheel`, `Tennessee Whiskey`, `Act Naturally`, `Me and Bobby McGee`, and `How Do I Live` require composition/recording/version handling. |
| 5 | `data/canonical_graph/family_5/import_warnings.md` | 12 | - Darius Rucker solo catalog must remain distinct from Hootie & the Blowfish. |
| 5 | `data/canonical_graph/family_5/import_warnings.md` | 23 | \| 034 \| Bridge to line dance, hat-act radio, new traditionalism, and patriotic/bar contexts; false-nearby risk is mistaking novelty recognition for artist depth. \| |
| 5 | `data/canonical_graph/family_5/import_warnings.md` | 31 | - Lock still requires source-aligned row review, Page 1/Page 2 ordering, and merge-table confirmation for aliases, covers, remixes, collaborations, live recordings, and language/version variants. |
| 6 | `data/canonical_graph/family_6/import_warnings.md` | 11 | \| era_specific_artist_scope \| Bee Gees disco-era; Diana Ross solo; Smokey Robinson solo versus Miracles; Jackson 5 versus Michael Jackson \| Preserve artist/era distinction through row warnings and proposed IDs. Do not auto-merge group and solo objects. \| |
| 6 | `data/canonical_graph/family_6/import_warnings.md` | 12 | \| version_specific_recordings \| Respect; Ain't No Mountain High Enough; I Heard It Through the Grapevine; Don't Leave Me This Way; Tyrone live \| Preserve recording/version identity rather than merging by composition title. \| |
| 7 | `data/canonical_graph/family_7/import_warnings.md` | 20 | \| Alias rows \| `2Pac`, `The Notorious B.I.G.`, `Mos Def / Yasiin Bey`, `Jeezy`, and `Afrika Bambaataa & Soulsonic Force` require alias-aware matching. \| |
| 7 | `data/canonical_graph/family_7/import_warnings.md` | 23 | ## Explicit, Clean, And Version Warnings |
| 7 | `data/canonical_graph/family_7/import_warnings.md` | 30 | \| cardi-b-feat-megan-thee-stallion-wap \| Explicit and clean versions are materially different survey objects. \| |
| 7 | `data/canonical_graph/family_7/import_warnings.md` | 32 | \| run-dmc-walk-this-way \| Run-DMC/Aerosmith version must not merge with Aerosmith original recording. \| |
| 7 | `data/canonical_graph/family_7/import_warnings.md` | 33 | \| fugees-killing-me-softly \| Fugees version must not merge with Roberta Flack or earlier recordings. \| |
| 7 | `data/canonical_graph/family_7/import_warnings.md` | 36 | \| chief-keef-feat-lil-reese-i-dont-like \| Original and Kanye remix should remain distinct if both are imported. \| |
| 8 | `data/canonical_graph/family_8/import_warnings.md` | 7 | ## Merge / Alias / Version Risks |
| 8 | `data/canonical_graph/family_8/import_warnings.md` | 10 | - Soft Cell: Preserve Soft Cell recording distinct from Gloria Jones original. |
| 8 | `data/canonical_graph/family_8/import_warnings.md` | 11 | - Patti Smith: Preserve Patti Smith recording distinct from Them/Van Morrison original. |
| 8 | `data/canonical_graph/family_8/import_warnings.md` | 15 | - James Chance / James White / Contortions aliases need review. |
| 8 | `data/canonical_graph/family_8/import_warnings.md` | 16 | - Public Image Ltd should remain distinct from Sex Pistols even though John Lydon links both identities. |
| 8 | `data/canonical_graph/family_8/import_warnings.md` | 17 | - Love and Rockets should remain distinct from Bauhaus. |
| 8 | `data/canonical_graph/family_8/import_warnings.md` | 18 | - Split Enz should remain distinct from Crowded House. |
| 8 | `data/canonical_graph/family_8/import_warnings.md` | 19 | - Yazoo/Yaz alias handling is required. |
| 9 | `data/canonical_graph/family_9/import_warnings.md` | 21 | \| `sleep / sleep-token` \| Do not merge Sleep with Sleep Token. \| |
| 9 | `data/canonical_graph/family_9/import_warnings.md` | 23 | \| `hurt` \| Nine Inch Nails song row must remain distinct from Johnny Cash cover/version rows in other families. \| |
| 9 | `data/canonical_graph/family_9/import_warnings.md` | 24 | \| `cum-on-feel-the-noize` \| Quiet Riot row is a cover/version-specific glam-metal gateway; do not merge with Slade original if imported elsewhere. \| |
