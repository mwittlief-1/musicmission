# Mission Construction Contract v0.2

Status: PM review contract design. Offline only.

## Purpose

Mission Construction Contract v0.2 defines the full affinity and graph-derived mission-planning input contract for review-only mission candidates assembled from Derived Affinity Substrate v0.1.1. It is not the full production mission schema.

This contract stops at planning input. It does not model runtime lifecycle, playback, persistence, catalog availability, UI rendering, or production mission state.

The contract uses this construction chain:

```text
mission_hypothesis
-> target_affinity_pattern
-> known anchors
-> gateway candidates
-> bridge candidates
-> frontier probes
-> caution/high-whiplash controls
-> route sequence
-> expected evidence
-> reaction prompts
-> AtlasDelta plan
```

## Non-Goals

This contract does not:

- Mutate canonical graph truth.
- Change app runtime behavior.
- Infer listener preference from affinity similarity.
- Assign personal Atlas roles.
- Wire a mission generator.
- Generate production missions.
- Model playback, persistence, catalog availability, UI rendering, or runtime lifecycle state.
- Promote mission candidates into product truth.

## Source Inputs

Allowed source package:

- `derived_affinity_substrate_v0_1_1/`

Primary v0.1.1 inputs:

- `mission_candidate_pool_v0_1_1.json`
- `hardened_bridge_candidates_v0_1_1.json`
- `atlas_road_candidates_v0_1_1.json`
- `cross_family_bridge_edges_v0_1_1.json`
- `manifest_v0_1_1.json`

No mission builder using this contract may read canonical graph files as authority. Candidate identifiers, tags, risk flags, readiness scores, graph-placement context, and provenance must come from the accepted substrate package or lineage claims already carried by that package.

## Required Layer Separation

Every mission candidate must keep these layers separate:

- `intrinsic_affinity`: the target musical and emotional pattern being tested.
- `context_overlays`: route, scene, social, historical, or use-case context.
- `graph_context`: graph placement and role context carried from the accepted substrate or its lineage.
- `risk_review`: false-nearby, high-whiplash, duplicate, identity, overfamiliar, gateway, and manual review flags.
- `listener_evidence`: absent at construction unless supplied later by explicit evidence.
- `product_role_assignment`: blocked during construction; AtlasDelta proposals are review plans only.

## Graph Context

Every candidate track, gateway candidate, bridge candidate, frontier probe, caution/high-whiplash control, and route sequence item must include a `graph_context` block.

The block supports:

- `family_ids` and `family_names`.
- `archetype_ids` and `archetype_names`.
- `archetype_role` or membership role.
- `track_tier_within_archetype`.
- `album_tier_within_archetype`.
- `artist_tier_within_archetype`.
- `graph_item_role`: one of `canonical_anchor`, `major_representative`, `gateway`, `bridge`, `deep_cut`, `contextual_object`, or `unknown`.
- `role_basis`: a readable explanation of the planning role.
- `provenance`: source files, source candidate IDs, source fields, and notes for the placement claim.

Unknown fields must be represented as `null`, `"unknown"`, or empty arrays. Do not fill missing family names, archetype names, or tier claims by reading canonical graph files in this pass.

## Mission Candidate Envelope

Each review-only mission candidate must use this envelope:

```json
{
  "mission_id": "string",
  "contract_version": "mission_construction_v0_2",
  "source_substrate_version": "derived_affinity_substrate_v0_1_1",
  "mission_type": "safe_risky_split|album_world_test|route_gateway_mission|cross_family_bridge_mission|frontier_probe|false_nearby_trap_test|one_object_exception_test|context_mission|b_b_plus_shelf_mission|modern_discovery_correction",
  "mission_hypothesis": "string",
  "target_affinity_pattern": [],
  "known_anchors": [],
  "gateway_candidates": [],
  "bridge_candidates": [],
  "frontier_probes": [],
  "caution_high_whiplash_controls": [],
  "identity_duplicate_quarantine_exclusions": [],
  "route_sequence": [],
  "reaction_prompts": [],
  "expected_evidence": {
    "confirming": [],
    "falsifying": [],
    "ambiguous": []
  },
  "atlas_delta_plan": {
    "if_confirmed": [],
    "if_falsified": [],
    "if_ambiguous": [],
    "write_mode": "evidence_only"
  },
  "listener_evidence": {
    "status": "absent_at_construction",
    "evidence_ids": [],
    "not_inferred_from_affinity": true
  },
  "review": {
    "pm_review_required": true,
    "runtime_allowed": false,
    "production_mission_allowed": false
  },
  "provenance": {
    "source_files": [],
    "canonical_graph_mutation": "not_performed",
    "runtime_ingestion": "not_performed"
  }
}
```

