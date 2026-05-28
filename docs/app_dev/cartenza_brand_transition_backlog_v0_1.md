# Cartenza Brand Transition Backlog v0.1

Date: 2026-05-23

Status: active transition plan. Assets have been saved for reference, and the first Cartenza naming slice has updated repo policy, app display strings, visible app copy, and legacy-named harness product wording. App icon wiring and deeper visual-token work are still pending.

## Asset Package

Source package:

- `/Users/matt_wittlief_home/Downloads/cartenza_codex_packet_v0_1.zip`

Repo reference location:

- `docs/app_dev/brand_assets/cartenza_codex_packet_v0_1/cartenza_codex_packet/`

Important package caveat:

- The reference boards are directional, not production artwork.
- The included SVG files are starter approximations.
- The wordmark file is a placeholder, not final typography.
- Final public-release vector cleanup still belongs with design.

## Brand Decision

The app name is now `Cartenza`. This supersedes prior Alpha planning docs that selected `Waymark`.

Working brand interpretation: Cartenza should feel like a sophisticated system for mapping personal music taste. It should not feel like a generic music player, playlist generator, AI assistant, dashboard, or travel/map product.

Preferred promise:

```text
Your music. Mapped.
```

Preferred visual direction:

- Master mark: Candidate B, Cartographic Cut, from the Concept 5 circular cartographic monogram / compass-seal C refinement pass.
- Secondary motif: Concept 1, topographic contour / taste terrain.
- Visual mode: Night Vision.
- Mood: dark, restrained, premium, intelligent, modern, slightly sexy, musical without being literal, cartographic without travel-app cliches.

## Mapping To Current Alpha Work

The current Alpha flow and mockup work remain structurally useful. The brand pass should rename and retune it, not reopen the entire product IA.

| Current Alpha element | Cartenza mapping | Planning note |
| --- | --- | --- |
| App name `Waymark` | Replace with `Cartenza` on user-facing surfaces. | Keep migration/internal notes where historically useful. |
| `Music Atlas` legacy name | Retire from user-facing app display unless used only as a descriptor. | `Music Taste Atlas` can remain as a descriptor if Product approves. |
| Tagline/copy | Introduce `Your music. Mapped.` on welcome, launch-style, and brand moments. | Do not force tagline into dense tool/player states. |
| Night Vision visual system | Keep dark-native posture, but shift from bright cyan/blue route energy to obsidian, charcoal, silver, antique gold, and muted teal. | Current mockup is close in darkness but too electric in accent color. |
| Route/signal line motif | Retune toward compass, contour, and field-line language. | Topographic texture should be subtle and low-contrast. |
| Survey | Keep fixed Alpha intake flow. | Apple Music artwork will carry the tiles; use Cartenza tokens for state and chrome only. |
| Mission tab | Keep 10-mission Alpha batch concept. | Use gold for guide/waypoint/selected signal and teal for atlas/frontier/substrate. |
| Mission detail | Keep song-level route preview and cautious hypothesis copy. | Avoid turning the page into a decorated map. The route exists to set up listening. |
| Player | Keep layout and interaction model mostly intact. | Player should remain the least logo-heavy surface; album art and reactions are the point. |
| Mission review/edit | Keep song-data review, editable selection/tags/notes, update/save per song. | Use evidence language. Do not imply Cartenza knows more than the evidence supports. |
| Share Evidence | Language can still work under Cartenza. | Privacy/retention/sync policy remains an executive/engineering blocker. |
| App icon / launch | Use the locked Candidate B Cartographic Cut mark as the Alpha direction. | Runtime icon/SwiftUI replacement remains a separate implementation slice. |

## Planning Backlog

### CBR-001: Preserve Cartenza assets as references

Status: done.

Scope:

- Save the full packet under `docs/app_dev/brand_assets/`.
- Keep assets out of `MusicAtlasController/Resources/Assets.xcassets` for now.
- Do not wire PNG/SVG files into SwiftUI or launch assets yet.

Acceptance:

- Packet files are inspectable in repo docs.
- No app code references the new assets.

### CBR-002: Supersede Waymark name decisions in planning docs

Status: in progress.

Scope:

- Add a short Cartenza decision addendum or update relevant planning docs.
- Mark older `Waymark` naming decisions as superseded, not silently erased.
- Keep historical Waymark docs understandable for audit trail.

