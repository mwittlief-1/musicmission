# Waymark Brand/UI Review Playbook v0.1

Purpose: prepare an executive/brand review of the current Waymark TestFlight Alpha app without changing app code.

Status: read-only audit drafted on 2026-05-22 from the current repo, the unified Alpha brief, TestFlight readiness docs, screen inventory, backlog, and the attached `waymark_night_vision_brand_system_v0_4.pdf`. Updated with founder Alpha 1 decisions on 2026-05-22.

## Executive Summary

Waymark is currently a credible Alpha runtime for mission playback, evidence capture, review, and export, but the target Alpha 1 flow is now broader than the current release tab shell. Alpha 1 should be a first-run guided experience: accept privacy/terms, sign in with Apple, connect Apple Music, complete required onboarding pages, complete required Survey intake, wait while Waymark generates the initial Atlas and first mission batch, then enter the core app.

The current app proves important pieces of the loop: Apple Music authorization/playback, mission display, reactions/chips/notes, persistence, review edits, and export/share mechanics. The main gap is now orchestration. The release experience should not open into an unguided tab shell on first launch; it should shepherd the tester through account/access, onboarding, Survey, generation status, and only then reveal the core IA.

The UI is not yet one finished product surface. Player and Survey already point toward the attached Night Vision brand direction: dark-native, tactile, instrument-like, and music-first. Mission, Review, Export, and Apple Music authorization still read more like internal SwiftUI tooling. That mismatch is the main brand/UI issue before broader TestFlight.

Survey is now included in Alpha 1. The old debug-only posture is no longer the desired product posture, though the current app may still require implementation work to make Survey release-facing. For Alpha 1, the Survey should be required during first intake and should not remain a top-level repeated workflow afterward; tuck it under account/support if a return path is needed.

The highest TestFlight risk is not visual polish alone. It is user trust: prebuilt missions must not appear as user content, paste/import JSON must not feel like the consumer path, evidence sharing/sync must have plain disclosures, and no screen should imply Waymark has promoted durable taste truth from weak evidence.

## Inputs Audited

- `/Users/matt_wittlief_home/Downloads/waymark_unified_alpha_product_technical_brief_v0_2.md`
- `docs/app_dev/user_facing_screen_spec_v0_1.md`
- `docs/app_dev/alpha_product_decision_addendum_2026_05_22.md`
- `docs/app_dev/testflight_non_code_readiness_checklist_v0_1.md`
- `docs/app_dev/testflight_packaging_checklist.md`
- `docs/alpha_backlog/README.md`
- Attached brand PDF: `waymark_night_vision_brand_system_v0_4.pdf`
- SwiftUI views under `MusicAtlasController/Views/`
- Supporting release/debug facts in `MusicAtlasController/Services/MissionLoader.swift`, `MusicAtlasController/Support/Info.plist`, and `MusicAtlasController.xcodeproj/project.pbxproj`

## Current Product/UI State

Current release tabs are Mission, Player, Review, and Export. Survey and Resolve are debug-only via `AppFeatureFlags`; Export debug panels are also debug-only. This is the current repo state, not the desired Alpha 1 first-run IA.

The installed display name is currently `Music Atlas`, while the target app name is now decided as `Waymark`. The main Mission navigation title already says `Waymark`; install name, TestFlight metadata, privacy copy, icon, and launch surfaces should align to Waymark.

Release builds are configured to exclude the current sample/personal mission JSON resources, and the app runtime only includes debug bundled missions when `DEBUG` is true. This supports the guardrail that TestFlight should not ship with prebuilt missions as user content, but the Release build still needs the packaging checklist verification before distribution.

There is no `.xcassets` catalog discovered in the repo, and `UILaunchScreen` is empty. App icon and launch presentation are therefore still open brand/release items.

## Alpha 1 Product Decisions Captured

These decisions should now be treated as the product target for Alpha 1 review.

