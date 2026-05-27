# Import Warnings - Family 6

| warning_type | source_values | normalized_handling |
| --- | --- | --- |
| controlling_source | Packet 006 dispatch; `F6.md`; `F10.md`; `F7.md` | Packet 006 is authoritative. `F6.md` was ignored. `F10.md` and `F7.md` were used only as clearly flagged salvage context. |
| seed_scope | Packet 006 artist names versus inferred albums/songs | Only artist rows explicitly named in Packet 006 are `existing_seed=true`. Albums and songs are non-seed gap-fill rows. |
| source_misalignment_disco | F10.md fallback Disco Continuum proxy | Used only to support obvious 040 additions and warnings. These rows are not source seeds. |
| source_misalignment_alt_rnb | F7.md fallback Alternative R&B proxy | Used only to support obvious 044 additions and warnings. These rows are not source seeds. |
| enum_normalization | dancefloor anchor, cultural furniture, album world, slow jam, quiet storm, New Jack, bedroom R&B, alt-R&B | Collapsed to approved roles and tier enums; style meaning is retained in inclusion_reason and archetype context. |
| duplicate_artist_membership | Marvin Gaye, Diana Ross, Smokey Robinson, Maxwell, Mary J. Blige, Beyonce, Usher | Duplicate proposed artist IDs are intentional archetype memberships, not duplicate canonical artists. |
| era_specific_artist_scope | Bee Gees disco-era; Diana Ross solo; Smokey Robinson solo versus Miracles; Jackson 5 versus Michael Jackson | Preserve artist/era distinction through row warnings and proposed IDs. Do not auto-merge group and solo objects. |
| version_specific_recordings | Respect; Ain't No Mountain High Enough; I Heard It Through the Grapevine; Don't Leave Me This Way; Tyrone live | Preserve recording/version identity rather than merging by composition title. |
| collaboration_crediting | Marvin Gaye & Tammi Terrell; Blackstreet feat. Dr. Dre; SZA feat. Travis Scott; The Roots feat. Erykah Badu | Importer should retain display credits and avoid collapsing featured artists into solo artist rows. |
| album_type_normalization | House of Balloons mixtape; Trilogy compilation of mixtapes; H.E.R. compilation; Saturday Night Fever soundtrack | Used approved album_object_type enum values only; schema may need a future `mixtape` type. |
| soundtrack_context | Saturday Night Fever; Super Fly; That's the Way of the World; Theme from Shaft; Earned It | Soundtrack membership is intentional and should not be converted to ordinary studio-album context. |
| punctuation_and_ascii | H.E.R.; 6LACK; Beyonce; Risque; C'est Chic; Booker T. & the M.G.'s | IDs are lowercase kebab-case ASCII. Display title refinements can be metadata-only later. |
| controversial_high_recognition_gap | R. Kelly and related 1990s R&B objects | Not auto-added in this pass despite high survey recognition. Requires explicit editorial/policy decision before import; possible future rows should likely use `survey_tier=suppress` or controlled presentation. |
| normal_user_contexts | Wedding, family, cookout, karaoke, party, radio-memory, dancefloor | Preserved through high-yield song rows and inclusion reasons; do not reduce this family to critic-canon album rows. |

## Import Notes

- `normalized_family_6.json` parses and uses only the requested enum values.
- Proposed IDs were validated as lowercase kebab-case.
- The global import dry-run script was not run, per task instruction.
