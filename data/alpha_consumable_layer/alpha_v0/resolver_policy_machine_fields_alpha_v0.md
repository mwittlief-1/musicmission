# Resolver Policy Machine Fields Alpha v0

Version: `alpha_v0`

Status: `frozen_for_alpha_consumable_layer`

This artifact supplies machine-readable resolver fields for App/MusicKit, Supabase, and OpenAI gating. It is an Alpha overlay; it does not mutate the canonical graph.

## Required Candidate Fields

- `music_object_ref`
- `music_kit_search_hint`
- `apple_music_resolution_policy`
- `version_risk_note`
- `review_status`
- `quarantine_reasons`
- `eligible_for_supabase`
- `eligible_for_openai`

## Required Song Recording Fields

- `recording_id`
- `composition_id`
- `recording_context`
- `display_artist_credit`
- `release_year_policy`
- `apple_music_resolution_policy`
- `survey_safe`
- `review_status`
- `composition_review_classification`
- `survey_safe_reason`
- `resolver_action`

## Resolver Action Counts

| resolver_action | count |
| --- | ---: |
| auto_resolve_allowed | 1857 |
| blocked | 60 |

## Apple Music Resolution Policy Counts

| policy | count |
| --- | ---: |
| exact_recording_required | 1857 |
| manual_review_required | 60 |

## Rule

Rows with `resolver_action != auto_resolve_allowed` are blocked from Apple Music auto-resolution, default Mission Generation, OpenAI prompt payloads, and Supabase active candidate insertion unless a later human review writes an explicit override.
