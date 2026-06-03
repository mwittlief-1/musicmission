# Cartenza Alpha Mission Delivery v0.2

This package is an offline, app-import readiness slice for Cartenza Alpha mission delivery.

It defines how accepted Mission Opportunity Selection outputs may be converted into guarded Alpha mission payloads that the app team can wire against. It is not a production mission generator and it does not connect runtime listener evidence.

## Included

- Mission Construction Contract v0.2 for Alpha-safe mission types.
- App-import mission payload JSON Schema v0.2.
- TypeScript contract types.
- Validator and product gates for route coherence, source purity, negative budget, playback/import readiness, explanation completeness, hidden-oracle leakage, and runtime/canonical mutation flags.
- Golden approved/revise/rejected fixture sets derived from accepted Phase 1G offline song-pack simulations.
- Backend endpoint contract draft for a future first mission batch Supabase function.
- App wiring readiness/gap report.

## Guardrails

- No runtime selector wiring.
- No real listener evidence connection.
- No production mission generation.
- No final mission copy generation.
- No canonical graph mutation.
- Hidden synthetic reactions are not written into app-import payloads.
- Ordinary Alpha app-import-ready missions may not contain unresolved route items.

## Commands

```bash
python3 scripts/build_alpha_mission_delivery_v0_2.py
python3 scripts/validate_alpha_mission_delivery_v0_2.py
```

## Current Bottom Line

App wiring can begin against these local fixtures/contracts for schema, route-card, reaction, validation, and resolution-adapter work. TestFlight UAT is still blocked until Apple Music resolution and app model/schema compatibility are closed.
