from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


PRIMARY_REACTIONS = ["love", "like", "keep", "not_for_me"]
STRUCTURALLY_USELESS_CHIP_LABELS = {
    "good",
    "bad",
    "like it",
    "liked it",
    "love it",
    "not for me",
    "great song",
    "catchy",
    "nice",
    "nice vocals",
    "boring",
    "skip",
    "meh",
    "not my style",
    "interesting",
}
TRAP_POSITIVE_TERMS = {
    "unexpected exception",
    "bounded exception",
    "cultural furniture",
    "reassess",
    "re-assess",
    "revisit",
    "dead end",
    "exception",
    "do not generalize",
    "needs recurrence",
    "future recurrence",
}
FORCED_NEGATIVE_TRAP_TERMS = {
    "still negative",
    "ignore the positive",
    "proves the dead end",
    "confirms the dead end",
    "must reject",
    "should reject",
    "positive does not matter",
}


def score_mission_output(
    parsed_output: Optional[Dict[str, Any]],
    request_fixture: Dict[str, Any],
    candidate_pool: Optional[Dict[str, Any]],
    context_mode: str,
    prompt_template_name: str,
    schema_valid: bool,
    parse_error: Optional[str] = None,
) -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []

    def add_check(check_id: str, status: str, detail: str) -> None:
        checks.append({"check_id": check_id, "status": status, "detail": detail})

    add_check("valid_json", "pass" if parsed_output is not None else "fail", parse_error or "Parsed model output JSON.")
    add_check("schema_conformance", "pass" if schema_valid else "fail", "Output conforms to mission_output_schema_v0_1.json." if schema_valid else "Schema validation failed.")

    if parsed_output is None:
        return _finish(checks)

    items = _route_items(parsed_output)
    add_check("route_not_empty", "pass" if items else "fail", f"Route item count: {len(items)}")

    expected_range = request_fixture.get("expected_route_item_count", {})
    min_items = expected_range.get("min", 1)
    max_items = expected_range.get("max", 999)
    count_status = "pass" if min_items <= len(items) <= max_items else "fail"
    add_check("route_item_count_expected", count_status, f"Expected {min_items}-{max_items}, got {len(items)}.")

    missing_reactions: List[str] = []
    thin_chip_sets: List[str] = []
    missing_search: List[str] = []
    useless_chip_labels: List[str] = []

    for item in items:
        item_ref = _item_ref(item)
        chip_sets = item.get("feedback_chip_sets", {})
        for reaction in PRIMARY_REACTIONS:
            chips = chip_sets.get(reaction)
            if not isinstance(chips, list):
                missing_reactions.append(f"{item_ref}:{reaction}")
            elif len(chips) < 2:
                thin_chip_sets.append(f"{item_ref}:{reaction}:{len(chips)}")
            for chip in chips or []:
                label = str(chip.get("label", "")).strip().lower()
                signal_meaning = str(chip.get("signal_meaning", "")).strip().lower()
                if label in STRUCTURALLY_USELESS_CHIP_LABELS or _chip_meaning_is_structurally_empty(label, signal_meaning):
                    useless_chip_labels.append(f"{item_ref}:{reaction}:{label}")
        search_hint = item.get("music_kit_search_hint", {})
        if not isinstance(search_hint, dict) or not search_hint.get("search_query"):
            missing_search.append(item_ref)

    add_check("all_items_have_four_chip_sets", "pass" if not missing_reactions else "fail", _detail_list(missing_reactions, "Missing chip sets"))
    add_check("each_chip_set_has_two_chips", "pass" if not thin_chip_sets else "fail", _detail_list(thin_chip_sets, "Chip sets with fewer than 2 chips"))
    add_check("music_kit_search_hints_present", "pass" if not missing_search else "fail", _detail_list(missing_search, "Missing MusicKit search hints"))

    duplicate_item_ids = _duplicate_route_item_ids(items)
    add_check(
        "route_item_ids_unique",
        "pass" if not duplicate_item_ids else "fail",
        _detail_list(duplicate_item_ids, "Duplicate route item IDs") if duplicate_item_ids else "No duplicate route item IDs found.",
    )

    duplicate_candidate_ids = _duplicate_candidate_ids(items)
    add_check(
        "route_candidate_ids_unique",
        "pass" if not duplicate_candidate_ids else "fail",
        _detail_list(duplicate_candidate_ids, "Duplicate route candidate IDs") if duplicate_candidate_ids else "No duplicate route candidate IDs found.",
    )

    duplicate_display_identities = _duplicate_display_identities(items)
    add_check(
        "route_display_identity_unique",
        "pass" if not duplicate_display_identities else "fail",
        _detail_list(duplicate_display_identities, "Duplicate route display identities") if duplicate_display_identities else "No duplicate route display identities found.",
    )

    duplicates = _duplicate_songs(items)
    allow_duplicates = request_fixture.get("constraints", {}).get("allow_duplicate_songs", False)
    duplicate_status = "pass" if (allow_duplicates or not duplicates) else "fail"
    add_check("no_duplicate_songs_unless_allowed", duplicate_status, _detail_list(duplicates, "Duplicate songs") if duplicates else "No duplicate songs found.")

    add_check(
        "expected_archetype_present",
        _expected_archetype_status(parsed_output, request_fixture),
        f"Expected one of {request_fixture.get('expected_archetypes', [])}; got {parsed_output.get('archetypes', [])}.",
    )

    candidate_status, candidate_detail = _candidate_constrained_status(items, candidate_pool, context_mode, prompt_template_name)
    add_check("candidate_constrained_uses_pool", candidate_status, candidate_detail)

    risk_status, risk_detail = _risk_ratio_status(items, request_fixture)
    add_check("risk_ratio_constraints", risk_status, risk_detail)

    year_status, year_detail = _year_constraint_status(items, request_fixture)
    add_check("year_constraints", year_status, year_detail)

    warning_status, warning_detail = _required_warning_status(parsed_output, request_fixture)
    add_check("known_dead_end_warnings_present", warning_status, warning_detail)

    trap_status, trap_detail = _false_nearby_status(items, request_fixture)
    add_check("false_nearby_traps_not_promoted", trap_status, trap_detail)

    useless_ratio = len(useless_chip_labels) / max(1, _chip_count(items))
    useless_status = "pass" if useless_ratio <= 0.05 else "partial" if useless_ratio <= 0.15 else "fail"
    add_check("feedback_chips_not_generic", useless_status, f"Structurally useless chip labels: {len(useless_chip_labels)} of {_chip_count(items)}.")

    waypoint_status, waypoint_detail = _waypoint_status(parsed_output, request_fixture)
    add_check("waypoint_landmark_distinction", waypoint_status, waypoint_detail)

    completion_status, completion_detail = _completion_semantics_status(parsed_output)
    add_check("completion_counts_primary_reactions_separately", completion_status, completion_detail)

    atlas_status, atlas_detail = _possible_atlas_update_status(parsed_output)
    add_check("possible_atlas_updates_are_conditional", atlas_status, atlas_detail)

    atlas_scope_status, atlas_scope_detail = _possible_atlas_update_scope_status(parsed_output, items)
    add_check("possible_atlas_updates_are_mission_scoped", atlas_scope_status, atlas_scope_detail)

    review_status, review_detail = _review_needed_status(parsed_output, items)
    add_check("risky_trap_frontier_items_need_review", review_status, review_detail)

    trap_chip_status, trap_chip_detail = _trap_positive_chip_semantics_status(items)
    add_check("trap_positive_chips_have_exception_semantics", trap_chip_status, trap_chip_detail)

    hypothesis_status, hypothesis_detail = _hypothesis_not_evidence_status(parsed_output)
    add_check("generated_hypothesis_is_not_evidence", hypothesis_status, hypothesis_detail)

    role_status, role_detail = _candidate_role_discipline_status(parsed_output, items, candidate_pool)
    add_check("candidate_role_discipline", role_status, role_detail)

    route_shape_status, route_shape_detail = _route_shape_status(parsed_output, items, request_fixture)
    add_check("mission_route_shape", route_shape_status, route_shape_detail)

    return _finish(checks)


