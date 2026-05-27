# Corrections To Source Report

| Source issue | Correction / import treatment |
|---|---|
| Standalone `F7.md` does not match the dispatch map | Did not use it as a Family 7 source. Packet 007 from `waymark_pass_one_dispatches_families_005_018.md` is authoritative; `F7.md` is treated as an Alternative R&B proxy misalignment only. |
| Packet 007 names artists but does not provide object tables | Instantiated named artists as `existing_seed=true`; instantiated album and song candidates as `existing_seed=false` missing-obvious additions because their titles are not named in Packet 007. |
| `Grandmaster Flash` source shorthand | Imported survey rows using `Grandmaster Flash and the Furious Five` and `Grandmaster Flash & Melle Mel` where recording identity requires it. |
| `Afrika Bambaataa` source shorthand | Imported `Afrika Bambaataa & Soulsonic Force` for `Planet Rock`-centered electro-rap identity. |
| `Tupac` source shorthand | Imported canonical artist display as `2Pac` and retained source alias warning. |
| `Biggie` source shorthand | Imported canonical artist display as `The Notorious B.I.G.` and retained source alias warning. |
| `Master P / No Limit` source shorthand | Imported `Master P` as the artist row and noted No Limit as label/context until label objects are supported. |
| `Cash Money / Juvenile` source shorthand | Imported `Juvenile` as the artist row and noted Cash Money as label/crew context. |
| `Mos Def / Yasiin Bey` source shorthand | Preserved the alias pair in display and slugged as `mos-def-yasiin-bey`. |
| Non-enum source language such as mass anchor, song-first, album-world, radio-first, party-first, false-nearby | Normalized to allowed role, recognition, survey, album type, and song artist status enum values only. |
| Explicit/clean version concerns are source guidance rather than rows | Preserved explicit titles where they are canonical and flagged clean/radio edit handling in warnings. |
