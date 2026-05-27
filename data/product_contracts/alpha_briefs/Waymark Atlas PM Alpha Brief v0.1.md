# Waymark Atlas PM Alpha Brief v0.1

## 1. Lane Purpose

The Atlas lane owns Waymark's user-specific interpretation layer: the living map of what Waymark thinks it has learned about a listener, what remains uncertain, and what should be tested next.

Atlas is not the canonical music graph. The canonical graph is the shared music-object substrate. Atlas is the personal layer above it: Signals, nodes, provisional roles, update candidates, digest views, deltas, evidence refs, confidence, scope, and review state.

For Alpha, Atlas must make the rest of Waymark feel coherent:

```text
The user gave evidence.
Waymark interpreted it cautiously.
Waymark can explain what it thinks, what it does not know, and why the next route exists.
```

The Alpha product goal is not a complete map. It is a trustworthy starter Atlas that can support Survey completion, WWTSF-style explanation, first missions, mission review, second-batch adaptation, evidence audit, and future correction without pretending provisional evidence is final truth.

## 2. Product Decisions Already Made

- Canonical graph equals shared music-object substrate; Atlas equals user-specific interpretation layer.
- Atlas records may reference canonical graph objects, but Atlas must also support user-local, external-catalog, unresolved, and composition-placeholder objects.
- Survey, Mission Generation, Mission Review, Candidate Pool Builder, and Atlas UI must not create, update, merge, or delete canonical graph entities.
- `AtlasNode` represents the thing. It does not own authoritative role truth.
- `AtlasRoleAssignment` owns user-specific role truth.
- UI role chips should derive from `AtlasRoleAssignment`, not `AtlasNode`.
- Survey writes Signals, provisional role assignments, and possible update candidates, not promoted Landmarks, Regions, Frontiers, Dead Ends, or Waypoints.
- Mission Generation writes hypotheses and digest-consumable suggestions, not promoted Atlas facts.
- Mission Review writes Signals and `PossibleAtlasUpdateCandidate` records, not automatic promotions.
- `Road` is a route or grouping structure, not an Atlas role.
- `Lineage` is represented through edge/network views, not an Atlas role.
- Lifecycle fields stay separate:
  - `status`
  - `review_state`
  - `promotion_state`
- `signal_strength` and `interpretation_confidence` stay separate.
- Apple Music evidence is exposure/import/familiarity context, not taste truth.
- `dont_know_enough` and familiarity uncertainty must not become negative taste evidence.
- Negative reactions must be scoped to the smallest justified object and should create dead-end hypotheses or contradiction checks, not blanket genre rejection.
- `AtlasDigestView` is the preferred downstream read surface for WWTSF, Mission Generation, Candidate Pool Builder, later node interpretation, evidence audit, and correction.
- `AtlasDelta` is the canonical "what changed?" object between one Atlas state and the next. It summarizes learning; it is not promoted Atlas truth.

## 3. What Has Been Built, Proven, or Validated So Far

The lane has proven the core substrate shape across several slices.

The Atlas Schema Contract v0.1 defines the user-interpretation layer, including:

- typed `music_object_ref`;
- `AtlasNode`;
- `AtlasRoleAssignment`;
- `Signal`;
- `PossibleAtlasUpdateCandidate`;
- `AtlasDigestView`;
- user taste feature and vocabulary records;
- lifecycle and confidence fields;
- examples for Landmark, Region, Frontier, Dead End, Waypoint, Signal, Taste Feature, Survey-seeded update, and Mission Review update.

The A3 Survey ingestion proof validated this flow for profiles 01, 05, and 06:

```text
Survey raw payload
-> Signal
-> AtlasNode
-> provisional AtlasRoleAssignment
-> PossibleAtlasUpdateCandidate
-> AtlasDigestView
-> slim node-interpretation packet
```

The v0.1.1 repair cleared the main PM blockers:

