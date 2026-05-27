from __future__ import annotations

from typing import Any, Dict, List, Optional

from .atlas_utils import SCHEMA_VERSION, records_by_type


ROLE_TO_DIGEST_KEY = {
    "landmark": "landmarks",
    "region": "regions",
    "frontier": "frontiers",
    "dead_end": "dead_ends",
    "waypoint": "waypoints",
}


def build_atlas_digest_view(
    *,
    records: List[Dict[str, Any]],
    user_id: str,
    generated_at: str,
    mission_context: str = "mission_generation_and_candidate_pool_builder",
) -> tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    nodes = {record["atlas_node_id"]: record for record in records_by_type(records, "atlas_node")}
    role_assignments = records_by_type(records, "atlas_role_assignment")
    signals = records_by_type(records, "signal")
    updates = records_by_type(records, "possible_atlas_update_candidate")
    vocabulary_terms = records_by_type(records, "user_vocabulary_term")
    taste_feature_states = records_by_type(records, "user_taste_feature_state")

    role_ids = {key: [] for key in ["landmarks", "regions", "frontiers", "dead_ends", "waypoints"]}
    expanded_roles = {key: [] for key in ["landmarks", "regions", "frontiers", "dead_ends", "waypoints", "unknowns", "signal_only"]}

    for role_assignment in role_assignments:
        role = role_assignment["role"]
        key = ROLE_TO_DIGEST_KEY.get(role, f"{role}s")
        if key in role_ids:
            role_ids[key].append(role_assignment["atlas_role_assignment_id"])
        expanded_key = key if key in expanded_roles else role
        if expanded_key not in expanded_roles:
            expanded_roles[expanded_key] = []
        expanded_roles[expanded_key].append(_role_summary(role_assignment, nodes.get(role_assignment["atlas_node_id"])))

    update_summaries = [_update_summary(update, nodes.get(update.get("target_atlas_node_id"))) for update in updates]
    for summary in update_summaries:
        role = summary.get("proposed_role")
        key = ROLE_TO_DIGEST_KEY.get(role)
        if key:
            expanded_roles[key].append(summary)
        elif role == "unknown":
            expanded_roles["unknowns"].append(summary)

    suggested_candidate_roles = _suggested_candidate_roles(role_assignments, updates, nodes)
    digest_record = {
        "record_type": "atlas_digest_view",
        "schema_version": SCHEMA_VERSION,
        "digest_id": "atlas_digest_view:synthetic_v0_1",
        "user_id": user_id,
        "generated_at": generated_at,
        "mission_context": mission_context,
        "relevant_role_assignment_ids": role_ids,
        "user_taste_feature_state_ids": [record["user_taste_feature_state_id"] for record in taste_feature_states],
        "user_vocabulary_term_ids": [record["term_id"] for record in vocabulary_terms],
        "anti_overfitting_rules": _anti_overfitting_rules(),
        "recent_signal_ids": [signal["signal_id"] for signal in signals[-12:]],
        "unresolved_questions": _unresolved_questions(expanded_roles, updates),
        "mission_relevant_constraints": _mission_relevant_constraints(),
        "suggested_candidate_roles": [
            {
                "music_object_ref": item["music_object_ref"],
                "suggested_role": item["suggested_role"],
                "reason": item["reason"],
            }
            for item in suggested_candidate_roles
            if item.get("music_object_ref")
        ],
    }

    expanded_digest = {
        "schema_version": "waymark.atlas_digest_view.expanded.v0.1",
        "record_type": "atlas_digest_view_expanded",
        "digest_id": "atlas_digest_view_expanded:synthetic_v0_1",
        "contract_digest_id": digest_record["digest_id"],
        "atlas_digest_view_contract_record": digest_record,
        "user_id": user_id,
        "generated_at": generated_at,
        "mission_context": mission_context,
        "core_taste_summary": (
            "Synthetic Atlas state shows strong provisional evidence for body-first, hook-pressure guitar anchors; "
            "useful waypoint evidence for QOTSA-style shelves; caution around fake-hard, post-grunge, and adult-alt lanes; "
            "and unresolved current-rock frontier questions that require candidate-constrained testing."
        ),
        "landmarks": expanded_roles["landmarks"],
        "strong_regions": expanded_roles["regions"],
        "regions": expanded_roles["regions"],
        "promising_frontiers": expanded_roles["frontiers"],
        "frontiers": expanded_roles["frontiers"],
        "known_dead_ends": expanded_roles["dead_ends"],
        "dead_ends": expanded_roles["dead_ends"],
        "useful_waypoints": expanded_roles["waypoints"],
        "waypoints": expanded_roles["waypoints"],
        "unknowns": expanded_roles["unknowns"],
        "signal_only": expanded_roles["signal_only"],
        "possible_atlas_update_candidates": update_summaries,
        "taste_feature_states": [_taste_feature_state_summary(record) for record in taste_feature_states],
        "user_vocabulary_terms": [_vocabulary_summary(record) for record in vocabulary_terms],
        "recent_signals": [_signal_summary(signal) for signal in signals[-12:]],
        "anti_overfitting_rules": digest_record["anti_overfitting_rules"],
        "unresolved_questions": digest_record["unresolved_questions"],
        "mission_relevant_constraints": digest_record["mission_relevant_constraints"],
        "candidate_pool_behavior_summaries": _candidate_pool_behavior_summaries(role_assignments, updates, nodes),
        "suggested_candidate_roles": suggested_candidate_roles,
        "read_surfaces": {
            "mission_generation": "Use expanded summaries for landmarks/frontiers/dead ends/waypoints, vocabulary, and anti-overfitting constraints.",
            "candidate_pool_builder": "Use candidate_pool_behavior_summaries and suggested_candidate_roles; do not read role truth from AtlasNode.",
        },
    }
    mission_generation_digest = build_mission_generation_digest_view(expanded_digest)
    return digest_record, expanded_digest, mission_generation_digest


