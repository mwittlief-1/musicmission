# Waymark Survey Intelligence PM Alpha Brief v0.1

Generated: 2026-05-21

Lane: Survey Intelligence / Survey Evidence

Controlling inputs:

- Current Waymark product principle: Survey gathers evidence; Atlas decides meaning; Mission tests hypotheses.
- Product contracts under `data/product_contracts/`
- Canonical graph staging outputs and warnings under `data/canonical_graph/`
- Survey simulation harness outputs under `data/survey_simulation/`
- Survey Evidence Export v0.1 contract under `data/survey_simulation/survey_evidence_export/`
- Recent PM decisions in this thread: Apple as exposure prior, hidden data separation, active survey selection, append-only Survey-to-Atlas evidence ledger.

## 1. Lane Purpose

The Survey Intelligence lane owns Waymark's onboarding evidence-gathering product surface.

Its purpose is to ask a small number of high-signal music questions that help Waymark establish a user's starting territory without pretending that the survey has already built the user's Atlas.

The lane is not a recommender. It is not a generic music quiz. It is a calibrated evidence collection layer that uses:

- Apple-derived exposure priors
- canonical graph structure
- visible user responses
- object type roles for artists, albums, and songs
- response semantics that preserve uncertainty

The Survey lane should answer:

- What does this user likely know?
- What responses are strong enough to become evidence?
- What should remain scoped to artist, album, song, context, or familiarity?
- What evidence can be safely passed to Atlas?
- What remains unresolved or construction-only?

## 2. Product Decisions Already Made

- Survey selection should maximize useful taste information, not likely likes.
- Apple Music data is exposure evidence, not taste truth.
- Apple-biased Page 1 prioritizes payload overrepresentation and likely-known anchors, while preserving diversity and boundary checks.
- Early survey pages should be signal-dense. `dont_know_enough` is useful only when intentionally testing a boundary or frontier.
- `dont_know_enough` means familiarity uncertainty, not negative preference.
- `ok` means waypoint/context/familiarity evidence, not landmark-level preference.
- `dont_like` is a scoped negative signal, not a genre-wide dead end.
- User responses should stay attached to the smallest justified object.
- Survey may propose evidence, but Atlas owns final interpretation, confidence, role assignment, and promotion state.
- Survey must not mutate canonical graph data.
- Survey Builder and prediction inputs must not receive hidden fake-profile data, hidden corpus reactions, hidden reason tags, or simulator lookup state.
- Survey Evidence Export v0.1 is the normalized append-only evidence ledger from Survey to Atlas.
- `evidence_strength_hint` is Survey-side basis metadata only. It is not final Atlas confidence.
- Every Atlas-ingestable response reference must resolve to a visible response in the same Survey Evidence Export.

## 3. Built, Proven, or Validated So Far

The current harness proves the Survey lane can operate against the staging canonical graph with clear boundaries.

Built and validated:

- `data/survey_simulation/` structure with fake profiles, Apple payloads, hidden corpora, runs, schemas, validators, reports.
- 10 fake profiles with mixed archetype seeds, context lanes, false-nearby lanes, anti-affinities, and simulated Apple payloads.
- Realistic hidden reaction corpora populated by profile tier, object popularity, Apple presence, false-nearby/anti-affinity, and control sampling.
- 20 Page 1 runs:
  - 10 graph-only
  - 10 Apple-biased
  - 12 tiles per page
- Active Page 1 selection:
  - payload signature artists
  - archetype confirmation anchors
  - multi-archetype junctions
  - false-nearby or boundary checks
  - mass-popular controls
  - broad coverage sentinels
- Artist Page 2 generation for all 20 runs using visible Page 1 responses only.
- Album Page 1 and Song Page 1 candidate handoff files.
- Hidden leakage validators for visible artifacts.
- Canonical graph read-only fingerprint checks.
- Page-count backtest across 18 configurations:
  - artist pages: 2, 3, 4
  - album pages: 1, 2
  - song pages: 1, 2, 3
- GPT-5.5 3x3 qualitative Profile Writer / Evaluator pilot:
  - 9 writer calls
  - 9 evidence-only evaluator calls
  - 9 truth-scored evaluator calls
  - average evaluator score 89.61
  - zero hidden-context leakage
  - no blocking red flags
