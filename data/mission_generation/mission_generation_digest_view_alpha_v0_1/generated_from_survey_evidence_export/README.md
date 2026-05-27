# MissionGenerationDigestView From Atlas Ingestion

This directory contains deterministic MissionGenerationDigestView packets built from Atlas Survey Evidence Export ingestion outputs.

The builder consumes `atlas_digest_view.json` and `signals.jsonl`. It does not read raw Survey payloads, Profile Writer output, hidden simulator truth, or canonical graph mutation instructions.

| profile | candidate roles | recent signals | evidence refs | output bytes | reduction vs Survey Evidence Export | reduction vs AtlasDigestView |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| public_profile_01_A3_Al1_S2 | 12 | 12 | 23 | 48433 | 87.4% | 70.2% |
| public_profile_05_A3_Al1_S2 | 12 | 12 | 25 | 48946 | 87.1% | 69.7% |
| public_profile_06_A3_Al1_S2 | 12 | 12 | 16 | 41814 | 89.1% | 72.8% |

## Remaining Blocker

`ATL-I001` remains open: Survey Simulator still needs to provide the fixed Alpha 1 `A4_Al2_S4` Survey Evidence Export fixture. Current generated packets prove the Atlas-to-MissionGenerationDigestView handoff on existing normalized `A3_Al1_S2` exports only.
