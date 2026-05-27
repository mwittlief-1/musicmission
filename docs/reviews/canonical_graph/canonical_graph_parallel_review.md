# Waymark Canonical Graph Parallel Review

Generated: 2026-05-19

Scope: Families 1-18, using the existing Family 1-4 work plus the new iCloud dispatch and supplemental family files.

## Source Inputs

Controlling taxonomy for Families 5-18:

- `/Users/matt_wittlief_home/Library/Mobile Documents/com~apple~CloudDocs/waymark_pass_one_dispatches_families_005_018.md`

Earlier family sources:

- `/Users/matt_wittlief_home/Library/Mobile Documents/com~apple~CloudDocs/waymark_family_1_latest_corpus_for_codex_2026-05-19.md`
- `/Users/matt_wittlief_home/Library/Mobile Documents/com~apple~CloudDocs/Family2.md`
- `/Users/matt_wittlief_home/Library/Mobile Documents/com~apple~CloudDocs/Family3.md`
- `/Users/matt_wittlief_home/Library/Mobile Documents/com~apple~CloudDocs/Family4.md`
- `/Users/matt_wittlief_home/Library/Mobile Documents/com~apple~CloudDocs/F2-2.md`
- `/Users/matt_wittlief_home/Library/Mobile Documents/com~apple~CloudDocs/F3-2.md`
- `/Users/matt_wittlief_home/Library/Mobile Documents/com~apple~CloudDocs/F4-2.md`

New iCloud supplemental files checked:

- `F5.md`, `F6.md`, `F7.md`, `F8.md`, `F9.md`, `F10.md`, `F11.md`, `F12.md`, `F13.md`, `F14.md`, `F16.md`, `F17.md`, `F18.md`

Source alignment note:

- `F5.md` describes a soul/R&B/funk/disco provisional family, so it was not imported as Country seed data.
- `F7.md` describes alternative R&B and was documented as misaligned for Hip-Hop.
- `F8.md` describes art-pop/creator-context material and was documented as misaligned for Punk/Post-Punk/New Wave.
- `F9.md` describes Afrobeats and was used only as supplemental context for Family 13, not Metal.
- `F10.md` describes disco-continuum material and was used only where it aligned with Family 6, not Alternative/Indie.
- `F11.md`, `F13.md`, and `F14.md` are mostly null/status reports and do not provide row-level seeds.
- `F16.md` describes dream pop/shoegaze and was not imported as Christian/Gospel seed data.

## Validation Summary

Required eight-file shape exists for all 18 family directories:

- `gap_summary.md`
- `artist_candidates.md`
- `album_candidates.md`
- `song_candidates.md`
- `corrections_to_source_report.md`
- `lock_readiness.md`
- `normalized_family_<family_id>.json`
- `import_warnings.md`

Final dry-run command:

```sh
python3 scripts/canonical_graph_import_dry_run.py
```

Final dry-run result:

| result | count |
|---|---:|
| imported family files | 18 |
| validation errors | 0 |
| validation warnings | 9 |
| composition/title review rows | 24 |
| canonical artists | 1499 |
| canonical albums | 1207 |
| canonical song recordings | 1917 |
| artist memberships | 1612 |
| album memberships | 1245 |
| song memberships | 1983 |
| families remaining | 0 |

Dry-run outputs:

- `data/canonical_graph/import_dry_run/import_dry_run_report.md`
- `data/canonical_graph/import_dry_run/merge_review_queue.md`
- `data/canonical_graph/import_dry_run/canonical_graph_manifest.json`

## Per-Family Row Counts

