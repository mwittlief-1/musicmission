# AtlasExplainerResearchPack Schema v0.1.1

Purpose: human/editorial research sidecar keyed to existing canonical graph refs. This schema hardens v0.1 by adding claim-level source refs, graph-ref audit, rights policy, Alpha v0 mission-boundary policy, and explicit non-mutation policy.

## Required top-level fields

- `schema_version`: `0.1.1`
- `pack_id`
- `graph_alignment`: existing family/archetype refs only
- `content_modules`: research copy and candidate rationales
- `source_references`: source registry keyed by `source_id`
- `claim_bank`: claim-level audit units with `claim_id`, `claim`, `source_refs`, `graph_refs`, and `audit_status`
- `module_audit_refs`: maps major modules to claim/source refs
- `rights_policy`: no lyrics, no long quotes, no proprietary album art dependency
- `non_mutation_policy`: no graph edits, no renamed archetypes, no new taxonomy
- `alpha_v0_mission_boundary`: no dynamic mission creation from Atlas in Alpha v0
- `atlas_state_field_contract`: allowed state fields for personalization hooks
- `graph_ref_integrity_audit`: verifies canonical-example refs against graph export and survey candidate files
- `audit`: editorial status and review flags

## Editorial status

Research packs remain draft research packs. They may inform Atlas Visualization and Mission Detail, but they are not production-approved copy until a separate editorial approval step.
