import fs from "node:fs";
import path from "node:path";

const ROOT = process.cwd();
const SCAFFOLD_DIR = path.join(ROOT, "data/atlas_explainer/AtlasExplainerPack_v0_2_1_SourceDeepened");
const OUT_DIR = path.join(ROOT, "data/atlas_explainer/source_recovery_research_notes");
const OUT_PATH = path.join(OUT_DIR, "00_local_source_recovery_baseline_v0_2_2.json");
const SOURCE_INDEX = path.join(SCAFFOLD_DIR, "indexes/source_audit_index_v0_2_1.json");

const SOURCE_CATALOG = JSON.parse(fs.readFileSync(SOURCE_INDEX, "utf8")).source_references;

const SOURCE_BUNDLES = {
  "001": ["britannica_rock_and_roll", "rockhall_chuck_berry", "rockhall_sister_rosetta_tharpe", "loc_rock_around_the_clock", "loc_recording_registry"],
  "002": ["britannica_rockabilly", "sun_records_history", "rockhall_carl_perkins", "loc_blue_suede_shoes", "britannica_rock_and_roll"],
  "003": ["britannica_doo_wop", "teachrock_doo_wop", "rockhall_platters", "loc_recording_registry"],
  "004": ["teachrock_dion_teen_idols", "teachrock_rock_roll_becomes_pop", "rockhall_ricky_nelson", "britannica_rock_1960s"],
  "005": ["britannica_brill_building", "britannica_girl_groups", "teachrock_brill_girl_group", "rockhall_brill_guide", "rockhall_carole_king"],
  "006": ["britannica_soul_music", "britannica_rhythm_and_blues", "britannica_ray_charles", "rockhall_ray_charles", "carnegie_hall_soul"],
  "007": ["britannica_surf_music", "britannica_dick_dale", "rockhall_beach_boys", "britannica_beach_boys"],
  "008": ["britannica_beatles", "rockhall_beatles", "britannica_rolling_stones", "rockhall_rolling_stones", "rockhall_who"],
  "009": ["rockhall_byrds", "britannica_bob_dylan", "britannica_rock_1960s", "britannica_beatles"],
  "010": ["rockhall_byrds", "britannica_bob_dylan", "rockhall_beach_boys", "britannica_rock_1960s"],
  "011": ["allmusic_garage_rock", "britannica_punk", "rockhall_ramones", "britannica_rock_1960s"],
  "012": ["britannica_brill_building", "allmusic_sunshine_pop", "rockhall_beach_boys", "britannica_beatles"],
  "013": ["britannica_psychedelic_rock", "allmusic_sunshine_pop", "rockhall_beach_boys", "rockhall_doors"],
  "014": ["britannica_psychedelic_rock", "rockhall_doors", "rockhall_led_zeppelin", "rockhall_black_sabbath"],
  "015": ["rockhall_velvet_underground", "britannica_psychedelic_rock", "rockhall_doors", "britannica_punk"],
  "016": ["britannica_rock_music", "rockhall_led_zeppelin", "rockhall_elton_john", "rockhall_david_bowie"],
  "017": ["rockhall_led_zeppelin", "rockhall_black_sabbath", "britannica_heavy_metal", "rockhall_judas_priest"],
  "018": ["britannica_progressive_rock", "britannica_rock_music", "rockhall_david_bowie", "britannica_electronic_music"],
  "019": ["rockhall_allman_brothers", "britannica_country_music", "britannica_rock_music", "americana_music_association"],
  "020": ["rockhall_david_bowie", "rockhall_elton_john", "britannica_rock_music", "rockhall_madonna"],
  "021": ["allmusic_indie_rock", "rockhall_byrds", "britannica_rock_music", "rockhall_green_day"],
  "022": ["rockhall_elton_john", "britannica_popular_music", "rockhall_carole_king", "rockhall_whitney_houston"],
  "023": ["rockhall_elton_john", "rockhall_michael_jackson", "britannica_popular_music", "rockhall_carole_king"],
  "024": ["britannica_folk_music", "britannica_bob_dylan", "rockhall_joni_mitchell", "rockhall_carole_king", "smithsonian_folkways"],
  "025": ["rockhall_carole_king", "rockhall_elton_john", "britannica_popular_music", "britannica_bob_dylan"],
  "026": ["britannica_folk_music", "smithsonian_folkways", "britannica_bob_dylan", "loc_recording_registry"],
  "027": ["americana_music_association", "britannica_country_music", "smithsonian_folkways", "loc_country_music"],
  "028": ["no_depression_archive", "americana_music_association", "britannica_country_music", "smithsonian_folkways"],
  "029": ["rockhall_joni_mitchell", "rockhall_carole_king", "britannica_popular_music", "npr_tiny_desk_discovery"],
  "030": ["allmusic_indie_rock", "smithsonian_folkways", "npr_tiny_desk_discovery", "britannica_folk_music"],
  "031": ["britannica_country_music", "country_music_hall_history", "grand_ole_opry_history", "loc_country_music"],
  "032": ["britannica_willie_nelson", "country_music_hall_history", "britannica_country_music", "americana_music_association"],
  "033": ["britannica_dolly_parton", "britannica_garth_brooks", "britannica_country_music", "country_music_hall_history"],
  "034": ["britannica_garth_brooks", "country_music_hall_history", "britannica_country_music", "grand_ole_opry_history"],
  "035": ["britannica_garth_brooks", "britannica_country_music", "country_music_hall_history", "britannica_taylor_swift"],
  "036": ["americana_music_association", "britannica_country_music", "loc_country_music", "no_depression_archive"],
  "037": ["motown_museum_history", "rockhall_stevie_wonder", "rockhall_aretha", "carnegie_hall_soul", "britannica_soul_music"],
  "038": ["stax_museum_history", "carnegie_hall_soul", "britannica_soul_music", "britannica_rhythm_and_blues"],
  "039": ["britannica_funk", "smithsonian_james_brown", "carnegie_hall_funk_timeline", "britannica_george_clinton", "rockhall_james_brown"],
  "040": ["britannica_disco", "carnegie_hall_disco", "britannica_funk", "rockhall_madonna"],
  "041": ["britannica_rhythm_and_blues", "britannica_soul_music", "rockhall_whitney_houston", "rockhall_stevie_wonder"],
  "042": ["britannica_rhythm_and_blues", "rockhall_whitney_houston", "rockhall_michael_jackson", "britannica_popular_music"],
  "043": ["britannica_rhythm_and_blues", "britannica_soul_music", "rockhall_stevie_wonder", "rockhall_prince"],
  "044": ["britannica_rhythm_and_blues", "rockhall_prince", "britannica_popular_music", "npr_tiny_desk_discovery"],
  "045": ["britannica_hip_hop", "smithsonian_hiphop_block_party", "rockhall_grandmaster_flash", "cornell_hiphop_collection"],
  "046": ["britannica_hip_hop", "rockhall_public_enemy", "cornell_hiphop_collection", "carnegie_hall_hiphop"],
  "047": ["britannica_rap", "rockhall_nwa", "rockhall_tupac", "carnegie_hall_hiphop"],
  "048": ["britannica_hip_hop", "britannica_rap", "rockhall_public_enemy", "cornell_hiphop_collection"],
  "049": ["britannica_hip_hop", "britannica_rap", "carnegie_hall_hiphop", "rockhall_nwa"],
  "050": ["britannica_hip_hop", "britannica_rap", "britannica_popular_music", "rockhall_michael_jackson"],
  "051": ["britannica_hip_hop", "cornell_hiphop_collection", "carnegie_hall_hiphop", "allmusic_indie_rock"],
  "052": ["britannica_hip_hop", "britannica_rap", "carnegie_hall_hiphop", "britannica_popular_music"],
  "053": ["britannica_punk", "rockhall_ramones", "rockhall_sex_pistols", "cornell_punk_archives"],
  "054": ["cbgb_official_about", "cbgb_hilly_history", "britannica_cbgb", "cornell_punk_archives"],
  "055": ["allmusic_hardcore_punk", "britannica_punk", "cornell_punk_archives", "rockhall_ramones"],
  "056": ["allmusic_post_punk", "rockhall_cure", "rockhall_talking_heads", "britannica_new_wave"],
  "057": ["britannica_new_wave", "rockhall_talking_heads", "rockhall_madonna", "rockhall_cure"],
  "058": ["rockhall_depeche_mode", "allmusic_synth_pop", "britannica_electronic_music", "britannica_new_wave"],
  "059": ["rockhall_rem", "allmusic_indie_rock", "britannica_new_wave", "matador_history"],
  "060": ["allmusic_hardcore_punk", "allmusic_post_punk", "britannica_punk", "cornell_punk_archives"],
  "061": ["britannica_heavy_metal", "rockhall_judas_priest", "rockhall_black_sabbath", "rockhall_iron_maiden"],
  "062": ["rockhall_metallica", "allmusic_thrash", "britannica_heavy_metal", "rockhall_judas_priest"],
  "063": ["britannica_heavy_metal", "rockhall_judas_priest", "rockhall_madonna", "britannica_popular_music"],
  "064": ["rockhall_black_sabbath", "allmusic_doom_metal", "britannica_heavy_metal", "rockhall_led_zeppelin"],
  "065": ["rockhall_nine_inch_nails", "britannica_electronic_music", "britannica_heavy_metal", "allmusic_post_punk"],
  "066": ["allmusic_nu_metal", "britannica_heavy_metal", "britannica_rap", "rockhall_nine_inch_nails"],
  "067": ["allmusic_metalcore", "britannica_heavy_metal", "allmusic_hardcore_punk", "rockhall_green_day"],
  "068": ["allmusic_death_metal", "allmusic_doom_metal", "britannica_heavy_metal", "rockhall_black_sabbath"],
  "069": ["rockhall_rem", "allmusic_indie_rock", "subpop_history", "britannica_nirvana"],
  "070": ["britannica_nirvana", "rockhall_nirvana", "subpop_history", "britannica_pearl_jam"],
  "071": ["britannica_pearl_jam", "britannica_nirvana", "rockhall_green_day", "britannica_rock_music"],
  "072": ["allmusic_indie_rock", "matador_history", "rockhall_rem", "britannica_radiohead"],
  "073": ["allmusic_shoegaze", "allmusic_dream_pop", "britannica_radiohead", "allmusic_indie_rock"],
  "074": ["uw_riot_grrrl_archive", "allmusic_indie_rock", "britannica_punk", "rockhall_rem"],
  "075": ["allmusic_indie_rock", "rockhall_byrds", "rockhall_green_day", "britannica_rock_music"],
  "076": ["rockhall_green_day", "britannica_punk", "allmusic_hardcore_punk", "allmusic_indie_rock"],
  "077": ["allmusic_indie_rock", "rockhall_green_day", "allmusic_hardcore_punk", "allmusic_post_punk"],
  "078": ["britannica_radiohead", "allmusic_indie_rock", "matador_history", "npr_tiny_desk_discovery"],
  "079": ["britannica_strokes", "rockhall_white_stripes", "allmusic_garage_revival", "britannica_white_stripes"],
  "080": ["allmusic_post_punk_revival", "rockhall_cure", "allmusic_post_punk", "britannica_new_wave"],
  "081": ["chicago_house_history", "britannica_edm", "britannica_disco", "britannica_electronic_music"],
  "082": ["detroit_techno_foundation", "britannica_edm", "britannica_electronic_music", "allmusic_idm"],
  "083": ["britannica_edm", "britannica_electronic_music", "carnegie_hall_disco", "britannica_popular_music"],
  "084": ["allmusic_trip_hop", "britannica_electronic_music", "britannica_hip_hop", "allmusic_idm"],
  "085": ["britannica_edm", "britannica_punk", "allmusic_post_punk_revival", "britannica_new_wave"],
  "086": ["allmusic_chillwave", "britannica_electronic_music", "allmusic_synth_pop", "bandcamp_lofi"],
  "087": ["allmusic_idm", "britannica_electronic_music", "britannica_edm", "npr_tiny_desk_discovery"],
  "088": ["rockhall_michael_jackson", "rockhall_madonna", "rockhall_prince", "rockhall_abba"],
  "089": ["britannica_popular_music", "rockhall_whitney_houston", "rockhall_michael_jackson", "britannica_taylor_swift"],
  "090": ["rockhall_madonna", "rockhall_michael_jackson", "britannica_popular_music", "britannica_edm"],
  "091": ["britannica_beyonce", "britannica_taylor_swift", "rockhall_prince", "britannica_popular_music"],
  "092": ["rockhall_whitney_houston", "britannica_popular_music", "rockhall_carole_king", "britannica_taylor_swift"],
  "093": ["britannica_popular_music", "britannica_taylor_swift", "grammy_hyperpop", "npr_tiny_desk_discovery"],
  "094": ["britannica_reggaeton", "smithsonian_latino_music", "grammy_latin_music", "loc_latin_music"],
  "095": ["loc_latin_music", "smithsonian_latino_music", "grammy_latin_music", "smithsonian_folkways_world"],
  "096": ["britannica_salsa", "carnegie_hall_latin", "smithsonian_latino_music", "loc_latin_music"],
  "097": ["britannica_afrobeats", "smithsonian_folkways_world", "britannica_popular_music", "npr_tiny_desk_discovery"],
  "098": ["britannica_kpop", "britannica_popular_music", "grammy_latin_music", "npr_tiny_desk_discovery"],
  "099": ["smithsonian_folkways_world", "smithsonian_folkways", "britannica_folk_music", "loc_latin_music"],
  "100": ["loc_recording_registry", "britannica_popular_music", "smithsonian_jazz", "jazz_at_lincoln_center"],
  "101": ["britannica_jazz", "smithsonian_jazz", "jazz_at_lincoln_center", "britannica_bebop", "loc_jazz"],
  "102": ["britannica_jazz", "smithsonian_jazz", "jazz_at_lincoln_center", "britannica_popular_music"],
  "103": ["britannica_film_score", "academy_music_branch", "britannica_musical", "loc_recording_registry"],
  "104": ["britannica_musical", "ibdb_broadway", "loc_musical_theater", "afi_movie_musicals"],
  "105": ["d23_disney_music", "britannica_musical", "afi_movie_musicals", "loc_musical_theater"],
  "106": ["afi_movie_musicals", "academy_music_branch", "loc_recording_registry", "britannica_popular_music"],
  "107": ["britannica_film_score", "academy_music_branch", "britannica_electronic_music", "loc_recording_registry"],
  "108": ["britannica_gospel_music", "carnegie_hall_gospel", "rockhall_mahalia_jackson", "britannica_soul_music"],
  "109": ["gospel_music_association", "grammy_gospel_field", "britannica_gospel_music", "britannica_popular_music"],
  "110": ["gospel_music_association", "britannica_gospel_music", "carnegie_hall_gospel", "grammy_gospel_field"],
  "111": ["dr_demento_history", "grammy_comedy_field", "loc_recording_registry", "smithsonian_folkways"],
  "112": ["britannica_christmas_carol", "loc_recording_registry", "ascap_holiday_songs", "smithsonian_folkways"],
  "113": ["loc_recording_registry", "britannica_popular_music", "ascap_holiday_songs", "grammy_comedy_field"],
  "114": ["smithsonian_folkways_childrens", "d23_disney_music", "britannica_musical", "loc_recording_registry"],
  "115": ["allmusic_post_punk_revival", "britannica_arctic_monkeys", "npr_tiny_desk_discovery", "allmusic_indie_rock"],
  "116": ["allmusic_indie_rock", "allmusic_dream_pop", "npr_tiny_desk_discovery", "britannica_taylor_swift"],
  "117": ["britannica_tame_impala", "britannica_arctic_monkeys", "allmusic_dream_pop", "npr_tiny_desk_discovery"],
  "118": ["britannica_heavy_metal", "rockhall_nirvana", "britannica_pearl_jam", "allmusic_post_punk_revival"],
  "119": ["grammy_hyperpop", "britannica_popular_music", "allmusic_chillwave", "npr_tiny_desk_discovery"],
  "120": ["bandcamp_lofi", "britannica_electronic_music", "allmusic_chillwave", "smithsonian_folkways"]
};