| family | scope | artists | albums | songs | total rows | source seeds | added rows |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | Early Rock, Oldies, Doo-Wop, Pre-Beatles Pop | 247 | 124 | 377 | 748 | 563 | 185 |
| 2 | Beatles, British Invasion, 60s Pop-Rock | 43 | 52 | 72 | 167 | 65 | 102 |
| 3 | Classic Rock, Album Rock, Progressive Rock | 136 | 117 | 150 | 403 | 277 | 126 |
| 4 | Singer-Songwriter, Folk, Americana, Adult Songcraft | 113 | 85 | 126 | 324 | 202 | 122 |
| 5 | Country | 88 | 56 | 89 | 233 | 0 | 233 |
| 6 | Soul, Funk, Disco, R&B Foundations | 107 | 71 | 139 | 317 | 63 | 254 |
| 7 | Hip-Hop | 97 | 104 | 174 | 375 | 68 | 307 |
| 8 | Punk, Hardcore, Post-Punk, New Wave | 92 | 81 | 96 | 269 | 0 | 269 |
| 9 | Metal and Heavy Music | 129 | 139 | 170 | 438 | 48 | 390 |
| 10 | Alternative, Indie, Grunge, Emo | 98 | 89 | 128 | 315 | 66 | 249 |
| 11 | Electronic, Dance, Club, Industrial, Experimental Pop | 103 | 70 | 89 | 262 | 0 | 262 |
| 12 | Pop Monoculture and Persona Pop | 54 | 36 | 50 | 140 | 43 | 97 |
| 13 | Latin, Caribbean, Global Pop | 84 | 54 | 82 | 220 | 0 | 220 |
| 14 | Jazz, Standards, Vocal, Classical-Adjacent | 41 | 32 | 43 | 116 | 0 | 116 |
| 15 | Soundtrack, Theater, Musicals, Family Context | 39 | 33 | 47 | 119 | 0 | 119 |
| 16 | Christian, Worship, Gospel | 39 | 29 | 44 | 112 | 0 | 112 |
| 17 | Nostalgia, Novelty, Context, Shared Listening | 35 | 22 | 42 | 99 | 35 | 64 |
| 18 | Modern Rock, Current Discovery, Internet-Native Scenes | 67 | 51 | 65 | 183 | 0 | 183 |

## Largest Remaining Gaps

| family | largest remaining gap |
|---:|---|
| 1 | Source-version split rules, alias/disambiguation, and compilation gateway policy. |
| 2 | Cross-family ownership for Beatles, Beach Boys, Dylan, Hendrix, Doors, Cream, Pink Floyd, Velvet Underground, Stooges, and Grateful Dead. |
| 3 | Duplicate-membership semantics and thresholding to prevent album-rock/prog/Page 2 bloat. |
| 4 | Traditional/protest standards, cover-version attribution, and unstable/null release-year handling. |
| 5 | Western swing, bluegrass, country gospel, deeper Bakersfield, and Tejano-country edges. |
| 6 | Era-specific artist scope for solo/group Motown, disco-era transformations, and live/single version handling. |
| 7 | Explicit/clean versions, aliases, remix splits, and collaboration-specific recordings. |
| 8 | Targeted depth pass complete; remaining work is alias/version consolidation, cross-family boundary QA, and Page 2 thresholding. |
| 9 | Extreme-metal depth and cover/version handling for glam/industrial/alt-metal gateway songs. |
| 10 | Family 8/9/11 boundaries and suppressing collector-only indie/post-hardcore tails. |
| 11 | Industrial, ambient, drum-and-bass, garage, trance, and regional club scenes remain bridge/contrast coverage. |
| 12 | Persona-pop recency control and solo/group credit handling, especially Beyonce/Destiny-era objects. |
| 13 | South Asian, MENA, Brazilian, reggae/dancehall, and non-Afrobeats African regional coverage remain thin. |
| 14 | Recording-level standard attribution and composition-versus-recording splits. |
| 15 | Entity modeling across show, cast recording, film, soundtrack album, composer, fictional performer, and pop recording. |
| 16 | Worship standard/version policy across live, church-brand, songwriter, and congregational versions. |
| 17 | Traditional/kids/holiday repertoire needs composition-level handling where performer is not meaningful. |
| 18 | Freshness control for fast-moving 2020s scenes and lo-fi/use-case shelves. |

## Import-Readiness Score

