# Atlas Schema Data

This directory contains the source contracts for Atlas schema work plus generated proof artifacts.

## Track As Source

- `atlas_schema_contract_v0_1.json`
- `atlas_schema_contract_v0_1.md`
- `atlas_delta_v0_1.schema.json`
- `atlas_delta_v0_1.md`
- `atlas_schema_acceptance_report.md`
- `examples/`
- `alpha_hardening/`

These files are first-class contracts, acceptance notes, or deterministic examples.

## Generated Evidence

The following directories are generated proof, smoke, or review artifacts and are ignored by default:

- `ingestion_proof/`
- `node_interpretation_smoke/`
- `wwtsf_substrate_smoke/`

Promote a generated artifact only by moving or copying the specific accepted file into `examples/`, `alpha_hardening/`, `data/product_contracts/`, or `docs/` with a note explaining why it became source-of-truth.
