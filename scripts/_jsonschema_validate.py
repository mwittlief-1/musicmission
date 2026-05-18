#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Iterable


def _load_json(path: Path) -> object:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        raise SystemExit(f"File not found: {path}") from None
    except json.JSONDecodeError as error:
        raise SystemExit(f"Invalid JSON in {path}: {error}") from None


def _format_path(path_parts: Iterable[object]) -> str:
    parts = [str(part) for part in path_parts]
    return ".".join(parts) if parts else "<root>"


def validate_document(schema_path: Path, document_path: Path) -> int:
    try:
        from jsonschema import Draft202012Validator, FormatChecker
    except ModuleNotFoundError:
        print(
            "Missing dependency: jsonschema. Install with "
            "`python3 -m pip install -r scripts/requirements.txt`.",
            file=sys.stderr,
        )
        return 2

    schema = _load_json(schema_path)
    document = _load_json(document_path)

    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(document), key=lambda error: list(error.path))

    if not errors:
        print(f"OK: {document_path} validates against {schema_path}")
        return 0

    print(f"INVALID: {document_path} failed {len(errors)} schema check(s)")
    for error in errors:
        print(f"- {_format_path(error.path)}: {error.message}")
    return 1
