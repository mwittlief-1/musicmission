from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


SCHEMA_VERSION = "0.1"
DEFAULT_USER_ID = "user_matt_atlas_harness"


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")


def slug(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._:-]+", "_", value.strip().lower())
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    return cleaned or "unknown"


def confidence(score: float, basis: str, summary: str) -> Dict[str, Any]:
    return {
        "confidence_score": round(score, 3),
        "confidence_band": confidence_band(score),
        "confidence_basis": basis,
        "confidence_summary": summary,
    }


def confidence_band(score: float) -> str:
    if score >= 0.75:
        return "high"
    if score >= 0.45:
        return "medium"
    return "low"


def lifecycle(status: str, review_state: str, promotion_state: str) -> Dict[str, str]:
    return {
        "status": status,
        "review_state": review_state,
        "promotion_state": promotion_state,
    }


def scope_global() -> Dict[str, Optional[str]]:
    return {
        "scope_type": "global",
        "scope_id": None,
        "scope_label": None,
    }


def clone_music_ref(refs: Dict[str, Any], key: str) -> Dict[str, Any]:
    if key not in refs:
        raise KeyError(f"Unknown music object ref key: {key}")
    return copy.deepcopy(refs[key])


def make_bundle(example_name: str, description: str, records: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "record_type": "atlas_example_bundle",
        "schema_version": SCHEMA_VERSION,
        "example_name": example_name,
        "description": description,
        "records": records,
    }


def make_signal(
    *,
    signal_id: str,
    user_id: str,
    source: str,
    event_type: str,
    occurred_at: str,
    captured_at: str,
    subject_music_object_ref: Dict[str, Any],
    subject_atlas_node_id: Optional[str],
    reaction_value: Any,
    observed_user_tags: List[str],
    user_note: Optional[str],
    signal_strength: float,
    interpretation_confidence: float,
    confidence_basis: str,
    confidence_summary: str,
    derived_update_candidate_ids: Optional[List[str]] = None,
    review_state: str = "unreviewed",
) -> Dict[str, Any]:
    return {
        "record_type": "signal",
        "schema_version": SCHEMA_VERSION,
        "signal_id": signal_id,
        "user_id": user_id,
        "source": source,
        "event_type": event_type,
        "occurred_at": occurred_at,
        "captured_at": captured_at,
        "subject_music_object_ref": subject_music_object_ref,
        "subject_atlas_node_id": subject_atlas_node_id,
        "reaction_value": reaction_value,
        "observed_user_tags": observed_user_tags,
        "user_note": user_note,
        "signal_strength": round(signal_strength, 3),
        "interpretation_confidence": round(interpretation_confidence, 3),
        "confidence": confidence(interpretation_confidence, confidence_basis, confidence_summary),
        "derived_update_candidate_ids": derived_update_candidate_ids or [],
        "lifecycle": lifecycle("active", review_state, "proposed"),
    }


def make_atlas_node(
    *,
    atlas_node_id: str,
    user_id: str,
    node_type: str,
    display_name: str,
    subtitle: Optional[str],
    music_object_ref: Optional[Dict[str, Any]],
    origin: str,
    render_summary: str,
    evidence_signal_ids: List[str],
    confidence_score: float,
    confidence_basis: str,
    confidence_summary: str,
    created_at: str,
    review_state: str = "unreviewed",
) -> Dict[str, Any]:
    return {
        "record_type": "atlas_node",
        "schema_version": SCHEMA_VERSION,
        "atlas_node_id": atlas_node_id,
        "user_id": user_id,
        "node_type": node_type,
        "display_name": display_name,
        "subtitle": subtitle,
        "music_object_ref": music_object_ref,
        "origin": origin,
        "render_hints": {
            "primary_label": display_name,
            "secondary_label": subtitle or "",
            "card_summary": render_summary,
        },
        "lifecycle": lifecycle("provisional", review_state, "candidate"),
        "confidence": confidence(confidence_score, confidence_basis, confidence_summary),
        "evidence_signal_ids": evidence_signal_ids,
        "created_at": created_at,
        "updated_at": created_at,
    }


def make_role_assignment(
    *,
    role_assignment_id: str,
    user_id: str,
    atlas_node_id: str,
    role: str,
    candidate_pool_behavior: str,
    assignment_summary: str,
    evidence_signal_ids: List[str],
    confidence_score: float,
    confidence_basis: str,
    confidence_summary: str,
    created_at: str,
    review_state: str = "needs_review",
) -> Dict[str, Any]:
    return {
        "record_type": "atlas_role_assignment",
        "schema_version": SCHEMA_VERSION,
        "atlas_role_assignment_id": role_assignment_id,
        "user_id": user_id,
        "atlas_node_id": atlas_node_id,
        "role": role,
        "scope": scope_global(),
        "candidate_pool_behavior": candidate_pool_behavior,
        "assignment_summary": assignment_summary,
        "lifecycle": lifecycle("provisional", review_state, "candidate"),
        "confidence": confidence(confidence_score, confidence_basis, confidence_summary),
        "evidence_signal_ids": evidence_signal_ids,
        "created_at": created_at,
        "updated_at": created_at,
    }


