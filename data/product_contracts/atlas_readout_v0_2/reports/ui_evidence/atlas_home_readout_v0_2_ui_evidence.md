# Atlas Home Readout v0.2 UI Evidence

Status: `approved_for_alpha_ui_render`

Screenshot:

- `atlas_home_readout_v0_2_ipad_full.png`
- `atlas_home_readout_v0_2_iphone_top.png`

Capture context:

- Device: iPad Pro 13-inch simulator
- Device: iPhone 17 Pro Max simulator
- Build: Release iOS Simulator
- Surface: Atlas Home
- Source: app-bundled synthetic fixture `MusicAtlasController/Resources/atlas_home_what_were_seeing_so_far_fixture_v0_2.json`

Visual acceptance notes:

- The module renders with the approved title, `What We're Seeing So Far`.
- The opening insight appears above the cards.
- All five insight cards are visible in the captured frame:
  - Strongest Center
  - Sound Shape
  - Secondary Branch
  - Small Signal
  - Open Question
- Evidence examples are compact and secondary: each card renders one `Evidence:` line with three visible examples.
- The sparse-clean heavy-rock pocket is visible as `Small but clean heavy-rock signal`.
- No raw affinity tags are user-facing in the rendered module.
- The module is rendered from synthetic fixture data only; no runtime model generation or mission selection/context is used for this surface.
- The iPhone top viewport shows the opening, first two cards, and start of the third card without text overflow; the full five-card module scrolls in the Atlas Home feed.

Implementation note:

- A temporary local launch argument was used only to open the screenshot build directly on Atlas Home. That screenshot-only source hook was removed before final validation.
