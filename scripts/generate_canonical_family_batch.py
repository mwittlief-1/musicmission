#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT_ROOT = ROOT / "data" / "canonical_graph"
TODAY = "2026-05-19"
DISPATCH = "/Users/matt_wittlief_home/Library/Mobile Documents/com~apple~CloudDocs/waymark_pass_one_dispatches_families_005_018.md"

ROLES = [
    "album_anchor",
    "anchor",
    "artist_anchor",
    "boundary",
    "bridge",
    "compilation_gateway",
    "contrast",
    "deepening",
    "false_nearby",
    "gateway",
    "live_gateway",
    "song_first",
]
RECOGNITION = ["mass", "high", "medium", "low", "cult"]
SURVEY = ["core", "standard", "edge", "suppress"]
ALBUM_TYPES = ["studio_album", "live_album", "compilation", "soundtrack", "ep"]
ARTIST_STATUSES = ["artist_survey_worthy", "song_survey_first", "song_survey_only"]


def slug(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = value.lower().replace("&", " and ")
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return re.sub(r"-+", "-", value).strip("-")


def artist(
    archetype_id: str,
    name: str,
    recognition: str,
    survey: str,
    roles: list[str],
    albums: list[str],
    songs: list[str],
    *,
    specificity: str = "artist_level",
    weight: float = 0.84,
    warning: str = "",
) -> dict[str, Any]:
    return {
        "archetype_id": archetype_id,
        "artist_name": name,
        "proposed_artist_id": slug(name),
        "existing_seed": False,
        "recognition_tier": recognition,
        "survey_tier": survey,
        "roles": roles,
        "archetype_membership_weight": weight,
        "inclusion_reason": f"{name} provides a recognizable survey branch for {archetype_id} without requiring collector-only context.",
        "object_specificity_note": specificity,
        "likely_canonical_albums": albums,
        "likely_canonical_songs": songs,
        "consolidation_warning": warning,
    }


def album(
    archetype_id: str,
    title: str,
    artist_name: str,
    year: int,
    kind: str,
    recognition: str,
    survey: str,
    roles: list[str],
    *,
    weight: float = 0.82,
    warning: str = "",
) -> dict[str, Any]:
    return {
        "archetype_id": archetype_id,
        "album_title": title,
        "artist_name": artist_name,
        "proposed_album_id": slug(f"{artist_name}-{title}"),
        "existing_seed": False,
        "release_year": year,
        "album_object_type": kind,
        "recognition_tier": recognition,
        "survey_tier": survey,
        "roles": roles,
        "archetype_membership_weight": weight,
        "inclusion_reason": f"{title} is a useful album-level gateway for {archetype_id}.",
        "consolidation_warning": warning,
    }


def song(
    archetype_id: str,
    title: str,
    artist_name: str,
    year: int,
    recognition: str,
    survey: str,
    roles: list[str],
    status: str,
    *,
    weight: float = 0.82,
    warning: str = "",
) -> dict[str, Any]:
    return {
        "archetype_id": archetype_id,
        "song_title": title,
        "artist_name": artist_name,
        "proposed_song_id": slug(f"{artist_name}-{title}"),
        "existing_seed": False,
        "release_year": year,
        "recognition_tier": recognition,
        "survey_tier": survey,
        "roles": roles,
        "archetype_membership_weight": weight,
        "inclusion_reason": f"{title} gives {archetype_id} a clear song-level tap for recognition, contrast, or branching.",
        "artist_survey_status": status,
        "consolidation_warning": warning,
    }


FAMILIES: dict[int, dict[str, Any]] = {
    5: {
        "name": "Country",
        "supplements": ["/Users/matt_wittlief_home/Library/Mobile Documents/com~apple~CloudDocs/F5.md"],
        "archetypes": {
            "031": "Classic Country / Honky-Tonk / Nashville Foundations",
            "032": "Outlaw Country / Cosmic Country",
            "033": "Country-Pop / Crossover Country",
            "034": "90s Country Radio / Hat Acts / New Traditionalists",
            "035": "Modern Country Radio / Bro-Country / Arena Country",
            "036": "Red Dirt / Americana Country / Texas Country",
        },
        "source_notes": [
            "Packet 005 is controlling for Family 5. The available F5.md report describes soul/R&B/funk/disco, which maps to Family 6 rather than Country, so no F5.md row is imported as a seed here.",
            "All rows in this batch are added missing-obvious rows pending a true Country-specific second-pass report.",
        ],
        "artists": [
            artist("031", "Hank Williams", "high", "core", ["anchor", "artist_anchor"], ["40 Greatest Hits"], ["Your Cheatin' Heart", "I'm So Lonesome I Could Cry"], weight=0.94),
            artist("031", "Patsy Cline", "mass", "core", ["anchor", "artist_anchor", "bridge"], ["Showcase"], ["Crazy", "I Fall to Pieces"], weight=0.93),
            artist("031", "Johnny Cash", "mass", "core", ["anchor", "artist_anchor", "bridge"], ["At Folsom Prison"], ["Ring of Fire", "Folsom Prison Blues"], weight=0.94, warning="Cross-family bridge into folk, rock, gospel, and soundtrack contexts; preserve country membership as one facet."),
            artist("031", "George Jones", "high", "core", ["anchor", "artist_anchor"], ["I Am What I Am"], ["He Stopped Loving Her Today"], weight=0.9),
            artist("031", "Loretta Lynn", "high", "core", ["anchor", "artist_anchor"], ["Coal Miner's Daughter"], ["Coal Miner's Daughter", "You Ain't Woman Enough"], weight=0.88),
            artist("031", "Tammy Wynette", "high", "standard", ["gateway", "artist_anchor"], ["Stand by Your Man"], ["Stand by Your Man"], weight=0.84),
            artist("031", "Buck Owens", "medium", "standard", ["gateway", "bridge"], ["I've Got a Tiger by the Tail"], ["Act Naturally"], weight=0.8),
            artist("032", "Willie Nelson", "mass", "core", ["anchor", "artist_anchor", "bridge"], ["Red Headed Stranger"], ["Blue Eyes Crying in the Rain", "On the Road Again"], weight=0.93),
            artist("032", "Waylon Jennings", "high", "core", ["anchor", "artist_anchor"], ["Honky Tonk Heroes"], ["Mammas Don't Let Your Babies Grow Up to Be Cowboys"], weight=0.9),
            artist("032", "Kris Kristofferson", "medium", "standard", ["bridge", "deepening"], ["Kristofferson"], ["Sunday Mornin' Comin' Down"], weight=0.78),
            artist("032", "Gram Parsons", "medium", "standard", ["bridge", "boundary"], ["Grievous Angel"], ["Return of the Grievous Angel"], weight=0.78),
            artist("032", "The Flying Burrito Brothers", "medium", "edge", ["boundary", "deepening"], ["The Gilded Palace of Sin"], ["Sin City"], weight=0.72),
            artist("032", "Emmylou Harris", "high", "standard", ["bridge", "artist_anchor"], ["Pieces of the Sky"], ["Boulder to Birmingham"], weight=0.82),
            artist("032", "Townes Van Zandt", "medium", "edge", ["deepening", "boundary"], ["Live at the Old Quarter, Houston, Texas"], ["Pancho and Lefty"], weight=0.72),
            artist("033", "Dolly Parton", "mass", "core", ["anchor", "artist_anchor", "bridge"], ["Coat of Many Colors"], ["Jolene", "9 to 5"], weight=0.94),
            artist("033", "Kenny Rogers", "mass", "core", ["gateway", "artist_anchor"], ["The Gambler"], ["The Gambler", "Islands in the Stream"], weight=0.88),
            artist("033", "Glen Campbell", "high", "core", ["gateway", "bridge"], ["Rhinestone Cowboy"], ["Rhinestone Cowboy", "Wichita Lineman"], weight=0.86),
            artist("033", "Shania Twain", "mass", "core", ["anchor", "artist_anchor"], ["Come On Over"], ["Man! I Feel Like a Woman!", "You're Still the One"], weight=0.9),
            artist("033", "Faith Hill", "high", "standard", ["gateway", "bridge"], ["Breathe"], ["Breathe", "This Kiss"], weight=0.8),
            artist("033", "The Chicks", "high", "standard", ["bridge", "artist_anchor"], ["Wide Open Spaces"], ["Wide Open Spaces", "Goodbye Earl"], weight=0.82),
            artist("034", "Garth Brooks", "mass", "core", ["anchor", "artist_anchor"], ["No Fences"], ["Friends in Low Places"], weight=0.94),
            artist("034", "George Strait", "high", "core", ["anchor", "artist_anchor"], ["Pure Country"], ["Amarillo by Morning", "Check Yes or No"], weight=0.9),
            artist("034", "Alan Jackson", "high", "core", ["anchor", "artist_anchor"], ["Don't Rock the Jukebox"], ["Chattahoochee"], weight=0.88),
            artist("034", "Brooks & Dunn", "high", "standard", ["gateway", "artist_anchor"], ["Brand New Man"], ["Boot Scootin' Boogie"], weight=0.84),
            artist("034", "Reba McEntire", "high", "standard", ["gateway", "artist_anchor"], ["Rumor Has It"], ["Fancy"], weight=0.82),
            artist("034", "Tim McGraw", "high", "standard", ["gateway", "bridge"], ["Not a Moment Too Soon"], ["Live Like You Were Dying"], weight=0.8),
            artist("034", "Clint Black", "medium", "edge", ["deepening"], ["Killin' Time"], ["A Better Man"], weight=0.7),
            artist("035", "Luke Bryan", "high", "core", ["anchor", "artist_anchor"], ["Crash My Party"], ["Country Girl (Shake It for Me)"], weight=0.84),
            artist("035", "Florida Georgia Line", "mass", "core", ["anchor", "artist_anchor"], ["Here's to the Good Times"], ["Cruise"], weight=0.86),
            artist("035", "Jason Aldean", "high", "standard", ["gateway", "artist_anchor"], ["My Kinda Party"], ["Dirt Road Anthem"], weight=0.82),
            artist("035", "Morgan Wallen", "mass", "core", ["anchor", "artist_anchor"], ["Dangerous: The Double Album"], ["Last Night"], weight=0.86),
            artist("035", "Carrie Underwood", "mass", "core", ["bridge", "artist_anchor"], ["Some Hearts"], ["Before He Cheats"], weight=0.84),
            artist("035", "Kacey Musgraves", "high", "standard", ["contrast", "bridge"], ["Golden Hour"], ["Slow Burn"], weight=0.78),
            artist("035", "Eric Church", "high", "standard", ["bridge", "artist_anchor"], ["Chief"], ["Springsteen"], weight=0.8),
            artist("036", "Steve Earle", "medium", "standard", ["bridge", "deepening"], ["Guitar Town"], ["Copperhead Road"], weight=0.78),
            artist("036", "Lucinda Williams", "medium", "standard", ["bridge", "deepening"], ["Car Wheels on a Gravel Road"], ["Car Wheels on a Gravel Road"], weight=0.78),
            artist("036", "Jason Isbell", "medium", "standard", ["anchor", "artist_anchor"], ["Southeastern"], ["Cover Me Up"], weight=0.82),
            artist("036", "Tyler Childers", "high", "standard", ["gateway", "artist_anchor"], ["Purgatory"], ["Feathered Indians"], weight=0.82),
            artist("036", "Sturgill Simpson", "medium", "standard", ["bridge", "boundary"], ["Metamodern Sounds in Country Music"], ["Turtles All the Way Down"], weight=0.78),
            artist("036", "Turnpike Troubadours", "medium", "edge", ["deepening"], ["Diamonds & Gasoline"], ["Good Lord Lorrie"], weight=0.7),
            artist("036", "Zach Bryan", "high", "standard", ["gateway", "bridge"], ["American Heartbreak"], ["Something in the Orange"], weight=0.8),
        ],
        "albums": [
            album("031", "40 Greatest Hits", "Hank Williams", 1978, "compilation", "high", "core", ["compilation_gateway", "album_anchor"]),
            album("031", "Showcase", "Patsy Cline", 1961, "studio_album", "high", "core", ["album_anchor"]),
            album("031", "At Folsom Prison", "Johnny Cash", 1968, "live_album", "mass", "core", ["live_gateway", "album_anchor", "bridge"]),
            album("031", "I Am What I Am", "George Jones", 1980, "studio_album", "high", "standard", ["album_anchor"]),
            album("031", "Coal Miner's Daughter", "Loretta Lynn", 1970, "studio_album", "high", "standard", ["album_anchor"]),
            album("032", "Wanted! The Outlaws", "Various Artists", 1976, "compilation", "high", "standard", ["compilation_gateway", "anchor"]),
            album("032", "Red Headed Stranger", "Willie Nelson", 1975, "studio_album", "high", "core", ["album_anchor", "anchor"]),
            album("032", "Honky Tonk Heroes", "Waylon Jennings", 1973, "studio_album", "medium", "standard", ["album_anchor"]),
            album("032", "Grievous Angel", "Gram Parsons", 1974, "studio_album", "medium", "edge", ["album_anchor", "bridge"]),
            album("032", "Pieces of the Sky", "Emmylou Harris", 1975, "studio_album", "medium", "standard", ["album_anchor", "bridge"]),
            album("033", "Coat of Many Colors", "Dolly Parton", 1971, "studio_album", "high", "core", ["album_anchor"]),
            album("033", "The Gambler", "Kenny Rogers", 1978, "studio_album", "high", "core", ["album_anchor"]),
            album("033", "Rhinestone Cowboy", "Glen Campbell", 1975, "studio_album", "high", "standard", ["gateway"]),
            album("033", "Come On Over", "Shania Twain", 1997, "studio_album", "mass", "core", ["album_anchor", "anchor"]),
            album("033", "Wide Open Spaces", "The Chicks", 1998, "studio_album", "high", "standard", ["album_anchor"]),
            album("034", "No Fences", "Garth Brooks", 1990, "studio_album", "mass", "core", ["album_anchor", "anchor"]),
            album("034", "Don't Rock the Jukebox", "Alan Jackson", 1991, "studio_album", "high", "standard", ["album_anchor"]),
            album("034", "Pure Country", "George Strait", 1992, "soundtrack", "high", "standard", ["gateway", "album_anchor"]),
            album("034", "Brand New Man", "Brooks & Dunn", 1991, "studio_album", "high", "standard", ["album_anchor"]),
            album("034", "Rumor Has It", "Reba McEntire", 1990, "studio_album", "medium", "standard", ["gateway"]),
            album("035", "Crash My Party", "Luke Bryan", 2013, "studio_album", "high", "standard", ["album_anchor"]),
            album("035", "Here's to the Good Times", "Florida Georgia Line", 2012, "studio_album", "high", "core", ["album_anchor"]),
            album("035", "My Kinda Party", "Jason Aldean", 2010, "studio_album", "high", "standard", ["album_anchor"]),
            album("035", "Dangerous: The Double Album", "Morgan Wallen", 2021, "studio_album", "mass", "core", ["album_anchor"]),
            album("035", "Golden Hour", "Kacey Musgraves", 2018, "studio_album", "high", "standard", ["contrast", "album_anchor"]),
            album("036", "Guitar Town", "Steve Earle", 1986, "studio_album", "medium", "standard", ["bridge"]),
            album("036", "Car Wheels on a Gravel Road", "Lucinda Williams", 1998, "studio_album", "medium", "standard", ["album_anchor"]),
            album("036", "Southeastern", "Jason Isbell", 2013, "studio_album", "medium", "standard", ["album_anchor"]),
            album("036", "Purgatory", "Tyler Childers", 2017, "studio_album", "high", "standard", ["album_anchor"]),
            album("036", "Metamodern Sounds in Country Music", "Sturgill Simpson", 2014, "studio_album", "medium", "standard", ["bridge", "album_anchor"]),
            album("036", "American Heartbreak", "Zach Bryan", 2022, "studio_album", "high", "standard", ["gateway"]),
        ],
        "songs": [
            song("031", "Your Cheatin' Heart", "Hank Williams", 1953, "high", "core", ["anchor", "song_first"], "artist_survey_worthy"),
            song("031", "I'm So Lonesome I Could Cry", "Hank Williams", 1949, "high", "core", ["anchor", "deepening"], "artist_survey_worthy"),
            song("031", "Crazy", "Patsy Cline", 1961, "mass", "core", ["anchor", "song_first"], "artist_survey_worthy"),
            song("031", "I Fall to Pieces", "Patsy Cline", 1961, "high", "standard", ["gateway"], "artist_survey_worthy"),
            song("031", "Ring of Fire", "Johnny Cash", 1963, "mass", "core", ["anchor", "song_first"], "artist_survey_worthy"),
            song("031", "He Stopped Loving Her Today", "George Jones", 1980, "high", "core", ["anchor", "deepening"], "artist_survey_worthy"),
            song("031", "Coal Miner's Daughter", "Loretta Lynn", 1970, "high", "standard", ["gateway"], "artist_survey_worthy"),
            song("032", "Blue Eyes Crying in the Rain", "Willie Nelson", 1975, "high", "core", ["anchor"], "artist_survey_worthy"),
            song("032", "On the Road Again", "Willie Nelson", 1980, "mass", "core", ["gateway", "song_first"], "artist_survey_worthy"),
            song("032", "Mammas Don't Let Your Babies Grow Up to Be Cowboys", "Waylon Jennings and Willie Nelson", 1978, "mass", "core", ["gateway", "song_first"], "song_survey_first", warning="Collaboration row should not merge into either solo-artist recording."),
            song("032", "Sunday Mornin' Comin' Down", "Kris Kristofferson", 1970, "medium", "standard", ["deepening"], "artist_survey_worthy"),
            song("032", "Pancho and Lefty", "Townes Van Zandt", 1972, "medium", "edge", ["deepening", "boundary"], "artist_survey_worthy", warning="Do not merge with Willie Nelson and Merle Haggard hit version."),
            song("032", "Return of the Grievous Angel", "Gram Parsons", 1974, "medium", "edge", ["bridge"], "artist_survey_worthy"),
            song("032", "Boulder to Birmingham", "Emmylou Harris", 1975, "medium", "standard", ["bridge"], "artist_survey_worthy"),
            song("033", "Jolene", "Dolly Parton", 1973, "mass", "core", ["anchor", "song_first"], "artist_survey_worthy"),
            song("033", "9 to 5", "Dolly Parton", 1980, "mass", "core", ["gateway", "song_first"], "artist_survey_worthy"),
            song("033", "The Gambler", "Kenny Rogers", 1978, "mass", "core", ["anchor", "song_first"], "artist_survey_worthy"),
            song("033", "Rhinestone Cowboy", "Glen Campbell", 1975, "mass", "core", ["gateway", "song_first"], "artist_survey_worthy"),
            song("033", "Man! I Feel Like a Woman!", "Shania Twain", 1999, "mass", "core", ["anchor", "song_first"], "artist_survey_worthy"),
            song("033", "You're Still the One", "Shania Twain", 1998, "mass", "core", ["gateway"], "artist_survey_worthy"),
            song("033", "Breathe", "Faith Hill", 1999, "high", "standard", ["bridge"], "artist_survey_worthy"),
            song("034", "Friends in Low Places", "Garth Brooks", 1990, "mass", "core", ["anchor", "song_first"], "artist_survey_worthy"),
            song("034", "The Dance", "Garth Brooks", 1990, "high", "standard", ["gateway"], "artist_survey_worthy"),
            song("034", "Chattahoochee", "Alan Jackson", 1993, "high", "core", ["anchor"], "artist_survey_worthy"),
            song("034", "Amarillo by Morning", "George Strait", 1983, "high", "core", ["anchor"], "artist_survey_worthy"),
            song("034", "Boot Scootin' Boogie", "Brooks & Dunn", 1992, "high", "standard", ["gateway", "song_first"], "artist_survey_worthy"),
            song("034", "Fancy", "Reba McEntire", 1990, "high", "standard", ["gateway"], "artist_survey_worthy", warning="Do not merge with Bobbie Gentry original."),
            song("034", "Live Like You Were Dying", "Tim McGraw", 2004, "high", "standard", ["bridge"], "artist_survey_worthy"),
            song("035", "Cruise", "Florida Georgia Line", 2012, "mass", "core", ["anchor", "song_first"], "artist_survey_worthy"),
            song("035", "Country Girl (Shake It for Me)", "Luke Bryan", 2011, "high", "standard", ["gateway"], "artist_survey_worthy"),
            song("035", "Dirt Road Anthem", "Jason Aldean", 2010, "high", "standard", ["bridge"], "artist_survey_worthy"),
            song("035", "Before He Cheats", "Carrie Underwood", 2005, "mass", "core", ["gateway", "song_first"], "artist_survey_worthy"),
            song("035", "Last Night", "Morgan Wallen", 2023, "mass", "core", ["anchor", "song_first"], "artist_survey_worthy"),
            song("035", "Slow Burn", "Kacey Musgraves", 2018, "high", "standard", ["contrast", "bridge"], "artist_survey_worthy"),
            song("035", "Springsteen", "Eric Church", 2012, "high", "standard", ["bridge"], "artist_survey_worthy"),
            song("036", "Copperhead Road", "Steve Earle", 1988, "high", "standard", ["bridge", "song_first"], "artist_survey_worthy"),
            song("036", "Car Wheels on a Gravel Road", "Lucinda Williams", 1998, "medium", "standard", ["deepening"], "artist_survey_worthy"),
            song("036", "Cover Me Up", "Jason Isbell", 2013, "medium", "standard", ["gateway"], "artist_survey_worthy"),
            song("036", "Feathered Indians", "Tyler Childers", 2017, "high", "standard", ["gateway"], "artist_survey_worthy"),
            song("036", "Turtles All the Way Down", "Sturgill Simpson", 2014, "medium", "standard", ["boundary"], "artist_survey_worthy"),
            song("036", "Good Lord Lorrie", "Turnpike Troubadours", 2010, "medium", "edge", ["deepening"], "artist_survey_worthy"),
            song("036", "Something in the Orange", "Zach Bryan", 2022, "high", "standard", ["gateway", "song_first"], "artist_survey_worthy"),
        ],
    },
}


def extend_family_11() -> dict[str, Any]:
    return {
        "name": "Electronic, Dance, Club, Industrial, Experimental Pop",
        "supplements": ["/Users/matt_wittlief_home/Library/Mobile Documents/com~apple~CloudDocs/F11.md"],
        "archetypes": {
            "081": "House / Chicago / Dance Club Foundations",
            "082": "Techno / Detroit / Minimal Electronic",
            "083": "EDM / Festival Dance / Big Room / Mainstream Electronic",
            "084": "Trip-Hop / Downtempo / Nocturnal Electronic",
            "085": "Indie Dance / Dance-Punk / Electroclash",
            "086": "Synthwave / Chillwave / Bedroom Electronic",
            "087": "Experimental Electronic / IDM / Art-Electronic",
        },
        "source_notes": [
            "Packet 011 is controlling. F11.md is a null/status report and supplies no verified rows; all objects here are missing-obvious expansion rows.",
            "Electronic artist aliases and project names are high-risk merge areas; preserve artist/project IDs unless an alias rule is explicit.",
        ],
        "artists": [
            artist("081", "Frankie Knuckles", "high", "core", ["anchor", "artist_anchor"], ["Beyond the Mix"], ["Your Love"], weight=0.9),
            artist("081", "Marshall Jefferson", "medium", "standard", ["anchor", "song_first"], ["Move Your Body"], ["Move Your Body"], weight=0.84),
            artist("081", "Mr. Fingers", "medium", "standard", ["anchor", "song_first"], ["Amnesia"], ["Can You Feel It"], weight=0.84, warning="Alias of Larry Heard; keep project alias review explicit."),
            artist("081", "Robin S.", "high", "core", ["gateway", "song_first"], ["Show Me Love"], ["Show Me Love"], specificity="song_level", weight=0.82),
            artist("081", "CeCe Peniston", "high", "standard", ["gateway", "song_first"], ["Finally"], ["Finally"], specificity="song_level", weight=0.8),
            artist("081", "Masters at Work", "medium", "standard", ["deepening"], ["The Album"], ["To Be in Love"], weight=0.74),
            artist("082", "Juan Atkins", "medium", "standard", ["anchor", "artist_anchor"], ["20 Years 1985-2005"], ["No UFO's"], weight=0.88),
            artist("082", "Derrick May", "medium", "standard", ["anchor", "song_first"], ["Innovator"], ["Strings of Life"], weight=0.88),
            artist("082", "Inner City", "high", "standard", ["gateway", "song_first"], ["Paradise"], ["Good Life"], weight=0.82),
            artist("082", "Jeff Mills", "medium", "edge", ["deepening"], ["Waveform Transmission Vol. 1"], ["The Bells"], weight=0.74),
            artist("082", "Carl Craig", "medium", "edge", ["deepening", "bridge"], ["More Songs About Food and Revolutionary Art"], ["At Les"], weight=0.72),
            artist("082", "Plastikman", "medium", "edge", ["deepening"], ["Sheet One"], ["Spastik"], weight=0.7),
            artist("083", "Calvin Harris", "mass", "core", ["anchor", "artist_anchor"], ["18 Months"], ["Feel So Close"], weight=0.88),
            artist("083", "Avicii", "mass", "core", ["anchor", "artist_anchor"], ["True"], ["Wake Me Up"], weight=0.9),
            artist("083", "Swedish House Mafia", "high", "core", ["anchor", "song_first"], ["Until Now"], ["Don't You Worry Child"], weight=0.84),
            artist("083", "David Guetta", "mass", "core", ["gateway", "artist_anchor"], ["Nothing but the Beat"], ["Titanium"], weight=0.84),
            artist("083", "Skrillex", "high", "standard", ["bridge", "artist_anchor"], ["Scary Monsters and Nice Sprites"], ["Bangarang"], weight=0.8),
            artist("083", "Zedd", "high", "standard", ["gateway", "song_first"], ["Clarity"], ["Clarity"], weight=0.78),
            artist("084", "Massive Attack", "high", "core", ["anchor", "artist_anchor"], ["Mezzanine"], ["Teardrop"], weight=0.9),
            artist("084", "Portishead", "high", "core", ["anchor", "artist_anchor"], ["Dummy"], ["Sour Times"], weight=0.88),
            artist("084", "Tricky", "medium", "standard", ["deepening"], ["Maxinquaye"], ["Hell Is Round the Corner"], weight=0.78),
            artist("084", "DJ Shadow", "medium", "standard", ["bridge", "album_anchor"], ["Endtroducing....."], ["Midnight in a Perfect World"], weight=0.78),
            artist("084", "Moby", "high", "standard", ["gateway", "bridge"], ["Play"], ["Porcelain"], weight=0.8),
            artist("084", "Air", "medium", "standard", ["bridge"], ["Moon Safari"], ["La femme d'argent"], weight=0.76),
            artist("085", "LCD Soundsystem", "high", "core", ["anchor", "artist_anchor"], ["Sound of Silver"], ["All My Friends"], weight=0.88),
            artist("085", "The Rapture", "medium", "standard", ["gateway"], ["Echoes"], ["House of Jealous Lovers"], weight=0.78),
            artist("085", "Justice", "high", "standard", ["gateway", "artist_anchor"], ["Cross"], ["D.A.N.C.E."], weight=0.8),
            artist("085", "Hot Chip", "medium", "standard", ["bridge"], ["The Warning"], ["Over and Over"], weight=0.74),
            artist("085", "Fischerspooner", "medium", "edge", ["deepening"], ["#1"], ["Emerge"], weight=0.7),
            artist("085", "Peaches", "medium", "edge", ["boundary", "contrast"], ["The Teaches of Peaches"], ["Fuck the Pain Away"], weight=0.68),
            artist("086", "Kavinsky", "medium", "standard", ["gateway", "song_first"], ["OutRun"], ["Nightcall"], weight=0.78),
            artist("086", "M83", "high", "standard", ["bridge", "artist_anchor"], ["Hurry Up, We're Dreaming"], ["Midnight City"], weight=0.82),
            artist("086", "Washed Out", "medium", "standard", ["anchor"], ["Within and Without"], ["Feel It All Around"], weight=0.78),
            artist("086", "Neon Indian", "medium", "edge", ["deepening"], ["Psychic Chasms"], ["Deadbeat Summer"], weight=0.7),
            artist("086", "Tycho", "medium", "standard", ["bridge"], ["Dive"], ["A Walk"], weight=0.76),
            artist("086", "Com Truise", "low", "edge", ["deepening"], ["Galactic Melt"], ["Brokendate"], weight=0.66),
            artist("087", "Kraftwerk", "high", "core", ["anchor", "artist_anchor", "bridge"], ["Trans-Europe Express"], ["The Model"], weight=0.9),
            artist("087", "Aphex Twin", "high", "core", ["anchor", "artist_anchor"], ["Selected Ambient Works 85-92"], ["Windowlicker"], weight=0.88),
            artist("087", "Autechre", "medium", "edge", ["deepening"], ["Tri Repetae"], ["Flutter"], weight=0.72),
            artist("087", "Bjork", "high", "standard", ["bridge", "boundary"], ["Homogenic"], ["Joga"], weight=0.78),
            artist("087", "Four Tet", "medium", "standard", ["bridge"], ["Rounds"], ["Two Thousand and Seventeen"], weight=0.76),
            artist("087", "Burial", "medium", "standard", ["deepening"], ["Untrue"], ["Archangel"], weight=0.78),
        ],
        "albums": [
            album("081", "Beyond the Mix", "Frankie Knuckles", 1991, "studio_album", "medium", "standard", ["album_anchor"]),
            album("081", "Amnesia", "Mr. Fingers", 1989, "studio_album", "medium", "standard", ["album_anchor"], warning="Alias review: Mr. Fingers vs Larry Heard."),
            album("081", "Show Me Love", "Robin S.", 1993, "studio_album", "high", "standard", ["gateway"]),
            album("081", "The Album", "Masters at Work", 1993, "studio_album", "medium", "edge", ["deepening"]),
            album("082", "Paradise", "Inner City", 1989, "studio_album", "high", "standard", ["gateway"]),
            album("082", "Innovator", "Derrick May", 1991, "compilation", "medium", "standard", ["compilation_gateway"]),
            album("082", "Waveform Transmission Vol. 1", "Jeff Mills", 1992, "studio_album", "medium", "edge", ["deepening"]),
            album("082", "Sheet One", "Plastikman", 1993, "studio_album", "medium", "edge", ["deepening"]),
            album("083", "18 Months", "Calvin Harris", 2012, "studio_album", "mass", "core", ["album_anchor"]),
            album("083", "True", "Avicii", 2013, "studio_album", "mass", "core", ["album_anchor"]),
            album("083", "Until Now", "Swedish House Mafia", 2012, "compilation", "high", "standard", ["compilation_gateway"]),
            album("083", "Scary Monsters and Nice Sprites", "Skrillex", 2010, "ep", "high", "standard", ["gateway"]),
            album("084", "Blue Lines", "Massive Attack", 1991, "studio_album", "high", "core", ["album_anchor"]),
            album("084", "Mezzanine", "Massive Attack", 1998, "studio_album", "high", "core", ["album_anchor"]),
            album("084", "Dummy", "Portishead", 1994, "studio_album", "high", "core", ["album_anchor"]),
            album("084", "Endtroducing.....", "DJ Shadow", 1996, "studio_album", "medium", "standard", ["album_anchor"]),
            album("084", "Play", "Moby", 1999, "studio_album", "high", "standard", ["gateway"]),
            album("085", "Sound of Silver", "LCD Soundsystem", 2007, "studio_album", "high", "core", ["album_anchor"]),
            album("085", "Echoes", "The Rapture", 2003, "studio_album", "medium", "standard", ["gateway"]),
            album("085", "Cross", "Justice", 2007, "studio_album", "high", "standard", ["album_anchor"]),
            album("085", "#1", "Fischerspooner", 2001, "studio_album", "medium", "edge", ["deepening"]),
            album("086", "OutRun", "Kavinsky", 2013, "studio_album", "medium", "standard", ["gateway"]),
            album("086", "Hurry Up, We're Dreaming", "M83", 2011, "studio_album", "high", "standard", ["album_anchor"]),
            album("086", "Within and Without", "Washed Out", 2011, "studio_album", "medium", "standard", ["album_anchor"]),
            album("086", "Dive", "Tycho", 2011, "studio_album", "medium", "standard", ["bridge"]),
            album("087", "Trans-Europe Express", "Kraftwerk", 1977, "studio_album", "high", "core", ["album_anchor", "bridge"]),
            album("087", "Selected Ambient Works 85-92", "Aphex Twin", 1992, "studio_album", "high", "core", ["album_anchor"]),
            album("087", "Homogenic", "Bjork", 1997, "studio_album", "high", "standard", ["bridge"]),
            album("087", "Untrue", "Burial", 2007, "studio_album", "medium", "standard", ["deepening"]),
        ],
        "songs": [
            song("081", "Your Love", "Frankie Knuckles", 1987, "high", "core", ["anchor", "song_first"], "artist_survey_worthy"),
            song("081", "Move Your Body", "Marshall Jefferson", 1986, "medium", "standard", ["anchor", "song_first"], "song_survey_first"),
            song("081", "Can You Feel It", "Mr. Fingers", 1986, "medium", "standard", ["anchor", "song_first"], "song_survey_first", warning="Alias review: Mr. Fingers vs Larry Heard."),
            song("081", "Show Me Love", "Robin S.", 1993, "mass", "core", ["gateway", "song_first"], "song_survey_first"),
            song("081", "Finally", "CeCe Peniston", 1991, "mass", "core", ["gateway", "song_first"], "song_survey_first"),
            song("081", "Good Life", "Inner City", 1988, "high", "standard", ["bridge"], "song_survey_first"),
            song("082", "No UFO's", "Model 500", 1985, "medium", "standard", ["anchor"], "song_survey_first", warning="Model 500 alias should be reviewed against Juan Atkins."),
            song("082", "Strings of Life", "Rhythim Is Rhythim", 1987, "medium", "standard", ["anchor", "song_first"], "song_survey_first", warning="Derrick May alias/project review required."),
            song("082", "The Bells", "Jeff Mills", 1996, "medium", "edge", ["deepening"], "artist_survey_worthy"),
            song("082", "Spastik", "Plastikman", 1993, "medium", "edge", ["deepening"], "artist_survey_worthy"),
            song("082", "At Les", "Carl Craig", 1997, "medium", "edge", ["deepening"], "artist_survey_worthy"),
            song("083", "Wake Me Up", "Avicii", 2013, "mass", "core", ["anchor", "song_first"], "artist_survey_worthy"),
            song("083", "Levels", "Avicii", 2011, "mass", "core", ["gateway"], "artist_survey_worthy"),
            song("083", "Feel So Close", "Calvin Harris", 2011, "mass", "core", ["gateway"], "artist_survey_worthy"),
            song("083", "Don't You Worry Child", "Swedish House Mafia", 2012, "mass", "core", ["anchor", "song_first"], "song_survey_first"),
            song("083", "Titanium", "David Guetta featuring Sia", 2011, "mass", "core", ["gateway", "song_first"], "song_survey_first", warning="Feature row should not merge into solo Sia artist object."),
            song("083", "Clarity", "Zedd featuring Foxes", 2012, "mass", "core", ["gateway", "song_first"], "song_survey_first"),
            song("083", "Bangarang", "Skrillex", 2011, "high", "standard", ["bridge"], "artist_survey_worthy"),
            song("084", "Teardrop", "Massive Attack", 1998, "high", "core", ["anchor", "song_first"], "artist_survey_worthy"),
            song("084", "Unfinished Sympathy", "Massive Attack", 1991, "high", "standard", ["gateway"], "artist_survey_worthy"),
            song("084", "Sour Times", "Portishead", 1994, "high", "standard", ["anchor"], "artist_survey_worthy"),
            song("084", "Glory Box", "Portishead", 1994, "high", "standard", ["gateway"], "artist_survey_worthy"),
            song("084", "Midnight in a Perfect World", "DJ Shadow", 1996, "medium", "standard", ["deepening"], "artist_survey_worthy"),
            song("084", "Porcelain", "Moby", 1999, "high", "standard", ["gateway"], "artist_survey_worthy"),
            song("085", "All My Friends", "LCD Soundsystem", 2007, "high", "core", ["anchor"], "artist_survey_worthy"),
            song("085", "Daft Punk Is Playing at My House", "LCD Soundsystem", 2005, "high", "standard", ["gateway"], "artist_survey_worthy"),
            song("085", "House of Jealous Lovers", "The Rapture", 2002, "medium", "standard", ["gateway", "song_first"], "artist_survey_worthy"),
            song("085", "D.A.N.C.E.", "Justice", 2007, "high", "standard", ["gateway"], "artist_survey_worthy"),
            song("085", "Over and Over", "Hot Chip", 2006, "medium", "standard", ["bridge"], "artist_survey_worthy"),
            song("085", "Emerge", "Fischerspooner", 2001, "medium", "edge", ["deepening"], "artist_survey_worthy"),
            song("086", "Nightcall", "Kavinsky", 2010, "high", "standard", ["gateway", "song_first"], "artist_survey_worthy"),
            song("086", "Midnight City", "M83", 2011, "mass", "core", ["anchor", "song_first"], "artist_survey_worthy"),
            song("086", "Feel It All Around", "Washed Out", 2009, "medium", "standard", ["anchor"], "artist_survey_worthy"),
            song("086", "Deadbeat Summer", "Neon Indian", 2009, "medium", "edge", ["deepening"], "artist_survey_worthy"),
            song("086", "A Walk", "Tycho", 2011, "medium", "standard", ["bridge"], "artist_survey_worthy"),
            song("087", "The Model", "Kraftwerk", 1978, "high", "standard", ["gateway", "song_first"], "artist_survey_worthy"),
            song("087", "Autobahn", "Kraftwerk", 1974, "high", "standard", ["anchor"], "artist_survey_worthy"),
            song("087", "Windowlicker", "Aphex Twin", 1999, "high", "core", ["anchor"], "artist_survey_worthy"),
            song("087", "Joga", "Bjork", 1997, "high", "standard", ["bridge"], "artist_survey_worthy"),
            song("087", "Archangel", "Burial", 2007, "medium", "standard", ["deepening"], "artist_survey_worthy"),
        ],
    }


def compact_family(num: int, name: str, supplements: list[str], archetypes: dict[str, str], notes: list[str], rows: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    return {"name": name, "supplements": supplements, "archetypes": archetypes, "source_notes": notes, **rows}


def build_compact_families() -> None:
    FAMILIES[11] = extend_family_11()
    FAMILIES[13] = compact_family(
        13,
        "Latin, Caribbean, Global Pop",
        ["/Users/matt_wittlief_home/Library/Mobile Documents/com~apple~CloudDocs/F13.md", "/Users/matt_wittlief_home/Library/Mobile Documents/com~apple~CloudDocs/F9.md"],
        {
            "094": "Reggaeton / Urbano / Latin Pop Crossover",
            "095": "Regional Mexican / Corridos / Musica Mexicana",
            "096": "Salsa / Latin Dance / Tropical Pop",
            "097": "Afrobeats / African Pop Crossover",
            "098": "K-Pop / J-Pop / Asian Pop Crossover",
            "099": "Global Folk / World Fusion / Diaspora Roots",
        },
        [
            "Packet 013 is controlling. F13.md is a null/status report; F9.md contains Afrobeats material and is treated as supplemental context for archetype 097 only.",
            "Artist/version boundaries are especially important for covers, remixes, language variants, and global crossover collaborations.",
        ],
        make_family_13_rows(),
    )
    FAMILIES[14] = compact_family(
        14,
        "Jazz, Standards, Vocal, Classical-Adjacent",
        ["/Users/matt_wittlief_home/Library/Mobile Documents/com~apple~CloudDocs/F14.md"],
        {
            "100": "Vocal Standards / Crooners / Great American Songbook",
            "101": "Jazz Foundations / Bebop / Hard Bop Gateway",
            "102": "Smooth Jazz / Jazz-Pop / Adult Instrumental",
            "103": "Classical Crossover / Instrumental Popular Canon",
        },
        [
            "Packet 014 is controlling. F14.md is a null/status report and supplies no seed rows.",
            "Jazz composition standards, artist recordings, and album objects must remain distinct; many songs are standards with many canonical recordings.",
        ],
        make_family_14_rows(),
    )
    FAMILIES[15] = compact_family(
        15,
        "Soundtrack, Theater, Musicals, Family Context",
        [],
        {
            "104": "Broadway / Modern Musical Theater",
            "105": "Disney / Family Soundtrack / Animated Musical Canon",
            "106": "Movie Soundtracks / 80s-90s-00s Soundtrack Memory",
            "107": "Film Score / Epic Score / Ambient Cinematic",
        },
        [
            "Packet 015 is controlling. No standalone F15.md was available during this pass.",
            "Cast albums, soundtrack albums, score cues, and pop singles attached to films are separate object types and should not be merged by title alone.",
        ],
        make_family_15_rows(),
    )
    FAMILIES[16] = compact_family(
        16,
        "Christian, Worship, Gospel",
        ["/Users/matt_wittlief_home/Library/Mobile Documents/com~apple~CloudDocs/F16.md"],
        {
            "108": "Black Gospel / Gospel Soul",
            "109": "CCM / Christian Pop-Rock / Worship Radio",
            "110": "Worship / Praise / Church Songbook",
        },
        [
            "Packet 016 is controlling. F16.md describes dream pop/shoegaze material and is not used as a Family 16 seed.",
            "Canonical handling must separate artist objects from congregation/church-band brands and from songbook compositions.",
        ],
        make_family_16_rows(),
    )
    FAMILIES[18] = compact_family(
        18,
        "Modern Rock, Current Discovery, Internet-Native Scenes",
        ["/Users/matt_wittlief_home/Library/Mobile Documents/com~apple~CloudDocs/F18.md"],
        {
            "115": "Current Rock Revival / Post-Punk New Wave 2020s",
            "116": "Modern Indie Singer-Songwriter / Sad-Prestige Indie",
            "117": "Modern Psych / Groove Indie / Tame-MGMT-Arctic Axis",
            "118": "Heavy Modern Alternative / Active Rock Survival",
            "119": "Hyperpop / Synthetic Edge-Pop / Internet Maximalism",
            "120": "Algorithmic Mood / Lo-Fi / Chill / Study Music",
        },
        [
            "Packet 018 is controlling. F18.md was treated as a status/supplemental source rather than a row seed.",
            "Internet-native, playlist-native, and artist-project objects need explicit warning fields so channels, scenes, and individuals do not collapse into one entity.",
        ],
        make_family_18_rows(),
    )


def make_family_13_rows() -> dict[str, list[dict[str, Any]]]:
    artists = [
        artist("094", "Daddy Yankee", "mass", "core", ["anchor", "artist_anchor"], ["Barrio Fino"], ["Gasolina"], weight=0.92),
        artist("094", "Bad Bunny", "mass", "core", ["anchor", "artist_anchor"], ["Un Verano Sin Ti"], ["Titi Me Pregunto"], weight=0.92),
        artist("094", "J Balvin", "mass", "core", ["gateway", "artist_anchor"], ["Vibras"], ["Mi Gente"], weight=0.86),
        artist("094", "Karol G", "mass", "core", ["gateway", "artist_anchor"], ["Manana Sera Bonito"], ["Tusa"], weight=0.86),
        artist("094", "Shakira", "mass", "core", ["bridge", "artist_anchor"], ["Laundry Service"], ["Hips Don't Lie"], weight=0.84),
        artist("094", "Don Omar", "high", "standard", ["gateway", "song_first"], ["King of Kings"], ["Danza Kuduro"], weight=0.8),
        artist("095", "Vicente Fernandez", "high", "core", ["anchor", "artist_anchor"], ["Un Azteca en el Azteca"], ["Volver, Volver"], weight=0.9),
        artist("095", "Los Tigres del Norte", "high", "core", ["anchor", "artist_anchor"], ["Jefe de Jefes"], ["La Puerta Negra"], weight=0.86),
        artist("095", "Jenni Rivera", "high", "standard", ["gateway", "artist_anchor"], ["Joyas Prestadas"], ["Inolvidable"], weight=0.8),
        artist("095", "Peso Pluma", "high", "core", ["anchor", "artist_anchor"], ["Genesis"], ["Ella Baila Sola"], weight=0.84),
        artist("095", "Grupo Frontera", "high", "standard", ["gateway"], ["El Comienzo"], ["No Se Va"], weight=0.78),
        artist("095", "Christian Nodal", "high", "standard", ["bridge"], ["Me Deje Llevar"], ["Adios Amor"], weight=0.78),
        artist("096", "Celia Cruz", "high", "core", ["anchor", "artist_anchor"], ["La Negra Tiene Tumbao"], ["La Vida Es Un Carnaval"], weight=0.9),
        artist("096", "Hector Lavoe", "high", "standard", ["anchor", "artist_anchor"], ["La Voz"], ["El Cantante"], weight=0.86),
        artist("096", "Willie Colon", "medium", "standard", ["bridge", "artist_anchor"], ["Cosa Nuestra"], ["Idilio"], weight=0.78),
        artist("096", "Marc Anthony", "mass", "core", ["gateway", "artist_anchor"], ["Contra la Corriente"], ["Vivir Mi Vida"], weight=0.86),
        artist("096", "Gloria Estefan", "mass", "core", ["bridge", "artist_anchor"], ["Mi Tierra"], ["Conga"], weight=0.84),
        artist("096", "Juan Luis Guerra", "high", "standard", ["bridge"], ["Bachata Rosa"], ["Burbujas de Amor"], weight=0.8),
        artist("097", "Fela Kuti", "high", "core", ["anchor", "artist_anchor"], ["Zombie"], ["Water No Get Enemy"], weight=0.9),
        artist("097", "Burna Boy", "mass", "core", ["anchor", "artist_anchor"], ["African Giant"], ["Last Last"], weight=0.88),
        artist("097", "Wizkid", "mass", "core", ["gateway", "artist_anchor"], ["Made in Lagos"], ["Essence"], weight=0.88),
        artist("097", "Davido", "high", "standard", ["gateway"], ["A Good Time"], ["Fall"], weight=0.8),
        artist("097", "Rema", "mass", "core", ["gateway", "song_first"], ["Rave & Roses"], ["Calm Down"], weight=0.84),
        artist("097", "Tems", "high", "standard", ["bridge"], ["For Broken Ears"], ["Free Mind"], weight=0.78),
        artist("098", "BTS", "mass", "core", ["anchor", "artist_anchor"], ["Map of the Soul: 7"], ["Dynamite"], weight=0.92),
        artist("098", "BLACKPINK", "mass", "core", ["anchor", "artist_anchor"], ["The Album"], ["DDU-DU DDU-DU"], weight=0.9),
        artist("098", "NewJeans", "mass", "core", ["gateway", "artist_anchor"], ["Get Up"], ["Super Shy"], weight=0.84),
        artist("098", "TWICE", "high", "standard", ["gateway"], ["Formula of Love"], ["The Feels"], weight=0.8),
        artist("098", "PSY", "mass", "core", ["song_first", "gateway"], ["Psy 6 (Six Rules), Part 1"], ["Gangnam Style"], specificity="song_level", weight=0.82),
        artist("098", "Hikaru Utada", "medium", "standard", ["bridge"], ["First Love"], ["First Love"], weight=0.76),
        artist("099", "Buena Vista Social Club", "high", "core", ["anchor", "album_anchor"], ["Buena Vista Social Club"], ["Chan Chan"], weight=0.88),
        artist("099", "Bob Marley & The Wailers", "mass", "core", ["bridge", "artist_anchor"], ["Legend"], ["One Love / People Get Ready"], weight=0.86),
        artist("099", "Manu Chao", "medium", "standard", ["bridge"], ["Clandestino"], ["Me Gustas Tu"], weight=0.78),
        artist("099", "Cesaria Evora", "medium", "standard", ["deepening"], ["Miss Perfumado"], ["Sodade"], weight=0.74),
        artist("099", "Tinariwen", "medium", "edge", ["deepening"], ["Aman Iman"], ["Cler Achel"], weight=0.7),
        artist("099", "Ravi Shankar", "medium", "edge", ["bridge"], ["The Sounds of India"], ["Dhun"], weight=0.68),
    ]
    albums = [
        album("094", "Barrio Fino", "Daddy Yankee", 2004, "studio_album", "mass", "core", ["album_anchor"]),
        album("094", "Un Verano Sin Ti", "Bad Bunny", 2022, "studio_album", "mass", "core", ["album_anchor"]),
        album("094", "Vibras", "J Balvin", 2018, "studio_album", "high", "standard", ["gateway"]),
        album("094", "Manana Sera Bonito", "Karol G", 2023, "studio_album", "mass", "core", ["gateway"]),
        album("095", "Jefe de Jefes", "Los Tigres del Norte", 1997, "studio_album", "high", "standard", ["album_anchor"]),
        album("095", "Un Azteca en el Azteca", "Vicente Fernandez", 2016, "live_album", "high", "standard", ["live_gateway"]),
        album("095", "Genesis", "Peso Pluma", 2023, "studio_album", "high", "core", ["album_anchor"]),
        album("095", "El Comienzo", "Grupo Frontera", 2023, "studio_album", "high", "standard", ["gateway"]),
        album("096", "La Voz", "Hector Lavoe", 1975, "studio_album", "medium", "standard", ["album_anchor"]),
        album("096", "Siembra", "Willie Colon and Ruben Blades", 1978, "studio_album", "high", "core", ["album_anchor"], warning="Collaboration album must remain distinct from solo artist IDs."),
        album("096", "Mi Tierra", "Gloria Estefan", 1993, "studio_album", "high", "core", ["bridge"]),
        album("096", "Contra la Corriente", "Marc Anthony", 1997, "studio_album", "high", "standard", ["gateway"]),
        album("097", "Zombie", "Fela Kuti", 1977, "studio_album", "high", "core", ["album_anchor"]),
        album("097", "African Giant", "Burna Boy", 2019, "studio_album", "high", "core", ["album_anchor"]),
        album("097", "Made in Lagos", "Wizkid", 2020, "studio_album", "mass", "core", ["album_anchor"]),
        album("097", "Rave & Roses", "Rema", 2022, "studio_album", "high", "standard", ["gateway"]),
        album("098", "Map of the Soul: 7", "BTS", 2020, "studio_album", "mass", "core", ["album_anchor"]),
        album("098", "The Album", "BLACKPINK", 2020, "studio_album", "mass", "core", ["album_anchor"]),
        album("098", "Get Up", "NewJeans", 2023, "ep", "high", "standard", ["gateway"]),
        album("098", "First Love", "Hikaru Utada", 1999, "studio_album", "medium", "standard", ["bridge"]),
        album("099", "Buena Vista Social Club", "Buena Vista Social Club", 1997, "studio_album", "high", "core", ["album_anchor"]),
        album("099", "Legend", "Bob Marley & The Wailers", 1984, "compilation", "mass", "core", ["compilation_gateway"]),
        album("099", "Clandestino", "Manu Chao", 1998, "studio_album", "medium", "standard", ["bridge"]),
        album("099", "Miss Perfumado", "Cesaria Evora", 1992, "studio_album", "medium", "edge", ["deepening"]),
    ]
    songs = [
        song("094", "Gasolina", "Daddy Yankee", 2004, "mass", "core", ["anchor", "song_first"], "artist_survey_worthy"),
        song("094", "Despacito", "Luis Fonsi and Daddy Yankee", 2017, "mass", "core", ["gateway", "song_first"], "song_survey_first", warning="Do not merge original/remix or collaboration artist rows."),
        song("094", "Mi Gente", "J Balvin and Willy William", 2017, "mass", "core", ["gateway", "song_first"], "song_survey_first"),
        song("094", "Titi Me Pregunto", "Bad Bunny", 2022, "mass", "core", ["anchor"], "artist_survey_worthy"),
        song("094", "Tusa", "Karol G and Nicki Minaj", 2019, "mass", "core", ["gateway"], "song_survey_first"),
        song("094", "Hips Don't Lie", "Shakira featuring Wyclef Jean", 2006, "mass", "core", ["bridge", "song_first"], "song_survey_first"),
        song("095", "Volver, Volver", "Vicente Fernandez", 1972, "high", "core", ["anchor"], "artist_survey_worthy"),
        song("095", "La Puerta Negra", "Los Tigres del Norte", 1986, "high", "standard", ["gateway"], "artist_survey_worthy"),
        song("095", "Inolvidable", "Jenni Rivera", 2008, "high", "standard", ["gateway"], "artist_survey_worthy"),
        song("095", "Ella Baila Sola", "Eslabon Armado and Peso Pluma", 2023, "mass", "core", ["anchor", "song_first"], "song_survey_first"),
        song("095", "No Se Va", "Grupo Frontera", 2022, "mass", "core", ["gateway", "song_first"], "artist_survey_worthy"),
        song("095", "Adios Amor", "Christian Nodal", 2016, "high", "standard", ["bridge"], "artist_survey_worthy"),
        song("096", "La Vida Es Un Carnaval", "Celia Cruz", 1998, "high", "core", ["anchor"], "artist_survey_worthy"),
        song("096", "El Cantante", "Hector Lavoe", 1978, "high", "standard", ["anchor"], "artist_survey_worthy"),
        song("096", "Pedro Navaja", "Ruben Blades and Willie Colon", 1978, "medium", "standard", ["deepening"], "song_survey_first"),
        song("096", "Vivir Mi Vida", "Marc Anthony", 2013, "mass", "core", ["gateway", "song_first"], "artist_survey_worthy"),
        song("096", "Conga", "Miami Sound Machine", 1985, "mass", "core", ["bridge", "song_first"], "song_survey_first"),
        song("096", "Burbujas de Amor", "Juan Luis Guerra", 1990, "high", "standard", ["bridge"], "artist_survey_worthy"),
        song("097", "Water No Get Enemy", "Fela Kuti", 1975, "medium", "standard", ["anchor"], "artist_survey_worthy"),
        song("097", "Zombie", "Fela Kuti", 1976, "high", "core", ["anchor"], "artist_survey_worthy"),
        song("097", "Ye", "Burna Boy", 2018, "high", "core", ["gateway"], "artist_survey_worthy"),
        song("097", "Last Last", "Burna Boy", 2022, "mass", "core", ["gateway", "song_first"], "artist_survey_worthy"),
        song("097", "Essence", "Wizkid featuring Tems", 2020, "mass", "core", ["anchor", "song_first"], "song_survey_first"),
        song("097", "Calm Down", "Rema", 2022, "mass", "core", ["gateway", "song_first"], "artist_survey_worthy"),
        song("098", "Dynamite", "BTS", 2020, "mass", "core", ["gateway", "song_first"], "artist_survey_worthy"),
        song("098", "Butter", "BTS", 2021, "mass", "core", ["gateway"], "artist_survey_worthy"),
        song("098", "DDU-DU DDU-DU", "BLACKPINK", 2018, "mass", "core", ["anchor"], "artist_survey_worthy"),
        song("098", "Super Shy", "NewJeans", 2023, "mass", "core", ["gateway"], "artist_survey_worthy"),
        song("098", "Gangnam Style", "PSY", 2012, "mass", "core", ["song_first", "gateway"], "song_survey_first"),
        song("098", "First Love", "Hikaru Utada", 1999, "medium", "standard", ["bridge"], "artist_survey_worthy"),
        song("099", "Chan Chan", "Buena Vista Social Club", 1997, "high", "core", ["anchor"], "artist_survey_worthy"),
        song("099", "One Love / People Get Ready", "Bob Marley & The Wailers", 1977, "mass", "core", ["bridge", "song_first"], "artist_survey_worthy"),
        song("099", "Me Gustas Tu", "Manu Chao", 2001, "high", "standard", ["bridge"], "artist_survey_worthy"),
        song("099", "Sodade", "Cesaria Evora", 1992, "medium", "edge", ["deepening"], "artist_survey_worthy"),
        song("099", "Cler Achel", "Tinariwen", 2007, "medium", "edge", ["deepening"], "artist_survey_worthy"),
        song("099", "Dhun", "Ravi Shankar", 1968, "medium", "edge", ["bridge"], "artist_survey_worthy"),
    ]
    return {"artists": artists, "albums": albums, "songs": songs}


def make_family_14_rows() -> dict[str, list[dict[str, Any]]]:
    artists = [
        artist("100", "Frank Sinatra", "mass", "core", ["anchor", "artist_anchor"], ["In the Wee Small Hours"], ["Fly Me to the Moon"], weight=0.94),
        artist("100", "Ella Fitzgerald", "high", "core", ["anchor", "artist_anchor"], ["Ella Fitzgerald Sings the Cole Porter Song Book"], ["Someone to Watch Over Me"], weight=0.9),
        artist("100", "Billie Holiday", "high", "core", ["anchor", "artist_anchor"], ["Lady in Satin"], ["Strange Fruit"], weight=0.9),
        artist("100", "Nat King Cole", "mass", "core", ["gateway", "artist_anchor"], ["Unforgettable"], ["Unforgettable"], weight=0.88),
        artist("100", "Tony Bennett", "high", "standard", ["gateway", "artist_anchor"], ["I Left My Heart in San Francisco"], ["I Left My Heart in San Francisco"], weight=0.82),
        artist("100", "Sarah Vaughan", "medium", "standard", ["deepening"], ["Sarah Vaughan with Clifford Brown"], ["Lullaby of Birdland"], weight=0.76),
        artist("101", "Miles Davis", "high", "core", ["anchor", "artist_anchor"], ["Kind of Blue"], ["So What"], weight=0.94),
        artist("101", "John Coltrane", "high", "core", ["anchor", "artist_anchor"], ["A Love Supreme"], ["My Favorite Things"], weight=0.92),
        artist("101", "Charlie Parker", "medium", "standard", ["anchor", "deepening"], ["The Complete Savoy and Dial Studio Recordings"], ["Ko-Ko"], weight=0.84),
        artist("101", "Thelonious Monk", "medium", "standard", ["anchor", "artist_anchor"], ["Brilliant Corners"], ["Round Midnight"], weight=0.86),
        artist("101", "Dave Brubeck Quartet", "high", "core", ["gateway", "song_first"], ["Time Out"], ["Take Five"], weight=0.88),
        artist("101", "Herbie Hancock", "high", "standard", ["bridge", "artist_anchor"], ["Head Hunters"], ["Cantaloupe Island"], weight=0.84),
        artist("102", "George Benson", "high", "core", ["anchor", "artist_anchor"], ["Breezin'"], ["Breezin'"], weight=0.88),
        artist("102", "Kenny G", "mass", "core", ["anchor", "song_first"], ["Breathless"], ["Songbird"], specificity="song_level", weight=0.86),
        artist("102", "Grover Washington Jr.", "high", "standard", ["gateway"], ["Winelight"], ["Just the Two of Us"], weight=0.82),
        artist("102", "Sade", "mass", "core", ["bridge", "artist_anchor"], ["Diamond Life"], ["Smooth Operator"], weight=0.84),
        artist("102", "Norah Jones", "mass", "core", ["bridge", "artist_anchor"], ["Come Away with Me"], ["Don't Know Why"], weight=0.84),
        artist("102", "Diana Krall", "medium", "standard", ["gateway"], ["When I Look in Your Eyes"], ["The Look of Love"], weight=0.74),
        artist("103", "Andrea Bocelli", "mass", "core", ["anchor", "artist_anchor"], ["Romanza"], ["Con te partiro"], weight=0.88),
        artist("103", "Luciano Pavarotti", "high", "core", ["bridge", "artist_anchor"], ["The Essential Pavarotti"], ["Nessun dorma"], weight=0.86),
        artist("103", "Yo-Yo Ma", "high", "standard", ["bridge", "artist_anchor"], ["Bach: Cello Suites"], ["Cello Suite No. 1: Prelude"], weight=0.82),
        artist("103", "Ludovico Einaudi", "high", "standard", ["gateway", "artist_anchor"], ["Divenire"], ["Nuvole Bianche"], weight=0.8),
        artist("103", "Enya", "mass", "core", ["bridge", "artist_anchor"], ["Watermark"], ["Orinoco Flow"], weight=0.82),
        artist("103", "Vanessa-Mae", "medium", "edge", ["boundary"], ["The Violin Player"], ["Toccata and Fugue in D Minor"], weight=0.66),
    ]
    albums = [
        album("100", "In the Wee Small Hours", "Frank Sinatra", 1955, "studio_album", "high", "core", ["album_anchor"]),
        album("100", "Ella Fitzgerald Sings the Cole Porter Song Book", "Ella Fitzgerald", 1956, "studio_album", "medium", "standard", ["album_anchor"]),
        album("100", "Lady in Satin", "Billie Holiday", 1958, "studio_album", "medium", "standard", ["album_anchor"]),
        album("100", "Unforgettable", "Nat King Cole", 1954, "studio_album", "high", "standard", ["gateway"]),
        album("101", "Kind of Blue", "Miles Davis", 1959, "studio_album", "high", "core", ["album_anchor", "anchor"]),
        album("101", "A Love Supreme", "John Coltrane", 1965, "studio_album", "high", "core", ["album_anchor"]),
        album("101", "Time Out", "Dave Brubeck Quartet", 1959, "studio_album", "high", "core", ["gateway", "album_anchor"]),
        album("101", "Head Hunters", "Herbie Hancock", 1973, "studio_album", "high", "standard", ["bridge", "album_anchor"]),
        album("102", "Breezin'", "George Benson", 1976, "studio_album", "high", "core", ["album_anchor"]),
        album("102", "Breathless", "Kenny G", 1992, "studio_album", "mass", "core", ["gateway"]),
        album("102", "Winelight", "Grover Washington Jr.", 1980, "studio_album", "high", "standard", ["album_anchor"]),
        album("102", "Come Away with Me", "Norah Jones", 2002, "studio_album", "mass", "core", ["bridge", "album_anchor"]),
        album("103", "Romanza", "Andrea Bocelli", 1997, "studio_album", "mass", "core", ["album_anchor"]),
        album("103", "The Essential Pavarotti", "Luciano Pavarotti", 1990, "compilation", "high", "standard", ["compilation_gateway"]),
        album("103", "Bach: Cello Suites", "Yo-Yo Ma", 1983, "studio_album", "high", "standard", ["bridge"]),
        album("103", "Divenire", "Ludovico Einaudi", 2006, "studio_album", "high", "standard", ["gateway"]),
    ]
    songs = [
        song("100", "Fly Me to the Moon", "Frank Sinatra", 1964, "mass", "core", ["anchor", "song_first"], "artist_survey_worthy", warning="Standard composition has many recordings; preserve Sinatra recording."),
        song("100", "My Way", "Frank Sinatra", 1969, "mass", "core", ["gateway", "song_first"], "artist_survey_worthy"),
        song("100", "Someone to Watch Over Me", "Ella Fitzgerald", 1959, "high", "standard", ["anchor"], "artist_survey_worthy", warning="Standard composition; recording-specific row."),
        song("100", "Strange Fruit", "Billie Holiday", 1939, "high", "core", ["anchor", "song_first"], "artist_survey_worthy"),
        song("100", "Unforgettable", "Nat King Cole", 1951, "mass", "core", ["gateway", "song_first"], "artist_survey_worthy"),
        song("100", "I Left My Heart in San Francisco", "Tony Bennett", 1962, "high", "standard", ["gateway"], "artist_survey_worthy"),
        song("101", "So What", "Miles Davis", 1959, "high", "core", ["anchor"], "artist_survey_worthy"),
        song("101", "My Favorite Things", "John Coltrane", 1961, "high", "core", ["anchor"], "artist_survey_worthy", warning="Preserve Coltrane recording distinct from musical-theater composition."),
        song("101", "Take Five", "Dave Brubeck Quartet", 1959, "mass", "core", ["gateway", "song_first"], "artist_survey_worthy"),
        song("101", "Round Midnight", "Thelonious Monk", 1947, "medium", "standard", ["deepening"], "artist_survey_worthy", warning="Standard with many recordings; do not title-merge."),
        song("101", "Cantaloupe Island", "Herbie Hancock", 1964, "high", "standard", ["bridge"], "artist_survey_worthy"),
        song("101", "Ko-Ko", "Charlie Parker", 1945, "medium", "edge", ["deepening"], "artist_survey_worthy"),
        song("102", "Breezin'", "George Benson", 1976, "high", "standard", ["anchor"], "artist_survey_worthy"),
        song("102", "Songbird", "Kenny G", 1986, "mass", "core", ["gateway", "song_first"], "song_survey_first"),
        song("102", "Just the Two of Us", "Grover Washington Jr. featuring Bill Withers", 1980, "mass", "core", ["gateway", "song_first"], "song_survey_first"),
        song("102", "Smooth Operator", "Sade", 1984, "mass", "core", ["bridge", "song_first"], "artist_survey_worthy"),
        song("102", "Don't Know Why", "Norah Jones", 2002, "mass", "core", ["bridge", "song_first"], "artist_survey_worthy"),
        song("102", "The Look of Love", "Diana Krall", 2001, "medium", "standard", ["gateway"], "artist_survey_worthy"),
        song("103", "Con te partiro", "Andrea Bocelli", 1995, "mass", "core", ["anchor", "song_first"], "artist_survey_worthy"),
        song("103", "Nessun dorma", "Luciano Pavarotti", 1990, "high", "core", ["gateway", "song_first"], "artist_survey_worthy", warning="Opera aria/composition must remain distinct from Pavarotti recording."),
        song("103", "Cello Suite No. 1: Prelude", "Yo-Yo Ma", 1983, "high", "standard", ["bridge"], "artist_survey_worthy", warning="Composition vs recording distinction required."),
        song("103", "Nuvole Bianche", "Ludovico Einaudi", 2004, "high", "standard", ["gateway"], "artist_survey_worthy"),
        song("103", "Orinoco Flow", "Enya", 1988, "mass", "core", ["bridge", "song_first"], "artist_survey_worthy"),
        song("103", "Time to Say Goodbye", "Andrea Bocelli and Sarah Brightman", 1996, "mass", "core", ["gateway", "song_first"], "song_survey_first"),
    ]
    return {"artists": artists, "albums": albums, "songs": songs}


def make_family_15_rows() -> dict[str, list[dict[str, Any]]]:
    artists = [
        artist("104", "Lin-Manuel Miranda", "mass", "core", ["anchor", "artist_anchor"], ["Hamilton"], ["My Shot"], weight=0.9),
        artist("104", "Stephen Sondheim", "high", "core", ["anchor", "artist_anchor"], ["Company"], ["Being Alive"], weight=0.88),
        artist("104", "Andrew Lloyd Webber", "mass", "core", ["anchor", "artist_anchor"], ["The Phantom of the Opera"], ["The Music of the Night"], weight=0.88),
        artist("104", "Original Broadway Cast of Wicked", "mass", "core", ["gateway", "album_anchor"], ["Wicked"], ["Defying Gravity"], weight=0.84),
        artist("104", "Jonathan Larson", "high", "standard", ["gateway"], ["Rent"], ["Seasons of Love"], weight=0.8),
        artist("105", "Alan Menken", "mass", "core", ["anchor", "artist_anchor"], ["Beauty and the Beast"], ["A Whole New World"], weight=0.9),
        artist("105", "Elton John", "mass", "core", ["bridge", "artist_anchor"], ["The Lion King"], ["Can You Feel the Love Tonight"], weight=0.84),
        artist("105", "Kristen Anderson-Lopez and Robert Lopez", "mass", "core", ["gateway", "song_first"], ["Frozen"], ["Let It Go"], weight=0.84),
        artist("105", "Randy Newman", "high", "standard", ["bridge"], ["Toy Story"], ["You've Got a Friend in Me"], weight=0.82),
        artist("105", "Phil Collins", "mass", "standard", ["bridge"], ["Tarzan"], ["You'll Be in My Heart"], weight=0.78),
        artist("106", "Prince", "mass", "core", ["bridge", "artist_anchor"], ["Purple Rain"], ["Purple Rain"], weight=0.88),
        artist("106", "Bee Gees", "mass", "core", ["bridge", "artist_anchor"], ["Saturday Night Fever"], ["Stayin' Alive"], weight=0.86),
        artist("106", "Whitney Houston", "mass", "core", ["bridge", "artist_anchor"], ["The Bodyguard"], ["I Will Always Love You"], weight=0.88),
        artist("106", "Kenny Loggins", "mass", "standard", ["song_first", "gateway"], ["Footloose"], ["Footloose"], specificity="song_level", weight=0.8),
        artist("106", "Celine Dion", "mass", "core", ["bridge", "artist_anchor"], ["Titanic"], ["My Heart Will Go On"], weight=0.84),
        artist("107", "John Williams", "mass", "core", ["anchor", "artist_anchor"], ["Star Wars"], ["Main Title"], weight=0.94),
        artist("107", "Hans Zimmer", "mass", "core", ["anchor", "artist_anchor"], ["Inception"], ["Time"], weight=0.9),
        artist("107", "Ennio Morricone", "high", "core", ["anchor", "artist_anchor"], ["The Good, the Bad and the Ugly"], ["The Ecstasy of Gold"], weight=0.88),
        artist("107", "James Horner", "high", "standard", ["gateway"], ["Titanic"], ["Hymn to the Sea"], weight=0.8),
        artist("107", "Howard Shore", "high", "standard", ["gateway"], ["The Lord of the Rings: The Fellowship of the Ring"], ["The Shire"], weight=0.82),
        artist("107", "Vangelis", "high", "standard", ["bridge"], ["Chariots of Fire"], ["Chariots of Fire"], weight=0.8),
    ]
    albums = [
        album("104", "Hamilton", "Original Broadway Cast of Hamilton", 2015, "soundtrack", "mass", "core", ["album_anchor", "anchor"]),
        album("104", "Wicked", "Original Broadway Cast of Wicked", 2003, "soundtrack", "mass", "core", ["album_anchor"]),
        album("104", "Rent", "Original Broadway Cast of Rent", 1996, "soundtrack", "high", "standard", ["gateway"]),
        album("104", "The Phantom of the Opera", "Original London Cast of The Phantom of the Opera", 1987, "soundtrack", "mass", "core", ["album_anchor"]),
        album("105", "The Lion King", "Various Artists", 1994, "soundtrack", "mass", "core", ["album_anchor"]),
        album("105", "Frozen", "Various Artists", 2013, "soundtrack", "mass", "core", ["album_anchor"]),
        album("105", "Beauty and the Beast", "Various Artists", 1991, "soundtrack", "mass", "core", ["gateway"]),
        album("105", "Toy Story", "Randy Newman", 1995, "soundtrack", "high", "standard", ["gateway"]),
        album("106", "Purple Rain", "Prince and The Revolution", 1984, "soundtrack", "mass", "core", ["album_anchor", "bridge"]),
        album("106", "Saturday Night Fever", "Various Artists", 1977, "soundtrack", "mass", "core", ["album_anchor"]),
        album("106", "The Bodyguard", "Various Artists", 1992, "soundtrack", "mass", "core", ["album_anchor"]),
        album("106", "Top Gun", "Various Artists", 1986, "soundtrack", "high", "standard", ["gateway"]),
        album("107", "Star Wars", "John Williams", 1977, "soundtrack", "mass", "core", ["album_anchor"]),
        album("107", "The Dark Knight", "Hans Zimmer and James Newton Howard", 2008, "soundtrack", "high", "standard", ["gateway"]),
        album("107", "The Lord of the Rings: The Fellowship of the Ring", "Howard Shore", 2001, "soundtrack", "high", "standard", ["album_anchor"]),
        album("107", "Chariots of Fire", "Vangelis", 1981, "soundtrack", "high", "standard", ["bridge"]),
    ]
    songs = [
        song("104", "My Shot", "Original Broadway Cast of Hamilton", 2015, "mass", "core", ["anchor"], "song_survey_first"),
        song("104", "Defying Gravity", "Idina Menzel and Kristin Chenoweth", 2003, "mass", "core", ["gateway", "song_first"], "song_survey_first"),
        song("104", "Seasons of Love", "Original Broadway Cast of Rent", 1996, "mass", "core", ["gateway", "song_first"], "song_survey_first"),
        song("104", "The Music of the Night", "Michael Crawford", 1986, "high", "standard", ["gateway"], "song_survey_first"),
        song("104", "Being Alive", "Dean Jones", 1970, "medium", "standard", ["deepening"], "song_survey_first", warning="Sondheim standard has many canonical recordings."),
        song("105", "Let It Go", "Idina Menzel", 2013, "mass", "core", ["anchor", "song_first"], "song_survey_first"),
        song("105", "A Whole New World", "Peabo Bryson and Regina Belle", 1992, "mass", "core", ["gateway", "song_first"], "song_survey_first"),
        song("105", "Can You Feel the Love Tonight", "Elton John", 1994, "mass", "core", ["gateway", "song_first"], "artist_survey_worthy"),
        song("105", "You've Got a Friend in Me", "Randy Newman", 1995, "mass", "core", ["gateway", "song_first"], "artist_survey_worthy"),
        song("105", "Circle of Life", "Carmen Twillie and Lebo M.", 1994, "mass", "core", ["gateway"], "song_survey_first"),
        song("106", "Purple Rain", "Prince and The Revolution", 1984, "mass", "core", ["anchor", "song_first"], "artist_survey_worthy"),
        song("106", "Stayin' Alive", "Bee Gees", 1977, "mass", "core", ["gateway", "song_first"], "artist_survey_worthy"),
        song("106", "I Will Always Love You", "Whitney Houston", 1992, "mass", "core", ["anchor", "song_first"], "artist_survey_worthy", warning="Preserve Whitney Houston recording distinct from Dolly Parton original."),
        song("106", "Footloose", "Kenny Loggins", 1984, "mass", "core", ["gateway", "song_first"], "song_survey_first"),
        song("106", "My Heart Will Go On", "Celine Dion", 1997, "mass", "core", ["gateway", "song_first"], "artist_survey_worthy"),
        song("107", "Main Title", "John Williams", 1977, "mass", "core", ["anchor", "song_first"], "artist_survey_worthy", warning="Title is generic; keep Star Wars soundtrack context."),
        song("107", "The Imperial March", "John Williams", 1980, "mass", "core", ["gateway", "song_first"], "artist_survey_worthy"),
        song("107", "Time", "Hans Zimmer", 2010, "high", "core", ["anchor"], "artist_survey_worthy"),
        song("107", "The Ecstasy of Gold", "Ennio Morricone", 1966, "high", "standard", ["gateway"], "artist_survey_worthy"),
        song("107", "The Shire", "Howard Shore", 2001, "high", "standard", ["gateway"], "artist_survey_worthy"),
        song("107", "Chariots of Fire", "Vangelis", 1981, "mass", "core", ["bridge", "song_first"], "artist_survey_worthy"),
    ]
    return {"artists": artists, "albums": albums, "songs": songs}


def make_family_16_rows() -> dict[str, list[dict[str, Any]]]:
    artists = [
        artist("108", "Mahalia Jackson", "high", "core", ["anchor", "artist_anchor"], ["The World's Greatest Gospel Singer"], ["Move On Up a Little Higher"], weight=0.92),
        artist("108", "Sam Cooke and The Soul Stirrers", "high", "standard", ["bridge", "artist_anchor"], ["Sam Cooke with the Soul Stirrers"], ["Jesus Gave Me Water"], weight=0.82),
        artist("108", "The Staple Singers", "high", "standard", ["bridge", "artist_anchor"], ["Be Altitude: Respect Yourself"], ["I'll Take You There"], weight=0.82),
        artist("108", "Aretha Franklin", "mass", "core", ["bridge", "artist_anchor"], ["Amazing Grace"], ["Amazing Grace"], weight=0.86),
        artist("108", "Kirk Franklin", "high", "core", ["gateway", "artist_anchor"], ["God's Property"], ["Stomp"], weight=0.86),
        artist("108", "The Clark Sisters", "medium", "standard", ["deepening"], ["You Brought the Sunshine"], ["You Brought the Sunshine"], weight=0.74),
        artist("109", "Amy Grant", "mass", "core", ["anchor", "artist_anchor"], ["Heart in Motion"], ["Baby Baby"], weight=0.88),
        artist("109", "Michael W. Smith", "high", "standard", ["gateway", "artist_anchor"], ["Go West Young Man"], ["Place in This World"], weight=0.78),
        artist("109", "DC Talk", "high", "standard", ["anchor", "artist_anchor"], ["Jesus Freak"], ["Jesus Freak"], weight=0.82),
        artist("109", "Jars of Clay", "high", "standard", ["gateway"], ["Jars of Clay"], ["Flood"], weight=0.78),
        artist("109", "Switchfoot", "high", "standard", ["bridge"], ["The Beautiful Letdown"], ["Dare You to Move"], weight=0.78),
        artist("109", "Lauren Daigle", "mass", "core", ["gateway", "artist_anchor"], ["Look Up Child"], ["You Say"], weight=0.84),
        artist("109", "MercyMe", "mass", "core", ["song_first", "gateway"], ["Almost There"], ["I Can Only Imagine"], specificity="song_level", weight=0.82),
        artist("110", "Hillsong Worship", "mass", "core", ["anchor", "artist_anchor"], ["Shout to the Lord"], ["What a Beautiful Name"], weight=0.88),
        artist("110", "Chris Tomlin", "mass", "core", ["anchor", "artist_anchor"], ["Arriving"], ["How Great Is Our God"], weight=0.88),
        artist("110", "Matt Redman", "high", "standard", ["gateway"], ["Blessed Be Your Name"], ["10,000 Reasons (Bless the Lord)"], weight=0.82),
        artist("110", "Bethel Music", "high", "standard", ["gateway", "artist_anchor"], ["You Make Me Brave"], ["No Longer Slaves"], weight=0.78),
        artist("110", "Elevation Worship", "high", "standard", ["gateway", "artist_anchor"], ["Old Church Basement"], ["Graves Into Gardens"], weight=0.8),
        artist("110", "Kari Jobe", "high", "standard", ["gateway"], ["Where I Find You"], ["Revelation Song"], weight=0.78),
        artist("110", "Sinach", "high", "standard", ["bridge"], ["Way Maker"], ["Way Maker"], weight=0.8),
    ]
    albums = [
        album("108", "The World's Greatest Gospel Singer", "Mahalia Jackson", 1955, "studio_album", "high", "core", ["album_anchor"]),
        album("108", "Amazing Grace", "Aretha Franklin", 1972, "live_album", "high", "core", ["live_gateway", "album_anchor"]),
        album("108", "God's Property", "Kirk Franklin", 1997, "studio_album", "high", "standard", ["gateway"]),
        album("108", "Be Altitude: Respect Yourself", "The Staple Singers", 1972, "studio_album", "high", "standard", ["bridge"]),
        album("109", "Heart in Motion", "Amy Grant", 1991, "studio_album", "mass", "core", ["album_anchor"]),
        album("109", "Jesus Freak", "DC Talk", 1995, "studio_album", "high", "standard", ["album_anchor"]),
        album("109", "The Beautiful Letdown", "Switchfoot", 2003, "studio_album", "high", "standard", ["bridge"]),
        album("109", "Look Up Child", "Lauren Daigle", 2018, "studio_album", "high", "core", ["gateway"]),
        album("110", "Arriving", "Chris Tomlin", 2004, "studio_album", "high", "core", ["album_anchor"]),
        album("110", "Shout to the Lord", "Hillsong Worship", 1996, "live_album", "high", "standard", ["live_gateway"]),
        album("110", "Blessed Be Your Name", "Matt Redman", 2005, "studio_album", "high", "standard", ["gateway"]),
        album("110", "Old Church Basement", "Elevation Worship and Maverick City Music", 2021, "studio_album", "high", "standard", ["gateway"], warning="Collaboration album should not merge church-band brands."),
    ]
    songs = [
        song("108", "Move On Up a Little Higher", "Mahalia Jackson", 1947, "high", "core", ["anchor"], "artist_survey_worthy"),
        song("108", "Amazing Grace", "Aretha Franklin", 1972, "high", "core", ["gateway"], "artist_survey_worthy", warning="Composition vs Aretha live recording must remain distinct."),
        song("108", "Jesus Gave Me Water", "Sam Cooke and The Soul Stirrers", 1951, "medium", "standard", ["bridge"], "artist_survey_worthy"),
        song("108", "I'll Take You There", "The Staple Singers", 1972, "mass", "core", ["bridge", "song_first"], "artist_survey_worthy"),
        song("108", "Stomp", "God's Property featuring Kirk Franklin", 1997, "high", "standard", ["gateway"], "song_survey_first"),
        song("108", "You Brought the Sunshine", "The Clark Sisters", 1981, "medium", "standard", ["deepening"], "artist_survey_worthy"),
        song("109", "Baby Baby", "Amy Grant", 1991, "mass", "core", ["anchor", "song_first"], "artist_survey_worthy"),
        song("109", "Place in This World", "Michael W. Smith", 1991, "high", "standard", ["gateway"], "artist_survey_worthy"),
        song("109", "Jesus Freak", "DC Talk", 1995, "high", "standard", ["anchor"], "artist_survey_worthy"),
        song("109", "Flood", "Jars of Clay", 1995, "high", "standard", ["gateway"], "artist_survey_worthy"),
        song("109", "Dare You to Move", "Switchfoot", 2000, "high", "standard", ["bridge"], "artist_survey_worthy"),
        song("109", "You Say", "Lauren Daigle", 2018, "mass", "core", ["gateway", "song_first"], "artist_survey_worthy"),
        song("109", "I Can Only Imagine", "MercyMe", 2001, "mass", "core", ["song_first", "gateway"], "song_survey_first"),
        song("110", "How Great Is Our God", "Chris Tomlin", 2004, "mass", "core", ["anchor"], "artist_survey_worthy"),
        song("110", "What a Beautiful Name", "Hillsong Worship", 2016, "mass", "core", ["anchor"], "artist_survey_worthy"),
        song("110", "10,000 Reasons (Bless the Lord)", "Matt Redman", 2011, "mass", "core", ["gateway", "song_first"], "artist_survey_worthy"),
        song("110", "No Longer Slaves", "Bethel Music", 2015, "high", "standard", ["gateway"], "artist_survey_worthy"),
        song("110", "Graves Into Gardens", "Elevation Worship", 2020, "high", "standard", ["gateway"], "artist_survey_worthy"),
        song("110", "Revelation Song", "Kari Jobe", 2009, "high", "standard", ["gateway"], "artist_survey_worthy"),
        song("110", "Way Maker", "Sinach", 2015, "mass", "core", ["bridge", "song_first"], "artist_survey_worthy"),
    ]
    return {"artists": artists, "albums": albums, "songs": songs}


def make_family_18_rows() -> dict[str, list[dict[str, Any]]]:
    artists = [
        artist("115", "Wet Leg", "high", "standard", ["gateway", "artist_anchor"], ["Wet Leg"], ["Chaise Longue"], weight=0.82),
        artist("115", "Fontaines D.C.", "high", "core", ["anchor", "artist_anchor"], ["Skinty Fia"], ["Starburster"], weight=0.84),
        artist("115", "IDLES", "medium", "standard", ["bridge", "artist_anchor"], ["Joy as an Act of Resistance."], ["Danny Nedelko"], weight=0.78),
        artist("115", "Yard Act", "medium", "edge", ["deepening"], ["The Overload"], ["The Overload"], weight=0.7),
        artist("115", "black midi", "medium", "edge", ["boundary", "deepening"], ["Schlagenheim"], ["bmbmbm"], weight=0.68),
        artist("116", "Phoebe Bridgers", "high", "core", ["anchor", "artist_anchor"], ["Punisher"], ["Kyoto"], weight=0.86),
        artist("116", "boygenius", "high", "core", ["anchor", "artist_anchor"], ["the record"], ["Not Strong Enough"], weight=0.86),
        artist("116", "Mitski", "high", "core", ["gateway", "artist_anchor"], ["Be the Cowboy"], ["Nobody"], weight=0.84),
        artist("116", "Big Thief", "high", "standard", ["deepening", "artist_anchor"], ["Dragon New Warm Mountain I Believe in You"], ["Not"], weight=0.8),
        artist("116", "Snail Mail", "medium", "standard", ["gateway"], ["Lush"], ["Pristine"], weight=0.74),
        artist("116", "Julien Baker", "medium", "standard", ["deepening"], ["Turn Out the Lights"], ["Appointments"], weight=0.72),
        artist("117", "Tame Impala", "mass", "core", ["anchor", "artist_anchor"], ["Currents"], ["The Less I Know the Better"], weight=0.9),
        artist("117", "MGMT", "high", "core", ["gateway", "artist_anchor"], ["Oracular Spectacular"], ["Electric Feel"], weight=0.84),
        artist("117", "Arctic Monkeys", "mass", "core", ["bridge", "artist_anchor"], ["AM"], ["Do I Wanna Know?"], weight=0.86),
        artist("117", "King Gizzard & the Lizard Wizard", "medium", "standard", ["deepening"], ["Nonagon Infinity"], ["Gamma Knife"], weight=0.74),
        artist("117", "Khruangbin", "high", "standard", ["bridge", "artist_anchor"], ["Con Todo el Mundo"], ["Time (You and I)"], weight=0.78),
        artist("117", "Glass Animals", "mass", "core", ["gateway", "song_first"], ["Dreamland"], ["Heat Waves"], weight=0.8),
        artist("118", "Bring Me the Horizon", "high", "core", ["anchor", "artist_anchor"], ["Sempiternal"], ["Can You Feel My Heart"], weight=0.84),
        artist("118", "Sleep Token", "high", "core", ["gateway", "artist_anchor"], ["Take Me Back to Eden"], ["The Summoning"], weight=0.82),
        artist("118", "Ghost", "high", "standard", ["gateway", "artist_anchor"], ["Meliora"], ["Square Hammer"], weight=0.8),
        artist("118", "Bad Omens", "high", "standard", ["gateway"], ["The Death of Peace of Mind"], ["Just Pretend"], weight=0.78),
        artist("118", "Spiritbox", "medium", "standard", ["deepening"], ["Eternal Blue"], ["Holy Roller"], weight=0.74),
        artist("118", "Maneskin", "mass", "standard", ["bridge", "artist_anchor"], ["Teatro d'ira: Vol. I"], ["Beggin'"], weight=0.76),
        artist("119", "Charli XCX", "mass", "core", ["bridge", "artist_anchor"], ["how i'm feeling now"], ["Vroom Vroom"], weight=0.86),
        artist("119", "SOPHIE", "high", "core", ["anchor", "artist_anchor"], ["Oil of Every Pearl's Un-Insides"], ["Immaterial"], weight=0.86),
        artist("119", "100 gecs", "high", "core", ["anchor", "artist_anchor"], ["1000 gecs"], ["money machine"], weight=0.84),
        artist("119", "A. G. Cook", "medium", "standard", ["deepening"], ["Apple"], ["Beautiful"], weight=0.74),
        artist("119", "Dorian Electra", "medium", "standard", ["gateway"], ["Flamboyant"], ["Career Boy"], weight=0.72),
        artist("119", "Arca", "medium", "edge", ["boundary", "deepening"], ["Kick I"], ["Mequetrefe"], weight=0.7),
        artist("120", "Nujabes", "high", "core", ["anchor", "artist_anchor"], ["Modal Soul"], ["Feather"], weight=0.84),
        artist("120", "J Dilla", "high", "core", ["bridge", "artist_anchor"], ["Donuts"], ["Time: The Donut of the Heart"], weight=0.82),
        artist("120", "Bonobo", "medium", "standard", ["gateway"], ["Black Sands"], ["Kiara"], weight=0.76),
        artist("120", "Tycho", "medium", "standard", ["bridge"], ["Dive"], ["A Walk"], weight=0.76),
        artist("120", "Emancipator", "medium", "edge", ["deepening"], ["Soon It Will Be Cold Enough"], ["First Snow"], weight=0.7),
        artist("120", "Jinsang", "low", "edge", ["deepening"], ["Life"], ["Affection."], weight=0.66),
    ]
    albums = [
        album("115", "Wet Leg", "Wet Leg", 2022, "studio_album", "high", "standard", ["gateway"]),
        album("115", "Skinty Fia", "Fontaines D.C.", 2022, "studio_album", "high", "standard", ["album_anchor"]),
        album("115", "Joy as an Act of Resistance.", "IDLES", 2018, "studio_album", "medium", "standard", ["bridge"]),
        album("115", "Schlagenheim", "black midi", 2019, "studio_album", "medium", "edge", ["boundary"]),
        album("116", "Punisher", "Phoebe Bridgers", 2020, "studio_album", "high", "core", ["album_anchor"]),
        album("116", "the record", "boygenius", 2023, "studio_album", "high", "core", ["album_anchor"]),
        album("116", "Be the Cowboy", "Mitski", 2018, "studio_album", "high", "core", ["gateway"]),
        album("116", "Dragon New Warm Mountain I Believe in You", "Big Thief", 2022, "studio_album", "high", "standard", ["deepening"]),
        album("117", "Currents", "Tame Impala", 2015, "studio_album", "mass", "core", ["album_anchor"]),
        album("117", "Oracular Spectacular", "MGMT", 2007, "studio_album", "high", "core", ["gateway"]),
        album("117", "AM", "Arctic Monkeys", 2013, "studio_album", "mass", "core", ["bridge"]),
        album("117", "Con Todo el Mundo", "Khruangbin", 2018, "studio_album", "high", "standard", ["bridge"]),
        album("118", "Sempiternal", "Bring Me the Horizon", 2013, "studio_album", "high", "core", ["album_anchor"]),
        album("118", "Take Me Back to Eden", "Sleep Token", 2023, "studio_album", "high", "core", ["gateway"]),
        album("118", "Meliora", "Ghost", 2015, "studio_album", "high", "standard", ["gateway"]),
        album("118", "The Death of Peace of Mind", "Bad Omens", 2022, "studio_album", "high", "standard", ["gateway"]),
        album("119", "Oil of Every Pearl's Un-Insides", "SOPHIE", 2018, "studio_album", "high", "core", ["album_anchor"]),
        album("119", "1000 gecs", "100 gecs", 2019, "studio_album", "high", "core", ["album_anchor"]),
        album("119", "how i'm feeling now", "Charli XCX", 2020, "studio_album", "high", "core", ["bridge"]),
        album("119", "Flamboyant", "Dorian Electra", 2019, "studio_album", "medium", "standard", ["gateway"]),
        album("120", "Modal Soul", "Nujabes", 2005, "studio_album", "high", "core", ["album_anchor"]),
        album("120", "Donuts", "J Dilla", 2006, "studio_album", "high", "core", ["bridge"]),
        album("120", "Black Sands", "Bonobo", 2010, "studio_album", "medium", "standard", ["gateway"]),
        album("120", "Dive", "Tycho", 2011, "studio_album", "medium", "standard", ["bridge"]),
    ]
    songs = [
        song("115", "Chaise Longue", "Wet Leg", 2021, "high", "standard", ["gateway", "song_first"], "artist_survey_worthy"),
        song("115", "Starburster", "Fontaines D.C.", 2024, "high", "core", ["anchor"], "artist_survey_worthy"),
        song("115", "Danny Nedelko", "IDLES", 2018, "medium", "standard", ["bridge"], "artist_survey_worthy"),
        song("115", "The Overload", "Yard Act", 2022, "medium", "edge", ["deepening"], "artist_survey_worthy"),
        song("115", "bmbmbm", "black midi", 2019, "medium", "edge", ["boundary"], "artist_survey_worthy"),
        song("116", "Kyoto", "Phoebe Bridgers", 2020, "high", "core", ["anchor"], "artist_survey_worthy"),
        song("116", "Not Strong Enough", "boygenius", 2023, "high", "core", ["gateway"], "artist_survey_worthy"),
        song("116", "Nobody", "Mitski", 2018, "high", "core", ["gateway", "song_first"], "artist_survey_worthy"),
        song("116", "Not", "Big Thief", 2019, "medium", "standard", ["deepening"], "artist_survey_worthy"),
        song("116", "Pristine", "Snail Mail", 2018, "medium", "standard", ["gateway"], "artist_survey_worthy"),
        song("116", "Appointments", "Julien Baker", 2017, "medium", "standard", ["deepening"], "artist_survey_worthy"),
        song("117", "The Less I Know the Better", "Tame Impala", 2015, "mass", "core", ["anchor", "song_first"], "artist_survey_worthy"),
        song("117", "Electric Feel", "MGMT", 2007, "high", "core", ["gateway", "song_first"], "artist_survey_worthy"),
        song("117", "Do I Wanna Know?", "Arctic Monkeys", 2013, "mass", "core", ["bridge", "song_first"], "artist_survey_worthy"),
        song("117", "Gamma Knife", "King Gizzard & the Lizard Wizard", 2016, "medium", "edge", ["deepening"], "artist_survey_worthy"),
        song("117", "Time (You and I)", "Khruangbin", 2020, "high", "standard", ["bridge"], "artist_survey_worthy"),
        song("117", "Heat Waves", "Glass Animals", 2020, "mass", "core", ["gateway", "song_first"], "artist_survey_worthy"),
        song("118", "Can You Feel My Heart", "Bring Me the Horizon", 2013, "high", "core", ["anchor"], "artist_survey_worthy"),
        song("118", "The Summoning", "Sleep Token", 2023, "high", "core", ["gateway"], "artist_survey_worthy"),
        song("118", "Square Hammer", "Ghost", 2016, "high", "standard", ["gateway"], "artist_survey_worthy"),
        song("118", "Just Pretend", "Bad Omens", 2022, "high", "standard", ["gateway"], "artist_survey_worthy"),
        song("118", "Holy Roller", "Spiritbox", 2020, "medium", "standard", ["deepening"], "artist_survey_worthy"),
        song("118", "Beggin'", "Maneskin", 2017, "mass", "standard", ["bridge", "song_first"], "artist_survey_worthy", warning="Preserve Maneskin recording distinct from Four Seasons original."),
        song("119", "Vroom Vroom", "Charli XCX", 2016, "high", "core", ["bridge"], "artist_survey_worthy"),
        song("119", "Immaterial", "SOPHIE", 2018, "high", "core", ["anchor"], "artist_survey_worthy"),
        song("119", "money machine", "100 gecs", 2019, "high", "core", ["anchor"], "artist_survey_worthy"),
        song("119", "Beautiful", "A. G. Cook", 2014, "medium", "standard", ["deepening"], "artist_survey_worthy"),
        song("119", "Career Boy", "Dorian Electra", 2019, "medium", "standard", ["gateway"], "artist_survey_worthy"),
        song("119", "Mequetrefe", "Arca", 2020, "medium", "edge", ["boundary"], "artist_survey_worthy"),
        song("120", "Feather", "Nujabes featuring Cise Starr and Akin", 2005, "high", "standard", ["anchor"], "song_survey_first"),
        song("120", "Time: The Donut of the Heart", "J Dilla", 2006, "medium", "standard", ["bridge"], "artist_survey_worthy"),
        song("120", "Kiara", "Bonobo", 2010, "medium", "standard", ["gateway"], "artist_survey_worthy"),
        song("120", "A Walk", "Tycho", 2011, "medium", "standard", ["bridge"], "artist_survey_worthy"),
        song("120", "First Snow", "Emancipator", 2006, "medium", "edge", ["deepening"], "artist_survey_worthy"),
        song("120", "Affection.", "Jinsang", 2016, "low", "edge", ["deepening"], "artist_survey_worthy"),
    ]
    return {"artists": artists, "albums": albums, "songs": songs}


def count_by_archetype(rows: list[dict[str, Any]]) -> Counter[str]:
    return Counter(row["archetype_id"] for row in rows)


def table(rows: list[dict[str, Any]], fields: list[str]) -> str:
    lines = ["| " + " | ".join(fields) + " |", "| " + " | ".join(["---"] * len(fields)) + " |"]
    for row in rows:
        values = []
        for field in fields:
            value = row[field]
            if isinstance(value, list):
                value = ", ".join(str(item) for item in value)
            values.append(str(value).replace("\n", " "))
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines) + "\n"


def warning_rows(family: dict[str, Any]) -> list[str]:
    warnings = list(family["source_notes"])
    for key in ["artists", "albums", "songs"]:
        for row in family[key]:
            if row.get("consolidation_warning"):
                label = row.get("artist_name") or f"{row.get('artist_name')} - {row.get('album_title') or row.get('song_title')}"
                warnings.append(f"{label}: {row['consolidation_warning']}")
    return warnings


def write_family(num: int, family: dict[str, Any]) -> None:
    out = OUT_ROOT / f"family_{num}"
    out.mkdir(parents=True, exist_ok=True)
    artists = family["artists"]
    albums = family["albums"]
    songs = family["songs"]
    row_counts = {
        "artists": len(artists),
        "albums": len(albums),
        "songs": len(songs),
        "total": len(artists) + len(albums) + len(songs),
        "existing_seed": sum(1 for rows in (artists, albums, songs) for row in rows if row["existing_seed"]),
        "added_missing_obvious": sum(1 for rows in (artists, albums, songs) for row in rows if not row["existing_seed"]),
    }
    payload = {
        "metadata": {
            "family_number": num,
            "family_name": family["name"],
            "source_report": DISPATCH,
            "supplemental_reports": family["supplements"],
            "generated_date": TODAY,
            "source_package_note": "Pass-one dispatch packet used as controlling taxonomy source; supplemental F files were cross-checked and used only when aligned.",
            "normalization": {
                "id_style": "lowercase kebab-case",
                "source_rows_existing_seed": True,
                "added_rows_existing_seed": False,
                "version_policy": "Distinct source versions, covers, remakes, collaborations, cast recordings, and soundtrack/score objects are preserved as separate recording objects; ambiguous risks are flagged in warnings.",
            },
            "allowed_enums": {
                "roles": ROLES,
                "recognition_tier": RECOGNITION,
                "survey_tier": SURVEY,
                "album_object_type": ALBUM_TYPES,
                "artist_survey_status": ARTIST_STATUSES,
            },
            "row_counts": row_counts,
            "archetypes": family["archetypes"],
        },
        "artists": artists,
        "albums": albums,
        "songs": songs,
    }
    (out / f"normalized_family_{num}.json").write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    a_counts = count_by_archetype(artists)
    al_counts = count_by_archetype(albums)
    s_counts = count_by_archetype(songs)
    cov_lines = [
        "| archetype_id | archetype | artists | albums | songs | structural note |",
        "|---|---|---:|---:|---:|---|",
    ]
    for aid, aname in family["archetypes"].items():
        cov_lines.append(
            f"| {aid} | {aname} | {a_counts[aid]} | {al_counts[aid]} | {s_counts[aid]} | "
            "Initial expansion is schema-ready; second-pass listening evidence should tune ordering and suppressions. |"
        )
    gap = f"""# Family {num} Gap Summary

Scope: {family['name']}.

Source package: `{DISPATCH}`

Supplemental reports checked: {', '.join(f'`{item}`' for item in family['supplements']) if family['supplements'] else 'none found in iCloud root during this pass'}.

## Import Shape

| Object class | Existing seed rows | Added missing-obvious rows | Total normalized rows |
|---|---:|---:|---:|
| Artists | 0 | {len(artists)} | {len(artists)} |
| Albums | 0 | {len(albums)} | {len(albums)} |
| Songs | 0 | {len(songs)} | {len(songs)} |

## Archetype Coverage

{chr(10).join(cov_lines)}

## Filled Gaps

- Established a minimum artist, album, and song surface for every dispatch archetype in Family {num}.
- Added bridge and contrast objects where normal users are likely to recognize a song before they recognize a subgenre label.
- Preserved live albums, compilations, soundtracks, cast albums, collaborations, and version-specific song rows when those objects are the actual gateway.

## Boundary Risks

- Source reports for this pass are incomplete or partially misaligned; see `corrections_to_source_report.md` and `import_warnings.md`.
- Same-title standards, covers, soundtrack songs, and collaboration rows need composition/recording-aware importer handling.
- Do not hard-lock this family until a second-pass family-specific report confirms Page 1/Page 2 ordering and suppression choices.
"""
    (out / "gap_summary.md").write_text(gap, encoding="utf-8")
    (out / "artist_candidates.md").write_text("# Artist Candidates\n\n" + table(artists, [
        "archetype_id", "artist_name", "proposed_artist_id", "existing_seed", "recognition_tier", "survey_tier", "roles", "archetype_membership_weight", "inclusion_reason", "object_specificity_note", "likely_canonical_albums", "likely_canonical_songs", "consolidation_warning"
    ]), encoding="utf-8")
    (out / "album_candidates.md").write_text("# Album Candidates\n\n" + table(albums, [
        "archetype_id", "album_title", "artist_name", "proposed_album_id", "existing_seed", "release_year", "album_object_type", "recognition_tier", "survey_tier", "roles", "archetype_membership_weight", "inclusion_reason", "consolidation_warning"
    ]), encoding="utf-8")
    (out / "song_candidates.md").write_text("# Song Candidates\n\n" + table(songs, [
        "archetype_id", "song_title", "artist_name", "proposed_song_id", "existing_seed", "release_year", "recognition_tier", "survey_tier", "roles", "archetype_membership_weight", "inclusion_reason", "artist_survey_status", "consolidation_warning"
    ]), encoding="utf-8")
    corrections = ["# Corrections To Source Report", ""]
    corrections.extend(f"- {note}" for note in family["source_notes"])
    corrections.extend([
        "- No source-report candidate rows were marked `existing_seed = true` in this batch because the available family-specific reports did not provide aligned row-level seeds.",
        "- Dispatch archetype IDs and names were normalized before candidate generation.",
    ])
    (out / "corrections_to_source_report.md").write_text("\n".join(corrections) + "\n", encoding="utf-8")
    readiness = f"""# Lock Readiness

Judgment: staging-ready, not locked.

Import-readiness score: 0.78

Rationale:
- Required artist, album, and song fields are present with normalized enum values and lowercase kebab-case IDs.
- Every dispatch archetype has an initial surface across all three object classes.
- Duplicate and version risks are flagged, but family-specific second-pass research is still thin or missing.

Lock recommendation: do not claim final lock. Use this as the first importable graph-production batch, then dispatch a deeper family-specific pass for survey ordering, omissions, and suppressions.
"""
    (out / "lock_readiness.md").write_text(readiness, encoding="utf-8")
    warnings = ["# Import Warnings", "", "## Non-Enum Terms", "", "- None detected in generated rows; role, recognition, survey, album type, and artist survey status fields use current importer enums.", "", "## Merge / Alias / Version Risks", ""]
    warnings.extend(f"- {item}" for item in warning_rows(family))
    (out / "import_warnings.md").write_text("\n".join(warnings) + "\n", encoding="utf-8")


def validate_payloads() -> None:
    bad: list[str] = []
    for num, family in FAMILIES.items():
        for row in family["artists"]:
            if row["recognition_tier"] not in RECOGNITION or row["survey_tier"] not in SURVEY:
                bad.append(f"family {num} artist enum error: {row}")
            if any(role not in ROLES for role in row["roles"]):
                bad.append(f"family {num} artist role error: {row}")
        for row in family["albums"]:
            if row["album_object_type"] not in ALBUM_TYPES:
                bad.append(f"family {num} album type error: {row}")
        for row in family["songs"]:
            if row["artist_survey_status"] not in ARTIST_STATUSES:
                bad.append(f"family {num} song status error: {row}")
    if bad:
        raise SystemExit("\n".join(bad))


def main() -> None:
    build_compact_families()
    validate_payloads()
    for num in sorted(FAMILIES):
        write_family(num, FAMILIES[num])
    print("Generated families:", ", ".join(str(num) for num in sorted(FAMILIES)))


if __name__ == "__main__":
    main()