- slim node packets were materially smaller than raw survey payloads;
- role assignment became density-aware rather than direct reaction mapping;
- selected and shown-unselected tags were validated with a tag-bearing fixture;
- LLM-facing packets were stripped of survey construction internals;
- no promoted Survey roles were created;
- no role truth was stored on `AtlasNode`;
- no canonical graph mutation path existed.

Survey Evidence Export v0.1 established the cleaner Survey-to-Atlas contract:

- append-only evidence atoms;
- visible survey evidence only;
- private/simulator/Profile Writer/page-construction internals excluded;
- Apple exposure marked as exposure prior only;
- response references validated inside the visible export.

The Survey Evidence Export ingestion proof generated per-profile Atlas deliverables for the available profile 01 export:

- `validation_report.json`;
- `signals.jsonl`;
- `atlas_nodes.json`;
- `atlas_role_assignments.json`;
- `possible_atlas_update_candidates.json`;
- `atlas_digest_view.json`;
- `size_report.md`;
- RFI notes for schema mismatches.

The node-interpretation smoke test showed all three slim A3 packets could be interpreted as structured Atlas substrate without raw payloads, Profile Writer output, hidden fake-profile truth, promotion, canonical graph mutation, final WWTSF copy, or mission generation.

The WWTSF substrate run showed `AtlasDigestView` plus node interpretation can produce structured explanation source material without returning to raw Survey payloads. Those outputs are explicitly source substrate, not final user-facing copy.

The mission-generation smoke run showed missions can be generated from Atlas substrate, but also exposed a key Alpha constraint: schema-valid missions can still include unresolved route placeholders that are not app-import-ready.

The closed-loop simulation showed that mission feedback can return as Signals, update candidates, confidence deltas, updated digests, and AtlasDelta records; second-batch missions can then cite the resulting deltas and adapt visibly.

## 4. What This Lane Owns

Atlas owns:

- user-specific music interpretation state;
- Atlas schema semantics;
- Atlas record contracts;
- typed music-object reference requirements for user interpretation;
- `Signal` semantics and evidence auditability;
- `AtlasNode` semantics as thing-only records;
- `AtlasRoleAssignment` semantics as authoritative user role truth;
- provisional role policy and promotion-state boundaries;
- `PossibleAtlasUpdateCandidate` semantics;
- digest views for downstream consumers;
- `AtlasDelta` semantics for "what changed";
- confidence, scope, lifecycle, and review-state semantics;
- anti-overfitting rules attached to Atlas read models;
- unresolved-question and contradiction representation;
- user taste feature state and vocabulary substrate;
- read surfaces that support WWTSF, Mission Generation, Candidate Pool Builder, Atlas Home, and correction.

Atlas also owns the product discipline that keeps evidence, interpretation, explanation, and promotion separate.

## 5. What This Lane Does Not Own

Atlas does not own:

- canonical graph entity identity, merge, normalization, family policy, or composition policy;
- Survey UI, Survey page construction, page-count strategy, or candidate display mechanics;
- hidden fake-profile truth, simulator-private reaction corpora, or evaluation-only artifacts;
- final WWTSF prose voice;
- final mission generation strategy, mission portfolio design, or route-item copy;
- Candidate Pool Builder ranking, routing behavior, or concrete item selection as a standalone product system;
- MusicKit resolution, playback, or app-import behavior;
- iOS reaction UX, mission execution UI, export UI, or Atlas Home interface design;
- account, sync, privacy infrastructure, or multi-user data architecture;
- automatic promotion/demotion policy beyond defining the record states and guardrails.

Unresolved boundary: Candidate Pool Builder needs Atlas roles and candidate-pool hints, but the mapping from Atlas role to routing behavior should not live on `AtlasNode`. Ownership should remain split: Atlas owns what a node means for a user; Candidate Pool owns how that meaning becomes route selection behavior.

