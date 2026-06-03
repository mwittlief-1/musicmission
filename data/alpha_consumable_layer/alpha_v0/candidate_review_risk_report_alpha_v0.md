# Candidate Review-Risk Report Alpha v0

Alpha contract version: `alpha_v0`

Generated: 2026-06-01T14:00:04.153Z

Status: `route_candidate_review_risk_clear`

Purpose: expose playback-ready candidate safety metadata so Mission Generation/Supabase can store review flags without false hard review gates.

## Summary

| metric | count |
| --- | ---: |
| total route candidates | 72 |
| default Alpha mission eligible | 72 |
| hard blocked | 0 |
| track candidates | 72 |
| album candidates | 0 |
| artist candidates | 0 |
| waypoints | 12 |
| dead-end checks | 12 |

## Gate Policy

Do not hard-block generation merely because a candidate has review flags. Use the flags for audit/review posture while continuing attempts toward the Alpha target.

Hard-block only when a candidate is actually blocked, quarantined, suppressed, manual-review-only, context-only, not playback-ready, or not approved.

## Review Actions

| action | count |
| --- | ---: |
| generate_allowed | 40 |
| generate_allowed_store_review_flags | 32 |

## Risk Classes

| risk_class | count |
| --- | ---: |
| low | 40 |
| medium | 8 |
| high | 24 |

## Candidate Rows

