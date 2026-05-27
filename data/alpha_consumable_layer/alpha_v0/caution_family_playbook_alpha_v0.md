# Caution Family Playbook Alpha v0

Version: `alpha_v0`

Status: `frozen_for_alpha_consumable_layer`

This playbook tells Survey, Mission Generation, App/MusicKit, and Supabase how to use caution families without turning fragile rows into bad recommendations or false Atlas truth.

## Family 11: Electronic, Dance, Club, Industrial, Experimental Pop

Primary risk:

- mix/edit/remix specificity
- producer aliases and project identities
- radio edit versus original mix versus remix
- club-track recognition versus actual dance/electronic appetite

Alpha handling:

- use approved candidates only
- require `apple_music_resolution_policy`
- block rows with `resolver_action != auto_resolve_allowed`
- include mix/edit risk in `version_risk_note`
- use false-nearby/boundary probes sparingly

Do not infer:

- broad electronic appetite from one club hit
- industrial/electronic compatibility from shared texture alone
- DJ/project identity equivalence without alias sidecar support

## Family 13: Latin, Caribbean, Global Pop

Primary risk:

- language variants
- remixes
- collaboration credits
- regional scene meaning
- global-pop versus diaspora/roots distinction

Alpha handling:

- require exact recording when language/remix/collab changes the object
- keep collaboration display credits visible
- avoid treating one crossover hit as broad Latin/global appetite
- preserve `do_not_infer` guardrails in OpenAI payloads

Do not infer:

- Spanish-language appetite from one English remix
- reggaeton appetite from one Latin-pop ballad
- K-pop/J-pop/global-pop appetite from one viral crossover

## Family 14: Jazz, Standards, Vocal, Classical-Adjacent

Primary risk:

- composition/work versus recording distinction
- standards with many canonical performances
- classical movements and arias
- vocal pop versus jazz versus lounge context

Alpha handling:

- use concrete recordings only for default first missions
- route composition-first rows to `composition_placeholder` or manual review
- preserve `recording_variant_type`
- block classical/work rows unless concrete approved recording exists

Do not infer:

- jazz appetite from one standard used as nostalgia/context
- classical appetite from one film/advertising-famous piece
- artist-level appetite from one famous recording of a standard

## Family 16: Christian, Worship, Gospel

Primary risk:

- worship standards with many versions
- church-brand versus songwriter versus performer identity
- live/congregational versions
- gospel as roots/soul history versus devotional context

Alpha handling:

- keep Black gospel roots rows distinct from worship-standard rows
- block church-brand/manual-review rows where version identity is unclear
- preserve `credit_context` when available
- avoid default mission use of worship standards unless exact recording is approved

Do not infer:

- devotional appetite from gospel/soul history alone
- church-brand affinity from one worship song
- broad CCM appetite from one family/context memory

## Families 15 and 17: Context Only

Family 15 and Family 17 stay out of default first Mission Generation.

Allowed:

- concierge/context mission
- explicit soundtrack/theater/family-context route
- QA/manual review

Blocked:

- Fast Survey default page
- default first Mission Generation
- starter Atlas promotion
- Apple Music auto-resolution for special rows

Do not infer:

- core taste identity from holiday/kids/party/context use
- artist appetite from cast, show, film, score, or compilation context
