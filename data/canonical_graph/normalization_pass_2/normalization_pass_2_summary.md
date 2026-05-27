# Normalization Pass 2 Summary

Generated: 2026-05-20

Status: limited beta-style survey pilot packet generated for v0.2 survey surfaces.

The underlying canonical graph remains staging-consolidated and not final-lock ready. The v0.2 packet adds alias, version, composition, special-entity, quarantine, survey-intent, and readiness sidecars around the staging corpus.

| artifact class | count |
| --- | --- |
| artist aliases | 12 |
| album aliases | 1 |
| recording aliases | 4 |
| entity relationships | 24 |
| do-not-merge rules | 48 |
| merge blocks | 5 |
| composition rows | 1879 |
| recording-version rows | 1917 |
| cover/source relationships | 10 |
| special entities | 19 |
| quarantine rows | 107 |
| page1 QA failures | 0 |
| recording/quarantine consistency failures | 0 |

Limited beta rule: use only the generated `survey_*_candidates_v0_2.json` surfaces, not raw family rows.
