# Repo Cleanup Inventory - 2026-05-26

Scope: initial repo stewardship pass for `/Users/matt_wittlief_home/Documents/GitHub/musicmission`.

Initial inventory pass: no files were deleted, moved, reverted, or reformatted. The first codebase changes were `.gitignore` additions and repo stewardship docs.

Follow-up classification-to-action pass: root canonical-graph review Markdown moved into `docs/reviews/canonical_graph/`; `README.md`, `docs/repo_map.md`, this inventory, and `data/README.md` were updated with the accepted structure decisions. Runtime/app/Supabase source remained untouched.

## Method

Read-only inventory used:

- `git status --short`
- `du -sh . ./*`
- `find . -maxdepth 2 -type d`
- `git ls-files`
- `git ls-files --others --exclude-standard`
- `git check-ignore -v`
- targeted `find`, `du`, `rg`, and README inspection

Subagent sidecar inventories were used only for read-only classification:

- `data/`
- `docs/`, `review_packets/`, and root review Markdown
- `waymark-ai-tests/` and `waymark-atlas-tests/`

## Worktree State

The worktree is active and contains many unrelated runtime and mission-logic changes. This pass intentionally avoided Swift, Supabase runtime, resource JSON, and mission-generation edits.

Notable modified runtime areas at the start of inventory included:

- `MusicAtlasController.xcodeproj/project.pbxproj`
- `MusicAtlasController/Models/`
- `MusicAtlasController/Resources/`
- `MusicAtlasController/Services/`
- `MusicAtlasController/Views/`
- `MusicAtlasControllerTests/`
- `supabase/functions/generate-first-mission-batch/index.ts`

Notable untracked runtime or contract candidates included:

- new app resources under `MusicAtlasController/Resources/`
- `MusicAtlasController/Services/AlphaDynamicSurveyPageProvider.swift`
- `MusicAtlasController/Services/AlphaSurveyPagePacketProvider.swift`
- `MusicAtlasControllerTests/Fixtures/`
- substantial new `data/`, `docs/`, `scripts/`, `supabase/`, and harness content

## Size Snapshot

| Path | Size | Initial classification |
| --- | ---: | --- |
| `.` | 806M | whole repo working tree |
| `build/` | 448M | local build/cache output |
| `data/` | 180M | mixed source, contracts, fixtures, generated artifacts |
| `waymark-ai-tests/` | 42M | test harness plus generated outputs |
| `MusicAtlasController/` | 12M | runtime source |
| `docs/` | 12M | product/technical contracts plus generated review evidence |
| `waymark-atlas-tests/` | 3.3M | test harness plus generated outputs |
| `review_packets/` | 2.9M | generated review/archive packets |
| `supabase/` | 1.8M | backend runtime source and infra contracts |
| `scripts/` | 1.3M | tooling source |

## Current Tracked Baseline

Tracked repo contents are still comparatively small and mostly include:

- `.gitignore`
- app project, Swift source, entitlements, app icons, and bundled schemas/resources
- app XCTest files
- `README.md`
- tracked `data/missions/` fixtures
- tracked `data/schemas/` contracts
- tracked `data/exports/**/.gitkeep`
- tracked v0.2 app-dev kickoff packet
- tracked validation scripts
- `supabase/functions/generate-first-mission-batch/index.ts`
- `tests/README.md`

No tracked `.zip` files were found.

## `.gitignore` State

Already ignored before this pass:

- `.DS_Store`
- `build/`
- `DerivedData/`
- Xcode user state
- SwiftPM build folders
- Python bytecode and virtualenv folders
- `waymark-ai-tests/.env`
- Supabase function env files except `.env.example`
- `supabase/.temp/`
- `data/exports/dev/*` and `data/exports/acceptance/*` except `.gitkeep`

Added in this pass:

- Xcode archive/result artifacts: `*.xcarchive/`, `*.xcresult/`, `*.dSYM/`, `*.ipa`
- harness local env variants for `waymark-ai-tests/` and `waymark-atlas-tests/`
- generated/archive zip patterns: `data/*.zip`, `data/**/*.zip`, `review_packets/*.zip`, `waymark-ai-tests/review_packets/*.zip`
- generated harness outputs and reports:
  - `waymark-ai-tests/outputs/*`
  - `waymark-ai-tests/reports/*`
  - `waymark-atlas-tests/outputs/*`
  - `waymark-atlas-tests/reports/*`
  - `.gitkeep` exceptions for each output/report directory

## Classification Inventory

### Runtime Source

