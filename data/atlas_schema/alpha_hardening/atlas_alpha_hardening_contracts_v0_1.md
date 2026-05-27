# Atlas Alpha Hardening Contracts v0.1

Generated: 2026-05-21

## Purpose

This packet completes the non-dependent Atlas Schema backlog items for the TestFlight Alpha planning pass. It turns the accepted Atlas Schema v0.1 into practical app-ingestion, read-model, delta, correction, candidate-pool, WWTSF, and privacy guidance without adding automatic promotion.

## 1. App Mission Evidence Ingestion Mapping

Core app exports should become Atlas `Signal` records through a mission evidence adapter. The adapter should be append-only and should not write promoted Atlas state.

### App Evidence Sources

| app evidence | Signal source | normalized signal | notes |
| --- | --- | --- | --- |
| item reaction: love/like | `mission` | `positive_high` / `positive_medium` | Taste evidence scoped to mission item. |
| item reaction: ok/context | `mission` | `contextual_waypoint` | Useful context, not Landmark evidence. |
| item reaction: dislike/not for me | `mission` | `negative_scope_carefully` | Scoped negative, never broad genre rejection by itself. |
| skipped item | `mission` | `skip_or_no_signal` | Behavior evidence; not automatic dislike. |
| no reaction after playback | `mission` | `skip_or_no_signal` | Weak evidence, usually low interpretation confidence. |
| note text | `note` or `mission` | `explicit_note_signal` where supported | High interpretive value if specific. |
| tag/chip selection | `mission` | tied to parent reaction signal | Selected tags are user-visible evidence. |
| shown but unselected chip | `mission` | weak/non-selected context | Store separately from selected tags. |
| playback completion | `playback` | `exposure_or_completion_context` | Exposure/completion context, not taste truth. |
| resolver result | `import` | `resolution_context` | Catalog identity support, not taste truth. |
| wrong-version report | `review` | `resolution_correction_needed` | Should seed resolution/correction candidate. |

### Minimum Signal Fields From App Export

Each app-derived `Signal` should carry:

- `signal_id`
- `user_id`
- `source`
- `source_context.source_event_id`
- `source_context.mission_id`
- `source_context.mission_item_id`
- `source_context.reaction_session_id`
- `subject_music_object_ref`
- `raw_reaction`
- `normalized_signal`
- `reaction_value`
- `signal_strength`
- `interpretation_confidence`
- `observed_user_tags`
- `shown_unselected_tags`
- `user_note`
- `occurred_at`
- `captured_at`

### Provisional Skip / No-Signal Policy

Until Product approves a final skip policy:

- skip is behavioral evidence, not negative taste evidence;
- no-signal is uncertainty, not dislike;
- repeated skips may create a `PossibleAtlasUpdateCandidate` with `proposed_action = pause_path` or `needs_review`;
- no skip/no-signal event may promote or demote a role by itself.

## 2. Survey Evidence Export Acceptance Criteria

A Survey Evidence Export is Atlas-ingestible only when:

- it contains visible evidence atoms under an Atlas-ingestable namespace;
- every ingestible atom has a stable `evidence_ref`;
- every `evidence_ref` resolves inside the same visible export;
- unresolved response refs are quarantined outside Atlas ingestion;
- each atom includes typed `music_object_ref`;
- selected tags and shown-unselected tags are separate arrays;
- raw reaction and normalized reaction operation are separate;
- `evidence_strength_hint` is present only as Survey-side hint and is not final Atlas confidence;
- comparison-set context is preserved when present;
- page intent is preserved as context, not user-facing truth;
- Apple exposure prior uses `taste_truth = false`;
- `dont_know_enough` maps to familiarity uncertainty, never negative evidence;
- hidden simulator truth, hidden corpus reactions, simulator lookup state, raw ranking scores, generator-visible inputs, page construction internals, and Profile Writer prose are excluded from Atlas-ingestable records.

Recommended acceptance outputs:

- `validation_report.json`
- `signals.jsonl`
- `atlas_nodes.json`
- `atlas_role_assignments.json`
- `possible_atlas_update_candidates.json`
- `atlas_digest_view.json`
- `size_report.md`