def build_mission_generation_digest_view(expanded_digest: Dict[str, Any]) -> Dict[str, Any]:
    """Compact read model for mission generation.

    The expanded digest is useful for inspection and candidate-builder debugging, but it exposes
    update candidate records that a generation model can accidentally copy. This mission-facing
    view keeps role/candidate behavior cues while omitting copyable Atlas update IDs and direct
    update payloads.
    """
    return {
        "schema_version": "waymark.mission_generation_digest_view.v0.1",
        "record_type": "mission_generation_digest_view",
        "digest_id": "mission_generation_digest_view:synthetic_v0_1",
        "source_digest_id": expanded_digest["digest_id"],
        "user_id": expanded_digest["user_id"],
        "generated_at": expanded_digest["generated_at"],
        "mission_context": "mission_generation",
        "core_taste_summary": expanded_digest["core_taste_summary"],
        "read_policy": {
            "purpose": "Mission Generation reads this compact adapter instead of raw Atlas records or expanded possible update records.",
            "role_truth_source": "AtlasRoleAssignment summaries and review-gated interpretation summaries only.",
            "possible_update_policy": (
                "Existing Atlas possible updates are summarized for caution only and are not exposed as copyable mission output. "
                "Generated mission output must create mission-scoped possible_atlas_update_candidates tied to selected route items."
            ),
            "canonical_graph_mutation_allowed": False,
        },
        "landmarks": [_mission_role_summary(item) for item in expanded_digest["landmarks"]],
        "regions": [_mission_role_summary(item) for item in expanded_digest["regions"]],
        "strong_regions": [_mission_role_summary(item) for item in expanded_digest["strong_regions"]],
        "frontiers": [_mission_role_summary(item) for item in expanded_digest["frontiers"]],
        "promising_frontiers": [_mission_role_summary(item) for item in expanded_digest["promising_frontiers"]],
        "dead_ends": [_mission_role_summary(item) for item in expanded_digest["dead_ends"]],
        "known_dead_ends": [_mission_role_summary(item) for item in expanded_digest["known_dead_ends"]],
        "waypoints": [_mission_role_summary(item) for item in expanded_digest["waypoints"]],
        "useful_waypoints": [_mission_role_summary(item) for item in expanded_digest["useful_waypoints"]],
        "unknowns": [_mission_role_summary(item) for item in expanded_digest["unknowns"]],
        "taste_feature_states": [_mission_taste_feature_summary(item) for item in expanded_digest["taste_feature_states"]],
        "user_vocabulary_terms": [_mission_vocabulary_summary(item) for item in expanded_digest["user_vocabulary_terms"]],
        "anti_overfitting_rules": expanded_digest["anti_overfitting_rules"],
        "unresolved_questions": expanded_digest["unresolved_questions"],
        "recent_signal_summaries": [_mission_signal_summary(item) for item in expanded_digest["recent_signals"]],
        "candidate_pool_behavior": [
            _mission_candidate_behavior_summary(item)
            for item in expanded_digest["candidate_pool_behavior_summaries"]
        ],
        "suggested_candidate_roles": [
            _mission_suggested_candidate_role(item)
            for item in expanded_digest["suggested_candidate_roles"]
        ],
        "review_gated_interpretation_summary": _review_gated_interpretation_summary(expanded_digest),
    }


