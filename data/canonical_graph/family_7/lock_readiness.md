# Family 7 Lock Readiness

## Judgment

Status: `dry_run_ready_not_locked`

Family 7 is ready for local schema validation and importer staging. It should not be locked until explicit/clean version handling, feature-credit ownership, and cross-family boundaries have been reviewed.

## Checks

| Check | Status | Notes |
|---|---|---|
| Required files present | Pass | Eight requested files are generated under `data/canonical_graph/family_7/`. |
| JSON import shape | Pass | Metadata plus `artists`, `albums`, and `songs` arrays. |
| Required row fields | Pass | Required fields are present by object type. |
| Role enum compliance | Pass | Rows use only the provided role enum values. |
| Tier enum compliance | Pass | Recognition and survey tiers use only normalized values. |
| Album object type compliance | Pass | Album rows use only studio_album, live_album, compilation, soundtrack, or ep; Family 7 currently uses studio_album only. |
| Song artist status compliance | Pass | Songs use only artist_survey_worthy, song_survey_first, or song_survey_only. |
| Slug normalization | Pass | Proposed IDs are lowercase kebab-case. |
| Seed preservation | Pass | Packet-named artists are `existing_seed=true`; album/song additions are `existing_seed=false` because Packet 007 names no titles. |
| Duplicate IDs | Pass | Local generator found no duplicate proposed artist, album, or song IDs. |
| Source alignment | Pass | Packet 007 used as controlling source; standalone `F7.md` not used. |
| Version ambiguity | Needs review | Explicit/clean edits, remixes, soundtrack contexts, and feature-heavy tracks need importer merge policy. |
| Cross-family ownership | Needs review | R&B, pop, rock, electronic, club, and internet-era boundary rows need editorial ownership review. |

## Lock Blockers

| Blocker | Required action |
|---|---|
| Explicit versus clean recognition | Confirm canonical recording/version model for radio edits and clean titles. |
| Feature and producer crediting | Confirm primary artist handling for Dre, Metro Boomin, Nate Dogg, UGK, Madvillain, Rich Gang, and multi-artist streaming hits. |
| Cross-family boundaries | Review R&B/pop rows for Fugees, Lauryn Hill, Drake, Doja Cat, Flo Rida, and The Roots; review rap-rock rows for Beastie Boys, Run-DMC, Cypress Hill, and Run the Jewels. |
| Standalone source misalignment | Keep `F7.md` excluded from Family 7 import unless the dispatch map is formally corrected. |

## Lock Recommendation

Run family-local JSON/schema checks first, then run the approved importer staging workflow when Family 7 is allowed into the global batch. Do not run the global import dry-run from this task.