def human_rubric() -> List[Dict[str, Any]]:
    categories = [
        "Mission is a mission, not a playlist.",
        "Route logic is coherent.",
        "Hypothesis is personalized.",
        "Uses Atlas context correctly.",
        "Avoids known overgeneralization.",
        "Handles Waypoint vs Landmark distinction.",
        "Handles Dead Ends intelligently.",
        "Feedback chips are specific and useful.",
        "Feedback chips are structurally useful.",
        "Feedback chips use user vocabulary naturally.",
        "Expected signals are meaningful.",
        "Mission would produce useful evidence.",
        "Mission would be listenable and attractive to Matt.",
        "Uncertainty is preserved.",
        "MusicKit resolution is plausible.",
        "Output length is appropriate.",
        "Product voice feels like Cartenza.",
    ]
    return [{"category": category, "scale": "0-3", "score": None, "notes": ""} for category in categories]


def _finish(checks: List[Dict[str, Any]]) -> Dict[str, Any]:
    passed = sum(1 for check in checks if check["status"] == "pass")
    partial = sum(1 for check in checks if check["status"] == "partial")
    failed = sum(1 for check in checks if check["status"] == "fail")
    automated_score = round((passed + 0.5 * partial) / max(1, len(checks)), 3)
    return {
        "automated_score": automated_score,
        "pass_count": passed,
        "partial_count": partial,
        "fail_count": failed,
        "checks": checks,
        "human_rubric": human_rubric(),
    }


def _route_items(parsed_output: Dict[str, Any]) -> List[Dict[str, Any]]:
    route = parsed_output.get("route", {})
    items = route.get("items") if isinstance(route, dict) else None
    return items if isinstance(items, list) else []


def _item_ref(item: Dict[str, Any]) -> str:
    metadata = item.get("display_metadata", {})
    artist = metadata.get("artist", "?")
    title = metadata.get("title", "?")
    return f"{artist} - {title}"


def _detail_list(values: Sequence[str], prefix: str) -> str:
    if not values:
        return "OK."
    shown = "; ".join(values[:10])
    suffix = f" (+{len(values) - 10} more)" if len(values) > 10 else ""
    return f"{prefix}: {shown}{suffix}"


