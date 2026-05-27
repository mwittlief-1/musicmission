# Family Inclusion Recommendation Alpha v0

Version: `alpha_v0`

Status: `frozen_for_alpha_consumable_layer`

This recommendation controls which canonical graph family surfaces may feed trusted Alpha Survey display and app/local first Mission Generation candidate pools.

## Included by Default

These families are eligible for default Alpha Survey and first Mission Generation, subject to quarantine, dedupe, version, role/risk, and `music_object_ref` checks:

| family_id | family | Recommendation | Rationale |
| --- | --- | --- | --- |
| 1 | Early Rock, Oldies, Doo-Wop, Pre-Beatles Pop | include | High recognition and source-version policy covered by sidecars/quarantine. |
| 2 | Beatles, British Invasion, 60s Pop-Rock | include | Strong trunk recognition; thin/adaptive archetypes are not anchor-eligible. |
| 3 | Classic Rock, Album Rock, Progressive Rock | include | Strong album/artist/song survey utility. |
| 4 | Singer-Songwriter, Folk, Americana, Adult Songcraft | include | Useful for album-world and songcraft branching; traditional rows guarded. |
| 5 | Country | include | Broad Alpha utility; cover/version cases guarded. |
| 6 | Soul, Funk, Disco, R&B Foundations | include | Repaired Page 1 trunk anchors; group/solo/version risks sidecar-controlled. |
| 7 | Hip-Hop | include | Strong survey utility; explicit/clean and cover/collab risks guarded. |
| 8 | Punk, Hardcore, Post-Punk, New Wave | include | Good bridge value into alt/indie; hardcore/noise handled as conditional probes. |
| 9 | Metal and Heavy Music | include | Strong boundary and intensity signal value; version risks guarded. |
| 10 | Alternative, Indie, Grunge, Emo | include | Core Waymark lineage value; grunge archetype remains conditional probe where needed. |
| 12 | Pop Monoculture and Persona Pop | include | Repaired toward high-recognition pop trunk anchors. |
| 18 | Modern Rock, Current Discovery, Internet-Native Scenes | include | Useful for current-discovery testing when candidates pass resolver checks. |

## Included With Caution

These families may be included, but Mission Generation and resolver handling should preserve their extra ambiguity:

| family_id | family | Recommendation | Caution |
| --- | --- | --- | --- |
| 11 | Electronic, Dance, Club, Industrial, Experimental Pop | include_with_caution | Mix/edit/remix specificity can change the object being tested. |
| 13 | Latin, Caribbean, Global Pop | include_with_caution | Language, remix, collaboration, and regional credit variants require care. |
| 14 | Jazz, Standards, Vocal, Classical-Adjacent | include_with_caution | Work/composition/recording distinction matters. |
| 16 | Christian, Worship, Gospel | include_with_caution | Worship standards, church brands, live/congregational versions, and songwriter/performance splits require care. |

## Concierge / Context Only

These families must not feed default first Mission Generation or Fast Survey.

| family_id | family | Recommendation | Rationale |
| --- | --- | --- | --- |
| 15 | Soundtrack, Theater, Musicals, Family Context | concierge_context_only | Cast/show/film/score/source-song modeling is context-first and special-entity heavy. |
| 17 | Nostalgia, Novelty, Context, Shared Listening | concierge_context_only | Use-case/context lane rather than default taste-canon lane. |

## Product Boundary

Inclusion means “eligible to ask questions,” not “user likes this family.” Survey and Mission responses create provisional evidence only.
