# Survey Grid Page 1 Archetype Scoring Review - 2026-06-02

Purpose: review the proposed Artist Grid 1 policy against Matt's latest uploaded Apple Music payload.

Payload used:

- `apple_music_signal_payload:95FC6DE7-D899-4D72-85D6-060490AA55B3`
- Captured at: `2026-05-31T17:10:03Z`
- Active universe used for this audit: active canonical graph/app canonical resources with Apple catalog resolution, not legacy `survey_*_candidates` allowlists.
- Active counts observed from bundled app resources/catalog index: 1,445 artists, 1,734 songs, 1,116 albums.

## Confirmed Interpretation

Apple-derived top artists means artists ranked by Apple payload scoring after canonical resolution and song/album-to-artist rollup. It does not mean recognition tier, canonical priority, old survey-surface priority, or generic popularity.

Archetype points from Apple-ranked artists:

- Artist ranks 1-10: 3 points to each archetype the artist belongs to.
- Artist ranks 11-20: 2 points.
- Artist ranks 21-30: 1 point.

Archetype points from Apple-ranked songs:

- Song ranks 1-20: 1.5 points to each archetype the song belongs to.
- Song ranks 21-40: 1 point.
- Song ranks 41-60: 0.5 points.

Artist Grid 1 proposal:

- Rank archetypes by total points.
- Archetype ranks 1-4 each get 3 slots.
- Slot A: user's highest Apple-scoring artist in that archetype.
- Slot B: high-recognition artist in that archetype; Apple artist score is tiebreaker.
- Slot C: medium-recognition artist in that archetype; Apple artist score is tiebreaker.

## Top Apple-Scored Artists

| Rank | Artist | Score | Archetype(s) | Why it scored |
| ---: | --- | ---: | --- | --- |
| 1 | The Turtles | 6.00 | 013 | Multiple recent-played Turtles songs rolled up to artist. |
| 2 | Radiohead | 5.30 | 078 | Replay artist ref plus Replay song/album rollups. |
| 3 | Sonic Youth | 5.25 | 059, 069 | Replay artist ref plus Replay song/album rollups. |
| 4 | The Beatles | 5.10 | 008 | Recent and Replay song rollups. |
| 5 | Pixies | 3.80 | 059, 069 | Replay artist ref plus Replay song rollups. |
| 6 | Nirvana | 3.70 | 070 | Recent song/album rollups plus Replay artist ref. |
| 7 | Elton John | 2.75 | 016, 022 | Recent song rollups plus Replay album rollup. |
| 8 | Wipers | 2.70 | 060, 069 | Recent song rollup plus Replay artist/song rollups. |
| 9 | Hole | 2.15 | 074 | Replay song/album rollups. |
| 10 | ABBA | 2.00 | 113 | Recent-played ABBA songs rolled up to artist. |
| 11 | The Ronettes | 2.00 | 005 | Recent-played song rollups. |
| 12 | Weezer | 2.00 | 075 | Recent-played song rollups. |
| 13 | Donovan | 2.00 | 010 | Recent-played song rollups. |
| 14 | Neutral Milk Hotel | 2.00 | 072 | Recent-played song rollups. |
| 15 | The Animals | 2.00 | 008 | Recent-played song/album rollups. |
| 16 | The Mamas & the Papas | 2.00 | 010 | Recent-played song/album rollups. |
| 17 | Amyl and the Sniffers | 2.00 | 115 | Recent-played song/album rollups. |
| 18 | Love | 2.00 | 012 | Recent-played song plus Replay artist ref. |
| 19 | Raspberries | 2.00 | 021 | Recent-played song/album rollups. |
| 20 | The Cure | 1.70 | 056, 069 | Recent song rollup plus Replay song rollup. |

## Top Archetypes From Proposed Point Rubric

| Rank | Archetype | Points | Main contributors |
| ---: | --- | ---: | --- |
| 1 | 069 | 13.50 | Sonic Youth, Pixies, Wipers, The Cure, Husker Du, `Teen Age Riot`. |
| 2 | 115 | 9.00 | Amyl and the Sniffers, `Blackout`, `Chaise Longue`, `Chosen to Deserve`, `Guided by Angels`, `She's Leaving You`. |
| 3 | 059 | 7.50 | Sonic Youth, Pixies, `Teen Age Riot`. |
| 4 | 010 | 6.50 | Donovan, The Mamas & the Papas, Simon & Garfunkel, `Yesterday`. |
| 5 | 013 | 6.50 | The Turtles, The Beach Boys, The Monkees, `Crimson and Clover`. |
| 6 | 070 | 6.50 | Nirvana, Smashing Pumpkins, Soundgarden, `Smells Like Teen Spirit`. |
| 7 | 074 | 6.00 | Hole, `Cannonball`, `Celebrity Skin`. |
| 8 | 075 | 6.00 | Weezer, `Buddy Holly`, `Radiation Vibe`, `Sucked Out`. |
| 9 | 021 | 5.50 | Raspberries, `Go All the Way`, `September Gurls`, `Shake Some Action`. |
| 10 | 008 | 5.00 | The Beatles, The Animals. |