Candidate track, bridge candidate, frontier probe, gateway candidate, caution control, and route item objects must include:

```json
{
  "graph_context": {
    "family_ids": [],
    "family_names": [],
    "archetype_ids": [],
    "archetype_names": [],
    "archetype_role": null,
    "membership_role": null,
    "track_tier_within_archetype": "unknown",
    "album_tier_within_archetype": "unknown",
    "artist_tier_within_archetype": "unknown",
    "graph_item_role": "unknown",
    "role_basis": "string",
    "provenance": {
      "source_files": [],
      "source_candidate_ids": [],
      "source_fields": [],
      "notes": "string"
    }
  }
}
```

## Candidate Selection Rules

Mission hypotheses:

- Must be testable.
- Must name the affinity pattern under test.
- Must identify what would confirm and falsify the hypothesis.
- Must not assume that similarity means preference.

Target affinity pattern:

- Must come from intrinsic affinity tags.
- May be explained by context overlays, but context overlays must not replace intrinsic affinity.
- Must not be broadened from one song, one album, or one narrow object without review labeling.

Known anchors:

- May be included only as non-personal review anchors unless explicit listener evidence is supplied by a later evidence source.
- Must not be treated as listener-positive by default.

Gateway candidates:

- Must include the reason they are accessible.
- Must include graph placement context, even when family/archetype names or tiers are unknown.
- Must state that gateway status is not a quality score.
- Must remain separate from listener preference.

Bridge candidates:

- Should prefer `clean_bridge_candidate` or PM-reviewed `mission_specific_bridge` inputs.
- Must include both `intrinsic_affinity_score` and `product_bridge_readiness_score` when available.
- Must include graph placement context for the bridge role and any family/archetype IDs carried by accepted substrate lineage.
- Must display any bridge category other than clean.
- Must exclude identity quarantine and duplicate/version ambiguity from route sequencing unless the mission explicitly tests identity review, which is outside v0.2 production scope.

Frontier probes:

- Must identify the evidence gap.
- Must include graph placement context for why the probe is a frontier/deep-cut/contextual planning item.
- Must be placed after gateways or anchors in the route sequence.
- Must include clear confirming and falsifying evidence.

Caution and high-whiplash controls:

- Must include framing requirements.
- Must include graph placement context for the caution role.
- Must not be hidden inside the route sequence.
- Must be spaced or isolated when used for a controlled probe.
- Must make false-nearby and high-whiplash risk visible to PM.

Identity and duplicate quarantine exclusions:

- Must list excluded candidate IDs and reasons.
- Must not appear in clean route sequencing.
- May remain in review notes for PM inspection.

## Route Sequencing Rules

Routes should be assembled in this order unless the mission hypothesis explicitly justifies a different order:

1. Gateway or accessible anchor.
2. Clean bridge or low-risk transition.
3. Target pattern reinforcement.
4. Frontier probe.
5. Caution or high-whiplash probe with framing.
6. Closing prompt that captures evidence.

Each route item must include:

- Source candidate ID.
- Track or cluster reference.
- Route role.
- Inclusion reason.
- Intrinsic affinity tags used.
- Context overlays used.
- Graph context.
- Risk flags.
- Readiness or confidence.
- Readiness notes.
- What the item is testing.

## Evidence Rules

