# Gap Summary - Family 3

Family 3 scope: Classic Rock, Album Rock, Progressive Rock, plus the source report's adjacent hard rock, southern roots, power-pop, soft-rock, glam, and yacht boundary archetypes.

## Row Counts

| archetype_id | archetype_name | artists | albums | songs | added_artists | added_albums | added_songs |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 016 | Classic Rock / Album-Rock Spine | 19 | 17 | 21 | 7 | 6 | 9 |
| 017 | Hard Rock / Riff Rock / Proto-Metal | 15 | 14 | 16 | 3 | 3 | 3 |
| 018 | Progressive Rock / Art-Prog Canon | 17 | 17 | 19 | 5 | 5 | 5 |
| 019 | Southern Rock / Roots Jam Rock | 11 | 10 | 12 | 0 | 0 | 0 |
| 020 | Glam Rock / Theatrical Seventies Rock | 10 | 10 | 12 | 0 | 0 | 0 |
| 021 | Power Pop / Melodic Guitar Pop | 11 | 10 | 13 | 0 | 0 | 0 |
| 022 | Soft Rock / AM Gold / Adult Pop | 13 | 11 | 16 | 1 | 1 | 1 |
| 023 | Yacht Rock / Smooth Studio Pop | 11 | 9 | 15 | 1 | 1 | 1 |

## Missing-Obvious Fill

| area | status | notes |
| --- | --- | --- |
| Classic-rock spine | filled | Added CCR, Tom Petty and the Heartbreakers, Dire Straits, Steve Miller Band, Journey, Foreigner, and Meat Loaf as missing-obvious album-radio/AOR objects. |
| Hard-rock bridge depth | filled | Added Rainbow, UFO, and Uriah Heep because they were named as bridge acts but absent from candidate rows. |
| Progressive specialist depth | filled | Added ELO and Peter Gabriel bridges plus Gentle Giant, Van der Graaf Generator, and Renaissance from the source limitations. |
| Soft-rock adjacency | filled | Added Dan Fogelberg as a conservative soft-rock singer-songwriter bridge. |
| Yacht false-nearby control | filled | Added Player/Baby Come Back as a flagged song-first false-nearby, not a broad strict-yacht anchor. |
| Version and cover risks | flagged | Live versions such as I Want You to Want Me (live) and Show Me the Way (live) remain distinct; no cover/version merging was inferred. |

## Bridge / Contrast / False-Nearby Expansion

