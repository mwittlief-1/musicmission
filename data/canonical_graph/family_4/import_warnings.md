# Import Warnings

| warning_type | source_values | normalized_handling |
| --- | --- | --- |
| source_enum_normalization | artist anchor, bridge anchor, gateway artist, late bridge artist, contrastive bridge, deeper bridge, false-nearby bridge, song-first furniture, writer-first object, late monoculture object, album-world anchor, late bridge album, historical anchor, protest anchor, specialty gateway, scene-defining song, monoculture object | Mapped to requested roles enum combinations such as artist_anchor, album_anchor, song_first, gateway, bridge, contrast, false_nearby, boundary, deepening. |
| recognition_tier_normalization | broad, selective, selective-broad, canonical, canonical/high, high/scene, broad/selective, mass/canonical, selective/high, scene-high | Collapsed to mass, high, medium, low, or cult. Canonical status is represented through survey_tier/core and inclusion_reason rather than a separate enum. |
| survey_tier_inference | survey_priority very high, high, medium-high plus confidence values | Converted to row-level survey_tier core, standard, edge, suppress using archetype role and import confidence. |
| album_type_normalization | studio, gateway album, bridge album, album-world anchor, depth album, late bridge album | Source album_type studio mapped to studio_album. Role-like album labels moved to roles/inclusion_reason. |
| date_normalization | 1940/1944, 20th c., traditional, 1998/2000 US breakthrough | release_year uses an integer where defensible and null where attribution/date is traditional or unstable; row warnings preserve ambiguity. |
| collaboration_and_version_risk | Wilco with Billy Bragg, Pete Seeger et al. / traditional, Pete Seeger and Lee Hays; Peter Paul and Mary popularized, Jason Isbell and the 400 Unit | Artist name retained as supplied when needed; import should not collapse collaborations into solo artist rows without manual confirmation. |
| duplicate_cross_archetype_objects | Carole King, Bob Dylan, John Prine, Norah Jones, Tapestry, The Freewheelin Bob Dylan, Come Away with Me, Blowin in the Wind, Dont Know Why | Kept as separate archetype placements with distinct proposed IDs. Consolidation should happen only at a later canonical entity layer. |

## Second-Pass Cross-Check Warnings

- Reviewed `F4-2.md` and merged curated additions into `normalized_family_4.json`.
- Several source terms in the second-pass files used non-enum labels such as `broad_anchor`, `tier_2`, `gateway_song`, `album_exception`, `regional_known`, and `specialist_known`; accepted rows were normalized to the approved enum sets.
- Deferred rows remain editorial candidates only. Do not auto-import all second-pass collector/depth suggestions without a separate thresholding pass.
## Status Enum Normalization Addendum

Normalized prior `artist_seeded`, `artist_added`, `artist_not_added`, and `artist_ambiguous_or_traditional` song status shorthand into the requested `artist_survey_worthy`, `song_survey_first`, and `song_survey_only` enum.