| family | score | judgment |
|---:|---:|---|
| 1 | 82/100 | Staging-ready; not hard-locked until duplicate membership and source-version rules are confirmed. |
| 2 | 80/100 | Broad enough for staging; needs version-aware cover and compilation/live policy. |
| 3 | 73/100 | Strong coverage, higher duplicate-membership and thresholding risk. |
| 4 | 78/100 | Staging-ready with manual review for traditional and cover-version rows. |
| 5 | 76/100 | Importable expanded pass; no aligned source seeds, so needs Country-specific second pass before lock. |
| 6 | 82/100 | Strong staging candidate; needs alias/version policy for Motown, disco, and R&B transitions. |
| 7 | 81/100 | Strong staging candidate; explicit/clean/remix/collaboration handling is the lock blocker. |
| 8 | 82/100 | Targeted depth pass completed; staging-ready but hard lock waits for alias/version consolidation and boundary QA. |
| 9 | 82/100 | Strong staging candidate; extreme/deep metal and cover-version issues remain. |
| 10 | 80/100 | Strong staging candidate; needs cross-family boundary QA with 8, 9, 11, and 18. |
| 11 | 77/100 | Importable expanded pass; club alias, mix/edit, and missing regional scenes remain. |
| 12 | 80/100 | Importable and broad; needs recency and persona-pop thresholding. |
| 13 | 75/100 | Importable global-pop pass; uneven regional coverage remains. |
| 14 | 74/100 | Importable but composition/recording standards are high-risk. |
| 15 | 73/100 | Importable but source-entity modeling is not lock-ready. |
| 16 | 74/100 | Importable but worship standard/version modeling is not lock-ready. |
| 17 | 76/100 | Importable; holiday/novelty/kids composition handling remains. |
| 18 | 76/100 | Importable; needs freshness cadence and current-scene QA. |
| Overall | 78/100 | Full corpus is dry-run ready with warnings. No family should be claimed as final lock yet. |

## Schema Drift Issues

| issue | affected families | action |
|---|---|---|
| Source reports and supplemental reports sometimes did not match controlling family numbers. | 5, 7, 8, 9, 10, 16 | Used dispatch packet as controlling source; documented misalignment in corrections/import warnings. |
| Source role and status shorthand did not match current enums. | 1-4 plus inherited source rows | Normalized to allowed role, recognition, survey, album-type, and song-status enums. |
| Several generated families have no aligned row-level seeds. | 5, 8, 11, 13, 14, 15, 16, 18 | Rows are marked `existing_seed=false`; treat as graph-production expansion, not source-preserved seed imports. |
| Traditional/standard/show/songbook objects do not always have stable artist ownership. | 4, 14, 15, 16, 17 | Route through composition/recording-aware QA before hard lock. |
| Live, compilation, cast, soundtrack, and score albums are canonical gateway objects but not standard studio albums. | 1, 2, 3, 5, 6, 14, 15, 16, 17 | Importer accepts object types; editorial policy still needs lock review. |
| Artist aliases, group/solo splits, and project names produce display-name drift. | 1, 6, 7, 11, 12, 15, 16 | Build alias tables before production import. |

Current dry-run warnings:

- Two Family 4 traditional/revival-circuit songs have `release_year=null`.
- Display/source-name drift exists for Kool & The Gang, Martha & the Vandellas, Simon & Garfunkel, Smokey Robinson & The Miracles, and `Here Are The Sonics`.
- `Dancing in the Street` has artist-name display drift.
- `Man! I Feel Like a Woman!` has a 1997/1999 release-year conflict.

## Duplicate / Merge Risks