| pool | object | display | role | risk | safety | action | flags |
| --- | --- | --- | --- | --- | --- | --- | --- |
| anchors | track | Elvis Presley - All Shook Up | anchor | low | alpha_safe_default | generate_allowed | exact_recording_required |
| anchors | track | Buffalo Springfield - For What It's Worth | anchor | low | alpha_safe_default | generate_allowed | exact_recording_required |
| anchors | track | Led Zeppelin - Stairway to Heaven | anchor | low | alpha_safe_default | generate_allowed | exact_recording_required |
| anchors | track | Don McLean - American Pie | anchor | low | alpha_safe_default | generate_allowed | exact_recording_required |
| anchors | track | Dolly Parton - Jolene | anchor | low | alpha_safe_default | generate_allowed | exact_recording_required |
| anchors | track | Al Green - Let's Stay Together | anchor | low | alpha_safe_default | generate_allowed | exact_recording_required |
| anchors | track | 2Pac feat. Dr. Dre - California Love | anchor | low | alpha_safe_default | generate_allowed | exact_recording_required |
| anchors | track | Depeche Mode - Enjoy the Silence | anchor | low | alpha_safe_default | generate_allowed | exact_recording_required |
| anchors | track | Gojira - Flying Whales | anchor | low | alpha_safe_default | generate_allowed | exact_recording_required |
| anchors | track | Blink-182 - All the Small Things | anchor | low | alpha_safe_default | generate_allowed | exact_recording_required |
| anchors | track | Kraftwerk - Autobahn | anchor | medium | alpha_safe_with_review_flags | generate_allowed_store_review_flags | mix_edit_remix_specificity, exact_recording_required |
| anchors | track | Adele - Rolling in the Deep | anchor | low | alpha_safe_default | generate_allowed | exact_recording_required |
| bridges | track | Barrett Strong - Money (That's What I Want) | bridge | low | alpha_safe_default | generate_allowed | exact_recording_required |
| bridges | track | ? and the Mysterians - 96 Tears | bridge | low | alpha_safe_default | generate_allowed | exact_recording_required |
| bridges | track | Pink Floyd - Money | bridge | low | alpha_safe_default | generate_allowed | exact_recording_required |
| bridges | track | Jim Croce - Time in a Bottle | bridge | low | alpha_safe_default | generate_allowed | exact_recording_required |
| bridges | track | Glen Campbell - Wichita Lineman | bridge | low | alpha_safe_default | generate_allowed | exact_recording_required |
| bridges | track | Alicia Keys - Fallin' | bridge | low | alpha_safe_default | generate_allowed | exact_recording_required |
| bridges | track | A Tribe Called Quest - Scenario | bridge | low | alpha_safe_default | generate_allowed | exact_recording_required |
| bridges | track | Depeche Mode - Personal Jesus | bridge | low | alpha_safe_default | generate_allowed | exact_recording_required |
| bridges | track | Black Sabbath - Iron Man | bridge | low | alpha_safe_default | generate_allowed | exact_recording_required |
| bridges | track | Alice in Chains - Man in the Box | bridge | low | alpha_safe_default | generate_allowed | exact_recording_required |
| bridges | track | Bjork - Joga | bridge | medium | alpha_safe_with_review_flags | generate_allowed_store_review_flags | mix_edit_remix_specificity, exact_recording_required |
| bridges | track | Beyonce - Crazy in Love | bridge | low | alpha_safe_default | generate_allowed | exact_recording_required |
| probes | track | Ben E. King - Spanish Harlem | probe | low | alpha_safe_default | generate_allowed | exact_recording_required |
| probes | track | The Balloon Farm - A Question of Temperature | probe | low | alpha_safe_default | generate_allowed | exact_recording_required |
| probes | track | Journey - Don't Stop Believin' | probe | low | alpha_safe_default | generate_allowed | exact_recording_required |
| probes | track | Marc Cohn - Walking in Memphis | probe | low | alpha_safe_default | generate_allowed | exact_recording_required |
| probes | track | Reba McEntire - Fancy | probe | low | alpha_safe_default | generate_allowed | exact_recording_required |
| probes | track | Aretha Franklin - Think | probe | low | alpha_safe_default | generate_allowed | exact_recording_required |
| probes | track | Eminem - The Real Slim Shady | probe | low | alpha_safe_default | generate_allowed | exact_recording_required |
| probes | track | Sonic Youth - Teen Age Riot | probe | low | alpha_safe_default | generate_allowed | exact_recording_required |
| probes | track | Deftones - My Own Summer (Shove It) | probe | low | alpha_safe_default | generate_allowed | exact_recording_required |
| probes | track | Bloc Party - Banquet | probe | low | alpha_safe_default | generate_allowed | exact_recording_required |
| probes | track | Fischerspooner - Emerge | probe | medium | alpha_safe_with_review_flags | generate_allowed_store_review_flags | mix_edit_remix_specificity, exact_recording_required |
| probes | track | Farruko - Pepas | probe | medium | alpha_safe_with_review_flags | generate_allowed_store_review_flags | language_remix_collaboration_specificity, exact_recording_required |
| boundary_probes | track | Link Wray - Rumble | risky_probe | high | alpha_safe_with_review_flags | generate_allowed_store_review_flags | boundary_probe_use_with_care, exact_recording_required |
| boundary_probes | track | The Kingsmen - Louie Louie | risky_probe | high | alpha_safe_with_review_flags | generate_allowed_store_review_flags | boundary_probe_use_with_care, exact_recording_required |
| boundary_probes | track | Queen - Killer Queen | risky_probe | high | alpha_safe_with_review_flags | generate_allowed_store_review_flags | boundary_probe_use_with_care, exact_recording_required |
| boundary_probes | track | Kacey Musgraves - Slow Burn | risky_probe | high | alpha_safe_with_review_flags | generate_allowed_store_review_flags | boundary_probe_use_with_care, exact_recording_required |
| boundary_probes | track | Sade - Smooth Operator | risky_probe | high | alpha_safe_with_review_flags | generate_allowed_store_review_flags | boundary_probe_use_with_care, exact_recording_required |
| boundary_probes | track | Drake - Hotline Bling | risky_probe | high | alpha_safe_with_review_flags | generate_allowed_store_review_flags | boundary_probe_use_with_care, exact_recording_required |
| boundary_probes | track | Suicidal Tendencies - Institutionalized | risky_probe | high | alpha_safe_with_review_flags | generate_allowed_store_review_flags | boundary_probe_use_with_care, exact_recording_required |
| boundary_probes | track | Linkin Park - In the End | risky_probe | high | alpha_safe_with_review_flags | generate_allowed_store_review_flags | boundary_probe_use_with_care, exact_recording_required |
| boundary_probes | track | My Bloody Valentine - Only Shallow | risky_probe | high | alpha_safe_with_review_flags | generate_allowed_store_review_flags | boundary_probe_use_with_care, exact_recording_required |
| boundary_probes | track | Darude - Sandstorm | risky_probe | high | alpha_safe_with_review_flags | generate_allowed_store_review_flags | mix_edit_remix_specificity, boundary_probe_use_with_care, exact_recording_required |
| boundary_probes | track | Britney Spears - Toxic | risky_probe | high | alpha_safe_with_review_flags | generate_allowed_store_review_flags | boundary_probe_use_with_care, exact_recording_required |
| boundary_probes | track | FIFTY FIFTY - Cupid | risky_probe | high | alpha_safe_with_review_flags | generate_allowed_store_review_flags | language_remix_collaboration_specificity, boundary_probe_use_with_care, exact_recording_required |
| dead_end_checks | track | Status Quo - Pictures of Matchstick Men | trap | high | alpha_safe_with_review_flags | generate_allowed_store_review_flags | dead_end_check_store_as_probe_not_conclusion, exact_recording_required |
| dead_end_checks | track | Passenger - Let Her Go | trap | high | alpha_safe_with_review_flags | generate_allowed_store_review_flags | dead_end_check_store_as_probe_not_conclusion, exact_recording_required |
| dead_end_checks | track | Beastie Boys - Fight for Your Right | trap | high | alpha_safe_with_review_flags | generate_allowed_store_review_flags | dead_end_check_store_as_probe_not_conclusion, exact_recording_required |
| dead_end_checks | track | Butthole Surfers - Pepper | trap | high | alpha_safe_with_review_flags | generate_allowed_store_review_flags | dead_end_check_store_as_probe_not_conclusion, exact_recording_required |
| dead_end_checks | track | Limp Bizkit - Break Stuff | trap | high | alpha_safe_with_review_flags | generate_allowed_store_review_flags | dead_end_check_store_as_probe_not_conclusion, exact_recording_required |
| dead_end_checks | track | Live - Lightning Crashes | trap | high | alpha_safe_with_review_flags | generate_allowed_store_review_flags | dead_end_check_store_as_probe_not_conclusion, exact_recording_required |
| dead_end_checks | track | Black Eyed Peas - I Gotta Feeling | trap | high | alpha_safe_with_review_flags | generate_allowed_store_review_flags | dead_end_check_store_as_probe_not_conclusion, exact_recording_required |
| dead_end_checks | track | Young-Holt Unlimited - Soulful Strut | trap | high | alpha_safe_with_review_flags | generate_allowed_store_review_flags | work_composition_recording_specificity, dead_end_check_store_as_probe_not_conclusion, exact_recording_required |
| dead_end_checks | track | Skillet - Monster | trap | high | alpha_safe_with_review_flags | generate_allowed_store_review_flags | worship_standard_church_brand_specificity, dead_end_check_store_as_probe_not_conclusion, exact_recording_required |
| dead_end_checks | track | Deftones - Change (In the House of Flies) | trap | high | alpha_safe_with_review_flags | generate_allowed_store_review_flags | dead_end_check_store_as_probe_not_conclusion, exact_recording_required |
| dead_end_checks | track | Digital Underground - The Humpty Dance | trap | high | alpha_safe_with_review_flags | generate_allowed_store_review_flags | dead_end_check_store_as_probe_not_conclusion, exact_recording_required |
| dead_end_checks | track | Bon Jovi - Livin' on a Prayer | trap | high | alpha_safe_with_review_flags | generate_allowed_store_review_flags | dead_end_check_store_as_probe_not_conclusion, exact_recording_required |
| waypoints | track | Maurice Williams and the Zodiacs - Stay | waypoint | low | alpha_safe_default | generate_allowed | exact_recording_required |
| waypoints | track | Carrie Underwood - Before He Cheats | waypoint | low | alpha_safe_default | generate_allowed | exact_recording_required |
| waypoints | track | Eurythmics - Sweet Dreams (Are Made of This) | waypoint | low | alpha_safe_default | generate_allowed | exact_recording_required |
| waypoints | track | Bon Jovi - You Give Love a Bad Name | waypoint | low | alpha_safe_default | generate_allowed | exact_recording_required |
| waypoints | track | Kavinsky - Nightcall | waypoint | medium | alpha_safe_with_review_flags | generate_allowed_store_review_flags | mix_edit_remix_specificity, exact_recording_required |
| waypoints | track | Adele - Hello | waypoint | low | alpha_safe_default | generate_allowed | exact_recording_required |
| waypoints | track | Aventura - Obsesion | waypoint | medium | alpha_safe_with_review_flags | generate_allowed_store_review_flags | language_remix_collaboration_specificity, exact_recording_required |
| waypoints | track | Chuck Mangione - Feels So Good | waypoint | medium | alpha_safe_with_review_flags | generate_allowed_store_review_flags | work_composition_recording_specificity, exact_recording_required |
| waypoints | track | Casting Crowns - Who Am I | waypoint | medium | alpha_safe_with_review_flags | generate_allowed_store_review_flags | worship_standard_church_brand_specificity, exact_recording_required |
| waypoints | track | PinkPantheress - Pain | waypoint | low | alpha_safe_default | generate_allowed | exact_recording_required |
| waypoints | track | Chris Montez - Let's Dance | waypoint | low | alpha_safe_default | generate_allowed | exact_recording_required |
| waypoints | track | Steppenwolf - Born to Be Wild | waypoint | low | alpha_safe_default | generate_allowed | exact_recording_required |
