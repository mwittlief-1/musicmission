# Cartenza Affinity Canonical Tag List Addendum v0.3.1

## Purpose

This addendum closes a dispatch gap for the Codex graph-wide affinity tagging exercise.

Codex must receive not only a reference to the approved ontology file, but also the explicit frozen list of approved canonical runtime tags. These are the only tags permitted in graph-wide tagging outputs. Aliases, analyst notes, genre labels, family names, and newly invented tags must not appear as runtime tags.

## Status

```text
Affinity ontology v0.2.2: APPROVED
Sparse tagging rules v0.3: APPROVED
Schema boundary amendment v0.3.1: APPROVED
Graph-wide tagging: PREPARED BUT BLOCKED PENDING GRAPH EXPANSION
Runtime ingestion: NOT APPROVED
```

## Hard rule

Any output containing tags outside this approved canonical list fails QA.

Aliases may be used only internally for interpretation. They must not appear in output JSON.

## Approved canonical runtime tags

### vocal_performance

```text
big_voice
intimate_voice
ragged_voice
plainspoken_voice
detached_cool
urgent_delivery
raw_confession
close_harmony
communal_vocal
processed_vocal
rhythmic_vocal
persona_voice
instrumental_identity
```

### emotion_theme

```text
romantic_longing
romantic_grief
desire
alienation
rage
rebellion
celebration
nostalgia
spiritual_yearning
self_mythology
comic_absurdity
mourning
dread
uplift
```

### sonic_texture

```text
guitar_forward
distorted_guitar
acoustic_intimate
piano_led
orchestral_swell
horn_arrangement
synthetic_texture
heavy_low_end
raw_live_band
polished_studio
studio_architecture
dark_atmosphere
sample_based
```

### rhythm_body

```text
backbeat_stomp
driving_eighths
groove_locked
dancefloor
syncopated_groove
ballad_pacing
slow_burn
anthemic_build
explosive_chorus
mosh_energy
minimal_pulse
swing_shuffle
```

### form_container

```text
single_craft
album_world
narrative_song
anthem
chorus_machine
riff_song
club_track
soundtrack_object
standard_interpretation
concept_piece
jam_vehicle
novelty_object
```

### social_context

```text
party_context
dance_context
karaoke_context
wedding_context
holiday_context
family_shared_context
worship_context
soundtrack_context
nostalgia_context
communal_ritual_context
```

### routing_caution

```text
safe_gateway
overfamiliar_anchor
high_whiplash
false_nearby_risk
requires_framing
context_dependent
explicit_context
camp_sensitive
sentimentality_risk
genre_costume_risk
novelty_risk
one_object_exception_risk
```

## Schema placement rule

The approved tag list has seven dimensions, but graph-wide output must split them into two schema layers.

### Core song affinity dimensions

These attach to canonical song/recording truth:

```text
vocal_performance
emotion_theme
sonic_texture
rhythm_body
form_container
```

### Membership / route-context overlay dimensions

These attach primarily to membership, family, archetype, survey, or route context:

```text
social_context
routing_caution
```

## Codex validation requirement

Codex must implement deterministic validation that checks:

```text
1. every output tag is in the approved canonical tag list;
2. no alias appears in output;
3. no social_context or routing_caution tag appears inside canonical_song_affinity_tags;
4. no core song affinity tag appears inside membership_context_overlays unless the schema explicitly supports a future overlay-core note field;
5. no invented tag is accepted silently;
6. output fails loudly on any unknown tag.
```

## Notes

The ontology source file remains the authoritative source for definitions, aliases, analyst notes, use/do-not-use rules, and examples:

```text
affinity_tag_ontology_v0_2_2_schema_amended_v0_3_1.json
```

This addendum is the frozen runtime tag checklist that should be embedded in the Codex dispatch and QA scripts.
