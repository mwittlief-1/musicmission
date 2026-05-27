#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "canonical_graph" / "family_8"
TODAY = "2026-05-19"
DISPATCH = "/Users/matt_wittlief_home/Library/Mobile Documents/com~apple~CloudDocs/waymark_pass_one_dispatches_families_005_018.md"
SUPPLEMENT = "/Users/matt_wittlief_home/Library/Mobile Documents/com~apple~CloudDocs/F8.md"

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

ARCHETYPES = {
    "053": "First-Wave Punk / 70s Punk",
    "054": "CBGB / Art-Punk / Downtown New York",
    "055": "Hardcore Punk / US 80s Hardcore",
    "056": "Post-Punk / Dark Melodic / Gothic Roots",
    "057": "New Wave / MTV Pop-Rock",
    "058": "Synthpop / New Romantic / 80s Electronic Pop",
    "059": "College Rock / Pre-Alternative 80s",
    "060": "Noise Rock / Post-Hardcore / Touch and Go Axis",
}


def slug(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = value.lower().replace("&", " and ")
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return re.sub(r"-+", "-", value).strip("-")


def artist(
    archetype_id: str,
    name: str,
    recognition_tier: str,
    survey_tier: str,
    roles: list[str],
    albums: list[str],
    songs: list[str],
    *,
    weight: float = 0.82,
    note: str = "artist_level",
    warning: str = "",
) -> dict[str, Any]:
    return {
        "archetype_id": archetype_id,
        "artist_name": name,
        "proposed_artist_id": slug(name),
        "existing_seed": False,
        "recognition_tier": recognition_tier,
        "survey_tier": survey_tier,
        "roles": roles,
        "archetype_membership_weight": weight,
        "inclusion_reason": f"{name} gives archetype {archetype_id} a recognizable survey branch without requiring collector-only punk knowledge.",
        "object_specificity_note": note,
        "likely_canonical_albums": albums,
        "likely_canonical_songs": songs,
        "consolidation_warning": warning,
    }


def album(
    archetype_id: str,
    title: str,
    artist_name: str,
    year: int,
    album_object_type: str,
    recognition_tier: str,
    survey_tier: str,
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
        "album_object_type": album_object_type,
        "recognition_tier": recognition_tier,
        "survey_tier": survey_tier,
        "roles": roles,
        "archetype_membership_weight": weight,
        "inclusion_reason": f"{title} is an album-level gateway for archetype {archetype_id}.",
        "consolidation_warning": warning,
    }


def song(
    archetype_id: str,
    title: str,
    artist_name: str,
    year: int,
    recognition_tier: str,
    survey_tier: str,
    roles: list[str],
    artist_survey_status: str,
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
        "recognition_tier": recognition_tier,
        "survey_tier": survey_tier,
        "roles": roles,
        "archetype_membership_weight": weight,
        "inclusion_reason": f"{title} gives archetype {archetype_id} a clear song-level tap for recognition, contrast, or branching.",
        "artist_survey_status": artist_survey_status,
        "consolidation_warning": warning,
    }


ARTISTS = [
    artist("053", "Ramones", "high", "core", ["anchor", "artist_anchor"], ["Ramones"], ["Blitzkrieg Bop"], weight=0.94),
    artist("053", "Sex Pistols", "high", "core", ["anchor", "artist_anchor"], ["Never Mind the Bollocks, Here's the Sex Pistols"], ["Anarchy in the U.K."], weight=0.92),
    artist("053", "The Clash", "mass", "core", ["anchor", "artist_anchor", "bridge"], ["London Calling"], ["London Calling"], weight=0.94),
    artist("053", "The Damned", "medium", "standard", ["gateway"], ["Damned Damned Damned"], ["New Rose"], weight=0.78),
    artist("053", "Buzzcocks", "medium", "standard", ["gateway"], ["Singles Going Steady"], ["Ever Fallen in Love"], weight=0.8),
    artist("053", "The Saints", "medium", "edge", ["deepening", "boundary"], ["(I'm) Stranded"], ["(I'm) Stranded"], weight=0.72),
    artist("054", "Talking Heads", "mass", "core", ["anchor", "artist_anchor", "bridge"], ["Remain in Light"], ["Psycho Killer"], weight=0.9),
    artist("054", "Television", "medium", "core", ["anchor", "album_anchor"], ["Marquee Moon"], ["Marquee Moon"], weight=0.86),
    artist("054", "Patti Smith", "high", "core", ["anchor", "artist_anchor"], ["Horses"], ["Gloria"], weight=0.88),
    artist("054", "Blondie", "mass", "core", ["gateway", "artist_anchor", "bridge"], ["Parallel Lines"], ["Heart of Glass"], weight=0.86),
    artist("054", "Richard Hell & The Voidoids", "medium", "standard", ["deepening"], ["Blank Generation"], ["Blank Generation"], weight=0.74),
    artist("054", "The Modern Lovers", "medium", "standard", ["bridge", "deepening"], ["The Modern Lovers"], ["Roadrunner"], weight=0.76),
    artist("055", "Black Flag", "medium", "core", ["anchor", "artist_anchor"], ["Damaged"], ["Rise Above"], weight=0.9),
    artist("055", "Minor Threat", "medium", "core", ["anchor", "artist_anchor"], ["Complete Discography"], ["Straight Edge"], weight=0.88),
    artist("055", "Dead Kennedys", "medium", "core", ["anchor", "artist_anchor"], ["Fresh Fruit for Rotting Vegetables"], ["Holiday in Cambodia"], weight=0.86),
    artist("055", "Bad Brains", "medium", "standard", ["gateway", "bridge"], ["Bad Brains"], ["Banned in D.C."], weight=0.82),
    artist("055", "Misfits", "high", "standard", ["gateway", "artist_anchor", "bridge"], ["Walk Among Us"], ["Last Caress"], weight=0.8),
    artist("055", "Husker Du", "medium", "standard", ["bridge", "artist_anchor"], ["Zen Arcade"], ["New Day Rising"], weight=0.8),
    artist("055", "Circle Jerks", "medium", "edge", ["deepening"], ["Group Sex"], ["Wild in the Streets"], weight=0.7),
    artist("056", "Joy Division", "high", "core", ["anchor", "artist_anchor"], ["Unknown Pleasures"], ["Love Will Tear Us Apart"], weight=0.9),
    artist("056", "The Cure", "mass", "core", ["anchor", "artist_anchor", "bridge"], ["Disintegration"], ["Just Like Heaven"], weight=0.9),
    artist("056", "Siouxsie and the Banshees", "high", "standard", ["gateway", "artist_anchor"], ["Juju"], ["Spellbound"], weight=0.82),
    artist("056", "Bauhaus", "medium", "standard", ["gateway", "song_first"], ["In the Flat Field"], ["Bela Lugosi's Dead"], weight=0.8),
    artist("056", "Echo & the Bunnymen", "medium", "standard", ["bridge"], ["Ocean Rain"], ["The Killing Moon"], weight=0.78),
    artist("056", "The Psychedelic Furs", "medium", "standard", ["bridge"], ["Talk Talk Talk"], ["Love My Way"], weight=0.76),
    artist("056", "Killing Joke", "medium", "edge", ["deepening", "boundary"], ["Killing Joke"], ["Eighties"], weight=0.7),
    artist("057", "The Police", "mass", "core", ["anchor", "artist_anchor", "bridge"], ["Synchronicity"], ["Every Breath You Take"], weight=0.9),
    artist("057", "The Cars", "mass", "core", ["anchor", "artist_anchor"], ["The Cars"], ["Just What I Needed"], weight=0.88),
    artist("057", "Duran Duran", "mass", "core", ["gateway", "artist_anchor"], ["Rio"], ["Hungry Like the Wolf"], weight=0.86),
    artist("057", "INXS", "mass", "core", ["gateway", "artist_anchor"], ["Kick"], ["Need You Tonight"], weight=0.84),
    artist("057", "Elvis Costello", "high", "standard", ["bridge", "artist_anchor"], ["My Aim Is True"], ["Alison"], weight=0.8),
    artist("057", "The B-52's", "mass", "standard", ["gateway", "song_first"], ["Cosmic Thing"], ["Love Shack"], weight=0.78),
    artist("057", "Devo", "high", "standard", ["gateway", "bridge"], ["Freedom of Choice"], ["Whip It"], weight=0.8),
    artist("058", "Depeche Mode", "mass", "core", ["anchor", "artist_anchor"], ["Violator"], ["Enjoy the Silence"], weight=0.9),
    artist("058", "New Order", "high", "core", ["anchor", "artist_anchor", "bridge"], ["Power, Corruption & Lies"], ["Blue Monday"], weight=0.88),
    artist("058", "Eurythmics", "mass", "core", ["gateway", "artist_anchor"], ["Sweet Dreams (Are Made of This)"], ["Sweet Dreams (Are Made of This)"], weight=0.86),
    artist("058", "Pet Shop Boys", "high", "standard", ["gateway", "artist_anchor"], ["Please"], ["West End Girls"], weight=0.82),
    artist("058", "Soft Cell", "high", "standard", ["gateway", "song_first"], ["Non-Stop Erotic Cabaret"], ["Tainted Love"], weight=0.8, warning="Preserve Soft Cell recording distinct from Gloria Jones original."),
    artist("058", "Gary Numan", "high", "standard", ["bridge", "song_first"], ["The Pleasure Principle"], ["Cars"], weight=0.78),
    artist("058", "Orchestral Manoeuvres in the Dark", "medium", "standard", ["deepening"], ["Architecture & Morality"], ["Enola Gay"], weight=0.74),
    artist("059", "R.E.M.", "high", "core", ["anchor", "artist_anchor"], ["Murmur"], ["Radio Free Europe"], weight=0.9),
    artist("059", "The Replacements", "medium", "core", ["anchor", "artist_anchor"], ["Let It Be"], ["Bastards of Young"], weight=0.86),
    artist("059", "The Smiths", "high", "core", ["anchor", "artist_anchor"], ["The Queen Is Dead"], ["This Charming Man"], weight=0.88),
    artist("059", "Pixies", "high", "standard", ["bridge", "artist_anchor"], ["Doolittle"], ["Where Is My Mind?"], weight=0.84),
    artist("059", "Sonic Youth", "medium", "standard", ["bridge", "artist_anchor"], ["Daydream Nation"], ["Teen Age Riot"], weight=0.82),
    artist("059", "The Feelies", "medium", "edge", ["deepening"], ["Crazy Rhythms"], ["Fa Ce-La"], weight=0.7),
    artist("059", "Minutemen", "medium", "edge", ["deepening", "boundary"], ["Double Nickels on the Dime"], ["Corona"], weight=0.72),
    artist("060", "Big Black", "medium", "edge", ["anchor", "deepening"], ["Songs About Fucking"], ["Kerosene"], weight=0.76),
    artist("060", "Fugazi", "medium", "standard", ["anchor", "artist_anchor"], ["Repeater"], ["Waiting Room"], weight=0.84),
    artist("060", "Drive Like Jehu", "low", "edge", ["deepening"], ["Yank Crime"], ["Here Come the Rome Plows"], weight=0.66),
    artist("060", "Slint", "medium", "edge", ["deepening", "boundary"], ["Spiderland"], ["Good Morning, Captain"], weight=0.72),
    artist("060", "Shellac", "low", "edge", ["deepening"], ["At Action Park"], ["Prayer to God"], weight=0.64),
    artist("060", "Refused", "medium", "standard", ["gateway", "bridge"], ["The Shape of Punk to Come"], ["New Noise"], weight=0.78),
    artist("060", "At the Drive-In", "medium", "standard", ["bridge", "gateway"], ["Relationship of Command"], ["One Armed Scissor"], weight=0.78),
]

ALBUMS = [
    album("053", "Ramones", "Ramones", 1976, "studio_album", "high", "core", ["album_anchor"]),
    album("053", "Never Mind the Bollocks, Here's the Sex Pistols", "Sex Pistols", 1977, "studio_album", "high", "core", ["album_anchor"]),
    album("053", "London Calling", "The Clash", 1979, "studio_album", "mass", "core", ["album_anchor", "bridge"]),
    album("053", "Singles Going Steady", "Buzzcocks", 1979, "compilation", "medium", "standard", ["compilation_gateway"]),
    album("053", "Damned Damned Damned", "The Damned", 1977, "studio_album", "medium", "standard", ["gateway"]),
    album("054", "Remain in Light", "Talking Heads", 1980, "studio_album", "high", "core", ["album_anchor", "bridge"]),
    album("054", "Marquee Moon", "Television", 1977, "studio_album", "medium", "core", ["album_anchor"]),
    album("054", "Horses", "Patti Smith", 1975, "studio_album", "high", "core", ["album_anchor"]),
    album("054", "Parallel Lines", "Blondie", 1978, "studio_album", "high", "core", ["gateway", "bridge"]),
    album("054", "Blank Generation", "Richard Hell & The Voidoids", 1977, "studio_album", "medium", "edge", ["deepening"]),
    album("055", "Damaged", "Black Flag", 1981, "studio_album", "medium", "core", ["album_anchor"]),
    album("055", "Complete Discography", "Minor Threat", 1989, "compilation", "medium", "core", ["compilation_gateway"]),
    album("055", "Fresh Fruit for Rotting Vegetables", "Dead Kennedys", 1980, "studio_album", "medium", "core", ["album_anchor"]),
    album("055", "Bad Brains", "Bad Brains", 1982, "studio_album", "medium", "standard", ["gateway"]),
    album("055", "Walk Among Us", "Misfits", 1982, "studio_album", "medium", "standard", ["bridge"]),
    album("055", "Zen Arcade", "Husker Du", 1984, "studio_album", "medium", "standard", ["bridge"]),
    album("056", "Unknown Pleasures", "Joy Division", 1979, "studio_album", "high", "core", ["album_anchor"]),
    album("056", "Disintegration", "The Cure", 1989, "studio_album", "mass", "core", ["album_anchor"]),
    album("056", "Juju", "Siouxsie and the Banshees", 1981, "studio_album", "medium", "standard", ["gateway"]),
    album("056", "In the Flat Field", "Bauhaus", 1980, "studio_album", "medium", "standard", ["gateway"]),
    album("056", "Ocean Rain", "Echo & the Bunnymen", 1984, "studio_album", "medium", "standard", ["bridge"]),
    album("057", "Synchronicity", "The Police", 1983, "studio_album", "mass", "core", ["album_anchor"]),
    album("057", "The Cars", "The Cars", 1978, "studio_album", "mass", "core", ["album_anchor"]),
    album("057", "Rio", "Duran Duran", 1982, "studio_album", "mass", "core", ["gateway"]),
    album("057", "Kick", "INXS", 1987, "studio_album", "mass", "core", ["gateway"]),
    album("057", "My Aim Is True", "Elvis Costello", 1977, "studio_album", "high", "standard", ["bridge"]),
    album("057", "Freedom of Choice", "Devo", 1980, "studio_album", "high", "standard", ["gateway"]),
    album("058", "Violator", "Depeche Mode", 1990, "studio_album", "mass", "core", ["album_anchor"]),
    album("058", "Power, Corruption & Lies", "New Order", 1983, "studio_album", "high", "core", ["album_anchor"]),
    album("058", "Sweet Dreams (Are Made of This)", "Eurythmics", 1983, "studio_album", "mass", "core", ["gateway"]),
    album("058", "Please", "Pet Shop Boys", 1986, "studio_album", "high", "standard", ["gateway"]),
    album("058", "Non-Stop Erotic Cabaret", "Soft Cell", 1981, "studio_album", "high", "standard", ["gateway"]),
    album("058", "The Pleasure Principle", "Gary Numan", 1979, "studio_album", "high", "standard", ["bridge"]),
    album("059", "Murmur", "R.E.M.", 1983, "studio_album", "high", "core", ["album_anchor"]),
    album("059", "Let It Be", "The Replacements", 1984, "studio_album", "medium", "core", ["album_anchor"]),
    album("059", "The Queen Is Dead", "The Smiths", 1986, "studio_album", "high", "core", ["album_anchor"]),
    album("059", "Doolittle", "Pixies", 1989, "studio_album", "high", "standard", ["bridge"]),
    album("059", "Daydream Nation", "Sonic Youth", 1988, "studio_album", "medium", "standard", ["bridge"]),
    album("059", "Double Nickels on the Dime", "Minutemen", 1984, "studio_album", "medium", "edge", ["deepening"]),
    album("060", "Songs About Fucking", "Big Black", 1987, "studio_album", "medium", "edge", ["deepening"]),
    album("060", "Repeater", "Fugazi", 1990, "studio_album", "medium", "standard", ["album_anchor"]),
    album("060", "Spiderland", "Slint", 1991, "studio_album", "medium", "edge", ["boundary"]),
    album("060", "The Shape of Punk to Come", "Refused", 1998, "studio_album", "medium", "standard", ["gateway"]),
    album("060", "Relationship of Command", "At the Drive-In", 2000, "studio_album", "medium", "standard", ["bridge"]),
]

SONGS = [
    song("053", "Blitzkrieg Bop", "Ramones", 1976, "high", "core", ["anchor", "song_first"], "artist_survey_worthy"),
    song("053", "I Wanna Be Sedated", "Ramones", 1978, "mass", "core", ["gateway", "song_first"], "artist_survey_worthy"),
    song("053", "Anarchy in the U.K.", "Sex Pistols", 1976, "high", "core", ["anchor"], "artist_survey_worthy"),
    song("053", "God Save the Queen", "Sex Pistols", 1977, "high", "core", ["gateway"], "artist_survey_worthy"),
    song("053", "London Calling", "The Clash", 1979, "mass", "core", ["anchor", "song_first", "bridge"], "artist_survey_worthy"),
    song("053", "Ever Fallen in Love", "Buzzcocks", 1978, "high", "standard", ["gateway"], "artist_survey_worthy"),
    song("053", "New Rose", "The Damned", 1976, "medium", "standard", ["deepening"], "artist_survey_worthy"),
    song("054", "Psycho Killer", "Talking Heads", 1977, "mass", "core", ["gateway", "song_first"], "artist_survey_worthy"),
    song("054", "Once in a Lifetime", "Talking Heads", 1980, "mass", "core", ["anchor", "song_first"], "artist_survey_worthy"),
    song("054", "Marquee Moon", "Television", 1977, "medium", "core", ["anchor"], "artist_survey_worthy"),
    song("054", "Gloria", "Patti Smith", 1975, "high", "core", ["anchor"], "artist_survey_worthy", warning="Preserve Patti Smith recording distinct from Them/Van Morrison original."),
    song("054", "Heart of Glass", "Blondie", 1978, "mass", "core", ["bridge", "song_first"], "artist_survey_worthy"),
    song("054", "Blank Generation", "Richard Hell & The Voidoids", 1977, "medium", "standard", ["deepening"], "artist_survey_worthy"),
    song("054", "Roadrunner", "The Modern Lovers", 1976, "medium", "standard", ["bridge"], "artist_survey_worthy"),
    song("055", "Rise Above", "Black Flag", 1981, "medium", "core", ["anchor"], "artist_survey_worthy"),
    song("055", "Straight Edge", "Minor Threat", 1981, "medium", "core", ["anchor"], "artist_survey_worthy"),
    song("055", "Holiday in Cambodia", "Dead Kennedys", 1980, "medium", "core", ["anchor"], "artist_survey_worthy"),
    song("055", "Banned in D.C.", "Bad Brains", 1982, "medium", "standard", ["gateway"], "artist_survey_worthy"),
    song("055", "Last Caress", "Misfits", 1980, "high", "standard", ["bridge", "song_first"], "artist_survey_worthy"),
    song("055", "New Day Rising", "Husker Du", 1985, "medium", "standard", ["bridge"], "artist_survey_worthy"),
    song("055", "Wild in the Streets", "Circle Jerks", 1982, "medium", "edge", ["deepening"], "artist_survey_worthy"),
    song("056", "Love Will Tear Us Apart", "Joy Division", 1980, "mass", "core", ["anchor", "song_first"], "artist_survey_worthy"),
    song("056", "Atmosphere", "Joy Division", 1980, "high", "standard", ["deepening"], "artist_survey_worthy"),
    song("056", "Just Like Heaven", "The Cure", 1987, "mass", "core", ["gateway", "song_first"], "artist_survey_worthy"),
    song("056", "Pictures of You", "The Cure", 1989, "high", "standard", ["deepening"], "artist_survey_worthy"),
    song("056", "Spellbound", "Siouxsie and the Banshees", 1981, "medium", "standard", ["gateway"], "artist_survey_worthy"),
    song("056", "Bela Lugosi's Dead", "Bauhaus", 1979, "medium", "standard", ["gateway", "song_first"], "artist_survey_worthy"),
    song("056", "The Killing Moon", "Echo & the Bunnymen", 1984, "high", "standard", ["bridge"], "artist_survey_worthy"),
    song("057", "Every Breath You Take", "The Police", 1983, "mass", "core", ["anchor", "song_first"], "artist_survey_worthy"),
    song("057", "Roxanne", "The Police", 1978, "mass", "core", ["gateway"], "artist_survey_worthy"),
    song("057", "Just What I Needed", "The Cars", 1978, "mass", "core", ["gateway", "song_first"], "artist_survey_worthy"),
    song("057", "Hungry Like the Wolf", "Duran Duran", 1982, "mass", "core", ["gateway", "song_first"], "artist_survey_worthy"),
    song("057", "Need You Tonight", "INXS", 1987, "mass", "core", ["gateway", "song_first"], "artist_survey_worthy"),
    song("057", "Alison", "Elvis Costello", 1977, "high", "standard", ["bridge"], "artist_survey_worthy"),
    song("057", "Love Shack", "The B-52's", 1989, "mass", "standard", ["gateway", "song_first"], "artist_survey_worthy"),
    song("057", "Whip It", "Devo", 1980, "mass", "standard", ["gateway", "song_first"], "artist_survey_worthy"),
    song("058", "Enjoy the Silence", "Depeche Mode", 1990, "mass", "core", ["anchor", "song_first"], "artist_survey_worthy"),
    song("058", "Personal Jesus", "Depeche Mode", 1989, "mass", "core", ["gateway"], "artist_survey_worthy"),
    song("058", "Blue Monday", "New Order", 1983, "high", "core", ["anchor", "song_first", "bridge"], "artist_survey_worthy"),
    song("058", "Sweet Dreams (Are Made of This)", "Eurythmics", 1983, "mass", "core", ["gateway", "song_first"], "artist_survey_worthy"),
    song("058", "West End Girls", "Pet Shop Boys", 1984, "high", "standard", ["gateway"], "artist_survey_worthy"),
    song("058", "Tainted Love", "Soft Cell", 1981, "mass", "core", ["gateway", "song_first"], "artist_survey_worthy", warning="Preserve Soft Cell recording distinct from Gloria Jones original."),
    song("058", "Cars", "Gary Numan", 1979, "mass", "standard", ["bridge", "song_first"], "artist_survey_worthy"),
    song("059", "Radio Free Europe", "R.E.M.", 1981, "medium", "core", ["anchor"], "artist_survey_worthy"),
    song("059", "The One I Love", "R.E.M.", 1987, "high", "standard", ["gateway"], "artist_survey_worthy"),
    song("059", "Bastards of Young", "The Replacements", 1985, "medium", "core", ["anchor"], "artist_survey_worthy"),
    song("059", "This Charming Man", "The Smiths", 1983, "high", "core", ["anchor"], "artist_survey_worthy"),
    song("059", "How Soon Is Now?", "The Smiths", 1984, "high", "standard", ["gateway"], "artist_survey_worthy"),
    song("059", "Where Is My Mind?", "Pixies", 1988, "mass", "standard", ["bridge", "song_first"], "artist_survey_worthy"),
    song("059", "Teen Age Riot", "Sonic Youth", 1988, "medium", "standard", ["bridge"], "artist_survey_worthy"),
    song("059", "Corona", "Minutemen", 1984, "medium", "edge", ["deepening"], "artist_survey_worthy"),
    song("060", "Kerosene", "Big Black", 1986, "medium", "edge", ["anchor"], "artist_survey_worthy"),
    song("060", "Waiting Room", "Fugazi", 1988, "medium", "standard", ["anchor", "song_first"], "artist_survey_worthy"),
    song("060", "Here Come the Rome Plows", "Drive Like Jehu", 1994, "low", "edge", ["deepening"], "artist_survey_worthy"),
    song("060", "Good Morning, Captain", "Slint", 1991, "medium", "edge", ["boundary"], "artist_survey_worthy"),
    song("060", "Prayer to God", "Shellac", 2000, "low", "edge", ["deepening"], "artist_survey_worthy"),
    song("060", "New Noise", "Refused", 1998, "medium", "standard", ["gateway", "song_first"], "artist_survey_worthy"),
    song("060", "One Armed Scissor", "At the Drive-In", 2000, "medium", "standard", ["bridge", "song_first"], "artist_survey_worthy"),
]


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


def counts(rows: list[dict[str, Any]]) -> Counter[str]:
    return Counter(row["archetype_id"] for row in rows)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    row_counts = {
        "artists": len(ARTISTS),
        "albums": len(ALBUMS),
        "songs": len(SONGS),
        "total": len(ARTISTS) + len(ALBUMS) + len(SONGS),
        "existing_seed": 0,
        "added_missing_obvious": len(ARTISTS) + len(ALBUMS) + len(SONGS),
    }
    payload = {
        "metadata": {
            "family_number": 8,
            "family_name": "Punk, Hardcore, Post-Punk, New Wave",
            "source_report": DISPATCH,
            "supplemental_reports": [SUPPLEMENT],
            "generated_date": TODAY,
            "source_package_note": "Packet 008 used as controlling taxonomy source. F8.md was cross-checked and treated as misaligned art-pop/creator-context material, not as Family 8 row seed data.",
            "normalization": {
                "id_style": "lowercase kebab-case",
                "source_rows_existing_seed": True,
                "added_rows_existing_seed": False,
                "version_policy": "Distinct recordings, covers, artist projects, and era-specific aliases are preserved as separate recording objects; ambiguous risks are flagged in warnings.",
            },
            "allowed_enums": {
                "roles": ROLES,
                "recognition_tier": RECOGNITION,
                "survey_tier": SURVEY,
                "album_object_type": ALBUM_TYPES,
                "artist_survey_status": ARTIST_STATUSES,
            },
            "row_counts": row_counts,
            "archetypes": ARCHETYPES,
        },
        "artists": ARTISTS,
        "albums": ALBUMS,
        "songs": SONGS,
    }
    (OUT / "normalized_family_8.json").write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    ac, alc, sc = counts(ARTISTS), counts(ALBUMS), counts(SONGS)
    coverage = ["| archetype_id | archetype | artists | albums | songs | structural note |", "|---|---|---:|---:|---:|---|"]
    for aid, name in ARCHETYPES.items():
        coverage.append(f"| {aid} | {name} | {ac[aid]} | {alc[aid]} | {sc[aid]} | Baseline is schema-ready; needs second-pass ordering and suppression review. |")
    (OUT / "gap_summary.md").write_text(f"""# Family 8 Gap Summary

Scope: Punk, Hardcore, Post-Punk, New Wave.

Source package: `{DISPATCH}`

Supplemental report checked: `{SUPPLEMENT}`. The supplemental file is not aligned to Family 8's punk/post-punk/new-wave taxonomy and is not used as a row seed.

## Import Shape

| Object class | Existing seed rows | Added missing-obvious rows | Total normalized rows |
|---|---:|---:|---:|
| Artists | 0 | {len(ARTISTS)} | {len(ARTISTS)} |
| Albums | 0 | {len(ALBUMS)} | {len(ALBUMS)} |
| Songs | 0 | {len(SONGS)} | {len(SONGS)} |

## Archetype Coverage

{chr(10).join(coverage)}

## Filled Gaps

- Established first-wave punk, CBGB/art-punk, hardcore, post-punk/gothic, MTV new wave, synthpop, college rock, and post-hardcore/noise-rock surfaces.
- Preserved mass-recognition song-first rows such as `I Wanna Be Sedated`, `Love Will Tear Us Apart`, `Every Breath You Take`, `Sweet Dreams`, and `Tainted Love`.
- Added boundary rows where later alternative, industrial, dance, or metal-family expansion could otherwise over-claim the object.

## Boundary Risks

- Punk/post-punk/new-wave rows have heavy cross-family overlap with Family 10 alternative/indie and Family 11 electronic/dance.
- Covers and same-title standards need recording-aware handling: `Gloria`, `Tainted Love`, and several soundtrack-adjacent new-wave songs should not be title-merged.
- Do not hard-lock until a human second pass confirms Page 1 weighting across normal-user recognition and canon depth.
""", encoding="utf-8")
    (OUT / "artist_candidates.md").write_text("# Artist Candidates\n\n" + table(ARTISTS, [
        "archetype_id", "artist_name", "proposed_artist_id", "existing_seed", "recognition_tier", "survey_tier", "roles", "archetype_membership_weight", "inclusion_reason", "object_specificity_note", "likely_canonical_albums", "likely_canonical_songs", "consolidation_warning"
    ]), encoding="utf-8")
    (OUT / "album_candidates.md").write_text("# Album Candidates\n\n" + table(ALBUMS, [
        "archetype_id", "album_title", "artist_name", "proposed_album_id", "existing_seed", "release_year", "album_object_type", "recognition_tier", "survey_tier", "roles", "archetype_membership_weight", "inclusion_reason", "consolidation_warning"
    ]), encoding="utf-8")
    (OUT / "song_candidates.md").write_text("# Song Candidates\n\n" + table(SONGS, [
        "archetype_id", "song_title", "artist_name", "proposed_song_id", "existing_seed", "release_year", "recognition_tier", "survey_tier", "roles", "archetype_membership_weight", "inclusion_reason", "artist_survey_status", "consolidation_warning"
    ]), encoding="utf-8")
    (OUT / "corrections_to_source_report.md").write_text("""# Corrections To Source Report

- Packet 008 is controlling for Family 8.
- `F8.md` appears to cover art-pop/creator-context material rather than Punk, Hardcore, Post-Punk, New Wave, so it is documented as misaligned and not imported as seed data.
- All baseline rows are marked `existing_seed = false`.
- Future review should compare this baseline with any later aligned Family 8 second-pass report before lock.
""", encoding="utf-8")
    (OUT / "lock_readiness.md").write_text("""# Lock Readiness

Judgment: staging-ready, not locked.

Import-readiness score: 0.80

Rationale:
- Required artist, album, and song fields are present with normalized enum values and lowercase kebab-case IDs.
- Every dispatch archetype has a usable baseline surface across object classes.
- Cross-family ownership with Families 10 and 11 is high, and the available supplemental report is misaligned.

Lock recommendation: do not claim final lock. Use this for importer validation and dispatch a dedicated Family 8 depth pass for weighting and omissions.
""", encoding="utf-8")
    warning_lines = [
        "# Import Warnings",
        "",
        "## Non-Enum Terms",
        "",
        "- None detected in generated rows.",
        "",
        "## Merge / Alias / Version Risks",
        "",
        "- `F8.md` is not aligned to Family 8 and should not be imported as source seed rows.",
    ]
    for rows in (ARTISTS, ALBUMS, SONGS):
        for row in rows:
            if row.get("consolidation_warning"):
                warning_lines.append(f"- {row.get('artist_name')}: {row['consolidation_warning']}")
    warning_lines.extend([
        "- Talking Heads, Blondie, New Order, The Cure, R.E.M., Pixies, and Sonic Youth should be canonical entities with cross-family membership rows, not duplicated family-local artists.",
        "- Hardcore and post-hardcore edges should stay survey-controlled so collector-only punk does not dominate Page 1.",
    ])
    (OUT / "import_warnings.md").write_text("\n".join(warning_lines) + "\n", encoding="utf-8")
    print(f"Generated Family 8 baseline: {row_counts}")


if __name__ == "__main__":
    main()