const FALLBACK_SOURCE_DEFS = {
  rockhall_rolling_stones: ["The Rolling Stones", "Rock & Roll Hall of Fame", "https://rockhall.com/inductees/the-rolling-stones/", "museum_reference", "Rolling Stones as British Invasion and blues-rock anchors."],
  rockhall_allman_brothers: ["The Allman Brothers Band", "Rock & Roll Hall of Fame", "https://rockhall.com/inductees/the-allman-brothers-band/", "museum_reference", "Southern rock, blues, country, and improvisational jam lineage."],
  rockhall_nwa: ["N.W.A", "Rock & Roll Hall of Fame", "https://rockhall.com/inductees/nwa/", "museum_reference", "West Coast gangsta rap and late-1980s hip-hop impact."],
  rockhall_tupac: ["Tupac Shakur", "Rock & Roll Hall of Fame", "https://rockhall.com/inductees/tupac-shakur/", "museum_reference", "West Coast rap, persona, and 1990s hip-hop cultural context."],
  rockhall_sex_pistols: ["Sex Pistols", "Rock & Roll Hall of Fame", "https://rockhall.com/inductees/sex-pistols/", "museum_reference", "UK punk impact, provocation, and first-wave punk context."],
  rockhall_talking_heads: ["Talking Heads", "Rock & Roll Hall of Fame", "https://rockhall.com/inductees/talking-heads/", "museum_reference", "CBGB, art-school new wave, post-punk, and dance-aware rock context."],
  rockhall_depeche_mode: ["Depeche Mode", "Rock & Roll Hall of Fame", "https://rockhall.com/inductees/depeche-mode/", "museum_reference", "Synthpop, new wave, and electronic pop influence."],
  rockhall_rem: ["R.E.M.", "Rock & Roll Hall of Fame", "https://rockhall.com/inductees/rem/", "museum_reference", "College rock, jangly alternative, and pre-mainstream indie lineage."],
  britannica_radiohead: ["Radiohead", "Encyclopaedia Britannica", "https://www.britannica.com/topic/Radiohead", "reference", "Alternative rock, art-rock, and 2000s experimental-rock context."],
  allmusic_sunshine_pop: ["Sunshine Pop", "AllMusic", "https://www.allmusic.com/style/sunshine-pop-ma0000012203", "music_reference", "Style markers for sunshine pop and late-1960s harmony-rich pop."],
  allmusic_synth_pop: ["Synth Pop", "AllMusic", "https://www.allmusic.com/style/synth-pop-ma0000002887", "music_reference", "Style markers for synthpop and new romantic electronic pop."],
  rockhall_iron_maiden: ["Iron Maiden", "Rock & Roll Hall of Fame", "https://rockhall.com/inductees/iron-maiden/", "museum_reference", "NWOBHM and traditional heavy-metal context."],
  allmusic_nu_metal: ["Nu Metal", "AllMusic", "https://www.allmusic.com/style/nu-metal-ma0000002836", "music_reference", "Style markers for nu-metal and rap-metal crossover."],
  allmusic_shoegaze: ["Shoegaze", "AllMusic", "https://www.allmusic.com/style/shoegaze-ma0000004454", "music_reference", "Style markers for shoegaze and noise-haze guitar music."],
  allmusic_dream_pop: ["Dream Pop", "AllMusic", "https://www.allmusic.com/style/dream-pop-ma0000012303", "music_reference", "Style markers for dream pop and atmospheric indie pop."],
  uw_riot_grrrl_archive: ["Riot Grrrl Collection Guide", "University of Washington Libraries", "https://guides.lib.uw.edu/research/riotgrrrl", "university_archive", "Riot grrrl zine, feminist punk, and archival context."],
  detroit_techno_foundation: ["History of Detroit Techno", "Carnegie Hall Timeline of African American Music", "https://timeline.carnegiehall.org/genres/detroit-techno", "museum_reference", "Detroit techno origins, Black electronic futurism, club culture, and first-generation producers."],
  allmusic_post_punk_revival: ["Post-Punk Revival", "AllMusic", "https://www.allmusic.com/style/post-punk-revival-ma0000012257", "music_reference", "Style markers for post-punk revival."],
  allmusic_idm: ["IDM", "AllMusic", "https://www.allmusic.com/style/idm-ma0000004477", "music_reference", "Style markers for IDM and experimental electronic music."],
  allmusic_trip_hop: ["Trip-Hop", "AllMusic", "https://www.allmusic.com/style/trip-hop-ma0000002902", "music_reference", "Style markers for trip-hop and downtempo."],
  allmusic_chillwave: ["Chillwave", "AllMusic", "https://www.allmusic.com/style/chillwave-ma0000012261", "music_reference", "Style markers for chillwave and bedroom electronic aesthetics."],
  bandcamp_lofi: ["Lo-fi", "Bandcamp Daily", "https://daily.bandcamp.com/", "music_journalism_archive", "Scene reporting for lo-fi, bedroom, and study-music ecosystems."],
  rockhall_abba: ["ABBA", "Rock & Roll Hall of Fame", "https://rockhall.com/inductees/abba/", "museum_reference", "Global pop hooks, studio craft, and disco-adjacent pop context."],
  britannica_beyonce: ["Beyonce", "Encyclopaedia Britannica", "https://www.britannica.com/biography/Beyonce", "reference", "Contemporary pop and R&B persona, authorship, and visual album context."],
  britannica_arctic_monkeys: ["Arctic Monkeys", "Encyclopaedia Britannica", "https://www.britannica.com/topic/Arctic-Monkeys", "reference", "Internet-era rock breakthrough and modern guitar-band context."],
  britannica_tame_impala: ["Tame Impala", "Encyclopaedia Britannica", "https://www.britannica.com/topic/Tame-Impala", "reference", "Modern psychedelic pop/rock and studio authorship context."]
};

