#!/usr/bin/env python3
"""Build MissionGenerationDigestView packets from Atlas ingestion outputs.

This intentionally consumes the Atlas substrate produced by Survey ingestion:
Signal ledger, provisional role assignments/update candidates through
AtlasDigestView summaries, and evidence refs. It does not read raw Survey
payloads or Profile Writer outputs.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_ROOT = REPO_ROOT / "data/atlas_schema/ingestion_proof/survey_evidence_export_v0_1"
DEFAULT_OUTPUT_ROOT = (
    REPO_ROOT
    / "data/mission_generation/mission_generation_digest_view_alpha_v0_1/generated_from_survey_evidence_export"
)
GENERATED_AT = "2026-05-23T12:00:00Z"
MAX_CANDIDATE_ROLES = 12
MAX_RECENT_SIGNALS = 12

NORMALIZED_SIGNAL_MAP = {
    "strong_positive": "positive_high",
    "positive": "positive_medium",
    "contextual_waypoint": "contextual_waypoint",
    "negative_scoped": "negative_scope_carefully",
    "familiarity_uncertainty": "familiarity_uncertainty",
    "skip": "skip_or_no_signal",
    "no_signal": "skip_or_no_signal",
}

MISSION_USE_BY_BEHAVIOR = {
    "anchor": "anchor",
    "bridge": "bridge",
    "probe": "probe",
    "risky_probe": "risky_probe",
    "waypoint": "waypoint_context",
    "trap": "trap_check",
    "exclude": "avoid_for_now",
    "unknown": "resolve_first",
}

BASE_PRIORITY_BY_BEHAVIOR = {
    "anchor": 0.9,
    "bridge": 0.78,
    "probe": 0.72,
    "risky_probe": 0.64,
    "waypoint": 0.58,
    "trap": 0.42,
    "exclude": 0.15,
    "unknown": 0.35,
}

DEFAULT_ANTI_OVERFITTING_RULES = [
    "Do not treat Survey-created roles as promoted Atlas truth.",
    "Do not broaden negative responses into genre-level dislikes without scoped recurrence.",
    "Treat dont_know_enough/familiarity_uncertainty as familiarity uncertainty, not negative evidence.",
    "Apple Music evidence is exposure/import/familiarity context, not taste truth.",
    "Do not infer family or archetype names when graph meanings are unavailable.",
    "Road and lineage are not Atlas roles.",
]

DEFAULT_MISSION_CONSTRAINTS = [
    "Consume MissionGenerationDigestView with route-ready Candidate Pool objects, not raw Survey payload.",
    "Mission Generation may return generated missions and PossibleAtlasUpdateCandidate hypotheses only.",
    "Atlas digest packets do not create playable mission objects or promoted Atlas truth.",
]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build compact MissionGenerationDigestView packets from Atlas ingestion proof outputs."
    )
    parser.add_argument("--input-root", type=Path, default=DEFAULT_INPUT_ROOT)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    args = parser.parse_args()

    input_root = args.input_root.resolve()
    output_root = args.output_root.resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    profile_dirs = [
        path
        for path in sorted(input_root.glob("public_profile_*"))
        if (path / "atlas_digest_view.json").exists() and (path / "signals.jsonl").exists()
    ]
    if not profile_dirs:
        raise SystemExit(f"No Atlas ingestion profile directories found under {rel(input_root)}")

    manifest_profiles = []
    for profile_dir in profile_dirs:
        digest, report = build_profile_digest(profile_dir)
        output_path = output_root / f"mission_generation_digest_view_{profile_dir.name}.json"
        write_json(output_path, digest)
        manifest_profiles.append(
            {
                "profile_dir": rel(profile_dir),
                "output_file": rel(output_path),
                **report,
            }
        )

    manifest = {
        "record_type": "mission_generation_digest_view_generation_manifest",
        "schema_version": "alpha_v0_1",
        "generated_at": GENERATED_AT,
        "input_root": rel(input_root),
        "output_root": rel(output_root),
        "raw_survey_payload_read": False,
        "profile_writer_output_read": False,
        "profile_count": len(manifest_profiles),
        "profiles": manifest_profiles,
        "blockers": [
            {
                "issue_id": "ATL-I001",
                "summary": "Fixed Alpha 1 A4_Al2_S4 Survey Evidence Export fixture is not yet available.",
                "owner_lane": "Survey Simulator",
            }
        ],
    }
    write_json(output_root / "manifest.json", manifest)
    write_text(output_root / "README.md", render_report(manifest_profiles))
    print(f"Wrote {len(manifest_profiles)} MissionGenerationDigestView packet(s) to {rel(output_root)}")
    return 0


def build_profile_digest(profile_dir: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    atlas_digest = load_json(profile_dir / "atlas_digest_view.json")
    signals = load_jsonl(profile_dir / "signals.jsonl")
    signal_by_id = {signal["signal_id"]: signal for signal in signals}
    first_signal = signals[0]
    first_source = first_signal["source_context"]

    profile_label = profile_dir.name
    subject_id = atlas_digest.get("user_id") or profile_label
    user_id = None if str(subject_id).startswith("fixture_") else subject_id
    fixture_profile_id = subject_id if str(subject_id).startswith("fixture_") else None

    full_evidence_ref_index = [make_evidence_ref_index_item(signal) for signal in signals[:120]]
    evidence_ref_by_signal_id = {
        item["signal_id"]: item["evidence_ref"]
        for item in full_evidence_ref_index
        if item.get("signal_id") and item.get("evidence_ref")
    }

    candidate_roles = [
        make_candidate_role_summary(index, hint, signal_by_id, evidence_ref_by_signal_id)
        for index, hint in enumerate(select_candidate_hints(atlas_digest), start=1)
    ]
    candidate_signal_ids = []
    for role in candidate_roles:
        candidate_signal_ids.extend(role["evidence"]["signal_ids"])

    recent_signal_ids = select_recent_signal_ids(
        signals=signals,
        atlas_digest=atlas_digest,
        candidate_signal_ids=candidate_signal_ids,
        limit=MAX_RECENT_SIGNALS,
    )
    recent_signals = [make_recent_signal_summary(signal_by_id[signal_id]) for signal_id in recent_signal_ids]

    contradictions = [
        make_contradiction_summary(index, contradiction, evidence_ref_by_signal_id)
        for index, contradiction in enumerate(atlas_digest.get("contradictions") or [], start=1)
    ][:12]
    unresolved_questions = make_unresolved_questions(
        atlas_digest.get("unresolved_questions") or [],
        contradictions,
        signals,
        profile_label,
    )

    vocabulary_terms = make_vocabulary_terms(signals)
    taste_features = make_taste_feature_summaries(atlas_digest, evidence_ref_by_signal_id)
    evidence_ref_index = filter_evidence_ref_index(
        full_evidence_ref_index,
        candidate_roles=candidate_roles,
        recent_signals=recent_signals,
        contradictions=contradictions,
        unresolved_questions=unresolved_questions,
        vocabulary_terms=vocabulary_terms,
        taste_features=taste_features,
    )

    digest = {
        "record_type": "mission_generation_digest_view",
        "schema_version": "alpha_v0_1",
        "digest_id": f"mgdv:alpha:survey_completion:{slug(profile_label)}",
        "created_at": GENERATED_AT,
        "user_id": user_id,
        "fixture_profile_id": fixture_profile_id,
        "source_context": {
            "source_event_type": "survey_completion",
            "source_event_id": f"survey_completion:{slug(profile_label)}",
            "survey_session_id": first_source["source_session_id"],
            "source_payload_ref": first_source.get("source_export_id") or first_source["source_file_ref"],
            "source_payload_version": "survey_evidence_export_v0_1",
            "visible_packet_id": first_source["visible_packet_id"],
            "input_fingerprint": first_source.get("source_input_fingerprint"),
            "atlas_digest_ref": atlas_digest.get("digest_id"),
            "generated_from": [
                "survey_evidence_export",
                "signal_ledger",
                "atlas_role_assignments",
                "possible_atlas_update_candidates",
            ],
        },
        "compactness_policy": {
            "target_max_bytes": 50000,
            "hard_review_threshold_bytes": 80000,
            "max_candidate_roles": MAX_CANDIDATE_ROLES,
            "max_recent_signals": MAX_RECENT_SIGNALS,
            "max_evidence_refs_per_item": 8,
            "raw_payload_required": False,
        },
        "evidence_separation_policy": {
            "atlas_node_role_truth_allowed": False,
            "role_truth_source": "atlas_role_assignment",
            "survey_role_promotion_allowed": False,
            "promoted_roles_allowed": False,
            "canonical_graph_mutation_allowed": False,
            "apple_exposure_as_taste_truth_allowed": False,
            "dont_know_as_negative_allowed": False,
            "signal_strength_and_confidence_separate": True,
        },
        "no_hidden_data_checks": {
            "raw_survey_payload_included": False,
            "survey_construction_internals_included": False,
            "page_layout_mechanics_included": False,
            "randomization_seed_included": False,
            "generator_visible_inputs_included": False,
            "raw_ranking_scores_included": False,
            "profile_writer_output_included": False,
            "hidden_simulator_truth_included": False,
            "hidden_corpus_reactions_included": False,
            "simulator_private_lookup_status_included": False,
            "canonical_graph_mutation_instructions_included": False,
            "all_evidence_refs_resolve_to_visible_survey_evidence": evidence_refs_resolve(
                candidate_roles, recent_signals, contradictions, unresolved_questions, evidence_ref_index
            ),
        },
        "evidence_ref_index": evidence_ref_index,
        "candidate_roles": candidate_roles,
        "recent_signals": recent_signals,
        "contradictions": contradictions,
        "unresolved_questions": unresolved_questions,
        "taste_feature_summaries": taste_features,
        "user_vocabulary_terms": vocabulary_terms,
        "anti_overfitting_rules": make_rule_objects(
            atlas_digest.get("anti_overfitting_rules") or DEFAULT_ANTI_OVERFITTING_RULES,
            prefix=f"anti_overfitting:{slug(profile_label)}",
            severity="warning",
        ),
        "mission_relevant_constraints": make_rule_objects(
            merge_unique(DEFAULT_MISSION_CONSTRAINTS, atlas_digest.get("mission_relevant_constraints") or []),
            prefix=f"mission_constraint:{slug(profile_label)}",
            severity="info",
        ),
        "consumer_contract": {
            "intended_consumer": "mission_generation",
            "raw_survey_payload_required": False,
            "mission_objects_created_here": False,
            "atlas_promotion_allowed": False,
            "canonical_graph_mutation_allowed": False,
            "profile_writer_mode_allowed": False,
            "final_wwtsf_copy_allowed": False,
        },
    }

    output_bytes = len(json.dumps(digest, ensure_ascii=True, separators=(",", ":")).encode("utf-8"))
    source_export_path = REPO_ROOT / first_source["source_file_ref"]
    atlas_digest_bytes = (profile_dir / "atlas_digest_view.json").stat().st_size
    source_export_bytes = source_export_path.stat().st_size if source_export_path.exists() else None
    report = {
        "profile_label": profile_label,
        "candidate_roles": len(candidate_roles),
        "recent_signals": len(recent_signals),
        "evidence_refs": len(evidence_ref_index),
        "contradictions": len(contradictions),
        "unresolved_questions": len(unresolved_questions),
        "user_vocabulary_terms": len(vocabulary_terms),
        "source_survey_evidence_export_bytes": source_export_bytes,
        "atlas_digest_view_bytes": atlas_digest_bytes,
        "mission_generation_digest_view_bytes": output_bytes,
        "reduction_vs_survey_evidence_export": reduction(source_export_bytes, output_bytes),
        "reduction_vs_atlas_digest_view": reduction(atlas_digest_bytes, output_bytes),
    }
    return digest, report


def make_evidence_ref_index_item(signal: dict[str, Any]) -> dict[str, Any]:
    source = signal["source_context"]
    page = signal.get("page_context") or {}
    return {
        "evidence_ref": source["evidence_ref"],
        "signal_id": signal["signal_id"],
        "response_id": source["response_id"],
        "survey_item_id": source.get("survey_item_id"),
        "survey_session_id": source["source_session_id"],
        "page_id": page.get("page_id") or "survey_page_unknown",
        "stage": page.get("stage") or "survey",
        "page_number": page.get("page_number"),
        "visible_packet_id": source["visible_packet_id"],
        "source_payload_ref": source.get("source_file_ref") or source.get("source_export_id"),
    }


def select_candidate_hints(atlas_digest: dict[str, Any]) -> list[dict[str, Any]]:
    hints = atlas_digest.get("candidate_pool_behavior_hints") or []
    if len(hints) <= MAX_CANDIDATE_ROLES:
        return hints

    quota_by_role = {
        "landmark": 3,
        "frontier": 3,
        "dead_end": 3,
        "waypoint": 3,
        "region": 1,
        "unknown": 1,
        "signal_only": 1,
    }
    selected: list[dict[str, Any]] = []
    selected_keys: set[str] = set()

    def add_hint(hint: dict[str, Any]) -> None:
        key = hint.get("atlas_role_assignment_id") or hint.get("atlas_node_id") or json.dumps(hint, sort_keys=True)
        if key not in selected_keys and len(selected) < MAX_CANDIDATE_ROLES:
            selected.append(hint)
            selected_keys.add(key)

    for role, quota in quota_by_role.items():
        role_hints = [hint for hint in hints if hint.get("role") == role]
        role_hints.sort(
            key=lambda hint: (
                hint.get("confidence", {}).get("confidence_score", 0),
                len(hint.get("evidence_signal_ids") or []),
            ),
            reverse=True,
        )
        for hint in role_hints[:quota]:
            add_hint(hint)

    remaining = sorted(
        hints,
        key=lambda hint: (
            hint.get("confidence", {}).get("confidence_score", 0),
            len(hint.get("evidence_signal_ids") or []),
        ),
        reverse=True,
    )
    for hint in remaining:
        add_hint(hint)
    return selected


def make_candidate_role_summary(
    index: int,
    hint: dict[str, Any],
    signal_by_id: dict[str, dict[str, Any]],
    evidence_ref_by_signal_id: dict[str, str],
) -> dict[str, Any]:
    signal_ids = [sid for sid in hint.get("evidence_signal_ids", []) if sid in signal_by_id][:8]
    evidence_refs = [evidence_ref_by_signal_id[sid] for sid in signal_ids if sid in evidence_ref_by_signal_id][:8]
    positive_refs, negative_refs, uncertainty_refs = split_evidence_refs_by_signal(signal_ids, signal_by_id)
    behavior = hint.get("candidate_pool_behavior") or "unknown"
    role = hint.get("role") or "unknown"
    music_ref = slim_music_object_ref(hint.get("music_object_ref") or {})
    confidence = normalize_confidence(hint.get("confidence") or {})
    return {
        "candidate_role_id": f"candidate_role:{slug(hint.get('atlas_role_assignment_id') or str(index))}",
        "atlas_node_id": hint.get("atlas_node_id") or f"atlas_node:unknown:{index}",
        "atlas_role_assignment_id": hint.get("atlas_role_assignment_id") or f"role:unknown:{index}",
        "role_truth_source": "atlas_role_assignment",
        "display_name": short_text(hint.get("name") or music_ref["display_name"] or "Unknown object"),
        "object_scope": music_ref["object_type"],
        "music_object_ref": music_ref,
        "recommended_role": role if role in role_values() else "unknown",
        "candidate_pool_behavior": behavior if behavior in MISSION_USE_BY_BEHAVIOR else "unknown",
        "status": hint.get("status") if hint.get("status") in {"active", "provisional"} else "provisional",
        "review_state": hint.get("review_state")
        if hint.get("review_state") in {"unreviewed", "needs_review", "reviewed", "rejected"}
        else "needs_review",
        "promotion_state": hint.get("promotion_state")
        if hint.get("promotion_state") in {"proposed", "candidate", "blocked"}
        else "blocked",
        "confidence": confidence,
        "evidence": {
            "signal_ids": signal_ids,
            "evidence_refs": evidence_refs,
            "positive_evidence_refs": positive_refs[:8],
            "negative_evidence_refs": negative_refs[:8],
            "uncertainty_evidence_refs": uncertainty_refs[:8],
        },
        "scope_limit": scope_limit_for(music_ref),
        "mission_use": MISSION_USE_BY_BEHAVIOR.get(behavior, "resolve_first"),
        "mission_generation_priority": mission_priority(behavior, role, confidence["confidence_score"]),
        "summary": short_text(hint.get("summary") or "Provisional Atlas role candidate from Survey evidence."),
    }


def make_recent_signal_summary(signal: dict[str, Any]) -> dict[str, Any]:
    source = signal["source_context"]
    music_ref = signal["subject_music_object_ref"]
    apple = signal.get("apple_exposure_context") or {}
    apple_refs = (apple.get("apple_evidence_refs") or [])[:8]
    return {
        "signal_id": signal["signal_id"],
        "source": "survey",
        "evidence_ref": source["evidence_ref"],
        "response_id": source["response_id"],
        "display_name": short_text(music_ref.get("display_name") or "Unknown object"),
        "object_type": music_ref.get("object_type") or "artist",
        "raw_reaction": short_text(signal.get("raw_reaction") or signal.get("reaction_value") or "unknown", 80),
        "normalized_signal": NORMALIZED_SIGNAL_MAP.get(signal.get("normalized_signal"), "skip_or_no_signal"),
        "signal_strength": clamp(signal.get("signal_strength"), 0, 1),
        "interpretation_confidence": clamp(signal.get("interpretation_confidence"), 0, 1),
        "selected_tags": clean_tags(signal.get("observed_user_tags") or []),
        "shown_unselected_tags": clean_tags(signal.get("shown_unselected_tags") or []),
        "note_excerpt": short_nullable(signal.get("user_note"), 240),
        "apple_exposure_context": {
            "present": bool(apple_refs or nonzero_apple_summary(apple.get("apple_evidence_summary") or {})),
            "taste_truth": False,
            "summary": "Apple Music context present as exposure/familiarity only; not taste truth."
            if apple_refs or nonzero_apple_summary(apple.get("apple_evidence_summary") or {})
            else "No Apple Music exposure context supplied for this item.",
            "evidence_refs": apple_refs,
        },
    }


def make_contradiction_summary(
    index: int, contradiction: dict[str, Any], evidence_ref_by_signal_id: dict[str, str]
) -> dict[str, Any]:
    positive_refs = [
        evidence_ref_by_signal_id[sid]
        for sid in contradiction.get("positive_signal_ids", [])
        if sid in evidence_ref_by_signal_id
    ][:8]
    negative_refs = [
        evidence_ref_by_signal_id[sid]
        for sid in contradiction.get("negative_signal_ids", [])
        if sid in evidence_ref_by_signal_id
    ][:8]
    return {
        "contradiction_id": contradiction.get("cluster_id") or f"contradiction:{index:02d}",
        "label": short_text(contradiction.get("label") or f"Contradiction {index}"),
        "scope_warning": short_text(
            contradiction.get("scope_warning")
            or "Mixed visible evidence requires scoped testing before broader interpretation."
        ),
        "positive_evidence_refs": positive_refs,
        "negative_evidence_refs": negative_refs,
        "uncertainty_evidence_refs": [],
        "recommended_test": "Use a scoped mission probe before broadening this interpretation.",
        "review_required": True,
    }


def make_unresolved_questions(
    questions: list[Any],
    contradictions: list[dict[str, Any]],
    signals: list[dict[str, Any]],
    profile_label: str,
) -> list[dict[str, Any]]:
    unresolved: list[dict[str, Any]] = []
    uncertainty_refs = [
        signal["source_context"]["evidence_ref"]
        for signal in signals
        if signal.get("normalized_signal") == "familiarity_uncertainty"
    ][:8]
    contradiction_refs = []
    for contradiction in contradictions:
        contradiction_refs.extend(contradiction["positive_evidence_refs"])
        contradiction_refs.extend(contradiction["negative_evidence_refs"])
    contradiction_refs = contradiction_refs[:8]

    for index, question in enumerate(questions[:16], start=1):
        text = str(question)
        qtype = question_type_for(text)
        if qtype == "familiarity":
            evidence_refs = uncertainty_refs
            mission_hint = "Use recognition or low-risk exposure checks before interpreting taste."
        elif qtype == "contradiction":
            evidence_refs = contradiction_refs
            mission_hint = "Use a scoped contrast mission to test which object level is reliable."
        else:
            evidence_refs = []
            mission_hint = "Use a narrow mission probe and preserve scope limits."
        unresolved.append(
            {
                "question_id": f"unresolved_question:{slug(profile_label)}:{index:02d}",
                "question_type": qtype,
                "question": short_text(text),
                "evidence_refs": evidence_refs[:8],
                "mission_hint": short_text(mission_hint),
                "review_required": True,
            }
        )
    return unresolved


def make_taste_feature_summaries(
    atlas_digest: dict[str, Any], evidence_ref_by_signal_id: dict[str, str]
) -> list[dict[str, Any]]:
    summaries = []
    for index, feature in enumerate(atlas_digest.get("user_taste_feature_summaries") or [], start=1):
        signal_ids = feature.get("evidence_signal_ids") or []
        evidence_refs = [evidence_ref_by_signal_id[sid] for sid in signal_ids if sid in evidence_ref_by_signal_id][:8]
        summaries.append(
            {
                "taste_feature_id": feature.get("taste_feature_id") or f"taste_feature:{index:02d}",
                "label": short_text(feature.get("label") or f"Taste feature {index}"),
                "state": feature.get("state") if feature.get("state") in {"candidate_affinity", "candidate_aversion", "mixed", "unknown"} else "unknown",
                "confidence": normalize_confidence(feature.get("confidence") or {}),
                "evidence_refs": evidence_refs,
                "mission_use": short_text(feature.get("mission_use") or "Use only as provisional context."),
            }
        )
    return summaries[:12]


def make_vocabulary_terms(signals: list[dict[str, Any]]) -> list[dict[str, Any]]:
    terms: dict[tuple[str, str], dict[str, Any]] = {}
    for signal in signals:
        evidence_ref = signal["source_context"]["evidence_ref"]
        for tag in clean_tags(signal.get("observed_user_tags") or []):
            key = ("selected_tag", tag.lower())
            terms.setdefault(
                key,
                {
                    "term_id": f"vocab:selected_tag:{slug(tag)}",
                    "term": tag,
                    "source": "selected_tag",
                    "evidence_refs": [],
                    "use_in_mission_copy": True,
                },
            )
            terms[key]["evidence_refs"] = merge_unique(terms[key]["evidence_refs"], [evidence_ref])[:8]
        note = signal.get("user_note")
        if isinstance(note, str) and note.strip():
            term = short_text(note.strip(), 80)
            key = ("user_note", term.lower())
            terms.setdefault(
                key,
                {
                    "term_id": f"vocab:user_note:{slug(term)}",
                    "term": term,
                    "source": "user_note",
                    "evidence_refs": [],
                    "use_in_mission_copy": False,
                },
            )
            terms[key]["evidence_refs"] = merge_unique(terms[key]["evidence_refs"], [evidence_ref])[:8]
    return list(terms.values())[:24]


def select_recent_signal_ids(
    signals: list[dict[str, Any]],
    atlas_digest: dict[str, Any],
    candidate_signal_ids: list[str],
    limit: int,
) -> list[str]:
    selected: list[str] = []
    available = {signal["signal_id"] for signal in signals}
    for signal_id in candidate_signal_ids:
        if signal_id in available:
            selected.append(signal_id)
    for contradiction in atlas_digest.get("contradictions") or []:
        for signal_id in (contradiction.get("positive_signal_ids") or []) + (contradiction.get("negative_signal_ids") or []):
            if signal_id in available:
                selected.append(signal_id)
    for summary in atlas_digest.get("recent_signals") or []:
        signal_id = summary.get("signal_id")
        if signal_id in available:
            selected.append(signal_id)
    for signal in signals:
        selected.append(signal["signal_id"])
    return merge_unique([], selected)[:limit]


def split_evidence_refs_by_signal(
    signal_ids: list[str], signal_by_id: dict[str, dict[str, Any]]
) -> tuple[list[str], list[str], list[str]]:
    positive: list[str] = []
    negative: list[str] = []
    uncertainty: list[str] = []
    for signal_id in signal_ids:
        signal = signal_by_id[signal_id]
        evidence_ref = signal["source_context"]["evidence_ref"]
        normalized = signal.get("normalized_signal")
        raw = signal.get("raw_reaction")
        if normalized in {"strong_positive", "positive"} or raw in {"love", "like"}:
            positive.append(evidence_ref)
        elif normalized == "negative_scoped" or raw == "dont_like":
            negative.append(evidence_ref)
        elif normalized == "familiarity_uncertainty" or raw == "dont_know_enough":
            uncertainty.append(evidence_ref)
    return positive, negative, uncertainty


def slim_music_object_ref(ref: dict[str, Any]) -> dict[str, Any]:
    object_type = ref.get("object_type") if ref.get("object_type") in {"artist", "album", "song_recording", "composition_placeholder"} else "artist"
    ref_source = ref.get("ref_source") if ref.get("ref_source") in {"canonical_graph", "user_local", "external_catalog", "unresolved"} else "unresolved"
    resolution_state = ref.get("resolution_state") if ref.get("resolution_state") in {"resolved", "needs_resolution", "intentionally_user_local"} else "needs_resolution"
    if ref_source == "unresolved":
        resolution_state = "needs_resolution"
    slim = {
        "object_type": object_type,
        "ref_source": ref_source,
        "display_name": short_text(ref.get("display_name") or "Unresolved music object"),
        "credited_artist_name": short_nullable(ref.get("credited_artist_name"), 220),
        "canonical_artist_id": ref.get("canonical_artist_id"),
        "canonical_album_id": ref.get("canonical_album_id"),
        "canonical_song_recording_id": ref.get("canonical_song_recording_id"),
        "composition_placeholder_id": ref.get("composition_placeholder_id"),
        "user_music_object_id": ref.get("user_music_object_id"),
        "external_catalog_refs": dict(list((ref.get("external_catalog_refs") or {}).items())[:6]),
        "resolution_state": resolution_state,
        "composition_policy_status": ref.get("composition_policy_status")
        if ref.get("composition_policy_status")
        in {
            "resolved",
            "needs_review",
            "not_applicable",
            "no_review_needed",
            "composition_first_required",
            "split_confirmed",
        }
        else "needs_review",
    }
    if object_type == "composition_placeholder" and not slim["composition_placeholder_id"]:
        slim["composition_placeholder_id"] = f"composition_placeholder:{slug(slim['display_name'])}"
    if ref_source == "canonical_graph":
        if object_type == "artist" and not slim["canonical_artist_id"]:
            slim["ref_source"] = "unresolved"
            slim["resolution_state"] = "needs_resolution"
        elif object_type == "album" and not slim["canonical_album_id"]:
            slim["ref_source"] = "unresolved"
            slim["resolution_state"] = "needs_resolution"
        elif object_type == "song_recording" and not slim["canonical_song_recording_id"]:
            slim["ref_source"] = "unresolved"
            slim["resolution_state"] = "needs_resolution"
    return slim


def normalize_confidence(confidence: dict[str, Any]) -> dict[str, Any]:
    basis = confidence.get("confidence_basis")
    allowed_basis = {
        "direct_user_reaction",
        "repeated_user_behavior",
        "explicit_user_note",
        "survey_pattern",
        "mission_review",
        "import_context",
        "editorial_seed",
        "generated_hypothesis",
        "mixed",
    }
    score = clamp(confidence.get("confidence_score"), 0, 1)
    return {
        "confidence_score": score,
        "confidence_band": confidence.get("confidence_band") if confidence.get("confidence_band") in {"low", "medium", "high"} else confidence_band(score),
        "confidence_basis": basis if basis in allowed_basis else "survey_pattern",
        "confidence_summary": short_text(
            confidence.get("confidence_summary")
            or "Survey substrate evidence is useful for mission generation but cannot promote Atlas truth."
        ),
    }


def make_rule_objects(rules: list[Any], prefix: str, severity: str) -> list[dict[str, Any]]:
    output = []
    for index, rule in enumerate(rules[:12], start=1):
        output.append(
            {
                "id": f"{prefix}:{index:02d}",
                "text": short_text(str(rule)),
                "severity": severity,
                "evidence_refs": [],
            }
        )
    return output


def filter_evidence_ref_index(
    full_index: list[dict[str, Any]],
    candidate_roles: list[dict[str, Any]],
    recent_signals: list[dict[str, Any]],
    contradictions: list[dict[str, Any]],
    unresolved_questions: list[dict[str, Any]],
    vocabulary_terms: list[dict[str, Any]],
    taste_features: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    refs: list[str] = []
    for role in candidate_roles:
        for key in ["evidence_refs", "positive_evidence_refs", "negative_evidence_refs", "uncertainty_evidence_refs"]:
            refs.extend(role["evidence"][key])
    refs.extend(signal["evidence_ref"] for signal in recent_signals)
    for contradiction in contradictions:
        refs.extend(contradiction["positive_evidence_refs"])
        refs.extend(contradiction["negative_evidence_refs"])
        refs.extend(contradiction["uncertainty_evidence_refs"])
    for question in unresolved_questions:
        refs.extend(question["evidence_refs"])
    for term in vocabulary_terms:
        refs.extend(term["evidence_refs"])
    for feature in taste_features:
        refs.extend(feature["evidence_refs"])

    wanted = set(merge_unique([], refs))
    filtered = [item for item in full_index if item["evidence_ref"] in wanted]
    return filtered or full_index[:1]


def evidence_refs_resolve(
    candidate_roles: list[dict[str, Any]],
    recent_signals: list[dict[str, Any]],
    contradictions: list[dict[str, Any]],
    unresolved_questions: list[dict[str, Any]],
    evidence_ref_index: list[dict[str, Any]],
) -> bool:
    valid_refs = {item["evidence_ref"] for item in evidence_ref_index}
    referenced: list[str] = []
    for role in candidate_roles:
        for key in ["evidence_refs", "positive_evidence_refs", "negative_evidence_refs", "uncertainty_evidence_refs"]:
            referenced.extend(role["evidence"][key])
    referenced.extend(signal["evidence_ref"] for signal in recent_signals)
    for contradiction in contradictions:
        referenced.extend(contradiction["positive_evidence_refs"])
        referenced.extend(contradiction["negative_evidence_refs"])
        referenced.extend(contradiction["uncertainty_evidence_refs"])
    for question in unresolved_questions:
        referenced.extend(question["evidence_refs"])
    return all(ref in valid_refs for ref in referenced)


def question_type_for(text: str) -> str:
    lowered = text.lower()
    if "familiarity" in lowered or "recognition" in lowered:
        return "familiarity"
    if "contradict" in lowered or "mixed" in lowered:
        return "contradiction"
    if "recurrence" in lowered or "repeat" in lowered:
        return "recurrence"
    if "resolution" in lowered or "unresolved" in lowered:
        return "resolution"
    if "tag" in lowered:
        return "tag_gap"
    return "scope"


def scope_limit_for(music_ref: dict[str, Any]) -> str:
    if music_ref["resolution_state"] == "needs_resolution":
        return "needs_resolution"
    return {
        "artist": "artist_level_only",
        "album": "album_level_only",
        "song_recording": "recording_level_only",
        "composition_placeholder": "needs_resolution",
    }.get(music_ref["object_type"], "unknown")


def mission_priority(behavior: str, role: str, confidence_score: float) -> float:
    value = BASE_PRIORITY_BY_BEHAVIOR.get(behavior, 0.35)
    if role == "landmark":
        value += 0.03
    elif role == "frontier":
        value += 0.02
    elif role == "dead_end":
        value -= 0.02
    elif role == "unknown":
        value -= 0.08
    value += (confidence_score - 0.5) * 0.2
    return round(clamp(value, 0, 1), 2)


def role_values() -> set[str]:
    return {"landmark", "region", "frontier", "dead_end", "waypoint", "unknown", "signal_only"}


def clean_tags(tags: list[Any]) -> list[str]:
    cleaned = []
    for tag in tags:
        if isinstance(tag, str) and tag.strip():
            cleaned.append(short_text(tag.strip(), 80))
    return cleaned[:12]


def short_text(value: Any, limit: int = 320) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    if not text:
        text = "Unspecified"
    return text[:limit]


def short_nullable(value: Any, limit: int) -> str | None:
    if value is None:
        return None
    text = re.sub(r"\s+", " ", str(value)).strip()
    return text[:limit] if text else None


def confidence_band(score: float) -> str:
    if score >= 0.74:
        return "high"
    if score >= 0.45:
        return "medium"
    return "low"


def nonzero_apple_summary(summary: dict[str, Any]) -> bool:
    return any(isinstance(value, (int, float)) and value > 0 for value in summary.values())


def clamp(value: Any, low: float, high: float) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = low
    return max(low, min(high, number))


def reduction(source_bytes: int | None, output_bytes: int) -> float | None:
    if not source_bytes:
        return None
    return round(1 - (output_bytes / source_bytes), 4)


def merge_unique(existing: list[Any], additions: list[Any]) -> list[Any]:
    output = list(existing)
    seen = {json.dumps(item, sort_keys=True) for item in output}
    for item in additions:
        key = json.dumps(item, sort_keys=True)
        if key not in seen:
            output.append(item)
            seen.add(key)
    return output


def slug(value: Any) -> str:
    text = str(value or "unknown").lower()
    text = re.sub(r"[^a-z0-9]+", "_", text).strip("_")
    return text or "unknown"


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        handle.write(value)


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def render_report(profiles: list[dict[str, Any]]) -> str:
    lines = [
        "# MissionGenerationDigestView From Atlas Ingestion",
        "",
        "This directory contains deterministic MissionGenerationDigestView packets built from Atlas Survey Evidence Export ingestion outputs.",
        "",
        "The builder consumes `atlas_digest_view.json` and `signals.jsonl`. It does not read raw Survey payloads, Profile Writer output, hidden simulator truth, or canonical graph mutation instructions.",
        "",
        "| profile | candidate roles | recent signals | evidence refs | output bytes | reduction vs Survey Evidence Export | reduction vs AtlasDigestView |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for profile in profiles:
        lines.append(
            "| {profile_label} | {candidate_roles} | {recent_signals} | {evidence_refs} | {mission_generation_digest_view_bytes} | {survey_reduction} | {atlas_reduction} |".format(
                profile_label=profile["profile_label"],
                candidate_roles=profile["candidate_roles"],
                recent_signals=profile["recent_signals"],
                evidence_refs=profile["evidence_refs"],
                mission_generation_digest_view_bytes=profile["mission_generation_digest_view_bytes"],
                survey_reduction=percent(profile["reduction_vs_survey_evidence_export"]),
                atlas_reduction=percent(profile["reduction_vs_atlas_digest_view"]),
            )
        )
    lines.extend(
        [
            "",
            "## Remaining Blocker",
            "",
            "`ATL-I001` remains open: Survey Simulator still needs to provide the fixed Alpha 1 `A4_Al2_S4` Survey Evidence Export fixture. Current generated packets prove the Atlas-to-MissionGenerationDigestView handoff on existing normalized `A3_Al1_S2` exports only.",
            "",
        ]
    )
    return "\n".join(lines)


def percent(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value * 100:.1f}%"


if __name__ == "__main__":
    raise SystemExit(main())
