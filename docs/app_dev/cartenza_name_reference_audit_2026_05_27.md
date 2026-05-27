# Cartenza Name Reference Audit - 2026-05-27

Scope: first Cartenza migration pass for repo policy, backend/tooling aliases, generated output defaults, active mockup copy, harness wording, and follow-up compatibility boundaries.

This audit does not authorize broad filesystem, schema, package, Supabase project, or archive renames. It records the classification used for the first safe naming slice.

## Updated In This Slice

- Supabase generation config now accepts preferred `CARTENZA_*` env/secrets while continuing to read legacy `WAYMARK_*` names.
- Mission-generation harness config now accepts preferred `CARTENZA_OPENAI_*` and `CARTENZA_MODEL_PRICING_*` variables while continuing to read legacy `WAYMARK_*` names.
- Generated mission packet and LLM profile-review public packet defaults now prefer `cartenza_*` filenames while readers, validators, and fixture builders tolerate legacy `waymark_*` filenames.
- Generated prompt/report wording for profile review, route-ready first-batch generation, survey simulation review, and A3 node-interpretation smoke now uses Cartenza while preserving legacy schema/request identifiers.
- Active Alpha orientation mockup and implementation handoff copy now use Cartenza. The visual token/route-art retune remains a separate backlog item.
- Root repo stewardship docs now identify Cartenza as the current product name.
- Legacy-named harness README/report/prompt wording now uses Cartenza while keeping existing `waymark-*` paths and Python package names.

## Keep As Legacy Technical Identifiers

Do not rename these without a dedicated compatibility migration:

- `waymark.*` schema IDs, `$id` values, and JSON contract fields
- legacy `WAYMARK_*` environment variables and Supabase secrets
- legacy `WaymarkSupabase*` Info.plist keys
- `waymark-ai-tests/`, `waymark-atlas-tests/`, and their Python package/import names
- persisted app filenames such as `waymark_survey_session_v0_1.json`, `waymark_session_library_v0_1.json`, and `waymark_reviewed_missions_v0_1.json`
- `waymark.alpha1.*` UserDefaults/AppStorage keys
- historical review packet filenames, PM alpha briefs, and dated archive manifests

## Compatibility Follow-Ups

These are good next migration candidates once the runtime slice is stable:

- Read legacy `waymark_*` persisted app files, then write new `cartenza_*` filenames after successful migration.
- Add an AppStorage migration from `waymark.alpha1.*` to a future `cartenza.alpha1.*` prefix.
- Add app-side `CartenzaSupabase*` Info.plist keys and keep legacy `WaymarkSupabase*` fallback in the same runtime slice.
- Decide whether accepted fixtures such as alpha1 required intake packets need explicit Cartenza successor artifacts; do not silently rename them.

## Deferred Or Historical

- Schema namespace changes require versioned contract approval across app, tests, Supabase fixtures, data contracts, and validators.
- Supabase project IDs and deployed secret names are deployment-sensitive and should not move as cleanup.
- Historical docs and archives should stay as Waymark when the name is part of artifact provenance.
- PM alpha briefs with Waymark in filenames should be superseded by Cartenza vNext docs rather than silently renamed.

## Validation Notes

This pass should be validated with:

- `git diff --check`
- Python compile checks for changed harness modules
- Supabase function typecheck/smoke checks for backend alias changes
