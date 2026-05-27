# Atlas Schema Contract v0.1 Acceptance Report

Generated: 2026-05-20

## Output Inventory

Created:

- `data/atlas_schema/atlas_schema_contract_v0_1.md`
- `data/atlas_schema/atlas_schema_contract_v0_1.json`
- `data/atlas_schema/examples/landmark.json`
- `data/atlas_schema/examples/region.json`
- `data/atlas_schema/examples/frontier.json`
- `data/atlas_schema/examples/dead_end.json`
- `data/atlas_schema/examples/waypoint.json`
- `data/atlas_schema/examples/signal.json`
- `data/atlas_schema/examples/taste_feature.json`
- `data/atlas_schema/examples/survey_seeded_update.json`
- `data/atlas_schema/examples/mission_review_possible_update.json`
- `data/atlas_schema/atlas_schema_acceptance_report.md`

## Validation

JSON syntax check:

```text
jq empty data/atlas_schema/atlas_schema_contract_v0_1.json data/atlas_schema/examples/*.json
```

Result:

```text
passed
```

JSON Schema validation:

```text
npx --yes ajv-cli@5 validate --strict=false --spec=draft2020 -s data/atlas_schema/atlas_schema_contract_v0_1.json -d 'data/atlas_schema/examples/*.json'
```

Result:

```text
data/atlas_schema/examples/dead_end.json valid
data/atlas_schema/examples/frontier.json valid
data/atlas_schema/examples/landmark.json valid
data/atlas_schema/examples/mission_review_possible_update.json valid
data/atlas_schema/examples/region.json valid
data/atlas_schema/examples/signal.json valid
data/atlas_schema/examples/survey_seeded_update.json valid
data/atlas_schema/examples/taste_feature.json valid
data/atlas_schema/examples/waypoint.json valid
```

Invariant checks:

```text
jq -r '.. | objects | select(.record_type? == "atlas_node") | select(has("role") or has("atlas_roles") or has("roles"))' data/atlas_schema/examples/*.json
jq -r '.. | objects | select(.record_type? == "possible_atlas_update_candidate") | select(.canonical_graph_mutation_allowed != false or (.source == "mission_review" and (.review_requirement.required != true or .lifecycle.promotion_state == "promoted")))' data/atlas_schema/examples/*.json
```

Result:

```text
passed with no matching violations
```

## Contract Decisions Accepted

### Canonical Graph Boundary

Accepted.

The contract separates:

```text
Canonical graph = shared music-object substrate
Atlas schema = user-specific interpretation layer
```

Atlas records can reference canonical IDs, but no Atlas write path is allowed to mutate canonical graph objects.

`PossibleAtlasUpdateCandidate.canonical_graph_mutation_allowed` is schema-pinned to `false`.

### Music Object Reference Union

Accepted.

`music_object_ref` supports:

- canonical graph refs
- user-local refs
- external-catalog refs
- unresolved refs
- composition placeholders

The examples cover:

- canonical artist: `landmark.json`
- canonical album: `waypoint.json`
- canonical song recording: `signal.json`
- user-local artist: `frontier.json`, `survey_seeded_update.json`
- external-catalog artist: `taste_feature.json`
- unresolved composition placeholder: `dead_end.json`

### Role Authority

Accepted.

`AtlasNode` contains no authoritative role field.

Role truth is stored in `AtlasRoleAssignment.role`.

The role enum is limited to:

- `landmark`
- `region`
- `frontier`
- `dead_end`
- `waypoint`
- `unknown`
- `signal_only`

`road` and `lineage` are modeled separately as structure and edge records.

### Survey Write Path

Accepted.

`survey_seeded_update.json` demonstrates:

- a Survey `Signal`
- a provisional `AtlasNode`
- a `PossibleAtlasUpdateCandidate`
- no promoted role assignment
- no canonical graph mutation

### Mission Review Write Path

Accepted.

`mission_review_possible_update.json` demonstrates:

- a Mission Review evidence `Signal`
- a possible role update candidate
- `review_requirement.required=true`
- `promotion_state=candidate`
- no automatic promotion
- no canonical graph mutation

### Candidate Pool Builder Read Path

Accepted.

Candidate Pool Builder can query `AtlasRoleAssignment.candidate_pool_behavior` using:

- `anchor`
- `bridge`
- `probe`
- `risky_probe`
- `waypoint`
- `trap`
- `exclude`
- `unknown`

This avoids overloading the Atlas role enum with routing behavior.

### Mission Generation Read Path

Accepted.

The contract defines `AtlasDigestView` as the read surface for Mission Generation. It includes role assignment IDs, recent signals, user taste feature states, vocabulary terms, anti-overfitting rules, unresolved questions, mission constraints, and suggested candidate roles.

Mission Generation should not consume raw Atlas tables directly in v0.1.

### Evidence Auditability

Accepted.

Persistent user state objects include `evidence_signal_ids` or source signal references. `Signal` separates:

- `signal_strength`
- `interpretation_confidence`

This preserves the difference between observed behavior volume and interpretive certainty.

## Acceptance Criteria Result

| criterion | result | evidence |
|---|---|---|
| Survey creates starter Atlas state without final verdicts. | Pass | `survey_seeded_update.json` uses provisional node and proposed candidate. |
| Mission Generation consumes an Atlas Digest. | Pass | `AtlasDigestView` is defined in JSON Schema and Markdown contract. |
| Candidate Pool Builder can query anchors, bridges, probes, risky probes, waypoints, and traps. | Pass | `candidate_pool_behavior` enum covers these behaviors. |
| Mission Review records Signals and possible updates without overpromotion. | Pass | `mission_review_possible_update.json`; mission-review candidates cannot use `promotion_state=promoted`. |
| Atlas UI can render basic Landmark, Region, Frontier, Dead End, and Waypoint cards. | Pass | Role card examples pair `AtlasNode` with authoritative `AtlasRoleAssignment`. |
| Evidence remains auditable back to signal sources. | Pass | Examples and schema use signal IDs and source fields. |

## Known v0.1 Limitations

- The JSON Schema validates record shape, not referential integrity across storage tables.
- The schema does not verify that canonical IDs exist in the current dry-run graph. That check belongs to importer or service-layer validation.
- `proposed_payload` is intentionally patch-like and loosely typed in v0.1 so Survey and Mission Review can propose multiple record updates without separate candidate tables.
- Promotion thresholds are policy-defined outside this schema. The schema blocks Survey/Mission auto-promotion candidates, but a later reviewed write path still needs application-level enforcement.
- Full composition modeling is not implemented here. `composition_placeholder` preserves user evidence until the canonical graph has an explicit composition layer.

## Recommendation

Use this as the v0.1 shared contract for Survey, Mission, Candidate Pool Builder, Mission Review, and Atlas UI prototypes. The next hardening pass should add service-level referential integrity checks and typed patch payload schemas for common update candidate actions.
