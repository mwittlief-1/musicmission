# Family 9 Lock Readiness

## Judgment

Status: `schema_ready_not_locked`

Family 9 is locally schema-normalized and ready for editorial review. It should not be locked until an authorized importer dry run and cross-family ownership review are completed.

## Checks

| Check | Status | Notes |
|---|---|---|
| Required files present | Pass | Eight requested files are present under `data/canonical_graph/family_9/`. |
| JSON import shape | Pass | Metadata plus `artists`, `albums`, and `songs` arrays. |
| Required row fields | Pass | Required fields are present by object type. |
| Role enum compliance | Pass | JSON uses only the provided role enum values. |
| Tier enum compliance | Pass | Recognition, survey, album object type, and song artist status values are normalized. |
| Slug normalization | Pass | Proposed IDs are lowercase kebab-case. |
| Seed preservation | Pass | Packet 009 named artist rows are `existing_seed=true`; album/song additions are `existing_seed=false`. |
| Duplicate handling | Needs review | Black Sabbath and selected songs carry duplicate archetype memberships; importer should create one canonical entity plus membership rows. |
| Version ambiguity | Needs review | Covers, title tracks, self-titled albums, live albums, and NIN `Hurt` need object-aware merge behavior. |
| Cross-family ownership | Needs review | Hard rock, glam, alternative, industrial, active-rock, punk/hardcore, and extreme-metal adjacent rows need editorial ownership review. |

## Lock Blockers

| Blocker | Required action |
|---|---|
| Global import dry run not run | Task explicitly prohibited running the global import dry-run script; run later only when authorized. |
| Boundary weighting | Confirm glam/pop-metal, active rock, rap-rock, and industrial rows should remain boundary/gateway rather than hard metal anchors. |
| Extreme thresholding | Confirm the gateway-only extreme policy is acceptable before expanding black/death/grind/sludge depth. |
| Title/version matching | Confirm importer distinguishes self-titled albums, title tracks, covers, and live/compilation gateways. |

## Lock Recommendation

Proceed to authorized staging/import QA after editorial review. Do not hard-lock until duplicate membership semantics, boundary-role weighting, and title/version merge rules are confirmed.
