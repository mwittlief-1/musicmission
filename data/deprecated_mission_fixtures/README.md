# Deprecated Mission Fixtures

This directory is a small holding area for retired app mission fixtures that should not be used by runtime code.

The files here are kept to preserve history while app resource deletions and replacement fixtures are reviewed. Move or remove them only after owner approval.

## App Resource Retirement Coverage

Observed on 2026-05-27 while the app worktree had pending deletions under `MusicAtlasController/Resources/`.

| App resource pending deletion | Matching tracked copy | SHA-256 |
| --- | --- | --- |
| `sample_mission_lithuanian_discovery_v0_3_alpha.json` | `data/missions/sample_mission_lithuanian_discovery_v0_3_alpha.json`; `data/deprecated_mission_fixtures/sample_mission_lithuanian_discovery_v0_3_alpha.json` | `8d7cfc337e8c93f73e3e8940a8e327291cecf9d5794198917a2aafc13a166299` |
| `waymark_matt_10_personal_missions_v0_1.json` | `data/missions/waymark_matt_10_personal_missions_v0_1.json`; `data/deprecated_mission_fixtures/waymark_matt_10_personal_missions_v0_1.json` | `3642f5547760136666298beb8730a27bbe8dd943d10aa314ce5b762d746e869b` |
| `sample_mission_love_tributaries_v0_2.json` | `data/missions/sample_mission_love_tributaries_v0_2.json` | `1c16f3a8fcc71581c2828c41d8a7b66695b7e77412d8334b05fe78e1a70795e6` |

Notes:

- The deprecated fixture copies for the Lithuanian discovery and personal missions files duplicate the tracked `data/missions/` copies exactly.
- The love-tributaries app resource has an exact tracked copy in `data/missions/`. The kickoff packet and XCTest fixture variants are intentionally not byte-identical.
- Do not remove this deprecated holding area until the app-resource deletion slice is reviewed and the owner approves any archive consolidation.