## Strict Artist Grid 1 Result

This is the direct result of the proposal as stated, with page-level artist dedupe enforced.

| Slot | Archetype | Slot type | Artist | Apple artist score | Why |
| ---: | --- | --- | --- | ---: | --- |
| 1 | 069 | User top | Sonic Youth | 5.25 | Highest Apple-scoring available artist in 069. |
| 2 | 069 | High recognition | Pixies | 3.80 | Mass/high recognition in 069; Apple score breaks ties. |
| 3 | 069 | Medium recognition | Wipers | 2.70 | Medium-recognition 069 artist with strongest Apple score. |
| 4 | 115 | User top | Amyl and the Sniffers | 2.00 | Highest Apple-scoring available artist in 115. |
| 5 | 115 | High recognition | Fontaines D.C. | 1.00 | High-recognition 115 artist; Apple score tie-breaker. |
| 6 | 115 | Medium recognition | Geese | 1.00 | Medium-recognition 115 artist; Apple score tie-breaker. |
| 7 | 059 | User top | needs fallback | 0.00 | Sonic Youth and Pixies already consumed by 069; no remaining Apple-scored artist in 059 under no-repeat page dedupe. |
| 8 | 059 | High recognition | The Replacements | 0.00 | High-recognition active 059 artist. |
| 9 | 059 | Medium recognition | Camper Van Beethoven | 0.00 | Medium-recognition active 059 artist. |
| 10 | 010 | User top | Donovan | 2.00 | Highest Apple-scoring available artist in 010. |
| 11 | 010 | High recognition | Simon & Garfunkel | 1.00 | Mass-recognition active 010 artist. |
| 12 | 010 | Medium recognition | needs fallback | 0.00 | No active medium-tier artist found for 010 under the current direct-artist Apple-ID filter. |

## Full 12-Tile Fallback View For Review

This is not yet an approved rule. It is a concrete fallback view if we choose:

- no duplicate artists on the page;
- if the user-top slot is exhausted by multi-membership dedupe, use the next best recognition artist in that archetype;
- if no medium-recognition artist exists, use the next best remaining active artist in that archetype.

| Slot | Archetype | Slot type | Artist | Apple artist score | Note |
| ---: | --- | --- | --- | ---: | --- |
| 1 | 069 | User top | Sonic Youth | 5.25 | Apple-scored top. |
| 2 | 069 | High recognition | Pixies | 3.80 | Recognition plus Apple tie-break. |
| 3 | 069 | Medium recognition | Wipers | 2.70 | Medium-recognition confirmation. |
| 4 | 115 | User top | Amyl and the Sniffers | 2.00 | Apple-scored top. |
| 5 | 115 | High recognition | Fontaines D.C. | 1.00 | Recognition plus Apple tie-break. |
| 6 | 115 | Medium recognition | Geese | 1.00 | Medium-recognition confirmation. |
| 7 | 059 | User fallback | The Replacements | 0.00 | Fallback because Sonic Youth/Pixies already appeared. |
| 8 | 059 | High recognition | R.E.M. | 0.00 | Next active high-recognition 059 candidate. |
| 9 | 059 | Medium recognition | Camper Van Beethoven | 0.00 | Medium-recognition confirmation. |
| 10 | 010 | User top | Donovan | 2.00 | Apple-scored top. |
| 11 | 010 | High recognition | Simon & Garfunkel | 1.00 | Mass-recognition anchor. |
| 12 | 010 | Medium fallback | The Mamas & the Papas | 2.00 | Fallback because 010 has no active medium-tier artist. |

## Decisions Needed

1. Should multi-membership artists be allowed to satisfy only one slot per page? Current assumption: yes, no duplicate artists on one page.
2. If the user-top slot for an archetype is exhausted by page dedupe, should it fall back to:
   - next active high-recognition artist in that archetype;
   - next Apple-scored artist from the same family;
   - or the next-ranked archetype?
3. If a target archetype lacks an active medium-recognition artist, should the fallback use:
   - next best active artist in that archetype;
   - next lower recognition tier;
   - or the next-ranked archetype with a valid medium slot?
