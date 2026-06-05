# Atlas Explainer Data Policy

Date: 2026-05-27

This subtree is mixed product data. It includes active Atlas explainer contracts and fixtures, a latest alpha render-candidate package, rebuildable intermediate packages, and local archive outputs. Do not blanket-add or blanket-delete this directory.

## Track As First-Class

| Path | Classification | Policy |
| --- | --- | --- |
| `atlas_explainer_render_pack_runtime_schema_v0_1_1.json` | Product/technical contract | Runtime schema for the app-facing explainer render pack loader. |
| `atlas_explainer_render_pack_runtime_schema_v0_1_1.md` | Product/technical contract | Human-readable runtime schema contract. |
| `render_pack_v0_1_hardened/` | Test/source fixture | Current hardened loader fixture referenced by `scripts/validate_atlas_explainer_render_pack.py` and the loader tech review. |
| `source_recovery_research_notes/` | Product source/provenance | Curated source-recovery notes used by the v0.2.2 and v0.2.3 builder chain. |
| `AtlasExplainerPack_v0_2_3_RenderHardened/` | Product/technical handoff and generated fixture | Source predecessor for v0.3. Keep tracked for lineage and rebuildability. |
| `AtlasExplainerPack_v0_3_ProfileLadders/` | Product/technical handoff and generated fixture | PM-approved 120-archetype Alpha production copy. The app bundle consumes `render_packs/` through `MusicAtlasController/Resources/atlas_explainer_render_packs_v0_3.json`. |

## Keep Local Or Archive Externally

| Path | Classification | Policy |
| --- | --- | --- |
| `AtlasExplainerPack_v0_2_Checkpoint/` | Generated intermediate | Rebuildable checkpoint output from `scripts/build_atlas_explainer_checkpoint_v0_2.mjs`. |
| `AtlasExplainerPack_v0_2_All_Archetypes/` | Generated intermediate | Rebuildable full v0.2 output used by the later source-deepening step. |
| `AtlasExplainerPack_v0_2_1_SourceDeepened/` | Generated intermediate | Rebuildable source-deepened output used by source recovery. |
| `AtlasExplainerPack_v0_2_2_SourceRecovery/` | Generated intermediate | Rebuildable source-recovery output used by v0.2.3 render hardening. |
| `*.zip` | Candidate for external/archive storage | Packet archives; keep out of git unless explicitly approved. |
| `* 2*` and `__MACOSX/` paths | Local duplicate/cache output | Finder duplicate expansions and macOS archive metadata. |
| `**/indexes/schema_validation_report_*.md` | Generated local validation log | Omitted because these reports embed absolute machine paths. Re-run validation locally when needed; manifests and readiness reports stay tracked. |

Promotion rule: if an older generated package becomes the active handoff or a required fixture, update this README and `data/README.md` before tracking it.
