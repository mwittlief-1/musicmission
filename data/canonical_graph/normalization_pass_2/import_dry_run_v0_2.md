# Import Dry Run v0.2

Generated: 2026-05-20

Command:

`python3 scripts/canonical_graph_import_dry_run.py`

Output:

```text
canonical graph dry run: 18 families, 1499 artists, 1207 albums, 1917 song recordings, 0 errors, 9 warnings
```

Validation warnings are not removed from the base importer. They are now covered by Normalization Pass 2 sidecars, quarantine, and survey-surface suppression.

| gate | status |
| --- | --- |
| Validation errors = 0 | pass |
| Page 1 duplicates absent | pass |
| No quarantined rows in Page 1 | pass |
| No quarantined recording approved + survey_safe | pass |
| Sidecar alias/version/composition tables exist | pass |
| Every generated survey candidate has survey intent | pass |
| Every generated survey candidate has do-not-infer guardrails | pass |
| Every family has survey readiness classification | pass |
| Every archetype has readiness classification | pass |
