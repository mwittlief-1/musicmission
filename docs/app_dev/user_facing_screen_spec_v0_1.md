# Cartenza User-Facing Screen Spec v0.1

Purpose: provide a complete editable inventory of current user-facing screens so Brand, UI, UX, Core, and Product can polish the TestFlight Alpha deliberately.

Source of truth audited: `MusicAtlasController/Views/*.swift` on 2026-05-22.

Product decision addendum: `docs/app_dev/alpha_product_decision_addendum_2026_05_22.md` now supersedes the open first-TestFlight questions below. The current code still reflects the audited state, but the Alpha 1 target flow is now a guided first-run funnel.

Approved wireframe reference: Product/Founder approved `docs/app_dev/mockups/alpha_orientation_flow_v0_1/index.html` for Alpha 1 Swift implementation on 2026-05-22. Use `docs/app_dev/mockups/alpha_orientation_flow_v0_1/IMPLEMENTATION_HANDOFF.md` as the Core/UI bridge from mockup to app code.

## Alpha 1 Target Flow

| Step | Screen/surface | Alpha posture |
| --- | --- | --- |
| 1 | Privacy + terms acknowledgement | Required first launch before data collection or account connection. |
| 2 | Sign in with Apple + Apple Music connection | Required, presented as one guided step even though Apple ID auth and MusicKit authorization are separate capabilities. |
| 3 | Guided onboarding walkthrough | Required first time; swipable copy pages using founder-provided copy. |
| 4 | Survey intake | Required after onboarding; fixed 4 artist screens, 2 album screens, 4 song screens. |
| 5 | Generation status | Show that Cartenza is building the user's Atlas and first missions. Preserve provisional language. |
| 6 | Core app IA | Appears after Survey completion and first mission generation/assignment. |
| 7 | My Account / FAQ | Returning-user FAQ, account/auth status, reset/recovery, and optional Survey revisit/support entry. |

## Release Shell Summary

Current `RootView` tabs:

| Tab | Current release visibility | Purpose | Design status |
| --- | --- | --- | --- |
| Survey | Debug only | Seed taste/profile evidence before first mission. | Built, but Product must decide first-TestFlight visibility. |
| Mission | Release | Missionless home, mission assignment/import, Apple Music status, mission detail entry. | Functional, needs tester-facing polish. |
| Resolve | Debug only | Resolver diagnostics and manual status tools. | Keep out of normal TestFlight path. |
| Player | Release | Full-screen mission playback, reactions, notes. | Most visually intentional surface; needs brand alignment and QA. |
| Review | Release | Mission evidence summary and item-level reaction editing. | Functional, needs language and visual hierarchy pass. |
| Export | Release | Export readiness, file generation, sharing. | Functional but currently engineer-facing. Needs Alpha support copy or support-only gating. |

Release initial tab is `Mission`; debug initial tab is `Survey`.

## Global UX Decisions

| Decision | Status | Owner | Notes |
| --- | --- | --- | --- |
| App name | decided | Founder/Design | Use `Cartenza`. Installed display name and TestFlight metadata should be aligned. |
| First-TestFlight Survey visibility | decided | Product/Core | Survey is included and required after onboarding for Alpha 1. |
| Survey length | decided | Product/Survey/Core | Force 4 artist screens, 2 album screens, and 4 song screens for Alpha intake. |
| Mission assignment UX | decided direction | Product/Core/Infra | No bundled missions. First mission batch is generated after Survey completion. Paste/import remains support/fallback only. |
| Export UX | decided direction | Product/Design/Infra | Use `Share Evidence` language. Product prefers automatic/scheduled Supabase upload if disclosures and engineering allow; keep manual share fallback. |
| Evidence/privacy copy | required | Product/Release | Privacy/terms acceptance is required before account connection, Survey, or upload. |
| Orientation support | decided | Design/Core | Restrict Alpha to portrait. |
| Visual system | decided | Design/Core | Dark mode only for Alpha. |
| Accessibility | open | Core/Design | Run Dynamic Type, VoiceOver labels, contrast, and touch target pass before external testers. |

## Screen Inventory

### 1. App Shell / Tab Bar

