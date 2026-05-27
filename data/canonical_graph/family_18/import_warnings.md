# Import Warnings

## Non-Enum Terms

- None detected in generated rows; role, recognition, survey, album type, and artist survey status fields use current importer enums.

## Source Alignment

- Packet 018 is controlling. F18.md is a null/status report with no aligned family mapping or row seeds.
- Treat every `existing_seed=false` row as gap-fill candidate data until an aligned row source or QA review promotes it.

## Merge / Alias / Version Risks

- Turnstile: Hardcore, alternative, and current-rock memberships should remain distinct.
- MJ Lenderman: Solo artist and Wednesday member rows should not merge.
- Adrianne Lenker: Solo Big Thief overlap should remain multi-membership.
- Foster the People: 2010s indie-pop hit can be false nearby for modern psych appetite.
- Royal Blood: Modern rock/active-rock bridge; may also fit 118.
- Deftones: Legacy/nu-metal resurgence should not be treated as current active-rock only.
- Grimes: Earlier alt-pop/electronic identity bridges into but predates hyperpop boom.
- Porter Robinson: EDM, electro-pop, and internet-emotional pop overlap.
- Lo-fi Girl: Channel/use-case shelf, not an ordinary artist entity.
- Boards of Canada: Ambient/electronic catalog object can be false nearby for study-beats use-case.
- Torches - Foster the People: Pumped Up Kicks recognition exceeds album/artist depth for many users.
- White Pony - Deftones: Legacy row included as modern-platform false nearby.
- lofi hip hop radio - Lo-fi Girl: Playlist/channel object, not ordinary album canon.
- Music Has the Right to Children - Boards of Canada: Ambient/electronic catalog bridge, not algorithmic study-beats proof by itself.
- Beggin' - Maneskin: Preserve Maneskin recording distinct from Four Seasons original.
- She's Leaving You - MJ Lenderman: Solo artist and Wednesday overlap.
- Pumped Up Kicks - Foster the People: Song-first indie-pop hit can be a false nearby for psych/groove appetite.
- Change (In the House of Flies) - Deftones: Legacy/platform-resurgence row; not current active-rock proof by itself.
- lofi hip hop radio - Lo-fi Girl: Use-case/channel object, not a conventional song recording.
- Roygbiv - Boards of Canada: Ambient/electronic catalog bridge, not lofi-study shelf by itself.

## Import Readiness Notes

- Largest remaining gap: The largest remaining gap is freshness control: fast-moving 2020s scenes and lo-fi/use-case shelves need periodic review so niche discourse does not distort Page 1 ordering.
- Duplicate object IDs across families should be interpreted as multi-membership unless a warning says the display names or source versions conflict.
