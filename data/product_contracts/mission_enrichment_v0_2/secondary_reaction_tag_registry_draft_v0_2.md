# Secondary Reaction Tag Registry Draft v0.2

Status: Runtime-candidate registry note. The machine-readable candidate registry is `registry/secondary_reaction_tag_registry_v0_2.json`.

This draft registry defines universal secondary reaction tags for Mission Enrichment v0.2. Tags must be stable, genre-neutral, display-safe, and useful for Atlas learning.

Song affinity tags may be specific. Secondary reaction tags should stay universal.

## Registry Rules

- The model may select only from approved tag IDs.
- The model may not invent runtime tag IDs.
- Each tag declares the primary reactions where it may appear.
- Each tag declares the intended Atlas effect.
- Facet-linked tags may declare allowed affinity facets.
- Display labels should be natural chips, not raw ontology tags.
- For v0.2, `display_label` is locked to the approved registry label; model-written label variants are not allowed.

## Positive / Confirming Tags

| Tag ID | Display label | Valid primary reactions | Atlas effect | Allowed facets |
| --- | --- | --- | --- | --- |
| `HOOK_WORKED` | The hook worked | `love`, `like` | `strengthen_songcraft_signal` | `form_container`, `melody_harmony` |
| `MELODY_WORKED` | The melody worked | `love`, `like` | `strengthen_melody_signal` | `melody_harmony` |
| `GROOVE_WORKED` | The groove worked | `love`, `like` | `strengthen_rhythm_body_signal` | `rhythm_body` |
| `BEAT_WORKED` | The beat worked | `love`, `like` | `strengthen_beat_or_rhythm_signal` | `rhythm_body`, `production` |
| `VOICE_WORKED` | The voice worked | `love`, `like` | `strengthen_vocal_signal` | `vocal_performance` |
| `PERFORMANCE_WORKED` | The performance worked | `love`, `like` | `strengthen_performance_signal` | `vocal_performance`, `instrumental_performance` |
| `LYRICS_WORKED` | The words worked | `love`, `like` | `strengthen_lyric_or_story_signal` | `lyrics_language`, `narrative_theme` |
| `MOOD_WORKED` | The mood worked | `love`, `like` | `strengthen_mood_signal` | `emotion_theme`, `atmosphere` |
| `ENERGY_WORKED` | The energy worked | `love`, `like` | `strengthen_energy_signal` | `energy_profile`, `rhythm_body` |
| `SOUND_WORKED` | The sound worked | `love`, `like` | `strengthen_sound_or_texture_signal` | `sonic_texture`, `production` |
| `PRODUCTION_WORKED` | The production worked | `love`, `like` | `strengthen_production_signal` | `production`, `sonic_texture` |
| `ARRANGEMENT_WORKED` | The arrangement worked | `love`, `like` | `strengthen_arrangement_signal` | `arrangement`, `form_container` |
| `STORY_WORKED` | The story worked | `love`, `like` | `strengthen_story_or_theme_signal` | `narrative_theme`, `lyrics_language` |
| `BUILD_WORKED` | The build worked | `love`, `like` | `strengthen_dynamic_shape_signal` | `dynamic_shape`, `arrangement`, `form_container` |
| `SURPRISED_ME` | This surprised me | `love`, `like`, `ok` | `open_or_strengthen_novelty_signal` | None |
| `WOULD_TRY_MORE_NEARBY` | I'd try more nearby | `love`, `like`, `ok` | `open_nearby_exploration` | None |

## Qualified Positive / Split-Signal Tags

| Tag ID | Display label | Valid primary reactions | Atlas effect | Allowed facets |
| --- | --- | --- | --- | --- |
| `GOOD_NOT_CORE` | Good, not core | `like`, `ok` | `mark_waypoint_not_landmark` | None |
| `GOOD_NOT_FOR_ME` | Good, not for me | `ok`, `dislike` | `mark_respect_without_appetite` | None |
| `RIGHT_SOUND_WRONG_SONG` | Right sound, wrong song | `like`, `ok`, `dislike` | `split_affinity_from_song_object` | `sonic_texture`, `production`, `arrangement` |
| `RIGHT_ARTIST_WRONG_TRACK` | Right artist, wrong track | `like`, `ok`, `dislike` | `split_artist_interest_from_track_fit` | None |
| `RIGHT_MOOD_WRONG_MOMENT` | Right mood, wrong moment | `like`, `ok` | `mark_context_dependence` | `emotion_theme`, `atmosphere`, `context_rule` |
| `NEEDS_MORE_CONTEXT` | Might need more context | `like`, `ok` | `defer_until_contextual_test` | None |
| `NEEDS_ANOTHER_LISTEN` | Needs another listen | `like`, `ok` | `mark_uncertain_repeat_test` | None |
| `FAMILIAR_BUT_STILL_WORKS` | Familiar, but still works | `love`, `like`, `ok` | `confirm_despite_familiarity` | None |
| `RESPECT_MORE_THAN_WANT` | I respect it more than I want it | `ok`, `dislike` | `mark_respect_without_appetite` | None |

## Waypoint / Uncertainty Tags

