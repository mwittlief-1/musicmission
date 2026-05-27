# Family 7 Import Warnings

## Enum Normalization

| Source shorthand / modeling phrase | Normalized handling |
|---|---|
| Mass anchor | `roles`: `anchor`; add `artist_anchor`, `album_anchor`, or `song_first` where object-specific. |
| Song-first, radio-first, party-first | `roles`: `song_first` plus `gateway`, `anchor`, `bridge`, `boundary`, or `false_nearby` as appropriate. |
| Album-world canon | `roles`: `album_anchor`; recognition tier reflects normal-user and specialist recognition separately from influence. |
| Scene/regional anchor | `roles`: `anchor` or `bridge`; archetype membership captures regional lane. |
| False nearby | `roles`: `false_nearby`; survey tier can be `edge` or `suppress` for boundary-only rows. |
| Modern streaming-era reality | `recognition_tier` can be `mass` or `high` even when older critical canon is weaker. |

## Source And Seed Warnings

| Area | Warning |
|---|---|
| Controlling source | Use Packet 007 from the pass-one dispatch. Do not use standalone `F7.md` as Family 7 source because it is an Alternative R&B proxy under the dispatch map. |
| Seed rule | Only artists named in Packet 007 are `existing_seed=true`; album and song rows are `existing_seed=false` because Packet 007 does not name specific album or song titles. |
| Alias rows | `2Pac`, `The Notorious B.I.G.`, `Mos Def / Yasiin Bey`, `Jeezy`, and `Afrika Bambaataa & Soulsonic Force` require alias-aware matching. |
| Label/context rows | No Limit and Cash Money appear in Packet 007 but are handled as context warnings through Master P and Juvenile, not standalone label objects. |

## Explicit, Clean, And Version Warnings

| Object | Warning |
|---|---|
| nwa-fuck-tha-police | Explicit title and lyric content; preserve canonical title and link clean/radio treatment separately if needed. |
| juvenile-feat-mannie-fresh-and-lil-wayne-back-that-azz-up | Clean/radio title variants may differ from explicit canonical title. |
| lil-jon-and-the-east-side-boyz-feat-ying-yang-twins-get-low | Party/club recognition often comes through clean radio edits. |
| cardi-b-feat-megan-thee-stallion-wap | Explicit and clean versions are materially different survey objects. |
| future-fuck-up-some-commas | Explicit title should not be silently sanitized in canonical ID/display mapping. |
| run-dmc-walk-this-way | Run-DMC/Aerosmith version must not merge with Aerosmith original recording. |
| fugees-killing-me-softly | Fugees version must not merge with Roberta Flack or earlier recordings. |
| kid-cudi-day-n-nite | Original and Crookers remix recognition may diverge. |
| migos-versace | Original and Drake-remix recognition may diverge. |
| chief-keef-feat-lil-reese-i-dont-like | Original and Kanye remix should remain distinct if both are imported. |

## Boundary And Ownership Notes

| Boundary | Objects / handling |
|---|---|
| R&B and rap-soul | Fugees, Lauryn Hill, Drake, The Roots, Doja Cat, and `Creepin'` should preserve hip-hop membership while allowing R&B family links. |
| Rock and alternative | Run-DMC `Walk This Way`, Beastie Boys, Cypress Hill, The Roots, Run the Jewels, and Death Grips need rock/alternative boundary links. |
| Electronic and club music | `Planet Rock`, crunk rows, Flo Rida, Travis Scott, and Metro Boomin rows may need dance/electronic adjacency without leaving hip-hop. |
| Internet and meme-era songs | Soulja Boy, Doja Cat, Chief Keef, Lil Uzi Vert, Playboi Carti, and TikTok-era rows should not be dismissed as novelty if they carry real survey recognition. |
| 90s East Coast overcapture | Do not allow Biggie/Nas/Wu/Jay-Z rows to crowd out Southern/trap, pop-rap, old-school, and modern streaming coverage. |

## Import Readiness Notes

| Area | Note |
|---|---|
| Required fields | All required artist, album, and song fields are present in `normalized_family_7.json`. |
| IDs | All proposed IDs are lowercase kebab-case and locally duplicate-free. |
| Enums | Roles, recognition tiers, survey tiers, album object types, and song artist status values are limited to the requested enum sets. |
| Global dry run | Not run for this task, per instruction. |
