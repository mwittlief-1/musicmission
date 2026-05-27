# Family 12 Corrections to Source Report

| issue_type | existing_report_area | correction |
|---|---|---|
| source package alignment | F12.md | Did not use standalone `F12.md`; Packet 012 from the dispatch is authoritative because the standalone report lacked the taxonomy. |
| seed interpretation | Packet 012 object warnings | Artist objects named in the packet are `existing_seed=true`; album and song rows added from obvious catalog knowledge are `existing_seed=false` unless the packet named the object itself. |
| role normalization | all candidate rows | Normalized context-like labels to allowed roles such as `gateway`, `song_first`, `boundary`, `bridge`, and `false_nearby`. |
| artist name normalization | Beyonce / Pink / Michael Buble-style names | Used ASCII canonical display names and lowercase kebab-case IDs; preserve accented/stylized aliases during import if canonical store supports them. |
| family boundary | holiday/family/shared-listening warnings | Holiday and shared-listening cases are deferred to Family 17 unless the row functions primarily as mainstream pop. |