| archetype_id | relationship_type | source_key | items | reason |
| --- | --- | --- | --- | --- |
| 016 | bridge | bridge_artists | Dire Straits; Supertramp; Tom Petty and the Heartbreakers; Steve Miller Band; Bad Company; ELO; Foreigner; Journey; REO Speedwagon; Meat Loaf; Steely Dan; Cheap Trick | matters because page-two often needs to separate broad classic-rock comfort from harder, softer, poppier, or slicker branches |
| 016 | bridge | bridge_songs | Sultans of Swing; Free Fallin'; More Than a Feeling; Dreams; Go Your Own Way; Take It Easy; Hotel California; Bohemian Rhapsody; Rocket Man; Piano Man; Show Me the Way (live); Carry On Wayward Son | matters because these songs frequently light up even when artist-level preference is fuzzy |
| 016 | contrast | contrast_artists | Black Sabbath; Yes; Genesis; Big Star; Hall & Oates; Allman Brothers Band; Steely Dan; T. Rex; Chicago; Toto | matters because they pull users toward harder, proggier, power-pop, soft-pop, southern, glam, or yacht branches |
| 016 | false_nearby | false_nearby_risks | Eagles as always-album-first; Elton/Billy as pure singer-songwriter; Queen as only glam; Heart as only hard rock; Steely Dan as generic classic-rock catchall | matters because sloppy placement weakens later adaptive questioning |
| 017 | bridge | bridge_artists | Queen; Heart; Blue Oyster Cult; Thin Lizzy; Alice Cooper; Kiss; Bad Company; Van Halen; UFO; Rainbow; Uriah Heep; ZZ Top | matters because page-two often needs to sort raw heaviness from theatricality, melody, or prog flavor |
| 017 | bridge | bridge_songs | Barracuda; Smoke on the Water; (Don't Fear) The Reaper; The Boys Are Back in Town; School's Out; Rock and Roll All Nite; Whole Lotta Love; Back in Black; Highway to Hell; Walk This Way; Runnin' with the Devil | matters because these are where casual classic-rock listeners and heavier listeners overlap |
| 017 | contrast | contrast_artists | Hall & Oates; America; Big Star; Yes; Genesis; Allman Brothers Band; Steely Dan; Carpenters | matters because they pull users away from heaviness toward soft, melodically pop, prog, roots, or studio-smooth lanes |
| 017 | false_nearby | false_nearby_risks | overclassifying Sabbath/Zeppelin as metal-only; filing Heart as soft rock only; treating Queen/Kiss/Alice only as glam | matters because hard-riff preference is broader than strict metal taste |
| 018 | bridge | bridge_artists | Steely Dan; ELO; Supertramp; Kansas; Rush; Moody Blues; Alan Parsons Project; Peter Gabriel; Jethro Tull; Bowie; Roxy Music; Toto | matters because album-world prog often shades into studio-pop, glam-art, or hard-riff territory |
| 018 | bridge | bridge_songs | Money; Wish You Were Here; Roundabout; Owner of a Lonely Heart; Tom Sawyer; Carry On Wayward Son; Nights in White Satin; Eye in the Sky; Sirius; Aqualung | matters because they separate mass-recognized prog entry points from specialist-only taste |
| 018 | contrast | contrast_artists | Eagles; Hall & Oates; America; Big Star; AC/DC; Lynyrd Skynyrd; Carpenters; Christopher Cross | matters because these anchor non-prog branches that still share some audience |
| 018 | false_nearby | false_nearby_risks | filing Pink Floyd as only classic rock; treating Rush as metal-only; treating Supertramp/ELO as pure pop; treating Bowie/Roxy as full prog | matters because album-survey branching depends on keeping art-prog distinct |
| 020 | bridge | bridge_artists | Queen; Alice Cooper; Sweet; Slade; Roxy Music; Bowie; Sparks; Cheap Trick; New York Dolls; Mott the Hoople | matters because glam often hands users into hard rock, art rock, proto-punk, or power pop |
| 020 | bridge | bridge_songs | Killer Queen; Rebel Rebel; Starman; Bang a Gong; Ballroom Blitz; Fox on the Run; Love Is the Drug; All the Young Dudes; School's Out; Cum On Feel the Noize | matters because these are the cleanest adaptive separators |
| 020 | contrast | contrast_artists | Allman Brothers Band; America; Christopher Cross; Steely Dan; Carpenters; Yes; Black Sabbath; Big Star | matters because they keep twang, softness, smoothness, dense prog, or plainspoken pop out of the glam bucket |
| 020 | false_nearby | false_nearby_risks | overclassifying Bowie and Queen everywhere; treating Alice/Kiss only as hard rock; confusing power-pop crunch with glam polish | matters because theatricality is the lane's strongest discriminator |
| 019 | bridge | bridge_artists | ZZ Top; Bad Company; The Black Crowes; 38 Special; Charlie Daniels Band; Little Feat; Gov't Mule; Marshall Tucker Band; Eagles; The Band | matters because southern taste often blends with classic, country, boogie, or jam pathways |
| 019 | bridge | bridge_songs | Free Bird; Sweet Home Alabama; Ramblin' Man; Jessica; Can't You See; La Grange; Dixie Chicken; Green Grass and High Tides; Flirtin' with Disaster; Remedy | matters because they identify whether a user wants roots-jam, guitar-hero, or radio-furniture southern rock |
| 019 | contrast | contrast_artists | Pink Floyd; Hall & Oates; Big Star; Toto; Bowie; Carpenters; Steely Dan; Yes | matters because they separate roots texture from prog, smooth, glam, or melodic-pop preferences |
| 019 | false_nearby | false_nearby_risks | treating ZZ Top as only hard rock; overpushing Marshall Tucker/Charlie Daniels into country only; treating Black Crowes purely as nineties alt-rock | matters because southern overlap is one of the family's biggest merge risks |
| 021 | bridge | bridge_artists | Cheap Trick; The Cars; Badfinger; Raspberries; Nick Lowe; Rockpile; Todd Rundgren; Sparks; Sweet; Slade | matters because this lane constantly touches glam, new wave, hard rock, and singer-songwriter pop |
| 021 | bridge | bridge_songs | September Gurls; Surrender; I Want You to Want Me (live); Come and Get It; No Matter What; Go All the Way; My Sharona; Just What I Needed; Cruel to Be Kind; Shake Some Action | matters because songs often travel ahead of artist recognition |
| 021 | contrast | contrast_artists | Pink Floyd; AC/DC; Hall & Oates; Allman Brothers; Christopher Cross; Carpenters; Steely Dan | matters because they distinguish hooky crunch-pop from long-form prog, heaviness, roots-jam, or smooth studio polish |
| 021 | false_nearby | false_nearby_risks | treating Cars/Knack only as new wave; treating Cheap Trick only as hard rock; treating Badfinger only as Beatles-adjacent soft pop | matters because power-pop identity is often obscured by neighboring lanes |
| 022 | bridge | bridge_artists | Fleetwood Mac; Eagles; Hall & Oates; Doobie Brothers; Boz Scaggs; Chicago; America; Bread; Ambrosia; Dan Fogelberg; Christopher Cross | matters because the lane shades into classic rock, singer-songwriter, and yacht |
| 022 | bridge | bridge_songs | Tiny Dancer; Your Song; Piano Man; Dreams; Landslide; Take It Easy; Sister Golden Hair; Make It with You; Summer Breeze; If You Leave Me Now; Lowdown | matters because songs are usually stronger survey triggers than album-world knowledge |
| 022 | contrast | contrast_artists | AC/DC; Yes; Big Star; T. Rex; Allman Brothers; Steely Dan; Black Sabbath; Cheap Trick | matters because they keep hard, prog, glam, roots, or crunch-pop users from being overclassified as soft-rock listeners |
| 022 | false_nearby | false_nearby_risks | treating Eagles/Fleetwood Mac as only soft rock; treating Hall & Oates as always yacht; treating Elton/Billy purely as singer-songwriter | matters because adult-pop recognition overlaps many neighboring families |
| 023 | bridge | bridge_artists | Steely Dan; Doobie Brothers; Toto; Christopher Cross; Boz Scaggs; Kenny Loggins; Michael McDonald; Ambrosia; Pages; Hall & Oates; Player | matters because page-two must distinguish strict yacht from generic soft-rock nostalgia |
| 023 | bridge | bridge_songs | Peg; Deacon Blues; What a Fool Believes; Minute by Minute; Sailing; Ride Like the Wind; Rosanna; Africa; Lowdown; This Is It; I Keep Forgettin'; Steal Away | matters because songs are the fastest way to find genuine smooth-studio affinity |
| 023 | contrast | contrast_artists | Eagles; Fleetwood Mac; America; AC/DC; Big Star; Allman Brothers; Bowie; Carpenters | matters because many mellow-listening users are not actually yacht users |
| 023 | false_nearby | false_nearby_risks | treating all mellow seventies pop as yacht; overincluding Eagles/Fleetwood/Hall & Oates; reducing Steely Dan to a joke category | matters because this lane only works if it stays musically precise |

## Second-Pass Cross-Check Addendum

Reviewed `/Users/matt_wittlief_home/Library/Mobile Documents/com~apple~CloudDocs/F3-2.md` after the initial artifact build. Accepted additions: 29 artists, 19 albums, 26 songs. New total rows: 403.

Merge policy: accepted missing-obvious and high-survey-value objects; deferred collector-depth, unstable boundary, and low-recognition rows to later consolidation rather than importing them now.
