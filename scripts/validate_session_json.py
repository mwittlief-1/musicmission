#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from _jsonschema_validate import validate_document


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA = REPO_ROOT / "data/schemas/schema_reaction_session_v0_2.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a Music Atlas reaction-session JSON file.")
    parser.add_argument("session", type=Path, help="Reaction-session JSON path.")
    parser.add_argument(
        "--schema",
        type=Path,
        default=DEFAULT_SCHEMA,
        help="Reaction-session schema path.",
    )
    args = parser.parse_args()

    return validate_document(args.schema, args.session)


if __name__ == "__main__":
    raise SystemExit(main())
