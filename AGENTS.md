# Agent Repo Stewardship Policy

This repo is an active Cartenza iOS TestFlight alpha workspace. Treat the worktree as shared with humans and other agents.

Waymark is the former product name. New product-facing text should say Cartenza unless it is quoting historical material or referring to an existing technical identifier.

## Start Here

Before editing, read:

- `README.md`
- `docs/repo_map.md`
- `docs/brand_migration_cartenza.md`
- `docs/repo_cleanup_inventory_2026_05_26.md`
- `data/README.md` before touching anything under `data/`

Run `git status --short` before making changes. If unrelated app/runtime work is already present, leave it alone.

## Core Rules

- Do not revert, delete, move, or reformat user/agent changes you did not make.
- Do not run destructive git commands such as `git reset --hard` or `git checkout --` unless explicitly asked.
- Do not delete files unless they are clearly local-only cache/build output or the owner has approved the deletion.
- Do not blanket-ignore or blanket-delete mixed directories such as `data/`, `docs/`, `MusicAtlasController/Resources/`, or harness fixtures.
- Keep cleanup slices small and logical. Prefer documentation, ignore rules, manifests, and clearly scoped source promotion over broad reshuffles.
- Do not opportunistically rename legacy Waymark technical identifiers. Schema IDs, environment variables, Supabase config, persisted filenames, package names, and harness directories need an explicit migration plan and validation.
- Use `rg`, `find`, `du`, `git status`, `git ls-files`, and `git check-ignore` for inventory and classification.
- Use `apply_patch` for manual file edits.

## Naming And Brand Policy

- Current product name: Cartenza.
- Former product name: Waymark.
- New human-facing docs, app copy, review notes, and generated filenames should prefer `Cartenza` / `cartenza` unless they are tied to a legacy contract.
- Existing `waymark.*` schema IDs, `WAYMARK_*` environment variables, `waymark-*` directories, Python package names, persisted JSON filenames, Supabase project IDs, and historical review/archive filenames remain as-is until a coordinated migration updates all references and tests in one slice.
- Historical docs may keep Waymark in titles and filenames when the name is part of the artifact provenance.

## What Belongs Where

- App runtime source and shipped resources belong in `MusicAtlasController/`, `MusicAtlasControllerTests/`, and `MusicAtlasController.xcodeproj/`.
- Supabase runtime/backend source belongs in `supabase/`; `supabase/.temp/` and local env files stay ignored.
- Product contracts, repo stewardship docs, accepted reviews, and runbooks belong in `docs/`.
- Source-of-truth data, accepted fixtures, contracts, and promotion notes belong in `data/` according to `data/README.md`.
- Harness code and deterministic fixtures belong in the legacy-named `waymark-ai-tests/` and `waymark-atlas-tests/` directories until those packages are migrated deliberately.
- Generated run outputs, reports, zips, review packet workspaces, local exports, build products, archives, dSYMs, virtualenvs, and local secrets should stay ignored or external unless explicitly promoted.

## Production Track Separation

- Treat the current TestFlight alpha runtime as the production track, even while the app is pre-release.
- Keep production-track app code/resources in `MusicAtlasController/`, `MusicAtlasControllerTests/`, and `MusicAtlasController.xcodeproj/`; document app-bundled resource classes in `MusicAtlasController/Resources/README.md`.
- Keep production-track source manifests, canonical graph inputs, contracts, and promotion notes in `data/` according to `data/README.md`.
- Keep cleanup/status packets and stewardship notes in `docs/`; do not scatter new status Markdown at repo root.
- Mark legacy or deprecated product paths in docs before deleting or rewiring them. Old Waymark identifiers, old sample/personal mission fixtures, legacy Survey priors, and superseded mission-generation paths require explicit migration or retirement notes.
- Do not mix production runtime promotion, generated artifact archival, repo cleanup, and brand/name migration in one commit unless the owner explicitly asks for a combined slice.

## Data And Artifact Policy

Classify files before acting:

- Runtime source
- Test/source fixture
- Product/technical contract
- Generated artifact
- Local build/cache output
- Candidate for external/archive storage

Generated artifacts become first-class only when a maintainer promotes a specific file or directory into `docs/`, `data/product_contracts/`, `data/schemas/`, `data/missions/`, `data/alpha_packets/`, a harness `fixtures/` directory, or another documented source path with a short reason.

Prefer tracking a source directory, manifest, or small review note over tracking a zip bundle.

## Survey Candidate Policy

- Survey tiles are not limited to legacy `survey_*_candidates_v*.json` surfaces. Those files can serve as priors, compatibility resources, or debug fixtures, but they are not the product ceiling.
- Any active canonical graph artist, album, or song may be eligible for Survey display when it has an appropriate usable Apple Music catalog resolution, is not quarantined/suppressed/blocklisted, and matches the object type for the page.
- For Survey purposes, "active" means the canonical object is present in the current canonical graph/app canonical resources and has a verified Apple Music ID or catalog-index resolution for the object type being displayed.
- Rows without usable Apple Music resolution may remain in the canonical graph for research, contracts, or future hardening, but they must not feed automatic Survey display or default playback surfaces.
- When discussing Apple-seeded Survey logic, "top artists" means artists ranked highest by the Apple payload scoring/rollup process, not canonical popularity, recognition tier, or old survey-surface priority.

## Staging And Commits

Stage only the files that belong to the current slice. Before committing, verify:

- `git diff --cached --name-only`
- `git diff --cached --check`
- relevant parsers/tests/smoke checks for touched code or JSON
- no local secrets or machine-specific paths were added

Keep repo-cleanup commits separate from app/runtime commits. If the remaining diff is mostly Swift, Xcode project wiring, app resources, tests, or backend behavior, treat it as runtime work unless the owner explicitly asks cleanup to handle it.

## If Unsure

Stop and document the classification instead of moving or deleting. Ask for owner approval when a file could be canonical product data, a test fixture, a release/debug artifact, a dSYM/archive retention item, or an app-shipping resource.