| Path | Notes |
| --- | --- |
| `MusicAtlasController.xcodeproj/` | Xcode project and shared scheme. |
| `MusicAtlasController/Models/` | Swift app model layer. Active changes present. |
| `MusicAtlasController/Services/` | Runtime services including MusicKit, mission loading, survey, export, persistence, and alpha survey providers. Active changes present. |
| `MusicAtlasController/Views/` | SwiftUI app views. Active changes present. |
| `MusicAtlasController/Support/` | Info.plist, entitlements, MusicKit setup notes. |
| `MusicAtlasController/Resources/` | App-bundled icons, schemas, and current alpha JSON resources. Several new large runtime resource candidates are untracked and should be reviewed before committing. |
| `supabase/functions/` | Edge Functions. `generate-first-mission-batch` is tracked and modified; submit diagnostic/evidence functions are untracked runtime candidates. |
| `supabase/migrations/` | Untracked database migrations; likely backend runtime source. |
| `supabase/config.toml` | Untracked Supabase project config; likely backend runtime source. |
| selected `scripts/` | Validation, generation, smoke, and import scripts that support runtime contracts. Many are untracked and should be reviewed by purpose. |

### Test/Source Fixture

| Path | Notes |
| --- | --- |
| `MusicAtlasControllerTests/` | XCTest source. |
| `MusicAtlasControllerTests/Fixtures/` | Untracked test fixtures for mission and Apple Music signal payload tests. |
| `data/missions/` | Tracked mission fixtures. |
| `docs/app_dev/kickoff_v0_2/sample_mission_love_tributaries_v0_2.json` | Tracked kickoff fixture. |
| `docs/app_dev/kickoff_v0_2/*.json` | Tracked schema examples; also technical-contract adjacent. |
| `data/alpha_packets/golden_alpha_packet_v0_1/` | Golden packet and app-import fixture material. |
| `data/atlas_schema/examples/` | Atlas schema examples. |
| `data/survey_simulation/schemas/`, `fake_profiles/`, `apple_payloads/`, `hidden_reaction_corpora/` | Simulator fixtures or fixture-like inputs; do not blanket-ignore. |
| `waymark-ai-tests/src/` | First-class mission-generation harness code. |
| `waymark-ai-tests/fixtures/` | First-class harness fixtures. Some generated digest snapshots function as integration fixtures. |
| `waymark-atlas-tests/src/` | First-class Atlas ingestion harness code. |
| `waymark-atlas-tests/fixtures/` | First-class Atlas harness fixtures. |

### Product/Technical Contract

| Path | Notes |
| --- | --- |
| `README.md` | Current tracked repo overview, now older than the alpha surface. |
| `data/schemas/` | Tracked JSON schemas. |
| `data/product_contracts/` | Untracked contracts and PM alpha briefs. |
| `data/atlas_schema/` roots | Atlas contract, schema docs, delta schema, acceptance report, alpha hardening contracts. |
| `data/alpha_consumable_layer/` | Alpha graph surfaces, resolver policy, guardrails, and route/candidate contracts. |
| `docs/app_dev/` | App specs, TestFlight reports, audit notes, brand transition docs, mockups. Mixed tracked/untracked. |
| `docs/app_dev/kickoff_v0_2/` | Tracked v0.2 controlling product and implementation packet. |
| `docs/alpha_backlog/` | Active alpha lane backlog and dispatch material. |
| `docs/infra/` | Supabase, diagnostics, evidence upload, and operations contracts. |
| `supabase/README.md` and `supabase/alpha_infra_acceptance_report.md` | Untracked infra docs. |

### Generated Artifact

| Path | Notes |
| --- | --- |
| `data/survey_simulation/runs/` | Generated simulator runs. |
| `data/survey_simulation/reports/` | Generated simulator reports. |
| `data/survey_simulation/llm_profile_review/` | Generated LLM review evidence; includes zip bundles. |
| `data/mission_generation/alpha_first_batch_route_ready_v0_1/` | Timestamped generated request/response attempts and app-import candidates. |
| `data/closed_loop_simulation/` | Generated closed-loop simulation evidence and adaptive contract outputs. |
| `data/atlas_schema/ingestion_proof/` | Generated proof bundles and validation evidence, plus some docs worth preserving. |
| `data/atlas_schema/node_interpretation_smoke/` and `wwtsf_substrate_smoke/` | Generated smoke outputs. |
| `review_packets/*.zip` | Generated review packets, now ignored for future accidental adds. |
| `waymark-ai-tests/outputs/` | 153 timestamped generated run directories, now ignored except `.gitkeep`. |
| `waymark-ai-tests/reports/` | Generated harness reports, now ignored except `.gitkeep`. |
| `waymark-atlas-tests/outputs/` | Generated Atlas ingestion run directories, now ignored except `.gitkeep`. |
| `waymark-atlas-tests/reports/` | Generated harness reports, now ignored except `.gitkeep`. |
| `docs/reviews/canonical_graph/canonical_graph_parallel_review.md` | Generated/staging review doc moved out of repo root in the next cleanup pass. |
| `docs/reviews/canonical_graph/waymark_canonical_graph_review_bundle_v0_1.md` | Generated/staging review bundle moved out of repo root in the next cleanup pass. |
| dated TestFlight/upload/audit docs | Useful evidence, but generated report-like artifacts. Keep visible until accepted archive structure is chosen. |

