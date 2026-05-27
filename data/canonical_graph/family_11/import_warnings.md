# Import Warnings

## Non-Enum Terms

- None detected in generated rows; role, recognition, survey, album type, and artist survey status fields use the current importer enums.

## Merge / Alias / Version Risks

- F11.md is a null/status report and should not be treated as a candidate source.
- Producer aliases and project names require explicit alias tables: Larry Heard/Mr. Fingers/Fingers Inc., Juan Atkins/Model 500/Cybotron, Kevin Saunderson/Inner City.
- Club rows often need mix/edit specificity; single titles can refer to radio edits, original mixes, remixes, live/DJ-set versions, or viral clips.
- Industrial rows such as Nine Inch Nails are contrast/false-nearby rows here, not the core of Family 11.
- Trip-hop, instrumental hip-hop, synthpop, hyperpop, indie rock, dancehall/global pop, and mainstream pop overlaps need family membership weights preserved.

## Bridge / Contrast / False-Nearby Notes

| archetype_id | warning |
|---|---|
| 081 | Bridge to disco, garage, pop-house, and vocal dance; false-nearby risk is merging producer, vocalist, remix, and project identities. |
| 082 | Bridge to electro, rave, minimal, dub techno, and ambient techno; false-nearby risk is over-weighting specialist techno for normal-user Page 1. |
| 083 | Bridge to festival EDM, big beat, trance, pop features, workout utility, and global dancehall-pop; false-nearby risk is confusing song-first hits with deep electronic affinity. |
| 084 | Bridge to trip-hop, downtempo, instrumental hip-hop, lounge, and nocturnal album listening; false-nearby risk is collapsing all slow electronic into one mood bucket. |
| 085 | Bridge to indie rock, post-punk, bloghouse, electroclash, and dance-punk; false-nearby risk is treating guitar-band danceability as club lineage. |
| 086 | Bridge to synthpop, chillwave, bedroom pop, internet nostalgia, and work/study listening; false-nearby risk is conflating atmosphere with dance utility. |
| 087 | Bridge to IDM, ambient, art pop, industrial, producer canon, and experimental club; false-nearby risk is letting critic canon erase normal-user electronic coverage. |

## Import-Readiness Notes

- All added rows are missing-obvious graph rows and remain `existing_seed = false`.
- Candidate IDs are normalized to lowercase kebab-case and checked for duplicate proposed IDs within each object class.
- Lock still requires source-aligned row review, Page 1/Page 2 ordering, and merge-table confirmation for aliases, covers, remixes, collaborations, live recordings, and language/version variants.
