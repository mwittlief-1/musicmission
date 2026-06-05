# Build 45 Mission Enrichment v0.2 Combined Validated Output

Created: `2026-06-04T17:31:19.556654+00:00`
Model: `gpt-4.1`
Validation: `all six missions passed`
Estimated API cost: `$0.414006`

## Data Findings

- Supabase diagnostic packet captured mission IDs only; complete route bodies came from local Build 45 share packet v2.
- Build 45 v2 supplied six missions and 36 route items.
- Song-level affinity tags were present for 33 of 36 route items.
- Missing affinity rows were left empty rather than inferred: Bastards of Young, The One I Love, I Will Dare.

## Mission Copy And Tags

### MIS_ALPHA_SURVEY_OPPORTUNITY_DEPTH_01

- Title: Testing the Center: 90s Alternative & Grunge
- Subtitle: Explore the core of a strong Survey signal
- Why now: You’ve given strong signals in this lane. Now, Cartenza is testing whether this center holds up with new songs you haven’t rated before.
- Listen for: Which moods, sounds, or performances feel right or off; If certain songs feel like anchors, waypoints, or outliers; How you react to big voices, guitar-forward textures, or anthemic builds
- Route chips:
  - 1. Alive — Pearl Jam: MOOD_WORKED, BUILD_WORKED, SOUND_WORKED, VOICE_WORKED, WOULD_TRY_MORE_NEARBY, MOOD_DEPENDENT. Pre-play: Start with a major anchor: Pearl Jam’s 'Alive' sets the tone for this lane.
  - 2. Black Hole Sun — Soundgarden: MOOD_WORKED, BUILD_WORKED, SOUND_WORKED, VOICE_WORKED, GOOD_NOT_CORE, WOULD_TRY_MORE_NEARBY. Pre-play: Next, try Soundgarden’s 'Black Hole Sun'—a classic with a darker edge.
  - 3. Man in the Box — Alice in Chains: GROOVE_WORKED, SOUND_WORKED, MOOD_WORKED, HOOK_WORKED, VOICE_WORKED, GOOD_NOT_CORE. Pre-play: Now, Alice in Chains’ 'Man in the Box' brings a heavy, groove-locked feel.
  - 4. Aneurysm — Nirvana: ENERGY_WORKED, HOOK_WORKED, SOUND_WORKED, VOICE_WORKED, KEEP_AS_WAYPOINT, WOULD_TRY_MORE_NEARBY. Pre-play: Compare with Nirvana’s 'Aneurysm'—raw energy and urgency.
  - 5. Drain You — Nirvana: RIGHT_SOUND_WRONG_SONG, HOOK_WORKED, SOUND_WORKED, VOICE_WORKED, WOULD_TRY_MORE_NEARBY, RIGHT_ARTIST_WRONG_TRACK. Pre-play: Check your response to another Nirvana track: 'Drain You'.
  - 6. Rape Me — Nirvana: MOOD_WORKED, BUILD_WORKED, SOUND_WORKED, VOICE_WORKED, GOOD_NOT_CORE, WOULD_TRY_MORE_NEARBY. Pre-play: Finish with 'Rape Me'—a bold, anthemic statement from Nirvana.

### MIS_ALPHA_SURVEY_OPPORTUNITY_DEPTH_02

