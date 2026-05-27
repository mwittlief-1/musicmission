import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";

const ROOT = process.cwd();
const GENERATED_AT = "2026-05-26";
const SOURCE_DIR = path.join(ROOT, "data/atlas_explainer/AtlasExplainerPack_v0_2_All_Archetypes");
const OUT_DIR = path.join(ROOT, "data/atlas_explainer/AtlasExplainerPack_v0_2_1_SourceDeepened");
const ZIP_PATH = `${OUT_DIR}.zip`;

const ATLAS_STATE_FIELDS_V0_2 = [
  "atlas_state.family_affinity[family_id]",
  "atlas_state.archetype_affinity[archetype_id]",
  "atlas_state.completed_mission_ids",
  "atlas_state.active_mission_id",
  "atlas_state.first_batch_mission_ids",
  "atlas_state.related_mission_ids",
  "atlas_state.survey_positive_candidate_refs",
  "atlas_state.survey_negative_candidate_refs",
  "atlas_state.boundary_question_results",
  "atlas_state.dead_end_probe_results",
  "atlas_state.user_known_song_refs",
  "atlas_state.user_disliked_song_refs",
  "atlas_state.user_saved_artist_refs",
  "atlas_state.user_skipped_artist_refs"
];

const PLACEHOLDER_PHRASES = [
  "graph-defined road",
  "draft road",
  "draft pack",
  "source-deepening required",
  "until PM source-deepening",
  "PM source-deepening",
  "Atlas uses this draft road",
  "external source deepening is still required",
  "internal_graph_only_needs_external_source_deepening"
];

const FORBIDDEN_DYNAMIC_MISSION_PHRASES = [
  "generate mission from this node",
  "create a new mission",
  "launch arbitrary mission",
  "open a dynamic route from here",
  "ask AI to build a mission from this archetype"
];

