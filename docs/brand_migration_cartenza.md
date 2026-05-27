# Cartenza Brand Migration Policy

Date: 2026-05-27

Cartenza is the current product name. Waymark is the former product name and remains present in existing technical identifiers, schemas, fixtures, archives, and historical documents.

This policy prevents accidental partial renames while the alpha app, backend, data contracts, and harnesses are changing in parallel.

Related planning and audit docs:

- `docs/app_dev/cartenza_brand_transition_backlog_v0_1.md`
- `docs/app_dev/cartenza_name_reference_audit_2026_05_27.md`

## Use Cartenza Now

Prefer Cartenza in new:

- product-facing docs
- app-visible copy
- review notes and runbooks
- new generated filenames that are not tied to an existing contract
- repo stewardship docs

Use lowercase `cartenza` for new machine filenames and slugs when no existing contract requires `waymark`.

## Keep Legacy Waymark Identifiers For Now

Do not rename these as incidental cleanup:

- `waymark.*` schema versions and `$id` values
- legacy `WAYMARK_*` environment variables, which remain accepted while new backend and harness config should prefer `CARTENZA_*`
- Supabase project IDs, function config keys, and deployment settings
- persisted app filenames such as local session or survey JSON files
- `waymark-ai-tests/`, `waymark-atlas-tests/`, and their Python package names
- test fixtures that assert existing contract values
- historical review packet filenames and manifests
- historical docs where Waymark is part of the artifact title or provenance

These identifiers can be renamed only in a dedicated migration that updates references, compatibility behavior, tests, docs, and deployment configuration together.

## File Rename Policy

Safe first-pass renames:

- new docs that are not referenced by scripts or tests
- newly generated reports before they are accepted as evidence
- root or docs-level Markdown titles when the file is not a historical artifact

Requires explicit migration:

- harness directories or Python packages
- app resource filenames referenced by Xcode, tests, schemas, or persisted state
- schema IDs or exported JSON contract fields
- Supabase environment variables and project identifiers
- zip/archive filenames already documented by manifests

When in doubt, add a note to this file or `docs/repo_map.md` instead of renaming the artifact.

## Suggested Migration Sequence

1. Update human-facing docs and app-visible copy to Cartenza.
2. Add compatibility aliases where app or backend code reads persisted Waymark-named local files or environment variables.
3. Rename new generated output defaults from `waymark_` to `cartenza_` while continuing to read legacy names.
4. Migrate harness package names and CLI entry points in one tested slice.
5. Migrate schema namespaces only with versioned contract approval.
6. Leave historical archives unchanged unless a maintainer explicitly republishes them under Cartenza names.

## Validation Checklist

Before committing a rename slice, run:

- `git diff --name-status`
- `git diff --check`
- `rg -n "Waymark|waymark|WAYMARK" <touched paths>`
- relevant JSON parsers, schema validators, harness tests, app tests, or Xcode build checks for touched paths

Do not stage unrelated runtime or data-generation changes with a brand rename slice.

## Current Compatibility State

- Supabase mission generation reads preferred `CARTENZA_*` env/secrets with fallback to legacy `WAYMARK_*` names.
- Mission-generation harness OpenAI/pricing config reads preferred `CARTENZA_OPENAI_*` and `CARTENZA_MODEL_PRICING_*` names with fallback to legacy `WAYMARK_*` names.
- Mission-generation and LLM profile-review tooling now prefers new generated output filenames such as `mission_output_cartenza_*` and `cartenza_survey_output_packet_*`, while readers and validators continue to tolerate legacy `mission_output_waymark_*` and `waymark_survey_output_packet_*` files.
- Generated prompt/report wording in active tooling uses Cartenza where it is user- or reviewer-facing; schema IDs, request schema names, package paths, and compatibility placeholders remain legacy Waymark identifiers.
- iOS bundle config and persisted app-state key migration are deferred to an app/runtime slice.
- Local persisted filenames and `waymark.alpha1.*` app state keys have not been migrated yet.
