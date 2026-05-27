# Corrections To Source Report

| Source issue | Correction / import treatment |
|---|---|
| `Needles and Pins` appears in both the British Invasion Core and Merseybeat/Jangle sections. | Import once as `the-searchers-needles-and-pins`; preserve `existing_seed=true`. |
| `Bus Stop` appears in both the British Invasion Core and Merseybeat/Jangle sections. | Import once as `the-hollies-bus-stop`; preserve `existing_seed=true`. |
| The `She's Not There` row is malformed in the source table, with an extra `The Zombies` value before the year. | Import as song title `She's Not There`, artist `The Zombies`, release_year `1964`. |
| Several source rows use `med-high`, `low-med`, `high graph`, and `cult-high graph` in object-level importance. | Normalize to allowed recognition tiers: `medium`, `high`, `cult`, or `mass`; retain nuance in `inclusion_reason` and warnings. |
| Source roles include non-enum phrases such as `Mass anchor`, `Song-first gateway`, `Album-object`, `Gateway compilation`, `jam bridge`, and `Bridge object`. | Normalize to allowed JSON role enum values only. |
| `Gloria` is represented by The Shadows of Knight. | Keep as a distinct cover/version object: `the-shadows-of-knight-gloria`; do not merge with Them's original recording. |
| `Nuggets: Come to the Sunshine` is a 2017 compilation outside the 1960s release window. | Retain as `existing_seed=true` compilation gateway because the source explicitly uses it as a validation/curation object for sunshine psych. |
| `The Velvet Underground & Nico` album artist can be represented as The Velvet Underground or The Velvet Underground & Nico. | Preserve source artist text on the album row; added artist anchor uses `The Velvet Underground`. |
| Artist name `? and the Mysterians` contains punctuation that is not slug-friendly. | Normalize slug segment to `question-mark-and-the-mysterians`. |
| Diacritic in `Walk Away Renee` may appear as `Renée` in external sources. | Import title stored as ASCII `Walk Away Renee`; flag for display-title enrichment if the app supports diacritics. |
