# Waymark App and MusicKit Execution PM Alpha Brief v0.1

## 1. Lane Purpose

This lane owns the trusted Alpha product surface that lets a real user run Waymark on an iPhone.

The lane exists to prove that Waymark can execute the core loop in a real listening context:

```text
choose or continue a mission
-> resolve playable music
-> listen through Apple Music
-> capture lightweight feedback
-> preserve evidence
-> make that evidence available to Survey, Atlas, Mission Review, and Mission Generation
```

For Alpha, this lane is less about final UX polish and more about whether the app can be a trustworthy evidence instrument. It must make listening feel like a real product experience, not a developer harness, while still keeping diagnostics and exports available for the team.

The App / MusicKit lane is the runtime bridge between product theory and user behavior. If this lane fails, the rest of the Waymark system can still simulate; it cannot learn from real listening.

## 2. Product Decisions Already Made

- Trusted Alpha should run on physical iPhone through Apple Music, not only simulator/stub playback.
- MusicKit is the playback system for the current product direction.
- Simulator/stub exports are allowed for development, but do not count as acceptance evidence.
- Physical-device acceptance evidence must include `device_context.is_physical_device = true`.
- Acceptance exports must remain `reconciliation_status = "not_reconciled"` until Atlas review/reconciliation occurs.
- The player should behave like a listening surface, not a playback-status test panel.
- Diagnostics, resolution details, and export mechanics should be separated from the core player UI.
- The player should support a clean top-level loop:
  - mission context;
  - artwork and transport;
  - four primary reactions;
  - contextual secondary chips;
  - optional notes.
- Primary reaction operations are stable even if display labels change.
- Current user-facing primary labels for Alpha direction are:
  - `Love`
  - `Like`
  - `Ok`
  - `Dislike`
- Stable internal reaction operations should remain:
  - `strong_positive`
  - `qualified_positive`
  - `keep_waypoint`
  - `negative`
- Mission schema and app schema must support reaction-dependent secondary chip sets.
- Secondary chips are user/song/mission-specific and should be provided by mission payload or later Atlas/Mission logic.
- Notes are optional for normal listening; Alpha may still require export/readiness gates where useful for review.
- Skip semantics:
  - intentional next after a started song is a skip event;
  - skip should preserve any explicit reaction already given;
  - skip without explicit feedback should create no-signal/skipped evidence, not automatic negative taste evidence;
  - advancing before a song starts should be logged but should not create playback evidence.
- Autoplay across mission songs is expected for Alpha listening.
- Completion should advance to the next mission track only when playback is actually complete or stopped/completed, not merely because elapsed progress crossed a threshold while still playing.
- Manual candidate selection is not required for first trusted Alpha; top MusicKit result is acceptable when confidence/displayed metadata are sufficient.
- Mission Review is a separate surface for depth, correction, and optional review; it should not clutter the player.
- Export may be required operationally during Alpha, but the ordinary user should not need to understand JSON.
- Local persistence is required for Alpha; users should not lose mission/reaction state when closing the app.
- Survey exists as part of the broader product, but survey intelligence/candidate selection is owned by the Survey lane, not this lane.
- CarPlay, lock-screen controls, custom speech capture, backend sync, graph visualization, and playlist creation are deferred for Alpha unless they become blocking.

## 3. What Has Been Built, Proven, or Validated So Far

The app has moved beyond the original v0.2 spike.

Built or proven in-app:

- Bundled mission loading.
- Multiple mission selection from a local mission library.
- Personal mission pack import into the app bundle.
- Live Apple Music authorization flow.
- Live MusicKit catalog search/resolution.
- Live MusicKit playback on physical iPhone.
- Basic playback controls:
  - play;
  - pause/resume;
  - next;
  - previous selection;
  - seek/scrub;
  - stop/end behavior.
- Whole-mission playback direction:
  - next-track skip semantics;
  - auto-advance after completion;
  - no early auto-advance while playback continues.
