# AtlasExplainerPack v0.1 — Alpha Hardening Notes

Generated: 2026-05-26

## Decision carried forward

The graph-aligned sidecar direction is preserved. Brill 005 and CBGB 054 remain draft research packs and are now hardened as Alpha render candidates. They should inform Atlas Visualization and Mission Detail design, but they are not production-approved copy.

## What changed

1. Added claim-level source/audit refs through `claim_bank` and `module_audit_refs`.
2. Added a compact runtime-facing `AtlasExplainerRenderPack` with deterministic copy variants.
3. Bound personalization hooks to explicit Atlas state fields in `state_field_contract`.
4. Added Alpha v0 mission-boundary policy: render related/included/test language only; no dynamic mission creation.
5. Added `compact`, `standard`, and `deep` variants for key modules.
6. Added explicit rights/copyright policy: no lyrics, no long quotes, no unlicensed/proprietary album art dependency.
7. Verified canonical example rationales against the 2026-05-26 canonical graph export.
8. Reaffirmed non-mutation policy: no graph edits, no renamed archetypes, no new taxonomy.

## Graph-ref verification summary

- Brill 005 canonical examples checked: 10
- Brill 005 normalized graph object misses: 0
- Brill 005 missing survey candidate IDs: 0
- CBGB 054 canonical examples checked: 10
- CBGB 054 normalized graph object misses: 0
- CBGB 054 missing survey candidate IDs: 0

Note: Dionne Warwick — “Anyone Who Had a Heart” is verified as an existing normalized Family 1 / Archetype 005 graph object but does not currently carry a matched survey candidate ID in the proof pack. This is acceptable under the acceptance rule because the rationale points to an existing graph ref; it is not a new invented example.

## Runtime rule

Production should render approved pack copy deterministically. A smaller model may select among variants or attach state-bound overlays. It must not invent music-history copy, graph refs, candidate refs, new missions, or new taxonomy at runtime.
