# Waymark Mission Generation and Closed-Loop Learning PM Alpha Brief v0.1

## 1. Lane Purpose

This lane owns the product behavior that turns Atlas state into guided listening Missions, then turns Mission feedback back into useful Atlas learning.

The lane exists to prove and preserve the core Waymark promise:

```text
I know what you mean. Let’s try this route. I think this might hit because of X, but I’m not sure yet, so let’s test it.
```

A Mission is not a playlist. A Mission is a structured listening experiment with a hypothesis, ordered route logic, per-item expected signals, reaction-specific feedback chips, review semantics, and scoped possible Atlas updates.

For Alpha, this lane is responsible for whether Waymark can generate credible first listening routes from limited onboarding evidence and then visibly improve after user feedback.

## 2. Product Decisions Already Made

- Mission Generation creates hypotheses and probe routes, not promoted Atlas truth.
- Mission Review creates Signals and `PossibleAtlasUpdateCandidate` records, not automatic promotions.
- AtlasDelta is the required bridge between batch-one evidence and adaptive second-batch missions.
- Second-batch missions must reference `source_atlas_delta_refs`; plausible adjacency is not enough.
- `gpt-5.4-mini` is the current default mission-generation model candidate under bounded context.
- `gpt-5.5` remains a quality-ceiling fallback for harder synthesis lanes, especially WWTSF baseline/review, not default mission generation.
- Mission generation should consume digest/read-model context, not raw Atlas tables or hidden simulator truth.
- Candidate-constrained generation is the preferred path for beta/app-import-ready missions.
- Route items must be concrete searchable objects or explicit unresolved candidate-search slots.
- Unresolved candidate-search slots can be useful planning artifacts, but they block app-import readiness unless the mission is explicitly a search calibration mission.
- Positive reaction to trap items means bounded exception, cultural furniture, or reassess-dead-end semantics. It must not be forced into either broad approval or forced negative interpretation.
- `product_fail` can never be `app_import_ready`.

## 3. What Has Been Built, Proven, or Validated So Far

The lane has moved through several product proofs:

- Mission-generation harness v0.1 proved bounded context can produce structured mission objects rather than generic playlist sludge.
- Model matrix work showed `gpt-5.4-mini` is a credible default candidate when context, schema, and evaluator are strong.
- Context matrix work indicated candidate pools and digest quality materially affect false-nearby discipline and resolution quality.
- Atlas ingestion + digest proof showed Survey/Mission evidence can become Signals, role candidates, digest views, and mission-generation context without overpromotion.
- WWTSF substrate work proved AtlasDigestView + node interpretation can produce source material for downstream mission generation without returning to monolithic Profile Writer.
- Closed-loop first-batch simulation proved:
  - first mission batches can be generated for A3 profiles;
  - simulated listening feedback can be converted into Atlas-facing payloads;
  - hidden simulator provenance can stay out of Atlas;
  - Atlas update candidates and updated digests can be produced;
  - second mission batches can be generated from updated state.
- Adaptive second-batch contract v0.1 proved a stricter product bar:
  - second-batch missions can require `adaptation_action`;
  - every adaptive mission can cite AtlasDelta, Signals, and update candidates;
  - evaluator catches schema-valid but non-adaptive second batches;
  - live A3 run passed with all profiles `closed_loop_pass`.

Most recent live adaptive run:

- profiles: `profile_01_A3`, `profile_05_A3`, `profile_06_A3`
- model: `gpt-5.4-mini`
- adaptive evaluator: pass for all profiles
- visibly adaptive missions: `6/6` per profile
- total estimated mission-generation cost: about `$0.76`
- main remaining product friction: resolution/search placeholders still create `product_review_needed` missions for some profiles.

## 4. What This Lane Owns

This lane owns:

- Mission object product contract.
- Mission archetype and portfolio semantics.
- Mission route logic.
- Mission hypothesis quality.
- Per-item route functions and expected signal design.
- Feedback chip semantics as evidence collection, not just UI copy.
- Mission review readiness fields.
- Mission-scoped possible Atlas update candidate semantics.
- First-batch mission portfolio quality.
- Second-batch adaptive mission contract.
- AtlasDelta consumption requirements for adaptive generation.
- Mission-generation prompt contracts and evaluator criteria.
- Model-quality, cost, latency, and consistency evaluation for mission generation.
- Product status rules for mission outputs:
  - `product_fail`
  - `product_review_needed`
  - `product_pass_candidate`
  - `app_import_candidate`
- App-import readiness rules for mission JSON, in partnership with app and MusicKit lanes.

## 5. What This Lane Does Not Own

This lane does not own:

- Canonical graph identity, merge, composition, or family policy.
- Final canonical graph mutation.
- Survey UI/UX, survey card selection, or survey page-count strategy.
- Hidden fake-profile truth or simulator-private reaction corpora.
- Atlas persistence, final promotion/demotion policy, or Atlas Home visualization.
- Candidate Pool Builder ranking/scoring as a standalone product lane.
- Live MusicKit resolution implementation.
- iOS playback UX, export UI, or Mission Review interface design.
- Final user-facing WWTSF copy.
- Account system, sync, cloud backend, or multi-user infrastructure.

Unresolved boundary: Candidate Pool Builder is adjacent enough that this lane currently stubs or pressures it through candidate-constrained generation, but long-term ownership should separate route-design semantics from candidate-object selection.

## 6. Interfaces With Other PM Lanes

### Survey

Mission Generation consumes Survey output only after it becomes Atlas evidence or digest context. Survey should provide:

- user-visible Signals;
- familiarity state;
- selected and shown-unselected tags;
- user vocabulary candidates;
- provisional Atlas role/update behavior.

Mission Generation should not consume raw hidden survey truth.

### Atlas

Atlas is the main upstream/downstream partner.

Mission Generation consumes:

- `AtlasDigestView`;
- `MissionGenerationDigestView`;
- role assignments;
- taste feature states;
- vocabulary;
- anti-overfitting rules;
- unresolved questions;
- candidate-pool behavior cues;
- `AtlasDelta` for adaptive second batches.

Mission feedback returns:

- Signals;
- possible update candidates;
- confidence deltas;
- scope warnings;
- contradiction/dead-end/waypoint/frontier evidence;
- no automatic promotions.

### Candidate Pool Builder

Mission Generation needs concrete candidates with:

- music object refs;
- artist/title/album/year when known;
- Apple Music search hints;
- risk class;
- candidate role;
- expected feature hints;
- known trap/waypoint/frontier semantics.

Candidate Pool Builder needs Atlas role and behavior cues:

- anchor;
- bridge;
- probe;
- risky_probe;
- waypoint;
- trap;
- exclude;
- unknown.

### MusicKit / App

The app needs mission JSON that can be imported, displayed, resolved, played, reacted to, and exported.

Mission Generation must distinguish:

- beta/app-import-ready concrete route items;
- review-needed items;
- unresolved candidate-search slots;
- search-calibration-only missions.

### WWTSF / User-Facing Copy

WWTSF can provide source material and first mission hints. Mission Generation may consume WWTSF substrate, but must not treat WWTSF as final copy or promoted truth.

### Evaluation / QA

This lane depends on deterministic evaluators that check product structure, not just schema validity. LLM-as-judge may come later, but Alpha should not rely on it as the only quality gate.

## 7. Current Product Assumptions

- Trusted Alpha can tolerate some manual review, but cannot tolerate invisible overclaiming.
- A first batch does not need perfect taste understanding; it must be credible, varied, explainable, safe enough, and instrumented to learn.
- Batch two must be visibly smarter than batch one.
- The strongest product architecture is likely:

```text
Atlas digest
+ Taste Feature Registry
+ Candidate Pool
+ Structured schema
+ Evaluator / repair loop
+ Model routing
```

- Raw model intelligence is not the taste brain. The model is the mission designer inside bounded context.
- Smaller models can be viable when the substrate is strong and the evaluator is strict.
- Cost matters, but product safety and evidence quality matter more before Alpha.
- Human/concierge review is acceptable for trusted Alpha if the review boundary is explicit.

