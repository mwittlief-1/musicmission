# Corrections To Source Report

- Packet 015 from the dispatch file is controlling for family name, archetype IDs, and scope.
- No aligned F15 supplemental report was present at baseline generation.
- No rows were marked `existing_seed = true`; the available family-specific supplemental reports did not provide aligned row-level seed rows.
- Dispatch archetype IDs and names were preserved while row slugs and enum values were normalized to the importer contract.
- Added gap-fill rows are candidate memberships, not final canonical-object assertions; merge/version risks are carried into `import_warnings.md`.
