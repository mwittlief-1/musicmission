# AtlasExplainerRenderPack Runtime Schema v0.1.1

Status: proposed before app integration

## Purpose

The v0.1 render schema proves the pack shape, but it is too loose for runtime because `entries[]` accepts any object. Runtime v0.1.1 should make the app contract explicit: each entry must carry graph alignment, required surfaces, deterministic copy variants, claim references, graph audit references, mission-boundary policy, state-bound personalization hooks, and rights/non-mutation guardrails.

## Required Top-Level Fields

- `schema_version`: must be `0.1.1`.
- `pack_id`
- `generated_at`
- `runtime_contract`
- `rights_policy`
- `non_mutation_policy`
- `alpha_v0_mission_boundary`
- `state_field_contract`
- `render_surfaces`
- `entries`
- `source_references`
- `source_research_pack_ids`
- `audit`

## Required Runtime Surfaces

Each runtime pack must declare and each entry must provide:

- `atlas_home_region_card`
- `region_scene_page`
- `mission_detail_history_module`
- `did_you_know_card`
- `what_to_listen_for_prompt`
- `personalized_overlay`
- `canonical_examples`
- `related_roads_lineage_module`

The current v0.1 fixture omits `canonical_examples` from top-level `render_surfaces` while still including it per entry. v0.1.1 should include it explicitly because examples are part of the renderable entry contract and carry graph audit refs.

## Entry Contract

Each `entries[]` item must include:

- `render_pack_id`
- `graph_alignment`
- `editorial_status`
- `source_claim_refs`
- `home_region_card`
- `region_scene_page`
- `mission_detail_history_module`
- `did_you_know_card`
- `what_to_listen_for_prompt`
- `personalized_overlay`
- `canonical_examples`
- `related_roads_lineage_module`

`graph_alignment` is required to bind rendering to an existing family/archetype ref. It is not a mutation path and must not rename, merge, or promote canonical graph objects.

## Copy Variant Contract

All user-facing copy modules that expose variants must include:

- `compact`
- `standard`
- `deep`

Each variant must include:

- `text`
- `claim_refs`
- `source_refs`
- `max_chars`

Runtime may select a variant or trim within the provided text. Runtime must not add factual claims or generate history copy from scratch.

## Personalization Contract

Every personalization hook must include:

- `hook_id`
- `state_field_bindings`
- `condition_logic`
- `copy_variants`
- `guardrail`

Every field referenced by `state_field_bindings` and `condition_logic` must match `state_field_contract.fields`, including bracketed placeholders such as `[archetype_ref]`, `[entity_id]`, and `[tag_id]`.

## Claim And Audit Refs

Runtime validation should confirm:

- every `claim_refs[]` value resolves to a research-pack `claim_bank[].claim_id`;
- every `source_refs[]` value resolves to top-level or research-pack `source_references`;
- every canonical example `graph_audit_ref` resolves to the research-pack graph audit for the same archetype/entity;
- each canonical example `graph_ref.family_id`, `graph_ref.archetype_id`, and `graph_ref.archetype_ref` match the entry `graph_alignment`.

## Hard Guardrails

- `runtime_contract.deterministic_render_required = true`
- `runtime_contract.history_generation_from_scratch_allowed = false`
- `rights_policy.no_lyrics = true`
- `rights_policy.no_long_quotes = true`
- `rights_policy.max_verbatim_quote_words_per_source = 0`
- `rights_policy.album_art_dependency = none`
- `non_mutation_policy.canonical_graph_mutation_allowed = false`
- `non_mutation_policy.renamed_archetypes_allowed = false`
- `non_mutation_policy.new_taxonomy_allowed = false`
- `non_mutation_policy.new_graph_identity_allowed = false`
- `alpha_v0_mission_boundary.mission_creation_from_atlas_allowed = false`
- `alpha_v0_mission_boundary.dynamic_route_generation_allowed = false`

## Small-Model Boundary

Allowed later, if separately authorized:

- select `compact`, `standard`, or `deep`;
- select a state-bound personalization hook;
- trim within provided text without adding factual claims.

Disallowed:

- generate music-history copy;
- invent graph refs, claim refs, candidate refs, or source refs;
- rename archetypes or create taxonomy;
- create missions dynamically;
- add lyrics, long quotes, or unlicensed visual dependencies.

Machine schema: `data/atlas_explainer/atlas_explainer_render_pack_runtime_schema_v0_1_1.json`
