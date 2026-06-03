# Atlas Visualization Input Contract v0.2

Status: PM review contract design. Offline only.

## Purpose

Atlas Visualization Input Contract v0.2 defines how Atlas-facing review surfaces may consume Derived Affinity Substrate v0.1.1 candidate pools. It is a contract for shaping reviewable visualization inputs, not a rendering implementation and not runtime wiring.

The contract supports these Atlas surface types:

- Region
- Road
- Frontier
- Dead End
- Caution
- Gateway
- Landmark
- Waypoint
- Bridge
- Recent Learning

## Non-Goals

This contract does not:

- Mutate canonical graph truth.
- Change app runtime behavior.
- Infer listener preference from affinity similarity.
- Assign personal Atlas roles.
- Promote derived candidates into product truth.
- Render thousands of raw song nodes.
- Wire Atlas visualization.

## Source Inputs

Allowed source package:

- `derived_affinity_substrate_v0_1_1/`

Primary v0.1.1 files:

- `manifest_v0_1_1.json`
- `hardened_bridge_candidates_v0_1_1.json`
- `cross_family_bridge_edges_v0_1_1.json`
- `atlas_road_candidates_v0_1_1.json`
- `mission_candidate_pool_v0_1_1.json`
- `pm_review_packet_v0_1_1.md`

When Region, Frontier, or Dead End source pools rely on retained v0.1 lineage artifacts, a consumer must treat those pools as v0.1.1 lineage inputs and must apply the v0.1.1 hardening boundary before any Atlas-facing review surface is emitted.

No downstream builder may read canonical graph files as authority for this contract. Canonical graph identifiers may appear only as provenance already carried by the accepted substrate.

## Required Layer Separation

Every Atlas visualization input object must keep these layers separate:

- `intrinsic_affinity`: dominant tags, secondary tags, shared tag counts, intrinsic affinity score.
- `context_overlays`: context or membership overlays that explain use, not taste.
- `risk_review`: risk flags, review flags, quarantine status, bridge category, duplicate or identity ambiguity.
- `listener_evidence`: absent unless supplied later by an explicit evidence source outside the substrate.
- `role_assignment`: candidate-only by default; assigned roles require PM approval and, where personal, listener evidence.

The contract forbids a single blended score from replacing these layers.

## Visualization Envelope

Each Atlas-facing object must use this envelope:

```json
{
  "surface_id": "string",
  "surface_type": "Region|Road|Frontier|Dead End|Caution|Gateway|Landmark|Waypoint|Bridge|Recent Learning",
  "contract_version": "atlas_visualization_input_v0_2",
  "source_substrate_version": "derived_affinity_substrate_v0_1_1",
  "source_candidate_ids": [],
  "source_candidate_types": [],
  "intrinsic_affinity": {
    "dominant_tags": [],
    "secondary_tags": [],
    "shared_tags": [],
    "intrinsic_affinity_score": null,
    "score_components": {}
  },
  "context_overlays": [],
  "risk_review": {
    "risk_flags": [],
    "review_flags": [],
    "bridge_category": null,
    "quarantine_status": "none|review|identity_quarantine|not_applicable",
    "review_required": true
  },
  "readiness": {
    "product_bridge_readiness_score": null,
    "confidence": "low|medium|high",
    "fog_state": "clear|hazy|fogged|blocked",
    "readiness_notes": []
  },
  "listener_evidence": {
    "status": "absent|present|required_before_assignment",
    "evidence_ids": [],
    "not_inferred_from_affinity": true
  },
  "role_assignment": {
    "status": "candidate_only|not_assignable_from_substrate|assigned_after_review",
    "scope": "non_personal_review_candidate|requires_listener_evidence|blocked",
    "requires_pm_approval": true,
    "assigned_role": null
  },
  "display_policy": {
    "can_render_in_review": true,
    "can_render_in_product": false,
    "label": "string",
    "explanation": "string"
  },
  "provenance": {
    "source_files": [],
    "canonical_graph_mutation": "not_performed",
    "runtime_ingestion": "not_performed"
  }
}
```

## Surface Rules

Region:

- May consume family, archetype, or cluster rollups with coherent intrinsic affinity and sufficient sample size.
- Must show dominant affinity, secondary affinity, sample size, confidence, context overlays, risk flags, and fog state.
- Must remain a Region candidate until PM approval.
- Must not become a personal Region without listener evidence.

Road:

- May consume hardened v0.1.1 road candidates and clean bridge candidates.
- Must rank by `product_bridge_readiness_score`, not intrinsic affinity alone.
- Must preserve source edge counts, clean edge counts, review edge counts, and quarantine edge counts.
- Must not show identity quarantine or same-artist cross-family edges as clean Roads.

Frontier:

- May consume promising but under-evidenced candidate pools.
- Must use `fogged` or `hazy` fog state unless explicit listener evidence later clears it.
- Must state the missing evidence.
- Must not imply preference or safe expansion.

