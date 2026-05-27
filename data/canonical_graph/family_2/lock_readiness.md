# Family 2 Lock Readiness

## Judgment

Status: `dry_run_ready_not_locked`

Family 2 is ready for importer dry-run and editorial review. It should not be locked until duplicate source rows, cover/version handling, and cross-family boundary ownership are reviewed.

## Checks

| Check | Status | Notes |
|---|---|---|
| Required files present | Pass | Eight requested files are present under `data/canonical_graph/family_2/`. |
| JSON import shape | Pass | Metadata plus `artists`, `albums`, and `songs` arrays. |
| Required row fields | Pass | Required fields are present by object type. |
| Role enum compliance | Pass | JSON uses only the provided role enum values. |
| Tier enum compliance | Pass | Recognition, survey, and album object type values are normalized. |
| Slug normalization | Pass | Proposed IDs are lowercase kebab-case. |
| Seed preservation | Pass | Source rows are `existing_seed=true`; missing-obvious additions are `existing_seed=false`. |
| Duplicate handling | Needs review | Duplicate source mentions for `Needles and Pins` and `Bus Stop` are consolidated into single import rows. |
| Version ambiguity | Needs review | `Gloria`, `Mr. Tambourine Man`, and `House of the Rising Sun` need version-aware merge rules. |
| Cross-family ownership | Needs review | Beatles, Dylan, Beach Boys, Hendrix, Doors, Cream, Pink Floyd, and Velvet Underground have strong claims in adjacent families. |

## Lock Blockers

| Blocker | Required action |
|---|---|
| Source duplicate rows | Confirm one normalized row per canonical object is acceptable. |
| Cover/version matching | Confirm importer can distinguish artist-recording IDs for shared compositions. |
| Later compilation objects | Confirm 1972 and 2017 compilation gateways are allowed in a 1960s family because they are canon-shaping objects. |

## Lock Recommendation

Run schema validation and a duplicate-ID dry run first. If no importer conflicts appear, this family can move to final editorial lock after cross-family ownership review.

## Second-Pass Lock Impact

The second-pass merge improves coverage but does not change the lock posture: this family is staging/import-dry-run ready, not hard-locked. Accepted additions increased duplicate/member and cross-family ownership pressure; importer QA must still confirm canonical object versus archetype membership behavior before final lock.