def _duplicate_route_item_ids(items: Sequence[Dict[str, Any]]) -> List[str]:
    seen = set()
    duplicates = []
    for item in items:
        item_id = str(item.get("item_id", "")).strip()
        if not item_id:
            continue
        if item_id in seen:
            duplicates.append(f"{item_id}:{_item_ref(item)}")
        seen.add(item_id)
    return duplicates


def _duplicate_candidate_ids(items: Sequence[Dict[str, Any]]) -> List[str]:
    seen = set()
    duplicates = []
    for item in items:
        candidate_id = str(item.get("candidate_id", "")).strip()
        if not candidate_id:
            continue
        if candidate_id in seen:
            duplicates.append(f"{candidate_id}:{_item_ref(item)}")
        seen.add(candidate_id)
    return duplicates


def _duplicate_display_identities(items: Sequence[Dict[str, Any]]) -> List[str]:
    seen = set()
    duplicates = []
    for item in items:
        key = _route_display_identity_key(item)
        if not key:
            continue
        if key in seen:
            duplicates.append(f"{key}:{_item_ref(item)}")
        seen.add(key)
    return duplicates


def _duplicate_songs(items: Sequence[Dict[str, Any]]) -> List[str]:
    seen = set()
    duplicates = []
    for item in items:
        artist = _route_artist(item)
        title = _route_title(item)
        if not artist or not title:
            continue
        key = f"{artist}:{title}"
        if key in seen:
            duplicates.append(_item_ref(item))
        seen.add(key)
    return duplicates


def _expected_archetype_status(parsed_output: Dict[str, Any], request_fixture: Dict[str, Any]) -> str:
    expected = {value.lower() for value in request_fixture.get("expected_archetypes", [])}
    actual = {str(value).lower() for value in parsed_output.get("archetypes", [])}
    if not expected:
        return "pass"
    if expected & actual:
        return "pass"
    actual_blob = " ".join(actual)
    if any(expected_value in actual_blob for expected_value in expected):
        return "partial"
    return "fail"


def _candidate_constrained_status(
    items: Sequence[Dict[str, Any]],
    candidate_pool: Optional[Dict[str, Any]],
    context_mode: str,
    prompt_template_name: str,
) -> Tuple[str, str]:
    constrained = "candidate_constrained" in prompt_template_name
    if not constrained:
        return "pass", "Candidate constraint was not requested for this run."
    if not candidate_pool or not candidate_pool.get("candidates"):
        return "partial", "Candidate-constrained run had no candidate pool fixture."

    candidates = candidate_pool.get("candidates", [])
    candidates_by_id = {
        str(candidate.get("candidate_id", "")).strip(): candidate
        for candidate in candidates
        if str(candidate.get("candidate_id", "")).strip()
    }
    misses = []
    mismatches = []
    for item in items:
        candidate_id = str(item.get("candidate_id", "")).strip()
        if not candidate_id:
            misses.append(f"{_item_ref(item)}: missing candidate_id")
            continue
        candidate = candidates_by_id.get(candidate_id)
        if not candidate:
            misses.append(f"{_item_ref(item)}: {candidate_id}")
            continue

        item_artist = _route_artist(item)
        item_title = _route_title(item)
        candidate_artist = _normalize_identity_part(candidate.get("artist"))
        candidate_title = _normalize_identity_part(candidate.get("title"))
        if item_artist and item_title and candidate_artist and candidate_title:
            if item_artist != candidate_artist or item_title != candidate_title:
                mismatches.append(
                    f"{_item_ref(item)} uses {candidate_id} but pool row is "
                    f"{candidate.get('artist', '?')} - {candidate.get('title', '?')}"
                )

    if misses:
        return "fail", _detail_list(misses, "Route items missing exact candidate-pool membership")
    if mismatches:
        return "fail", _detail_list(mismatches, "Route item metadata mismatches selected candidate_id")
    return "pass", "All route items copy an exact candidate_id from candidate_pool.candidates."


def _route_display_identity_key(item: Dict[str, Any]) -> str:
    item_type = _normalize_identity_part(item.get("item_type"))
    artist = _route_artist(item)
    title = _route_title(item)
    if not artist or not title:
        return ""
    return f"{item_type or 'unknown'}:{artist}:{title}"


def _route_artist(item: Dict[str, Any]) -> str:
    metadata = item.get("display_metadata", {})
    search_hint = item.get("music_kit_search_hint", {})
    value = None
    if isinstance(metadata, dict):
        value = metadata.get("artist")
    if not value and isinstance(search_hint, dict):
        value = search_hint.get("artist")
    return _normalize_identity_part(value)


def _route_title(item: Dict[str, Any]) -> str:
    metadata = item.get("display_metadata", {})
    search_hint = item.get("music_kit_search_hint", {})
    value = None
    if isinstance(metadata, dict):
        value = metadata.get("title")
    if not value and isinstance(search_hint, dict):
        value = search_hint.get("title")
    return _normalize_identity_part(value)