| Area | Decision |
| --- | --- |
| App name | Use `Waymark`. Retire `Music Atlas` as the installed/display name unless there is a deliberate transitional reason. |
| First-run gate | On first open, require privacy/terms acceptance before account/access and onboarding. |
| Account | Provide a single easy CTA that begins Sign in with Apple and Apple Music connection. Apple may still present separate OS permission/authentication moments; the product should feel like one guided action. |
| Session persistence | Keep the user signed in as long as the platform/backend safely allow. On return, only reauthenticate with Apple if the session has timed out or credentials require refresh. |
| Guided onboarding | Required on first use after account/access. It is a simple swipeable page sequence using supplied copy. Returning users should have FAQ access after onboarding. |
| Survey | Include Survey in Alpha 1. Make it required immediately after onboarding. Do not expose Survey as a normal repeat tab after intake; place any return path under My Account/support. |
| Survey length | Force four artist screens, two album screens, and four song screens for Alpha 1 intake. This supersedes the current debug screen inventory, which has fewer pages. |
| Post-Survey generation | After Survey completion, show a short status/timer message that Waymark is generating the user's Atlas and first missions. |
| Missions | No prebuilt missions as user content. First Alpha creates one batch of missions after Survey completion. |
| Evidence return | `Share Evidence` is acceptable language, but engineering should confirm whether Alpha evidence is pushed to Supabase automatically/scheduled or shared manually as a support fallback. |
| Disclosures | Privacy, retention, support, Apple Music access, evidence storage, and evidence sharing disclosures are required. |
| Visual system | Alpha is dark mode only. Apply the Night Vision direction across the release path. |
| Orientation | Restrict Alpha to portrait unless engineering/product explicitly choose to QA landscape. |
| Icon/launch | App icon and launch visual are required; founder will review candidates. |

## Target Alpha 1 First-run Flow

This is the recommended review baseline.

```text
Open Waymark
→ Accept privacy / terms / Alpha disclosures
→ Sign in with Apple + connect Apple Music
→ Required guided onboarding pages
→ Required Survey intake
   - 4 artist screens
   - 2 album screens
   - 4 song screens
→ "Generating your Atlas and first missions" status
→ Core app IA appears
→ First generated mission batch
→ Listen / react / review
→ Evidence sync or Share Evidence fallback
```

Returning use should skip completed first-run gates. If authentication has timed out, the app should reauthenticate through Apple and then return the user to the appropriate core state.

## Brand/UX Evaluation Criteria

Use these criteria in every screen review.

| Criterion | Review question | Pass condition |
| --- | --- | --- |
| Product truth | Does the screen say only what the app can prove or do now? | No fake learning, no implied automation if assignment/review is manual, no prebuilt mission as user content. |
| Evidence, not verdicts | Does the copy preserve uncertainty and scope? | Survey, reactions, Apple Music exposure, and mission hypotheses are framed as evidence or tests, not durable Atlas truth. |
| Music-first | Does the screen lead the user back to listening? | The model, schema, resolver, and export machinery stay secondary or hidden. |
| Night Vision fit | Does the surface feel like one dark-native listening instrument? | Black field, quiet panels, restrained semantic color, route/signal grammar; no generic dashboard feel. |
| Human language | Can a trusted tester understand the job without support in the room? | Internal terms are rewritten or moved behind support/debug affordances. |
| Alpha honesty | Are support workflows clearly support workflows? | Paste/import JSON and raw export flows are labeled as Alpha/support paths, not final consumer UX. |
| TestFlight readiness | Can a tester complete the intended loop on a physical iPhone? | Clear first launch, disclosures, Apple sign-in, Apple Music connection, onboarding, Survey, generation status, mission playback, reaction, review, evidence sync/share, reset/recovery. |
| Privacy and retention clarity | Does the user know what is local, shared, uploaded, and deletable? | Consent/support copy exists before any evidence leaves the device. |
| Accessibility basics | Can the screen survive small phones, Dynamic Type, contrast, VoiceOver, and landscape policy? | Buttons have clear labels, touch targets hold, text does not truncate critical meaning, orientation behavior is intentional. |

## Screen Classification

### TestFlight-ready With Light Polish

These screens can remain in the Alpha 1 path if copy, navigation, and QA issues are addressed.

- Player: Now Testing core playback/reaction surface
- Player: Artwork Flip Card
- Player: Notes Panel, if the mic icon is corrected or audio notes are added
- Mission Review: Summary and Route Items
- Mission Review: Item Editor
- Reset Confirmation, after plain-language deletion copy

### Needs Copy/Brand Pass

These are structurally useful but currently expose internal terms, diagnostic labels, or mixed visual systems.

- App Shell / Tab Bar
- Mission Home
- Apple Music Authorization Panel
- Mission Detail
- Player Empty State
- Mission Review Empty State
- Export Files and Share, if kept visible as an Alpha evidence return path
- Survey Welcome/Connect/Grid/Readout, now that Survey is included in Alpha 1

### Needs UX Restructuring

These screens represent the right capability but not the right normal tester flow.

- Mission Import Sheet: Reviewed Mission
- Mission Import Sheet: Generated Response
- Export: Readiness and Current Mission
- Export: Generate Dev Stub / Acceptance Export actions
- Empty Player/Review dead ends with no direct route back to Mission
- Survey advanced/nuance interactions, because long-press and freeform evidence need clearer affordances and consent if included in the forced intake
- First-run app shell, because the current repo opens into tabs rather than privacy/account/onboarding/Survey orchestration