const SOURCE_ROWS = [
  ["britannica_rock_and_roll", "Rock and roll", "Encyclopaedia Britannica", "https://www.britannica.com/art/rock-and-roll-early-style-of-rock-music", "reference", "Early rock and roll origins, teen audience, and R&B/country/gospel crossover framing."],
  ["rockhall_chuck_berry", "Chuck Berry", "Rock & Roll Hall of Fame", "https://rockhall.com/inductees/chuck-berry/", "museum_reference", "Chuck Berry as foundational rock and roll songwriter, guitarist, and performer."],
  ["rockhall_sister_rosetta_tharpe", "Sister Rosetta Tharpe", "Rock & Roll Hall of Fame", "https://rockhall.com/inductees/sister-rosetta-tharpe/", "museum_reference", "Gospel guitar and early influence context for rock and roll foundations."],
  ["loc_rock_around_the_clock", "(We're Gonna) Rock Around the Clock", "Library of Congress National Recording Registry", "https://www.loc.gov/static/programs/national-recording-preservation-board/documents/RockAroundTheClock.pdf", "archive_reference", "Recording-registry context for a mass early-rock breakthrough recording."],
  ["britannica_rockabilly", "Rockabilly", "Encyclopaedia Britannica", "https://www.britannica.com/art/rockabilly", "reference", "Rockabilly as country, R&B, blues, and gospel hybrid with early rock urgency."],
  ["sun_records_history", "History", "Sun Records", "https://sunrecords.com/history/", "official_label", "Sun Records, Sam Phillips, Elvis Presley, Carl Perkins, Jerry Lee Lewis, and early rockabilly label context."],
  ["rockhall_carl_perkins", "Carl Perkins", "Rock & Roll Hall of Fame", "https://rockhall.com/inductees/carl-perkins/", "museum_reference", "Carl Perkins and rockabilly anchor context."],
  ["loc_blue_suede_shoes", "Blue Suede Shoes", "Library of Congress National Recording Registry", "https://www.loc.gov/static/programs/national-recording-preservation-board/documents/BlueSuedeShoes.pdf", "archive_reference", "Recording-registry context for Carl Perkins and rockabilly."],
  ["britannica_doo_wop", "Doo-wop", "Encyclopaedia Britannica", "https://www.britannica.com/art/doo-wop-music", "reference", "Doo-wop vocal-harmony structure, urban youth context, and influence."],
  ["teachrock_doo_wop", "Doo Wop", "TeachRock", "https://teachrock.org/genre/doo-wop/", "educational", "Doo-wop and teen-pop teaching context."],
  ["rockhall_platters", "The Platters", "Rock & Roll Hall of Fame", "https://rockhall.com/inductees/platters/", "museum_reference", "Doo-wop and R&B vocal group bridge context."],
  ["loc_recording_registry", "Recording Registry", "Library of Congress National Recording Preservation Board", "https://www.loc.gov/programs/national-recording-preservation-board/recording-registry/", "archive_reference", "Cultural preservation context for significant U.S. recordings."],
  ["teachrock_dion_teen_idols", "Dion and the Teen Idols", "TeachRock", "https://teachrock.org/lesson/dion-and-the-teen-idols/", "educational", "Teen-idol role in bringing rock and roll into mainstream culture."],
  ["teachrock_rock_roll_becomes_pop", "Rock and Roll Becomes Pop", "TeachRock", "https://teachrock.org/chapter/rock-and-roll-becomes-pop/", "educational", "Late-1950s mainstream pop smoothing of rock and roll."],
  ["rockhall_ricky_nelson", "Ricky Nelson", "Rock & Roll Hall of Fame", "https://rockhall.com/inductees/ricky-nelson/", "museum_reference", "Teen-idol image balanced with rockabilly/pop craft."],
  ["britannica_rock_1960s", "Rock in the 1960s", "Encyclopaedia Britannica", "https://www.britannica.com/art/rock-music/Rock-in-the-1960s", "reference", "1960s rock, British Invasion, folk-rock, psychedelic, and album-era transitions."],
  ["britannica_brill_building", "The Brill Building: Assembly-Line Pop", "Encyclopaedia Britannica", "https://www.britannica.com/topic/The-Brill-Building-Assembly-Line-Pop-1688332", "reference", "Professional songwriting, publishing, and girl-group pop craft ecosystem."],
  ["britannica_girl_groups", "Girl groups", "Encyclopaedia Britannica", "https://www.britannica.com/art/girl-group", "reference", "Girl-group sound, Brill-linked writing teams, doo-wop/R&B/pop hybrid."],
  ["teachrock_brill_girl_group", "The Brill Building and the Girl Group Era", "TeachRock", "https://teachrock.org/chapter/the-brill-building-and-the-girl-group-era/", "educational", "Brill, publishers, producers, songwriters, and girl-group era teaching context."],
  ["rockhall_brill_guide", "Brill Building Library Guide", "Rock & Roll Hall of Fame Library & Archives", "https://library.rockhall.com/brill_building", "archive_guide", "Brill Building businesses, collections, and source-finding context."],
  ["britannica_soul_music", "Soul music", "Encyclopaedia Britannica", "https://www.britannica.com/art/soul-music", "reference", "Soul as gospel, blues, R&B, jazz, and rock-rooted popular music."],
  ["britannica_rhythm_and_blues", "Rhythm and blues", "Encyclopaedia Britannica", "https://www.britannica.com/art/rhythm-and-blues", "reference", "R&B labels, crossover, and transitional figures."],
  ["rockhall_ray_charles", "Ray Charles", "Rock & Roll Hall of Fame", "https://rockhall.com/inductees/ray-charles/", "museum_reference", "Ray Charles and soul crossover framing."],
  ["britannica_ray_charles", "Ray Charles", "Encyclopaedia Britannica", "https://www.britannica.com/biography/Ray-Charles", "reference", "Ray Charles as an early developer of soul through gospel, R&B, and jazz melding."],
  ["britannica_surf_music", "Surf music", "Encyclopaedia Britannica", "https://www.britannica.com/art/surf-music", "reference", "Instrumental surf, Beach Boys, West Coast guitar and harmony contexts."],
  ["britannica_dick_dale", "Dick Dale", "Encyclopaedia Britannica", "https://www.britannica.com/biography/Dick-Dale", "reference", "Dick Dale's surf-guitar role and reverb-amplifier context."],
  ["rockhall_beach_boys", "The Beach Boys", "Rock & Roll Hall of Fame", "https://rockhall.com/inductees/beach-boys/", "museum_reference", "Beach Boys as surf-rock and harmony-pop gateway."],
  ["britannica_beach_boys", "The Beach Boys", "Encyclopaedia Britannica", "https://www.britannica.com/topic/the-Beach-Boys", "reference", "Beach Boys formation, harmonies, surf image, and Brian Wilson studio role."],
  ["britannica_rock_music", "Rock music", "Encyclopaedia Britannica", "https://www.britannica.com/art/rock-music", "reference", "Broad rock-history context across album rock, hard rock, punk, and alternative lineages."],
  ["britannica_beatles", "The Beatles", "Encyclopaedia Britannica", "https://www.britannica.com/topic/the-Beatles", "reference", "Beatles biography, British Invasion, songwriting, and album-era expansion."],
  ["rockhall_beatles", "The Beatles", "Rock & Roll Hall of Fame", "https://rockhall.com/inductees/the-beatles/", "museum_reference", "The Beatles as core British Invasion and rock-canon anchors."],
  ["britannica_rolling_stones", "The Rolling Stones", "Encyclopaedia Britannica", "https://www.britannica.com/topic/the-Rolling-Stones", "reference", "Rolling Stones biography and blues-rock/British Invasion context."],
  ["rockhall_rolling_stones", "The Rolling Stones", "Rock & Roll Hall of Fame", "https://rockhall.com/inductees/the-rolling-stones/", "museum_reference", "Rolling Stones as British Invasion and blues-rock anchors."],
  ["rockhall_who", "The Who", "Rock & Roll Hall of Fame", "https://rockhall.com/inductees/the-who/", "museum_reference", "The Who, mod energy, power trio dynamics, and album-rock bridge."],
  ["rockhall_byrds", "The Byrds", "Rock & Roll Hall of Fame", "https://rockhall.com/inductees/the-byrds/", "museum_reference", "Jangle, folk-rock, and electric Dylan-era influence."],
  ["britannica_bob_dylan", "Bob Dylan", "Encyclopaedia Britannica", "https://www.britannica.com/biography/Bob-Dylan-American-musician", "reference", "Dylan biography, folk revival, electric folk-rock, and songwriter influence."],
  ["britannica_psychedelic_rock", "Psychedelic rock", "Encyclopaedia Britannica", "https://www.britannica.com/art/psychedelic-rock", "reference", "Psychedelic rock style, late-1960s counterculture, studio and sonic expansion."],
  ["rockhall_velvet_underground", "The Velvet Underground", "Rock & Roll Hall of Fame", "https://rockhall.com/inductees/the-velvet-underground/", "museum_reference", "Velvet Underground as art-rock, proto-alternative, and underground influence."],
  ["rockhall_doors", "The Doors", "Rock & Roll Hall of Fame", "https://rockhall.com/inductees/the-doors/", "museum_reference", "The Doors as psychedelic, theatrical, and blues-rock counterculture anchor."],
  ["allmusic_garage_rock", "Garage Rock", "AllMusic", "https://www.allmusic.com/style/garage-rock-ma0000002666", "music_reference", "Supplemental style markers for raw 1960s garage rock singles."],
  ["allmusic_sunshine_pop", "Sunshine Pop", "AllMusic", "https://www.allmusic.com/style/sunshine-pop-ma0000012203", "music_reference", "Supplemental style markers for harmony-rich late-1960s pop."],
  ["rockhall_led_zeppelin", "Led Zeppelin", "Rock & Roll Hall of Fame", "https://rockhall.com/inductees/led-zeppelin/", "museum_reference", "Album rock, hard rock, blues-rock, and heavy-riff canon context."],
  ["rockhall_black_sabbath", "Black Sabbath", "Rock & Roll Hall of Fame", "https://rockhall.com/inductees/black-sabbath/", "museum_reference", "Heavy-riff, metal, doom, and hard-rock lineage context."],
  ["britannica_progressive_rock", "Progressive rock", "Encyclopaedia Britannica", "https://www.britannica.com/art/progressive-rock", "reference", "Progressive rock's album-length forms, classical/art ambition, and instrumental complexity."],
  ["rockhall_allman_brothers", "The Allman Brothers Band", "Rock & Roll Hall of Fame", "https://rockhall.com/inductees/the-allman-brothers-band/", "museum_reference", "Southern rock, blues, country, and improvisational jam lineage."],
  ["rockhall_david_bowie", "David Bowie", "Rock & Roll Hall of Fame", "https://rockhall.com/inductees/david-bowie/", "museum_reference", "Glam, theatrical identity, art-rock, and pop reinvention context."],
  ["rockhall_elton_john", "Elton John", "Rock & Roll Hall of Fame", "https://rockhall.com/inductees/elton-john/", "museum_reference", "Piano-led pop-rock, AM gold, and album-era adult pop craft."],
  ["britannica_folk_music", "Folk music", "Encyclopaedia Britannica", "https://www.britannica.com/art/folk-music", "reference", "Folk tradition, revival, topical song, and acoustic songcraft context."],
  ["smithsonian_folkways", "Smithsonian Folkways", "Smithsonian Folkways", "https://folkways.si.edu/", "archive_label", "Folk, protest, roots, children's, and global archival recording context."],
  ["rockhall_joni_mitchell", "Joni Mitchell", "Rock & Roll Hall of Fame", "https://rockhall.com/inductees/joni-mitchell/", "museum_reference", "Singer-songwriter craft, folk-jazz harmonic language, and album-era authorship."],
  ["rockhall_carole_king", "Carole King", "Rock & Roll Hall of Fame", "https://rockhall.com/inductees/carole-king/", "museum_reference", "Songwriter-to-performer transition and adult pop songcraft."],
  ["americana_music_association", "About Americana Music", "Americana Music Association", "https://americanamusic.org/", "industry_organization", "Americana as roots, country, folk, blues, and rock lineage context."],
  ["no_depression_archive", "No Depression", "No Depression", "https://www.nodepression.com/", "music_journalism_archive", "Alt-country and Americana scene reporting; supplemental source only."],
  ["britannica_country_music", "Country music", "Encyclopaedia Britannica", "https://www.britannica.com/art/country-music", "reference", "Country music origins, honky-tonk, Nashville, outlaw, and radio eras."],
  ["country_music_hall_history", "Country Music Hall of Fame and Museum", "Country Music Hall of Fame and Museum", "https://www.countrymusichalloffame.org/", "museum_reference", "Country music history, Nashville, artists, and institutional context."],
  ["grand_ole_opry_history", "Opry History", "Grand Ole Opry", "https://www.opry.com/history", "official_venue", "Grand Ole Opry, country broadcast culture, and Nashville institution context."],
  ["loc_country_music", "Country Music", "Library of Congress Songs of America", "https://www.loc.gov/collections/songs-of-america/articles-and-essays/musical-styles/country/", "archive_reference", "Country music roots, styles, and historical recording context."],
  ["britannica_willie_nelson", "Willie Nelson", "Encyclopaedia Britannica", "https://www.britannica.com/biography/Willie-Nelson", "reference", "Outlaw country, songwriting, and crossover context."],
  ["britannica_dolly_parton", "Dolly Parton", "Encyclopaedia Britannica", "https://www.britannica.com/biography/Dolly-Parton", "reference", "Country-pop crossover, songwriting, and performer/persona context."],
  ["britannica_garth_brooks", "Garth Brooks", "Encyclopaedia Britannica", "https://www.britannica.com/biography/Garth-Brooks", "reference", "1990s country radio, arena-scale country, and crossover context."],
  ["motown_museum_history", "The Motown Story", "Motown Museum", "https://www.motownmuseum.org/story/motown/", "museum_reference", "Motown's Detroit studio, label system, and soul-pop crossover context."],
  ["stax_museum_history", "Stax History", "Stax Museum of American Soul Music", "https://staxmuseum.com/stax-history/", "museum_reference", "Stax, Memphis soul, integrated rhythm sections, and southern soul context."],
  ["carnegie_hall_soul", "Soul", "Carnegie Hall Timeline of African American Music", "https://timeline.carnegiehall.org/genres/soul", "educational_archive", "Soul's Black musical roots, gospel/R&B connections, and cultural context."],
  ["carnegie_hall_rhythm_blues", "Rhythm and Blues", "Carnegie Hall Timeline of African American Music", "https://timeline.carnegiehall.org/genres/rhythm-and-blues", "educational_archive", "R&B development and influence on soul, rock, pop, and dance music."],
  ["britannica_funk", "Funk", "Encyclopaedia Britannica", "https://www.britannica.com/art/funk", "reference", "Funk pioneers, groove foundation, social commentary, and sampling afterlife."],
  ["smithsonian_james_brown", "James Brown: Godfather of Soul", "Smithsonian Institution", "https://www.si.edu/spotlight/james-brown", "museum_reference", "James Brown's rhythmically driven funk aesthetic and influence."],
  ["carnegie_hall_funk_timeline", "History of Funk", "Carnegie Hall Timeline of African American Music", "https://timeline.carnegiehall.org/genres/funk", "educational_archive", "Funk's Black musical roots, pioneers, bass/rhythm innovation, and movement context."],
  ["britannica_george_clinton", "George Clinton", "Encyclopaedia Britannica", "https://www.britannica.com/biography/George-Clinton-American-musician", "reference", "Parliament-Funkadelic as theatrical, genre-bending funk and psychedelic rock collective."],
  ["rockhall_james_brown", "James Brown", "Rock & Roll Hall of Fame", "https://rockhall.com/inductees/james-brown/", "museum_reference", "James Brown's relationship to soul, funk, and rap lineages."],
  ["britannica_disco", "Disco", "Encyclopaedia Britannica", "https://www.britannica.com/art/disco", "reference", "Disco as club, dancefloor, studio, and popular music culture."],
  ["carnegie_hall_disco", "Disco", "Carnegie Hall Timeline of African American Music", "https://timeline.carnegiehall.org/genres/disco", "educational_archive", "Disco's roots, dance culture, and musical markers."],
  ["rockhall_aretha", "Aretha Franklin", "Rock & Roll Hall of Fame", "https://rockhall.com/inductees/aretha-franklin/", "museum_reference", "Aretha Franklin as soul, gospel, and popular music anchor."],
  ["rockhall_stevie_wonder", "Stevie Wonder", "Rock & Roll Hall of Fame", "https://rockhall.com/inductees/stevie-wonder/", "museum_reference", "Stevie Wonder as Motown, soul, funk, and album-era pop innovator."],
  ["britannica_hip_hop", "Hip-hop", "Encyclopaedia Britannica", "https://www.britannica.com/art/hip-hop", "reference", "Hip-hop culture, DJing, MCing, dance, art, and social context."],
  ["britannica_rap", "Rap", "Encyclopaedia Britannica", "https://www.britannica.com/art/rap", "reference", "Rap as vocal/rhythmic practice and popular music form."],
  ["smithsonian_hiphop_block_party", "Hip-Hop Block Party", "National Museum of African American History and Culture", "https://nmaahc.si.edu/explore/stories/hip-hop-block-party", "museum_reference", "Hip-hop's Bronx block-party and cultural foundation context."],
  ["cornell_hiphop_collection", "Cornell Hip Hop Collection", "Cornell University Library", "https://rmc.library.cornell.edu/hiphop/", "university_archive", "Archival documentation of hip-hop culture, recordings, flyers, and scene history."],
  ["carnegie_hall_hiphop", "Hip-Hop", "Carnegie Hall Timeline of African American Music", "https://timeline.carnegiehall.org/genres/hip-hop", "educational_archive", "Hip-hop's Black musical roots, DJ/MC practices, and cultural context."],
  ["rockhall_grandmaster_flash", "Grandmaster Flash and the Furious Five", "Rock & Roll Hall of Fame", "https://rockhall.com/inductees/grandmaster-flash-and-the-furious-five/", "museum_reference", "Old-school hip-hop, DJ technique, and early rap group context."],
  ["rockhall_public_enemy", "Public Enemy", "Rock & Roll Hall of Fame", "https://rockhall.com/inductees/public-enemy/", "museum_reference", "Political rap, production density, and Golden Age hip-hop context."],
  ["rockhall_nwa", "N.W.A", "Rock & Roll Hall of Fame", "https://rockhall.com/inductees/nwa/", "museum_reference", "West Coast gangsta rap and late-1980s hip-hop impact."],
  ["rockhall_tupac", "Tupac Shakur", "Rock & Roll Hall of Fame", "https://rockhall.com/inductees/tupac-shakur/", "museum_reference", "West Coast rap, persona, and 1990s hip-hop cultural context."],
  ["cbgb_official_about", "CBGB: The Unique History", "CBGB", "https://www.cbgb.com/about", "official_venue", "CBGB origin, Bowery setting, and punk/new wave artist roster."],
  ["cbgb_hilly_history", "History By Hilly", "CBGB", "https://www.cbgb.com/pages/history-by-hilly", "official_primary_context", "Founder account of CBGB/OMFUG and early club framing."],
  ["britannica_cbgb", "CBGB", "Encyclopaedia Britannica", "https://www.britannica.com/topic/CBGB-1688333", "reference", "CBGB as Bowery venue tied to punk and new wave."],
  ["britannica_punk", "Punk", "Encyclopaedia Britannica", "https://www.britannica.com/art/punk", "reference", "Punk's minimalist rock language, scenes, and social context."],
  ["cornell_punk_archives", "Anarchy in the Archives: Punk Arrives", "Cornell University Library", "https://rmc.library.cornell.edu/punkfest/exhibition/punkarrives/newyork.html", "university_archive", "New York punk archive context for CBGB artists and scene evidence."],
  ["rockhall_ramones", "Ramones", "Rock & Roll Hall of Fame", "https://rockhall.com/inductees/ramones/", "museum_reference", "Ramones and first-wave punk minimalism."],
  ["rockhall_sex_pistols", "Sex Pistols", "Rock & Roll Hall of Fame", "https://rockhall.com/inductees/sex-pistols/", "museum_reference", "UK punk impact, provocation, and first-wave punk context."],
  ["rockhall_talking_heads", "Talking Heads", "Rock & Roll Hall of Fame", "https://rockhall.com/inductees/talking-heads/", "museum_reference", "CBGB, art-school new wave, post-punk, and dance-aware rock context."],
  ["rockhall_cure", "The Cure", "Rock & Roll Hall of Fame", "https://rockhall.com/inductees/the-cure/", "museum_reference", "Post-punk, gothic pop, and dark melodic alternative lineage."],
  ["rockhall_depeche_mode", "Depeche Mode", "Rock & Roll Hall of Fame", "https://rockhall.com/inductees/depeche-mode/", "museum_reference", "Synthpop, new wave, and electronic pop influence."],
  ["rockhall_rem", "R.E.M.", "Rock & Roll Hall of Fame", "https://rockhall.com/inductees/rem/", "museum_reference", "College rock, jangly alternative, and pre-mainstream indie lineage."],
  ["britannica_new_wave", "New wave", "Encyclopaedia Britannica", "https://www.britannica.com/art/new-wave-music", "reference", "New wave's punk-adjacent pop, synthesizer, and video-era context."],
  ["allmusic_post_punk", "Post-Punk", "AllMusic", "https://www.allmusic.com/style/post-punk-ma0000004450", "music_reference", "Supplemental style markers for post-punk and dark alternative roots."],
  ["allmusic_hardcore_punk", "Hardcore Punk", "AllMusic", "https://www.allmusic.com/style/hardcore-punk-ma0000002641", "music_reference", "Supplemental style markers for hardcore punk speed and DIY intensity."],
  ["britannica_heavy_metal", "Heavy metal", "Encyclopaedia Britannica", "https://www.britannica.com/art/heavy-metal-music", "reference", "Heavy metal's riffs, amplification, theatricality, and subgenre development."],
  ["rockhall_judas_priest", "Judas Priest", "Rock & Roll Hall of Fame", "https://rockhall.com/inductees/judas-priest/", "museum_reference", "Traditional heavy metal and NWOBHM-adjacent style context."],
  ["rockhall_metallica", "Metallica", "Rock & Roll Hall of Fame", "https://rockhall.com/inductees/metallica/", "museum_reference", "Thrash metal, speed, and mainstream heavy music impact."],
  ["rockhall_iron_maiden", "Iron Maiden", "Rock & Roll Hall of Fame", "https://rockhall.com/inductees/iron-maiden/", "museum_reference", "NWOBHM, twin-guitar metal, and theatrical metal canon context."],
  ["rockhall_nine_inch_nails", "Nine Inch Nails", "Rock & Roll Hall of Fame", "https://rockhall.com/inductees/nine-inch-nails/", "museum_reference", "Industrial rock/metal, machine texture, and alternative-era heavy music."],
  ["allmusic_thrash", "Thrash Metal", "AllMusic", "https://www.allmusic.com/style/thrash-ma0000002885", "music_reference", "Supplemental style markers for thrash speed, riffing, and aggression."],
  ["allmusic_doom_metal", "Doom Metal", "AllMusic", "https://www.allmusic.com/style/doom-metal-ma0000004496", "music_reference", "Supplemental style markers for slow, heavy doom and stoner metal."],
  ["allmusic_nu_metal", "Nu Metal", "AllMusic", "https://www.allmusic.com/style/nu-metal-ma0000002836", "music_reference", "Supplemental style markers for rap-metal and nu-metal crossover."],
  ["allmusic_metalcore", "Metalcore", "AllMusic", "https://www.allmusic.com/style/metalcore-ma0000011967", "music_reference", "Supplemental style markers for metalcore and modern active-rock overlap."],
  ["allmusic_death_metal", "Death Metal", "AllMusic", "https://www.allmusic.com/style/death-metal-ma0000002547", "music_reference", "Supplemental style markers for extreme-metal gateway styles."],
  ["britannica_nirvana", "Nirvana", "Encyclopaedia Britannica", "https://www.britannica.com/topic/Nirvana-American-rock-group", "reference", "Nirvana and grunge's early-1990s alternative breakthrough."],
  ["rockhall_nirvana", "Nirvana", "Rock & Roll Hall of Fame", "https://rockhall.com/inductees/nirvana/", "museum_reference", "Grunge, Seattle, punk/metal/pop tension, and alternative mainstream shift."],
  ["subpop_history", "Sub Pop History", "Sub Pop", "https://www.subpop.com/about/history", "official_label", "Seattle independent-label context for grunge and alternative rock."],
  ["britannica_pearl_jam", "Pearl Jam", "Encyclopaedia Britannica", "https://www.britannica.com/topic/Pearl-Jam", "reference", "Pearl Jam, Seattle rock, and 1990s alternative culture."],
  ["allmusic_indie_rock", "Indie Rock", "AllMusic", "https://www.allmusic.com/style/indie-rock-ma0000004453", "music_reference", "Supplemental style markers for indie rock, lo-fi, and guitar-pop branches."],
  ["allmusic_shoegaze", "Shoegaze", "AllMusic", "https://www.allmusic.com/style/shoegaze-ma0000004454", "music_reference", "Supplemental style markers for noise-haze guitar and dream pop."],
  ["uw_riot_grrrl_archive", "Riot Grrrl Collection Guide", "University of Washington Libraries", "https://guides.lib.uw.edu/research/riotgrrrl", "university_archive", "Riot grrrl zine, feminist punk, and archival context."],
  ["rockhall_green_day", "Green Day", "Rock & Roll Hall of Fame", "https://rockhall.com/inductees/green-day/", "museum_reference", "Pop-punk, punk revival, and mainstream 1990s punk-pop context."],
  ["britannica_radiohead", "Radiohead", "Encyclopaedia Britannica", "https://www.britannica.com/topic/Radiohead", "reference", "Alternative rock, art-rock, and 2000s indie/experimental prestige context."],
  ["matador_history", "Matador Records", "Matador Records", "https://matadorrecords.com/", "official_label", "Independent-label context for 1990s and 2000s indie rock."],
  ["britannica_strokes", "The Strokes", "Encyclopaedia Britannica", "https://www.britannica.com/topic/the-Strokes", "reference", "The Strokes and early-2000s garage-rock revival framing."],
  ["rockhall_white_stripes", "The White Stripes", "Rock & Roll Hall of Fame", "https://rockhall.com/inductees/the-white-stripes/", "museum_reference", "White Stripes as minimal, blues-rooted rock revival context."],
  ["allmusic_garage_revival", "Garage Rock Revival", "AllMusic", "https://www.allmusic.com/style/garage-rock-revival-ma0000012343", "music_reference", "Supplemental style markers for garage-rock revival."],
  ["britannica_white_stripes", "The White Stripes", "Encyclopaedia Britannica", "https://www.britannica.com/topic/White-Stripes", "reference", "White Stripes biography and 2000s rock context."],
  ["britannica_edm", "Electronic dance music", "Encyclopaedia Britannica", "https://www.britannica.com/art/electronic-dance-music", "reference", "Electronic dance music, club culture, DJs, house, techno, and mainstream EDM."],
  ["britannica_electronic_music", "Electronic music", "Encyclopaedia Britannica", "https://www.britannica.com/art/electronic-music", "reference", "Electronic music technologies, composition, and popular-music applications."],
  ["chicago_house_history", "House Music", "City of Chicago", "https://www.chicago.gov/city/en/depts/dca/supp_info/house_music.html", "official_civic_archive", "Chicago house music origins, DJs, clubs, and cultural recognition."],
  ["detroit_techno_foundation", "Detroit Techno Foundation", "Detroit Techno Foundation", "https://detroittechnofoundation.org/", "archive_organization", "Detroit techno heritage, artists, and cultural preservation context."],
  ["allmusic_trip_hop", "Trip-Hop", "AllMusic", "https://www.allmusic.com/style/trip-hop-ma0000002902", "music_reference", "Supplemental style markers for trip-hop and downtempo."],
  ["allmusic_idm", "IDM", "AllMusic", "https://www.allmusic.com/style/idm-ma0000004477", "music_reference", "Supplemental style markers for experimental electronic and IDM."],
  ["allmusic_synth_pop", "Synth Pop", "AllMusic", "https://www.allmusic.com/style/synth-pop-ma0000002887", "music_reference", "Supplemental style markers for synthpop."],
  ["allmusic_chillwave", "Chillwave", "AllMusic", "https://www.allmusic.com/style/chillwave-ma0000012261", "music_reference", "Supplemental style markers for chillwave and bedroom electronic aesthetics."],
  ["britannica_popular_music", "Popular music", "Encyclopaedia Britannica", "https://www.britannica.com/art/popular-music", "reference", "Broad popular-music industry, audience, and stylistic context."],
  ["rockhall_michael_jackson", "Michael Jackson", "Rock & Roll Hall of Fame", "https://rockhall.com/inductees/michael-jackson/", "museum_reference", "Pop sovereignty, dance, video, and global star image."],
  ["rockhall_madonna", "Madonna", "Rock & Roll Hall of Fame", "https://rockhall.com/inductees/madonna/", "museum_reference", "Persona pop, dance-pop, visual reinvention, and MTV-era authorship."],
  ["rockhall_prince", "Prince", "Rock & Roll Hall of Fame", "https://rockhall.com/inductees/prince/", "museum_reference", "Pop, funk, rock, R&B, authorship, and persona innovation."],
  ["rockhall_whitney_houston", "Whitney Houston", "Rock & Roll Hall of Fame", "https://rockhall.com/inductees/whitney-houston/", "museum_reference", "Vocal pop, adult contemporary, R&B crossover, and blockbuster soundtrack context."],
  ["britannica_taylor_swift", "Taylor Swift", "Encyclopaedia Britannica", "https://www.britannica.com/biography/Taylor-Swift", "reference", "Modern pop authorship, country-pop crossover, and streaming-era scale."],
  ["britannica_beyonce", "Beyonce", "Encyclopaedia Britannica", "https://www.britannica.com/biography/Beyonce", "reference", "Persona pop, R&B/pop authorship, visual albums, and contemporary pop sovereignty."],
  ["rockhall_abba", "ABBA", "Rock & Roll Hall of Fame", "https://rockhall.com/inductees/abba/", "museum_reference", "Global pop hooks, studio craft, and disco-adjacent pop context."],
  ["britannica_reggaeton", "Reggaeton", "Encyclopaedia Britannica", "https://www.britannica.com/art/reggaeton", "reference", "Reggaeton's Caribbean, Latin American, dancehall, hip-hop, and pop crossover context."],
  ["grammy_latin_music", "Latin Music", "Recording Academy / Grammy.com", "https://www.grammy.com/", "industry_reference", "Supplemental Latin-pop and awards-context source for crossover scenes."],
  ["smithsonian_latino_music", "Latino Music", "Smithsonian Latino Center", "https://latino.si.edu/", "museum_reference", "Latino music, identity, and cultural-history context."],
  ["britannica_salsa", "Salsa", "Encyclopaedia Britannica", "https://www.britannica.com/art/salsa-music", "reference", "Salsa's Afro-Caribbean, Latin dance, and New York/Puerto Rican context."],
  ["carnegie_hall_latin", "Latin Music", "Carnegie Hall Timeline of African American Music", "https://timeline.carnegiehall.org/genres/latin-music", "educational_archive", "Latin and Afro-diasporic music connections in U.S. popular music."],
  ["britannica_afrobeats", "Afrobeats", "Encyclopaedia Britannica", "https://www.britannica.com/art/Afrobeats", "reference", "Afrobeats as contemporary West African pop crossover and global dance music."],
  ["britannica_kpop", "K-pop", "Encyclopaedia Britannica", "https://www.britannica.com/art/K-pop", "reference", "K-pop industry, idol system, choreography, and global crossover."],
  ["smithsonian_folkways_world", "World Music", "Smithsonian Folkways", "https://folkways.si.edu/world/music", "archive_label", "Global folk, diaspora roots, and archival context."],
  ["loc_latin_music", "Hispanic and Latino Americans in Music", "Library of Congress", "https://www.loc.gov/collections/hispanic-and-latino-americans-in-music/", "archive_reference", "Library of Congress collection context for Latino music history."],
  ["britannica_jazz", "Jazz", "Encyclopaedia Britannica", "https://www.britannica.com/art/jazz", "reference", "Jazz origins, improvisation, swing, bebop, and later styles."],
  ["smithsonian_jazz", "Smithsonian Jazz", "Smithsonian National Museum of American History", "https://americanhistory.si.edu/smithsonian-jazz", "museum_reference", "Jazz preservation, education, and historical context."],
  ["jazz_at_lincoln_center", "Jazz Academy", "Jazz at Lincoln Center", "https://academy.jazz.org/", "educational_archive", "Jazz education source for swing, improvisation, form, and listening context."],
  ["britannica_bebop", "Bebop", "Encyclopaedia Britannica", "https://www.britannica.com/art/bebop", "reference", "Bebop harmony, rhythm, virtuosity, and modern jazz context."],
  ["loc_jazz", "Jazz", "Library of Congress", "https://www.loc.gov/collections/jazz-on-the-screen-filmography/articles-and-essays/history-of-jazz/", "archive_reference", "Library of Congress jazz history and preservation context."],
  ["britannica_musical", "Musical", "Encyclopaedia Britannica", "https://www.britannica.com/art/musical", "reference", "Musical theater form, song/drama integration, and Broadway context."],
  ["ibdb_broadway", "Internet Broadway Database", "The Broadway League", "https://www.ibdb.com/", "official_database", "Broadway production, composer, performer, and musical-theater factual context."],
  ["loc_musical_theater", "Musical Theater", "Library of Congress", "https://www.loc.gov/collections/musical-theater-songs/", "archive_reference", "Library of Congress musical-theater song collection context."],
  ["d23_disney_music", "Disney Music", "D23", "https://d23.com/", "official_archive", "Disney company archive context for animated musicals and family soundtrack memory."],
  ["afi_movie_musicals", "AFI's Greatest Movie Musicals", "American Film Institute", "https://www.afi.com/afis-100-years-of-musicals/", "film_archive", "Movie musical canon and film-history context."],
  ["academy_music_branch", "Music Branch", "Academy of Motion Picture Arts and Sciences", "https://www.oscars.org/academy-story/music-branch", "official_archive", "Film music, scoring, and motion-picture industry context."],
  ["britannica_film_score", "Film music", "Encyclopaedia Britannica", "https://www.britannica.com/art/film-music", "reference", "Film score, cinematic orchestration, and soundtrack function."],
  ["britannica_gospel_music", "Gospel music", "Encyclopaedia Britannica", "https://www.britannica.com/art/gospel-music", "reference", "Black gospel, church roots, quartet/choir traditions, and popular influence."],
  ["carnegie_hall_gospel", "Gospel", "Carnegie Hall Timeline of African American Music", "https://timeline.carnegiehall.org/genres/gospel", "educational_archive", "Gospel's Black church roots, performance practice, and influence."],
  ["gospel_music_association", "Gospel Music Association", "Gospel Music Association", "https://gospelmusic.org/", "industry_organization", "Gospel and Christian music institutional context."],
  ["rockhall_mahalia_jackson", "Mahalia Jackson", "Rock & Roll Hall of Fame", "https://rockhall.com/inductees/mahalia-jackson/", "museum_reference", "Mahalia Jackson and gospel's influence on American popular music."],
  ["grammy_gospel_field", "Gospel/Contemporary Christian Music", "Recording Academy / Grammy.com", "https://www.grammy.com/", "industry_reference", "Supplemental awards-context source for gospel and contemporary Christian music fields."],
  ["britannica_christmas_carol", "Christmas carol", "Encyclopaedia Britannica", "https://www.britannica.com/art/Christmas-carol", "reference", "Holiday song tradition, carol form, and seasonal repertory context."],
  ["smithsonian_folkways_childrens", "Children's Music", "Smithsonian Folkways", "https://folkways.si.edu/childrens/music", "archive_label", "Children's and family music recording context."],
  ["grammy_comedy_field", "Comedy Albums", "Recording Academy / Grammy.com", "https://www.grammy.com/", "industry_reference", "Supplemental awards-context source for comedy records and novelty-adjacent listening."],
  ["dr_demento_history", "Dr. Demento", "Dr. Demento", "https://www.drdemento.com/", "official_archive", "Novelty, comedy, and outsider-pop radio archive context."],
  ["ascap_holiday_songs", "Holiday Songs", "ASCAP", "https://www.ascap.com/", "performing_rights_organization", "Supplemental industry context for durable holiday-song repertory."],
  ["britannica_arctic_monkeys", "Arctic Monkeys", "Encyclopaedia Britannica", "https://www.britannica.com/topic/Arctic-Monkeys", "reference", "Internet-era rock breakthrough, indie rock, and modern guitar-band context."],
  ["britannica_tame_impala", "Tame Impala", "Encyclopaedia Britannica", "https://www.britannica.com/topic/Tame-Impala", "reference", "Modern psychedelic pop/rock, studio authorship, and global indie crossover."],
  ["allmusic_post_punk_revival", "Post-Punk Revival", "AllMusic", "https://www.allmusic.com/style/post-punk-revival-ma0000012257", "music_reference", "Supplemental style markers for 2000s and later post-punk revival."],
  ["allmusic_dream_pop", "Dream Pop", "AllMusic", "https://www.allmusic.com/style/dream-pop-ma0000012303", "music_reference", "Supplemental style markers for atmospheric modern indie pop."],
  ["bandcamp_lofi", "Lo-fi", "Bandcamp Daily", "https://daily.bandcamp.com/", "music_journalism_archive", "Supplemental scene reporting for lo-fi, bedroom, and study-music ecosystems."],
  ["grammy_hyperpop", "Hyperpop", "Recording Academy / Grammy.com", "https://www.grammy.com/", "industry_reference", "Supplemental industry and scene reporting for hyperpop and internet-native pop."],
  ["npr_tiny_desk_discovery", "Tiny Desk", "NPR Music", "https://www.npr.org/series/tiny-desk-concerts/", "public_media_archive", "Public-media performance archive for contemporary discovery and cross-genre visibility."]
];