- Survey Evidence Export v0.1:
  - normalized append-only evidence atoms
  - typed music object refs
  - reaction normalization
  - Apple priors with `taste_truth: false`
  - `dont_know_enough` as `familiarity_uncertainty`
  - hard response-ref integrity validation
  - A3 sample export with 72 evidence atoms
  - Atlas Tech Owner handoff package for ingestion testing

Important negative finding:

The deterministic page-count backtest did not reach the pre-declared predictive thresholds. `A2_Al1_S1` is currently the best fatigue-adjusted fallback, not a final product answer. The result says the harness works, but the predictor, fake hidden-map realism, and/or evaluation method need another pass before final onboarding length is decided.

## 4. What This Lane Owns

The Survey Intelligence lane owns product decisions for:

- onboarding survey purpose and evidence philosophy
- survey page composition principles
- artist, album, and song survey surface behavior
- reaction semantics for Survey-collected responses
- Apple payload interpretation as exposure prior
- unknown/familiarity handling
- waypoint/context handling
- false-nearby and boundary-test survey behavior
- Survey Evidence Export contract
- Survey-to-Atlas evidence atom content
- Survey simulator fixtures and QA reports used to test survey intelligence
- public/visible survey evidence boundaries
- trusted-alpha survey evidence quality gates

The lane also owns the product stance that Survey output is evidence, not Atlas truth.

## 5. What This Lane Does Not Own

This lane does not own:

- final Atlas confidence calculations
- Atlas role promotion rules
- Atlas node lifecycle, review state, or promotion state
- Mission generation
- Mission review reconciliation
- canonical graph normalization or repair
- canonical graph final-lock decisions
- real Apple Music account integration and permission UX
- final iOS survey UI implementation
- player behavior or Apple Music playback
- final first-mission user-facing copy
- final public onboarding length decision
- final multi-user account or sync model

Unresolved boundary:

Survey owns `evidence_strength_hint`; Atlas owns final confidence. This boundary must stay explicit in Alpha planning because it is easy for teams to treat Survey's hint as an Atlas-ready confidence score.

## 6. Interfaces With Other PM Lanes

### Atlas PM

Interface: Survey Evidence Export v0.1.

Survey sends append-only evidence atoms. Atlas ingests those atoms, computes confidence, resolves contradictions, assigns roles, and decides promotion state.

Open boundary:

Atlas must define how `evidence_strength_hint`, reaction operation, comparison sets, Apple exposure priors, graph refs, and selected tags become Atlas Signals or candidate updates.

### Canonical Graph PM

Interface: typed `music_object_ref` and graph refs.

Survey consumes canonical artists, albums, songs, memberships, roles, and recognition/survey tiers as a candidate substrate. It does not mutate the graph.

Open boundary:

Graph PM must decide when visible family/archetype meanings are stable enough to expose beyond IDs and roles. Until then, Survey exports refs/IDs only.

### Apple Import PM

Interface: Apple evidence summary and exposure prior fields.

Survey needs observed Apple evidence such as recency, repetition, library commitment, playlist context, album completion hints, track-level signals, and loved/favorite hints. Survey treats all of this as exposure prior.

Open boundary:

Apple Import PM must define what real payload fields are available in Alpha, what requires user consent, and what cannot be inferred reliably.

### App/UI PM

Interface: survey page UX, reaction controls, tags, notes, and friction.

Survey PM defines response semantics. App/UI PM owns in-app presentation and capture.

Open boundary:

Final user-facing labels for `love`, `like`, `ok`, `dont_like`, and `dont_know_enough` need product/UI alignment without changing the internal enum semantics.

### Mission PM

Interface: Survey-derived Atlas state, not raw Survey output.

Mission should consume Atlas hypotheses or digests after Atlas interpretation. It should not consume raw Survey page construction logs.

Open boundary:

For trusted Alpha, a concierge pass may manually translate Survey evidence into first mission hypotheses before full Atlas ingestion is production-ready.

### Research / User Testing PM

Interface: survey feel, burden, and trust.

Survey can be technically valid and still feel like a generic quiz. Research PM should evaluate whether users understand the purpose, whether the page burden is acceptable, and whether the first Atlas/Mission output feels earned.

## 7. Current Product Assumptions

- Trusted Alpha users can tolerate a more explicit calibration flow than eventual public users.
- Early survey pages should be mostly known-response signal.
- Page 3 and later are more appropriate for frontier depth and unknown-boundary probing.
- A 12-tile page remains a workable survey unit for simulation and Alpha planning.
- Apple bias improves Page 1 relevance only if overrepresentation is separated from general popularity.
- The canonical graph is sufficient for Alpha candidate generation, but not complete enough to be treated as the whole music world.
- The survey should support canonical, external, unresolved, and user-local music object refs over time.
- `ok` responses are strategically important because they distinguish useful/contextual music from actual landmarks.
- Survey evidence should be append-only so later contradictions remain auditable.
- Qualitative LLM review can help evaluate product feel, but it should not be the selector of record.
- Full public automation is not required for trusted Alpha, but evidence boundaries and validation gates are required.

## 8. Open Questions To Resolve Before Alpha

- What is the trusted Alpha onboarding length target?
  Current backtest recommends `A2_Al1_S1` only as a fallback, not as a predictive-quality win.
- Which parts of the survey will be in-app versus concierge/manual for the first trusted Alpha?
- What is the minimum viable Apple payload in real Alpha conditions?
- Are selected tags and shown-but-unselected tags in scope for Alpha UI, or are they deferred?
- Should notes be captured during onboarding survey, or only during missions?
- How will Atlas consume `evidence_strength_hint` without treating it as final confidence?
- What does Atlas do with `construction_only_excluded` quarantines during ingestion testing?
- Are graph role labels user-visible, PM-visible, or only internal during Alpha?
- How should Survey handle Apple objects that do not resolve to canonical graph objects?
- What are the user-facing labels for `ok` and `dont_know_enough`?
- What is the acceptable unknown rate by page in real user testing?
- Does Page 2 adaptation need to be in-app for Alpha, or can Alpha use precomputed slates?
- How much manual review is acceptable before first mission generation?
- What product threshold determines that Survey has enough evidence to hand off to Atlas?

## 9. Risks and Failure Modes

- Survey feels like a generic music quiz instead of a Waymark calibration instrument.
- Apple payload overfits convenience listening, household listening, nostalgia, or recent noise.
- A single `love` response gets overpromoted into broad genre taste.
- `ok` gets misread as active appetite.
- `dont_know_enough` gets misread as dislike.
- False-nearby probes become user-facing dead ends too early.
- Page 1 becomes too same-cluster and fails to map broader territory.
- Page 2 becomes recommendations instead of evidence gathering.
- Canonical graph alias/version/composition issues create bad survey tiles.
- Hidden simulator truth leaks into visible artifacts, predictor inputs, or Profile Writer packets.
- Survey Evidence Export is treated as mutable state rather than append-only evidence.
- Atlas consumes Survey construction logs instead of normalized evidence atoms.
- LLM Profile Writer prose is mistaken for Atlas truth.
- Backtest metrics are overinterpreted despite not clearing predictive thresholds.
- Trusted Alpha users experience too much survey fatigue before receiving a meaningful payoff.

## 10. Alpha-Readiness View From This Lane

The lane is partially Alpha-ready.

Ready enough:

- Product doctrine is coherent.
- The core simulator exists.
- Page 1 and Page 2 selection are validated in harness form.
- Hidden-data boundaries are testable.
- Survey Evidence Export v0.1 gives Atlas a clean ingestion contract.
- A trusted Alpha can use precomputed or semi-manual survey slates.

Not yet ready as a fully automated public onboarding system:

- Real Apple payload ingestion is not implemented in this lane.
- Page-count decision is unresolved.
- Predictor/backtest quality is below threshold.
- Atlas ingestion of Survey Evidence Export still needs owner acceptance.
- App UI behavior and reaction labels are not final.
- Real-user familiarity rates are not yet calibrated.
- Canonical graph duplicate/version risks remain material.

Alpha posture:

Use this lane for trusted Alpha only if the team accepts a constrained, evidence-led flow with manual review where needed. Do not present Survey output as a finished Atlas.

## 11. What Can Be Manual / Concierge For Trusted Alpha

The following can be manual or concierge without invalidating the Alpha:

- selecting or reviewing the first survey slate
- resolving ambiguous Apple imports
- suppressing obvious graph duplicates or bad version/cast objects
- deciding whether to ask A2/Al1/S1, A3/Al1/S2, or a shorter custom version
- reviewing Survey Evidence Export before Atlas ingestion
- translating early evidence into first Atlas hypotheses
- writing first mission rationale from Atlas-interpreted evidence
- qualitative review of whether the resulting Atlas seed feels like Waymark
- handling non-canonical user objects outside the automated graph pipeline

Manual is acceptable only if the visible evidence ledger remains valid and auditable.

## 12. What Likely Must Be Real / In-App For Trusted Alpha

The following should be real in-app or product-real for trusted Alpha:

- user-facing survey response capture
- stable internal reaction enum mapping
- typed music object refs for every shown object
- Apple consent and import summary, if Apple seeding is used
- visible distinction between preference and familiarity uncertainty
- a way to record `dont_know_enough`
- response persistence
- Survey Evidence Export generation or equivalent normalized evidence emission
- validation that no private/simulator fields enter Atlas-ingestable evidence
- append-only evidence behavior once exported
- enough UX structure that the user understands this is calibration, not recommendation

If these are not real, the Alpha risks testing a PM workflow rather than the user product.

## 13. Recommended Constraints or Guardrails

- Keep Survey-to-Atlas output restricted to Survey Evidence Export v0.1 or a compatible successor.
- Do not let Survey write promoted Atlas nodes directly.
- Do not let Mission consume raw Survey page construction payloads.
- Keep Apple fields under `apple_exposure_prior` with `taste_truth: false`.
- Keep `dont_know_enough` mapped to `familiarity_uncertainty`.
- Keep `construction_only_excluded` outside Atlas ingestion.
- Require every Atlas-ingestable response ref to resolve inside the same export.
- Keep graph refs as IDs/roles unless visible meanings are explicitly present.
- Treat `evidence_strength_hint` as basis metadata, not confidence.
- Preserve hidden simulator data only in simulator-private evaluation paths.
- Keep canonical graph read-only from Survey.
- Require typed `music_object_ref` values.
- Prefer fewer high-signal known-response pages over early broad exploration.
- Put frontier/unknown probing behind an intentional boundary-test rationale.
- Separate product recommendations from evidence diagnostics in all PM reviews.

## 14. Dispatches or Dependencies Needed From Other PMs

### Atlas PM

- Confirm ingestion acceptance criteria for Survey Evidence Export v0.1.
- Define how evidence atoms become Atlas Signals.
- Define how Atlas handles `evidence_strength_hint`.
- Define how Atlas stores Survey provenance and comparison sets.
- Confirm correction/superseding atom semantics for append-only Survey evidence.

### Canonical Graph PM

- Confirm which graph roles are safe for Survey candidate selection in Alpha.
- Provide duplicate/alias/version suppression policy for Alpha survey tiles.
- Decide whether public family/archetype labels are available or IDs-only remains required.
- Confirm handling for canonical gaps and unresolved Apple objects.

### Apple Import PM

- Define Alpha-available Apple payload fields.
- Define privacy/consent language for survey seeding.
- Confirm whether playlist context, loved/favorite hints, track-level signals, and album-completion hints are available.
- Define fallback behavior when Apple import is unavailable or low-signal.

### App/UI PM

- Resolve final user-facing reaction labels.
- Decide whether tags and notes are in Alpha onboarding.
- Define survey page interaction pattern and acceptable page burden.
- Ensure `dont_know_enough` is available and does not feel punitive.

### Mission PM

- Confirm Mission consumes Atlas-interpreted hypotheses, not raw Survey outputs.
- Define what minimum Atlas digest is needed after Survey for a first trusted Alpha mission.
- Identify which first-mission content can be concierge-authored from Survey evidence.

### Research PM

- Define trusted Alpha survey-feel test questions.
- Validate whether users understand the difference between known/familiar, liked, contextual, and not-for-me.
- Evaluate whether the first Atlas/Mission output feels earned by the survey.

## Bottom Line

The Survey Intelligence lane is ready to contribute to a trusted Alpha plan as an evidence collection and evidence-export lane. It is not ready to be treated as a fully automated public onboarding decision engine.

The lane's Alpha value is strongest if constrained to:

- high-signal onboarding survey evidence
- Apple as exposure prior
- typed canonical refs with non-canonical extensibility
- visible response-led adaptation
- no hidden leakage
- append-only Survey Evidence Export into Atlas
- manual review where product truth is not yet stable