### Should Be Hidden Or Support-only For Alpha 1

These should not be in the normal external tester path unless Product/Support explicitly chooses a support build.

- Resolve Diagnostics
- Export Debug Panels
- Apple Music Signal Probe
- Raw JSON/Markdown preview
- Paste/import JSON flows, unless they are explicitly documented as an Alpha support path
- Any repeat Survey tab in the normal core IA after first intake

## Screen-by-Screen Review Checklist

Mapped to `docs/app_dev/user_facing_screen_spec_v0_1.md`.

| # | Screen | Current posture | Review checklist | Classification |
| --- | --- | --- | --- | --- |
| 1 | App Shell / Tab Bar | Current Release tabs: Mission, Player, Review, Export. Debug adds Survey/Resolve. | First-time users should not land directly in this shell. Review the post-onboarding IA only after privacy/account/onboarding/Survey/generation gates are complete. Confirm `Player` hiding tab chrome does not strand the user. Confirm tab names match Waymark. | Needs copy/brand pass |
| 2 | Mission Home | Current Release first tab. | In Alpha 1 this should represent generated mission status after Survey, not a paste/import hub. If missions are still generating, show the Atlas/mission generation status. Hide or soften JSON language for normal testers. | Needs copy/brand pass |
| 3 | Mission Import: Reviewed Mission | Current Release. | Treat as support fallback only. Normal Alpha 1 missions should be generated after Survey completion, not pasted by the user. | Should be support-only |
| 4 | Mission Import: Generated Response | Release. | Treat as infrastructure/support flow. The words Supabase, status flags, and `app_missions` are not normal tester language. | Should be support-only |
| 5 | Reset Confirmation | Release. | Say exactly what is deleted locally, what is not deleted, and whether already shared evidence remains with the team. | Ready with light polish |
| 6 | Apple Music Authorization Panel | Release where embedded. | Replace diagnostic labels with tester language: access needed, ready/not ready, subscription/catalog requirements, retry/check. Keep storefront/cloud library details expandable or support-only. | Needs copy/brand pass |
| 7 | Mission Detail | Release. | Hypothesis should be the hero. Rename internal terms such as Success Bar and Inflation Warning. Route items should explain the job of each item before playback without feeling like a schema view. | Needs copy/brand pass |
| 8 | Player Empty State | Release. | Add or require a direct path back to Mission. Empty Player should not feel broken. | Needs UX restructuring |
| 9 | Player: Now Testing | Release. | Preserve calm fieldwork feel. Validate reaction labels against brand: likely `Love`, `Like`, `Keep`, `Not For Me` rather than `Ok`/`Dislike` if Product agrees. Confirm `Resolve Issue` is appropriate when diagnostics are hidden. | Ready with light polish |
| 10 | Artwork Flip Card | Release. | Keep artwork music-first. Finalize fallback art style against Night Vision tokens. Make flip affordance understandable and not decorative-only. | Ready with light polish |
| 11 | Notes Panel | Release. | Mic icon currently opens text notes. Either change icon/copy in a future pass or add voice notes. Explain whether notes are shared in exports. | Ready with light polish |
| 12 | Review Empty State | Release. | Add direct path back to Mission or make the state impossible from the normal flow. | Needs UX restructuring |
| 13 | Mission Review Summary/Route Items | Release. | Keep evidence completeness, but translate clinical labels. Avoid confidence math. Use human labels like needs review, ready to share, missing reaction. | Ready with light polish |
| 14 | Mission Review Item Editor | Release. | Signal labels must match Player labels. `Keep As No Signal` needs clearer language. Review edits should feel like correction, not data entry. | Ready with light polish |
| 15 | Export Readiness/Current Mission | Release. | Current copy exposes contract, schema, dev path, acceptance path. For external testers, restructure as Share Evidence or move behind support. Engineering should decide whether evidence is automatically/scheduled to Supabase instead. | Needs UX restructuring |
| 16 | Export Files/Share | Release after preview/save. | If visible, say what files include, where they are saved, who receives them, and whether sharing is optional. Avoid Atlas candidate count unless reviewer/support-facing. If backend sync is implemented, Share Evidence becomes a fallback/support action. | Needs copy/brand pass |
| 17 | Export Debug Panels | Debug-only. | Keep out of normal TestFlight. Only expose through support build when requested. | Should be hidden/support-only |
| 18 | Resolve Diagnostics | Debug-only. | Keep hidden. Review Player's `Resolve Issue` fallback when diagnostics are unavailable. | Should be hidden/support-only |
| 19 | Survey Welcome | Debug-only currently; target Alpha 1 required. | Rewrite any claim that the grid is Apple Music-seeded unless live seeding is true. Add evidence boundary before collection. This should come after privacy/terms/account/onboarding. | Needs copy/brand pass |
| 20 | Survey Apple Music Connect | Debug-only currently; target Alpha 1 account/access should happen before Survey. | Avoid duplicating the first-run Apple Music connection unless needed for recovery. If retained, make it a status/repair surface. | Needs UX restructuring |
| 21 | Survey Grid Pages | Debug-only currently; target Alpha 1 required. | Force 4 artist, 2 album, and 4 song screens. State rings must be consistent and accessible. Unknown must mean no evidence, not dislike. Long-press nuance needs a visible affordance or alternate detail action. | Needs copy/brand pass |
| 22 | Survey Optional Third Artist Prompt | Debug-only currently; target flow forces four artist screens. | Remove optionality from Alpha 1 forced intake or rewrite as progress copy. Rationale must avoid overstating certainty from early signal. | Needs UX restructuring |
| 23 | Survey Go Deeper Prompt | Debug-only currently. | For Alpha 1, this likely becomes completion/progress copy rather than a choice to skip depth. Must provide a clear path into generation status. | Needs UX restructuring |
| 24 | Advanced Survey | Debug-only currently. | Freeform notes need privacy/share language. Filters need final labels. Decide whether advanced is included in forced intake or moved to My Account/support after Alpha onboarding. | Needs UX restructuring |
| 25 | Survey Nuance Sheet | Debug-only currently. | Long-press discovery, segmented label fit, and nuanced states need small-phone QA. If nuance is important, provide an explicit detail affordance. | Needs UX restructuring |
| 26 | Survey Readout | Debug-only currently. | Keep provisional. `Likely dead ends` may overclaim from Survey evidence; prefer scoped/caution language. Must lead directly into Atlas/mission generation status. | Needs copy/brand pass |