| Field | Spec |
| --- | --- |
| Route | `RootView` |
| Visibility | Release: Mission, Player, Review, Export. Debug: Survey and Resolve also visible. |
| User intent | Move between assignment, playback, evidence review, and export. |
| Key components | SwiftUI `TabView`; SF Symbols labels. |
| Primary actions | Select tab. Player internally hides the tab bar. |
| States | Release/debug feature flags; initial tab differs by build. |
| Design questions | Should Alpha expose four tabs, or collapse Mission/Review/Export behind a guided mission flow? Should Player hide tab chrome permanently or offer an obvious way back? |

### 2. Mission Home

| Field | Spec |
| --- | --- |
| Route | `MissionListView`, title `Cartenza` |
| Visibility | Release |
| User intent | See active mission or understand that no mission is assigned yet. |
| Key components | Loading/error states, Active section, Reviewed Mission Assignments, Import, Recovery, Apple Music, Status. |
| Primary actions | Open mission detail; import reviewed mission JSON; import generated batch response; reset reviewed missions/sessions; request/check Apple Music access. |
| Empty state | "No reviewed mission assigned"; explains production starts missionless. |
| Data dependencies | `AppModel.missionLoadState`, reviewed assignments, active mission, Music authorization. |
| Design questions | Paste-import is not a consumer-grade action. For Alpha, should this screen say "Waiting for your mission" and hide import behind support instructions? |

### 3. Mission Import Sheet: Reviewed Mission

| Field | Spec |
| --- | --- |
| Route | `MissionListView.importSheetView(.manualReviewed)` |
| Visibility | Release |
| User intent | Paste a product-reviewed `mission.v0.2` JSON object or array. |
| Key components | Instruction copy, monospaced `TextEditor`, Cancel, Import. |
| Primary actions | Import, cancel. |
| Validation/errors | Import button disabled on empty draft; app rejects non-app-ready missions via model layer and posts status message. |
| Design questions | Should support paste mission JSON for testers, or should Supabase assignment replace this before external Alpha? |

### 4. Mission Import Sheet: Generated Response

| Field | Spec |
| --- | --- |
| Route | `MissionListView.importSheetView(.supabaseResponse)` |
| Visibility | Release |
| User intent | Paste a Supabase `generate-first-mission-batch` response and import only app candidates. |
| Key components | Instruction copy, monospaced `TextEditor`, Cancel, Import. |
| Primary actions | Import, cancel. |
| Validation/errors | Only `status=app_import_candidate` responses with valid `app_missions` should import. |
| Design questions | This is infrastructure-facing. Consider hiding behind debug/support mode when live assignment exists. |

### 5. Reset Confirmation

| Field | Spec |
| --- | --- |
| Route | `MissionListView.confirmationDialog` |
| Visibility | Release |
| User intent | Clear imported/reviewed missions and local session state. |
| Key components | Destructive Reset, Cancel, explanation text. |
| Primary actions | Reset reviewed missions and sessions. |
| Design questions | Needs clearer tester wording: what gets deleted locally, what remains, and whether shared evidence is affected. |

### 6. Apple Music Authorization Panel

| Field | Spec |
| --- | --- |
| Route | `MusicAuthorizationPanel`, embedded in Mission and Survey Connect. |
| Visibility | Release where embedded; Survey copy debug-only unless Survey ships. |
| User intent | Grant Apple Music access and verify playback environment. |
| Key components | Authorization status/detail, Request Access, MusicKit check, storefront, can play catalog, cloud library, Check MusicKit Status. |
| Primary actions | Request authorization; refresh MusicKit environment. |
| States | Can request, authorized, denied/restricted, environment unknown/ready. |
| Design questions | Current labels are diagnostic. For testers, translate to "Apple Music Ready" / "Needs Apple Music Access" with details expandable. |

### 7. Mission Detail

| Field | Spec |
| --- | --- |
| Route | `MissionDetailView` |
| Visibility | Release |
| User intent | Understand the mission, start it, choose a track. |
| Key components | Start/Active button, Hypothesis, inflation warning, Success Bar, Items list with resolution badge. |
| Primary actions | Start mission; select item. |
| States | Active mission, selected item, item resolution statuses. |
| Design questions | "Success Bar" and "Inflation Warning" are internal terms. Rename for testers or keep behind details. |

### 8. Player: Empty State

