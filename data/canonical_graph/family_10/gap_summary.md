# Family 10 Gap Summary

Scope: Alternative, Indie, Grunge, Emo.

## Import Shape

| Object class | Existing seed rows | Added missing-obvious rows | Total normalized rows |
|---|---:|---:|---:|
| Artists | 66 | 32 | 98 |
| Albums | 0 | 89 | 89 |
| Songs | 0 | 128 | 128 |

## Archetype Balance

| archetype_id | archetype_name | artists | albums | songs | total |
|---|---|---|---|---|---|
| 069 | 1980s Alternative Source-Code / Pre-Grunge | 10 | 7 | 10 | 27 |
| 070 | Grunge / Seattle / 90s Alt Center | 6 | 7 | 10 | 23 |
| 071 | Post-Grunge / Modern Rock Radio | 8 | 7 | 11 | 26 |
| 072 | 90s Indie / Lo-Fi / Slacker / Matador Axis | 7 | 7 | 10 | 24 |
| 073 | Shoegaze / Dream Pop / Noise Haze | 9 | 7 | 10 | 26 |
| 074 | Female 90s Alt / Riot Grrrl / Guitar Voices | 10 | 8 | 11 | 29 |
| 075 | Power-Pop Revival / Crunchy Alt-Pop | 8 | 7 | 10 | 25 |
| 076 | Pop-Punk / Skate Punk / 90s-00s Punk Pop | 7 | 7 | 12 | 26 |
| 077 | Emo / Mall Emo / Post-Hardcore Pop | 9 | 9 | 12 | 30 |
| 078 | Blog Indie / Prestige Indie / 2000s Indie Rock | 8 | 8 | 10 | 26 |
| 079 | Garage Revival / Rock-Is-Back 2000s | 7 | 7 | 10 | 24 |
| 080 | Post-Punk Revival / Dark Indie Rock | 9 | 8 | 12 | 29 |

## Filled Gaps

| Gap area | Added coverage | Reason |
|---|---|---|
| College-rock / pre-grunge source-code | R.E.M., The Replacements, Husker Du, Jane's Addiction, The Cure | Packet 010 named source-code bands but omitted several obvious artist-level anchors required to explain 1980s alternative before grunge. |
| 90s alt center beyond Seattle | Smashing Pumpkins, Foo Fighters, Third Eye Blind | Keeps Family 10 from equating all 90s alternative with grunge while still respecting normal-user radio familiarity. |
| Indie canon and lo-fi | Neutral Milk Hotel, Elliott Smith, Pavement/GBV/Yo La Tengo/Built to Spill album and song objects | Packet guidance requires critic-canon indie without letting it swallow normal-user alternative. |
| Shoegaze / dream-pop | Loveless, Souvlaki, Heaven or Las Vegas, Fade Into You, Beach House, A.R. Kane | F16.md was useful only as a misnumbered 073 aid; Packet 010 remains controlling. |
| Female 90s guitar voices | The Breeders, Garbage, The Cranberries, Alanis Morissette boundary rows | Balances riot grrrl, indie-guitar, alt-radio, and pop-adjacent mega-recognition. |
| Post-grunge false-nearby | Creed, Nickelback, Bush, Live, Collective Soul rows carry false_nearby roles | Normal-user familiarity is preserved without promoting radio slop to alternative center. |
| Pop-punk / emo split | Green Day/Offspring/Blink/NOFX/Sum 41 separated from Jimmy Eat World/MCR/Fall Out Boy/Paramore | Avoids collapsing skate-punk, pop-punk, emo, mall emo, and post-hardcore pop. |
| 2000s indie and revival lanes | Blog indie, garage revival, and dark post-punk revival each get dedicated albums/songs | Prevents Strokes/White Stripes/Interpol/Arcade Fire from crowding out adjacent 2000s sublanes. |

## Boundary Risks

| Risk | Handling |
|---|---|
| Post-grunge and modern rock can be strong false positives for alternative taste. | Marked Creed, Nickelback, Bush, Live, Collective Soul, and some radio hits as false_nearby/gateway rather than family anchors. |
| Female 90s alt overlaps pop/persona pop and singer-songwriter. | Alanis Morissette is edge/boundary; PJ Harvey, Liz Phair, Hole, and Sleater-Kinney remain core/standard Family 10 rows. |
| Shoegaze/dream-pop overlaps slowcore, post-punk, and blog indie. | Archetype 073 rows use bridge/boundary roles and explicitly note F16.md's source misnumbering. |
| Pop-punk and emo share Warped Tour and mall-era audiences. | Archetypes 076 and 077 are separated by object function and roles. |
| The Killers, The National, and TV on the Radio are not strict post-punk revival bands. | Kept as boundary/bridge rows under 080 because Packet 010 explicitly asks for dark indie rock coverage. |

## Recommendation

Ready for schema validation and local duplicate-ID review. Do not lock until cross-family ownership and post-grunge false-nearby thresholds are reviewed.