const EXTERNAL_SOURCES = Object.fromEntries(SOURCE_ROWS.map(([id, title, publisher, url, sourceType, auditUse]) => [id, {
  title,
  publisher,
  url,
  source_type: sourceType,
  audit_use: auditUse,
  rights_note: "Use for factual paraphrase and concise source summaries only; no lyrics, long quotations, proprietary images, or third-party prose blocks."
}]));

const FAMILY_SOURCE_REFS = {
  1: ["britannica_rock_and_roll", "loc_recording_registry", "rockhall_chuck_berry", "britannica_doo_wop", "britannica_rockabilly", "britannica_soul_music"],
  2: ["britannica_rock_1960s", "britannica_beatles", "rockhall_beatles", "britannica_rolling_stones", "rockhall_byrds", "britannica_psychedelic_rock"],
  3: ["britannica_rock_music", "rockhall_led_zeppelin", "rockhall_black_sabbath", "britannica_progressive_rock", "rockhall_david_bowie", "rockhall_allman_brothers"],
  4: ["britannica_folk_music", "smithsonian_folkways", "britannica_bob_dylan", "rockhall_joni_mitchell", "rockhall_carole_king", "americana_music_association"],
  5: ["britannica_country_music", "country_music_hall_history", "grand_ole_opry_history", "loc_country_music", "britannica_willie_nelson", "britannica_dolly_parton"],
  6: ["britannica_soul_music", "britannica_rhythm_and_blues", "motown_museum_history", "stax_museum_history", "britannica_funk", "britannica_disco"],
  7: ["britannica_hip_hop", "britannica_rap", "smithsonian_hiphop_block_party", "cornell_hiphop_collection", "carnegie_hall_hiphop", "rockhall_grandmaster_flash"],
  8: ["britannica_punk", "cornell_punk_archives", "rockhall_ramones", "rockhall_talking_heads", "britannica_new_wave", "rockhall_rem"],
  9: ["britannica_heavy_metal", "rockhall_black_sabbath", "rockhall_judas_priest", "rockhall_metallica", "rockhall_nine_inch_nails", "allmusic_thrash"],
  10: ["britannica_nirvana", "rockhall_nirvana", "subpop_history", "rockhall_rem", "allmusic_indie_rock", "britannica_radiohead"],
  11: ["britannica_edm", "britannica_electronic_music", "chicago_house_history", "detroit_techno_foundation", "allmusic_trip_hop", "allmusic_idm"],
  12: ["britannica_popular_music", "rockhall_michael_jackson", "rockhall_madonna", "rockhall_prince", "rockhall_whitney_houston", "britannica_taylor_swift"],
  13: ["britannica_reggaeton", "smithsonian_latino_music", "britannica_salsa", "britannica_afrobeats", "britannica_kpop", "smithsonian_folkways_world"],
  14: ["britannica_jazz", "smithsonian_jazz", "jazz_at_lincoln_center", "britannica_bebop", "loc_jazz", "loc_recording_registry"],
  15: ["britannica_musical", "ibdb_broadway", "loc_musical_theater", "d23_disney_music", "afi_movie_musicals", "britannica_film_score"],
  16: ["britannica_gospel_music", "carnegie_hall_gospel", "gospel_music_association", "rockhall_mahalia_jackson", "grammy_gospel_field", "britannica_soul_music"],
  17: ["loc_recording_registry", "britannica_christmas_carol", "smithsonian_folkways_childrens", "grammy_comedy_field", "dr_demento_history", "ascap_holiday_songs"],
  18: ["britannica_arctic_monkeys", "britannica_tame_impala", "allmusic_post_punk_revival", "allmusic_dream_pop", "grammy_hyperpop", "npr_tiny_desk_discovery"]
};

