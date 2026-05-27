# Import Warnings

## Non-Enum Terms

- None detected in generated rows; role, recognition, survey, album type, and artist survey status fields use the current importer enums.

## Merge / Alias / Version Risks

- F5.md is misaligned to soul/R&B/funk/disco and is retained only as a correction note, not as candidate evidence.
- Taylor Swift rows are early-country-pop only; do not classify her full career as Family 5.
- `Wagon Wheel`, `Tennessee Whiskey`, `Act Naturally`, `Me and Bobby McGee`, and `How Do I Live` require composition/recording/version handling.
- Darius Rucker solo catalog must remain distinct from Hootie & the Blowfish.
- David Allan Coe, `Okie from Muskogee`, and some bar/patriotic-context songs need content and context review before Page 1 surfacing.
- Americana, southern rock, folk, Christian, and country-pop boundaries remain active false-nearby risks.

## Bridge / Contrast / False-Nearby Notes

| archetype_id | warning |
|---|---|
| 031 | Bridge to folk foundations, rockabilly, western/cowboy song, and country-pop standards; false-nearby risk is treating every old rural song as country survey core. |
| 032 | Bridge to singer-songwriter, southern rock, folk, and Americana; false-nearby risk is collapsing outlaw, cosmic country, and Red Dirt into one bucket. |
| 033 | Bridge to adult contemporary, 90s/2000s pop, wedding songs, and family memory; false-nearby risk is overclassifying all crossover pop as country. |
| 034 | Bridge to line dance, hat-act radio, new traditionalism, and patriotic/bar contexts; false-nearby risk is mistaking novelty recognition for artist depth. |
| 035 | Bridge to streaming-era pop, rock, hip-hop cadence, worship-adjacent uplift, and arena radio; false-nearby risk is treating modern country as disposable rather than survey-useful. |
| 036 | Bridge to Texas country, Red Dirt, indie folk, alt-country, and roots singer-songwriters; false-nearby risk is letting Americana swallow mainstream country affinity. |

## Import-Readiness Notes

- All added rows are missing-obvious graph rows and remain `existing_seed = false`.
- Candidate IDs are normalized to lowercase kebab-case and checked for duplicate proposed IDs within each object class.
- Lock still requires source-aligned row review, Page 1/Page 2 ordering, and merge-table confirmation for aliases, covers, remixes, collaborations, live recordings, and language/version variants.
