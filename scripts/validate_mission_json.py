#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from _jsonschema_validate import validate_document


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA = REPO_ROOT / "data/schemas/schema_mission_v0_2.json"
DEFAULT_MISSION = REPO_ROOT / "data/missions/sample_mission_love_tributaries_v0_2.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a Music Atlas mission JSON file.")
    parser.add_argument(
        "mission",
        nargs="?",
        type=Path,
        default=DEFAULT_MISSION,
        help="Mission JSON path. Defaults to the bundled v0.2 sample mission.",
    )
    parser.add_argument(
        "--schema",
        type=Path,
        default=DEFAULT_SCHEMA,
        help="Mission schema path.",
    )
    args = parser.parse_args()

    return validate_document(args.schema, args.mission)


if __name__ == "__main__":
    raise SystemExit(main())
