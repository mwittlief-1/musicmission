# MissionGenerationDigestView Alpha v0.1

## Purpose

`MissionGenerationDigestView` is the minimum Alpha read model that Mission Generation may consume after in-app Survey evidence has been ingested into Atlas.

It is produced from user-visible Survey evidence, Atlas Signals, provisional `AtlasRoleAssignment` records, and `PossibleAtlasUpdateCandidate` records. It is not raw Survey payload, not Profile Writer output, and not promoted Atlas truth.

The view exists to answer one narrow question:

```text
What compact, auditable Atlas substrate is enough to generate the next mission hypotheses?
```

## Contract Files

- JSON Schema: `mission_generation_digest_view_alpha_v0_1.schema.json`
- Sample: `mission_generation_digest_view_alpha_v0_1.sample.json`

## Required Flow

```text
In-app Survey evidence
-> Survey Evidence Export / equivalent visible evidence atoms
-> Signal
-> provisional AtlasNode when needed
-> provisional AtlasRoleAssignment when policy allows
-> PossibleAtlasUpdateCandidate
-> MissionGenerationDigestView
-> Mission Generation
```

Mission Generation should not consume raw Survey payloads, page construction internals, hidden simulator truth, Profile Writer prose, or canonical graph mutation instructions.

## Minimum Required Fields

Top-level required fields:

- `record_type`
- `schema_version`
- `digest_id`
- `created_at`
- `user_id` or `fixture_profile_id`
- `source_context`
- `compactness_policy`
- `evidence_separation_policy`
- `no_hidden_data_checks`
- `evidence_ref_index`
- `candidate_roles`
- `recent_signals`
- `contradictions`
- `unresolved_questions`
- `taste_feature_summaries`
- `user_vocabulary_terms`
- `anti_overfitting_rules`
- `mission_relevant_constraints`
- `consumer_contract`

## Source Context

`source_context` identifies the visible evidence batch that produced the digest.

Required:

- `source_event_type = survey_completion`
- `source_event_id`
- `survey_session_id`
- `source_payload_ref`
- `source_payload_version`
- `visible_packet_id`
- `input_fingerprint`
- `atlas_digest_ref`
- `generated_from`

`generated_from` must list compact, production-facing sources only:

- `survey_evidence_export`
- `signal_ledger`
- `atlas_role_assignments`
- `possible_atlas_update_candidates`

## Evidence Separation Rules

The view must preserve these separations:

- `AtlasNode` represents the thing only.
- `AtlasRoleAssignment` is the role truth source.
- Survey-created roles must use `promotion_state = proposed | candidate | blocked`.
- `promotion_state = promoted` is forbidden in this view.
- `status`, `review_state`, and `promotion_state` remain separate.
- `signal_strength` and `interpretation_confidence` remain separate.
- Raw reaction, normalized signal, confidence, and candidate role are separate fields.
- Apple exposure is context only and must set `taste_truth = false`.
- `dont_know_enough` / familiarity uncertainty must not become negative evidence.
- Negative evidence must be scoped to the smallest justified object.

## Compactness Rules

The Alpha target is a single compact JSON object that can fit comfortably in Supabase JSONB and OpenAI structured-input calls.

Recommended caps:

- target JSON size: `<= 50 KB`
- hard review threshold: `> 80 KB`
- `candidate_roles`: max `24`
- `recent_signals`: max `36`
- `contradictions`: max `12`
- `unresolved_questions`: max `16`
- `taste_feature_summaries`: max `12`
- `user_vocabulary_terms`: max `24`
- evidence refs per item: max `8`

If a profile exceeds caps, choose mission-relevant evidence by:

1. review need;
2. role confidence and uncertainty;
3. contradiction severity;
4. frontier/dead-end/waypoint utility;
5. recency;
6. tag/note richness.

Do not solve size pressure by dropping evidence refs from claims that remain in the digest.

## Candidate Role Summaries

`candidate_roles[]` is the main Mission Generation input.

Each item must include:

- compact target object identity;
- `atlas_node_id`;
- `atlas_role_assignment_id`;
- `role_truth_source = atlas_role_assignment`;
- provisional `recommended_role`;
- downstream `candidate_pool_behavior`;
- separate lifecycle fields;
- confidence;
- evidence refs;
- mission-use summary.

`recommended_role` may be:

- `landmark`
- `region`
- `frontier`
- `dead_end`
- `waypoint`
- `unknown`
- `signal_only`

`candidate_pool_behavior` may be:

- `anchor`
- `bridge`
- `probe`
- `risky_probe`
- `waypoint`
- `trap`
- `exclude`
- `unknown`