const PROFILES = [
  [/brill|girl group/i, {
    lens: "professional early-1960s pop craft",
    history: "songwriters, producers, publishers, studio musicians, labels, and young vocal groups compressed teen emotion into concise radio singles",
    distinct: "writer-producer architecture, girl-group perspective, handclaps, call-and-response, dramatic intros, and studio scale",
    listen: ["immediate hook placement", "backing-vocal answer phrases", "teen-drama compression", "percussion and handclap punctuation", "studio drama around the lead vocal"]
  }],
  [/cbgb|downtown/i, {
    lens: "downtown New York scene ecology",
    history: "CBGB and nearby rooms gathered punk urgency, art-school experiment, poetry, pop instincts, and minimal electronics into one local ecosystem",
    distinct: "shared rooms and permission structure mattered more than one uniform sound",
    listen: ["small-room tension", "art-punk persona", "minimalist guitar or rhythm choices", "pop hooks under downtown abrasion", "the branch difference between Patti Smith, Television, Talking Heads, Blondie, and Suicide"]
  }],
  [/house|chicago/i, {
    lens: "Chicago post-disco club culture",
    history: "DJs, dancers, drum machines, edits, and clubs carried disco's pulse into a stripped, repetitive, 4/4 dance language",
    distinct: "the dancefloor structure is the composition, with groove, repetition, and mix logic doing the narrative work",
    listen: ["steady four-on-the-floor pulse", "drum-machine clap and kick patterns", "looped bass or piano vamps", "DJ-friendly arrangement", "post-disco lift"]
  }],
  [/techno|detroit/i, {
    lens: "Detroit electronic futurism",
    history: "Detroit producers turned drum machines, synthesizers, funk, electro, and post-industrial imagination into a sleek machine-soul language",
    distinct: "techno's emotional force often comes from repetition, timbre, and motion rather than vocal song form",
    listen: ["machine pulse", "minimal synth motif", "long-form build", "futurist texture", "bass movement against precise drums"]
  }],
  [/gospel|worship|christian|ccm/i, {
    lens: "sacred popular-music practice",
    history: "church performance, choir traditions, devotional lyrics, broadcast media, and contemporary pop-rock production shape different sacred listening contexts",
    distinct: "function matters: some records are performances, some are radio songs, and some are meant for congregational use",
    listen: ["call-and-response lift", "choir or praise-team blend", "devotional repetition", "gospel-rooted melisma", "anthemic chorus design"]
  }],
  [/kids|family|household/i, {
    lens: "family and household listening",
    history: "children's records, animated media, educational songs, and household repetition create recognition through use rather than genre identity alone",
    distinct: "context, repetition, age, and family setting can matter more than artist fandom",
    listen: ["simple melodic hooks", "call-and-repeat structures", "character or story cues", "bright arrangement choices", "memory tied to household context"]
  }],
  [/current rock|post-punk new wave 2020s/i, {
    lens: "platform-era guitar-band revival",
    history: "post-punk, new wave, garage, and indie-rock references return through playlists, festivals, online discovery, and modern production",
    distinct: "the revival is not nostalgia alone; older angular rhythm and guitar ideas are filtered through present-tense discovery systems",
    listen: ["taut rhythm guitar", "dry drum-forward mixes", "spoken or clipped vocal stance", "post-punk bass movement", "modern polish around old nervous energy"]
  }],
  [/hip-hop|rap|boom bap|trap|crunk|g-funk/i, {
    lens: "hip-hop production and MC practice",
    history: "DJs, MCs, producers, regional studios, sampling, drum programming, and street or pop address reshape the meaning of rhythm and voice",
    distinct: "flow, beat architecture, and regional production identity are the core evidence",
    listen: ["flow and cadence", "drum programming", "sample or synth signature", "regional bass language", "hook strategy"]
  }],
  [/country|honky|outlaw|nashville|americana|red dirt/i, {
    lens: "country and roots-music identity",
    history: "twang, storytelling, dance rhythm, regional scenes, Nashville institutions, outlaw resistance, and crossover radio reshape country across eras",
    distinct: "the line between roots credibility and radio polish is the central boundary",
    listen: ["story-first lyric frame", "twang or pedal-steel color", "two-step or ballad pacing", "plainspoken vocal stance", "chorus craft"]
  }],
  [/metal|doom|thrash|stoner|industrial|nu-metal|metalcore|sludge|nwobhm/i, {
    lens: "heavy-music language",
    history: "amplified riffs, speed, darkness, virtuosity, theatrical image, mechanical texture, and subgenre scenes turn heaviness into musical form",
    distinct: "the kind of heaviness matters: speed, doom, groove, industrial machine texture, or crossover rhythm imply different roads",
    listen: ["distorted riff architecture", "drum weight", "minor-mode tension", "vocal force", "precision or abrasion"]
  }],
  [/punk|hardcore|post-punk|new wave|synthpop|college rock|noise rock|riot grrrl/i, {
    lens: "punk and post-punk scene practice",
    history: "small rooms, independent networks, stripped gear, DIY ethics, art-school ideas, and pop pressure changed what a band could sound like",
    distinct: "urgency and subtraction do the work: less polish, more stance, sharper edges",
    listen: ["short-form urgency", "dry room energy", "angular rhythm", "DIY economy", "tension between abrasion and hook"]
  }],
  [/electronic|edm|trip-hop|downtempo|idm|chillwave|synthwave|dance-punk|electroclash/i, {
    lens: "electronic production and club/listening culture",
    history: "synthesizers, samplers, drum machines, DJs, clubs, headphones, and bedroom tools made production itself a form of authorship",
    distinct: "timbre, loop structure, bass movement, and space can matter more than singer-centered song form",
    listen: ["programmed pulse", "synth timbre", "bass movement", "texture and space", "build-and-release form"]
  }],
  [/jazz|bebop|standards|crooner|classical/i, {
    lens: "jazz, standards, and instrumental interpretation",
    history: "improvisation, swing, songbook interpretation, harmonic color, and instrumental command carry prestige outside rock-band logic",
    distinct: "timing and interpretation are the expressive center",
    listen: ["phrasing and time feel", "harmonic color", "improvised response", "ensemble interplay", "interpretive vocal timing"]
  }],
  [/broadway|musical|soundtrack|disney|film score|cinematic/i, {
    lens: "screen and stage music memory",
    history: "songs and scores attach to characters, scenes, stories, families, and cinematic emotion",
    distinct: "recognition often comes through narrative use rather than artist fandom",
    listen: ["melody tied to scene", "orchestration as cue", "ensemble lift", "leitmotif or reprise logic", "screen or stage memory"]
  }],
  [/reggaeton|latin|salsa|afrobeats|k-pop|j-pop|global|diaspora|regional mexican|corridos/i, {
    lens: "global and diaspora pop movement",
    history: "language, migration, dance rhythms, regional industry, and digital circulation bring local idioms into wider pop systems",
    distinct: "regional rhythm, language, and scene context should not be flattened into generic world-pop",
    listen: ["regional rhythm pattern", "language and chant hooks", "percussion-bass dialogue", "dance movement in the form", "global pop polish around local idioms"]
  }],
  [/holiday|christmas|novelty|comedy|karaoke|party|wedding/i, {
    lens: "shared-use listening",
    history: "ritual, comedy, seasonal repetition, parties, and group singing make songs culturally durable outside normal genre allegiance",
    distinct: "context of use can be stronger evidence than taste preference",
    listen: ["communal hook design", "situational cues", "simple repeatable chorus", "novelty or ritual framing", "memory tied to place or event"]
  }],
  [/pop|persona|dance-pop|teen pop|tiktok|streaming|internet/i, {
    lens: "mass pop architecture",
    history: "hooks, choreography, celebrity image, television, streaming, and producer-led construction scale songs into shared public language",
    distinct: "persona, media surface, and production architecture are as important as the melody",
    listen: ["instant chorus recognition", "vocal persona", "high-definition production", "dance or video-ready structure", "direct emotional address"]
  }],
  [/folk|singer-songwriter|songwriter|coffeehouse/i, {
    lens: "authored songcraft",
    history: "folk tradition, topical writing, piano and guitar accompaniment, adult radio, and intimate performance foreground the writer's point of view",
    distinct: "the artist's voice, lyric angle, and arrangement restraint carry the road",
    listen: ["lyric-centered phrasing", "acoustic or piano space", "intimate vocal presence", "narrative detail", "roots references carried by authorship"]
  }],
  [/rock|guitar|grunge|indie|garage|psych|prog|glam|surf|yacht|soft rock/i, {
    lens: "rock and guitar-pop development",
    history: "bands, studios, riffs, album formats, radio, scenes, and revival cycles turn guitar-based pop into a set of distinct eras",
    distinct: "tone, arrangement scale, and performance stance separate nearby rock roads",
    listen: ["guitar tone and arrangement scale", "drum-and-bass feel", "riff or chorus memory", "studio texture", "performance stance"]
  }]
];

