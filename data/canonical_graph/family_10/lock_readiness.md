# Family 10 Lock Readiness

## Judgment

Status: `dry_run_ready_not_locked`

Family 10 is ready for schema validation and local duplicate-ID review. It should not be locked until editorial review confirms post-grunge false-nearby handling, cross-family ownership, and the Packet 010 source-seed policy.

## Checks

| Check | Status | Notes |
|---|---|---|
| Required files present | Pass | Eight requested files are generated under `data/canonical_graph/family_10/`. |
| JSON import shape | Pass | `metadata`, `artists`, `albums`, and `songs` arrays are present. |
| Required row fields | Pass | Required fields are present by object type. |
| Role enum compliance | Pass | Roles use only the requested enum values. |
| Tier enum compliance | Pass | Recognition, survey, album type, and song status values are normalized. |
| Slug normalization | Pass | Proposed IDs are lowercase kebab-case. |
| Seed preservation | Pass | Packet 010 named artist objects are `existing_seed=true`; all other instantiated objects are `existing_seed=false`. |
| Source alignment | Needs review | `F10.md` was ignored as instructed; `F16.md` was used only as a misnumbered 073 aid. |
| Cross-family ownership | Needs review | Several objects need non-exclusive memberships with pop, punk, new wave, classic rock, soundtrack/context, and singer-songwriter families. |
| False-nearby thresholds | Needs review | Post-grunge and modern-rock rows are included for recognition but should not define alternative center. |

## Lock Blockers

| Blocker | Required action |
|---|---|
| Packet 010 source sparsity | Confirm that artist-only Packet 010 seeds and missing-obvious album/song additions are acceptable. |
| Post-grunge calibration | Confirm edge/false_nearby treatment for Creed, Nickelback, and adjacent radio objects. |
| Cross-family ownership | Confirm multi-family behavior for The Cure, R.E.M., Alanis Morissette, Beach House, The Killers, and The National. |
| Version/display normalization | Confirm display handling for self-titled albums, punctuation-heavy emo titles, and diacritic-capable artist names. |

## Lock Recommendation

Run schema validation and duplicate-ID checks first. Do not run the global import dry-run until Family 10 has editorial approval for source alignment and false-nearby policy.