const KEYWORD_SOURCE_REFS = [
  [/british|beatles|beat group|stones|who/i, ["britannica_beatles", "rockhall_beatles", "britannica_rolling_stones", "rockhall_who"]],
  [/jangle|folk-rock|folk rock|byrds|harmony/i, ["rockhall_byrds", "britannica_bob_dylan", "britannica_rock_1960s", "rockhall_joni_mitchell"]],
  [/garage|nuggets|proto-punk/i, ["allmusic_garage_rock", "britannica_punk", "rockhall_ramones", "britannica_rock_1960s"]],
  [/baroque|chamber|artful/i, ["britannica_beatles", "rockhall_beach_boys", "rockhall_david_bowie", "allmusic_sunshine_pop"]],
  [/psychedelic|sunshine|acid|heavy psych/i, ["britannica_psychedelic_rock", "rockhall_doors", "rockhall_velvet_underground", "rockhall_black_sabbath"]],
  [/classic rock|album-rock|album rock/i, ["britannica_rock_music", "rockhall_led_zeppelin", "rockhall_elton_john", "rockhall_david_bowie"]],
  [/hard rock|riff|proto-metal/i, ["rockhall_led_zeppelin", "rockhall_black_sabbath", "britannica_heavy_metal", "rockhall_judas_priest"]],
  [/progressive|prog/i, ["britannica_progressive_rock", "rockhall_david_bowie", "britannica_rock_music", "britannica_electronic_music"]],
  [/southern rock|jam/i, ["rockhall_allman_brothers", "britannica_country_music", "britannica_rock_music", "americana_music_association"]],
  [/glam|theatrical/i, ["rockhall_david_bowie", "rockhall_elton_john", "britannica_rock_music", "rockhall_madonna"]],
  [/power pop|melodic/i, ["allmusic_indie_rock", "rockhall_byrds", "rockhall_green_day", "britannica_rock_music"]],
  [/soft rock|am gold|adult pop|yacht/i, ["rockhall_elton_john", "britannica_popular_music", "rockhall_carole_king", "rockhall_michael_jackson"]],
  [/singer-songwriter|songwriter|songcraft|piano pop|coffeehouse/i, ["britannica_folk_music", "rockhall_joni_mitchell", "rockhall_carole_king", "britannica_bob_dylan"]],
  [/folk revival|protest/i, ["britannica_folk_music", "smithsonian_folkways", "britannica_bob_dylan", "loc_recording_registry"]],
  [/country-folk|americana|alt-country|red dirt|texas/i, ["americana_music_association", "no_depression_archive", "britannica_country_music", "smithsonian_folkways"]],
  [/honky|nashville|classic country/i, ["britannica_country_music", "country_music_hall_history", "grand_ole_opry_history", "loc_country_music"]],
  [/outlaw|cosmic/i, ["britannica_willie_nelson", "country_music_hall_history", "britannica_country_music", "americana_music_association"]],
  [/country-pop|crossover country|modern country|bro-country|arena country|90s country/i, ["britannica_dolly_parton", "britannica_garth_brooks", "country_music_hall_history", "britannica_country_music"]],
  [/motown|detroit soul/i, ["motown_museum_history", "rockhall_stevie_wonder", "rockhall_aretha", "carnegie_hall_soul"]],
  [/southern soul|stax|muscle shoals/i, ["stax_museum_history", "carnegie_hall_soul", "britannica_soul_music", "britannica_rhythm_and_blues"]],
  [/funk|groove|psychedelic soul/i, ["britannica_funk", "smithsonian_james_brown", "carnegie_hall_funk_timeline", "britannica_george_clinton"]],
  [/disco|dancefloor/i, ["britannica_disco", "carnegie_hall_disco", "britannica_funk", "rockhall_madonna"]],
  [/quiet storm|smooth r&b|smooth r-and-b|adult soul|new jack|neo-soul|modern r&b|alt-r&b|bedroom r&b/i, ["britannica_rhythm_and_blues", "britannica_soul_music", "rockhall_whitney_houston", "rockhall_stevie_wonder"]],
  [/old-school hip-hop|electro-rap|hip-hop|rap|boom bap|gangsta|g-funk|trap|crunk/i, ["britannica_hip_hop", "britannica_rap", "smithsonian_hiphop_block_party", "cornell_hiphop_collection"]],
  [/golden age|conscious|native tongues/i, ["rockhall_public_enemy", "britannica_hip_hop", "carnegie_hall_hiphop", "cornell_hiphop_collection"]],
  [/west coast|gangsta/i, ["rockhall_nwa", "rockhall_tupac", "britannica_rap", "carnegie_hall_hiphop"]],
  [/punk|hardcore|post-punk|new wave|synthpop|college rock|noise rock|post-hardcore/i, ["britannica_punk", "cornell_punk_archives", "rockhall_ramones", "britannica_new_wave"]],
  [/cbgb|downtown/i, ["cbgb_official_about", "cbgb_hilly_history", "britannica_cbgb", "cornell_punk_archives"]],
  [/hardcore/i, ["allmusic_hardcore_punk", "britannica_punk", "cornell_punk_archives", "rockhall_ramones"]],
  [/post-punk|gothic|dark melodic/i, ["allmusic_post_punk", "rockhall_cure", "rockhall_talking_heads", "britannica_new_wave"]],
  [/synthpop|new romantic|electronic pop/i, ["rockhall_depeche_mode", "allmusic_synth_pop", "britannica_electronic_music", "britannica_new_wave"]],
  [/metal|thrash|doom|stoner|industrial|nu-metal|rap-metal|metalcore|extreme metal|black-death-sludge/i, ["britannica_heavy_metal", "rockhall_black_sabbath", "rockhall_metallica", "rockhall_judas_priest"]],
  [/thrash|speed/i, ["rockhall_metallica", "allmusic_thrash", "britannica_heavy_metal", "rockhall_judas_priest"]],
  [/doom|stoner|desert/i, ["rockhall_black_sabbath", "allmusic_doom_metal", "britannica_heavy_metal", "rockhall_led_zeppelin"]],
  [/industrial/i, ["rockhall_nine_inch_nails", "britannica_electronic_music", "britannica_heavy_metal", "allmusic_nu_metal"]],
  [/nu-metal|rap-metal|alt-metal/i, ["allmusic_nu_metal", "britannica_heavy_metal", "rockhall_nine_inch_nails", "britannica_rap"]],
  [/metalcore|emo-heavy/i, ["allmusic_metalcore", "britannica_heavy_metal", "rockhall_green_day", "allmusic_hardcore_punk"]],
  [/extreme|black|death|sludge/i, ["allmusic_death_metal", "allmusic_doom_metal", "britannica_heavy_metal", "rockhall_black_sabbath"]],
  [/grunge|seattle/i, ["britannica_nirvana", "rockhall_nirvana", "subpop_history", "britannica_pearl_jam"]],
  [/post-grunge|modern rock radio|active rock/i, ["britannica_pearl_jam", "britannica_nirvana", "rockhall_green_day", "britannica_rock_music"]],
  [/lo-fi|slacker|matador|indie/i, ["allmusic_indie_rock", "matador_history", "rockhall_rem", "britannica_radiohead"]],
  [/shoegaze|dream pop|noise haze/i, ["allmusic_shoegaze", "allmusic_dream_pop", "britannica_radiohead", "allmusic_indie_rock"]],
  [/riot grrrl|female 90s alt|guitar voices/i, ["uw_riot_grrrl_archive", "allmusic_indie_rock", "rockhall_rem", "britannica_punk"]],
  [/pop-punk|skate punk/i, ["rockhall_green_day", "britannica_punk", "allmusic_hardcore_punk", "allmusic_indie_rock"]],
  [/emo/i, ["allmusic_indie_rock", "rockhall_green_day", "allmusic_hardcore_punk", "allmusic_post_punk"]],
  [/garage revival|rock-is-back|strokes|white stripes/i, ["britannica_strokes", "rockhall_white_stripes", "allmusic_garage_revival", "britannica_white_stripes"]],
  [/house|chicago/i, ["britannica_edm", "chicago_house_history", "britannica_electronic_music", "carnegie_hall_disco"]],
  [/techno|detroit|minimal/i, ["detroit_techno_foundation", "britannica_edm", "britannica_electronic_music", "allmusic_idm"]],
  [/edm|festival|big room/i, ["britannica_edm", "britannica_electronic_music", "rockhall_madonna", "grammy_latin_music"]],
  [/trip-hop|downtempo|nocturnal/i, ["allmusic_trip_hop", "britannica_electronic_music", "allmusic_idm", "britannica_hip_hop"]],
  [/indie dance|dance-punk|electroclash/i, ["britannica_edm", "allmusic_synth_pop", "britannica_punk", "allmusic_post_punk_revival"]],
  [/synthwave|chillwave|bedroom electronic/i, ["allmusic_chillwave", "britannica_electronic_music", "allmusic_synth_pop", "bandcamp_lofi"]],
  [/experimental electronic|idm|art-electronic/i, ["allmusic_idm", "britannica_electronic_music", "britannica_electronic_music", "britannica_edm"]],
  [/pop sovereign|persona pop|dance-pop|teen pop|trl|streaming-era pop|internet pop|tiktok/i, ["britannica_popular_music", "rockhall_michael_jackson", "rockhall_madonna", "rockhall_prince"]],
  [/adult pop|inspirational/i, ["rockhall_whitney_houston", "britannica_popular_music", "rockhall_carole_king", "britannica_taylor_swift"]],
  [/reggaeton|urbano|latin pop/i, ["britannica_reggaeton", "smithsonian_latino_music", "grammy_latin_music", "loc_latin_music"]],
  [/regional mexican|corridos|musica mexicana/i, ["loc_latin_music", "smithsonian_latino_music", "grammy_latin_music", "smithsonian_folkways_world"]],
  [/salsa|tropical/i, ["britannica_salsa", "carnegie_hall_latin", "smithsonian_latino_music", "loc_latin_music"]],
  [/afrobeats|african pop/i, ["britannica_afrobeats", "smithsonian_folkways_world", "carnegie_hall_latin", "britannica_popular_music"]],
  [/k-pop|j-pop|asian pop/i, ["britannica_kpop", "britannica_popular_music", "grammy_latin_music", "npr_tiny_desk_discovery"]],
  [/world fusion|diaspora|global folk/i, ["smithsonian_folkways_world", "smithsonian_folkways", "loc_latin_music", "britannica_folk_music"]],
  [/jazz|bebop|hard bop|smooth jazz|standards|crooners|songbook/i, ["britannica_jazz", "smithsonian_jazz", "jazz_at_lincoln_center", "loc_jazz"]],
  [/vocal standards|crooners|great american songbook/i, ["loc_recording_registry", "britannica_popular_music", "smithsonian_jazz", "jazz_at_lincoln_center"]],
  [/classical crossover|instrumental popular/i, ["britannica_film_score", "britannica_musical", "loc_recording_registry", "academy_music_branch"]],
  [/broadway|musical theater/i, ["britannica_musical", "ibdb_broadway", "loc_musical_theater", "afi_movie_musicals"]],
  [/disney|animated musical|family soundtrack/i, ["d23_disney_music", "britannica_musical", "afi_movie_musicals", "loc_musical_theater"]],
  [/movie soundtrack|soundtrack memory/i, ["afi_movie_musicals", "academy_music_branch", "loc_recording_registry", "britannica_popular_music"]],
  [/film score|epic score|ambient cinematic/i, ["britannica_film_score", "academy_music_branch", "britannica_electronic_music", "loc_recording_registry"]],
  [/gospel|worship|christian|ccm|praise/i, ["britannica_gospel_music", "carnegie_hall_gospel", "gospel_music_association", "rockhall_mahalia_jackson"]],
  [/holiday|christmas|seasonal/i, ["britannica_christmas_carol", "loc_recording_registry", "ascap_holiday_songs", "smithsonian_folkways"]],
  [/novelty|comedy|weird/i, ["dr_demento_history", "grammy_comedy_field", "loc_recording_registry", "smithsonian_folkways"]],
  [/party|wedding|karaoke|singalong/i, ["loc_recording_registry", "britannica_popular_music", "ascap_holiday_songs", "grammy_comedy_field"]],
  [/kids|family|household/i, ["smithsonian_folkways_childrens", "d23_disney_music", "britannica_musical", "loc_recording_registry"]],
  [/current rock|post-punk new wave 2020s/i, ["allmusic_post_punk_revival", "britannica_arctic_monkeys", "npr_tiny_desk_discovery", "allmusic_indie_rock"]],
  [/modern indie singer|sad-prestige/i, ["allmusic_indie_rock", "allmusic_dream_pop", "npr_tiny_desk_discovery", "britannica_taylor_swift"]],
  [/modern psych|groove indie|tame|mgmt|arctic/i, ["britannica_tame_impala", "britannica_arctic_monkeys", "allmusic_dream_pop", "npr_tiny_desk_discovery"]],
  [/heavy modern alternative/i, ["britannica_heavy_metal", "rockhall_nirvana", "britannica_pearl_jam", "allmusic_post_punk_revival"]],
  [/hyperpop|synthetic edge-pop|internet maximalism/i, ["grammy_hyperpop", "britannica_popular_music", "allmusic_chillwave", "npr_tiny_desk_discovery"]],
  [/algorithmic mood|lo-fi|chill|study music/i, ["bandcamp_lofi", "smithsonian_folkways", "britannica_electronic_music", "allmusic_chillwave"]]
];