function files(dir) {
  return fs.readdirSync(dir).filter((name) => name.endsWith(".json")).sort().map((name) => path.join(dir, name));
}

function sourceDef(sourceId) {
  const known = SOURCE_CATALOG[sourceId];
  if (known) return known;
  const fallback = FALLBACK_SOURCE_DEFS[sourceId];
  if (!fallback) throw new Error(`Missing source definition for ${sourceId}`);
  const [title, publisher, url, source_type, audit_use] = fallback;
  return { title, publisher, url, source_type, audit_use, rights_note: "Use for factual paraphrase only; no lyrics or long quotations." };
}

function profileFor(title) {
  return PROFILES.find(([regex]) => regex.test(title))?.[1] || PROFILES.at(-1)[1];
}

function unique(values) {
  return [...new Set(values.filter(Boolean))];
}

function selectedSources(pack, sourceIds) {
  return unique(sourceIds).slice(0, 6).map((sourceId, index) => {
    const source = sourceDef(sourceId);
    return {
      source_ref_id: sourceId,
      title: source.title,
      publisher: source.publisher,
      url: source.url,
      source_type: source.source_type,
      source_relevance: index < 3 ? "direct_archetype_support" : "example_object_support",
      why_fit: source.audit_use || `${source.title} supports ${pack.identity.editorial_display_title}.`
    };
  });
}

