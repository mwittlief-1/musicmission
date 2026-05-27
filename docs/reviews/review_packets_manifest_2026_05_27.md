# Review Packets Local Archive Manifest - 2026-05-27

This manifest records the local `review_packets/` contents observed during repo cleanup. The directory is classified as generated review/archive material and is ignored by default. Promote active human-readable review docs into `docs/reviews/` before tracking them.

## Local Contents

| Path | Size | Classification | Action |
| --- | ---: | --- | --- |
| `review_packets/affinity_graphwide_v0_1/` | 48M | Generated affinity review/output packet | Keep local or archive externally. Scripts still write generated affinity sidecar outputs here. |
| `review_packets/atlas_explainer_alpha_acceptance_2026_05_26/` | 32K | Generated Atlas acceptance packet | Promote selected Markdown into `docs/reviews/atlas_explainer/` only if it remains an active review artifact. |
| `review_packets/build18_mission_atlas_product_review_2026_05_26/` | 24K | Generated product review packet | Promote selected Markdown into `docs/reviews/mission_atlas/` only if it remains active. |
| `review_packets/*.zip` | 148K-472K each | Generated packet archives | Keep out of git; store externally if needed. |

## Notes

- `scripts/build_affinity_graphwide_phase0_2_v0_1.py`, `scripts/generate_affinity_graphwide_sidecar_v0_1.py`, `scripts/build_affinity_research_batches_v0_1.py`, and related affinity reporting/merge scripts use `review_packets/affinity_graphwide_v0_1/` as a generated output workspace.
- The source-like affinity contract package is tracked separately under `data/canonical_graph/affinity_contracts/v0_3_1/`.
- Do not delete local review packets until the owner confirms old packet archives, zips, and screenshots are no longer needed.