def _normalize_identity_part(value: Any) -> str:
    text = str(value or "").lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def _risk_ratio_status(items: Sequence[Dict[str, Any]], request_fixture: Dict[str, Any]) -> Tuple[str, str]:
    expected = request_fixture.get("constraints", {}).get("expected_risk_ratio")
    if not expected:
        return "pass", "No risk-ratio constraint for this request."
    safe_target = float(expected.get("safe", 0))
    risky_target = float(expected.get("risky", 0))
    safe_count = sum(1 for item in items if item.get("risk_class") == "safe")
    risky_count = sum(1 for item in items if item.get("risk_class") in {"risky", "trap", "dead_end_check"})
    total = max(1, len(items))
    safe_ratio = safe_count / total
    risky_ratio = risky_count / total
    ok = abs(safe_ratio - safe_target) <= 0.20 and abs(risky_ratio - risky_target) <= 0.20
    status = "pass" if ok else "partial" if abs(safe_ratio - safe_target) <= 0.30 else "fail"
    return status, f"Target safe/risky {safe_target:.2f}/{risky_target:.2f}; got {safe_ratio:.2f}/{risky_ratio:.2f}."


def _year_constraint_status(items: Sequence[Dict[str, Any]], request_fixture: Dict[str, Any]) -> Tuple[str, str]:
    expected_year = request_fixture.get("constraints", {}).get("expected_year")
    if expected_year is None:
        return "pass", "No fixed-year constraint for this request."
    mismatches = []
    for item in items:
        year = item.get("display_metadata", {}).get("release_year")
        if year != expected_year:
            mismatches.append(f"{_item_ref(item)}:{year}")
    return ("pass", f"All items use release year {expected_year}.") if not mismatches else ("fail", _detail_list(mismatches, "Wrong-year items"))


def _required_warning_status(parsed_output: Dict[str, Any], request_fixture: Dict[str, Any]) -> Tuple[str, str]:
    terms = request_fixture.get("constraints", {}).get("required_warning_terms", [])
    if not terms:
        return "pass", "No request-specific warning terms required."
    blob = _text_blob(parsed_output)
    missing = [term for term in terms if term.lower() not in blob]
    return ("pass", "Required warning terms are present.") if not missing else ("fail", _detail_list(missing, "Missing warning terms"))


def _false_nearby_status(items: Sequence[Dict[str, Any]], request_fixture: Dict[str, Any]) -> Tuple[str, str]:
    avoid_terms = request_fixture.get("constraints", {}).get("avoid_artist_terms", [])
    if not avoid_terms:
        return "pass", "No request-specific false-nearby artist terms configured."
    promoted = []
    explicit_tests = []
    ambiguous_tests = []
    for item in items:
        item_text = _text_blob(item)
        metadata = item.get("display_metadata", {})
        display_text = _text_blob(
            {
                "artist": metadata.get("artist", ""),
                "title": metadata.get("title", ""),
            }
        )
        for term in avoid_terms:
            if term.lower() in item_text:
                term_l = term.lower()
                selected_avoid_artist = term_l in display_text
                if not selected_avoid_artist and _term_only_appears_as_caution(item_text, term_l):
                    continue
                if item.get("risk_class") in {"trap", "dead_end_check"} or item.get("selection_role") == "trap":
                    if _item_has_explicit_trap_use(item) and _item_has_trap_positive_semantics(item):
                        explicit_tests.append(term)
                    else:
                        ambiguous_tests.append(term)
                else:
                    promoted.append(term)
    if promoted:
        return "fail", _detail_list(sorted(set(promoted)), "False-nearby terms promoted")
    if ambiguous_tests:
        return "partial", _detail_list(sorted(set(ambiguous_tests)), "False-nearby terms used ambiguously")
    if explicit_tests:
        return "pass", _detail_list(sorted(set(explicit_tests)), "False-nearby terms used as explicit boundary tests")
    return "pass", "False-nearby terms were not selected."


def _waypoint_status(parsed_output: Dict[str, Any], request_fixture: Dict[str, Any]) -> Tuple[str, str]:
    waypoint_terms = request_fixture.get("constraints", {}).get("waypoint_terms", [])
    if not waypoint_terms:
        return "pass", "No request-specific Waypoint terms configured."
    blob = _text_blob(parsed_output)
    failures = []
    for term in waypoint_terms:
        term_l = term.lower()
        if term_l in blob:
            pattern = re.compile(rf"{re.escape(term_l)}.{{0,80}}landmark|landmark.{{0,80}}{re.escape(term_l)}")
            if pattern.search(blob):
                failures.append(term)
    return ("pass", "Waypoint terms were not promoted to Landmarks.") if not failures else ("fail", _detail_list(failures, "Waypoint terms near Landmark language"))


def _completion_semantics_status(parsed_output: Dict[str, Any]) -> Tuple[str, str]:
    criteria = parsed_output.get("completion_criteria", {})
    if not isinstance(criteria, dict):
        return "fail", "Missing completion_criteria object."
    if "min_reactions" in criteria:
        return "fail", "Legacy min_reactions conflates primary reactions with chip selections."
    required = [
        "min_primary_reactions",
        "primary_reaction_policy",
        "min_chip_selections_for_summary",
        "chip_selection_policy",
    ]
    missing = [key for key in required if key not in criteria]
    if missing:
        return "fail", _detail_list(missing, "Missing completion semantics fields")
    policy_blob = _text_blob(
        {
            "primary_reaction_policy": criteria.get("primary_reaction_policy", ""),
            "chip_selection_policy": criteria.get("chip_selection_policy", ""),
            "completion_logic": criteria.get("completion_logic", ""),
        }
    )
    if "primary" not in policy_blob or "chip" not in policy_blob:
        return "partial", "Completion policy fields exist but do not clearly distinguish primary reactions from chip selections."
    return "pass", "Completion criteria count primary reactions separately from chip selections."


