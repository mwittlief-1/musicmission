# Alpha Survey App/UI Implementation Notes v0.1

Generated: 2026-05-21

Status: Survey-lane handoff notes for Core app integration

## Packet Scope

Core should render `waymark.alpha_survey_page_packet.v0.1` packets. The packet is app-renderable and evidence-export-compatible, but it is not Atlas-ingestable by itself.

Atlas ingestion starts after visible user responses become Survey Evidence Export v0.1 atoms.

## Alpha 1 Required Intake

Product decision addendum `docs/app_dev/alpha_product_decision_addendum_2026_05_22.md` supersedes the earlier fast-survey fallback. For Alpha 1, Survey is required immediately after onboarding and before the core app IA.

Required Alpha 1 intake:

| surface | pages | tiles |
|---|---:|---:|
| Artist | 4 | 48 |
| Album | 2 | 24 |
| Song | 4 | 48 |
| Total | 10 | 120 |

Normal first-run Alpha intake has no optional early exit. Any revisit/support path should live outside the first-run flow, under My Account or a support/debug affordance.

The current fixed intake fixture is:

`data/survey_simulation/survey_evidence_export/alpha1_required_intake/public_profile_01_A4_Al2_S4_alpha1_survey_page_packet.json`

## Legacy Fast Survey Fallback

The trusted Alpha Fast Survey default is `A2_Al1_S1`:

| surface | pages | tiles |
|---|---:|---:|
| Artist | 2 | 24 |
| Album | 1 | 12 |
| Song | 1 | 12 |
| Total | 4 | 48 |

The earlier `A2_Al1_S1` packet remains useful as a fallback/test fixture, but it is not the Alpha 1 required intake target after the 2026-05-22 product decision.

The page packet schema supports configurable page counts for evaluated configs, render fixtures, and the required Alpha 1 intake. Core should not hard-code four pages.

## Tile Rendering Fields

Each tile includes:

- ordered render identity: `render_tile_id`, `display_order`
- typed `music_object_ref`
- `display.primary_text`
- `display.secondary_text`
- `display.object_type`
- `page_intent`
- `candidate_basis`
- `approved_graph_surface_ref`
- `graph_refs`
- `apple_exposure_prior`
- `response_capture`
- planned `evidence_export_linkage`

Artwork is not guaranteed in v0.1 packets. Core should render a stable text-first tile with a deterministic placeholder, object-type icon, or later-resolved artwork slot. Missing artwork must not block response capture.

## Response Cycle

Every tile exposes the same five internal response states:

| state | app label | normalized operation |
|---|---|---|
| `love` | Love | `positive_high` |
| `like` | Like | `positive_medium` |
| `ok` | OK | `waypoint_context` |
| `dont_like` | Not for me | `negative_scope_carefully` |
| `dont_know_enough` | Don't know enough | `familiarity_uncertainty` |

Pre-response slate examples may use `captured_state: null` and `normalized_operation: null`. Completed survey packets and evidence exports must carry one of the five states.

`dont_know_enough` is familiarity uncertainty, not dislike.

## Required Intake Progress Copy

Use concise progress labels that describe position, not certainty:

- `Artists 1 of 4`
- `Albums 1 of 2`
- `Songs 1 of 4`
- `Survey complete`

Avoid copy like "we know your taste" or "your Atlas is ready" at Survey completion. Safer language:

- "Thanks. Waymark has enough starting signals to build a first pass."
- "Next, Waymark turns these responses into provisional Atlas evidence."
- "Building your Atlas starter map and first missions."

Generation/waiting copy should remain provisional:

- "Building a first map from your Survey signals."
- "Preparing first missions from provisional evidence."
- "This is a starting point, not a final verdict."

## Page Source Labels

Each page can be described internally as one of:

- Apple-derived
- graph-derived
- mixed

Do not expose Apple-derived as taste truth. If user-facing copy mentions Apple at all, use "things you may know from Apple Music context" or "Apple Music helps Waymark choose recognizable starting points."

The fixed Alpha 1 packet should preserve page/tile metadata that lets Core, Atlas, and Mission Generation audit whether evidence came from Apple exposure context, graph structure, or both.

## Long-Press And Nuance

For Alpha 1, long-press nuance should be treated as polish unless Core/Product explicitly includes it. Required intake must be completable with the five visible response states alone.

If nuance is included:

- provide an explicit affordance in addition to long press
- preserve selected nuance as visible Signal evidence
- preserve shown-but-unselected nuance as weak context only
- keep freeform notes optional

## Tags And Notes

Every tile has:

- `selected_tags`
- `selected_tags_semantics: visible_signal_evidence`
- `shown_unselected_tags`
- `shown_unselected_tags_semantics: weak_non_selected_context`
- `note`

For Alpha, tags may be empty and notes may be null.

If tag chips are shown, selected tags become visible Signal evidence. Shown-but-unselected tags are weak context only and must not be treated as user-selected negative tag evidence.

Freeform notes are optional. If enabled, notes should be captured as visible user evidence suitable for later Signal or UserVocabularyTerm extraction. Notes must not be generated by the simulator or inferred from hidden profile truth.

## Local Persistence Expectations

Core should be able to persist:

- active packet id
- page id and page number
- tile response state
- selected tags
- shown-unselected tags snapshot
- note
- response timestamp
- evidence linkage ids

Core should not persist raw ranking scores, generation prompts, simulator hidden truth, hidden lookup state, or Profile Writer output as user evidence.

## Accessibility Constraints

Minimum Alpha expectations:

- every tile has accessible text from `display.primary_text`
- secondary text should identify artist context for album/song tiles when present
- response controls expose stable labels for all five states
- `dont_know_enough` copy should avoid sounding like a taste rejection
- tag chips should distinguish selected from merely shown
- keyboard/VoiceOver order should follow `display_order`

## Failure States

Core should handle:

- missing artwork: use placeholder
- unresolved or non-approved graph surface: fail closed or hide packet
- missing `music_object_ref` typed id: fail packet validation
- Apple prior absent: render normally
- evidence export linkage missing: do not submit to Atlas
- local response persistence failure: keep user on current page and retry
- Atlas upload/ingestion unavailable: persist local export and retry later

## Trusted-Tester Survey Feel Prompts

Use these after a tester completes the Survey:

1. Did this feel like Waymark was calibrating your taste map, or did it feel like a generic music quiz?
2. Were the five response choices enough to answer honestly?
3. Did `OK` feel different from `Like` in a useful way?
4. Did `Don't know enough` feel safe to choose?
5. Did any page feel too random, too obvious, or too much like recommendations?
6. Did the artist/album/song mix help you answer more precisely?
7. Were any tags or notes helpful, confusing, or missing?
8. Would you trust Waymark to make a first listening route from this evidence?
