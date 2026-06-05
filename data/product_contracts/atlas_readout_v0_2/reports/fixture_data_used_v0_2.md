# Fixture Data Used v0.2

Runtime resource:

- `MusicAtlasController/Resources/atlas_home_what_were_seeing_so_far_fixture_v0_2.json`

Product contract source:

- `data/product_contracts/atlas_readout_v0_2/fixtures/atlas_home_what_were_seeing_so_far_fixture_v0_2.json`

Fixture identity:

- Schema version: `cartenza.atlas_home_what_were_seeing_so_far.v0.2`
- Source fixture ID: `synthetic_atlas_home_readout_v0_2`
- Module name: `What We're Seeing So Far`
- Optional setup line: omitted with `null`

Rendered data:

- The app renders only `display_model`.
- The rendered model contains one opening insight and five insight cards.
- Each card has one role, one title, one body, and up to three evidence examples.

Non-rendered review data:

- `sparse_signal_debug` is bundled for tests and product review.
- `acceptance_audit` is bundled for deterministic validation.
- Neither debug nor audit fields are displayed in the Atlas Home UI.

Scope notes:

- The fixture is synthetic.
- No Matt-specific or founder-specific data is used.
- No Mission-team metadata is consumed.
- No runtime model generation is used.