- Player surface closer to target mockup:
  - mission banner;
  - artwork area;
  - transport controls;
  - primary reaction panel;
  - contextual secondary chips;
  - optional notes.
- Artwork retrieval for resolved tracks and survey tiles.
- Reaction capture with configurable user-facing labels mapped to stable operations.
- Contextual mission item fields:
  - `expected_test_signal`;
  - `player_card`;
  - reaction-specific `feedback_chip_sets`.
- Mission Review surface with editable evidence.
- Skip/no-signal review visibility.
- Session persistence across launches.
- Development/stub export and physical-device/acceptance export separation.
- JSON and Markdown export generation.
- Export sharing/saving path.
- Apple Music signal probe for internal payload inspection.
- Survey shell:
  - welcome/connect flow;
  - artist/album/song grid stages;
  - 12-tile one-screen page direction;
  - five-state response cycle;
  - nuance/freeform scaffolding;
  - local persistence.
- Automated test coverage for mission decoding, export shape, reaction persistence, session persistence, skip semantics, completion semantics, seek semantics, and survey state.

Recent user/device validation:

- MusicKit token/capability issue was resolved through Apple Developer/App ID setup.
- Song playback through MusicKit has worked on physical iPhone.
- A full acceptance-style reaction export was captured from real listening with 12 resolved/played/reacted items.
- Physical testing surfaced and drove fixes around keyboard dismissal, player surface layout, artwork sizing, progress scrubber behavior, and premature auto-advance.

Schema/contract alignment currently proven:

- `mission.v0.2` supports mission hypothesis, run instructions, expected signals, player card copy, and reaction-dependent feedback chips.
- `reaction_session.v0.2` supports device context, MusicKit context, resolution metadata, playback evidence, reaction evidence, timestamps, and export metadata.
- Current Atlas contract requires app evidence to remain auditable Signals or possible update candidates, not automatic Atlas truth.
- Cross-team consistency review confirms Survey, Mission Generation, Atlas, and Mission Review should not mutate the canonical graph.

Simulation/user-testing context relevant to this lane:

- Survey simulation proves hidden simulator truth can be separated from visible evidence.
- Survey pilot import-safety checks pass: quarantined rows are excluded, false-nearby rows do not directly create Dead Ends, and survey responses do not directly create Atlas objects.
- Closed-loop simulation proves mission feedback can become Atlas Signals, PossibleAtlasUpdateCandidates, AtlasDelta, and adaptive second-batch mission context without automatic promotion.
- Mission Generation Alpha brief states that the app does not need to generate missions locally for Alpha; it does need to execute missions and produce trustworthy evidence.

## 4. What This Lane Owns

This lane owns:

- The trusted Alpha iOS app experience.
- First-run app framing only to the extent needed to start real Alpha use.
- Mission selection/continue behavior in the app.
- In-app mission display and mission item navigation.
- MusicKit authorization status and user-facing handling.
- MusicKit catalog resolution behavior as experienced by the user.
- MusicKit playback behavior.
- Core player UX.
- Playback lifecycle semantics:
  - started;
  - playing;
  - paused;
  - completed;
  - skipped after start;
  - advanced before start;
  - failed/unavailable.
- Primary reaction capture in the listening flow.
- Secondary chip display and selection in the listening flow.
- Optional note capture in the listening flow.
- Mission Review as an evidence-review/editing surface.
- Local persistence of mission sessions, reactions, playback records, resolution records, survey responses, and exports.
- App-side export generation and share/save affordances.
- Separation between user-facing surfaces and internal diagnostics.
- TestFlight readiness of the iOS app:
  - signing;
  - bundle/version discipline;
  - app icon/basic metadata;
  - TestFlight-friendly tester flow;
  - physical-device QA checklist.
- App-facing acceptance criteria for imported missions.
- App-facing interpretation of resolution failures, unavailable tracks, wrong versions, and ambiguous catalog matches.

## 5. What This Lane Does Not Own

This lane does not own:

- Canonical graph identity, merge policy, composition policy, or lock readiness.
- Survey candidate generation, page intelligence, hidden fake-user corpora, or survey prediction models.
- Final Survey PM decisions about page count, item mix, or adaptation rules.
- Atlas persistence model beyond the app's local evidence capture needs.
- Atlas promotion/demotion policy.
- Atlas visualization or final Home/Map presentation.
- Candidate Pool Builder ranking or music-object selection.
- Mission Generation prompt design, route semantics, or evaluator policy.
- WWTSF final copy or explanatory synthesis.
- Backend sync, account model, cloud storage, or multi-user architecture.
- Final public reaction language beyond mapping display labels to stable operations.
- CarPlay, lock-screen playback controls, or custom voice capture.
- Playlist creation.

Unresolved ownership boundary: Survey exists in the app today as a UI shell and persistence surface, but its intelligence is not owned by this lane. This lane owns whether the app can render and persist survey activity; Survey PM owns what objects appear and why.

Unresolved ownership boundary: Mission Review exists in the app today as an evidence editor. This lane owns the UI and edit mechanics; Atlas/Mission Review PM owns whether an edit implies a Signal, PossibleAtlasUpdateCandidate, promotion candidate, or no-op.

Unresolved ownership boundary: resolution quality sits between App / MusicKit, Candidate Pool Builder, and Mission Generation. This lane can detect and expose ambiguity; Candidate Pool and Mission Generation must provide better search hints and concrete route items.

## 6. Interfaces With Other PM Lanes

### Survey

The app needs from Survey:

- a production-facing Survey Output Contract;
- stable visible response enums;
- reaction/state normalization map;
- visible selected tags and shown-unselected tags;
- clear separation from simulator-private hidden truth;
- Apple Music payload fields that can be safely displayed or used in-app;
- page size and layout constraints for iPhone.

The app provides to Survey:

- rendered survey surface;
- response persistence;
- Apple Music authorization bridge;
- artwork lookup;
- optional Apple Music signal probe payloads;
- future path for survey export or local evidence capture.

### Atlas

The app needs from Atlas:

- Signal contract for mission feedback;
- `music_object_ref` contract for canonical, user-local, external catalog, and unresolved objects;
- promotion/review state semantics;
- policy for skips/no-signal evidence;
- policy for user notes and user vocabulary terms;
- minimum Alpha digest fields needed after a mission.

The app provides to Atlas:

- real playback evidence;
- user reactions;
- selected and unselected contextual chips if preserved;
- notes;
- resolution metadata;
- device/MusicKit context;
- session timing;
- skipped/no-signal records;
- exportable evidence bundles.

### Mission Generation and Closed-Loop Learning

The app needs from Mission Generation:

- app-import-ready mission JSON;
- concrete route items;
- stable item IDs;
- search hints where possible;
- expected signals;
- player-card copy;
- reaction-dependent chip sets;
- route/order expectations;
- app-readiness status distinct from product-readiness status.

The app provides to Mission Generation:

- reaction-session evidence;
- playback outcomes;
- skip/no-signal context;
- wrong-version/ambiguous resolution issues;
- mission-review edits;
- export payloads for second-batch or concierge generation.

### Candidate Pool Builder

The app needs from Candidate Pool Builder:

- concrete playable candidates;
- Apple Music search hints;
- version/canonical recording guidance where needed;
- risk flags for trap, waypoint, dead end, false-nearby, and frontier candidates.

The app provides back:

- catalog IDs selected by MusicKit;
- candidate counts;
- resolved metadata;
- confidence;
- storefront;
- ambiguity/failure data;
- user-visible wrong-version corrections if built.

### WWTSF / Copy

The app needs from WWTSF/Copy:

- concise mission description text;
- player-card hypothesis copy;
- optional "why this route" copy;
- guidance on what learning summary, if any, appears to Alpha users.

The app should not expose long-form synthesis unless the product team decides it is part of Alpha.

### Release / Trust / Privacy

