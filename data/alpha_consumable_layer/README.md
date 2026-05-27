# Alpha Consumable Layer

This directory contains the frozen `alpha_v0` graph surface used by the app, Survey, Mission Generation, resolver policy, and audit/diagnostic handoff.

## Tracking Policy

Track the complete `alpha_v0/` surface as source-of-truth for the current alpha:

- paired JSON and Markdown contracts
- manifests and validation reports
- machine-readable resolver and candidate policy files
- sample compact candidate pools
- survey page-selection audit references
- QA exception and review-risk ledgers

Some files are generated from canonical graph inputs, but once they are included in `alpha_graph_surface_manifest.*` they become frozen alpha handoff artifacts. Do not regenerate or partially replace them without updating the manifest, validation report, and downstream app/resource references together.

## Archive Policy

Future timestamped experiments, raw generation logs, or review bundles should not be added here. Put generated evidence under a generated-output path and promote only the accepted alpha surface files into this directory.
