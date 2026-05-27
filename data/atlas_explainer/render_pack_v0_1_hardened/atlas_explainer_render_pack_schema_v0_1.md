# AtlasExplainerRenderPack Schema v0.1

Purpose: compact runtime-facing copy pack for deterministic Atlas rendering. It is derived from approved or draft-approved research packs and is designed so production does not ask GPT-5.5 to explain music history from scratch.

## Required top-level fields

- `schema_version`: `0.1`
- `pack_id`
- `runtime_contract`
- `rights_policy`
- `non_mutation_policy`
- `alpha_v0_mission_boundary`
- `state_field_contract`
- `render_surfaces`
- `entries`
- `source_references`
- `audit`

## Entry surfaces

Each entry should support:

1. `home_region_card`
2. `region_scene_page`
3. `mission_detail_history_module`
4. `did_you_know_card`
5. `what_to_listen_for_prompt`
6. `personalized_overlay`
7. `canonical_examples`
8. `related_roads_lineage_module`

## Copy variants

Key modules carry `compact`, `standard`, and `deep` variants. Runtime may select variants based on screen surface and space, but may not generate new history claims.

## Personalization

Personalization hooks must bind to explicit Atlas state field paths. No free-text hook should ship without `state_field_bindings` and structured `condition_logic`.

## Alpha v0 mission boundary

Atlas may render “related mission,” “included in first batch,” and “what this route tests.” It must not imply dynamic mission creation from an Atlas region/node in Alpha v0.
