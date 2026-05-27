# Atlas Tech Owner Handoff

Purpose: Survey Evidence Export v0.1 ingestion testing.

Contents:

- `public_profile_01_A3_Al1_S2_survey_evidence_export.json`
  A3 normalized Survey-to-Atlas evidence export with 72 Atlas-ingestable evidence atoms.
- `survey_evidence_export_v0_1_validation_report.md`
  Validator output for the A3 export.
- `survey_evidence_export_v0_1.schema.json`
  JSON Schema for ingestion validation.
- `survey_evidence_export_v0_1.md`
  Contract spec.

Integrity notes:

- The export is append-only ledger evidence, not mutable Atlas state.
- `evidence_strength_hint` is Survey-side evidence-basis metadata only; it is not final Atlas confidence.
- All Apple exposure priors require `taste_truth: false`.
- All Atlas-ingestable response refs must resolve inside the same export.
- External/unresolved refs are quarantined under `construction_only_excluded` and must not be ingested.

SHA-256:

```text
d13bc8f4d4c43f3defc5581af0ee2884514cbd69163b0a79b7ad8d6abf22f6e2  public_profile_01_A3_Al1_S2_survey_evidence_export.json
8581c0a8d427d05a451a1700b532d410f1f7e7aaf5491d857d79f6055358a036  survey_evidence_export_v0_1_validation_report.md
fac559e6baa0e3220eb58b232f4ab0ab2202f2863cc2a92524cce662cecfc567  survey_evidence_export_v0_1.schema.json
25b3b50e753dbc2ca91f4086bd234c67837ba992c76787ac05d6513bdd4dd73e  survey_evidence_export_v0_1.md
```
