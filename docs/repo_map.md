# Repo Map

Date: 2026-05-26

This map describes the intended repository shape for the Cartenza alpha. Waymark is the former product name and still appears in legacy technical identifiers. This is a stewardship guide, not a deletion plan. When a directory mixes source-of-truth material and generated artifacts, keep it visible until the owner reviews a more specific move.

## Classification Labels

- Runtime source: code, app resources, backend functions, migrations, and project files needed to build or run the alpha.
- Test/source fixture: deterministic inputs, golden samples, schemas, and fixture snapshots needed by tests or harnesses.
- Product/technical contract: specs, data contracts, runbooks, policies, and lane dispatch material that other work depends on.
- Generated artifact: reproducible outputs, run logs, review packets, reports, model responses, and evidence bundles.
- Local build/cache output: machine-local build products, cache directories, temporary CLI state, secrets, and exports.
- Candidate for external/archive storage: bulky generated artifacts, zip bundles, historical review packets, and dated outputs that should not be primary repo content unless explicitly accepted as source-of-truth.

## Top-Level Layout

| Path | Primary classification | What belongs here |
| --- | --- | --- |
| `MusicAtlasController.xcodeproj/` | Runtime source | Xcode project and shared scheme files. User-specific Xcode state belongs in ignored `xcuserdata` paths. |
| `MusicAtlasController/` | Runtime source | SwiftUI app source, bundled app resources, app entitlements, Info.plist, and runtime resource JSON that ships with the app. |
| `MusicAtlasControllerTests/` | Test/source fixture | XCTest sources and deterministic fixtures used by app tests. |
| `supabase/` | Runtime source and product/technical contract | Supabase config, Edge Functions, migrations, examples, and infra acceptance docs. `supabase/.temp/` is local CLI state and stays ignored. |
| `scripts/` | Runtime support and generation tooling | Validation, generation, import, smoke, and reporting scripts. Generated outputs should land under the appropriate `data/`, harness `outputs/`, or ignored export path, not beside scripts. |
| `data/` | Mixed source, contracts, fixtures, and generated artifacts | Canonical graph material, schemas, mission fixtures, product contracts, simulation data, generation runs, and exports. `data/README.md` is the source/generated/archive policy. |
| `docs/` | Product/technical contract and generated review evidence | Active specs, app-dev notes, infra docs, alpha backlog, repo stewardship docs, and dated reports. Historical or generated docs should move only after owner review. |
| `review_packets/` | Generated artifact and archive candidate | Ignored local archive/output surface for generated zip packets and extracted review material. Promote active Markdown into `docs/reviews/`; keep only small manifests in repo. |
| `waymark-ai-tests/` | Legacy-named first-class tracked test harness with generated outputs | Track README, `pyproject.toml`, `.env.example`, `docs/`, `src/`, and `fixtures/`. Ignore `outputs/`, generated reports, local `.env*`, and zip packets. Do not rename as incidental cleanup. |
| `waymark-atlas-tests/` | Legacy-named first-class tracked test harness with generated outputs | Track README, `pyproject.toml`, `.env.example` if present, `src/`, and `fixtures/`. Ignore `outputs/`, generated reports, local `.env*`, and zip packets. Do not rename as incidental cleanup. |
| `build/` | Local build/cache output | Xcode build products, DerivedData, archives, dSYMs, device smoke exports. This directory is ignored and should not be tracked. |
| `.venv/` | Local build/cache output | Local Python environment. Ignored. |
| `tests/` | Test/source fixture | Lightweight test notes and future test space. |

## `data/` Map

`data/README.md` is the action policy for `data/`: it names source-of-truth paths, first-class fixture paths, and generated/archive candidates.

| Path | Primary classification | Notes |
| --- | --- | --- |
| `data/README.md` | Product/technical contract | Source-of-truth versus generated/archive policy for `data/`. |
| `data/missions/` | Runtime app fixture and test/source fixture | Tracked mission fixtures. Do not delete without checking app resources and tests. |
| `data/schemas/` | Product/technical contract | Tracked mission and reaction-session schemas. |
| `data/product_contracts/` | Product/technical contract | App, graph, survey, Atlas, and mission-generation contracts. Should remain visible for review. |
| `data/atlas_schema/` | Product/technical contract and generated proofs | Contract roots and examples are source-like. `ingestion_proof/`, smoke outputs, and zip bundles are generated evidence or archive candidates. |
| `data/atlas_explainer/` | Product/technical handoff, fixture, and generated archive | Track runtime schema docs, `render_pack_v0_1_hardened/`, source-recovery notes, and latest `AtlasExplainerPack_v0_2_3_RenderHardened/`. Ignore zips, Finder duplicates, local validation logs, and older rebuildable package outputs unless promoted. |
| `data/canonical_graph/` | Canonical/product source material and promoted fixtures | Track family sources, `current/`, policy hardening, affinity contracts, and promoted `import_dry_run/` plus `normalization_pass_2/` fixtures. Ignore depth-hardening pass trees and zips unless a specific artifact is promoted. |
| `data/alpha_consumable_layer/` | Product/technical contract and canonical handoff | Alpha graph surfaces, resolver policy, guardrails, and audit refs. Large audit JSON may be generated evidence, but it supports active contracts. |
| `data/alpha_packets/` | Test/source fixture and generated artifact | Golden integration packet used for app/import review. Keep visible until the accepted golden-packet policy is decided. |
| `data/mission_generation/` | Generated artifact and product contract | Handoff contracts plus timestamped first-batch generation runs. Raw request/response attempts are archive candidates. |
| `data/survey_simulation/` | Mixed fixture, contract, and generated artifact | Track schemas, fake profiles, Apple payloads, hidden corpora, Survey Evidence Export handoffs, and LLM review prompts/schemas/public packets. Ignore generated runs, reports, backtests, API pilots, evidence bundles, private evaluator material, and Finder duplicates. |
| `data/closed_loop_simulation/` | Generated artifact and product contract | Closed-loop simulation outputs and adaptive contract evidence. Archive after review if no longer active. |
| `data/deprecated_mission_fixtures/` | Candidate for external/archive storage | Deprecated duplicate mission fixtures. Keep until owner approves removal or archive move. |
| `data/exports/` | Local build/cache output | Local app/device/export products. Ignored except `.gitkeep` placeholders. |
| `data/**/*.zip` | Candidate for external/archive storage | Generated review or handoff bundles. Keep source directories or manifests in repo instead of tracking zips unless explicitly approved. |