def _possible_atlas_update_status(parsed_output: Dict[str, Any]) -> Tuple[str, str]:
    if "atlas_update_candidates" in parsed_output:
        return "fail", "Legacy atlas_update_candidates field implies too-immediate updates."
    candidates = parsed_output.get("possible_atlas_update_candidates")
    if not isinstance(candidates, list):
        return "fail", "Missing possible_atlas_update_candidates array."
    if not candidates:
        return "pass", "No possible Atlas updates proposed."

    missing_conditions = []
    weak_conditions = []
    missing_review = []
    insufficient_recurrence = []
    direct_mutation = []
    landmark_overclaim = []
    for candidate in candidates:
        candidate_id = str(candidate.get("candidate_id", "<unknown>"))
        atlas_role = str(candidate.get("atlas_role", ""))
        candidate_blob = _text_blob(candidate)
        conditions = candidate.get("trigger_conditions")
        if not isinstance(conditions, list) or not conditions:
            missing_conditions.append(candidate_id)
            continue
        if candidate.get("review_required") is not True:
            missing_review.append(candidate_id)
        if atlas_role == "Landmark" and candidate.get("confidence") == "high":
            landmark_overclaim.append(candidate_id)
        if _contains_direct_atlas_mutation_language(candidate_blob):
            direct_mutation.append(candidate_id)
        for condition in conditions:
            operations = condition.get("future_reaction_operations", []) if isinstance(condition, dict) else []
            condition_blob = _text_blob(condition)
            has_reaction = any(operation in PRIMARY_REACTIONS for operation in operations) or "reaction" in condition_blob
            has_future_gate = any(term in condition_blob for term in ["future", "after", "if", "when", "only if", "recurrence", "repeat"])
            if not has_reaction or not has_future_gate:
                weak_conditions.append(candidate_id)
                break
            minimum_occurrences = condition.get("minimum_occurrences", 0) if isinstance(condition, dict) else 0
            if atlas_role != "Signal only" and _to_int(minimum_occurrences) < 2:
                insufficient_recurrence.append(candidate_id)
                break

    if missing_conditions:
        return "fail", _detail_list(missing_conditions, "Possible Atlas updates without trigger conditions")
    if weak_conditions:
        return "fail", _detail_list(weak_conditions, "Trigger conditions are not tied to future reactions")
    if missing_review:
        return "fail", _detail_list(missing_review, "Possible Atlas updates missing review_required=true")
    if insufficient_recurrence:
        return "fail", _detail_list(insufficient_recurrence, "Non-Signal Atlas role changes need at least 2 future occurrences")
    if landmark_overclaim:
        return "fail", _detail_list(landmark_overclaim, "Possible Atlas updates overclaim high-confidence Landmark status")
    if direct_mutation:
        return "fail", _detail_list(direct_mutation, "Possible Atlas updates imply direct mutation")
    return "pass", "Possible Atlas updates are explicitly conditional on future reactions."


def _possible_atlas_update_scope_status(parsed_output: Dict[str, Any], items: Sequence[Dict[str, Any]]) -> Tuple[str, str]:
    candidates = parsed_output.get("possible_atlas_update_candidates")
    if not isinstance(candidates, list) or not candidates:
        return "pass", "No possible Atlas updates to scope."

    route_candidate_ids = {str(item.get("candidate_id", "")) for item in items if item.get("candidate_id")}
    route_items_by_candidate_id = {
        str(item.get("candidate_id", "")): item
        for item in items
        if item.get("candidate_id")
    }
    route_refs = []
    route_terms_by_candidate_id: Dict[str, Dict[str, str]] = {}
    for item in items:
        metadata = item.get("display_metadata", {})
        artist = str(metadata.get("artist", "")).strip().lower()
        title = str(metadata.get("title", "")).strip().lower()
        candidate_id = str(item.get("candidate_id", ""))
        if candidate_id:
            route_terms_by_candidate_id[candidate_id] = {"artist": artist, "title": title}
        if artist and title:
            route_refs.append(f"{artist} {title}")
        if artist:
            route_refs.append(artist)
        if title:
            route_refs.append(title)

    copied_context_candidates = []
    mismatched_candidate_text = []
    risky_role_mismatches = []
    unscoped_candidates = []
    for candidate in candidates:
        candidate_id = str(candidate.get("candidate_id", "")).strip()
        candidate_blob = _text_blob(candidate)
        if candidate_id.startswith(("update_candidate:survey_", "update_candidate:mission_review_")):
            copied_context_candidates.append(candidate_id)
            continue
        if candidate_id in route_candidate_ids:
            own_terms = route_terms_by_candidate_id.get(candidate_id, {})
            own_title = own_terms.get("title", "")
            own_artist = own_terms.get("artist", "")
            other_mentions = []
            for other_candidate_id, terms in route_terms_by_candidate_id.items():
                if other_candidate_id == candidate_id:
                    continue
                for term_type, term in terms.items():
                    if term and len(term) >= 4 and term in candidate_blob:
                        other_mentions.append(f"{other_candidate_id}:{term_type}={term}")
            own_mentioned = any(term and len(term) >= 4 and term in candidate_blob for term in [own_title, own_artist])
            if other_mentions and not own_mentioned:
                mismatched_candidate_text.append(f"{candidate_id}: update text references another route item ({', '.join(other_mentions[:3])})")
            route_item = route_items_by_candidate_id.get(candidate_id, {})
            route_risk = route_item.get("risk_class")
            atlas_role = candidate.get("atlas_role")
            if atlas_role == "Dead End" and route_risk not in {"trap", "dead_end_check"}:
                risky_role_mismatches.append(f"{candidate_id}: Dead End update proposed for non-trap route item")
            continue
        if any(route_id.lower() in candidate_blob for route_id in route_candidate_ids):
            continue
        if any(route_ref and route_ref in candidate_blob for route_ref in route_refs):
            continue
        unscoped_candidates.append(candidate_id or "<missing candidate_id>")

    if copied_context_candidates:
        return "fail", _detail_list(copied_context_candidates, "Mission output appears to copy existing Atlas update candidates from digest context")
    if mismatched_candidate_text:
        return "fail", _detail_list(mismatched_candidate_text, "Possible Atlas update candidate IDs do not match their rationale text")
    if risky_role_mismatches:
        return "fail", _detail_list(risky_role_mismatches, "Possible Atlas update roles do not match route item risk")
    if unscoped_candidates:
        return "partial", _detail_list(unscoped_candidates, "Possible Atlas updates are not clearly tied to selected route items")
    return "pass", "Possible Atlas updates are scoped to selected route evidence."