## 3. PossibleAtlasUpdateCandidate Patch Shapes

`PossibleAtlasUpdateCandidate` remains extensible, but common Alpha payloads should use typed patch shapes.

### Survey-Seeded Role Candidate

```json
{
  "proposed_record_type": "atlas_role_assignment",
  "proposed_action": "create_or_update_role_candidate",
  "proposed_payload": {
    "patch_shape": "survey_seeded_role_candidate_v0_1",
    "target_atlas_node_id": "atlas_node:...",
    "recommended_role": "frontier",
    "candidate_pool_behavior": "probe",
    "status": "provisional",
    "review_state": "unreviewed",
    "promotion_state": "candidate",
    "scope_limit": "artist_level_only",
    "evidence_signal_ids": ["signal:..."],
    "evidence_refs": ["artist_page_001:artist:04:Example:love"],
    "canonical_graph_mutation_allowed": false
  }
}
```

### Mission Review Role Refinement

```json
{
  "proposed_record_type": "atlas_role_assignment",
  "proposed_action": "refine_role_candidate",
  "proposed_payload": {
    "patch_shape": "mission_review_role_refinement_v0_1",
    "target_role_assignment_id": "role:...",
    "recommended_role": "waypoint",
    "recommended_promotion_state": "candidate",
    "confidence_delta": 0.12,
    "scope_change": "recording_level_only",
    "review_requirement": {
      "required": true,
      "reason": "Mission feedback remains mixed."
    },
    "evidence_signal_ids": ["signal:mission:..."],
    "evidence_refs": ["mission_review:..."],
    "canonical_graph_mutation_allowed": false
  }
}
```

### Pause / Block / Demotion Recommendation

```json
{
  "proposed_record_type": "atlas_role_assignment",
  "proposed_action": "pause_or_block_candidate",
  "proposed_payload": {
    "patch_shape": "role_pause_block_recommendation_v0_1",
    "target_role_assignment_id": "role:...",
    "recommended_promotion_state": "blocked",
    "pause_reason": "repeated skips or scoped negative evidence",
    "evidence_signal_ids": ["signal:..."],
    "evidence_refs": ["mission_review:..."],
    "canonical_graph_mutation_allowed": false
  }
}
```

Common rules:

- `canonical_graph_mutation_allowed` must be `false`;
- generated hypotheses set `generated_hypothesis_only = true`;
- evidence refs are required for every recommendation;
- promotion remains a separate reviewed write.

## 4. Correction / Superseding Atom Policy

Survey and app evidence are append-only. Corrections must not rewrite historical evidence atoms.

Allowed correction atom types:

- `supersedes_response`
- `retracts_response`
- `corrects_music_object_ref`
- `corrects_reaction`
- `corrects_tag`
- `corrects_note`
- `marks_wrong_version`
- `marks_duplicate_signal`

Minimum correction atom fields:

- `correction_atom_id`
- `source`
- `source_event_id`
- `supersedes_evidence_ref`
- `correction_type`
- `corrected_payload`
- `reason`
- `created_at`
- `user_visible`
- `review_state`

Atlas current state is derived by applying correction atoms over the append-only ledger. Historical Signals remain auditable and should be marked `status = suppressed` or `review_state = rejected` only through explicit derived state, not by deleting source evidence.

## 5. Manual Promotion / Demotion Policy Draft

Automatic promotion is out of scope for Alpha. Manual/reviewed promotion may be represented when all criteria are satisfied.

### Candidate to Promoted

Minimum reviewed promotion requirements:

- at least one explicit user-visible positive Signal;
- recurrence across object scope, time, or mission context;
- no unresolved high-severity contradiction;
- clear scope limit;
- evidence refs attached;
- reviewer identity or reviewed system event;
- `review_state = reviewed`;
- promotion decision stored separately from Survey/Mission Generation.

### Candidate to Blocked

Block when:

- evidence is too thin;
- contradiction is unresolved;
- object identity is unresolved;
- graph/family labels are unavailable and required for the claim;
- a generated hypothesis lacks review;
- Apple exposure is the only support.

### Candidate to Demoted

Demotion requires:

- new negative, skip, correction, or contradiction evidence;
- evidence refs;
- explanation of scope;
- no deletion of prior positive Signals.

## 6. Mission Feedback to AtlasDelta Proof

The closed-loop proof path is:

```text
reaction session
-> mission Signals
-> PossibleAtlasUpdateCandidate records
-> updated AtlasDigestView
-> AtlasDelta
-> adaptive second-batch mission input
```

Existing proof artifacts:

- `data/closed_loop_simulation/a3_first_batch_learning_v0_1_adaptive_contract_v0_1/profile_01/atlas_update_records_after_batch_1.json`
- `data/closed_loop_simulation/a3_first_batch_learning_v0_1_adaptive_contract_v0_1/profile_01/atlas_digest_after_batch_1.json`
- `data/closed_loop_simulation/a3_first_batch_learning_v0_1_adaptive_contract_v0_1/profile_01/atlas_delta_after_batch_1.json`
- matching profile 05 and profile 06 artifacts in the same directory.

Acceptance checks already demonstrated:

- mission feedback ingests as Signals / update candidates / confidence deltas;
- `AtlasDelta` is generated after batch one;
- second-batch missions require Delta references;
- no canonical graph mutation;
- no automatic Atlas promotion.

## 7. App-Facing Starter Read Model

Before final Atlas UI, the app may safely show a small starter read model if Product chooses to expose it.

Safe fields:

- candidate role display name;
- provisional role label;
- confidence band;
- scope warning;
- evidence count;
- top evidence refs or source labels;
- unresolved question text;
- "needs mission test" or "needs review" state;
- recent learning summary generated from `AtlasDelta` source inputs.

Default-off fields until Product decides placement:

- full graph/family/archetype labels;
- final-sounding Region names;
- promoted-role language;
- generated WWTSF prose;
- hidden evaluator notes;
- raw debug provenance.

Recommended Alpha stance: app-safe starter view may exist behind a feature flag, with all roles labeled provisional/candidate unless manually reviewed.

## 8. AtlasDelta User-Facing Summary Guardrail

`AtlasDelta.user_facing_summary_inputs` are source bullets, not final copy.

Rules:

- keep `not_final_copy = true` when represented;
- preserve evidence refs;
- include confidence/scope caveats;
- do not present promotion/demotion recommendations as completed truth changes;
- default UI display is hidden/off until Product chooses placement;
- WWTSF or App copy may render from these bullets only with a separate copy/review step.

## 9. Privacy / Deletion Inventory

Atlas Alpha data classes:

| data class | examples | deletion/review notes |
| --- | --- | --- |
| Signals | survey reactions, mission reactions, skips, playback events | User evidence; must be exportable and deletable/suppressible. |
| Notes | Survey notes, mission notes, correction reasons | User-authored; higher privacy sensitivity. |
| Tags/chips | selected tags, shown-unselected tags | Selected tags are evidence; shown-unselected tags are weak context. |
| Apple exposure context | library/import/familiarity hints | Exposure context only; not taste truth. |
| Atlas interpretations | role assignments, feature states, contradictions | Derived user profile data; must be explainable/correctable. |
| Update candidates | Survey-seeded and Mission Review proposals | Not truth; preserve evidence refs and review state. |
| AtlasDigestView | compact read model | Derived; regenerate after deletion/correction. |
| AtlasDelta | change summary | Derived; regenerate after deletion/correction. |
| Model packets | node interpretation, WWTSF substrate, mission inputs | External model context; keep raw debug and hidden truth excluded. |
| Exports | JSON/Markdown evidence exports | Must respect user deletion and product retention policy. |

Release/Privacy still owns final retention periods, user-visible privacy copy, and deletion UX. Atlas should keep all derived objects traceable to source evidence so suppression/deletion can cascade.

## 10. Candidate Pool Builder Read Path Guide

Candidate Pool Builder should consume:

- `AtlasRoleAssignment`;
- `AtlasDigestView`;
- `MissionGenerationDigestView`;
- `candidate_pool_behavior` hints;
- confidence and scope fields;
- evidence refs for audit.

It should not consume:

- role-like summaries from `AtlasNode`;
- raw Atlas tables without digest filtering;
- raw Survey payloads;
- hidden simulator truth;
- canonical graph rows marked quarantined.

Recommended mapping remains downstream:

| Atlas role | candidate-pool behavior examples |
| --- | --- |
| `landmark` | `anchor` |
| `region` | `anchor`, `bridge` |
| `frontier` | `probe`, `risky_probe` |
| `dead_end` | `trap`, `exclude` |
| `waypoint` | `waypoint`, `bridge` |
| `unknown` | `probe` |
| `signal_only` | `unknown`, `resolve_first` |

## 11. WWTSF Substrate Guidance

WWTSF should consume Atlas read models, not raw Survey payloads.

Allowed inputs:

- `AtlasDigestView`;
- `AtlasDelta`;
- interpreted update candidates;
- selected Signal summaries;
- user vocabulary terms;
- anti-overfitting rules;
- scope/confidence warnings.

Forbidden inputs:

- raw Survey payload as primary source;
- hidden fake-profile truth;
- Profile Writer output;
- unavailable family/archetype meanings;
- canonical graph mutation instructions;
- generated missions as truth.

Model posture:

- GPT-5.5 remains fallback/baseline where mini guardrails do not pass;
- mini outputs need functional guardrail checks, not only schema validity;
- WWTSF substrate is source material, not final user-facing copy.

## 12. Alpha 1 Post-Brand Review Addendum

Product decisions captured on 2026-05-22 add three Atlas-facing requirements.

### Fixed Survey Intake

Alpha 1 intake is required and fixed at:

- 4 artist pages;
- 2 album pages;
- 4 song pages;
- no optional early exit in the normal first-run flow.

Atlas accepts this shape through the existing Survey Evidence Export ingestion contract as long as the export declares the page-count config and all visible completed tile responses become evidence atoms. Survey evidence remains evidence only. It may seed Signals, provisional role assignments, update candidates, digest views, and MissionGenerationDigestView inputs, but it must not promote Atlas truth.

The machine-readable Atlas profile is:

`data/atlas_schema/alpha_hardening/atlas_alpha1_ingestion_profile_v0_1.json`

The validation gate is:

```bash
python3 scripts/validate_atlas_alpha1_intake_profile.py \
  --survey-export path/to/A4_Al2_S4_survey_evidence_export.json
```

### "Building Your Atlas" Status Copy

The phrase "Building your Atlas" is allowed as progress/status copy after Survey completion if nearby copy preserves provisionality.

Safe supporting phrases:

- "Reading your Survey evidence"
- "Finding a careful first route"
- "Preparing your first mission batch"
- "Checking uncertainty before we recommend anything"

Do not imply confirmed Landmarks, permanent Regions, a final taste profile, or Apple Music-proven taste.

### Uploaded Evidence

Supabase upload/sync is compatible with Atlas if it remains:

- consent-gated;
- append-only;
- provisional;
- auditable to source evidence;
- free of hidden simulator/evaluator/debug data;
- unable to promote Atlas roles by itself;
- unable to mutate canonical graph.

Final privacy/terms copy is required before enabling upload, but the Atlas evidence policy does not depend on the final wording.

## 13. Live Alpha Diagnostic Artifact Classification

Live Alpha diagnostics are support/audit artifacts first. They may help explain the chain from Apple Music signal to Survey to generation to import, but they do not become Atlas truth by default.

### Diagnostic Artifact Classes