The app needs from release/privacy ownership:

- TestFlight app name and brand decision;
- privacy policy position;
- App Store Connect privacy answers;
- handling policy for exported user taste data;
- tester support/feedback path;
- decision on whether Alpha testers are internal-only or external TestFlight users.

## 7. Current Product Assumptions

- Alpha is trusted and small: roughly 3-5 friends/testers.
- Alpha can tolerate rough edges, but not broken playback or lost evidence.
- Users should not need to understand schemas or JSON to participate.
- Team can require exports operationally during Alpha if needed.
- Concierge mission generation and review are acceptable during Alpha.
- In-app mission execution must feel real enough that feedback reflects listening, not test frustration.
- Apple Music access is an Alpha prerequisite.
- Physical iPhone is the target runtime for meaningful playback validation.
- Local persistence is acceptable for Alpha; backend sync is not required.
- The app can remain iPhone-first and portrait-first for Alpha.
- Survey can remain partially scaffolded if the first trusted Alpha is mission-led.
- If Survey is included in Alpha, the app should render Survey pages from a contract supplied by Survey PM rather than inventing candidate logic.
- The player should optimize for quick, low-friction feedback while still allowing deeper review later.
- Voice-to-text can rely on iOS keyboard dictation for Alpha unless custom speech capture becomes a validated need.
- App export evidence is the durable product artifact until backend ingestion is available.

## 8. Open Questions to Resolve Before Alpha

- Is trusted Alpha mission-led, survey-led, or a hybrid?
- Should testers start on Today, Mission, or Player?
- Should Survey be visible to trusted Alpha testers in this build, or held for a separate intake test?
- What is the minimum first Alpha mission set per tester?
- Are missions assigned concierge-style, bundled in app, imported manually, or generated from a server/harness and then bundled?
- What is the final Alpha display language for the four primary reactions?
- Should `Ok` mean weak positive, waypoint/shelf, or neutral tolerated evidence in the user surface?
- Are notes optional everywhere, or required for certain Alpha exports/review states?
- Should secondary chips save immediately on tap, or only once a song completes/skips?
- What does the user see when resolution is ambiguous, unavailable, or probably wrong version?
- Is manual resolution required before Alpha, or can wrong-version issues remain review-only?
- Should Export be hidden under diagnostics, available under More, or part of the visible Alpha flow?
- Who receives exports in Alpha, and by what process?
- Does Alpha require in-app "Review Past Missions" or is session persistence plus export enough?
- What privacy language is needed around taste data, Apple Music access, notes, and exports?
- Is the app name for TestFlight `Waymark`, `Music Atlas`, or another temporary label?
- Does Alpha need reset/delete-local-data behavior?
- Does Alpha need crash/error reporting beyond manual feedback?
- What is the product policy when a tester does not have Apple Music playback capability?

## 9. Risks and Failure Modes

Major product risks:

- Playback is unreliable enough that taste feedback is contaminated by app frustration.
- Auto-advance or skip semantics misclassify behavior as taste evidence.
- Wrong MusicKit versions get played and reactions attach to the wrong object.
- Resolution succeeds technically but fails musically.
- Alpha users see too many diagnostics and experience the app as a test tool.
- Export becomes necessary but opaque, causing users to miss the key evidence step.
- Local persistence fails or resets, destroying Alpha evidence.
- Survey appears more intelligent than it is because the app shell renders before candidate logic is production-ready.
- Feedback chips feel personalized but are structurally too generic for Atlas learning.
- User notes become high-value evidence but are not routed into Atlas/Mission Review contracts.
- App-visible reaction labels drift from simulator, Atlas, Mission Review, or export labels.
- Skipped/no-signal items become accidental negative evidence.
- Physical-device MusicKit capability differs by tester account, storefront, or subscription state.
- The app imports schema-valid missions that are not app-ready because route items are placeholders.
- TestFlight users receive a build that still exposes internal tabs without clear instructions.

Alpha-specific failure modes:

- A tester opens the app and does not know what to do first.
- A tester cannot connect Apple Music and has no fallback path.
- A tester finishes a mission but the team receives no usable evidence.
- A tester gives good feedback in the app but it cannot be connected back to Mission/Atlas IDs.
- A tester reacts to a track before it starts or after a skip, and the app records misleading evidence.
- A tester closes the app mid-mission and cannot continue cleanly.

## 10. Alpha-Readiness View From This Lane

This lane is Alpha-promising but not yet Alpha-ready.

Green lights:

- The core iPhone/MusicKit loop has been proven.
- Mission loading, resolution, playback, reaction capture, review, persistence, and export all exist.
- Physical-device MusicKit setup has been worked through once.
- Recent tests cover the riskiest playback/evidence semantics.
- The app can already produce useful evidence for product review.
- The player surface is close enough to continue hardening rather than restart.

Yellow lights:

- Whole-mission playback still needs repeated physical-device QA across different missions.
- Navigation remains more internal-tool-like than friend-Alpha-like.
- Export is operationally useful but not yet product-natural.
- Survey is implemented as a shell/prototype, not a finished intake system.
- Mission schema in app remains closer to v0.2/v0.3-alpha than the richer Mission Generation harness schema.
- MusicKit resolution quality is acceptable for early Alpha, but manual correction is not built.
- Release packaging, privacy metadata, app icon, and TestFlight configuration still need product/release decisions.

Red lines:

- Do not ship trusted Alpha if playback cannot reliably start, seek, skip, and advance through a full mission on physical iPhone.
- Do not ship trusted Alpha if mission evidence can be lost by closing/reopening the app.
- Do not ship trusted Alpha with placeholder route items presented as playable tracks.
- Do not let app evidence automatically promote Atlas truth.
- Do not expose hidden simulator truth, private reason tags, or evaluator-only data in user-facing app artifacts.

## 11. What Can Be Manual / Concierge for Trusted Alpha

Trusted Alpha can manually support:

- Mission generation.
- Mission review before app import.
- Candidate pool curation.
- Apple Music version checks before bundling missions.
- Resolving problematic route items outside the app.
- Assigning missions to specific testers.
- Collecting exports through manual share/save workflow.
- Interpreting exported JSON/Markdown.
- Turning reaction-session evidence into Atlas Signals.
- Creating AtlasDelta and second-batch missions outside the app.
- Repairing or replacing bad missions between TestFlight builds.
- Tester onboarding through a written runbook.
- Support/feedback through direct messages rather than in-app tooling.
- Privacy/support explanation outside the app, if acceptable for trusted friends.

This is acceptable for Alpha if the app still captures real listening behavior cleanly.

## 12. What Likely Must Be Real / In-App for Trusted Alpha

Trusted Alpha likely needs real in-app:

- Apple Music permission request and status handling.
- Clear mission selection or continue path.
- Mission detail display.
- Resolved/playable route items.
- Reliable track playback on iPhone.
- Reliable next/skip behavior.
- Reliable auto-advance after completion.
- Pause/resume and seek/scrub.
- Four primary reactions.
- Contextual secondary chips.
- Optional notes.
- Local save/persistence.
- Mission Review or equivalent evidence correction path.
- Export/share path, even if hidden under More/Diagnostics.
- Handling for unresolved/unavailable/failed playback states.
- App-side evidence IDs that round-trip to mission and Atlas contracts.
- Basic tester-safe navigation.
- Basic reset/recover path if a session becomes unusable.

The app does not likely need real in-app:

- Autonomous mission generation.
- Full Atlas visualization.
- Final WWTSF synthesis.
- Backend sync.
- Account system.
- CarPlay.
- Custom speech recognition.
- Playlist creation.
- Advanced manual resolution UI.

## 13. Recommended Constraints or Guardrails

