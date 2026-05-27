#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
BASE_DIR = REPO_ROOT / "data/closed_loop_simulation/a3_first_batch_learning_v0_1"
PRIOR_DIGEST_DIR = REPO_ROOT / "data/atlas_schema/ingestion_proof/survey_to_atlas_digest_v0_1"
OUT_DIR = REPO_ROOT / "data/atlas_schema/examples"
GENERATED_AT = "2026-05-21T18:00:00Z"


PROFILE_MAP = {
    "profile_01": "profile_01_A3",
    "profile_05": "profile_05_A3",
    "profile_06": "profile_06_A3",
}


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for profile_dir_name, profile_id in PROFILE_MAP.items():
        delta = build_delta(profile_dir_name, profile_id)
        output = OUT_DIR / f"atlas_delta_closed_loop_{profile_dir_name}.json"
        write_json(output, delta)
    return 0


def build_delta(profile_dir_name: str, profile_id: str) -> dict[str, Any]:
    profile_dir = BASE_DIR / profile_dir_name
    update_records = load_json(profile_dir / "atlas_update_records_after_batch_1.json")
    updated_digest = load_json(profile_dir / "atlas_digest_after_batch_1.json")
    feedback = load_json(profile_dir / "simulated_mission_feedback_atlas_payload.json")

    prior_digest_path = PRIOR_DIGEST_DIR / f"{profile_dir_name}_A3" / "atlas_digest_view.json"
    updated_digest_path = profile_dir / "atlas_digest_after_batch_1.json"
    source_event_id = feedback.get("batch_id") or f"{profile_id}_first_batch_001"
    changes = update_records.get("role_assignment_candidate_changes", [])
    candidates = update_records.get("possible_atlas_update_candidates", [])
    confidence_deltas = update_records.get("confidence_deltas", [])
    signals = update_records.get("signals", [])

    candidate_by_signal = {
        (candidate.get("evidence_signal_ids") or [None])[0]: candidate
        for candidate in candidates
    }
    signal_by_id = {signal["signal_id"]: signal for signal in signals}

    strengthened = []
    weakened = []
    new_frontiers = []
    new_waypoints = []
    new_dead_ends = []
    confidence_changes = []
    paused_paths = []
    promotion_recommendations = []
    promotion_blockers = []
    demotion_recommendations = []
    scope_changes = []

    for change in changes:
        signal_id = first(change.get("evidence_signal_ids"))
        candidate = candidate_by_signal.get(signal_id, {})
        signal = signal_by_id.get(signal_id, {})
        role = normalize_role(change.get("proposed_role") or candidate.get("atlas_role"))
        item = role_change_item(change, candidate, signal)
        delta = float(change.get("confidence_delta") or candidate.get("confidence_delta") or 0.0)
        if delta > 0:
            strengthened.append(item)
        elif delta < 0:
            weakened.append(item)

        if role == "frontier" and delta > 0:
            new_frontiers.append(candidate_item(change, candidate, signal, "frontier"))
        elif role == "waypoint" and delta > 0:
            new_waypoints.append(candidate_item(change, candidate, signal, "waypoint"))
        elif role == "dead_end":
            new_dead_ends.append(candidate_item(change, candidate, signal, "dead_end"))

        confidence_changes.append(confidence_change_item(change, candidate, signal))

        if signal.get("playback_status") == "skipped" or delta <= 0:
            paused_paths.append(paused_path_item(change, candidate, signal))

        if delta >= 0.12:
            promotion_recommendations.append(
                {
                    "target_ref": target_ref(change, candidate, signal),
                    "recommendation": "review_for_candidate_reinforcement",
                    "promotion_state": "candidate",
                    "auto_promote": False,
                    "reason": "Meaningful positive confidence movement, but closed-loop policy requires review and recurrence before promotion.",
                    "evidence_refs": evidence_refs(change, candidate, signal),
                }
            )

        if candidate.get("review_required", True) or candidate.get("auto_promote") is False:
            promotion_blockers.append(
                {
                    "target_ref": target_ref(change, candidate, signal),
                    "blocker_type": "review_or_recurrence_required",
                    "reason": "; ".join(candidate.get("trigger_conditions") or ["future recurrence required before promotion"]),
                    "evidence_refs": evidence_refs(change, candidate, signal),
                }
            )

        if delta < 0:
            demotion_recommendations.append(
                {
                    "target_ref": target_ref(change, candidate, signal),
                    "recommendation": "do_not_demote_without_review",
                    "reason": "Negative movement is scoped mission evidence; it should create review pressure, not automatic demotion.",
                    "evidence_refs": evidence_refs(change, candidate, signal),
                }
            )

        if role in {"dead_end", "signal_only"} or delta <= 0:
            scope_changes.append(scope_change_item(change, candidate, signal))

    unresolved = [
        {
            "question": question,
            "evidence_refs": [],
            "resolution_path": "future_mission_or_review",
        }
        for question in updated_digest.get("unresolved_questions_after_batch_1", [])
    ]

    delta = {
        "schema_version": "waymark.atlas_delta.v0.1",
        "atlas_delta_id": f"atlas_delta:closed_loop:{slug(profile_id)}:batch_1",
        "user_id": None,
        "fixture_profile_id": profile_id,
        "source_event_type": "mission_batch",
        "source_event_id": source_event_id,
        "created_at": GENERATED_AT,
        "prior_digest_ref": {
            "digest_id": load_json(prior_digest_path)["digest_id"] if prior_digest_path.exists() else None,
            "path": rel(prior_digest_path),
        },
        "updated_digest_ref": {
            "digest_id": updated_digest.get("digest_id"),
            "path": rel(updated_digest_path),
        },
        "strengthened_roles": strengthened,
        "weakened_roles": weakened,
        "new_candidate_landmarks": [],
        "new_candidate_frontiers": new_frontiers,
        "new_dead_end_hypotheses": new_dead_ends,
        "new_waypoints": new_waypoints,
        "contradictions": [
            {
                "contradiction_id": item.get("cluster_id") or f"contradiction:{slug(item.get('label', 'unknown'))}",
                "label": item.get("label", "unknown"),
                "positive_evidence_refs": evidence_ref_list(item.get("positive_signal_ids", [])),
                "negative_evidence_refs": evidence_ref_list(item.get("negative_signal_ids", [])),
                "scope_warning": item.get("scope_warning", "Requires scoped review."),
                "review_requirement": {"required": True, "reason": "Contradiction cannot be promoted as truth."},
            }
            for item in update_records.get("contradiction_clusters", [])
        ],
        "unresolved_questions": unresolved,
        "paused_paths": dedupe_by_key(paused_paths, "path_id")[:10],
        "promotion_recommendations": dedupe_by_target(promotion_recommendations)[:8],
        "promotion_blockers": dedupe_by_target(promotion_blockers)[:10],
        "demotion_recommendations": dedupe_by_target(demotion_recommendations)[:8],
        "confidence_changes": confidence_changes,
        "scope_changes": dedupe_by_target(scope_changes)[:10],
        "next_mission_implications": next_mission_implications(updated_digest, new_frontiers, new_dead_ends, new_waypoints, unresolved),
        "user_facing_summary_inputs": {
            "not_final_copy": True,
            "learned_bullets": learned_bullets(profile_id, update_records, new_frontiers, new_dead_ends, new_waypoints),
            "caution_bullets": [
                "No Atlas truth was promoted by this delta.",
                "Review and recurrence are still required before promotion or demotion.",
                "Unresolved questions should drive the next route, not broad claims.",
            ],
            "evidence_refs": evidence_ref_list([signal["signal_id"] for signal in signals[:12]]),
        },
        "hard_rule_checks": {
            "atlas_delta_is_promoted_truth": False,
            "derived_from_signals_role_assignments_and_update_candidates": True,
            "canonical_graph_mutation_allowed": False,
            "auto_promotions": update_records.get("summary", {}).get("auto_promotions", 0),
            "canonical_graph_mutations": update_records.get("summary", {}).get("canonical_graph_mutations", 0),
        },
    }
    return delta