## `docs/` Map

| Path | Primary classification | Notes |
| --- | --- | --- |
| `docs/app_dev/` | Product/technical contract and generated review evidence | Active app specs, TestFlight reports, audits, brand material, and kickoff packet. The current Cartenza brand packet is tracked design input; future bulky generated brand iterations should move to external design storage or manifest-only tracking. |
| `docs/app_dev/kickoff_v0_2/` | Product/technical contract and test/source fixture | Tracked v0.2 product/implementation packet, schemas, and sample mission. |
| `docs/alpha_backlog/` | Product/technical contract | Active alpha lane backlog and dispatch material. |
| `docs/infra/` | Product/technical contract and generated review evidence | Supabase, diagnostics, evidence upload, and operations docs. |
| `docs/discovery_log/` | Product/technical contract | Tracked discovery-log guidance. |
| `docs/reviews/` | Generated review evidence or active technical review | Human-readable review Markdown that should not live at repo root. Use topic subdirectories. |
| `docs/repo_map.md` | Product/technical contract | This intended-structure map. |
| `docs/repo_cleanup_inventory_YYYY_MM_DD.md` | Generated stewardship artifact | Point-in-time inventory and cleanup recommendations. |

## Test Harness Map

| Path | Primary classification | Notes |
| --- | --- | --- |
| `waymark-ai-tests/src/` | Test/source fixture | First-class mission-generation harness code. Directory and Python package names are legacy Waymark identifiers pending a coordinated Cartenza migration. |
| `waymark-ai-tests/fixtures/` | Test/source fixture | Prompt templates, candidate pools, expected outputs, pricing table, schemas, and digest fixtures. Some digest fixtures are generated by the Atlas harness but currently serve as integration fixtures. |
| `waymark-ai-tests/outputs/` | Generated artifact | Timestamped live/mock/dry-run outputs. Ignored except optional `.gitkeep`. |
| `waymark-ai-tests/reports/` | Generated artifact | Harness reports. Ignored except optional `.gitkeep`; promote selected reports to docs only when accepted as evidence. |
| `waymark-ai-tests/review_packets/*.zip` | Candidate for external/archive storage | Generated packet archives. |
| `waymark-atlas-tests/src/` | Test/source fixture | First-class Atlas ingestion harness code. Directory and Python package names are legacy Waymark identifiers pending a coordinated Cartenza migration. |
| `waymark-atlas-tests/fixtures/` | Test/source fixture | Synthetic survey and mission-review fixtures plus expected references. |
| `waymark-atlas-tests/outputs/` | Generated artifact | Timestamped Atlas ingestion outputs. Ignored except optional `.gitkeep`. |
| `waymark-atlas-tests/reports/` | Generated artifact | Harness reports. Ignored except optional `.gitkeep`; promote selected reports to docs only when accepted as evidence. |

## Naming Policy

See `docs/brand_migration_cartenza.md` for the Cartenza rename policy. New product-facing material should use Cartenza. Existing Waymark schema IDs, environment variables, persisted filenames, Supabase project identifiers, harness directories, Python package names, and historical archive filenames remain legacy technical identifiers until migrated in a deliberate compatibility slice.

## Repo Hygiene Rules

- Do not commit local build products, Xcode archives, DerivedData, local virtualenvs, Supabase CLI temp state, local secrets, or app export outputs.
- Do not delete or blanket-ignore mixed `data/` directories. Classify at the subtree or file-pattern level first.
- Prefer checked-in source directories, manifests, and small review notes over zip bundles.
- Keep app-shipping resources in `MusicAtlasController/Resources/`, with their upstream generation source or contract documented under `data/`.
- Keep first-class harness code and fixtures visible; keep timestamped harness run outputs ignored.
- Keep root-level generated review docs under `docs/reviews/` or a dated archive, not at repo root.
