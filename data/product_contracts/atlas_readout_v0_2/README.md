# Cartenza Atlas Readout v0.2

Status: Atlas Home module spec and synthetic fixture output. Offline only.

This package revises the post-survey Atlas Home module from the v0.1 prompt-test direction into a compact, insight-first product surface.

The v0.2 contract now includes the sparse-signal correction: the module should show the strongest insights, not merely the highest-volume clusters. A small coherent pocket with positive evidence and no meaningful negative signal can earn a card when it is useful to test.

Approved module name:

```text
What We're Seeing So Far
```

## Included

- Module spec: [atlas_home_what_were_seeing_so_far_v0_2.md](atlas_home_what_were_seeing_so_far_v0_2.md)
- Display-model schema: [schemas/atlas_home_what_were_seeing_so_far_v0_2.schema.json](schemas/atlas_home_what_were_seeing_so_far_v0_2.schema.json)
- Synthetic fixture output: [fixtures/atlas_home_what_were_seeing_so_far_fixture_v0_2.json](fixtures/atlas_home_what_were_seeing_so_far_fixture_v0_2.json)
- Rendered sample output: [rendered_sample_output.md](rendered_sample_output.md)
- Fixture data note: [reports/fixture_data_used_v0_2.md](reports/fixture_data_used_v0_2.md)
- Sparse-card eligibility debug report: [reports/sparse_card_eligibility_debug_report_v0_2.md](reports/sparse_card_eligibility_debug_report_v0_2.md)
- Copy compliance report: [reports/copy_compliance_report_v0_2.md](reports/copy_compliance_report_v0_2.md)

## Boundary

Allowed:

- Atlas Home copy/spec work.
- Synthetic fixture state.
- Compact evidence examples as secondary support.
- Sparse-but-clean positive pockets when they are coherent and testable.

Not allowed:

- Mission selection.
- Mission context implementation.
- Post-mission learning summaries.
- Runtime GPT generation.
- Matt-specific or founder-specific data.
- Survey-report language such as "you selected" or "out of 84 responses."
- Ranking cards only by count volume.

## PM Correction From v0.1

`B02` is a structural reference only. It is not the final copy direction.

The v0.2 module must lead with interpretation, then support with compact evidence. It should read like Cartenza is noticing the early shape of the map, not reporting back survey inputs.

## PM Correction For Sparse Signals

The module must not hide low-volume, high-purity regions behind larger clusters. The synthetic fixture surfaces classic/heavy rock as a small but clean signal: not enough evidence to call a center, but too coherent to ignore.

The fixture carries a non-rendered sparse-signal debug section so review and tests can verify why a low-volume pocket is eligible without exposing those mechanics in the app surface.