def _review_needed_status(parsed_output: Dict[str, Any], items: Sequence[Dict[str, Any]]) -> Tuple[str, str]:
    review_config = parsed_output.get("review_config", {})
    policy_values = set(review_config.get("default_item_review_needed_for", [])) if isinstance(review_config, dict) else set()
    missing_policy_values = [value for value in ["risky", "trap", "dead_end_check"] if value not in policy_values]
    frontier_mission = any("frontier" in str(archetype).lower() for archetype in parsed_output.get("archetypes", []))
    if frontier_mission and "frontier_unknown" not in policy_values:
        missing_policy_values.append("frontier_unknown")

    missing_item_review = []
    for item in items:
        risk_class = item.get("risk_class")
        familiarity = item.get("familiarity_assumption")
        should_review = risk_class in {"risky", "trap", "dead_end_check"} or (frontier_mission and familiarity == "unknown")
        review_state = item.get("review_state", {})
        if should_review and review_state.get("needs_human_review") is not True:
            missing_item_review.append(_item_ref(item))

    if missing_item_review:
        return "fail", _detail_list(missing_item_review, "Items that should default to review-needed")
    if missing_policy_values:
        return "partial", _detail_list(sorted(set(missing_policy_values)), "Review config does not name default review classes")
    return "pass", "Risky, trap, dead-end, and frontier-unknown items default to review-needed."


def _trap_positive_chip_semantics_status(items: Sequence[Dict[str, Any]]) -> Tuple[str, str]:
    trap_items = [
        item
        for item in items
        if item.get("risk_class") in {"trap", "dead_end_check"} or item.get("selection_role") == "trap"
    ]
    if not trap_items:
        return "pass", "No trap or Dead End items selected."

    missing_semantics = []
    forced_negative = []
    negative_weight_only = []
    for item in trap_items:
        positive_chips = []
        chip_sets = item.get("feedback_chip_sets", {})
        for reaction in ["love", "like"]:
            positive_chips.extend(chip_sets.get(reaction, []) or [])
        blob = _text_blob(
            {
                "expected_positive_signal": item.get("expected_positive_signal", ""),
                "positive_chips": positive_chips,
            }
        )
        if not any(term in blob for term in TRAP_POSITIVE_TERMS):
            missing_semantics.append(_item_ref(item))
        if any(term in blob for term in FORCED_NEGATIVE_TRAP_TERMS):
            forced_negative.append(_item_ref(item))
        if positive_chips and all(chip.get("weight_hint") == "negative" for chip in positive_chips):
            negative_weight_only.append(_item_ref(item))

    if forced_negative:
        return "fail", _detail_list(forced_negative, "Trap positive reactions forced into negative interpretation")
    if negative_weight_only:
        return "fail", _detail_list(negative_weight_only, "Trap love/like chips all have negative weight")
    if missing_semantics:
        return "fail", _detail_list(missing_semantics, "Trap love/like chips missing exception/cultural-furniture/reassess semantics")
    return "pass", "Trap love/like chips use unexpected-exception, cultural-furniture, or reassess-dead-end semantics."


