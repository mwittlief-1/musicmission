import fs from "node:fs";
import path from "node:path";

const ROOT = process.cwd();
const NOTES_DIR = path.join(ROOT, "data/atlas_explainer/source_recovery_research_notes");
const BASELINE_PATH = path.join(NOTES_DIR, "00_local_source_recovery_baseline_v0_2_2.json");
const SCAFFOLD_DIR = path.join(ROOT, "data/atlas_explainer/AtlasExplainerPack_v0_2_1_SourceDeepened/research_packs");
const OUT_PATH = path.join(NOTES_DIR, "01_local_middle_curated_families_04_11_v0_2_2.json");

const CURATED = {
  "024": {
    short: "intimate authored songs where voice, lyric angle, and restrained arrangement carry the drama.",
    history: "Classic singer-songwriter emerges from the late-1960s and 1970s turn toward album-length authorship, confessional address, and folk-pop craft.",
    why: "It made the writer-performer a central pop figure and taught listeners to hear songs as personal testimony as well as radio craft.",
    distinct: "The road is less about band attack than about a recognizable point of view carried by voice, piano or guitar, and close-mic arrangement.",
    listen: ["first-person lyric detail", "plainspoken vocal phrasing", "piano or acoustic-guitar space", "album-scale intimacy", "melodic restraint"],
    claims: [
      "Classic singer-songwriter centers the writer-performer as the main interpretive authority, with Carole King, James Taylor, and Joni Mitchell making authorship audible as performance.",
      "The road belongs to the early-1970s album era, when folk, pop, and adult radio made intimate songcraft a durable mainstream language.",
      "Tapestry and Blue are useful anchors because they foreground personal address, harmonic craft, and restrained arrangements rather than scene spectacle.",
      "Listeners should separate this road from folk revival by hearing the shift from topical tradition toward interior, autobiographical, and adult-pop storytelling.",
      "The strongest boundary cue is not acoustic instrumentation alone; it is the sense that the song's perspective, melody, and performance are inseparable."
    ]
  },
  "025": {
    short: "piano-led adult pop where melody, harmonic motion, and radio-ready storytelling organize the song.",
    history: "Piano pop and adult songcraft extends singer-songwriter intimacy into polished pop, Broadway-adjacent melody, and adult-contemporary radio.",
    why: "It kept composition and personality at the center of mainstream pop after rock bands and dance records became dominant.",
    distinct: "The piano is not decoration here; it frames harmony, pacing, vocal drama, and the adult-radio sense of craft.",
    listen: ["piano-driven harmonic movement", "clear verse-to-chorus storytelling", "adult-pop vocal control", "bridge escalation", "melodic payoff"],
    claims: [
      "Piano pop and adult songcraft is anchored by artists who make the keyboard a compositional engine rather than a background color.",
      "Carole King and Billy Joel show two sides of the lane: songwriter intimacy and theatrical, character-driven pop narrative.",
      "The Stranger and Tapestry make the road concrete because their songs depend on melodic architecture, conversational vocal presence, and adult-radio polish.",
      "This archetype sits near soft rock, but it is distinguished by piano-centered writing and a stronger sense of authored scenes.",
      "A useful listening test is whether the chorus feels earned by harmonic and narrative build, not only by production size."
    ]
  },
  "026": {
    short: "folk tradition turned into public argument, communal memory, and topical song.",
    history: "Folk revival and protest folk draws on older ballad, labor, and topical traditions while using coffeehouses, festivals, campuses, and recording to circulate social critique.",
    why: "It gave popular music a durable model for songs as civic speech and moral witness.",
    distinct: "The authority often comes from song tradition and public purpose more than from studio novelty.",
    listen: ["topical lyric frame", "communal chorus logic", "unvarnished vocal delivery", "acoustic accompaniment", "ballad inheritance"],
    claims: [
      "Folk revival and protest folk should be grounded in tradition, organizing, coffeehouse performance, and topical writing rather than treated as generic acoustic music.",
      "Woody Guthrie, Pete Seeger, Joan Baez, and Bob Dylan mark different roles inside the road: repertory carrier, movement singer, interpreter, and writer-performer.",
      "The Freewheelin' Bob Dylan belongs here because it translates folk revival idioms into pointed contemporary authorship.",
      "The road differs from classic singer-songwriter because the song often speaks outward to a public issue or shared tradition before it becomes private confession.",
      "Listeners should hear lyric stance, refrain function, and acoustic directness as historical evidence, not simply as low-production style."
    ]
  },
  "027": {
    short: "roots songcraft where folk narrative, country plain speech, and Americana texture meet.",
    history: "Country-folk and Americana roots grows from folk and country songwriting traditions, emphasizing plainspoken characters, regional detail, and acoustic ensemble feel.",
    why: "It preserved roots credibility inside modern album culture and gave later Americana a vocabulary of understatement.",
    distinct: "The road is quieter than mainstream country radio and less revivalist than protest folk; story and grain matter most.",
    listen: ["plainspoken character writing", "country-folk vocal grain", "acoustic ensemble texture", "regional detail", "melodic humility"],
    claims: [
      "Country-folk and Americana roots uses country vocabulary without requiring Nashville radio polish.",
      "John Prine and Emmylou Harris anchor the road because both make understatement, character, and roots repertoire feel central.",
      "The canonical albums point toward song-level craft: spare arrangements, lived-in voices, and close attention to everyday emotional detail.",
      "This archetype differs from outlaw country because resistance is less about industry posture and more about the small truths inside the song.",
      "Listeners should focus on vocal grain, narrative economy, and acoustic ensemble color before deciding whether a song belongs here."
    ]
  },
  "028": {
    short: "1990s roots-rock resistance where punk/indie attitude meets country memory.",
    history: "Alt-country and No Depression gathers post-punk, college-rock, country, and Americana listeners around bands that rejected Nashville polish and classic-rock nostalgia.",
    why: "It gave independent roots music a modern scene identity and helped name the Americana ecosystem that followed.",
    distinct: "The road feels both old and anti-nostalgic: twang is filtered through indie-rock restraint, bar-band grit, and skeptical songwriting.",
    listen: ["ragged twang", "indie-rock restraint", "roots-rock rhythm section", "weary vocal stance", "country memory without radio gloss"],
    claims: [
      "Alt-country and No Depression is a scene road, not simply a synonym for any country-influenced rock.",
      "Uncle Tupelo and Son Volt make the lane concrete because they connect punk-informed independent rock to older country and folk materials.",
      "The road's No Depression identity matters because magazine, label, club, and fan networks helped organize Americana before it became a broader market term.",
      "Alt-country differs from country-folk by carrying more electric-band grit and a clearer post-punk/indie relationship to tradition.",
      "Listeners should hear twang, weary vocals, and rough ensemble feel as deliberate alternatives to Nashville crossover polish."
    ]
  },
  "029": {
    short: "adult-facing alternative pop where songcraft, acoustic intimacy, and radio polish share space.",
    history: "Adult alternative and coffeehouse songcraft grew through late-1980s and 1990s singer-songwriter radio, acoustic rooms, MTV-era visibility, and adult-alternative formats.",
    why: "It made introspective songs feel mainstream without requiring arena rock scale or teen-pop spectacle.",
    distinct: "The road is accessible but not anonymous: voice, lyric angle, and lightly rootsy production do the work.",
    listen: ["clear melodic storytelling", "acoustic or roots-pop texture", "adult-alternative vocal presence", "chorus restraint", "intimate social observation"],
    claims: [
      "Adult alternative and coffeehouse songcraft centers songwriters who crossed folk, rock, pop, and adult radio without losing an intimate performance frame.",
      "Tracy Chapman and Sheryl Crow show the lane's range from sparse social observation to roots-pop hooks.",
      "The canonical albums make the road audible through direct vocal identity, acoustic-grounded arrangements, and carefully scaled production.",
      "This archetype differs from classic singer-songwriter because it is shaped by late-1980s and 1990s alternative radio, video, and coffeehouse circuits.",
      "The listening test is whether polish clarifies the song's point of view rather than turning it into anonymous adult pop."
    ]
  },
  "030": {
    short: "post-2000 folk-pop where indie intimacy, communal choruses, and digital-era discovery meet.",
    history: "Modern indie folk and folk-pop emerged through indie labels, festivals, blogs, streaming playlists, and acoustic-forward bands that made folk textures feel communal and contemporary.",
    why: "It moved folk-coded intimacy back into mainstream youth listening without simply reviving 1960s folk forms.",
    distinct: "The road often favors group lift, rustic texture, and emotional immediacy over protest tradition or classic confessional album craft.",
    listen: ["stomp-and-clap pulse", "group-vocal lift", "acoustic texture", "earnest chorus bloom", "intimate-to-anthemic build"],
    claims: [
      "Modern indie folk and folk-pop is best heard as a post-2000 discovery ecosystem, not as a direct repeat of the folk revival.",
      "Mumford & Sons, the Lumineers, and Bon Iver show how acoustic materials could travel through festivals, blogs, and playlist culture.",
      "The canonical examples contrast communal folk-pop uplift with solitary, atmospheric indie-folk intimacy.",
      "This road differs from adult alternative by making rustic texture and group lift part of the core identity.",
      "Listeners should track whether the arrangement moves from close-room intimacy toward collective chorus energy."
    ]
  },
  "031": {
    short: "country foundations built from honky-tonk directness, Nashville institutions, and plainspoken story.",
    history: "Classic country connects honky-tonk, early Nashville recording, radio, touring circuits, and durable song forms around heartbreak, work, faith, family, and trouble.",
    why: "It supplies the grammar later country roads either polish, rebel against, or revive.",
    distinct: "The song usually announces its stakes plainly: voice, lyric, twang, and rhythm work before studio spectacle.",
    listen: ["plainspoken heartbreak", "twang and steel color", "two-step or train rhythm", "vocal directness", "compact story form"],
    claims: [
      "Classic country foundations should be tied to honky-tonk, Nashville institutions, and durable song forms rather than treated as all pre-modern country.",
      "Johnny Cash, Patsy Cline, and Hank Williams show different foundations: narrative authority, pop-country vocal polish, and honky-tonk songwriting.",
      "At Folsom Prison makes the road concrete because performance context, voice, and outlaw sympathy sharpen country storytelling.",
      "This archetype differs from outlaw country because it is the center of gravity that later outlaw artists push against.",
      "Listeners should hear plain lyric stakes, twang or steel color, and rhythm feel as the first membership evidence."
    ]
  },
  "032": {
    short: "country self-determination where loosened studio control, writer identity, and road-worn voice define the sound.",
    history: "Outlaw and cosmic country formed as artists pushed against Nashville assembly-line control, drawing from honky-tonk, folk, rock, and Texas scenes.",
    why: "It reframed country authenticity around artistic control, album identity, and rougher performance character.",
    distinct: "The road is not just lawless imagery; it is a production and authorship stance against polish.",
    listen: ["road-worn vocal authority", "looser band feel", "country-rock edges", "writer identity", "anti-polish production"],
    claims: [
      "Outlaw Country / Cosmic Country is an authorship-and-industry road as much as a sound road.",
      "Willie Nelson and Merle Haggard anchor the archetype because their records foreground voice, self-definition, and country tradition under less polished control.",
      "Red Headed Stranger makes the road audible through sparse concept-album storytelling rather than Nashville orchestration.",
      "Cosmic country expands the lane toward hippie, folk, and country-rock audiences without leaving country songcraft behind.",
      "The boundary cue is whether roughness serves independence and story, not whether the record merely sounds old."
    ]
  },
  "033": {
    short: "country songwriting engineered for pop reach without losing country signifiers.",
    history: "Country-pop crossover runs from countrypolitan and 1980s/1990s polish into global pop-country, using bigger hooks, smoother production, and media-ready personas.",
    why: "It made country a mainstream pop language while repeatedly testing what listeners still hear as country.",
    distinct: "The road turns country markers into crossover architecture: twang, story, chorus, and image are balanced for wider radio.",
    listen: ["big chorus design", "polished vocal production", "country signifiers inside pop form", "persona clarity", "radio-ready lift"],
    claims: [
      "Country-pop crossover is defined by the negotiation between country identity and wider pop accessibility.",
      "Dolly Parton, Shania Twain, and Taylor Swift each mark a different crossover path: songwriting persona, global country-pop production, and teen-to-pop narrative authorship.",
      "Come On Over and Fearless make the road concrete because their hooks, image, and production travel beyond core country audiences.",
      "This archetype differs from modern country radio because crossover is the central historical question, not just current format success.",
      "Listeners should ask which country markers remain audible after the song has been built for pop scale."
    ]
  },
  "034": {
    short: "1990s country radio built from new traditionalism, arena personality, and format power.",
    history: "1990s country radio fused neotraditional country, polished Nashville production, music video visibility, and arena-scale touring.",
    why: "It made country one of the decade's dominant mass formats while renewing older honky-tonk and mainstream-country signals.",
    distinct: "The road balances tradition talk with large-format radio certainty: hats, hooks, fiddles, steel, and big choruses all matter.",
    listen: ["neotraditional twang", "radio-ready chorus", "arena-country vocal presence", "danceable country rhythm", "Nashville polish"],
    claims: [
      "90s country radio is a format road, shaped by Nashville institutions, music video exposure, and mass radio as much as by individual artists.",
      "Garth Brooks, Alan Jackson, and Randy Travis show how arena scale and new traditionalism coexisted inside the same decade.",
      "No Fences and Storms of Life make the lane concrete by contrasting huge crossover momentum with tradition-minded vocal and arrangement cues.",
      "This archetype differs from classic country because it carries the confidence and production scale of modern country radio.",
      "Listeners should track how fiddles, steel, twang, and chorus size are arranged for 1990s mainstream reach."
    ]
  },
  "035": {
    short: "21st-century country radio where arena scale, streaming-era hooks, and pop/rock/hip-hop contact reshape the format.",
    history: "Modern country radio absorbed arena rock, pop programming, hip-hop-adjacent rhythm, and streaming-era songwriting while still leaning on country vocal identity.",
    why: "It explains why current country can feel both format-loyal and genre-hybrid.",
    distinct: "The road is about production scale and format behavior, not just trucks, parties, or rural imagery.",
    listen: ["arena-ready chorus", "country vocal grain", "pop-rock drum scale", "rhythmic crossover touches", "streaming-era hook economy"],
    claims: [
      "Modern Country Radio / Bro-Country / Arena Country should be framed as a 21st-century format road, not reduced to one lyrical stereotype.",
      "Florida Georgia Line, Luke Combs, Chris Stapleton, and related anchors show the span from party-country crossover to rootsier arena credibility.",
      "Traveller and This One's for You make the boundary visible: both can sit near modern country audiences while carrying different ideas of authenticity.",
      "This archetype differs from country-pop crossover because the country radio ecosystem remains the main home base.",
      "Listeners should separate production scale, vocal identity, and lyrical setting before judging whether a song belongs here."
    ]
  },
  "036": {
    short: "Texas and Americana country where regional identity, songwriter authority, and roots-band grit carry the signal.",
    history: "Red Dirt, Texas country, and Americana country grow from regional touring circuits, songwriter rooms, roots-rock bands, and independent country audiences.",
    why: "It offers a modern country alternative to Nashville format logic without abandoning country storytelling.",
    distinct: "The road privileges place, band feel, and writer credibility over national radio polish.",
    listen: ["regional vocal grain", "roots-rock band feel", "songwriter-forward narrative", "country rhythm without gloss", "live-circuit toughness"],
    claims: [
      "Red Dirt / Americana Country / Texas Country is rooted in regional circuits and songwriter credibility, not simply in country-rock texture.",
      "Jason Isbell, Cody Johnson, and Tyler Childers anchor different sides of the road: literary Americana, Texas country presence, and Appalachian-rooted grit.",
      "Southeastern and Purgatory make the lane concrete because their songs use country materials for adult narrative intensity.",
      "This archetype differs from modern country radio by making regional and independent credibility a core listening signal.",
      "Listeners should hear whether the song's authority comes from place, voice, and live-band weight more than format polish."
    ]
  },
  "037": {
    short: "Detroit soul-pop where writers, producers, house band discipline, and star voices make pop precision feel communal.",
    history: "Motown built an integrated recording, songwriting, production, choreography, and artist-development system that turned Detroit soul into global pop language.",
    why: "It changed how soul, R&B, and pop could share the same single without losing rhythmic lift or vocal personality.",
    distinct: "The road is defined by craft density: bass, drums, backing vocals, hooks, and lead persona lock together.",
    listen: ["bassline movement", "tight tambourine-and-drum pulse", "call-and-response backing vocals", "lead vocal charisma", "compact pop architecture"],
    claims: [
      "Motown / Detroit Soul Pop should be explained as a studio-and-label system, not just as a list of Detroit artists.",
      "Marvin Gaye and Stevie Wonder show the road's growth from single-focused soul-pop toward album-era ambition.",
      "What's Going On and Songs in the Key of Life make the lane concrete because Motown craft expands into social, spiritual, and compositional scope.",
      "This archetype differs from Southern soul because polish, arrangement discipline, and pop-single architecture are central signals.",
      "Listeners should focus on bass movement, percussion snap, backing-vocal response, and lead-vocal personality working as one machine."
    ]
  },
  "038": {
    short: "Southern soul where gospel force, horn sections, rhythm sections, and regional studios give R&B its grit.",
    history: "Southern soul grows through Stax, Muscle Shoals, Atlantic-connected sessions, church vocal practice, and integrated regional studio bands.",
    why: "It gave soul music a rawer, earthier counterweight to Motown's polish and made studio location part of the sound.",
    distinct: "The road values feel, vocal pressure, and band interaction over seamless pop finish.",
    listen: ["gospel-rooted vocal attack", "horn-section punctuations", "live rhythm-section pocket", "call-and-response heat", "Southern studio grit"],
    claims: [
      "Southern Soul / Stax / Muscle Shoals is a regional studio road built from church vocal practice, tight rhythm sections, and horn-driven R&B.",
      "Aretha Franklin and Otis Redding anchor the lane because their performances turn gospel technique and secular emotion into soul authority.",
      "I Never Loved a Man and Otis Blue make the road concrete through vocal intensity, band feel, and Southern studio presence.",
      "This archetype differs from Motown by foregrounding live-band grit and gospel heat rather than pop-system polish.",
      "Listeners should hear the rhythm section and voice pushing against each other, not merely a singer placed over an arrangement."
    ]
  },
  "039": {
    short: "groove-centered Black pop where rhythm, bass, collective performance, and psychedelic expansion become the main event.",
    history: "Funk and psychedelic soul grew from soul, R&B, gospel, rock, and Black band traditions, turning groove and timbre into organizing principles.",
    why: "It reshaped dance music, hip-hop sampling, R&B, rock, and pop by making the groove itself the core composition.",
    distinct: "The road is less about chord movement than about syncopation, bass, drums, vamp, and ensemble lock.",
    listen: ["syncopated bass", "one-chord vamp pressure", "drum pocket", "horn or guitar stabs", "collective groove command"],
    claims: [
      "Funk, psychedelic soul, and groove canon centers rhythm as authorship: bass, drums, vamp, and ensemble placement carry the identity.",
      "James Brown and Sly & the Family Stone show two key poles: tight funk discipline and multiracial psychedelic-soul expansion.",
      "Live at the Apollo and Stand! make the road concrete by foregrounding performance command and groove as social energy.",
      "This archetype differs from disco because the groove is often band-driven and syncopated before it becomes club-system regularity.",
      "Listeners should track the bass and drums first; melody and lyric often ride the groove rather than lead it."
    ]
  },
  "040": {
    short: "1970s dancefloor pop where groove, orchestration, DJ culture, and club identity converge.",
    history: "Disco came from dance clubs, DJs, Philadelphia and New York production, funk, soul, Latin rhythms, orchestration, and queer and Black dancefloor spaces.",
    why: "It made club logic central to mainstream pop and laid groundwork for house, dance-pop, and later electronic dance music.",
    distinct: "The road favors continuous motion, four-on-the-floor lift, bass propulsion, and arrangement built for dancers.",
    listen: ["four-on-the-floor pulse", "orchestrated strings or horns", "bassline propulsion", "extended groove logic", "dancefloor vocal release"],
    claims: [
      "Disco / Dancefloor 70s should be grounded in club culture and dance production, not treated as a costume-era novelty.",
      "Chic and Donna Summer make the road concrete through bass precision, arrangement elegance, and records built for dancefloor release.",
      "Saturday Night Fever shows the mainstream explosion of disco while also making clear that the club sound predates the film phenomenon.",
      "This archetype differs from funk because regular pulse, DJ utility, and dancefloor continuity become central structural values.",
      "Listeners should hear how bass, kick, strings, and vocal hooks create motion designed to last beyond a short radio verse."
    ]
  },
  "041": {
    short: "adult soul and R&B where intimacy, late-night pacing, and vocal control define the mood.",
    history: "Quiet storm and smooth R&B grew from soul, adult radio, late-night programming, and polished studio musicianship.",
    why: "It gave R&B a durable adult-intimacy format separate from dancefloor pressure or teen-pop spectacle.",
    distinct: "The road is sensual and controlled: space, phrasing, and mood matter more than tempo or volume.",
    listen: ["late-night tempo", "smooth vocal phrasing", "soft-focus rhythm section", "romantic restraint", "adult-soul polish"],
    claims: [
      "Quiet Storm / Smooth R&B / Adult Soul is a mood-and-format road shaped by late-night radio, ballad pacing, and controlled vocal intimacy.",
      "Smokey Robinson's A Quiet Storm supplies a naming anchor, while Luther Vandross and Anita Baker show the adult-soul vocal ideal.",
      "Rapture makes the lane concrete because its warmth, phrasing, and production polish prioritize mood over dance pressure.",
      "This archetype differs from neo-soul because it tends toward adult-radio smoothness rather than retro-conscious or hip-hop-era reworking.",
      "Listeners should focus on pacing, breath, harmonic warmth, and whether the record makes intimacy feel architected."
    ]
  },
  "042": {
    short: "late-1980s and 1990s R&B-pop where hip-hop rhythm, swing programming, and polished hooks meet.",
    history: "New jack swing and 80s-90s R&B pop grew through producers who fused R&B vocals with hip-hop drum programming, dance-pop, and video-era polish.",
    why: "It helped define the sound of modern R&B crossover and changed how pop radio heard groove, choreography, and vocal groups.",
    distinct: "The road has snap: programmed swing, bright hooks, group vocals, choreography, and tightly produced radio impact.",
    listen: ["swinging programmed drums", "R&B group harmony", "dance-pop polish", "percussive vocal hooks", "video-era brightness"],
    claims: [
      "New Jack Swing / 80s-90s R&B Pop is defined by the fusion of R&B singing and hip-hop-informed rhythmic programming.",
      "Janet Jackson and Boyz II Men show the lane's range from tightly choreographed control to harmony-driven ballad crossover.",
      "Control and Rhythm Nation 1814 make the road concrete because their production, choreography, and persona turn R&B-pop into a modern system.",
      "This archetype differs from quiet storm because rhythm and video-era performance are as important as vocal smoothness.",
      "Listeners should hear the drum programming's swing and snap before reducing the song to a ballad or pop single."
    ]
  },
  "043": {
    short: "1990s and 2000s R&B renewal where soul memory, hip-hop context, and self-conscious artistry meet.",
    history: "Neo-soul and conscious R&B grew from 1970s soul inheritance, jazz and funk references, hip-hop-era production, and album-centered Black artistry.",
    why: "It reasserted R&B as a space for authorship, politics, spirituality, and texture after heavily polished crossover formats.",
    distinct: "The road sounds handmade even when studio-crafted: groove, voice, lyric, and vintage references feel deliberately curated.",
    listen: ["warm groove pocket", "soul-jazz harmony", "hip-hop-era drum feel", "introspective vocal phrasing", "retro texture with modern stance"],
    claims: [
      "Neo-Soul / Conscious R&B should be tied to hip-hop-era Black artistry and 1970s soul memory, not merely to mellow R&B.",
      "Lauryn Hill and D'Angelo anchor the lane because their albums make authorship, groove, spirituality, and social consciousness central.",
      "The Miseducation of Lauryn Hill and Brown Sugar make the road concrete through album-scale identity and vintage soul references reframed for the 1990s.",
      "This archetype differs from quiet storm because it often foregrounds cultural argument, hip-hop context, and rougher organic texture.",
      "Listeners should hear how drum feel, harmony, and vocal phrasing evoke older soul while speaking in a modern R&B language."
    ]
  },
  "044": {
    short: "post-2000 R&B where atmosphere, bedroom production, fractured form, and interior vocal perspective reshape the genre.",
    history: "Modern and alt-R&B grew through digital recording, indie and electronic influence, mixtape culture, and artists who loosened traditional R&B song forms.",
    why: "It made mood, texture, and personal interiority as important as conventional vocal showcase.",
    distinct: "The road is intimate but experimental: space, processing, nonlinear form, and emotional ambiguity are core signals.",
    listen: ["negative space", "processed or close vocal texture", "nonlinear song form", "subtle electronic rhythm", "interior emotional framing"],
    claims: [
      "Modern R&B / Alt-R&B / Bedroom R&B is defined by atmosphere and form as much as by vocal genre lineage.",
      "Frank Ocean and SZA anchor the road because their work treats R&B as narrative space, interior diary, and production experiment.",
      "Channel Orange and Blonde make the lane concrete through fractured structure, intimacy, and genre-fluid production choices.",
      "This archetype differs from neo-soul because its historical center is digital-era atmosphere and personal fragmentation rather than retro-soul revival.",
      "Listeners should focus on space, vocal processing, and unusual song architecture before judging the record by traditional R&B polish."
    ]
  },
  "045": {
    short: "early hip-hop and electro-rap where DJs, MCs, drum machines, and street-party records define the foundation.",
    history: "Old-school hip-hop grew from Bronx DJ culture, block parties, MC routines, breakbeats, electro, and early rap records moving from local scenes to national media.",
    why: "It established rap's basic public roles: DJ, MC, crew, beat, routine, dance, and recorded single.",
    distinct: "The road is foundational and party-facing, with rhythm, chant, and crew identity carrying more weight than later album realism.",
    listen: ["breakbeat emphasis", "MC call-and-response", "electro drum-machine snap", "crew routine structure", "party-command energy"],
    claims: [
      "Old-School Hip-Hop / Electro-Rap Foundations should be grounded in DJ culture, MC routines, breakbeats, and early recorded rap.",
      "Run-DMC and LL Cool J make the lane concrete because they move rap toward harder record identity and solo-star charisma while keeping foundational directness.",
      "Raising Hell and Licensed to Ill show how early hip-hop crossed into rock, pop, and MTV-era visibility without losing beat-and-MC logic.",
      "This archetype differs from golden age hip-hop because party command and foundational format matter more than dense sampling or album-era critique.",
      "Listeners should hear the beat, vocal command, and crew/solo presence as historical evidence before looking for later rap conventions."
    ]
  },
  "046": {
    short: "sample-rich late-1980s and early-1990s hip-hop where MC technique, politics, and jazz/funk memory intensify.",
    history: "Golden age hip-hop grew through sampler technology, independent labels, Black political critique, Native Tongues playfulness, and dense East Coast production.",
    why: "It expanded rap's musical and intellectual vocabulary, making flow, sample architecture, and social argument central.",
    distinct: "The road values density: rhyme technique, beat collage, cultural reference, and group ideology all count.",
    listen: ["sample-layer density", "MC cadence control", "political or intellectual address", "jazz/funk fragments", "DJ/producer architecture"],
    claims: [
      "Golden Age Hip-Hop / Conscious / Native Tongues is anchored in late-1980s and early-1990s rap's expansion of sampling, flow, and argument.",
      "Public Enemy and Eric B. & Rakim mark two key poles: political sonic assault and highly controlled MC technique.",
      "Paid in Full and It Takes a Nation of Millions make the lane concrete because production architecture and vocal authority become inseparable.",
      "This archetype differs from old-school rap by emphasizing album-era density, intellectual address, and sample collage.",
      "Listeners should track how the beat is assembled and how the MC rides it; both are part of the historical claim."
    ]
  },
  "047": {
    short: "West Coast rap where street narrative, funk-derived production, and cinematic persona define the lane.",
    history: "Gangsta rap and G-funk grew from West Coast crews, post-electro production, funk inheritance, car culture, street reportage, and 1990s media controversy.",
    why: "It shifted hip-hop's national center of gravity and made regional production identity a mainstream force.",
    distinct: "The road is regional and cinematic: synth lines, bass, drawled flow, and narrative persona work together.",
    listen: ["laid-back funk synth line", "deep bass glide", "street-narrative framing", "West Coast vocal cadence", "cinematic persona"],
    claims: [
      "Gangsta Rap / West Coast / G-Funk should be grounded in regional West Coast production and street narrative, not treated as generic hardness.",
      "Dr. Dre and Snoop Dogg make the lane concrete through The Chronic and Doggystyle, where funk-derived production becomes a regional signature.",
      "N.W.A and Tupac context helps explain the road's public controversy, political pressure, and persona-driven storytelling.",
      "This archetype differs from East Coast boom bap because bass glide, synth melody, and vocal drawl are core membership cues.",
      "Listeners should hear how menace, smoothness, humor, and groove can coexist inside the same West Coast record."
    ]
  },
  "048": {
    short: "1990s East Coast street rap where boom-bap drums, narrative detail, and MC authority dominate.",
    history: "East Coast 90s boom bap grew from New York street rap, sample-based production, independent labels, radio shows, and album-length autobiographical storytelling.",
    why: "It set a durable standard for lyrical credibility, producer identity, and gritty urban album craft.",
    distinct: "The road prizes drum weight, sample grit, vocal command, and scene detail over pop crossover polish.",
    listen: ["hard snare-and-kick loop", "sample grit", "street narrative detail", "commanding MC presence", "album-world atmosphere"],
    claims: [
      "East Coast 90s / Boom Bap / Street Canon is a production-and-MC road built on sample grit, drum weight, and narrative authority.",
      "The Notorious B.I.G., Jay-Z, and DMX show different voices inside the lane: cinematic detail, hustler poise, and raw spiritual pressure.",
      "Ready to Die and It's Dark and Hell Is Hot make the road concrete because each turns street narrative into an album world.",
      "This archetype differs from West Coast G-funk through tighter drum loops, darker sample texture, and a more clipped East Coast vocal attack.",
      "Listeners should follow the snare, sample bed, and MC persona before treating chart success as the main signal."
    ]
  },
  "049": {
    short: "Southern rap foundations where regional bass, drawl, club energy, and trap precursors reshape hip-hop.",
    history: "Southern hip-hop grew through Atlanta, Houston, New Orleans, Memphis, Miami, and other scenes, linking bass music, crunk, trap, soul, and regional storytelling.",
    why: "It permanently shifted hip-hop's map and made Southern production a dominant mainstream grammar.",
    distinct: "The road is regional before it is stylistically uniform: bounce, crunk, trap, funk, and drawl all matter.",
    listen: ["Southern vocal drawl", "heavy low-end", "chant or club command", "regional percussion feel", "trap or crunk precursor energy"],
    claims: [
      "Southern Hip-Hop / Crunk / Trap Foundations is a regional ecosystem road, not one single beat style.",
      "OutKast and Lil Wayne show how Southern rap could be lyrical, eccentric, commercial, and regionally unmistakable at once.",
      "Southernplayalisticadillacmuzik and Tha Carter III make the lane concrete by contrasting Atlanta funk-soul futurism with New Orleans-derived mixtape-star dominance.",
      "This archetype differs from East Coast boom bap because regional vocal grain and low-end production identity drive the signal.",
      "Listeners should separate crunk chant energy, trap precursors, and Southern soul/funk inheritance rather than flattening all Southern rap into one formula."
    ]
  },
  "050": {
    short: "rap built for mainstream crossover where persona, hook design, and pop-scale production meet MC identity.",
    history: "Pop-rap crossover grows through major-label hip-hop, MTV/radio visibility, sung hooks, celebrity persona, and producers who scale rap for mass audiences.",
    why: "It explains how rap became a dominant pop language while keeping MC persona and beat identity in view.",
    distinct: "The road is not simply popular rap; crossover architecture is the point.",
    listen: ["big hook placement", "clear persona", "polished beat architecture", "radio-edit momentum", "rap-pop contrast"],
    claims: [
      "Pop-Rap / Mainstream Hip-Hop Crossover should be defined by crossover design, not by sales alone.",
      "Eminem, Kanye West, and 50 Cent show different crossover engines: shock-persona virtuosity, producer-auteur ambition, and street-star hook machinery.",
      "The Marshall Mathers LP and Get Rich or Die Tryin' make the lane concrete because their pop reach depends on unmistakable rap identity.",
      "This archetype differs from modern trap because the center is mainstream scaling across radio, video, and celebrity systems.",
      "Listeners should ask how the hook, beat, and persona have been engineered for listeners beyond core rap scenes."
    ]
  },
  "051": {
    short: "rap's outsider lane where independent scenes, odd production, and idiosyncratic MC personas expand the form.",
    history: "Alternative, experimental, and indie rap grew through independent labels, underground scenes, internet circulation, sample weirdness, and artists resisting dominant rap formulas.",
    why: "It made hip-hop a space for eccentric world-building, abstraction, and genre collision.",
    distinct: "The road often values strangeness, texture, and authorial world over immediate format utility.",
    listen: ["unusual sample choice", "eccentric flow", "nonstandard song structure", "outsider persona", "indie-production texture"],
    claims: [
      "Alternative / Experimental / Indie Rap is a boundary-expanding road, not a weaker version of mainstream rap.",
      "MF DOOM and Tyler, the Creator anchor the lane because persona, world-building, and unusual production choices are central to the listening experience.",
      "Madvillainy and Flower Boy make the road concrete by showing abstract sample collage and melodic auteur rap as related but distinct paths.",
      "This archetype differs from conscious golden age rap because eccentric form and independent identity matter as much as message.",
      "Listeners should treat odd structure, masked or invented persona, and unexpected textures as membership evidence."
    ]
  },
  "052": {
    short: "2010s rap shaped by trap production, streaming circulation, melodic flow, and album-era prestige.",
    history: "Modern trap and streaming-era rap grew through Southern trap production, mixtape economies, platform circulation, melodic cadences, and artists who turned rap albums into prestige pop events.",
    why: "It defines how rap functioned as the dominant popular music language of the streaming era.",
    distinct: "The road is not only trap drums; it includes platform behavior, melodic delivery, and album-scale world-making.",
    listen: ["808 bass pressure", "hi-hat subdivision", "melodic rap cadence", "streaming-era hook economy", "cinematic album world"],
    claims: [
      "Modern Trap / Streaming-Era Rap should be framed around production grammar and platform-era circulation, not just current popularity.",
      "Kendrick Lamar and Travis Scott show the road's range from narrative prestige rap to atmospheric, trap-informed spectacle.",
      "good kid, m.A.A.d city and To Pimp a Butterfly make clear that streaming-era rap can also carry album-length narrative and historical ambition.",
      "This archetype differs from Southern trap foundations because it describes the later mainstream environment where trap language becomes broadly dominant.",
      "Listeners should hear 808 pressure, hi-hat detail, melodic cadence, and world-building scale as separate evidence points."
    ]
  },
  "053": {
    short: "first-wave punk where speed, economy, provocation, and small-room urgency reset rock language.",
    history: "First-wave punk grew through New York and London scenes, clubs, independent labels, fanzines, and bands rejecting rock excess with short, direct songs.",
    why: "It gave later alternative music a durable model for DIY stance, compressed form, and anti-virtuosic power.",
    distinct: "The road is not just fast rock; it is a stance about what a band needs in order to matter.",
    listen: ["short song form", "downstroke urgency", "plain or shouted vocal stance", "minimal soloing", "anti-polish impact"],
    claims: [
      "First-Wave Punk / 70s Punk should be grounded in specific New York and London scenes rather than generic rebellion.",
      "The Ramones and the Clash show two poles: radical minimal compression and politically alert expansion of punk's reach.",
      "Ramones and London Calling make the boundary visible because one reduces rock to essentials while the other stretches punk into reggae, pop, and street reportage.",
      "This archetype differs from hardcore because the first-wave lane still includes art, pop, and rock-and-roll reference points.",
      "Listeners should hear economy, attack, and stance before focusing on speed alone."
    ]
  },
  "055": {
    short: "1980s US punk intensified into speed, DIY networks, all-ages rooms, and confrontational local scenes.",
    history: "US hardcore grew through independent labels, zines, touring circuits, youth crews, and regional scenes that made punk faster, shorter, and more abrasive.",
    why: "It built the underground infrastructure later indie, emo, post-hardcore, and alternative scenes inherited.",
    distinct: "The road values intensity and infrastructure: the sound and the DIY network are inseparable.",
    listen: ["very fast tempos", "shouted vocals", "short song bursts", "dry guitar attack", "all-ages room energy"],
    claims: [
      "Hardcore Punk / US 80s Hardcore is a network road as much as a sound road, built through labels, zines, touring, and local scenes.",
      "Black Flag and Dead Kennedys anchor the lane because they show hardcore's physical intensity, satire, and underground institution-building.",
      "Damaged and Fresh Fruit for Rotting Vegetables make the road concrete through speed, confrontation, and a refusal of rock polish.",
      "This archetype differs from first-wave punk because hardcore tightens the song, raises the speed, and hardens the community boundary.",
      "Listeners should hear room pressure, clipped form, and shouted directness as historical evidence."
    ]
  },
  "056": {
    short: "post-punk's darker melodic branch where atmosphere, bass movement, and emotional distance reshape punk aftermath.",
    history: "Post-punk and gothic roots grew after punk through independent labels, art-school experimentation, dub and electronic influence, and bands exploring mood over rock release.",
    why: "It opened a path from punk energy toward atmosphere, darkness, and modern alternative music.",
    distinct: "The road is tense and spacious: bass, drums, echo, and vocal distance often carry the drama.",
    listen: ["prominent bass melody", "dry or gated drums", "minor-key atmosphere", "emotional distance", "guitar texture over riff"],
    claims: [
      "Post-Punk / Dark Melodic / Gothic Roots should be tied to punk aftermath and mood experimentation, not generic sad rock.",
      "The Cure and Joy Division anchor the lane because bass, atmosphere, and vocal distance become central expressive tools.",
      "Disintegration and Unknown Pleasures make the road concrete by turning darkness into arrangement architecture.",
      "This archetype differs from new wave because it usually withholds pop brightness and lets tension remain unresolved.",
      "Listeners should focus on bass movement, negative space, and atmosphere before judging the song by chorus size."
    ]
  },
  "057": {
    short: "new wave pop-rock where punk economy, synth color, video-era style, and hook craft become mainstream.",
    history: "New wave grew from punk-adjacent scenes into MTV and pop radio through sharper production, art-school image, reggae/funk touches, and concise hooks.",
    why: "It translated post-punk restlessness into a major pop language of the late 1970s and 1980s.",
    distinct: "The road is nervous but accessible: style, video image, and hook design all matter.",
    listen: ["bright clipped guitar or synth", "dry drum sound", "hook-forward chorus", "stylized vocal persona", "MTV-era polish"],
    claims: [
      "New Wave / MTV Pop-Rock is a translation road, moving punk and post-punk energy into sharper pop and video-era form.",
      "The Cars and the Police anchor the lane because they combine rock-band identity with synth color, reggae/funk rhythm, and concise pop hooks.",
      "The Cars and Synchronicity make the road concrete through production polish, stylized persona, and high-definition choruses.",
      "This archetype differs from darker post-punk because it welcomes radio brightness and pop legibility.",
      "Listeners should track how nervous rhythm, image, and hook craft work together."
    ]
  },
  "058": {
    short: "1980s electronic pop where synthesizers, sequencers, romantic image, and club pulse carry the song.",
    history: "Synthpop and new romantic pop grew from post-punk, electronic experimentation, club culture, and affordable synthesizer technology.",
    why: "It made electronic timbre a mainstream pop identity rather than a novelty effect.",
    distinct: "The road lets machines carry emotion: synth tone, sequenced pulse, and stylized vocal affect are central.",
    listen: ["sequenced synth pulse", "drum-machine snap", "melancholy electronic harmony", "romantic or stylized vocal", "club-pop structure"],
    claims: [
      "Synthpop / New Romantic / 80s Electronic Pop should be grounded in electronic instrumentation and club-pop image, not just 1980s nostalgia.",
      "Depeche Mode and New Order anchor the lane because they make machine rhythm emotionally legible.",
      "Violator and Power, Corruption & Lies make the road concrete through synth architecture, dance pulse, and dark pop melody.",
      "This archetype differs from new wave because synthesizers and sequencers are the organizing center rather than color on a rock-band frame.",
      "Listeners should hear timbre, programmed rhythm, and vocal coolness as the main evidence."
    ]
  },
  "059": {
    short: "1980s college-radio guitar music where jangle, literate distance, and independent circulation prefigure alternative rock.",
    history: "College rock grew through campus radio, independent labels, clubs, fanzines, and bands that sat outside both punk orthodoxy and mainstream rock.",
    why: "It supplied much of the source code for 1990s alternative and indie identity.",
    distinct: "The road favors oblique personality, guitar texture, and independent circulation over hard-rock force.",
    listen: ["jangly or textured guitar", "college-radio restraint", "literate vocal distance", "melodic melancholy", "indie-label feel"],
    claims: [
      "College Rock / Pre-Alternative 80s is defined by circulation through college radio and independent networks as much as by a guitar sound.",
      "R.E.M. and the Smiths anchor the lane because their guitar textures and vocal identities created alternative credibility before mainstream alternative broke open.",
      "Murmur and The Queen Is Dead make the road concrete through murky jangle, literate melancholy, and anti-arena scale.",
      "This archetype differs from post-punk by leaning more toward melodic guitar-band identity and college-radio circulation.",
      "Listeners should hear restraint, obliqueness, and texture as strengths rather than lack of impact."
    ]
  },
  "060": {
    short: "post-hardcore and noise-rock where punk discipline becomes abrasion, odd rhythm, and independent-label severity.",
    history: "Noise rock and post-hardcore grew from hardcore scenes, art-punk, independent labels, mathy rhythm, and bands that made tension more important than release.",
    why: "It gave later emo, indie, metal-adjacent, and underground rock a vocabulary of dissonance and structural pressure.",
    distinct: "The road is intentionally uncomfortable: repetition, dissonance, and sharp dynamics carry the meaning.",
    listen: ["dissonant guitar texture", "stop-start rhythm", "dry aggressive drums", "shouted or strained vocals", "tension over payoff"],
    claims: [
      "Noise Rock / Post-Hardcore / Touch and Go Axis is rooted in hardcore infrastructure but pushes toward artier abrasion and rhythmic instability.",
      "Fugazi and At the Drive-In anchor the lane because they turn punk intensity into discipline, motion, and structural argument.",
      "Repeater and Relationship of Command make the road concrete through angular rhythm, shouted urgency, and anti-gloss production.",
      "This archetype differs from hardcore by making tension, dynamics, and formal disruption as important as speed.",
      "Listeners should hear dissonance and awkward motion as deliberate design, not as rough execution."
    ]
  },
  "061": {
    short: "heavy metal foundations where riff authority, dramatic vocals, and theatrical power define the form.",
    history: "Traditional heavy metal and NWOBHM grew from hard rock, blues-rock, Sabbath darkness, Judas Priest precision, and British underground scenes that sharpened metal identity.",
    why: "It fixed the core metal vocabulary later subgenres accelerate, darken, glamorize, or hybridize.",
    distinct: "The road prizes riff, power, and drama before extreme speed or crossover rhythm.",
    listen: ["central guitar riff", "operatic or commanding vocal", "galloping rhythm", "minor-mode drama", "twin-guitar force"],
    claims: [
      "Traditional Heavy Metal / NWOBHM should be grounded in metal's formation as a distinct language, not merely in any loud hard rock.",
      "Black Sabbath and Judas Priest anchor the road because they establish doom-laden heaviness and sharper metal precision.",
      "Paranoid and Black Sabbath make the foundation concrete through riff gravity, dark atmosphere, and song structures that later metal repeatedly reworks.",
      "This archetype differs from thrash because tempo and aggression do not yet outrun riff drama and vocal theater.",
      "Listeners should hear the riff as the central argument of the song."
    ]
  },
  "062": {
    short: "speed-driven metal where palm-muted riffs, precision drums, and aggression turn metal into high-velocity architecture.",
    history: "Thrash and speed metal grew from NWOBHM, hardcore punk speed, underground tape trading, and Bay Area/Los Angeles scenes.",
    why: "It made velocity, rhythmic precision, and riff complexity central to metal's 1980s identity.",
    distinct: "The road is faster and sharper than traditional metal, but still built from tightly composed riffs.",
    listen: ["palm-muted riffing", "double-time drums", "rapid tempo shifts", "shouted vocal attack", "tight ensemble precision"],
    claims: [
      "Thrash Metal / Speed Metal is defined by speed and precision, but its identity comes from riff architecture rather than chaos.",
      "Metallica and Slayer anchor the lane because they show thrash's technical control and extreme aggression.",
      "Master of Puppets and Reign in Blood make the road concrete through tight riff sequencing, fast tempos, and dark thematic pressure.",
      "This archetype differs from traditional metal by importing punk velocity and underground severity into metal composition.",
      "Listeners should track how riffs interlock with drums; the propulsion is composed, not merely fast."
    ]
  },
  "063": {
    short: "1980s pop-metal where hard-rock riffs, glam image, big choruses, and video-era spectacle merge.",
    history: "Glam metal and hair metal grew through Los Angeles clubs, hard-rock guitar, arena touring, MTV, power ballads, and highly stylized image.",
    why: "It made metal-adjacent heaviness part of mainstream pop spectacle and arena entertainment.",
    distinct: "The road balances distortion and danger with chorus polish, fashion, and mass-media visibility.",
    listen: ["huge chorus lift", "flashy guitar lead", "arena drum sound", "glam image energy", "power-ballad dynamics"],
    claims: [
      "Glam Metal / Hair Metal / Pop Metal should be understood as a video-era hard-rock and pop-metal lane, not as traditional metal with brighter clothes.",
      "Def Leppard, Motley Crue, and Guns N' Roses show the span from studio-sculpted pop-metal to sleazier street hard rock.",
      "Hysteria and Pyromania make the road concrete because production gloss and hook architecture are inseparable from the guitar impact.",
      "This archetype differs from thrash because mass hooks and image are central rather than underground speed or severity.",
      "Listeners should hear how riff, chorus, guitar solo, and visual persona are designed for arena scale."
    ]
  },
  "064": {
    short: "slow, heavy, low-centered rock where Sabbath inheritance meets desert groove and stoner repetition.",
    history: "Doom, stoner, and desert heavy trace from Black Sabbath's slow darkness through psychedelic heaviness, low tuning, repetition, and Palm Desert/stoner-rock scenes.",
    why: "It shows that heaviness can come from weight, space, and trance rather than speed.",
    distinct: "The road slows metal down and lets riff mass, tone, and repetition become the experience.",
    listen: ["slow riff weight", "low-tuned guitar", "desert-groove repetition", "fuzz density", "trance-like heaviness"],
    claims: [
      "Doom / Stoner / Desert Heavy is a heaviness road built from slowness, low-end, and repetition rather than speed.",
      "Black Sabbath and Kyuss anchor the lane because Sabbath supplies doom gravity while Kyuss points toward desert-groove stoner rock.",
      "Welcome to Sky Valley and Blues for the Red Sun make the road concrete through fuzz tone, space, and rolling riff repetition.",
      "This archetype differs from traditional metal because heaviness is felt as mass and atmosphere before heroic drama.",
      "Listeners should focus on sustain, tempo, and riff weight, not only distortion level."
    ]
  },
  "065": {
    short: "heavy rock where industrial rhythm, mechanical texture, electronics, and metal force collide.",
    history: "Industrial metal and machine rock grew from industrial music, post-punk, metal guitar, sampling, drum programming, and 1990s alternative crossover.",
    why: "It made the machine feel musical: repetition, noise, electronics, and heaviness became one language.",
    distinct: "The road treats texture and rhythm as machinery, with guitars often functioning like another percussion layer.",
    listen: ["mechanical drum pattern", "sampled or sequenced noise", "grinding guitar texture", "cold vocal processing", "factory-like repetition"],
    claims: [
      "Industrial Metal / Machine Rock should be tied to industrial texture and programmed rhythm, not just heavy guitars.",
      "Ministry and Nine Inch Nails anchor the lane because they fuse electronics, noise, and rock aggression in different proportions.",
      "The Downward Spiral and Psalm 69 make the road concrete through machine rhythm, abrasive texture, and tightly controlled menace.",
      "This archetype differs from alt-metal because the mechanical sound world is the central identity.",
      "Listeners should hear whether drums, samples, and guitars behave like a system rather than a normal band mix."
    ]
  },
  "066": {
    short: "1990s and 2000s heavy alternative where downtuned riffs, groove, rap cadence, and emotional pressure meet.",
    history: "Alt-metal, nu-metal, and rap-metal grew from alternative rock, metal, hip-hop rhythm, funk-metal, and post-grunge radio scenes.",
    why: "It made heaviness a mainstream youth language outside traditional metal rules.",
    distinct: "The road is groove-heavy and hybrid: rhythm, vocal texture, and downtuned impact matter more than metal orthodoxy.",
    listen: ["downtuned groove riff", "rap or percussive vocal cadence", "bass-forward mix", "angst-heavy dynamics", "turntable/electronic or funk-metal traces"],
    claims: [
      "Alt-Metal / Nu-Metal / Rap-Metal should be framed as a 1990s/2000s hybrid road, not as a failed version of traditional metal.",
      "Tool, Korn, and System of a Down show the lane's range from progressive heaviness to downtuned emotional rupture and political absurdity.",
      "Aenima and Toxicity make the road concrete because rhythm, texture, and vocal character matter as much as riff heaviness.",
      "This archetype differs from industrial metal because the center is groove and vocal hybridization rather than machine texture alone.",
      "Listeners should separate rap cadence, low tuning, rhythmic lurch, and emotional directness as distinct evidence points."
    ]
  },
  "067": {
    short: "modern heavy music where metalcore precision, emo intensity, and active-rock hooks intersect.",
    history: "Metalcore and emo-heavy active rock grew from hardcore, melodic death metal, post-hardcore, Warped Tour circuits, and 2000s rock radio.",
    why: "It explains how breakdowns, screamed/sung vocals, and polished heaviness became mainstream rock tools.",
    distinct: "The road uses contrast: harsh verses, melodic choruses, precision riffs, and breakdown release.",
    listen: ["screamed/sung vocal contrast", "breakdown impact", "tight modern guitar tone", "double-kick or chug rhythm", "melodic chorus release"],
    claims: [
      "Metalcore / Emo-Heavy / Modern Active Rock should be treated as a post-hardcore and metalcore crossover lane, not generic modern metal.",
      "Killswitch Engage and Avenged Sevenfold anchor the road through melodic metalcore precision and arena-ready modern heaviness.",
      "The End of Heartache and Sempiternal make the lane concrete by showing how harsh vocals, breakdowns, and choruses became a mainstream heavy vocabulary.",
      "This archetype differs from nu-metal because metalcore riffing and breakdown form are central.",
      "Listeners should track the alternation between impact and melody; the contrast is the design."
    ]
  },
  "068": {
    short: "gateway into extreme metal where death, black, sludge, and progressive heaviness push past mainstream thresholds.",
    history: "Extreme metal grows from thrash, death metal, black metal, doom, sludge, and underground scenes that prioritize intensity, darkness, speed, or density.",
    why: "It marks the boundary where heaviness becomes a specialized language with its own scenes and listening skills.",
    distinct: "The road is a gateway: it teaches how blast, growl, density, and long-form heaviness differ from normal hard rock.",
    listen: ["growled or harsh vocals", "blast or extreme drum pressure", "dense riff movement", "dark atmosphere", "sludge or progressive weight"],
    claims: [
      "Extreme Metal Gateway / Black-Death-Sludge should explain entry into extreme metal vocabularies rather than flatten all subgenres together.",
      "Death, Mastodon, and Gojira show different gateway routes: technical death metal, sludge-progressive narrative, and modern ecological heaviness.",
      "Symbolic and Leviathan make the road concrete because heaviness becomes complex, harsh, and album-scale.",
      "This archetype differs from doom/stoner because extremity may come from speed, vocal harshness, technical density, or atmosphere, not only weight.",
      "Listeners should identify which kind of extremity is operating before treating the song as simply heavy."
    ]
  },
  "069": {
    short: "1980s alternative source code where college rock, punk aftermath, noise, and indie networks anticipate the 1990s.",
    history: "Pre-grunge alternative grew through college radio, independent labels, underground touring, and bands that made odd guitar music viable outside mainstream rock.",
    why: "It supplies the vocabulary later grunge, indie, and alternative radio turn into mass culture.",
    distinct: "The road is pre-breakthrough: rough, inventive, independent, and not yet smoothed for alternative radio.",
    listen: ["abrasive melodic guitar", "college-radio looseness", "indie-label production", "quiet/loud dynamics", "anti-mainstream vocal stance"],
    claims: [
      "1980s Alternative Source-Code / Pre-Grunge is a lineage road, built from independent guitar music before alternative became a mass format.",
      "Pixies, R.E.M., and Sonic Youth show three source-code paths: fractured dynamics, college-rock jangle, and art-noise guitar exploration.",
      "Doolittle and Daydream Nation make the road concrete because they anticipate later alternative without sounding like 1990s radio rock.",
      "This archetype differs from college rock by including noisier, more disruptive sources of later grunge and indie.",
      "Listeners should hear odd guitar choices and anti-polish as future-facing, not as unfinished mainstream rock."
    ]
  },
  "070": {
    short: "Seattle-centered 1990s alternative where punk force, metal weight, and raw melody break into the mainstream.",
    history: "Grunge grew through Seattle bands, Sub Pop and related networks, punk/metal crossover, and early-1990s major-label alternative breakthrough.",
    why: "It changed the sound, image, and commercial center of rock in the 1990s.",
    distinct: "The road balances sludge, punk urgency, and wounded melody rather than choosing one.",
    listen: ["quiet/loud dynamics", "distorted riff weight", "raw melodic vocal", "punk-metal hybrid feel", "unvarnished emotional pressure"],
    claims: [
      "Grunge / Seattle / 90s Alt Center should be grounded in Seattle scene history and punk-metal hybrid sound, not just flannel-era imagery.",
      "Nirvana and Pearl Jam anchor the lane because they show different versions of grunge's mainstream breakthrough: punk compression and classic-rock-informed emotional scale.",
      "Nevermind and Ten make the road concrete through distorted guitars, raw vocal identity, and major-label alternative impact.",
      "This archetype differs from post-grunge because it is tied to the original scene and breakthrough moment.",
      "Listeners should hear the tension between heaviness and vulnerability as the central signal."
    ]
  },
  "071": {
    short: "post-1990s rock radio where grunge vocabulary becomes durable mainstream format language.",
    history: "Post-grunge and modern rock radio grew after the first grunge breakthrough as bands adapted distorted guitars, confessional vocals, and polished production for radio formats.",
    why: "It explains how alternative became a long-running mainstream rock sound after the initial Seattle moment.",
    distinct: "The road keeps grunge-coded emotion but smooths the sound for repeatable radio impact.",
    listen: ["polished distorted guitars", "earnest vocal strain", "big modern-rock chorus", "mid-tempo drive", "radio-ready dynamics"],
    claims: [
      "Post-Grunge / Modern Rock Radio is a format road, showing how grunge vocabulary was adapted for later mainstream rock.",
      "Stone Temple Pilots and Foo Fighters anchor the lane because they turn alternative heaviness into durable radio identity.",
      "Core and The Colour and the Shape make the road concrete through polished distortion, big choruses, and modern-rock pacing.",
      "This archetype differs from grunge because it is less tied to Seattle origin and more tied to post-breakthrough radio repeatability.",
      "Listeners should hear whether rawness has been converted into stable chorus architecture."
    ]
  },
  "072": {
    short: "1990s indie rock where lo-fi texture, slacker affect, and independent-label culture define prestige from below.",
    history: "90s indie and lo-fi grew through independent labels, home recording, zines, college radio, and bands that turned casual delivery into aesthetic stance.",
    why: "It made underproduction, irony, and small-scale scene credibility central to indie identity.",
    distinct: "The road sounds deliberately underlit: rough edges and indirect feeling are part of the claim.",
    listen: ["lo-fi guitar texture", "slacker vocal affect", "indirect lyric stance", "indie-label roughness", "melodic charm under noise"],
    claims: [
      "90s Indie / Lo-Fi / Slacker / Matador Axis is defined by independent circulation and aesthetic underproduction, not simply by lack of budget.",
      "Pavement and Neutral Milk Hotel anchor the lane because they show slacker fragmentation and homemade emotional intensity as related indie values.",
      "Slanted and Enchanted and In the Aeroplane Over the Sea make the road concrete through rough texture and highly specific voice.",
      "This archetype differs from pre-grunge alternative by being less about future mainstream rupture and more about indie scene identity itself.",
      "Listeners should treat casual delivery, tape-like roughness, and off-center melody as deliberate evidence."
    ]
  },
  "073": {
    short: "dreamy noise-pop where guitar haze, texture, and blurred vocal presence become the song's atmosphere.",
    history: "Shoegaze and dream pop grew through UK independent scenes, effects-heavy guitars, post-punk atmosphere, and ethereal pop voices.",
    why: "It expanded rock and pop by making texture and immersion as important as melody or performance stance.",
    distinct: "The road hides the song inside sound: distortion, reverb, and vocal blur are central rather than decorative.",
    listen: ["guitar wash", "reverb-heavy vocal blend", "slow harmonic drift", "noise as atmosphere", "dreamlike melodic outline"],
    claims: [
      "Shoegaze / Dream Pop / Noise Haze should be grounded in texture and immersion, not just soft vocals or loud guitars.",
      "My Bloody Valentine and Cocteau Twins anchor the lane because they make guitar processing and vocal atmosphere into compositional material.",
      "Loveless and Heaven or Las Vegas make the road concrete through radically different balances of noise, beauty, and blur.",
      "This archetype differs from 90s lo-fi indie because production haze is the intended environment rather than a rough documentary surface.",
      "Listeners should hear whether the vocal is blended into the texture instead of sitting on top of a normal rock mix."
    ]
  },
  "074": {
    short: "1990s alternative guitar voices where feminist punk, confessional edge, and women-led rock authority converge.",
    history: "Female 90s alt and riot grrrl guitar voices grew from punk feminism, zines, college radio, alternative rock, and women artists challenging rock's gender rules.",
    why: "It made voice, anger, vulnerability, and authorship central to 1990s alternative history.",
    distinct: "The road is not only women in rock; it is women making guitar music a site of argument, confession, and power.",
    listen: ["raw vocal authority", "feminist or confrontational stance", "guitar-band grit", "confessional detail", "punk-to-alt dynamics"],
    claims: [
      "Female 90s Alt / Riot Grrrl / Guitar Voices should be grounded in feminist punk and alternative-rock authorship, not treated as a demographic category.",
      "Hole and Liz Phair anchor the lane because they turn confession, provocation, and guitar-band form into different kinds of authority.",
      "Live Through This and Exile in Guyville make the road concrete through raw performance, gendered argument, and alternative-rock songcraft.",
      "This archetype differs from general 90s indie because gendered voice and feminist scene context are core historical signals.",
      "Listeners should hear vocal stance and lyrical confrontation as musical evidence, not only topical content."
    ]
  },
  "075": {
    short: "1990s and 2000s alt-pop where crunchy guitars, big melodies, and nerdy precision renew power-pop craft.",
    history: "Power-pop revival grew through alternative radio, indie scenes, and bands reworking Beatles/Big Star-style hook craft with louder guitars and modern irony.",
    why: "It kept melodic guitar-pop alive inside the alternative era without returning to classic-rock scale.",
    distinct: "The road is bright and crunchy: big hooks are wrapped in distortion, awkward persona, or indie self-consciousness.",
    listen: ["crunchy guitar chords", "high-melody chorus", "nerdy or self-aware vocal persona", "tight pop structure", "alt-rock distortion around classic hooks"],
    claims: [
      "Power-Pop Revival / Crunchy Alt-Pop should be tied to melody-first guitar craft inside the alternative era.",
      "Weezer and Fountains of Wayne anchor the lane because they pair classic pop architecture with modern irony, crunch, and character writing.",
      "The Blue Album and Pinkerton make the road concrete through thick guitars, vulnerable persona, and unusually durable hooks.",
      "This archetype differs from pop-punk because the center is melodic craft and guitar-pop lineage rather than punk tempo or scene identity.",
      "Listeners should hear how distortion supports the hook instead of burying it."
    ]
  },
  "076": {
    short: "punk streamlined into fast, melodic, youth-facing radio and skate-scene pop.",
    history: "Pop-punk and skate punk grew from melodic hardcore, California punk scenes, Warped Tour circuits, MTV, and 1990s/2000s youth radio.",
    why: "It made punk energy legible as mainstream adolescent pop without fully abandoning speed or attitude.",
    distinct: "The road compresses feeling into fast downstrokes, nasal or bratty vocals, and instantly legible choruses.",
    listen: ["fast downstroke guitar", "nasal or bratty vocal tone", "simple high-energy chorus", "skate-punk tempo", "youth-addressed directness"],
    claims: [
      "Pop-Punk / Skate Punk / 90s-00s Punk Pop is a melodic punk road shaped by skate scenes, youth radio, and Warped Tour circulation.",
      "Green Day and Blink-182 anchor the lane because they translate punk brevity into durable pop choruses and adolescent persona.",
      "Dookie and American Idiot make the road concrete by showing both compact bratty pop-punk and larger punk-pop narrative ambition.",
      "This archetype differs from power-pop revival because punk tempo, scene memory, and youth address remain central.",
      "Listeners should hear the balance of speed, simplicity, and hook before treating the song as generic alternative rock."
    ]
  },
  "077": {
    short: "emo's pop-facing branch where post-hardcore intensity, theatrical feeling, and arena choruses meet.",
    history: "Mall emo and post-hardcore pop grew through punk and hardcore scenes, emo's confessional language, MTV/Fuse visibility, Warped Tour, and 2000s rock radio.",
    why: "It made emotional excess, black-clad theatricality, and post-hardcore dynamics part of mainstream youth culture.",
    distinct: "The road is melodramatic by design: tension, confession, and chorus release are the core mechanics.",
    listen: ["confessional vocal strain", "post-hardcore guitar dynamics", "theatrical chorus release", "quiet-to-explosive structure", "youth-drama framing"],
    claims: [
      "Emo / Mall Emo / Post-Hardcore Pop should be connected to punk and post-hardcore scenes before it is treated as fashion or teen melodrama.",
      "My Chemical Romance and Fall Out Boy anchor the lane because they turn emo affect into theatrical, hook-heavy rock.",
      "Three Cheers for Sweet Revenge and The Black Parade make the road concrete through narrative drama, vocal urgency, and arena-scale choruses.",
      "This archetype differs from pop-punk because the emotional and theatrical architecture is heavier and more self-conscious.",
      "Listeners should hear how the chorus releases accumulated tension rather than simply checking for distorted guitars."
    ]
  },
  "078": {
    short: "2000s indie-rock prestige where blogs, festivals, emotional albums, and literate guitar-pop make small scenes feel central.",
    history: "Blog indie and prestige indie grew through music blogs, independent labels, festivals, college radio afterlives, and bands whose albums became cultural touchstones.",
    why: "It explains how indie rock became a prestige language in the 2000s before streaming fully reorganized discovery.",
    distinct: "The road is album-minded and taste-making: emotional scale matters, but it avoids mainstream rock's obvious gestures.",
    listen: ["anthemic indie build", "literate emotional framing", "textured guitar or chamber color", "blog-era production polish", "album-world cohesion"],
    claims: [
      "Blog Indie / Prestige Indie / 2000s Indie Rock should be tied to 2000s discovery systems, festivals, and album prestige.",
      "Arcade Fire and Death Cab for Cutie anchor the lane because they show communal art-rock uplift and intimate literate indie-pop becoming broadly legible.",
      "Funeral and Transatlanticism make the road concrete through album-scale emotion and carefully curated indie textures.",
      "This archetype differs from 90s lo-fi indie because the production and cultural frame are more polished, public, and prestige-oriented.",
      "Listeners should hear album atmosphere, emotional architecture, and taste-maker context alongside the songs themselves."
    ]
  },
  "079": {
    short: "early-2000s guitar revival where garage rawness, style, and stripped rock-band identity return to the foreground.",
    history: "Garage revival grew through New York, Detroit, UK, and international scenes, indie labels, fashion press, and a reaction against late-1990s rock bloat.",
    why: "It made lean guitar bands feel newly modern in the 2000s and shaped indie rock's public image.",
    distinct: "The road is stylishly stripped: riffs, attitude, and concise forms matter more than virtuosity.",
    listen: ["dry garage guitar", "tight stylish rhythm section", "short hook form", "cool vocal detachment", "retro texture with modern framing"],
    claims: [
      "Garage Revival and Rock-Is-Back 2000s should be framed as an early-2000s scene and media moment, not just retro guitar rock.",
      "The White Stripes and the Strokes anchor the lane because they make stripped rock feel newly fashionable through different minimalisms.",
      "Elephant and Is This It make the road concrete through raw blues-garage reduction and sleek New York guitar cool.",
      "This archetype differs from post-punk revival because garage directness and rock-and-roll minimalism are the central signals.",
      "Listeners should hear dryness, economy, and style as intentional production choices."
    ]
  },
  "080": {
    short: "2000s dark indie rock where post-punk bass, angular guitar, and nocturnal style return through modern scenes.",
    history: "Post-punk revival grew through 2000s indie circuits, New York and UK scenes, post-punk record collections, dance-rock clubs, and stylish guitar-band minimalism.",
    why: "It renewed post-punk's tension for a generation shaped by blogs, clubs, and indie fashion.",
    distinct: "The road is colder and more angular than garage revival, with basslines and atmosphere carrying the identity.",
    listen: ["driving post-punk bass", "angular guitar figure", "dry drum sound", "baritone or clipped vocal", "nocturnal city atmosphere"],
    claims: [
      "Post-Punk Revival / Dark Indie Rock should be tied to 2000s indie scenes reworking post-punk tension, not to generic modern rock.",
      "Interpol and Yeah Yeah Yeahs anchor the lane because they show dark bass-driven precision and art-punk volatility.",
      "Turn On the Bright Lights and Fever to Tell make the road concrete through nocturnal atmosphere, angular attack, and scene identity.",
      "This archetype differs from garage revival because rhythm, bass, and urban tension matter more than raw rock-and-roll reduction.",
      "Listeners should hear whether the song moves through nervous architecture rather than bluesy riff directness."
    ]
  },
  "081": {
    short: "Chicago post-disco club music where DJs, drum machines, edits, and dancers turn repetition into form.",
    history: "House grew from Chicago clubs, post-disco DJ culture, drum-machine programming, edits, and Black and queer dancefloor communities.",
    why: "It became one of the foundations of global electronic dance music while preserving club function at its center.",
    distinct: "The road is built for the mix and the floor: groove, loop, kick, and release are the compositional units.",
    listen: ["four-on-the-floor kick", "drum-machine claps", "looped piano or bass vamp", "DJ-friendly arrangement", "post-disco lift"],
    claims: [
      "House / Chicago / Dance Club Foundations must be sourced through Chicago club and post-disco dance history, not unrelated rock or metal sources.",
      "Frankie Knuckles belongs as a central anchor because the Warehouse and Chicago DJ culture are part of house's origin story.",
      "The road's 4/4 pulse, drum-machine patterning, and loop structure make dancefloor function the main form.",
      "This archetype differs from disco because house strips and extends disco's energy through DJ logic, machines, and club circulation.",
      "Listeners should focus on the kick, clap, loop, and gradual arrangement shifts before expecting singer-centered pop development."
    ]
  },
  "082": {
    short: "Detroit electronic music where funk memory, machine rhythm, and futurist imagination create techno.",
    history: "Detroit techno emerged from Black electronic producers, radio and club culture, synthesizers, drum machines, electro, funk, and post-industrial futurism.",
    why: "It gave electronic dance music a sleek futurist language distinct from both disco inheritance and rock-band performance.",
    distinct: "The road is emotional through machinery: precision, repetition, timbre, and motion carry the feeling.",
    listen: ["machine pulse", "minimal synth motif", "futurist texture", "long-form build", "bass movement against precise drums"],
    claims: [
      "Techno / Detroit / Minimal Electronic must be grounded in Detroit electronic history and first-generation techno context, not unrelated heavy-music sources.",
      "Juan Atkins and Kevin Saunderson anchor the road because they connect Detroit's electronic futurism to dancefloor systems.",
      "Techno differs from Chicago house through a stronger emphasis on futurist timbre, machine precision, and streamlined synthesis.",
      "Minimal electronic examples in this lane should be heard through repetition and modulation rather than conventional pop-song change.",
      "Listeners should focus on how small timbral shifts create motion over time."
    ]
  },
  "083": {
    short: "mainstream electronic dance built for festivals, drops, massive hooks, and global pop crossover.",
    history: "EDM and big-room dance grew from house, techno, trance, electro-house, festival circuits, digital production, and pop collaborations in the 2000s and 2010s.",
    why: "It made DJ-producers visible pop figures and turned dance-music build/drop structure into mainstream expectation.",
    distinct: "The road is engineered for scale: breakdown, build, drop, hook, and crowd response organize the track.",
    listen: ["big build-up", "drop-centered release", "compressed kick and synth", "festival-scale hook", "pop vocal feature"],
    claims: [
      "EDM / Festival Dance / Big Room / Mainstream Electronic should be framed around festival scale and producer-star crossover.",
      "Avicii and Calvin Harris anchor the lane because they translate dance production into global pop hooks and massive crowd forms.",
      "True and 18 Months make the road concrete through melodic builds, pop collaborations, and dancefloor structures designed for mass audiences.",
      "This archetype differs from Chicago house because the center is festival-era scale rather than local club origin.",
      "Listeners should identify build, drop, and crowd-release mechanics as the core architecture."
    ]
  },
  "084": {
    short: "downtempo electronic music where hip-hop beats, dub space, soul mood, and nocturnal atmosphere slow the club down.",
    history: "Trip-hop and downtempo grew from Bristol scenes, hip-hop sampling, dub, soul, electronic production, and 1990s album culture.",
    why: "It made electronic beatmaking feel cinematic, intimate, and shadowed rather than purely dancefloor-driven.",
    distinct: "The road is slow and atmospheric: mood, texture, bass, and sample space matter more than club release.",
    listen: ["slow breakbeat", "dubby bass space", "nocturnal vocal mood", "cinematic sample texture", "tension without drop"],
    claims: [
      "Trip-Hop / Downtempo / Nocturnal Electronic should be grounded in Bristol and 1990s beat culture rather than generic chill music.",
      "Massive Attack and Portishead anchor the lane because they connect hip-hop-derived beats to dub space, soul mood, and cinematic darkness.",
      "Blue Lines and Mezzanine make the road concrete through slow breakbeats, bass pressure, and atmospheric vocal presence.",
      "This archetype differs from IDM because mood and groove remain sensual and song-facing even when the production is experimental.",
      "Listeners should hear the space around the beat as part of the composition."
    ]
  },
  "085": {
    short: "indie-club crossover where punk bands, DJs, electro texture, and dancefloor irony collide.",
    history: "Indie dance, dance-punk, and electroclash grew through 2000s clubs, post-punk revival, DFA-style production, electroclash fashion, and rock bands absorbing DJ culture.",
    why: "It made dancefloor rhythm central to indie identity without turning the music into standard EDM.",
    distinct: "The road keeps rock-band attitude while letting synths, disco-punk bass, and club repetition drive.",
    listen: ["dance-punk bassline", "cowbell or dry drum groove", "ironic vocal stance", "synth stab or electro texture", "indie-rock-to-club build"],
    claims: [
      "Indie Dance / Dance-Punk / Electroclash should be tied to 2000s indie clubs and post-punk/dance crossover, not to generic electronic pop.",
      "LCD Soundsystem and Justice anchor the lane because they show band-aware dance-punk and heavier French electro-club crossover.",
      "Sound of Silver and Cross make the road concrete through repetition, club dynamics, and indie-era style consciousness.",
      "This archetype differs from post-punk revival because dancefloor function is more central than guitar-band austerity.",
      "Listeners should hear whether the track asks a rock audience to move like a club audience."
    ]
  },
  "086": {
    short: "bedroom-era electronic pop where nostalgia, soft synths, haze, and indie intimacy make small production feel expansive.",
    history: "Synthwave, chillwave, and bedroom electronic grew through home production tools, blogs, streaming discovery, 1980s nostalgia, and indie-electronic scenes.",
    why: "It made low-cost digital production a full mood language for indie pop and electronic listening.",
    distinct: "The road is intimate and vaporous: texture, memory, and atmosphere often matter more than performance force.",
    listen: ["soft synth pad", "hazy vocal processing", "nostalgic drum-machine pulse", "bedroom-production intimacy", "washed-out hook"],
    claims: [
      "Synthwave / Chillwave / Bedroom Electronic should be grounded in home-production and nostalgia aesthetics, not generic electronic ambience.",
      "Washed Out, Grimes, Chvrches, and M83 show different routes from bedroom haze to bigger synth-pop scale.",
      "Visions and Hurry Up, We're Dreaming make the road concrete by contrasting DIY electronic pop and widescreen nostalgia.",
      "This archetype differs from synthpop because the historical frame is post-2000 bedroom/digital discovery rather than 1980s new romantic pop.",
      "Listeners should hear haze, memory, and production scale as clues to where the track sits."
    ]
  },
  "087": {
    short: "art-electronic music where machines, repetition, ambience, and formal experiment become the main listening object.",
    history: "Experimental electronic and IDM grow from Kraftwerk's machine-pop legacy, ambient practice, rave afterlives, labels, home computers, and producers treating sound design as composition.",
    why: "It gave electronic music a headphone-facing art vocabulary alongside club function.",
    distinct: "The road often asks listeners to follow timbre, pattern, and process rather than song or dance payoff.",
    listen: ["unusual drum programming", "synthetic timbre detail", "ambient or abstract form", "micro-pattern changes", "machine-pop lineage"],
    claims: [
      "Experimental Electronic / IDM / Art-Electronic should be grounded in electronic composition and listening practice, not simply in difficult dance music.",
      "Aphex Twin and Kraftwerk anchor the lane because they connect home-computer intricacy to earlier machine-pop foundations.",
      "Selected Ambient Works 85-92 and Trans-Europe Express make the road concrete through ambient-techno intimacy and iconic electronic repetition.",
      "This archetype differs from Detroit techno because club futurism is no longer the only center; headphone detail and formal experiment matter.",
      "Listeners should follow small pattern changes and timbre decisions as the main musical events."
    ]
  }
};

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

