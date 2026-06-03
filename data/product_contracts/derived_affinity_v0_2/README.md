# Derived Affinity Downstream Contracts v0.2

Status: PM review contract design. Offline only.

This package defines two downstream contracts that consume the accepted Derived Affinity Substrate v0.1.1 as review input:

- [Atlas Visualization Input Contract v0.2](atlas_visualization_input_contract_v0_2.md)
- [Mission Construction Contract v0.2](mission_construction_contract_v0_2.md)

Sample fixtures:

- [Atlas visualization input sample v0.2](fixtures/atlas_visualization_input_sample_v0_2.json)
- [Mission construction sample v0.2](fixtures/mission_construction_sample_v0_2.json)

Schemas:

- [Atlas visualization input schema v0.2](schemas/atlas_visualization_input_contract_v0_2.schema.json)
- [Mission construction schema v0.2](schemas/mission_construction_contract_v0_2.schema.json)

TypeScript domain types:

- [Atlas visualization input types v0.2](types/atlas_visualization_input_contract_v0_2.ts)
- [Mission construction types v0.2](types/mission_construction_contract_v0_2.ts)

Offline validation and fixture tests:

```sh
.venv/bin/python scripts/validate_derived_affinity_contracts_v0_2.py
.venv/bin/python data/product_contracts/derived_affinity_v0_2/tests/fixture_contract_tests_v0_2.py
```

The validator uses the repo's existing `jsonschema` dependency. If a local environment does not already have it, install the standard script requirements first:

```sh
python3 -m pip install -r scripts/requirements.txt
```

## Source Boundary

Allowed source input:

- `derived_affinity_substrate_v0_1_1/`

Allowed lineage references:

- Candidate identifiers, scores, categories, and provenance recorded by the v0.1.1 substrate.
- Candidate pools retained by the v0.1.1 review lineage when a surface type was not rewritten during hardening.

Not allowed:

- Runtime ingestion.
- Canonical graph mutation.
- Product-role promotion.
- Listener preference inference from affinity similarity.
- Personal Atlas role assignment.
- Production mission generation.

## Layer Boundary

Both contracts preserve five separate layers:

1. Intrinsic affinity: musical and emotional tag structure.
2. Context overlays: route, scene, social, historical, or use-case context.
3. Risk and review metadata: quarantine, false-nearby, high-whiplash, gateway, duplicate, identity, and review flags.
4. Listener evidence: explicit user evidence only, absent from the v0.1.1 substrate.
5. Product role assignment: PM- or evidence-gated assignment, never implied by raw affinity.

## Acceptance Summary

A downstream consumer passes this contract only when it treats every v0.1.1 candidate as review substrate, keeps risk and quarantine labels visible, and refuses to turn affinity similarity into listener taste or product truth.
