# Family 9 Import Warnings

## Enum Normalization

| Source / curation shorthand | Normalized handling |
|---|---|
| Packet 009 artist seed list | Source-named artist rows use `existing_seed=true`; album and song instantiations use `existing_seed=false`. |
| Glam/pop-metal hooks | `gateway`, `boundary`, `false_nearby`, and `song_first` roles instead of non-enum pop-metal shorthand. |
| Industrial machine-rock rows | `gateway`, `bridge`, `boundary`, and `deepening` roles only. |
| Extreme gateway rows | `gateway`, `anchor`, `bridge`, `boundary`, and `deepening` roles; no collector-only frontier enum. |

## Slug And Merge Warnings

| Object | Warning |
|---|---|
| `Motorhead / Motley Crue` | Source diacritics normalized to ASCII slugs. Preserve richer display names only if the display layer supports them safely. |
| `black-sabbath` | Artist has memberships in 061 and 064. Import as one canonical artist plus two archetype memberships. |
| `black-sabbath-black-sabbath` | Artist, album, and song can share display text. Use object class and proposed ID to avoid merges. |
| `metallica-metallica` | Black Album self-title must not merge with artist row. |
| `korn-korn, slipknot-slipknot, system-of-a-down-system-of-a-down` | Self-titled album rows require object-class-aware import. |
| `sleep / sleep-token` | Do not merge Sleep with Sleep Token. |
| `death` | Generic artist slug must resolve to the band Death, not the genre label or common word. |
| `hurt` | Nine Inch Nails song row must remain distinct from Johnny Cash cover/version rows in other families. |
| `cum-on-feel-the-noize` | Quiet Riot row is a cover/version-specific glam-metal gateway; do not merge with Slade original if imported elsewhere. |
| `bon-jovi, def-leppard, guns-n-roses, whitesnake, europe, van-halen` | High recognition rows are glam/hard-rock boundary objects; do not use as true-metal anchors by default. |
| `linkin-park, limp-bizkit, papa-roach, rage-against-the-machine` | Nu/rap-metal positives may dead-end; adaptive survey should branch before assuming metalcore, thrash, or extreme affinity. |
| `nine-inch-nails, marilyn-manson, filter, kmfdm` | Industrial/alternative ownership is strong; keep machine-rock rows scoped to Family 9 boundary/gateway behavior. |
| `breaking-benjamin, shinedown, i-prevail` | Modern active-rock false-nearby rows should stay low-weight unless user response confirms heavier taste. |
| `extreme-metal rows` | Gateway policy only. Do not infer exhaustive black/death/grind/sludge scene import from this packet. |

## Import Readiness Notes

| Area | Note |
|---|---|
| Required fields | All required artist, album, and song fields are present in `normalized_family_9.json`. |
| Roles | JSON roles use only the approved role enum. |
| Tiers | Recognition and survey tiers are normalized to the approved enums. |
| Object types | Album rows use only `studio_album`, `live_album`, `compilation`, `soundtrack`, and `ep`; this family currently uses studio, live, compilation, and EP rows. |
| Existing seeds | Packet 009 artist names are preserved as source seeds; added missing-obvious objects are false. |
| Dry run | The global import dry-run script was not run, per task instruction. |