def role_change_item(change: dict[str, Any], candidate: dict[str, Any], signal: dict[str, Any]) -> dict[str, Any]:
    return {
        "change_id": change.get("change_id") or candidate.get("candidate_id"),
        "target_ref": target_ref(change, candidate, signal),
        "role": normalize_role(change.get("proposed_role") or candidate.get("atlas_role")),
        "change_direction": "strengthened" if (change.get("confidence_delta") or 0) > 0 else "weakened",
        "confidence_delta": change.get("confidence_delta") or candidate.get("confidence_delta") or 0,
        "promotion_state": normalize_promotion_state(change.get("promotion_state")),
        "review_required": bool(change.get("review_required", candidate.get("review_required", True))),
        "candidate_pool_behavior": change.get("candidate_pool_behavior") or candidate.get("candidate_pool_behavior") or "unknown",
        "evidence_refs": evidence_refs(change, candidate, signal),
        "atlas_truth_changed": False,
    }


def candidate_item(change: dict[str, Any], candidate: dict[str, Any], signal: dict[str, Any], role: str) -> dict[str, Any]:
    return {
        "candidate_id": candidate.get("candidate_id") or change.get("change_id"),
        "target_ref": target_ref(change, candidate, signal),
        "role": role,
        "candidate_pool_behavior": candidate.get("candidate_pool_behavior") or change.get("candidate_pool_behavior") or "unknown",
        "confidence_delta": candidate.get("confidence_delta") if candidate.get("confidence_delta") is not None else change.get("confidence_delta", 0),
        "promotion_state": normalize_promotion_state(change.get("promotion_state")),
        "review_required": bool(candidate.get("review_required", True)),
        "scope": candidate.get("scope") or "mission_item_object_scope",
        "trigger_conditions": candidate.get("trigger_conditions") or ["future recurrence required before promotion"],
        "evidence_refs": evidence_refs(change, candidate, signal),
        "atlas_truth_changed": False,
    }