### Local Build/Cache Output

| Path | Notes |
| --- | --- |
| `build/` | 448M Xcode build products, DerivedData, `.xcarchive` directories, dSYMs, and device smoke exports. Already ignored. Not deleted in this pass. |
| `.venv/` | Local Python virtual environment. Ignored. |
| `supabase/.temp/` | Supabase CLI local state. Ignored. |
| `data/exports/` | Local app/device/export outputs. Ignored except tracked `.gitkeep` placeholders. |
| `.DS_Store` files | Ignored. Present in several directories but not deleted. |

### Candidate For External/Archive Storage

| Path | Reason |
| --- | --- |
| `data/**/*.zip` | Generated review/evidence/handoff bundles. Prefer external artifact storage or a repo manifest. |
| `review_packets/*.zip` | Generated review packet archives. |
| `waymark-ai-tests/review_packets/*.zip` | Generated harness review packet archives. |
| `data/mission_generation/**/request/` and raw response attempts | Timestamped LLM/API run evidence; bulky and often reproducible. |
| `data/survey_simulation/llm_profile_review/` | LLM evidence bundles and review outputs. |
| `data/deprecated_mission_fixtures/` | Deprecated duplicate fixtures; requires owner approval before removal. |
| `docs/app_dev/brand_assets/*.png` | Large generated/reference PNGs, about 11M total; keep only if they are canonical design inputs. |
| `docs/reviews/canonical_graph/` | Home for generated canonical graph review Markdown moved out of repo root. Archive externally or into a dated docs archive when no longer active. |
| old local `build/*.xcarchive` directories | Local build artifacts; can be deleted locally only after confirming no dSYM/archive retention need. |

## Large Artifact Findings

Largest directory-level findings:

- `build/`: 448M, ignored local build output.
- `data/survey_simulation/`: 78M, mixed fixtures and generated simulation/LLM artifacts.
- `data/atlas_schema/`: 37M, contracts plus generated ingestion proof evidence.
- `waymark-ai-tests/outputs/`: 38M, generated harness outputs.
- `data/canonical_graph/`: 19M, canonical/product source material mixed with generated import and normalization artifacts.
- `data/mission_generation/`: 18M, contracts plus generated first-batch attempts.
- `data/alpha_consumable_layer/`: 15M, contract/canonical handoff material with a large audit refs JSON.
- `docs/app_dev/brand_assets/`: 11M, large untracked PNG references.

Largest notable files:

- `data/alpha_consumable_layer/alpha_v0/survey_page_selection_audit_refs_alpha_v0.json`: 13M.
- `data/canonical_graph/normalization_pass_2/survey_song_candidates_v0_2.json`: 2.9M.
- `MusicAtlasController/Resources/survey_song_candidates_v0_2.json`: 2.9M, runtime resource candidate.
- `MusicAtlasController/Resources/survey_artist_candidates_v0_2.json`: 2.1M, runtime resource candidate.
- `MusicAtlasController/Resources/survey_album_candidates_v0_2.json`: 1.8M, runtime resource candidate.
- `data/survey_simulation/hidden_reaction_corpora/*.json`: about 1.9M to 2.0M each.
- `data/exports/review_packets/waymark_canonical_graph_full_export_2026-05-26.zip`: 1.9M, already ignored by `data/exports/*`.
- `data/survey_simulation/llm_profile_review/evidence_bundles/gpt_5_5_3x3_2026_05_20.zip`: 1.4M, now covered by zip ignore.

## Approval-Needed Follow-Ups

Resolved in the next cleanup pass:

- `waymark-ai-tests/` and `waymark-atlas-tests/` are first-class tracked harnesses for README, config examples, `pyproject.toml`, `docs/`, `src/`, and `fixtures/`.
- Harness `outputs/`, generated `reports/`, local `.env*`, and zip review packets remain generated/local and ignored by default.
- `data/README.md` now defines source-of-truth paths, first-class fixture paths, generated/archive candidates, and promotion rules for `data/`.
- Root-level canonical graph review Markdown moved to `docs/reviews/canonical_graph/`.
- `build/` was retained locally because repo docs reference TestFlight archives and those archives contain dSYMs; delete only after dSYM/archive retention is confirmed elsewhere.

Remaining follow-ups:

1. Review all `data/**/*.zip`, `review_packets/*.zip`, and harness review packet zips for external artifact storage.
2. Promote selected generated reports into `docs/` only when they are accepted as evidence.
3. Classify `data/survey_simulation/` more deeply into source fixtures, generated runs, and historical LLM evidence.
4. Classify `data/atlas_schema/ingestion_proof/` into contract proof fixtures vs generated run evidence.
5. Decide whether `docs/app_dev/brand_assets/*.png` are canonical brand inputs or external design artifacts.
6. Review `data/deprecated_mission_fixtures/` before deleting or archiving duplicate mission fixtures.
