# Gate 2B Pre-Pilot Repair Delta Report

Generated: 2026-05-20

Status: `LIMITED_BETA_SURVEY_PILOT_READY_WITH_GUARDRAILS` for the generated v0.2 survey surfaces. The raw canonical graph remains staging-consolidated and not hard-lock ready.

## Summary

| check | result |
| --- | --- |
| manifest status | `limited_beta_survey_packet_ready_with_guardrails` |
| quarantine rows | 146 before / 107 after |
| rows unquarantined | 39 |
| newly quarantined rows | 0 |
| page1 QA failures | 0 |
| recording/quarantine consistency failures | 0 |
| import dry run | 0 errors / 9 warnings |

## Special-Entity Repair

Broad substring matching was replaced by typed exact IDs, church-brand IDs, and token-boundary phrase matching. The repair is object/context-scoped: risky recordings no longer globally block ordinary artist, album, or song rows.

| watched object | current state |
| --- | --- |
| `artist:aretha-franklin` | clear |
| `song_recording:aretha-franklin-respect` | clear |
| `song_recording:aretha-franklin-chain-of-fools` | clear |
| `song_recording:aretha-franklin-think` | clear |
| `album:aretha-franklin-i-never-loved-a-man-the-way-i-love-you` | clear |
| `album:aretha-franklin-lady-soul` | clear |
| `song_recording:aretha-franklin-amazing-grace` | quarantined |
| `artist:john-coltrane` | clear |
| `album:john-coltrane-a-love-supreme` | clear |
| `song_recording:john-coltrane-my-favorite-things` | quarantined |
| `artist:crystal-castles` | clear |
| `song_recording:crystal-castles-crimewave` | clear |
| `artist:casting-crowns` | clear |
| `artist:original-broadway-cast-of-wicked` | quarantined |
| `album:various-artists-the-lion-king` | quarantined |
| `artist:hillsong-worship` | quarantined |
| `song_recording:encanto-cast-we-dont-talk-about-bruno` | quarantined |

## Family Readiness Repair

| family | readiness | fast_survey_allowed | page1_total |
| --- | --- | --- | --- |
| 12 Pop Monoculture and Persona Pop | `survey_ready` | `True` | 36 |
| 15 Soundtrack/Theater | `context_only` | `False` | 0 |
| 17 Nostalgia/Context | `context_only` | `False` | 0 |

## Page 1 Before / After

### Family 6 Artist Page 1

**Before:** Aaliyah | Al Green | Alicia Keys | Anita Baker | Barry White | Beyonce | Boyz II Men | Chic | Diana Ross | Earth, Wind & Fire | Four Tops | Frank Ocean

**After:** Al Green | Aretha Franklin | Donna Summer | Earth, Wind & Fire | James Brown | Janet Jackson | Lauryn Hill | Marvin Gaye | Otis Redding | Stevie Wonder | The Supremes | The Temptations

### Family 12 Artist Page 1

**Before:** Adele | Dua Lipa | Olivia Rodrigo | Ed Sheeran | Sabrina Carpenter | Charli XCX | Doja Cat | Sam Smith | Sia | Demi Lovato | Lewis Capaldi | Camila Cabello

**After:** Adele | Backstreet Boys | Beyonce | Britney Spears | Lady Gaga | Madonna | Mariah Carey | Michael Jackson | Prince | Rihanna | Taylor Swift | Whitney Houston

### Family 6 Album Page 1

**Before:** A Seat at the Table | Bad Girls | Baduizm | Blonde | Channel Orange | Control | Cooleyhighharmony | CrazySexyCool | Ctrl | Diamond Life | Don't Be Cruel | Innervisions

**After:** Bad Girls | Control | I Never Loved a Man the Way I Love You | Innervisions | Lady Soul | Live at the Apollo | Otis Blue | Rhythm Nation 1814 | Songs in the Key of Life | The Miseducation of Lauryn Hill | The Temptations Sing Smokey | What's Going On

### Family 12 Album Page 1

**Before:** 21 | 25 | Future Nostalgia | Sour | x | In the Lonely Hour | Brat | Short n Sweet | Planet Her | 1000 Forms of Fear | Divinely Uninspired to a Hellish Extent | The Rise and Fall of a Midwest Princess

**After:** ...Baby One More Time | 1989 | 21 | Daydream | Good Girl Gone Bad | Lemonade | Like a Prayer | Millennium | Purple Rain | The Fame | Thriller | Whitney Houston

### Family 6 Song Page 1