| Field | Spec |
| --- | --- |
| Route | `NowTestingView` with no mission/item. |
| Visibility | Release |
| User intent | Understand why playback is unavailable. |
| Key components | `ContentUnavailableView`: "No Item Selected"; description "Choose a mission item before playback." |
| Primary actions | None in surface; user must return to Mission. |
| Design questions | Add direct route to Mission tab or make empty Player impossible before mission selection. |

### 9. Player: Now Testing

| Field | Spec |
| --- | --- |
| Route | `NowTestingView` with active mission and selected item. |
| Visibility | Release |
| User intent | Play a mission track, capture reaction, add optional context. |
| Key components | Mission rail banner, playback notice banner, artwork flip card, track metadata, playback meter, transport controls, reaction tiles, context chip rail, bottom action bar. |
| Primary actions | Open mission review; switch to Live MusicKit from Stub mode; previous/play-pause-next; scrub; select reaction; select context chip; add note; open resolve issue. |
| States | Stub/live mode, playback blocking message, playing/paused/played/skipped, resolved/unresolved, reaction selected/unselected, context chip selected/unselected. |
| Data dependencies | Active mission, selected item, Apple Music resolution, playback snapshot, reaction record. |
| Design questions | This is the visual center of the Alpha. Brand should define color/tone, reaction labels, empty chip copy, and whether "Resolve Issue" should be visible to external testers. |

### 10. Player: Artwork Flip Card

| Field | Spec |
| --- | --- |
| Route | `ArtworkFlipCard` inside Player. |
| Visibility | Release |
| User intent | See artwork; optionally flip to mission hypothesis context. |
| Key components | Resolved artwork or gradient fallback, sequence number, flip icon, hypothesis/detail back side. |
| Primary actions | Tap to flip when flip-side exists. |
| States | Artwork loaded/loading/fallback; front/back. |
| Design questions | Need final fallback artwork style and an affordance that does not feel decorative-only. |

### 11. Player: Notes Panel

| Field | Spec |
| --- | --- |
| Route | `NotesPanel`, opened from bottom mic button. |
| Visibility | Release |
| User intent | Attach a text note to the selected reaction. |
| Key components | Text field, Attach Note. |
| Primary actions | Enter note; attach note. |
| States | Keyboard visible, existing note hydrated. |
| Design questions | The mic icon currently opens text notes, not voice recording. Rename/icon should match behavior unless audio notes are added. |

### 12. Mission Review: Empty State

| Field | Spec |
| --- | --- |
| Route | `MissionReviewView` with no mission. |
| Visibility | Release |
| User intent | Understand why review is unavailable. |
| Key components | `ContentUnavailableView`: "No mission loaded"; description "Load a mission before reviewing evidence." |
| Primary actions | None. |
| Design questions | Add route back to Mission or guided next step. |

### 13. Mission Review: Summary And Route Items

| Field | Spec |
| --- | --- |
| Route | `MissionReviewView` with mission. |
| Visibility | Release |
| User intent | See evidence completeness and open item-level review. |
| Key components | Evidence Summary, readiness pill, counts for resolved/playback/completed/skipped/reactions/exportable/review needed, Route Items list. |
| Primary actions | Open item editor. |
| States | Review needed, exportable candidate, playback and reaction pills, flags. |
| Design questions | Counts are useful but clinical. Decide Alpha-friendly labels for "Exportable Items" and "Review Needed." |

### 14. Mission Review: Item Editor

| Field | Spec |
| --- | --- |
| Route | `MissionReviewItemEditorView` |
| Visibility | Release |
| User intent | Correct or enrich a captured reaction after playback. |
| Key components | Evidence details, Primary Signal grid, Keep As No Signal, Context Tags, Notes, Save Review Edits, Set As Player Item. |
| Primary actions | Choose primary signal; choose tags; add note; save; return item to Player. |
| States | No selected signal, selected signal with/without tags, missing item evidence. |
| Design questions | Signal labels need final brand/product language. "Keep As No Signal" may need clearer copy. |

### 15. Export: Readiness And Current Mission

