# QA Exception Ledger Alpha v0

Version: `alpha_v0`

Status: `active_for_alpha_consumable_layer`

This ledger preserves known warnings, manual-review rows, quarantine rows, and Alpha overlay blocks. It does not clear the graph for hard lock.

## Summary

| category | count |
| --- | ---: |
| validation_warning_count | 9 |
| warning_snippet_count | 99 |
| composition_review_rows | 24 |
| quarantine_rows | 107 |
| manual_or_blocked_recording_rows | 60 |
| alpha_blocklist_rows | 1 |

## Import Validation Warnings

- import-warning-001: family 4 song f4-026-song-we-shall-overcome-pete-seeger-et-al-traditional: release_year is `None`
- import-warning-002: family 4 song f4-026-song-house-of-the-rising-sun-traditional-revival-circuit-object: release_year is `None`
- import-warning-003: artist `kool-and-the-gang` has multiple display/source names: Kool & The Gang; Kool & the Gang
- import-warning-004: artist `martha-and-the-vandellas` has multiple display/source names: Martha & the Vandellas; Martha and the Vandellas
- import-warning-005: artist `simon-and-garfunkel` has multiple display/source names: Simon & Garfunkel; Simon and Garfunkel
- import-warning-006: artist `smokey-robinson-and-the-miracles` has multiple display/source names: Smokey Robinson & The Miracles; Smokey Robinson and the Miracles
- import-warning-007: album `the-sonics-here-are-the-sonics` has multiple display/source names: Here Are The Sonics; Here Are the Sonics
- import-warning-008: song_recording `martha-and-the-vandellas-dancing-in-the-street` has conflicting `artist_names` values: Martha & the Vandellas; Martha and the Vandellas
- import-warning-009: song_recording `shania-twain-man-i-feel-like-a-woman` has conflicting `release_years` values: 1997; 1999

## Alpha Blocklist

- alpha-block-001: album:robin-s-show-me-love - canonical_id_collision_with_quarantined_song_recording_mix_edit_risk

## Downstream Rule

Exception rows are QA context or blocked rows. They must not feed Survey display, starter Atlas, default Mission Generation, Supabase active candidates, OpenAI prompt payloads, or Apple Music auto-resolution unless a later reviewed Alpha contract explicitly allows them.
