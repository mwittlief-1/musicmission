#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
INPUT_DIR = REPO_ROOT / "data/survey_simulation/survey_evidence_export/samples"
OUTPUT_ROOT = REPO_ROOT / "data/atlas_schema/ingestion_proof/survey_evidence_export_v0_1"
SCHEMA_VERSION = "0.1"
INGESTION_VERSION = "survey_evidence_export_to_atlas_v0.1"
GENERATED_AT = "2026-05-21T17:15:00Z"

REACTION_VALUE_MAP = {
    "love": "love",
    "like": "like",
    "ok": "neutral",
    "dont_like": "dislike",
    "dont_know_enough": "dont_know",
}

NORMALIZED_SIGNAL_MAP = {
    "positive_high": "strong_positive",
    "positive_medium": "positive",
    "waypoint_context": "contextual_waypoint",
    "negative_scope_carefully": "negative_scoped",
    "familiarity_uncertainty": "familiarity_uncertainty",
}

SIGNAL_STRENGTH = {
    "positive_high": 0.86,
    "positive_medium": 0.68,
    "waypoint_context": 0.42,
    "negative_scope_carefully": 0.62,
    "familiarity_uncertainty": 0.28,
}

INTERPRETATION_CONFIDENCE = {
    "positive_high": 0.7,
    "positive_medium": 0.58,
    "waypoint_context": 0.5,
    "negative_scope_carefully": 0.55,
    "familiarity_uncertainty": 0.44,
}

ROLE_BUCKET_TO_DIGEST_FIELD = {
    "landmark": "candidate_landmarks",
    "region": "candidate_regions",
    "frontier": "candidate_frontiers",
    "dead_end": "candidate_dead_end_hypotheses",
    "waypoint": "candidate_waypoints",
}


def main() -> int:
    global INPUT_DIR, OUTPUT_ROOT
    parser = argparse.ArgumentParser(description="Build Atlas ingestion proof records from Survey Evidence Export v0.1 files.")
    parser.add_argument("--input-dir", type=Path, default=INPUT_DIR)
    parser.add_argument("--output-root", type=Path, default=OUTPUT_ROOT)
    args = parser.parse_args()

    INPUT_DIR = args.input_dir.resolve()
    OUTPUT_ROOT = args.output_root.resolve()
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    export_paths = sorted(INPUT_DIR.glob("*_survey_evidence_export.json"))
    if not export_paths:
        raise SystemExit(f"No Survey Evidence Export files found under {rel(INPUT_DIR)}")

    profiles = []
    for export_path in export_paths:
        profiles.append(ingest_export(export_path))

    write_json(
        OUTPUT_ROOT / "manifest.json",
        {
            "schema_version": "waymark.survey_evidence_export_atlas_ingestion_manifest.v0.1",
            "ingestion_version": INGESTION_VERSION,
            "generated_at": GENERATED_AT,
            "input_dir": rel(INPUT_DIR),
            "output_dir": rel(OUTPUT_ROOT),
            "profile_count": len(profiles),
            "required_flow": [
                "Survey Evidence Export",
                "Signal",
                "AtlasNode",
                "provisional AtlasRoleAssignment",
                "PossibleAtlasUpdateCandidate",
                "AtlasDigestView",
            ],
            "hard_rules": hard_rules(),
            "profiles": profiles,
        },
    )
    write_text(OUTPUT_ROOT / "README.md", render_manifest_readme(profiles))
    return 0


def ingest_export(export_path: Path) -> dict[str, Any]:
    export = load_json(export_path)
    source = export["source"]
    atoms = export["atlas_ingestable"]["evidence_atoms"]
    profile_id = source["profile_public_id"]
    config_id = source["page_count_config"]["config_id"]
    profile_label = f"{profile_id}_{config_id}"
    output_dir = OUTPUT_ROOT / profile_label
    output_dir.mkdir(parents=True, exist_ok=True)

    validation = validate_export_for_atlas(export, export_path)
    density_contexts = build_density_contexts(atoms)
    user_id = f"fixture_{profile_id}"

    signals: list[dict[str, Any]] = []
    nodes_by_id: dict[str, dict[str, Any]] = {}
    node_signal_ids: dict[str, list[str]] = defaultdict(list)
    role_assignments: list[dict[str, Any]] = []
    update_candidates: list[dict[str, Any]] = []

    for atom in atoms:
        music_ref = normalize_music_ref(atom["music_object_ref"], atom.get("graph_refs") or {})
        node_id = node_id_for(profile_id, music_ref)
        signal_id = f"signal:survey_export:{slug(profile_id)}:{slug(atom['response_id'])}"
        role_policy = provisional_role_policy(atom, density_contexts[atom["evidence_atom_id"]])
        role = role_policy["role"]
        update_id = f"update_candidate:survey_export:{slug(profile_id)}:{slug(atom['response_id'])}:{role}"

        signal = make_signal(
            signal_id=signal_id,
            user_id=user_id,
            atom=atom,
            source=source,
            export=export,
            export_path=export_path,
            music_ref=music_ref,
            node_id=node_id,
            update_id=update_id,
        )
        signals.append(signal)
        node_signal_ids[node_id].append(signal_id)

        if node_id not in nodes_by_id:
            nodes_by_id[node_id] = make_node(node_id, user_id, music_ref, signal_id, atom)

        if role_policy["threshold_allows_role_assignment"]:
            role_assignment_id = f"role:survey_export:{slug(profile_id)}:{slug(atom['response_id'])}:{role}"
            role_assignment = make_role_assignment(
                role_assignment_id=role_assignment_id,
                user_id=user_id,
                atlas_node_id=node_id,
                atom=atom,
                role_policy=role_policy,
                signal_id=signal_id,
            )
            role_assignments.append(role_assignment)
            update_candidates.append(
                make_update_candidate(
                    update_id=update_id,
                    user_id=user_id,
                    source_signal_ids=[signal_id],
                    target_node_id=node_id,
                    target_role_assignment_id=role_assignment_id,
                    atom=atom,
                    music_ref=music_ref,
                    role_policy=role_policy,
                )
            )
        else:
            signal["derived_update_candidate_ids"] = []

    nodes = []
    for node_id, node in sorted(nodes_by_id.items()):
        node["evidence_signal_ids"] = sorted(set(node_signal_ids[node_id]))
        nodes.append(node)

    contradiction_candidates, contradictions = build_contradictions(profile_id, user_id, signals)
    update_candidates.extend(contradiction_candidates)
    digest = build_digest(
        profile_id=profile_id,
        config_id=config_id,
        user_id=user_id,
        export=export,
        signals=signals,
        nodes=nodes,
        role_assignments=role_assignments,
        update_candidates=update_candidates,
        contradictions=contradictions,
    )
    size_report = build_size_report(export_path, output_dir, signals, nodes, role_assignments, update_candidates, digest)
    notes = build_notes(export_path, export, validation, role_assignments, digest)

    write_json(output_dir / "validation_report.json", validation)
    write_jsonl(output_dir / "signals.jsonl", signals)
    write_json(output_dir / "atlas_nodes.json", nodes)
    write_json(output_dir / "atlas_role_assignments.json", role_assignments)
    write_json(output_dir / "possible_atlas_update_candidates.json", update_candidates)
    write_json(output_dir / "atlas_digest_view.json", digest)
    write_text(output_dir / "size_report.md", render_size_report(size_report))
    write_text(output_dir / "rfi_notes.md", notes)
    write_json(
        output_dir / "atlas_records_bundle.json",
        {
            "record_type": "atlas_example_bundle",
            "schema_version": SCHEMA_VERSION,
            "example_name": f"survey_evidence_export_ingestion_{slug(profile_label)}",
            "description": "Schema-validation bundle for Survey Evidence Export v0.1 ingestion records.",
            "records": signals + nodes + role_assignments + update_candidates + [digest],
        },
    )

    return {
        "profile_public_id": profile_id,
        "config_id": config_id,
        "input_file": rel(export_path),
        "output_dir": rel(output_dir),
        "status": validation["status"],
        "signals": len(signals),
        "atlas_nodes": len(nodes),
        "atlas_role_assignments": len(role_assignments),
        "possible_atlas_update_candidates": len(update_candidates),
        "atlas_digest_view": rel(output_dir / "atlas_digest_view.json"),
        "rfi_notes": rel(output_dir / "rfi_notes.md"),
    }