| Field | Spec |
| --- | --- |
| Route | `ExportPreviewView` |
| Visibility | Release |
| User intent | Check whether enough evidence exists and generate shareable files. |
| Key components | Export Contract, Mission Export Readiness, Current Mission, Generate Dev Stub Mission Export, Generate Acceptance Mission Export, Last Action. |
| Primary actions | Generate dev export; generate acceptance export. |
| States | No mission, mission present, insufficient readiness, export preview created. |
| Design questions | Current screen exposes schema names, dev paths, and acceptance terms. For external testers, replace with "Share Alpha Evidence" and move contract details to debug/support. |

### 16. Export: Files And Share

| Field | Spec |
| --- | --- |
| Route | `ExportPreviewView` after preview/save. |
| Visibility | Release |
| User intent | Save JSON/Markdown evidence and share it back to the team. |
| Key components | Files section, Atlas candidate count, Save Export Files, Saved Export folder/filenames, ShareLink. |
| Primary actions | Save files; share saved files using iOS share sheet. |
| States | Preview available, saved export available, share sheet launched. |
| Design questions | Need plain-language confirmation of what is being shared and where local files live. |

### 17. Export Debug Panels

| Field | Spec |
| --- | --- |
| Route | `AppleMusicSignalProbePanel`, JSON Preview, Markdown Preview inside Export. |
| Visibility | Debug only via `AppFeatureFlags.showExportDebugPanels`. |
| User intent | Support diagnostics: inspect Apple Music signal payload and raw export. |
| Key components | Request Apple Music Access, Run Read-Only Signal Probe, Save/Share Signal Payload JSON, raw JSON/Markdown text. |
| Primary actions | Run probe, save probe, share probe, inspect raw preview. |
| Design questions | Keep out of normal TestFlight path unless support build explicitly enables it. |

### 18. Resolve Diagnostics

| Field | Spec |
| --- | --- |
| Route | `ResolverStatusView` |
| Visibility | Debug only |
| User intent | Inspect and override catalog resolution status. |
| Key components | Service Mode picker, Resolve Whole Mission, Catalog Resolution list, Selected Item detail, resolve/skip/unavailable/reset actions. |
| Primary actions | Switch service mode; resolve mission/item; mark skipped/unavailable; reset unresolved. |
| Design questions | Do not expose to external testers. If release Player has "Resolve Issue", it currently routes to Review when diagnostics are hidden. Confirm that behavior is understandable. |

## Survey Screens

Survey is currently debug-only in the audited code, but Product has decided Survey is included in Alpha 1 as required first-run intake. The current debug-only implementation is no longer the target release behavior.

### 19. Survey Welcome

| Field | Spec |
| --- | --- |
| Route | `SurveyView`, `.welcome` |
| Visibility | Debug only currently |
| User intent | Understand the quick taste pass before starting. |
| Key components | Icon, title "Tune the starting map", explanatory copy, three rows, Start Survey. |
| Primary actions | Start Survey. |
| Design questions | Copy says Apple Music-seeded, but current build uses seeded fixtures for the grid. Must not overclaim in TestFlight. |

### 20. Survey Apple Music Connect

| Field | Spec |
| --- | --- |
| Route | `SurveyView`, `.connectAppleMusic` |
| Visibility | Debug only currently |
| User intent | Grant Apple Music and continue. |
| Key components | Connect Apple Music title/copy, embedded MusicAuthorizationPanel, Continue to Artist Grid. |
| Primary actions | Request/check Apple Music; continue. |
| Design questions | Current copy explicitly says seeded fixtures; rewrite if live Apple Music seed exists. |

### 21. Survey Grid Pages

| Field | Spec |
| --- | --- |
| Route | `SurveyView`, `.artistPage1`, `.artistPage2`, `.artistPage3`, `.albumPage1`, `.songPage1` |
| Visibility | Debug only currently |
| User intent | Tap music objects through five states; long-press for nuance. |
| Key components | Header, 3-column grid, artwork/gradient tiles, state icons, nuance/note markers, bottom Back/Next. |
| Primary actions | Tap to cycle response; long-press to nuance sheet; navigate back/forward. |
| States | Don't Know, Fine, Like, Favorite, Not For Me; artwork loading/fallback. |
| Design questions | Need discoverable long-press or alternate detail button; five-state language and color must be brand/accessibility reviewed. |

### 22. Survey Optional Third Artist Prompt

