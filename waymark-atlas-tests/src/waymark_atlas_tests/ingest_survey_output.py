from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from .atlas_utils import (
    clone_music_ref,
    make_atlas_node,
    make_role_assignment,
    make_signal,
    make_update_candidate,
    make_user_taste_feature_state,
    make_vocabulary_term,
    slug,
)


MUSIC_NODE_TYPES = {"artist", "album", "song_recording", "composition_placeholder"}


def ingest_survey_fixture(fixture: Dict[str, Any], refs: Dict[str, Any]) -> List[Dict[str, Any]]:
    user_id = fixture["user_id"]
    node_id = fixture["atlas_node_id"]
    ref = clone_music_ref(refs, fixture["subject_ref_key"])
    node_ref = ref if fixture["node_type"] in MUSIC_NODE_TYPES else None
    signal_id = f"signal:{slug(fixture['survey_event_id'])}"
    update_candidate_id = f"update_candidate:{slug(fixture['fixture_id'])}"
    policy = fixture["seed_policy"]
    reaction = fixture["reaction_value"]
    event_type = _event_type_for_reaction(reaction)
    signal_strength, interpretation_confidence, basis, confidence_summary = _survey_signal_confidence(reaction, fixture)

    records: List[Dict[str, Any]] = []
    signal = make_signal(
        signal_id=signal_id,
        user_id=user_id,
        source="survey",
        event_type=event_type,
        occurred_at=fixture["occurred_at"],
        captured_at=fixture["captured_at"],
        subject_music_object_ref=node_ref,
        subject_atlas_node_id=node_id,
        reaction_value=_schema_reaction_value(reaction),
        observed_user_tags=fixture.get("selected_tags", []),
        user_note=fixture.get("user_note"),
        signal_strength=signal_strength,
        interpretation_confidence=interpretation_confidence,
        confidence_basis=basis,
        confidence_summary=confidence_summary,
        derived_update_candidate_ids=[update_candidate_id] if policy["proposed_role"] != "signal_only" else [],
        review_state="unreviewed",
    )
    records.append(signal)

    records.append(
        make_atlas_node(
            atlas_node_id=node_id,
            user_id=user_id,
            node_type=fixture["node_type"],
            display_name=ref["display_name"],
            subtitle=f"Survey seed: {reaction}",
            music_object_ref=node_ref,
            origin="survey",
            render_summary="Survey-created provisional Atlas object. It preserves evidence without final role truth.",
            evidence_signal_ids=[signal_id],
            confidence_score=interpretation_confidence,
            confidence_basis=basis,
            confidence_summary="Node exists so survey evidence remains auditable and resolvable.",
            created_at=fixture["captured_at"],
            review_state="needs_review" if policy.get("review_required") else "unreviewed",
        )
    )

    if policy.get("allow_provisional_role_assignment"):
        role = policy["proposed_role"]
        records.append(
            make_role_assignment(
                role_assignment_id=f"role:{slug(fixture['fixture_id'])}:{role}",
                user_id=user_id,
                atlas_node_id=node_id,
                role=role,
                candidate_pool_behavior=policy["candidate_pool_behavior"],
                assignment_summary=_survey_assignment_summary(role, policy["candidate_pool_behavior"]),
                evidence_signal_ids=[signal_id],
                confidence_score=min(0.74, interpretation_confidence),
                confidence_basis=basis,
                confidence_summary="Survey-created role assignment is provisional and must not be treated as final Atlas truth.",
                created_at=fixture["captured_at"],
                review_state="needs_review" if policy.get("review_required") else "unreviewed",
            )
        )

    if policy["proposed_role"] != "signal_only":
        records.append(
            make_update_candidate(
                update_candidate_id=update_candidate_id,
                user_id=user_id,
                source="survey",
                source_signal_ids=[signal_id],
                target_atlas_node_id=node_id,
                target_role_assignment_id=None,
                proposed_record_type="atlas_role_assignment",
                proposed_action="create",
                proposed_payload={
                    "atlas_node_id": node_id,
                    "role": policy["proposed_role"],
                    "scope": {
                        "scope_type": "global",
                        "scope_id": None,
                        "scope_label": None,
                    },
                    "candidate_pool_behavior": policy["candidate_pool_behavior"],
                    "survey_seed_only": True,
                    "allow_promoted_role_assignment": False,
                    "linked_taste_feature_ids": fixture.get("taste_feature_ids", []),
                },
                confidence_delta=_survey_confidence_delta(reaction),
                required_count=policy["recurrence_required_count"],
                min_distinct_sources=1,
                review_required=bool(policy.get("review_required")),
                review_reason="Survey creates seed evidence and candidates; role truth needs recurrence or review before promotion.",
                generated_hypothesis_only=False,
                created_at=fixture["captured_at"],
            )
        )

    vocabulary_terms = []
    for candidate in fixture.get("vocabulary_candidates", []):
        term_id = f"term:{candidate['normalized_term']}"
        vocabulary_terms.append(term_id)
        records.append(
            make_vocabulary_term(
                term_id=term_id,
                user_id=user_id,
                term=candidate["term"],
                normalized_term=candidate["normalized_term"],
                term_type=candidate["term_type"],
                source_signal_ids=[signal_id],
                created_at=fixture["captured_at"],
                mapped_taste_feature_id=candidate.get("mapped_taste_feature_id"),
            )
        )

    if vocabulary_terms:
        for candidate in fixture.get("vocabulary_candidates", []):
            feature_id = candidate.get("mapped_taste_feature_id")
            if not feature_id:
                continue
            affinity = "avoids" if candidate["term_type"] == "avoidance_label" else "seeks"
            records.append(
                make_user_taste_feature_state(
                    state_id=f"user_taste_feature_state:{slug(user_id)}:{slug(feature_id)}",
                    user_id=user_id,
                    taste_feature_id=feature_id,
                    affinity=affinity,
                    intensity_score=0.67,
                    representative_refs=[ref],
                    linked_atlas_node_ids=[node_id],
                    user_vocabulary_term_ids=[f"term:{candidate['normalized_term']}"],
                    evidence_signal_ids=[signal_id],
                    created_at=fixture["captured_at"],
                    summary="User note introduced a reusable feature phrase. Keep candidate-level until recurrence or review.",
                )
            )

    return records