## Highest-risk User-facing Moments

1. First launch currently lacks the target privacy/account/onboarding/Survey orchestration. This is now the main IA gap before Alpha 1.
2. Sign in with Apple and Apple Music connection need to feel like one guided step while staying honest about separate OS permissions and session expiration.
3. Survey is now required and longer than the current debug flow. Copy, progress, fatigue, recovery, and persistence matter.
4. The post-Survey wait state must feel trustworthy. "Generating your Atlas and first missions" should not imply final Atlas truth or fully autonomous promotion.
5. No prebuilt missions may ship as user content. First mission batch should be generated after Survey completion.
6. Paste/import flows are acceptable only as support fallback, not the normal user path.
7. Apple Music authorization exposes diagnostic status. Testers need plain readiness language and a clear path when access, subscription, storefront, or catalog playback fails.
8. The Player is the brand center of gravity. It must reliably play, capture reactions, and recover from unresolved items on a physical iPhone.
9. Evidence handling must be clear. If evidence syncs to Supabase automatically or on a schedule, disclosures must say so; if Share Evidence remains manual, the app must say what is shared.
10. Export currently exposes schemas, dev/acceptance terms, paths, and Atlas candidate counts. This is high-risk for external trusted testers unless reframed as Share Evidence or support-only.
11. The app name conflict will be visible before any screen review: TestFlight/install name says `Music Atlas`, while the decided app name is `Waymark`.
12. Portrait-only and dark-mode-only Alpha choices need to be reflected in metadata, QA, and design review.

## Executive Decisions And Remaining Open Items

### Product Decisions

| Decision | Status | Notes |
| --- | --- | --- |
| App name | Decided: Waymark | Update installed name, TestFlight/App Store Connect metadata, privacy copy, and any old Music Atlas references intended for users. |
| Survey in first TestFlight | Decided: included | Required after onboarding; not a normal top-level repeat workflow after intake. |
| Required Survey length | Decided for Alpha 1 | Four artist screens, two album screens, four song screens. |
| Mission assignment path | Decided product posture | No prebuilt missions. Generate one first mission batch after Survey completion. Paste/import only as support fallback. |
| Export vs Share Evidence | Partially decided | `Share Evidence` language is acceptable. Engineering must decide whether evidence is local-only/manual share or synced to Supabase automatically/on schedule. |
| Privacy/retention/deletion | Direction agreed, copy pending | Required before evidence collection/sharing/sync. Include Apple Music access, Sign in with Apple, local storage, Supabase artifacts, retention, deletion, and support. |
| App icon and launch visual | Required, candidates pending | Founder will review candidates. Current repo has no `.xcassets` app icon and empty launch screen. |
| Visual system scope for Alpha 1 | Decided: dark mode only | Apply Night Vision direction across Alpha release path. A "token pass" means mapping brand decisions into reusable UI constants such as colors, text styles, surfaces, radii, spacing, and semantic state colors. |
| Orientation policy | Decided: portrait only | Current Info.plist supports landscape; Alpha target should restrict to portrait unless this changes. |
| Returning-user FAQ | Decided: include after onboarding | FAQ should live outside required first-run pages, likely under My Account/help. |

