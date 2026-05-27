# Supabase Alpha Infrastructure Acceptance Report

Generated: 2026-05-27T12:22:46.523Z

## Tooling

- Supabase CLI: `not installed`
- Supabase CLI via npx: `2.101.0`
- Deno CLI: `not installed`
- Node: `v24.13.1`
- npx: `11.8.0`

Supabase and Deno CLI absence does not block offline fixture/typecheck validation. Live link, migration, secrets, and deploy still require a real Supabase project and access token.

## Local Checks

- pass: build fixtures
- pass: fixture smoke
- pass: edge function typecheck
- pass: evidence upload function typecheck
- pass: diagnostic upload function typecheck

## Live Supabase Status

- Project ref: `ewuffhezhgyskcfyzkvw`
- Project accessible: `yes`
- Project linked: `yes`
- Required migrations applied: `yes`
- Edge Function secrets checked: `yes`
- `OPENAI_API_KEY` present: `yes`
- `WAYMARK_ALPHA_REVIEW_NEEDED_APP_MISSION_POLICY` present: `yes`
- `WAYMARK_ALPHA_DIAGNOSTIC_TERMS_VERSION` present: `yes`
- `generate-first-mission-batch` deployed/active: `yes`
- `submit-alpha-evidence` deployed/active: `yes`
- `submit-alpha-diagnostic` deployed/active: `yes`

## Remaining Live Blockers

- authenticated app/JWT smoke path
- Supabase Auth Apple provider end-to-end smoke
- final privacy/retention/deletion policy before automatic evidence upload

## Result

`offline_acceptance_pass`
