# Cartenza Logo Refinement - 2026-05-27

Status: Candidate B locked for Alpha logo direction. Runtime app assets are not updated by this packet.

## Locked Decision

Candidate B, `Cartographic Cut`, is the selected Cartenza logo direction as of 2026-05-27.

Selected aliases:

- `assets/svg/cartenza_logo_selected.svg`
- `assets/png/cartenza_logo_selected.png`

Use those aliases for downstream design review and future runtime implementation. Keep the A/B/C files as decision history.

## Goal

Refine the Cartenza Concept 5 direction without reopening the broader brand system.

Kept:

- Cartenza name
- Night Vision palette
- circular cartographic C / compass-seal direction
- subtle topographic motif as secondary language

Changed:

- cleaner C silhouette
- less small-detail noise
- stronger small-size app icon read
- clearer hierarchy between mark, compass, and waypoint accents

## Candidates

| Candidate | File | Intent |
| --- | --- | --- |
| A: Atlas Seal | `assets/svg/cartenza_logo_candidate_a_atlas_seal.svg` | Most conservative. Keeps the circular seal but simplifies the C, ring system, and compass detail. |
| B: Cartographic Cut | `assets/svg/cartenza_logo_candidate_b_cartographic_cut.svg` | Locked. Stronger monogram. Uses a cut C with route/contour accents and fewer explicit compass cues. |
| C: Waypoint C | `assets/svg/cartenza_logo_candidate_c_waypoint_c.svg` | Most app-icon oriented. Minimal, high-contrast C arc with waypoint nodes and a small center signal. |

PNG previews are available in `assets/png/` for quick viewing and sharing.

## Review Page

Open `index.html` in this folder for phone-width comparison and small-size previews.

## Runtime Follow-Up

After implementation approval, replace the current alpha placeholder icon and update the SwiftUI code-drawn mark to match Candidate B. Keep that as a separate runtime slice because the app worktree is currently active.

## Decision Criteria

- Reads as a C at 29 px and 60 px.
- Feels premium and cartographic without looking like a generic compass app.
- Supports Night Vision without becoming too decorative.
- Has enough personality to be owned by Cartenza.
- Can be redrawn as clean final vector artwork later.