### Implementation Tasks That Follow Decisions

These are not decisions; they are execution work once the executive choices are made.

- Rename/rewrite internal labels: Success Bar, Inflation Warning, Export Contract, Dev Stub, Acceptance Export, app-import candidate, Supabase response.
- Add first-run gate for privacy/terms/Alpha disclosures.
- Add guided Sign in with Apple + Apple Music connection flow with persistent session handling and timeout reauthentication.
- Add required swipeable onboarding pages and returning-user FAQ location.
- Promote Survey into the Alpha 1 first-run path and update it to the forced 4 artist / 2 album / 4 song intake.
- Add post-Survey generation status/timer before the core app IA appears.
- Generate/import the first mission batch after Survey completion; keep paste/import as support fallback only.
- Add tester-facing empty-state routes from Player/Review back to Mission.
- Reframe Apple Music status as ready/not ready with diagnostic details hidden or collapsed.
- Align release path to Night Vision visual tokens in dark mode.
- Add final or temporary app icon and launch treatment.
- Add privacy, consent, retention, deletion, and support copy to TestFlight materials and relevant app surfaces.
- Decide with engineering whether evidence syncs to Supabase automatically/on schedule or remains manual Share Evidence for Alpha 1.
- Restrict supported orientation to portrait for Alpha.
- Run the Release packaging command to confirm no sample/personal mission JSON ships.
- Capture screenshots for every screen state in the screen spec after decisions are applied.

## 60-minute Executive/Brand Review Agenda

| Time | Topic | Output |
| --- | --- | --- |
| 0-5 min | Confirm locked Alpha posture | Waymark name, Survey included, no prebuilt missions, dark-only, portrait-only. |
| 5-13 min | First-run gate | Review privacy/terms, Sign in with Apple, Apple Music connection, persistence/reauth posture. |
| 13-23 min | Onboarding pages | Review swipeable copy, required completion, and returning-user FAQ placement. |
| 23-35 min | Survey intake | Review forced 4 artist / 2 album / 4 song flow, fatigue, progress, provisional language, and recovery. |
| 35-43 min | Generation handoff | Review "generating Atlas and first missions" status, wait language, and no-overclaim guardrails. |
| 43-50 min | Core loop walkthrough | Review Mission, Player, Review, and first batch handoff. |
| 50-55 min | Evidence return and trust | Decide automatic/scheduled Supabase sync vs manual Share Evidence fallback and required disclosure copy. |
| 55-60 min | Brand/release blockers | Confirm icon/launch candidates, Night Vision dark pass, portrait policy, and TestFlight metadata owners. |

## Review Output Template

Use this format during the review so decisions do not blur into implementation notes.

| Screen | Decision needed? | Product decision | Implementation follow-up | Alpha 1 posture |
| --- | --- | --- | --- | --- |
| First-run gate | yes/no |  |  | ready / polish / restructure / support-only / hidden |
| Onboarding | yes/no |  |  | ready / polish / restructure / support-only / hidden |
| Survey intake | yes/no |  |  | ready / polish / restructure / support-only / hidden |
| Generation status | yes/no |  |  | ready / polish / restructure / support-only / hidden |
| Mission Home | yes/no |  |  | ready / polish / restructure / support-only / hidden |
| Player | yes/no |  |  | ready / polish / restructure / support-only / hidden |
| Review | yes/no |  |  | ready / polish / restructure / support-only / hidden |
| Share Evidence / sync | yes/no |  |  | ready / polish / restructure / support-only / hidden |

## Bottom Line

For Alpha 1, Waymark should feel like a guided listening instrument that collects evidence carefully, not like a recommender dashboard or an internal data tool. The target path is now clear: first-run disclosures, Apple sign-in and Apple Music connection, required onboarding, required Survey intake, generated first Atlas/mission batch, then the core listening loop. The remaining review work is to make that path honest, dark-native, portrait-first, and calm enough that testers understand what Waymark is learning without believing it knows more than the evidence supports.
