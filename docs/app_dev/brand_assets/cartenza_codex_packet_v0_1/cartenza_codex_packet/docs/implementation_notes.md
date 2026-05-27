# Cartenza Implementation Notes for Codex

## Scope

This packet is for implementing the working **Cartenza / Night Vision** visual direction inside the app shell or prototype. It is not a final legal/trademark/production design clearance package.

## Primary implementation target

Build a small design-system layer and replace old Waymark branding references where appropriate in visual surfaces.

Recommended first implementation targets:

1. App display name string: `Cartenza` in local/dev UI.
2. Splash / launch-style screen using selected mark direction.
3. App icon placeholder using `assets/svg/cartenza_app_icon_concept5.svg` or rendered PNG equivalent.
4. Onboarding welcome screen with wordmark and `Your music. Mapped.`
5. Starter Atlas card using Night Vision tokens and subtle topographic texture.
6. Mission card styling using restrained charcoal/silver/gold/teal palette.

## Asset usage

### Production caution

- Do not treat generated PNG concept boards as final art.
- Do not embed concept board text or generated mockup UI in production screens.
- Use the SVGs as starter implementation assets only.
- Final brand assets should eventually be rebuilt as clean vector source files by design.

### SVGs included

- `cartenza_mark_concept5.svg` — transparent master mark approximation.
- `cartenza_app_icon_concept5.svg` — dark rounded-square icon approximation.
- `cartenza_topographic_texture.svg` — subtle contour texture.
- `cartenza_wordmark_placeholder.svg` — wordmark placeholder, not a final typography asset.

## Design rules

### Backgrounds

Use near-black / charcoal layered backgrounds. Prefer quiet depth over gradients.

Good:

- low-contrast texture
- subtle radial shadows
- faint map/field lines
- small gold signal points

Bad:

- bright neon
- green music-app color dominance
- glassmorphism overload
- tech SaaS blue gradients

### Accent usage

Gold should mean signal, waypoint, guide, center, selected, or important path.

Teal should mean Atlas substrate, map layer, confidence, field, unknown/frontier, or system intelligence.

Do not overuse either accent.

### Components

- Cards: dark charcoal panels with soft border and subtle elevation.
- Mission cards: a small gold/teal route hint is enough.
- Atlas cards: faint topographic texture or orbit/compass motif.
- Buttons: restrained, not bright.
- Text: silver/ash on charcoal, high contrast but not pure white everywhere.

## App copy examples

Welcome screen:

```text
Cartenza
Your music. Mapped.

Connect Apple Music and answer a short Survey. Cartenza will build your starter Atlas and generate your first listening missions.
```

Starter profile surface:

```text
What We Think So Far
Your first map is provisional. We are using your Survey answers and Apple Music context to build a starter Atlas, then testing it through listening missions.
```

Mission card language:

```text
Why this route exists
This mission tests whether [hypothesis] is a real signal or a false-nearby road.
```