- Title: Testing the Edges of 80s/90s Alternative
- Subtitle: Explore what holds up across early alt-rock favorites
- Why now: We’re running this test because your earlier signals suggested a strong pull toward 90s alternative and related styles, but it’s still unclear how deep or broad that interest goes.
- Listen for: Songs that feel like a clear fit versus those that just pass through; Moments where the mood, sound, or energy stands out; Whether any track surprises you or feels like a turning point
- Missing affinity rows: ITEM_ALPHA_SURVEY_DEPTH_02_3_THE_REPLACEMENTS_BASTARDS_OF_YOUNG, ITEM_ALPHA_SURVEY_DEPTH_02_5_R_E_M_THE_ONE_I_LOVE
- Route chips:
  - 1. Where Is My Mind? — Pixies: MOOD_WORKED, HOOK_WORKED, BUILD_WORKED, SOUND_WORKED, VOICE_WORKED, SURPRISED_ME. Pre-play: Start with a touchstone: the Pixies’ ‘Where Is My Mind?’ anchors this test.
  - 2. Teen Age Riot — Sonic Youth: MOOD_WORKED, HOOK_WORKED, BUILD_WORKED, SOUND_WORKED, VOICE_WORKED, KEEP_AS_WAYPOINT. Pre-play: Now, check your reaction to Sonic Youth’s energetic ‘Teen Age Riot’.
  - 3. Bastards of Young — The Replacements: SURPRISED_ME, WOULD_TRY_MORE_NEARBY, GOOD_NOT_CORE, KEEP_AS_WAYPOINT, UNSURE_BUT_CURIOUS, RIGHT_ARTIST_WRONG_TRACK. Pre-play: Next, try The Replacements’ ‘Bastards of Young’—a neighboring sound from the same era.
  - 4. Radio Free Europe — R.E.M.: MOOD_WORKED, HOOK_WORKED, BUILD_WORKED, SOUND_WORKED, VOICE_WORKED, KEEP_AS_WAYPOINT. Pre-play: Compare with R.E.M.’s ‘Radio Free Europe’—an early alternative classic.
  - 5. The One I Love — R.E.M.: SURPRISED_ME, WOULD_TRY_MORE_NEARBY, RIGHT_ARTIST_WRONG_TRACK, GOOD_NOT_CORE, KEEP_AS_WAYPOINT, UNSURE_BUT_CURIOUS. Pre-play: Try another R.E.M. track: ‘The One I Love’.
  - 6. Driver 8 — R.E.M.: MOOD_WORKED, HOOK_WORKED, BUILD_WORKED, SOUND_WORKED, VOICE_WORKED, KEEP_AS_WAYPOINT. Pre-play: Finish with ‘Driver 8’ by R.E.M.—another probe into the era’s sound.

### MIS_ALPHA_SURVEY_OPPORTUNITY_BRIDGE_01

- Title: Testing the Bridge: 90s Alt & Grunge Connections
- Subtitle: See if your early signals connect across this classic lane.
- Why now: Early Survey results show enough positive signals to justify testing a bridge through this territory. Your feedback will help us see if these connections hold up or reveal new splits.
- Listen for: Moments when the mood, groove, or energy especially work for you; Songs that feel like a natural fit versus those that feel out of place; Differences in sound, performance, or production that stand out; Tracks that make you curious to explore more in this direction
- Route chips:
  - 1. Daughter — Pearl Jam: MOOD_WORKED, GROOVE_WORKED, VOICE_WORKED, HOOK_WORKED, SOUND_WORKED, WOULD_TRY_MORE_NEARBY. Pre-play: Start with a touchstone: Pearl Jam’s "Daughter" anchors this route with a familiar sound and emotional core.
  - 2. Jeremy — Pearl Jam: MOOD_WORKED, BUILD_WORKED, SOUND_WORKED, VOICE_WORKED, HOOK_WORKED, WOULD_TRY_MORE_NEARBY. Pre-play: Next, Pearl Jam’s "Jeremy" tests if your lane connects to nearby territory with more intensity.
  - 3. Would? — Alice in Chains: MOOD_WORKED, GROOVE_WORKED, PERFORMANCE_WORKED, SOUND_WORKED, HOOK_WORKED, WOULD_TRY_MORE_NEARBY. Pre-play: Now, Alice in Chains’ "Would?" explores a heavier, more atmospheric side of this lane.
  - 4. Spoonman — Soundgarden: ENERGY_WORKED, GROOVE_WORKED, PERFORMANCE_WORKED, SOUND_WORKED, HOOK_WORKED, WOULD_TRY_MORE_NEARBY. Pre-play: Soundgarden’s "Spoonman" brings energy and celebration to the mix.
  - 5. Heart-Shaped Box — Nirvana: MOOD_WORKED, BUILD_WORKED, SOUND_WORKED, VOICE_WORKED, HOOK_WORKED, WOULD_TRY_MORE_NEARBY. Pre-play: Compare with Nirvana’s "Heart-Shaped Box," a landmark track with a different emotional edge.
  - 6. Better Man — Pearl Jam: MOOD_WORKED, BUILD_WORKED, VOICE_WORKED, SOUND_WORKED, HOOK_WORKED, MOOD_DEPENDENT. Pre-play: Finally, "Better Man" by Pearl Jam offers a control: familiar but with a different emotional focus.

