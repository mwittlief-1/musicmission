# Waymark Canonical Graph Review Bundle v0.1

Generated: 2026-05-20

Status: staging-consolidated, schema-clean, not final-lock ready.

This bundle is derived from current dry-run outputs and normalized family files. Alias and version counts are derived from QA queues and warning notes because final alias/version sidecar tables do not exist yet.

## Dataset Inventory

| metric | value | basis |
| --- | --- | --- |
| total artists | 1499 | canonical_artists.json |
| total albums | 1207 | canonical_albums.json |
| total song recordings | 1917 | canonical_song_recordings.json |
| total composition groups | 1865 | unique composition_key values |
| total archetypes | 120 | normalized family metadata plus Family 2 fallback |
| total families | 18 | expected 18 / imported 18 |
| total memberships / edges | 4840 | artists 1612 + albums 1245 + songs 1983 |
| total aliases | 11 | explicit alias/name issues; 30 total alias/merge QA issues |
| total source-version / cover-version groups | 73 | warning-derived version/source/cover/cast/traditional notes |
| validation errors | 0 | import dry run |
| validation warnings | 9 | import dry run |

## Family Summary Table

| family_id | family_name | artist_count | album_count | song_recording_count | archetype_count | lock_status | known risks |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Early Rock, Oldies, Doo-Wop, Pre-Beatles Pop | 247 | 124 | 377 | 7 | staging yes / hard-lock no | medium risk; Source-version split rules and early artist aliases. |
| 2 | Beatles, British Invasion, 60s Pop-Rock | 43 | 52 | 72 | 8 | staging yes / hard-lock no | medium risk; British Invasion covers and cross-family ownership. |
| 3 | Classic Rock, Album Rock, Progressive Rock | 136 | 117 | 150 | 8 | staging yes / hard-lock no | medium risk; Duplicate-membership semantics and Page 2 bloat. |
| 4 | Singer-Songwriter, Folk, Americana, Adult Songcraft | 113 | 85 | 126 | 7 | staging yes / hard-lock no | high risk; Traditional/protest standards and null/unstable years. |
| 5 | Country | 88 | 56 | 89 | 6 | staging yes / hard-lock no | medium risk; No aligned row-level source seeds and country edge coverage. |
| 6 | Soul, Funk, Disco, R&B Foundations | 107 | 71 | 139 | 8 | staging yes / hard-lock no | medium risk; Motown group/solo, disco-era, and R&B version splits. |
| 7 | Hip-Hop | 97 | 104 | 174 | 8 | staging yes / hard-lock no | high risk; Explicit/clean/remix/collaboration version policy. |
| 8 | Punk, Hardcore, Post-Punk, New Wave | 92 | 81 | 96 | 8 | staging yes / hard-lock no | medium risk; Targeted depth pass complete; alias/version consolidation and cross-family boundary QA remain. |
| 9 | Metal and Heavy Music | 129 | 139 | 170 | 8 | staging yes / hard-lock no | medium risk; Extreme/deep metal coverage and cover-version gateways. |
| 10 | Alternative, Indie, Grunge, Emo | 98 | 89 | 128 | 12 | staging yes / hard-lock no | medium risk; Boundary with Families 8, 9, 11, and 18. |
| 11 | Electronic, Dance, Club, Industrial, Experimental Pop | 103 | 70 | 89 | 7 | staging yes / hard-lock no | high risk; Club alias/mix/edit specificity and missing regional club scenes. |
| 12 | Pop Monoculture and Persona Pop | 54 | 36 | 50 | 6 | staging yes / hard-lock no | medium risk; Persona-pop recency and solo/group credits. |
| 13 | Latin, Caribbean, Global Pop | 84 | 54 | 82 | 6 | staging yes / hard-lock no | high risk; Uneven regional coverage and language/remix variants. |
| 14 | Jazz, Standards, Vocal, Classical-Adjacent | 41 | 32 | 43 | 4 | staging yes / hard-lock no | high risk; Standards need composition/recording split. |
| 15 | Soundtrack, Theater, Musicals, Family Context | 39 | 33 | 47 | 4 | staging yes / hard-lock no | high risk; Show/film/cast/composer entity model. |
| 16 | Christian, Worship, Gospel | 39 | 29 | 44 | 3 | staging yes / hard-lock no | high risk; Worship standard/version policy. |
| 17 | Nostalgia, Novelty, Context, Shared Listening | 35 | 22 | 42 | 4 | staging yes / hard-lock no | high risk; Traditional/kids/holiday repertoire often lacks meaningful performer ownership. |
| 18 | Modern Rock, Current Discovery, Internet-Native Scenes | 67 | 51 | 65 | 6 | staging yes / hard-lock no | medium risk; Recency volatility and internet-native shelf stability. |

## Archetype Summary Table

| archetype_id | family_id | archetype_name | primary survey purpose | primary object type | count by object type | top 10 artist anchors | top 20 song anchors | overlap risks | boundary risks |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 001 | 1 | Early Rock & Roll Foundations | song-first recognition and branching | song | A:35 / Al:21 / S:65 | Chuck Berry; Elvis Presley; Little Richard; Buddy Holly; The Everly Brothers; Roy Orbison; The Drifters; The Platters; Dion; Chubby Checker | Rock Around the Clock — Bill Haley & His Comets; Johnny B. Goode — Chuck Berry; Heartbreak Hotel — Elvis Presley; Hound Dog — Elvis Presley; Jailhouse Rock — Elvis Presley; The Twist — Chubby Checker; Don't Be Cruel — Elvis Presley; Tutti Frutti — Little Richard; That'll Be the Day — Buddy Holly; Blue Suede Shoes — Carl Perkins; All Shook Up — Elvis Presley; La Bamba — Ritchie Valens; Blueberry Hill — Fats Domino; Great Balls of Fire — Jerry Lee Lewis; Runaway — Del Shannon; Summertime Blues — Eddie Cochran; Whole Lotta Shakin' Goin' On — Jerry Lee Lewis; Save the Last Dance for Me — The Drifters; Bye Bye Love — The Everly Brothers; Only You — The Platters | 32 multi-membership overlaps | 12 boundary/contrast rows |
| 002 | 1 | Rockabilly / Primitive Guitar / Proto-Garage | song-first recognition and branching | song | A:33 / Al:16 / S:53 | Johnny Cash; Carl Perkins; Gene Vincent; Link Wray; Eddie Cochran; Duane Eddy; Jerry Lee Lewis; Bo Diddley; The Kingsmen; Roy Orbison | Blue Suede Shoes — Carl Perkins; Be-Bop-A-Lula — Gene Vincent; Rumble — Link Wray; Summertime Blues — Eddie Cochran; Rebel-'Rouser — Duane Eddy; Susie Q — Dale Hawkins; Misirlou — Dick Dale and His Del-Tones; Train Kept A-Rollin' — Johnny Burnette and the Rock 'n Roll Trio; Matchbox — Carl Perkins; Race with the Devil — Gene Vincent; C'mon Everybody — Eddie Cochran; Forty Miles of Bad Road — Duane Eddy; Louie Louie — The Kingsmen; Walk, Don't Run — The Ventures; Folsom Prison Blues — Johnny Cash; Surfin' Bird — The Trashmen; I Fought the Law — The Bobby Fuller Four; Mystery Train — Elvis Presley; Honey Don't — Carl Perkins; Let's Have a Party — Wanda Jackson | 32 multi-membership overlaps | 13 boundary/contrast rows |
| 003 | 1 | Doo-Wop / Vocal Group Oldies | song-first recognition and branching | mixed | A:37 / Al:15 / S:51 | The Platters; The Drifters; Frankie Lymon and the Teenagers; The Marcels; The Flamingos; The Five Satins; The Penguins; The Coasters; The Del-Vikings; Little Anthony and the Imperials | Earth Angel — The Penguins; Sh-Boom — The Chords; In the Still of the Night — The Five Satins; I Only Have Eyes for You — The Flamingos; Only You — The Platters; Why Do Fools Fall in Love — Frankie Lymon and the Teenagers; The Great Pretender — The Platters; Stay — Maurice Williams and the Zodiacs; Come Go with Me — The Del-Vikings; Tears on My Pillow — Little Anthony and the Imperials; 16 Candles — The Crests; Smoke Gets in Your Eyes — The Platters; Barbara Ann — The Regents; Since I Don't Have You — The Skyliners; Silhouettes — The Rays; Get a Job — The Silhouettes; Duke of Earl — Gene Chandler; Blue Moon — The Marcels; A Teenager in Love — Dion and the Belmonts; Book of Love — The Monotones | 12 multi-membership overlaps | 5 boundary/contrast rows |
| 004 | 1 | Teen Idol / Early Pop-Rock Radio | song-first recognition and branching | song | A:34 / Al:16 / S:52 | Ricky Nelson; Paul Anka; Neil Sedaka; Brenda Lee; Connie Francis; Lesley Gore; Johnny Mathis; Bobby Vee; Bobby Rydell; Frankie Avalon | Diana — Paul Anka; Poor Little Fool — Ricky Nelson; Travelin' Man — Ricky Nelson; Breaking Up Is Hard to Do — Neil Sedaka; Hello Mary Lou — Ricky Nelson; It's My Party — Lesley Gore; Take Good Care of My Baby — Bobby Vee; Calendar Girl — Neil Sedaka; Put Your Head on My Shoulder — Paul Anka; The Night Has a Thousand Eyes — Bobby Vee; Where the Boys Are — Connie Francis; Venus — Frankie Avalon; I'm Sorry — Brenda Lee; Stupid Cupid — Connie Francis; Town Without Pity — Gene Pitney; Sheila — Tommy Roe; Sealed with a Kiss — Brian Hyland; Poetry in Motion — Johnny Tillotson; Let's Dance — Chris Montez; Happy Birthday Sweet Sixteen — Neil Sedaka | 8 multi-membership overlaps | 10 boundary/contrast rows |
| 005 | 1 | Brill Building / Girl Group / Early 60s Pop Craft | album-world and gateway testing | mixed | A:34 / Al:18 / S:49 | The Shirelles; The Ronettes; The Crystals; The Chiffons; The Shangri-Las; The Dixie Cups; The Marvelettes; Lesley Gore; Little Eva; Dionne Warwick | Be My Baby — The Ronettes; Will You Love Me Tomorrow — The Shirelles; It's My Party — Lesley Gore; Da Doo Ron Ron — The Crystals; Then He Kissed Me — The Crystals; Chapel of Love — The Dixie Cups; Leader of the Pack — The Shangri-Las; The Loco-Motion — Little Eva; He's So Fine — The Chiffons; One Fine Day — The Chiffons; He's a Rebel — The Crystals; Please Mr. Postman — The Marvelettes; Baby It's You — The Shirelles; You Don't Own Me — Lesley Gore; My Boyfriend's Back — The Angels; A Lover's Concerto — The Toys; Tell Him — The Exciters; Baby, I Love You — The Ronettes; Mama Said — The Shirelles; Remember (Walking in the Sand) — The Shangri-Las | 13 multi-membership overlaps | 5 boundary/contrast rows |
| 006 | 1 | Early Soul-Pop / R&B Crossover | song-first recognition and branching | mixed | A:39 / Al:19 / S:55 | Ray Charles; Sam Cooke; Ben E. King; Jackie Wilson; The Drifters; Smokey Robinson and the Miracles; Martha and the Vandellas; The Isley Brothers; James Brown & The Famous Flames; Mary Wells | Stand by Me — Ben E. King; What'd I Say — Ray Charles; You Send Me — Sam Cooke; Shout — The Isley Brothers; Hit the Road Jack — Ray Charles; Dancing in the Street — Martha and the Vandellas; Cupid — Sam Cooke; Save the Last Dance for Me — The Drifters; Spanish Harlem — Ben E. King; At Last — Etta James; Lonely Teardrops — Jackie Wilson; Heat Wave — Martha and the Vandellas; Twistin' the Night Away — Sam Cooke; Shop Around — Smokey Robinson and the Miracles; My Guy — Mary Wells; Georgia on My Mind — Ray Charles; You've Really Got a Hold on Me — Smokey Robinson and the Miracles; Up on the Roof — The Drifters; Twist and Shout — The Isley Brothers; Money (That's What I Want) — Barrett Strong | 26 multi-membership overlaps | 5 boundary/contrast rows |
| 007 | 1 | Surf / Instrumental / Early Guitar Pop | song-first recognition and branching | song | A:35 / Al:19 / S:52 | The Beach Boys; Dick Dale and His Del-Tones; The Ventures; Jan and Dean; The Chantays; The Surfaris; Santo & Johnny; The Tornados; The Trashmen; Johnny and the Hurricanes | Surfin' U.S.A. — The Beach Boys; Wipe Out — The Surfaris; Surfin' Safari — The Beach Boys; Pipeline — The Chantays; Misirlou — Dick Dale and His Del-Tones; Fun, Fun, Fun — The Beach Boys; I Get Around — The Beach Boys; Surf City — Jan and Dean; California Girls — The Beach Boys; Don't Worry Baby — The Beach Boys; Surfer Girl — The Beach Boys; Walk, Don't Run — The Ventures; Little Deuce Coupe — The Beach Boys; Dead Man's Curve — Jan and Dean; The Little Old Lady (from Pasadena) — Jan and Dean; G.T.O. — Ronny and the Daytonas; Hey Little Cobra — The Rip Chords; Let's Go Trippin' — Dick Dale and His Del-Tones; Little Honda — The Hondells; Surfin' Bird — The Trashmen | 15 multi-membership overlaps | 5 boundary/contrast rows |
| 008 | 2 | British Invasion / Core UK Beat Groups | song-first recognition and branching | song | A:12 / Al:3 / S:18 | The Beatles; The Rolling Stones; The Who; The Kinks; The Animals; The Yardbirds; Small Faces; Gerry and the Pacemakers; Manfred Mann; Spencer Davis Group | I Want to Hold Your Hand — The Beatles; (I Can't Get No) Satisfaction — The Rolling Stones; House of the Rising Sun — The Animals; You Really Got Me — The Kinks; My Generation — The Who; A Hard Day's Night — The Beatles; Wild Thing — The Troggs; Gimme Some Lovin' — Spencer Davis Group; Ferry Cross the Mersey — Gerry and the Pacemakers; Do Wah Diddy Diddy — Manfred Mann; She's Not There — The Zombies; Because — The Dave Clark Five; For Your Love — The Yardbirds; Gloria — Them; We Gotta Get Out of This Place — The Animals; All Day and All of the Night — The Kinks; Glad All Over — The Dave Clark Five; Friday on My Mind — The Easybeats | none obvious | 4 boundary/contrast rows |
| 009 | 2 | Jangle Pop / Folk-Rock Precursor | mixed survey coverage | mixed | A:3 / Al:0 / S:3 | The Byrds; The Hollies; The Searchers | Mr. Tambourine Man — The Byrds; Needles and Pins — The Searchers; Bus Stop — The Hollies | none obvious | thin contrast set |
| 010 | 2 | Folk-Rock / Harmony Pop / 60s Songcraft | album-world and gateway testing | mixed | A:6 / Al:5 / S:6 | Bob Dylan; Simon & Garfunkel; Buffalo Springfield; The Mamas & the Papas; The Lovin' Spoonful; Donovan | For What It's Worth — Buffalo Springfield; California Dreamin' — The Mamas & the Papas; Mrs. Robinson — Simon & Garfunkel; Yesterday — The Beatles; Turn! Turn! Turn! — The Byrds; Do You Believe in Magic — The Lovin' Spoonful | 1 multi-membership overlaps | thin contrast set |
| 011 | 2 | Garage Rock / Nuggets / Proto-Punk Singles | song-first recognition and branching | song | A:3 / Al:3 / S:12 | Paul Revere & the Raiders; The Kingsmen; The Sonics | Louie Louie — The Kingsmen; 96 Tears — ? and the Mysterians; Psychotic Reaction — Count Five; Kicks — Paul Revere & the Raiders; I Had Too Much to Dream (Last Night) — The Electric Prunes; Pushin' Too Hard — The Seeds; Dirty Water — The Standells; Gloria — The Shadows of Knight; A Question of Temperature — The Balloon Farm; Action Woman — The Litter; Talk Talk — The Music Machine; Little Girl — Syndicate of Sound | 4 multi-membership overlaps | thin contrast set |
| 012 | 2 | Baroque Pop / Chamber Pop / Artful 60s Pop | album-world and gateway testing | song | A:5 / Al:5 / S:8 | The Zombies; Procol Harum; Love; The Moody Blues (early); Bee Gees (early) | God Only Knows — The Beach Boys; Time of the Season — The Zombies; Wouldn't It Be Nice — The Beach Boys; Never My Love — The Association; A Whiter Shade of Pale — Procol Harum; Walk Away Renee — The Left Banke; Pretty Ballerina — The Left Banke; My World Fell Down — Sagittarius | none obvious | 3 boundary/contrast rows |
| 013 | 2 | Psychedelic Pop / Sunshine Pop / Late-60s Pop-Rock | boundary and contrast calibration | song | A:3 / Al:9 / S:14 | The Beach Boys; The Monkees; The Turtles | Good Vibrations — The Beach Boys; Strawberry Fields Forever — The Beatles; Happy Together — The Turtles; Penny Lane — The Beatles; Somebody to Love — Jefferson Airplane; White Rabbit — Jefferson Airplane; Itchycoo Park — Small Faces; Incense and Peppermints — Strawberry Alarm Clock; Sunshine Superman — Donovan; Green Tambourine — The Lemon Pipers; Hurdy Gurdy Man — Donovan; Crimson and Clover — Tommy James and the Shondells; Pictures of Matchstick Men — Status Quo; Yellow Balloon — The Yellow Balloon | 1 multi-membership overlaps | 5 boundary/contrast rows |
| 014 | 2 | Heavy Psych / Blues-Rock / Acid Rock | album-world and gateway testing | mixed | A:7 / Al:11 / S:8 | The Jimi Hendrix Experience; The Doors; Cream; Iron Butterfly; Steppenwolf; Big Brother and the Holding Company; Grateful Dead | Light My Fire — The Doors; Purple Haze — The Jimi Hendrix Experience; Sunshine of Your Love — Cream; Paint It, Black — The Rolling Stones; Born to Be Wild — Steppenwolf; In-A-Gadda-Da-Vida — Iron Butterfly; Piece of My Heart — Big Brother and the Holding Company; You're Gonna Miss Me — 13th Floor Elevators | none obvious | thin contrast set |
| 015 | 2 | Art-Rock / Proto-Alternative / Freak Underground | boundary and contrast calibration | album | A:4 / Al:16 / S:3 | The Velvet Underground; The United States of America; Nico; The Fugs | I Wanna Be Your Dog — The Stooges; White Light/White Heat — The Velvet Underground; Open My Eyes — Nazz | none obvious | 13 boundary/contrast rows |
| 016 | 3 | Classic Rock / Album-Rock Spine | album-world and gateway testing | mixed | A:21 / Al:19 / S:23 | Led Zeppelin; Pink Floyd; Eagles; Fleetwood Mac; Queen; Elton John; Billy Joel; Aerosmith; Creedence Clearwater Revival; Tom Petty and the Heartbreakers | Stairway to Heaven — Led Zeppelin; Hotel California — Eagles; Dreams — Fleetwood Mac; Bohemian Rhapsody — Queen; Fortunate Son — Creedence Clearwater Revival; Bad Moon Rising — Creedence Clearwater Revival; Old Time Rock and Roll — Bob Seger; Piano Man — Billy Joel; Rocket Man — Elton John; Baba O'Riley — The Who; More Than a Feeling — Boston; Sweet Emotion — Aerosmith; Go Your Own Way — Fleetwood Mac; Barracuda — Heart; Sultans of Swing — Dire Straits; Refugee — Tom Petty and the Heartbreakers; American Girl — Tom Petty and the Heartbreakers; Don't Stop Believin' — Journey; The Joker — Steve Miller Band; Show Me the Way (live) — Peter Frampton | 19 multi-membership overlaps | 5 boundary/contrast rows |
| 017 | 3 | Hard Rock / Riff Rock / Proto-Metal | album-world and gateway testing | mixed | A:19 / Al:17 / S:20 | Led Zeppelin; AC/DC; Black Sabbath; Aerosmith; Deep Purple; Heart; Thin Lizzy; Van Halen; Alice Cooper; Kiss | Back in Black — AC/DC; Highway to Hell — AC/DC; Iron Man — Black Sabbath; Whole Lotta Love — Led Zeppelin; Paranoid — Black Sabbath; Smoke on the Water — Deep Purple; Walk This Way — Aerosmith; Barracuda — Heart; The Boys Are Back in Town — Thin Lizzy; Runnin' with the Devil — Van Halen; School's Out — Alice Cooper; Rock and Roll All Nite — Kiss; (Don't Fear) The Reaper — Blue Oyster Cult; All Right Now — Free; Mississippi Queen — Mountain; Slow Ride — Foghat; We're an American Band — Grand Funk Railroad; Since You Been Gone — Rainbow; Doctor Doctor — UFO; Easy Livin' — Uriah Heep | 5 multi-membership overlaps | 5 boundary/contrast rows |
| 018 | 3 | Progressive Rock / Art-Prog Canon | boundary and contrast calibration | mixed | A:21 / Al:20 / S:22 | Pink Floyd; Yes; Genesis; Rush; Jethro Tull; The Moody Blues; King Crimson; Emerson, Lake & Palmer; Kansas; Electric Light Orchestra | Money — Pink Floyd; Tom Sawyer — Rush; Roundabout — Yes; Wish You Were Here — Pink Floyd; Owner of a Lonely Heart — Yes; Mr. Blue Sky — Electric Light Orchestra; Carry On Wayward Son — Kansas; Aqualung — Jethro Tull; Nights in White Satin — The Moody Blues; Lucky Man — Emerson, Lake & Palmer; Solsbury Hill — Peter Gabriel; Tubular Bells — Mike Oldfield; Hocus Pocus — Focus; 21st Century Schizoid Man — King Crimson; 2112 Overture / The Temples of Syrinx — Rush; Firth of Fifth — Genesis; Carpet Crawlers — Genesis; Karn Evil 9 1st Impression Pt. 2 — Emerson, Lake & Palmer; The Low Spark of High Heeled Boys — Traffic; Northern Lights — Renaissance | 2 multi-membership overlaps | 15 boundary/contrast rows |
| 019 | 3 | Southern Rock / Roots Jam Rock | boundary and contrast calibration | mixed | A:11 / Al:10 / S:12 | Lynyrd Skynyrd; The Allman Brothers Band; ZZ Top; Marshall Tucker Band; Little Feat; 38 Special; Molly Hatchet; Gov't Mule; Charlie Daniels Band; The Black Crowes | Sweet Home Alabama — Lynyrd Skynyrd; Free Bird — Lynyrd Skynyrd; Whipping Post — The Allman Brothers Band; Ramblin' Man — The Allman Brothers Band; La Grange — ZZ Top; Midnight Rider — The Allman Brothers Band; Can't You See — Marshall Tucker Band; Jessica — The Allman Brothers Band; Remedy — The Black Crowes; Dixie Chicken — Little Feat; Green Grass and High Tides — Outlaws; Flirtin' with Disaster — Molly Hatchet | none obvious | 8 boundary/contrast rows |
| 020 | 3 | Glam Rock / Theatrical Seventies Rock | album-world and gateway testing | mixed | A:13 / Al:12 / S:15 | David Bowie; Queen; T. Rex; Roxy Music; Sweet; Slade; Lou Reed; Mott the Hoople; Suzi Quatro; The Runaways | Starman — David Bowie; Walk on the Wild Side — Lou Reed; Bang a Gong (Get It On) — T. Rex; Rebel Rebel — David Bowie; Killer Queen — Queen; Ballroom Blitz — Sweet; 20th Century Boy — T. Rex; All the Young Dudes — Mott the Hoople; Cum On Feel the Noize — Slade; Suffragette City — David Bowie; Fox on the Run — Sweet; Love Is the Drug — Roxy Music; Cherry Bomb — The Runaways; Virginia Plain — Roxy Music; Can the Can — Suzi Quatro | 3 multi-membership overlaps | 4 boundary/contrast rows |
| 021 | 3 | Power Pop / Melodic Guitar Pop | album-world and gateway testing | mixed | A:15 / Al:12 / S:17 | Cheap Trick; Big Star; Badfinger; Raspberries; The Cars; The Knack; Todd Rundgren; The Romantics; Tommy Tutone; Marshall Crenshaw | I Want You to Want Me (live) — Cheap Trick; My Sharona — The Knack; What I Like About You — The Romantics; Surrender — Cheap Trick; Just What I Needed — The Cars; September Gurls — Big Star; 867-5309/Jenny — Tommy Tutone; Go All the Way — Raspberries; Come and Get It — Badfinger; No Matter What — Badfinger; Cruel to Be Kind — Nick Lowe; In the Street — Big Star; Hanging on the Telephone — The Nerves; Thirteen — Big Star; Shake Some Action — Flamin' Groovies; Tonight — Raspberries; Someday, Someway — Marshall Crenshaw | none obvious | 3 boundary/contrast rows |
| 022 | 3 | Soft Rock / AM Gold / Adult Pop | album-world and gateway testing | mixed | A:22 / Al:16 / S:24 | Elton John; Billy Joel; Fleetwood Mac; Eagles; Chicago; Carpenters; Hall & Oates; Carole King; James Taylor; America | Your Song — Elton John; Dreams — Fleetwood Mac; Piano Man — Billy Joel; Tiny Dancer — Elton John; Fire and Rain — James Taylor; You're So Vain — Carly Simon; It's Too Late — Carole King; Rocket Man — Elton John; Just the Way You Are — Billy Joel; Take It Easy — Eagles; If You Leave Me Now — Chicago; Landslide — Fleetwood Mac; Baker Street — Gerry Rafferty; Time in a Bottle — Jim Croce; A Horse with No Name — America; Sister Golden Hair — America; Make It with You — Bread; Lowdown — Boz Scaggs; She's Gone — Hall & Oates; Summer Breeze — Seals & Crofts | 15 multi-membership overlaps | 2 boundary/contrast rows |
| 023 | 3 | Yacht Rock / Smooth Studio Pop | album-world and gateway testing | mixed | A:14 / Al:11 / S:17 | Steely Dan; The Doobie Brothers; Christopher Cross; Toto; Boz Scaggs; Michael McDonald; Kenny Loggins; Robbie Dupree; Player; Pablo Cruise | What a Fool Believes — The Doobie Brothers; Sailing — Christopher Cross; Africa — Toto; Peg — Steely Dan; Ride Like the Wind — Christopher Cross; Rosanna — Toto; Minute by Minute — The Doobie Brothers; Lowdown — Boz Scaggs; I Keep Forgettin' — Michael McDonald; This Is It — Kenny Loggins; Steal Away — Robbie Dupree; Reelin' in the Years — Steely Dan; Biggest Part of Me — Ambrosia; Baby Come Back — Player; Deacon Blues — Steely Dan; Love Will Find a Way — Pablo Cruise; I Just Wanna Stop — Gino Vannelli | 4 multi-membership overlaps | 7 boundary/contrast rows |
| 024 | 4 | Classic singer-songwriter | album-world and gateway testing | mixed | A:18 / Al:12 / S:19 | Carole King; James Taylor; Cat Stevens; Paul Simon; Joni Mitchell; Leonard Cohen; Jackson Browne; John Prine; Bob Dylan; Neil Young | Fire and Rain — James Taylor; You've Got a Friend — Carole King; American Pie — Don McLean; Big Yellow Taxi — Joni Mitchell; Wild World — Cat Stevens; Time in a Bottle — Jim Croce; Cat's in the Cradle — Harry Chapin; Heart of Gold — Neil Young; Blowin' in the Wind — Bob Dylan; Both Sides Now — Joni Mitchell; Peace Train — Cat Stevens; At Seventeen — Janis Ian; If You Could Read My Mind — Gordon Lightfoot; Suzanne — Leonard Cohen; Running on Empty — Jackson Browne; Father and Son — Cat Stevens; Vincent — Don McLean; Operator — Jim Croce; Me and Bobby McGee — Kris Kristofferson | none obvious | thin contrast set |
| 025 | 4 | Piano pop and adult songcraft | album-world and gateway testing | mixed | A:14 / Al:11 / S:17 | Carole King; Billy Joel; Randy Newman; Elton John; Norah Jones; Harry Nilsson; Ben Folds; Sara Bareilles; Fiona Apple; Marc Cohn | Piano Man — Billy Joel; It's Too Late — Carole King; Your Song — Elton John; Don't Know Why — Norah Jones; Without You — Harry Nilsson; Love Song — Sara Bareilles; She's Always a Woman — Billy Joel; The Way It Is — Bruce Hornsby and the Range; Walking in Memphis — Marc Cohn; Short People — Randy Newman; Brick — Ben Folds Five; Fallin' — Alicia Keys; Daniel — Elton John; A Thousand Miles — Vanessa Carlton; Someone Like You — Adele; Superman — Five for Fighting; Criminal — Fiona Apple | none obvious | 6 boundary/contrast rows |
| 026 | 4 | Folk revival and protest folk | song-first recognition and branching | mixed | A:15 / Al:8 / S:18 | Bob Dylan; Pete Seeger; Woody Guthrie; Joan Baez; Odetta; Phil Ochs; Peter, Paul and Mary; Judy Collins; Arlo Guthrie; Buffy Sainte-Marie | This Land Is Your Land — Woody Guthrie; Blowin' in the Wind — Bob Dylan; We Shall Overcome — Pete Seeger et al. / traditional; The Times They Are A-Changin' — Bob Dylan; If I Had a Hammer — Pete Seeger and Lee Hays; Peter, Paul and Mary popularized; Where Have All the Flowers Gone — Pete Seeger; Tom Dooley — The Kingston Trio; Goodnight, Irene — The Weavers; Universal Soldier — Buffy Sainte-Marie; Alice's Restaurant Massacree — Arlo Guthrie; 500 Miles — Peter, Paul and Mary; Turn! Turn! Turn! — The Byrds / Pete Seeger; House of the Rising Sun — Traditional / revival circuit object; Early Morning Rain — Gordon Lightfoot; Little Boxes — Malvina Reynolds; Freedom — Richie Havens; There But for Fortune — Phil Ochs; Deportee — Woody Guthrie | none obvious | 3 boundary/contrast rows |
| 027 | 4 | Country-folk and Americana roots | album-world and gateway testing | mixed | A:15 / Al:11 / S:19 | John Prine; Emmylou Harris; Lucinda Williams; Gillian Welch; Townes Van Zandt; Guy Clark; Steve Earle; Lyle Lovett; Jason Isbell; Nanci Griffith | Pancho and Lefty — Townes Van Zandt; Angel from Montgomery — John Prine; If I Needed You — Townes Van Zandt; Boulder to Birmingham — Emmylou Harris; Hello in There — John Prine; Passionate Kisses — Lucinda Williams; Copperhead Road — Steve Earle; If We Were Vampires — Jason Isbell and the 400 Unit; Cover Me Up — Jason Isbell; Orphan Girl — Gillian Welch; Our Town — Iris DeMent; Trouble in the Fields — Nanci Griffith; Desperados Waiting for a Train — Guy Clark; Speed of the Sound of Loneliness — John Prine; Sunday Mornin' Comin' Down — Kris Kristofferson; Something in the Orange — Zach Bryan; L.A. Freeway — Guy Clark; Gulf Coast Highway — Nanci Griffith; Dublin Blues — Guy Clark | none obvious | thin contrast set |
| 028 | 4 | Alt-country and No Depression | album-world and gateway testing | mixed | A:13 / Al:11 / S:14 | Son Volt; Old 97's; Uncle Tupelo; Whiskeytown; Wilco; Drive-By Truckers; The Jayhawks; Ryan Adams; Lucero; The Bottle Rockets | Windfall — Son Volt; Timebomb — Old 97's; No Depression — Uncle Tupelo; Still Be Around — Uncle Tupelo; Barrier Reef — Old 97's; 16 Days — Whiskeytown; Jacksonville Skyline — Whiskeytown; California Stars — Wilco with Billy Bragg; Outfit — Drive-By Truckers; Drown — Son Volt; Passenger Side — Wilco; New Madrid — Uncle Tupelo; Too Far to Care — Old 97's; Waiting for a Superman — The Jayhawks | none obvious | 2 boundary/contrast rows |
| 029 | 4 | Adult alternative and coffeehouse songcraft | album-world and gateway testing | mixed | A:20 / Al:16 / S:22 | Tracy Chapman; Sheryl Crow; Sarah McLachlan; Indigo Girls; Shawn Colvin; Jewel; Norah Jones; Natalie Merchant; Jack Johnson; David Gray | Fast Car — Tracy Chapman; Give Me One Reason — Tracy Chapman; If It Makes You Happy — Sheryl Crow; Closer to Fine — Indigo Girls; Building a Mystery — Sarah McLachlan; Sunny Came Home — Shawn Colvin; Mr. Jones — Counting Crows; You Were Meant for Me — Jewel; Don't Know Why — Norah Jones; Angel — Sarah McLachlan; Everyday Is a Winding Road — Sheryl Crow; Babylon — David Gray; Better Together — Jack Johnson; Wonder — Natalie Merchant; Galileo — Indigo Girls; One of Us — Joan Osborne; Iris — Goo Goo Dolls; Crash Into Me — Dave Matthews Band; Stay — Lisa Loeb; Barely Breathing — Duncan Sheik | none obvious | 2 boundary/contrast rows |
| 030 | 4 | Modern indie folk and folk-pop | album-world and gateway testing | mixed | A:18 / Al:16 / S:17 | Mumford & Sons; The Lumineers; Bon Iver; Fleet Foxes; Iron & Wine; Sufjan Stevens; Noah Kahan; The Avett Brothers; Of Monsters and Men; Vance Joy | Ho Hey — The Lumineers; Little Lion Man — Mumford & Sons; Skinny Love — Bon Iver; Holocene — Bon Iver; White Winter Hymnal — Fleet Foxes; I Will Wait — Mumford & Sons; Stick Season — Noah Kahan; Ophelia — The Lumineers; Riptide — Vance Joy; Home — Edward Sharpe and the Magnetic Zeros; Little Talks — Of Monsters and Men; I and Love and You — The Avett Brothers; Flightless Bird, American Mouth — Iron & Wine; Take Me to Church — Hozier; The Night We Met — Lord Huron; Rivers and Roads — The Head and the Heart; Let Her Go — Passenger | none obvious | 5 boundary/contrast rows |
| 031 | 5 | Classic Country / Honky-Tonk / Nashville Foundations | album-world and gateway testing | mixed | A:14 / Al:9 / S:16 | Johnny Cash; Patsy Cline; Hank Williams; George Jones; Loretta Lynn; Tammy Wynette; Charley Pride; Marty Robbins; Roger Miller; Jimmie Rodgers | Ring of Fire — Johnny Cash; Crazy — Patsy Cline; He Stopped Loving Her Today — George Jones; I'm So Lonesome I Could Cry — Hank Williams; Your Cheatin' Heart — Hank Williams; Coal Miner's Daughter — Loretta Lynn; I Fall to Pieces — Patsy Cline; Stand by Your Man — Tammy Wynette; El Paso — Marty Robbins; Kiss an Angel Good Mornin' — Charley Pride; King of the Road — Roger Miller; Act Naturally — Buck Owens; Blue Yodel No. 1 (T for Texas) — Jimmie Rodgers; Wildwood Flower — The Carter Family; Walking the Floor Over You — Ernest Tubb; It Wasn't God Who Made Honky Tonk Angels — Kitty Wells | 1 multi-membership overlaps | 2 boundary/contrast rows |
| 032 | 5 | Outlaw Country / Cosmic Country | boundary and contrast calibration | mixed | A:13 / Al:9 / S:15 | Willie Nelson; Merle Haggard; Waylon Jennings; Emmylou Harris; Jerry Jeff Walker; Gram Parsons; Kris Kristofferson; Billy Joe Shaver; John Prine; Guy Clark | Mammas Don't Let Your Babies Grow Up to Be Cowboys — Waylon Jennings and Willie Nelson; On the Road Again — Willie Nelson; Mama Tried — Merle Haggard; Blue Eyes Crying in the Rain — Willie Nelson; Me and Bobby McGee — Kris Kristofferson; Luckenbach, Texas (Back to the Basics of Love) — Waylon Jennings; You Never Even Called Me by My Name — David Allan Coe; Angel from Montgomery — John Prine; Okie from Muskogee — Merle Haggard; Boulder to Birmingham — Emmylou Harris; Sunday Mornin' Comin' Down — Kris Kristofferson; Up Against the Wall, Redneck Mother — Jerry Jeff Walker; Return of the Grievous Angel — Gram Parsons; Pancho and Lefty — Townes Van Zandt; Desperados Waiting for a Train — Guy Clark | none obvious | 8 boundary/contrast rows |
| 033 | 5 | Country-Pop / Crossover Country | song-first recognition and branching | mixed | A:13 / Al:9 / S:14 | Dolly Parton; Shania Twain; Kenny Rogers; Taylor Swift; Glen Campbell; John Denver; Alabama; The Chicks; Faith Hill; Lady A | Islands in the Stream — Kenny Rogers and Dolly Parton; Jolene — Dolly Parton; 9 to 5 — Dolly Parton; Rhinestone Cowboy — Glen Campbell; The Gambler — Kenny Rogers; You're Still the One — Shania Twain; Man! I Feel Like a Woman! — Shania Twain; Take Me Home, Country Roads — John Denver; Need You Now — Lady A; Love Story — Taylor Swift; Wichita Lineman — Glen Campbell; How Do I Live — LeAnn Rimes; I Hope You Dance — Lee Ann Womack; Breathe — Faith Hill | 4 multi-membership overlaps | thin contrast set |
| 034 | 5 | 90s Country Radio / Hat Acts / New Traditionalists | artist/anchor affinity branching | mixed | A:15 / Al:9 / S:14 | Garth Brooks; George Strait; Alan Jackson; Randy Travis; Brooks & Dunn; Dwight Yoakam; Reba McEntire; The Judds; Tim McGraw; Toby Keith | Friends in Low Places — Garth Brooks; Chattahoochee — Alan Jackson; Amarillo by Morning — George Strait; Forever and Ever, Amen — Randy Travis; Boot Scootin' Boogie — Brooks & Dunn; The Dance — Garth Brooks; Fancy — Reba McEntire; Should've Been a Cowboy — Toby Keith; Independence Day — Martina McBride; Grandpa (Tell Me Bout the Good Old Days) — The Judds; She's in Love with the Boy — Trisha Yearwood; Achy Breaky Heart — Billy Ray Cyrus; Live Like You Were Dying — Tim McGraw; Guitars, Cadillacs — Dwight Yoakam | 2 multi-membership overlaps | 3 boundary/contrast rows |
| 035 | 5 | Modern Country Radio / Bro-Country / Arena Country | song-first recognition and branching | mixed | A:16 / Al:10 / S:15 | Luke Combs; Florida Georgia Line; Morgan Wallen; Carrie Underwood; Chris Stapleton; Luke Bryan; Jason Aldean; Eric Church; Lainey Wilson; Sam Hunt | Before He Cheats — Carrie Underwood; Cruise — Florida Georgia Line; Beer Never Broke My Heart — Luke Combs; Last Night — Morgan Wallen; Tennessee Whiskey — Chris Stapleton; Body Like a Back Road — Sam Hunt; Beautiful Crazy — Luke Combs; Wagon Wheel — Darius Rucker; Country Girl (Shake It for Me) — Luke Bryan; Heart Like a Truck — Lainey Wilson; Die a Happy Man — Thomas Rhett; Need a Favor — Jelly Roll; Springsteen — Eric Church; Dirt Road Anthem — Jason Aldean; Slow Burn — Kacey Musgraves | none obvious | 3 boundary/contrast rows |
| 036 | 5 | Red Dirt / Americana Country / Texas Country | bridge and lineage branching | mixed | A:17 / Al:10 / S:15 | Tyler Childers; Cody Johnson; Zach Bryan; Parker McCollum; Old Crow Medicine Show; Jason Isbell; Cody Jinks; Koe Wetzel; Lucinda Williams; Steve Earle | Copperhead Road — Steve Earle; Feathered Indians — Tyler Childers; Something in the Orange — Zach Bryan; 'Til You Can't — Cody Johnson; Whitehouse Road — Tyler Childers; Oklahoma Smokeshow — Zach Bryan; Cover Me Up — Jason Isbell; Hippies and Cowboys — Cody Jinks; If We Were Vampires — Jason Isbell and the 400 Unit; Long Hot Summer Day — Turnpike Troubadours; Car Wheels on a Gravel Road — Lucinda Williams; Turtles All the Way Down — Sturgill Simpson; The Road Goes on Forever — Robert Earl Keen; Good Lord Lorrie — Turnpike Troubadours; Sleeping on the Blacktop — Colter Wall | none obvious | 5 boundary/contrast rows |
| 037 | 6 | Motown / Detroit Soul Pop | album-world and gateway testing | mixed | A:11 / Al:7 / S:15 | Stevie Wonder; Marvin Gaye; The Supremes; The Temptations; Jackson 5; Smokey Robinson & The Miracles; Diana Ross; Four Tops; Martha & the Vandellas; Mary Wells | My Girl — The Temptations; Superstition — Stevie Wonder; I Want You Back — Jackson 5; I Heard It Through the Grapevine — Marvin Gaye; Reach Out I'll Be There — Four Tops; Dancing in the Street — Martha & the Vandellas; Ain't No Mountain High Enough — Marvin Gaye & Tammi Terrell; Where Did Our Love Go — The Supremes; ABC — Jackson 5; You Can't Hurry Love — The Supremes; I Can't Help Myself — Four Tops; Stop! In the Name of Love — The Supremes; Signed, Sealed, Delivered (I'm Yours) — Stevie Wonder; My Guy — Mary Wells; The Tears of a Clown — Smokey Robinson & The Miracles | 11 multi-membership overlaps | thin contrast set |
| 038 | 6 | Southern Soul / Stax / Muscle Shoals | album-world and gateway testing | mixed | A:12 / Al:8 / S:15 | Aretha Franklin; Otis Redding; Al Green; Sam & Dave; Wilson Pickett; Isaac Hayes; Percy Sledge; Etta James; Booker T. & the M.G.'s; Staple Singers | Respect — Aretha Franklin; (Sittin' On) The Dock of the Bay — Otis Redding; Let's Stay Together — Al Green; Soul Man — Sam & Dave; Chain of Fools — Aretha Franklin; Think — Aretha Franklin; In the Midnight Hour — Wilson Pickett; Try a Little Tenderness — Otis Redding; Hold On, I'm Comin' — Sam & Dave; When a Man Loves a Woman — Percy Sledge; I'll Take You There — Staple Singers; Green Onions — Booker T. & the M.G.'s; Theme from Shaft — Isaac Hayes; Land of 1000 Dances — Wilson Pickett; Tired of Being Alone — Al Green | 4 multi-membership overlaps | thin contrast set |
| 039 | 6 | Funk / Psychedelic Soul / Groove Canon | album-world and gateway testing | mixed | A:13 / Al:8 / S:17 | James Brown; Earth, Wind & Fire; Kool & the Gang; Parliament/Funkadelic; Sly & the Family Stone; Commodores; Curtis Mayfield; The Isley Brothers; Ohio Players; War | September — Earth, Wind & Fire; I Got You (I Feel Good) — James Brown; Everyday People — Sly & the Family Stone; Papa's Got a Brand New Bag — James Brown; Get Up (I Feel Like Being a) Sex Machine — James Brown; Give Up the Funk — Parliament; Brick House — Commodores; Shining Star — Earth, Wind & Fire; Super Freak — Rick James; Cold Sweat — James Brown; Flash Light — Parliament; Jungle Boogie — Kool & the Gang; Superfly — Curtis Mayfield; Dance to the Music — Sly & the Family Stone; Family Affair — Sly & the Family Stone; Maggot Brain — Funkadelic; Cissy Strut — The Meters | 5 multi-membership overlaps | 6 boundary/contrast rows |
| 040 | 6 | Disco / Dancefloor 70s | album-world and gateway testing | mixed | A:13 / Al:9 / S:18 | Donna Summer; Chic; Bee Gees; Gloria Gaynor; KC and the Sunshine Band; Diana Ross; Sister Sledge; Village People; Sylvester; The Trammps | Stayin' Alive — Bee Gees; I Feel Love — Donna Summer; I Will Survive — Gloria Gaynor; Le Freak — Chic; Good Times — Chic; Night Fever — Bee Gees; Last Dance — Donna Summer; We Are Family — Sister Sledge; Hot Stuff — Donna Summer; That's the Way (I Like It) — KC and the Sunshine Band; Get Down Tonight — KC and the Sunshine Band; Disco Inferno — The Trammps; Y.M.C.A. — Village People; You Make Me Feel (Mighty Real) — Sylvester; He's the Greatest Dancer — Sister Sledge; Don't Leave Me This Way — Thelma Houston; Young Hearts Run Free — Candi Staton; Turn the Beat Around — Vicki Sue Robinson | 6 multi-membership overlaps | 2 boundary/contrast rows |
| 041 | 6 | Quiet Storm / Smooth R&B / Adult Soul | album-world and gateway testing | mixed | A:13 / Al:8 / S:15 | Luther Vandross; Anita Baker; Sade; Barry White; Teddy Pendergrass; Marvin Gaye; Roberta Flack; Toni Braxton; Maxwell; Smokey Robinson | Let's Get It On — Marvin Gaye; Sweet Love — Anita Baker; Never Too Much — Luther Vandross; Sexual Healing — Marvin Gaye; Smooth Operator — Sade; Quiet Storm — Smokey Robinson; Can't Get Enough of Your Love, Babe — Barry White; Here and Now — Luther Vandross; Killing Me Softly with His Song — Roberta Flack; Un-Break My Heart — Toni Braxton; Close the Door — Teddy Pendergrass; Caught Up in the Rapture — Anita Baker; Lovin' You — Minnie Riperton; No Ordinary Love — Sade; Turn Off the Lights — Teddy Pendergrass | 4 multi-membership overlaps | 3 boundary/contrast rows |
| 042 | 6 | New Jack Swing / 80s-90s R&B Pop | album-world and gateway testing | mixed | A:15 / Al:10 / S:20 | Janet Jackson; TLC; Boyz II Men; Mary J. Blige; Whitney Houston; Usher; Aaliyah; Beyonce; New Edition; Bobby Brown | No Scrubs — TLC; I Wanna Dance with Somebody — Whitney Houston; Poison — Bell Biv DeVoe; End of the Road — Boyz II Men; Rhythm Nation — Janet Jackson; My Prerogative — Bobby Brown; I'll Make Love to You — Boyz II Men; How Will I Know — Whitney Houston; Nasty — Janet Jackson; One in a Million — Aaliyah; Real Love — Mary J. Blige; No Diggity — Blackstreet feat. Dr. Dre; Hold On — En Vogue; Weak — SWV; Control — Janet Jackson; Creep — TLC; Every Little Step — Bobby Brown; Forever My Lady — Jodeci; If It Isn't Love — New Edition; Freek'n You — Jodeci | 8 multi-membership overlaps | thin contrast set |
| 043 | 6 | Neo-Soul / Conscious R&B | album-world and gateway testing | mixed | A:13 / Al:9 / S:16 | Lauryn Hill; Alicia Keys; D'Angelo; Erykah Badu; Maxwell; Mary J. Blige; Jill Scott; India.Arie; Musiq Soulchild; Raphael Saadiq | Doo Wop (That Thing) — Lauryn Hill; Fallin' — Alicia Keys; If I Ain't Got You — Alicia Keys; Brown Sugar — D'Angelo; Untitled (How Does It Feel) — D'Angelo; On & On — Erykah Badu; Ex-Factor — Lauryn Hill; Tyrone — Erykah Badu; Fortunate — Maxwell; Video — India.Arie; A Long Walk — Jill Scott; Ascension (Don't Ever Wonder) — Maxwell; You Got Me — The Roots feat. Erykah Badu; Golden — Jill Scott; Love — Musiq Soulchild; Charlene — Anthony Hamilton | 6 multi-membership overlaps | thin contrast set |
| 044 | 6 | Modern R&B / Alt-R&B / Bedroom R&B | album-world and gateway testing | mixed | A:17 / Al:12 / S:23 | Frank Ocean; SZA; The Weeknd; Miguel; Solange; Beyonce; Usher; H.E.R.; Summer Walker; Brent Faiyaz | Thinkin Bout You — Frank Ocean; Kill Bill — SZA; The Hills — The Weeknd; Adorn — Miguel; The Weekend — SZA; Love Galore — SZA feat. Travis Scott; Cranes in the Sky — Solange; Wicked Games — The Weeknd; Novacane — Frank Ocean; Pyramids — Frank Ocean; Good Days — SZA; Earned It — The Weeknd; Pink + White — Frank Ocean; Exchange — Bryson Tiller; Focus — H.E.R.; Girls Need Love — Summer Walker; Losing You — Solange; Playing Games — Summer Walker; House of Balloons / Glass Table Girls — The Weeknd; Clouded — Brent Faiyaz | 3 multi-membership overlaps | 5 boundary/contrast rows |
| 045 | 7 | Old-School Hip-Hop / Electro-Rap Foundations | album-world and gateway testing | mixed | A:12 / Al:9 / S:16 | Run-DMC; LL Cool J; The Sugarhill Gang; Beastie Boys; Grandmaster Flash and the Furious Five; Afrika Bambaataa & Soulsonic Force; Kurtis Blow; Slick Rick; Big Daddy Kane; Whodini | The Message — Grandmaster Flash and the Furious Five; Rapper's Delight — The Sugarhill Gang; Walk This Way — Run-DMC; Fight for Your Right — Beastie Boys; I Need Love — LL Cool J; Planet Rock — Afrika Bambaataa & Soulsonic Force; Sucker M.C.'s — Run-DMC; It's Like That — Run-DMC; The Breaks — Kurtis Blow; La Di Da Di — Doug E. Fresh and Slick Rick; Children's Story — Slick Rick; Paul Revere — Beastie Boys; White Lines — Grandmaster Flash & Melle Mel; I Can't Live Without My Radio — LL Cool J; Rock Box — Run-DMC; Friends — Whodini | none obvious | 2 boundary/contrast rows |
| 046 | 7 | Golden Age Hip-Hop / Conscious / Native Tongues | album-world and gateway testing | mixed | A:11 / Al:13 / S:17 | Salt-N-Pepa; Public Enemy; Eric B. & Rakim; A Tribe Called Quest; De La Soul; Boogie Down Productions; Gang Starr; Queen Latifah; MC Lyte; Jungle Brothers | Fight the Power — Public Enemy; Push It — Salt-N-Pepa; Paid in Full — Eric B. & Rakim; Can I Kick It? — A Tribe Called Quest; Scenario — A Tribe Called Quest; Me Myself and I — De La Soul; U.N.I.T.Y. — Queen Latifah; Rebel Without a Pause — Public Enemy; Bring the Noise — Public Enemy; Electric Relaxation — A Tribe Called Quest; Bonita Applebum — A Tribe Called Quest; Mass Appeal — Gang Starr; Eric B. Is President — Eric B. & Rakim; South Bronx — Boogie Down Productions; My Philosophy — Boogie Down Productions; Ladies First — Queen Latifah feat. Monie Love; Buddy — De La Soul | none obvious | thin contrast set |
| 047 | 7 | Gangsta Rap / West Coast / G-Funk | album-world and gateway testing | song | A:11 / Al:11 / S:17 | 2Pac; Dr. Dre; Snoop Dogg; N.W.A; Ice Cube; Eazy-E; Warren G; Scarface; Geto Boys; Too Short | Nuthin' but a G Thang — Dr. Dre feat. Snoop Doggy Dogg; California Love — 2Pac feat. Dr. Dre; Gin and Juice — Snoop Dogg; It Was a Good Day — Ice Cube; Regulate — Warren G feat. Nate Dogg; Dear Mama — 2Pac; Straight Outta Compton — N.W.A; Fuck tha Police — N.W.A; Who Am I? (What's My Name?) — Snoop Dogg; Insane in the Brain — Cypress Hill; Mind Playing Tricks on Me — Geto Boys; Boyz-n-the-Hood — Eazy-E; Ambitionz Az a Ridah — 2Pac; Let Me Ride — Dr. Dre; Express Yourself — N.W.A; Check Yo Self — Ice Cube; No Vaseline — Ice Cube | none obvious | 8 boundary/contrast rows |
| 048 | 7 | East Coast 90s / Boom Bap / Street Canon | album-world and gateway testing | song | A:9 / Al:12 / S:19 | The Notorious B.I.G.; Jay-Z; DMX; Nas; Wu-Tang Clan; Mobb Deep; Busta Rhymes; Big L; The LOX | Juicy — The Notorious B.I.G.; Big Poppa — The Notorious B.I.G.; Hypnotize — The Notorious B.I.G.; Ruff Ryders' Anthem — DMX; Hard Knock Life (Ghetto Anthem) — Jay-Z; Mo Money Mo Problems — The Notorious B.I.G.; Shook Ones, Pt. II — Mobb Deep; C.R.E.A.M. — Wu-Tang Clan; N.Y. State of Mind — Nas; The World Is Yours — Nas; Big Pimpin' — Jay-Z feat. UGK; If I Ruled the World (Imagine That) — Nas feat. Lauryn Hill; Woo Hah!! Got You All in Check — Busta Rhymes; Dead Presidents II — Jay-Z; Survival of the Fittest — Mobb Deep; Protect Ya Neck — Wu-Tang Clan; Put Your Hands Where My Eyes Could See — Busta Rhymes; Triumph — Wu-Tang Clan; Ante Up — M.O.P. | none obvious | thin contrast set |
| 049 | 7 | Southern Hip-Hop / Crunk / Trap Foundations | album-world and gateway testing | song | A:14 / Al:16 / S:27 | OutKast; Lil Wayne; Ludacris; T.I.; UGK; Gucci Mane; Jeezy; Three 6 Mafia; Juvenile; Lil Jon & The East Side Boyz | Back That Azz Up — Juvenile feat. Mannie Fresh and Lil Wayne; Get Low — Lil Jon & The East Side Boyz feat. Ying Yang Twins; Ms. Jackson — OutKast; A Milli — Lil Wayne; Lollipop — Lil Wayne; What You Know — T.I.; Int'l Players Anthem — UGK feat. OutKast; Rosa Parks — OutKast; Stay Fly — Three 6 Mafia; Soul Survivor — Jeezy feat. Akon; Stand Up — Ludacris feat. Shawnna; Player's Ball — OutKast; Make 'Em Say Uhh! — Master P; Lemonade — Gucci Mane; Put On — Jeezy feat. Kanye West; Go DJ — Lil Wayne; Elevators (Me & You) — OutKast; B.O.B. — OutKast; Sippin' on Some Syrup — Three 6 Mafia feat. UGK; Still Fly — Big Tymers | none obvious | 3 boundary/contrast rows |
| 050 | 7 | Pop-Rap / Mainstream Hip-Hop Crossover | boundary and contrast calibration | song | A:15 / Al:15 / S:27 | Drake; Eminem; Kanye West; 50 Cent; Nicki Minaj; Missy Elliott; Fugees; Nelly; Lauryn Hill; Cardi B | In Da Club — 50 Cent; Lose Yourself — Eminem; Bodak Yellow — Cardi B; God's Plan — Drake; Gold Digger — Kanye West feat. Jamie Foxx; Work It — Missy Elliott; Gangsta's Paradise — Coolio feat. L.V.; Empire State of Mind — Jay-Z feat. Alicia Keys; Stronger — Kanye West; Doo Wop (That Thing) — Lauryn Hill; Get Ur Freak On — Missy Elliott; Super Bass — Nicki Minaj; Hotline Bling — Drake; The Real Slim Shady — Eminem; Stan — Eminem feat. Dido; Ready or Not — Fugees; Killing Me Softly — Fugees; Savage — Megan Thee Stallion; 21 Questions — 50 Cent feat. Nate Dogg; WAP — Cardi B feat. Megan Thee Stallion | 8 multi-membership overlaps | 13 boundary/contrast rows |
| 051 | 7 | Alternative / Experimental / Indie Rap | boundary and contrast calibration | song | A:11 / Al:12 / S:18 | Tyler, the Creator; MF DOOM; Mos Def / Yasiin Bey; The Roots; Kid Cudi; Childish Gambino; Run the Jewels; Danny Brown; Earl Sweatshirt; Death Grips | EARFQUAKE — Tyler, the Creator; Day 'n' Nite — Kid Cudi; This Is America — Childish Gambino; Pursuit of Happiness — Kid Cudi feat. MGMT and Ratatat; All Caps — Madvillain; You Got Me — The Roots feat. Erykah Badu; Yonkers — Tyler, the Creator; Ms. Fat Booty — Mos Def / Yasiin Bey; The Light — Common; The Seed (2.0) — The Roots feat. Cody Chesnutt; Accordion — Madvillain; Respiration — Black Star feat. Common; Doomsday — MF DOOM; Close Your Eyes (And Count to Fuck) — Run the Jewels feat. Zack de la Rocha; Mathematics — Mos Def / Yasiin Bey; Ain't It Funny — Danny Brown; Get Got — Death Grips; Guillotine — Death Grips | 1 multi-membership overlaps | 18 boundary/contrast rows |
| 052 | 7 | Modern Trap / Streaming-Era Rap | album-world and gateway testing | song | A:14 / Al:16 / S:33 | Kendrick Lamar; Travis Scott; Migos; Future; J. Cole; Lil Uzi Vert; 21 Savage; Chief Keef; Young Thug; Metro Boomin | SICKO MODE — Travis Scott; HUMBLE. — Kendrick Lamar; Bad and Boujee — Migos feat. Lil Uzi Vert; Mask Off — Future; Alright — Kendrick Lamar; XO Tour Llif3 — Lil Uzi Vert; No Role Modelz — J. Cole; Swimming Pools (Drank) — Kendrick Lamar; Antidote — Travis Scott; a lot — 21 Savage feat. J. Cole; March Madness — Future; m.A.A.d city — Kendrick Lamar feat. MC Eiht; Magnolia — Playboi Carti; Bank Account — 21 Savage; DNA. — Kendrick Lamar; goosebumps — Travis Scott; Low Life — Future feat. The Weeknd; Drip Too Hard — Lil Baby and Gunna; Dior — Pop Smoke; Creepin' — Metro Boomin, The Weeknd, and 21 Savage | none obvious | 8 boundary/contrast rows |
| 053 | 8 | First-Wave Punk / 70s Punk | album-world and gateway testing | mixed | A:10 / Al:9 / S:11 | The Clash; Ramones; Sex Pistols; Buzzcocks; The Damned; X; X-Ray Spex; Wire; The Saints; Stiff Little Fingers | I Wanna Be Sedated — Ramones; London Calling — The Clash; Blitzkrieg Bop — Ramones; Anarchy in the U.K. — Sex Pistols; God Save the Queen — Sex Pistols; Ever Fallen in Love — Buzzcocks; Oh Bondage Up Yours! — X-Ray Spex; Los Angeles — X; New Rose — The Damned; Ex Lion Tamer — Wire; Alternative Ulster — Stiff Little Fingers | none obvious | 2 boundary/contrast rows |
| 054 | 8 | CBGB / Art-Punk / Downtown New York | album-world and gateway testing | mixed | A:9 / Al:8 / S:10 | Talking Heads; Blondie; Patti Smith; Television; Suicide; The Modern Lovers; Richard Hell & The Voidoids; Pere Ubu; James Chance and the Contortions | Heart of Glass — Blondie; Once in a Lifetime — Talking Heads; Psycho Killer — Talking Heads; Gloria — Patti Smith; Marquee Moon — Television; Ghost Rider — Suicide; Blank Generation — Richard Hell & The Voidoids; Roadrunner — The Modern Lovers; Non-Alignment Pact — Pere Ubu; Contort Yourself — James Chance and the Contortions | none obvious | 5 boundary/contrast rows |
| 055 | 8 | Hardcore Punk / US 80s Hardcore | artist/anchor affinity branching | mixed | A:12 / Al:11 / S:12 | Black Flag; Minor Threat; Dead Kennedys; Misfits; Bad Brains; Descendents; Husker Du; Germs; Suicidal Tendencies; Circle Jerks | Rise Above — Black Flag; Holiday in Cambodia — Dead Kennedys; Straight Edge — Minor Threat; Last Caress — Misfits; Institutionalized — Suicidal Tendencies; Banned in D.C. — Bad Brains; Suburban Home — Descendents; Lexicon Devil — Germs; New Day Rising — Husker Du; Wild in the Streets — Circle Jerks; We Gotta Know — Cro-Mags; Break Down the Walls — Youth of Today | 2 multi-membership overlaps | 6 boundary/contrast rows |
| 056 | 8 | Post-Punk / Dark Melodic / Gothic Roots | bridge and lineage branching | mixed | A:13 / Al:10 / S:13 | The Cure; Joy Division; Siouxsie and the Banshees; Gang of Four; Bauhaus; Public Image Ltd; Love and Rockets; The Church; Echo & the Bunnymen; The Psychedelic Furs | Love Will Tear Us Apart — Joy Division; Just Like Heaven — The Cure; Under the Milky Way — The Church; So Alive — Love and Rockets; Damaged Goods — Gang of Four; Bela Lugosi's Dead — Bauhaus; Spellbound — Siouxsie and the Banshees; Public Image — Public Image Ltd; The Killing Moon — Echo & the Bunnymen; Atmosphere — Joy Division; Pictures of You — The Cure; Swamp Thing — The Chameleons; Totally Wired — The Fall | 2 multi-membership overlaps | thin contrast set |
| 057 | 8 | New Wave / MTV Pop-Rock | song-first recognition and branching | mixed | A:11 / Al:10 / S:12 | The Police; The Cars; Duran Duran; INXS; The B-52's; Pretenders; The Go-Go's; Devo; Elvis Costello; Joe Jackson | Hungry Like the Wolf — Duran Duran; Need You Tonight — INXS; Just What I Needed — The Cars; Every Breath You Take — The Police; Roxanne — The Police; Brass in Pocket — Pretenders; Our Lips Are Sealed — The Go-Go's; Whip It — Devo; Love Shack — The B-52's; Is She Really Going Out with Him? — Joe Jackson; I Got You — Split Enz; Alison — Elvis Costello | none obvious | thin contrast set |
| 058 | 8 | Synthpop / New Romantic / 80s Electronic Pop | song-first recognition and branching | mixed | A:12 / Al:11 / S:12 | Depeche Mode; Eurythmics; New Order; A-ha; Pet Shop Boys; The Human League; Soft Cell; Erasure; Gary Numan; Tears for Fears | Take On Me — A-ha; Enjoy the Silence — Depeche Mode; Personal Jesus — Depeche Mode; Sweet Dreams (Are Made of This) — Eurythmics; Tainted Love — Soft Cell; Blue Monday — New Order; Don't You Want Me — The Human League; Cars — Gary Numan; Everybody Wants to Rule the World — Tears for Fears; West End Girls — Pet Shop Boys; A Little Respect — Erasure; Only You — Yazoo | none obvious | thin contrast set |
| 059 | 8 | College Rock / Pre-Alternative 80s | artist/anchor affinity branching | mixed | A:12 / Al:11 / S:13 | R.E.M.; The Smiths; The Replacements; Pixies; Violent Femmes; They Might Be Giants; Sonic Youth; Meat Puppets; Minutemen; The Dream Syndicate | This Charming Man — The Smiths; Radio Free Europe — R.E.M.; Bastards of Young — The Replacements; Blister in the Sun — Violent Femmes; Where Is My Mind? — Pixies; The One I Love — R.E.M.; How Soon Is Now? — The Smiths; Ana Ng — They Might Be Giants; Teen Age Riot — Sonic Youth; Lake of Fire — Meat Puppets; Corona — Minutemen; Tell Me When It's Over — The Dream Syndicate; Take the Skinheads Bowling — Camper Van Beethoven | 9 multi-membership overlaps | 5 boundary/contrast rows |
| 060 | 8 | Noise Rock / Post-Hardcore / Touch and Go Axis | boundary and contrast calibration | mixed | A:13 / Al:11 / S:13 | Fugazi; At the Drive-In; Refused; Quicksand; Big Black; The Jesus Lizard; Mission of Burma; Wipers; Slint; Butthole Surfers | One Armed Scissor — At the Drive-In; Waiting Room — Fugazi; New Noise — Refused; That's When I Reach for My Revolver — Mission of Burma; Fazer — Quicksand; Pepper — Butthole Surfers; Kerosene — Big Black; Mouth Breather — The Jesus Lizard; D-7 — Wipers; Good Morning, Captain — Slint; Here Come the Rome Plows — Drive Like Jehu; Prayer to God — Shellac; Cannibal — Scratch Acid | 1 multi-membership overlaps | 8 boundary/contrast rows |
| 061 | 9 | Traditional Heavy Metal / NWOBHM | album-world and gateway testing | mixed | A:15 / Al:15 / S:20 | Black Sabbath; Ozzy Osbourne; Iron Maiden; Judas Priest; Motorhead; Dio; Rainbow; Scorpions; Ghost; Accept | Paranoid — Black Sabbath; Crazy Train — Ozzy Osbourne; Iron Man — Black Sabbath; War Pigs — Black Sabbath; Breaking the Law — Judas Priest; Ace of Spades — Motorhead; The Trooper — Iron Maiden; You've Got Another Thing Comin' — Judas Priest; Rainbow in the Dark — Dio; The Number of the Beast — Iron Maiden; Black Sabbath — Black Sabbath; Run to the Hills — Iron Maiden; Holy Diver — Dio; Living After Midnight — Judas Priest; Sweet Leaf — Black Sabbath; 2 Minutes to Midnight — Iron Maiden; Mr. Crowley — Ozzy Osbourne; N.I.B. — Black Sabbath; Electric Eye — Judas Priest; Overkill — Motorhead | 3 multi-membership overlaps | 8 boundary/contrast rows |
| 062 | 9 | Thrash Metal / Speed Metal | album-world and gateway testing | mixed | A:13 / Al:14 / S:20 | Metallica; Slayer; Megadeth; Pantera; Anthrax; Sepultura; Lamb of God; Testament; Exodus; Kreator | Master of Puppets — Metallica; Enter Sandman — Metallica; One — Metallica; Walk — Pantera; Symphony of Destruction — Megadeth; For Whom the Bell Tolls — Metallica; Raining Blood — Slayer; Holy Wars... The Punishment Due — Megadeth; Cowboys from Hell — Pantera; Angel of Death — Slayer; Peace Sells — Megadeth; Battery — Metallica; Seek & Destroy — Metallica; Seasons in the Abyss — Slayer; Madhouse — Anthrax; Refuse/Resist — Sepultura; South of Heaven — Slayer; Bonded by Blood — Exodus; Indians — Anthrax; Black Metal — Venom | 1 multi-membership overlaps | 6 boundary/contrast rows |
| 063 | 9 | Glam Metal / Hair Metal / Pop Metal | boundary and contrast calibration | mixed | A:16 / Al:18 / S:23 | Motley Crue; Def Leppard; Bon Jovi; Guns N' Roses; Poison; Twisted Sister; Whitesnake; Europe; Skid Row; Ratt | Pour Some Sugar on Me — Def Leppard; Livin' on a Prayer — Bon Jovi; Sweet Child o' Mine — Guns N' Roses; You Give Love a Bad Name — Bon Jovi; Photograph — Def Leppard; Welcome to the Jungle — Guns N' Roses; Dr. Feelgood — Motley Crue; Every Rose Has Its Thorn — Poison; Kickstart My Heart — Motley Crue; 18 and Life — Skid Row; Nothin' but a Good Time — Poison; We're Not Gonna Take It — Twisted Sister; Here I Go Again — Whitesnake; Paradise City — Guns N' Roses; Cum On Feel the Noize — Quiet Riot; Wanted Dead or Alive — Bon Jovi; Cherry Pie — Warrant; The Final Countdown — Europe; Rock of Ages — Def Leppard; Round and Round — Ratt | 3 multi-membership overlaps | 20 boundary/contrast rows |
| 064 | 9 | Doom / Stoner / Desert Heavy | album-world and gateway testing | mixed | A:13 / Al:13 / S:16 | Black Sabbath; Kyuss; Sleep; Queens of the Stone Age; Fu Manchu; Monster Magnet; Electric Wizard; Candlemass; Melvins; Baroness | No One Knows — Queens of the Stone Age; Green Machine — Kyuss; Dragonaut — Sleep; Sweet Leaf — Black Sabbath; Electric Funeral — Black Sabbath; Go With the Flow — Queens of the Stone Age; Space Lord — Monster Magnet; Gardenia — Kyuss; Freya — The Sword; Funeralopolis — Electric Wizard; Dopesmoker — Sleep; Solitude — Candlemass; Demon Cleaner — Kyuss; Honey Bucket — Melvins; Vinum Sabbathi — Electric Wizard; Born Too Late — Saint Vitus | 2 multi-membership overlaps | 8 boundary/contrast rows |
| 065 | 9 | Industrial Metal / Machine Rock | boundary and contrast calibration | mixed | A:12 / Al:14 / S:15 | Nine Inch Nails; Ministry; Rammstein; White Zombie; Rob Zombie; Static-X; Marilyn Manson; Fear Factory; Filter; KMFDM | Head Like a Hole — Nine Inch Nails; Du hast — Rammstein; Closer — Nine Inch Nails; Jesus Built My Hotrod — Ministry; Dragula — Rob Zombie; The Beautiful People — Marilyn Manson; Hurt — Nine Inch Nails; More Human Than Human — White Zombie; Just One Fix — Ministry; Wish — Nine Inch Nails; Sonne — Rammstein; Push It — Static-X; Demanufacture — Fear Factory; Hey Man Nice Shot — Filter; Stigmata — Ministry | 3 multi-membership overlaps | 14 boundary/contrast rows |
| 066 | 9 | Alt-Metal / Nu-Metal / Rap-Metal | boundary and contrast calibration | mixed | A:20 / Al:22 / S:27 | Tool; Korn; Slipknot; System of a Down; Linkin Park; Limp Bizkit; Rage Against the Machine; Deftones; Faith No More; Disturbed | In the End — Linkin Park; Chop Suey! — System of a Down; Freak on a Leash — Korn; Killing in the Name — Rage Against the Machine; Wait and Bleed — Slipknot; Toxicity — System of a Down; Sober — Tool; Schism — Tool; Epic — Faith No More; Break Stuff — Limp Bizkit; One Step Closer — Linkin Park; Numb — Linkin Park; Crawling — Linkin Park; Blind — Korn; My Own Summer (Shove It) — Deftones; Change (In the House of Flies) — Deftones; Stinkfist — Tool; Down with the Sickness — Disturbed; Bulls on Parade — Rage Against the Machine; Nookie — Limp Bizkit | 4 multi-membership overlaps | 21 boundary/contrast rows |
| 067 | 9 | Metalcore / Emo-Heavy / Modern Active Rock | boundary and contrast calibration | mixed | A:22 / Al:20 / S:25 | Avenged Sevenfold; Killswitch Engage; Bring Me the Horizon; Bullet for My Valentine; Spiritbox; Sleep Token; Bad Omens; Trivium; Five Finger Death Punch; Motionless in White | Bat Country — Avenged Sevenfold; Can You Feel My Heart — Bring Me the Horizon; The Summoning — Sleep Token; Just Pretend — Bad Omens; The End of Heartache — Killswitch Engage; Tears Don't Fall — Bullet for My Valentine; My Curse — Killswitch Engage; Shadow Moses — Bring Me the Horizon; Holy Roller — Spiritbox; Circle With Me — Spiritbox; Afterlife — Avenged Sevenfold; Sleepwalking — Bring Me the Horizon; Pull Harder on the Strings of Your Martyr — Trivium; Dethrone — Bad Omens; Throne — Bring Me the Horizon; Chokehold — Sleep Token; The Bleeding — Five Finger Death Punch; A Grave Mistake — Ice Nine Kills; Another Life — Motionless in White; Doomsday — Architects | 13 multi-membership overlaps | 22 boundary/contrast rows |
| 068 | 9 | Extreme Metal Gateway / Black-Death-Sludge | boundary and contrast calibration | mixed | A:18 / Al:23 / S:24 | Gojira; Mastodon; Death; Cannibal Corpse; Meshuggah; Opeth; Behemoth; Morbid Angel; Mayhem; Deafheaven | Flying Whales — Gojira; Bleed — Meshuggah; Blood and Thunder — Mastodon; Crystal Mountain — Death; Hammer Smashed Face — Cannibal Corpse; Stranded — Gojira; Oblivion — Mastodon; Ghost of Perdition — Opeth; Silvera — Gojira; Blackwater Park — Opeth; Dream House — Deafheaven; New Millennium Cyanide Christ — Meshuggah; Pull the Plug — Death; Chapel of Ghouls — Morbid Angel; Lack of Comprehension — Death; God of Emptiness — Morbid Angel; Heartwork — Carcass; Freezing Moon — Mayhem; I Am the Black Wizards — Emperor; Sunbather — Deafheaven | none obvious | 15 boundary/contrast rows |
| 069 | 10 | 1980s Alternative Source-Code / Pre-Grunge | boundary and contrast calibration | mixed | A:10 / Al:7 / S:10 | Pixies; R.E.M.; Sonic Youth; The Replacements; The Cure; Dinosaur Jr.; The Jesus and Mary Chain; Jane's Addiction; Husker Du; Wipers | Where Is My Mind? — Pixies; The One I Love — R.E.M.; Debaser — Pixies; Teen Age Riot — Sonic Youth; Freak Scene — Dinosaur Jr.; Jane Says — Jane's Addiction; Radio Free Europe — R.E.M.; Just Like Honey — The Jesus and Mary Chain; Bastards of Young — The Replacements; Makes No Sense at All — Husker Du | 12 multi-membership overlaps | 8 boundary/contrast rows |
| 070 | 10 | Grunge / Seattle / 90s Alt Center | album-world and gateway testing | mixed | A:6 / Al:7 / S:10 | Nirvana; Pearl Jam; Smashing Pumpkins; Soundgarden; Alice in Chains; Mudhoney | Smells Like Teen Spirit — Nirvana; Black Hole Sun — Soundgarden; Come As You Are — Nirvana; Alive — Pearl Jam; Heart-Shaped Box — Nirvana; Jeremy — Pearl Jam; Man in the Box — Alice in Chains; Would? — Alice in Chains; Black — Pearl Jam; Spoonman — Soundgarden | 1 multi-membership overlaps | 2 boundary/contrast rows |
| 071 | 10 | Post-Grunge / Modern Rock Radio | boundary and contrast calibration | mixed | A:8 / Al:7 / S:11 | Foo Fighters; Stone Temple Pilots; Bush; Live; Collective Soul; Third Eye Blind; Nickelback; Creed | Everlong — Foo Fighters; Plush — Stone Temple Pilots; Interstate Love Song — Stone Temple Pilots; Lightning Crashes — Live; Semi-Charmed Life — Third Eye Blind; Glycerine — Bush; Machinehead — Bush; Shine — Collective Soul; How You Remind Me — Nickelback; With Arms Wide Open — Creed; Higher — Creed | none obvious | 17 boundary/contrast rows |
| 072 | 10 | 90s Indie / Lo-Fi / Slacker / Matador Axis | album-world and gateway testing | mixed | A:7 / Al:7 / S:10 | Pavement; Neutral Milk Hotel; Elliott Smith; Guided by Voices; Built to Spill; Yo La Tengo; Sebadoh | Cut Your Hair — Pavement; Gold Soundz — Pavement; Holland, 1945 — Neutral Milk Hotel; In the Aeroplane Over the Sea — Neutral Milk Hotel; Between the Bars — Elliott Smith; Game of Pricks — Guided by Voices; The Plan — Built to Spill; Summer Babe — Pavement; Sugarcube — Yo La Tengo; I Am a Scientist — Guided by Voices | none obvious | thin contrast set |
| 073 | 10 | Shoegaze / Dream Pop / Noise Haze | album-world and gateway testing | mixed | A:9 / Al:7 / S:10 | My Bloody Valentine; Cocteau Twins; Slowdive; Mazzy Star; Beach House; Ride; Galaxie 500; Lush; A.R. Kane | Fade Into You — Mazzy Star; Only Shallow — My Bloody Valentine; When the Sun Hits — Slowdive; Heaven or Las Vegas — Cocteau Twins; Sometimes — My Bloody Valentine; Space Song — Beach House; Cherry-Coloured Funk — Cocteau Twins; Alison — Slowdive; Vapour Trail — Ride; Sweetness and Light — Lush | none obvious | 3 boundary/contrast rows |
| 074 | 10 | Female 90s Alt / Riot Grrrl / Guitar Voices | boundary and contrast calibration | mixed | A:10 / Al:8 / S:11 | Hole; PJ Harvey; Liz Phair; The Cranberries; The Breeders; Garbage; Veruca Salt; Sleater-Kinney; Alanis Morissette; Bikini Kill | Doll Parts — Hole; Down by the Water — PJ Harvey; Zombie — The Cranberries; Rebel Girl — Bikini Kill; Cannonball — The Breeders; Celebrity Skin — Hole; Seether — Veruca Salt; Supernova — Liz Phair; Volcano Girls — Veruca Salt; Fuck and Run — Liz Phair; You Oughta Know — Alanis Morissette | none obvious | 6 boundary/contrast rows |
| 075 | 10 | Power-Pop Revival / Crunchy Alt-Pop | album-world and gateway testing | mixed | A:8 / Al:7 / S:10 | Weezer; Fountains of Wayne; The Lemonheads; Nada Surf; Matthew Sweet; Superdrag; The Rentals; That Dog | Buddy Holly — Weezer; Say It Ain't So — Weezer; Stacy's Mom — Fountains of Wayne; El Scorcho — Weezer; Into Your Arms — The Lemonheads; Popular — Nada Surf; Girlfriend — Matthew Sweet; Radiation Vibe — Fountains of Wayne; Sucked Out — Superdrag; Friends of P. — The Rentals | none obvious | thin contrast set |
| 076 | 10 | Pop-Punk / Skate Punk / 90s-00s Punk Pop | album-world and gateway testing | song | A:7 / Al:7 / S:12 | Green Day; Blink-182; The Offspring; Sum 41; Rancid; New Found Glory; NOFX | All the Small Things — Blink-182; Basket Case — Green Day; What's My Age Again? — Blink-182; When I Come Around — Green Day; American Idiot — Green Day; Self Esteem — The Offspring; Come Out and Play — The Offspring; Good Riddance (Time of Your Life) — Green Day; Fat Lip — Sum 41; The Rock Show — Blink-182; Time Bomb — Rancid; Linoleum — NOFX | none obvious | thin contrast set |
| 077 | 10 | Emo / Mall Emo / Post-Hardcore Pop | album-world and gateway testing | mixed | A:9 / Al:9 / S:12 | My Chemical Romance; Fall Out Boy; Paramore; Jimmy Eat World; Panic! at the Disco; Dashboard Confessional; Taking Back Sunday; The Get Up Kids; Brand New | Welcome to the Black Parade — My Chemical Romance; Sugar, We're Goin Down — Fall Out Boy; The Middle — Jimmy Eat World; Misery Business — Paramore; Helena — My Chemical Romance; I'm Not Okay (I Promise) — My Chemical Romance; I Write Sins Not Tragedies — Panic! at the Disco; Decode — Paramore; Screaming Infidelities — Dashboard Confessional; Sweetness — Jimmy Eat World; Cute Without the 'E' (Cut from the Team) — Taking Back Sunday; Hands Down — Dashboard Confessional | none obvious | 4 boundary/contrast rows |
| 078 | 10 | Blog Indie / Prestige Indie / 2000s Indie Rock | album-world and gateway testing | mixed | A:8 / Al:8 / S:10 | Arcade Fire; Death Cab for Cutie; Modest Mouse; The Shins; Vampire Weekend; Sufjan Stevens; Spoon; Broken Social Scene | Float On — Modest Mouse; A-Punk — Vampire Weekend; I Will Follow You into the Dark — Death Cab for Cutie; Wake Up — Arcade Fire; New Slang — The Shins; Soul Meets Body — Death Cab for Cutie; Rebellion (Lies) — Arcade Fire; Chicago — Sufjan Stevens; Dashboard — Modest Mouse; Anthems for a Seventeen Year-Old Girl — Broken Social Scene | none obvious | thin contrast set |
| 079 | 10 | Garage Revival / Rock-Is-Back 2000s | album-world and gateway testing | mixed | A:7 / Al:7 / S:10 | The White Stripes; The Strokes; Arctic Monkeys; The Black Keys; The Hives; The Libertines; The Vines | Seven Nation Army — The White Stripes; Last Nite — The Strokes; Lonely Boy — The Black Keys; Hate to Say I Told You So — The Hives; Fell in Love with a Girl — The White Stripes; I Bet You Look Good on the Dancefloor — Arctic Monkeys; Someday — The Strokes; The Hardest Button to Button — The White Stripes; Gold on the Ceiling — The Black Keys; Get Free — The Vines | 1 multi-membership overlaps | 2 boundary/contrast rows |
| 080 | 10 | Post-Punk Revival / Dark Indie Rock | boundary and contrast calibration | mixed | A:9 / Al:8 / S:12 | Interpol; Yeah Yeah Yeahs; The Killers; Franz Ferdinand; Bloc Party; The National; TV on the Radio; The Walkmen; Editors | Take Me Out — Franz Ferdinand; Maps — Yeah Yeah Yeahs; Obstacle 1 — Interpol; Mr. Brightside — The Killers; Banquet — Bloc Party; Helicopter — Bloc Party; Fake Empire — The National; Date with the Night — Yeah Yeah Yeahs; Wolf Like Me — TV on the Radio; The Rat — The Walkmen; NYC — Interpol; Munich — Editors | 2 multi-membership overlaps | 7 boundary/contrast rows |
| 081 | 11 | House / Chicago / Dance Club Foundations | song-first recognition and branching | mixed | A:15 / Al:8 / S:13 | Disclosure; Frankie Knuckles; Robin S.; CeCe Peniston; Basement Jaxx; Crystal Waters; Black Box; Stardust; Marshall Jefferson; Mr. Fingers | Finally — CeCe Peniston; Gypsy Woman (She's Homeless) — Crystal Waters; Show Me Love — Robin S.; Latch — Disclosure featuring Sam Smith; Music Sounds Better With You — Stardust; Your Love — Frankie Knuckles; Ride on Time — Black Box; Push the Feeling On — Nightcrawlers; Move Your Body — Marshall Jefferson; Can You Feel It — Mr. Fingers; Promised Land — Joe Smooth; French Kiss — Lil Louis; Good Life — Inner City | none obvious | thin contrast set |
| 082 | 11 | Techno / Detroit / Minimal Electronic | artist/anchor affinity branching | mixed | A:14 / Al:9 / S:11 | Inner City; Orbital; Derrick May; Juan Atkins; Kevin Saunderson; Cybotron; Underground Resistance; Model 500; Robert Hood; Laurent Garnier | Big Fun — Inner City; No UFO's — Model 500; Strings of Life — Rhythim Is Rhythim; Clear — Cybotron; Halcyon On and On — Orbital; Jupiter Jazz — Underground Resistance; At Les — Carl Craig; The Bells — Jeff Mills; Spastik — Plastikman; Minus — Robert Hood; Phylyps Trak II — Basic Channel | none obvious | 2 boundary/contrast rows |
| 083 | 11 | EDM / Festival Dance / Big Room / Mainstream Electronic | song-first recognition and branching | mixed | A:17 / Al:12 / S:17 | Daft Punk; Avicii; Calvin Harris; David Guetta; Fred again..; Swedish House Mafia; Major Lazer; The Chemical Brothers; The Prodigy; Fatboy Slim | One More Time — Daft Punk; Around the World — Daft Punk; Levels — Avicii; Wake Me Up — Avicii; Feel So Close — Calvin Harris; Titanium — David Guetta featuring Sia; Don't You Worry Child — Swedish House Mafia; Clarity — Zedd featuring Foxes; Lean On — Major Lazer and DJ Snake featuring MO; Praise You — Fatboy Slim; Sandstorm — Darude; Animals — Martin Garrix; Block Rockin' Beats — The Chemical Brothers; Strobe — Deadmau5; Firestarter — The Prodigy; Marea (We've Lost Dancing) — Fred again.. and The Blessed Madonna; Bangarang — Skrillex | none obvious | 2 boundary/contrast rows |
| 084 | 11 | Trip-Hop / Downtempo / Nocturnal Electronic | mixed survey coverage | mixed | A:14 / Al:11 / S:13 | Massive Attack; Portishead; Moby; Zero 7; DJ Shadow; Bonobo; Thievery Corporation; Morcheeba; Tricky; Air | Teardrop — Massive Attack; Unfinished Sympathy — Massive Attack; Porcelain — Moby; Glory Box — Portishead; Sour Times — Portishead; Protection — Massive Attack; Roads — Portishead; Destiny — Zero 7; 6 Underground — Sneaker Pimps; Lebanese Blonde — Thievery Corporation; Midnight in a Perfect World — DJ Shadow; Black Milk — Massive Attack; Ghostwriter — RJD2 | 2 multi-membership overlaps | thin contrast set |
| 085 | 11 | Indie Dance / Dance-Punk / Electroclash | bridge and lineage branching | mixed | A:14 / Al:9 / S:12 | LCD Soundsystem; Justice; Crystal Castles; The Rapture; The Knife; !!!; Soulwax; Cut Copy; Chromeo; Hercules & Love Affair | All My Friends — LCD Soundsystem; D.A.N.C.E. — Justice; Daft Punk Is Playing at My House — LCD Soundsystem; Heartbeats — The Knife; Crimewave — Crystal Castles; House of Jealous Lovers — The Rapture; Me and Giuliani Down by the School Yard — !!!; Lights & Music — Cut Copy; Blind — Hercules & Love Affair; Over and Over — Hot Chip; Emerge — Fischerspooner; Raingurl — Yaeji | none obvious | 6 boundary/contrast rows |
| 086 | 11 | Synthwave / Chillwave / Bedroom Electronic | bridge and lineage branching | mixed | A:13 / Al:10 / S:11 | M83; Chvrches; Grimes; Porter Robinson; Kavinsky; Washed Out; Purity Ring; HOME; Tycho; Caribou | Midnight City — M83; Nightcall — Kavinsky; Oblivion — Grimes; Recover — Chvrches; Shelter — Porter Robinson and Madeon; Feel It All Around — Washed Out; Fineshrine — Purity Ring; Resonance — HOME; A Walk — Tycho; Odessa — Caribou; Deadbeat Summer — Neon Indian | 6 multi-membership overlaps | 3 boundary/contrast rows |
| 087 | 11 | Experimental Electronic / IDM / Art-Electronic | artist/anchor affinity branching | mixed | A:16 / Al:11 / S:12 | Kraftwerk; Aphex Twin; Brian Eno; SOPHIE; Jean-Michel Jarre; Boards of Canada; Tangerine Dream; Nine Inch Nails; Bjork; Burial | Windowlicker — Aphex Twin; Autobahn — Kraftwerk; The Model — Kraftwerk; Oxygene, Pt. 4 — Jean-Michel Jarre; BIPP — SOPHIE; Roygbiv — Boards of Canada; 1/1 — Brian Eno; Closer — Nine Inch Nails; Joga — Bjork; Archangel — Burial; Chrome Country — Oneohtrix Point Never; My Red Hot Car — Squarepusher | 8 multi-membership overlaps | 6 boundary/contrast rows |
| 088 | 12 | 70s-80s Pop Sovereigns | album-world and gateway testing | mixed | A:7 / Al:6 / S:8 | Michael Jackson; Madonna; Whitney Houston; Prince; Janet Jackson; George Michael; Cyndi Lauper | Billie Jean — Michael Jackson; Thriller — Michael Jackson; Like a Prayer — Madonna; I Wanna Dance with Somebody — Whitney Houston; When Doves Cry — Prince; Girls Just Want to Have Fun — Cyndi Lauper; Careless Whisper — George Michael; Vogue — Madonna | 6 multi-membership overlaps | thin contrast set |
| 089 | 12 | 90s Pop / Teen Pop / TRL Monoculture | album-world and gateway testing | artist | A:12 / Al:6 / S:8 | Britney Spears; Mariah Carey; Backstreet Boys; Spice Girls; Christina Aguilera; Celine Dion; NSYNC; Justin Timberlake; Kelly Clarkson; Pink | ...Baby One More Time — Britney Spears; I Want It That Way — Backstreet Boys; Wannabe — Spice Girls; Fantasy — Mariah Carey; Bye Bye Bye — NSYNC; Genie in a Bottle — Christina Aguilera; Since U Been Gone — Kelly Clarkson; My Heart Will Go On — Celine Dion | 3 multi-membership overlaps | 2 boundary/contrast rows |
| 090 | 12 | 2000s Pop / Dance-Pop / Club-Pop | boundary and contrast calibration | mixed | A:8 / Al:6 / S:8 | Beyonce; Rihanna; Lady Gaga; Katy Perry; Bruno Mars; Black Eyed Peas; The Weeknd; Kesha | Bad Romance — Lady Gaga; Umbrella — Rihanna; Crazy in Love — Beyonce; Toxic — Britney Spears; Poker Face — Lady Gaga; Firework — Katy Perry; SexyBack — Justin Timberlake; I Gotta Feeling — Black Eyed Peas | 2 multi-membership overlaps | 5 boundary/contrast rows |
| 091 | 12 | 2010s Persona Pop / Architectural Pop | boundary and contrast calibration | mixed | A:7 / Al:6 / S:8 | Taylor Swift; Billie Eilish; Ariana Grande; Lorde; Lana Del Rey; Harry Styles; Miley Cyrus | Blank Space — Taylor Swift; Royals — Lorde; Bad Guy — Billie Eilish; Shake It Off — Taylor Swift; Thank U, Next — Ariana Grande; Formation — Beyonce; Video Games — Lana Del Rey; Wrecking Ball — Miley Cyrus | 1 multi-membership overlaps | 7 boundary/contrast rows |
| 092 | 12 | Adult Pop / TV-Drama Anthem / Inspirational Pop | album-world and gateway testing | mixed | A:9 / Al:6 / S:8 | Adele; Ed Sheeran; Sam Smith; Sia; Demi Lovato; Lewis Capaldi; Selena Gomez; Christina Perri; Rachel Platten | Rolling in the Deep — Adele; Hello — Adele; Chandelier — Sia; Shape of You — Ed Sheeran; Thinking Out Loud — Ed Sheeran; Stay with Me — Sam Smith; Someone You Loved — Lewis Capaldi; Fight Song — Rachel Platten | 1 multi-membership overlaps | 5 boundary/contrast rows |
| 093 | 12 | TikTok / Streaming-Era Pop / Internet Pop | boundary and contrast calibration | mixed | A:11 / Al:6 / S:10 | Olivia Rodrigo; Dua Lipa; Sabrina Carpenter; Doja Cat; Charli XCX; Chappell Roan; Camila Cabello; Shawn Mendes; Ice Spice; Tate McRae | Drivers License — Olivia Rodrigo; Levitating — Dua Lipa; Good 4 U — Olivia Rodrigo; Espresso — Sabrina Carpenter; Good Luck, Babe! — Chappell Roan; Say So — Doja Cat; Boy's a Liar Pt. 2 — PinkPantheress; Greedy — Tate McRae; Princess Diana — Ice Spice; 360 — Charli XCX | 5 multi-membership overlaps | 9 boundary/contrast rows |
| 094 | 13 | Reggaeton / Urbano / Latin Pop Crossover | song-first recognition and branching | mixed | A:14 / Al:9 / S:14 | Bad Bunny; Daddy Yankee; J Balvin; Karol G; Shakira; Enrique Iglesias; Ricky Martin; Luis Fonsi; Don Omar; Wisin & Yandel | Livin' la Vida Loca — Ricky Martin; Titi Me Pregunto — Bad Bunny; Gasolina — Daddy Yankee; Danza Kuduro — Don Omar featuring Lucenzo; Bailando — Enrique Iglesias featuring Descemer Bueno and Gente de Zona; Mi Gente — J Balvin and Willy William; Tusa — Karol G and Nicki Minaj; Despacito — Luis Fonsi and Daddy Yankee; Hips Don't Lie — Shakira featuring Wyclef Jean; Provenza — Karol G; Pepas — Farruko; Con Altura — Rosalia and J Balvin; Rakata — Wisin & Yandel; Envolver — Anitta | none obvious | thin contrast set |
| 095 | 13 | Regional Mexican / Corridos / Musica Mexicana | artist/anchor affinity branching | mixed | A:14 / Al:9 / S:14 | Juan Gabriel; Selena; Vicente Fernandez; Los Tigres del Norte; Peso Pluma; Jenni Rivera; Grupo Frontera; Natanael Cano; Eslabon Armado; Fuerza Regida | Como La Flor — Selena; Ella Baila Sola — Eslabon Armado and Peso Pluma; No Se Va — Grupo Frontera; Amor Prohibido — Selena; Bebe Dame — Fuerza Regida and Grupo Frontera; AMG — Natanael Cano, Peso Pluma, and Gabito Ballesteros; Volver, Volver — Vicente Fernandez; Querida — Juan Gabriel; Inolvidable — Jenni Rivera; La Puerta Negra — Los Tigres del Norte; El Rey — Vicente Fernandez; Adios Amor — Christian Nodal; Primera Cita — Carin Leon; Nieves de Enero — Chalino Sanchez | none obvious | thin contrast set |
| 096 | 13 | Salsa / Latin Dance / Tropical Pop | artist/anchor affinity branching | mixed | A:14 / Al:9 / S:13 | Marc Anthony; Gloria Estefan; Aventura; Romeo Santos; Celia Cruz; Hector Lavoe; Ruben Blades; Tito Puente; El Gran Combo de Puerto Rico; Elvis Crespo | Obsesion — Aventura; Suavemente — Elvis Crespo; Vivir Mi Vida — Marc Anthony; Conga — Miami Sound Machine; Propuesta Indecente — Romeo Santos; La Vida Es Un Carnaval — Celia Cruz; Oye Como Va — Tito Puente; El Cantante — Hector Lavoe; Quimbara — Celia Cruz and Johnny Pacheco; Idilio — Willie Colon; Burbujas de Amor — Juan Luis Guerra; Pedro Navaja — Ruben Blades and Willie Colon; Lloraras — Oscar D'Leon | none obvious | thin contrast set |
| 097 | 13 | Afrobeats / African Pop Crossover | song-first recognition and branching | mixed | A:14 / Al:9 / S:15 | Burna Boy; Wizkid; Rema; Tyla; Fela Kuti; CKay; Davido; Asake; Ayra Starr; Fireboy DML | Water — Tyla; Last Last — Burna Boy; Love Nwantiti — CKay; Calm Down — Rema; Essence — Wizkid featuring Tems; Unavailable — Davido featuring Musa Keys; Ye — Burna Boy; Zombie — Fela Kuti; Rush — Ayra Starr; Peru — Fireboy DML; Amapiano — Asake and Olamide; People — Libianca; Ku Lo Sa — Oxlade; Water No Get Enemy — Fela Kuti; Soso — Omah Lay | none obvious | thin contrast set |
| 098 | 13 | K-Pop / J-Pop / Asian Pop Crossover | song-first recognition and branching | mixed | A:14 / Al:9 / S:13 | BTS; BLACKPINK; NewJeans; PSY; SEVENTEEN; Stray Kids; TWICE; Girls' Generation; EXO; YOASOBI | DDU-DU DDU-DU — BLACKPINK; Dynamite — BTS; Butter — BTS; Super Shy — NewJeans; Gangnam Style — PSY; Cupid — FIFTY FIFTY; The Feels — TWICE; Gimme Chocolate!! — BABYMETAL; God's Menu — Stray Kids; Gee — Girls' Generation; Fantastic Baby — BIGBANG; Idol — YOASOBI; First Love — Hikaru Utada | none obvious | 4 boundary/contrast rows |
| 099 | 13 | Global Folk / World Fusion / Diaspora Roots | artist/anchor affinity branching | mixed | A:14 / Al:9 / S:13 | Bob Marley & The Wailers; Gipsy Kings; Buena Vista Social Club; Miriam Makeba; Ali Farka Toure; Nusrat Fateh Ali Khan; Youssou N'Dour; Deep Forest; Manu Chao; Cesaria Evora | One Love / People Get Ready — Bob Marley & The Wailers; Bamboleo — Gipsy Kings; Chan Chan — Buena Vista Social Club; 7 Seconds — Youssou N'Dour and Neneh Cherry; Pata Pata — Miriam Makeba; Mustt Mustt — Nusrat Fateh Ali Khan; Sweet Lullaby — Deep Forest; Me Gustas Tu — Manu Chao; Ai Du — Ali Farka Toure and Ry Cooder; Sabali — Amadou & Mariam; Sodade — Cesaria Evora; Dhun — Ravi Shankar; Cler Achel — Tinariwen | none obvious | 2 boundary/contrast rows |
| 100 | 14 | Vocal Standards / Crooners / Great American Songbook | song-first recognition and branching | mixed | A:10 / Al:8 / S:11 | Frank Sinatra; Nat King Cole; Louis Armstrong; Billie Holiday; Ella Fitzgerald; Bing Crosby; Dean Martin; Michael Buble; Tony Bennett; Sarah Vaughan | Fly Me to the Moon — Frank Sinatra; My Way — Frank Sinatra; Unforgettable — Nat King Cole; What a Wonderful World — Louis Armstrong; Strange Fruit — Billie Holiday; White Christmas — Bing Crosby; That's Amore — Dean Martin; Sway — Dean Martin; Feeling Good — Nina Simone; Someone to Watch Over Me — Ella Fitzgerald; I Left My Heart in San Francisco — Tony Bennett | 4 multi-membership overlaps | thin contrast set |
| 101 | 14 | Jazz Foundations / Bebop / Hard Bop Gateway | album-world and gateway testing | mixed | A:11 / Al:8 / S:11 | Miles Davis; John Coltrane; Dave Brubeck Quartet; Herbie Hancock; Chet Baker; Nina Simone; Stan Getz; Thelonious Monk; Charlie Parker; Charles Mingus | Take Five — Dave Brubeck Quartet; The Girl from Ipanema — Stan Getz and Astrud Gilberto; My Favorite Things — John Coltrane; So What — Miles Davis; My Funny Valentine — Chet Baker; Cantaloupe Island — Herbie Hancock; Blue in Green — Miles Davis; Round Midnight — Thelonious Monk; Goodbye Pork Pie Hat — Charles Mingus; Ko-Ko — Charlie Parker; Moanin — Art Blakey and the Jazz Messengers | none obvious | thin contrast set |
| 102 | 14 | Smooth Jazz / Jazz-Pop / Adult Instrumental | song-first recognition and branching | mixed | A:10 / Al:8 / S:11 | Kenny G; Norah Jones; Sade; George Benson; Grover Washington Jr.; Chuck Mangione; Herb Alpert; Diana Krall; David Sanborn; Spyro Gyra | Just the Two of Us — Grover Washington Jr. featuring Bill Withers; Songbird — Kenny G; Don't Know Why — Norah Jones; Smooth Operator — Sade; Feels So Good — Chuck Mangione; Breezin' — George Benson; Rise — Herb Alpert; The Look of Love — Diana Krall; Lily Was Here — David A. Stewart featuring Candy Dulfer; Soulful Strut — Young-Holt Unlimited; Morning Dance — Spyro Gyra | 2 multi-membership overlaps | 2 boundary/contrast rows |
| 103 | 14 | Classical Crossover / Instrumental Popular Canon | boundary and contrast calibration | mixed | A:10 / Al:8 / S:10 | Andrea Bocelli; Enya; Luciano Pavarotti; Yo-Yo Ma; Ludovico Einaudi; Lang Lang; Yiruma; Max Richter; Vanessa-Mae; Jackie Evancho | Con te partiro — Andrea Bocelli; Time to Say Goodbye — Andrea Bocelli and Sarah Brightman; Orinoco Flow — Enya; River Flows in You — Yiruma; Nessun dorma — Luciano Pavarotti; Nuvole Bianche — Ludovico Einaudi; On the Nature of Daylight — Max Richter; Cello Suite No. 1: Prelude — Yo-Yo Ma; La Campanella — Lang Lang; Adagio for Strings — London Philharmonic Orchestra | none obvious | 8 boundary/contrast rows |
| 104 | 15 | Broadway / Modern Musical Theater | album-world and gateway testing | mixed | A:10 / Al:8 / S:11 | Lin-Manuel Miranda; Andrew Lloyd Webber; Rodgers and Hammerstein; Original Broadway Cast of Wicked; Stephen Sondheim; Jonathan Larson; Claude-Michel Schonberg; Leonard Bernstein; Stephen Schwartz; Benj Pasek and Justin Paul | Defying Gravity — Idina Menzel and Kristin Chenoweth; My Shot — Original Broadway Cast of Hamilton; Seasons of Love — Original Broadway Cast of Rent; Do-Re-Mi — Julie Andrews and The Sound of Music Cast; I Dreamed a Dream — Patti LuPone; The Room Where It Happens — Leslie Odom Jr.; America — Original Broadway Cast of West Side Story; One Day More — Original London Cast of Les Miserables; The Music of the Night — Michael Crawford; You Will Be Found — Original Broadway Cast of Dear Evan Hansen; Being Alive — Dean Jones | none obvious | thin contrast set |
| 105 | 15 | Disney / Family Soundtrack / Animated Musical Canon | song-first recognition and branching | mixed | A:9 / Al:8 / S:11 | Alan Menken; Elton John; Kristen Anderson-Lopez and Robert Lopez; Kristen Anderson-Lopez; Robert Lopez; Howard Ashman; Germaine Franco; Phil Collins; Randy Newman | Circle of Life — Carmen Twillie and Lebo M.; Can You Feel the Love Tonight — Elton John; Let It Go — Idina Menzel; A Whole New World — Peabo Bryson and Regina Belle; You've Got a Friend in Me — Randy Newman; How Far I'll Go — Auli'i Cravalho; We Don't Talk About Bruno — Carolina Gaitan, Mauro Castillo, Adassa, Rhenzy Feliz, Diane Guerrero, Stephanie Beatriz and Encanto Cast; Part of Your World — Jodi Benson; Under the Sea — Samuel E. Wright; Colors of the Wind — Judy Kuhn; Remember Me — Benjamin Bratt | 2 multi-membership overlaps | thin contrast set |
| 106 | 15 | Movie Soundtracks / 80s-90s-00s Soundtrack Memory | album-world and gateway testing | mixed | A:9 / Al:8 / S:12 | Prince; Whitney Houston; Bee Gees; Celine Dion; Bill Medley and Jennifer Warnes; Kenny Loggins; Simon and Garfunkel; Adele; Eminem | Stayin' Alive — Bee Gees; My Heart Will Go On — Celine Dion; Footloose — Kenny Loggins; Purple Rain — Prince and The Revolution; I Will Always Love You — Whitney Houston; (I've Had) The Time of My Life — Bill Medley and Jennifer Warnes; Lose Yourself — Eminem; Danger Zone — Kenny Loggins; Eye of the Tiger — Survivor; Skyfall — Adele; Hooked on a Feeling — Blue Swede; Man of Constant Sorrow — The Soggy Bottom Boys | 11 multi-membership overlaps | thin contrast set |
| 107 | 15 | Film Score / Epic Score / Ambient Cinematic | artist/anchor affinity branching | mixed | A:11 / Al:9 / S:13 | John Williams; Hans Zimmer; Ennio Morricone; Howard Shore; Danny Elfman; James Horner; Alan Silvestri; John Barry; Ludwig Goransson; Trent Reznor and Atticus Ross | Main Title — John Williams; The Imperial March — John Williams; Chariots of Fire — Vangelis; Hedwig's Theme — John Williams; Time — Hans Zimmer; James Bond Theme — John Barry Orchestra; Theme from Jurassic Park — John Williams; The Ecstasy of Gold — Ennio Morricone; The Shire — Howard Shore; Back to the Future — Alan Silvestri; Batman Theme — Danny Elfman; Wakanda — Ludwig Goransson; Hand Covers Bruise — Trent Reznor and Atticus Ross | none obvious | thin contrast set |
| 108 | 16 | Black Gospel / Gospel Soul | artist/anchor affinity branching | mixed | A:13 / Al:11 / S:13 | Aretha Franklin; Mahalia Jackson; Kirk Franklin; Sister Rosetta Tharpe; Sam Cooke and The Soul Stirrers; The Staple Singers; Andrae Crouch; CeCe Winans; Mary Mary; Yolanda Adams | I'll Take You There — The Staple Singers; Amazing Grace — Aretha Franklin; Move On Up a Little Higher — Mahalia Jackson; Stomp — God's Property featuring Kirk Franklin; Soon and Very Soon — Andrae Crouch; Believe for It — CeCe Winans; Shackles (Praise You) — Mary Mary; Up Above My Head — Sister Rosetta Tharpe; Break Every Chain — Tasha Cobbs Leonard; Open My Heart — Yolanda Adams; No Weapon — Fred Hammond; Jesus Gave Me Water — Sam Cooke and The Soul Stirrers; You Brought the Sunshine — The Clark Sisters | 3 multi-membership overlaps | thin contrast set |
| 109 | 16 | CCM / Christian Pop-Rock / Worship Radio | artist/anchor affinity branching | mixed | A:14 / Al:9 / S:14 | Amy Grant; Lauren Daigle; MercyMe; DC Talk; Casting Crowns; Jars of Clay; Michael W. Smith; Steven Curtis Chapman; TobyMac; Third Day | Baby Baby — Amy Grant; You Say — Lauren Daigle; I Can Only Imagine — MercyMe; Jesus Freak — DC Talk; Flood — Jars of Clay; Place in This World — Michael W. Smith; Who Am I — Casting Crowns; God's Not Dead (Like a Lion) — Newsboys; Dive — Steven Curtis Chapman; Cry Out to Jesus — Third Day; Made to Love — TobyMac; God Only Knows — for KING & COUNTRY; Dare You to Move — Switchfoot; Monster — Skillet | none obvious | 3 boundary/contrast rows |
| 110 | 16 | Worship / Praise / Church Songbook | song-first recognition and branching | mixed | A:12 / Al:9 / S:17 | Chris Tomlin; Hillsong Worship; Matt Redman; Elevation Worship; Maverick City Music; Bethel Music; Kari Jobe; Keith and Kristyn Getty; Phil Wickham; Passion | How Great Is Our God — Chris Tomlin; What a Beautiful Name — Hillsong Worship; 10,000 Reasons (Bless the Lord) — Matt Redman; Way Maker — Sinach; Goodness of God — Bethel Music and Jenn Johnson; Reckless Love — Cory Asbury; Shout to the Lord — Darlene Zschech; Oceans (Where Feet May Fail) — Hillsong United; In Christ Alone — Keith and Kristyn Getty; No Longer Slaves — Bethel Music; Graves Into Gardens — Elevation Worship; Revelation Song — Kari Jobe; Great Are You Lord — All Sons & Daughters; Jireh — Elevation Worship and Maverick City Music featuring Chandler Moore and Naomi Raine; The Blessing — Kari Jobe, Cody Carnes and Elevation Worship; Build My Life — Pat Barrett; House of the Lord — Phil Wickham | none obvious | thin contrast set |
| 111 | 17 | Novelty / Comedy / Weird Pop | song-first recognition and branching | mixed | A:7 / Al:4 / S:8 | Weird Al Yankovic; Ray Stevens; Bobby Boris Pickett; The Lonely Island; Spike Jones; Sheb Wooley; Napoleon XIV | Monster Mash — Bobby Boris Pickett; Amish Paradise — Weird Al Yankovic; Eat It — Weird Al Yankovic; The Streak — Ray Stevens; White & Nerdy — Weird Al Yankovic; The Purple People Eater — Sheb Wooley; They're Coming to Take Me Away, Ha-Haaa! — Napoleon XIV; Ahab the Arab — Ray Stevens | none obvious | 4 boundary/contrast rows |
| 112 | 17 | Holiday / Christmas / Seasonal Canon | album-world and gateway testing | mixed | A:12 / Al:8 / S:10 | Mariah Carey; Bing Crosby; Brenda Lee; Nat King Cole; Wham!; Trans-Siberian Orchestra; Bobby Helms; Jose Feliciano; Michael Buble; Vince Guaraldi | All I Want for Christmas Is You — Mariah Carey; White Christmas — Bing Crosby; Rockin' Around the Christmas Tree — Brenda Lee; The Christmas Song — Nat King Cole; Jingle Bell Rock — Bobby Helms; Feliz Navidad — Jose Feliciano; Last Christmas — Wham!; Have Yourself a Merry Little Christmas — Judy Garland; Linus and Lucy — Vince Guaraldi Trio; Christmas Eve/Sarajevo 12/24 — Trans-Siberian Orchestra | 7 multi-membership overlaps | thin contrast set |
| 113 | 17 | Party / Wedding / Karaoke / Bar Singalong Canon | boundary and contrast calibration | mixed | A:11 / Al:6 / S:15 | ABBA; Neil Diamond; Bon Jovi; Journey; The Killers; Garth Brooks; Village People; Shania Twain; DJ Casper; Cupid | Don't Stop Believin' — Journey; Sweet Caroline — Neil Diamond; Livin' on a Prayer — Bon Jovi; Mr. Brightside — The Killers; Y.M.C.A. — Village People; Friends in Low Places — Garth Brooks; Dancing Queen — ABBA; Man! I Feel Like a Woman! — Shania Twain; Cha Cha Slide — DJ Casper; September — Earth, Wind & Fire; Celebration — Kool & The Gang; Macarena — Los Del Rio; Bohemian Rhapsody — Queen; Love Shack — The B-52s; Cupid Shuffle — Cupid | 14 multi-membership overlaps | 25 boundary/contrast rows |
| 114 | 17 | Kids / Family / Household Context Music | boundary and contrast calibration | song | A:5 / Al:4 / S:9 | Disney; Raffi; Pinkfong; Kidz Bop; The Wiggles | Baby Beluga — Raffi; Down by the Bay — Raffi; Baby Shark — Pinkfong; Let It Go — Idina Menzel; We Don't Talk About Bruno — Encanto Cast; Hakuna Matata — The Lion King Cast; The Wheels on the Bus — Traditional; Bananaphone — Raffi; Hot Potato — The Wiggles | 2 multi-membership overlaps | 10 boundary/contrast rows |
| 115 | 18 | Current Rock Revival / Post-Punk New Wave 2020s | boundary and contrast calibration | mixed | A:13 / Al:9 / S:11 | Fontaines D.C.; Turnstile; Wet Leg; IDLES; Amyl and the Sniffers; The Beths; Wednesday; The Linda Lindas; MJ Lenderman; Yard Act | Starburster — Fontaines D.C.; Blackout — Turnstile; Chaise Longue — Wet Leg; Guided by Angels — Amyl and the Sniffers; She's Leaving You — MJ Lenderman; Chosen to Deserve — Wednesday; Racist, Sexist Boy — The Linda Lindas; Danny Nedelko — IDLES; The Overload — Yard Act; bmbmbm — black midi; Concorde — Black Country, New Road | none obvious | 8 boundary/contrast rows |
| 116 | 18 | Modern Indie Singer-Songwriter / Sad-Prestige Indie | artist/anchor affinity branching | mixed | A:12 / Al:9 / S:12 | Phoebe Bridgers; boygenius; Mitski; Big Thief; Japanese Breakfast; Clairo; Lucy Dacus; Snail Mail; Adrianne Lenker; Soccer Mommy | Nobody — Mitski; Kyoto — Phoebe Bridgers; Not Strong Enough — boygenius; Bags — Clairo; Be Sweet — Japanese Breakfast; Night Shift — Lucy Dacus; Pristine — Snail Mail; Your Dog — Soccer Mommy; Not — Big Thief; Appointments — Julien Baker; anything — Adrianne Lenker; Runner — Alex G | none obvious | thin contrast set |
| 117 | 18 | Modern Psych / Groove Indie / Tame-MGMT-Arctic Axis | song-first recognition and branching | mixed | A:10 / Al:8 / S:10 | Tame Impala; Arctic Monkeys; Glass Animals; MGMT; Foster the People; Khruangbin; alt-J; Royal Blood; Unknown Mortal Orchestra; King Gizzard & the Lizard Wizard | Do I Wanna Know? — Arctic Monkeys; Heat Waves — Glass Animals; The Less I Know the Better — Tame Impala; Electric Feel — MGMT; Pumped Up Kicks — Foster the People; Out of the Black — Royal Blood; Breezeblocks — alt-J; Multi-Love — Unknown Mortal Orchestra; Time (You and I) — Khruangbin; Gamma Knife — King Gizzard & the Lizard Wizard | 1 multi-membership overlaps | thin contrast set |
| 118 | 18 | Heavy Modern Alternative / Active Rock Survival | artist/anchor affinity branching | mixed | A:10 / Al:8 / S:10 | Bring Me the Horizon; Sleep Token; Maneskin; Ghost; Bad Omens; Nothing But Thieves; Highly Suspect; I Prevail; Deftones; Spiritbox | Can You Feel My Heart — Bring Me the Horizon; The Summoning — Sleep Token; Beggin' — Maneskin; Just Pretend — Bad Omens; Square Hammer — Ghost; My Name Is Human — Highly Suspect; Hurricane — I Prevail; Amsterdam — Nothing But Thieves; Holy Roller — Spiritbox; Change (In the House of Flies) — Deftones | 17 multi-membership overlaps | 3 boundary/contrast rows |
| 119 | 18 | Hyperpop / Synthetic Edge-Pop / Internet Maximalism | artist/anchor affinity branching | mixed | A:12 / Al:9 / S:12 | Charli XCX; SOPHIE; 100 gecs; Caroline Polachek; PinkPantheress; Rina Sawayama; Grimes; Porter Robinson; Dorian Electra; A. G. Cook | money machine — 100 gecs; Immaterial — SOPHIE; Pain — PinkPantheress; Bunny Is a Rider — Caroline Polachek; Oblivion — Grimes; Look at the Sky — Porter Robinson; XS — Rina Sawayama; Career Boy — Dorian Electra; Vroom Vroom — Charli XCX; Beautiful — A. G. Cook; Mequetrefe — Arca; dazies — Yeule | 8 multi-membership overlaps | 4 boundary/contrast rows |
| 120 | 18 | Algorithmic Mood / Lo-Fi / Chill / Study Music | bridge and lineage branching | mixed | A:10 / Al:8 / S:10 | Nujabes; J Dilla; Lo-fi Girl; Bonobo; idealism; potsu; Tycho; Boards of Canada; Emancipator; Jinsang | lofi hip hop radio — Lo-fi Girl; Feather — Nujabes featuring Cise Starr and Akin; Kiara — Bonobo; both of us — idealism; just friends — potsu; Time: The Donut of the Heart — J Dilla; A Walk — Tycho; Roygbiv — Boards of Canada; First Snow — Emancipator; Affection. — Jinsang | 8 multi-membership overlaps | 6 boundary/contrast rows |

## Survey Surface Samples

These are candidate surfaces, not final UI pages. Page 1 favors `core`, high-recognition anchors/gateways. Page 2/3 favors bridges, boundary rows, contrast rows, and deeper lane checks.

| family_id | family_name | Artist Survey Page 1 candidates | Artist Survey Page 2 adaptive candidates | Song Survey Page 1 candidates | Song Survey Page 2/3 candidates | Album Survey candidates |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Early Rock, Oldies, Doo-Wop, Pre-Beatles Pop | Chuck Berry; Elvis Presley; Ray Charles; Ricky Nelson; Sam Cooke; The Beach Boys; The Platters; The Shirelles; Little Richard; The Drifters; The Ronettes; Buddy Holly | The Trashmen; The Kingsmen; Carole King; Hank Ballard & The Midnighters; Eddie Cochran; Clyde McPhatter; Solomon Burke; Dee Dee Sharp; Fabian; Johnny and the Hurricanes; Lloyd Price; The Impressions | Stand by Me — Ben E. King; Rock Around the Clock — Bill Haley & His Comets; Blue Suede Shoes — Carl Perkins; Johnny B. Goode — Chuck Berry; Heartbreak Hotel — Elvis Presley; Hound Dog — Elvis Presley; Jailhouse Rock — Elvis Presley; Earth Angel — The Penguins; Be My Baby — The Ronettes; Will You Love Me Tomorrow — The Shirelles; The Twist — Chubby Checker; Don't Be Cruel — Elvis Presley | Blue Moon — The Marcels; Book of Love — The Monotones; Louie Louie — The Kingsmen; Dream Lover — Bobby Darin; Teen Angel — Mark Dinning; Tell Laura I Love Her — Ray Peterson; Iko Iko — The Dixie Cups; Please Mr. Postman — The Marvelettes; To Know Him Is to Love Him — The Teddy Bears; Walk, Don't Run — The Ventures; Itsy Bitsy Teenie Weenie Yellow Polkadot Bikini — Brian Hyland; The Boy from New York City — The Ad Libs; Rhythm of the Rain — The Cascades; Surfin' Bird — The Trashmen; Johnny Angel — Shelley Fabares; Surfin' Bird — The Trashmen | Elvis Presley — Elvis Presley; Here's Little Richard — Little Richard; The Genius of Ray Charles — Ray Charles; Surfin' U.S.A. — The Beach Boys; Presenting the Fabulous Ronettes Featuring Veronica — The Ronettes; Surfin' Safari — The Beach Boys; King of the Surf Guitar — Dick Dale and His Del-Tones; Live at the Apollo — James Brown; A Christmas Gift for You from Phil Spector — Various Artists; Where Did Our Love Go — The Supremes; At Last! — Etta James; Johnny's Greatest Hits — Johnny Mathis |
| 2 | Beatles, British Invasion, 60s Pop-Rock | The Beatles; The Rolling Stones; The Jimi Hendrix Experience; The Who; The Doors; Bob Dylan; The Beach Boys; Simon & Garfunkel; The Byrds; The Kinks; Cream; The Velvet Underground | The Monkees; The Animals; The Hollies; The Yardbirds; The Zombies; Buffalo Springfield; Iron Butterfly; Steppenwolf; The Turtles; Procol Harum; Donovan; Paul Revere & the Raiders | God Only Knows — The Beach Boys; Louie Louie — The Kingsmen; Good Vibrations — The Beach Boys; Strawberry Fields Forever — The Beatles; I Want to Hold Your Hand — The Beatles; (I Can't Get No) Satisfaction — The Rolling Stones; House of the Rising Sun — The Animals; Light My Fire — The Doors; Purple Haze — The Jimi Hendrix Experience; You Really Got Me — The Kinks; My Generation — The Who; 96 Tears — ? and the Mysterians | Born to Be Wild — Steppenwolf; Wouldn't It Be Nice — The Beach Boys; Penny Lane — The Beatles; Never My Love — The Association; Turn! Turn! Turn! — The Byrds; Somebody to Love — Jefferson Airplane; White Rabbit — Jefferson Airplane; A Whiter Shade of Pale — Procol Harum; Wild Thing — The Troggs; I Wanna Be Your Dog — The Stooges; In-A-Gadda-Da-Vida — Iron Butterfly; Gimme Some Lovin' — Spencer Davis Group; Piece of My Heart — Big Brother and the Holding Company; Ferry Cross the Mersey — Gerry and the Pacemakers; Do Wah Diddy Diddy — Manfred Mann; Psychotic Reaction — Count Five | Sgt. Pepper's Lonely Hearts Club Band — The Beatles; Are You Experienced — The Jimi Hendrix Experience; Revolver — The Beatles; Pet Sounds — The Beach Boys; The Doors — The Doors; Disraeli Gears — Cream; Magical Mystery Tour — The Beatles; Rubber Soul — The Beatles; Electric Ladyland — The Jimi Hendrix Experience; A Hard Day's Night — The Beatles; Nuggets: Original Artyfacts From the First Psychedelic Era, 1965-1968 — Various Artists; The Velvet Underground & Nico — The Velvet Underground & Nico |
| 3 | Classic Rock, Album Rock, Progressive Rock | Led Zeppelin; Pink Floyd; Pink Floyd; David Bowie; Led Zeppelin; AC/DC; Eagles; Fleetwood Mac; Lynyrd Skynyrd; Black Sabbath; Elton John; Queen | Aerosmith; Aerosmith; Creedence Clearwater Revival; Tom Petty and the Heartbreakers; Carpenters; Hall & Oates; Carole King; James Taylor; Rush; Deep Purple; T. Rex; The Who | Stairway to Heaven — Led Zeppelin; Back in Black — AC/DC; Hotel California — Eagles; Dreams — Fleetwood Mac; Sweet Home Alabama — Lynyrd Skynyrd; Bohemian Rhapsody — Queen; Highway to Hell — AC/DC; Free Bird — Lynyrd Skynyrd; Iron Man — Black Sabbath; Whole Lotta Love — Led Zeppelin; What a Fool Believes — The Doobie Brothers; Starman — David Bowie | Piano Man — Billy Joel; Tom Sawyer — Rush; My Sharona — The Knack; Fortunate Son — Creedence Clearwater Revival; Fire and Rain — James Taylor; You're So Vain — Carly Simon; It's Too Late — Carole King; Bad Moon Rising — Creedence Clearwater Revival; Old Time Rock and Roll — Bob Seger; Walk on the Wild Side — Lou Reed; What I Like About You — The Romantics; Bang a Gong (Get It On) — T. Rex; Roundabout — Yes; Piano Man — Billy Joel; Rocket Man — Elton John; Peg — Steely Dan | The Rise and Fall of Ziggy Stardust and the Spiders from Mars — David Bowie; Led Zeppelin IV — Led Zeppelin; The Dark Side of the Moon — Pink Floyd; The Dark Side of the Moon — Pink Floyd; Rumours — Fleetwood Mac; Paranoid — Black Sabbath; Their Greatest Hits 1971-1975 — Eagles; Back in Black — AC/DC; Hotel California — Eagles; Highway to Hell — AC/DC; Led Zeppelin II — Led Zeppelin; Wish You Were Here — Pink Floyd |
| 4 | Singer-Songwriter, Folk, Americana, Adult Songcraft | Carole King; Carole King; Tracy Chapman; Billy Joel; James Taylor; Cat Stevens; Paul Simon; Sheryl Crow; Bob Dylan; Mumford & Sons; The Lumineers; John Prine | Elton John; Bob Dylan; Neil Young; Norah Jones; Noah Kahan; Norah Jones; Wilco; Harry Nilsson; Ben Folds; Steve Earle; Natalie Merchant; The Avett Brothers | Fast Car — Tracy Chapman; This Land Is Your Land — Woody Guthrie; Piano Man — Billy Joel; Fire and Rain — James Taylor; Blowin' in the Wind — Bob Dylan; You've Got a Friend — Carole King; American Pie — Don McLean; Ho Hey — The Lumineers; It's Too Late — Carole King; Big Yellow Taxi — Joni Mitchell; Little Lion Man — Mumford & Sons; We Shall Overcome — Pete Seeger et al. / traditional | Mr. Jones — Counting Crows; Time in a Bottle — Jim Croce; Cat's in the Cradle — Harry Chapin; Your Song — Elton John; I Will Wait — Mumford & Sons; Heart of Gold — Neil Young; Blowin' in the Wind — Bob Dylan; You Were Meant for Me — Jewel; Both Sides Now — Joni Mitchell; Stick Season — Noah Kahan; Don't Know Why — Norah Jones; Angel — Sarah McLachlan; Ophelia — The Lumineers; Don't Know Why — Norah Jones; Riptide — Vance Joy; Without You — Harry Nilsson | Tapestry — Carole King; Tapestry — Carole King; Blue — Joni Mitchell; Tracy Chapman — Tracy Chapman; The Freewheelin' Bob Dylan — Bob Dylan; The Stranger — Billy Joel; Sigh No More — Mumford & Sons; Tuesday Night Music Club — Sheryl Crow; The Lumineers — The Lumineers; John Prine — John Prine; For Emma, Forever Ago — Bon Iver; Car Wheels on a Gravel Road — Lucinda Williams |
| 5 | Country | Dolly Parton; Garth Brooks; Johnny Cash; Patsy Cline; Willie Nelson; Shania Twain; Kenny Rogers; Luke Combs; Florida Georgia Line; Morgan Wallen; Carrie Underwood; Chris Stapleton | John Denver; Dwight Yoakam; Emmylou Harris; The Chicks; Eric Church; Faith Hill; Tim McGraw; Zach Bryan; Lady A; Marty Robbins; Toby Keith; LeAnn Rimes | Islands in the Stream — Kenny Rogers and Dolly Parton; Before He Cheats — Carrie Underwood; Jolene — Dolly Parton; 9 to 5 — Dolly Parton; Cruise — Florida Georgia Line; Friends in Low Places — Garth Brooks; Rhinestone Cowboy — Glen Campbell; Ring of Fire — Johnny Cash; The Gambler — Kenny Rogers; Beer Never Broke My Heart — Luke Combs; Last Night — Morgan Wallen; Crazy — Patsy Cline | How Do I Live — LeAnn Rimes; Wagon Wheel — Darius Rucker; Me and Bobby McGee — Kris Kristofferson; Boot Scootin' Boogie — Brooks & Dunn; Copperhead Road — Steve Earle; Something in the Orange — Zach Bryan; Stand by Your Man — Tammy Wynette; El Paso — Marty Robbins; I Hope You Dance — Lee Ann Womack; Should've Been a Cowboy — Toby Keith; Independence Day — Martina McBride; King of the Road — Roger Miller; Oklahoma Smokeshow — Zach Bryan; Act Naturally — Buck Owens; Need a Favor — Jelly Roll; Blue Yodel No. 1 (T for Texas) — Jimmie Rodgers | Traveller — Chris Stapleton; No Fences — Garth Brooks; At Folsom Prison — Johnny Cash; Dangerous: The Double Album — Morgan Wallen; Come On Over — Shania Twain; This One's for You — Luke Combs; Fearless — Taylor Swift; Coat of Many Colors — Dolly Parton; Here's to the Good Times — Florida Georgia Line; 40 Greatest Hits — Hank Williams; The Gambler — Kenny Rogers; Mama Tried — Merle Haggard |
| 6 | Soul, Funk, Disco, R&B Foundations | Aretha Franklin; Donna Summer; Frank Ocean; James Brown; Stevie Wonder; Janet Jackson; Marvin Gaye; Otis Redding; Chic; Lauryn Hill; Luther Vandross; SZA | Commodores; Percy Sledge; Etta James; Marvin Gaye; Mary J. Blige; Roberta Flack; Village People; Beyonce; Toni Braxton; Usher; Booker T. & the M.G.'s; Jill Scott | Respect — Aretha Franklin; Stayin' Alive — Bee Gees; I Feel Love — Donna Summer; I Will Survive — Gloria Gaynor; My Girl — The Temptations; (Sittin' On) The Dock of the Bay — Otis Redding; Superstition — Stevie Wonder; Let's Stay Together — Al Green; Le Freak — Chic; Good Times — Chic; September — Earth, Wind & Fire; I Want You Back — Jackson 5 | When a Man Loves a Woman — Percy Sledge; No Diggity — Blackstreet feat. Dr. Dre; Can't Get Enough of Your Love, Babe — Barry White; Hold On — En Vogue; Weak — SWV; I'll Take You There — Staple Singers; Disco Inferno — The Trammps; Brick House — Commodores; Shining Star — Earth, Wind & Fire; Here and Now — Luther Vandross; My Guy — Mary Wells; Killing Me Softly with His Song — Roberta Flack; Un-Break My Heart — Toni Braxton; Y.M.C.A. — Village People; Earned It — The Weeknd; Super Freak — Rick James | I Never Loved a Man the Way I Love You — Aretha Franklin; The Miseducation of Lauryn Hill — Lauryn Hill; What's Going On — Marvin Gaye; Channel Orange — Frank Ocean; Blonde — Frank Ocean; Ctrl — SZA; Songs in the Key of Life — Stevie Wonder; Saturday Night Fever — Various Artists; Control — Janet Jackson; CrazySexyCool — TLC; Rapture — Anita Baker; Bad Girls — Donna Summer |
| 7 | Hip-Hop | Run-DMC; 2Pac; Dr. Dre; Drake; Eminem; Kanye West; Kendrick Lamar; OutKast; The Notorious B.I.G.; Jay-Z; Lil Wayne; Snoop Dogg | Boogie Down Productions; Mobb Deep; MF DOOM; UGK; Chief Keef; Gang Starr; Gucci Mane; Jeezy; Mos Def / Yasiin Bey; The Roots; Three 6 Mafia; Young Thug | In Da Club — 50 Cent; Nuthin' but a G Thang — Dr. Dre feat. Snoop Doggy Dogg; Lose Yourself — Eminem; The Message — Grandmaster Flash and the Furious Five; Rapper's Delight — The Sugarhill Gang; California Love — 2Pac feat. Dr. Dre; Fight the Power — Public Enemy; Juicy — The Notorious B.I.G.; SICKO MODE — Travis Scott; HUMBLE. — Kendrick Lamar; Bad and Boujee — Migos feat. Lil Uzi Vert; Gin and Juice — Snoop Dogg | Day 'n' Nite — Kid Cudi; Magnolia — Playboi Carti; Bank Account — 21 Savage; This Is America — Childish Gambino; DNA. — Kendrick Lamar; Stand Up — Ludacris feat. Shawnna; Who Am I? (What's My Name?) — Snoop Dogg; goosebumps — Travis Scott; 21 Questions — 50 Cent feat. Nate Dogg; WAP — Cardi B feat. Megan Thee Stallion; Insane in the Brain — Cypress Hill; Low Life — Future feat. The Weeknd; Big Pimpin' — Jay-Z feat. UGK; Heartless — Kanye West; Drip Too Hard — Lil Baby and Gunna; If I Ruled the World (Imagine That) — Nas feat. Lauryn Hill | The Chronic — Dr. Dre; The Marshall Mathers LP — Eminem; good kid, m.A.A.d city — Kendrick Lamar; To Pimp a Butterfly — Kendrick Lamar; Doggystyle — Snoop Dogg; Ready to Die — The Notorious B.I.G.; All Eyez on Me — 2Pac; Get Rich or Die Tryin' — 50 Cent; Raising Hell — Run-DMC; Licensed to Ill — Beastie Boys; Take Care — Drake; The Score — Fugees |
| 8 | Punk, Hardcore, Post-Punk, New Wave | The Clash; Depeche Mode; Talking Heads; The Cure; The Police; The Cars; Blondie; Duran Duran; Eurythmics; INXS; Ramones; Sex Pistols | A-ha; The B-52's; Pixies; The Human League; Devo; Elvis Costello; Misfits; Soft Cell; Violent Femmes; Gary Numan; Tears for Fears; They Might Be Giants | Take On Me — A-ha; Heart of Glass — Blondie; Enjoy the Silence — Depeche Mode; Personal Jesus — Depeche Mode; Hungry Like the Wolf — Duran Duran; Sweet Dreams (Are Made of This) — Eurythmics; Need You Tonight — INXS; Love Will Tear Us Apart — Joy Division; I Wanna Be Sedated — Ramones; Tainted Love — Soft Cell; Once in a Lifetime — Talking Heads; Psycho Killer — Talking Heads | Brass in Pocket — Pretenders; Our Lips Are Sealed — The Go-Go's; Don't You Want Me — The Human League; Blister in the Sun — Violent Femmes; Whip It — Devo; Cars — Gary Numan; Where Is My Mind? — Pixies; Everybody Wants to Rule the World — Tears for Fears; Love Shack — The B-52's; Last Caress — Misfits; Institutionalized — Suicidal Tendencies; A Little Respect — Erasure; Under the Milky Way — The Church; Is She Really Going Out with Him? — Joe Jackson; So Alive — Love and Rockets; Only You — Yazoo | Violator — Depeche Mode; Rio — Duran Duran; Sweet Dreams (Are Made of This) — Eurythmics; Kick — INXS; The Cars — The Cars; London Calling — The Clash; Disintegration — The Cure; Synchronicity — The Police; Parallel Lines — Blondie; Unknown Pleasures — Joy Division; Power, Corruption & Lies — New Order; Horses — Patti Smith |
| 9 | Metal and Heavy Music | Black Sabbath; Metallica; Motley Crue; Tool; Korn; Black Sabbath; Nine Inch Nails; Slipknot; System of a Down; Avenged Sevenfold; Linkin Park; Ozzy Osbourne | Queens of the Stone Age; Disturbed; Twisted Sister; Whitesnake; Europe; Anthrax; Cannibal Corpse; Sepultura; Skid Row; Meshuggah; Opeth; Trivium | Paranoid — Black Sabbath; Pour Some Sugar on Me — Def Leppard; Master of Puppets — Metallica; Enter Sandman — Metallica; Crazy Train — Ozzy Osbourne; Iron Man — Black Sabbath; War Pigs — Black Sabbath; Livin' on a Prayer — Bon Jovi; Sweet Child o' Mine — Guns N' Roses; In the End — Linkin Park; One — Metallica; Chop Suey! — System of a Down | Dragula — Rob Zombie; We're Not Gonna Take It — Twisted Sister; Here I Go Again — Whitesnake; Down with the Sickness — Disturbed; Cum On Feel the Noize — Quiet Riot; Bulls on Parade — Rage Against the Machine; Wanted Dead or Alive — Bon Jovi; Nookie — Limp Bizkit; Last Resort — Papa Roach; Rollin' — Limp Bizkit; The Beautiful People — Marilyn Manson; Cherry Pie — Warrant; The Final Countdown — Europe; Hurt — Nine Inch Nails; Sweet Leaf — Black Sabbath; Sweet Leaf — Black Sabbath | Paranoid — Black Sabbath; Master of Puppets — Metallica; Hybrid Theory — Linkin Park; Toxicity — System of a Down; Aenima — Tool; Hysteria — Def Leppard; The Downward Spiral — Nine Inch Nails; Slippery When Wet — Bon Jovi; Follow the Leader — Korn; Metallica — Metallica; Dr. Feelgood — Motley Crue; Pyromania — Def Leppard |
| 10 | Alternative, Indie, Grunge, Emo | Nirvana; Green Day; Pearl Jam; Pixies; Blink-182; My Chemical Romance; The White Stripes; R.E.M.; Weezer; Fall Out Boy; Foo Fighters; Paramore | Arctic Monkeys; The Black Keys; The Cure; The Cranberries; The Killers; Panic! at the Disco; Dinosaur Jr.; The Jesus and Mary Chain; Bloc Party; Jane's Addiction; The Breeders; Dashboard Confessional | Smells Like Teen Spirit — Nirvana; Seven Nation Army — The White Stripes; Welcome to the Black Parade — My Chemical Romance; All the Small Things — Blink-182; Basket Case — Green Day; Black Hole Sun — Soundgarden; Sugar, We're Goin Down — Fall Out Boy; Everlong — Foo Fighters; The Middle — Jimmy Eat World; Fade Into You — Mazzy Star; Float On — Modest Mouse; Come As You Are — Nirvana | Mr. Brightside — The Killers; Come Out and Play — The Offspring; I Write Sins Not Tragedies — Panic! at the Disco; Stacy's Mom — Fountains of Wayne; Good Riddance (Time of Your Life) — Green Day; Lightning Crashes — Live; Black — Pearl Jam; Lonely Boy — The Black Keys; Zombie — The Cranberries; Semi-Charmed Life — Third Eye Blind; Space Song — Beach House; Glycerine — Bush; Decode — Paramore; Rebel Girl — Bikini Kill; Banquet — Bloc Party; Cannonball — The Breeders | Nevermind — Nirvana; Dookie — Green Day; Ten — Pearl Jam; Doolittle — Pixies; Enema of the State — Blink-182; The Black Parade — My Chemical Romance; Superunknown — Soundgarden; Weezer (Blue Album) — Weezer; The Colour and the Shape — Foo Fighters; In Utero — Nirvana; Siamese Dream — Smashing Pumpkins; Elephant — The White Stripes |
| 11 | Electronic, Dance, Club, Industrial, Experimental Pop | Daft Punk; Avicii; Calvin Harris; David Guetta; Disclosure; Fred again..; Frankie Knuckles; Kraftwerk; Massive Attack; Aphex Twin; LCD Soundsystem; Portishead | Major Lazer; Inner City; M83; Brian Eno; CeCe Peniston; Fatboy Slim; Moby; Skrillex; Crystal Waters; Flume; Orbital; Zedd | One More Time — Daft Punk; Around the World — Daft Punk; Levels — Avicii; Wake Me Up — Avicii; Feel So Close — Calvin Harris; Finally — CeCe Peniston; Gypsy Woman (She's Homeless) — Crystal Waters; Titanium — David Guetta featuring Sia; Midnight City — M83; Show Me Love — Robin S.; Don't You Worry Child — Swedish House Mafia; Clarity — Zedd featuring Foxes | Praise You — Fatboy Slim; Ride on Time — Black Box; Sandstorm — Darude; Animals — Martin Garrix; Nightcall — Kavinsky; The Model — Kraftwerk; Oblivion — Grimes; Big Fun — Inner City; Heartbeats — The Knife; Oxygene, Pt. 4 — Jean-Michel Jarre; Push the Feeling On — Nightcrawlers; BIPP — SOPHIE; Firestarter — The Prodigy; Marea (We've Lost Dancing) — Fred again.. and The Blessed Madonna; Shelter — Porter Robinson and Madeon; 6 Underground — Sneaker Pimps | Discovery — Daft Punk; Homework — Daft Punk; True — Avicii; 18 Months — Calvin Harris; Settle — Disclosure; Actual Life 3 — Fred again..; Selected Ambient Works 85-92 — Aphex Twin; Trans-Europe Express — Kraftwerk; Sound of Silver — LCD Soundsystem; Blue Lines — Massive Attack; Mezzanine — Massive Attack; Dummy — Portishead |
| 12 | Pop Monoculture and Persona Pop | Michael Jackson; Taylor Swift; Madonna; Adele; Beyonce; Britney Spears; Rihanna; Whitney Houston; Lady Gaga; Mariah Carey; Prince; Backstreet Boys | Black Eyed Peas; Justin Bieber; Sabrina Carpenter; The Weeknd; Harry Styles; Cyndi Lauper; Doja Cat; Miley Cyrus; Sam Smith; Sia; Charli XCX; One Direction | Billie Jean — Michael Jackson; ...Baby One More Time — Britney Spears; Thriller — Michael Jackson; I Want It That Way — Backstreet Boys; Bad Romance — Lady Gaga; Like a Prayer — Madonna; Umbrella — Rihanna; Wannabe — Spice Girls; I Wanna Dance with Somebody — Whitney Houston; Rolling in the Deep — Adele; Crazy in Love — Beyonce; When Doves Cry — Prince | I Gotta Feeling — Black Eyed Peas; Espresso — Sabrina Carpenter; Stay with Me — Sam Smith; Good Luck, Babe! — Chappell Roan; Say So — Doja Cat; Someone You Loved — Lewis Capaldi; Wrecking Ball — Miley Cyrus; Fight Song — Rachel Platten; Boy's a Liar Pt. 2 — PinkPantheress; Greedy — Tate McRae; Princess Diana — Ice Spice; 360 — Charli XCX | Thriller — Michael Jackson; 1989 — Taylor Swift; 21 — Adele; ...Baby One More Time — Britney Spears; The Fame — Lady Gaga; Like a Virgin — Madonna; Purple Rain — Prince; Millennium — Backstreet Boys; Lemonade — Beyonce; Teenage Dream — Katy Perry; Sour — Olivia Rodrigo; 25 — Adele |
| 13 | Latin, Caribbean, Global Pop | BTS; Bad Bunny; Daddy Yankee; BLACKPINK; Burna Boy; Wizkid; Bob Marley & The Wailers; J Balvin; Juan Gabriel; Karol G; Marc Anthony; Selena | CKay; Luis Fonsi; Don Omar; Rosalia; Elvis Crespo; Eslabon Armado; YOASOBI; Anitta; Libianca; FIFTY FIFTY; Willie Colon; Chalino Sanchez | Livin' la Vida Loca — Ricky Martin; Como La Flor — Selena; Water — Tyla; Obsesion — Aventura; DDU-DU DDU-DU — BLACKPINK; Dynamite — BTS; Butter — BTS; Titi Me Pregunto — Bad Bunny; One Love / People Get Ready — Bob Marley & The Wailers; Last Last — Burna Boy; Love Nwantiti — CKay; Gasolina — Daddy Yankee | The Feels — TWICE; Gimme Chocolate!! — BABYMETAL; Pepas — Farruko; Oye Como Va — Tito Puente; 7 Seconds — Youssou N'Dour and Neneh Cherry; El Rey — Vicente Fernandez; Peru — Fireboy DML; Pata Pata — Miriam Makeba; Con Altura — Rosalia and J Balvin; Envolver — Anitta; Amapiano — Asake and Olamide; People — Libianca; Ku Lo Sa — Oxlade; Idol — YOASOBI; Sweet Lullaby — Deep Forest; Adios Amor — Christian Nodal | Amor Prohibido — Selena; The Album — BLACKPINK; Map of the Soul: 7 — BTS; Un Verano Sin Ti — Bad Bunny; Legend — Bob Marley & The Wailers; Barrio Fino — Daddy Yankee; Manana Sera Bonito — Karol G; Made in Lagos — Wizkid; We Broke the Rules — Aventura; Love, Damini — Burna Boy; Gipsy Kings — Gipsy Kings; Vuelve — Ricky Martin |
| 14 | Jazz, Standards, Vocal, Classical-Adjacent | Frank Sinatra; Andrea Bocelli; Nat King Cole; Kenny G; Louis Armstrong; Norah Jones; Sade; Enya; Miles Davis; John Coltrane; Billie Holiday; Ella Fitzgerald | Bing Crosby; Dean Martin; Michael Buble; Herbie Hancock; Yo-Yo Ma; Chet Baker; Nina Simone; Stan Getz; Chuck Mangione; Lang Lang; Herb Alpert; Yiruma | Con te partiro — Andrea Bocelli; Time to Say Goodbye — Andrea Bocelli and Sarah Brightman; Take Five — Dave Brubeck Quartet; Orinoco Flow — Enya; Fly Me to the Moon — Frank Sinatra; My Way — Frank Sinatra; Just the Two of Us — Grover Washington Jr. featuring Bill Withers; Songbird — Kenny G; Unforgettable — Nat King Cole; Don't Know Why — Norah Jones; Smooth Operator — Sade; Feels So Good — Chuck Mangione | White Christmas — Bing Crosby; That's Amore — Dean Martin; Sway — Dean Martin; Feeling Good — Nina Simone; My Funny Valentine — Chet Baker; Rise — Herb Alpert; On the Nature of Daylight — Max Richter; Lily Was Here — David A. Stewart featuring Candy Dulfer; Cantaloupe Island — Herbie Hancock; Cello Suite No. 1: Prelude — Yo-Yo Ma; La Campanella — Lang Lang; Blue in Green — Miles Davis; Soulful Strut — Young-Holt Unlimited; Round Midnight — Thelonious Monk; Goodbye Pork Pie Hat — Charles Mingus; Adagio for Strings — London Philharmonic Orchestra | Romanza — Andrea Bocelli; Breathless — Kenny G; Come Away with Me — Norah Jones; Time Out — Dave Brubeck Quartet; In the Wee Small Hours — Frank Sinatra; Breezin' — George Benson; A Love Supreme — John Coltrane; Kind of Blue — Miles Davis; Dino: The Essential Dean Martin — Dean Martin; Call Me Irresponsible — Michael Buble; Winelight — Grover Washington Jr.; Head Hunters — Herbie Hancock |
| 15 | Soundtrack, Theater, Musicals, Family Context | John Williams; Alan Menken; Hans Zimmer; Lin-Manuel Miranda; Andrew Lloyd Webber; Prince; Whitney Houston; Bee Gees; Rodgers and Hammerstein; Celine Dion; Elton John; Kristen Anderson-Lopez and Robert Lopez | Kenny Loggins; Kristen Anderson-Lopez; Robert Lopez; Simon and Garfunkel; Adele; Eminem; Howard Ashman; Leonard Bernstein; Trent Reznor and Atticus Ross; Benj Pasek and Justin Paul; Phil Collins; Randy Newman | Stayin' Alive — Bee Gees; Circle of Life — Carmen Twillie and Lebo M.; My Heart Will Go On — Celine Dion; Can You Feel the Love Tonight — Elton John; Let It Go — Idina Menzel; Defying Gravity — Idina Menzel and Kristin Chenoweth; Main Title — John Williams; The Imperial March — John Williams; Footloose — Kenny Loggins; My Shot — Original Broadway Cast of Hamilton; Seasons of Love — Original Broadway Cast of Rent; A Whole New World — Peabo Bryson and Regina Belle | Skyfall — Adele; Hooked on a Feeling — Blue Swede; James Bond Theme — John Barry Orchestra; Theme from Jurassic Park — John Williams; Colors of the Wind — Judy Kuhn; The Room Where It Happens — Leslie Odom Jr.; America — Original Broadway Cast of West Side Story; One Day More — Original London Cast of Les Miserables; Back to the Future — Alan Silvestri; Remember Me — Benjamin Bratt; Batman Theme — Danny Elfman; Wakanda — Ludwig Goransson; You Will Be Found — Original Broadway Cast of Dear Evan Hansen; Man of Constant Sorrow — The Soggy Bottom Boys; Hand Covers Bruise — Trent Reznor and Atticus Ross; Being Alive — Dean Jones | Star Wars — John Williams; Hamilton — Original Broadway Cast of Hamilton; Wicked — Original Broadway Cast of Wicked; The Phantom of the Opera — Original London Cast of The Phantom of the Opera; Purple Rain — Prince and The Revolution; The Lion King — Various Artists; Frozen — Various Artists; Beauty and the Beast — Various Artists; Saturday Night Fever — Various Artists; The Bodyguard — Various Artists; The Sound of Music — Original Broadway Cast of The Sound of Music; West Side Story — Original Broadway Cast of West Side Story |
| 16 | Christian, Worship, Gospel | Amy Grant; Chris Tomlin; Hillsong Worship; Aretha Franklin; Lauren Daigle; MercyMe; Mahalia Jackson; Kirk Franklin; Sister Rosetta Tharpe | Sam Cooke and The Soul Stirrers; The Staple Singers; Newsboys; Cory Asbury; Fred Hammond; Sinach; Switchfoot; The Clark Sisters; Skillet | Baby Baby — Amy Grant; How Great Is Our God — Chris Tomlin; What a Beautiful Name — Hillsong Worship; You Say — Lauren Daigle; 10,000 Reasons (Bless the Lord) — Matt Redman; I Can Only Imagine — MercyMe; Way Maker — Sinach; I'll Take You There — The Staple Singers; Goodness of God — Bethel Music and Jenn Johnson; Reckless Love — Cory Asbury; Shout to the Lord — Darlene Zschech; Oceans (Where Feet May Fail) — Hillsong United | Great Are You Lord — All Sons & Daughters; Soon and Very Soon — Andrae Crouch; Who Am I — Casting Crowns; Jireh — Elevation Worship and Maverick City Music featuring Chandler Moore and Naomi Raine; The Blessing — Kari Jobe, Cody Carnes and Elevation Worship; Shackles (Praise You) — Mary Mary; God's Not Dead (Like a Lion) — Newsboys; Build My Life — Pat Barrett; Up Above My Head — Sister Rosetta Tharpe; Break Every Chain — Tasha Cobbs Leonard; No Weapon — Fred Hammond; Dare You to Move — Switchfoot; Jesus Gave Me Water — Sam Cooke and The Soul Stirrers; You Brought the Sunshine — The Clark Sisters; Monster — Skillet | Heart in Motion — Amy Grant; Almost There — MercyMe; Amazing Grace — Aretha Franklin; Arriving — Chris Tomlin; Look Up Child — Lauren Daigle; The World's Greatest Gospel Singer — Mahalia Jackson; Jesus Freak — DC Talk; Old Church Basement — Elevation Worship and Maverick City Music; Shout to the Lord — Hillsong Worship; God's Property — Kirk Franklin; Blessed Be Your Name — Matt Redman; Casting Crowns — Casting Crowns |
| 17 | Nostalgia, Novelty, Context, Shared Listening |  | Mariah Carey; Bing Crosby; ABBA; Brenda Lee; Nat King Cole; Neil Diamond; Wham!; Bon Jovi; Journey; The Killers; Garth Brooks; Village People |  | All I Want for Christmas Is You — Mariah Carey; White Christmas — Bing Crosby; Rockin' Around the Christmas Tree — Brenda Lee; Don't Stop Believin' — Journey; Sweet Caroline — Neil Diamond; Livin' on a Prayer — Bon Jovi; The Christmas Song — Nat King Cole; Mr. Brightside — The Killers; Y.M.C.A. — Village People; Jingle Bell Rock — Bobby Helms; Friends in Low Places — Garth Brooks; Feliz Navidad — Jose Feliciano; Last Christmas — Wham!; Dancing Queen — ABBA; Monster Mash — Bobby Boris Pickett; Have Yourself a Merry Little Christmas — Judy Garland | Merry Christmas — Mariah Carey; A Charlie Brown Christmas — Vince Guaraldi Trio; Merry Christmas — Bing Crosby; The Christmas Song — Nat King Cole; A Christmas Gift for You from Phil Spector — Various Artists; Gold: Greatest Hits — ABBA; Journey Greatest Hits — Journey; Slippery When Wet — Bon Jovi; Come On Over — Shania Twain; Christmas — Michael Buble; Singable Songs for the Very Young — Raffi; Christmas Eve and Other Stories — Trans-Siberian Orchestra |
| 18 | Modern Rock, Current Discovery, Internet-Native Scenes | Tame Impala; Arctic Monkeys; Charli XCX; Glass Animals; Phoebe Bridgers; SOPHIE; boygenius; 100 gecs; Bring Me the Horizon; Fontaines D.C.; MGMT; Mitski | PinkPantheress; Foster the People; Maneskin; Lo-fi Girl; Big Thief; Clairo; Khruangbin; Rina Sawayama; Grimes; Porter Robinson; alt-J; Highly Suspect | Do I Wanna Know? — Arctic Monkeys; Heat Waves — Glass Animals; The Less I Know the Better — Tame Impala; money machine — 100 gecs; Can You Feel My Heart — Bring Me the Horizon; Starburster — Fontaines D.C.; Electric Feel — MGMT; Nobody — Mitski; Kyoto — Phoebe Bridgers; Immaterial — SOPHIE; The Summoning — Sleep Token; Not Strong Enough — boygenius | Beggin' — Maneskin; Pumped Up Kicks — Foster the People; lofi hip hop radio — Lo-fi Girl; Pain — PinkPantheress; Chaise Longue — Wet Leg; Bags — Clairo; Oblivion — Grimes; My Name Is Human — Highly Suspect; Night Shift — Lucy Dacus; Look at the Sky — Porter Robinson; XS — Rina Sawayama; Out of the Black — Royal Blood; Breezeblocks — alt-J; Guided by Angels — Amyl and the Sniffers; She's Leaving You — MJ Lenderman; Multi-Love — Unknown Mortal Orchestra | Currents — Tame Impala; 1000 gecs — 100 gecs; Sempiternal — Bring Me the Horizon; Oracular Spectacular — MGMT; Be the Cowboy — Mitski; Modal Soul — Nujabes; Punisher — Phoebe Bridgers; Oil of Every Pearl's Un-Insides — SOPHIE; Take Me Back to Eden — Sleep Token; the record — boygenius; Desire, I Want to Turn Into You — Caroline Polachek; Glow On — Turnstile |

## Recording Specificity Review

### All Composition Groups With Multiple Recordings

| composition_key | song_title | artist_names | canonical_song_recording_ids | review reason |
| --- | --- | --- | --- | --- |
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

### Covers / Remakes / Live Versions That Must Remain Distinct

| family | source | line | warning note |
| --- | --- | --- | --- |
| 1 | data/canonical_graph/family_1/import_warnings.md | 18 | High-risk duplicate/version cases: |
| 1 | data/canonical_graph/family_1/import_warnings.md | 27 | \| `barbara-ann` \| Keep Regents original distinct from later Beach Boys cover if/when imported. \| |
| 1 | data/canonical_graph/family_1/import_warnings.md | 28 | \| `sh-boom` \| Define split rules for The Chords and The Crew-Cuts/pop-cover versions before title-based merging. \| |
| 1 | data/canonical_graph/family_1/import_warnings.md | 29 | \| `love-potion-no-9` \| Preserve The Clovers source version separately from later Searchers/British Invasion cover behavior. \| |
| 1 | data/canonical_graph/family_1/import_warnings.md | 30 | \| `louie-louie` \| Keep Kingsmen garage/frat-rock recording distinct from Richard Berry/source and other covers. \| |
| 1 | data/canonical_graph/family_1/import_warnings.md | 33 | \| `gene-vincent` / Blue Caps \| Decide whether to canonicalize early band recordings under `gene-vincent-and-his-blue-caps` or keep Gene Vincent with alias credits. \| |
| 1 | data/canonical_graph/family_1/import_warnings.md | 35 | \| The Crickets / Buddy Holly and the Crickets \| Keep Buddy Holly solo, Crickets, and Buddy Holly and the Crickets alias rules explicit. \| |
| 1 | data/canonical_graph/family_1/import_warnings.md | 36 | \| Jackie Brenston / Ike Turner \| Store `Rocket 88` with Jackie Brenston and His Delta Cats while preserving Ike Turner/Kings of Rhythm credit aliases. \| |
| 10 | data/canonical_graph/family_10/import_warnings.md | 28 | \| `green-day-good-riddance-time-of-your-life` \| Acoustic/context use should not split away from Green Day recording without version evidence. \| |
| 11 | data/canonical_graph/family_11/import_warnings.md | 7 | ## Merge / Alias / Version Risks |
| 11 | data/canonical_graph/family_11/import_warnings.md | 10 | - Producer aliases and project names require explicit alias tables: Larry Heard/Mr. Fingers/Fingers Inc., Juan Atkins/Model 500/Cybotron, Kevin Saunderson/Inner City. |
| 11 | data/canonical_graph/family_11/import_warnings.md | 11 | - Club rows often need mix/edit specificity; single titles can refer to radio edits, original mixes, remixes, live/DJ-set versions, or viral clips. |
| 11 | data/canonical_graph/family_11/import_warnings.md | 31 | - Lock still requires source-aligned row review, Page 1/Page 2 ordering, and merge-table confirmation for aliases, covers, remixes, collaborations, live recordings, and language/version variants. |
| 12 | data/canonical_graph/family_12/import_warnings.md | 22 | \| `beyonce` solo vs group-era credits \| Do not merge Destiny-era recordings into solo Beyonce without explicit alias/member handling. \| |
| 13 | data/canonical_graph/family_13/import_warnings.md | 7 | ## Merge / Alias / Version Risks |
| 13 | data/canonical_graph/family_13/import_warnings.md | 10 | - Language versions, remixes, and collaboration credits are high-risk in Family 13: `Despacito`, `Bailando`, `Danza Kuduro`, `Love Nwantiti`, `AMG`, `Bebe Dame`, and `7 Seconds` need recording-level care. |
| 13 | data/canonical_graph/family_13/import_warnings.md | 14 | - World-fusion rows such as Deep Forest require sampling/ethics/version review before import lock. |
| 13 | data/canonical_graph/family_13/import_warnings.md | 31 | - Lock still requires source-aligned row review, Page 1/Page 2 ordering, and merge-table confirmation for aliases, covers, remixes, collaborations, live recordings, and language/version variants. |
| 14 | data/canonical_graph/family_14/import_warnings.md | 12 | ## Merge / Alias / Version Risks |
| 14 | data/canonical_graph/family_14/import_warnings.md | 35 | - My Favorite Things - John Coltrane: Preserve Coltrane recording distinct from musical-theater composition. |
| 14 | data/canonical_graph/family_14/import_warnings.md | 37 | - Nessun dorma - Luciano Pavarotti: Opera aria/composition must remain distinct from Pavarotti recording. |
| 14 | data/canonical_graph/family_14/import_warnings.md | 38 | - Cello Suite No. 1: Prelude - Yo-Yo Ma: Composition vs recording distinction required. |
| 14 | data/canonical_graph/family_14/import_warnings.md | 54 | - Largest remaining gap: The largest remaining gap is recording-level standard attribution: many songs need composition, definitive recording, and holiday/context split rules before hard lock. |
| 14 | data/canonical_graph/family_14/import_warnings.md | 55 | - Duplicate object IDs across families should be interpreted as multi-membership unless a warning says the display names or source versions conflict. |
| 15 | data/canonical_graph/family_15/import_warnings.md | 12 | ## Merge / Alias / Version Risks |
| 15 | data/canonical_graph/family_15/import_warnings.md | 14 | - Claude-Michel Schonberg: Composer/show-first object; do not merge with cast recordings. |
| 15 | data/canonical_graph/family_15/import_warnings.md | 27 | - Ludwig Goransson: Score and hip-hop/R&B soundtrack album rows should remain distinct. |
| 15 | data/canonical_graph/family_15/import_warnings.md | 33 | - Guardians of the Galaxy: Awesome Mix Vol. 1 - Various Artists: Compilation soundtrack made of older songs; do not merge with original release albums. |
| 15 | data/canonical_graph/family_15/import_warnings.md | 36 | - Black Panther - Ludwig Goransson: Score album distinct from Kendrick Lamar-curated soundtrack album. |
| 15 | data/canonical_graph/family_15/import_warnings.md | 38 | - I Will Always Love You - Whitney Houston: Preserve Whitney Houston recording distinct from Dolly Parton original. |
| 15 | data/canonical_graph/family_15/import_warnings.md | 43 | - We Don't Talk About Bruno - Carolina Gaitan, Mauro Castillo, Adassa, Rhenzy Feliz, Diane Guerrero, Stephanie Beatriz and Encanto Cast: Ensemble cast credit is version-specific and should not merge to one artist. |
| 15 | data/canonical_graph/family_15/import_warnings.md | 44 | - Remember Me - Benjamin Bratt: Coco has multiple in-film versions; preserve recording context. |
| 15 | data/canonical_graph/family_15/import_warnings.md | 48 | - Man of Constant Sorrow - The Soggy Bottom Boys: Film-fictional group and traditional/roots song attribution need review. |
| 15 | data/canonical_graph/family_15/import_warnings.md | 55 | - Duplicate object IDs across families should be interpreted as multi-membership unless a warning says the display names or source versions conflict. |
| 16 | data/canonical_graph/family_16/import_warnings.md | 12 | ## Merge / Alias / Version Risks |
| 16 | data/canonical_graph/family_16/import_warnings.md | 19 | - Passion: Conference/live worship brand needs distinct entity handling. |
| 16 | data/canonical_graph/family_16/import_warnings.md | 22 | - In Christ Alone - Keith and Kristyn Getty: Modern hymn/songbook row; many church versions exist. |
| 16 | data/canonical_graph/family_16/import_warnings.md | 24 | - People - Hillsong United: Hillsong Worship, Hillsong United, and church-brand rows should remain distinct. |
| 16 | data/canonical_graph/family_16/import_warnings.md | 25 | - Amazing Grace - Aretha Franklin: Composition vs Aretha live recording must remain distinct. |
| 16 | data/canonical_graph/family_16/import_warnings.md | 26 | - Soon and Very Soon - Andrae Crouch: Gospel standard has many church and choir versions. |
| 16 | data/canonical_graph/family_16/import_warnings.md | 28 | - Break Every Chain - Tasha Cobbs Leonard: Worship standard and live gospel recording should remain distinct. |
| 16 | data/canonical_graph/family_16/import_warnings.md | 29 | - God's Not Dead (Like a Lion) - Newsboys: Newsboys cover/version should not merge with original Daniel Bashta worship song. |
| 16 | data/canonical_graph/family_16/import_warnings.md | 31 | - Shout to the Lord - Darlene Zschech: Church-songbook standard with many Hillsong and congregation versions. |
| 16 | data/canonical_graph/family_16/import_warnings.md | 33 | - In Christ Alone - Keith and Kristyn Getty: Modern hymn should be standard-first and version-aware. |
| 16 | data/canonical_graph/family_16/import_warnings.md | 35 | - Jireh - Elevation Worship and Maverick City Music featuring Chandler Moore and Naomi Raine: Collaboration and featured-vocal credits need manual handling. |
| 16 | data/canonical_graph/family_16/import_warnings.md | 37 | - Build My Life - Pat Barrett: Modern worship standard with many artist and church versions. |
| 16 | data/canonical_graph/family_16/import_warnings.md | 42 | - Largest remaining gap: The largest remaining gap is worship standard/version policy: live, church-brand, songwriter, and congregational versions need explicit import split rules. |
| 16 | data/canonical_graph/family_16/import_warnings.md | 43 | - Duplicate object IDs across families should be interpreted as multi-membership unless a warning says the display names or source versions conflict. |
| 17 | data/canonical_graph/family_17/import_warnings.md | 26 | \| Traditional/kids repertoire \| Composition-level objects need non-artist canonical handling where performer is not meaningful. \| |
| 18 | data/canonical_graph/family_18/import_warnings.md | 12 | ## Merge / Alias / Version Risks |
| 18 | data/canonical_graph/family_18/import_warnings.md | 28 | - Beggin' - Maneskin: Preserve Maneskin recording distinct from Four Seasons original. |
| 18 | data/canonical_graph/family_18/import_warnings.md | 38 | - Duplicate object IDs across families should be interpreted as multi-membership unless a warning says the display names or source versions conflict. |
| 2 | data/canonical_graph/family_2/import_warnings.md | 21 | \| `the-shadows-of-knight-gloria` \| Cover/version-specific row; do not merge with Them's `Gloria`. \| |
| 2 | data/canonical_graph/family_2/import_warnings.md | 23 | \| `the-animals-house-of-the-rising-sun` \| Arrangement/recording-specific row; do not merge with traditional-song records. \| |
| 3 | data/canonical_graph/family_3/import_warnings.md | 26 | \| ambiguous_versions \| Live vs studio versions and cover-adjacent later memories are not merged. \| Requires downstream version-aware matching. \| |
| 4 | data/canonical_graph/family_4/import_warnings.md | 9 | \| date_normalization \| 1940/1944, 20th c., traditional, 1998/2000 US breakthrough \| release_year uses an integer where defensible and null where attribution/date is traditional or unstable; row warnings preserve ambiguity. \| |
| 4 | data/canonical_graph/family_4/import_warnings.md | 10 | \| collaboration_and_version_risk \| Wilco with Billy Bragg, Pete Seeger et al. / traditional, Pete Seeger and Lee Hays; Peter Paul and Mary popularized, Jason Isbell and the 400 Unit \| Artist name retained as supplied when needed; import should not collapse collaborations into solo artist rows without manual confirmation. \| |
| 5 | data/canonical_graph/family_5/import_warnings.md | 7 | ## Merge / Alias / Version Risks |
| 5 | data/canonical_graph/family_5/import_warnings.md | 11 | - `Wagon Wheel`, `Tennessee Whiskey`, `Act Naturally`, `Me and Bobby McGee`, and `How Do I Live` require composition/recording/version handling. |
| 5 | data/canonical_graph/family_5/import_warnings.md | 31 | - Lock still requires source-aligned row review, Page 1/Page 2 ordering, and merge-table confirmation for aliases, covers, remixes, collaborations, live recordings, and language/version variants. |
| 6 | data/canonical_graph/family_6/import_warnings.md | 12 | \| version_specific_recordings \| Respect; Ain't No Mountain High Enough; I Heard It Through the Grapevine; Don't Leave Me This Way; Tyrone live \| Preserve recording/version identity rather than merging by composition title. \| |
| 7 | data/canonical_graph/family_7/import_warnings.md | 20 | \| Alias rows \| `2Pac`, `The Notorious B.I.G.`, `Mos Def / Yasiin Bey`, `Jeezy`, and `Afrika Bambaataa & Soulsonic Force` require alias-aware matching. \| |
| 7 | data/canonical_graph/family_7/import_warnings.md | 23 | ## Explicit, Clean, And Version Warnings |
| 7 | data/canonical_graph/family_7/import_warnings.md | 30 | \| cardi-b-feat-megan-thee-stallion-wap \| Explicit and clean versions are materially different survey objects. \| |
| 7 | data/canonical_graph/family_7/import_warnings.md | 32 | \| run-dmc-walk-this-way \| Run-DMC/Aerosmith version must not merge with Aerosmith original recording. \| |
| 7 | data/canonical_graph/family_7/import_warnings.md | 33 | \| fugees-killing-me-softly \| Fugees version must not merge with Roberta Flack or earlier recordings. \| |
| 7 | data/canonical_graph/family_7/import_warnings.md | 36 | \| chief-keef-feat-lil-reese-i-dont-like \| Original and Kanye remix should remain distinct if both are imported. \| |
| 8 | data/canonical_graph/family_8/import_warnings.md | 7 | ## Merge / Alias / Version Risks |
| 8 | data/canonical_graph/family_8/import_warnings.md | 10 | - Soft Cell: Preserve Soft Cell recording distinct from Gloria Jones original. |
| 8 | data/canonical_graph/family_8/import_warnings.md | 11 | - Patti Smith: Preserve Patti Smith recording distinct from Them/Van Morrison original. |
| 8 | data/canonical_graph/family_8/import_warnings.md | 19 | - Yazoo/Yaz alias handling is required. |
| 9 | data/canonical_graph/family_9/import_warnings.md | 23 | \| `hurt` \| Nine Inch Nails song row must remain distinct from Johnny Cash cover/version rows in other families. \| |
| 9 | data/canonical_graph/family_9/import_warnings.md | 24 | \| `cum-on-feel-the-noize` \| Quiet Riot row is a cover/version-specific glam-metal gateway; do not merge with Slade original if imported elsewhere. \| |

### Likely Accidental Duplicate Titles

| composition_key | song_title | artists | recording_ids | why suspicious |
| --- | --- | --- | --- | --- |
| i-ll-take-you-there | I'll Take You There | Staple Singers; The Staple Singers | staple-singers-ill-take-you-there; the-staple-singers-i-ll-take-you-there | artist display variants or overlapping credits; review alias before treating as separate compositions |
| turn-turn-turn | Turn! Turn! Turn! | The Byrds; The Byrds / Pete Seeger | f4-026-song-turn-turn-turn-the-byrds-pete-seeger; the-byrds-turn-turn-turn | artist display variants or overlapping credits; review alias before treating as separate compositions |
| we-don-t-talk-about-bruno | We Don't Talk About Bruno | Carolina Gaitan, Mauro Castillo, Adassa, Rhenzy Feliz, Diane Guerrero, Stephanie Beatriz and Encanto Cast; Encanto Cast | carolina-gaitan-mauro-castillo-adassa-rhenzy-feliz-diane-guerrero-stephanie-beatriz-and-encanto-cast-we-don-t-talk-about-bruno; encanto-cast-we-dont-talk-about-bruno | artist display variants or overlapping credits; review alias before treating as separate compositions |

### Suspicious Collapses

| warning |
| --- |
| family 4 song f4-026-song-we-shall-overcome-pete-seeger-et-al-traditional: release_year is `None` |
| family 4 song f4-026-song-house-of-the-rising-sun-traditional-revival-circuit-object: release_year is `None` |
| artist `kool-and-the-gang` has multiple display/source names: Kool & The Gang; Kool & the Gang |
| artist `martha-and-the-vandellas` has multiple display/source names: Martha & the Vandellas; Martha and the Vandellas |
| artist `simon-and-garfunkel` has multiple display/source names: Simon & Garfunkel; Simon and Garfunkel |
| artist `smokey-robinson-and-the-miracles` has multiple display/source names: Smokey Robinson & The Miracles; Smokey Robinson and the Miracles |
| album `the-sonics-here-are-the-sonics` has multiple display/source names: Here Are The Sonics; Here Are the Sonics |
| song_recording `martha-and-the-vandellas-dancing-in-the-street` has conflicting `artist_names` values: Martha & the Vandellas; Martha and the Vandellas |
| song_recording `shania-twain-man-i-feel-like-a-woman` has conflicting `release_years` values: 1997; 1999 |

## Alias / Merge Risk Ledger

### Safe Display Name Normalization

| issue_id | priority | examples | recommended_action |
| --- | --- | --- | --- |
| display-ampersand-martha-vandellas | high | Martha & the Vandellas; Martha and the Vandellas | Normalize display aliases after confirming same entity. |
| display-ampersand-simon-garfunkel | medium | Simon & Garfunkel; Simon and Garfunkel | Normalize display aliases after confirming same entity. |
| display-case-kool-gang | medium | Kool & The Gang; Kool & the Gang | Normalize case; preserve source display names. |
| display-punctuation-b52s | medium | The B-52's; The B-52s; Love Shack | Confirm same artist and recording, then normalize display alias. |
| display-article-staple-singers | medium | Staple Singers; The Staple Singers; I'll Take You There | Confirm same artist identity and recording, then normalize. |

### Likely Same Artist Entity

| issue_id | priority | examples | recommended_action |
| --- | --- | --- | --- |
| smokey-miracles-display | medium | Smokey Robinson & The Miracles; Smokey Robinson and the Miracles | Create alias row; do not duplicate artist. |
| rap-aliases | high | 2Pac / Tupac; Mos Def / Yasiin Bey; Jeezy / Young Jeezy | Create explicit alias table entries before hard lock. |
| electronic-project-aliases | high | Larry Heard / Mr. Fingers / Fingers Inc.; Juan Atkins / Model 500 / Cybotron; Kevin Saunderson / Inner City | Human review; project aliases may be linked but not collapsed by default. |

### Must Remain Separate

| issue_id | priority | examples | recommended_action |
| --- | --- | --- | --- |
| group-vs-solo | high | Diana Ross vs The Supremes; Michael Jackson vs Jackson 5; Beyonce vs Destiny's Child; Darius Rucker vs Hootie & the Blowfish | Keep separate canonical artists; link through relationship metadata later. |
| different-artists-similar-name | high | Sleep vs Sleep Token; U.S. Wailers vs Bob Marley & The Wailers; Jimmie Rodgers pop vs country Jimmie Rodgers | Keep separate canonical IDs. |
| different-compositions-same-title | high | Fela Kuti - Zombie; The Cranberries - Zombie; Korn - Blind; Hercules & Love Affair - Blind; Mastodon - Oblivion; Grimes - Oblivion | Keep separate composition IDs and recording IDs. |

### Needs Human Review

| issue_id | priority | examples | recommended_action |
| --- | --- | --- | --- |
| buddy-holly-crickets | medium | The Crickets; Buddy Holly and the Crickets; Buddy Holly solo | Decide canonical entity and credit alias model. |
| gene-vincent-blue-caps | medium | Gene Vincent; Gene Vincent and His Blue Caps | Decide canonical entity and recording-credit model. |
| release-year-shania | medium | Shania Twain - Man! I Feel Like a Woman!; 1997; 1999 | Decide album-release vs single-release policy. |

### Composition Vs Recording Review

| issue_id | priority | examples | recommended_action |
| --- | --- | --- | --- |
| hound-dog | high | Big Mama Thornton - Hound Dog; Elvis Presley - Hound Dog | Keep recordings separate; link composition only after source review. |
| the-twist | high | Hank Ballard & The Midnighters - The Twist; Chubby Checker - The Twist | Keep recordings separate. |
| shake-rattle-and-roll | high | Big Joe Turner - Shake, Rattle and Roll; Bill Haley & His Comets - Shake, Rattle and Roll | Keep recordings separate. |
| thats-all-right | high | Arthur Big Boy Crudup - That's All Right; Elvis Presley - That's All Right | Keep recordings separate. |
| walk-this-way | high | Aerosmith - Walk This Way; Run-DMC - Walk This Way | Keep original and remake separate. |
| gloria | high | Patti Smith - Gloria; The Shadows of Knight - Gloria; Them - Gloria; The Cadillacs - Gloria | Manual composition review; do not merge by title. |
| house-of-the-rising-sun | high | The Animals - House of the Rising Sun; Traditional / revival circuit object | Composition-first traditional-song model needed. |
| god-only-knows | medium | The Beach Boys - God Only Knows; for KING & COUNTRY - God Only Knows | Review likely separate compositions; do not merge by title. |
| zombie | high | Fela Kuti - Zombie; The Cranberries - Zombie | Separate compositions and recordings. |

### Cast Show Soundtrack Review

| issue_id | priority | examples | recommended_action |
| --- | --- | --- | --- |
| we-dont-talk-about-bruno | high | Encanto Cast; Carolina Gaitan, Mauro Castillo, Adassa, Rhenzy Feliz, Diane Guerrero, Stephanie Beatriz and Encanto Cast | Model film/show, cast recording, performers, and recording separately. |
| score-vs-curated-soundtrack | high | Black Panther score; Black Panther curated soundtrack; Guardians of the Galaxy: Awesome Mix Vol. 1 | Separate score album, curated soundtrack album, and source song recordings. |
| fictional-performer | medium | The Soggy Bottom Boys - Man of Constant Sorrow | Preserve fictional performer credit; link traditional composition separately. |

### Worship Traditional Review

| issue_id | priority | examples | recommended_action |
| --- | --- | --- | --- |
| we-shall-overcome | high | We Shall Overcome; Pete Seeger et al. / traditional | Composition-first movement-standard model needed. |
| amazing-grace | high | Amazing Grace; Aretha Franklin; traditional hymn | Composition-first hymn model; preserve definitive recordings. |
| modern-worship-standards | high | Shout to the Lord; In Christ Alone; Build My Life; Way Maker | Songbook composition plus recording variants. |
| church-brand-splits | high | Hillsong Worship; Hillsong United; Bethel Music; Elevation Worship; Maverick City Music; Passion | Keep brands and individual performers distinct until relationship table exists. |

### Same-Title Album Risks

| normalized_title | albums / artists | risk |
| --- | --- | --- |
| album | The Album — BLACKPINK; The Album — Masters at Work | same album title across artist contexts; review before title-based merge |
| blue | Blue — Joni Mitchell; Blue — LeAnn Rimes | same album title across artist contexts; review before title-based merge |
| escape | Escape — Journey; Escape — Enrique Iglesias | same album title across artist contexts; review before title-based merge |
| first-love | First Love — Hikaru Utada; First Love — Yiruma | same album title across artist contexts; review before title-based merge |
| follow-the-leader | Follow the Leader — Eric B. & Rakim; Follow the Leader — Korn | same album title across artist contexts; review before title-based merge |
| merry-christmas | Merry Christmas — Bing Crosby; Merry Christmas — Mariah Carey | same album title across artist contexts; review before title-based merge |
| purple-rain | Purple Rain — Prince and The Revolution; Purple Rain — Prince | same album title across artist contexts; review before title-based merge |

### Same-Title Song Risks

Same-title song risks are represented by the composition review queue above. They must not be auto-merged by title.

## Membership / Weight Audit

### Objects With Many Archetype Memberships

| membership_count | object_type | canonical_id | display_name | families | archetypes | roles |
| --- | --- | --- | --- | --- | --- | --- |
| 3 | artist | beyonce | Beyonce | 6; 12 | 042; 044; 090 | album_anchor; anchor; artist_anchor; bridge; gateway |
| 3 | artist | marvin-gaye | Marvin Gaye | 1; 6 | 006; 037; 041 | anchor; artist_anchor; bridge; gateway; song_first |
| 3 | artist | prince | Prince | 6; 12; 15 | 039; 088; 106 | anchor; artist_anchor; boundary; bridge; gateway |
| 3 | artist | the-drifters | The Drifters | 1 | 001; 003; 006 | anchor; artist_anchor; bridge; gateway; song_first |
| 3 | artist | the-marvelettes | The Marvelettes | 1; 6 | 005; 006; 037 | bridge; gateway; song_first |
| 3 | artist | whitney-houston | Whitney Houston | 6; 12; 15 | 042; 088; 106 | anchor; artist_anchor; bridge; gateway; song_first |
| 3 | song | the-drifters-there-goes-my-baby | There Goes My Baby | 1 | 001; 003; 006 | boundary; gateway; song_first |
| 2 | album | various-artists-a-christmas-gift-for-you-from-phil-spector | A Christmas Gift for You from Phil Spector | 1; 17 | 005; 112 | album_anchor; compilation_gateway; gateway |
| 2 | album | album-a-night-at-the-opera-1975 | A Night at the Opera | 3 | 016; 020 | album_anchor; gateway |
| 2 | album | bonobo-black-sands | Black Sands | 11; 18 | 084; 120 | gateway |
| 2 | album | bo-diddley-bo-diddley | Bo Diddley | 1 | 001; 002 | album_anchor |
| 2 | album | shania-twain-come-on-over | Come On Over | 5; 17 | 033; 113 | album_anchor; anchor; false_nearby; gateway |
| 2 | album | janet-jackson-control | Control | 6; 12 | 042; 088 | album_anchor; anchor; bridge; gateway |
| 2 | album | carl-perkins-dance-album-of-carl-perkins | Dance Album of Carl Perkins | 1 | 001; 002 | album_anchor |
| 2 | album | sonic-youth-daydream-nation | Daydream Nation | 8; 10 | 059; 069 | album_anchor; anchor; boundary; bridge |
| 2 | album | tycho-dive | Dive | 11; 18 | 086; 120 | bridge |
| 2 | album | pixies-doolittle | Doolittle | 8; 10 | 059; 069 | album_anchor; anchor; bridge |
| 2 | album | various-artists-frozen | Frozen | 15; 17 | 105; 114 | album_anchor; false_nearby; gateway |
| 2 | album | album-goodbye-yellow-brick-road-1973 | Goodbye Yellow Brick Road | 3 | 016; 022 | album_anchor; gateway |
| 2 | album | sister-rosetta-tharpe-gospel-train | Gospel Train | 1; 16 | 001; 108 | album_anchor; bridge |
| 2 | album | the-sonics-here-are-the-sonics | Here Are The Sonics | 1; 2 | 002; 011 | album_anchor; boundary; bridge; deepening |
| 2 | album | lesley-gore-ill-cry-if-i-want-to | I'll Cry If I Want To | 1 | 004; 005 | album_anchor; bridge |
| 2 | album | johnny-cash-with-his-hot-and-blue-guitar | Johnny Cash with His Hot and Blue Guitar! | 1 | 001; 002 | album_anchor; bridge |
| 2 | album | dick-dale-and-his-del-tones-king-of-the-surf-guitar | King of the Surf Guitar | 1 | 002; 007 | album_anchor; bridge |
| 2 | album | the-replacements-let-it-be | Let It Be | 8; 10 | 059; 069 | album_anchor; bridge; deepening |
| 2 | album | james-brown-live-at-the-apollo | Live at the Apollo | 1; 6 | 006; 039 | album_anchor; anchor; gateway; live_gateway |
| 2 | album | boards-of-canada-music-has-the-right-to-children | Music Has the Right to Children | 11; 18 | 087; 120 | album_anchor; bridge; false_nearby |
| 2 | album | sophie-oil-of-every-pearl-s-un-insides | Oil of Every Pearl's Un-Insides | 11; 18 | 087; 119 | album_anchor; bridge |
| 2 | album | doja-cat-planet-her | Planet Her | 7; 12 | 050; 093 | album_anchor; boundary; bridge; gateway |
| 2 | album | the-marvelettes-please-mr-postman | Please Mr. Postman | 1 | 005; 006 | album_anchor; bridge |
| 2 | album | album-rumours-1977 | Rumours | 3 | 016; 022 | album_anchor; gateway |
| 2 | album | various-artists-saturday-night-fever | Saturday Night Fever | 6; 15 | 040; 106 | album_anchor; compilation_gateway; gateway |
| 2 | album | bring-me-the-horizon-sempiternal | Sempiternal | 9; 18 | 067; 118 | album_anchor; anchor; bridge |
| 2 | album | album-silk-degrees-1976 | Silk Degrees | 3 | 022; 023 | bridge; gateway |
| 2 | album | bon-jovi-slippery-when-wet | Slippery When Wet | 9; 17 | 063; 113 | album_anchor; false_nearby; gateway |
| 2 | album | sleep-token-take-me-back-to-eden | Take Me Back to Eden | 9; 18 | 067; 118 | album_anchor; boundary; gateway |
| 2 | album | album-the-dark-side-of-the-moon-1973 | The Dark Side of the Moon | 3 | 016; 018 | album_anchor; gateway |
| 2 | album | bad-omens-the-death-of-peace-of-mind | The Death of Peace of Mind | 9; 18 | 067; 118 | album_anchor; boundary; gateway |
| 2 | album | lauryn-hill-the-miseducation-of-lauryn-hill | The Miseducation of Lauryn Hill | 6; 7 | 043; 050 | album_anchor; anchor; bridge; gateway |
| 2 | album | album-the-stranger-1977 | The Stranger | 3 | 016; 022 | album_anchor; gateway |
| 2 | album | album-their-greatest-hits-1971-1975-1976 | Their Greatest Hits 1971-1975 | 3 | 016; 022 | compilation_gateway; gateway |
| 2 | album | i-prevail-trauma | Trauma | 9; 18 | 067; 118 | album_anchor; boundary; gateway |
| 2 | album | the-supremes-where-did-our-love-go | Where Did Our Love Go | 1; 6 | 006; 037 | album_anchor; bridge; gateway |
| 2 | album | deftones-white-pony | White Pony | 9; 18 | 066; 118 | album_anchor; anchor; bridge; false_nearby |
| 2 | album | whitney-houston-whitney-houston | Whitney Houston | 6; 12 | 042; 088 | album_anchor; gateway |
| 2 | artist | adele | Adele | 12; 15 | 092; 106 | album_anchor; anchor; artist_anchor; bridge; song_first |
| 2 | artist | artist-aerosmith | Aerosmith | 3 | 016; 017 | anchor; bridge; gateway; song_first |
| 2 | artist | artist-alice-cooper | Alice Cooper | 3 | 017; 020 | anchor; boundary; bridge |
| 2 | artist | alice-in-chains | Alice in Chains | 9; 10 | 066; 070 | anchor; artist_anchor; boundary; bridge; false_nearby |
| 2 | artist | annette-funicello | Annette Funicello | 1 | 004; 007 | bridge; gateway |
| 2 | artist | arca | Arca | 11; 18 | 087; 119 | boundary; bridge; deepening |
| 2 | artist | arctic-monkeys | Arctic Monkeys | 10; 18 | 079; 117 | artist_anchor; bridge; gateway |
| 2 | artist | aretha-franklin | Aretha Franklin | 6; 16 | 038; 108 | anchor; artist_anchor; bridge; gateway |
| 2 | artist | bad-omens | Bad Omens | 9; 18 | 067; 118 | boundary; gateway; song_first |
| 2 | artist | bee-gees | Bee Gees | 6; 15 | 040; 106 | artist_anchor; bridge; gateway; song_first |
| 2 | artist | artist-billy-joel | Billy Joel | 3 | 016; 022 | album_anchor; anchor; bridge; gateway; song_first |
| 2 | artist | bing-crosby | Bing Crosby | 14; 17 | 100; 112 | gateway; song_first |
| 2 | artist | black-sabbath | Black Sabbath | 9 | 061; 064 | album_anchor; anchor; artist_anchor; bridge |
| 2 | artist | bo-diddley | Bo Diddley | 1 | 001; 002 | anchor; artist_anchor; bridge; deepening; song_first |
| 2 | artist | boards-of-canada | Boards of Canada | 11; 18 | 087; 120 | anchor; artist_anchor; bridge; false_nearby |

### Objects With Suspiciously High Weights

| object_type | canonical_id | display_name | family | archetype | weight | survey_tier | roles | warning |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| album | taylor-swift-1989 | 1989 | 12 | 091 | 1.0 | core | album_anchor; anchor |  |
| album | f4-024-album-blue-joni-mitchell | Blue | 4 | 024 | 1 | core | anchor; album_anchor | Touches folk and art-pop. |
| album | carl-perkins-dance-album-of-carl-perkins | Dance Album of Carl Perkins | 1 | 002 | 1.0 | core | album_anchor | True album |
| album | elvis-presley-elvis-presley | Elvis Presley | 1 | 001 | 1.0 | core | album_anchor | True album |
| album | f4-027-album-john-prine-john-prine | John Prine | 4 | 027 | 1 | core | anchor; album_anchor | Also 024 bridge. |
| album | album-led-zeppelin-iv-1971 | Led Zeppelin IV | 3 | 016 | 1 | core | album_anchor; gateway | overlaps 017 |
| album | metallica-master-of-puppets | Master of Puppets | 9 | 062 | 1.0 | core | album_anchor; anchor |  |
| album | nirvana-nevermind | Nevermind | 10 | 070 | 1 | core | album_anchor; anchor; gateway |  |
| album | f4-028-album-no-depression-uncle-tupelo | No Depression | 4 | 028 | 1 | core | anchor; album_anchor | Genre-name object; distinguish from song and magazine/culture. |
| album | black-sabbath-paranoid | Paranoid | 9 | 061 | 1.0 | core | album_anchor; anchor; gateway |  |
| album | f4-024-album-tapestry-carole-king | Tapestry | 4 | 024 | 1 | core | anchor; album_anchor | Also archetype 025; duplicate by design. |
| album | f4-025-album-tapestry-carole-king | Tapestry | 4 | 025 | 1 | core | anchor; album_anchor | Also 024. |
| album | album-the-dark-side-of-the-moon-1973 | The Dark Side of the Moon | 3 | 016 | 1 | core | album_anchor; gateway | overlaps 018 |
| album | album-the-dark-side-of-the-moon-1973 | The Dark Side of the Moon | 3 | 018 | 1 | core | album_anchor; gateway | overlaps 016 |
| album | album-ziggy-stardust-1972 | The Rise and Fall of Ziggy Stardust and the Spiders from Mars | 3 | 020 | 1 | core | album_anchor; gateway | overlaps 018 |
| album | michael-jackson-thriller | Thriller | 12 | 088 | 1.0 | core | album_anchor; anchor |  |
| album | f4-029-album-tracy-chapman-tracy-chapman | Tracy Chapman | 4 | 029 | 1 | core | anchor; album_anchor | Also 024 bridge. |
| artist | aretha-franklin | Aretha Franklin | 6 | 038 | 1.0 | core | anchor; artist_anchor; gateway | Columbia jazz-pop and later adult-R&B eras should not be collapsed blindly. |
| artist | black-sabbath | Black Sabbath | 9 | 061 | 1.0 | core | anchor; artist_anchor; album_anchor; bridge | Also anchors 064 doom roots; keep duplicate membership as archetype membership, not duplicate artist entity. |
| artist | carl-perkins | Carl Perkins | 1 | 002 | 1.0 | core | anchor; deepening; song_first; artist_anchor |  |
| artist | f4-024-artist-carole-king | Carole King | 4 | 024 | 1 | core | anchor; artist_anchor; bridge | Also central to archetype 025; do not merge the 024 and 025 placements. |
| artist | f4-025-artist-carole-king | Carole King | 4 | 025 | 1 | core | anchor; artist_anchor | Duplicate with 024 by design. |
| artist | chuck-berry | Chuck Berry | 1 | 001 | 1.0 | core | anchor; bridge; song_first; artist_anchor |  |
| artist | donna-summer | Donna Summer | 6 | 040 | 1.0 | core | anchor; artist_anchor; song_first | Giorgio Moroder production and album/single versions should be preserved. |
| artist | elvis-presley | Elvis Presley | 1 | 001 | 1.0 | core | anchor; gateway; artist_anchor |  |
| artist | frank-ocean | Frank Ocean | 6 | 044 | 1.0 | core | anchor; artist_anchor; album_anchor | F7 salvage supports alt-R&B treatment but Packet 006 is the seed authority. |
| artist | james-brown | James Brown | 6 | 039 | 1.0 | core | anchor; artist_anchor; song_first | Early soul, funk breakbeat, and live-album objects need separate memberships. |
| artist | f4-027-artist-john-prine | John Prine | 4 | 027 | 1 | core | anchor; artist_anchor | Also 024 bridge; keep roots context explicit. |
| artist | f4-024-artist-joni-mitchell | Joni Mitchell | 4 | 024 | 1 | core | anchor; artist_anchor | Overlap with folk-rock and jazz/art-pop phases; evaluate object by object. |
| artist | artist-led-zeppelin | Led Zeppelin | 3 | 016 | 1 | core | anchor; gateway; album_anchor; bridge | overlaps 017 and metal family |
| artist | metallica | Metallica | 9 | 062 | 1.0 | core | anchor; artist_anchor; album_anchor; gateway |  |
| artist | michael-jackson | Michael Jackson | 12 | 088 | 1.0 | core | anchor; artist_anchor; song_first |  |
| artist | nirvana | Nirvana | 10 | 070 | 1 | core | anchor; artist_anchor | Preserve band row separately from Kurt Cobain biography and unplugged/live objects. |
| artist | f4-026-artist-pete-seeger | Pete Seeger | 4 | 026 | 1 | core | anchor; artist_anchor | Often appears through group/traditional/movement attributions. |
| artist | artist-pink-floyd | Pink Floyd | 3 | 016 | 1 | core | anchor; gateway; album_anchor; bridge | overlaps 018 |
| artist | artist-pink-floyd | Pink Floyd | 3 | 018 | 1 | core | anchor; album_anchor; gateway | overlaps 016 |
| artist | ray-charles | Ray Charles | 1 | 006 | 1.0 | core | anchor; gateway; song_first; artist_anchor |  |
| artist | ricky-nelson | Ricky Nelson | 1 | 004 | 1.0 | core | anchor; gateway; song_first; artist_anchor |  |
| artist | sam-cooke | Sam Cooke | 1 | 006 | 1.0 | core | anchor; gateway; song_first; artist_anchor |  |
| artist | artist-steely-dan | Steely Dan | 3 | 023 | 1 | core | anchor; bridge; album_anchor | overlaps 016 and 018 |
| artist | stevie-wonder | Stevie Wonder | 6 | 037 | 1.0 | core | anchor; artist_anchor; gateway | Also anchors broader 1970s soul/funk and adult-pop listening. |
| artist | taylor-swift | Taylor Swift | 12 | 091 | 1.0 | core | anchor; artist_anchor; album_anchor |  |
| artist | the-beach-boys | The Beach Boys | 1 | 007 | 1.0 | core | anchor; gateway; artist_anchor |  |
| artist | the-beatles | The Beatles | 2 | 008 | 1 | core | anchor; artist_anchor | Cross-family mass object; keep Family 2 membership but allow links to later classic-rock and pop families. |
| artist | the-platters | The Platters | 1 | 003 | 1.0 | core | anchor; gateway; song_first; artist_anchor |  |
| artist | the-shirelles | The Shirelles | 1 | 005 | 1.0 | core | anchor; gateway; song_first; artist_anchor |  |
| artist | f4-029-artist-tracy-chapman | Tracy Chapman | 4 | 029 | 1 | core | anchor; artist_anchor | Also bridges 024 and 027. |
| artist | f4-028-artist-uncle-tupelo | Uncle Tupelo | 4 | 028 | 1 | core | anchor; artist_anchor | Influence exceeds normal-user familiarity. |
| artist | f4-026-artist-woody-guthrie | Woody Guthrie | 4 | 026 | 1 | core | anchor; artist_anchor | Song recognition often exceeds artist recall. |
| song | the-ronettes-be-my-baby | Be My Baby | 1 | 005 | 1.0 | core | anchor; gateway | Artist-worthy |
| song | michael-jackson-billie-jean | Billie Jean | 12 | 088 | 1.0 | core | anchor; gateway |  |
| song | carl-perkins-blue-suede-shoes | Blue Suede Shoes | 1 | 002 | 1.0 | core | anchor; bridge | Artist-worthy |
| song | ozzy-osbourne-crazy-train | Crazy Train | 9 | 061 | 1.0 | core | anchor; gateway; song_first |  |
| song | the-penguins-earth-angel | Earth Angel | 1 | 003 | 1.0 | core | anchor; gateway | Song-first |
| song | metallica-enter-sandman | Enter Sandman | 9 | 062 | 1.0 | core | gateway; anchor |  |
| song | f4-029-song-fast-car-tracy-chapman | Fast Car | 4 | 029 | 1 | core | song_first; anchor | Renewed recognition via Luke Combs cover; distinct versions. |
| song | elvis-presley-heartbreak-hotel | Heartbreak Hotel | 1 | 001 | 1.0 | core | anchor; gateway | Artist-worthy |
| song | elvis-presley-hound-dog | Hound Dog | 1 | 001 | 1.0 | core | anchor; gateway | Artist-worthy |
| song | elvis-presley-jailhouse-rock | Jailhouse Rock | 1 | 001 | 1.0 | core | anchor; gateway | Artist-worthy |
| song | chuck-berry-johnny-b-goode | Johnny B. Goode | 1 | 001 | 1.0 | core | anchor; gateway | Artist-worthy |
| song | metallica-master-of-puppets | Master of Puppets | 9 | 062 | 1.0 | core | anchor; gateway |  |
| song | black-sabbath-paranoid | Paranoid | 9 | 061 | 1.0 | core | anchor; gateway |  |
| song | def-leppard-pour-some-sugar-on-me | Pour Some Sugar on Me | 9 | 063 | 1.0 | core | gateway; anchor; song_first |  |
| song | aretha-franklin-respect | Respect | 6 | 038 | 1.0 | core | song_first; anchor; gateway | Preserve Aretha recording distinct from Otis Redding original. |
| song | bill-haley-and-his-comets-rock-around-the-clock | Rock Around the Clock | 1 | 001 | 1.0 | core | anchor; gateway | Artist-worthy |
| song | nirvana-smells-like-teen-spirit | Smells Like Teen Spirit | 10 | 070 | 1 | core | song_first; anchor; gateway |  |
| song | song-stairway-to-heaven-1971 | Stairway to Heaven | 3 | 016 | 1 | core | song_first; gateway | overlaps 017 |
| song | ben-e-king-stand-by-me | Stand by Me | 1 | 006 | 1.0 | core | anchor; gateway | Artist-worthy |
| song | f4-026-song-this-land-is-your-land-woody-guthrie | This Land Is Your Land | 4 | 026 | 1 | core | song_first; anchor | Publication/recording date varies; standard exceeds artist. |
| song | the-shirelles-will-you-love-me-tomorrow | Will You Love Me Tomorrow | 1 | 005 | 1.0 | core | anchor; gateway | Artist-worthy |
| album | album-aja-1977 | Aja | 3 | 023 | 0.99 | core | album_anchor; gateway | overlaps 018 |
| album | album-at-fillmore-east-1971 | At Fillmore East | 3 | 019 | 0.99 | core | live_gateway; album_anchor | live bias vs studio objects |
| album | album-rumours-1977 | Rumours | 3 | 016 | 0.99 | core | album_anchor; gateway | overlaps 022 |
| album | little-richard-heres-little-richard | Here's Little Richard | 1 | 001 | 0.98 | core | album_anchor | True album |
| album | aretha-franklin-i-never-loved-a-man-the-way-i-love-you | I Never Loved a Man the Way I Love You | 6 | 038 | 0.98 | core | album_anchor; anchor; gateway |  |
| album | nas-illmatic | Illmatic | 7 | 048 | 0.98 | core | album_anchor; anchor |  |
| album | album-paranoid-1970 | Paranoid | 3 | 017 | 0.98 | core | album_anchor | overlaps metal family |
| album | the-ronettes-presenting-the-fabulous-ronettes-featuring-veronica | Presenting the Fabulous Ronettes Featuring Veronica | 1 | 005 | 0.98 | core | album_anchor | True album |
| album | the-beach-boys-surfin-usa | Surfin' U.S.A. | 1 | 007 | 0.98 | core | album_anchor | True album |
| album | ray-charles-the-genius-of-ray-charles | The Genius of Ray Charles | 1 | 006 | 0.98 | core | album_anchor | True album |

### Objects With Suspiciously Low Weights

| object_type | canonical_id | display_name | family | archetype | weight | survey_tier | roles | warning |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| song | f4-028-song-waiting-for-a-superman-the-jayhawks | Waiting for a Superman | 4 | 028 | 0.1 | suppress | false_nearby; boundary | Likely erroneous attribution/title; canonical song is associated with The Flaming Lips. |
| song | f4-030-song-let-her-go-passenger | Let Her Go | 4 | 030 | 0.3 | suppress | false_nearby; song_first | Often resolves outside family-core folk-pop. |
| artist | f4-030-artist-passenger | Passenger | 4 | 030 | 0.34 | suppress | false_nearby; song_first; artist_anchor | Often too pop-ballad/playlist-core for family center. |
| artist | f4-029-artist-jason-mraz | Jason Mraz | 4 | 029 | 0.36 | suppress | false_nearby; gateway; artist_anchor | Often resolves as pop/AC rather than family-core songcraft. |
| artist | f4-028-artist-robbie-fulks | Robbie Fulks | 4 | 028 | 0.42 | edge | deepening; artist_anchor | Low general recognition. |
| song | ray-stevens-ahab-the-arab | Ahab the Arab | 17 | 111 | 0.42 | suppress | song_first; boundary | Use only for historical/duplicate handling; not a normal recommendation object. |
| artist | f4-028-artist-freakwater | Freakwater | 4 | 028 | 0.44 | edge | deepening; artist_anchor | Specialist scene inclusion only. |
| artist | f4-025-artist-vanessa-carlton | Vanessa Carlton | 4 | 025 | 0.44 | edge | gateway; song_first; artist_anchor | Teen-pop framing is a false-nearby risk. |
| song | f4-025-song-someone-like-you-adele | Someone Like You | 4 | 025 | 0.44 | edge | song_first; boundary | Better as song than artist row here. |
| artist | f4-028-artist-jason-molina | Jason Molina | 4 | 028 | 0.45 | edge | false_nearby; bridge; artist_anchor | Sad-prestige indie overlap; include with warning. |
| album | f4-029-album-room-for-squares-john-mayer | Room for Squares | 4 | 029 | 0.46 | edge | gateway; album_anchor | Pop celebrity framing may dominate. |
| artist | f4-026-artist-dave-van-ronk | Dave Van Ronk | 4 | 026 | 0.46 | edge | deepening; artist_anchor | Low mass survey value. |
| artist | hermans-hermits | Herman's Hermits | 2 | 008 | 0.46 | edge | false_nearby; contrast | Do not promote as core despite mass 60s visibility. |
| artist | f4-024-artist-warren-zevon | Warren Zevon | 4 | 024 | 0.46 | edge | contrast; bridge; artist_anchor | Novelty/rock identity makes this an edge object. |
| song | f4-025-song-criminal-fiona-apple | Criminal | 4 | 025 | 0.46 | edge | contrast; bridge; song_first | Alternative/art-pop routing likely. |
| song | f4-027-song-dublin-blues-guy-clark | Dublin Blues | 4 | 027 | 0.46 | edge | deepening; song_first | Specialist survey value. |
| album | f4-029-album-bachelor-no-2-aimee-mann | Bachelor No. 2 | 4 | 029 | 0.48 | edge | deepening; album_anchor | Critic/prestige more than mass survey. |
| artist | artist-govt-mule | Gov't Mule | 3 | 019 | 0.48 | edge | deepening; bridge; anchor | later-jam branch more than page-one |
| artist | incubus | Incubus | 9 | 066 | 0.48 | edge | boundary; false_nearby | Usually suppress from true metal pages unless needed for boundary. |
| artist | jackie-evancho | Jackie Evancho | 14 | 103 | 0.48 | edge | false_nearby; boundary | Talent-show/classical-crossover recognition should stay boundary until user confirms appetite. |
| artist | f4-027-artist-mary-chapin-carpenter | Mary Chapin Carpenter | 4 | 027 | 0.48 | edge | gateway; bridge; artist_anchor | Country family overlap; do not merge with Lucinda original. |
| artist | f4-026-artist-the-kingston-trio | The Kingston Trio | 4 | 026 | 0.48 | edge | gateway; contrast; artist_anchor | Can resolve as collegiate folk-pop rather than protest/revival core. |
| song | f4-028-song-passenger-side-wilco | Passenger Side | 4 | 028 | 0.48 | edge | bridge; song_first | Later Wilco art-rock should not bleed in. |
| song | f4-030-song-rivers-and-roads-the-head-and-the-heart | Rivers and Roads | 4 | 030 | 0.48 | edge | bridge; song_first | Artist not separately seeded; add later if expanding. |
| song | f4-028-song-too-far-to-care-old-97-s | Too Far to Care | 4 | 028 | 0.48 | edge | deepening; song_first | Album-title distinction needed. |
| song | f4-029-song-why-georgia-john-mayer | Why Georgia | 4 | 029 | 0.48 | edge | gateway; song_first | Pop celebrity/blues-rock contexts. |
| album | f4-028-album-heartbreaker-ryan-adams | Heartbreaker | 4 | 028 | 0.5 | edge | bridge; album_anchor | Solo object distinct from Whiskeytown. |
| album | f4-026-album-in-concert-joan-baez | In Concert | 4 | 026 | 0.5 | edge | live_gateway; deepening | Live album; check canonical title if imported. |
| album | f4-030-album-strange-trails-lord-huron | Strange Trails | 4 | 030 | 0.5 | edge | bridge; album_anchor | Mood/sync overfitting risk. |
| album | f4-025-album-when-the-pawn-fiona-apple | When the Pawn... | 4 | 025 | 0.5 | edge | contrast; bridge; album_anchor | Use as edge, not core. |
| artist | f4-027-artist-gram-parsons | Gram Parsons | 4 | 027 | 0.5 | edge | bridge; artist_anchor | Often belongs in country-rock rather than this family center. |
| artist | f4-030-artist-hozier | Hozier | 4 | 030 | 0.5 | edge | contrast; bridge; artist_anchor | Soul-rock and gospel-blues identity usually dominates. |
| artist | f4-030-artist-phoebe-bridgers | Phoebe Bridgers | 4 | 030 | 0.5 | edge | contrast; bridge; artist_anchor | Often routes to indie-rock/alternative family. |
| artist | f4-026-artist-richie-havens | Richie Havens | 4 | 026 | 0.5 | edge | bridge; artist_anchor | Often remembered through performance context. |
| artist | shinedown | Shinedown | 9 | 067 | 0.5 | edge | false_nearby; gateway; boundary | Keep low-weight; not a metal anchor. |
| artist | f4-028-artist-the-bottle-rockets | The Bottle Rockets | 4 | 028 | 0.5 | edge | deepening; artist_anchor | Scene-depth more than survey anchor. |
| artist | artist-tommy-tutone | Tommy Tutone | 3 | 021 | 0.5 | edge | song_first; false_nearby | Artist effectively song-only. |
| song | f4-026-song-deportee-woody-guthrie | Deportee | 4 | 026 | 0.5 | edge | deepening; song_first | Lyrics/music attribution and cover versions require care. |
| song | f4-027-song-gulf-coast-highway-nanci-griffith | Gulf Coast Highway | 4 | 027 | 0.5 | edge | deepening; song_first | Duet/version attribution risk. |
| song | f4-028-song-new-madrid-uncle-tupelo | New Madrid | 4 | 028 | 0.5 | edge | deepening; song_first | Scene-depth object. |
| song | f4-029-song-save-me-aimee-mann | Save Me | 4 | 029 | 0.5 | edge | deepening; song_first | Film soundtrack context may dominate. |

### Archetypes With Too Many High-Weight Anchors

| archetype_id | high_weight_anchor_count | archetype_name | family_id |
| --- | --- | --- | --- |
| 001 | 32 | Early Rock & Roll Foundations | 1 |
| 061 | 18 | Traditional Heavy Metal / NWOBHM | 9 |
| 037 | 16 | Motown / Detroit Soul Pop | 6 |
| 050 | 16 | Pop-Rap / Mainstream Hip-Hop Crossover | 7 |
| 066 | 16 | Alt-Metal / Nu-Metal / Rap-Metal | 9 |
| 003 | 15 | Doo-Wop / Vocal Group Oldies | 1 |
| 016 | 15 | Classic Rock / Album-Rock Spine | 3 |
| 024 | 15 | Classic singer-songwriter | 4 |
| 047 | 15 | Gangsta Rap / West Coast / G-Funk | 7 |
| 062 | 15 | Thrash Metal / Speed Metal | 9 |
| 070 | 14 | Grunge / Seattle / 90s Alt Center | 10 |
| 088 | 14 | 70s-80s Pop Sovereigns | 12 |
| 002 | 13 | Rockabilly / Primitive Guitar / Proto-Garage | 1 |
| 042 | 13 | New Jack Swing / 80s-90s R&B Pop | 6 |
| 006 | 12 | Early Soul-Pop / R&B Crossover | 1 |
| 007 | 12 | Surf / Instrumental / Early Guitar Pop | 1 |
| 038 | 12 | Southern Soul / Stax / Muscle Shoals | 6 |

### Archetypes With Too Few Page 1 Candidates

| archetype_id | page1_candidate_count | archetype_name | family_id |
| --- | --- | --- | --- |
| 036 | 0 | Red Dirt / Americana Country / Texas Country | 5 |
| 060 | 0 | Noise Rock / Post-Hardcore / Touch and Go Axis | 8 |
| 082 | 0 | Techno / Detroit / Minimal Electronic | 11 |
| 111 | 0 | Novelty / Comedy / Weird Pop | 17 |
| 112 | 0 | Holiday / Christmas / Seasonal Canon | 17 |
| 113 | 0 | Party / Wedding / Karaoke / Bar Singalong Canon | 17 |
| 114 | 0 | Kids / Family / Household Context Music | 17 |
| 086 | 1 | Synthwave / Chillwave / Bedroom Electronic | 11 |
| 015 | 2 | Art-Rock / Proto-Alternative / Freak Underground | 2 |
| 009 | 3 | Jangle Pop / Folk-Rock Precursor | 2 |
| 011 | 3 | Garage Rock / Nuggets / Proto-Punk Singles | 2 |
| 085 | 3 | Indie Dance / Dance-Punk / Electroclash | 11 |
| 120 | 3 | Algorithmic Mood / Lo-Fi / Chill / Study Music | 18 |

### Archetypes With Too Few Page 2 Candidates

| archetype_id | page2_candidate_count | archetype_name | family_id |
| --- | --- | --- | --- |
| 088 | 1 | 70s-80s Pop Sovereigns | 12 |
| 009 | 2 | Jangle Pop / Folk-Rock Precursor | 2 |
| 089 | 2 | 90s Pop / Teen Pop / TRL Monoculture | 12 |
| 091 | 3 | 2010s Persona Pop / Architectural Pop | 12 |

## Coverage Balance Review

### Families / Archetypes That Look Underfilled

| archetype_id | family_id | archetype_name | artists | albums | songs | total |
| --- | --- | --- | --- | --- | --- | --- |
| 009 | 2 | Jangle Pop / Folk-Rock Precursor | 3 | 0 | 3 | 6 |
| 010 | 2 | Folk-Rock / Harmony Pop / 60s Songcraft | 6 | 5 | 6 | 17 |
| 011 | 2 | Garage Rock / Nuggets / Proto-Punk Singles | 3 | 3 | 12 | 18 |
| 012 | 2 | Baroque Pop / Chamber Pop / Artful 60s Pop | 5 | 5 | 8 | 18 |
| 114 | 17 | Kids / Family / Household Context Music | 5 | 4 | 9 | 18 |
| 111 | 17 | Novelty / Comedy / Weird Pop | 7 | 4 | 8 | 19 |
| 088 | 12 | 70s-80s Pop Sovereigns | 7 | 6 | 8 | 21 |
| 091 | 12 | 2010s Persona Pop / Architectural Pop | 7 | 6 | 8 | 21 |
| 090 | 12 | 2000s Pop / Dance-Pop / Club-Pop | 8 | 6 | 8 | 22 |
| 015 | 2 | Art-Rock / Proto-Alternative / Freak Underground | 4 | 16 | 3 | 23 |
| 070 | 10 | Grunge / Seattle / 90s Alt Center | 6 | 7 | 10 | 23 |
| 092 | 12 | Adult Pop / TV-Drama Anthem / Inspirational Pop | 9 | 6 | 8 | 23 |
| 072 | 10 | 90s Indie / Lo-Fi / Slacker / Matador Axis | 7 | 7 | 10 | 24 |
| 079 | 10 | Garage Revival / Rock-Is-Back 2000s | 7 | 7 | 10 | 24 |

### Families / Archetypes That Look Bloated

| archetype_id | family_id | archetype_name | artists | albums | songs | total |
| --- | --- | --- | --- | --- | --- | --- |
| 001 | 1 | Early Rock & Roll Foundations | 35 | 21 | 65 | 121 |
| 006 | 1 | Early Soul-Pop / R&B Crossover | 39 | 19 | 55 | 113 |
| 007 | 1 | Surf / Instrumental / Early Guitar Pop | 35 | 19 | 52 | 106 |
| 003 | 1 | Doo-Wop / Vocal Group Oldies | 37 | 15 | 51 | 103 |
| 002 | 1 | Rockabilly / Primitive Guitar / Proto-Garage | 33 | 16 | 53 | 102 |
| 004 | 1 | Teen Idol / Early Pop-Rock Radio | 34 | 16 | 52 | 102 |
| 005 | 1 | Brill Building / Girl Group / Early 60s Pop Craft | 34 | 18 | 49 | 101 |
| 066 | 9 | Alt-Metal / Nu-Metal / Rap-Metal | 20 | 22 | 27 | 69 |
| 067 | 9 | Metalcore / Emo-Heavy / Modern Active Rock | 22 | 20 | 25 | 67 |

### Song-First vs Artist-First Balance

| scope | song_first | artist_anchor | album_anchor | anchor | gateway | bridge | boundary | false_nearby | contrast |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| all families | 1795 | 675 | 1009 | 985 | 2616 | 1510 | 431 | 136 | 31 |
| family 1 | 337 | 53 | 102 | 101 | 501 | 149 | 53 | 1 | 3 |
| family 2 | 82 | 23 | 52 | 39 | 62 | 107 | 20 | 3 | 6 |
| family 3 | 131 | 2 | 116 | 70 | 265 | 133 | 45 | 4 | 0 |
| family 4 | 136 | 102 | 86 | 87 | 104 | 109 | 8 | 5 | 8 |
| family 5 | 53 | 41 | 39 | 45 | 79 | 67 | 18 | 0 | 5 |
| family 6 | 194 | 59 | 81 | 105 | 235 | 112 | 16 | 0 | 0 |
| family 7 | 209 | 49 | 103 | 125 | 221 | 164 | 43 | 12 | 0 |
| family 8 | 54 | 33 | 32 | 42 | 98 | 101 | 22 | 2 | 4 |
| family 9 | 56 | 38 | 154 | 97 | 269 | 109 | 99 | 29 | 1 |
| family 10 | 144 | 76 | 90 | 86 | 177 | 155 | 32 | 21 | 1 |
| family 11 | 60 | 39 | 35 | 38 | 91 | 68 | 20 | 0 | 3 |
| family 12 | 77 | 18 | 33 | 40 | 90 | 30 | 23 | 6 | 0 |
| family 13 | 61 | 42 | 24 | 34 | 91 | 63 | 6 | 0 | 0 |
| family 14 | 35 | 20 | 14 | 18 | 39 | 37 | 10 | 5 | 0 |
| family 15 | 47 | 23 | 21 | 16 | 68 | 28 | 0 | 0 | 0 |
| family 16 | 27 | 27 | 7 | 13 | 73 | 18 | 0 | 3 | 0 |
| family 17 | 71 | 1 | 9 | 12 | 63 | 2 | 4 | 36 | 0 |
| family 18 | 21 | 29 | 11 | 17 | 90 | 58 | 12 | 9 | 0 |

### Album Exceptions and Compilation-Gateway Usage

| family | archetype | album | artist | album_object_type | roles | warning |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 001 | Atlantic Rhythm and Blues 1947-1974 | Various Artists | compilation | compilation_gateway; album_anchor | Also 006 |
| 1 | 001 | Jerry Lee's Greatest! | Jerry Lee Lewis | compilation | gateway; album_anchor | Greatest-hits style LP |
| 1 | 001 | Let the Good Times Roll | Louis Jordan | compilation | compilation_gateway; gateway | Compilation > original album |
| 1 | 001 | Rock Around the Clock | Bill Haley & His Comets | soundtrack | album_anchor | Soundtrack-linked LP |
| 1 | 001 | The Great Twenty-Eight | Chuck Berry | compilation | gateway; compilation_gateway | Compilation/gateway |
| 1 | 001 | The Specialty Story | Various Artists | compilation | compilation_gateway; album_anchor | Also 006 |
| 1 | 001 | The Sun Sessions | Elvis Presley | compilation | gateway; compilation_gateway | Compilation/gateway |
| 1 | 002 | Hop, Skip and Jump | The Collins Kids | compilation | compilation_gateway | Depth only |
| 1 | 002 | Mr. Frantic Is Boppin' the Blues | Ronnie Self | compilation | deepening; compilation_gateway | Specialist only |
| 1 | 002 | The Sun Rockabilly Years | Various Artists | compilation | compilation_gateway; album_anchor | Sun comp naming needs canonical selection |
| 1 | 003 | Encore of Golden Hits | The Platters | compilation | gateway; compilation_gateway | Gateway |
| 1 | 003 | Golden Hits | The Five Satins | compilation | compilation_gateway | Gateway |
| 1 | 003 | Life Is But a Dream | The Harptones | compilation | compilation_gateway; deepening | Depth |
| 1 | 003 | The Best of The Jive Five | The Jive Five | compilation | compilation_gateway; gateway | Song-first |
| 1 | 003 | The Best of the Crests | The Crests | compilation | compilation_gateway | Gateway |
| 1 | 003 | The Doo Wop Box | Various Artists | compilation | compilation_gateway; album_anchor | Should not replace individual songs |
| 1 | 003 | The Drifters' Golden Hits | The Drifters | compilation | gateway; compilation_gateway | Gateway |
| 1 | 004 | A Thousand Stars | Kathy Young & The Innocents | compilation | compilation_gateway | Song-first |
| 1 | 004 | Johnny's Greatest Hits | Johnny Mathis | compilation | compilation_gateway; album_anchor | More contrast than core 004 |
| 1 | 004 | Pat Boone's Golden Hits | Pat Boone | compilation | compilation_gateway; album_anchor | Dead-end risk |
| 1 | 005 | A Christmas Gift for You from Phil Spector | Various Artists | compilation | gateway; album_anchor; compilation_gateway | Compilation/gateway |
| 1 | 005 | Back to Mono (1958-1969) | Phil Spector / Various Artists | compilation | compilation_gateway; album_anchor | Artist credit normalization required |
| 1 | 005 | One Kiss Can Lead to Another: Girl Group Sounds Lost & Found | Various Artists | compilation | compilation_gateway; album_anchor | Compilation object should not overtake anchor songs |
| 1 | 005 | The Red Bird Girls | Various Artists | compilation | compilation_gateway; album_anchor | Label comp |
| 1 | 006 | Live at the Apollo | James Brown | live_album | live_gateway; album_anchor; gateway | Later soul family overlap |
| 1 | 007 | Intoxica!!! | The Revels | compilation | compilation_gateway; deepening | Deep/cult only |
| 1 | 007 | Ride the Wild Surf | Various Artists | soundtrack | gateway | Soundtrack |
| 1 | 007 | Surf-Age Nuggets | Various Artists | compilation | compilation_gateway; album_anchor | Use as Page 3 gateway |
| 2 | 008 | A Hard Day's Night | The Beatles | soundtrack | album_anchor; gateway; anchor | Same title as song; keep ID artist-prefixed. |
| 2 | 011 | Nuggets: Original Artyfacts From the First Psychedelic Era, 1965-1968 | Various Artists | compilation | compilation_gateway; gateway; anchor | Compilation, not a single-artist album. |
| 2 | 011 | Pebbles, Volume 1 | Various Artists | compilation | compilation_gateway; deepening | Compilation object; do not inflate every Pebbles artist. |
| 2 | 013 | Magical Mystery Tour | The Beatles | soundtrack | album_anchor; anchor; gateway | UK/US format differences should be handled by release metadata, not duplicate rows. |
| 2 | 013 | Nuggets: Come to the Sunshine | Various Artists | compilation | compilation_gateway; gateway; deepening | Later compilation; do not treat as original 1960s release. |
| 2 | 014 | Live/Dead | Grateful Dead | live_album | live_gateway; album_anchor; bridge | Jam-family overlap; keep edge. |
| 2 | 014 | Wheels of Fire | Cream | live_album | album_anchor; live_gateway; bridge | Hybrid studio/live double album; object type set to live_album because source emphasized jam bridge. |
| 2 | 015 | Kick Out the Jams | MC5 | live_album | album_anchor; live_gateway; bridge | Live album; do not normalize as studio_album. |
| 3 | 016 | Frampton Comes Alive! | Peter Frampton | live_album | live_gateway; gateway; album_anchor | live-object dominance |
| 3 | 016 | Their Greatest Hits 1971-1975 | Eagles | compilation | compilation_gateway; gateway | compilation vs studio split |
| 3 | 017 | Alive! | Kiss | live_album | live_gateway; gateway; album_anchor | overlaps 020 |
| 3 | 019 | At Fillmore East | The Allman Brothers Band | live_album | live_gateway; album_anchor | live bias vs studio objects |
| 3 | 019 | Waiting for Columbus | Little Feat | live_album | live_gateway; gateway; album_anchor | live-object dominance |
| 3 | 021 | Cheap Trick at Budokan | Cheap Trick | live_album | live_gateway; gateway; album_anchor | live-object dominance |
| 3 | 022 | History: America's Greatest Hits | America | compilation | compilation_gateway; gateway | compilation dominance |
| 3 | 022 | The Best of Bread | Bread | compilation | compilation_gateway; gateway | compilation dominance |
| 3 | 022 | Their Greatest Hits 1971-1975 | Eagles | compilation | compilation_gateway; gateway | overlaps 016 |
| 4 | 026 | In Concert | Joan Baez | live_album | live_gateway; deepening | Live album; check canonical title if imported. |
| 5 | 031 | 40 Greatest Hits | Hank Williams | compilation | compilation_gateway; album_anchor |  |
| 5 | 031 | At Folsom Prison | Johnny Cash | live_album | live_gateway; album_anchor; bridge |  |
| 5 | 031 | The Essential Charley Pride | Charley Pride | compilation | compilation_gateway |  |
| 5 | 031 | The Essential Jimmie Rodgers | Jimmie Rodgers | compilation | compilation_gateway | Compilation object stands in for pre-LP foundational catalog. |
| 5 | 031 | The Queen of Country Music | Kitty Wells | compilation | compilation_gateway | Compilation gateway; verify exact anthology/version before import lock. |
| 5 | 032 | Viva Terlingua | Jerry Jeff Walker | live_album | live_gateway; bridge | Live-recording specificity matters. |
| 5 | 032 | Wanted! The Outlaws | Various Artists | compilation | compilation_gateway; anchor |  |
| 5 | 034 | Pure Country | George Strait | soundtrack | gateway; album_anchor |  |
| 6 | 039 | Live at the Apollo | James Brown | live_album | live_gateway; album_anchor; anchor | Live object, not a studio best-of. |
| 6 | 039 | Sex Machine | James Brown | live_album | live_gateway; album_anchor; gateway | Hybrid live/studio release; object type set by live gateway function. |
| 6 | 039 | Super Fly | Curtis Mayfield | soundtrack | album_anchor; bridge; gateway | Soundtrack object. |
| 6 | 039 | That's the Way of the World | Earth, Wind & Fire | soundtrack | album_anchor; gateway; bridge | Film soundtrack context; commonly treated as core EWF album. |
| 6 | 040 | Saturday Night Fever | Various Artists | soundtrack | album_anchor; gateway; compilation_gateway | Compilation/soundtrack; do not assign all tracks to Bee Gees only. |
| 6 | 044 | Fuck the World | Brent Faiyaz | ep | gateway; album_anchor | Explicit title and EP type should be reviewed for UI display. |
| 6 | 044 | H.E.R. | H.E.R. | compilation | compilation_gateway; gateway | Compilation object; periods normalized in ID. |
| 6 | 044 | House of Balloons | The Weeknd | ep | album_anchor; anchor; boundary | Mixtape object type requires later schema review. |
| 6 | 044 | Trilogy | The Weeknd | compilation | compilation_gateway; gateway; album_anchor | Compilation of mixtapes; do not replace individual mixtape objects automatically. |
| 8 | 053 | Singles Going Steady | Buzzcocks | compilation | compilation_gateway |  |
| 8 | 054 | No New York | Various Artists | compilation | compilation_gateway; deepening | Compilation object; do not treat Various Artists as an artist preference signal. |
| 8 | 055 | Complete Discography | Minor Threat | compilation | compilation_gateway |  |
| 8 | 060 | The Greatest Gift | Scratch Acid | compilation | compilation_gateway; deepening |  |
| 9 | 061 | Live After Death | Iron Maiden | live_album | live_gateway; album_anchor |  |
| 9 | 061 | No Sleep 'til Hammersmith | Motorhead | live_album | live_gateway; album_anchor |  |
| 9 | 063 | Greatest Hits | Bon Jovi | compilation | compilation_gateway; gateway | Later compilation object; use for survey utility, not era chronology. |
| 9 | 063 | Vault: Def Leppard Greatest Hits 1980-1995 | Def Leppard | compilation | compilation_gateway; gateway |  |
| 9 | 065 | Broken | Nine Inch Nails | ep | album_anchor; bridge |  |
| 10 | 070 | Superfuzz Bigmuff | Mudhoney | ep | album_anchor; deepening; bridge |  |
| 11 | 082 | Innovator | Derrick May | compilation | compilation_gateway |  |
| 11 | 082 | Techno! The New Dance Sound of Detroit | Various Artists | compilation | compilation_gateway | Label/compilation object; do not merge as a normal artist album. |
| 11 | 083 | Scary Monsters and Nice Sprites | Skrillex | ep | gateway |  |
| 11 | 083 | Until Now | Swedish House Mafia | compilation | compilation_gateway |  |
| 12 | 088 | Purple Rain | Prince | soundtrack | album_anchor; bridge |  |
| 13 | 095 | Un Azteca en el Azteca | Vicente Fernandez | live_album | live_gateway |  |
| 13 | 098 | Get Up | NewJeans | ep | gateway |  |

## False-Nearby / Dead-End Readiness

### Family-Level Contrast Readiness

| family_id | family_name | contrast_boundary_count | adaptive Page 2 readiness | example contrast / boundary objects |
| --- | --- | --- | --- | --- |
| 1 | Early Rock, Oldies, Doo-Wop, Pre-Beatles Pop | 55 | yes | The Sonics; Ronnie Self; The Phantom; The Rock-A-Teens; Fabian; Johnny Mathis; Pat Boone; Garnet Mimms; Here Are The Sonics — The Sonics; Bo Diddley — Bo Diddley; Rave On — Buddy Holly; That's All Right — Elvis Presley |
| 2 | Beatles, British Invasion, 60s Pop-Rock | 26 | yes | The Monkees; Love; The Velvet Underground; Herman's Hermits; The Dave Clark Five; Bee Gees (early); Pisces, Aquarius, Capricorn & Jones Ltd. — The Monkees; The Velvet Underground & Nico — The Velvet Underground & Nico; The Stooges — The Stooges; Freak Out! — The Mothers of Invention; Safe as Milk — Captain Beefheart & His Magic Band; The Piper at the Gates of Dawn — Pink Floyd |
| 3 | Classic Rock, Album Rock, Progressive Rock | 49 | yes | Meat Loaf; Alice Cooper; Kiss; Gentle Giant; Van der Graaf Generator; Renaissance; Lynyrd Skynyrd; Marshall Tucker Band; Charlie Daniels Band; Molly Hatchet; Outlaws; Alice Cooper |
| 4 | Singer-Songwriter, Folk, Americana, Adult Songcraft | 20 | yes | Tori Amos; Jason Molina; Warren Zevon; Fiona Apple; The Kingston Trio; Jason Mraz; Hozier; Phoebe Bridgers; Passenger; When the Pawn... — Fiona Apple; House of the Rising Sun — Traditional / revival circuit object; Waiting for a Superman — The Jayhawks |
| 5 | Country | 21 | yes | David Allan Coe; Gram Parsons; The Flying Burrito Brothers; Townes Van Zandt; Billy Ray Cyrus; Kacey Musgraves; Colter Wall; Koe Wetzel; Sturgill Simpson; Some Gave All — Billy Ray Cyrus; Golden Hour — Kacey Musgraves; Blue Yodel No. 1 (T for Texas) — Jimmie Rodgers |
| 6 | Soul, Funk, Disco, R&B Foundations | 16 | yes | Parliament/Funkadelic; Rick James; Prince; Village People; Sade; FKA twigs; Maggot Brain — Funkadelic; Diamond Life — Sade; House of Balloons — The Weeknd; Take Me Apart — Kelela; Maggot Brain — Funkadelic; Super Freak — Rick James |
| 7 | Hip-Hop | 54 | yes | Roxanne Shante; Geto Boys; Cypress Hill; The LOX; 2 Live Crew; Doja Cat; MC Hammer; Vanilla Ice; Flo Rida; Danny Brown; Death Grips; Childish Gambino |
| 8 | Punk, Hardcore, Post-Punk, New Wave | 27 | yes | The Saints; Wire; James Chance and the Contortions; Suicide; Cro-Mags; Suicidal Tendencies; Killing Joke; Minutemen; They Might Be Giants; Butthole Surfers; Scratch Acid; Slint |
| 9 | Metal and Heavy Music | 114 | yes | Mercyful Fate; Rainbow; Deep Purple; Scorpions; Ghost; Thin Lizzy; Kreator; Venom; Suicidal Tendencies; Bon Jovi; Def Leppard; Guns N' Roses |
| 10 | Alternative, Indie, Grunge, Emo | 52 | yes | Sonic Youth; Wipers; The Jesus and Mary Chain; Husker Du; The Cure; Bush; Live; Collective Soul; Creed; Nickelback; My Bloody Valentine; Bikini Kill |
| 11 | Electronic, Dance, Club, Industrial, Experimental Pop | 21 | yes | Basic Channel; Nicolas Jaar; Crystal Castles; Peaches; Yaeji; HOME; Arca; Bjork; Nine Inch Nails; Oneohtrix Point Never; Crystal Castles — Crystal Castles; Odyssey — HOME |
| 12 | Pop Monoculture and Persona Pop | 29 | yes | Celine Dion; Black Eyed Peas; The Weeknd; Lorde; Lana Del Rey; Ed Sheeran; Rachel Platten; Christina Perri; Chappell Roan; Charli XCX; Ice Spice; PinkPantheress |
| 13 | Latin, Caribbean, Global Pop | 6 | maybe | BABYMETAL; FIFTY FIFTY; Deep Forest; Metal Resistance — BABYMETAL; Cupid — FIFTY FIFTY; Sweet Lullaby — Deep Forest |
| 14 | Jazz, Standards, Vocal, Classical-Adjacent | 11 | maybe | Vanessa-Mae; Max Richter; Jackie Evancho; Classics in the Key of G — Kenny G; The Chopin Album — Lang Lang; The Blue Notebooks — Max Richter; Watermark — Enya; Blue in Green — Miles Davis; Soulful Strut — Young-Holt Unlimited; La Campanella — Lang Lang; Adagio for Strings — London Philharmonic Orchestra |
| 15 | Soundtrack, Theater, Musicals, Family Context | 0 | thin |  |
| 16 | Christian, Worship, Gospel | 3 | thin | Skillet; Awake — Skillet; Monster — Skillet |
| 17 | Nostalgia, Novelty, Context, Shared Listening | 40 | yes | Spike Jones; Napoleon XIV; Mariah Carey; Journey; Bon Jovi; Neil Diamond; ABBA; Shania Twain; The Killers; Garth Brooks; Kool & The Gang; Kidz Bop |
| 18 | Modern Rock, Current Discovery, Internet-Native Scenes | 21 | yes | black midi; Arca; Geese; Black Country, New Road; Deftones; Yeule; Lo-fi Girl; Boards of Canada; Schlagenheim — black midi; Ants From Up There — Black Country, New Road; White Pony — Deftones; lofi hip hop radio — Lo-fi Girl |

### Contrast Objects

| family | archetype | object_type | object | roles | survey_tier | warning |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 004 | artist | Johnny Mathis | gateway; contrast | core | More adult-pop than teen-idol |
| 1 | 004 | artist | Fabian | gateway; contrast; song_first | standard |  |
| 1 | 004 | artist | Pat Boone | contrast; gateway; false_nearby; boundary | standard | Useful but often dead-end check |
| 2 | 008 | song | Glad All Over — The Dave Clark Five | song_first; gateway; contrast | standard | Do not overpromote to core anchor. |
| 2 | 008 | artist | The Dave Clark Five | gateway; contrast | standard | Avoid over-weighting relative to Beatles/Stones/Who/Kinks. |
| 2 | 008 | artist | Herman's Hermits | false_nearby; contrast | edge | Do not promote as core despite mass 60s visibility. |
| 2 | 012 | artist | Bee Gees (early) | bridge; false_nearby | edge | Do not merge with later Bee Gees disco/pop family behavior. |
| 2 | 013 | artist | The Monkees | gateway; artist_anchor; contrast | standard | Do not suppress solely as manufactured pop; keep as contrast/gateway. |
| 2 | 013 | album | Pisces, Aquarius, Capricorn & Jones Ltd. — The Monkees | album_anchor; gateway; contrast | standard | Ampersand normalized to `and` in slug. |
| 2 | 013 | song | Crimson and Clover — Tommy James and the Shondells | song_first; contrast; boundary | edge | Group name ampersand normalized. |
| 2 | 013 | song | Pictures of Matchstick Men — Status Quo | song_first; false_nearby; boundary | edge | Do not merge with later boogie-rock Status Quo canon. |
| 3 | 021 | artist | Tommy Tutone | song_first; false_nearby | edge | Artist effectively song-only. |
| 3 | 023 | song | Baby Come Back — Player | gateway; song_first; false_nearby | edge | false-nearby risk if used as strict yacht anchor |
| 3 | 023 | artist | Player | song_first; false_nearby | edge | one-song dominance; not a broad yacht anchor |
| 3 | 023 | album | Player — Player | gateway; false_nearby | edge | not a broad yacht anchor |
| 4 | 024 | artist | Warren Zevon | contrast; bridge; artist_anchor | edge | Novelty/rock identity makes this an edge object. |
| 4 | 025 | artist | Fiona Apple | bridge; contrast; artist_anchor | edge | Often belongs in alternative/art-pop; use as boundary bridge. |
| 4 | 025 | album | When the Pawn... — Fiona Apple | contrast; bridge; album_anchor | edge | Use as edge, not core. |
| 4 | 025 | song | Criminal — Fiona Apple | contrast; bridge; song_first | edge | Alternative/art-pop routing likely. |
| 4 | 025 | artist | Tori Amos | bridge; contrast; artist_anchor | edge | Alt-art catalog can pull this outside family center. |
| 4 | 026 | artist | The Kingston Trio | gateway; contrast; artist_anchor | edge | Can resolve as collegiate folk-pop rather than protest/revival core. |
| 4 | 028 | artist | Jason Molina | false_nearby; bridge; artist_anchor | edge | Sad-prestige indie overlap; include with warning. |
| 4 | 028 | song | Waiting for a Superman — The Jayhawks | false_nearby; boundary | suppress | Likely erroneous attribution/title; canonical song is associated with The Flaming Lips. |
| 4 | 029 | artist | Jason Mraz | false_nearby; gateway; artist_anchor | suppress | Often resolves as pop/AC rather than family-core songcraft. |
| 4 | 030 | artist | Hozier | contrast; bridge; artist_anchor | edge | Soul-rock and gospel-blues identity usually dominates. |
| 4 | 030 | artist | Phoebe Bridgers | contrast; bridge; artist_anchor | edge | Often routes to indie-rock/alternative family. |
| 4 | 030 | song | Let Her Go — Passenger | false_nearby; song_first | suppress | Often resolves outside family-core folk-pop. |
| 4 | 030 | artist | Passenger | false_nearby; song_first; artist_anchor | suppress | Often too pop-ballad/playlist-core for family center. |
| 5 | 032 | song | Okie from Muskogee — Merle Haggard | boundary; contrast | standard | Culture-war/context object; avoid treating every tap as outlaw affinity. |
| 5 | 032 | artist | David Allan Coe | boundary; contrast | edge | High merge and content-risk review before Page 1 use. |
| 5 | 035 | album | Golden Hour — Kacey Musgraves | contrast; album_anchor | standard |  |
| 5 | 035 | song | Slow Burn — Kacey Musgraves | contrast; bridge | standard |  |
| 5 | 035 | artist | Kacey Musgraves | contrast; bridge | standard |  |
| 7 | 045 | song | Fight for Your Right — Beastie Boys | song_first; gateway; false_nearby | core | Can over-signal frat/rock taste; keep as boundary-aware. |
| 7 | 049 | song | Crank That — Soulja Boy Tell'em | song_first; gateway; false_nearby | edge | Do not overpromote as album-world rap. |
| 7 | 049 | artist | 2 Live Crew | boundary; false_nearby; song_first | edge | Explicit-content row; likely edge rather than core. |
| 7 | 050 | song | The Humpty Dance — Digital Underground | song_first; gateway; false_nearby | standard |  |
| 7 | 050 | song | U Can't Touch This — MC Hammer | song_first; gateway; false_nearby | edge | Sample and novelty-pop handling should be flagged. |
| 7 | 050 | song | Low — Flo Rida feat. T-Pain | song_first; false_nearby; gateway | edge | Feature credit to T-Pain and radio edits matter. |
| 7 | 050 | song | Say So — Doja Cat | song_first; false_nearby; gateway | edge | Pop boundary row. |
| 7 | 050 | song | Starships — Nicki Minaj | song_first; false_nearby; gateway | edge | Do not over-signal hip-hop affinity from this row alone. |
| 7 | 050 | artist | MC Hammer | gateway; false_nearby; song_first | edge | High recognition but often a one-object pop boundary. |
| 7 | 050 | artist | Flo Rida | false_nearby; gateway; song_first | edge | Often more club-pop than hip-hop affinity. |
| 7 | 050 | song | Ice Ice Baby — Vanilla Ice | song_first; false_nearby | suppress | Use for boundary testing; likely suppress as recommendation seed. |
| 7 | 050 | artist | Vanilla Ice | false_nearby; song_first | suppress | Use carefully; likely suppress outside boundary tests. |
| 8 | 059 | artist | They Might Be Giants | contrast; song_first | standard | False-nearby risk with novelty/family context; keep as contrast row. |
| 8 | 059 | song | Ana Ng — They Might Be Giants | contrast; song_first | standard | False-nearby risk with novelty/context family. |
| 8 | 059 | album | Lincoln — They Might Be Giants | contrast; gateway | standard |  |
| 8 | 059 | song | Take the Skinheads Bowling — Camper Van Beethoven | deepening; contrast | edge |  |
| 8 | 060 | song | Pepper — Butthole Surfers | false_nearby; bridge; song_first | edge | Later alt-rock hit; keep as bridge/false-nearby, not a pure noise-rock anchor. |
| 8 | 060 | artist | Butthole Surfers | boundary; false_nearby | edge | `Pepper` is a later alt-rock hit; use as bridge/false-nearby, not a pure noise-rock anchor. |
| 9 | 061 | artist | Ghost | gateway; boundary; contrast | standard | Modern rock/pop crossover; do not use as true-metal proof alone. |
| 9 | 061 | artist | Deep Purple | boundary; bridge; false_nearby | edge | Do not let classic-rock ownership turn this into a full Family 9 anchor. |
| 9 | 063 | song | Livin' on a Prayer — Bon Jovi | gateway; song_first; false_nearby | core | Boundary song. |
| 9 | 063 | artist | Bon Jovi | gateway; boundary; false_nearby; song_first | core | Treat as glam/pop-metal hook row, not true metal proof. |
| 9 | 063 | song | Cherry Pie — Warrant | song_first; false_nearby | standard |  |
| 9 | 063 | song | The Final Countdown — Europe | song_first; false_nearby; gateway | standard | Artist survey usually not needed. |
| 9 | 063 | artist | Europe | song_first; false_nearby; gateway | standard | Artist survey usually unnecessary unless song response is unusually strong. |
| 9 | 063 | artist | Warrant | song_first; gateway; false_nearby | standard |  |
| 9 | 063 | artist | Van Halen | boundary; false_nearby; bridge | edge | Primary ownership outside Family 9; keep low-weight boundary. |
| 9 | 064 | artist | Queens of the Stone Age | gateway; bridge; boundary; false_nearby | standard | Alternative-rock ownership is strong; use as gateway/boundary. |
| 9 | 065 | song | The Beautiful People — Marilyn Manson | gateway; false_nearby | standard | Image recognition warning. |
| 9 | 065 | artist | Marilyn Manson | gateway; boundary; false_nearby | standard | Controversy/image recognition can overstate music affinity. |
| 9 | 065 | song | Hey Man Nice Shot — Filter | song_first; false_nearby | edge |  |
| 9 | 065 | artist | Filter | song_first; false_nearby; boundary | edge | Usually a boundary row, not metal ownership. |
| 9 | 065 | album | Short Bus — Filter | album_anchor; false_nearby | edge |  |
| 9 | 066 | song | Break Stuff — Limp Bizkit | gateway; false_nearby | core |  |
| 9 | 066 | album | Significant Other — Limp Bizkit | album_anchor; gateway; false_nearby | core |  |
| 9 | 066 | artist | Limp Bizkit | gateway; false_nearby; song_first | core |  |
| 9 | 066 | song | Nookie — Limp Bizkit | gateway; false_nearby | standard |  |
| 9 | 066 | song | Last Resort — Papa Roach | song_first; false_nearby | standard |  |
| 9 | 066 | artist | Papa Roach | song_first; false_nearby; gateway | standard |  |
| 9 | 066 | album | Infest — Papa Roach | album_anchor; song_first; false_nearby | standard |  |
| 9 | 066 | song | Bring Me to Life — Evanescence | song_first; boundary; false_nearby | edge |  |
| 9 | 066 | artist | Alice in Chains | boundary; bridge; false_nearby | edge | Primary ownership likely alternative/grunge family. |
| 9 | 066 | artist | Evanescence | gateway; boundary; false_nearby | edge | Song-first boundary more than metal anchor. |
| 9 | 066 | artist | Primus | boundary; false_nearby; bridge | edge | Use only as boundary. |
| 9 | 066 | artist | Incubus | boundary; false_nearby | edge | Usually suppress from true metal pages unless needed for boundary. |
| 9 | 067 | artist | Breaking Benjamin | false_nearby; gateway; boundary | edge | Often not metal enough for true-metal survey branching. |
| 9 | 067 | artist | Shinedown | false_nearby; gateway; boundary | edge | Keep low-weight; not a metal anchor. |
| 9 | 067 | artist | A Day to Remember | boundary; false_nearby; gateway | edge |  |
| 10 | 071 | song | Lightning Crashes — Live | song_first; gateway; false_nearby | standard |  |
| 10 | 071 | song | Glycerine — Bush | song_first; gateway; false_nearby | standard |  |
| 10 | 071 | album | Sixteen Stone — Bush | album_anchor; gateway; false_nearby | standard |  |
| 10 | 071 | album | Throwing Copper — Live | album_anchor; gateway; false_nearby | standard |  |
| 10 | 071 | artist | Bush | gateway; false_nearby; song_first | standard | Do not promote as alternative-center anchor above Seattle and first-wave 90s alt. |
| 10 | 071 | song | Machinehead — Bush | song_first; gateway; false_nearby | standard |  |
| 10 | 071 | song | Shine — Collective Soul | song_first; gateway; false_nearby | standard |  |
| 10 | 071 | artist | Live | gateway; false_nearby; song_first | standard | Spiritual/anthemic modern-rock identity is adjacent, not grunge center. |
| 10 | 071 | artist | Collective Soul | gateway; song_first; false_nearby | standard | Keep as standard/gateway rather than core alternative canon. |
| 10 | 071 | song | How You Remind Me — Nickelback | song_first; gateway; false_nearby | edge |  |
| 10 | 071 | song | With Arms Wide Open — Creed | song_first; gateway; false_nearby | edge |  |
| 10 | 071 | artist | Nickelback | gateway; false_nearby; song_first | edge | Strong false-nearby risk; do not let this row define the family center. |
| 10 | 071 | song | Higher — Creed | song_first; gateway; false_nearby | edge |  |
| 10 | 071 | album | Human Clay — Creed | album_anchor; gateway; false_nearby | edge |  |
| 10 | 071 | artist | Creed | gateway; false_nearby; song_first | edge | False-nearby risk for alt users; keep edge despite mass radio memory. |
| 10 | 071 | album | Silver Side Up — Nickelback | album_anchor; gateway; false_nearby | edge |  |
| 10 | 074 | artist | Alanis Morissette | boundary; gateway; false_nearby | edge | Primary ownership may be pop/persona; Family 10 keeps edge boundary value. |
| 10 | 074 | album | Jagged Little Pill — Alanis Morissette | album_anchor; boundary; false_nearby | edge |  |
| 10 | 075 | song | Popular — Nada Surf | song_first; gateway; contrast | standard |  |
| 10 | 079 | song | Get Free — The Vines | song_first; gateway; false_nearby | edge |  |
| 10 | 079 | artist | The Vines | gateway; song_first; false_nearby | edge | Keep edge; avoid inflating a short-lived hype lane. |
| 10 | 080 | artist | Editors | gateway; false_nearby | edge | Avoid duplicating Interpol's role; keep as edge gateway. |
| 11 | 085 | artist | Peaches | boundary; contrast | edge |  |
| 11 | 087 | artist | Nine Inch Nails | contrast; bridge | standard | Industrial rock belongs elsewhere as artist core; include only as electronic/industrial false-nearby warning. |
| 11 | 087 | song | Closer — Nine Inch Nails | contrast; boundary | standard | Industrial-rock false-nearby; explicit-content/context review. |
| 12 | 090 | song | I Gotta Feeling — Black Eyed Peas | gateway; song_first; false_nearby | standard |  |
| 12 | 090 | artist | Black Eyed Peas | gateway; song_first; false_nearby | standard |  |
| 12 | 090 | album | The E.N.D. — Black Eyed Peas | gateway; false_nearby | standard |  |
| 12 | 092 | song | Fight Song — Rachel Platten | song_first; false_nearby | edge |  |
| 12 | 092 | artist | Christina Perri | song_first; false_nearby | edge | Mostly a song-first boundary row. |
| 12 | 092 | artist | Rachel Platten | song_first; false_nearby | edge | Do not promote one inspirational hit into broad artist appetite. |
| 14 | 102 | album | Classics in the Key of G — Kenny G | false_nearby; boundary | standard | Classical-themed smooth-jazz object, not a classical-performance album. |
| 14 | 102 | song | Soulful Strut — Young-Holt Unlimited | false_nearby; boundary | standard | Instrumental soul-jazz/adult instrumental title may bridge Family 6. |
| 14 | 103 | album | Watermark — Enya | bridge; false_nearby | standard | New age/pop recognition should remain bridge, not classical-crossover proof by itself. |
| 14 | 103 | song | Adagio for Strings — London Philharmonic Orchestra | false_nearby; boundary | edge | Classical composition and film/trance uses need separate handling. |
| 14 | 103 | artist | Jackie Evancho | false_nearby; boundary | edge | Talent-show/classical-crossover recognition should stay boundary until user confirms appetite. |
| 16 | 109 | album | Awake — Skillet | bridge; false_nearby | edge | Hard-rock crossover row, not worship appetite by default. |
| 16 | 109 | song | Monster — Skillet | bridge; false_nearby | edge | Mainstream hard-rock recognition can be a false nearby for worship/CCM appetite. |
| 16 | 109 | artist | Skillet | bridge; false_nearby | edge | Christian-market and mainstream hard-rock identities should not be merged into worship appetite. |

### Boundary-Test Songs

| family | archetype | song | roles | survey_tier | warning |
| --- | --- | --- | --- | --- | --- |
| 9 | 063 | Livin' on a Prayer — Bon Jovi | gateway; song_first; false_nearby | core | Boundary song. |
| 9 | 063 | Sweet Child o' Mine — Guns N' Roses | gateway; boundary | core | Primary hard-rock ownership. |
| 1 | 002 | Rumble — Link Wray | anchor; boundary | core | Artist-worthy |
| 9 | 066 | In the End — Linkin Park | gateway; song_first; boundary | core |  |
| 12 | 088 | When Doves Cry — Prince | anchor; boundary | core |  |
| 12 | 091 | Royals — Lorde | anchor; boundary | core |  |
| 9 | 063 | Every Rose Has Its Thorn — Poison | song_first; gateway; boundary | core |  |
| 9 | 066 | Killing in the Name — Rage Against the Machine | gateway; bridge; boundary | core |  |
| 2 | 011 | Louie Louie — The Kingsmen | song_first; anchor; boundary | core | Song outranks artist. |
| 12 | 090 | Toxic — Britney Spears | gateway; boundary | core |  |
| 9 | 064 | No One Knows — Queens of the Stone Age | gateway; boundary | core | Alternative-rock boundary. |
| 9 | 066 | Break Stuff — Limp Bizkit | gateway; false_nearby | core |  |
| 9 | 066 | Numb — Linkin Park | gateway; boundary | core |  |
| 9 | 065 | Closer — Nine Inch Nails | gateway; boundary | core |  |
| 6 | 041 | Smooth Operator — Sade | song_first; gateway; boundary | core | Band/project identity. |
| 12 | 089 | My Heart Will Go On — Celine Dion | boundary; song_first | core | Boundary with soundtrack family. |
| 7 | 050 | Hotline Bling — Drake | song_first; gateway; boundary | core | R&B boundary row. |
| 1 | 005 | You Don't Own Me — Lesley Gore | gateway; boundary | core | Artist-worthy |
| 10 | 070 | Heart-Shaped Box — Nirvana | song_first; deepening; boundary | core |  |
| 10 | 078 | I Will Follow You into the Dark — Death Cab for Cutie | song_first; gateway; boundary | core |  |
| 12 | 092 | Thinking Out Loud — Ed Sheeran | gateway; boundary | core |  |
| 1 | 007 | Dead Man's Curve — Jan and Dean | gateway; boundary | core | Artist-worthy |
| 9 | 067 | The Summoning — Sleep Token | gateway; boundary | core |  |
| 9 | 067 | Just Pretend — Bad Omens | gateway; song_first; boundary | core |  |
| 7 | 045 | Fight for Your Right — Beastie Boys | song_first; gateway; false_nearby | core | Can over-signal frat/rock taste; keep as boundary-aware. |
| 13 | 098 | Cupid — FIFTY FIFTY | song_first; boundary | core | One-song global pop and group/legal history. |
| 9 | 061 | Black Sabbath — Black Sabbath | anchor; boundary | core | Artist/song/album title collision. |
| 1 | 001 | Bo Diddley — Bo Diddley | anchor; boundary | core | Artist-worthy |
| 1 | 002 | Train Kept A-Rollin' — Johnny Burnette and the Rock 'n Roll Trio | anchor; boundary | core | Song-first |
| 10 | 073 | Only Shallow — My Bloody Valentine | song_first; anchor; boundary | core |  |
| 7 | 047 | Fuck tha Police — N.W.A | song_first; boundary; anchor | core | Explicit title and radio unsuitability are import warnings, not reasons to rename. |
| 9 | 062 | Angel of Death — Slayer | anchor; boundary | core |  |
| 12 | 091 | Formation — Beyonce | anchor; boundary | core |  |
| 1 | 001 | Rave On — Buddy Holly | gateway; boundary | core | Artist-worthy |
| 1 | 001 | That's All Right — Elvis Presley | gateway; boundary | core | Song-first |
| 12 | 091 | Video Games — Lana Del Rey | gateway; boundary | core |  |
| 1 | 006 | I Got a Woman — Ray Charles | anchor; boundary | core | Artist-worthy |
| 10 | 069 | Teen Age Riot — Sonic Youth | song_first; anchor; boundary | core |  |
| 1 | 005 | Remember (Walking in the Sand) — The Shangri-Las | gateway; boundary | core | Artist-worthy |
| 1 | 005 | Walking in the Rain — The Ronettes | gateway; boundary | core | Artist-worthy |
| 7 | 051 | EARFQUAKE — Tyler, the Creator | song_first; gateway; boundary | core | Rap-adjacent art-pop boundary. |
| 17 | 113 | Don't Stop Believin' — Journey | anchor; song_first; false_nearby | standard |  |
| 17 | 113 | Sweet Caroline — Neil Diamond | anchor; song_first; false_nearby | standard |  |
| 17 | 113 | Livin' on a Prayer — Bon Jovi | anchor; song_first; false_nearby | standard |  |
| 17 | 113 | Mr. Brightside — The Killers | anchor; song_first; false_nearby | standard |  |
| 17 | 113 | Friends in Low Places — Garth Brooks | anchor; song_first; false_nearby | standard |  |
| 1 | 002 | Louie Louie — The Kingsmen | gateway; boundary | standard | Artist-worthy |
| 9 | 063 | Here I Go Again — Whitesnake | gateway; boundary; song_first | standard |  |
| 12 | 090 | I Gotta Feeling — Black Eyed Peas | gateway; song_first; false_nearby | standard |  |
| 1 | 004 | Teen Angel — Mark Dinning | song_first; boundary | standard | Song-first |
| 7 | 052 | Magnolia — Playboi Carti | song_first; gateway; boundary | standard |  |
| 1 | 004 | Tell Laura I Love Her — Ray Peterson | song_first; boundary | standard | Song-first |
| 10 | 080 | Mr. Brightside — The Killers | song_first; gateway; boundary | standard |  |
| 9 | 063 | Wanted Dead or Alive — Bon Jovi | gateway; boundary | standard |  |
| 7 | 051 | This Is America — Childish Gambino | song_first; boundary; bridge | standard | Do not infer broad hip-hop taste from this row alone. |
| 9 | 066 | Nookie — Limp Bizkit | gateway; false_nearby | standard |  |
| 9 | 066 | Last Resort — Papa Roach | song_first; false_nearby | standard |  |
| 6 | 040 | Y.M.C.A. — Village People | song_first; gateway; boundary | standard | Novelty risk; do not over-weight as deep disco preference. |
| 7 | 050 | WAP — Cardi B feat. Megan Thee Stallion | song_first; boundary; gateway | standard | Explicit/clean title and lyric differences must be preserved. |
| 7 | 047 | Insane in the Brain — Cypress Hill | song_first; gateway; boundary | standard | Can route to alternative/rock contexts. |
| 10 | 077 | I Write Sins Not Tragedies — Panic! at the Disco | song_first; gateway; boundary | standard |  |
| 7 | 052 | Dior — Pop Smoke | song_first; gateway; boundary | standard | Drill subfamily ownership may need later review. |
| 17 | 113 | Dancing Queen — ABBA | gateway; song_first; false_nearby | standard |  |
| 7 | 050 | The Humpty Dance — Digital Underground | song_first; gateway; false_nearby | standard |  |
| 10 | 076 | Good Riddance (Time of Your Life) — Green Day | song_first; gateway; boundary | standard |  |
| 7 | 051 | Pursuit of Happiness — Kid Cudi feat. MGMT and Ratatat | song_first; boundary; gateway | standard | Feature and remix versions require care. |
| 10 | 071 | Lightning Crashes — Live | song_first; gateway; false_nearby | standard |  |
| 18 | 120 | lofi hip hop radio — Lo-fi Girl | false_nearby; gateway | standard | Use-case/channel object, not a conventional song recording. |
| 9 | 065 | The Beautiful People — Marilyn Manson | gateway; false_nearby | standard | Image recognition warning. |
| 7 | 052 | Creepin' — Metro Boomin, The Weeknd, and 21 Savage | song_first; gateway; boundary | standard | Cover/interpolation and multi-artist credit handling required. |
| 10 | 071 | Semi-Charmed Life — Third Eye Blind | song_first; gateway; boundary | standard |  |
| 9 | 063 | Cherry Pie — Warrant | song_first; false_nearby | standard |  |
| 10 | 071 | Glycerine — Bush | song_first; gateway; false_nearby | standard |  |
| 11 | 083 | Sandstorm — Darude | song_first; boundary | standard | Meme/sports-arena context may exceed trance knowledge. |
| 9 | 063 | The Final Countdown — Europe | song_first; false_nearby; gateway | standard | Artist survey usually not needed. |
| 9 | 065 | Hurt — Nine Inch Nails | gateway; boundary | standard | Also version-sensitive because Johnny Cash cover exists. |
| 10 | 077 | Decode — Paramore | song_first; gateway; boundary | standard |  |
| 6 | 039 | Super Freak — Rick James | song_first; gateway; boundary | standard | Also pop/hip-hop sample-memory boundary. |
| 17 | 113 | Man! I Feel Like a Woman! — Shania Twain | gateway; song_first; false_nearby | standard |  |
| 2 | 012 | A Whiter Shade of Pale — Procol Harum | song_first; bridge; boundary | standard | Strong prog-family boundary. |
| 1 | 002 | I Fought the Law — The Bobby Fuller Four | boundary; song_first; deepening | standard | Song-first |
| 3 | 018 | Owner of a Lonely Heart — Yes | gateway; boundary | standard | pop-overlap warning |
| 3 | 020 | Killer Queen — Queen | gateway; boundary | standard | overlaps 016 |
| 3 | 019 | Whipping Post — The Allman Brothers Band | song_first; boundary; live_gateway | standard | live version often primary memory |
| 3 | 016 | Barracuda — Heart | gateway; boundary | standard | overlaps 017 |
| 3 | 017 | Barracuda — Heart | gateway; boundary | standard | overlaps 016 |
| 3 | 023 | Lowdown — Boz Scaggs | gateway; boundary | standard | overlaps 022 |
| 3 | 021 | Just What I Needed — The Cars | gateway; boundary | standard | new-wave overlap |
| 10 | 074 | Rebel Girl — Bikini Kill | song_first; bridge; boundary | standard |  |
| 9 | 068 | Hammer Smashed Face — Cannibal Corpse | gateway; boundary; song_first | standard |  |
| 7 | 047 | Mind Playing Tricks on Me — Geto Boys | song_first; bridge; boundary | standard |  |
| 7 | 046 | Bring the Noise — Public Enemy | song_first; bridge; boundary | standard | Anthrax collaboration version should remain separate if imported. |
| 7 | 051 | Yonkers — Tyler, the Creator | song_first; boundary; gateway | standard | Explicit/controversial content warning. |
| 8 | 055 | Institutionalized — Suicidal Tendencies | gateway; song_first; boundary | standard | Boundary with Family 9; do not over-promote into metal-only context. |
| 7 | 049 | B.O.B. — OutKast | song_first; bridge; boundary | standard | Title punctuation normalized only in slug. |
| 9 | 064 | Go With the Flow — Queens of the Stone Age | gateway; boundary | standard |  |
| 1 | 005 | Sally Go 'Round the Roses — The Jaynetts | song_first; boundary | standard | Song-first |
| 1 | 001 | That's All Right — Arthur "Big Boy" Crudup | gateway; song_first; boundary | standard | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 001 | Shake, Rattle and Roll — Big Joe Turner | gateway; song_first; boundary | standard | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 001 | Hound Dog — Big Mama Thornton | gateway; song_first; boundary | standard | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 006 | I Pity the Fool — Bobby "Blue" Bland | gateway; song_first; boundary | standard | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 006 | Mercy, Mercy — Don Covay | gateway; song_first; boundary | standard | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 006 | The Twist — Hank Ballard & The Midnighters | gateway; song_first; boundary | standard | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 004 | Dreamin' — Johnny Burnette | gateway; song_first; boundary | standard | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 004 | Chances Are — Johnny Mathis | gateway; song_first; boundary | standard | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 001 | Bony Moronie — Larry Williams | gateway; song_first; boundary | standard | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 001 | Caldonia — Louis Jordan | gateway; song_first; boundary | standard | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 001 | Saturday Night Fish Fry — Louis Jordan | gateway; song_first; boundary | standard | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 005 | Oh No Not My Baby — Maxine Brown | gateway; song_first; boundary | standard | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 004 | Love Letters in the Sand — Pat Boone | gateway; song_first; boundary | standard | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 003 | Denise — Randy & The Rainbows | gateway; song_first; boundary | standard | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 003 | Crying in the Chapel — The Orioles | gateway; song_first; boundary | standard | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 007 | Comanche — The Revels | gateway; song_first; boundary | standard | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 7 | 051 | The Seed (2.0) — The Roots feat. Cody Chesnutt | song_first; boundary; gateway | standard |  |
| 1 | 007 | Harlem Nocturne — The Viscounts | gateway; song_first; boundary | standard | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 001 | Good Rockin' Tonight — Wynonie Harris | gateway; song_first; boundary | standard | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 10 | 071 | Machinehead — Bush | song_first; gateway; false_nearby | standard |  |
| 10 | 071 | Shine — Collective Soul | song_first; gateway; false_nearby | standard |  |
| 10 | 075 | Popular — Nada Surf | song_first; gateway; contrast | standard |  |
| 7 | 052 | Sky — Playboi Carti | song_first; boundary | standard |  |

### Dead-End Checks

The canonical graph uses `false_nearby`, `contrast`, and `boundary` roles, not final Atlas `dead_end` state. Dead Ends are user-specific Atlas role assignments and must be promoted only from Signals.

## Random Stratified Samples

Deterministic sample seed: `20260520`. Samples are across families and tiers, not exhaustive QA.

### 25 Artists

| id | display_name | object_type | families | memberships | roles | survey eligibility | recognition | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| dion | Dion | artist | 1 | 001 | bridge; gateway; song_first | core | mass |  |
| gerry-and-the-pacemakers | Gerry and the Pacemakers | artist | 2 | 008 | gateway; song_first | standard | high |  |
| artist-carpenters | Carpenters | artist | 3 | 022 | anchor; bridge; gateway | standard | mass |  |
| f4-028-artist-old-97-s | Old 97's | artist | 4 | 028 | artist_anchor; gateway | core | medium |  |
| kacey-musgraves | Kacey Musgraves | artist | 5 | 035 | bridge; contrast | standard | high |  |
| sam-and-dave | Sam & Dave | artist | 6 | 038 | anchor; gateway; song_first | core | high |  |
| childish-gambino | Childish Gambino | artist | 7 | 051 | boundary; bridge | standard | high |  |
| quicksand | Quicksand | artist | 8 | 060 | bridge; gateway | standard | medium |  |
| rainbow | Rainbow | artist | 9 | 061 | boundary; bridge; gateway | standard | high |  |
| matthew-sweet | Matthew Sweet | artist | 10 | 075 | artist_anchor; bridge | standard | medium |  |
| the-rapture | The Rapture | artist | 11 | 085 | gateway | standard | medium |  |
| miley-cyrus | Miley Cyrus | artist | 12 | 091 | bridge; gateway; song_first | standard | high |  |
| enrique-iglesias | Enrique Iglesias | artist | 13 | 094 | bridge; song_first | core | mass |  |
| chuck-mangione | Chuck Mangione | artist | 14 | 102 | gateway; song_first | standard | high |  |
| rodgers-and-hammerstein | Rodgers and Hammerstein | artist | 15 | 104 | anchor; artist_anchor | core | mass |  |
| chris-tomlin | Chris Tomlin | artist | 16 | 110 | anchor; artist_anchor | core | mass |  |
| spike-jones | Spike Jones | artist | 17 | 111 | boundary; deepening; song_first | edge | medium |  |
| a-g-cook | A. G. Cook | artist | 18 | 119 | deepening | standard | medium |  |
| f4-027-artist-john-prine | John Prine | artist | 4 | 027 | anchor; artist_anchor | core | high |  |
| a-day-to-remember | A Day to Remember | artist | 9 | 067 | boundary; false_nearby; gateway | edge | high |  |
| sister-rosetta-tharpe | Sister Rosetta Tharpe | artist | 1; 16 | 001; 108 | anchor; artist_anchor; bridge; deepening; gateway | core | high | multi-membership |
| cinderella | Cinderella | artist | 9 | 063 | boundary; gateway | standard | high |  |
| f4-026-artist-joan-baez | Joan Baez | artist | 4 | 026 | anchor; artist_anchor | core | high |  |
| the-atlantics | The Atlantics | artist | 1 | 007 | deepening; song_first | edge | medium |  |
| gang-starr | Gang Starr | artist | 7 | 046 | artist_anchor; bridge; deepening | standard | high |  |

### 25 Albums

| id | display_name | object_type | families | memberships | roles | survey eligibility | recognition | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| the-ronettes-presenting-the-fabulous-ronettes-featuring-veronica | Presenting the Fabulous Ronettes Featuring Veronica | album | 1 | 005 | album_anchor | core | mass |  |
| the-velvet-underground-and-nico-the-velvet-underground-and-nico | The Velvet Underground & Nico | album | 2 | 015 | album_anchor; boundary; bridge | core | high |  |
| album-2112-1976 | 2112 | album | 3 | 018 | album_anchor; gateway | standard | high |  |
| f4-027-album-time-the-revelator-gillian-welch | Time (The Revelator) | album | 4 | 027 | album_anchor; anchor; deepening | core | medium |  |
| various-artists-wanted-the-outlaws | Wanted! The Outlaws | album | 5 | 032 | anchor; compilation_gateway | standard | high |  |
| jackson-5-diana-ross-presents-the-jackson-5 | Diana Ross Presents The Jackson 5 | album | 6 | 037 | album_anchor; gateway | standard | high |  |
| run-dmc-run-dmc | Run-D.M.C. | album | 7 | 045 | album_anchor; anchor | core | high |  |
| the-church-starfish | Starfish | album | 8 | 056 | bridge; gateway | standard | medium |  |
| nine-inch-nails-broken | Broken | album | 9 | 065 | album_anchor; bridge | standard | high |  |
| built-to-spill-perfect-from-now-on | Perfect from Now On | album | 10 | 072 | album_anchor; bridge | standard | medium |  |
| portishead-dummy | Dummy | album | 11 | 084 | album_anchor | core | high |  |
| christina-aguilera-christina-aguilera | Christina Aguilera | album | 12 | 089 | album_anchor; gateway | core | high |  |
| fuerza-regida-pa-las-baby-s-y-belikeada | Pa Las Baby's y Belikeada | album | 13 | 095 | gateway | standard | high |  |
| andrea-bocelli-romanza | Romanza | album | 14 | 103 | album_anchor | core | mass |  |
| various-artists-the-bodyguard | The Bodyguard | album | 15 | 106 | album_anchor | core | mass |  |
| mercyme-almost-there | Almost There | album | 16 | 109 | gateway; song_first | core | mass |  |
| the-killers-direct-hits | Direct Hits | album | 17 | 113 | compilation_gateway; false_nearby | edge | high |  |
| arctic-monkeys-am | AM | album | 18 | 117 | bridge | core | mass |  |
| inner-city-paradise | Paradise | album | 11 | 082 | gateway | standard | high |  |
| janet-jackson-rhythm-nation-1814 | Rhythm Nation 1814 | album | 6 | 042 | album_anchor; anchor; bridge | core | mass |  |
| chic-cest-chic | C'est Chic | album | 6 | 040 | album_anchor; gateway | core | high |  |
| marty-robbins-gunfighter-ballads-and-trail-songs | Gunfighter Ballads and Trail Songs | album | 5 | 031 | album_anchor; gateway | standard | high |  |
| fatboy-slim-you-ve-come-a-long-way-baby | You've Come a Long Way, Baby | album | 11 | 083 | gateway | standard | high |  |
| the-stooges-the-stooges | The Stooges | album | 2 | 015 | album_anchor; boundary; bridge | standard | high |  |
| sophie-oil-of-every-pearl-s-un-insides | Oil of Every Pearl's Un-Insides | album | 11; 18 | 087; 119 | album_anchor; bridge | core | high | multi-membership |

### 50 Song Recordings

| id | display_name | object_type | families | memberships | roles | survey eligibility | recognition | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| the-regents-barbara-ann | Barbara Ann | song | 1 | 003 | bridge; gateway | core | mass | composition barbara-ann |
| the-jimi-hendrix-experience-purple-haze | Purple Haze | song | 2 | 014 | anchor; bridge; song_first | core | mass | composition purple-haze |
| song-old-time-rock-and-roll-1978 | Old Time Rock and Roll | song | 3 | 016 | gateway; song_first | standard | mass | composition old-time-rock-and-roll |
| f4-028-song-timebomb-old-97-s | Timebomb | song | 4 | 028 | gateway; song_first | core | medium | composition timebomb |
| buck-owens-act-naturally | Act Naturally | song | 5 | 031 | bridge; song_first | standard | high | composition act-naturally |
| anita-baker-sweet-love | Sweet Love | song | 6 | 041 | anchor; gateway; song_first | core | mass | composition sweet-love |
| missy-elliott-work-it | Work It | song | 7 | 050 | anchor; gateway; song_first | core | mass | composition work-it |
| bad-brains-banned-in-d-c | Banned in D.C. | song | 8 | 055 | gateway | standard | medium | composition banned-in-d-c |
| megadeth-peace-sells | Peace Sells | song | 9 | 062 | gateway | core | high | composition peace-sells |
| modest-mouse-dashboard | Dashboard | song | 10 | 078 | gateway; song_first | standard | high | composition dashboard |
| carl-craig-at-les | At Les | song | 11 | 082 | deepening | edge | medium | composition at-les |
| lana-del-rey-video-games | Video Games | song | 12 | 091 | boundary; gateway | core | high | composition video-games |
| fifty-fifty-cupid | Cupid | song | 13 | 098 | boundary; song_first | core | mass | composition cupid |
| john-coltrane-my-favorite-things | My Favorite Things | song | 14 | 101 | anchor | core | high | composition my-favorite-things |
| jodi-benson-part-of-your-world | Part of Your World | song | 15 | 105 | gateway; song_first | core | mass | composition part-of-your-world |
| elevation-worship-graves-into-gardens | Graves Into Gardens | song | 16 | 110 | gateway | standard | high | composition graves-into-gardens |
| kool-and-the-gang-celebration | Celebration | song | 17 | 113 | false_nearby; gateway; song_first | edge | mass | composition celebration |
| maneskin-beggin | Beggin' | song | 18 | 118 | bridge; song_first | standard | mass | composition beggin |
| chief-keef-feat-lil-reese-i-dont-like | I Don't Like | song | 7 | 052 | anchor; bridge; song_first | standard | high | composition i-don-t-like |
| bill-haley-and-his-comets-shake-rattle-and-roll | Shake, Rattle and Roll | song | 1 | 001 | gateway | core | high | composition shake-rattle-and-roll |
| big-tymers-still-fly | Still Fly | song | 7 | 049 | gateway; song_first | standard | high | composition still-fly |
| liz-phair-supernova | Supernova | song | 10 | 074 | gateway; song_first | standard | high | composition supernova |
| phil-wickham-house-of-the-lord | House of the Lord | song | 16 | 110 | gateway | standard | high | composition house-of-the-lord |
| simon-and-garfunkel-mrs-robinson | Mrs. Robinson | song | 2 | 010 | bridge; gateway; song_first | core | mass | composition mrs-robinson |
| arthur-big-boy-crudup-thats-all-right | That's All Right | song | 1 | 001 | boundary; gateway; song_first | standard | high | composition that-s-all-right |
| the-cure-pictures-of-you | Pictures of You | song | 8 | 056 | deepening | standard | high | composition pictures-of-you |
| the-dixie-cups-chapel-of-love | Chapel of Love | song | 1 | 005 | gateway | core | mass | composition chapel-of-love |
| duran-duran-hungry-like-the-wolf | Hungry Like the Wolf | song | 8 | 057 | gateway; song_first | core | mass | composition hungry-like-the-wolf |
| link-wray-rumble | Rumble | song | 1 | 002; 007 | anchor; boundary | core | mass | multi-membership |
| f4-024-song-big-yellow-taxi-joni-mitchell | Big Yellow Taxi | song | 4 | 024 | gateway; song_first | core | mass | composition big-yellow-taxi |
| korn-freak-on-a-leash | Freak on a Leash | song | 9 | 066 | anchor; gateway | core | mass | composition freak-on-a-leash |
| judy-garland-have-yourself-a-merry-little-christmas | Have Yourself a Merry Little Christmas | song | 17 | 112 | gateway; song_first | standard | mass | composition have-yourself-a-merry-little-christmas |
| en-vogue-hold-on | Hold On | song | 6 | 042 | gateway; song_first | standard | mass | composition hold-on |
| f4-029-song-angel-sarah-mclachlan | Angel | song | 4 | 029 | gateway; song_first | standard | mass | composition angel |
| song-rock-and-roll-all-nite-1975 | Rock and Roll All Nite | song | 3 | 017 | gateway | edge | high | composition rock-and-roll-all-nite |
| darius-rucker-wagon-wheel | Wagon Wheel | song | 5 | 035 | bridge; song_first | standard | mass | composition wagon-wheel |
| jill-scott-a-long-walk | A Long Walk | song | 6 | 043 | gateway; song_first | standard | high | composition a-long-walk |
| bush-glycerine | Glycerine | song | 10 | 071 | false_nearby; gateway; song_first | standard | mass | composition glycerine |
| isaac-hayes-theme-from-shaft | Theme from Shaft | song | 6 | 038 | bridge; gateway; song_first | standard | high | composition theme-from-shaft |
| the-viscounts-harlem-nocturne | Harlem Nocturne | song | 1 | 007 | boundary; gateway; song_first | standard | high | composition harlem-nocturne |
| sam-cooke-and-the-soul-stirrers-jesus-gave-me-water | Jesus Gave Me Water | song | 16 | 108 | bridge | standard | medium | composition jesus-gave-me-water |
| nightcrawlers-push-the-feeling-on | Push the Feeling On | song | 11 | 081 | gateway; song_first | standard | high | composition push-the-feeling-on |
| mayhem-freezing-moon | Freezing Moon | song | 9 | 068 | boundary; gateway | standard | cult | composition freezing-moon |
| kendrick-lamar-swimming-pools-drank | Swimming Pools (Drank) | song | 7 | 052 | bridge; gateway; song_first | core | mass | composition swimming-pools-drank |
| bring-me-the-horizon-can-you-feel-my-heart | Can You Feel My Heart | song | 9; 18 | 067; 118 | anchor; gateway; song_first | core | mass | multi-membership |
| aretha-franklin-amazing-grace | Amazing Grace | song | 16 | 108 | gateway | core | high | composition amazing-grace |
| judas-priest-you-ve-got-another-thing-comin | You've Got Another Thing Comin' | song | 9 | 061 | anchor; gateway | core | mass | composition you-ve-got-another-thing-comin |
| cody-johnson-til-you-can-t | 'Til You Can't | song | 5 | 036 | gateway | standard | high | composition til-you-can-t |
| death-grips-get-got | Get Got | song | 7 | 051 | boundary; deepening; song_first | edge | cult | composition get-got |
| f4-027-song-our-town-iris-dement | Our Town | song | 4 | 027 | gateway; song_first | standard | medium | composition our-town |

## Known TODO / Human Review Queue

### Rows Codex Is Not Confident About

This is represented by consolidation warnings, import warnings, alias/merge QA, and composition/title review queues. The table below samples warning-bearing rows with direct object IDs.

| family | archetype | object_type | object_id | object | warning |
| --- | --- | --- | --- | --- | --- |
| 1 | 001 | artist | gene-vincent | Gene Vincent | Early Blue Caps recordings may need performer-credit alias `gene-vincent-and-his-blue-caps`. |
| 1 | 001 | artist | arthur-big-boy-crudup | Arthur "Big Boy" Crudup | Better in source-code layer than normal survey |
| 1 | 001 | artist | big-joe-turner | Big Joe Turner | Also 006; distinguish from Bill Haley cover |
| 1 | 001 | artist | big-mama-thornton | Big Mama Thornton | Song recognition mostly via Elvis; keep source version distinct |
| 1 | 001 | artist | huey-piano-smith-and-the-clowns | Huey "Piano" Smith & The Clowns | Also 006 and dance-party oldies |
| 1 | 001 | artist | jackie-brenston-and-his-delta-cats | Jackie Brenston and His Delta Cats | Merge carefully with Ike Turner/Kings of Rhythm |
| 1 | 001 | artist | larry-williams | Larry Williams | Also 002 edge |
| 1 | 001 | artist | louis-jordan | Louis Jordan | Also jump-blues/R&B roots; not core 1955+ oldies |
| 1 | 001 | artist | sister-rosetta-tharpe | Sister Rosetta Tharpe | Also 006 roots; not Page 1 for normal users |
| 1 | 001 | artist | smiley-lewis | Smiley Lewis | Also 006/New Orleans lane |
| 1 | 001 | artist | wynonie-harris | Wynonie Harris | Mostly roots/depth, not mass survey |
| 1 | 002 | artist | gene-vincent | Gene Vincent | Early Blue Caps recordings may need performer-credit alias `gene-vincent-and-his-blue-caps`. |
| 1 | 002 | artist | the-wailers | The Wailers | Disambiguate Pacific Northwest Wailers from Bob Marley and the Wailers; canonical import may prefer `the-wailers-us`. |
| 1 | 002 | artist | johnny-carroll | Johnny Carroll | Specialist |
| 1 | 002 | artist | mac-curtis | Mac Curtis | Specialist |
| 1 | 002 | artist | ray-smith | Ray Smith | Not Page 1 |
| 1 | 002 | artist | ronnie-self | Ronnie Self | Deep but high Page 3 value |
| 1 | 002 | artist | the-collins-kids | The Collins Kids | More depth than normal survey |
| 1 | 002 | artist | the-phantom | The Phantom | Page 3 only |
| 1 | 002 | artist | the-rock-a-teens | The Rock-A-Teens | Song-survey-first |
| 1 | 002 | artist | warren-smith | Warren Smith | Artist recognition low; song/depth only |
| 1 | 003 | artist | randy-and-the-rainbows | Randy & The Rainbows | Song-survey-first |
| 1 | 003 | artist | the-bobbettes | The Bobbettes | Also 005 |
| 1 | 003 | artist | the-capris | The Capris | Song-survey-first |
| 1 | 003 | artist | the-channels | The Channels | Song-survey-first |
| 1 | 003 | artist | the-chantels | The Chantels | Also 005 |
| 1 | 003 | artist | the-dubs | The Dubs | Depth only |
| 1 | 003 | artist | the-harptones | The Harptones | Mostly song-first |
| 1 | 003 | artist | the-jive-five | The Jive Five | Song > artist |
| 1 | 003 | artist | the-mello-kings | The Mello-Kings | Song-survey-first |
| 1 | 003 | artist | the-mystics | The Mystics | Song-first |
| 1 | 003 | artist | the-orioles | The Orioles | Early precursor, not mass artist |
| 1 | 003 | artist | the-ravens | The Ravens | Specialist/depth |
| 1 | 004 | artist | jimmie-rodgers-pop | Jimmie Rodgers | Use suffix to avoid country Jimmie Rodgers merge |
| 1 | 004 | artist | jimmy-darren | Jimmy Darren | Also 007 image boundary |
| 1 | 004 | artist | johnny-burnette-solo | Johnny Burnette | Do not merge with Rock and Roll Trio without alias handling |
| 1 | 004 | artist | johnny-mathis | Johnny Mathis | More adult-pop than teen-idol |
| 1 | 004 | artist | johnny-preston | Johnny Preston | Song-survey-only |
| 1 | 004 | artist | kathy-young-and-the-innocents | Kathy Young & The Innocents | Song-survey-only |
| 1 | 004 | artist | little-peggy-march | Little Peggy March | Also 005 pop-craft edge |
| 1 | 004 | artist | pat-boone | Pat Boone | Useful but often dead-end check |
| 1 | 004 | artist | robin-luke | Robin Luke | Page 3 |
| 1 | 005 | artist | barbara-lewis | Barbara Lewis | Also 006 |
| 1 | 005 | artist | claudine-clark | Claudine Clark | Song-survey-only |
| 1 | 005 | artist | dee-dee-sharp | Dee Dee Sharp | Also 004/006 dance-pop edge |
| 1 | 005 | artist | maxine-brown | Maxine Brown | Also 006 |
| 1 | 005 | artist | the-bobbettes | The Bobbettes | Also 003 |
| 1 | 005 | artist | the-chantels | The Chantels | Also 003 |
| 1 | 005 | artist | the-ikettes | The Ikettes | Also 006 |
| 1 | 005 | artist | the-raindrops | The Raindrops | Also songwriter ecosystem |
| 1 | 005 | artist | the-velvelettes | The Velvelettes | Also 006/Motown |
| 1 | 006 | artist | arthur-alexander | Arthur Alexander | Also later source-code |
| 1 | 006 | artist | bobby-blue-bland | Bobby "Blue" Bland | Also blues/soul family |
| 1 | 006 | artist | clarence-frogman-henry | Clarence "Frogman" Henry | Song > artist |
| 1 | 006 | artist | don-covay | Don Covay | Later soul/R&B overlap |
| 1 | 006 | artist | doris-troy | Doris Troy | Song-survey-first |
| 1 | 006 | artist | ernie-k-doe | Ernie K-Doe | Song-survey-first |
| 1 | 006 | artist | garnet-mimms | Garnet Mimms | Strong 006/next-family bridge |
| 1 | 006 | artist | hank-ballard-and-the-midnighters | Hank Ballard & The Midnighters | Also 001/003/004 dance-craze overlap |
| 1 | 006 | artist | ike-and-tina-turner | Ike & Tina Turner | Later soul/rock overlap |
| 1 | 006 | artist | irma-thomas | Irma Thomas | Also New Orleans lane |
| 1 | 006 | artist | james-brown-and-the-famous-flames | James Brown & The Famous Flames | Later funk/soul family overlap |
| 1 | 006 | artist | otis-redding | Otis Redding | Later family should carry primary weight |
| 1 | 006 | artist | ruth-brown | Ruth Brown | Also 001 roots |
| 1 | 006 | artist | the-contours | The Contours | Artist survey usually not needed |
| 1 | 007 | artist | johnny-and-the-hurricanes | Johnny and the Hurricanes | Also 001 instrumental pop |
| 1 | 007 | artist | santo-and-johnny | Santo & Johnny | Also 004/oldies ache |
| 1 | 007 | artist | the-atlantics | The Atlantics | Regional/non-U.S. surf |
| 1 | 007 | artist | the-centurions | The Centurions | Mostly soundtrack/cult |
| 1 | 007 | artist | the-frantics | The Frantics | Also 002/garage bridge |
| 1 | 007 | artist | the-gamblers | The Gamblers | Specialist |
| 1 | 007 | artist | the-revels | The Revels | Page 3/soundtrack utility |
| 1 | 007 | artist | the-rivieras | The Rivieras | Also 002/garage edge |
| 1 | 007 | artist | the-routers | The Routers | Song-survey-only |
| 1 | 007 | artist | the-tornados | The Tornados | UK/instrumental overlap |
| 1 | 001 | album | chuck-berry-after-school-session | After School Session — Chuck Berry | True album |
| 1 | 001 | album | bo-diddley-bo-diddley | Bo Diddley — Bo Diddley | True album |
| 1 | 001 | album | buddy-holly-buddy-holly | Buddy Holly — Buddy Holly | True album |
| 1 | 001 | album | carl-perkins-dance-album-of-carl-perkins | Dance Album of Carl Perkins — Carl Perkins | True album |
| 1 | 001 | album | elvis-presley-elvis | Elvis — Elvis Presley | True album |
| 1 | 001 | album | elvis-presley-elvis-presley | Elvis Presley — Elvis Presley | True album |
| 1 | 001 | album | bo-diddley-go-bo-diddley | Go Bo Diddley — Bo Diddley | True album |
| 1 | 001 | album | little-richard-heres-little-richard | Here's Little Richard — Little Richard | True album |
| 1 | 001 | album | jerry-lee-lewis-jerry-lees-greatest | Jerry Lee's Greatest! — Jerry Lee Lewis | Greatest-hits style LP |
| 1 | 001 | album | johnny-cash-with-his-hot-and-blue-guitar | Johnny Cash with His Hot and Blue Guitar! — Johnny Cash | Album exception |
| 1 | 001 | album | ritchie-valens-ritchie-valens | Ritchie Valens — Ritchie Valens | Album exception |
| 1 | 001 | album | bill-haley-and-his-comets-rock-around-the-clock | Rock Around the Clock — Bill Haley & His Comets | Soundtrack-linked LP |
| 1 | 001 | album | buddy-holly-and-the-crickets-the-chirping-crickets | The "Chirping" Crickets — Buddy Holly and the Crickets | True album |
| 1 | 001 | album | chuck-berry-the-great-twenty-eight | The Great Twenty-Eight — Chuck Berry | Compilation/gateway |
| 1 | 001 | album | elvis-presley-the-sun-sessions | The Sun Sessions — Elvis Presley | Compilation/gateway |
| 1 | 001 | album | fats-domino-this-is-fats-domino | This Is Fats Domino! — Fats Domino | True album |
| 1 | 001 | album | various-artists-atlantic-rhythm-and-blues-1947-1974 | Atlantic Rhythm and Blues 1947-1974 — Various Artists | Also 006 |
| 1 | 001 | album | big-joe-turner-boss-of-the-blues | Boss of the Blues — Big Joe Turner | Also 006 |
| 1 | 001 | album | sister-rosetta-tharpe-gospel-train | Gospel Train — Sister Rosetta Tharpe | Artist is source-code, not normal Page 1 |
| 1 | 001 | album | louis-jordan-let-the-good-times-roll | Let the Good Times Roll — Louis Jordan | Compilation > original album |
| 1 | 001 | album | various-artists-the-specialty-story | The Specialty Story — Various Artists | Also 006 |
| 1 | 002 | album | gene-vincent-bluejean-bop | Bluejean Bop! — Gene Vincent | True album |
| 1 | 002 | album | bo-diddley-bo-diddley | Bo Diddley — Bo Diddley | Album exception |
| 1 | 002 | album | carl-perkins-dance-album-of-carl-perkins | Dance Album of Carl Perkins — Carl Perkins | True album |
| 1 | 002 | album | eddie-cochran-sings-to-you | Eddie Cochran Sings to You — Eddie Cochran | True album |
| 1 | 002 | album | gene-vincent-and-his-blue-caps-gene-vincent-and-his-blue-caps | Gene Vincent and His Blue Caps — Gene Vincent | True album |
| 1 | 002 | album | duane-eddy-have-twangy-guitar-will-travel | Have "Twangy" Guitar Will Travel — Duane Eddy | True album |
| 1 | 002 | album | the-sonics-here-are-the-sonics | Here Are The Sonics — The Sonics | Boundary LP |
| 1 | 002 | album | johnny-burnette-and-the-rock-n-roll-trio-johnny-burnette-and-the-rock-n-roll-trio | Johnny Burnette and the Rock 'n Roll Trio — Johnny Burnette and the Rock 'n Roll Trio | True album |
| 1 | 002 | album | johnny-cash-with-his-hot-and-blue-guitar | Johnny Cash with His Hot and Blue Guitar! — Johnny Cash | Album exception |
| 1 | 002 | album | dick-dale-and-his-del-tones-king-of-the-surf-guitar | King of the Surf Guitar — Dick Dale and His Del-Tones | Album exception |
| 1 | 002 | album | link-wray-and-the-wraymen-link-wray-and-the-wraymen | Link Wray & the Wraymen — Link Wray | True album |
| 1 | 002 | album | johnny-cash-the-fabulous-johnny-cash | The Fabulous Johnny Cash — Johnny Cash | Album exception |
| 1 | 002 | album | the-collins-kids-hop-skip-and-jump | Hop, Skip and Jump — The Collins Kids | Depth only |
| 1 | 002 | album | ronnie-self-mr-frantic-is-boppin-the-blues | Mr. Frantic Is Boppin' the Blues — Ronnie Self | Specialist only |
| 1 | 002 | album | the-rock-a-teens-woo-hoo | The Rock-A-Teens: Woo-Hoo — The Rock-A-Teens | Song-first |
| 1 | 002 | album | various-artists-the-sun-rockabilly-years | The Sun Rockabilly Years — Various Artists | Sun comp naming needs canonical selection |
| 1 | 003 | album | the-marcels-blue-moon | Blue Moon — The Marcels | Gateway |
| 1 | 003 | album | the-platters-encore-of-golden-hits | Encore of Golden Hits — The Platters | Gateway |
| 1 | 003 | album | the-flamingos-flamingo-serenade | Flamingo Serenade — The Flamingos | True album |
| 1 | 003 | album | the-five-satins-golden-hits | Golden Hits — The Five Satins | Gateway |
| 1 | 003 | album | dion-and-the-belmonts-presenting-dion-and-the-belmonts | Presenting Dion and the Belmonts — Dion and the Belmonts | True album |
| 1 | 003 | album | the-drifters-save-the-last-dance-for-me | Save the Last Dance for Me — The Drifters | True album |
| 1 | 003 | album | the-crests-the-best-of-the-crests | The Best of the Crests — The Crests | Gateway |
| 1 | 003 | album | the-drifters-the-drifters-golden-hits | The Drifters' Golden Hits — The Drifters | Gateway |

### Missing Release Years

| family | archetype | object_type | object_id | object | warning |
| --- | --- | --- | --- | --- | --- |
| 4 | 026 | song | f4-026-song-we-shall-overcome-pete-seeger-et-al-traditional | We Shall Overcome — Pete Seeger et al. / traditional | Traditional/movement attribution; do not assign single owner without source. |
| 4 | 026 | song | f4-026-song-house-of-the-rising-sun-traditional-revival-circuit-object | House of the Rising Sun — Traditional / revival circuit object | Artist assignment unstable; Animals version is separate. |

### Uncertain Canonical Album Status

| family | archetype | album_id | album | warning |
| --- | --- | --- | --- | --- |
| 1 | 001 | bill-haley-and-his-comets-rock-around-the-clock | Rock Around the Clock — Bill Haley & His Comets | Soundtrack-linked LP |
| 1 | 001 | sister-rosetta-tharpe-gospel-train | Gospel Train — Sister Rosetta Tharpe | Artist is source-code, not normal Page 1 |
| 1 | 001 | louis-jordan-let-the-good-times-roll | Let the Good Times Roll — Louis Jordan | Compilation > original album |
| 1 | 005 | phil-spector-various-artists-back-to-mono-1958-1969 | Back to Mono (1958-1969) — Phil Spector / Various Artists | Artist credit normalization required |
| 1 | 007 | various-artists-ride-the-wild-surf | Ride the Wild Surf — Various Artists | Soundtrack |
| 2 | 010 | the-byrds-mr-tambourine-man | Mr. Tambourine Man — The Byrds | Do not merge album with song row or Dylan composition. |
| 2 | 013 | nuggets-come-to-the-sunshine | Nuggets: Come to the Sunshine — Various Artists | Later compilation; do not treat as original 1960s release. |
| 2 | 014 | the-jimi-hendrix-experience-electric-ladyland | Electric Ladyland — The Jimi Hendrix Experience | Keep Experience-era credit. |
| 2 | 014 | cream-wheels-of-fire | Wheels of Fire — Cream | Hybrid studio/live double album; object type set to live_album because source emphasized jam bridge. |
| 2 | 015 | the-velvet-underground-and-nico-the-velvet-underground-and-nico | The Velvet Underground & Nico — The Velvet Underground & Nico | Album artist credit differs from added artist entity. |
| 2 | 015 | mc5-kick-out-the-jams | Kick Out the Jams — MC5 | Live album; do not normalize as studio_album. |
| 2 | 015 | the-mothers-of-invention-freak-out | Freak Out! — The Mothers of Invention | Keep Mothers credit separate from Frank Zappa solo. |
| 2 | 015 | the-fugs-the-fugs-first-album | The Fugs First Album — The Fugs | Title/version variance needs import check. |
| 3 | 016 | album-frampton-comes-alive-1976 | Frampton Comes Alive! — Peter Frampton | live-object dominance |
| 3 | 019 | album-at-fillmore-east-1971 | At Fillmore East — The Allman Brothers Band | live bias vs studio objects |
| 3 | 019 | album-waiting-for-columbus-1978 | Waiting for Columbus — Little Feat | live-object dominance |
| 3 | 021 | album-cheap-trick-at-budokan-1978 | Cheap Trick at Budokan — Cheap Trick | live-object dominance |
| 3 | 023 | album-nightwatch-1978 | Nightwatch — Kenny Loggins | soundtrack/pop-family overlap |
| 4 | 026 | f4-026-album-joan-baez-joan-baez | Joan Baez — Joan Baez | Traditional-focused. |
| 4 | 026 | f4-026-album-if-i-had-a-hammer-peter-paul-and-mary | If I Had a Hammer — Peter, Paul and Mary | Source album-object needs verification; title is better known as a song/single. |
| 4 | 027 | f4-027-album-other-voices-other-rooms-nanci-griffith | Other Voices, Other Rooms — Nanci Griffith | Tribute/cover framing. |
| 4 | 029 | f4-029-album-white-ladder-david-gray | White Ladder — David Gray | US breakthrough came later than original release. |
| 4 | 026 | f4-026-album-peter-paul-and-mary-peter-paul-and-mary | Peter, Paul and Mary — Peter, Paul and Mary | Added to clarify source album-title ambiguity. |
| 4 | 026 | f4-026-album-in-concert-joan-baez | In Concert — Joan Baez | Live album; check canonical title if imported. |
| 4 | 028 | f4-028-album-mermaid-avenue-billy-bragg-and-wilco | Mermaid Avenue — Billy Bragg and Wilco | Collaboration object; do not merge with Wilco-only catalog. |
| 5 | 031 | kitty-wells-the-queen-of-country-music | The Queen of Country Music — Kitty Wells | Compilation gateway; verify exact anthology/version before import lock. |
| 5 | 032 | jerry-jeff-walker-viva-terlingua | Viva Terlingua — Jerry Jeff Walker | Live-recording specificity matters. |
| 5 | 033 | lady-a-need-you-now | Need You Now — Lady A | Band-name alias review required. |
| 5 | 035 | darius-rucker-true-believers | True Believers — Darius Rucker | Contains a major cover gateway; keep separate from Old Crow recording. |
| 6 | 037 | smokey-robinson-and-the-miracles-going-to-a-go-go | Going to a Go-Go — Smokey Robinson & The Miracles | Group credit distinct from Smokey solo. |
| 6 | 038 | isaac-hayes-hot-buttered-soul | Hot Buttered Soul — Isaac Hayes | Long-form cover versions should not merge with original recordings. |
| 6 | 039 | james-brown-live-at-the-apollo | Live at the Apollo — James Brown | Live object, not a studio best-of. |
| 6 | 039 | james-brown-sex-machine | Sex Machine — James Brown | Hybrid live/studio release; object type set by live gateway function. |
| 6 | 039 | funkadelic-maggot-brain | Maggot Brain — Funkadelic | Artist credit is Funkadelic, while artist umbrella row is Parliament/Funkadelic. |
| 6 | 039 | parliament-mothership-connection | Mothership Connection — Parliament | Artist credit is Parliament, not full umbrella row. |
| 6 | 039 | curtis-mayfield-super-fly | Super Fly — Curtis Mayfield | Soundtrack object. |
| 6 | 039 | earth-wind-and-fire-thats-the-way-of-the-world | That's the Way of the World — Earth, Wind & Fire | Film soundtrack context; commonly treated as core EWF album. |
| 6 | 040 | various-artists-saturday-night-fever | Saturday Night Fever — Various Artists | Compilation/soundtrack; do not assign all tracks to Bee Gees only. |
| 6 | 044 | brent-faiyaz-fuck-the-world | Fuck the World — Brent Faiyaz | Explicit title and EP type should be reviewed for UI display. |
| 7 | 045 | grandmaster-flash-and-the-furious-five-the-message | The Message — Grandmaster Flash and the Furious Five | Artist credit varies across Grandmaster Flash, Melle Mel, and Furious Five contexts. |
| 7 | 045 | run-dmc-raising-hell | Raising Hell — Run-DMC | Contains version-specific `Walk This Way` concerns. |
| 7 | 047 | nwa-straight-outta-compton | Straight Outta Compton — N.W.A | Explicit versions and censorship context must be preserved. |
| 7 | 047 | dr-dre-the-chronic | The Chronic — Dr. Dre | Producer/featured-artist credits require version-aware handling. |
| 7 | 049 | jeezy-lets-get-it-thug-motivation-101 | Let's Get It: Thug Motivation 101 — Jeezy | Young Jeezy alias should map to Jeezy. |
| 7 | 050 | eminem-the-marshall-mathers-lp | The Marshall Mathers LP — Eminem | Explicit/clean edit handling required. |
| 7 | 050 | cardi-b-invasion-of-privacy | Invasion of Privacy — Cardi B | Clean/explicit survey versions important. |
| 7 | 051 | mos-def-yasiin-bey-black-on-both-sides | Black on Both Sides — Mos Def / Yasiin Bey | Alias handling required. |
| 7 | 051 | madvillain-madvillainy | Madvillainy — Madvillain | Madvillain is a group-project alias, not a duplicate MF DOOM solo album. |
| 7 | 052 | 21-savage-and-metro-boomin-savage-mode-ii | Savage Mode II — 21 Savage & Metro Boomin | Artist credit includes both 21 Savage and Metro Boomin. |
| 7 | 052 | metro-boomin-heroes-and-villains | Heroes & Villains — Metro Boomin | Feature-heavy album; importer must preserve primary artist credit. |
| 9 | 064 | sleep-dopesmoker | Dopesmoker — Sleep | Release/version history needs review. |
| 11 | 081 | black-box-dreamland | Dreamland — Black Box | Sample and vocalist-credit review required. |
| 11 | 081 | fingers-inc-another-side | Another Side — Fingers Inc. | Larry Heard/Mr. Fingers alias network. |
| 11 | 081 | mr-fingers-amnesia | Amnesia — Mr. Fingers | Alias review: Mr. Fingers vs Larry Heard. |
| 11 | 082 | cybotron-enter | Enter — Cybotron | Juan Atkins project alias. |
| 11 | 082 | model-500-deep-space | Deep Space — Model 500 | Juan Atkins alias/project row. |
| 11 | 083 | fred-again-actual-life-3 | Actual Life 3 — Fred again.. | Album project and live/DJ-set objects must remain distinct. |
| 13 | 096 | celia-cruz-and-johnny-pacheco-celia-and-johnny | Celia & Johnny — Celia Cruz and Johnny Pacheco | Collaboration album row. |
| 13 | 096 | willie-colon-and-ruben-blades-siembra | Siembra — Willie Colon and Ruben Blades | Collaboration album must remain distinct from solo artist IDs. |
| 13 | 099 | ali-farka-toure-and-ry-cooder-talking-timbuktu | Talking Timbuktu — Ali Farka Toure and Ry Cooder | Collaboration/global-fusion object. |
| 14 | 100 | bing-crosby-bing-his-legendary-years-1931-1957 | Bing: His Legendary Years, 1931-1957 — Bing Crosby | Holiday-standard recognition should not merge with all standards rows. |
| 14 | 101 | stan-getz-and-joao-gilberto-getz-gilberto | Getz/Gilberto — Stan Getz and Joao Gilberto | Preserve bossa nova collaboration credits. |
| 14 | 103 | max-richter-the-blue-notebooks | The Blue Notebooks — Max Richter | Modern classical/ambient/film-score overlap. |
| 15 | 104 | original-london-cast-of-les-miserables-les-miserables | Les Miserables — Original London Cast of Les Miserables | Cast recording, stage show, and film soundtrack need separate IDs. |
| 15 | 104 | original-broadway-cast-of-west-side-story-west-side-story | West Side Story — Original Broadway Cast of West Side Story | Stage cast and film soundtrack rows should not merge. |
| 15 | 106 | various-artists-o-brother-where-art-thou | O Brother, Where Art Thou? — Various Artists | Americana/roots soundtrack row overlaps country/folk families. |
| 15 | 106 | various-artists-guardians-of-the-galaxy-awesome-mix-vol-1 | Guardians of the Galaxy: Awesome Mix Vol. 1 — Various Artists | Compilation soundtrack made of older songs; do not merge with original release albums. |
| 15 | 106 | various-artists-garden-state | Garden State — Various Artists | Indie soundtrack-compilation object, not a single artist discography. |
| 15 | 107 | trent-reznor-and-atticus-ross-the-social-network | The Social Network — Trent Reznor and Atticus Ross | Score composer identity overlaps Nine Inch Nails/industrial-rock context. |
| 15 | 107 | ludwig-goransson-black-panther | Black Panther — Ludwig Goransson | Score album distinct from Kendrick Lamar-curated soundtrack album. |
| 16 | 110 | elevation-worship-and-maverick-city-music-old-church-basement | Old Church Basement — Elevation Worship and Maverick City Music | Collaboration album should not merge church-band brands. |
| 16 | 110 | keith-and-kristyn-getty-in-christ-alone | In Christ Alone — Keith and Kristyn Getty | Modern hymn/songbook row; many church versions exist. |
| 16 | 110 | hillsong-united-people | People — Hillsong United | Hillsong Worship, Hillsong United, and church-brand rows should remain distinct. |

### Uncertain Recording-vs-Composition Handling

| family | archetype | song_id | song | warning |
| --- | --- | --- | --- | --- |
| 1 | 001 | larry-williams-bony-moronie | Bony Moronie — Larry Williams | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 001 | louis-jordan-caldonia | Caldonia — Louis Jordan | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 001 | wynonie-harris-good-rockin-tonight | Good Rockin' Tonight — Wynonie Harris | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 001 | big-mama-thornton-hound-dog | Hound Dog — Big Mama Thornton | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 001 | smiley-lewis-i-hear-you-knocking | I Hear You Knocking — Smiley Lewis | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 001 | jackie-brenston-and-his-delta-cats-rocket-88 | Rocket 88 — Jackie Brenston and His Delta Cats | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 001 | huey-piano-smith-and-the-clowns-rockin-pneumonia-and-the-boogie-woogie-flu | Rockin' Pneumonia and the Boogie Woogie Flu — Huey "Piano" Smith & The Clowns | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 001 | louis-jordan-saturday-night-fish-fry | Saturday Night Fish Fry — Louis Jordan | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 001 | big-joe-turner-shake-rattle-and-roll | Shake, Rattle and Roll — Big Joe Turner | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 001 | sister-rosetta-tharpe-strange-things-happening-every-day | Strange Things Happening Every Day — Sister Rosetta Tharpe | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 001 | arthur-big-boy-crudup-thats-all-right | That's All Right — Arthur "Big Boy" Crudup | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 002 | ronnie-self-bop-a-lena | Bop-A-Lena — Ronnie Self | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 002 | mac-curtis-grandaddys-rockin | Grandaddy's Rockin' — Mac Curtis | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 002 | johnny-carroll-hot-rock | Hot Rock — Johnny Carroll | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 002 | the-phantom-love-me | Love Me — The Phantom | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 002 | ray-smith-right-behind-you-baby | Right Behind You Baby — Ray Smith | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 002 | warren-smith-rock-n-roll-ruby | Rock 'n' Roll Ruby — Warren Smith | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 002 | warren-smith-ubangi-stomp | Ubangi Stomp — Warren Smith | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 002 | the-rock-a-teens-woo-hoo | Woo-Hoo — The Rock-A-Teens | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 003 | the-dubs-could-this-be-magic | Could This Be Magic — The Dubs | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 003 | the-ravens-count-every-star | Count Every Star — The Ravens | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 003 | the-orioles-crying-in-the-chapel | Crying in the Chapel — The Orioles | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 003 | randy-and-the-rainbows-denise | Denise — Randy & The Rainbows | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 003 | the-orioles-its-too-soon-to-know | It's Too Soon to Know — The Orioles | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 003 | the-harptones-life-is-but-a-dream | Life Is But a Dream — The Harptones | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 003 | the-chantels-maybe | Maybe — The Chantels | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 003 | the-bobbettes-mr-lee | Mr. Lee — The Bobbettes | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 003 | the-jive-five-my-true-story | My True Story — The Jive Five | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 003 | the-channels-the-closer-you-are | The Closer You Are — The Channels | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 003 | the-capris-theres-a-moon-out-tonight | There's a Moon Out Tonight — The Capris | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 003 | the-mello-kings-tonight-tonight | Tonight, Tonight — The Mello-Kings | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 004 | kathy-young-and-the-innocents-a-thousand-stars | A Thousand Stars — Kathy Young & The Innocents | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 004 | johnny-mathis-chances-are | Chances Are — Johnny Mathis | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 004 | johnny-burnette-solo-dreamin | Dreamin' — Johnny Burnette | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 004 | jimmy-darren-goodbye-cruel-world | Goodbye Cruel World — Jimmy Darren | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 004 | jimmie-rodgers-pop-honeycomb | Honeycomb — Jimmie Rodgers | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 004 | little-peggy-march-i-will-follow-him | I Will Follow Him — Little Peggy March | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 004 | pat-boone-love-letters-in-the-sand | Love Letters in the Sand — Pat Boone | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 004 | johnny-preston-running-bear | Running Bear — Johnny Preston | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 004 | robin-luke-susie-darlin | Susie Darlin' — Robin Luke | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 005 | barbara-lewis-hello-stranger | Hello Stranger — Barbara Lewis | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 005 | the-ikettes-im-blue-the-gong-gong-song | I'm Blue (The Gong-Gong Song) — The Ikettes | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 005 | dee-dee-sharp-mashed-potato-time | Mashed Potato Time — Dee Dee Sharp | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 005 | the-chantels-maybe | Maybe — The Chantels | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 005 | the-bobbettes-mr-lee | Mr. Lee — The Bobbettes | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 005 | the-velvelettes-needle-in-a-haystack | Needle in a Haystack — The Velvelettes | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 005 | maxine-brown-oh-no-not-my-baby | Oh No Not My Baby — Maxine Brown | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 005 | claudine-clark-party-lights | Party Lights — Claudine Clark | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 005 | the-raindrops-the-kind-of-boy-you-cant-forget | The Kind of Boy You Can't Forget — The Raindrops | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 005 | the-crystals-uptown | Uptown — The Crystals | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 006 | ike-and-tina-turner-a-fool-in-love | A Fool in Love — Ike & Tina Turner | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 006 | clarence-frogman-henry-aint-got-no-home | Ain't Got No Home — Clarence "Frogman" Henry | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 006 | garnet-mimms-cry-baby | Cry Baby — Garnet Mimms | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 006 | the-contours-do-you-love-me | Do You Love Me — The Contours | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 006 | bobby-blue-bland-i-pity-the-fool | I Pity the Fool — Bobby "Blue" Bland | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 006 | doris-troy-just-one-look | Just One Look — Doris Troy | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 006 | don-covay-mercy-mercy | Mercy, Mercy — Don Covay | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 006 | ernie-k-doe-mother-in-law | Mother-in-Law — Ernie K-Doe | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 006 | james-brown-and-the-famous-flames-please-please-please | Please, Please, Please — James Brown & The Famous Flames | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 006 | ruth-brown-teardrops-from-my-eyes | Teardrops from My Eyes — Ruth Brown | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 006 | hank-ballard-and-the-midnighters-the-twist | The Twist — Hank Ballard & The Midnighters | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 006 | james-brown-and-the-famous-flames-try-me | Try Me — James Brown & The Famous Flames | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 006 | irma-thomas-wish-someone-would-care | Wish Someone Would Care — Irma Thomas | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 006 | hank-ballard-and-the-midnighters-work-with-me-annie | Work With Me Annie — Hank Ballard & The Midnighters | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 006 | arthur-alexander-you-better-move-on | You Better Move On — Arthur Alexander | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 007 | the-atlantics-bombora | Bombora — The Atlantics | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 007 | the-centurions-bullwinkle-part-ii | Bullwinkle Part II — The Centurions | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 007 | the-tornadoes-bustin-surfboards | Bustin' Surfboards — The Tornadoes | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 007 | the-rivieras-california-sun | California Sun — The Rivieras | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 007 | the-revels-church-key | Church Key — The Revels | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 007 | the-revels-comanche | Comanche — The Revels | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 007 | the-viscounts-harlem-nocturne | Harlem Nocturne — The Viscounts | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 007 | the-routers-lets-go-pony | Let's Go (Pony) — The Routers | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 007 | the-gamblers-moon-dawg | Moon Dawg! — The Gamblers | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 007 | johnny-and-the-hurricanes-red-river-rock | Red River Rock — Johnny and the Hurricanes | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 007 | santo-and-johnny-sleep-walk | Sleep Walk — Santo & Johnny | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 007 | the-tornados-telstar | Telstar — The Tornados | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 007 | the-frantics-werewolf | Werewolf — The Frantics | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 1 | 007 | the-string-a-longs-wheels | Wheels — The String-A-Longs | Accepted 001-D gap-fill compact song row; verify recording/version where applicable. |
| 2 | 008 | the-animals-house-of-the-rising-sun | House of the Rising Sun — The Animals | Traditional song; preserve Animals recording identity. |
| 2 | 009 | the-searchers-needles-and-pins | Needles and Pins — The Searchers | Duplicate source mention consolidated. |
| 2 | 009 | the-hollies-bus-stop | Bus Stop — The Hollies | Duplicate source mention consolidated. |
| 2 | 008 | the-zombies-shes-not-there | She's Not There — The Zombies | Source row malformed; corrected artist/year. |
| 2 | 009 | the-byrds-mr-tambourine-man | Mr. Tambourine Man — The Byrds | Do not merge with Dylan composition or recordings. |
| 2 | 011 | the-shadows-of-knight-gloria | Gloria — The Shadows of Knight | Must not merge with Them/Van Morrison version. |
| 2 | 014 | 13th-floor-elevators-youre-gonna-miss-me | You're Gonna Miss Me — 13th Floor Elevators | Artist leading `The` varies by source. |
| 2 | 010 | the-beatles-yesterday | Yesterday — The Beatles | Cover-heavy composition; preserve Beatles recording. |
| 2 | 008 | the-kinks-you-really-got-me | You Really Got Me — The Kinks | Preserve original Kinks recording. |
| 2 | 013 | jefferson-airplane-somebody-to-love | Somebody to Love — Jefferson Airplane | Do not merge with Great Society version. |
| 2 | 008 | the-troggs-wild-thing | Wild Thing — The Troggs | Preserve Troggs recording, not later covers. |
| 2 | 010 | simon-and-garfunkel-mrs-robinson | Mrs. Robinson — Simon & Garfunkel | Film soundtrack context may create alternate object links. |
| 2 | 014 | the-jimi-hendrix-experience-purple-haze | Purple Haze — The Jimi Hendrix Experience | Experience-era recording. |
| 2 | 014 | cream-sunshine-of-your-love | Sunshine of Your Love — Cream | Do not merge with later live versions. |
| 2 | 014 | the-doors-light-my-fire | Light My Fire — The Doors | Single edit and album version should link as versions, not duplicate canonical song rows. |
| 2 | 008 | them-gloria | Gloria — Them | Do not merge with Shadows of Knight version. |
| 3 | 016 | song-show-me-the-way-live-1976 | Show Me the Way (live) — Peter Frampton | live-object dependence |
| 3 | 019 | song-whipping-post-1969 | Whipping Post — The Allman Brothers Band | live version often primary memory |
| 3 | 021 | song-i-want-you-to-want-me-live-1978 | I Want You to Want Me (live) — Cheap Trick | live-version merge risk |
| 3 | 023 | song-this-is-it-1979 | This Is It — Kenny Loggins | soundtrack-pop adjacency |
| 3 | 016 | song-old-time-rock-and-roll-1978 | Old Time Rock and Roll — Bob Seger | Soundtrack/cultural-furniture pull. |
| 3 | 021 | song-hanging-on-the-telephone-1976 | Hanging on the Telephone — The Nerves | Blondie cover may dominate recognition. |
| 4 | 024 | f4-024-song-big-yellow-taxi-joni-mitchell | Big Yellow Taxi — Joni Mitchell | Heavily covered; distinguish original from later covers. |
| 4 | 024 | f4-024-song-you-ve-got-a-friend-carole-king | You've Got a Friend — Carole King | James Taylor version broadens familiarity; do not merge recordings. |
| 4 | 024 | f4-024-song-running-on-empty-jackson-browne | Running on Empty — Jackson Browne | Live/road-song identity. |
| 4 | 024 | f4-024-song-blowin-in-the-wind-bob-dylan | Blowin' in the Wind — Bob Dylan | Also 026 and Family 2; cover-standard risk. |
| 4 | 025 | f4-025-song-without-you-harry-nilsson | Without You — Harry Nilsson | Nilsson recording of Badfinger song; keep version distinct. |
| 4 | 025 | f4-025-song-don-t-know-why-norah-jones | Don't Know Why — Norah Jones | Written by Jesse Harris; Norah recording is the survey object. |
| 4 | 026 | f4-026-song-this-land-is-your-land-woody-guthrie | This Land Is Your Land — Woody Guthrie | Publication/recording date varies; standard exceeds artist. |
| 4 | 026 | f4-026-song-blowin-in-the-wind-bob-dylan | Blowin' in the Wind — Bob Dylan | Peter, Paul and Mary version broadened reach. |
| 4 | 026 | f4-026-song-we-shall-overcome-pete-seeger-et-al-traditional | We Shall Overcome — Pete Seeger et al. / traditional | Traditional/movement attribution; do not assign single owner without source. |
| 4 | 026 | f4-026-song-universal-soldier-buffy-sainte-marie | Universal Soldier — Buffy Sainte-Marie | Donovan cover aided recognition. |
| 4 | 026 | f4-026-song-house-of-the-rising-sun-traditional-revival-circuit-object | House of the Rising Sun — Traditional / revival circuit object | Artist assignment unstable; Animals version is separate. |
| 4 | 027 | f4-027-song-angel-from-montgomery-john-prine | Angel from Montgomery — John Prine | Bonnie Raitt version broadened reach; do not merge recordings. |
| 4 | 027 | f4-027-song-pancho-and-lefty-townes-van-zandt | Pancho and Lefty — Townes Van Zandt | Merle Haggard and Willie Nelson version expanded reach. |
| 4 | 027 | f4-027-song-passionate-kisses-lucinda-williams | Passionate Kisses — Lucinda Williams | Mary Chapin Carpenter version is distinct. |
| 4 | 027 | f4-027-song-orphan-girl-gillian-welch | Orphan Girl — Gillian Welch | Covers and soundtrack life. |
| 4 | 028 | f4-028-song-california-stars-wilco-with-billy-bragg | California Stars — Wilco with Billy Bragg | Collaboration object; not Wilco-only. |
| 4 | 029 | f4-029-song-fast-car-tracy-chapman | Fast Car — Tracy Chapman | Renewed recognition via Luke Combs cover; distinct versions. |
| 4 | 030 | f4-030-song-skinny-love-bon-iver | Skinny Love — Bon Iver | Birdy cover widened reach; distinct versions. |
| 4 | 024 | f4-024-song-both-sides-now-joni-mitchell | Both Sides Now — Joni Mitchell | Judy Collins version is distinct and historically important. |

### Ambiguous Genre / Archetype Placement

| family | archetype | object_type | object_id | object | warning |
| --- | --- | --- | --- | --- | --- |
| 1 | 001 | artist | big-joe-turner | Big Joe Turner | Also 006; distinguish from Bill Haley cover |
| 1 | 001 | artist | big-mama-thornton | Big Mama Thornton | Song recognition mostly via Elvis; keep source version distinct |
| 1 | 001 | artist | huey-piano-smith-and-the-clowns | Huey "Piano" Smith & The Clowns | Also 006 and dance-party oldies |
| 1 | 001 | artist | larry-williams | Larry Williams | Also 002 edge |
| 1 | 001 | artist | louis-jordan | Louis Jordan | Also jump-blues/R&B roots; not core 1955+ oldies |
| 1 | 001 | artist | sister-rosetta-tharpe | Sister Rosetta Tharpe | Also 006 roots; not Page 1 for normal users |
| 1 | 001 | artist | smiley-lewis | Smiley Lewis | Also 006/New Orleans lane |
| 1 | 003 | artist | the-bobbettes | The Bobbettes | Also 005 |
| 1 | 003 | artist | the-chantels | The Chantels | Also 005 |
| 1 | 004 | artist | jimmy-darren | Jimmy Darren | Also 007 image boundary |
| 1 | 004 | artist | little-peggy-march | Little Peggy March | Also 005 pop-craft edge |
| 1 | 005 | artist | barbara-lewis | Barbara Lewis | Also 006 |
| 1 | 005 | artist | dee-dee-sharp | Dee Dee Sharp | Also 004/006 dance-pop edge |
| 1 | 005 | artist | maxine-brown | Maxine Brown | Also 006 |
| 1 | 005 | artist | the-bobbettes | The Bobbettes | Also 003 |
| 1 | 005 | artist | the-chantels | The Chantels | Also 003 |
| 1 | 005 | artist | the-ikettes | The Ikettes | Also 006 |
| 1 | 005 | artist | the-raindrops | The Raindrops | Also songwriter ecosystem |
| 1 | 005 | artist | the-velvelettes | The Velvelettes | Also 006/Motown |
| 1 | 006 | artist | arthur-alexander | Arthur Alexander | Also later source-code |
| 1 | 006 | artist | bobby-blue-bland | Bobby "Blue" Bland | Also blues/soul family |
| 1 | 006 | artist | garnet-mimms | Garnet Mimms | Strong 006/next-family bridge |
| 1 | 006 | artist | hank-ballard-and-the-midnighters | Hank Ballard & The Midnighters | Also 001/003/004 dance-craze overlap |
| 1 | 006 | artist | irma-thomas | Irma Thomas | Also New Orleans lane |
| 1 | 006 | artist | james-brown-and-the-famous-flames | James Brown & The Famous Flames | Later funk/soul family overlap |
| 1 | 006 | artist | otis-redding | Otis Redding | Later family should carry primary weight |
| 1 | 006 | artist | ruth-brown | Ruth Brown | Also 001 roots |
| 1 | 007 | artist | johnny-and-the-hurricanes | Johnny and the Hurricanes | Also 001 instrumental pop |
| 1 | 007 | artist | santo-and-johnny | Santo & Johnny | Also 004/oldies ache |
| 1 | 007 | artist | the-frantics | The Frantics | Also 002/garage bridge |
| 1 | 007 | artist | the-rivieras | The Rivieras | Also 002/garage edge |
| 1 | 001 | album | various-artists-atlantic-rhythm-and-blues-1947-1974 | Atlantic Rhythm and Blues 1947-1974 — Various Artists | Also 006 |
| 1 | 001 | album | big-joe-turner-boss-of-the-blues | Boss of the Blues — Big Joe Turner | Also 006 |
| 1 | 001 | album | various-artists-the-specialty-story | The Specialty Story — Various Artists | Also 006 |
| 1 | 002 | album | the-sonics-here-are-the-sonics | Here Are The Sonics — The Sonics | Boundary LP |
| 1 | 003 | album | the-chantels-we-are-the-chantels | We Are the Chantels — The Chantels | Also 005 |
| 1 | 006 | album | james-brown-live-at-the-apollo | Live at the Apollo — James Brown | Later soul family overlap |
| 1 | 006 | album | otis-redding-pain-in-my-heart | Pain in My Heart — Otis Redding | Later family should carry primary weight |
| 1 | 006 | album | bobby-blue-bland-two-steps-from-the-blues | Two Steps from the Blues — Bobby "Blue" Bland | Also blues family |
| 1 | 006 | album | irma-thomas-wish-someone-would-care | Wish Someone Would Care — Irma Thomas | Also regional soul |
| 1 | 007 | album | the-rivieras-california-sun | California Sun — The Rivieras | Also garage edge |
| 2 | 008 | artist | the-beatles | The Beatles | Cross-family mass object; keep Family 2 membership but allow links to later classic-rock and pop families. |
| 2 | 008 | artist | the-rolling-stones | The Rolling Stones | Avoid collapsing later 1970s Stones canon into this 60s family row. |
| 2 | 008 | artist | the-who | The Who | Later arena/classic-rock identity should not dominate this family row. |
| 2 | 008 | artist | the-kinks | The Kinks | Preserve distinction between early riff-rock hits and later album-world Kinks. |
| 2 | 010 | artist | bob-dylan | Bob Dylan | Strong adjacent-family ownership; avoid overloading Family 2 with full Dylan canon. |
| 2 | 010 | artist | simon-and-garfunkel | Simon & Garfunkel | Adjacent folk/singer-songwriter ownership likely. |
| 2 | 013 | artist | the-beach-boys | The Beach Boys | Strong surf/pop family overlap; avoid merging all Beach Boys eras into this family. |
| 2 | 008 | artist | small-faces | Small Faces | Bridge into 013; avoid whole-catalog overcapture. |
| 2 | 011 | artist | paul-revere-and-the-raiders | Paul Revere & the Raiders | Boundary between British-Invasion pop, garage, and TV-era pop. |
| 2 | 012 | artist | bee-gees-early | Bee Gees (early) | Do not merge with later Bee Gees disco/pop family behavior. |
| 2 | 012 | artist | the-moody-blues-early | The Moody Blues (early) | Cross-family prog ownership required. |
| 2 | 014 | artist | grateful-dead | Grateful Dead | Deeper jam-family ownership later. |
| 2 | 014 | artist | big-brother-and-the-holding-company | Big Brother and the Holding Company | Janis Joplin solo/family ownership later. |
| 2 | 015 | artist | nico | Nico | Distinct from Velvet Underground & Nico album artist. |
| 2 | 013 | album | the-beach-boys-pet-sounds | Pet Sounds — The Beach Boys | Strong surf/pop overlap; Family 2 claim is 1966 studio-pop phase. |
| 2 | 014 | album | cream-wheels-of-fire | Wheels of Fire — Cream | Hybrid studio/live double album; object type set to live_album because source emphasized jam bridge. |
| 2 | 014 | album | the-doors-the-doors | The Doors — The Doors | Self-titled album must remain distinct from artist row. |
| 2 | 015 | album | the-stooges-the-stooges | The Stooges — The Stooges | Self-titled album distinct from artist. |
| 2 | 015 | album | pink-floyd-the-piper-at-the-gates-of-dawn | The Piper at the Gates of Dawn — Pink Floyd | Pink Floyd has stronger adjacent-family ownership. |
| 2 | 015 | album | silver-apples-silver-apples | Silver Apples — Silver Apples | Artist/album self-title requires distinct album row. |
| 2 | 015 | album | soft-machine-the-soft-machine | The Soft Machine — Soft Machine | Later prog ownership likely. |
| 2 | 013 | album | the-beatles-revolver | Revolver — The Beatles | Cross-family classic-rock ownership likely. |
| 2 | 015 | album | the-who-tommy | Tommy — The Who | Adjacent classic-rock family likely. |
| 2 | 013 | album | jefferson-airplane-surrealistic-pillow | Surrealistic Pillow — Jefferson Airplane | Strong adjacent psych family ownership. |
| 2 | 010 | album | simon-and-garfunkel-bookends | Bookends — Simon & Garfunkel | Keep separate from later `Bridge Over Troubled Water`. |
| 2 | 012 | album | the-moody-blues-days-of-future-passed | Days of Future Passed — The Moody Blues | Also Family 3/prog object. |
| 2 | 014 | album | iron-butterfly-in-a-gadda-da-vida | In-A-Gadda-Da-Vida — Iron Butterfly | One-object artist; album and song need distinct rows. |
| 2 | 014 | album | big-brother-and-the-holding-company-cheap-thrills | Cheap Thrills — Big Brother and the Holding Company | Later Janis ownership needs review. |
| 2 | 014 | album | grateful-dead-live-dead | Live/Dead — Grateful Dead | Jam-family overlap; keep edge. |
| 2 | 015 | album | nico-the-marble-index | The Marble Index — Nico | Keep distinct from VU rows. |
| 2 | 012 | song | procol-harum-a-whiter-shade-of-pale | A Whiter Shade of Pale — Procol Harum | Strong prog-family boundary. |
| 2 | 013 | song | jefferson-airplane-white-rabbit | White Rabbit — Jefferson Airplane | Adjacent psych-family claim. |
| 2 | 013 | song | donovan-sunshine-superman | Sunshine Superman — Donovan | Donovan artist likely belongs to folk/psych boundary. |
| 2 | 008 | song | the-easybeats-friday-on-my-mind | Friday on My Mind — The Easybeats | Australian act; keep as boundary rather than British Invasion core. |
| 2 | 013 | song | donovan-hurdy-gurdy-man | Hurdy Gurdy Man — Donovan | Adjacent folk/psych boundary. |
| 2 | 008 | song | manfred-mann-do-wah-diddy-diddy | Do Wah Diddy Diddy — Manfred Mann | Keep 60s Manfred Mann distinct from Earth Band. |
| 2 | 011 | song | paul-revere-and-the-raiders-kicks | Kicks — Paul Revere & the Raiders | 008/011 boundary. |
| 2 | 012 | song | the-beach-boys-god-only-knows | God Only Knows — The Beach Boys | Also 013 bridge. |
| 2 | 012 | song | the-beach-boys-wouldnt-it-be-nice | Wouldn't It Be Nice — The Beach Boys | Also 013 bridge. |
| 2 | 014 | song | big-brother-and-the-holding-company-piece-of-my-heart | Piece of My Heart — Big Brother and the Holding Company | Later Janis ownership. |
| 3 | 016 | artist | artist-led-zeppelin | Led Zeppelin | overlaps 017 and metal family |
| 3 | 016 | artist | artist-elton-john | Elton John | overlaps 022 and Family Four |
| 3 | 016 | artist | artist-billy-joel | Billy Joel | overlaps 022 and Family Four |
| 3 | 016 | artist | artist-the-who | The Who | overlaps earlier British-invasion family |
| 3 | 016 | artist | artist-journey | Journey | later AOR boundary; avoid merging with prog Journey |
| 3 | 017 | artist | artist-led-zeppelin | Led Zeppelin | overlaps 016 and metal family |
| 3 | 017 | artist | artist-ac-dc | AC/DC | overlaps metal family but belongs here |
| 3 | 017 | artist | artist-black-sabbath | Black Sabbath | overlaps metal family heavily |
| 3 | 017 | artist | artist-blue-oyster-cult | Blue Oyster Cult | overlaps 018 and metal family |
| 3 | 018 | artist | artist-yes | Yes | later-pop crossover warning |
| 3 | 018 | artist | artist-peter-gabriel | Peter Gabriel | solo art-pop overlap; distinct from Genesis |
| 3 | 019 | artist | artist-charlie-daniels-band | Charlie Daniels Band | push some objects to country family |
| 3 | 020 | artist | artist-new-york-dolls | New York Dolls | overlaps proto-punk family |
| 3 | 021 | artist | artist-the-cars | The Cars | overlaps new-wave family |
| 3 | 021 | artist | artist-todd-rundgren | Todd Rundgren | overlaps Family Four and art-pop |
| 3 | 022 | artist | artist-elton-john | Elton John | overlaps 016 and Family Four |
| 3 | 022 | artist | artist-billy-joel | Billy Joel | overlaps 016 and Family Four |
| 3 | 022 | artist | artist-carpenters | Carpenters | pop-family overlap stronger than rock identity |
| 3 | 022 | artist | artist-hall-and-oates | Hall & Oates | 023 false-nearby risk |
| 3 | 022 | artist | artist-dan-fogelberg | Dan Fogelberg | Family Four overlap |
| 3 | 016 | artist | artist-bob-seger | Bob Seger | Family 4/heartland overlap. |
| 3 | 016 | artist | artist-santana | Santana | Latin-rock family overlap. |
| 3 | 017 | artist | artist-mountain | Mountain | Metal-family overlap. |
| 3 | 018 | artist | artist-procol-harum | Procol Harum | Early song may route to Family 2. |
| 3 | 021 | artist | artist-marshall-crenshaw | Marshall Crenshaw | Later-era boundary. |
| 3 | 022 | artist | artist-james-taylor | James Taylor | Family 4 overlap. |
| 3 | 022 | artist | artist-carole-king | Carole King | Family 4 overlap. |
| 3 | 022 | artist | artist-carly-simon | Carly Simon | Family 4 overlap. |
| 3 | 022 | artist | artist-jim-croce | Jim Croce | Family 4 overlap; song-first. |
| 3 | 022 | artist | artist-gordon-lightfoot | Gordon Lightfoot | Family 4/folk overlap. |
| 3 | 016 | album | album-whos-next-1971 | Who's Next — The Who | overlaps earlier British rock family |
| 3 | 016 | album | album-damn-the-torpedoes-1979 | Damn the Torpedoes — Tom Petty and the Heartbreakers | solo Petty catalog boundary |
| 3 | 016 | album | album-bat-out-of-hell-1977 | Bat Out of Hell — Meat Loaf | theatrical boundary with 020 |
| 3 | 016 | album | album-brothers-in-arms-1985 | Brothers in Arms — Dire Straits | eighties boundary case |
| 3 | 016 | album | album-escape-1981 | Escape — Journey | later-AOR boundary |
| 3 | 017 | album | album-paranoid-1970 | Paranoid — Black Sabbath | overlaps metal family |
| 3 | 017 | album | album-back-in-black-1980 | Back in Black — AC/DC | overlaps metal family |
| 3 | 017 | album | album-highway-to-hell-1979 | Highway to Hell — AC/DC | overlaps metal family |
| 3 | 017 | album | album-demons-and-wizards-1972 | Demons and Wizards — Uriah Heep | prog boundary |

## Machine-Readable Appendix

```json
{
  "generated": "2026-05-20",
  "status": "staging_consolidated_not_final_lock",
  "counts": {
    "canonical_artists": 1499,
    "canonical_albums": 1207,
    "canonical_song_recordings": 1917,
    "composition_groups": 1865,
    "composition_groups_with_multiple_recordings": 24,
    "families": 18,
    "archetypes": 120,
    "memberships_total": 4840,
    "artist_memberships": 1612,
    "album_memberships": 1245,
    "song_memberships": 1983,
    "explicit_alias_issue_count": 11,
    "alias_merge_qa_issue_count": 30,
    "warning_derived_source_version_issue_count": 73,
    "validation_errors": 0,
    "validation_warnings": 9
  },
  "risk_counts": {
    "manifest_warnings": 9,
    "warning_snippets": 99,
    "raw_rows_with_consolidation_warning": 2383,
    "missing_release_year_rows": 2,
    "same_title_album_risk_groups": 7,
    "likely_accidental_duplicate_title_groups": 3,
    "objects_with_multi_memberships": 210,
    "underfilled_archetypes_lt_25_rows": 14,
    "bloated_archetypes_gt_65_rows": 9,
    "thin_page1_archetypes_lt_4_candidates": 13,
    "thin_page2_archetypes_lt_4_candidates": 4
  },
  "review_queues": {
    "composition_review_queue": "data/canonical_graph/import_dry_run/composition_review_queue.json",
    "merge_review_queue": "data/canonical_graph/import_dry_run/merge_review_queue.md",
    "alias_merge_qa_queue": "data/canonical_graph/policy_hardening/alias_merge_qa_queue.json",
    "warning_snippets": "data/canonical_graph/import_dry_run/warning_snippets.json",
    "family_lock_triage": "data/canonical_graph/policy_hardening/family_lock_triage.md"
  },
  "top_multi_membership_objects": [
    {
      "count": 3,
      "object_type": "artist",
      "id": "beyonce",
      "display_name": "Beyonce",
      "families": [
        6,
        12
      ],
      "archetypes": [
        "042",
        "044",
        "090"
      ]
    },
    {
      "count": 3,
      "object_type": "artist",
      "id": "marvin-gaye",
      "display_name": "Marvin Gaye",
      "families": [
        1,
        6
      ],
      "archetypes": [
        "006",
        "037",
        "041"
      ]
    },
    {
      "count": 3,
      "object_type": "artist",
      "id": "prince",
      "display_name": "Prince",
      "families": [
        6,
        12,
        15
      ],
      "archetypes": [
        "039",
        "088",
        "106"
      ]
    },
    {
      "count": 3,
      "object_type": "artist",
      "id": "the-drifters",
      "display_name": "The Drifters",
      "families": [
        1
      ],
      "archetypes": [
        "001",
        "003",
        "006"
      ]
    },
    {
      "count": 3,
      "object_type": "artist",
      "id": "the-marvelettes",
      "display_name": "The Marvelettes",
      "families": [
        1,
        6
      ],
      "archetypes": [
        "005",
        "006",
        "037"
      ]
    },
    {
      "count": 3,
      "object_type": "artist",
      "id": "whitney-houston",
      "display_name": "Whitney Houston",
      "families": [
        6,
        12,
        15
      ],
      "archetypes": [
        "042",
        "088",
        "106"
      ]
    },
    {
      "count": 3,
      "object_type": "song",
      "id": "the-drifters-there-goes-my-baby",
      "display_name": "There Goes My Baby",
      "families": [
        1
      ],
      "archetypes": [
        "001",
        "003",
        "006"
      ]
    },
    {
      "count": 2,
      "object_type": "album",
      "id": "various-artists-a-christmas-gift-for-you-from-phil-spector",
      "display_name": "A Christmas Gift for You from Phil Spector",
      "families": [
        1,
        17
      ],
      "archetypes": [
        "005",
        "112"
      ]
    },
    {
      "count": 2,
      "object_type": "album",
      "id": "album-a-night-at-the-opera-1975",
      "display_name": "A Night at the Opera",
      "families": [
        3
      ],
      "archetypes": [
        "016",
        "020"
      ]
    },
    {
      "count": 2,
      "object_type": "album",
      "id": "bonobo-black-sands",
      "display_name": "Black Sands",
      "families": [
        11,
        18
      ],
      "archetypes": [
        "084",
        "120"
      ]
    },
    {
      "count": 2,
      "object_type": "album",
      "id": "bo-diddley-bo-diddley",
      "display_name": "Bo Diddley",
      "families": [
        1
      ],
      "archetypes": [
        "001",
        "002"
      ]
    },
    {
      "count": 2,
      "object_type": "album",
      "id": "shania-twain-come-on-over",
      "display_name": "Come On Over",
      "families": [
        5,
        17
      ],
      "archetypes": [
        "033",
        "113"
      ]
    },
    {
      "count": 2,
      "object_type": "album",
      "id": "janet-jackson-control",
      "display_name": "Control",
      "families": [
        6,
        12
      ],
      "archetypes": [
        "042",
        "088"
      ]
    },
    {
      "count": 2,
      "object_type": "album",
      "id": "carl-perkins-dance-album-of-carl-perkins",
      "display_name": "Dance Album of Carl Perkins",
      "families": [
        1
      ],
      "archetypes": [
        "001",
        "002"
      ]
    },
    {
      "count": 2,
      "object_type": "album",
      "id": "sonic-youth-daydream-nation",
      "display_name": "Daydream Nation",
      "families": [
        8,
        10
      ],
      "archetypes": [
        "059",
        "069"
      ]
    },
    {
      "count": 2,
      "object_type": "album",
      "id": "tycho-dive",
      "display_name": "Dive",
      "families": [
        11,
        18
      ],
      "archetypes": [
        "086",
        "120"
      ]
    },
    {
      "count": 2,
      "object_type": "album",
      "id": "pixies-doolittle",
      "display_name": "Doolittle",
      "families": [
        8,
        10
      ],
      "archetypes": [
        "059",
        "069"
      ]
    },
    {
      "count": 2,
      "object_type": "album",
      "id": "various-artists-frozen",
      "display_name": "Frozen",
      "families": [
        15,
        17
      ],
      "archetypes": [
        "105",
        "114"
      ]
    },
    {
      "count": 2,
      "object_type": "album",
      "id": "album-goodbye-yellow-brick-road-1973",
      "display_name": "Goodbye Yellow Brick Road",
      "families": [
        3
      ],
      "archetypes": [
        "016",
        "022"
      ]
    },
    {
      "count": 2,
      "object_type": "album",
      "id": "sister-rosetta-tharpe-gospel-train",
      "display_name": "Gospel Train",
      "families": [
        1,
        16
      ],
      "archetypes": [
        "001",
        "108"
      ]
    }
  ],
  "composition_review_keys": [
    "alison",
    "blind",
    "cum-on-feel-the-noize",
    "cupid",
    "doomsday",
    "gee",
    "gloria",
    "god-only-knows",
    "hound-dog",
    "house-of-the-rising-sun",
    "i-ll-take-you-there",
    "lonely-boy",
    "love-shack",
    "oblivion",
    "only-you",
    "push-it",
    "shake-rattle-and-roll",
    "stay",
    "that-s-all-right",
    "the-twist",
    "turn-turn-turn",
    "walk-this-way",
    "we-don-t-talk-about-bruno",
    "zombie"
  ]
}
```