def _mission_role_summary(item: Dict[str, Any]) -> Dict[str, Any]:
    music_ref = item.get("music_object_ref") or {}
    summary = {
        "name": item.get("name"),
        "role": item.get("role") or item.get("proposed_role"),
        "scope": item.get("scope"),
        "candidate_pool_behavior": item.get("candidate_pool_behavior"),
        "confidence_band": item.get("confidence_band") or _confidence_band_from_delta(item.get("confidence_delta")),
        "evidence_summary": item.get("evidence_summary") or _review_gated_evidence_summary(item),
        "linked_taste_feature_ids": item.get("linked_taste_feature_ids", []),
        "failure_or_edge_conditions": item.get("failure_or_edge_conditions", []),
        "review_state": item.get("review_state"),
        "promotion_state": item.get("promotion_state"),
    }
    if music_ref:
        summary["music_object_ref"] = _compact_music_object_ref(music_ref)
    if item.get("recurrence_requirement"):
        summary["recurrence_requirement"] = item["recurrence_requirement"]
    if item.get("review_requirement"):
        summary["review_required"] = bool((item.get("review_requirement") or {}).get("required"))
    return summary


def _mission_taste_feature_summary(item: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "taste_feature_id": item["taste_feature_id"],
        "state": item["state"],
        "affinity": item["affinity"],
        "intensity_score": item["intensity_score"],
        "confidence_band": item["confidence_band"],
        "vocabulary_term_count": len(item.get("user_vocabulary_term_ids", [])),
        "evidence_count": len(item.get("evidence_signal_ids", [])),
    }


def _mission_vocabulary_summary(item: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "term": item["term"],
        "normalized_term": item["normalized_term"],
        "term_type": item["term_type"],
        "status": item["status"],
        "usable_in_chips": item["usable_in_chips"],
    }


def _mission_signal_summary(item: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "source": item["source"],
        "event_type": item["event_type"],
        "reaction_value": item["reaction_value"],
        "subject_display_name": item["subject_display_name"],
        "observed_user_tags": item["observed_user_tags"],
        "user_note": item["user_note"],
        "signal_strength": item["signal_strength"],
        "interpretation_confidence": item["interpretation_confidence"],
        "confidence_band": item["confidence_band"],
    }


def _mission_candidate_behavior_summary(item: Dict[str, Any]) -> Dict[str, Any]:
    summary = {
        "name": item.get("name"),
        "role": item.get("role"),
        "candidate_pool_behavior": item.get("candidate_pool_behavior"),
        "confidence_band": item.get("confidence_band"),
        "source_record_type": item.get("source_record_type"),
        "evidence_count": len(item.get("evidence_signal_ids", [])),
    }
    music_ref = item.get("music_object_ref") or {}
    if music_ref:
        summary["music_object_ref"] = _compact_music_object_ref(music_ref)
    if item.get("review_required") is not None:
        summary["review_required"] = bool(item.get("review_required"))
    return summary


def _mission_suggested_candidate_role(item: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "music_object_ref": _compact_music_object_ref(item["music_object_ref"]),
        "suggested_role": item.get("suggested_role"),
        "candidate_pool_behavior": item.get("candidate_pool_behavior"),
        "confidence_band": item.get("confidence_band"),
        "reason": item.get("reason"),
        "review_required": bool(item.get("review_required")) if item.get("review_required") is not None else None,
    }


