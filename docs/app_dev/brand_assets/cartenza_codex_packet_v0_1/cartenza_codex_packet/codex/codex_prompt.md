# Codex Prompt — Implement Cartenza Night Vision Branding v0.1

You are working on the iOS app formerly referred to as Waymark / My Music OS. Implement the working Cartenza visual identity direction in the app prototype without changing core product behavior.

## Inputs

Use this packet:

- `docs/brand_direction_v0_1.md`
- `docs/implementation_notes.md`
- `tokens/cartenza_night_vision_tokens.json`
- `assets/svg/cartenza_mark_concept5.svg`
- `assets/svg/cartenza_app_icon_concept5.svg`
- `assets/svg/cartenza_topographic_texture.svg`
- `assets/reference/concept_5_selected_compass_seal_reference.png`
- `assets/reference/concept_1_topographic_c_reference.png`

## Goal

Apply the working **Cartenza / Night Vision** brand layer to the current app shell/prototype.

## Required visual direction

- Brand name: `Cartenza`
- Preferred tagline: `Your music. Mapped.`
- Master mark: Concept 5 circular cartographic monogram / compass-seal C
- Secondary texture: Concept 1 topographic contour C / taste terrain
- Mood: dark, restrained, premium, intelligent, modern, slightly sexy

## Implementation requirements

1. Add or update a central brand/theme constants file for Cartenza tokens.
2. Add the SVG or equivalent image asset for the app icon placeholder / logo mark.
3. Update visible brand copy on welcome / onboarding / starter surfaces from Waymark to Cartenza where appropriate.
4. Add a Cartenza-branded welcome/splash-style component if none exists.
5. Apply Night Vision colors to onboarding, mission cards, and starter Atlas surfaces.
6. Use topographic texture only as a subtle background layer, never as busy foreground ornament.
7. Keep Listen/player surface clean and functional.
8. Do not change survey, mission, atlas, playback, export, or backend schemas.
9. Do not embed generated concept-board screenshots as UI assets.
10. Preserve existing tests; add snapshot or asset-loading checks if the repo has conventions for that.

## Non-goals

- Do not rebuild the app architecture.
- Do not change product IA.
- Do not implement final production logo export pipeline.
- Do not add social features or unrelated visual systems.
- Do not overuse animation/glow effects.

## Acceptance

Use `codex/acceptance_checklist.md` as the acceptance checklist.