def _hypothesis_not_evidence_status(parsed_output: Dict[str, Any]) -> Tuple[str, str]:
    checked_text = _text_blob(
        {
            "brief": parsed_output.get("brief", ""),
            "hypothesis": parsed_output.get("hypothesis", ""),
            "why_now": parsed_output.get("why_now", ""),
            "risk_model": parsed_output.get("risk_model", {}),
            "route_summary": parsed_output.get("route", {}).get("route_summary", "") if isinstance(parsed_output.get("route"), dict) else "",
        }
    )
    bad_patterns = [
        r"\bopens? a region\b",
        r"\bcreates? a region\b",
        r"\bestablishes? (a )?(region|landmark)\b",
        r"\bproves? (that )?(you|matt)\b",
        r"\bconfirms? (that )?(you|matt)\b",
        r"\bnew confirmed\b",
        r"\bconfirmed landmark\b",
        r"\bwill update\b",
    ]
    for pattern in bad_patterns:
        match = re.search(pattern, checked_text)
        if match and not _has_uncertainty_near(checked_text, match.start(), match.end()):
            return "fail", f"Generated mission premise is treated as learned evidence near: {match.group(0)}"
    return "pass", "Mission hypothesis is framed as testable rather than already-learned evidence."


def _candidate_role_discipline_status(
    parsed_output: Dict[str, Any],
    items: Sequence[Dict[str, Any]],
    candidate_pool: Optional[Dict[str, Any]],
) -> Tuple[str, str]:
    if not candidate_pool:
        return "pass", "No candidate pool supplied for role-discipline checks."

    candidates = {
        candidate.get("candidate_id"): candidate
        for candidate in candidate_pool.get("candidates", [])
        if candidate.get("candidate_id")
    }
    possible_updates = parsed_output.get("possible_atlas_update_candidates", [])
    update_by_candidate: Dict[str, List[Dict[str, Any]]] = {}
    for update in possible_updates if isinstance(possible_updates, list) else []:
        update_by_candidate.setdefault(str(update.get("candidate_id", "")), []).append(update)

    failures = []
    partials = []
    explicit_trap_notes = []
    for item in items:
        candidate_id = item.get("candidate_id")
        candidate = candidates.get(candidate_id)
        if not candidate:
            continue
        candidate_risk = candidate.get("risk_class")
        item_risk = item.get("risk_class")
        item_role = item.get("selection_role")
        candidate_blob = _text_blob(candidate)
        item_ref = _item_ref(item)

        if candidate_risk == "trap":
            if item_risk not in {"trap", "dead_end_check"}:
                failures.append(f"{item_ref}: trap candidate promoted outside trap/dead-end risk")
            elif item_role == "trap":
                pass
            elif _item_has_explicit_trap_use(item) and _item_has_trap_positive_semantics(item):
                explicit_trap_notes.append(f"{item_ref}: trap candidate used as explicit boundary/checkpoint")
            else:
                partials.append(f"{item_ref}: trap candidate used ambiguously")
        if candidate_risk == "safe" and item_risk in {"risky", "trap", "dead_end_check"}:
            failures.append(f"{item_ref}: safe candidate escalated into risky/trap role")
        if "waypoint" in candidate_blob:
            for update in update_by_candidate.get(str(candidate_id), []):
                if update.get("atlas_role") == "Landmark":
                    failures.append(f"{item_ref}: Waypoint candidate has Landmark update candidate")
        if candidate.get("known_to_user") == "unknown":
            for update in update_by_candidate.get(str(candidate_id), []):
                if update.get("confidence") == "high" or update.get("atlas_role") in {"Landmark", "Region"}:
                    partials.append(f"{item_ref}: unknown candidate has high-confidence or Region/Landmark update")

    if failures:
        return "fail", _detail_list(failures, "Candidate role failures")
    if partials:
        return "partial", _detail_list(partials, "Candidate role caution flags")
    if explicit_trap_notes:
        return "pass", _detail_list(explicit_trap_notes, "Explicit trap/checkpoint uses")
    return "pass", "Selected candidate roles match route usage."


def _route_shape_status(
    parsed_output: Dict[str, Any],
    items: Sequence[Dict[str, Any]],
    request_fixture: Dict[str, Any],
) -> Tuple[str, str]:
    archetypes = {str(value).lower() for value in parsed_output.get("archetypes", [])}
    roles = [str(item.get("selection_role", "")) for item in items]
    risks = [str(item.get("risk_class", "")) for item in items]
    failures = []
    partials = []

    if any("bridge route" in archetype for archetype in archetypes):
        if "anchor" not in roles:
            failures.append("Bridge Route needs at least one anchor.")
        if "bridge" not in roles:
            failures.append("Bridge Route needs at least one bridge item.")
        if "probe" not in roles:
            failures.append("Bridge Route needs at least one probe.")

    if any("dead end check" in archetype or "correction route" in archetype for archetype in archetypes):
        trap_count = sum(1 for item in items if item.get("selection_role") == "trap" or item.get("risk_class") in {"trap", "dead_end_check"})
        has_reference = any(role in {"anchor", "checkpoint", "bridge"} for role in roles)
        has_safer_probe = any(item.get("risk_class") not in {"trap", "dead_end_check"} and item.get("selection_role") in {"probe", "bridge", "checkpoint"} for item in items)
        if not has_reference:
            failures.append("Dead End/Correction Route needs an anchor or reference point.")
        if trap_count == 0:
            failures.append("Dead End/Correction Route needs at least one boundary/trap item.")
        if not has_safer_probe:
            failures.append("Dead End/Correction Route needs a safer probe or alternative path.")
        if trap_count > 2 and "dead end" not in request_fixture.get("prompt", "").lower():
            partials.append(f"Dead End/Correction Route uses {trap_count} traps; expected no more than 2 unless explicitly requested.")

    if any("country/scene frontier" in archetype or "frontier route" in archetype for archetype in archetypes):
        blob = _text_blob(parsed_output)
        if not any(term in blob for term in ["uncertainty", "unresolved", "availability", "resolver", "not sure", "review"]):
            failures.append("Frontier route needs uncertainty or resolution caution.")
        if any(term in blob for term in ["definitive scene", "best lithuanian", "proves this scene"]):
            failures.append("Frontier route overclaims scene expertise.")

    if any("era personal route" in archetype for archetype in archetypes):
        weak_items = []
        for item in items:
            rationale_blob = _text_blob(
                {
                    "why_selected": item.get("why_selected", ""),
                    "route_function": item.get("route_function", ""),
                    "expected_positive_signal": item.get("expected_positive_signal", ""),
                }
            )
            if "critic" in rationale_blob and not any(term in rationale_blob for term in ["personal", "body", "bite", "architecture", "pressure", "matt"]):
                weak_items.append(_item_ref(item))
        if weak_items:
            failures.append(_detail_list(weak_items, "Era items leaning on critic canon"))

    if failures:
        return "fail", " ".join(failures)
    if partials:
        return "partial", " ".join(partials)
    return "pass", "Route shape matches the expected archetype."