def ingest_survey_fixtures(fixtures: List[Dict[str, Any]], refs: Dict[str, Any]) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    for fixture in fixtures:
        records.extend(ingest_survey_fixture(fixture, refs))
    return records


def _event_type_for_reaction(reaction: Any) -> str:
    if reaction == "dont_know":
        return "familiarity"
    if reaction == "note":
        return "note"
    return "reaction"


def _schema_reaction_value(reaction: Any) -> Any:
    if reaction == "favorite":
        return "love"
    if reaction == "note":
        return None
    return reaction


def _survey_signal_confidence(reaction: Any, fixture: Dict[str, Any]) -> tuple[float, float, str, str]:
    if reaction == "favorite":
        return 0.9, 0.72, "direct_user_reaction", "A highest-positive survey mark is strong evidence, but still survey seed state."
    if reaction == "like":
        return 0.66, 0.55, "direct_user_reaction", "A like/useful survey mark supports a candidate role, not a Landmark."
    if reaction == "not_for_me":
        return 0.76, 0.6, "direct_user_reaction", "A negative survey mark is meaningful but broad-scope dead ends require review."
    if reaction == "dont_know":
        return 0.2, 0.22, "survey_pattern", "Unknown familiarity is real survey state but not positive taste evidence."
    if reaction == "note":
        return 0.45, 0.78, "explicit_user_note", "A note can be interpretively strong even when it is one-off evidence."
    return 0.4, 0.35, "survey_pattern", f"Survey event {fixture['fixture_id']} is retained as low-confidence evidence."


def _survey_confidence_delta(reaction: Any) -> float:
    return {
        "favorite": 0.22,
        "like": 0.14,
        "not_for_me": 0.17,
        "dont_know": 0.04,
    }.get(reaction, 0.05)


def _survey_assignment_summary(role: str, candidate_pool_behavior: str) -> str:
    if role == "landmark":
        return "Candidate Landmark seed for anchoring routes; still provisional until recurrence or review."
    if role == "waypoint":
        return "Use as a useful route shelf or bridge, not as core canon."
    if role == "unknown":
        return "Preserve unknown state for candidate-pool caution; do not infer positive taste."
    return f"Survey-created provisional {role} assignment with {candidate_pool_behavior} candidate behavior."