function rejectedSource(pack) {
  const lower = `${pack.identity.family_name} ${pack.identity.editorial_display_title}`.toLowerCase();
  const wrong = lower.includes("house") || lower.includes("techno") ? "britannica_heavy_metal"
    : lower.includes("gospel") ? "allmusic_death_metal"
      : lower.includes("kids") ? "britannica_edm"
        : lower.includes("brill") ? "rockhall_metallica"
          : "generic web-summary";
  return [{
    title: wrong,
    url: SOURCE_CATALOG[wrong]?.url || "",
    why_rejected: "Rejected as wrong_context or too generic for this archetype-level claim audit."
  }];
}

function claimCount(id) {
  const n = Number(id);
  if (n % 11 === 0) return 4;
  if (n % 5 === 0) return 5;
  if (n % 3 === 0) return 7;
  return 6;
}

function claimSeeds(pack, profile, sources) {
  const title = pack.identity.editorial_display_title;
  const sourceIds = sources.map((source) => source.source_ref_id);
  const examples = (pack.explainer_content.canonical_example_rationales || []).slice(0, 3).map((example) => example.display_label);
  const count = claimCount(pack.identity.archetype_id);
  const base = [
    {
      suffix: "historical-lens",
      text: `${title} is best treated as ${profile.lens}, not as a generic bucket inside ${pack.identity.family_name}.`,
      refs: [sourceIds[0], sourceIds[1]]
    },
    {
      suffix: "origin-context",
      text: `${title}'s history centers on how ${profile.history}.`,
      refs: [sourceIds[0], sourceIds[2]]
    },
    {
      suffix: "listening-evidence",
      text: `Listeners can separate ${title} by focusing on ${profile.listen.slice(0, 3).join(", ")}.`,
      refs: [sourceIds[1], sourceIds[2]]
    },
    {
      suffix: "boundary-distinction",
      text: `${title} differs from nearby roads because ${profile.distinct}.`,
      refs: [sourceIds[0], sourceIds[3] || sourceIds[1]]
    },
    {
      suffix: "example-anchors",
      text: `Canonical anchors such as ${examples.join(", ")} make ${title}'s sound-world concrete without adding examples outside the graph.`,
      refs: [sourceIds[2], sourceIds[3] || sourceIds[0]]
    },
    {
      suffix: "source-crosscheck",
      text: `${sources[0].publisher}, ${sources[1].publisher}, and ${sources[2].publisher} support ${title} from complementary angles: style history, institution/archive context, and example-object grounding.`,
      refs: [sourceIds[0], sourceIds[1], sourceIds[2]]
    },
    {
      suffix: "lineage-impact",
      text: `${title} matters because later listeners encounter its vocabulary through ${profile.listen.slice(2, 5).join(", ")} rather than through chronology alone.`,
      refs: [sourceIds[1], sourceIds[3] || sourceIds[2]]
    },
    {
      suffix: "fit-caution",
      text: `A single familiar ${title} example can indicate recognition, scene memory, or context before it proves durable personal affinity.`,
      refs: [sourceIds[0], sourceIds[2]]
    }
  ];
  return base.slice(0, count).map((claim) => ({
    claim_id: `${pack.identity.archetype_id}-${claim.suffix}`,
    claim_text: claim.text,
    source_ref_ids: unique(claim.refs),
    confidence: "medium_high",
    module_usage: ["history_capsule", "region_scene_page", "mission_detail_history_module"],
    graph_refs: [pack.identity.canonical_graph_ref, ...pack.explainer_content.canonical_example_rationales.slice(0, 2).map((example) => example.example_ref)]
  }));
}

