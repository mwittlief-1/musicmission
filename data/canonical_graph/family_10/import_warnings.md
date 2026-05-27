# Family 10 Import Warnings

## Enum Normalization

| Area | Normalized handling |
|---|---|
| Roles | All JSON role values use the requested enum only: `album_anchor`, `anchor`, `artist_anchor`, `boundary`, `bridge`, `compilation_gateway`, `contrast`, `deepening`, `false_nearby`, `gateway`, `live_gateway`, `song_first`. |
| Recognition tiers | All rows use `mass`, `high`, `medium`, `low`, or `cult`. |
| Survey tiers | All rows use `core`, `standard`, `edge`, or `suppress`; no suppress rows were needed. |
| Album object types | Albums use `studio_album` except `Superfuzz Bigmuff`, which is an `ep`. |
| Song artist survey status | Song rows use only `artist_survey_worthy`, `song_survey_first`, or `song_survey_only`. |

## Seed Handling

| Area | Warning |
|---|---|
| Packet 010 artist names | Artist rows named in Packet 010 are marked `existing_seed=true`. |
| Album and song rows | Packet 010 did not name album/song objects, so all album and song candidates are `existing_seed=false`. |
| Added artist anchors | R.E.M., Foo Fighters, Neutral Milk Hotel, The Breeders, Vampire Weekend, Arctic Monkeys, The Killers, and similar additions are `existing_seed=false`. |

## Slug And Merge Warnings

| Object | Warning |
|---|---|
| `weezer-weezer-blue-album` | Weezer has multiple self-titled albums; retain Blue Album disambiguation. |
| `franz-ferdinand-franz-ferdinand` | Artist and album share display title; do not collapse artist and album rows. |
| `the-killers-mr-brightside` | Song has massive karaoke/bar-context afterlife; keep original Killers recording object. |
| `green-day-good-riddance-time-of-your-life` | Acoustic/context use should not split away from Green Day recording without version evidence. |
| `my-chemical-romance-im-not-okay-i-promise` | Parenthetical is part of common display title; slug strips punctuation only. |
| `taking-back-sunday-cute-without-the-e-cut-from-the-team` | Apostrophe/quote variants need display-title normalization. |
| `rancid-and-out-come-the-wolves` | Leading ellipsis stripped in slug; preserve official display title. |
| `husker-du` | ASCII slug used; display metadata may later restore diacritic. |
| `that-dog` | External lowercase/punctuated display variants are expected. |

## Cross-Family Ownership

| Area | Warning |
|---|---|
| R.E.M., The Cure, Husker Du, Jane's Addiction | Strong 80s college/new-wave/hardcore boundaries; Family 10 uses them as alternative source-code. |
| Smashing Pumpkins, Foo Fighters, The Killers, The National | Strong broader rock/pop-rock claims; keep Family 10 as one membership, not exclusive ownership. |
| Alanis Morissette and The Cranberries | Pop/persona and adult-alternative overlap; kept as boundary/gateway rows rather than family center. |
| Beach House and Sufjan Stevens | Blog indie / dream-pop / singer-songwriter overlap; roles mark bridge/deepening behavior. |
| Creed and Nickelback | High familiarity but weak alternative-center signal; false_nearby roles are intentional. |

## Import Readiness Notes

| Area | Note |
|---|---|
| Required fields | All required artist, album, and song fields are present in `normalized_family_10.json`. |
| IDs | Proposed IDs are lowercase kebab-case. |
| Duplicates | No duplicate IDs exist within the artist, album, or song namespaces. Four album/song title collisions remain by existing family convention and require object-type-aware import handling: `neutral-milk-hotel-in-the-aeroplane-over-the-sea`, `cocteau-twins-heaven-or-las-vegas`, `matthew-sweet-girlfriend`, `green-day-american-idiot`. |
| Dry run | The global import dry-run script was intentionally not run per instruction. |
