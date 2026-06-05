# Legacy Full OpenAI Mission Generation Deprecation Review - 2026-06-05

## Status

Deprecated for production-alpha app mission creation and manual mission regeneration.

Keep this path in the repo for possible backend review, replay, and retirement planning. Do not delete or rewire it as part of app runtime work without an explicit owner-approved deprecation slice.

## Decision

The production-alpha app should use the deterministic Survey/Atlas opportunity selector for mission creation and regeneration:

1. Read saved Survey evidence and eligible canonical Atlas/Apple Music references.
2. Score available opportunities by the approved mission-type selectors.
3. Retain the top six missions.
4. Import those six app-ready missions into the reviewed mission catalog.

Mission Enrichment v0.2 is a separate language/tag overlay contract. It may enrich already-selected missions with mission copy, per-route-item copy, and secondary reaction tag candidates, but it must not replace the deterministic mission-selection step.

## Deprecated Path

`supabase/functions/generate-first-mission-batch` is the legacy full OpenAI mission-generation path. It was previously used to create mission content inside the model call.

For the current production alpha, this path is not the app launch path and is not the manual Regenerate Missions path. It may remain in source control because it still has historical fixtures, infra reports, diagnostics, and possible review value.

## Guardrails

- Do not call `generate-first-mission-batch` from the iOS Regenerate Missions button.
- Do not require Supabase generation configuration for local deterministic regeneration.
- Do not use full OpenAI mission generation as a fallback unless the owner explicitly reopens this backend path.
- Any future review should define a separate contract, latency/cost envelope, test plan, and deployment plan before production-alpha use.