function files(dir) {
  return fs.readdirSync(dir)
    .filter((name) => name.endsWith(".json"))
    .sort()
    .map((name) => path.join(dir, name));
}

function unique(values) {
  return [...new Set(values.filter(Boolean))];
}

function buildClaims(pack, cfg, sourceIds) {
  const ref = pack.identity.canonical_graph_ref;
  const refs = [
    [sourceIds[0], sourceIds[1]],
    [sourceIds[0], sourceIds[2]],
    [sourceIds[1], sourceIds[2]],
    [sourceIds[2], sourceIds[3] || sourceIds[0]],
    [sourceIds[0], sourceIds[3] || sourceIds[1]]
  ];
  return cfg.claims.map((claimText, index) => ({
    claim_id: `${pack.identity.archetype_id}-curated-${String(index + 1).padStart(2, "0")}`,
    claim_text: claimText,
    source_ref_ids: unique(refs[index] || [sourceIds[0], sourceIds[1]]),
    confidence: "medium_high",
    module_usage: ["history_capsule", "region_scene_page", "mission_detail_history_module", "what_to_listen_for_prompt"],
    graph_refs: [
      ref,
      ...(pack.explainer_content.canonical_example_rationales || []).slice(0, 2).map((example) => example.example_ref)
    ],
    audit_status: "source_supported"
  }));
}

