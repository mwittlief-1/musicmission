# Atlas Explainer Render Pack Loader Tech Review v0.1

Date: 2026-05-26

Fixture: `data/atlas_explainer/render_pack_v0_1_hardened/`

Source zip: `/Users/matt_wittlief_home/Downloads/AtlasExplainerPack_v0_1_Hardened.zip`

## Decision

Use `AtlasExplainerPack_v0_1_Hardened` as the first render-pack fixture, but do not wire it into app rendering until the runtime schema is tightened to v0.1.1.

The deterministic loader/validator is implemented in:

```text
scripts/validate_atlas_explainer_render_pack.py
```

It supports both an extracted fixture directory and the original zip.

## Loader Scope

The loader validates:

- `AtlasExplainerRenderPack`
- per-entry `graph_alignment`
- required surface modules
- `compact`, `standard`, and `deep` copy variants
- `claim_refs`
- `source_refs`
- `graph_audit_ref` values for canonical examples
- `alpha_v0_mission_boundary`
- `state_field_contract`
- `rights_policy`
- `non_mutation_policy`
- manifest completeness

It does not generate, rewrite, summarize, or embellish history copy.

## Validation Result

Command:

```bash
python3 scripts/validate_atlas_explainer_render_pack.py \
  --report-json data/atlas_explainer/render_pack_v0_1_hardened/atlas_explainer_render_pack_validation_report_v0_1.json
```

Result:

```text
ATLAS_EXPLAINER_RENDER_PACK_VALIDATION_PASS
entries=2
claim_refs_checked=190
source_refs_checked=159
graph_audit_refs_checked=20
copy_variant_sets_checked=24
```

The original zip also passes:

```bash
python3 scripts/validate_atlas_explainer_render_pack.py \
  /Users/matt_wittlief_home/Downloads/AtlasExplainerPack_v0_1_Hardened.zip
```

## Fixture Observations

- The v0.1 pack is graph-aligned and deterministic-render ready.
- The v0.1 JSON schema is intentionally loose: `entries[]` is only typed as `object`.
- The actual fixture entries are much stricter than the schema: both entries include the same required surface modules and state-bound personalization hooks.
- `canonical_examples` are present per entry and carry `graph_audit_ref`, but `canonical_examples` is not listed in top-level `render_surfaces`. v0.1.1 should require it.
- The pack correctly marks copy as `alpha_render_candidate_not_production_copy_approved`.
- Rights policy is present and blocks lyrics, long quotes, and unlicensed album-art dependency.
- Alpha v0 mission boundary is present and blocks dynamic mission creation from Atlas.

## Runtime Rule

Production rendering should be deterministic:

```text
render pack entry + requested surface + selected variant + optional state-bound hook -> rendered copy
```

Allowed small-model actions, only if later authorized:

- select `compact`, `standard`, or `deep`;
- select one eligible state-bound personalization hook;
- trim within provided text without adding factual claims.

Disallowed:

- generate music-history copy;
- invent graph refs, candidate refs, source refs, or claim refs;
- create missions dynamically;
- rename archetypes;
- mutate canonical graph or Atlas truth;
- add lyrics, long quotes, or unlicensed image dependencies.

## Proposed v0.1.1 Runtime Schema

Proposed files:

```text
data/atlas_explainer/atlas_explainer_render_pack_runtime_schema_v0_1_1.md
data/atlas_explainer/atlas_explainer_render_pack_runtime_schema_v0_1_1.json
```

The stricter schema requires:

- explicit required surfaces;
- per-entry surface modules;
- exact `compact`, `standard`, `deep` variant sets;
- variant-level `text`, `claim_refs`, `source_refs`, and `max_chars`;
- required graph alignment;
- required canonical example graph refs and audit refs;
- state-bound personalization hooks;
- hard rights, non-mutation, and Alpha mission-boundary policies.

## App Integration Recommendation

Before app integration:

1. Convert the render pack to `schema_version = 0.1.1`.
2. Add `canonical_examples` to top-level `render_surfaces`.
3. Keep the loader as a preflight gate for bundled render-pack resources.
4. App code should select existing text only. It should not call a model to write history copy.
5. Any future app UI should display `editorial_status` or hide non-production packs behind Alpha/debug flags until copy approval is explicit.

No app integration was performed in this slice.
