# Agent Repo Stewardship Policy

This repo is an active iOS TestFlight alpha workspace. Treat the worktree as shared with humans and other agents.

## Start Here

Before editing, read:

- `README.md`
- `docs/repo_map.md`
- `docs/repo_cleanup_inventory_2026_05_26.md`
- `data/README.md` before touching anything under `data/`

Run `git status --short` before making changes. If unrelated app/runtime work is already present, leave it alone.

## Core Rules

- Do not revert, delete, move, or reformat user/agent changes you did not make.
- Do not run destructive git commands such as `git reset --hard` or `git checkout --` unless explicitly asked.
- Do not delete files unless they are clearly local-only cache/build output or the owner has approved the deletion.
- Do not blanket-ignore or blanket-delete mixed directories such as `data/`, `docs/`, `MusicAtlasController/Resources/`, or harness fixtures.
- Keep cleanup slices small and logical. Prefer documentation, ignore rules, manifests, and clearly scoped source promotion over broad reshuffles.
- Use `rg`, `find`, `du`, `git status`, `git ls-files`, and `git check-ignore` for inventory and classification.
- Use `apply_patch` for manual file edits.

## What Belongs Where

- App runtime source and shipped resources belong in `MusicAtlasController/`, `MusicAtlasControllerTests/`, and `MusicAtlasController.xcodeproj/`.
- Supabase runtime/backend source belongs in `supabase/`; `supabase/.temp/` and local env files stay ignored.
- Product contracts, repo stewardship docs, accepted reviews, and runbooks belong in `docs/`.
- Source-of-truth data, accepted fixtures, contracts, and promotion notes belong in `data/` according to `data/README.md`.
- Harness code and deterministic fixtures belong in `waymark-ai-tests/` and `waymark-atlas-tests/`.
- Generated run outputs, reports, zips, review packet workspaces, local exports, build products, archives, dSYMs, virtualenvs, and local secrets should stay ignored or external unless explicitly promoted.

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

## Staging And Commits

Stage only the files that belong to the current slice. Before committing, verify:

- `git diff --cached --name-only`
- `git diff --cached --check`
- relevant parsers/tests/smoke checks for touched code or JSON
- no local secrets or machine-specific paths were added

Keep repo-cleanup commits separate from app/runtime commits. If the remaining diff is mostly Swift, Xcode project wiring, app resources, tests, or backend behavior, treat it as runtime work unless the owner explicitly asks cleanup to handle it.

## If Unsure

Stop and document the classification instead of moving or deleting. Ask for owner approval when a file could be canonical product data, a test fixture, a release/debug artifact, a dSYM/archive retention item, or an app-shipping resource.