## 8. Open Questions to Resolve Before Alpha

- What is the minimum accepted mission portfolio for a trusted Alpha user: one mission, three missions, or six-mission first batch?
- Does Alpha require adaptive second batch in-app, or can it be concierge-generated after exported feedback?
- What degree of unresolved candidate-search is acceptable in Alpha missions?
- Who owns final Candidate Pool Builder quality and resolution fallback?
- What is the threshold for `app_import_candidate` versus `product_pass_candidate`?
- How much of Mission Review feedback must be captured through chips versus freeform notes?
- Should Alpha expose “why this mission now” and “what Waymark is not doing anymore” to users, or keep some of that in reviewer/Atlas-facing copy?
- What is the first Alpha policy for Atlas promotion after mission feedback: all manual, semi-automated candidate creation, or limited deterministic promotion?
- How many misses/skips/no-signals should pause a path in Alpha?
- Does the app need to show user-facing mission learning immediately, or is exported review enough?
- How should mission generation behave when Apple Music resolution fails after mission creation?

## 9. Risks and Failure Modes

Major risks:

- Mission outputs look polished but are just playlists.
- Model generates plausible adjacent recommendations without strong evidence design.
- Second batch is “more stuff” rather than visibly caused by Atlas changes.
- Generated hypotheses are mistaken for learned evidence.
- Mission Review accidentally promotes Atlas truth.
- Waypoints are inflated into Landmarks.
- One-object exceptions are generalized into lanes or genres.
- Known Dead Ends are ignored or softened too much.
- Trap items are handled with forced negative semantics instead of exception/reassessment semantics.
- Candidate-search placeholders slip into app-ready missions.
- MusicKit search fails or resolves to wrong versions.
- Feedback chips are charming but structurally useless.
- Generic chips are over-penalized before the system has enough personal vocabulary.
- Hidden simulator/private truth leaks into production-facing Signals.
- The app captures reactions but not enough context for Atlas learning.

False-nearby risks remain especially important:

- Muse must not imply generic prog-metal or Tool/APC-style seriousness.
- Type O Negative must not imply broad gothic metal.
- LCD Soundsystem must not imply generic dance-punk.
- The Decemberists must not imply generic indie-folk.
- Taylor Swift must not imply generic pop appetite.
- Jimmy Eat World must not imply broad emo/pop-punk approval.
- QOTSA/Kyuss are useful shelves, not core canon by default.
- Current rock must avoid fake-hard, scene-posture, and post-grunge slop traps.

## 10. Alpha-Readiness View From This Lane

This lane is Alpha-promising but not fully Alpha-ready.

Green lights:

- The closed loop works in synthetic form.
- Mission schema and evaluator infrastructure exist.
- Model routing hypothesis is credible.
- `gpt-5.4-mini` can generate valid, useful mission objects under bounded context.
- Adaptive second-batch contract now forces visible learning from AtlasDelta.
- Hidden simulator truth can be excluded from Atlas-facing evidence.
- Product status can distinguish schema validity from product readiness.

Yellow lights:

- Candidate object selection and resolution quality remain the largest Alpha blocker.
- Some adaptive missions still land as `product_review_needed` due to unresolved/search-calibration placeholders.
- Mission generation can follow contract, but only when the context packet makes refs and obligations explicit.
- The app-facing mission schema may need reconciliation with the richer AI harness schema.

Red line:

- Do not allow trusted Alpha to import missions where route items are pseudo-playable placeholders.

## 11. What Can Be Manual / Concierge for Trusted Alpha

Trusted Alpha can manually support:

- Mission generation review before import.
- Candidate pool curation.
- Apple Music search/version correction.
- App-import gating.
- Mission batch selection and ordering.
- Atlas promotion/demotion review.
- WWTSF copy polishing.
- Resolving unclear no-signal/skipped interpretations.
- Repairing route items that are musically right but catalog-ambiguous.
- Running model/evaluator harnesses outside the app.
- Producing second-batch missions after exported reaction sessions.

