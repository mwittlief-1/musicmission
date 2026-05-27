# Corrections To Source Report

- Packet 016 from the dispatch file is controlling for family name, archetype IDs, and scope.
- F16.md is misaligned; it describes dream-pop/shoegaze rather than Christian, worship, or gospel material, so it was not used as seed evidence.
- No rows were marked `existing_seed = true`; the available family-specific supplemental reports did not provide aligned row-level seed rows.
- Dispatch archetype IDs and names were preserved while row slugs and enum values were normalized to the importer contract.
- Added gap-fill rows are candidate memberships, not final canonical-object assertions; merge/version risks are carried into `import_warnings.md`.