**Before:** Adorn | Cranes in the Sky | Doo Wop (That Thing) | End of the Road | Everyday People | Fallin' | I Got You (I Feel Good) | I Wanna Dance with Somebody | I Want You Back | I Will Survive | In the Midnight Hour | Last Dance

**After:** (Sittin' On) The Dock of the Bay | Doo Wop (That Thing) | I Feel Love | I Got You (I Feel Good) | I Heard It Through the Grapevine | I Wanna Dance with Somebody | Let's Stay Together | My Girl | Respect | September | Superstition | You Can't Hurry Love

### Family 12 Song Page 1

**Before:** Drivers License | Hello | Rolling in the Deep | Chandelier | Levitating | Good 4 U | Shape of You | Thinking Out Loud | Espresso | Stay with Me | Good Luck, Babe! | Say So

**After:** ...Baby One More Time | Bad Romance | Billie Jean | Blank Space | Crazy in Love | I Wanna Dance with Somebody | I Want It That Way | Like a Prayer | Rolling in the Deep | Thriller | Toxic | Umbrella

## Sidecar Consistency

| recording | review_status | survey_safe | survey_safe_reason |
| --- | --- | --- | --- |
| `f4-028-song-waiting-for-a-superman-the-jayhawks` | `quarantined` | `False` | quarantined: wrong_attribution_suspected |
| `aretha-franklin-respect` | `approved` | `True` | approved exact recording |
| `john-coltrane-my-favorite-things` | `quarantined` | `False` | quarantined: composition_unresolved; special_entity_model_missing |
| `crystal-castles-crimewave` | `approved` | `True` | approved exact recording |
| `encanto-cast-we-dont-talk-about-bruno` | `quarantined` | `False` | quarantined: special_entity_model_missing; composition_unresolved |

## Rows Unquarantined

- `album:aretha-franklin-i-never-loved-a-man-the-way-i-love-you`
- `album:aretha-franklin-lady-soul`
- `album:casting-crowns-casting-crowns`
- `album:crystal-castles-crystal-castles`
- `album:john-coltrane-a-love-supreme`
- `album:luciano-pavarotti-the-essential-pavarotti`
- `album:nuggets-come-to-the-sunshine`
- `album:nuggets-original-artyfacts-from-the-first-psychedelic-era-1965-1968`
- `album:pebbles-volume-1`
- `album:phil-spector-various-artists-back-to-mono-1958-1969`
- `album:various-artists-a-christmas-gift-for-you-from-phil-spector`
- `album:various-artists-atlantic-rhythm-and-blues-1947-1974`
- `album:various-artists-disney-childrens-favorites`
- `album:various-artists-dr-demento-20th-anniversary-collection`
- `album:various-artists-garden-state`
- `album:various-artists-no-new-york`
- `album:various-artists-one-kiss-can-lead-to-another-girl-group-sounds-lost-and-found`
- `album:various-artists-ride-the-wild-surf`
- `album:various-artists-surf-age-nuggets`
- `album:various-artists-techno-the-new-dance-sound-of-detroit`
- `album:various-artists-the-doo-wop-box`
- `album:various-artists-the-red-bird-girls`
- `album:various-artists-the-specialty-story`
- `album:various-artists-the-sun-rockabilly-years`
- `album:various-artists-wanted-the-outlaws`
- `artist:aretha-franklin`
- `artist:casting-crowns`
- `artist:crystal-castles`
- `artist:f4-026-artist-pete-seeger`
- `artist:john-coltrane`
- `artist:luciano-pavarotti`
- `song_recording:aretha-franklin-chain-of-fools`
- `song_recording:aretha-franklin-respect`
- `song_recording:aretha-franklin-think`
- `song_recording:casting-crowns-who-am-i`
- `song_recording:crystal-castles-crimewave`
- `song_recording:f4-026-song-if-i-had-a-hammer-pete-seeger-and-lee-hays-peter-paul-and-mary-popularized`
- `song_recording:f4-026-song-turn-turn-turn-the-byrds-pete-seeger`
- `song_recording:f4-026-song-where-have-all-the-flowers-gone-pete-seeger`

## Rows Newly Quarantined

None.

## Remaining Guardrails

- Use only generated `survey_*_candidates_v0_2.json` surfaces for pilot survey tests.
- Do not use raw family rows for Fast Survey or starter Atlas writes.
- Families 15 and 17 remain `context_only` and excluded from Fast Survey.
- Quarantined rows remain blocked from Fast Survey, starter Atlas, default mission generation, and automatic Apple Music resolution.
- False-nearby/dead-end probe rows remain candidate experiments only; they do not create Atlas Dead Ends without repeated user signal.
