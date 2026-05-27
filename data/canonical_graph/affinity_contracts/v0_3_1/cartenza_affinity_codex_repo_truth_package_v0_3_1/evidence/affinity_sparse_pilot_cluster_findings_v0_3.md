# Affinity Retag Pilot v0.3 — Cluster Findings

## Readout

The sparse rules reduced tag density while preserving visible cross-family clusters. The pilot is less bridge-heavy than the 60-song QA sample, so cluster counts should be read as evidence of natural recurrence, not forced coverage.

## Surviving bridge clusters

## big_voice + romantic_grief/uplift + orchestral_swell

Count: 3
- `carolina-gaitan-mauro-castillo-adassa-rhenzy-feliz-diane-guerrero-stephanie-beatriz-and-encanto-cast-we-don-t-talk-about-bruno` — We Don't Talk About Bruno — Carolina Gaitan, Mauro Castillo, Adassa, Rhenzy Feliz, Diane Guerrero, Stephanie Beatriz and Encanto Cast
- `idina-menzel-and-kristin-chenoweth-defying-gravity` — Defying Gravity — Idina Menzel and Kristin Chenoweth
- `leslie-odom-jr-the-room-where-it-happens` — The Room Where It Happens — Leslie Odom Jr.

## dance/groove + celebration/uplift + party or dance context

Count: 5
- `chris-montez-lets-dance` — Let's Dance — Chris Montez
- `daddy-yankee-gasolina` — Gasolina — Daddy Yankee
- `elvis-crespo-suavemente` — Suavemente — Elvis Crespo
- `farruko-pepas` — Pepas — Farruko
- `dj-casper-cha-cha-slide` — Cha Cha Slide — DJ Casper

## synthetic/persona or processed vocal + dance/minimal pulse

Count: 6
- `frankie-knuckles-your-love` — Your Love — Frankie Knuckles
- `mr-fingers-can-you-feel-it` — Can You Feel It — Mr. Fingers
- `tame-impala-the-less-i-know-the-better` — The Less I Know the Better — Tame Impala
- `bonobo-kiara` — Kiara — Bonobo
- `cybotron-clear` — Clear — Cybotron
- `pinkpantheress-boys-a-liar-pt-2` — Boy's a Liar Pt. 2 — PinkPantheress

## distorted_guitar + alienation/rebellion/rage + explosive/mosh/driving energy

Count: 5
- `metallica-enter-sandman` — Enter Sandman — Metallica
- `kyuss-green-machine` — Green Machine — Kyuss
- `megadeth-holy-wars-the-punishment-due` — Holy Wars... The Punishment Due — Megadeth
- `pearl-jam-alive` — Alive — Pearl Jam
- `the-breeders-cannonball` — Cannonball — The Breeders

## novelty/context object + context_dependent/novelty/camp caution

Count: 2
- `cupid-cupid-shuffle` — Cupid Shuffle — Cupid
- `dj-casper-cha-cha-slide` — Cha Cha Slide — DJ Casper

## worship_context + spiritual_yearning/uplift + context-dependent routing

Count: 3
- `darlene-zschech-shout-to-the-lord` — Shout to the Lord — Darlene Zschech
- `casting-crowns-who-am-i` — Who Am I — Casting Crowns
- `hillsong-united-oceans-where-feet-may-fail` — Oceans (Where Feet May Fail) — Hillsong United

## plainspoken/acoustic + mourning/nostalgia + narrative form

Count: 7
- `f4-024-song-american-pie-don-mclean` — American Pie — Don McLean
- `f4-028-song-windfall-son-volt` — Windfall — Son Volt
- `f4-028-song-timebomb-old-97-s` — Timebomb — Old 97's
- `dolly-parton-jolene` — Jolene — Dolly Parton
- `jason-isbell-cover-me-up` — Cover Me Up — Jason Isbell
- `f4-026-song-this-land-is-your-land-woody-guthrie` — This Land Is Your Land — Woody Guthrie
- `sam-hunt-body-like-a-back-road` — Body Like a Back Road — Sam Hunt

## Tags causing confusion / watchlist

- `uplift`: useful, but still needs boundary testing against `celebration`, `spiritual_yearning`, and `self_mythology`.
- `safe_gateway`: no longer behaves like a filler tag under sparse rules, but should remain capped/reviewed in graph-wide work.
- `context_dependent`: improved, but still needs careful separation from ordinary `social_context`.
- `communal_vocal`: can cover call-and-response for now, but soul/funk/gospel-heavy future tests may still justify a narrower tag.
- `groove_locked`: currently covers what a future `head_nod` tag might isolate; hip-hop-dense QA should revisit later.

## Candidate ontology changes

Add no further tags before graph-wide tagging. Keep `uplift` as the only v0.2.2 addition. Revisit `head_nod`, `call_and_response`, and narrower `big_voice` subtypes only after a hip-hop/soul/funk/vocal-showpiece-heavy QA lane.

## Unused canonical tags in this pilot

anthem, comic_absurdity, communal_ritual_context, concept_piece, detached_cool, one_object_exception_risk, raw_live_band, wedding_context

## Overused tags in this pilot

polished_studio: 59, single_craft: 46, big_voice: 30, romantic_longing: 27, overfamiliar_anchor: 27, guitar_forward: 25