def _review_gated_interpretation_summary(expanded_digest: Dict[str, Any]) -> List[Dict[str, Any]]:
    summaries = []
    for item in expanded_digest.get("possible_atlas_update_candidates", []):
        summaries.append(
            {
                "name": item.get("name"),
                "possible_role": item.get("proposed_role"),
                "candidate_pool_behavior": item.get("candidate_pool_behavior"),
                "confidence_band": _confidence_band_from_delta(item.get("confidence_delta")),
                "review_required": bool((item.get("review_requirement") or {}).get("required")),
                "recurrence_required_count": (item.get("recurrence_requirement") or {}).get("required_count"),
                "evidence_count": len(item.get("evidence_signal_ids", [])),
                "generated_hypothesis_only": bool(item.get("generated_hypothesis_only")),
                "caution": "; ".join(item.get("failure_or_edge_conditions", [])),
                "music_object_ref": _compact_music_object_ref(item["music_object_ref"]) if item.get("music_object_ref") else None,
            }
        )
    return summaries


def _compact_music_object_ref(music_ref: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "object_type": music_ref.get("object_type"),
        "display_name": music_ref.get("display_name"),
        "credited_artist_name": music_ref.get("credited_artist_name"),
        "resolution_state": music_ref.get("resolution_state"),
        "canonical_artist_id": music_ref.get("canonical_artist_id"),
        "canonical_album_id": music_ref.get("canonical_album_id"),
        "canonical_song_recording_id": music_ref.get("canonical_song_recording_id"),
        "composition_placeholder_id": music_ref.get("composition_placeholder_id"),
    }


def _confidence_band_from_delta(delta: Any) -> str:
    try:
        value = float(delta)
    except (TypeError, ValueError):
        return "candidate"
    if value >= 0.25:
        return "medium"
    if value >= 0.12:
        return "low_to_medium"
    return "low"


def _review_gated_evidence_summary(item: Dict[str, Any]) -> str:
    role = item.get("proposed_role") or item.get("role") or "signal"
    behavior = item.get("candidate_pool_behavior") or "unknown"
    return f"Review-gated possible {role}; use as candidate_pool_behavior={behavior} cue, not promoted truth."


