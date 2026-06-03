# App-Import Readiness Status Model v0.2

This status model separates offline product review from app import readiness.

| status | meaning | may show in app as ordinary mission? |
| --- | --- | --- |
| `review_only` | Shape exists for PM/harness review only. | no |
| `schema_valid` | JSON shape passes schema but product gates have not passed. | no |
| `contract_valid` | Mission-type contract gates pass, but import readiness is not established. | no |
| `needs_revision` | Route could become useful, but currently misses a product gate. | no |
| `rejected_product` | Route is not Alpha-safe or mission type is deferred. | no |
| `app_import_candidate` | Route is coherent, concrete enough for resolution, and eligible after playback metadata/Apple Music resolution. | dev/debug only until resolved |
| `app_import_blocked_unresolved` | One or more route items are unresolved or blocked. | no |
| `app_import_blocked_policy` | A policy guardrail failed. | no |
| `app_import_ready` | All schema, contract, policy, explanation, and playback/import gates pass. | yes |

`alpha_plausible` from earlier simulations is intentionally not reused as app readiness.
