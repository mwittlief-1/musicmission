# Waymark Alpha Orientation Flow Implementation Handoff v0.1

Status: approved for Alpha 1 Swift implementation by Product/Founder on 2026-05-22.

Source mock:

- `docs/app_dev/mockups/alpha_orientation_flow_v0_1/index.html`
- `docs/app_dev/mockups/alpha_orientation_flow_v0_1/README.md`

## Approval Scope

This approval unblocks Core/UI implementation of:

- the first-run flow order
- the screen hierarchy and information architecture
- dark, portrait-first, mobile-first visual direction
- the guided Apple access, onboarding, Survey, generation, mission, player, review, and account surfaces
- `Share Evidence` as the user-facing evidence language

This approval does not by itself finalize:

- legal/privacy/terms copy
- retention, deletion, support-access, or automatic evidence upload policy
- final onboarding or FAQ text if Product/Release replaces copy before TestFlight
- final app icon assets
- any production mission content

## Required Flow

Implement the approved Alpha 1 sequence as a gated path:

1. Privacy / Alpha disclosure gate
2. Sign in with Apple + Apple Music connection
3. Six onboarding pages
4. Alpha FAQ access point
5. Required Survey intake: 4 artist pages, 2 album pages, 4 song pages
6. Post-Survey generation status
7. Mission home with generated first batch
8. Mission detail
9. Player / listen and react
10. Mission review
11. Per-song evidence edit
12. My Account

Returning users should resume to the furthest valid completed state. If a Supabase or Apple session times out, route them back through the minimum reauthentication step without repeating accepted terms or completed onboarding unless the stored version changes.

## Screen Mapping

| approved mock surface | Swift target area | implementation notes |
| --- | --- | --- |
| Privacy | `RootView` first-run gate | Versioned acceptance; blocks account, Survey, generation, and upload. |
| Apple access | First-run access screen / auth services | One product CTA may trigger separate Sign in with Apple and MusicKit flows. |
| Welcome, steps, Survey, Missions, React, Atlas | Onboarding shell | Swipable pages; copy should be externally replaceable. |
| FAQ | My Account / help | Accessible after onboarding; optional link during orientation is fine. |
| Survey pages | `SurveyView` / Survey provider | Fixed Alpha intake count; no normal post-intake Survey tab. |
| Generating | Post-Survey generation status | Preserve cautious/provisional language; retry/recover without losing Survey. |
| Mission home | `MissionListView` or replacement home | No bundled missions; hide paste/import from normal testers once remote generation is live. |
| Mission detail | Mission detail surface | Mission hypothesis is the hero; route should not read like a playlist. |
| Player | `NowTestingView` | Brand center of gravity; reaction-specific secondary tags. |
| Review | `MissionReviewView` | Close the loop; show song/artist/album evidence rows. |
| Edit evidence | Review item editor | Primary selection, dependent tags, freeform note, clear save/update. |
| My Account | Account/help surface | Apple status, Apple Music status, FAQ, privacy, support, Share Evidence backup. |

## Implementation Priorities

Core/UI can proceed without waiting on Supabase live smoke:

- Apply approved visual hierarchy to existing SwiftUI first-run and core shells.
- Keep production TestFlight missionless until Survey completion and generated assignment.
- Keep `Share Evidence Backup` available as manual support fallback.
- Keep automatic evidence upload disabled until privacy/retention/deletion/support policy is approved.
- Keep debug import, raw JSON, resolver, and schema panels out of the normal Release path.
- Preserve dark mode and portrait-only constraints already added for Alpha.

## Open Dependencies

| dependency | owner | impact |
| --- | --- | --- |
| Final privacy/terms/retention/deletion/support copy | Product / Release | Replace placeholder consent and upload language before external testers. |
| Supabase authenticated smoke path | Infra / Core | Proves real auth session, generation, and upload writes. |
| Evidence upload policy | Product / Infra / Release | Determines whether Account shows sync status, manual backup only, or scheduled upload. |
| Final app icon candidates | Design / Release | Required for TestFlight polish. |

## Guardrails

- Do not ship prebuilt missions as user content.
- Do not expose Survey as a normal top-level tab after required intake.
- Do not describe Survey output or Atlas reads as final truth.
- Do not treat Apple Music exposure as taste truth.
- Do not upload evidence automatically before approved disclosure and retention/deletion policy.
- Do not show implementation terms such as schema, app-import, resolver, or generated JSON in normal Alpha UI.
