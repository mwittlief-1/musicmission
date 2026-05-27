from __future__ import annotations

from typing import Any, Dict, List

from .atlas_utils import (
    clone_music_ref,
    make_atlas_node,
    make_signal,
    make_update_candidate,
    slug,
)


def ingest_mission_review_fixture(fixture: Dict[str, Any], refs: Dict[str, Any]) -> List[Dict[str, Any]]:
    user_id = fixture["user_id"]
    ref = clone_music_ref(refs, fixture["subject_ref_key"])
    node_id = fixture["atlas_node_id"]
    event_id = fixture["review_event_id"]
    signal_id = f"signal:{slug(event_id)}"
    update_candidate_id = f"update_candidate:{slug(fixture['fixture_id'])}"
    update = fixture["proposed_update"]
    fixture_reaction = fixture.get("primary_reaction_operation") or "skip"
    reaction_value = _schema_reaction_value(fixture_reaction)
    signal_strength, interpretation_confidence, summary = _mission_review_confidence(fixture)
    records: List[Dict[str, Any]] = []

    records.append(
        make_signal(
            signal_id=signal_id,
            user_id=user_id,
            source="review",
            event_type="skip" if fixture_reaction == "skip" else "review_decision",
            occurred_at=fixture["occurred_at"],
            captured_at=fixture["captured_at"],
            subject_music_object_ref=ref,
            subject_atlas_node_id=node_id,
            reaction_value=reaction_value,
            observed_user_tags=fixture.get("selected_chip_labels", []),
            user_note=fixture.get("user_note"),
            signal_strength=signal_strength,
            interpretation_confidence=interpretation_confidence,
            confidence_basis="mission_review",
            confidence_summary=summary,
            derived_update_candidate_ids=[update_candidate_id],
            review_state="needs_review" if reaction_value == "skip" else "reviewed",
        )
    )

    records.append(
        make_atlas_node(
            atlas_node_id=node_id,
            user_id=user_id,
            node_type=fixture["node_type"],
            display_name=ref["display_name"],
            subtitle=f"Mission Review evidence: {fixture_reaction}",
            music_object_ref=ref,
            origin="review",
            render_summary="Mission Review-created provisional node used only to attach auditable evidence and possible updates.",
            evidence_signal_ids=[signal_id],
            confidence_score=interpretation_confidence,
            confidence_basis="mission_review",
            confidence_summary="Mission Review evidence can guide an update candidate but does not auto-promote Atlas truth.",
            created_at=fixture["captured_at"],
            review_state="needs_review",
        )
    )

    proposed_payload = {
        "atlas_node_id": node_id,
        "role": update["role"],
        "scope": {
            "scope_type": "global",
            "scope_id": None,
            "scope_label": None,
        },
        "candidate_pool_behavior": update["candidate_pool_behavior"],
        "mission_id": fixture["mission_id"],
        "primary_reaction_operation": fixture.get("primary_reaction_operation"),
        "selected_chip_labels": fixture.get("selected_chip_labels", []),
        "linked_taste_feature_ids": fixture.get("taste_feature_ids", []),
        "review_created_possible_update_only": True,
    }
    for optional_key in [
        "exception_semantics",
        "do_not_erase_dead_end",
        "do_not_promote_broad_lane",
        "do_not_promote_to_landmark",
    ]:
        if optional_key in update:
            proposed_payload[optional_key] = update[optional_key]

    records.append(
        make_update_candidate(
            update_candidate_id=update_candidate_id,
            user_id=user_id,
            source="mission_review",
            source_signal_ids=[signal_id],
            target_atlas_node_id=node_id,
            target_role_assignment_id=None,
            proposed_record_type="atlas_role_assignment" if update["proposed_action"] != "resolution_request" else "atlas_node",
            proposed_action=update["proposed_action"],
            proposed_payload=proposed_payload,
            confidence_delta=update.get("confidence_delta"),
            required_count=update["recurrence_required_count"],
            min_distinct_sources=update["min_distinct_sources"],
            review_required=True,
            review_reason=_review_reason(fixture),
            generated_hypothesis_only=True,
            created_at=fixture["captured_at"],
        )
    )
    return records


def ingest_mission_review_fixtures(fixtures: List[Dict[str, Any]], refs: Dict[str, Any]) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    for fixture in fixtures:
        records.extend(ingest_mission_review_fixture(fixture, refs))
    return records


def _mission_review_confidence(fixture: Dict[str, Any]) -> tuple[float, float, str]:
    reaction = fixture.get("primary_reaction_operation") or "skip"
    completion_ratio = fixture.get("playback", {}).get("completion_ratio") or 0
    chip_count = len(fixture.get("selected_chip_labels", []))
    if reaction == "not_for_me":
        return 0.84, 0.78, "Explicit rejection plus chips strongly supports a possible Dead End update, still review-gated."
    if reaction == "like" and "trap" in fixture["fixture_id"]:
        return 0.66, 0.48, "Positive trap reaction is real but semantically narrow: exception/cultural furniture, not broad lane approval."
    if reaction == "like":
        return 0.74, 0.66, "Positive Mission Review reaction supports a Frontier candidate with recurrence requirements."
    if reaction == "keep":
        return 0.62, 0.58, "Keep plus chips supports Waypoint clarification, not Landmark promotion."
    if reaction == "skip":
        strength = 0.18 if completion_ratio < 0.25 else 0.28
        return strength, 0.16, "Skip is real playback behavior but weak interpretation without explicit reaction or recurrence."
    return 0.5 + min(chip_count, 2) * 0.05, 0.45, "Mission Review evidence retained as a cautious possible update."


def _schema_reaction_value(reaction: Any) -> Any:
    if reaction == "keep":
        return "neutral"
    return reaction


def _review_reason(fixture: Dict[str, Any]) -> str:
    if fixture.get("primary_reaction_operation") is None:
        return "Skipped item produces weak evidence; keep node unresolved and require review before any role movement."
    if "trap_unexpectedly_liked" in fixture["fixture_id"]:
        return "Positive trap response should create exception/reassess semantics, not erase a Dead End or promote a broad lane."
    return "Mission Review creates possible Atlas updates with recurrence and review requirements; it does not auto-promote."
