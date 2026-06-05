# Cartenza Mission Enrichment v0.2

Status: Provisionally alpha-locked contract package. Offline/local only; not app/backend integrated.

Alpha lock note: CEO/Product provisionally accepted Mission Enrichment v0.2 for alpha on 2026-06-04 after six Build 45 missions passed live OpenAI output validation. See [reports/mission_enrichment_alpha_provisional_lock_2026_06_04.md](reports/mission_enrichment_alpha_provisional_lock_2026_06_04.md).

This package defines a runtime-candidate Mission Enrichment layer for Cartenza alpha. It supersedes the earlier v0.1 direction and removes founder-specific, rock-specific, and genre-assumptive language.

Mission Enrichment is not mission selection. A deterministic mission already exists before this contract is used. The enrichment layer may write app-ready mission copy and rank secondary reaction tag candidates from an approved registry, but it may not change mission content.

## Included

- Product/contract review packet: [mission_enrichment_product_review_packet_v0_2.md](mission_enrichment_product_review_packet_v0_2.md)
- Draft secondary reaction tag registry note: [secondary_reaction_tag_registry_draft_v0_2.md](secondary_reaction_tag_registry_draft_v0_2.md)
- Input schema: [schemas/mission_enrichment_input_v0_2.schema.json](schemas/mission_enrichment_input_v0_2.schema.json)
- Output schema: [schemas/mission_enrichment_output_v0_2.schema.json](schemas/mission_enrichment_output_v0_2.schema.json)
- Registry schema: [schemas/secondary_reaction_tag_registry_v0_2.schema.json](schemas/secondary_reaction_tag_registry_v0_2.schema.json)
- Machine-readable registry: [registry/secondary_reaction_tag_registry_v0_2.json](registry/secondary_reaction_tag_registry_v0_2.json)
- Prompt template: [prompts/mission_enrichment_prompt_v0_2.md](prompts/mission_enrichment_prompt_v0_2.md)
- Runtime-candidate scripts: [scripts/](scripts/)
- Positive and negative fixtures: [fixtures/](fixtures/)
- Fixture tests: [tests/fixture_contract_tests_v0_2.py](tests/fixture_contract_tests_v0_2.py)
- Runtime-candidate report: [reports/mission_enrichment_runtime_candidate_report_v0_2.md](reports/mission_enrichment_runtime_candidate_report_v0_2.md)
- Alpha provisional lock report: [reports/mission_enrichment_alpha_provisional_lock_2026_06_04.md](reports/mission_enrichment_alpha_provisional_lock_2026_06_04.md)
- Build 45 combined validated output: [runs/build45_six_mission_enrichment_v0_2_combined_validated_20260604T173100Z/combined_summary.md](runs/build45_six_mission_enrichment_v0_2_combined_validated_20260604T173100Z/combined_summary.md)

## Alpha-Locked Posture

This package is provisionally locked for alpha contract behavior and Build 45-style mission-enrichment output. It adds schemas, fixtures, prompt material, prefilter logic, validation tooling, and one validated six-mission live OpenAI output packet, but it does not wire Mission Enrichment into the iOS app, Supabase runtime, Atlas mutation, or production OpenAI execution.

## Locked Boundaries

- Mission selection remains deterministic.
- OpenAI may not add, remove, reorder, or replace songs.
- OpenAI may not change mission type, route roles, graph IDs, or canonical IDs.
- OpenAI may not invent artists, songs, genres, tags, affinity facts, or final taste truth.
- Secondary reaction tags must come from a stable approved registry.
- Song affinity tags are evidence, not user-facing chip labels.
- User alignment hints personalize the chip set without creating personalized tag IDs.
- `love`, `like`, `ok`, and `dislike` are the v0.2 primary reaction words for this surface.

## Validation

Run the package fixture checks from repo root:

```sh
.venv/bin/python data/product_contracts/mission_enrichment_v0_2/tests/fixture_contract_tests_v0_2.py
```

Run the dry prompt candidate:

```sh
.venv/bin/python data/product_contracts/mission_enrichment_v0_2/scripts/run_mission_enrichment_prompt_test_v0_2.py --dry-run
```

## Supersession

Mission Enrichment v0.2 supersedes the v0.1 mission-enrichment design direction. Do not implement v0.1 as a separate runtime path.
