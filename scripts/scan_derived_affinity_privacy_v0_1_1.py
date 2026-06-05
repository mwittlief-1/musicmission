#!/usr/bin/env python3
"""Scan the v0.1.1 derived affinity package for restricted naming terms."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TARGETS = [
    ROOT / "derived_affinity_substrate_v0_1_1",
    ROOT / "scripts" / "build_derived_affinity_substrate_v0_1_1.py",
]


def restricted_terms() -> list[str]:
    return [
        "Way" + "mark",
        "way" + "mark",
        "WAY" + "MARK",
        "found" + "er",
        "Jane" + " Doe",
        "way" + "mark_m" + "att",
        "m" + "att_10_personal",
        "personal " + "calibration",
        "restricted project label",
        "individual listener name",
    ]


def iter_files() -> list[Path]:
    files: list[Path] = []
    for target in TARGETS:
        if target.is_file():
            files.append(target)
        elif target.is_dir():
            files.extend(path for path in target.rglob("*") if path.is_file())
    return sorted(files)


def main() -> int:
    matches: list[tuple[str, str]] = []
    files = iter_files()
    for path in files:
        relative = path.relative_to(ROOT).as_posix()
        for term in restricted_terms():
            if term in relative:
                matches.append((relative, "file_name"))
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for term in restricted_terms():
            if term in text:
                matches.append((relative, "file_content"))
    if matches:
        print(f"FAIL privacy_naming_scan matches={len(matches)}")
        for relative, location in matches[:50]:
            print(f"{location}: {relative}")
        return 1
    print(f"PASS privacy_naming_scan scanned_files={len(files)} matches=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
