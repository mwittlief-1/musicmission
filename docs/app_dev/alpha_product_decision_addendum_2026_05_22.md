# Alpha Product Decision Addendum

Date: 2026-05-22

Purpose: record Product decisions that supersede open questions in the Brand/UI review, screen spec, and Alpha lane backlogs.

## Decisions

| Area | Decision | Immediate implication |
| --- | --- | --- |
| App name | The app name is `Waymark`. | Rename install/display/app metadata from `Music Atlas` to `Waymark` before external TestFlight. |
| First launch | First launch must begin with privacy/terms acknowledgement. | Add first-run gate and persist acceptance locally/account-side as appropriate. |
| Login/access | User should have one easy button to sign in with Apple ID and connect Apple Music. | Implement or specify Sign in with Apple plus MusicKit authorization as a single guided step, while recognizing they are separate Apple capabilities. |
| Session persistence | Keep users authenticated as long as possible; reauthenticate via Apple ID only if timed out. | Core/Infra need auth persistence and graceful reauth states. |
| Onboarding | Required first-time guided onboarding after privacy/login. | Add swipable copy pages using founder-supplied near-final copy. |
| FAQ | Returning users should have an FAQ available after onboarding. | Put FAQ under My Account or equivalent, not in the first-run critical path after completion. |
| Survey | Survey is included in Alpha 1 and immediately follows onboarding. | Release Survey gating must change from debug-only to first-run intake flow. |
| Survey length | Force four artist screens, two album screens, and four song screens for Alpha intake. | Survey lane/Core must support fixed Alpha intake counts and no optional early exit. |
| Post-survey | After Survey, show a status/timer that Waymark is generating the user's Atlas and first missions. | Add generation/waiting surface and backend handoff. |
| Core IA | Core app IA appears only after Survey completion. | App should be first-run funnel first, core shell second. |
| Returning Survey access | Do not return users to Survey in normal Alpha use after intake. | Move Survey access to My Account only as a support/revisit path. |
| Missions | No prebuilt missions. First Alpha creates one batch of missions after Survey completion. | Backend generation is part of first-run completion; app must not ship mission content. |
| Evidence return | `Share Evidence` is fine, but Product prefers automatic/scheduled Supabase evidence push if engineering can support it safely. | Infra should design upload/sync after consent/retention policy; manual share remains fallback. |
| Disclosures | Privacy, terms, and related disclosures are required. | Release copy and in-app first-run consent become blockers. |
| App icon | App icon candidates are needed for founder review. | Design/Core should produce options; app icon remains required for external polish. |
| Visual system | Alpha is dark mode only. | Apply dark visual system across all Alpha surfaces. |
| Token pass | Treat token pass as reusable visual system values: colors, type scale, spacing, radii, semantic states. | Implement only the dark-mode Alpha token set needed for consistency. |
| Orientation | Restrict to portrait for Alpha. | Update iPhone supported orientations and QA policy. |

## Target Alpha 1 First-Run Flow

```text
Install / open Waymark
  -> Privacy + terms acknowledgement
  -> Sign in with Apple + connect Apple Music
  -> Required guided onboarding pages
  -> Required Survey intake
       - 4 artist screens
       - 2 album screens
       - 4 song screens
  -> Generating status / timer
       - "building your Atlas"
       - "building your first missions"
  -> Core app IA
       - first mission batch
       - player
       - review
       - share/sync evidence
       - My Account / FAQ
```

## Evidence Upload Position

Previous infra recommendation was manual export/share for Alpha 1 because privacy and retention were open. Product now prefers Supabase upload/sync if it can be implemented safely.

Updated engineering stance:

- Do not silently upload evidence until privacy/terms copy is approved and accepted in-app.
- Design the endpoint and data policy now.
- Prefer event-based or scheduled upload after meaningful evidence milestones, not a constant full sync loop.
- Keep manual `Share Evidence` as a fallback and support/debug path.
- Do not expose service-role keys in the app.
- Treat uploaded evidence as provisional Alpha evidence, not promoted Atlas truth.

## Superseded Open Questions

| Previous open question | New status |
| --- | --- |
| Waymark vs Music Atlas | Resolved: Waymark. |
| Survey visible in first TestFlight | Resolved: yes, required after onboarding. |
| Survey optional/advanced path | Resolved for Alpha intake: required fixed 4 artist / 2 album / 4 song screens; no normal return after intake. |
| Export vs Share Evidence | Direction: use Share Evidence language, with auto/scheduled Supabase upload preferred if privacy and engineering allow. |
| Dark vs mixed visual system | Resolved: dark mode only for Alpha. |
| Portrait vs landscape | Resolved: portrait-only for Alpha. |

## New Implementation Work By Lane

### Core Waymark Build

- Build the first-run state machine: consent -> Apple ID/MusicKit -> onboarding -> Survey -> generation wait -> core IA.
- Persist consent, onboarding completion, Survey completion, auth status, and generation status.
- Change Release Survey from debug-only tab to required first-run intake.
- Move post-intake Survey access to My Account/support.
- Add onboarding walkthrough shell and FAQ shell.
- Rename app metadata/display surfaces to Waymark.
- Restrict iPhone orientation to portrait.
- Apply dark-mode-only visual baseline across release surfaces.
- Reframe Export as Share Evidence and hide schema/dev language from normal Alpha users.
- Keep no-prebuilt-missions guardrail intact.

### Survey Simulator

- Produce/validate Alpha intake packet configuration for exactly 4 artist pages, 2 album pages, and 4 song pages.
- Make sure Survey Evidence Export carries enough refs for Atlas/Mission Generation without hidden simulator truth.
- Provide copy/UX notes for required, non-optional Alpha intake.
- Document whether each page is Apple-derived, graph-derived, or mixed without implying Apple exposure is taste truth.

### Supabase / Infrastructure

- Continue live project setup work when account/project is available.
- Add auth/user identity design for Sign in with Apple and Supabase, without full account/sync sprawl.
- Add backend handoff for Survey completion -> first mission batch generation.
- Design evidence upload/sync endpoint and retention/deletion policy hooks.
- Keep manual Share Evidence fallback.

### Mission Generation / Closed-Loop Learning

- Treat first batch as generated after Survey completion, not bundled.
- Ensure first batch response can be assigned/imported by Core automatically once Supabase handoff is live.
- Preserve audit status: generated, product-reviewed/app-import-candidate, blocked, or review-needed.

### Atlas Schema

- Confirm Survey Evidence Export -> Signal -> AtlasDigestView supports first mission batch generation.
- Confirm uploaded app evidence remains provisional and append-only.
- Confirm user-facing "building your Atlas" language is allowed without implying promoted Atlas truth.

### Brand / Design / Release

- Provide app icon candidates for Waymark.
- Provide dark-mode Alpha visual tokens: colors, typography scale, spacing, radii, semantic status colors.
- Provide privacy/terms/onboarding/FAQ copy for implementation.
- Approve TestFlight metadata language for the new first-run flow.