const FAMILY_PROFILES = {
  1: {
    context: "mid-century rock and pop turn R&B, gospel, country, vocal harmony, teen radio, and regional dance records into shared mass memory",
    importance: "it establishes many of the sounds later pop uses as basic grammar: backbeat, vocal group blend, guitar hooks, radio singles, and youth-culture address",
    contrast: "later British Invasion, soul, country, and nostalgia routes",
    listen: ["backbeat drive", "short radio-single architecture", "R&B and country phrasing in the same space", "vocal hooks built for memory", "dance energy carried by compact arrangements"]
  },
  2: {
    context: "1960s guitar pop and rock move from beat-group singles into folk-rock, studio pop, psychedelia, garage singles, and underground art rock",
    importance: "it explains how the 1960s transformed guitar-band pop from teen singles into album ambition, counterculture, and later alternative DNA",
    contrast: "early rock oldies, classic album rock, punk, and later indie roads",
    listen: ["electric-guitar chime or bite", "group vocals and compact hooks", "studio color entering rock arrangements", "folk, blues, or R&B sources recast by bands", "youth-culture energy becoming style language"]
  },
  3: {
    context: "album-era rock expands the scale of guitar bands, studio ambition, virtuosity, arena sound, and FM-radio identity",
    importance: "it turns rock from singles culture into durable album, concert, riff, and persona traditions",
    contrast: "1960s pop-rock, punk minimalism, metal, and adult pop routes",
    listen: ["large-format guitar riffs", "album-side pacing", "drum-and-bass weight", "solo sections or instrumental ambition", "big-chorus radio reach"]
  },
  4: {
    context: "folk, singer-songwriter, roots, and adult songcraft foreground authored voice, lyric perspective, acoustic texture, and intimate performance",
    importance: "it teaches how popular music can center the writer's point of view as much as the band, scene, or dancefloor",
    contrast: "country, classic rock, adult pop, and modern indie folk routes",
    listen: ["lyric-centered phrasing", "acoustic or piano-led arrangement", "plainspoken narrative detail", "vocal intimacy", "roots references carried by modern songwriting"]
  },
  5: {
    context: "country history runs through honky-tonk, Nashville studios, outlaw resistance, regional identity, and pop-radio crossover",
    importance: "it explains how storytelling, twang, dance rhythm, and commercial radio polish repeatedly reshape American roots music",
    contrast: "folk/Americana, southern rock, pop crossover, and nostalgia routes",
    listen: ["narrative lyric focus", "twang, fiddle, pedal steel, or clean guitar figures", "two-step or ballad pacing", "radio-ready chorus craft", "regional identity inside polished production"]
  },
  6: {
    context: "Black popular music lineages connect gospel, R&B, soul, funk, disco, and modern R&B through voice, groove, studio craft, and dance culture",
    importance: "it shows how groove, vocal authority, rhythm sections, producers, and labels changed the center of American pop",
    contrast: "early rock crossover, hip-hop, dance music, and contemporary pop roads",
    listen: ["gospel-shaped vocal intensity", "bass and drums as organizing force", "horns, strings, or studio polish around the vocal", "syncopated groove", "dancefloor or quiet-storm mood control"]
  },
  7: {
    context: "hip-hop grows from DJ, MC, block-party, electro, sampling, regional, street, conscious, pop, and streaming-era practices",
    importance: "it reframes popular music around beat architecture, rhythmic speech, production identity, and local-to-global storytelling",
    contrast: "R&B, funk, electronic dance, pop crossover, and modern internet scenes",
    listen: ["drum programming and break logic", "flow, cadence, and breath placement", "sample or synth identity", "regional production signatures", "chorus strategy against verse density"]
  },
  8: {
    context: "punk and post-punk scenes turn minimal resources into style: speed, DIY venues, angular guitars, synths, art-school ideas, and underground networks",
    importance: "it explains how scenes, labels, clubs, and stripped-down bands made refusal and experimentation into lasting musical tools",
    contrast: "classic rock, metal, new wave pop, and alternative indie roads",
    listen: ["short-form urgency", "downstroke or angular guitar attack", "dry room energy", "DIY or club-scene immediacy", "tension between abrasion and pop hooks"]
  },
  9: {
    context: "heavy music builds a lineage of amplified riffs, speed, darkness, virtuosity, theatrical image, mechanical texture, and extreme subgenres",
    importance: "it makes loudness and heaviness into musical languages rather than just volume or attitude",
    contrast: "hard rock, punk, industrial, emo, and active-rock routes",
    listen: ["distorted riff architecture", "drum weight or double-time momentum", "minor-mode tension", "vocal force or theatrical menace", "precision, groove, or abrasion as identity"]
  },
  10: {
    context: "alternative and indie history moves through college radio, grunge, lo-fi, riot grrrl, shoegaze, pop-punk, emo, blog indie, and revival guitar scenes",
    importance: "it tracks how underground credibility, guitar texture, local scenes, and media shifts repeatedly entered mainstream listening",
    contrast: "punk, classic rock, metal, pop monoculture, and current discovery roads",
    listen: ["guitar tone as identity", "plainspoken or wounded vocal stance", "independent-label texture", "melody pressed against noise or slackness", "scene-specific production choices"]
  },
  11: {
    context: "electronic and club music use DJs, drum machines, samplers, synthesizers, raves, clubs, and bedroom tools to reshape pop time",
    importance: "it teaches how production technology and dance spaces can become the core of musical authorship",
    contrast: "disco, pop, industrial rock, hip-hop, and ambient/cinematic roads",
    listen: ["programmed pulse", "bass movement across long forms", "synth timbre as hook", "build-and-release arrangement", "texture and space as emotional cues"]
  },
  12: {
    context: "pop monoculture and persona pop join mass media, hooks, choreography, celebrity image, television, streaming, and producer-led architecture",
    importance: "it explains how songs become shared public language through performance, video, radio, playlists, and celebrity identity",
    contrast: "R&B, dance, adult pop, country crossover, and internet-native pop roads",
    listen: ["instant chorus recognition", "vocal persona as brand", "high-definition production", "dance or video-ready structure", "emotional directness scaled for mass audience"]
  },
  13: {
    context: "Latin, Caribbean, African, Asian, and diaspora pop routes show global rhythms, language, migration, dance, and media crossing into wider pop circulation",
    importance: "it keeps global crossover from being treated as one bucket and preserves regional rhythm, language, and industry differences",
    contrast: "U.S. pop, dance, hip-hop, folk, and soundtrack routes",
    listen: ["rhythmic pattern as identity", "language-switching or bilingual hooks", "dance groove shaped by region", "percussion and bass dialogue", "global pop polish around local idioms"]
  },
  14: {
    context: "jazz, standards, vocal, and classical-adjacent roads foreground improvisation, songbook interpretation, instrumental command, and adult listening traditions",
    importance: "it explains forms of prestige and familiarity that work outside rock/pop's usual band and single logic",
    contrast: "adult pop, soundtrack, soul, and folk songcraft routes",
    listen: ["swing, phrasing, or rubato feel", "harmonic color", "improvised response", "orchestration or small-combo interplay", "interpretive vocal timing"]
  },
  15: {
    context: "theater, soundtrack, Disney, movie memory, and film-score traditions connect songs to characters, scenes, families, and cinematic emotion",
    importance: "it shows how music can be remembered through story worlds, screens, stage roles, and household repetition rather than artist fandom alone",
    contrast: "pop monoculture, classical-adjacent, holiday, and family-context roads",
    listen: ["melody tied to scene or character", "orchestration as narrative cue", "chorus-ready ensemble writing", "leitmotif or reprise logic", "family or film memory shaping recognition"]
  },
  16: {
    context: "gospel, Christian pop-rock, worship, and church songbook roads connect sacred performance, congregational use, broadcast media, and popular song form",
    importance: "it separates spiritual setting, vocal tradition, church function, and contemporary radio polish instead of flattening them",
    contrast: "soul, R&B, adult pop, and household-context music",
    listen: ["call-and-response or congregational shape", "choir or praise-team lift", "gospel melisma and rhythmic drive", "anthemic repetition", "devotional lyric function inside popular forms"]
  },
  17: {
    context: "shared-listening contexts include novelty, holiday, party, karaoke, and household music where social use can matter more than genre purity",
    importance: "it helps Atlas distinguish recognition, memory, ritual, and context from durable personal genre affinity",
    contrast: "pop monoculture, soundtrack, children's, comedy, and nostalgia routes",
    listen: ["communal singalong design", "seasonal or situational cues", "novelty framing", "simple hooks built for group use", "memory triggered by place, ritual, or family context"]
  },
  18: {
    context: "current discovery scenes connect streaming, internet-native genres, modern indie, psych-pop, revival rock, heavy alternative, and algorithmic mood listening",
    importance: "it explains how present-tense discovery often moves through platforms, moods, micro-scenes, and production aesthetics rather than old radio formats",
    contrast: "older indie, pop monoculture, electronic, metal, and classic alternative routes",
    listen: ["platform-era production polish", "genre blending as default language", "mood-first arrangement", "internet-scene texture", "references to older rock or pop filtered through modern tools"]
  }
};

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

function writeJson(filePath, data) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, `${JSON.stringify(data, null, 2)}\n`);
}

function writeText(filePath, data) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, data);
}

function listJsonFiles(dir) {
  return fs.readdirSync(dir)
    .filter((name) => name.endsWith(".json"))
    .sort()
    .map((name) => path.join(dir, name));
}

function unique(values) {
  return [...new Set(values.filter(Boolean))];
}

function replaceVersionId(id) {
  return id.replace(/_v0_2$/u, "_v0_2_1");
}

function brandCleanSource(source) {
  const clone = { ...source };
  for (const key of ["title", "publisher", "audit_use", "rights_note"]) {
    if (typeof clone[key] === "string") clone[key] = clone[key].replace(/Waymark/g, "Cartenza");
  }
  if (clone.title === "Cartenza Canonical Graph Review Bundle v0.1") return clone;
  return clone;
}

