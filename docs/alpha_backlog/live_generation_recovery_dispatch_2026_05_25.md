# Live Generation Recovery Dispatch - 2026-05-25

## Broadcast Note

Send this to every active lane:

```text
Please read docs/alpha_backlog/live_generation_recovery_dispatch_2026_05_25.md first, then open your lane-specific file linked there. The immediate Alpha blocker is live mission generation/import: Supabase is producing missions, but live validation is still allowing duplicate route item IDs, non-candidate route items, and repeated items across the 10-mission batch. Work every non-dependent task in your lane until you hit a dependency listed in the file. Edit your lane file with status, outputs, tests, and blockers.
```

## Current Evidence

Start with:

- `docs/infra/waymark_alpha_live_diagnostic_evidence_review_2026_05_25.md`
- `docs/infra/waymark_alpha_generation_recovery_implementation_2026_05_25.md`
- `docs/app_dev/waymark_alpha_app_state_recovery_diagnostics_audit_2026_05_25.md`
- `docs/app_dev/waymark_alpha_intake_lineage_report_2026_05_25.md`

Latest live finding:

- Build 12 sent clean Survey evidence to Supabase.
- Supabase generated rows, so auth/generation access is working.
- Live backend marked invalid missions as `app_import_candidate`.
- The app importer correctly rejected duplicate route `item_id` cases.
- `alpha_client_diagnostic_artifacts` has zero rows, so support diagnostics upload still needs proof.

## Shared Goal

Next TestFlight smoke should:

- start fresh
- complete Alpha Survey
- generate/import 10 missions
- reject bad model output before app import
- never strand the tester on the generation screen
- upload support diagnostics into Supabase when requested
- leave enough Supabase audit evidence to reconstruct Survey -> generation -> import

## Lane Files

| lane | file | priority |
| --- | --- | --- |
| Supabase / Infrastructure | `docs/alpha_backlog/live_generation_recovery_supabase_infrastructure_2026_05_25.md` | P0 |
| Core Waymark Build | `docs/alpha_backlog/live_generation_recovery_core_waymark_build_2026_05_25.md` | P0 |
| Mission Generation / Closed Loop | `docs/alpha_backlog/live_generation_recovery_mission_generation_2026_05_25.md` | P0 |
| Survey Lineage | `docs/alpha_backlog/live_generation_recovery_survey_lineage_2026_05_25.md` | P1 |
| Canonical Graph / Atlas Support | `docs/alpha_backlog/live_generation_recovery_canonical_atlas_support_2026_05_25.md` | P1 |

## Dependency Order

1. Infrastructure deploys and verifies live Supabase guards.
2. Core packages only after Infrastructure confirms live backend accepts the new diagnostics and route-identity validation.
3. Mission Generation can work in parallel on prompt/contract/fixture hardening.
4. Survey Lineage can work in parallel on diagnostic lineage and Survey quality findings.
5. Canonical Graph / Atlas stays mostly support-mode unless ID/display-name/ingestion contract issues are found.

## Cross-Lane Non-Negotiables

- No bundled/prebuilt missions as Alpha user content.
- Survey evidence is provisional evidence, not promoted Atlas truth.
- Apple Music data is exposure/resolution context, not taste truth.
- Mission generation must use concrete candidate-pool objects only.
- App import readiness is stricter than schema validity.
- A `review_needed` mission may be retained for support diagnostics, but must not enter the app unless locally app-valid.
- Diagnostics are support artifacts, not Atlas truth and not automatic upload until policy approves it.

## Report-Back Format

Each lane should append a completion note to its lane file:

```text
## Completion Note

- status:
- files changed:
- commands/tests run:
- live deploy or build number:
- remaining blockers:
- handoff needed from:
```