def _role_summary(role_assignment: Dict[str, Any], node: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    music_ref = node.get("music_object_ref") if node else None
    name = node.get("display_name") if node else role_assignment["atlas_node_id"]
    return {
        "role_assignment_id": role_assignment["atlas_role_assignment_id"],
        "atlas_node_id": role_assignment["atlas_node_id"],
        "name": name,
        "role": role_assignment["role"],
        "scope": role_assignment["scope"],
        "candidate_pool_behavior": role_assignment["candidate_pool_behavior"],
        "confidence_score": role_assignment["confidence"]["confidence_score"],
        "confidence_band": role_assignment["confidence"]["confidence_band"],
        "confidence_basis": role_assignment["confidence"]["confidence_basis"],
        "evidence_signal_ids": role_assignment["evidence_signal_ids"],
        "evidence_summary": role_assignment.get("assignment_summary", role_assignment["confidence"]["confidence_summary"]),
        "linked_taste_feature_ids": [],
        "failure_or_edge_conditions": _edge_conditions_for_role(role_assignment["role"], name),
        "music_object_ref": music_ref,
        "review_state": role_assignment["lifecycle"]["review_state"],
        "promotion_state": role_assignment["lifecycle"]["promotion_state"],
    }


def _update_summary(update: Dict[str, Any], node: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    payload = update.get("proposed_payload", {})
    role = payload.get("role")
    name = node.get("display_name") if node else update.get("target_atlas_node_id")
    return {
        "update_candidate_id": update["update_candidate_id"],
        "atlas_node_id": update.get("target_atlas_node_id"),
        "name": name,
        "proposed_role": role,
        "role": role,
        "candidate_pool_behavior": payload.get("candidate_pool_behavior"),
        "proposed_action": update["proposed_action"],
        "confidence_delta": update["confidence_delta"],
        "recurrence_requirement": update["recurrence_requirement"],
        "review_requirement": update["review_requirement"],
        "canonical_graph_mutation_allowed": update["canonical_graph_mutation_allowed"],
        "generated_hypothesis_only": update["generated_hypothesis_only"],
        "evidence_signal_ids": update["source_signal_ids"],
        "linked_taste_feature_ids": payload.get("linked_taste_feature_ids", []),
        "failure_or_edge_conditions": _update_edge_conditions(update),
        "music_object_ref": node.get("music_object_ref") if node else None,
        "scope": payload.get("scope"),
        "promotion_state": update["lifecycle"]["promotion_state"],
        "review_state": update["lifecycle"]["review_state"],
    }


def _taste_feature_state_summary(record: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "user_taste_feature_state_id": record["user_taste_feature_state_id"],
        "taste_feature_id": record["taste_feature_id"],
        "state": record["state"],
        "affinity": record["affinity"],
        "intensity_score": record["intensity_score"],
        "confidence_band": record["confidence"]["confidence_band"],
        "evidence_signal_ids": record["evidence_signal_ids"],
        "user_vocabulary_term_ids": record["user_vocabulary_term_ids"],
    }


def _vocabulary_summary(record: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "term_id": record["term_id"],
        "term": record["term"],
        "normalized_term": record["normalized_term"],
        "term_type": record["term_type"],
        "status": record["lifecycle"]["status"],
        "promotion_state": record["lifecycle"]["promotion_state"],
        "review_state": record["lifecycle"]["review_state"],
        "source_signal_ids": record["source_signal_ids"],
        "usable_in_chips": record["lifecycle"]["promotion_state"] in {"candidate", "promoted"},
    }


def _signal_summary(signal: Dict[str, Any]) -> Dict[str, Any]:
    ref = signal.get("subject_music_object_ref") or {}
    return {
        "signal_id": signal["signal_id"],
        "source": signal["source"],
        "event_type": signal["event_type"],
        "reaction_value": signal["reaction_value"],
        "subject_atlas_node_id": signal["subject_atlas_node_id"],
        "subject_display_name": ref.get("display_name"),
        "observed_user_tags": signal["observed_user_tags"],
        "user_note": signal["user_note"],
        "signal_strength": signal["signal_strength"],
        "interpretation_confidence": signal["interpretation_confidence"],
        "confidence_band": signal["confidence"]["confidence_band"],
    }


def _candidate_pool_behavior_summaries(
    role_assignments: List[Dict[str, Any]],
    updates: List[Dict[str, Any]],
    nodes: Dict[str, Dict[str, Any]],
) -> List[Dict[str, Any]]:
    summaries = []
    for role_assignment in role_assignments:
        node = nodes.get(role_assignment["atlas_node_id"], {})
        summaries.append(
            {
                "source_record_id": role_assignment["atlas_role_assignment_id"],
                "source_record_type": "atlas_role_assignment",
                "name": node.get("display_name", role_assignment["atlas_node_id"]),
                "role": role_assignment["role"],
                "candidate_pool_behavior": role_assignment["candidate_pool_behavior"],
                "confidence_band": role_assignment["confidence"]["confidence_band"],
                "evidence_signal_ids": role_assignment["evidence_signal_ids"],
                "music_object_ref": node.get("music_object_ref"),
            }
        )
    for update in updates:
        payload = update.get("proposed_payload", {})
        behavior = payload.get("candidate_pool_behavior")
        if not behavior:
            continue
        node = nodes.get(update.get("target_atlas_node_id"), {})
        summaries.append(
            {
                "source_record_id": update["update_candidate_id"],
                "source_record_type": "possible_atlas_update_candidate",
                "name": node.get("display_name", update.get("target_atlas_node_id")),
                "role": payload.get("role"),
                "candidate_pool_behavior": behavior,
                "confidence_band": "candidate",
                "evidence_signal_ids": update["source_signal_ids"],
                "music_object_ref": node.get("music_object_ref"),
                "review_required": update["review_requirement"]["required"],
            }
        )
    return summaries


def _suggested_candidate_roles(
    role_assignments: List[Dict[str, Any]],
    updates: List[Dict[str, Any]],
    nodes: Dict[str, Dict[str, Any]],
) -> List[Dict[str, Any]]:
    suggestions = []
    for role_assignment in role_assignments:
        node = nodes.get(role_assignment["atlas_node_id"])
        if not node or not node.get("music_object_ref"):
            continue
        suggestions.append(
            {
                "source_record_id": role_assignment["atlas_role_assignment_id"],
                "music_object_ref": node["music_object_ref"],
                "suggested_role": role_assignment["role"],
                "candidate_pool_behavior": role_assignment["candidate_pool_behavior"],
                "confidence_band": role_assignment["confidence"]["confidence_band"],
                "reason": role_assignment.get("assignment_summary", role_assignment["confidence"]["confidence_summary"]),
                "evidence_signal_ids": role_assignment["evidence_signal_ids"],
            }
        )
    for update in updates:
        payload = update.get("proposed_payload", {})
        node = nodes.get(update.get("target_atlas_node_id"))
        if not node or not node.get("music_object_ref") or not payload.get("role"):
            continue
        suggestions.append(
            {
                "source_record_id": update["update_candidate_id"],
                "music_object_ref": node["music_object_ref"],
                "suggested_role": payload["role"],
                "candidate_pool_behavior": payload.get("candidate_pool_behavior"),
                "confidence_band": "candidate",
                "reason": _suggestion_reason(update, node),
                "evidence_signal_ids": update["source_signal_ids"],
                "review_required": update["review_requirement"]["required"],
            }
        )
    return suggestions


def _suggestion_reason(update: Dict[str, Any], node: Dict[str, Any]) -> str:
    payload = update.get("proposed_payload", {})
    behavior = payload.get("candidate_pool_behavior", "unknown")
    role = payload.get("role", "unknown")
    return (
        f"{node['display_name']} is a review-gated possible {role} with candidate_pool_behavior={behavior}; "
        "use as a candidate-pool cue, not promoted Atlas truth."
    )


def _edge_conditions_for_role(role: str, name: str) -> List[str]:
    if role == "landmark":
        return [f"{name} anchors only the evidenced feature lane; do not infer broad genre approval."]
    if role == "waypoint":
        return [f"{name} is useful route material, not core canon."]
    if role == "dead_end":
        return [f"{name} may still contain one-object exceptions; positive trap response should trigger reassessment, not erasure."]
    if role == "frontier":
        return [f"{name} needs recurrence before Region or Landmark claims."]
    if role == "unknown":
        return [f"{name} should be probed only when the mission explicitly needs uncertainty."]
    return ["Use only within the evidenced scope."]


def _update_edge_conditions(update: Dict[str, Any]) -> List[str]:
    payload = update.get("proposed_payload", {})
    role = payload.get("role")
    if payload.get("do_not_erase_dead_end"):
        return ["Unexpected trap positive means exception/cultural furniture/reassess dead end; do not erase the Dead End automatically."]
    if payload.get("do_not_promote_to_landmark"):
        return ["Waypoint clarification explicitly blocks Landmark promotion without stronger recurrence."]
    if role == "frontier":
        return ["Frontier candidate requires recurrence before promotion."]
    if role == "dead_end":
        return ["Dead End strengthening remains review-gated and scope-bounded."]
    if role == "unknown":
        return ["Skip/unknown evidence cannot become a role verdict."]
    return ["Possible update remains conditional on future reactions and review."]


def _anti_overfitting_rules() -> List[str]:
    return [
        "Survey and Mission Review create evidence, not final verdicts.",
        "Do not promote Waypoints into Landmarks without recurrence and review.",
        "Do not turn one-object exceptions into broad lane approval.",
        "Positive trap response means unexpected exception, cultural furniture, or reassess-dead-end candidate.",
        "Mission Generation must preserve uncertainty and write possible updates only.",
        "Candidate Pool Builder reads candidate_pool_behavior, not AtlasNode display fields.",
        "Signal strength and interpretation confidence must remain separate.",
    ]


def _mission_relevant_constraints() -> List[str]:
    return [
        "Use provisional Landmarks as anchors only with visible evidence summaries.",
        "Use dead-end candidates as explicit boundary tests, not recommendations.",
        "Use unknown/frontier items as probes with review-needed defaults.",
        "Do not mutate canonical graph objects from Atlas ingestion or Mission Review.",
    ]


def _unresolved_questions(expanded_roles: Dict[str, List[Dict[str, Any]]], updates: List[Dict[str, Any]]) -> List[str]:
    questions = [
        "Does the provisional Nirvana Landmark seed survive repeated playback and mission review?",
        "Are QOTSA-style items useful waypoints only, or do any become stronger anchors later?",
        "Can current rock probes show body and pulse without fake-hard scene posture?",
    ]
    if any((update.get("proposed_payload") or {}).get("role") == "dead_end" for update in updates):
        questions.append("Which Dead End scopes are broad lane exclusions versus narrow trap items?")
    if expanded_roles.get("unknowns"):
        questions.append("Which unknown objects should be resolved before use in mission routes?")
    return questions
