#!/usr/bin/env python3
"""Regenerate the v0.1.1 hardening package and compare file hashes."""

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "derived_affinity_substrate_v0_1_1"
BUILDER = ROOT / "scripts" / "build_derived_affinity_substrate_v0_1_1.py"


def package_hashes() -> dict[str, str]:
    hashes: dict[str, str] = {}
    for path in sorted(PACKAGE.glob("*")):
        if path.is_file():
            hashes[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes


def main() -> int:
    before = package_hashes()
    result = subprocess.run([sys.executable, str(BUILDER)], cwd=ROOT, check=False, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"FAIL determinism_regeneration command_exit={result.returncode}")
        if result.stdout.strip():
            print(result.stdout.strip())
        if result.stderr.strip():
            print(result.stderr.strip())
        return result.returncode
    after = package_hashes()
    if before != after:
        changed = sorted(set(before) ^ set(after) | {key for key in before.keys() & after.keys() if before[key] != after[key]})
        print(f"FAIL determinism_regeneration changed_files={','.join(changed)}")
        return 1
    print(f"PASS determinism_regeneration files={len(after)} hashes_identical=true builder_stdout_empty={not bool(result.stdout.strip())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