Confirming evidence may include:

- Explicit positive reaction.
- Save, replay intent, or equivalent future signal.
- Listener note that confirms the target affinity pattern.
- Positive reaction to the bridge after gateway exposure.
- Positive reaction to a frontier probe without requiring context-only explanation.

Falsifying evidence may include:

- Skip, low rating, or explicit negative reaction.
- Listener note rejecting the hypothesized connection.
- Evidence that fit was context-only, identity-confused, overfamiliar, or false-nearby.
- Acceptance of gateway items with rejection of bridge or frontier items.
- High-whiplash response that requires reframing before reuse.

Ambiguous evidence may include:

- Positive response to familiarity but not the target affinity pattern.
- Interest in context but not the song or cluster.
- Mixed reaction that requires a safer follow-up mission.

## AtlasDelta Plan Rules

AtlasDelta plans are review proposals only.

Allowed write mode:

- `evidence_only`

Blocked write modes:

- automatic Landmark assignment.
- automatic Region promotion.
- automatic Road promotion.
- automatic Dead End promotion.
- canonical graph mutation.
- runtime mission generation.

If confirmed:

- Record evidence only.
- Queue scoped review for Waypoint, Frontier, Caution, Road, Region, or Landmark depending on evidence type.
- Require repeated listener evidence before personal role assignment.

If falsified:

- Record negative evidence only.
- Queue Caution or Dead End review only when mismatch is repeated or clearly explained.
- Do not mutate canonical graph truth.

If ambiguous:

- Record ambiguity.
- Lower confidence or request a safer follow-up test.
- Do not promote the candidate.

## Mission Type Gates

Safe/risky split:

- Requires at least one gateway candidate and one framed caution or high-whiplash candidate.
- Must ask whether risk was interesting, off-putting, or context-sensitive.

Album-world test:

- Requires album-world affinity evidence.
- Must avoid broad genre inference from a single album.

Route gateway mission:

- Requires gateway candidates and low route risk.
- Must state that gateway status is not listener preference.

Cross-family bridge mission:

- Requires clean bridge or explicit review bridge category.
- Must use product bridge readiness for sequencing.

Frontier probe:

- Requires an evidence gap and controlled exposure.
- Must keep fog state visible.

False-nearby trap test:

- Requires explicit false-nearby framing.
- Must identify what would prove the surface similarity is misleading.

One-object exception test:

- Requires narrow scope.
- Must prevent broad lane inference.

Context mission:

- Requires context overlays to remain explanatory, not intrinsic.
- Must ask whether the context mattered.

B/B+ shelf mission:

- Requires clear distinction between interest, durability, and core-role fit.
- Must not assign Landmark from a single positive response.

Modern discovery correction:

- Requires a stated correction hypothesis.
- Must use caution controls for novelty or overfamiliarity when present.

## Acceptance Gates

A v0.2 mission construction payload passes only if:

- The payload declares `contract_version: mission_construction_v0_2`.
- Every mission references `source_substrate_version: derived_affinity_substrate_v0_1_1`.
- `mission_type` is one of the approved affinity-derived mission planning patterns.
- Every mission has a testable hypothesis.
- Target affinity pattern, context overlays, risk/review metadata, listener evidence, and role assignment are separate.
- Candidate tracks, bridge candidates, frontier probes, gateway candidates, caution controls, and route items include sourced graph context.
- Gateway, bridge, frontier, caution, and quarantine sections are explicit.
- Identity quarantine and duplicate/version ambiguity are excluded from clean route sequencing.
- Route sequence includes inclusion reasons and test intent for every item.
- Route sequence includes intrinsic affinity tags, context overlays, graph context, confidence, and readiness notes for every item.
- Confirming, falsifying, and ambiguous evidence are stated.
- AtlasDelta plan uses `evidence_only` write mode.
- Runtime use and production mission use are explicitly blocked.
- Provenance states no canonical graph mutation and no runtime ingestion.
- No personal/private labels appear in values, filenames, comments, or examples.