Acceptance:

- Product/release docs consistently state `Cartenza` as the new app name.
- Any remaining `Waymark` references are clearly historical or migration notes.

Progress:

- Added repo-wide naming policy in `docs/brand_migration_cartenza.md`.
- Updated `README.md`, `AGENTS.md`, and `docs/repo_map.md` to identify Cartenza as the current product name.
- Added the first name-reference audit in `docs/app_dev/cartenza_name_reference_audit_2026_05_27.md`.

### CBR-003: Name/reference audit

Status: in progress.

Scope:

- Audit app code, docs, mockups, TestFlight copy, bundle display strings, launch copy, account/help copy, privacy language, and screenshots.
- Classify references as user-facing, internal/historical, code-symbol, or file/repo legacy.
- Do not rename code modules such as `MusicAtlasController` until engineering decides whether the churn is worth it.

Acceptance:

- A list exists of every user-facing `Waymark` and `Music Atlas` reference that must change before TestFlight.
- Internal symbols that are safe to defer are explicitly documented.

Progress:

- The 2026-05-27 audit classifies app-visible strings, legacy technical identifiers, generated output defaults, and historical archive material.

### CBR-004: Cartenza token plan

Status: first SwiftUI pass in progress.

Scope:

- Translate `tokens/cartenza_night_vision_tokens.json` into implementation-ready SwiftUI theme constants later.
- Preserve dark-mode-only Alpha scope.
- Define semantic usage:
  - gold: signal, waypoint, guide, selected, important path.
  - teal: atlas substrate, frontier, system intelligence, map layer, uncertainty.
  - silver/warm silver: primary text, logo, high-value labels.

Acceptance:

- Token names and semantic meanings are agreed before UI wiring.
- Existing cyan/blue accents have a clear replacement map.

Progress:

- Added SwiftUI constants for the Night Vision palette in `RootView.swift`.
- Kept `WaymarkTheme` as the compatibility theme API while retuning its colors to Cartenza tokens.
- Pointed `SurveyStyle` at the shared Cartenza-tuned theme so Survey chrome follows the same palette.

### CBR-005: App icon and launch direction review

Status: Candidate B locked; runtime replacement pending.

Scope:

- Review Concept 5 app icon and mark at small sizes.
- Decide whether the starter SVG/PNG is acceptable as an Alpha placeholder or whether design must clean it first.
- Define launch-style surface: icon, Cartenza wordmark, `Your music. Mapped.`

Acceptance:

- Founder/design approval on Alpha icon placeholder direction.
- Clear decision on whether to use included starter assets or wait for refined vectors.

Progress:

- Resized `cartenza_app_icon_concept5.png` into the existing iOS `AppIcon.appiconset` slots as an Alpha placeholder.
- Did not add reference concept boards to runtime resources.
- Added `docs/app_dev/brand_assets/cartenza_logo_refinement_2026_05_27/` with three logo refinement candidates for owner review before any runtime replacement.
- Locked Candidate B, `Cartographic Cut`, as the Alpha logo direction and promoted it to selected aliases in the refinement packet.
- Replaced the iOS app icon set with a flattened no-alpha Candidate B render.

### CBR-006: Mockup rebrand pass

Status: copy pass complete; visual retune pending.

Scope:

- Rename the HTML mockup packet from Waymark-facing copy to Cartenza-facing copy. Completed on 2026-05-27.
- Retune CSS variables from current cyan/blue/bright signal palette to Cartenza tokens.
- Replace simple route-art motif with subtle contour/compass language.
- Keep the currently approved flow, spacing, Survey, Player, and Review interaction model.

Acceptance:

- 26-screen mockup still passes mobile spacing review at 390x844.
- No product flow is changed during the visual pass.

### CBR-007: SwiftUI brand layer implementation plan

Status: first low-churn implementation pass in progress.

Scope:

- Plan a centralized brand/theme layer for Cartenza colors, typography, radii, and semantic accents.
- Identify the minimum SwiftUI surfaces for Alpha:
  - first-run consent
  - Apple access
  - onboarding
  - Survey
  - generation status
  - Mission tab
  - Mission detail
  - Player
  - Mission review/edit
  - My Account/FAQ