def make_update_candidate(
    *,
    update_candidate_id: str,
    user_id: str,
    source: str,
    source_signal_ids: List[str],
    target_atlas_node_id: Optional[str],
    target_role_assignment_id: Optional[str],
    proposed_record_type: str,
    proposed_action: str,
    proposed_payload: Dict[str, Any],
    confidence_delta: Optional[float],
    required_count: int,
    min_distinct_sources: int,
    review_required: bool,
    review_reason: str,
    generated_hypothesis_only: bool,
    created_at: str,
) -> Dict[str, Any]:
    return {
        "record_type": "possible_atlas_update_candidate",
        "schema_version": SCHEMA_VERSION,
        "update_candidate_id": update_candidate_id,
        "user_id": user_id,
        "source": source,
        "source_signal_ids": source_signal_ids,
        "target_atlas_node_id": target_atlas_node_id,
        "target_role_assignment_id": target_role_assignment_id,
        "proposed_record_type": proposed_record_type,
        "proposed_action": proposed_action,
        "proposed_payload": proposed_payload,
        "confidence_delta": None if confidence_delta is None else round(confidence_delta, 3),
        "recurrence_requirement": {
            "required_count": required_count,
            "min_distinct_sources": min_distinct_sources,
            "satisfied": False,
        },
        "review_requirement": {
            "required": review_required,
            "reviewer_type": "human" if review_required else "none",
            "reason": review_reason,
        },
        "canonical_graph_mutation_allowed": False,
        "generated_hypothesis_only": generated_hypothesis_only,
        "lifecycle": lifecycle("provisional", "needs_review" if review_required else "unreviewed", "candidate"),
        "created_at": created_at,
        "updated_at": created_at,
    }


def make_vocabulary_term(
    *,
    term_id: str,
    user_id: str,
    term: str,
    normalized_term: str,
    term_type: str,
    source_signal_ids: List[str],
    created_at: str,
    mapped_taste_feature_id: Optional[str] = None,
) -> Dict[str, Any]:
    summary = f"Survey note exposed reusable Waymark user language: {term!r}."
    if mapped_taste_feature_id:
        summary += f" Candidate mapping: {mapped_taste_feature_id}."
    return {
        "record_type": "user_vocabulary_term",
        "schema_version": SCHEMA_VERSION,
        "term_id": term_id,
        "user_id": user_id,
        "term": term,
        "normalized_term": normalized_term,
        "term_type": term_type,
        "source_signal_ids": source_signal_ids,
        "lifecycle": lifecycle("provisional", "unreviewed", "candidate"),
        "confidence": confidence(0.68, "explicit_user_note", summary),
        "created_at": created_at,
        "updated_at": created_at,
    }


def make_user_taste_feature_state(
    *,
    state_id: str,
    user_id: str,
    taste_feature_id: str,
    affinity: str,
    intensity_score: float,
    representative_refs: List[Dict[str, Any]],
    linked_atlas_node_ids: List[str],
    user_vocabulary_term_ids: List[str],
    evidence_signal_ids: List[str],
    created_at: str,
    summary: str,
) -> Dict[str, Any]:
    return {
        "record_type": "user_taste_feature_state",
        "schema_version": SCHEMA_VERSION,
        "user_taste_feature_state_id": state_id,
        "user_id": user_id,
        "taste_feature_id": taste_feature_id,
        "state": "provisional",
        "affinity": affinity,
        "intensity_score": round(intensity_score, 3),
        "representative_music_object_refs": representative_refs,
        "linked_atlas_node_ids": linked_atlas_node_ids,
        "user_vocabulary_term_ids": user_vocabulary_term_ids,
        "lifecycle": lifecycle("provisional", "needs_review", "candidate"),
        "confidence": confidence(intensity_score, "explicit_user_note", summary),
        "evidence_signal_ids": evidence_signal_ids,
        "created_at": created_at,
        "updated_at": created_at,
    }


def records_by_type(records: Iterable[Dict[str, Any]], record_type: str) -> List[Dict[str, Any]]:
    return [record for record in records if record.get("record_type") == record_type]


def dedupe_records(records: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    id_fields = [
        "signal_id",
        "atlas_node_id",
        "atlas_role_assignment_id",
        "update_candidate_id",
        "term_id",
        "user_taste_feature_state_id",
        "digest_id",
    ]
    seen = set()
    result: List[Dict[str, Any]] = []
    for record in records:
        key = None
        for field in id_fields:
            if field in record:
                key = (record.get("record_type"), record[field])
                break
        if key is None:
            key = (record.get("record_type"), json.dumps(record, sort_keys=True))
        if key in seen:
            continue
        seen.add(key)
        result.append(record)
    return result