| risk area | examples | handling |
|---|---|---|
| Duplicate canonical IDs across memberships | 107 duplicate artist IDs, 38 duplicate album IDs, 65 duplicate song IDs | Expected; import canonical entities plus membership rows, not family-local entities. |
| Same-title songs across different recordings/compositions | `Gloria`, `Hound Dog`, `House of the Rising Sun`, `The Twist`, `Walk This Way`, `Zombie`, `Oblivion`, `God Only Knows`, `We Don't Talk About Bruno` | Keep `merge_review_queue.md` as manual QA; never title-merge automatically. |
| Covers and famous alternate recordings | `I Will Always Love You`, `Tainted Love`, `Cum On Feel the Noize`, `Beggin'`, `Hurt`, `Fancy`, `Pancho and Lefty` | Preserve recording-specific IDs and warnings. |
| Artist aliases and project names | 2Pac/Tupac, Mos Def/Yasiin Bey, Mr. Fingers/Larry Heard, Model 500/Juan Atkins, Hillsong brands, group/solo Motown artists | Build alias/split table before hard lock. |
| Soundtrack/show/cast entity splits | `Hamilton`, `Wicked`, `Frozen`, `Encanto`, `Black Panther`, `Guardians of the Galaxy`, `James Bond Theme` | Model show/film, soundtrack album, score album, cast recording, and pop recording separately where needed. |
| Standards, hymnals, and traditional repertoire | `Amazing Grace`, `We Shall Overcome`, `My Favorite Things`, `Nessun dorma`, `In Christ Alone`, `Shout to the Lord` | Require composition-first or standard-first review before import lock. |
| Fast-moving modern scenes | hyperpop, modern active rock, internet mood/lo-fi, TikTok pop | Add recency QA cadence and avoid over-promoting short-lived virality. |

## Lock-Readiness Recommendation

Do not claim final lock for any family.

The full corpus is now suitable for staging import and importer-contract testing because:

- all 18 normalized JSON files parse;
- all required row fields are present;
- enum normalization is enforced;
- lowercase kebab-case IDs are present;
- canonical entity plus membership-table dry run succeeds with 0 validation errors;
- merge-review and warning queues exist.

The corpus is not final-lock ready because:

- many families still need source-aligned second-pass reports;
- duplicate and same-title risks require human review;
- alias/split tables are not yet canonicalized;
- composition/recording policy is not complete for standards, worship, theater, soundtrack, and traditional repertoire;
- current/streaming-era families need freshness controls.

## Recommended Next Dispatch

| family | next dispatch |
|---:|---|
| 1 | QA source-version splits and early-rock alias rules from `merge_review_queue.md`. |
| 2 | Version-aware import QA for British Invasion covers, garage rows, and late compilation gateways. |
| 3 | Threshold QA for album-rock/prog depth and duplicate membership behavior. |
| 4 | Manual attribution pass for traditional/protest standards and AAA/adult-pop false-nearby controls. |
| 5 | Country-specific second pass focused on bluegrass, Bakersfield, western swing, country gospel, and Tejano-country. |
| 6 | Alias/version pass for Motown group/solo splits, disco-era transformations, and R&B song-first rows. |
| 7 | Hip-hop explicit/clean/remix/collaboration policy pass plus alias normalization. |
| 8 | Consolidation pass: alias/version warnings, cross-family boundary QA with Families 9/10/11/17/18, and Page 2 thresholding. |
| 9 | Metal depth QA across extreme metal, industrial/nu-metal, metalcore, and cover-version gateways. |
| 10 | Cross-family boundary pass with Families 8, 9, 11, and 18. |
| 11 | Club/electronic second pass for industrial, ambient, D&B, garage, trance, and alias/mix specificity. |
| 12 | Persona-pop recency and survey-tier calibration, including solo/group credit handling. |
| 13 | Regional expansion for South Asian, MENA, Brazilian, reggae/dancehall, and non-Afrobeats Africa. |
| 14 | Standards policy pass: composition, definitive recording, vocal standard, jazz standard, and classical-crossover split. |
| 15 | Show/film/source-entity model pass before expanding more soundtrack memory rows. |
| 16 | Worship-songbook version policy pass across live, church-brand, songwriter, and congregation objects. |
| 17 | Composition-first treatment for holiday, kids, novelty, karaoke, wedding, and party standards. |
| 18 | Freshness cadence and Page 1 suppression rules for fast-moving current/internet-native scenes. |
