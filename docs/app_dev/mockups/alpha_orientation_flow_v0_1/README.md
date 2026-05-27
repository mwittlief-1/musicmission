# Cartenza Alpha Orientation Flow Mockup v0.1

Status: approved for Alpha 1 Swift implementation by Product/Founder on 2026-05-22.

Purpose: clickable HTML review prototype for the Alpha 1 first-run experience.

Open `index.html` in a browser, or serve this folder locally:

```sh
python3 -m http.server 8765
```

Then open:

```text
http://localhost:8765/
```

You can also jump directly to a numbered screen:

```text
http://localhost:8765/?screen=23
```

Useful review jumps:

```text
http://localhost:8765/?screen=21
http://localhost:8765/?screen=23&reaction=like
http://localhost:8765/?screen=25
```

## Included Surfaces

- Privacy / Alpha disclosure gate
- Sign in with Apple + Apple Music connection concept
- Six founder-provided orientation pages
- Alpha FAQ
- Forced Survey intake mockups: 4 artist pages, 2 album pages, 4 song pages
- Post-Survey generation status
- Core IA starter surfaces: Mission home, Mission detail, Player, Review, My Account
- Mission tab pass with a 10-mission Alpha batch surface
- Player pass with larger proportional layout, support-only issue action removed, and reaction-specific secondary tags
- Mission Review pass using song / artist / album evidence rows, plus per-song edit/save for reaction, tags, and notes
- Orientation pass with consistent header placement and a tighter mobile-first content area
- Full mobile spacing pass across all 26 screens at a 390x844 review viewport

## Notes

- This is a product/design mockup only. It does not change Swift app code.
- Approval covers flow, hierarchy, mobile-first layout direction, and interaction model. Final legal/privacy copy, retention/deletion language, app icon art, and automatic evidence upload policy still require their separate release approvals.
- Survey and mission content is sample mock data, not production mission/user content.
- `Share Evidence` remains represented as a product concept while engineering confirms automatic/scheduled Supabase sync versus manual support fallback.
- Visual direction follows the attached Night Vision brand system: dark-native, restrained semantic color, evidence-first copy, no confidence math.
- The layout now treats mobile preview as the primary test case: on narrow screens, only the phone mockup and Back/Next controls are shown.

Implementation handoff: `docs/app_dev/mockups/alpha_orientation_flow_v0_1/IMPLEMENTATION_HANDOFF.md`.
