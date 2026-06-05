# Reaction & Mission Evidence Gap Audit v0.1

Date: 2026-05-29

Product context: Cartenza v0.2 alpha/TestFlight preparation. TestFlight is the primary validation path; physical-device installs are reserved for selective checks that should not disrupt the TestFlight build on the phone.

This audit translates the current PM v0.2 readiness picture into the app/data plumbing lane. It focuses on current app behavior and code contracts, not a full Mission Generation or Atlas profile rewrite.

## PM Readiness Snapshot

| Domain | Current status |
| --- | --- |
| App UI/UX | Ready for v0.2 |
| Onboarding message | Ready; no changes planned |
| Survey | Ready; no changes planned |
| Survey results to Atlas | Needs contract confirmation if Atlas schema requirements changed |
| Atlas visuals | Not ready, not a v0.2 blocker |
| Player | Ready; no planned v0.2 changes |
| Canonical graph | Ready for v0.2 usage |
| Album sidecar with Apple IDs | Ready for v0.2 usage |
| Mission generation | In progress |
| Mission delivery | Next convergence point after selection locks |
| Reaction/evidence schema | Needs gap closure before Mission Delivery is treated as complete |

## Current Technical Capture Surface

Current app evidence is centered on item-level mission listening:

- `ReactionSession` exports `reaction_session.v0.2` with device context, music context, item results, session summary, and an `atlas_signal_candidate_bundle`.
- `ItemResult` captures one mission item with resolution, playback, reaction, and timestamps.
- `PlaybackRecord` captures `not_attempted`, `queued`, `playing`, `played`, `skipped`, and `failed`, with attempted/started/ended timestamps and duration when available.
- `ReactionRecord` captures one primary reaction value, selected context tags, and free-text notes.
- `AtlasSignalCandidateBuilder` emits candidate-only events for `resolution`, `playback`, `skip`, `reaction`, selected `chip`, `note`, and `review`.
- `MissionReviewView` exposes review/edit affordances for per-item evidence after listening.
- `AppModel.playerActionLog` records some navigation actions in memory: `skip_before_start`, `skip_after_start`, `skip_unresolved`, and `completed_by_threshold`. These actions are not persisted or exported as first-class evidence.

Important guardrail: exported Atlas signal candidates explicitly set `writes_atlas_truth = false` and `canonical_graph_mutation_allowed = false`.

## Evidence Gap Matrix