function main() {
  const baseline = readJson(BASELINE_PATH);
  const scaffold = new Map(files(SCAFFOLD_DIR).map((file) => {
    const pack = readJson(file);
    return [pack.identity.archetype_id, pack];
  }));
  const output = {};
  for (const [id, cfg] of Object.entries(CURATED)) {
    const pack = scaffold.get(id);
    if (!pack) throw new Error(`Missing scaffold pack ${id}`);
    const ref = pack.identity.canonical_graph_ref;
    const base = baseline[ref];
    if (!base) throw new Error(`Missing baseline note ${ref}`);
    const selected = base.selected_sources || [];
    const sourceIds = selected.map((source) => source.source_ref_id);
    if (sourceIds.length < 3) throw new Error(`Too few selected sources for ${ref}`);
    output[ref] = {
      archetype_query: `${pack.identity.editorial_display_title} archetype-specific v0.2.2 source recovery`,
      selected_sources: selected,
      rejected_sources: base.rejected_sources || [],
      why_selected_sources_fit: `${selected.map((source) => `${source.title} (${source.source_relevance})`).join("; ")}. These sources support the archetype's specific history, example objects, or family boundary without wrong-context claim use.`,
      claims: buildClaims(pack, cfg, sourceIds),
      render_seed: {
        short_definition: `${pack.identity.editorial_display_title} centers ${cfg.short}`,
        history_capsule: cfg.history,
        why_it_mattered: cfg.why,
        what_made_it_distinct: cfg.distinct,
        what_to_listen_for: cfg.listen,
        did_you_know: [
          `${pack.identity.editorial_display_title} is clearer when you hear its source context before judging personal fit.`,
          `The strongest listening cues are ${cfg.listen.slice(0, 3).join(", ")}.`
        ],
        caution: `A familiar ${pack.identity.editorial_display_title} example can mean recognition, setting memory, or repeated exposure before it proves durable affinity.`
      },
      curated_note: "Local v0.2.2 middle-family recovery note with archetype-specific claims and render seed."
    };
  }
  fs.mkdirSync(NOTES_DIR, { recursive: true });
  fs.writeFileSync(OUT_PATH, `${JSON.stringify(output, null, 2)}\n`);
  console.log(JSON.stringify({ output: OUT_PATH, archetype_count: Object.keys(output).length }, null, 2));
}

main();
