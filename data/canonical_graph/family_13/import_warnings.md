# Import Warnings

## Non-Enum Terms

- None detected in generated rows; role, recognition, survey, album type, and artist survey status fields use the current importer enums.

## Merge / Alias / Version Risks

- F13.md is a null/status report; F9.md is Afrobeats-relevant but family-misaligned, so neither produces `existing_seed = true` rows.
- Language versions, remixes, and collaboration credits are high-risk in Family 13: `Despacito`, `Bailando`, `Danza Kuduro`, `Love Nwantiti`, `AMG`, `Bebe Dame`, and `7 Seconds` need recording-level care.
- Do not over-U.S.-center Family 13: regional centrality can outweigh U.S. chart recognition.
- Afrobeat, Afrobeats, Afropiano, African pop, and global-roots rows must remain distinct enough for adaptive survey interpretation.
- K-pop/J-pop group names, solo careers, anime ties, legal/group-history issues, and fandom recognition should not be flattened into one Asian-pop bucket.
- World-fusion rows such as Deep Forest require sampling/ethics/version review before import lock.

## Bridge / Contrast / False-Nearby Notes

| archetype_id | warning |
|---|---|
| 094 | Bridge to reggaeton, Latin pop, EDM, Brazilian pop/funk, English-language pop, and dancefloor hits; false-nearby risk is treating all Spanish-language pop as urbano. |
| 095 | Bridge to ranchera, norteño, banda, Tejano, corridos tumbados, and family/community contexts; false-nearby risk is flattening regional Mexican into one streaming-era corrido lane. |
| 096 | Bridge to salsa, mambo, merengue, bachata, Latin dance, and tropical pop; false-nearby risk is merging cover standards and dance forms by title alone. |
| 097 | Bridge to Afrobeat, Afrobeats, Afropiano, Afro-R&B, African pop, and global streaming hits; false-nearby risk is using Afrobeats as a generic African-pop tag. |
| 098 | Bridge to K-pop idol systems, J-pop/anime, Asian pop crossover, metal/fandom edges, and song-first viral hits; false-nearby risk is overfitting fandom intensity as mass recognition. |
| 099 | Bridge to diaspora roots, global folk, reggae, qawwali, Malian blues, flamenco-rumba, and world-fusion; false-nearby risk is treating this as a leftover appendix rather than real survey territory. |

## Import-Readiness Notes

- All added rows are missing-obvious graph rows and remain `existing_seed = false`.
- Candidate IDs are normalized to lowercase kebab-case and checked for duplicate proposed IDs within each object class.
- Lock still requires source-aligned row review, Page 1/Page 2 ordering, and merge-table confirmation for aliases, covers, remixes, collaborations, live recordings, and language/version variants.