This is not product failure. Concierge review is a sane Alpha bridge as long as the user experience remains coherent and the data exported from the app is real.

## 12. What Likely Must Be Real / In-App for Trusted Alpha

Trusted Alpha likely needs real in-app:

- Mission loading.
- Mission detail display.
- Apple Music authorization.
- At least partial Apple Music search/resolution.
- Playback of resolved items.
- Per-item primary reactions.
- Sparse secondary tag/chip selection.
- Notes or lightweight field notes.
- Skip/no-signal capture where possible.
- Export of reaction session JSON and readable Markdown.
- Stable mission item IDs that can round-trip into Atlas Signals.
- Clear separation between user-visible feedback and any private/evaluator-only data.

The app does not need to generate missions locally for Alpha. It does need to execute missions and produce trustworthy evidence.

## 13. Recommended Constraints or Guardrails

- Require every Mission to have a hypothesis, route logic, expected signals, and completion criteria.
- Require every route item to be concrete or explicitly unresolved.
- Block app import for unresolved placeholders unless the mission is explicitly a search calibration mission.
- Require all mission-scoped Atlas updates to be conditional and review-gated.
- Require risky, trap, frontier, contradiction, and unresolved items to default to review-needed.
- Require second-batch missions to reference `source_atlas_delta_refs`.
- Require second-batch missions to state:
  - what batch one taught;
  - what changed;
  - what Waymark is not doing anymore;
  - success/failure/no-signal interpretations;
  - expected next Atlas update.
- Keep `signal_strength` separate from `interpretation_confidence`.
- Treat no-signal/skips as behavior, not automatic dislike.
- Keep hidden simulator artifacts out of Atlas-facing payloads.
- Keep Product Review as a first-class gate separate from JSON Schema validation.
- Keep `gpt-5.5` available for fallback/adjudication, but do not spend it by default on routine mission generation.

## 14. Dispatches or Dependencies Needed From Other PMs

Needed from Survey PM:

- Final Survey Output Contract for Alpha.
- Reaction normalization map from survey labels to Atlas/Mission/App labels.
- Policy for shown-but-unselected survey tags.
- Clear split between visible survey evidence and simulator-private hidden truth.

Needed from Atlas PM:

- Alpha promotion/review policy.
- Stable `AtlasDelta` contract for production-like mission feedback.
- MissionGenerationDigestView acceptance criteria.
- Atlas UI/read model expectations for recent learning.

Needed from Candidate Pool PM:

- Candidate Pool Contract v0.1.
- Candidate role taxonomy and required fields.
- Resolution status semantics.
- Trap/waypoint/dead-end handling rules.
- Fallback behavior when a route need has no concrete candidate.

Needed from App / MusicKit PM:

- App-import mission schema reconciliation.
- Route item resolution requirements.
- Reaction session export contract.
- Minimum viable Mission Review UI for Alpha.
- Handling of unresolved, unavailable, wrong-version, or ambiguous Apple Music matches.

Needed from WWTSF / Copy PM:

- Boundary between WWTSF substrate, mission explanation text, and final user-facing copy.
- Decision on whether “what Waymark is not doing anymore” appears in Alpha UI.
- Voice guidelines for mission hypotheses and learning summaries.

## Alpha Recommendation From This Lane

Proceed toward trusted Alpha with mission generation as a reviewed/concierge-backed system, not a fully autonomous in-app generator.

The lane is ready to support Alpha planning if the unified plan accepts these constraints:

- mission generation remains server/harness/concierge-driven for Alpha;
- app captures real listening evidence;
- candidate resolution gets a hard gate before import;
- Atlas updates remain possible/reviewed, not automatic;
- second-batch adaptivity requires AtlasDelta references;
- product-review status remains separate from schema validity.

The core product loop is now plausible. The remaining Alpha question is less “can Waymark generate missions?” and more “can we reliably feed it concrete candidates and capture enough real feedback to make the next mission obviously smarter?”