| Field | Spec |
| --- | --- |
| Route | `SurveyView`, `.artistPage3Prompt` |
| Visibility | Debug only currently |
| User intent | Decide whether to sharpen artist signal or move to albums. |
| Key components | Conditional icon/color, "One more artist pass?", explanatory copy, Do One More Artist Page, Continue to Albums. |
| Primary actions | Open third artist page; continue. |
| Design questions | Ensure rationale does not imply certainty from weak signal. |

### 23. Survey Go Deeper Prompt

| Field | Spec |
| --- | --- |
| Route | `SurveyView`, `.deeperPrompt` |
| Visibility | Debug only currently |
| User intent | Choose readout now or advanced tuning. |
| Key components | Map icon, title, explanatory copy, signal count pill, Show What We Think So Far, Go Deeper. |
| Primary actions | Go to readout; open advanced survey. |
| Design questions | This is a good place for consent/trust copy if Survey ships. |

### 24. Advanced Survey

| Field | Spec |
| --- | --- |
| Route | `SurveyView`, `.advancedSurvey` |
| Visibility | Debug only currently |
| User intent | Add lens-specific signals and freeform notes. |
| Key components | Filter chips, advanced grid, "Anything Cartenza should know?" TextEditor, Add Note, bottom Readout. |
| Primary actions | Select filter; tap/long-press grid items; add note; advance. |
| States | Selected filter, note draft, freeform saved/empty. |
| Design questions | Need final list and language for filters; freeform note privacy must be explicit if uploaded/shared. |

### 25. Survey Nuance Sheet

| Field | Spec |
| --- | --- |
| Route | `SurveyNuanceSheet`, opened by long-press. |
| Visibility | Debug only currently |
| User intent | Add specific nuance and note to a survey item. |
| Key components | Item title/subtitle, segmented signal picker, nuance options, note editor, Done. |
| Primary actions | Change signal; toggle nuances; save note on Done. |
| Design questions | Long-press hidden interaction needs visible affordance; segmented labels must fit on small phones. |

### 26. Survey Readout

| Field | Spec |
| --- | --- |
| Route | `SurveyView`, `.readout` |
| Visibility | Debug only currently |
| User intent | See initial evidence summary before mission generation. |
| Key components | "What We Think So Far", evidence caveat, stat cards, Strongest territory, Useful waypoints, Likely dead ends, user-asserted notes, Add Advanced Signals. |
| Primary actions | Return to advanced signals. |
| Design questions | Readout must remain provisional. If shown before mission generation, define the call to action into first mission. |

## Brand/UI Polish Backlog

| Task | Owner | Dependency | Notes |
| --- | --- | --- | --- |
| Decide Alpha app name and in-app naming | Founder/Design | none | Cartenza supersedes `Music Atlas` and `Waymark` for user-facing naming. |
| Define visual tokens | Design/Core | none | Colors, typography scale, radii, icon treatment, list surface style. |
| Build app icon asset catalog | Design/Core | brand direction | No `.xcassets` discovered in repo. |
| Simplify Mission empty/import copy | Product/Design/Core | mission assignment decision | Hide JSON language from normal tester path if possible. |
| Rewrite Apple Music status panel | Product/Design/Core | none | Diagnostic details can remain expandable. |
| Rename internal terms | Product/Design | none | Success Bar, Inflation Warning, Export Contract, Dev Stub, Acceptance Export. |
| Decide Export tab visibility | Product/Core | evidence return path | Maybe release-facing "Share Evidence" instead of raw export tooling. |
| Add direct navigation from empty Player/Review to Mission | Core/Design | none | Avoid dead-end tabs. |
| Align dark and list surfaces | Design/Core | visual tokens | Mission/Review/Export currently feel like system tools next to immersive Player/Survey. |
| Accessibility pass | Core/Design | UI polish | Dynamic Type, contrast, VoiceOver labels, reduced motion, landscape behavior. |
| Screenshot packet for design review | Core/Design | app build runnable | Capture every screen/state listed here. |

## Suggested First Design Review Order

1. Missionless first launch and Apple Music access.
2. Mission detail and start flow.
3. Player/reaction loop.
4. Review and item edit loop.
5. Export/share evidence.
6. Survey only if Product chooses to include it in TestFlight Alpha 1.