| Player action | Currently captured? | Desired capture | Learning value | Gap |
| --- | --- | --- | --- | --- |
| Mission viewed | No first-class event. Mission selection/persistence can imply active mission. | `mission_viewed` with mission ID, timestamp, surface, and whether it came from TestFlight/live path. | Separates exposure from acceptance. | Add mission lifecycle event model/export. |
| Mission accepted / skipped / regenerated | Accepted is implied by `selectMission`; skipped/regenerated are not first-class. | `mission_accepted`, `mission_skipped`, `mission_regenerated` with reason where available. | Learns from avoided mission concepts and weak route framing. | Needed for Mission Delivery. |
| Track shown | Partially implied by selected item and exported item results; no impression event. | `track_shown` per route item with timestamp, position, and mission context. | Distinguishes ignored items from unseen items. | Add persistent impression event. |
| Track played / not played | Played/skipped/failed captured for exportable resolved items. Not-played-before-start is only in `playerActionLog`. | Explicit `track_play_attempted`, `track_not_played`, and `track_play_failed` events. | Avoidance before playback is a strong negative/uncertainty signal. | Persist/export pre-play skips and failures. |
| Track completed / skipped early | Completion captured as `played`; skip-after-start captured as `skipped` plus skip candidate. | Completion threshold, observed elapsed fraction, skip reason, and whether auto-advanced. | Separates completion, passive finish, and early rejection. | Add richer playback event detail. |
| Track liked / disliked / neutral | Captured through reaction values: `hit`, `partial`, `ok_shelf`, `miss`; `unresolved` is used for no-signal. | Keep current values, but add explicit no-response/ignored state separate from unresolved. | Positive and negative preference learning. | Mostly present; avoidance state missing. |
| Tag chips shown | Partially inferred as `shown_unselected_chips` for the selected reaction's chip set during export. | Actual chip impression list with timestamp and visible order. | Learns from ignored tag language. | Inferred only after reaction; may not match actual visible chips. |
| Tag chips selected / rejected | Selected chips captured. Rejected chips are inferred from shown-unselected chips. | Explicit selected, deselected/rejected, and ignored chip states. | Fine-grained explanation tuning. | Add event state/history for chip interactions. |
| Free-text note | Captured when attached to a reaction. Voice note refs exist in schema but no current audio capture path. | Text note plus optional voice note refs if/when implemented. | High-value qualitative learning. | Text is present; voice note UX/schema path unfinished. |
| Album track feedback | Schema supports album item type, but current player/reaction flow is track-centric. | Album-level and album-track-level feedback tied to sidecar track identities. | Supports sidecar-only discovery and album-specific learning. | Needs Mission Delivery design. |
| Mission completed / abandoned | Session summary counts exist at export time; no explicit mission completion/abandon event. | `mission_completed` and `mission_abandoned` with route progress and last item. | Learns from route-level friction. | Add mission lifecycle event/export. |
| Post-mission summary reaction | No dedicated UI/schema event. | Summary reaction and optional "what we learned" confirmation. | Validates mission claim, route quality, and learning summary. | Needed for closed-loop delivery. |
| Save / add / revisit signal | No current capture. | Save/add/revisit event against track, album, or mission. | Strong durable preference signal. | Add when the UI exposes this action. |
| More like this / less like this | Approximate via reactions/chips only. | Explicit command-level signal tied to subject object and mission context. | Direct next-mission steering. | Add if PM wants it in v0.2 delivery. |
| Sidecar-only track promotion signal | No explicit event. Catalog IDs are captured in resolution and sidecar data is ready. | Promotion candidate event for sidecar-derived track identity, gated as review-only. | Converts sidecar coverage into learning without mutating Atlas truth. | Add review-gated sidecar promotion candidate. |

## Current Strengths

- `reaction_session.v0.2` is already capable of exporting usable per-item listening evidence.
- The Atlas candidate bundle preserves resolution, playback, reaction, chip, note, skip, and review records as ingestion candidates.
- Skip-after-start and completion-threshold flows are tested.
- The mission review rail lets a tester correct no-signal/skipped items before export.
- The export guardrails prevent accidental Atlas truth writes.

## Main Risks For v0.2 Mission Delivery

1. Mission-level lifecycle is not first-class. Mission viewed, accepted, skipped, regenerated, completed, and abandoned are currently absent or only implied.
2. Avoidance before playback is not durable enough. `skip_before_start` exists only in memory and does not survive persistence/export.
3. Chip "shown but ignored" is inferred after a reaction rather than captured at display time.
4. Album/sidecar evidence is not yet modeled as a distinct learning path.
5. `ReactionSession` exports only items with resolved playback evidence and a reaction. That is good for clean acceptance evidence, but it drops some informative avoidance and failure events unless they become explicit candidates elsewhere.

## Recommended Implementation Sequence

1. Add a lightweight `MissionEvent` / `PlayerEvidenceEvent` model and persistence path for mission lifecycle and pre-play avoidance.
2. Extend export with an event ledger that remains candidate-only and does not change Atlas truth.
3. Add schema/tests for mission viewed, accepted, track shown, skip-before-start, abandoned, and completed events.
4. Add actual chip impression capture before relying on `shown_unselected_chips` as learning evidence.
5. Add sidecar-only promotion candidates after Mission Delivery confirms where album/track sidecar feedback appears in the UI.
6. Reconfirm `waymark.survey_evidence_export.v0.1` against the current Atlas ingestion contract before treating Survey-to-Atlas as locked for v0.2.

## v0.2 Decision

The current app is sufficient for item-level alpha listening evidence, especially for TestFlight smoke and reviewed mission feedback. It is not yet sufficient for the full PM learning question:

> Are we capturing enough evidence to learn from both positive action and avoidance?

Answer: partially. Positive action and post-play reaction are covered. Avoidance, mission-level intent, chip impressions, album-specific feedback, and sidecar promotion need a small event-ledger pass before Mission Delivery should be considered evidence-complete.
