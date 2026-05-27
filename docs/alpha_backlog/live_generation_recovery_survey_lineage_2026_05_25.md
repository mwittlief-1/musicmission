# Survey Lineage Dispatch - Live Generation Recovery - 2026-05-25

## Mission

Make Apple Music payload -> Survey page construction -> Survey evidence export reconstructable, and identify Survey logic defects that are feeding poor mission candidates.

## Read First

- `docs/alpha_backlog/live_generation_recovery_dispatch_2026_05_25.md`
- `docs/app_dev/waymark_alpha_intake_lineage_report_2026_05_25.md`
- `docs/infra/alpha_client_diagnostic_audit_trail_v0_1.md`

## P1 Tasks

- [ ] SUR-LGR-001 Confirm page-selection diagnostic payload.
  - It should include page number, page kind, displayed items, item IDs, titles, artist/subtitle display, source mix, candidate basis, Apple exposure prior, prior-response summary, and visible history.
  - It should be PM-readable without exposing hidden simulator truth.

- [ ] SUR-LGR-002 Investigate page-repeat behavior.
  - Review why Page 3 repeated artists from earlier pages.
  - Review why tapping one tile caused the visible grid to reshuffle.
  - Confirm no-repeat rules are stable after response state changes.

- [ ] SUR-LGR-003 Investigate negative propagation.
  - If a tester dislikes an artist, album/song candidates from that artist should be suppressed or explicitly justified.
  - Report whether this is Survey selection, candidate-pool construction, or mission-generation behavior.

- [ ] SUR-LGR-004 Investigate display-name leakage.
  - Song/album grids should show human display names, not internal slugs such as `dolly-parton`.
  - Identify source fields Core should render.

- [ ] SUR-LGR-005 Produce a Survey lineage summary.
  - For one live-like session, summarize Apple exposure -> Page 1 -> later pages -> final Survey evidence export.
  - Include what cannot be reconstructed until diagnostic upload works.

## Acceptance

- A PM can explain why each displayed Survey tile appeared.
- Page repeats/reshuffles are either fixed or assigned to Core with concrete reproduction notes.
- Negative artist response behavior has a clear rule.
- Display-name source of truth is identified.

## Blockers To Raise

| issue id | blocker | owner lane | needed for | current workaround | status |
| --- | --- | --- | --- | --- | --- |
| `SUR-LGR-I001` | Live diagnostic artifacts are not in Supabase yet. | Core / Supabase Infrastructure | Apple payload and live page lineage reconstruction. | Use local app package if tester exports it to Mac/iCloud; otherwise use static session evidence only. | open |

## Completion Note

- status:
- files changed:
- commands/tests run:
- live deploy or build number:
- remaining blockers:
- handoff needed from:
