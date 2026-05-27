# Waymark Canonical Graph PM Alpha Brief v0.1

## 1. Lane Purpose

This lane owns the canonical music-object substrate that lets Waymark ask useful taste questions without pretending the graph already knows the user's taste.

The canonical graph exists to support:

```text
Artist Survey -> Album Survey -> Song Survey -> Starter Atlas -> First Missions -> Later Atlas Expansion
```

It is not an encyclopedia, critic canon, final user profile, playlist generator, or exhaustive discography. Its product job is to provide normalized artists, albums, song recordings, archetype memberships, aliases, version policy, quarantine policy, and survey-safe candidate surfaces that other lanes can consume safely.

Product truth:

- The graph asks good questions.
- User taps, listening behavior, notes, and review create evidence.
- Atlas owns user-specific interpretation.
- Mission Generation owns hypotheses and routes.
- Survey owns page logic and user interaction.

Current Alpha contract:

- Use the repaired v0.2 survey candidate surfaces for controlled survey pilot work.
- Do not use raw graph rows for Fast Survey.
- Do not treat canonical graph metadata as promoted Atlas truth.
- Do not hard-lock or fully production-import the graph yet.

## 2. Product Decisions Already Made

- Canonical graph equals shared music-object substrate, not taste truth.
- Atlas schema equals user-specific interpretation layer above canonical music data.
- Survey, Mission Generation, and Mission Review must not mutate the canonical graph.
- Apple Music payloads are a bias layer and resolution aid, not the graph brain.
- Artist, album, song recording, composition/work, context, and special-entity objects must remain distinct.
- Song-first and one-hit objects are valid graph objects when they ask useful questions.
- Live albums, compilations, and soundtrack/context objects may be valid gateway objects, but only with explicit object type and survey policy.
- Covers, source versions, live versions, remixes, clean/explicit variants, cast recordings, worship standards, traditional songs, and classical works must not be merged by title.
- False-nearby and boundary objects are probes, not conclusions.
- Canonical rows can suggest a possible Dead End probe, but no graph row directly creates an Atlas Dead End.
- Limited beta-style survey pilot is approved with guardrails.
- Full canonical production import, hard lock, raw-graph Fast Survey use, and unguarded Atlas promotion are not approved.

## 3. What Has Been Built, Proven, or Validated So Far

The staging graph has been consolidated across all 18 families.

Current staging dry-run emission:

- 18 families imported
- 0 validation errors
- 9 validation warnings
- 1499 canonical artists
- 1207 canonical albums
- 1917 canonical song recordings
- 1612 artist memberships
- 1245 album memberships
- 1983 song memberships
- 24 composition/title review rows

Normalization Pass 2 added the policy and safety layer needed for limited survey pilot work:

- artist, album, and recording alias sidecars
- entity relationship and do-not-merge sidecars
- composition and recording-version sidecars
- cover/source relationship handling
- special-entity modeling support
- quarantine queue and quarantine report
- family and archetype readiness files
- survey candidate files for artists, albums, and songs
- row-level survey intent, inference, and do-not-infer fields
- false-nearby and boundary probe artifacts
- import dry-run and QA evidence

The repaired pre-pilot packet resolved the main Gate 2 blockers:

- quarantine rows reduced from 146 to 107
- 39 rows unquarantined after fixing over-broad special-entity matching
- 0 Page 1 QA failures
- 0 recording/quarantine consistency failures
- import dry run remained at 0 errors and 9 warnings
- Family 6 and Family 12 Page 1 surfaces were repaired toward recognizable trunk anchors
- Family 15 and Family 17 remained `context_only`

Controlled survey pilot integration has also passed against the approved graph inputs:

- approved input files only
- 9 generated pages
- 108 displayed tiles logged
- 108 simulated responses logged
- 0 acceptance failures
- no Apple payload consumed in that run because the dispatch restricted inputs to repaired Normalization Pass 2 files

## 4. What This Lane Owns

This lane owns:

- canonical artist, album, song recording, composition, and special-entity substrate
- family and archetype membership context
- canonical ID and slug normalization policy
- alias sidecars and display-name normalization rules
- do-not-merge and merge-block policy
- composition versus recording/version policy
- source, cover, live, remix, edit, clean/explicit, cast, traditional, worship, soundtrack, and classical review flags
- quarantine system for unsafe rows
- family and archetype survey-readiness classification
- survey-safe candidate files derived from the graph
- row-level survey intent and inference guardrails for graph-supplied candidates
- false-nearby, boundary, contrast, and dead-end probe metadata
- graph import safety reports and QA exception ledgers

This lane should be the source of truth for whether a graph row is safe to show, safe to resolve automatically, safe only for manual review, or blocked from survey and mission surfaces.

## 5. What This Lane Does Not Own

This lane does not own:

- Survey UI, survey page composition logic, or adaptive selection behavior
- final reaction language or reaction enum mapping
- Apple Music payload ranking, library import interpretation, or catalog search implementation
- Atlas persistence, Atlas visualization, role promotion, confidence formulas, or final user-specific truth
- Mission Generation route design, Mission Review behavior, or Candidate Pool Builder ranking
- product copy for explaining user taste
- playback UX, account system, cloud sync, or app shell behavior
- final worldwide music ontology or exhaustive catalog completeness
- automatic promotion of Landmarks, Regions, Frontiers, Dead Ends, or Waypoints

Unresolved ownership boundary:

Candidate Pool Builder sits between this lane, Atlas, Mission Generation, and Survey. The canonical graph can provide candidate roles, boundary probes, and resolution policy, but it should not own final route-level selection, mission sequencing, or user-specific promotion logic.

## 6. Interfaces With Other PM Lanes

### Survey

Survey consumes:

- `survey_artist_candidates_v0_2.json`
- `survey_album_candidates_v0_2.json`
- `survey_song_candidates_v0_2.json`
- family and archetype readiness files
- quarantine and recording-version policy
- survey intent and do-not-infer guardrails

Survey owns:

- page logic
- adaptive branching
- user response capture
- Apple payload integration behavior
- final survey transcript shape

The current rule is that Fast Survey may use only `survey_ready` families, only `page1_core` for Page 1, only `page2_adaptive` for Page 2, and only `page3_deep` for Page 3 or Deep Survey.

### Atlas

Atlas consumes canonical graph references when available, but must also support user-local, unresolved, external catalog, and composition-placeholder objects.

This lane provides typed canonical references and safety metadata. Atlas owns Signals, role assignments, user-specific confidence, promotion state, and interpretation.

No survey response should directly create a promoted Landmark, Region, Frontier, Dead End, or Waypoint from graph metadata alone.

### Mission Generation and Candidate Pool Builder

Mission and Candidate Pool Builder may use graph-provided anchors, bridges, probes, waypoint/context candidates, and false-nearby candidates, but only through the approved candidate and readiness layers.

False-nearby rows must be treated as experiment candidates. They cannot become standard recommendations or Atlas Dead Ends without user evidence and promotion logic.

### Apple Music / Resolver

This lane provides:

- exact-recording requirements
- version-flexible versus manual-review policies
- quarantine restrictions
- composition/work ambiguity flags
- Apple Music auto-resolution blocks

Resolver owns actual search, matching, playback availability, and catalog payload interpretation.

### App / Telemetry

This lane defines the graph fields that must be preserved in tile logs:

- `candidate_id`
- `canonical_entity_id`
- `object_type`
- `family_id`
- `archetype_ids`
- `survey_page_role`
- `survey_intent`
- `dedupe_group`
- `priority_score`
- `trigger_rule`
- `positive_inference`
- `negative_inference`
- `do_not_infer`

The app/telemetry lane owns actual logging implementation and data transport.

## 7. Current Product Assumptions

- Trusted Alpha can tolerate manual review and concierge intervention.
- Trusted Alpha cannot tolerate invisible overclaiming, unsafe merges, or raw graph leakage into user-facing surfaces.
- The repaired v0.2 survey surfaces are good enough for controlled pilot review, not full public launch.
- Page 1 should privilege normal-user recognition, broad branching value, and unambiguous object identity.
- Page 2 and Page 3 should be adaptive and question-driven, not merely deeper or more obscure.
- Context-only families should remain outside Fast Survey unless another lane creates a specific context surface.
- Family 13, Family 14, and Family 16 still require caution because language/remix/work/worship handling is more fragile.
- Apple payload seeding may improve survey relevance, but it must be capped and audited so it does not overfit.
- User Atlas objects may exist outside the canonical database, and the graph must not block those objects from being represented elsewhere.
- The current graph is a staging substrate with safety sidecars, not a final canonical lock.

## 8. Open Questions to Resolve Before Alpha

- Which families are included in the first trusted Alpha Fast Survey, and which are sandboxed or excluded?
- Does Product Owner review approve the repaired Family 6 and Family 12 Page 1 surfaces as normal-user useful?
- How much Apple payload seeding is allowed in Page 1 before it becomes overfit?
- Should cautious families 13, 14, and 16 appear in Fast Survey, Deep Survey only, or concierge-only Alpha flows?
- What is the final reaction normalization map across survey UI, simulator, Atlas Signals, and Mission Review?
- Which special entity types can be safely user-facing in Alpha, and which require concierge/manual handling?
- How should composition placeholders appear, if at all, in survey and Atlas during Alpha?
- What exact line separates `approved_not_survey_safe`, `needs_review`, and `quarantined` for downstream systems?
- Who owns final conflict resolution when Survey wants a row for recognition value but graph policy marks it version-risky?
- What evidence threshold will later permit movement from staging substrate to full canonical import or hard lock?

## 9. Risks and Failure Modes

- Raw family rows get used directly instead of approved v0.2 survey surfaces.
- A title merge collapses distinct recordings, covers, source versions, standards, or cast versions.
- Artist aliases collapse group, solo, project, producer, fictional performer, church brand, or credited-artist distinctions.
- Quarantined rows leak into Fast Survey, starter Atlas, default mission generation, or Apple auto-resolution.
- Apple payloads dominate Page 1 and make the survey look personalized while collecting narrow or biased evidence.
- Graph roles are mistaken for Atlas roles, creating fake Landmarks, Regions, or Dead Ends.
- False-nearby probes appear too often or too early and feel hostile or irrelevant.
- Page 1 grids ask duplicate questions despite having distinct IDs.
- Canon depth pushes out normal-user recognition, making survey onboarding feel obscure.
- Context, worship, theater, classical, holiday, kids, and soundtrack objects are treated as ordinary artist/song taste signals.
- ID prefix drift or typed-ref drift breaks integration across Survey, Atlas, Mission, and Resolver lanes.

## 10. Alpha-Readiness View From This Lane

This lane supports a limited trusted Alpha survey pilot with guardrails.

Ready for Alpha-level use:

- approved v0.2 survey candidate surfaces
- family and archetype readiness classifications
- quarantine and version sidecars as safety controls
- row-level survey intent and inference guardrails
- controlled survey pilot logging and import-safety checks
- false-nearby and boundary probes as experiments, not conclusions

Not ready:

- full canonical production import
- hard canonical lock
- raw graph use in Fast Survey
- automatic cover/version/composition merging
- automatic Atlas promotion
- unreviewed special-entity surfacing
- broad public release without product-owner review of survey usefulness

Alpha status from this lane:

```text
limited_beta_survey_pilot_ready_with_guardrails
not_full_import_ready
not_hard_lock_ready
not_raw_graph_fast_survey_ready
not_unguarded_atlas_promotion_ready
```

## 11. What Can Be Manual / Concierge for Trusted Alpha

The following can be manual or concierge in trusted Alpha:

- final review of Page 1 family surfaces
- Apple Music resolution for risky recordings, covers, live versions, standards, and special entities
- manual handling of user library objects not found in the canonical graph
- merge and alias adjudication when sidecars say `needs_review`
- composition/work decisions for standards, hymns, classical works, theater songs, and traditional songs
- inclusion or exclusion of cautious families for specific testers
- special-case survey pages for context families, holiday/kids/shared listening, soundtrack/theater, and worship
- hand-curated candidate overrides for early Mission or Atlas experiments
- human review of suspicious high-impact survey responses before Atlas promotion