| artifact type | Atlas-ingestable? | allowed Atlas use | must not become |
| --- | --- | --- | --- |
| `apple_music_signal_payload` | no, except as referenced exposure context on a user-visible Survey or mission Signal | Exposure/familiarity context; resolver/search context; diagnostics for Survey construction. | Taste truth, role evidence, promoted affinity, or final profile copy. |
| `survey_page_selection_audit` | no | Page/tile explainability; displayed-page validation; quarantine diagnosis; candidate-basis audit. | User-facing Atlas claim, Signal, role truth, or evidence of taste by itself. |
| `survey_evidence_export` | yes, for valid visible evidence atoms only | Primary Survey-to-Signal source; may create AtlasNode refs, provisional AtlasRoleAssignment, PossibleAtlasUpdateCandidate, AtlasDigestView, and MissionGenerationDigestView. | Promoted Landmark/Region/Frontier/Dead End/Waypoint truth. |
| `mission_generation_request_packet` | no | Model/request audit; digest/candidate-pool hash lineage; support replay where policy allows. | Signal, user taste evidence, Atlas role assignment, or canonical graph mutation instruction. |
| `mission_generation_result` | limited | Structured generated hypotheses may become `PossibleAtlasUpdateCandidate` with `generated_hypothesis_only = true` and review required. | Promoted Atlas truth, Signal, final WWTSF copy, or mission-review evidence before user interaction. |
| `mission_import_result` | limited | Operational import audit; imported mission IDs; resolver/import status; app validation outcome. | Taste Signal, role promotion, or negative taste evidence when import fails. |
| `client_error_event` | no | Support diagnosis; missing-link explanation; retry/runbook context. | Taste Signal, Atlas role evidence, or user-facing Atlas copy. |

### Atlas-Ingestible Evidence Rule

An artifact is Atlas-ingestable only when it contains a user-visible evidence atom or a reviewed correction atom. For Alpha this means:

- valid `survey_evidence_export` atoms may become Survey `Signal` records;
- valid mission reactions, notes, tags, skips, playback events, and review events may become app/mission `Signal` records;
- generated mission output may propose `PossibleAtlasUpdateCandidate` records only when explicitly structured for that purpose;
- operational artifacts may be linked from provenance, but are not themselves evidence of preference.

### Diagnostics That Stay PM / Support Only

The following must remain outside Atlas-ingestable state unless a later reviewed evidence adapter explicitly converts a user-visible atom:

- raw Apple Music samples and endpoint snapshots;
- Survey page-construction audit rows;
- candidate scoring, ranking, and exclusion internals;
- generation prompts, model request packets, and raw model traces;
- backend run statuses by themselves;
- app import failures, validation errors, and client exceptions.

These can be stored in a diagnostic table or support artifact store. They may be referenced by ID/hash from validation reports, but should not be copied into `Signal`, `AtlasRoleAssignment`, `AtlasDigestView`, or `AtlasDelta` except as bounded provenance summaries.

### Review-Needed Import Tolerance

Trusted Alpha may store structurally valid `review_needed` generation results and continue attempts toward the target mission count. Atlas interpretation rules remain unchanged:

- `review_needed` is an operational/review state, not negative user evidence;
- importing an app-valid mission with review flags does not promote Atlas roles;
- review flags should be preserved for Mission Generation and QA;
- user interaction with the imported mission is what can later create mission Signals.

Machine-readable companion:

`data/atlas_schema/alpha_hardening/atlas_live_smoke_diagnostic_contract_v0_1.json`

## 14. Live Alpha Audit Link Semantics

Atlas needs stable links across diagnostics without broadening what counts as evidence. Core and Infrastructure may store richer diagnostic artifacts, while Atlas ingestion continues to consume only approved evidence atoms.

### Common Link Envelope

Every diagnostic artifact should carry these fields when available:

| field | requirement | purpose |
| --- | --- | --- |
| `artifact_id` | required | Stable artifact identity for support and replay. |
| `artifact_type` | required | One of the diagnostic artifact classes above. |
| `tester_alias` | required for PM review when available | Lets PM query one trusted Alpha run without exposing normal UI internals. |
| `supabase_user_id` | recommended | Auth/account linkage. |
| `survey_session_id` | required for Survey, generation, and Survey-derived artifacts | Joins Apple signal, page selection, Survey export, digest, and generation request. |
| `client_request_id` | required for generation request/result/import chains | App-generated request join key before backend run ID exists. |
| `generation_run_id` | required for backend generation result and import result | Joins Supabase audit row to client import outcome. |
| `mission_id` | required for mission import and mission evidence artifacts when a mission exists | Joins generated mission, imported app mission, and later mission feedback. |
| `evidence_ref` | required only for Atlas-ingestable evidence atoms | Durable link from Signal to visible Survey/mission evidence. |
| `source_app_version` / `source_app_build` | required | Reconstructs app behavior for the run. |
| `client_created_at` | required | Client-side event ordering. |
| `payload_sha256` | required for uploaded artifact payloads | Verifies replay/audit identity without duplicating large payloads. |
| `redaction_level` | required | Separates support diagnostics from Atlas-ingestable evidence. |

Do not invent IDs. Missing IDs should be omitted or explicitly `null` according to the storage contract. A later artifact may backfill linkage through a correction/link event, not by mutating the original evidence atom.

### Artifact-Specific Required Links

| artifact type | required links | recommended links |
| --- | --- | --- |
| `apple_music_signal_payload` | `artifact_id`, `artifact_type`, `tester_alias`, `source_app_version`, `source_app_build`, `client_created_at`, `payload_sha256` | `supabase_user_id`, `survey_session_id` if captured before Survey generation. |
| `survey_page_selection_audit` | `survey_session_id`, `artifact_id`, displayed `page_id` values, `source_app_version`, `source_app_build` | candidate surface refs, typed music refs, prior visible response refs, Apple exposure context IDs. |
| `survey_evidence_export` | `survey_session_id`, valid `evidence_ref` values, `response_id`, `survey_item_id`, `page_id`, `stage`, `page_number` | `client_request_id` for the generation request that used the export. |
| `mission_generation_request_packet` | `client_request_id`, `survey_session_id`, digest ref/hash, candidate-pool ref/hash | app build, requested batch size, attempt index, prior generation IDs. |
| `mission_generation_result` | `client_request_id`, `generation_run_id`, status, validation summary | generated mission IDs, token/latency/model versions, backend audit row ID. |
| `mission_import_result` | `generation_run_id`, local import status, imported mission IDs when present | `client_request_id`, validation errors, local mission count after import. |
| `client_error_event` | `artifact_id`, error category, app version/build, client timestamp | associated `survey_session_id`, `client_request_id`, `generation_run_id`, or `mission_id` when known. |

### Quarantined Survey Response Semantics

Quarantined Survey responses remain visible in diagnostics and validation reports, but they do not become `Signal` records.

Required quarantine fields:

- `quarantine_id`;
- `survey_session_id`;
- `response_id` when available;
- attempted or missing `evidence_ref`;
- `page_id` / `survey_item_id` when available;
- `quarantine_reason`;
- `diagnostic_artifact_id`;
- `created_at`;
- `review_state`.

Allowed `quarantine_reason` values:

- `missing_displayed_page`;
- `missing_evidence_ref`;
- `invalid_response_state`;
- `duplicate_response`;
- `schema_mismatch`;
- `object_ref_resolution_failed`;
- `page_count_mismatch`;
- `hidden_or_private_source`;
- `consent_missing`;
- `unknown_needs_review`.

If a quarantined response is later repaired, the repair should create a new reviewed correction or superseding atom. The original quarantine row should remain auditable and should not be silently converted into a Signal.

### Evidence Ref Boundary

`evidence_ref` is reserved for user-visible Survey or mission evidence that Atlas may ingest. Support-only artifacts should use `artifact_id`, `payload_sha256`, `client_request_id`, `generation_run_id`, or `quarantine_id` instead of inventing evidence refs.

## 15. Current Cross-Lane Caveats

- Core app export fields should be checked against the app evidence Signal mapping when the app export shape is finalized.
- A fixed `A4_Al2_S4` Survey Evidence Export fixture is still needed from Survey for the full Alpha 1 intake proof.
- Release/Privacy must approve final retention and deletion policy.
- Product/Core/Atlas must choose where, if anywhere, starter Atlas and `AtlasDelta` summaries appear in Alpha UI.