| Tag ID | Display label | Valid primary reactions | Atlas effect | Allowed facets |
| --- | --- | --- | --- | --- |
| `KEEP_AS_WAYPOINT` | Keep as waypoint | `like`, `ok` | `preserve_as_navigation_reference` | None |
| `INTERESTING_NOT_MINE` | Interesting, not mine | `ok`, `dislike` | `mark_boundary_or_low_appetite` | None |
| `MOOD_DEPENDENT` | Mood-dependent | `like`, `ok` | `mark_mood_dependence` | `emotion_theme`, `atmosphere`, `context_rule` |
| `CONTEXT_DEPENDENT` | Context-dependent | `like`, `ok` | `mark_context_dependence` | `context_rule`, `activity_context`, `social_context` |
| `TOO_FAMILIAR_TO_JUDGE` | Too familiar to judge | `love`, `like`, `ok` | `discount_due_to_familiarity` | None |
| `NOT_TODAY_MAYBE_LATER` | Not today, maybe later | `ok`, `dislike` | `mark_temporal_context_dependence` | `context_rule`, `emotion_theme` |
| `UNSURE_BUT_CURIOUS` | Unsure, but curious | `ok`, `like` | `open_frontier_with_uncertainty` | None |

## Negative / Boundary Tags

| Tag ID | Display label | Valid primary reactions | Atlas effect | Allowed facets |
| --- | --- | --- | --- | --- |
| `TOO_INTENSE` | Too intense | `ok`, `dislike` | `weaken_intensity_fit` | `energy_profile`, `sonic_texture`, `emotion_theme`, `rhythm_body` |
| `TOO_LOW_ENERGY` | Too low-energy | `ok`, `dislike` | `weaken_low_energy_fit` | `energy_profile`, `rhythm_body`, `dynamic_shape` |
| `TOO_SMOOTH` | Too smooth | `ok`, `dislike` | `weaken_smoothness_fit` | `production`, `sonic_texture`, `vocal_performance` |
| `TOO_ROUGH` | Too rough | `ok`, `dislike` | `weaken_roughness_fit` | `production`, `sonic_texture`, `vocal_performance` |
| `TOO_BUSY` | Too busy | `ok`, `dislike` | `weaken_density_fit` | `arrangement`, `production`, `rhythm_body` |
| `TOO_SPARSE` | Too sparse | `ok`, `dislike` | `weaken_sparseness_fit` | `arrangement`, `production`, `dynamic_shape` |
| `TOO_REPETITIVE` | Too repetitive | `ok`, `dislike` | `weaken_repetition_fit` | `form_container`, `rhythm_body`, `production` |
| `TOO_PREDICTABLE` | Too predictable | `ok`, `dislike` | `weaken_predictability_fit` | `form_container`, `melody_harmony`, `production` |
| `TOO_ABSTRACT` | Too abstract | `ok`, `dislike` | `weaken_abstraction_fit` | `form_container`, `lyrics_language`, `melody_harmony`, `production` |
| `TOO_DRAMATIC` | Too dramatic | `ok`, `dislike` | `weaken_drama_fit` | `vocal_performance`, `emotion_theme`, `arrangement` |
| `TOO_DETACHED` | Too detached | `ok`, `dislike` | `weaken_detachment_fit` | `vocal_performance`, `emotion_theme`, `production` |
| `VOICE_DID_NOT_WORK` | The voice did not work | `ok`, `dislike` | `weaken_vocal_signal` | `vocal_performance` |
| `BEAT_DID_NOT_WORK` | The beat did not work | `ok`, `dislike` | `weaken_beat_or_rhythm_signal` | `rhythm_body`, `production` |
| `LYRICS_DID_NOT_WORK` | The words did not work | `ok`, `dislike` | `weaken_lyric_or_story_signal` | `lyrics_language`, `narrative_theme` |
| `PRODUCTION_DID_NOT_WORK` | The production did not work | `ok`, `dislike` | `weaken_production_signal` | `production`, `sonic_texture` |
| `NO_CLEAR_HOOK` | No clear hook | `ok`, `dislike` | `weaken_songcraft_or_hook_signal` | `form_container`, `melody_harmony` |
| `NOT_MY_LANE` | Not my lane | `ok`, `dislike` | `mark_broad_boundary` | None |
| `LESS_LIKE_THIS` | Less like this | `dislike` | `reduce_nearby_recommendation_weight` | None |
| `DID_NOT_HOLD_ATTENTION` | Did not hold my attention | `ok`, `dislike` | `weaken_attention_or_engagement_fit` | `form_container`, `dynamic_shape`, `arrangement`, `production`, `rhythm_body` |
| `WRONG_VERSION_OR_RECORDING` | Wrong version or recording | `ok`, `dislike` | `mark_version_or_recording_issue` | None |

## Product Review Flags

These draft items may need special review:

- `RIGHT_ARTIST_WRONG_TRACK`: Useful, but may imply artist familiarity. Runtime candidate gates it behind known artist context or explicit artist-level evidence.
- `NEEDS_MORE_CONTEXT`: Useful for album, jazz, classical, long-form, or mood-dependent music. Runtime candidate gates it behind album/context/long-form applicability.
- `RESPECT_MORE_THAN_WANT`: Clear for many users, but slightly critic-coded. Product should approve tone.
- `TOO_ABSTRACT`: Useful across jazz, electronic, experimental, and art-pop cases, but Product should confirm it is not too judgmental.
- `TOO_DETACHED`: Useful for vocal and mood boundaries, but should not over-assume emotional intent.
- `LESS_LIKE_THIS`: Strong action label. Runtime candidate keeps it `dislike` only.

## Deliberately Excluded Founder-Specific Tags

Do not include these as v0.2 runtime tags:

- `SLOP_SIGNAL`
- `TOO_HEAVY` as a universal default
- `TOO_POLISHED` as a universal default
- `RIFF_WORKED` as a universal default
- Any chip that assumes guitars, rock bands, English lyrics, albums, or founder calibration terms.

Specific music-domain traits can still appear as song affinity evidence. They should not become universal chip IDs unless Product approves them for a narrower specialist surface.