def _chip_count(items: Sequence[Dict[str, Any]]) -> int:
    count = 0
    for item in items:
        for chips in item.get("feedback_chip_sets", {}).values():
            if isinstance(chips, list):
                count += len(chips)
    return count


def _to_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _chip_meaning_is_structurally_empty(label: str, signal_meaning: str) -> bool:
    if not signal_meaning:
        return True
    if signal_meaning == label:
        return True
    meaningful_terms = [
        "signal",
        "feature",
        "atlas",
        "route",
        "because",
        "means",
        "suggests",
        "evidence",
        "boundary",
        "exception",
        "recurrence",
        "waypoint",
        "body",
        "pressure",
        "architecture",
        "persona",
        "dead end",
        "review",
    ]
    return len(signal_meaning.split()) < 4 and not any(term in signal_meaning for term in meaningful_terms)


def _item_has_explicit_trap_use(item: Dict[str, Any]) -> bool:
    item_blob = _text_blob(
        {
            "selection_role": item.get("selection_role", ""),
            "risk_class": item.get("risk_class", ""),
            "why_selected": item.get("why_selected", ""),
            "route_function": item.get("route_function", ""),
            "item_hypothesis": item.get("item_hypothesis", ""),
            "expected_positive_signal": item.get("expected_positive_signal", ""),
            "expected_negative_signal": item.get("expected_negative_signal", ""),
        }
    )
    return any(term in item_blob for term in ["trap", "boundary", "dead end", "false-nearby", "false nearby", "check"])


def _item_has_trap_positive_semantics(item: Dict[str, Any]) -> bool:
    positive_chips = []
    for reaction in ["love", "like"]:
        positive_chips.extend(item.get("feedback_chip_sets", {}).get(reaction, []) or [])
    blob = _text_blob(
        {
            "expected_positive_signal": item.get("expected_positive_signal", ""),
            "positive_chips": positive_chips,
        }
    )
    return any(term in blob for term in TRAP_POSITIVE_TERMS)


def _has_uncertainty_near(text: str, start: int, end: int) -> bool:
    window = text[max(0, start - 80) : min(len(text), end + 80)]
    return any(term in window for term in ["could", "might", "if", "test", "hypothesis", "possible", "future", "would", "may"])


def _contains_direct_atlas_mutation_language(text: str) -> bool:
    direct_patterns = [
        r"\b(update|write|mutate|change) (the )?atlas\b",
        r"\badd(s)? .{0,40} to (the )?atlas\b",
        r"\bpromote(s)? .{0,40} to (a )?(landmark|region)\b",
        r"\bbecomes? (a )?(confirmed )?(landmark|region)\b",
    ]
    for pattern in direct_patterns:
        match = re.search(pattern, text)
        if match and not _has_negation_near(text, match.start()) and not _has_uncertainty_near(text, match.start(), match.end()):
            return True
    return False


def _term_only_appears_as_caution(text: str, term: str) -> bool:
    starts = [match.start() for match in re.finditer(re.escape(term), text)]
    if not starts:
        return False
    caution_terms = [
        "avoid",
        "boundary",
        "caution",
        "dead end",
        "false-nearby",
        "false nearby",
        "guardrail",
        "known error",
        "not ",
        "not permission",
        "rather than",
        "instead of",
        "trap",
        "without",
    ]
    for start in starts:
        window = text[max(0, start - 100) : min(len(text), start + len(term) + 100)]
        if not any(caution in window for caution in caution_terms):
            return False
    return True


def _has_negation_near(text: str, start: int) -> bool:
    window = text[max(0, start - 50) : start]
    return any(term in window for term in ["not ", "never ", "no direct ", "must not ", "do not ", "don't "])


def _text_blob(value: Any) -> str:
    if isinstance(value, dict):
        return " ".join(_text_blob(item) for item in value.values()).lower()
    if isinstance(value, list):
        return " ".join(_text_blob(item) for item in value).lower()
    return str(value).lower()