Unresolved boundary: WWTSF needs Atlas summary inputs, but final user-facing language should not become Atlas truth. Ownership of final wording, tone, and surface placement belongs to WWTSF/App, with Atlas preserving evidence and scope.

Unresolved boundary: friendly Region names and graph/family explanations may require Canonical Graph labels, Atlas synthesis, or WWTSF rendering. Alpha needs an explicit owner for naming when graph dictionaries are unavailable.

## 6. Interfaces With Other PM Lanes

### Survey

Survey should provide visible, append-only evidence atoms through Survey Evidence Export. Atlas consumes only the ingestable evidence ledger, not page construction state, raw ranking scores, hidden simulator truth, or Profile Writer prose.

Atlas expects Survey evidence to include:

- reaction and normalized reaction operation;
- selected tags and shown-unselected tags;
- note text when present;
- typed `music_object_ref`;
- page intent and comparison context;
- Apple exposure context;
- visible provenance refs.

Atlas returns starter state, contradictions, unresolved questions, and digest views that Survey can use for follow-up calibration decisions, as long as Survey does not treat them as canonical graph edits.

### Canonical Graph

Atlas references canonical graph objects when available. It does not mutate them.

Atlas needs stable canonical IDs and clear policy for:

- artist, album, and song recording refs;
- composition placeholders;
- canonical vs display-credit identity;
- family/archetype refs and whether labels are available;
- unresolved or external-catalog object resolution.

### WWTSF / Copy

WWTSF should consume `AtlasDigestView`, interpreted update candidates, selected Signal summaries, user vocabulary terms, anti-overfitting rules, and later `AtlasDelta`.

WWTSF should not consume raw Survey payload as its primary source. WWTSF outputs are explanation source material until explicitly rendered and reviewed as final user copy.

### Mission Generation

Mission Generation should consume `AtlasDigestView`, `AtlasDelta`, candidate role summaries, unresolved questions, anti-overfitting rules, and candidate-pool behavior hints.

Mission Generation should return hypotheses, mission hints, and mission-scoped update candidates. It must not promote Atlas facts.

### Mission Review / Closed Loop

Mission Review sends new Signals, possible update candidates, confidence deltas, contradiction evidence, dead-end checks, waypoint evidence, and review recommendations back to Atlas.

Atlas summarizes the change through updated digests and `AtlasDelta`; it does not automatically promote the reviewed outcome unless a separate promotion policy acts.

### Candidate Pool Builder

Candidate Pool Builder should consume `AtlasRoleAssignment` and `AtlasDigestView`, not raw `AtlasNode` role-like summaries.

Atlas may provide behavior hints such as:

- `anchor`;
- `bridge`;
- `probe`;
- `risky_probe`;
- `waypoint`;
- `trap`;
- `exclude`;
- `unknown`.

Those hints are downstream routing aids, not authoritative Atlas roles.

### App / Atlas UI

Atlas UI should render role chips, confidence, scope, review state, and evidence links from Atlas records, not from inferred node labels.

For Alpha, App likely needs enough Atlas state to show what Waymark learned, why a path is being tested, and how the user can correct it. It does not need the full graph visualization to be product-useful.

## 7. Current Product Assumptions

- Trusted Alpha users can tolerate provisional language if it is useful, specific, and honest.
- A starter Atlas can be valuable without final promotion policy automation.
- The product should privilege auditable uncertainty over confident but ungrounded taste claims.
- Users will trust Waymark more if it says "this is a candidate Frontier" or "this needs a mission test" instead of overstating first-pass evidence.
- `AtlasDigestView` can be the main read surface for WWTSF, first missions, second missions, evidence audit, and future correction.
- `AtlasDelta` can power "What Waymark Learned" moments after Survey or Mission completion.
- Apple Music history is useful for exposure and familiarity, but explicit user reaction remains the stronger taste signal.
- Unknown/familiarity uncertainty is a valuable routing signal, not a dislike.
- Density-aware role assignment is directionally correct but still provisional.
- Manual review is acceptable in trusted Alpha for promotion, naming, contradiction adjudication, and mission readiness.
- The first Alpha does not need a complete Atlas Home if the user can see credible learning and route explanations in the right moments.

