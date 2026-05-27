# Core Return Integration Acceptance Checklist

Date: 2026-05-24

Purpose: final integration gate for the next TestFlight Alpha after Core finishes the live-smoke recovery work.

## Current Lane State

- Core Waymark Build: still running.
- Supabase / Infrastructure: complete for the current recovery pass.
- Mission Generation / Closed Loop: complete unless Core reports new response-shape or import-policy blockers.
- Survey Simulator: complete unless Core reports new page-selection audit or quarantine-shape blockers.
- Canonical Music Graph: complete unless Core/Mission reports a new candidate safety/review-risk blocker.
- Atlas Schema: complete unless Core/Infra reports a new diagnostic/evidence classification blocker.

## Do Not Reopen Idle Lanes Unless

Reopen a completed lane only if Core raises a concrete blocker with:

- exact file or payload shape
- expected field/behavior
- actual field/behavior
- owning lane
- why Core cannot proceed with a local adapter or diagnostic fallback

## Core Completion Must Include

- `CWB-030`: generation continues after isolated `review_needed` attempts and keeps working toward 10 missions.
- `CWB-031`: client diagnostic artifacts are captured and can be manually uploaded/exported.
- `CWB-032`: Survey runtime audit is persisted enough to explain displayed tiles and quarantined responses.
- `CWB-033`: a next device/TestFlight smoke report is produced after the build.

## Integrated Acceptance Gates

Gate 1: First-run flow

- Existing install migrates/clears old Alpha state as intended.
- User accepts current Alpha terms/privacy acknowledgement.
- Sign in with Apple succeeds through Supabase Auth.
- Apple Music authorization succeeds.
- Onboarding completes.
- Required Survey starts clean.

Gate 2: Survey

- Exactly 4 artist pages, 2 album pages, and 4 song pages are displayed.
- Survey responses total is explainable against displayed pages.
- Quarantined responses, if any, include reason counts.
- `survey_page_selection_audit` exists locally and can be uploaded/exported.
- Apple exposure is marked as exposure context, not taste truth.

Gate 3: Generation/import

- App sends real Survey Evidence Export and digest/candidate context to Supabase.
- Supabase writes `alpha_generation_runs` rows.
- `app_import_candidate` imports normally.
- `review_needed` with `alpha_import_policy.app_import_allowed_for_trusted_alpha=true` does not hard-stop the whole batch.
- `blocked` and failed app validation still do not import.
- App keeps attempting until it imports 10 missions or reaches a documented hard stop / max-attempt ceiling.
- Generation screen shows visible activity and progress.

Gate 4: Diagnostics

- App can upload/export:
  - `apple_music_signal_payload`
  - `survey_page_selection_audit`
  - `survey_evidence_export`
  - `mission_generation_request_packet`
  - `mission_generation_result`
  - `mission_import_result`
  - `client_error_event`
- Supabase persists diagnostics to `alpha_client_diagnostic_artifacts`.
- `scripts/summarize_alpha_live_run.mjs` can summarize the tester run by alias/time window.

Gate 5: User-facing UI

- No prebuilt missions appear as user content.
- Resolve/MusicKit diagnostics remain hidden from normal tester UI.
- Manual import/debug controls remain hidden from normal tester UI.
- Tester sees clear generation/progress states.
- Tester can enter the core app once usable missions are available.

Gate 6: Evidence

- Manual Share Evidence remains available.
- Manual authenticated evidence upload works when a saved evidence package exists.
- Automatic evidence/diagnostic upload remains off until final privacy/retention/deletion/support policy is approved.

## PM Summary Query

After a physical/TestFlight run, use:

```sh
SUPABASE_URL=... SUPABASE_SERVICE_ROLE_KEY=... node scripts/summarize_alpha_live_run.mjs --tester-alias <alias> --since <iso>
```

Expected summary should show:

- generation run count
- `app_import_candidate` count
- `review_needed` count
- blocked/failed count
- diagnostic artifact count
- evidence artifact count
- run IDs and client request IDs

## Remaining Product/Policy Blockers

- Final privacy/terms/retention/deletion/support copy.
- Automatic evidence/diagnostic upload approval.
- Final app icon/art polish.

These do not block the next trusted internal Alpha smoke, but they do block broader external polish and automatic upload.