def validate_export_for_atlas(export: dict[str, Any], export_path: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    atoms = export.get("atlas_ingestable", {}).get("evidence_atoms", [])
    evidence_refs = {atom["evidence_ref"] for atom in atoms}
    response_ids = {atom["response_id"] for atom in atoms}
    index = export.get("atlas_ingestable", {}).get("response_ref_index", {})

    if set(index.get("evidence_refs", [])) != evidence_refs:
        errors.append("response_ref_index.evidence_refs does not match evidence atom refs")
    if set(index.get("response_ids", [])) != response_ids:
        errors.append("response_ref_index.response_ids does not match evidence atom response IDs")
    if export.get("construction_only_excluded", {}).get("atlas_ingestable") is not False:
        warnings.append("construction_only_excluded.atlas_ingestable is not explicitly false")

    unresolved_ingestable_refs = []
    apple_truth_violations = []
    familiarity_negative_violations = []
    tag_semantic_violations = []
    evidence_strength_hint_violations = []
    unresolved_music_refs = []
    for atom in atoms:
        if not atom.get("atlas_ingestable", False):
            errors.append(f"{atom.get('evidence_atom_id')} is not marked atlas_ingestable")
        if atom["evidence_ref"] not in evidence_refs:
            errors.append(f"{atom['evidence_atom_id']} evidence_ref is not self-resolving")
        for ref in atom.get("comparison_set", {}).get("peer_response_refs", []):
            if ref not in evidence_refs:
                unresolved_ingestable_refs.append({"evidence_atom_id": atom["evidence_atom_id"], "ref": ref})
        for ref in atom.get("supporting_visible_response_refs", []):
            evidence_ref = ref.get("evidence_ref")
            if evidence_ref not in evidence_refs:
                unresolved_ingestable_refs.append({"evidence_atom_id": atom["evidence_atom_id"], "ref": evidence_ref})
        prior = atom.get("apple_exposure_prior") or {}
        if prior.get("taste_truth") is not False or prior.get("interpretation") != "exposure_prior":
            apple_truth_violations.append(atom["evidence_atom_id"])
        reaction = atom["reaction"]
        if reaction["raw_value"] == "dont_know_enough" and (
            reaction["normalized_operation"] != "familiarity_uncertainty"
            or reaction.get("taste_polarity") == "negative"
        ):
            familiarity_negative_violations.append(atom["evidence_atom_id"])
        tags = atom.get("tags", {})
        if tags.get("selected_semantics") != "visible_signal_evidence":
            tag_semantic_violations.append(f"{atom['evidence_atom_id']}: selected tags")
        if tags.get("shown_but_unselected_semantics") != "weak_non_selected_context":
            tag_semantic_violations.append(f"{atom['evidence_atom_id']}: shown-unselected tags")
        if set(tags.get("selected") or []).intersection(tags.get("shown_but_unselected") or []):
            tag_semantic_violations.append(f"{atom['evidence_atom_id']}: overlapping selected/non-selected tags")
        hint = atom.get("evidence_strength_hint", {})
        if hint.get("source") != "survey" or hint.get("is_final_atlas_confidence") is not False:
            evidence_strength_hint_violations.append(atom["evidence_atom_id"])
        ref = atom["music_object_ref"]
        if ref.get("ref_source") == "unresolved" or ref.get("resolution_state") == "needs_resolution":
            unresolved_music_refs.append(atom["evidence_atom_id"])

    if unresolved_ingestable_refs:
        errors.append(f"{len(unresolved_ingestable_refs)} unresolved refs found inside atlas_ingestable")
    if apple_truth_violations:
        errors.append(f"{len(apple_truth_violations)} Apple priors treated as taste truth")
    if familiarity_negative_violations:
        errors.append(f"{len(familiarity_negative_violations)} familiarity uncertainty atoms treated as negative")
    if tag_semantic_violations:
        errors.append(f"{len(tag_semantic_violations)} tag semantic violation(s)")
    if evidence_strength_hint_violations:
        errors.append(f"{len(evidence_strength_hint_violations)} evidence_strength_hint metadata violation(s)")

    quarantined = export.get("construction_only_excluded", {}).get("quarantined_response_refs", [])
    return {
        "schema_version": "waymark.survey_evidence_export_atlas_validation_report.v0.1",
        "ingestion_version": INGESTION_VERSION,
        "input_file": export_path.name,
        "input_file_ref": rel(export_path),
        "export_schema_version": export.get("schema_version"),
        "export_id": export.get("export_id"),
        "profile_public_id": export.get("source", {}).get("profile_public_id"),
        "visible_evidence_atom_count": len(atoms),
        "response_ref_index_counts": {
            "evidence_refs": len(index.get("evidence_refs", [])),
            "response_ids": len(index.get("response_ids", [])),
        },
        "unresolved_ingestable_response_refs": unresolved_ingestable_refs,
        "construction_only_excluded_ignored": True,
        "quarantined_response_refs_outside_ingestion": quarantined,
        "apple_exposure_prior_policy": {
            "status": "pass" if not apple_truth_violations else "fail",
            "handling": "Apple priors retained as exposure context only and never used for promotion.",
        },
        "familiarity_uncertainty_policy": {
            "status": "pass" if not familiarity_negative_violations else "fail",
            "handling": "dont_know_enough/familiarity_uncertainty becomes unknown/familiarity evidence, not negative taste.",
        },
        "tag_semantics_policy": {
            "status": "pass" if not tag_semantic_violations else "fail",
            "handling": "Selected tags become visible Signal evidence; shown-unselected tags stay weak/non-selected context.",
            "violations": tag_semantic_violations,
        },
        "evidence_strength_hint_policy": {
            "status": "pass" if not evidence_strength_hint_violations else "fail",
            "handling": "evidence_strength_hint is preserved only as Survey metadata, not final Atlas confidence.",
            "violations": evidence_strength_hint_violations,
        },
        "unresolved_music_object_refs": unresolved_music_refs,
        "errors": errors,
        "warnings": warnings,
        "status": "pass" if not errors else "fail",
    }


def build_density_contexts(atoms: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    contexts = {}
    for atom in atoms:
        graph = atom.get("graph_refs") or {}
        families = set(graph.get("family_numbers") or [])
        archetypes = set(graph.get("archetype_ids") or [])
        display_artist = credited_artist(atom)
        neighbors = []
        for other in atoms:
            other_graph = other.get("graph_refs") or {}
            if (
                families.intersection(other_graph.get("family_numbers") or [])
                or archetypes.intersection(other_graph.get("archetype_ids") or [])
                or (display_artist and credited_artist(other) == display_artist)
            ):
                neighbors.append(other)
        total = max(len(neighbors), 1)
        positive = [row for row in neighbors if row["reaction"]["normalized_operation"] in {"positive_high", "positive_medium"}]
        strong_positive = [row for row in neighbors if row["reaction"]["normalized_operation"] == "positive_high"]
        negative = [row for row in neighbors if row["reaction"]["normalized_operation"] == "negative_scope_carefully"]
        unknown = [row for row in neighbors if row["reaction"]["normalized_operation"] == "familiarity_uncertainty"]
        scopes = sorted({row["music_object_ref"]["object_type"] for row in positive})
        contexts[atom["evidence_atom_id"]] = {
            "policy_version": "survey_evidence_export_density_policy_v0.1",
            "neighborhood_size": len(neighbors),
            "local_positive_count": len(positive),
            "local_positive_density": round(len(positive) / total, 3),
            "local_strong_positive_count": len(strong_positive),
            "local_negative_count": len(negative),
            "local_negative_density": round(len(negative) / total, 3),
            "local_unknown_count": len(unknown),
            "local_unknown_density": round(len(unknown) / total, 3),
            "recurrence_scope_count": len(scopes),
            "recurrence_scopes": scopes,
            "graph_family_numbers": sorted(families),
            "graph_archetype_ids": sorted(archetypes),
            "graph_roles": sorted(graph.get("roles") or []),
            "page_intent": atom.get("page_context", {}).get("page_intent"),
            "apple_exposure_score": (atom.get("apple_exposure_prior", {}).get("dimensions") or {}).get("exposure_score", 0.0),
        }
    return contexts


def provisional_role_policy(atom: dict[str, Any], density: dict[str, Any]) -> dict[str, Any]:
    operation = atom["reaction"]["normalized_operation"]
    object_type = atom["music_object_ref"]["object_type"]
    role = "signal_only"
    behavior = "unknown"
    reason = "No threshold met for role assignment."
    allows = True

    if operation == "positive_high":
        if density["local_positive_density"] >= 0.55 and density["recurrence_scope_count"] >= 2:
            role, behavior = "landmark", "anchor"
            reason = "Strong positive evidence is supported by local positive density and cross-scope recurrence."
        elif density["local_negative_density"] >= 0.25:
            role, behavior = "waypoint", "bridge"
            reason = "Strong positive evidence sits inside mixed territory, so it remains a bridge/exception candidate."
        else:
            role, behavior = "frontier", "probe"
            reason = "Strong positive evidence is relatively isolated and should become a high-value Frontier opportunity."
    elif operation == "positive_medium":
        if object_type == "album" or density["local_positive_density"] >= 0.5:
            role, behavior = "waypoint", "bridge"
            reason = "Medium positive evidence has contextual support but is not enough for a Landmark."
        else:
            role, behavior = "frontier", "probe"
            reason = "Medium positive evidence is thin and should be probed as Frontier material."
    elif operation == "waypoint_context":
        role, behavior = "waypoint", "waypoint"
        reason = "Contextual response supports route calibration without Landmark promotion."
    elif operation == "negative_scope_carefully":
        if density["local_positive_count"] > density["local_negative_count"]:
            role, behavior = "unknown", "risky_probe"
            reason = "Negative evidence conflicts with nearby positives; create scoped review rather than a blanket dead end."
        else:
            role, behavior = "dead_end", "trap"
            reason = "Negative evidence can seed a scoped Dead End hypothesis only."
    elif operation == "familiarity_uncertainty":
        role, behavior = "unknown", "risky_probe"
        reason = "Familiarity uncertainty is not negative taste evidence."

    return {
        "threshold_allows_role_assignment": allows,
        "role": role,
        "candidate_pool_behavior": behavior,
        "reason": reason,
        "density_context": density,
        "survey_policy_notes": [
            "Survey Evidence Export creates provisional/candidate records only.",
            "Apple exposure prior is retained as context and does not promote roles.",
            "dont_know_enough/familiarity_uncertainty is not negative evidence.",
            "Road and lineage are not Atlas roles.",
        ],
    }


def make_signal(
    *,
    signal_id: str,
    user_id: str,
    atom: dict[str, Any],
    source: dict[str, Any],
    export: dict[str, Any],
    export_path: Path,
    music_ref: dict[str, Any],
    node_id: str,
    update_id: str,
) -> dict[str, Any]:
    operation = atom["reaction"]["normalized_operation"]
    confidence_score = INTERPRETATION_CONFIDENCE[operation]
    selected_tags = atom.get("tags", {}).get("selected") or []
    shown_unselected = atom.get("tags", {}).get("shown_but_unselected") or []
    return {
        "record_type": "signal",
        "schema_version": SCHEMA_VERSION,
        "signal_id": signal_id,
        "user_id": user_id,
        "source": "survey",
        "event_type": "familiarity" if operation == "familiarity_uncertainty" else "reaction",
        "occurred_at": atom.get("timestamps", {}).get("survey_packet_created_at") or export.get("created_at") or GENERATED_AT,
        "captured_at": atom.get("timestamps", {}).get("exported_at") or export.get("created_at") or GENERATED_AT,
        "subject_music_object_ref": music_ref,
        "subject_atlas_node_id": node_id,
        "reaction_value": REACTION_VALUE_MAP.get(atom["reaction"]["raw_value"], "unknown"),
        "raw_reaction": atom["reaction"]["raw_value"],
        "normalized_signal": NORMALIZED_SIGNAL_MAP[operation],
        "observed_user_tags": selected_tags,
        "shown_unselected_tags": shown_unselected,
        "visible_signal_evidence": {
            "selected_tags": selected_tags,
        },
        "weak_non_selected_context": {
            "shown_unselected_tags": shown_unselected,
        },
        "user_note": atom.get("note"),
        "survey_metadata": {
            "evidence_strength_hint": atom.get("evidence_strength_hint"),
            "use_as_final_atlas_confidence": False,
            "selected_tags_semantics": atom.get("tags", {}).get("selected_semantics"),
            "shown_unselected_tags_semantics": atom.get("tags", {}).get("shown_but_unselected_semantics"),
        },
        "source_context": {
            "source_export_id": export["export_id"],
            "source_file_ref": rel(export_path),
            "source_session_id": source["survey_run_id"],
            "source_input_fingerprint": source["source_input_fingerprint"],
            "source_public_packet_sha256": source["source_public_packet_sha256"],
            "source_payload_ref": source["source_packet_path"],
            "source_payload_schema_version": source["source_packet_schema_version"],
            "survey_item_id": atom["response_id"],
            "response_id": atom["response_id"],
            "evidence_atom_id": atom["evidence_atom_id"],
            "evidence_ref": atom["evidence_ref"],
            "visible_packet_id": source["survey_run_id"],
            "simulation_profile_id": source["profile_public_id"],
            "comparison_set_id": atom.get("comparison_set", {}).get("comparison_set_id"),
            "supporting_visible_response_refs": atom.get("supporting_visible_response_refs", []),
        },
        "page_context": {
            **atom.get("page_context", {}),
            "comparison_set": atom.get("comparison_set"),
            "graph_refs": atom.get("graph_refs"),
        },
        "apple_exposure_context": {
            "context_type": "exposure_import_familiarity_not_taste_truth",
            "apple_payload_id": source.get("apple_payload_id"),
            "apple_evidence_refs": atom.get("apple_exposure_prior", {}).get("signal_ids", []),
            "apple_evidence_summary": atom.get("apple_exposure_prior", {}).get("dimensions", {}),
            "taste_truth": False,
        },
        "integrity_state": "valid",
        "signal_strength": SIGNAL_STRENGTH[operation],
        "interpretation_confidence": confidence_score,
        "confidence": confidence(
            confidence_score,
            "direct_user_reaction" if operation != "familiarity_uncertainty" else "survey_pattern",
            confidence_summary(atom),
        ),
        "derived_update_candidate_ids": [update_id],
        "lifecycle": lifecycle("active", "unreviewed", "proposed"),
    }


def make_node(node_id: str, user_id: str, music_ref: dict[str, Any], signal_id: str, atom: dict[str, Any]) -> dict[str, Any]:
    timestamp = atom.get("timestamps", {}).get("survey_packet_created_at") or GENERATED_AT
    return {
        "record_type": "atlas_node",
        "schema_version": SCHEMA_VERSION,
        "atlas_node_id": node_id,
        "user_id": user_id,
        "node_type": music_ref["object_type"],
        "display_name": music_ref["display_name"],
        "subtitle": f"Survey Evidence Export {music_ref['object_type'].replace('_', ' ')}",
        "music_object_ref": music_ref,
        "origin": "survey",
        "render_hints": {
            "primary_label": music_ref["display_name"],
            "secondary_label": "Survey-seeded object",
            "card_summary": "Object record created so Atlas can reason about survey evidence; role truth is stored only in AtlasRoleAssignment.",
        },
        "lifecycle": lifecycle("provisional", "unreviewed", "candidate"),
        "confidence": confidence(0.4, "survey_pattern", "Node exists to preserve visible Survey Evidence Export atoms. It carries no role truth."),
        "evidence_signal_ids": [signal_id],
        "created_at": timestamp,
        "updated_at": timestamp,
    }


def make_role_assignment(
    *,
    role_assignment_id: str,
    user_id: str,
    atlas_node_id: str,
    atom: dict[str, Any],
    role_policy: dict[str, Any],
    signal_id: str,
) -> dict[str, Any]:
    role = role_policy["role"]
    review_state = "needs_review" if role in {"landmark", "dead_end", "waypoint"} else "unreviewed"
    score = INTERPRETATION_CONFIDENCE[atom["reaction"]["normalized_operation"]]
    return {
        "record_type": "atlas_role_assignment",
        "schema_version": SCHEMA_VERSION,
        "atlas_role_assignment_id": role_assignment_id,
        "user_id": user_id,
        "atlas_node_id": atlas_node_id,
        "role": role,
        "scope": {"scope_type": "global", "scope_id": None, "scope_label": None},
        "candidate_pool_behavior": role_policy["candidate_pool_behavior"],
        "assignment_summary": f"{role_policy['reason']} Provisional Survey-created role only.",
        "lifecycle": lifecycle("provisional", review_state, "candidate"),
        "confidence": confidence(min(0.74, score), "survey_pattern", "Survey-created role assignment is provisional and cannot be promoted by Survey alone."),
        "evidence_signal_ids": [signal_id],
        "created_at": GENERATED_AT,
        "updated_at": GENERATED_AT,
    }


def make_update_candidate(
    *,
    update_id: str,
    user_id: str,
    source_signal_ids: list[str],
    target_node_id: str,
    target_role_assignment_id: str,
    atom: dict[str, Any],
    music_ref: dict[str, Any],
    role_policy: dict[str, Any],
) -> dict[str, Any]:
    role = role_policy["role"]
    review_required = role in {"landmark", "dead_end", "waypoint", "unknown"}
    return {
        "record_type": "possible_atlas_update_candidate",
        "schema_version": SCHEMA_VERSION,
        "update_candidate_id": update_id,
        "user_id": user_id,
        "source": "survey",
        "source_signal_ids": source_signal_ids,
        "target_atlas_node_id": target_node_id,
        "target_role_assignment_id": target_role_assignment_id,
        "proposed_record_type": "atlas_role_assignment",
        "proposed_action": "create",
        "proposed_payload": {
            "atlas_node_id": target_node_id,
            "role": role,
            "candidate_pool_behavior": role_policy["candidate_pool_behavior"],
            "policy_version": role_policy["density_context"]["policy_version"],
            "policy_reason": role_policy["reason"],
            "density_context": role_policy["density_context"],
            "survey_seed_only": True,
            "source_evidence_atom_id": atom["evidence_atom_id"],
            "source_response_id": atom["response_id"],
            "raw_reaction": atom["reaction"]["raw_value"],
            "normalized_operation": atom["reaction"]["normalized_operation"],
            "music_object_ref": music_ref,
            "apple_music_context_policy": "exposure_prior_not_taste_truth",
            "scope_limit": scope_limit_for(music_ref, atom["reaction"]["normalized_operation"]),
            "policy_notes": role_policy["survey_policy_notes"],
        },
        "confidence_delta": confidence_delta(atom["reaction"]["normalized_operation"]),
        "recurrence_requirement": {
            "required_count": 2 if role in {"landmark", "frontier", "dead_end", "waypoint"} else 1,
            "min_distinct_sources": 1,
            "satisfied": False,
        },
        "review_requirement": {
            "required": review_required,
            "reviewer_type": "human" if review_required else "none",
            "reason": review_reason(role, atom["reaction"]["normalized_operation"]),
        },
        "canonical_graph_mutation_allowed": False,
        "generated_hypothesis_only": False,
        "lifecycle": lifecycle("provisional", "needs_review" if review_required else "unreviewed", "candidate"),
        "created_at": GENERATED_AT,
        "updated_at": GENERATED_AT,
    }


def build_contradictions(profile_id: str, user_id: str, signals: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    by_credit: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for signal in signals:
        ref = signal["subject_music_object_ref"]
        key = ref.get("credited_artist_name") or ref.get("display_name")
        if key:
            by_credit[key].append(signal)

    candidates = []
    contradictions = []
    for label, rows in sorted(by_credit.items()):
        positives = [row for row in rows if row.get("raw_reaction") in {"love", "like"}]
        negatives = [row for row in rows if row.get("raw_reaction") == "dont_like"]
        if not positives or not negatives:
            continue
        signal_ids = [row["signal_id"] for row in positives + negatives]
        cluster_id = f"contradiction:survey_export:{slug(profile_id)}:{slug(label)}"
        contradictions.append(
            {
                "cluster_id": cluster_id,
                "label": label,
                "positive_signal_ids": [row["signal_id"] for row in positives],
                "negative_signal_ids": [row["signal_id"] for row in negatives],
                "scope_warning": "Mixed visible evidence. Do not broaden the negative signal into genre-level rejection.",
            }
        )
        candidates.append(
            {
                "record_type": "possible_atlas_update_candidate",
                "schema_version": SCHEMA_VERSION,
                "update_candidate_id": f"update_candidate:survey_export:{slug(profile_id)}:contradiction:{slug(label)}",
                "user_id": user_id,
                "source": "survey",
                "source_signal_ids": signal_ids,
                "target_atlas_node_id": None,
                "target_role_assignment_id": None,
                "proposed_record_type": "atlas_role_assignment",
                "proposed_action": "resolution_request",
                "proposed_payload": {
                    "candidate_type": "contradiction_cluster",
                    "cluster_id": cluster_id,
                    "cluster_label": label,
                    "recommended_role": "unknown",
                    "candidate_pool_behavior": "risky_probe",
                    "scope_limit": "object_or_recording_level_until_tested",
                    "positive_signal_ids": [row["signal_id"] for row in positives],
                    "negative_signal_ids": [row["signal_id"] for row in negatives],
                },
                "confidence_delta": 0.08,
                "recurrence_requirement": {"required_count": 2, "min_distinct_sources": 1, "satisfied": True},
                "review_requirement": {
                    "required": True,
                    "reviewer_type": "human",
                    "reason": "Contradictory visible survey evidence requires scoped review or mission testing.",
                },
                "canonical_graph_mutation_allowed": False,
                "generated_hypothesis_only": False,
                "lifecycle": lifecycle("provisional", "needs_review", "candidate"),
                "created_at": GENERATED_AT,
                "updated_at": GENERATED_AT,
            }
        )
    return candidates, contradictions


def build_digest(
    *,
    profile_id: str,
    config_id: str,
    user_id: str,
    export: dict[str, Any],
    signals: list[dict[str, Any]],
    nodes: list[dict[str, Any]],
    role_assignments: list[dict[str, Any]],
    update_candidates: list[dict[str, Any]],
    contradictions: list[dict[str, Any]],
) -> dict[str, Any]:
    nodes_by_id = {node["atlas_node_id"]: node for node in nodes}
    grouped_roles: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for role in role_assignments:
        grouped_roles[role["role"]].append(role)

    role_ids = {key: [] for key in ["landmarks", "regions", "frontiers", "dead_ends", "waypoints"]}
    candidate_fields = {field: [] for field in ROLE_BUCKET_TO_DIGEST_FIELD.values()}
    for role in sorted(role_assignments, key=lambda item: item["confidence"]["confidence_score"], reverse=True):
        role_ids_key = f"{role['role']}s" if role["role"] != "dead_end" else "dead_ends"
        if role_ids_key in role_ids:
            role_ids[role_ids_key].append(role["atlas_role_assignment_id"])
        field = ROLE_BUCKET_TO_DIGEST_FIELD.get(role["role"])
        if field and len(candidate_fields[field]) < 8:
            candidate_fields[field].append(digest_role_summary(role, nodes_by_id.get(role["atlas_node_id"])))

    recent_signals = signals[-12:]
    unknown_count = sum(1 for signal in signals if signal["raw_reaction"] == "dont_know_enough")
    unresolved_questions = []
    if contradictions:
        unresolved_questions.append("Contradictory visible evidence needs scoped mission testing before promotion.")
    if unknown_count:
        unresolved_questions.append(f"{unknown_count} familiarity-uncertainty responses need exposure or recognition checks, not negative interpretation.")
    unresolved_questions.append("Family/archetype IDs are refs only unless a dictionary is available.")

    digest = {
        "record_type": "atlas_digest_view",
        "schema_version": SCHEMA_VERSION,
        "digest_id": f"atlas_digest_view:survey_export:{slug(profile_id)}:{slug(config_id)}",
        "user_id": user_id,
        "generated_at": GENERATED_AT,
        "mission_context": "starter_atlas_wwtsf_first_mission_and_correction_from_survey_evidence_export",
        "relevant_role_assignment_ids": role_ids,
        "user_taste_feature_state_ids": [],
        "user_vocabulary_term_ids": [],
        "user_taste_feature_states": [],
        "user_vocabulary_terms": [],
        "anti_overfitting_rules": [
            "Do not treat Survey-created roles as promoted Atlas truth.",
            "Do not broaden negative responses into genre-level dislikes without scoped recurrence.",
            "Treat dont_know_enough/familiarity_uncertainty as familiarity uncertainty, not negative evidence.",
            "Apple Music evidence is exposure/import/familiarity context, not taste truth.",
            "Do not infer family or archetype names when graph meanings are unavailable.",
            "Road and lineage are not Atlas roles.",
        ],
        "recent_signal_ids": [signal["signal_id"] for signal in recent_signals],
        "recent_signals": [compact_signal(signal) for signal in recent_signals],
        "signal_summaries": [compact_signal(signal) for signal in recent_signals],
        "unresolved_questions": unresolved_questions,
        "mission_relevant_constraints": [
            "Consume AtlasDigestView and AtlasRoleAssignment, not raw Survey payload.",
            "Mission Generation may return PossibleAtlasUpdateCandidate hypotheses only.",
            "No canonical graph mutation path is available from this digest.",
            "Mission hints are hypotheses and must not become mission objects in this ingestion step.",
        ],
        "suggested_candidate_roles": [
            {
                "music_object_ref": nodes_by_id[role["atlas_node_id"]]["music_object_ref"],
                "suggested_role": role["role"],
                "candidate_pool_behavior": role["candidate_pool_behavior"],
                "confidence": role["confidence"],
                "source_signal_ids": role["evidence_signal_ids"],
                "review_required": role["lifecycle"]["review_state"] == "needs_review",
                "reason": role.get("assignment_summary", ""),
            }
            for role in role_assignments[:18]
            if role["role"] != "signal_only" and role["atlas_node_id"] in nodes_by_id
        ],
        "candidate_pool_behavior_hints": [
            digest_role_summary(role, nodes_by_id.get(role["atlas_node_id"]))
            for role in role_assignments[:24]
        ],
        "contradictions": contradictions,
        "user_taste_feature_summaries": [],
        "starter_atlas_state": {
            "source_export_id": export["export_id"],
            "signal_count": len(signals),
            "node_count": len(nodes),
            "role_assignment_count": len(role_assignments),
            "possible_update_candidate_count": len(update_candidates),
            "source_of_role_truth": "AtlasRoleAssignment only; AtlasNode has no authoritative role truth.",
        },
        "mission_generation_inputs": {
            "first_batch_source": "candidate landmarks/frontiers/dead-end hypotheses/waypoints, recent signals, contradictions, and unresolved questions in this digest",
            "second_batch_source": "mission review feedback should append Signals and PossibleAtlasUpdateCandidates, then regenerate the digest",
            "mission_objects_created_here": False,
        },
        "wwtsf_inputs": {
            "source": "AtlasDigestView plus Signal summaries",
            "final_copy_generated_here": False,
            "copy_policy": "Use as substrate for WWTSF-style rendering, not final Atlas truth.",
        },
        "evidence_audit": {
            "all_signals_trace_to_visible_survey_evidence_atoms": True,
            "source_export_id": export["export_id"],
            "evidence_atom_count": len(signals),
            "raw_payload_required_for_audit": False,
        },
        "future_correction": {
            "append_only_source_semantics": export.get("ledger_semantics", {}).get("mode") == "append_only",
            "correction_source_records": ["Signal", "AtlasRoleAssignment", "PossibleAtlasUpdateCandidate", "AtlasDigestView"],
            "promotion_requires_separate_policy_or_review": True,
            "canonical_graph_mutation_allowed": False,
        },
        "consumer_contract": {
            "intended_consumers": ["WWTSF", "Mission Generation", "Candidate Pool Builder", "node interpretation", "evidence audit", "future correction"],
            "raw_survey_payload_required": False,
            "canonical_graph_mutation_allowed": False,
            "survey_role_promotion_allowed": False,
        },
    }
    digest.update(candidate_fields)
    return digest


def normalize_music_ref(ref: dict[str, Any], graph_refs: dict[str, Any]) -> dict[str, Any]:
    object_type = ref["object_type"]
    credited = ref.get("credited_artist_name") or ref.get("artist_display_name") or ref.get("display_name")
    normalized = {
        "object_type": object_type,
        "ref_source": ref.get("ref_source", "unresolved"),
        "canonical_artist_id": ref.get("canonical_artist_id"),
        "canonical_album_id": ref.get("canonical_album_id"),
        "canonical_song_recording_id": ref.get("canonical_song_recording_id"),
        "composition_placeholder_id": ref.get("composition_placeholder_id"),
        "user_music_object_id": ref.get("user_music_object_id"),
        "external_catalog_refs": ref.get("external_catalog_refs") or {},
        "display_name": ref["display_name"],
        "credited_artist_name": credited,
        "credit_context": ref.get("credit_context", "unknown"),
        "resolution_state": ref.get("resolution_state", "needs_resolution" if ref.get("ref_source") == "unresolved" else "resolved"),
        "composition_policy_status": ref.get("composition_policy_status", "needs_review" if object_type in {"song_recording", "composition_placeholder"} else "not_applicable"),
        "recording_variant_type": ref.get("recording_variant_type", "unknown" if object_type == "song_recording" else None),
        "canonical_membership_context": {
            "family_numbers": graph_refs.get("family_numbers") or [],
            "archetype_ids": graph_refs.get("archetype_ids") or [],
            "membership_role_notes": "Survey graph roles are canonical membership context only, not Atlas role truth.",
        },
    }
    return normalized


def node_id_for(profile_id: str, music_ref: dict[str, Any]) -> str:
    object_type = music_ref["object_type"]
    identifier = (
        music_ref.get("canonical_artist_id")
        or music_ref.get("canonical_album_id")
        or music_ref.get("canonical_song_recording_id")
        or music_ref.get("composition_placeholder_id")
        or music_ref.get("user_music_object_id")
        or slug(music_ref["display_name"])
    )
    return f"atlas_node:survey_export:{slug(profile_id)}:{object_type}:{slug(identifier)}"


def digest_role_summary(role: dict[str, Any], node: dict[str, Any] | None) -> dict[str, Any]:
    lifecycle_state = role["lifecycle"]
    return {
        "atlas_role_assignment_id": role["atlas_role_assignment_id"],
        "atlas_node_id": role["atlas_node_id"],
        "name": node["display_name"] if node else role["atlas_node_id"],
        "music_object_ref": node["music_object_ref"] if node else None,
        "role": role["role"],
        "candidate_pool_behavior": role["candidate_pool_behavior"],
        "status": lifecycle_state["status"],
        "review_state": lifecycle_state["review_state"],
        "promotion_state": lifecycle_state["promotion_state"],
        "confidence": role["confidence"],
        "evidence_signal_ids": role["evidence_signal_ids"],
        "summary": role.get("assignment_summary", ""),
        "survey_seed_only": True,
        "authoritative_role_truth_source": "atlas_role_assignment",
    }


def compact_signal(signal: dict[str, Any]) -> dict[str, Any]:
    ref = signal["subject_music_object_ref"]
    return {
        "signal_id": signal["signal_id"],
        "source": signal["source"],
        "event_type": signal["event_type"],
        "subject_display_name": ref["display_name"],
        "object_type": ref["object_type"],
        "raw_reaction": signal.get("raw_reaction"),
        "reaction_value": signal["reaction_value"],
        "normalized_signal": signal.get("normalized_signal"),
        "selected_tags": signal["observed_user_tags"],
        "shown_unselected_tags": signal.get("shown_unselected_tags", []),
        "selected_tags_semantics": signal.get("survey_metadata", {}).get("selected_tags_semantics"),
        "shown_unselected_tags_semantics": signal.get("survey_metadata", {}).get("shown_unselected_tags_semantics"),
        "signal_strength": signal["signal_strength"],
        "interpretation_confidence": signal["interpretation_confidence"],
        "evidence_ref": signal["source_context"]["evidence_ref"],
        "page_id": signal["page_context"].get("page_id"),
        "page_intent": signal["page_context"].get("page_intent"),
        "apple_context_policy": signal["apple_exposure_context"]["context_type"],
    }


def build_size_report(
    export_path: Path,
    output_dir: Path,
    signals: list[dict[str, Any]],
    nodes: list[dict[str, Any]],
    role_assignments: list[dict[str, Any]],
    update_candidates: list[dict[str, Any]],
    digest: dict[str, Any],
) -> dict[str, Any]:
    raw_size = export_path.stat().st_size
    serialized = {
        "signals": "\n".join(stable_json(row) for row in signals) + "\n",
        "nodes": pretty_json(nodes),
        "roles": pretty_json(role_assignments),
        "updates": pretty_json(update_candidates),
        "digest": pretty_json(digest),
    }
    return {
        "schema_version": "waymark.survey_evidence_export_atlas_size_report.v0.1",
        "source_export": {"path": rel(export_path), "bytes": raw_size},
        "output_dir": rel(output_dir),
        "signals_jsonl": {"bytes": len(serialized["signals"].encode("utf-8")), "ratio_vs_raw": ratio(len(serialized["signals"].encode("utf-8")), raw_size)},
        "atlas_nodes_json": {"bytes": len(serialized["nodes"].encode("utf-8"))},
        "atlas_role_assignments_json": {"bytes": len(serialized["roles"].encode("utf-8"))},
        "possible_atlas_update_candidates_json": {"bytes": len(serialized["updates"].encode("utf-8"))},
        "atlas_digest_view_json": {
            "bytes": len(serialized["digest"].encode("utf-8")),
            "ratio_vs_raw": ratio(len(serialized["digest"].encode("utf-8")), raw_size),
            "raw_to_digest_reduction_percent": round((1 - len(serialized["digest"].encode("utf-8")) / raw_size) * 100, 2),
        },
    }


def render_size_report(report: dict[str, Any]) -> str:
    digest = report["atlas_digest_view_json"]
    lines = [
        "# Size Report",
        "",
        f"- Source export: `{report['source_export']['path']}`",
        f"- Raw Survey Evidence Export: `{report['source_export']['bytes']}` bytes",
        f"- Signals JSONL: `{report['signals_jsonl']['bytes']}` bytes; ratio vs raw `{report['signals_jsonl']['ratio_vs_raw']}`",
        f"- AtlasNodes JSON: `{report['atlas_nodes_json']['bytes']}` bytes",
        f"- AtlasRoleAssignments JSON: `{report['atlas_role_assignments_json']['bytes']}` bytes",
        f"- PossibleAtlasUpdateCandidates JSON: `{report['possible_atlas_update_candidates_json']['bytes']}` bytes",
        f"- AtlasDigestView JSON: `{digest['bytes']}` bytes; ratio vs raw `{digest['ratio_vs_raw']}`",
        f"- Raw-to-digest reduction: `{digest['raw_to_digest_reduction_percent']}`%",
        "",
        "## Acceptance Notes",
        "",
        "- Digest is designed as downstream substrate for starter Atlas state, WWTSF-style rendering, first mission generation, evidence audit, and future correction.",
        "- Raw Survey Evidence Export is not required by downstream consumers once this digest and record bundle exist.",
    ]
    return "\n".join(lines) + "\n"


def build_notes(export_path: Path, export: dict[str, Any], validation: dict[str, Any], role_assignments: list[dict[str, Any]], digest: dict[str, Any]) -> str:
    lines = [
        "# Schema Mismatch / RFI Notes",
        "",
        f"- Source export: `{rel(export_path)}`",
        f"- Validation status: `{validation['status']}`",
        "- No canonical graph mutation path is present.",
        "- `construction_only_excluded` was read only for validation/reporting and ignored for Atlas ingestion.",
        "- Apple exposure prior is retained on Signals as exposure context and does not promote roles.",
        "- `dont_know_enough` / `familiarity_uncertainty` is represented as familiarity/unknown evidence, not negative taste.",
        "- AtlasNode records contain no role fields; role truth is only in AtlasRoleAssignment.",
        "- Survey-created AtlasRoleAssignments use `status=provisional` and `promotion_state=candidate` only.",
    ]
    if not role_assignments:
        lines.append("- RFI: No role assignments met threshold; downstream consumers would need signal-only handling.")
    if not digest.get("candidate_regions"):
        lines.append("- RFI: No candidate Regions are emitted from this A3 export. This appears correct for the current threshold policy; do not fabricate Regions from thin evidence.")
    if validation["errors"]:
        lines.append("")
        lines.append("## Validation Errors")
        lines.extend(f"- {error}" for error in validation["errors"])
    return "\n".join(lines) + "\n"


def render_manifest_readme(profiles: list[dict[str, Any]]) -> str:
    lines = [
        "# Survey Evidence Export to Atlas Ingestion Proof v0.1",
        "",
        f"Generated: {GENERATED_AT}",
        "",
        "Flow: `Survey Evidence Export -> Signal -> AtlasNode -> provisional AtlasRoleAssignment -> PossibleAtlasUpdateCandidate -> AtlasDigestView`",
        "",
        "| profile | status | signals | nodes | roles | candidates | output |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in profiles:
        lines.append(
            f"| {row['profile_public_id']} | {row['status']} | {row['signals']} | {row['atlas_nodes']} | "
            f"{row['atlas_role_assignments']} | {row['possible_atlas_update_candidates']} | `{row['output_dir']}` |"
        )
    return "\n".join(lines) + "\n"


def hard_rules() -> dict[str, Any]:
    return {
        "canonical_graph_mutation_allowed": False,
        "atlas_node_role_truth_allowed": False,
        "atlas_role_assignment_owns_role_truth": True,
        "survey_created_promoted_roles_allowed": False,
        "apple_exposure_prior_promotes_roles_by_itself": False,
        "familiarity_uncertainty_becomes_negative_taste": False,
        "construction_only_excluded_ingested": False,
        "signals_trace_to_visible_survey_evidence_atoms": True,
        "evidence_strength_hint_is_survey_metadata_only": True,
        "selected_tags_become_visible_signal_evidence": True,
        "shown_unselected_tags_are_weak_non_selected_context": True,
    }


def credited_artist(atom: dict[str, Any]) -> str | None:
    ref = atom.get("music_object_ref") or {}
    return ref.get("credited_artist_name") or ref.get("artist_display_name") or (
        ref.get("display_name") if ref.get("object_type") == "artist" else None
    )


def scope_limit_for(music_ref: dict[str, Any], operation: str) -> str:
    if operation == "familiarity_uncertainty":
        return "familiarity_only"
    if music_ref["object_type"] == "song_recording":
        return "recording_level"
    if music_ref["object_type"] == "album":
        return "album_level"
    if operation == "negative_scope_carefully":
        return "artist_level_only_until_recurrence"
    return "object_level_until_recurrence"


def confidence_summary(atom: dict[str, Any]) -> str:
    operation = atom["reaction"]["normalized_operation"]
    if operation == "positive_high":
        return "Love is strong survey evidence but remains provisional until recurrence or review."
    if operation == "positive_medium":
        return "Like is positive survey evidence but not enough for broad promotion."
    if operation == "waypoint_context":
        return "Ok is contextual/waypoint evidence, not Landmark evidence."
    if operation == "negative_scope_carefully":
        return "Negative evidence is scoped to the smallest justified object."
    return "Familiarity uncertainty is not negative taste evidence."


def confidence_delta(operation: str) -> float:
    return {
        "positive_high": 0.22,
        "positive_medium": 0.14,
        "waypoint_context": 0.04,
        "negative_scope_carefully": -0.12,
        "familiarity_uncertainty": 0.0,
    }[operation]


def review_reason(role: str, operation: str) -> str:
    if role == "landmark":
        return "Candidate Landmark from Survey requires recurrence or review before promotion."
    if role == "dead_end":
        return "Dead End hypothesis from Survey requires scope review before exclusion behavior."
    if operation == "familiarity_uncertainty":
        return "Familiarity uncertainty should be reviewed or tested before any role promotion."
    return "Survey-created candidate remains provisional."


def confidence(score: float, basis: str, summary: str) -> dict[str, Any]:
    if score >= 0.67:
        band = "medium"
    elif score >= 0.45:
        band = "medium"
    else:
        band = "low"
    return {
        "confidence_score": round(score, 3),
        "confidence_band": band,
        "confidence_basis": basis,
        "confidence_summary": summary,
    }


def lifecycle(status: str, review_state: str, promotion_state: str) -> dict[str, str]:
    return {"status": status, "review_state": review_state, "promotion_state": promotion_state}


def ratio(numerator: int | float, denominator: int | float | None) -> float | None:
    if not denominator:
        return None
    return round(numerator / denominator, 4)


def slug(value: Any) -> str:
    text = str(value).strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = text.strip("_")
    return text or "unknown"


def stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def pretty_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(pretty_json(value), encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(stable_json(row))
            handle.write("\n")


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(REPO_ROOT))


if __name__ == "__main__":
    raise SystemExit(main())