## 8. Open Questions to Resolve Before Alpha

- What is the first Alpha promotion policy for moving `candidate` role assignments to `promoted`, if any?
- Which Atlas facts can be user-visible as provisional, and which should remain reviewer/internal until stronger evidence exists?
- What is the minimum useful Atlas Home surface for Alpha: recent learning only, starter map cards, route rationale, correction queue, or all of these?
- Who owns friendly names for Regions, scenes, and taste features when canonical graph labels are unavailable?
- How should users correct Atlas state in Alpha: direct edits, thumbs-down on explanations, mission review chips, concierge review, or all of these?
- What evidence recurrence is required before Atlas can safely call something a Landmark or Region?
- How many contradictory or negative Signals should pause a path, create a dead-end hypothesis, or block promotion?
- How should Atlas represent "one-object exception" versus broader lane appetite in user-facing copy?
- How much of `AtlasDelta` should appear in-app versus staying as substrate for WWTSF/Mission Generation?
- What is the first privacy/deletion policy for Signals, notes, Apple exposure context, and generated interpretations?
- How should non-canonical user-local and external-catalog objects resolve over time without rewriting historical evidence?
- What is the product stance when Atlas has enough evidence for a good mission but not enough evidence for a confident explanation?

## 9. Risks and Failure Modes

Major risks:

- Survey evidence gets mistaken for final Atlas truth.
- `AtlasNode` quietly regains role truth through denormalized shortcuts.
- Role chips drift away from `AtlasRoleAssignment`.
- One Love becomes an automatic Landmark.
- Positive isolated evidence is not distinguished from dense positive territory.
- Negative evidence broadens into genre rejection.
- `dont_know_enough` gets interpreted as dislike.
- Apple exposure gets treated as taste truth.
- Mission-generated hypotheses auto-promote into Atlas facts.
- WWTSF bullets read like final user truth even though they are substrate.
- Contradictions become confident claims instead of review/test recommendations.
- Road and Lineage semantics blur back into role enums.
- AtlasDigestView grows into a raw-payload dump and loses its product value.
- Debug/provenance or construction internals leak into LLM-facing packets or user-facing copy.
- Candidate Pool Builder consumes node labels and bypasses role assignments.
- AtlasDelta becomes narrative copy instead of deterministic change summary.
- The UI shows too much ontology and not enough useful learning.
- Manual review hides gaps that later become product trust failures.

False-nearby risk is especially important for Alpha. Atlas must keep scope tight enough to avoid turning one reference into a fake lane, fake genre, or fake personality claim.

## 10. Alpha-Readiness View From This Lane

Atlas is ready to support trusted Alpha planning as a guarded substrate.

Green lights:

- The core schema boundary is clear.
- The Survey-to-Atlas ingestion architecture is proven on representative A3 profiles and a Survey Evidence Export sample.
- Digest views are sufficient for downstream proof slices without returning to full raw Survey payloads.
- Node interpretation can run from slim packets only.
- WWTSF substrate can consume Atlas read models instead of raw Survey payloads.
- Mission Generation can consume Atlas substrate.
- Closed-loop feedback can return to Atlas and produce updated digests and deltas.
- Core invariants have held across proofs: no canonical graph mutation, no Survey promotion, no role truth on `AtlasNode`.

Yellow lights:

- Role policy is still provisional and needs more real, tag-bearing data.
- Promotion/demotion policy is intentionally unresolved.
- Region naming and graph-label availability need ownership clarity.
- Survey Evidence Export currently has one available sample; profiles 05 and 06 exports are expected but not yet present in the same contract form.
- Atlas UI expectations are not yet reduced to a trusted Alpha minimum.
- The product has not yet proven live user correction against Atlas state.