### MIS_ALPHA_SURVEY_OPPORTUNITY_BOUNDARY_01

- Title: Testing the Edge: 90s Alt Boundaries
- Subtitle: Explore where the lane starts to blur
- Why now: We’ve seen only a single negative signal so far, so this route gently explores the boundary—without repeating songs or artists you’ve already rated. Your reactions here help map out what’s core, what’s a stretch, and what’s outside your lane.
- Listen for: How you respond to intense moods or raw performances; Whether certain sounds or song structures feel right or off-base; If any track surprises you or feels like a useful waypoint
- Route chips:
  - 1. Violet — Hole: MOOD_WORKED, SOUND_WORKED, VOICE_WORKED, BUILD_WORKED, ENERGY_WORKED, WOULD_TRY_MORE_NEARBY. Pre-play: Start with a defining track: intense, raw, and unmistakably bold.
  - 2. Black — Pearl Jam: MOOD_WORKED, SOUND_WORKED, VOICE_WORKED, BUILD_WORKED, WOULD_TRY_MORE_NEARBY, MOOD_DEPENDENT. Pre-play: Another anchor—moody, confessional, and guitar-forward.
  - 3. Bullet with Butterfly Wings — Smashing Pumpkins: MOOD_WORKED, SOUND_WORKED, PERFORMANCE_WORKED, BUILD_WORKED, GOOD_NOT_CORE, SURPRISED_ME. Pre-play: Now, a boundary test: anthem-sized, ferocious, and dramatic.
  - 4. Angry Chair — Alice in Chains: MOOD_WORKED, SOUND_WORKED, PERFORMANCE_WORKED, BUILD_WORKED, KEEP_AS_WAYPOINT, SURPRISED_ME. Pre-play: A comparator: dark, slow-burning, and full of dread.
  - 5. Grind — Alice in Chains: MOOD_WORKED, SOUND_WORKED, GROOVE_WORKED, VOICE_WORKED, RIGHT_SOUND_WRONG_SONG, MOOD_DEPENDENT. Pre-play: A control: groove-locked, alienated, and harmonized.
  - 6. Heaven Beside You — Alice in Chains: MOOD_WORKED, SOUND_WORKED, VOICE_WORKED, BUILD_WORKED, GOOD_NOT_CORE, SURPRISED_ME. Pre-play: A probe: intimate, melodic, and quietly intense.

### MIS_ALPHA_SURVEY_OPPORTUNITY_CONTEXT_01