def confidence_change_item(change: dict[str, Any], candidate: dict[str, Any], signal: dict[str, Any]) -> dict[str, Any]:
    delta = float(change.get("confidence_delta") or candidate.get("confidence_delta") or 0.0)
    return {
        "target_ref": target_ref(change, candidate, signal),
        "prior_confidence": None,
        "updated_confidence": None,
        "delta": delta,
        "direction": "up" if delta > 0 else "down" if delta < 0 else "flat",
        "confidence_basis": "mission_signal_pattern",
        "review_required": bool(change.get("review_required", candidate.get("review_required", True))),
        "evidence_refs": evidence_refs(change, candidate, signal),
    }


def paused_path_item(change: dict[str, Any], candidate: dict[str, Any], signal: dict[str, Any]) -> dict[str, Any]:
    target = target_ref(change, candidate, signal)
    return {
        "path_id": f"paused_path:{slug(target['label'])}",
        "target_ref": target,
        "reason": "Mission evidence was skipped, flat, negative, or signal-only; keep route paused until review or recurrence.",
        "resume_conditions": ["additional positive mission evidence", "human review", "narrower object-scope test"],
        "evidence_refs": evidence_refs(change, candidate, signal),
    }


def scope_change_item(change: dict[str, Any], candidate: dict[str, Any], signal: dict[str, Any]) -> dict[str, Any]:
    return {
        "target_ref": target_ref(change, candidate, signal),
        "prior_scope": None,
        "updated_scope": candidate.get("scope") or "mission_item_object_scope",
        "scope_change_type": "narrowed_or_held",
        "reason": "Mission evidence should stay object-scoped until review confirms broader meaning.",
        "evidence_refs": evidence_refs(change, candidate, signal),
    }


def target_ref(change: dict[str, Any], candidate: dict[str, Any], signal: dict[str, Any]) -> dict[str, Any]:
    label = change.get("target_label") or candidate.get("target_label") or signal.get("subject_music_object_ref", {}).get("title") or "unknown"
    return {
        "target_id": slug(label),
        "label": label,
        "target_type": signal.get("subject_music_object_ref", {}).get("object_type") or "candidate",
        "source_candidate_id": candidate.get("candidate_id"),
    }