- Keep behavior, schemas, Survey evidence, Mission generation, playback, and evidence export unchanged.

Acceptance:

- Engineering has a low-churn implementation path before any UI code edits begin.
- Brand is isolated in constants/assets where possible.

Progress:

- Introduced `CartenzaBrand`, `CartenzaBrandLockup`, `CartenzaCompassMark`, and a subtle topographic backdrop for first-run surfaces.
- Preserved existing `Waymark*` view/type names as internal compatibility names to avoid broad runtime churn.

### CBR-008: Copy migration pass

Status: in progress.

Scope:

- Replace user-facing `Waymark` references with `Cartenza`.
- Re-evaluate copy where the name changes the tone.
- Use the tagline sparingly.
- Keep uncertainty language:
  - evidence, not truth.
  - Survey is a starting point.
  - Atlas is provisional.
  - missions test what might be true.

Acceptance:

- No screen implies Cartenza knows more than the available evidence supports.
- No old name leaks in user-facing Alpha screens.

Progress:

- First-run welcome, account/FAQ, generation, Survey, mission, review, export, and support copy now prefer Cartenza where surfaced to testers.
- Legacy Waymark identifiers remain in schemas, filenames, app storage keys, and internal type names until a deliberate compatibility migration.

### CBR-009: Surface-specific visual backlog

Status: first app-shell pass in progress.

Scope by surface:

- Consent/access: use Cartenza name and privacy language, minimal icon/lockup.
- Onboarding: strongest brand moment; introduce Cartenza and `Your music. Mapped.`
- FAQ: rename, preserve explanatory tone, avoid brand over-decoration.
- Survey: keep dense/fitted mobile layout; use Apple artwork; use Cartenza state tokens.
- Generation: use topographic/atlas texture carefully to make waiting feel intentional.
- Mission batch: use compass/waypoint semantics; avoid dashboard card overload.
- Mission detail: use route preview and listen-for chips; keep hypothesis cautious.
- Player: preserve tested layout; minimal texture; dependent tags remain primary-response-driven.
- Review/edit: song-data evidence rows; save/update per song; gold/teal chips only where meaningful.
- Account: Cartenza support, FAQ, privacy, Apple status, Share Evidence backup.

Acceptance:

- Each surface has a visual direction before implementation.
- Player remains functional and uncluttered.

Progress:

- First-run consent/access/onboarding/generation/account now share the Cartenza lockup, compass mark, and Night Vision backdrop.
- Mission, detail, review, player-adjacent, and diagnostic surfaces inherit the retuned theme where they already used `WaymarkTheme`.

### CBR-010: TestFlight/release metadata planning

Status: pending.

Scope:

- Update eventual TestFlight app name, icon, screenshots, build notes, privacy copy, and support language to Cartenza.
- Confirm whether `Music Taste Atlas` appears as subtitle/descriptor.
- Confirm any legal/trademark constraints before external testers.

Acceptance:

- Release checklist reflects Cartenza before app metadata is changed.
- Privacy/support copy uses the new name consistently.

## Risks And Watch Items

1. The current mockup palette is too bright for Cartenza. It should move away from electric cyan/blue buttons and toward restrained gold/teal accents.
2. The included wordmark is a placeholder. Do not treat it as final production typography.
3. Concept boards are not implementation assets. They should guide design, not be embedded in UI.
4. Overusing contour texture would make the app feel themed instead of premium. Use it as atmosphere, not wallpaper.
5. The Player should not become a branding canvas. Album art, playback, reactions, tags, and notes must stay primary.
6. Renaming code modules now could create unnecessary churn. Separate user-facing brand from internal architecture unless engineering chooses otherwise.
7. Existing docs now contain stale Waymark decisions. They need a superseding note so the team does not execute the wrong name.

## Recommended Next Review

Before any UI wiring, review these five decisions:

1. Approve `Cartenza` as the TestFlight-facing app name.
2. Approve `Your music. Mapped.` as the primary Alpha tagline.
3. Decide whether Concept 5 starter assets are acceptable as Alpha placeholders.
4. Decide whether `Music Taste Atlas` is a visible descriptor or internal category language.
5. Confirm that the rebrand should preserve the approved Alpha flow exactly while only changing name, copy, tokens, icon/launch direction, and visual texture.