- Keep Alpha iPhone-first.
- Keep the player uncluttered and separate diagnostics from listening.
- Keep mission route items concrete and playable.
- Require stable `mission_id` and `item_id` for every imported mission.
- Preserve both user-facing labels and stable internal reaction operations.
- Preserve selected secondary chips and shown-unselected chips if the mission-review/Atlas contracts require them.
- Treat skip/no-signal as weak behavioral evidence, not taste rejection.
- Treat notes as potentially high-value evidence even when sparse.
- Store resolution metadata for every resolved item:
  - catalog ID;
  - URL;
  - resolved title;
  - resolved artist;
  - resolved album;
  - storefront;
  - confidence;
  - candidate count;
  - resolver method.
- Keep acceptance exports separated from development/stub exports.
- Keep physical-device evidence distinguishable from simulator evidence.
- Hide or demote Export/Resolve diagnostics in the Alpha user flow unless the tester explicitly needs them.
- Use local persistence for Alpha but keep data exportable and resettable.
- Do not add backend assumptions into app behavior before backend ownership is resolved.
- Do not let Survey fixture behavior imply production Survey intelligence.
- Gate TestFlight readiness on physical-device mission QA, not simulator test pass alone.
- Keep product-review status separate from JSON schema validity.

## 14. Dispatches or Dependencies Needed From Other PMs

Needed from Survey PM:

- Final Alpha decision: Survey visible in app or deferred.
- Survey Output Contract for app rendering/persistence.
- Survey reaction/state normalization map.
- Page-size/layout requirements for iPhone.
- Rules for selected tags, shown-unselected tags, and freeform survey evidence.
- Policy for using Apple Music signal payloads in-app.

Needed from Atlas PM:

- Alpha Signal contract for mission playback/reaction evidence.
- Policy for skip/no-signal evidence.
- Policy for notes and user vocabulary extraction.
- Promotion/review/demotion policy for Alpha.
- Minimum Atlas ingestion fields expected from app exports.
- Decision on whether app exports remain manual or feed an ingestion harness.

Needed from Mission Generation PM:

- App-import-ready mission schema reconciliation.
- Required fields for player surface:
  - mission headline;
  - mission description;
  - route item hypothesis;
  - expected signal;
  - reaction-dependent chip sets;
  - Apple Music search hints.
- Definition of `app_import_candidate`.
- Rules for unresolved/search-placeholder items.
- First trusted Alpha mission pack.

Needed from Candidate Pool PM:

- Apple Music search/version hint policy.
- Candidate quality gate before app import.
- Handling rules for wrong versions, remasters, live versions, covers, and regional catalog variants.
- Candidate role/risk flags useful in app review.

Needed from Release / Trust / Privacy PM:

- App/TestFlight name decision.
- Internal versus external TestFlight path.
- Tester list and support channel.
- Privacy policy and App Store Connect privacy answers.
- App icon/brand minimum for Alpha.
- Export/data-retention language.
- Whether Alpha requires visible terms/privacy copy in-app.

Needed from Design PM:

- Final trusted Alpha navigation shell.
- Whether Today is required for first Alpha.
- Player surface final v0 layout constraints.
- Mission Review minimum usable state.
- How to hide diagnostics without blocking tester support.
- Empty/error state copy for MusicKit failures.

## Alpha Recommendation From This Lane

Proceed toward trusted Alpha with the app as a mission execution and evidence capture product, not as a full autonomous Waymark system.

This lane can support Alpha if the unified plan accepts these constraints:

- mission generation remains concierge/harness-driven;
- missions imported into the app must be concrete and playable;
- Apple Music is required for testers;
- app captures real playback/reaction evidence;
- exports or equivalent evidence bundles remain mandatory operationally;
- Atlas updates remain reviewed, not automatic;
- Survey can be included only if its Alpha scope is explicitly defined;
- TestFlight readiness is gated by physical-device full-mission QA.

The product question for Alpha is no longer whether an iPhone can play a Waymark mission and capture useful evidence. That has been proven. The remaining Alpha question is whether the app can make that loop reliable and understandable enough that trusted friends produce clean evidence without needing the team in the room.