Concierge support is acceptable only if the system records the uncertainty instead of hiding it.

## 12. What Likely Must Be Real / In-App for Trusted Alpha

The following likely must be real in-app or enforced by service code:

- survey display must use only approved candidate surfaces, not raw graph rows
- Page 1, Page 2, and Page 3 pool restrictions must be enforced
- duplicate canonical IDs and duplicate dedupe groups must be blocked per page
- quarantined and suppressed rows must not display
- quarantined rows must not enter Apple Music auto-resolution
- displayed tile logs must preserve candidate metadata, page number, position, and user response
- survey responses must write provisional evidence only
- typed music-object references must be preserved in logs and downstream payloads
- positive, negative, skip, and don't-know responses must keep do-not-infer guardrails
- false-nearby and boundary probes must remain labeled as probes
- no survey tap may directly create a promoted Atlas role

Manual review can improve quality, but these safety rails should not rely on memory or operator discipline.

## 13. Recommended Constraints or Guardrails

- Use only:
  - `survey_artist_candidates_v0_2.json`
  - `survey_album_candidates_v0_2.json`
  - `survey_song_candidates_v0_2.json`
  - `family_survey_readiness_v0_2.json`
  - `archetype_readiness_v0_2.json`
  - `canonical_quarantine_queue.json`
  - `canonical_recording_versions.json`
  - `dead_end_probe_candidates_v0_2.json`
  - `boundary_question_bank_v0_2.json`
- Fast Survey may use `survey_ready` families only.
- Fast Survey must not use `context_only` families.
- Page 1 must pull only from `page1_core`.
- Page 2 must pull only from `page2_adaptive`.
- Page 3 and Deep Survey may pull from `page3_deep`.
- `suppressed_quarantined` rows are not eligible for survey display.
- Quarantined rows are not eligible for Apple Music auto-resolution.
- Page generation must log dedupe and quarantine checks.
- Artist, album, and song surfaces should produce different but coherent evidence.
- Apple payload seeding should have explicit source-mix logging and caps.
- False-nearby rows should be sparse, intentional, and clearly marked as probes.
- All graph-derived user evidence should be auditable back to candidate IDs and displayed tiles.
- Product teams should use typed object refs, not untyped strings.

## 14. Dispatches or Dependencies Needed From Other PMs

### Product Owner

Needed before broader Alpha:

- approve or revise first Alpha family inclusion policy
- confirm whether cautious families 13, 14, and 16 are included, sandboxed, or concierge-only
- review whether repaired Page 1 surfaces feel recognizably useful to normal users
- confirm that limited pilot guardrails are acceptable for trusted Alpha

### Survey PM

Needed:

- complete `SURVEY_PILOT_PAGE_LOGIC_REVIEW`
- confirm Page 1, Page 2, and Page 3 selection rules against the v0.2 candidate files
- define final reaction normalization map
- decide how Apple payload seeding affects source mix and tile priority
- confirm that survey logs carry required graph metadata

### Atlas PM

Needed:

- confirm the shared `music_object_ref` union, including canonical, user-local, external catalog, unresolved, and composition-placeholder refs
- confirm survey response to Signal to provisional Atlas update behavior
- confirm that graph metadata cannot bypass Atlas promotion logic
- define how non-canonical user objects appear beside canonical graph refs

### Mission / Candidate Pool PM

Needed:

- align candidate role vocabulary across graph, Atlas, and Mission
- confirm how false-nearby, boundary, waypoint, and probe candidates are consumed
- confirm that graph rows never directly create Atlas Dead Ends
- define whether candidate pool ranking lives in Mission, Atlas digest, or its own lane

### Apple Music / Resolver PM

Needed:

- define exact recording resolution behavior
- define manual review fallbacks for risky versions and special entities
- confirm no quarantined entity can be auto-resolved
- define how Apple payloads bias survey without becoming taste proof

### Engineering

Needed:

- freeze the v0.2 graph input contract once PM review accepts it
- enforce guardrails in code, not just docs
- preserve QA reports and exception ledgers as artifacts
- prevent raw graph tables from feeding Fast Survey, starter Atlas, or default mission generation