- Title: Does Context Change Your Song Signals?
- Subtitle: Test how your reactions shift with different surroundings.
- Why now: You’ve given enough 'ok' signals for us to explore if context makes a difference. This test helps refine how Cartenza reads your taste boundaries and centers.
- Listen for: Songs that feel different in a new order; Tracks you might keep as waypoints, not favorites; Moments where context changes your response
- Missing affinity rows: ITEM_ALPHA_SURVEY_CONTEXT_01_2_THE_REPLACEMENTS_I_WILL_DARE
- Route chips:
  - 1. So. Central Rain — R.E.M.: MOOD_WORKED, VOICE_WORKED, HOOK_WORKED, GROOVE_WORKED, KEEP_AS_WAYPOINT, SURPRISED_ME. Pre-play: Start with a steady reference point: R.E.M.’s "So. Central Rain." Notice if your feelings about it shift in this lineup.
  - 2. I Will Dare — The Replacements: CONTEXT_DEPENDENT, WOULD_TRY_MORE_NEARBY, GOOD_NOT_CORE, SURPRISED_ME, NEEDS_MORE_CONTEXT, UNSURE_BUT_CURIOUS. Pre-play: Next, try The Replacements’ "I Will Dare." See if its place in this set changes your impression.
  - 3. Plateau — Meat Puppets: MOOD_WORKED, HOOK_WORKED, GROOVE_WORKED, VOICE_WORKED, KEEP_AS_WAYPOINT, SURPRISED_ME. Pre-play: Now, listen to "Plateau" by Meat Puppets. Does its comic, narrative style land differently here?
  - 4. Up on the Sun — Meat Puppets: MOOD_WORKED, GROOVE_WORKED, SOUND_WORKED, VOICE_WORKED, PERFORMANCE_WORKED, KEEP_AS_WAYPOINT. Pre-play: Switch gears with "Up on the Sun." Notice the uplift and groove—does it reset your mood?
  - 5. Finest Worksong — R.E.M.: MOOD_WORKED, BUILD_WORKED, BEAT_WORKED, SOUND_WORKED, VOICE_WORKED, KEEP_AS_WAYPOINT. Pre-play: Return to R.E.M. with "Finest Worksong." Does its anthemic energy feel different now?
  - 6. Dirty Boots — Sonic Youth: MOOD_WORKED, BUILD_WORKED, SOUND_WORKED, VOICE_WORKED, PERFORMANCE_WORKED, SURPRISED_ME. Pre-play: Finish with Sonic Youth’s "Dirty Boots." See if its rebellious, riff-driven sound pulls you in or pushes you out.

### MIS_ALPHA_SURVEY_OPPORTUNITY_GATEWAY_01

- Title: Test a New Frontier: 90s Alternative Gateway
- Subtitle: Explore how close this lane comes to your core taste
- Why now: After your initial Survey, this test uses familiar but not overplayed tracks to see if a nearby musical lane could be a lasting part of your listening world.
- Listen for: Songs that feel like a natural fit or just outside your core; Unexpected moments or sounds that catch your ear; Whether the mood, sound, or energy feels right for you; Tracks you’d want to hear more of—or not
- Route chips:
  - 1. I Stay Away — Alice in Chains: MOOD_WORKED, BUILD_WORKED, SOUND_WORKED, VOICE_WORKED, WOULD_TRY_MORE_NEARBY, SURPRISED_ME. Pre-play: Start with a steady anchor: Alice in Chains at their most textured and anthemic.
  - 2. No Excuses — Alice in Chains: MOOD_WORKED, GROOVE_WORKED, SOUND_WORKED, VOICE_WORKED, WOULD_TRY_MORE_NEARBY, KEEP_AS_WAYPOINT. Pre-play: Next, a bridge track—warmer but still unmistakably Alice in Chains.
  - 3. Nutshell — Alice in Chains: MOOD_WORKED, PERFORMANCE_WORKED, BUILD_WORKED, SOUND_WORKED, WOULD_TRY_MORE_NEARBY, KEEP_AS_WAYPOINT. Pre-play: Now, a probe—stripped back and confessional.
  - 4. Them Bones — Alice in Chains: ENERGY_WORKED, SOUND_WORKED, VOICE_WORKED, MOOD_WORKED, WOULD_TRY_MORE_NEARBY, KEEP_AS_WAYPOINT. Pre-play: A comparator: sharper edges and heavier drive.
  - 5. Tribe — Gruntruck: MOOD_WORKED, ENERGY_WORKED, SOUND_WORKED, VOICE_WORKED, RIGHT_SOUND_WRONG_SONG, MOOD_DEPENDENT. Pre-play: Control track: a neighboring artist with a rougher edge.
  - 6. Bound for the Floor — Local H: HOOK_WORKED, MOOD_WORKED, ENERGY_WORKED, SOUND_WORKED, VOICE_WORKED, KEEP_AS_WAYPOINT. Pre-play: Final probe: a hook-driven track from the same era.
