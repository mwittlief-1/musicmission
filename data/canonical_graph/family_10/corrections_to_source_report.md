# Corrections To Source Report

| Source issue | Correction / import treatment |
|---|---|
| Packet 010 is a guidance packet rather than a tabular source. | Treated named artist objects in Packet 010 as `existing_seed=true`; album and song rows are added missing-obvious candidates with `existing_seed=false`. |
| Standalone `F10.md` exists locally but is not Family 10 under the dispatch map. | Did not use `F10.md`; recorded it as a source-misalignment warning only. |
| `F16.md` discusses shoegaze/dream-pop but is misnumbered relative to the dispatch map. | Used only as a non-controlling aid for archetype 073; did not treat it as Family 16 source authority. |
| Packet uses an en dash in `90s-00s Punk Pop`. | Normalized archetype label to ASCII `90s-00s Punk Pop` for generated artifacts. |
| Packet names several artists without common leading articles: Offspring, White Stripes, Black Keys, Hives, Vines, Libertines, Get Up Kids, Jesus and Mary Chain. | Display names use common canonical forms where appropriate: The Offspring, The White Stripes, The Black Keys, The Hives, The Vines, The Libertines, The Get Up Kids, The Jesus and Mary Chain. |
| `That Dog` may appear externally as `that dog.`. | Stored display as `That Dog` and ID as `that-dog`; flagged punctuation variance. |
| `Husker Du` and `A.R. Kane` require slug care. | Stored ASCII import IDs `husker-du` and `ar-kane`; display-title enrichment can restore diacritics/punctuation later. |
| Packet warns not to over-promote post-grunge radio. | Creed, Nickelback, Bush, Live, Collective Soul, and related songs use `false_nearby`, `gateway`, and edge/standard tiers rather than core alternative-center status. |
| Packet warns critic-prestige indie must not swallow the family. | Indie-canon rows are balanced against normal-user alt radio, grunge, pop-punk, emo, garage revival, and post-punk revival rows. |