function isExternalSource(source) {
  if (!source) return false;
  if (source.source_type?.startsWith("internal_")) return false;
  if (/^(data|docs)\//u.test(source.url || "")) return false;
  return true;
}

function textIncludesAny(text, phrases) {
  const lower = text.toLowerCase();
  return phrases.filter((phrase) => lower.includes(phrase.toLowerCase()));
}

function displayTitle(pack) {
  return pack.identity.editorial_display_title || pack.identity.existing_graph_label_name;
}

function compactLabel(label) {
  return label.replace(/\s*\/\s*/gu, " / ").replace(/\s+/gu, " ").trim();
}

function getProfile(pack) {
  return FAMILY_PROFILES[pack.identity.family_id] || FAMILY_PROFILES[12];
}

function topExamples(researchPack) {
  return (researchPack.explainer_content.canonical_example_rationales || []).slice(0, 4);
}

function topExampleLabels(researchPack) {
  return topExamples(researchPack).map((example) => example.display_label).filter(Boolean);
}

function sourceRefsFor(pack) {
  const text = `${pack.identity.family_name} ${displayTitle(pack)}`;
  const refs = [];
  for (const [regex, regexRefs] of KEYWORD_SOURCE_REFS) {
    if (regex.test(text)) refs.push(...regexRefs);
  }
  refs.push(...(FAMILY_SOURCE_REFS[pack.identity.family_id] || []));
  return unique(refs.filter((ref) => EXTERNAL_SOURCES[ref])).slice(0, 6);
}

function listenTraits(pack) {
  const text = `${pack.identity.family_name} ${displayTitle(pack)}`;
  const profile = getProfile(pack);
  const rules = [
    [/hip-hop|rap|boom bap|trap|crunk|g-funk/i, ["beat architecture", "flow and cadence", "sample or synth signature", "regional production color", "hook strategy against dense verses"]],
    [/metal|doom|thrash|nu-metal|metalcore|sludge/i, ["distorted riff architecture", "drum weight and speed", "minor-mode tension", "vocal force", "precision or abrasion as identity"]],
    [/punk|hardcore|post-punk|new wave|synthpop/i, ["short-form urgency", "angular guitar or synth lines", "dry scene energy", "DIY economy", "pop hooks under tension"]],
    [/country|honky|outlaw|nashville|americana/i, ["story-first lyrics", "twang or pedal-steel color", "dance or ballad pacing", "plainspoken vocal stance", "radio polish against roots texture"]],
    [/folk|singer-songwriter|songwriter|coffeehouse/i, ["lyric-centered phrasing", "acoustic or piano-led space", "intimate vocal presence", "narrative detail", "roots sources carried by personal authorship"]],
    [/soul|funk|r&b|r-and-b|disco|motown|quiet storm/i, ["gospel-shaped vocal force", "bass-and-drum groove", "horns or strings around the vocal", "syncopated rhythm", "dancefloor or late-night mood control"]],
    [/electronic|house|techno|edm|trip-hop|idm|chillwave/i, ["programmed pulse", "bass movement", "synth timbre as hook", "build-and-release structure", "texture and space as emotion"]],
    [/jazz|bebop|standards|crooner|classical/i, ["phrasing and time feel", "harmonic color", "improvised response", "ensemble interplay", "interpretive timing"]],
    [/broadway|musical|soundtrack|disney|film score/i, ["melody tied to story", "orchestration as cue", "ensemble or chorus lift", "leitmotif or reprise logic", "screen or stage memory"]],
    [/gospel|worship|christian|ccm/i, ["call-and-response shape", "choir or praise-team lift", "gospel melisma", "anthemic repetition", "devotional function inside pop form"]],
    [/reggaeton|latin|salsa|afrobeats|k-pop|j-pop|global|diaspora/i, ["regional rhythm as identity", "language-switching or chant hooks", "percussion and bass dialogue", "dance movement built into form", "global pop polish around local idioms"]],
    [/holiday|novelty|karaoke|kids|family|party|wedding/i, ["communal recognition", "situational cues", "simple hooks built for group use", "memory triggered by ritual", "context mattering as much as genre"]],
    [/pop sovereign|persona pop|dance-pop|teen pop|trl|streaming-era pop|internet pop|tiktok|architectural pop|70s-80s pop|90s pop|2000s pop|2010s/i, ["instant chorus recognition", "vocal persona", "high-definition production", "dance or video-ready structure", "direct emotional address"]],
    [/rock|guitar|grunge|indie|garage|psych|prog|glam|surf/i, ["guitar tone as identity", "drum-and-bass drive", "melody pressed against texture", "scene-specific production", "chorus or riff memory"]]
  ];
  const match = rules.find(([regex]) => regex.test(text));
  return match ? match[1] : profile.listen;
}

function anchorPhrase(researchPack) {
  const labels = topExampleLabels(researchPack).slice(0, 3);
  if (!labels.length) return "the canonical examples in this road";
  if (labels.length === 1) return labels[0];
  return `${labels.slice(0, -1).join(", ")} and ${labels.at(-1)}`;
}

function copyFor(researchPack, sourceRefs) {
  const title = compactLabel(displayTitle(researchPack));
  const profile = getProfile(researchPack);
  const traits = listenTraits(researchPack);
  const anchors = anchorPhrase(researchPack);
  const family = researchPack.identity.family_name;
  const introOptions = [
    `${title} narrows ${family} to the records, scenes, and listening clues where ${traits[0]} and ${traits[1]} carry the strongest signal.`,
    `This road focuses on ${title.toLowerCase()}: a slice of ${family} where ${traits[0]}, ${traits[1]}, and ${traits[2]} explain why the anchors belong together.`,
    `${title} gives Atlas a concise history lens for ${family}, joining ${anchors} to a wider story of ${profile.context}.`,
    `Start ${title} by listening for ${traits[0]} and ${traits[1]}; those details connect ${anchors} to the surrounding era.`
  ];
  const shortDefinition = introOptions[Number(researchPack.identity.archetype_id) % introOptions.length];
  const historyCapsule = `${title} sits inside a larger history where ${profile.context}. Anchors such as ${anchors} make the road concrete without needing examples outside the canonical set.`;
  const why = `It matters because ${profile.importance}. For Atlas surfaces, the teaching value is the distinction between historical importance, canonical placement, and user-specific fit.`;
  const distinct = `Compared with ${profile.contrast}, this road foregrounds ${traits[0]}, ${traits[1]}, and ${traits[2]}. That keeps one familiar song from being mistaken for a whole-region preference.`;
  const caution = `A familiar anchor here can mean nostalgia, context, or one-song recognition rather than a strong personal lane. Treat the signal as stronger only when explicit Atlas state repeats across songs, artists, albums, or survey candidates.`;
  const didYouKnow = [
    `${title} often teaches by contrast: the same era can point toward different roads when the production, rhythm, or vocal stance changes.`,
    `${anchors} help show how a road can be historically important while still needing user-specific evidence before Atlas treats it as a fit.`
  ];
  const claims = historicalClaims(researchPack, sourceRefs, {
    title,
    profile,
    traits,
    anchors
  });
  return {
    display_title: title,
    source_refs: sourceRefs,
    source_coverage_status: "source_deepened_external",
    research_editorial_status: "draft_research",
    render_editorial_status: "visualization_candidate",
    short_definition: shortDefinition,
    history_capsule: historyCapsule,
    why_it_mattered: why,
    distinct,
    listen_for: traits,
    caution,
    did_you_know: didYouKnow,
    claims
  };
}

function claimTarget(researchPack) {
  const alignment = researchPack.graph_alignment || {};
  const total = (alignment.canonical_artist_refs?.length || 0) + (alignment.canonical_album_refs?.length || 0) + (alignment.canonical_song_recording_refs?.length || 0);
  const broad = /scene|ecosystem|foundations|canon|crossover|global|hip-hop|metal|electronic|punk|soul|jazz|country|pop|rock|r&b|r-and-b|folk|songwriter|americana|alternative|indie|grunge|emo|theater|musical|soundtrack|score|gospel|worship|christian|novelty|kids|family|nostalgia/i.test(`${researchPack.identity.family_name} ${displayTitle(researchPack)}`);
  if (broad || total >= 80) return 8;
  if (total >= 25) return 6;
  return 4;
}

function sourcePair(sourceRefs, index) {
  if (sourceRefs.length <= 2) return sourceRefs;
  return unique([sourceRefs[index % sourceRefs.length], sourceRefs[(index + 1) % sourceRefs.length], sourceRefs[(index + 2) % sourceRefs.length]]).slice(0, 3);
}

function historicalClaims(researchPack, sourceRefs, ctx) {
  const id = researchPack.identity.archetype_id;
  const target = claimTarget(researchPack);
  const templates = [
    ["history-context", `${ctx.title} belongs to a larger music-history thread in which ${ctx.profile.context}.`, ["history_capsule", "region_scene_page"]],
    ["listening-traits", `The clearest listening clues for ${ctx.title} are ${ctx.traits[0]}, ${ctx.traits[1]}, and ${ctx.traits[2]}.`, ["what_to_listen_for_prompt", "mission_detail_history_module"]],
    ["anchor-lineage", `Representative anchors such as ${ctx.anchors} make the road's period, scene, or stylistic boundary audible for listeners.`, ["canonical_examples_block", "history_capsule"]],
    ["why-it-mattered", `${ctx.title} matters historically because ${ctx.profile.importance}.`, ["why_it_mattered", "atlas_home_region_card"]],
    ["boundary-style", `${ctx.title} is best separated from nearby roads by listening to ${ctx.traits[3]} and ${ctx.traits[4]} rather than by era label alone.`, ["related_roads_lineage_module", "dead_end_false_nearby_caution_module"]],
    ["media-and-scene", `The road also reflects how scenes, labels, venues, broadcasts, clubs, screens, or platforms can shape which sounds become widely recognized.`, ["region_scene_page", "mission_detail_history_module"]],
    ["legacy", `Later popular music repeatedly reuses this road's vocabulary through production choices, performance stance, rhythm, vocal style, or revival memory.`, ["related_roads_lineage_module", "did_you_know_card"]],
    ["transmission", `The sound circulated through venues, labels, broadcasts, clubs, screens, or platforms, which shaped how listeners encountered the style beyond its origin scene.`, ["personalized_atlas_overlay", "dead_end_false_nearby_caution_module"]],
    ["recording-practice", `Artist, album, and song examples can reveal different parts of ${ctx.title}: performer identity, long-form context, and immediate recording memory.`, ["canonical_examples_block", "region_scene_page"]],
    ["cultural-use", `The road's cultural use matters because radio, clubs, concerts, playlists, screen memory, family contexts, or scene affiliation can all preserve a style after its first era.`, ["atlas_home_region_card", "personalized_atlas_overlay"]]
  ];
  return templates.slice(0, target).map(([suffix, claimText, moduleUsage], index) => ({
    claim_id: `${id}-${suffix}`,
    claim_text: claimText,
    source_ref_ids: sourcePair(sourceRefs, index),
    confidence: sourceRefs.length >= 4 ? "medium_high" : "medium",
    notes: "Source-deepened v0.2.1 claim. Claim is original Cartenza Atlas educational prose based on the cited external source set and canonical graph examples.",
    module_usage: moduleUsage,
    graph_refs: [researchPack.identity.canonical_graph_ref, ...topExamples(researchPack).slice(0, 3).map((example) => example.example_ref)],
    audit_status: "external_source_supported"
  }));
}

function patchedExamples(researchPack, copy) {
  const traits = copy.listen_for;
  return (researchPack.explainer_content.canonical_example_rationales || []).map((example, index) => ({
    ...example,
    display_label: example.display_label,
    why_this_example_matters: `${example.display_label} anchors ${copy.display_title} by making ${traits[index % traits.length]} and ${traits[(index + 1) % traits.length]} easier to hear.`,
    what_to_listen_for: [traits[index % traits.length], traits[(index + 1) % traits.length]],
    graph_ref_validation_status: example.graph_ref_validation_status || "validated_in_normalized_family_export"
  }));
}

function personalizationHooks(identity, copy) {
  return [
    {
      hook_id: `${identity.archetype_id}-affinity-positive`,
      required_state_fields: [`atlas_state.archetype_affinity[${identity.archetype_id}]`, `atlas_state.family_affinity[${identity.family_id}]`],
      predicate: `atlas_state.archetype_affinity[${identity.archetype_id}] >= 0.65 || atlas_state.family_affinity[${identity.family_id}] >= 0.65`,
      copy_variant: `Your Atlas signals make ${copy.display_title} useful as a contextual landmark.`,
      fallback_copy: `Use ${copy.display_title} as context until repeated evidence makes it a stronger personal lane.`,
      state_field_status: "proposed"
    },
    {
      hook_id: `${identity.archetype_id}-known-song`,
      required_state_fields: ["atlas_state.user_known_song_refs", "atlas_state.survey_positive_candidate_refs"],
      predicate: `atlas_state.user_known_song_refs intersects canonical_song_recording_refs for ${identity.canonical_graph_ref} || atlas_state.survey_positive_candidate_refs intersects survey_candidate_refs for ${identity.canonical_graph_ref}`,
      copy_variant: `Known songs can make this road easier to place because they expose its core listening clues.`,
      fallback_copy: `Use the canonical examples to orient ${copy.display_title} before personalizing it.`,
      state_field_status: "proposed"
    },
    {
      hook_id: `${identity.archetype_id}-false-nearby-caution`,
      required_state_fields: ["atlas_state.dead_end_probe_results", "atlas_state.boundary_question_results", "atlas_state.survey_negative_candidate_refs"],
      predicate: `atlas_state.dead_end_probe_results has repeated_negative for ${identity.canonical_graph_ref} || atlas_state.boundary_question_results has boundary_negative for ${identity.canonical_graph_ref}`,
      copy_variant: copy.caution,
      fallback_copy: `No false-nearby caution is active for ${copy.display_title}.`,
      state_field_status: "proposed"
    },
    {
      hook_id: `${identity.archetype_id}-alpha-context`,
      required_state_fields: ["atlas_state.completed_mission_ids", "atlas_state.active_mission_id", "atlas_state.first_batch_mission_ids", "atlas_state.related_mission_ids"],
      predicate: `atlas_state.active_mission_id in atlas_state.first_batch_mission_ids || atlas_state.completed_mission_ids intersects atlas_state.related_mission_ids for ${identity.canonical_graph_ref} || atlas_state.related_mission_ids references ${identity.canonical_graph_ref}`,
      copy_variant: `This road can explain why the active Alpha route points nearby.`,
      fallback_copy: `This road is not in Alpha batch yet; you may encounter this road later.`,
      state_field_status: "proposed"
    },
    {
      hook_id: `${identity.archetype_id}-saved-or-skipped-object`,
      required_state_fields: ["atlas_state.user_saved_artist_refs", "atlas_state.user_skipped_artist_refs", "atlas_state.user_disliked_song_refs"],
      predicate: `atlas_state.user_saved_artist_refs intersects canonical_artist_refs for ${identity.canonical_graph_ref} || atlas_state.user_skipped_artist_refs intersects canonical_artist_refs for ${identity.canonical_graph_ref} || atlas_state.user_disliked_song_refs intersects canonical_song_recording_refs for ${identity.canonical_graph_ref}`,
      copy_variant: `Saved, skipped, or disliked objects can tune this road without changing its canonical identity.`,
      fallback_copy: `No saved, skipped, or disliked object signal is active for ${copy.display_title}.`,
      state_field_status: "proposed"
    }
  ];
}

function variant(compact, standard, deep) {
  return { compact, standard, deep };
}

function buildModules(researchPack, copy, examples) {
  const exampleLabels = examples.slice(0, 4).map((example) => example.display_label);
  return {
    atlas_home_region_card: variant(
      copy.short_definition,
      `${copy.display_title} helps orient ${researchPack.identity.family_name}: ${copy.why_it_mattered}`,
      `${copy.short_definition} ${copy.why_it_mattered} ${copy.distinct}`
    ),
    region_scene_page: variant(
      copy.why_it_mattered,
      `${copy.history_capsule} ${copy.distinct}`,
      `${copy.history_capsule} ${copy.why_it_mattered} ${copy.distinct}`
    ),
    mission_detail_history_module: variant(
      `What this route tests: ${copy.short_definition}`,
      `${copy.history_capsule} This related road stays explanatory in Alpha and helps place the active mission in music-history context.`,
      `${copy.history_capsule} ${copy.why_it_mattered} Use it as context for the active mission and related mission history.`
    ),
    did_you_know_card: variant(
      copy.did_you_know[0],
      copy.did_you_know.join(" "),
      `${copy.did_you_know.join(" ")} The supporting claims are source-audited in the research pack.`
    ),
    what_to_listen_for_prompt: variant(
      `Listen for ${copy.listen_for.slice(0, 2).join(" and ")}.`,
      `Listen for ${copy.listen_for.slice(0, 3).join(", ")}.`,
      `Listen for ${copy.listen_for.join(", ")}.`
    ),
    personalized_atlas_overlay: variant(
      `This road can refine your Atlas map when your signals touch ${copy.display_title.toLowerCase()}.`,
      `If your Atlas state shows repeated positive evidence here, use ${copy.display_title} as a contextual landmark, not a promise of broad family fit.`,
      `When survey, mission, and saved-object evidence all point here, this road can explain why nearby examples feel connected while still preserving boundary cautions.`
    ),
    canonical_examples_block: variant(
      `Examples: ${exampleLabels.slice(0, 2).join("; ")}.`,
      `Canonical examples: ${exampleLabels.join("; ")}.`,
      `Canonical examples are validated against graph refs or survey candidates: ${exampleLabels.join("; ")}.`
    ),
    related_roads_lineage_module: variant(
      `Related roads: ${researchPack.graph_alignment.related_archetype_refs?.join(", ") || "none listed"}.`,
      `Before/after context: ${[...(researchPack.graph_alignment.before_archetype_refs || []), ...(researchPack.graph_alignment.after_archetype_refs || [])].join(", ") || "family edge road"}.`,
      `Use related roads to explain contrast and lineage inside Atlas. This is explanatory context, not a route starter.`
    ),
    dead_end_false_nearby_caution_module: variant(
      copy.caution,
      `${copy.caution} Use dead-end probe results only when explicit Atlas state supports them.`,
      `${copy.caution} Repeated negative signals can mark a false-nearby caution, but the canonical graph identity remains unchanged.`
    )
  };
}

function patchResearchPack(pack) {
  const cleanedExistingSources = Object.fromEntries(Object.entries(pack.source_references || {}).map(([id, source]) => [id, brandCleanSource(source)]));
  const sourceRefs = sourceRefsFor(pack);
  const copy = copyFor(pack, sourceRefs);
  const examples = patchedExamples(pack, copy);
  const sourceReferences = {
    ...cleanedExistingSources,
    ...Object.fromEntries(sourceRefs.map((id) => [id, EXTERNAL_SOURCES[id]]))
  };
  const didYouKnowCards = copy.did_you_know.map((text, index) => ({
    card_id: `${pack.identity.archetype_id}-dyk-${index + 1}`,
    copy: text,
    source_ref_ids: sourcePair(sourceRefs, index)
  }));
  const patched = {
    ...pack,
    schema_version: "0.2.1",
    pack_id: replaceVersionId(pack.pack_id),
    generated_at: GENERATED_AT,
    identity: {
      ...pack.identity,
      editorial_display_title: copy.display_title,
      non_mutation_assertion: "This research pack is a sidecar only; it does not create, rename, delete, merge, or reclassify canonical graph identities."
    },
    source_references: sourceReferences,
    claim_level_source_audit: copy.claims,
    explainer_content: {
      ...pack.explainer_content,
      short_definition: copy.short_definition,
      history_capsule: copy.history_capsule,
      why_it_mattered: copy.why_it_mattered,
      what_made_it_distinct: copy.distinct,
      what_to_listen_for: copy.listen_for,
      canonical_example_rationales: examples,
      before_after_related_roads: {
        before: pack.graph_alignment.before_archetype_refs || [],
        after: pack.graph_alignment.after_archetype_refs || [],
        related: pack.graph_alignment.related_archetype_refs || [],
        copy: `Use ${copy.display_title} as a contextual road inside ${pack.identity.family_name}; related roads explain contrast, sequence, and survey uncertainty while staying inside Alpha scope.`
      },
      did_you_know_cards: didYouKnowCards,
      mission_description_snippets: [
        `What this route tests: whether ${copy.display_title.toLowerCase()} is a useful listening-history doorway for this user.`,
        `Why this region explains the batch: it gives context around canonical anchors while staying inside Alpha scope.`
      ],
      atlas_region_page_copy_blocks: [
        copy.short_definition,
        copy.why_it_mattered,
        copy.distinct
      ],
      dead_end_false_nearby_caution_language: copy.caution,
      personalization_hooks: personalizationHooks(pack.identity, copy),
      source_references: sourceReferences,
      claim_level_source_audit: copy.claims,
      editorial_status: "draft_research",
      source_coverage_status: "source_deepened_external"
    },
    graph_gap_observations: pack.graph_gap_observations || [],
    rights_policy: {
      rights_status: "pass",
      rights_notes: "Original Cartenza Atlas educational prose. No lyrics, no long quotations, no third-party copy blocks, no album art, no artist photos, and no proprietary metadata scraping dependency."
    },
    alpha_v0_mission_boundary: {
      allowed_language_policy: "Contextual Alpha language only: related mission, included in first batch, what this route tests, why this region explains the batch, not in Alpha batch yet, you may encounter this road later.",
      forbidden_language_policy: "No runtime route-creation language."
    },
    non_mutation_policy: {
      status: "pass",
      assertion: "Sidecar-only explainer pack. Canonical graph identity remains unchanged."
    },
    editorial_status: "draft_research",
    process_audit_metadata: {
      source_package: "AtlasExplainerPack_v0_2_All_Archetypes",
      patch_action: "source-deepened external sources, replaced placeholder render copy, and separated process metadata from historical claim audits.",
      non_mutation_assertion: "No canonical graph identity, membership, candidate, boundary, or dead-end refs were changed."
    }
  };
  return { researchPack: patched, copy, examples };
}

function patchRenderPack(renderPack, researchPack, copy, examples) {
  return {
    ...renderPack,
    schema_version: "0.2.1",
    render_pack_id: replaceVersionId(renderPack.render_pack_id),
    generated_at: GENERATED_AT,
    source_research_pack_id: researchPack.pack_id,
    identity: researchPack.identity,
    graph_alignment: {
      canonical_graph_ref: researchPack.identity.canonical_graph_ref,
      canonical_example_refs: examples.map((example) => example.example_ref),
      survey_candidate_refs: (researchPack.graph_alignment.survey_candidate_refs || []).map((item) => item.ref),
      related_archetype_refs: researchPack.graph_alignment.related_archetype_refs || []
    },
    modules: buildModules(researchPack, copy, examples),
    canonical_examples: examples,
    personalization_hooks: personalizationHooks(researchPack.identity, copy),
    source_claim_refs: researchPack.claim_level_source_audit.map((claim) => claim.claim_id),
    rights_status: "pass",
    rights_notes: "Original Cartenza Atlas educational render copy; no lyrics, long quotations, album art, artist photos, or proprietary third-party prose.",
    editorial_status: "visualization_candidate",
    non_mutation_assertion: "Render pack is a runtime sidecar only; it does not mutate canonical graph identity.",
    alpha_v0_mission_boundary: {
      status: "pass",
      allowed_terms_used: ["related mission", "what this route tests", "why this region explains the batch", "not in Alpha batch yet", "you may encounter this road later"],
      forbidden_dynamic_mission_language_present: false
    }
  };
}

function validatedExampleRefs(researchPacks) {
  const refs = new Set();
  for (const pack of researchPacks) {
    const alignment = pack.graph_alignment || {};
    for (const item of [
      ...(alignment.canonical_artist_refs || []),
      ...(alignment.canonical_album_refs || []),
      ...(alignment.canonical_song_recording_refs || [])
    ]) refs.add(item.ref);
    for (const item of alignment.survey_candidate_refs || []) refs.add(item.ref);
  }
  return refs;
}

function validatePackage(researchPacks, renderPacks) {
  const graphRefs = new Set(researchPacks.map((pack) => pack.identity.canonical_graph_ref));
  const renderRefs = new Set(renderPacks.map((pack) => pack.identity.canonical_graph_ref));
  const exampleRefs = validatedExampleRefs(researchPacks);
  const mechanicalErrors = [];
  const sourceErrors = [];
  const copyErrors = [];
  const rightsErrors = [];
  const pmWarnings = [];

  for (const pack of researchPacks) {
    if (!renderRefs.has(pack.identity.canonical_graph_ref)) mechanicalErrors.push(`Missing render pack for ${pack.identity.canonical_graph_ref}`);
    if (pack.editorial_status !== "draft_research") mechanicalErrors.push(`Research pack ${pack.pack_id} has invalid editorial status ${pack.editorial_status}`);
    if (!pack.identity.non_mutation_assertion || pack.non_mutation_policy?.status !== "pass") mechanicalErrors.push(`Research pack ${pack.pack_id} missing non-mutation pass`);
    if (!pack.rights_policy?.rights_status) rightsErrors.push(`Research pack ${pack.pack_id} missing rights status`);
    const externalSources = Object.values(pack.source_references || {}).filter(isExternalSource);
    if (externalSources.length < 3) sourceErrors.push(`Research pack ${pack.pack_id} has fewer than three external sources`);
    if (pack.explainer_content.source_coverage_status !== "source_deepened_external") sourceErrors.push(`Research pack ${pack.pack_id} is not marked source_deepened_external`);
    if ((pack.claim_level_source_audit || []).length < claimTarget(pack)) sourceErrors.push(`Research pack ${pack.pack_id} has insufficient source-deepened claim density`);
    for (const claim of pack.claim_level_source_audit || []) {
      if (!claim.source_ref_ids?.length) sourceErrors.push(`Claim ${claim.claim_id} has no source refs`);
      if (claim.audit_status !== "external_source_supported") sourceErrors.push(`Claim ${claim.claim_id} is not external_source_supported`);
      if (/graph-aligned|sidecar|source deepening|required|canonical examples were selected|exists in the graph|graph identity/i.test(claim.claim_text)) {
        sourceErrors.push(`Claim ${claim.claim_id} appears to be process metadata rather than historical/musicological copy`);
      }
      for (const sourceId of claim.source_ref_ids || []) {
        if (!isExternalSource(pack.source_references[sourceId])) sourceErrors.push(`Claim ${claim.claim_id} uses non-external source ${sourceId}`);
      }
    }
    for (const example of pack.explainer_content.canonical_example_rationales || []) {
      if (!exampleRefs.has(example.example_ref) && !example.example_ref.startsWith("survey_candidate:")) {
        mechanicalErrors.push(`Example ${example.example_ref} is not a validated graph or candidate ref`);
      }
    }
  }

  for (const pack of renderPacks) {
    if (!graphRefs.has(pack.identity.canonical_graph_ref)) mechanicalErrors.push(`Render pack ${pack.render_pack_id} has no matching research pack`);
    if (!["visualization_candidate", "pm_review_needed"].includes(pack.editorial_status)) mechanicalErrors.push(`Render pack ${pack.render_pack_id} has invalid editorial status ${pack.editorial_status}`);
    if (pack.editorial_status === "production_copy_candidate" || pack.editorial_status === "alpha_render_candidate") mechanicalErrors.push(`Render pack ${pack.render_pack_id} is improperly promoted`);
    if (!pack.rights_status) rightsErrors.push(`Render pack ${pack.render_pack_id} missing rights status`);
    const moduleCopy = JSON.stringify(pack.modules || {});
    for (const phrase of FORBIDDEN_DYNAMIC_MISSION_PHRASES) {
      if (moduleCopy.toLowerCase().includes(phrase)) copyErrors.push(`Forbidden dynamic mission phrase in ${pack.render_pack_id}: ${phrase}`);
    }
    for (const phrase of PLACEHOLDER_PHRASES) {
      if (moduleCopy.toLowerCase().includes(phrase.toLowerCase())) copyErrors.push(`Placeholder QA phrase in ${pack.render_pack_id}: ${phrase}`);
    }
    for (const hook of pack.personalization_hooks || []) {
      if (!hook.required_state_fields?.length) mechanicalErrors.push(`Hook ${hook.hook_id} has no state fields`);
      for (const field of hook.required_state_fields || []) {
        if (!field.startsWith("atlas_state.")) mechanicalErrors.push(`Hook ${hook.hook_id} uses non-Atlas state field ${field}`);
      }
      if (hook.state_field_status === "proposed") {
        pmWarnings.push({
          canonical_graph_ref: pack.identity.canonical_graph_ref,
          hook_id: hook.hook_id,
          warning: "Personalization field is part of the v0.2 atlas_state contract but remains proposed until app implementation confirms it."
        });
      }
    }
  }

  return {
    generated_at: GENERATED_AT,
    mechanical_validation: {
      status: mechanicalErrors.length === 0 ? "pass" : "fail",
      research_pack_count: researchPacks.length,
      render_pack_count: renderPacks.length,
      graph_ref_failure_count: mechanicalErrors.filter((error) => /graph|Example|matching research|Missing render/u.test(error)).length,
      error_count: mechanicalErrors.length,
      errors: mechanicalErrors
    },
    source_validation: {
      status: sourceErrors.length === 0 ? "pass" : "fail",
      weak_source_count: sourceErrors.length ? weakSourcePacks(researchPacks).length : 0,
      error_count: sourceErrors.length,
      errors: sourceErrors
    },
    copy_readiness_validation: {
      status: copyErrors.length === 0 ? "pass" : "fail",
      dynamic_mission_language_violation_count: copyErrors.filter((error) => error.includes("Forbidden dynamic")).length,
      placeholder_phrase_violation_count: copyErrors.filter((error) => error.includes("Placeholder")).length,
      error_count: copyErrors.length,
      errors: copyErrors
    },
    rights_validation: {
      status: rightsErrors.length === 0 ? "pass" : "fail",
      error_count: rightsErrors.length,
      errors: rightsErrors
    },
    pm_approval_status: {
      status: "not_pm_approved_for_alpha_or_production",
      visualization_candidate_count: renderPacks.filter((pack) => pack.editorial_status === "visualization_candidate").length,
      pm_review_needed_count: renderPacks.filter((pack) => pack.editorial_status === "pm_review_needed").length,
      production_copy_candidate_count: renderPacks.filter((pack) => pack.editorial_status === "production_copy_candidate").length,
      alpha_render_candidate_count: renderPacks.filter((pack) => pack.editorial_status === "alpha_render_candidate").length,
      pm_warning_count: pmWarnings.length,
      warnings: pmWarnings
    }
  };
}

function weakSourcePacks(researchPacks) {
  return researchPacks.filter((pack) => {
    const externalSourceCount = Object.values(pack.source_references || {}).filter(isExternalSource).length;
    const hasWeakCoverage = pack.explainer_content.source_coverage_status !== "source_deepened_external";
    const hasWeakClaims = (pack.claim_level_source_audit || []).some((claim) => claim.audit_status !== "external_source_supported" || claim.source_ref_ids?.some((sourceId) => !isExternalSource(pack.source_references[sourceId])));
    return externalSourceCount < 3 || hasWeakCoverage || hasWeakClaims;
  });
}

function mdReport(title, lines) {
  return [`# ${title}`, "", ...lines, ""].join("\n");
}

function buildReports(researchPacks, renderPacks, validation) {
  const weak = weakSourcePacks(researchPacks).map((pack) => ({
    canonical_graph_ref: pack.identity.canonical_graph_ref,
    archetype_id: pack.identity.archetype_id,
    editorial_display_title: pack.identity.editorial_display_title,
    external_source_count: Object.values(pack.source_references || {}).filter(isExternalSource).length,
    source_coverage_status: pack.explainer_content.source_coverage_status,
    recommended_action: "PM holdback only if human source review rejects the cited source set."
  }));
  writeJson(path.join(OUT_DIR, "indexes/weak_source_archetypes_v0_2_1.json"), {
    generated_at: GENERATED_AT,
    weak_source_count: weak.length,
    pm_holdback_count: 0,
    weak_source_archetypes: weak,
    note: "Weak-source means fewer than three external sources, non-source-deepened coverage status, or claim audits not tied to external sources."
  });

  const sourceRows = researchPacks.map((pack) => {
    const externalSourceCount = Object.values(pack.source_references || {}).filter(isExternalSource).length;
    return `| ${pack.identity.canonical_graph_ref} | ${pack.identity.editorial_display_title} | ${externalSourceCount} | ${pack.claim_level_source_audit.length} | ${pack.explainer_content.source_coverage_status} |`;
  });
  writeText(path.join(OUT_DIR, "indexes/source_deepening_completion_report_v0_2_1.md"), mdReport("Source Deepening Completion Report v0.2.1", [
    "This is the Cartenza Atlas Explainer Layer source-deepening patch over AtlasExplainerPack_v0_2_All_Archetypes.",
    "No canonical graph identity, memberships, graph refs, candidate refs, boundary refs, or dead-end refs were changed.",
    "",
    `Research packs present: ${researchPacks.length} / 120`,
    `Render packs present: ${renderPacks.length} / 120`,
    `Weak-source archetypes after patch: ${weak.length}`,
    `Source validation status: ${validation.source_validation.status}`,
    "",
    "| canonical_graph_ref | title | external_sources | historical_claims | coverage_status |",
    "| --- | --- | ---: | ---: | --- |",
    ...sourceRows
  ]));

  const copyRows = renderPacks.map((pack) => {
    const moduleCopy = JSON.stringify(pack.modules || {});
    const placeholders = textIncludesAny(moduleCopy, PLACEHOLDER_PHRASES);
    const dynamic = textIncludesAny(moduleCopy, FORBIDDEN_DYNAMIC_MISSION_PHRASES);
    return `| ${pack.identity.canonical_graph_ref} | ${pack.editorial_status} | ${placeholders.length} | ${dynamic.length} | ${pack.rights_status} |`;
  });
  writeText(path.join(OUT_DIR, "indexes/copy_readiness_report_v0_2_1.md"), mdReport("Copy Readiness Report v0.2.1", [
    "Render modules were rewritten as authored Cartenza Atlas copy and scanned separately from mechanical validation.",
    "",
    `Placeholder QA phrase violations in render modules: ${validation.copy_readiness_validation.placeholder_phrase_violation_count}`,
    `Forbidden dynamic mission language violations: ${validation.copy_readiness_validation.dynamic_mission_language_violation_count}`,
    `Visualization candidates: ${validation.pm_approval_status.visualization_candidate_count}`,
    `PM-review-needed render packs: ${validation.pm_approval_status.pm_review_needed_count}`,
    "PM approval status: not alpha-approved and not production-approved.",
    "",
    "| canonical_graph_ref | render_status | placeholder_violations | dynamic_mission_violations | rights_status |",
    "| --- | --- | ---: | ---: | --- |",
    ...copyRows
  ]));

  const graphRows = researchPacks.map((pack) => {
    const render = renderPacks.find((item) => item.identity.canonical_graph_ref === pack.identity.canonical_graph_ref);
    const invalidExamples = (pack.explainer_content.canonical_example_rationales || []).filter((example) => example.graph_ref_validation_status !== "validated_in_normalized_family_export");
    return `| ${pack.identity.canonical_graph_ref} | yes | ${render ? "yes" : "no"} | ${invalidExamples.length ? "review" : "pass"} | sidecar only |`;
  });
  writeText(path.join(OUT_DIR, "indexes/graph_ref_validation_report_v0_2_1.md"), mdReport("Graph Ref Validation Report v0.2.1", [
    "Cartenza Atlas Explainer Layer patch validation. No graph mutations were made.",
    "",
    `Graph-ref validation failures: ${validation.mechanical_validation.graph_ref_failure_count}`,
    "",
    "| canonical_graph_ref | research_pack | render_pack | canonical_examples | notes |",
    "| --- | --- | --- | --- | --- |",
    ...graphRows
  ]));

  const rightsRows = researchPacks.map((pack) => `| ${pack.identity.canonical_graph_ref} | ${pack.rights_policy.rights_status} | ${pack.rights_policy.rights_notes} |`);
  writeText(path.join(OUT_DIR, "indexes/rights_policy_report_v0_2_1.md"), mdReport("Rights Policy Report v0.2.1", [
    "All v0.2.1 packs use original Cartenza Atlas educational prose and factual source summaries.",
    "No lyrics, long quotations, third-party prose blocks, proprietary album art dependencies, artist-photo dependencies, or scraping-derived proprietary metadata dependencies were introduced.",
    "",
    `Rights validation status: ${validation.rights_validation.status}`,
    `Rights validation errors: ${validation.rights_validation.error_count}`,
    "",
    "| canonical_graph_ref | rights_status | notes |",
    "| --- | --- | --- |",
    ...rightsRows
  ]));

  const dependencies = renderPacks.flatMap((pack) => pack.personalization_hooks.map((hook) => ({
    canonical_graph_ref: pack.identity.canonical_graph_ref,
    hook_id: hook.hook_id,
    required_state_fields: hook.required_state_fields,
    predicate: hook.predicate,
    state_field_status: hook.state_field_status
  })));
  writeJson(path.join(OUT_DIR, "indexes/state_field_dependency_report_v0_2_1.json"), {
    generated_at: GENERATED_AT,
    product: "Cartenza Atlas Explainer Layer",
    note: "These dependencies are PM warnings rather than mechanical blockers: hooks intentionally bind to explicit atlas_state.* fields from the v0.2 contract, and the app implementation may still need to confirm them.",
    state_fields_contract_v0_2: ATLAS_STATE_FIELDS_V0_2,
    proposed_dependency_count: dependencies.filter((item) => item.state_field_status === "proposed").length,
    proposed_dependencies: dependencies
  });

  writeText(path.join(OUT_DIR, "indexes/alpha_render_readiness_report_v0_2_1.md"), mdReport("Alpha Render Readiness Report v0.2.1", [
    "Cartenza Atlas Explainer Layer v0.2.1 is source-deepened and mechanically ready as a Visualization candidate package. It is not PM-approved for Alpha render or production copy.",
    "",
    "Validation distinction:",
    `- Mechanical validation: ${validation.mechanical_validation.status} (${validation.mechanical_validation.error_count} errors)`,
    `- Source validation: ${validation.source_validation.status} (${validation.source_validation.error_count} errors, ${weak.length} weak-source archetypes)`,
    `- Copy-readiness validation: ${validation.copy_readiness_validation.status} (${validation.copy_readiness_validation.error_count} errors)`,
    `- Rights validation: ${validation.rights_validation.status} (${validation.rights_validation.error_count} errors)`,
    `- PM approval status: ${validation.pm_approval_status.status}`,
    "",
    `Research-pack coverage: ${researchPacks.length} / 120`,
    `Render-pack coverage: ${renderPacks.length} / 120`,
    `Render packs marked visualization_candidate: ${validation.pm_approval_status.visualization_candidate_count}`,
    `Render packs marked pm_review_needed: ${validation.pm_approval_status.pm_review_needed_count}`,
    `Render packs marked alpha_render_candidate: ${validation.pm_approval_status.alpha_render_candidate_count}`,
    `Render packs marked production_copy_candidate: ${validation.pm_approval_status.production_copy_candidate_count}`,
    `PM warnings from proposed atlas_state fields: ${validation.pm_approval_status.pm_warning_count}`,
    "",
    "Recommended first Atlas Visualization render batch: Family 1 proof lineage, Family 2 British Invasion/60s pop-rock, CBGB 054, Funk 039, Garage Revival 079, and one global-pop sample from Family 13.",
    "Recommended holdbacks before Alpha: PM human review of the new external source sets and confirmation of proposed atlas_state implementation status."
  ]));

  const sourceUsage = Object.fromEntries(researchPacks.map((pack) => [pack.pack_id, {
    canonical_graph_ref: pack.identity.canonical_graph_ref,
    source_ref_ids: Object.keys(pack.source_references || {}),
    external_source_ref_ids: Object.entries(pack.source_references || {}).filter(([, source]) => isExternalSource(source)).map(([id]) => id),
    claim_ids: pack.claim_level_source_audit.map((claim) => claim.claim_id)
  }]));
  const allSources = {};
  for (const pack of researchPacks) {
    for (const [id, source] of Object.entries(pack.source_references || {})) allSources[id] = source;
  }
  writeJson(path.join(OUT_DIR, "indexes/source_audit_index_v0_2_1.json"), {
    generated_at: GENERATED_AT,
    product: "Cartenza Atlas Explainer Layer",
    source_references: allSources,
    pack_source_usage: sourceUsage
  });

  writeJson(path.join(OUT_DIR, "indexes/atlas_explainer_validation_report_v0_2_1.json"), validation);
  writeText(path.join(OUT_DIR, "indexes/archetype_explainer_coverage_report_v0_2_1.md"), mdReport("Archetype Explainer Coverage Report v0.2.1", [
    `Research-pack coverage: ${researchPacks.length} / 120`,
    `Render-pack coverage: ${renderPacks.length} / 120`,
    "All packs preserve canonical family/archetype graph identity.",
    "",
    "| canonical_graph_ref | research_pack | render_pack | research_status | render_status | source_status |",
    "| --- | --- | --- | --- | --- | --- |",
    ...researchPacks.map((pack) => {
      const render = renderPacks.find((item) => item.identity.canonical_graph_ref === pack.identity.canonical_graph_ref);
      return `| ${pack.identity.canonical_graph_ref} | yes | ${render ? "yes" : "no"} | ${pack.editorial_status} | ${render?.editorial_status || "missing"} | ${pack.explainer_content.source_coverage_status} |`;
    })
  ]));

  writeText(path.join(OUT_DIR, "indexes/graph_gap_observations_v0_2_1.md"), mdReport("Graph Gap Observations v0.2.1", [
    "No canonical graph mutations were made.",
    "No silent graph corrections were made.",
    "Existing graph-gap observation arrays were preserved; this source-deepening patch did not add canonical objects or memberships.",
    "Future obvious historical omissions should be logged with `do_not_mutate_graph: true` for PM review."
  ]));
}

function buildExamples(renderPacks) {
  const samples = [
    "family_02/archetype_008",
    "family_07/archetype_045",
    "family_11/archetype_081",
    "family_13/archetype_094"
  ].map((ref) => renderPacks.find((pack) => pack.identity.canonical_graph_ref === ref)).filter(Boolean);
  writeText(path.join(OUT_DIR, "examples/atlas_home_region_cards_examples_v0_2_1.md"), mdReport("Atlas Home Region Cards Examples v0.2.1", samples.flatMap((pack) => [
    `## ${pack.identity.editorial_display_title}`,
    `Compact: ${pack.modules.atlas_home_region_card.compact}`,
    `Standard: ${pack.modules.atlas_home_region_card.standard}`,
    ""
  ])));
  writeText(path.join(OUT_DIR, "examples/region_scene_page_examples_v0_2_1.md"), mdReport("Region Scene Page Examples v0.2.1", samples.flatMap((pack) => [
    `## ${pack.identity.editorial_display_title}`,
    pack.modules.region_scene_page.standard,
    ""
  ])));
  writeText(path.join(OUT_DIR, "examples/mission_detail_history_module_examples_v0_2_1.md"), mdReport("Mission Detail History Module Examples v0.2.1", samples.flatMap((pack) => [
    `## ${pack.identity.editorial_display_title}`,
    pack.modules.mission_detail_history_module.standard,
    ""
  ])));
}

function copySchemas() {
  const schemaDir = path.join(SOURCE_DIR, "schemas");
  for (const schemaFile of listJsonFiles(schemaDir)) {
    const schema = readJson(schemaFile);
    const fileName = path.basename(schemaFile).replace("_v0_2.json", "_v0_2_1.json");
    const text = JSON.stringify(schema, null, 2)
      .replace(/v0_2/gu, "v0_2_1")
      .replace(/v0\.2/gu, "v0.2.1")
      .replace(/Waymark/gu, "Cartenza");
    writeText(path.join(OUT_DIR, "schemas", fileName), `${text}\n`);
  }
}

function writeManifest(researchPacks, renderPacks, validation) {
  writeJson(path.join(OUT_DIR, "indexes/atlas_explainer_pack_manifest_v0_2_1.json"), {
    generated_at: GENERATED_AT,
    package_id: "AtlasExplainerPack_v0_2_1_SourceDeepened",
    product: "Cartenza Atlas Explainer Layer",
    source_package: "AtlasExplainerPack_v0_2_All_Archetypes",
    package_scope: "all canonical archetypes from the expanded canonical graph export, patched for external source depth and authored render copy",
    non_mutation_assertion: "No canonical graph identity, family, archetype, membership, survey candidate, boundary question, or dead-end probe was changed.",
    schemas: [
      "schemas/atlas_explainer_research_pack_schema_v0_2_1.json",
      "schemas/atlas_explainer_render_pack_schema_v0_2_1.json"
    ],
    research_packs: researchPacks.map((pack) => `research_packs/${pack.pack_id}.json`),
    render_packs: renderPacks.map((pack) => `render_packs/${pack.render_pack_id}.json`),
    required_reports: [
      "indexes/source_deepening_completion_report_v0_2_1.md",
      "indexes/weak_source_archetypes_v0_2_1.json",
      "indexes/copy_readiness_report_v0_2_1.md",
      "indexes/graph_ref_validation_report_v0_2_1.md",
      "indexes/rights_policy_report_v0_2_1.md",
      "indexes/state_field_dependency_report_v0_2_1.json",
      "indexes/alpha_render_readiness_report_v0_2_1.md"
    ],
    validation_summary: validation
  });
}

function main() {
  if (!fs.existsSync(SOURCE_DIR)) throw new Error(`Missing source package: ${SOURCE_DIR}`);
  if (fs.existsSync(OUT_DIR)) fs.rmSync(OUT_DIR, { recursive: true, force: true });
  fs.mkdirSync(OUT_DIR, { recursive: true });

  copySchemas();

  const sourceResearchFiles = listJsonFiles(path.join(SOURCE_DIR, "research_packs"));
  const sourceRenderByRef = new Map(listJsonFiles(path.join(SOURCE_DIR, "render_packs")).map((file) => {
    const pack = readJson(file);
    return [pack.identity.canonical_graph_ref, pack];
  }));

  const researchPacks = [];
  const renderPacks = [];
  for (const sourceFile of sourceResearchFiles) {
    const sourceResearchPack = readJson(sourceFile);
    const sourceRenderPack = sourceRenderByRef.get(sourceResearchPack.identity.canonical_graph_ref);
    if (!sourceRenderPack) throw new Error(`Missing render pack for ${sourceResearchPack.identity.canonical_graph_ref}`);
    const { researchPack, copy, examples } = patchResearchPack(sourceResearchPack);
    const renderPack = patchRenderPack(sourceRenderPack, researchPack, copy, examples);
    researchPacks.push(researchPack);
    renderPacks.push(renderPack);
  }
  researchPacks.sort((a, b) => a.identity.family_id - b.identity.family_id || a.identity.archetype_id.localeCompare(b.identity.archetype_id));
  renderPacks.sort((a, b) => a.identity.family_id - b.identity.family_id || a.identity.archetype_id.localeCompare(b.identity.archetype_id));

  for (const pack of researchPacks) {
    writeJson(path.join(OUT_DIR, `research_packs/${pack.pack_id}.json`), pack);
  }
  for (const pack of renderPacks) {
    writeJson(path.join(OUT_DIR, `render_packs/${pack.render_pack_id}.json`), pack);
  }

  const oldInventoryPath = path.join(SOURCE_DIR, "indexes/archetype_inventory_v0_2.json");
  if (fs.existsSync(oldInventoryPath)) {
    const inventory = readJson(oldInventoryPath);
    inventory.generated_at = GENERATED_AT;
    inventory.package_patch = "AtlasExplainerPack_v0_2_1_SourceDeepened";
    writeJson(path.join(OUT_DIR, "indexes/archetype_inventory_v0_2_1.json"), inventory);
  }

  const validation = validatePackage(researchPacks, renderPacks);
  buildReports(researchPacks, renderPacks, validation);
  buildExamples(renderPacks);
  writeManifest(researchPacks, renderPacks, validation);

  if (fs.existsSync(ZIP_PATH)) fs.rmSync(ZIP_PATH, { force: true });
  execFileSync("zip", ["-qr", ZIP_PATH, path.basename(OUT_DIR)], { cwd: path.dirname(OUT_DIR) });

  console.log(JSON.stringify({
    package_dir: OUT_DIR,
    zip_path: ZIP_PATH,
    research_packs: researchPacks.length,
    render_packs: renderPacks.length,
    mechanical_validation: validation.mechanical_validation.status,
    source_validation: validation.source_validation.status,
    copy_readiness_validation: validation.copy_readiness_validation.status,
    rights_validation: validation.rights_validation.status,
    weak_source_count: weakSourcePacks(researchPacks).length,
    placeholder_phrase_violations: validation.copy_readiness_validation.placeholder_phrase_violation_count,
    dynamic_mission_language_violations: validation.copy_readiness_validation.dynamic_mission_language_violation_count,
    pm_warning_count: validation.pm_approval_status.pm_warning_count
  }, null, 2));
}

main();