def evidence_refs(change: dict[str, Any], candidate: dict[str, Any], signal: dict[str, Any]) -> list[dict[str, str]]:
    ids = change.get("evidence_signal_ids") or candidate.get("evidence_signal_ids") or ([signal["signal_id"]] if signal.get("signal_id") else [])
    return evidence_ref_list(ids)


def evidence_ref_list(ids: list[str]) -> list[dict[str, str]]:
    return [{"signal_id": item, "ref_type": "signal"} for item in ids]


def next_mission_implications(
    updated_digest: dict[str, Any],
    frontiers: list[dict[str, Any]],
    dead_ends: list[dict[str, Any]],
    waypoints: list[dict[str, Any]],
    unresolved: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    implications = []
    if frontiers:
        implications.append(
            {
                "implication_type": "frontier_probe",
                "recommendation": "Use strengthened Frontier candidates as controlled probes in the next route.",
                "target_refs": [item["target_ref"] for item in frontiers[:4]],
                "risk_level": "medium",
                "evidence_refs": flatten_refs(item["evidence_refs"] for item in frontiers[:4]),
            }
        )
    if waypoints:
        implications.append(
            {
                "implication_type": "waypoint_bridge",
                "recommendation": "Use confirmed Waypoints as bridges or calibration controls.",
                "target_refs": [item["target_ref"] for item in waypoints[:4]],
                "risk_level": "low",
                "evidence_refs": flatten_refs(item["evidence_refs"] for item in waypoints[:4]),
            }
        )
    if dead_ends:
        implications.append(
            {
                "implication_type": "dead_end_check",
                "recommendation": "Keep Dead End hypotheses scoped and avoid broad exclusion until review.",
                "target_refs": [item["target_ref"] for item in dead_ends[:4]],
                "risk_level": "medium",
                "evidence_refs": flatten_refs(item["evidence_refs"] for item in dead_ends[:4]),
            }
        )
    if unresolved:
        implications.append(
            {
                "implication_type": "unresolved_question",
                "recommendation": "Use unresolved questions as next-route diagnostics.",
                "target_refs": [],
                "risk_level": "medium",
                "evidence_refs": [],
            }
        )
    return implications


def learned_bullets(profile_id: str, update_records: dict[str, Any], frontiers: list[dict[str, Any]], dead_ends: list[dict[str, Any]], waypoints: list[dict[str, Any]]) -> list[str]:
    summary = update_records.get("summary", {})
    return [
        f"{profile_id}: {summary.get('signals_created', 0)} mission Signals produced {summary.get('possible_update_candidates_created', 0)} PossibleAtlasUpdateCandidates.",
        f"{profile_id}: {len(frontiers)} Frontier candidates strengthened, {len(waypoints)} Waypoints were confirmed or reinforced, and {len(dead_ends)} Dead End hypotheses need review.",
        f"{profile_id}: No promoted Atlas truth or canonical graph mutation occurred.",
    ]


def normalize_role(value: str | None) -> str:
    if not value:
        return "unknown"
    key = value.strip().lower().replace(" ", "_")
    mapping = {
        "frontier": "frontier",
        "waypoint": "waypoint",
        "dead_end": "dead_end",
        "landmark": "landmark",
        "region": "region",
        "signal_only": "signal_only",
    }
    return mapping.get(key, key if key in mapping.values() else "unknown")


def normalize_promotion_state(value: str | None) -> str:
    return value if value in {"proposed", "candidate", "blocked", "demoted"} else "candidate"


def dedupe_by_target(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen = set()
    out = []
    for item in items:
        key = item.get("target_ref", {}).get("label")
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out


def dedupe_by_key(items: list[dict[str, Any]], key_name: str) -> list[dict[str, Any]]:
    seen = set()
    out = []
    for item in items:
        key = item.get(key_name)
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out


def flatten_refs(ref_groups: Any) -> list[dict[str, str]]:
    out = []
    for refs in ref_groups:
        out.extend(refs)
    return out


def first(values: list[Any] | None) -> Any:
    return values[0] if values else None


def slug(value: Any) -> str:
    text = str(value).strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = text.strip("_")
    return text or "unknown"


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(REPO_ROOT))


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
