# Family 17 Corrections to Source Report

| issue_type | existing_report_area | correction |
|---|---|---|
| source package alignment | F17.md | Did not use standalone `F17.md`; Packet 017 from the dispatch is authoritative because the standalone report lacked the taxonomy. |
| seed interpretation | Packet 017 object warnings | Named artist/title/context objects are `existing_seed=true` when instantiated; missing-obvious supporting artists, albums, and songs are `existing_seed=false`. |
| context role normalization | family guidance | No non-schema `context` role was used; context meaning is expressed with `song_first`, `false_nearby`, `gateway`, `boundary`, and survey-tier caps. |
| artist name normalization | Jose Feliciano / Michael Buble | Used ASCII display names and lowercase kebab-case IDs; preserve accented aliases during canonical import if supported. |
| composition handling | kids/traditional songs | Rows such as `The Wheels on the Bus` require composition/standard handling rather than a normal artist recording merge. |