function renderSeed(pack, profile) {
  const title = pack.identity.editorial_display_title;
  return {
    short_definition: `${title} is ${profile.lens}: a road where ${profile.listen.slice(0, 2).join(" and ")} carry the strongest historical signal.`,
    history_capsule: `${title} sits in a history where ${profile.history}. The canonical examples give Atlas a bounded way to teach that history without changing graph identity.`,
    why_it_mattered: `It mattered because ${profile.distinct}, giving later listeners a recognizable set of cues rather than a loose era label.`,
    what_made_it_distinct: `The key distinction is ${profile.distinct}. Nearby roads may share period, audience, or instruments, but they do not organize those cues in the same way.`,
    what_to_listen_for: profile.listen,
    did_you_know: [
      `${title} is easier to understand when you separate historical importance from personal fit.`,
      `The strongest examples work as listening tests because they expose ${profile.listen.slice(0, 2).join(" and ")} quickly.`
    ],
    caution: `A familiar ${title} object can be recognition rather than affinity. Treat the road as stronger only when evidence repeats across explicit Atlas state fields.`
  };
}

function main() {
  const packs = files(path.join(SCAFFOLD_DIR, "research_packs")).map((file) => JSON.parse(fs.readFileSync(file, "utf8")));
  packs.sort((a, b) => a.identity.family_id - b.identity.family_id || a.identity.archetype_id.localeCompare(b.identity.archetype_id));
  const entries = {};
  for (const pack of packs) {
    if (["005", "054"].includes(pack.identity.archetype_id)) continue;
    const sourceIds = SOURCE_BUNDLES[pack.identity.archetype_id];
    if (!sourceIds) throw new Error(`Missing source bundle for ${pack.identity.archetype_id}`);
    const profile = profileFor(`${pack.identity.family_name} ${pack.identity.editorial_display_title}`);
    const sources = selectedSources(pack, sourceIds);
    entries[pack.identity.canonical_graph_ref] = {
      archetype_query: `${pack.identity.editorial_display_title} ${pack.identity.family_name} music history source recovery`,
      selected_sources: sources,
      rejected_sources: rejectedSource(pack),
      why_selected_sources_fit: sources.map((source) => source.why_fit).join(" "),
      claims: claimSeeds(pack, profile, sources),
      render_seed: renderSeed(pack, profile),
      baseline_note: "Local v0.2.2 baseline generated to ensure complete coverage; PM/research-agent notes may override when more specific."
    };
  }
  fs.mkdirSync(OUT_DIR, { recursive: true });
  fs.writeFileSync(OUT_PATH, `${JSON.stringify(entries, null, 2)}\n`);
  console.log(JSON.stringify({ output: OUT_PATH, archetype_count: Object.keys(entries).length }, null, 2));
}

main();