The behavior hint helps Mission Generation route candidates. It is not an Atlas role.

## Recent Signal Summaries

`recent_signals[]` carries the compact evidence ledger Mission Generation needs.

Each Signal summary must keep separate:

- raw reaction;
- normalized signal;
- `signal_strength`;
- `interpretation_confidence`;
- selected tags;
- shown but unselected tags;
- user-visible note excerpt;
- Apple exposure context;
- evidence refs.

Mission Generation may use this for hypothesis design. It must not treat it as promoted truth.

## No-Hidden-Data Checks

`no_hidden_data_checks` must be present and must declare:

- raw Survey payload excluded;
- survey construction internals excluded;
- page layout mechanics excluded;
- randomization seed excluded;
- generator-visible inputs excluded;
- raw ranking scores excluded;
- Profile Writer output excluded;
- hidden simulator truth excluded;
- hidden corpus reactions excluded;
- simulator-private lookup status excluded;
- canonical graph mutation instructions excluded;
- all evidence refs resolve to visible Survey evidence.

These checks are not decorative metadata. A digest failing any check is not Mission Generation input.

## Required Builder Validation

The JSON Schema validates structure, enum values, caps, and hard guardrail fields. The digest builder must also run these cross-record checks before writing a digest:

- every `evidence_ref` used anywhere in the digest exists in `evidence_ref_index`;
- every `evidence_ref_index[].evidence_ref` resolves to a visible Survey Evidence Export atom or equivalent in-app Survey evidence atom;
- every `evidence_ref_index[]` item maps to exactly one `signal_id` and `response_id`;
- no `candidate_roles[].promotion_state` equals `promoted`;
- no `candidate_roles[].role_truth_source` differs from `atlas_role_assignment`;
- no Signal with `normalized_signal = familiarity_uncertainty` appears in `negative_evidence_refs`;
- every `apple_exposure_context.taste_truth` is `false`;
- no object contains page-construction, raw ranking, hidden simulator, Profile Writer, or canonical graph mutation fields;
- payload byte count is below `compactness_policy.hard_review_threshold_bytes`.

## Mapping Back to Survey Evidence Refs

Every mission-relevant claim in the digest maps back through `evidence_ref_index`.

Mapping chain:

```text
candidate_roles[].evidence.evidence_refs[]
recent_signals[].evidence_ref
contradictions[].positive_evidence_refs[]
contradictions[].negative_evidence_refs[]
unresolved_questions[].evidence_refs[]
taste_feature_summaries[].evidence_refs[]
user_vocabulary_terms[].evidence_refs[]
anti_overfitting_rules[].evidence_refs[]
mission_relevant_constraints[].evidence_refs[]

-> evidence_ref_index[].evidence_ref
-> evidence_ref_index[].response_id
-> evidence_ref_index[].survey_session_id
-> evidence_ref_index[].source_payload_ref
```

Each `evidence_ref_index[]` item also carries:

- `signal_id`
- `survey_item_id`
- `page_id`
- `stage`
- `page_number`
- `visible_packet_id`

This allows PM review, evidence audit, future correction, and user-data deletion without reopening raw Survey construction payloads.

## Consumer Contract

Mission Generation may use this view to generate:

- mission hypotheses;
- route strategy;
- candidate-pool requests;
- unresolved candidate-search slots;
- expected signal design;
- Mission Review feedback prompts.

Mission Generation must not use this view to:

- promote Atlas roles;
- mutate canonical graph;
- create final WWTSF copy;
- infer hidden graph meanings;
- broaden a scoped negative into a genre-level rejection;
- treat Apple exposure as taste truth.

## Supabase Storage Guidance

Minimum Alpha storage can be one row per digest:

- `digest_id` primary key
- `user_id`
- `fixture_profile_id`
- `schema_version`
- `source_event_id`
- `created_at`
- `payload_jsonb`
- `payload_byte_count`

Optional audit table:

- `digest_id`
- `evidence_ref`
- `signal_id`
- `response_id`
- `survey_session_id`
- `source_payload_ref`

The optional audit table is a convenience index, not a replacement for evidence refs inside the JSON payload.

## Open Questions

- Whether Alpha should store full note text in Signals only and pass note excerpts in this digest, or allow short full user notes in mission inputs.
- Whether `candidate_roles` should be split into role-specific arrays for easier dashboarding, or kept unified for compactness.
- Whether second-batch digests should extend this contract with `atlas_delta_ref` or use a separate MissionGenerationDeltaDigestView.