Red lines:

- Do not let Alpha promote Survey-created or mission-generated Atlas roles automatically.
- Do not let any downstream consumer mutate canonical graph state through Atlas.
- Do not show generated interpretation as confirmed user truth.

## 11. What Can Be Manual / Concierge for Trusted Alpha

Trusted Alpha can rely on manual or concierge support for:

- role promotion and demotion review;
- contradiction adjudication;
- friendly Region or taste-feature naming;
- graph ID resolution for unresolved/user-local/external objects;
- deciding whether a candidate Landmark is visible enough to show;
- reviewing WWTSF source bullets before final user copy;
- reviewing first and second mission batches before app import;
- determining whether an AtlasDelta should be user-facing;
- interpreting sparse notes or ambiguous reactions;
- repairing weird object-scope edge cases;
- recovering from false-nearby recommendations;
- maintaining a PM review log of why Atlas truth did or did not change.

This is acceptable for trusted Alpha if the product boundary is explicit: concierge review may approve what the app shows, but it should not erase the evidence trail or bypass Atlas lifecycle fields.

## 12. What Likely Must Be Real / In-App for Trusted Alpha

Trusted Alpha likely needs real in-app or production-like behavior for:

- capturing user-visible Signals from Survey and Mission Review;
- preserving Signal provenance and evidence refs;
- maintaining separate `status`, `review_state`, and `promotion_state`;
- deriving role chips from `AtlasRoleAssignment`;
- preserving selected tags separately from shown-unselected tags;
- preserving Apple exposure as context only;
- producing or consuming `AtlasDigestView` for explanation and mission generation;
- showing at least a lightweight "what Waymark learned" state after meaningful evidence;
- carrying correction intent back into Atlas as evidence or review state;
- ensuring downstream model packets exclude raw debug/construction internals;
- preventing canonical graph mutation;
- exporting enough evidence for PM audit and future correction.

The app does not need a full Atlas graph visualization for trusted Alpha. It does need the learning loop to feel real, grounded, and correctable.

## 13. Recommended Constraints or Guardrails

- Treat all Survey-created roles as provisional or candidate-level.
- Require explicit review before any promoted Landmark, Region, Frontier, Dead End, or Waypoint becomes durable user truth.
- Keep direct reaction-to-role mapping as fallback only; density-aware interpretation should remain the default direction.
- Require role policy to consider reaction strength, object scope, local positive density, local negative density, unknown density, recurrence, graph adjacency, Apple exposure, page intent, comparison context, and contradictions.
- Keep `AtlasNode` role-free.
- Require all Signals to trace to user-visible survey, mission, note, reaction, tag, skip, playback, import, or review events.
- Keep `signal_strength` separate from `interpretation_confidence`.
- Treat Apple Music evidence as exposure/import/familiarity context only.
- Treat `dont_know_enough` and no-signal behavior as uncertainty unless later evidence says otherwise.
- Scope negative evidence narrowly.
- Treat contradictions as test/review recommendations.
- Keep `Road` and `Lineage` out of the role enum.
- Keep WWTSF bullets and AtlasDelta user-facing inputs marked as source material until final copy rendering.
- Prevent raw Survey payloads, construction internals, debug provenance, hidden simulator truth, Profile Writer prose, and unavailable graph meanings from entering LLM-facing Atlas packets.
- Require Candidate Pool Builder to consume role assignments and digest hints rather than node-level role summaries.
- Preserve evidence refs on `PossibleAtlasUpdateCandidate` and `AtlasDelta`.
- If graph/family/archetype labels are unavailable, do not invent them.

## 14. Dispatches or Dependencies Needed From Other PMs

Needed from Survey PM:

- Survey Evidence Export samples for profiles 05 and 06 in the v0.1 contract shape.
- More tag-bearing real or realistic survey fixtures.
- Final Alpha reaction normalization map.
- Clear policy for shown-but-unselected tags.
- Confirmation that Survey production export excludes construction/debug/private fields.

Needed from Canonical Graph PM:

- Stable canonical object ID policy for Alpha.
- Composition-placeholder and recording-first handoff policy.
- Family/archetype dictionary availability rules.
- Resolution policy for user-local, external-catalog, unresolved, and composition-placeholder refs.
- Clear boundary for when an Atlas unresolved object should become a canonical graph candidate, without Atlas mutating the graph directly.

Needed from Mission Generation PM:

- Confirmation that mission inputs consume `AtlasDigestView` and `AtlasDelta`, not raw Survey payloads.
- Agreement that mission feedback returns Signals and update candidates, not promotions.
- Candidate-pool behavior mapping that remains downstream of Atlas roles.
- Concrete route-item requirements for app import.

Needed from WWTSF / Copy PM:

- Final boundary between WWTSF substrate, WWTSF rendered copy, Atlas Home copy, and Mission explanation copy.
- Voice rules for provisionality, confidence, scope, contradictions, and "what changed."
- Decision on where `AtlasDelta.user_facing_summary_inputs` appears in the Alpha experience.

Needed from App / Atlas UI PM:

- Minimum Atlas-visible surface for trusted Alpha.
- Role chip rendering rules sourced from `AtlasRoleAssignment`.
- Confidence/scope visualization requirements.
- Correction affordance policy.
- Evidence audit/debug access expectations for PM review versus user view.

Needed from Privacy / Data PM:

- Retention and deletion policy for Signals, notes, Apple exposure context, Atlas interpretations, model packets, and deltas.
- Policy for separating production user evidence from simulator-private/evaluator artifacts.

## Alpha Recommendation From This Lane

Proceed toward trusted Alpha with Atlas as a guarded, auditable interpretation substrate, not a fully autonomous truth engine.

Atlas is ready to support Alpha planning if the unified plan accepts these constraints:

- Survey and Mission evidence create Signals, candidates, digests, and deltas;
- promotion stays reviewed/manual until a separate policy is accepted;
- WWTSF and Mission Generation consume Atlas read models instead of raw Survey payloads;
- Candidate Pool Builder respects role-assignment boundaries;
- user-facing copy preserves uncertainty, scope, and evidence-backed humility;
- canonical graph mutation remains outside Atlas.

The Alpha product question is no longer whether Atlas can represent starter learning. It can. The real question is how much of that learning should be shown, reviewed, corrected, and acted on during the first trusted user loop.

## Primary Controlling Inputs

- `data/atlas_schema/atlas_schema_contract_v0_1.md`
- `data/product_contracts/atlas_schema_build_brief.md`
- `data/product_contracts/cross_team_consistency_review.md`
- `data/survey_simulation/survey_evidence_export/survey_evidence_export_v0_1.md`
- `data/atlas_schema/ingestion_proof/a3_gpt_5_5_3x3/a3_ingestion_acceptance_report.md`
- `data/atlas_schema/ingestion_proof/survey_to_atlas_digest_v0_1/README.md`
- `data/atlas_schema/node_interpretation_smoke/a3_v0_1_1/a3_node_interpretation_smoke_report_v0_1_1.md`
- `data/atlas_schema/wwtsf_substrate_smoke/a3_v0_1_2/wwtsf_substrate_smoke_report_v0_1_2.md`
- `data/mission_generation/atlas_substrate_a3_v0_1_2/mission_generation_repair_brief_v0_1_3.md`
- `data/closed_loop_simulation/a3_first_batch_learning_v0_1_adaptive_contract_v0_1/closed_loop_acceptance_report.md`
- `data/atlas_schema/atlas_delta_v0_1.md`
- `docs/app_dev/kickoff_v0_2/Music_Atlas_Controller_Product_Brief_v0_2.md`
