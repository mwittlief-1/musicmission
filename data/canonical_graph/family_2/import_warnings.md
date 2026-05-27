# Family 2 Import Warnings

## Enum Normalization

| Source shorthand | Normalized handling |
|---|---|
| `Mass anchor` | `roles`: `anchor`; add `artist_anchor`, `album_anchor`, or `song_first` where object-specific. |
| `Song-first`, `Song-first gateway`, `Song-first mass anchor` | `roles`: `song_first`, optionally `gateway` or `anchor`. |
| `Album-object`, `Album-object gateway`, `Album-object mass anchor` | `roles`: `album_anchor`, optionally `gateway`, `anchor`, or `bridge`. |
| `Gateway compilation` | `roles`: `compilation_gateway`, `gateway`. |
| `Bridge artist`, `Bridge object`, `jam bridge` | `roles`: `bridge`; `live_gateway` only where the object is materially live-shaped. |
| `med-high`, `low-med` | Mapped to `medium` or `high` by object recognizability. |
| `high graph`, `cult-high graph` | Mapped to `high` or `cult`; graph value retained in `inclusion_reason`. |
| `Comp: canonical`, `Comp: high` | Album rows use `album_object_type=compilation`; recognition tier mapped to `high`. |

## Slug And Merge Warnings

| Object | Warning |
|---|---|
| `question-mark-and-the-mysterians-96-tears` | Slug expands leading question mark; preserve display artist as `? and the Mysterians`. |
| `the-shadows-of-knight-gloria` | Cover/version-specific row; do not merge with Them's `Gloria`. |
| `the-byrds-mr-tambourine-man` | Byrds recording must not merge with Bob Dylan composition or Dylan recordings. |
| `the-animals-house-of-the-rising-sun` | Arrangement/recording-specific row; do not merge with traditional-song records. |
| `nuggets-original-artyfacts-from-the-first-psychedelic-era-1965-1968` | Compilation object, not an album by a single artist. |
| `nuggets-come-to-the-sunshine` | Later compilation included for canon-shaping, not original 1960s release chronology. |
| `a-hard-days-night` | Album and song share title; proposed IDs include artist prefix for song and album slug for album. |
| `the-doors` | Artist and self-titled album share display name; album ID is `the-doors-the-doors`. |
| `the-stooges-the-stooges` | Artist and self-titled album share display name; preserve album object row. |

## Import Readiness Notes

| Area | Note |
|---|---|
| Required fields | All required artist, album, and song fields are present in `normalized_family_2.json`. |
| Roles | JSON roles use only the allowed enum: `anchor`, `gateway`, `bridge`, `contrast`, `false_nearby`, `boundary`, `deepening`, `song_first`, `album_anchor`, `artist_anchor`, `compilation_gateway`, `live_gateway`. |
| Tiers | JSON recognition tiers use only `mass`, `high`, `medium`, `low`, `cult`; survey tiers use only `core`, `standard`, `edge`, `suppress`. |
| Object types | Album object types use only `studio_album`, `live_album`, `compilation`, `soundtrack`, `ep`. |
| Existing seeds | Source report objects are marked `existing_seed=true`; added missing-obvious objects are marked `existing_seed=false`. |

## Second-Pass Cross-Check Warnings

- Reviewed `F2-2.md` and merged curated additions into `normalized_family_2.json`.
- Several source terms in the second-pass files used non-enum labels such as `broad_anchor`, `tier_2`, `gateway_song`, `album_exception`, `regional_known`, and `specialist_known`; accepted rows were normalized to the approved enum sets.
- Deferred rows remain editorial candidates only. Do not auto-import all second-pass collector/depth suggestions without a separate thresholding pass.
## Status Enum Normalization Addendum

Normalized prior `artist_seeded`, `artist_added`, `artist_not_added`, and `artist_ambiguous_or_traditional` song status shorthand into the requested `artist_survey_worthy`, `song_survey_first`, and `song_survey_only` enum.
