# Resolver and Version Policy Sidecar Alpha v0

Version: `alpha_v0`

Status: `frozen_for_alpha_consumable_layer`

Controlling source:

```text
data/canonical_graph/normalization_pass_2/canonical_recording_versions.json
```

This sidecar hardens how app/local candidate pools should treat MusicKit resolution and version risk before first mission generation.

## Default Rule

```text
song_recording -> exact_recording_required
```

The resolver should assume exact recording specificity unless a candidate is explicitly marked `version_flexible` or `composition_search_ok`.

## Auto-Resolution Allowed

MusicKit auto-resolution may run only when all of these are true:

- candidate `review_status == approved`
- candidate `quarantine_reasons == []`
- no matching entry exists in `canonical_quarantine_queue.json`
- recording-version row has `review_status == approved`
- recording-version row has `survey_safe == true`
- `apple_music_resolution_policy` is `exact_recording_required` or `version_flexible`
- family is not `context_only`
- candidate is not from `suppressed_quarantined`

## Manual Review Required

Manual review is required when any of these are true:

- `apple_music_resolution_policy == manual_review_required`
- `recording_context` is `source_version`, `cover`, `remake`, `live`, `radio_edit`, `clean`, `explicit`, `remix`, `cast_recording`, `film_version`, or `traditional_arrangement`
- composition review is unresolved or needs human review
- Family 11 row has mix/edit/remix ambiguity
- Family 13 row has language/remix/collaboration ambiguity
- Family 14 row has work/composition/recording ambiguity
- Family 16 row has worship-standard or church-brand ambiguity
- entity is a show, film, cast recording, church brand, worship standard, classical work, traditional song, or composition-first object

## Blocked

Resolver, Supabase active candidate insertion, and OpenAI mission generation are blocked when any of these are true:

- source row is not from the approved Alpha candidate surfaces
- candidate `review_status != approved`
- candidate has non-empty `quarantine_reasons`
- entity appears in `canonical_quarantine_queue.json`
- recording-version row has `review_status == quarantined`
- recording-version row has `review_status == needs_review`
- recording-version row has `survey_safe == false`
- source bucket is `suppressed_quarantined`
- family is `context_only`
- `survey_intent == do_not_survey`
- wrong attribution is suspected

## Family Cautions

| family_id | caution | Alpha rule |
| --- | --- | --- |
| 11 | mix/edit/remix specificity | Electronic/dance rows need exact recording or explicit `version_flexible` policy before auto-resolution. |
| 13 | language/remix/collaboration specificity | Latin/global rows need variant clarity when the remix/language/collab changes the listening object. |
| 14 | work versus recording specificity | Jazz standards and classical-adjacent rows require work/recording distinction. |
| 16 | worship standard/church brand specificity | Worship/church-brand rows require brand/version handling unless explicitly approved. |

## Search Hint Requirements

| object_type | Required hint content |
| --- | --- |
| `artist` | display label |
| `album` | display label plus artist or primary credit when known |
| `song_recording` | display label plus artist/credit; include recording context when not an ordinary original |

## OpenAI Payload Policy

OpenAI may see:

- `music_kit_search_hint`
- `apple_music_resolution_policy`
- `version_risk_note`
- object identity and mission role fields

OpenAI must not see:

- raw Apple private library payloads
- Apple auth tokens
- quarantined rows
- suppressed rows
- manual-review-only rows in default mission generation
