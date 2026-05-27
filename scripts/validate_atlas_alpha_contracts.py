#!/usr/bin/env python3
"""Validate Atlas Alpha contracts, examples, proofs, and invariants.

This runner intentionally separates:
- JSON syntax checks
- JSON Schema checks via ajv
- Atlas invariant checks
- service-level referential integrity checks
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]


ATLAS_SCHEMA = REPO_ROOT / "data/atlas_schema/atlas_schema_contract_v0_1.json"
ATLAS_DELTA_SCHEMA = REPO_ROOT / "data/atlas_schema/atlas_delta_v0_1.schema.json"
MISSION_DIGEST_SCHEMA = (
    REPO_ROOT
    / "data/mission_generation/mission_generation_digest_view_alpha_v0_1/mission_generation_digest_view_alpha_v0_1.schema.json"
)
MISSION_DIGEST_SAMPLE = (
    REPO_ROOT
    / "data/mission_generation/mission_generation_digest_view_alpha_v0_1/mission_generation_digest_view_alpha_v0_1.sample.json"
)
MISSION_DIGEST_GENERATED_ROOT = (
    REPO_ROOT
    / "data/mission_generation/mission_generation_digest_view_alpha_v0_1/generated_from_survey_evidence_export"
)


@dataclass
class Finding:
    category: str
    path: Path
    message: str

    def render(self) -> str:
        return f"[{self.category}] {self.path.relative_to(REPO_ROOT)}: {self.message}"


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def json_files() -> list[Path]:
    paths: set[Path] = {
        ATLAS_SCHEMA,
        ATLAS_DELTA_SCHEMA,
        MISSION_DIGEST_SCHEMA,
        MISSION_DIGEST_SAMPLE,
    }
    paths.update((REPO_ROOT / "data/atlas_schema/examples").glob("*.json"))
    paths.update((REPO_ROOT / "data/atlas_schema/alpha_hardening").glob("*.json"))
    paths.update((REPO_ROOT / "data/atlas_schema/ingestion_proof").glob("**/*.json"))
    paths.update((REPO_ROOT / "data/atlas_schema/node_interpretation_smoke").glob("**/*.json"))
    paths.update(MISSION_DIGEST_GENERATED_ROOT.glob("*.json"))
    paths.update((REPO_ROOT / "data/closed_loop_simulation/a3_first_batch_learning_v0_1_adaptive_contract_v0_1").glob("**/atlas_delta_after_batch_1.json"))
    paths.update((REPO_ROOT / "data/closed_loop_simulation/a3_first_batch_learning_v0_1_adaptive_contract_v0_1").glob("**/atlas_update_records_after_batch_1.json"))
    paths.update((REPO_ROOT / "data/closed_loop_simulation/a3_first_batch_learning_v0_1_adaptive_contract_v0_1").glob("**/atlas_digest_after_batch_1.json"))
    return sorted(path for path in paths if path.exists())


def atlas_schema_targets() -> list[Path]:
    examples = [
        path
        for path in (REPO_ROOT / "data/atlas_schema/examples").glob("*.json")
        if not path.name.startswith("atlas_delta_")
    ]
    proofs = [
        path
        for path in (REPO_ROOT / "data/atlas_schema/ingestion_proof").glob("**/atlas_records_bundle*.json")
        # This operational convenience bundle preserves Survey Evidence Export metadata
        # beyond the strict Atlas schema. Its component artifacts are still syntax and
        # invariant checked by this runner.
        if "survey_evidence_export_v0_1" not in str(path)
    ]
    proofs += list((REPO_ROOT / "data/atlas_schema/ingestion_proof").glob("**/atlas_digest_view*.json"))
    return sorted(path for path in examples + proofs if path.exists())


def atlas_delta_targets() -> list[Path]:
    targets = list((REPO_ROOT / "data/atlas_schema/examples").glob("atlas_delta_closed_loop_profile_*.json"))
    return sorted(path for path in targets if path.exists())


def mission_digest_targets() -> list[Path]:
    targets = [MISSION_DIGEST_SAMPLE]
    targets.extend(MISSION_DIGEST_GENERATED_ROOT.glob("mission_generation_digest_view_*.json"))
    return sorted(path for path in targets if path.exists())


def run_ajv(schema: Path, targets: Iterable[Path]) -> list[Finding]:
    target_list = [path for path in targets if path.exists()]
    if not target_list:
        return []
    cmd = [
        "npx",
        "--yes",
        "ajv-cli@5",
        "validate",
        "--strict=false",
        "--spec=draft2020",
        "-s",
        str(schema.relative_to(REPO_ROOT)),
    ]
    for target in target_list:
        cmd.extend(["-d", str(target.relative_to(REPO_ROOT))])
    result = subprocess.run(cmd, cwd=REPO_ROOT, text=True, capture_output=True, check=False)
    if result.returncode == 0:
        return []
    output = "\n".join(part for part in [result.stdout, result.stderr] if part.strip()).strip()
    return [Finding("schema", schema, output or "ajv validation failed")]


def records_from_document(document: Any) -> list[dict[str, Any]]:
    if isinstance(document, dict) and document.get("record_type") == "atlas_example_bundle":
        return [record for record in document.get("records", []) if isinstance(record, dict)]
    if isinstance(document, dict) and isinstance(document.get("records"), list):
        return [record for record in document["records"] if isinstance(record, dict)]
    if isinstance(document, dict) and isinstance(document.get("record_type"), str):
        return [document]
    if isinstance(document, list):
        return [record for record in document if isinstance(record, dict)]
    return []


def lifecycle_state(record: dict[str, Any], field: str) -> str | None:
    if isinstance(record.get("lifecycle"), dict):
        value = record["lifecycle"].get(field)
        if isinstance(value, str):
            return value
    value = record.get(field)
    return value if isinstance(value, str) else None


def collect_ids(records: list[dict[str, Any]]) -> dict[str, set[str]]:
    ids = {
        "node": set(),
        "signal": set(),
        "role": set(),
        "update": set(),
        "digest": set(),
    }
    for record in records:
        if record.get("record_type") == "atlas_node" and isinstance(record.get("atlas_node_id"), str):
            ids["node"].add(record["atlas_node_id"])
        elif record.get("record_type") == "signal" and isinstance(record.get("signal_id"), str):
            ids["signal"].add(record["signal_id"])
        elif record.get("record_type") == "atlas_role_assignment" and isinstance(record.get("atlas_role_assignment_id"), str):
            ids["role"].add(record["atlas_role_assignment_id"])
        elif record.get("record_type") == "possible_atlas_update_candidate" and isinstance(record.get("update_candidate_id"), str):
            ids["update"].add(record["update_candidate_id"])
        elif record.get("record_type") == "atlas_digest_view" and isinstance(record.get("digest_id"), str):
            ids["digest"].add(record["digest_id"])
    return ids


def iter_music_refs(value: Any) -> Iterable[dict[str, Any]]:
    if isinstance(value, dict):
        if {"object_type", "ref_source", "resolution_state"}.issubset(value.keys()):
            yield value
        for child in value.values():
            yield from iter_music_refs(child)
    elif isinstance(value, list):
        for child in value:
            yield from iter_music_refs(child)


def check_music_ref(path: Path, ref: dict[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    if ref.get("ref_source") == "canonical_graph":
        object_type = ref.get("object_type")
        required_by_type = {
            "artist": "canonical_artist_id",
            "album": "canonical_album_id",
            "song_recording": "canonical_song_recording_id",
        }
        required = required_by_type.get(object_type)
        if required and not ref.get(required):
            findings.append(Finding("invariant", path, f"canonical {object_type} ref missing {required}"))
    if ref.get("ref_source") == "user_local" and not ref.get("user_music_object_id"):
        findings.append(Finding("invariant", path, "user_local music object ref missing user_music_object_id"))
    if ref.get("ref_source") == "external_catalog" and not ref.get("external_catalog_refs"):
        findings.append(Finding("invariant", path, "external_catalog music object ref missing external_catalog_refs"))
    if ref.get("ref_source") == "unresolved" and ref.get("resolution_state") != "needs_resolution":
        findings.append(Finding("invariant", path, "unresolved music object ref must use resolution_state=needs_resolution"))
    if ref.get("object_type") == "composition_placeholder" and not ref.get("composition_placeholder_id"):
        findings.append(Finding("invariant", path, "composition_placeholder ref missing composition_placeholder_id"))
    return findings


def check_invariants(path: Path, document: Any) -> list[Finding]:
    findings: list[Finding] = []
    records = records_from_document(document)
    is_ingestion = "data/atlas_schema/ingestion_proof" in str(path)
    forbidden_node_fields = {
        "role",
        "roles",
        "atlas_roles",
        "landmark",
        "region",
        "frontier",
        "dead_end",
        "waypoint",
        "candidate_pool_behavior",
    }

    for record in records:
        record_type = record.get("record_type")
        if record_type == "atlas_node":
            present = sorted(forbidden_node_fields.intersection(record.keys()))
            if present:
                findings.append(Finding("invariant", path, f"AtlasNode contains role-like field(s): {', '.join(present)}"))
        if record_type == "atlas_role_assignment" and is_ingestion:
            if lifecycle_state(record, "promotion_state") == "promoted":
                findings.append(Finding("invariant", path, "ingestion role assignment is promoted"))
        if record_type == "possible_atlas_update_candidate":
            if record.get("canonical_graph_mutation_allowed") is not False:
                findings.append(Finding("invariant", path, "PossibleAtlasUpdateCandidate must set canonical_graph_mutation_allowed=false"))
        if record_type == "signal":
            if "signal_strength" not in record or "interpretation_confidence" not in record:
                findings.append(Finding("invariant", path, "Signal missing signal_strength or interpretation_confidence"))
        if record_type == "atlas_digest_view":
            contract = record.get("consumer_contract")
            if isinstance(contract, dict):
                if contract.get("canonical_graph_mutation_allowed") is not False:
                    findings.append(Finding("invariant", path, "AtlasDigestView consumer_contract must forbid canonical graph mutation"))
                if contract.get("raw_survey_payload_required") is not False:
                    findings.append(Finding("invariant", path, "AtlasDigestView must not require raw survey payload"))
        if record_type == "mission_generation_digest_view":
            compactness = record.get("compactness_policy") or {}
            hard_threshold = compactness.get("hard_review_threshold_bytes")
            if isinstance(hard_threshold, int) and path.exists() and path.stat().st_size > hard_threshold:
                findings.append(Finding("invariant", path, f"MissionGenerationDigestView exceeds hard review threshold of {hard_threshold} bytes"))
            checks = record.get("no_hidden_data_checks") or {}
            hidden_fields = [
                "raw_survey_payload_included",
                "survey_construction_internals_included",
                "page_layout_mechanics_included",
                "randomization_seed_included",
                "generator_visible_inputs_included",
                "raw_ranking_scores_included",
                "profile_writer_output_included",
                "hidden_simulator_truth_included",
                "hidden_corpus_reactions_included",
                "simulator_private_lookup_status_included",
                "canonical_graph_mutation_instructions_included",
            ]
            for field in hidden_fields:
                if checks.get(field) is not False:
                    findings.append(Finding("invariant", path, f"MissionGenerationDigestView hidden-data check failed: {field}"))
            if checks.get("all_evidence_refs_resolve_to_visible_survey_evidence") is not True:
                findings.append(Finding("invariant", path, "MissionGenerationDigestView evidence refs do not resolve to visible survey evidence"))
            policy = record.get("evidence_separation_policy") or {}
            if policy.get("role_truth_source") != "atlas_role_assignment":
                findings.append(Finding("invariant", path, "MissionGenerationDigestView role truth source must be atlas_role_assignment"))
            for role_summary in record.get("candidate_roles", []) or []:
                if role_summary.get("promotion_state") == "promoted":
                    findings.append(Finding("invariant", path, "MissionGenerationDigestView contains promoted candidate role"))
                if role_summary.get("role_truth_source") != "atlas_role_assignment":
                    findings.append(Finding("invariant", path, "MissionGenerationDigestView candidate role bypasses AtlasRoleAssignment"))
        for ref in iter_music_refs(record):
            findings.extend(check_music_ref(path, ref))

    if isinstance(document, dict) and "hard_rule_checks" in document:
        checks = document["hard_rule_checks"]
        if isinstance(checks, dict):
            if checks.get("atlas_delta_is_promoted_truth") is not False:
                findings.append(Finding("invariant", path, "AtlasDelta must not be promoted truth"))
            if checks.get("canonical_graph_mutation_allowed") is not False:
                findings.append(Finding("invariant", path, "AtlasDelta must forbid canonical graph mutation"))
            if checks.get("auto_promotions") not in (0, None):
                findings.append(Finding("invariant", path, "AtlasDelta reports auto promotions"))

    return findings


def check_referential_integrity(path: Path, document: Any) -> list[Finding]:
    records = records_from_document(document)
    if not records:
        return []
    ids = collect_ids(records)
    findings: list[Finding] = []
    for record in records:
        record_type = record.get("record_type")
        if record_type == "signal":
            node_id = record.get("subject_atlas_node_id")
            if node_id and ids["node"] and node_id not in ids["node"]:
                findings.append(Finding("referential", path, f"Signal {record.get('signal_id')} references missing node {node_id}"))
            for update_id in record.get("derived_update_candidate_ids", []) or []:
                if ids["update"] and update_id not in ids["update"]:
                    findings.append(Finding("referential", path, f"Signal {record.get('signal_id')} references missing update candidate {update_id}"))
        elif record_type == "atlas_role_assignment":
            node_id = record.get("atlas_node_id")
            if node_id and ids["node"] and node_id not in ids["node"]:
                findings.append(Finding("referential", path, f"Role {record.get('atlas_role_assignment_id')} references missing node {node_id}"))
            for signal_id in record.get("evidence_signal_ids", []) or []:
                if ids["signal"] and signal_id not in ids["signal"]:
                    findings.append(Finding("referential", path, f"Role {record.get('atlas_role_assignment_id')} references missing signal {signal_id}"))
        elif record_type == "possible_atlas_update_candidate":
            node_id = record.get("target_atlas_node_id")
            if node_id and ids["node"] and node_id not in ids["node"]:
                findings.append(Finding("referential", path, f"Update {record.get('update_candidate_id')} references missing node {node_id}"))
            role_id = record.get("target_role_assignment_id")
            if role_id and ids["role"] and role_id not in ids["role"]:
                findings.append(Finding("referential", path, f"Update {record.get('update_candidate_id')} references missing role {role_id}"))
            for signal_id in record.get("source_signal_ids", []) or []:
                if ids["signal"] and signal_id not in ids["signal"]:
                    findings.append(Finding("referential", path, f"Update {record.get('update_candidate_id')} references missing signal {signal_id}"))
        elif record_type == "atlas_digest_view":
            for signal_id in record.get("recent_signal_ids", []) or []:
                if ids["signal"] and signal_id not in ids["signal"]:
                    findings.append(Finding("referential", path, f"Digest {record.get('digest_id')} references missing recent signal {signal_id}"))
            role_refs = record.get("relevant_role_assignment_ids", []) or []
            if isinstance(role_refs, dict):
                flattened: list[str] = []
                for value in role_refs.values():
                    if isinstance(value, list):
                        flattened.extend(item for item in value if isinstance(item, str))
                role_refs = flattened
            for role_id in role_refs:
                if ids["role"] and role_id not in ids["role"]:
                    findings.append(Finding("referential", path, f"Digest {record.get('digest_id')} references missing role {role_id}"))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Atlas Alpha contracts and proof artifacts.")
    parser.add_argument("--json-only", action="store_true", help="Run only JSON syntax checks.")
    parser.add_argument("--skip-schema", action="store_true", help="Skip AJV JSON Schema validation.")
    args = parser.parse_args()

    findings: list[Finding] = []
    loaded: dict[Path, Any] = {}

    for path in json_files():
        try:
            loaded[path] = load_json(path)
        except Exception as exc:  # noqa: BLE001 - show direct file parse failure
            findings.append(Finding("json", path, str(exc)))

    if not args.json_only and not args.skip_schema:
        findings.extend(run_ajv(ATLAS_SCHEMA, atlas_schema_targets()))
        findings.extend(run_ajv(ATLAS_DELTA_SCHEMA, atlas_delta_targets()))
        if MISSION_DIGEST_SCHEMA.exists():
            findings.extend(run_ajv(MISSION_DIGEST_SCHEMA, mission_digest_targets()))

    if not args.json_only:
        for path, document in loaded.items():
            findings.extend(check_invariants(path, document))
            findings.extend(check_referential_integrity(path, document))

    if findings:
        print(f"Atlas Alpha validation failed with {len(findings)} finding(s):")
        for finding in findings:
            print(f"- {finding.render()}")
        return 1

    print("Atlas Alpha validation passed.")
    print(f"- JSON files checked: {len(loaded)}")
    if not args.json_only and not args.skip_schema:
        print(f"- Atlas schema targets: {len(atlas_schema_targets())}")
        print(f"- AtlasDelta schema targets: {len(atlas_delta_targets())}")
        print(f"- MissionGenerationDigestView schema targets: {len(mission_digest_targets())}")
    print("- Invariant checks: passed")
    print("- Referential integrity prototype checks: passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