Dead End:

- May surface only as Dead End candidate from substrate risk/review evidence.
- Must not become a known Dead End without repeated listener evidence or PM-approved product evidence.
- Must show whether the evidence is risk-based, context-based, false-nearby-based, or listener-based.

Caution:

- May consume false-nearby, high-whiplash, context-dependent, duplicate, identity, or overfamiliar risk evidence.
- Must be visible in review and never silently filtered away.
- Must include framing requirements for any downstream route use.

Gateway:

- May consume route gateway candidates and gateway rollups.
- Must state that gateway status is an accessibility/routing signal, not a quality score.
- Must not become a Landmark without listener evidence.

Landmark:

- Not assignable from Derived Affinity Substrate v0.1.1 alone.
- Requires explicit listener evidence and PM-accepted role criteria.
- A v0.2 input may include a blocked Landmark placeholder only to show why a candidate cannot yet be assigned.

Waypoint:

- May be nominated as a useful but non-core review candidate.
- Requires scoped explanation, confidence, and risk state.
- Must not imply broad preference or durable personal role without evidence.

Bridge:

- Must include one v0.1.1 bridge category:
  - `clean_bridge_candidate`
  - `review_bridge_candidate`
  - `identity_quarantine`
  - `context_only_bridge`
  - `high_whiplash_bridge`
  - `false_nearby_bridge`
  - `mission_specific_bridge`
- Clean Bridge surfaces require `clean_bridge_candidate`.
- Review, caution, and quarantine Bridge surfaces must display the reason they are not clean.

Recent Learning:

- Not emitted from substrate alone.
- Requires a future AtlasDelta or listener evidence source.
- A v0.2 review input may include a blocked placeholder documenting that no recent learning is available.

## Readiness And Fog

Readiness must not collapse risk or listener evidence into affinity.

Recommended mapping:

- `clear`: high confidence, clean category, low review risk, no quarantine, and product readiness at or above `0.80`.
- `hazy`: medium confidence or review-required risk that does not block review rendering.
- `fogged`: promising but under-evidenced, frontier-like, context-dependent, or high-whiplash.
- `blocked`: identity quarantine, duplicate/version ambiguity, same-object concern, missing evidence for Landmark or Recent Learning, or runtime/product use attempted from substrate alone.

`intrinsic_affinity_score` measures technical tag similarity.

`product_bridge_readiness_score` measures whether the candidate is useful as an Atlas road, Bridge, route transition, or mission-supporting explanation after hardening penalties.

## Bridge Ranking Rules

Clean Road and Bridge rankings must:

- Include only `clean_bridge_candidate` edges unless the surface is explicitly labeled review or quarantine.
- Sort by `product_bridge_readiness_score` first.
- Use clean edge count and source confidence as tie-breakers.
- Preserve `intrinsic_affinity_score` separately for explanation.
- Penalize identity/version ambiguity, same-artist cross-family pairs, same-title or near-title pairs, context-only overlap, high-whiplash, false-nearby risk, and overfamiliarity when discovery value is weakened.

Review and quarantine rankings must:

- Keep high technical affinity visible.
- Make the review reason the first explanation, not a footnote.
- Never appear in clean top-Road or clean top-Bridge lists.

## Product Role Gates

Candidate surface output is allowed for PM review. Product role assignment is blocked unless all required gates pass.

- Region: PM approval required; listener evidence required for personal Region.
- Road: PM approval required; must use clean bridge readiness or explicit reviewed exception.
- Frontier: PM approval required; evidence gap must remain visible.
- Dead End: listener or PM-reviewed product evidence required before known Dead End assignment.
- Caution: may be review-visible; product use requires framing and approval.
- Gateway: may be review-visible; not a quality score.
- Landmark: listener evidence required.
- Waypoint: scoped review or listener evidence required.
- Bridge: clean or explicitly reviewed category required.
- Recent Learning: AtlasDelta or listener evidence required.

## Acceptance Gates

A v0.2 Atlas visualization input passes only if:

- The payload declares `contract_version: atlas_visualization_input_v0_2`.
- Every object references `source_substrate_version: derived_affinity_substrate_v0_1_1`.
- Intrinsic affinity, context overlays, risk/review metadata, listener evidence, and role assignment are separate fields.
- Listener evidence is absent or externally referenced; it is never inferred from affinity.
- Landmark and Recent Learning are blocked unless explicit evidence is present.
- Clean Road and clean Bridge surfaces exclude identity quarantine, duplicate/version ambiguity, same-object concern, and same-artist cross-family bridge contamination.
- Risk flags are preserved, including false-nearby and high-whiplash flags.
- Product readiness and intrinsic affinity are separate scores.
- Display policy distinguishes review rendering from product rendering.
- Provenance states no canonical graph mutation and no runtime ingestion.
- No personal/private labels appear in values, filenames, comments, or examples.
