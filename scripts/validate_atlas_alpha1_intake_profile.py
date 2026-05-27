#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = REPO_ROOT / "data/atlas_schema/alpha_hardening/atlas_alpha1_ingestion_profile_v0_1.json"


FORBIDDEN_ATLAS_INGESTABLE_KEYS = {
    "debug_provenance",
    "scores",
    "raw_ranking_scores",
    "generator_visible_inputs",
    "hidden_fake_profile_truth",
    "hidden_corpus_reactions",
    "simulator_private_lookup_status",
    "profile_writer_output",
    "page_generation_prompt",
    "randomization_seed",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def stage_page_counts(atoms: list[dict[str, Any]]) -> dict[str, int]:
    pages_by_stage: dict[str, set[str]] = {}
    for atom in atoms:
        page_context = atom.get("page_context") or {}
        stage = page_context.get("stage")
        page_id = page_context.get("page_id")
        if stage and page_id:
            pages_by_stage.setdefault(stage, set()).add(page_id)
    return {stage: len(pages) for stage, pages in pages_by_stage.items()}


def collect_nested_keys(value: Any, found: Counter[str] | None = None) -> Counter[str]:
    if found is None:
        found = Counter()
    if isinstance(value, dict):
        for key, child in value.items():
            found[key] += 1
            collect_nested_keys(child, found)
    elif isinstance(value, list):
        for child in value:
            collect_nested_keys(child, found)
    return found


def validate_profile(profile: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = profile.get("required_intake") or {}
    expected = {
        "artist_pages": 4,
        "album_pages": 2,
        "song_pages": 4,
        "expected_total_pages": 10,
        "normal_first_run_survey_optional": False,
    }
    for key, value in expected.items():
        if required.get(key) != value:
            errors.append(f"profile required_intake.{key} expected {value!r}, got {required.get(key)!r}")
    policy = profile.get("evidence_policy") or {}
    for key in [
        "survey_output_is_evidence_not_truth",
        "uploaded_app_evidence_append_only",
        "uploaded_app_evidence_provisional",
        "delete_or_reset_requires_derived_state_regeneration",
    ]:
        if policy.get(key) is not True:
            errors.append(f"profile evidence_policy.{key} must be true")
    for key in ["apple_exposure_as_taste_truth_allowed", "dont_know_as_negative_allowed"]:
        if policy.get(key) is not False:
            errors.append(f"profile evidence_policy.{key} must be false")
    mission = profile.get("mission_generation_readiness") or {}
    for key in ["raw_survey_payload_required", "profile_writer_output_allowed", "hidden_simulator_truth_allowed", "canonical_graph_mutation_allowed", "survey_role_promotion_allowed"]:
        if mission.get(key) is not False:
            errors.append(f"profile mission_generation_readiness.{key} must be false")
    return errors


def validate_export(export: dict[str, Any], profile: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = profile["required_intake"]
    source = export.get("source") or {}
    page_config = source.get("page_count_config") or {}
    expected_counts = {
        "artist": required["artist_pages"],
        "album": required["album_pages"],
        "song": required["song_pages"],
    }
    config_key_map = {
        "artist": "artist_pages",
        "album": "album_pages",
        "song": "song_pages",
    }
    for stage, expected in expected_counts.items():
        actual = page_config.get(config_key_map[stage])
        if actual != expected:
            errors.append(f"source.page_count_config.{config_key_map[stage]} expected {expected}, got {actual}")

    atoms = ((export.get("atlas_ingestable") or {}).get("evidence_atoms") or [])
    if not atoms:
        errors.append("atlas_ingestable.evidence_atoms is empty or missing")
        return errors

    actual_counts = stage_page_counts(atoms)
    for stage, expected in expected_counts.items():
        actual = actual_counts.get(stage, 0)
        if actual != expected:
            errors.append(f"visible evidence page count for {stage} expected {expected}, got {actual}")

    nested_keys = collect_nested_keys({"atlas_ingestable": export.get("atlas_ingestable")})
    forbidden_present = sorted(key for key in FORBIDDEN_ATLAS_INGESTABLE_KEYS if nested_keys.get(key))
    if forbidden_present:
        errors.append(f"forbidden Atlas-ingestable key(s) present: {', '.join(forbidden_present)}")

    evidence_refs = {atom.get("evidence_ref") for atom in atoms if atom.get("evidence_ref")}
    index_refs = set(((export.get("atlas_ingestable") or {}).get("response_ref_index") or {}).get("evidence_refs") or [])
    if evidence_refs and index_refs and evidence_refs != index_refs:
        errors.append("response_ref_index.evidence_refs does not exactly match evidence atom refs")
    for atom in atoms:
        evidence_ref = atom.get("evidence_ref")
        if not evidence_ref:
            errors.append("evidence atom missing evidence_ref")
        operation = atom.get("reaction", {}).get("normalized_operation")
        raw_reaction = atom.get("reaction", {}).get("raw_reaction")
        if raw_reaction == "dont_know_enough" and operation != "familiarity_uncertainty":
            errors.append(f"{evidence_ref}: dont_know_enough must normalize to familiarity_uncertainty")
        apple = atom.get("apple_exposure_prior") or {}
        if apple.get("taste_truth") is not False:
            errors.append(f"{evidence_ref}: apple_exposure_prior.taste_truth must be false")
        for ref in atom.get("supporting_visible_response_refs") or []:
            if ref.get("evidence_ref") not in evidence_refs:
                errors.append(f"{evidence_ref}: supporting ref {ref.get('evidence_ref')} does not resolve inside export")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Atlas Alpha 1 fixed Survey intake profile and optional Survey Evidence Export.")
    parser.add_argument("--profile", default=str(PROFILE_PATH), help="Atlas Alpha 1 ingestion profile JSON.")
    parser.add_argument("--survey-export", help="Optional Survey Evidence Export to validate against the fixed 4/2/4 intake profile.")
    args = parser.parse_args()

    profile_path = Path(args.profile)
    if not profile_path.is_absolute():
        profile_path = REPO_ROOT / profile_path
    errors = validate_profile(load_json(profile_path))

    export_path: Path | None = None
    if args.survey_export:
        export_path = Path(args.survey_export)
        if not export_path.is_absolute():
            export_path = REPO_ROOT / export_path
        errors.extend(validate_export(load_json(export_path), load_json(profile_path)))

    if errors:
        print(f"INVALID: Atlas Alpha 1 intake profile failed {len(errors)} check(s)")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"OK: Atlas Alpha 1 intake profile validates at {rel(profile_path)}")
    if export_path:
        print(f"OK: Survey Evidence Export matches fixed Alpha intake at {rel(export_path)}")
    else:
        print("No Survey Evidence Export supplied; fixed 4/2/4 export validation not run.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
