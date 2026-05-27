#!/usr/bin/env python3
"""Build auditable song-level research batches for graph-wide affinity retagging."""

from __future__ import annotations

import json
import re
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PASS_D = ROOT / "data/canonical_graph/depth_hardening_v0_2/pass_d/graph_tagging_corpus_v1.json"
ARCHETYPE_TARGETS = ROOT / "data/canonical_graph/depth_hardening_v0_2/pass_d/atlas_archetype_profile_targets_v1.json"
OUT_DIR = ROOT / "review_packets/affinity_graphwide_v0_1/research_batches"
INPUT_DIR = OUT_DIR / "inputs"

BATCH_SIZE = 25

SENTINELS = [
    "song|queen|bohemian rhapsody",
    "song|raffi|baby beluga",
    "song|bing crosby|white christmas",
    "song|aqua|barbie girl",
    "song|willie nelson|blue eyes crying in the rain",
    "song|rolling stones|i can t get no satisfaction",
]


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def family_number_lookup() -> dict[str, int]:
    data = load_json(ARCHETYPE_TARGETS)
    return {
        str(row["archetype_id"]): int(row["family_number"])
        for row in data["rows"]
        if row.get("archetype_id") and row.get("family_number") is not None
    }


def sort_key(song: dict[str, Any]) -> tuple[int, str]:
    sid = song["canonical_song_recording_id"]
    sentinel_rank = SENTINELS.index(sid) if sid in SENTINELS else 999999
    return (sentinel_rank, sid)


def main() -> None:
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    family_by_archetype = family_number_lookup()
    rows = [
        row
        for row in load_json(PASS_D)["rows"]
        if row.get("candidate_type") == "song" and row.get("active_in_v1", True)
    ]
    rows_by_song: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        rows_by_song[row["candidate_identity_key"]].append(row)

    songs = []
    for sid, memberships in rows_by_song.items():
        first = sorted(memberships, key=lambda row: row.get("v1_membership_id", ""))[0]
        songs.append(
            {
                "canonical_song_recording_id": sid,
                "song_title": first.get("title", ""),
                "artist_names": [first.get("artist_display_name", "")],
                "release_years": [first["year"]] if first.get("year") not in ("", None) else [],
                "memberships": [
                    {
                        "membership_id": row.get("v1_membership_id", ""),
                        "family_number": family_by_archetype.get(str(row.get("archetype_id", ""))),
                        "family_scope": row.get("primary_family", ""),
                        "archetype_id": str(row.get("archetype_id", "")),
                        "archetype_name": row.get("primary_archetype", ""),
                        "membership_roles": [row.get("mission_role", "")] if row.get("mission_role") else [],
                        "recognition_tier": row.get("recognition_band", ""),
                        "version_or_composition_risk": row.get("version_or_composition_risk", ""),
                        "risk_status": row.get("risk_status", ""),
                        "why_it_belongs": row.get("why_it_belongs", ""),
                        "notes": row.get("notes", ""),
                    }
                    for row in sorted(memberships, key=lambda row: row.get("v1_membership_id", ""))
                ],
            }
        )

    songs = sorted(songs, key=sort_key)
    batches = []
    for index in range(0, len(songs), BATCH_SIZE):
        batch_songs = songs[index : index + BATCH_SIZE]
        batch_id = f"research_batch_{index // BATCH_SIZE + 1:04d}"
        input_file = INPUT_DIR / f"{batch_id}.json"
        output_file = OUT_DIR / "outputs" / f"{batch_id}_researched_tags.json"
        write_json(
            input_file,
            {
                "metadata": {
                    "batch_id": batch_id,
                    "generated": str(date.today()),
                    "source_graph": str(PASS_D.relative_to(ROOT)),
                    "schema": "affinity_research_batch_input_v0_1",
                    "instructions": [
                        "Research every song individually.",
                        "Do not infer core tags from family/archetype alone.",
                        "Core tags describe intrinsic song/recording truth.",
                        "Membership overlays describe social/routing context only.",
                        "Use only approved canonical tags from the v0.3.1 allowlist.",
                        "Include public source URLs or clearly marked general-knowledge notes for every song.",
                    ],
                },
                "songs": batch_songs,
            },
        )
        batches.append(
            {
                "batch_id": batch_id,
                "input_file": str(input_file.relative_to(ROOT)),
                "expected_output_file": str(output_file.relative_to(ROOT)),
                "song_count": len(batch_songs),
                "song_ids": [song["canonical_song_recording_id"] for song in batch_songs],
                "status": "pending",
                "assigned_to": "",
            }
        )

    write_json(
        OUT_DIR / "affinity_research_batch_manifest_v0_1.json",
        {
            "metadata": {
                "artifact_name": "affinity_research_batch_manifest_v0_1",
                "generated": str(date.today()),
                "batch_size": BATCH_SIZE,
                "batch_count": len(batches),
                "song_count": len(songs),
                "status": "research_not_complete",
                "notes": "This manifest replaces the failed heuristic Phase 3 process with per-song research batches.",
            },
            "batches": batches,
        },
    )

    (OUT_DIR / "AFFINITY_RESEARCH_BATCH_SCHEMA_v0_1.md").write_text(
        """# Affinity Research Batch Output Schema v0.1

Each output file must contain:

```json
{
  "metadata": {
    "batch_id": "research_batch_0001",
    "researcher": "name or agent",
    "status": "complete",
    "notes": ""
  },
  "songs": [
    {
      "canonical_song_recording_id": "Pass D candidate_identity_key",
      "song_title": "",
      "artist_names": [],
      "release_years": [],
      "research_evidence": [
        {
          "source_type": "public_url | general_music_knowledge",
          "source": "URL or concise note",
          "supports": "identity | composition | lyrics_theme | sonic_texture | rhythm_form | social_context | version_context"
        }
      ],
      "canonical_song_affinity_tags": {
        "vocal_performance": {"primary": [], "secondary": []},
        "emotion_theme": {"primary": [], "secondary": []},
        "sonic_texture": {"primary": [], "secondary": []},
        "rhythm_body": {"primary": [], "secondary": []},
        "form_container": {"primary": [], "secondary": []}
      },
      "membership_context_overlays": [
        {
          "membership_id": "",
          "social_context": {"primary": [], "secondary": []},
          "routing_caution": {"primary": [], "secondary": []},
          "overlay_notes": ""
        }
      ],
      "review": {
        "identity_review_needed": false,
        "tag_review_needed": false,
        "overlay_review_needed": false,
        "review_reason_codes": [],
        "review_reason": ""
      },
      "tagging_notes": "",
      "source_confidence": "high | medium | low"
    }
  ]
}
```
""",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
