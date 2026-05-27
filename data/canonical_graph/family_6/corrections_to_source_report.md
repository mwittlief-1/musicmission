# Corrections To Source Report - Family 6

| source_issue | correction |
| --- | --- |
| `F6.md` says Family 6 was unspecified | Ignored `F6.md` as requested. Packet 006 in the dispatch file is the controlling source. |
| Packet 006 is guidance, not row tables | Instantiated a conservative importable universe using Packet 006's archetypes and object warnings. |
| Packet 006 names artist objects but not album/song objects | Marked only explicitly named artist objects as `existing_seed=true`; all album and song rows are `existing_seed=false`. |
| F10.md has a disco-continuum fallback report, not a verified Family 6 source | Used it only as salvage context for archetype 040 additions such as Sylvester and Sister Sledge; these rows remain `existing_seed=false` and are flagged in warnings. |
| F7.md has an Alternative R&B fallback report, not a verified Family 6 source | Used it only as salvage context for archetype 044 additions such as FKA twigs, Kelela, Tinashe, PARTYNEXTDOOR, Bryson Tiller, 6LACK, and Daniel Caesar; these rows remain `existing_seed=false`. |
| Non-enum source language such as dancefloor, cultural furniture, album-world, song gateway, adult soul, and dark R&B | Normalized row roles to the approved enum set: `anchor`, `artist_anchor`, `album_anchor`, `gateway`, `bridge`, `boundary`, `deepening`, `song_first`, `compilation_gateway`, `live_gateway`. |
| Source uses R&B and era labels that are not import enums | Preserved those meanings in archetype IDs, inclusion reasons, and consolidation warnings rather than creating new enum values. |
| Album object type lacks `mixtape` | Normalized `House of Balloons` to `ep` and flagged the schema limitation. `Trilogy` and `H.E.R.` are compilation rows. |
| Non-ASCII public spellings | Rendered Beyonce and Risque in ASCII for import stability; display/style corrections can be handled at metadata layer if needed. |
| Punctuation-heavy artist IDs | Normalized H.E.R. to `h-e-r`, Booker T. & the M.G.'s to `booker-t-and-the-mgs`, KC and the Sunshine Band to `kc-and-the-sunshine-band`, and 6LACK to `6lack`. |
| Era-specific artist scope | Scoped Bee Gees to disco-era membership in 040 and Diana Ross solo disco membership separately from Supremes/Motown membership. |
| Collaboration/version-specific songs | Preserved artist-credit specificity for Marvin Gaye & Tammi Terrell, The Roots feat. Erykah Badu, SZA feat. Travis Scott, and Blackstreet feat. Dr. Dre. |
