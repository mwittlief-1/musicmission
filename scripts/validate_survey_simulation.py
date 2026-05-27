#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
SIM_DIR = REPO_ROOT / "data/survey_simulation"
GRAPH_DIR = REPO_ROOT / "data/canonical_graph/import_dry_run"
PAGE_SIZE = 12

PAGE1_INTENT_TARGETS = {
    "payload_signature_artist": 4,
    "archetype_confirmation_anchor": 3,
    "multi_archetype_junction": 2,
    "false_nearby_or_boundary_check": 1,
    "mass_popular_control": 1,
    "coverage_repair_broad_sentinel": 1,
}

PAGE1_GRAPH_ONLY_INTENT_TARGETS = {
    "archetype_confirmation_anchor": 4,
    "multi_archetype_junction": 3,
    "false_nearby_or_boundary_check": 1,
    "mass_popular_control": 2,
    "coverage_repair_broad_sentinel": 2,
}

PAGE2_SCORE_KEYS = {
    "posterior_relevance",
    "information_gain",
    "response_disambiguation_value",
    "graph_bridge_value",
    "coverage_repair_value",
    "false_nearby_value",
    "expected_familiarity",
    "apple_evidence",
    "novelty",
    "penalties",
    "final",
}

FORBIDDEN_VISIBLE_KEYS = {
    "fake_profile_id",
    "display_label",
    "hidden_reaction_corpus_id",
    "hidden_anti_affinities",
    "primary_archetype_affinities",
    "secondary_archetype_affinities",
    "reason_tags",
    "lookup_status",
    "hidden_lookup_status",
}

VISIBLE_RUN_JSON_FILES = {
    "survey_run.json",
    "page_generation_log.json",
    "recorded_responses.json",
    "apple_payload_used.json",
    "survey_state_after_page_001.json",
    "page_002_artists.json",
    "page_002_generation_log.json",
    "page_002_candidate_debug.json",
    "recorded_responses_page_002.json",
    "album_page_001_candidates.json",
    "song_page_001_candidates.json",
    "survey_state_after_page_002.json",
}

REQUIRED_RUN_FILES = {
    "survey_run.json",
    "survey_transcript.md",
    "page_generation_log.json",
    "recorded_responses.json",
    "apple_payload_used.json",
    "hidden_lookup_coverage_report.md",
    "hidden_lookup_coverage.json",
    "survey_state_after_page_001.json",
    "page_002_artists.json",
    "page_002_generation_log.json",
    "page_002_candidate_debug.json",
    "page_002_transcript.md",
    "recorded_responses_page_002.json",
    "coverage_report_page_002.json",
    "album_page_001_candidates.json",
    "song_page_001_candidates.json",
    "survey_state_after_page_002.json",
}

BACKTEST_REQUIRED_FILES = {
    "page_count_backtest_report.md",
    "config_metrics.json",
    "per_profile_metrics.json",
    "marginal_lift_by_page_type.json",
    "recommended_minimum_config.md",
}

LLM_PROFILE_REVIEW_REQUIRED_FILES = {
    "README.md",
    "schemas/profile_writer_input.schema.json",
    "schemas/profile_writer_output.schema.json",
    "schemas/profile_evaluator_output.schema.json",
    "prompts/profile_writer_system.md",
    "prompts/profile_writer_developer.md",
    "prompts/profile_evaluator_system.md",
    "prompts/profile_evaluator_developer.md",
    "api_requests/profile_writer_reference_request.json",
    "api_requests/evaluator_evidence_only_reference_request.json",
    "simulator_private/api_requests/evaluator_truth_scored_reference_request.json",
    "simulator_private/hidden_truth_packets/hidden_truth_public_profile_01_A2_Al1_S1.json",
    "reports/qualitative_profile_review_report.md",
}

LLM_PROFILE_REVIEW_PUBLIC_PACKET_CANDIDATES = (
    "public_packets/cartenza_survey_output_packet_public_profile_01_A2_Al1_S1.json",
    "public_packets/waymark_survey_output_packet_public_profile_01_A2_Al1_S1.json",
)

SURVEY_EVIDENCE_EXPORT_REQUIRED_FILES = {
    "survey_evidence_export_v0_1.md",
    "survey_evidence_export_v0_1.schema.json",
    "samples/public_profile_01_A3_Al1_S2_survey_evidence_export.json",
    "samples/public_profile_05_A3_Al1_S2_survey_evidence_export.json",
    "samples/public_profile_06_A3_Al1_S2_survey_evidence_export.json",
    "samples/public_profile_01_A4_Al2_S4_survey_evidence_export.json",
    "samples/public_profile_05_A4_Al2_S4_survey_evidence_export.json",
    "samples/public_profile_06_A4_Al2_S4_survey_evidence_export.json",
    "survey_evidence_export_v0_1_validation_report.md",
    "alpha_fast_survey_app_handoff/waymark_alpha_survey_output_contract_v0_1.md",
    "alpha_fast_survey_app_handoff/alpha_survey_app_ui_notes_v0_1.md",
    "alpha_fast_survey_app_handoff/alpha_survey_construction_exclusion_report_v0_1.md",
    "alpha_fast_survey_app_handoff/alpha_survey_page_packet_v0_1.schema.json",
    "alpha_fast_survey_app_handoff/public_profile_01_A2_Al1_S1_alpha_survey_page_packet.json",
    "alpha_fast_survey_app_handoff/public_profile_01_A2_Al1_S1_survey_evidence_export.json",
    "alpha_fast_survey_app_handoff/alpha_survey_output_validation_report.md",
    "alpha_fast_survey_app_handoff/alpha_fast_survey_evidence_validation_report.md",
    "alpha_fast_survey_app_handoff/examples/README.md",
    "alpha_fast_survey_app_handoff/examples/graph_only_artist_page_001_alpha_survey_slate_packet.json",
    "alpha_fast_survey_app_handoff/examples/apple_biased_artist_page_001_alpha_survey_slate_packet.json",
    "alpha_fast_survey_app_handoff/examples/public_profile_05_A3_Al1_S2_alpha_survey_page_packet.json",
    "alpha_fast_survey_app_handoff/examples/public_profile_06_A3_Al1_S2_alpha_survey_page_packet.json",
    "alpha1_required_intake/waymark_survey_output_packet_public_profile_01_A4_Al2_S4_alpha1_intake.json",
    "alpha1_required_intake/public_profile_01_A4_Al2_S4_alpha1_survey_page_packet.json",
    "alpha1_required_intake/public_profile_01_A4_Al2_S4_survey_evidence_export.json",
    "alpha1_required_intake/alpha1_required_intake_validation_report.md",
    "alpha1_required_intake/alpha1_required_intake_evidence_validation_report.md",
    "alpha1_required_intake/alpha1_required_intake_mission_generation_handoff_report.md",
}


def load_json(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        raise ValidationError(f"Missing file: {path}") from None
    except json.JSONDecodeError as error:
        raise ValidationError(f"Invalid JSON in {path}: {error}") from None


class ValidationError(Exception):
    pass


def first_existing_path(paths: Iterable[Path]) -> Path:
    path_list = list(paths)
    return next((path for path in path_list if path.exists()), path_list[0])


def first_existing_relative_path(base: Path, relative_paths: Iterable[str]) -> str | None:
    for relative_path in relative_paths:
        if (base / relative_path).exists():
            return relative_path
    return None


def page1_intent_targets(page_mode: str) -> dict[str, int]:
    if page_mode == "generic_graph_seed":
        return PAGE1_GRAPH_ONLY_INTENT_TARGETS
    return PAGE1_INTENT_TARGETS


def format_path(path_parts: Iterable[object]) -> str:
    parts = [str(part) for part in path_parts]
    return ".".join(parts) if parts else "<root>"


def validate_schema(schema_path: Path, document_path: Path) -> list[str]:
    try:
        from jsonschema import Draft202012Validator, FormatChecker
    except ModuleNotFoundError:
        raise ValidationError(
            "Missing dependency: jsonschema. Install with "
            "`python3 -m pip install -r scripts/requirements.txt`."
        ) from None

    schema = load_json(schema_path)
    document = load_json(document_path)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(document), key=lambda error: list(error.path))
    return [
        f"{document_path.relative_to(REPO_ROOT)} {format_path(error.path)}: {error.message}"
        for error in errors
    ]


def iter_dicts(value: Any) -> Iterable[dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from iter_dicts(child)
    elif isinstance(value, list):
        for child in value:
            yield from iter_dicts(child)


def iter_keys(value: Any) -> Iterable[str]:
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from iter_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from iter_keys(child)


def typed_ref_key(ref: dict[str, Any]) -> tuple[str, str] | None:
    if ref.get("ref_source") != "canonical_graph":
        return None
    object_type = ref.get("object_type")
    if object_type == "artist":
        return object_type, ref.get("canonical_artist_id", "")
    if object_type == "album":
        return object_type, ref.get("canonical_album_id", "")
    if object_type == "song_recording":
        return object_type, ref.get("canonical_song_recording_id", "")
    return None


def load_graph_keysets() -> dict[str, set[str]]:
    artists = load_json(GRAPH_DIR / "canonical_artists.json")
    albums = load_json(GRAPH_DIR / "canonical_albums.json")
    songs = load_json(GRAPH_DIR / "canonical_song_recordings.json")
    return {
        "artist": {item["canonical_artist_id"] for item in artists},
        "album": {item["canonical_album_id"] for item in albums},
        "song_recording": {item["canonical_song_recording_id"] for item in songs},
    }


def validate_typed_refs(document: Any, path: Path, graph_keys: dict[str, set[str]]) -> list[str]:
    errors = []
    for item in iter_dicts(document):
        if "object_id" in item:
            errors.append(f"{path.relative_to(REPO_ROOT)} contains vague `object_id`")
        if not {"object_type", "ref_source", "display_name", "resolution_state"}.issubset(item):
            continue
        ref_source = item.get("ref_source")
        if ref_source == "canonical_graph":
            key = typed_ref_key(item)
            if key is None:
                errors.append(f"{path.relative_to(REPO_ROOT)} has invalid canonical music_object_ref: {item}")
                continue
            object_type, canonical_id = key
            if not canonical_id:
                errors.append(f"{path.relative_to(REPO_ROOT)} has empty canonical id in {item}")
            elif canonical_id not in graph_keys[object_type]:
                errors.append(
                    f"{path.relative_to(REPO_ROOT)} references missing canonical {object_type}: {canonical_id}"
                )
        elif ref_source == "external_catalog":
            if "external_catalog_refs" not in item:
                errors.append(f"{path.relative_to(REPO_ROOT)} external ref lacks external_catalog_refs")
    return errors


def validate_schema_group(schema_name: str, files: list[Path]) -> list[str]:
    schema_path = SIM_DIR / "schemas" / schema_name
    errors = []
    for path in files:
        errors.extend(validate_schema(schema_path, path))
    return errors


def check_profile_fixtures(
    profiles: list[Path],
    apple_payloads: list[Path],
    hidden_corpora: list[Path],
) -> list[str]:
    errors = []
    if len(profiles) < 10:
        errors.append(f"Expected at least 10 fake profiles; found {len(profiles)}")

    apple_ids = {load_json(path)["apple_payload_id"] for path in apple_payloads}
    corpus_ids = {load_json(path)["hidden_reaction_corpus_id"] for path in hidden_corpora}
    profile_ids = set()
    for path in profiles:
        profile = load_json(path)
        profile_ids.add(profile["fake_profile_id"])
        if profile["apple_payload_id"] not in apple_ids:
            errors.append(f"{path.relative_to(REPO_ROOT)} references missing Apple payload")
        if profile["hidden_reaction_corpus_id"] not in corpus_ids:
            errors.append(f"{path.relative_to(REPO_ROOT)} references missing hidden corpus")

    for path in hidden_corpora:
        corpus = load_json(path)
        if corpus["fake_profile_id"] not in profile_ids:
            errors.append(f"{path.relative_to(REPO_ROOT)} references missing fake profile")
        object_types = {
            item["music_object_ref"]["object_type"]
            for item in corpus["reactions"]
        }
        missing_types = {"artist", "album", "song_recording"} - object_types
        if missing_types:
            errors.append(
                f"{path.relative_to(REPO_ROOT)} lacks hidden reactions for: {', '.join(sorted(missing_types))}"
            )
    return errors


def check_visible_data_boundaries(run_dirs: list[Path]) -> list[str]:
    errors = []
    for run_dir in run_dirs:
        for filename in VISIBLE_RUN_JSON_FILES:
            payload = load_json(run_dir / filename)
            leaked = sorted(FORBIDDEN_VISIBLE_KEYS & set(iter_keys(payload)))
            if leaked:
                errors.append(
                    f"{(run_dir / filename).relative_to(REPO_ROOT)} leaks hidden/private keys: {', '.join(leaked)}"
                )
        transcripts = [
            run_dir / "survey_transcript.md",
            run_dir / "page_002_transcript.md",
        ]
        forbidden_phrases = [
            "reason_tags",
            "fake_profile_",
            "Classic Suburban Dad",
            "Pop / Radio Generalist",
            "Alt Formation User",
            "Country-Pop Listener",
            "R&B / Hip-Hop Listener",
            "Theater / Family Context User",
            "Indie / Prestige Listener",
            "Metal / Heavy User",
            "Modern Pop + TikTok User",
            "Low-Library Streaming User",
        ]
        for transcript_path in transcripts:
            if not transcript_path.exists():
                continue
            transcript = transcript_path.read_text(encoding="utf-8")
            for phrase in forbidden_phrases:
                if phrase in transcript:
                    errors.append(
                        f"{transcript_path.relative_to(REPO_ROOT)} contains hidden phrase `{phrase}`"
                    )
    return errors


def check_run_artifacts(run_dirs: list[Path]) -> list[str]:
    errors = []
    for run_dir in run_dirs:
        present = {path.name for path in run_dir.iterdir() if path.is_file()}
        missing = REQUIRED_RUN_FILES - present
        if missing:
            errors.append(f"{run_dir.relative_to(REPO_ROOT)} missing required files: {', '.join(sorted(missing))}")
            continue

        survey_run = load_json(run_dir / "survey_run.json")
        page = survey_run["pages"][0]
        generation_log = load_json(run_dir / "page_generation_log.json")
        recorded = load_json(run_dir / "recorded_responses.json")
        coverage = load_json(run_dir / "hidden_lookup_coverage.json")

        if page["tile_count"] != PAGE_SIZE or len(page["tiles"]) != PAGE_SIZE:
            errors.append(f"{run_dir.relative_to(REPO_ROOT)} does not contain a 12-tile page")
        if page["stage"] != "artists" or page["page_number"] != 1:
            errors.append(f"{run_dir.relative_to(REPO_ROOT)} is not Artist Page 1")
        if len(recorded["responses"]) != len(page["tiles"]):
            errors.append(f"{run_dir.relative_to(REPO_ROOT)} response count does not match tile count")
        if survey_run["boundary_assertions"]["canonical_graph_mutated"] is not False:
            errors.append(f"{run_dir.relative_to(REPO_ROOT)} reports canonical graph mutation")
        if page["generator_visible_inputs"]["hidden_inputs_consumed"] is not False:
            errors.append(f"{run_dir.relative_to(REPO_ROOT)} page consumed hidden inputs during generation")
        intent_counts = {}
        for tile in page["tiles"]:
            intent_counts[tile["page_intent"]] = intent_counts.get(tile["page_intent"], 0) + 1
            if "active_survey_selection" not in tile["candidate_basis"]:
                errors.append(f"{run_dir.relative_to(REPO_ROOT)} tile lacks active survey selection basis")
        for intent, target in page1_intent_targets(survey_run["page_mode"]).items():
            if intent_counts.get(intent, 0) != target:
                errors.append(
                    f"{run_dir.relative_to(REPO_ROOT)} has {intent_counts.get(intent, 0)} `{intent}` tiles; expected {target}"
                )

        response_by_tile = {item["tile_id"]: item for item in recorded["responses"]}
        for lookup in coverage["lookups"]:
            response = response_by_tile.get(lookup["tile_id"])
            if response is None:
                errors.append(f"{run_dir.relative_to(REPO_ROOT)} coverage references unknown tile {lookup['tile_id']}")
                continue
            if lookup["lookup_status"] == "missing_default" and response["reaction"] != "dont_know_enough":
                errors.append(
                    f"{run_dir.relative_to(REPO_ROOT)} missing hidden lookup did not default to dont_know_enough"
                )
            if lookup["recorded_reaction"] != response["reaction"]:
                errors.append(
                    f"{run_dir.relative_to(REPO_ROOT)} coverage reaction differs from recorded response"
                )

        if survey_run["page_mode"] == "generic_graph_seed":
            if generation_log["candidate_selection"]["direct_apple_match_count"] != 0:
                errors.append(f"{run_dir.relative_to(REPO_ROOT)} graph seed used direct Apple matches")
            if load_json(run_dir / "apple_payload_used.json")["candidate_generation_application"][
                "applied_to_candidate_generation"
            ]:
                errors.append(f"{run_dir.relative_to(REPO_ROOT)} graph seed applied Apple payload")
        if survey_run["page_mode"] == "apple_biased_seed":
            direct_count = generation_log["candidate_selection"]["direct_apple_match_count"]
            payload_signature_count = intent_counts.get("payload_signature_artist", 0)
            if direct_count != payload_signature_count:
                errors.append(f"{run_dir.relative_to(REPO_ROOT)} Apple direct matches do not match payload signature target")
            non_payload_count = len(page["tiles"]) - payload_signature_count
            if non_payload_count < 8:
                errors.append(f"{run_dir.relative_to(REPO_ROOT)} Apple-biased Page 1 lacks non-payload hypothesis tests")
        errors.extend(check_page2_artifacts(run_dir, survey_run, page))
    return errors


def check_page2_artifacts(
    run_dir: Path,
    survey_run: dict[str, Any],
    page1: dict[str, Any],
) -> list[str]:
    errors = []
    page2 = load_json(run_dir / "page_002_artists.json")
    page2_log = load_json(run_dir / "page_002_generation_log.json")
    page2_debug = load_json(run_dir / "page_002_candidate_debug.json")
    recorded_page2 = load_json(run_dir / "recorded_responses_page_002.json")
    coverage_page2 = load_json(run_dir / "coverage_report_page_002.json")
    state1 = load_json(run_dir / "survey_state_after_page_001.json")
    state2 = load_json(run_dir / "survey_state_after_page_002.json")
    album_candidates = load_json(run_dir / "album_page_001_candidates.json")
    song_candidates = load_json(run_dir / "song_page_001_candidates.json")

    if state1.get("hidden_data_access") != "forbidden":
        errors.append(f"{run_dir.relative_to(REPO_ROOT)} page 1 state does not forbid hidden data")
    if state2.get("hidden_data_access") != "forbidden":
        errors.append(f"{run_dir.relative_to(REPO_ROOT)} page 2 state does not forbid hidden data")
    if state1.get("current_page_number") != 2:
        errors.append(f"{run_dir.relative_to(REPO_ROOT)} page 1 state current_page_number is not 2")
    if state2.get("current_page_number") != 3:
        errors.append(f"{run_dir.relative_to(REPO_ROOT)} page 2 state current_page_number is not 3")

    if page2.get("page_id") != "page_02" or page2.get("page_number") != 2:
        errors.append(f"{run_dir.relative_to(REPO_ROOT)} Page 2 artifact has wrong page identity")
    if page2.get("tile_count") != PAGE_SIZE or len(page2.get("tiles", [])) != PAGE_SIZE:
        errors.append(f"{run_dir.relative_to(REPO_ROOT)} Page 2 does not contain 12 tiles")
    if page2["generator_visible_inputs"].get("hidden_inputs_consumed") is not False:
        errors.append(f"{run_dir.relative_to(REPO_ROOT)} Page 2 consumed hidden inputs")
    if page2_log.get("hidden_inputs_consumed") is not False:
        errors.append(f"{run_dir.relative_to(REPO_ROOT)} Page 2 generation log consumed hidden inputs")

    target_mix = page2_log.get("target_mix", {})
    actual_mix = page2_log.get("candidate_selection", {}).get("intent_counts", {})
    if target_mix != actual_mix:
        errors.append(
            f"{run_dir.relative_to(REPO_ROOT)} Page 2 intent mix {actual_mix} does not match target {target_mix}"
        )

    seen_ids = set()
    seen_displays = set()
    family_counts: dict[str, int] = {}
    archetype_counts: dict[str, int] = {}
    response_ids = {item["response_id"] for item in load_json(run_dir / "recorded_responses.json")["responses"]}
    for tile in page2["tiles"]:
        ref = tile["music_object_ref"]
        canonical_id = ref.get("canonical_artist_id")
        display_key = ref["display_name"].casefold()
        if canonical_id in seen_ids:
            errors.append(f"{run_dir.relative_to(REPO_ROOT)} Page 2 repeats canonical artist {canonical_id}")
        if display_key in seen_displays:
            errors.append(f"{run_dir.relative_to(REPO_ROOT)} Page 2 repeats display name {ref['display_name']}")
        seen_ids.add(canonical_id)
        seen_displays.add(display_key)
        if "page_intent" not in tile:
            errors.append(f"{run_dir.relative_to(REPO_ROOT)} Page 2 tile lacks page_intent")
        if "active_survey_adaptation" not in tile.get("candidate_basis", []):
            errors.append(f"{run_dir.relative_to(REPO_ROOT)} Page 2 tile lacks active adaptation basis")
        if set(tile.get("scores", {}).keys()) != PAGE2_SCORE_KEYS:
            errors.append(f"{run_dir.relative_to(REPO_ROOT)} Page 2 tile has wrong score keys")
        if not isinstance(tile.get("response_evidence_refs"), list):
            errors.append(f"{run_dir.relative_to(REPO_ROOT)} Page 2 tile lacks response evidence refs")
        for ref_item in tile.get("response_evidence_refs", []):
            if ref_item.get("response_id") not in response_ids:
                errors.append(f"{run_dir.relative_to(REPO_ROOT)} Page 2 references unknown Page 1 response")
        if not isinstance(tile.get("suppression_warnings"), list):
            errors.append(f"{run_dir.relative_to(REPO_ROOT)} Page 2 tile lacks suppression warnings list")
        for family in tile["graph_context"]["family_numbers"]:
            family_counts[str(family)] = family_counts.get(str(family), 0) + 1
        for archetype in tile["graph_context"]["archetype_ids"]:
            archetype_counts[archetype] = archetype_counts.get(archetype, 0) + 1

    for family, count in family_counts.items():
        if count > 3 and not any(
            "adaptive_override_quota_relaxed" in tile.get("suppression_warnings", [])
            and family in {str(item) for item in tile["graph_context"]["family_numbers"]}
            for tile in page2["tiles"]
        ):
            errors.append(f"{run_dir.relative_to(REPO_ROOT)} Page 2 family {family} exceeds quota without override")
    for archetype, count in archetype_counts.items():
        if count > 2 and not any(
            "adaptive_override_quota_relaxed" in tile.get("suppression_warnings", [])
            and archetype in set(tile["graph_context"]["archetype_ids"])
            for tile in page2["tiles"]
        ):
            errors.append(f"{run_dir.relative_to(REPO_ROOT)} Page 2 archetype {archetype} exceeds quota without override")

    if len(recorded_page2.get("responses", [])) != PAGE_SIZE:
        errors.append(f"{run_dir.relative_to(REPO_ROOT)} Page 2 recorded response count is not 12")
    if coverage_page2["summary"]["tile_count"] != PAGE_SIZE:
        errors.append(f"{run_dir.relative_to(REPO_ROOT)} Page 2 coverage count is not 12")

    debug_candidates = page2_debug.get("selected_candidates", [])
    if len(debug_candidates) != PAGE_SIZE:
        errors.append(f"{run_dir.relative_to(REPO_ROOT)} Page 2 debug candidate count is not 12")
    for candidate in debug_candidates:
        if "music_object_ref" not in candidate:
            errors.append(f"{run_dir.relative_to(REPO_ROOT)} Page 2 debug candidate lacks typed ref")

    for payload, object_type, filename in [
        (album_candidates, "album", "album_page_001_candidates.json"),
        (song_candidates, "song_recording", "song_page_001_candidates.json"),
    ]:
        if "candidates" not in payload:
            errors.append(f"{(run_dir / filename).relative_to(REPO_ROOT)} lacks candidates")
            continue
        for candidate in payload["candidates"]:
            ref = candidate.get("music_object_ref", {})
            if ref.get("object_type") != object_type:
                errors.append(f"{(run_dir / filename).relative_to(REPO_ROOT)} has wrong object type candidate")
            if candidate.get("uses_object_type_roles") is not True:
                errors.append(f"{(run_dir / filename).relative_to(REPO_ROOT)} has candidate without object-role basis")
            if not candidate.get("response_evidence_refs"):
                errors.append(f"{(run_dir / filename).relative_to(REPO_ROOT)} candidate lacks response evidence refs")
            if not isinstance(candidate.get("suppression_warnings"), list):
                errors.append(f"{(run_dir / filename).relative_to(REPO_ROOT)} candidate lacks warning metadata list")
            if "graph_context" not in candidate or "roles" not in candidate["graph_context"]:
                errors.append(f"{(run_dir / filename).relative_to(REPO_ROOT)} candidate lacks graph role context")

    return errors


def check_graph_integrity() -> list[str]:
    integrity_path = SIM_DIR / "reports" / "graph_readonly_fingerprint.json"
    if not integrity_path.exists():
        return ["Missing graph readonly fingerprint report"]
    integrity = load_json(integrity_path)
    errors = []
    if not integrity.get("unchanged_during_generation"):
        errors.append("Generator recorded a canonical graph fingerprint change")
    before = integrity.get("before", {}).get("sha256")
    after = integrity.get("after", {}).get("sha256")
    if before != after:
        errors.append("Graph before/after fingerprints differ")
    return errors


def check_hidden_realism_report() -> list[str]:
    report_path = SIM_DIR / "reports" / "hidden_corpus_realism_report.md"
    if not report_path.exists():
        return ["Missing hidden corpus realism report"]
    text = report_path.read_text(encoding="utf-8")
    required_phrases = [
        "Population probability uses `1 - product(1 - contributing_rate)`",
        "| Artist Page 1 |",
        "| Artist Page 2 |",
        "| Album Page 1 pools |",
        "| Song Page 1 pools |",
        "Page 2 has enough non-null signal for selector-quality backtesting: `true`",
    ]
    errors = [
        f"Hidden corpus realism report missing phrase: {phrase}"
        for phrase in required_phrases
        if phrase not in text
    ]
    target_section = text.split("## Hidden Lookup Hit Rate by Object Type and Page", 1)[0]
    if "`review`" in target_section:
        errors.append("Hidden corpus realism target-rate section has a review status")
    return errors


def check_page_count_backtest() -> list[str]:
    backtest_dir = SIM_DIR / "page_count_backtest"
    if not backtest_dir.exists():
        return ["Missing page_count_backtest output directory"]
    present = {path.name for path in backtest_dir.iterdir() if path.is_file()}
    missing = BACKTEST_REQUIRED_FILES - present
    errors = []
    if missing:
        errors.append(f"Page count backtest missing required files: {', '.join(sorted(missing))}")
        return errors

    config_metrics = load_json(backtest_dir / "config_metrics.json")
    per_profile_metrics = load_json(backtest_dir / "per_profile_metrics.json")
    marginal = load_json(backtest_dir / "marginal_lift_by_page_type.json")
    configs = config_metrics.get("configs", [])
    profiles = per_profile_metrics.get("profiles", [])
    if len(configs) != 18:
        errors.append(f"Page count backtest expected 18 configs; found {len(configs)}")
    if len(profiles) != 180:
        errors.append(f"Page count backtest expected 180 per-profile rows; found {len(profiles)}")
    config_ids = {item.get("config_id") for item in configs}
    expected_configs = {
        f"A{artist}_Al{album}_S{song}"
        for artist in [2, 3, 4]
        for album in [1, 2]
        for song in [1, 2, 3]
    }
    if config_ids != expected_configs:
        errors.append("Page count backtest config matrix is incomplete")
    metadata = config_metrics.get("metadata", {})
    if metadata.get("hidden_inputs_used_for_page_generation") is not False:
        errors.append("Page count backtest reports hidden inputs used for page generation")
    if not metadata.get("canonical_graph_fingerprint_unchanged"):
        errors.append("Page count backtest reports canonical graph fingerprint changed")
    expected_lift_keys = {
        "artist_A2_to_A3",
        "artist_A3_to_A4",
        "album_Al1_to_Al2",
        "song_S1_to_S2",
        "song_S2_to_S3",
    }
    if set(marginal.get("marginal_lift_by_page_type", {}).keys()) != expected_lift_keys:
        errors.append("Page count backtest marginal lift keys are incomplete")

    forbidden_phrases = [
        "reason_tags",
        "hidden_reaction_corpus_id",
        "hidden_anti_affinities",
        "fake_profile_",
        "display_label",
    ]
    for path in sorted(backtest_dir.rglob("*")):
        if not path.is_file() or path.suffix not in {".json", ".md"}:
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in forbidden_phrases:
            if phrase in text:
                errors.append(f"{path.relative_to(REPO_ROOT)} contains forbidden phrase `{phrase}`")
    return errors


def check_llm_profile_review() -> list[str]:
    review_dir = SIM_DIR / "llm_profile_review"
    if not review_dir.exists():
        return ["Missing llm_profile_review output directory"]
    errors = []
    for relative_name in sorted(LLM_PROFILE_REVIEW_REQUIRED_FILES):
        if not (review_dir / relative_name).exists():
            errors.append(f"LLM profile review missing required file: {relative_name}")
    public_packet_relative = first_existing_relative_path(
        review_dir,
        LLM_PROFILE_REVIEW_PUBLIC_PACKET_CANDIDATES,
    )
    if public_packet_relative is None:
        candidates = " or ".join(LLM_PROFILE_REVIEW_PUBLIC_PACKET_CANDIDATES)
        errors.append(f"LLM profile review missing required file: {candidates}")
    if errors:
        return errors

    try:
        from jsonschema import Draft202012Validator, FormatChecker
    except ModuleNotFoundError:
        raise ValidationError(
            "Missing dependency: jsonschema. Install with "
            "`python3 -m pip install -r scripts/requirements.txt`."
        ) from None

    schema_paths = [
        review_dir / "schemas" / "profile_writer_input.schema.json",
        review_dir / "schemas" / "profile_writer_output.schema.json",
        review_dir / "schemas" / "profile_evaluator_output.schema.json",
    ]
    for schema_path in schema_paths:
        schema = load_json(schema_path)
        Draft202012Validator.check_schema(schema)

    public_packet_path = review_dir / public_packet_relative
    public_packet = load_json(public_packet_path)
    input_schema = load_json(review_dir / "schemas" / "profile_writer_input.schema.json")
    validator = Draft202012Validator(input_schema, format_checker=FormatChecker())
    for error in sorted(validator.iter_errors(public_packet), key=lambda item: list(item.path)):
        errors.append(
            f"{public_packet_path.relative_to(REPO_ROOT)} {format_path(error.path)}: {error.message}"
        )

    if public_packet.get("schema_version") != "waymark.profile_writer_input.v0.1":
        errors.append("LLM public packet has wrong schema version")
    if public_packet.get("profile_public_id") != "public_profile_01":
        errors.append("LLM public packet has wrong public profile id")
    config = public_packet.get("page_count_config", {})
    if config.get("config_id") != "A2_Al1_S1" or config.get("tile_count") != 48:
        errors.append("LLM public packet has wrong page-count config")
    blindness = public_packet.get("blindness_contract", {})
    if blindness.get("hidden_inputs_used_for_generation") is not False:
        errors.append("LLM public packet does not declare hidden generation inputs absent")
    if blindness.get("public_packet_contains_hidden_truth") is not False:
        errors.append("LLM public packet does not declare hidden truth absent")

    leaked_keys = sorted(FORBIDDEN_VISIBLE_KEYS & set(iter_keys(public_packet)))
    if leaked_keys:
        errors.append(f"LLM public packet leaks hidden/private keys: {', '.join(leaked_keys)}")

    private_phrases = [
        "Classic Suburban Dad",
        "Pop / Radio Generalist",
        "Alt Formation User",
        "Country-Pop Listener",
        "R&B / Hip-Hop Listener",
        "Theater / Family Context User",
        "Indie / Prestige Listener",
        "Metal / Heavy User",
        "Modern Pop + TikTok User",
        "Low-Library Streaming User",
        "fake_profile_",
        "hidden_corpus_",
    ]
    public_text_paths = [
        public_packet_path,
        review_dir / "api_requests" / "profile_writer_reference_request.json",
        review_dir / "api_requests" / "evaluator_evidence_only_reference_request.json",
    ]
    for path in public_text_paths:
        text = path.read_text(encoding="utf-8")
        for phrase in private_phrases:
            if phrase in text:
                errors.append(f"{path.relative_to(REPO_ROOT)} contains private phrase `{phrase}`")

    page_counts = {
        "artist": 0,
        "album": 0,
        "song": 0,
    }
    evidence_refs = set()
    tile_total = 0
    for page in public_packet.get("pages", []):
        stage = page.get("stage")
        if stage not in page_counts:
            errors.append(f"LLM public packet has unsupported stage `{stage}`")
            continue
        page_counts[stage] += 1
        if page.get("tile_count") != PAGE_SIZE or len(page.get("tiles", [])) != PAGE_SIZE:
            errors.append(f"LLM public packet page {page.get('page_id')} is not 12 tiles")
        if page.get("generator_visible_inputs", {}).get("hidden_inputs_consumed") is not False:
            errors.append(f"LLM public packet page {page.get('page_id')} consumed hidden inputs")
        for tile in page.get("tiles", []):
            tile_total += 1
            evidence_ref = tile.get("evidence_ref")
            if not evidence_ref:
                errors.append(f"LLM public packet tile lacks evidence_ref on {page.get('page_id')}")
            elif evidence_ref in evidence_refs:
                errors.append(f"LLM public packet repeats evidence_ref `{evidence_ref}`")
            evidence_refs.add(evidence_ref)
            if "music_object_ref" not in tile:
                errors.append(f"LLM public packet tile lacks music_object_ref on {page.get('page_id')}")
            if "reaction" not in tile:
                errors.append(f"LLM public packet tile lacks reaction on {page.get('page_id')}")
    if page_counts != {"artist": 2, "album": 1, "song": 1}:
        errors.append(f"LLM public packet has wrong page mix: {page_counts}")
    if tile_total != 48:
        errors.append(f"LLM public packet expected 48 tiles; found {tile_total}")

    writer_request = load_json(review_dir / "api_requests" / "profile_writer_reference_request.json")
    evaluator_request = load_json(review_dir / "api_requests" / "evaluator_evidence_only_reference_request.json")
    truth_request = load_json(review_dir / "simulator_private" / "api_requests" / "evaluator_truth_scored_reference_request.json")
    for name, request in [
        ("profile writer", writer_request),
        ("evidence-only evaluator", evaluator_request),
        ("truth-scored evaluator", truth_request),
    ]:
        text_format = request.get("text", {}).get("format", {})
        if text_format.get("type") != "json_schema" or text_format.get("strict") is not True:
            errors.append(f"LLM {name} request lacks strict structured-output format")
    if "hidden_profile_truth" in json.dumps(writer_request):
        errors.append("LLM profile writer request embeds hidden truth")
    if "hidden_profile_truth" in json.dumps(evaluator_request):
        errors.append("LLM evidence-only evaluator request embeds hidden truth")
    if "hidden_profile_truth" not in json.dumps(truth_request):
        errors.append("LLM truth-scored evaluator request lacks simulator-private hidden truth")

    hidden_truth = load_json(
        review_dir
        / "simulator_private"
        / "hidden_truth_packets"
        / "hidden_truth_public_profile_01_A2_Al1_S1.json"
    )
    if hidden_truth.get("not_allowed_for_profile_writer") is not True:
        errors.append("LLM hidden truth packet does not block Profile Writer use")
    hidden_truth_text = json.dumps(hidden_truth)
    if "reason_tags" in hidden_truth_text and "reason_tags removed" not in hidden_truth_text:
        errors.append("LLM hidden truth packet includes hidden reason tags")
    if "lookup_status" in hidden_truth_text:
        errors.append("LLM hidden truth packet includes lookup status")
    if hidden_truth.get("heldout_populated_reaction_count", 0) <= 0:
        errors.append("LLM hidden truth packet lacks held-out reactions")

    pilot_metadata_path = review_dir / "api_pilot" / "api_pilot_execution_metadata.json"
    if pilot_metadata_path.exists():
        pilot_metadata = load_json(pilot_metadata_path)
        if pilot_metadata.get("model_id") != "gpt-5.5":
            errors.append("LLM API pilot metadata does not record model gpt-5.5")
        status = pilot_metadata.get("status")
        if status not in {"blocked", "failed", "completed"}:
            errors.append(f"LLM API pilot metadata has invalid status `{status}`")
        call_counts = pilot_metadata.get("call_counts", {})
        if call_counts.get("profile_writer", 0) > 1:
            errors.append("LLM API pilot made more than one Profile Writer call")
        if call_counts.get("evaluator_evidence_only", 0) > 1:
            errors.append("LLM API pilot made more than one evidence-only Evaluator call")
        if call_counts.get("evaluator_truth_scored", 0) > 1:
            errors.append("LLM API pilot made more than one truth-scored Evaluator call")
        if status == "completed":
            response_paths = pilot_metadata.get("response_paths", {})
            required_response_paths = {
                "profile_writer_output",
                "evaluator_evidence_only_output",
                "evaluator_truth_scored_output",
            }
            if set(response_paths) != required_response_paths:
                errors.append("Completed LLM API pilot does not record all response paths")
            for key, relative_path in response_paths.items():
                path = REPO_ROOT / relative_path
                if not path.exists():
                    errors.append(f"Completed LLM API pilot missing response path for {key}: {relative_path}")
            validation_status = pilot_metadata.get("validation_status", {})
            for key in [
                "profile_writer_output",
                "evaluator_evidence_only_output",
                "evaluator_truth_scored_output",
                "blind_boundary",
            ]:
                if validation_status.get(key) != "passed":
                    errors.append(f"Completed LLM API pilot did not pass validation `{key}`")

    return errors


def check_llm_profile_review_3x3() -> list[str]:
    pilot_dir = SIM_DIR / "llm_profile_review" / "api_pilot_3x3"
    if not pilot_dir.exists():
        return []
    errors = []
    metadata_path = pilot_dir / "api_pilot_3x3_execution_metadata.json"
    report_path = SIM_DIR / "llm_profile_review" / "reports" / "api_pilot_3x3_execution_report.md"
    if not metadata_path.exists():
        return ["3x3 LLM API pilot missing execution metadata"]
    if not report_path.exists():
        errors.append("3x3 LLM API pilot missing execution report")
    metadata = load_json(metadata_path)
    if metadata.get("status") != "completed":
        errors.append(f"3x3 LLM API pilot status is not completed: {metadata.get('status')}")
    if metadata.get("model_id") != "gpt-5.5":
        errors.append("3x3 LLM API pilot metadata does not record model gpt-5.5")
    if metadata.get("scope", {}).get("full_180_call_batch_run") is not False:
        errors.append("3x3 LLM API pilot reports full batch execution")

    call_counts = metadata.get("call_counts", {})
    expected_call_counts = {
        "profile_writer": 9,
        "evaluator_evidence_only": 9,
        "evaluator_truth_scored": 9,
    }
    if call_counts != expected_call_counts:
        errors.append(f"3x3 LLM API pilot call counts are {call_counts}; expected {expected_call_counts}")

    rows = metadata.get("rows", [])
    if len(rows) != 9:
        errors.append(f"3x3 LLM API pilot expected 9 rows; found {len(rows)}")
    profile_ids = {row.get("profile_public_id") for row in rows}
    if profile_ids != {"public_profile_01", "public_profile_05", "public_profile_06"}:
        errors.append(f"3x3 LLM API pilot has unexpected profiles: {sorted(profile_ids)}")
    config_ids = {row.get("config_id") for row in rows}
    if config_ids != {"A2_Al1_S1", "A3_Al1_S2", "A4_Al2_S3"}:
        errors.append(f"3x3 LLM API pilot has unexpected configs: {sorted(config_ids)}")

    aggregate = metadata.get("aggregate", {})
    if aggregate.get("gate_passed") is not True:
        errors.append("3x3 LLM API pilot did not pass aggregate gate")
    scores = aggregate.get("scores", {})
    if scores.get("average_all_evaluators", 0) < 85:
        errors.append("3x3 LLM API pilot average evaluator score is below 85")
    issue_counts = aggregate.get("issue_counts", {})
    if issue_counts.get("hidden_context_leakage_count") != 0:
        errors.append("3x3 LLM API pilot has hidden-context leakage")
    if issue_counts.get("blocking_red_flag_count") != 0:
        errors.append("3x3 LLM API pilot has blocking red flags")
    for key in [
        "genre_shorthand_issue_count",
        "direct_contextual_counterevidence_issue_count",
        "secondary_lane_underdevelopment_count",
    ]:
        if key not in issue_counts:
            errors.append(f"3x3 LLM API pilot does not track {key}")

    writer_schema = SIM_DIR / "llm_profile_review" / "schemas" / "profile_writer_output.schema.json"
    evaluator_schema = SIM_DIR / "llm_profile_review" / "schemas" / "profile_evaluator_output.schema.json"
    private_phrases = [
        "Classic Suburban Dad",
        "R&B / Hip-Hop Listener",
        "Theater / Family Context User",
        "fake_profile_",
        "hidden_corpus_",
        "hidden_profile_truth",
        "primary_archetype_affinities",
        "secondary_archetype_affinities",
        "hidden_anti_affinities",
        "display_label",
    ]
    for row in rows:
        for key, schema in [
            ("profile_writer_output_path", writer_schema),
            ("evidence_output_path", evaluator_schema),
            ("truth_output_path", evaluator_schema),
        ]:
            relative_path = row.get(key)
            if not relative_path:
                errors.append(f"3x3 row {row.get('profile_public_id')} {row.get('config_id')} lacks {key}")
                continue
            path = REPO_ROOT / relative_path
            if not path.exists():
                errors.append(f"3x3 row output missing: {relative_path}")
                continue
            errors.extend(validate_schema(schema, path))

        public_packet_paths = [
            pilot_dir
            / "public_packets"
            / f"cartenza_survey_output_packet_{row.get('profile_public_id')}_{row.get('config_id')}.json",
            pilot_dir
            / "public_packets"
            / f"waymark_survey_output_packet_{row.get('profile_public_id')}_{row.get('config_id')}.json",
        ]
        public_packet_path = first_existing_path(public_packet_paths)
        if not public_packet_path.exists():
            candidates = " or ".join(str(path.relative_to(REPO_ROOT)) for path in public_packet_paths)
            errors.append(f"3x3 public packet missing: {candidates}")
        else:
            public_packet = load_json(public_packet_path)
            if public_packet.get("blindness_contract", {}).get("public_packet_contains_hidden_truth") is not False:
                errors.append(f"3x3 public packet contains hidden truth: {public_packet_path.relative_to(REPO_ROOT)}")
            if public_packet.get("blindness_contract", {}).get("hidden_inputs_used_for_generation") is not False:
                errors.append(f"3x3 public packet used hidden generation inputs: {public_packet_path.relative_to(REPO_ROOT)}")
            leaked_keys = sorted(FORBIDDEN_VISIBLE_KEYS & set(iter_keys(public_packet)))
            if leaked_keys:
                errors.append(
                    f"{public_packet_path.relative_to(REPO_ROOT)} leaks hidden/private keys: {', '.join(leaked_keys)}"
                )
            public_text = public_packet_path.read_text(encoding="utf-8")
            for phrase in private_phrases:
                if phrase in public_text:
                    errors.append(f"{public_packet_path.relative_to(REPO_ROOT)} contains private phrase `{phrase}`")

        writer_request_path = (
            pilot_dir
            / "executed_requests"
            / f"profile_writer_request_{row.get('profile_public_id')}_{row.get('config_id')}.json"
        )
        evidence_request_path = (
            pilot_dir
            / "executed_requests"
            / f"evaluator_evidence_only_request_{row.get('profile_public_id')}_{row.get('config_id')}.json"
        )
        truth_request_path = (
            pilot_dir
            / "executed_requests"
            / f"evaluator_truth_scored_request_{row.get('profile_public_id')}_{row.get('config_id')}.json"
        )
        for path in [writer_request_path, evidence_request_path, truth_request_path]:
            if not path.exists():
                errors.append(f"3x3 request missing: {path.relative_to(REPO_ROOT)}")
                continue
            request = load_json(path)
            text_format = request.get("text", {}).get("format", {})
            if text_format.get("type") != "json_schema" or text_format.get("strict") is not True:
                errors.append(f"3x3 request lacks strict structured-output format: {path.relative_to(REPO_ROOT)}")
        for path in [writer_request_path, evidence_request_path]:
            if path.exists() and "hidden_profile_truth" in path.read_text(encoding="utf-8"):
                errors.append(f"{path.relative_to(REPO_ROOT)} embeds hidden truth")
        if truth_request_path.exists() and "hidden_profile_truth" not in truth_request_path.read_text(encoding="utf-8"):
            errors.append(f"{truth_request_path.relative_to(REPO_ROOT)} lacks simulator-private hidden truth")

    return errors


def check_survey_evidence_export() -> list[str]:
    export_dir = SIM_DIR / "survey_evidence_export"
    if not export_dir.exists():
        return ["Missing survey_evidence_export output directory"]
    errors = []
    for relative_name in sorted(SURVEY_EVIDENCE_EXPORT_REQUIRED_FILES):
        if not (export_dir / relative_name).exists():
            errors.append(f"Survey Evidence Export missing required file: {relative_name}")
    if errors:
        return errors

    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    try:
        from validate_survey_evidence_export_v0_1 import validate_export
        from validate_alpha_survey_output_v0_1 import validate as validate_alpha_survey_output
    finally:
        try:
            sys.path.remove(str(REPO_ROOT / "scripts"))
        except ValueError:
            pass

    for sample_path in sorted((export_dir / "samples").glob("*_survey_evidence_export.json")):
        export_errors = validate_export(
            sample_path,
            export_dir / "survey_evidence_export_v0_1.schema.json",
        )
        errors.extend(f"Survey Evidence Export {sample_path.name}: {error}" for error in export_errors)
        if "_A4_Al2_S4_" in sample_path.name:
            export = load_json(sample_path)
            atoms = export.get("atlas_ingestable", {}).get("evidence_atoms", [])
            pages_by_stage: dict[str, set[int]] = {"artist": set(), "album": set(), "song": set()}
            for atom in atoms:
                context = atom.get("page_context", {})
                stage = context.get("stage")
                if stage in pages_by_stage:
                    pages_by_stage[stage].add(context.get("page_number"))
            page_counts = {stage: len(numbers) for stage, numbers in pages_by_stage.items()}
            if page_counts != {"artist": 4, "album": 2, "song": 4}:
                errors.append(f"Survey Evidence Export {sample_path.name}: wrong fixed-intake page mix {page_counts}")
            if len(atoms) != 120:
                errors.append(f"Survey Evidence Export {sample_path.name}: expected 120 atoms; found {len(atoms)}")
    alpha_handoff_dir = export_dir / "alpha_fast_survey_app_handoff"
    alpha_errors = validate_alpha_survey_output(
        alpha_handoff_dir / "public_profile_01_A2_Al1_S1_alpha_survey_page_packet.json",
        alpha_handoff_dir / "alpha_survey_page_packet_v0_1.schema.json",
        alpha_handoff_dir / "public_profile_01_A2_Al1_S1_survey_evidence_export.json",
    )
    errors.extend(f"Alpha Survey Output: {error}" for error in alpha_errors)
    alpha1_dir = export_dir / "alpha1_required_intake"
    alpha1_page_packet = alpha1_dir / "public_profile_01_A4_Al2_S4_alpha1_survey_page_packet.json"
    alpha1_evidence_export = alpha1_dir / "public_profile_01_A4_Al2_S4_survey_evidence_export.json"
    alpha1_errors = validate_alpha_survey_output(
        alpha1_page_packet,
        alpha_handoff_dir / "alpha_survey_page_packet_v0_1.schema.json",
        alpha1_evidence_export,
    )
    errors.extend(f"Alpha 1 Required Intake Survey Output: {error}" for error in alpha1_errors)
    errors.extend(
        f"Alpha 1 Required Intake Evidence Export: {error}"
        for error in validate_export(
            alpha1_evidence_export,
            export_dir / "survey_evidence_export_v0_1.schema.json",
        )
    )

    alpha1_packet = load_json(alpha1_page_packet)
    recommendation = alpha1_packet.get("page_count_recommendation", {})
    expected_recommendation = {
        "config_id": "A4_Al2_S4",
        "artist_pages": 4,
        "album_pages": 2,
        "song_pages": 4,
        "tile_count": 120,
        "alpha_status": "required_alpha1_intake",
    }
    for key, expected in expected_recommendation.items():
        if recommendation.get(key) != expected:
            errors.append(
                f"Alpha 1 Required Intake page_count_recommendation.{key} is "
                f"{recommendation.get(key)!r}; expected {expected!r}"
            )
    stage_counts = {"artist": 0, "album": 0, "song": 0}
    tile_count = 0
    for page in alpha1_packet.get("pages", []):
        stage = page.get("stage")
        if stage in stage_counts:
            stage_counts[stage] += 1
        else:
            errors.append(f"Alpha 1 Required Intake has unsupported stage `{stage}`")
        tiles = page.get("tiles", [])
        tile_count += len(tiles)
        if len(tiles) != PAGE_SIZE:
            errors.append(f"Alpha 1 Required Intake page {page.get('page_id')} is not 12 tiles")
    if stage_counts != {"artist": 4, "album": 2, "song": 4}:
        errors.append(f"Alpha 1 Required Intake has wrong page mix: {stage_counts}")
    if tile_count != 120:
        errors.append(f"Alpha 1 Required Intake expected 120 tiles; found {tile_count}")

    alpha1_ingestion_manifest = (
        REPO_ROOT
        / "data/atlas_schema/ingestion_proof/alpha1_required_intake_survey_evidence_export_v0_1/manifest.json"
    )
    if not alpha1_ingestion_manifest.exists():
        errors.append(
            "Alpha 1 Required Intake missing Atlas ingestion proof manifest: "
            f"{alpha1_ingestion_manifest.relative_to(REPO_ROOT)}"
        )
    else:
        manifest = load_json(alpha1_ingestion_manifest)
        profile_statuses = {profile.get("status") for profile in manifest.get("profiles", [])}
        if profile_statuses != {"pass"}:
            errors.append(
                "Alpha 1 Required Intake Atlas ingestion proof did not pass for every profile: "
                f"{sorted(profile_statuses)}"
            )
        if manifest.get("input_dir") != "data/survey_simulation/survey_evidence_export/alpha1_required_intake":
            errors.append("Alpha 1 Required Intake Atlas ingestion proof has wrong source input dir")
        if manifest.get("profile_count") != 1:
            errors.append("Alpha 1 Required Intake Atlas ingestion proof should contain exactly one profile")
        if manifest.get("required_flow") != [
            "Survey Evidence Export",
            "Signal",
            "AtlasNode",
            "provisional AtlasRoleAssignment",
            "PossibleAtlasUpdateCandidate",
            "AtlasDigestView",
        ]:
            errors.append("Alpha 1 Required Intake Atlas ingestion proof has wrong required flow")
    for example_path in sorted((alpha_handoff_dir / "examples").glob("*alpha_survey*packet.json")):
        schema_errors = validate_schema(
            alpha_handoff_dir / "alpha_survey_page_packet_v0_1.schema.json",
            example_path,
        )
        errors.extend(f"Alpha Survey example {example_path.name}: {error}" for error in schema_errors)
    return errors


def validate(root: Path) -> list[str]:
    errors = []
    if not root.exists():
        return [f"Missing survey simulation directory: {root}"]

    profile_files = sorted((root / "fake_profiles").glob("*.json"))
    apple_payload_files = sorted((root / "apple_payloads").glob("*.json"))
    hidden_corpus_files = sorted((root / "hidden_reaction_corpora").glob("*.json"))
    run_dirs = sorted(
        path
        for path in (root / "runs").iterdir()
        if path.is_dir() and (path / "survey_run.json").exists()
    )
    run_json_files = [path / "survey_run.json" for path in run_dirs]
    recorded_files = [path / "recorded_responses.json" for path in run_dirs]
    page_log_files = [path / "page_generation_log.json" for path in run_dirs]
    coverage_files = [path / "hidden_lookup_coverage.json" for path in run_dirs]

    schema_checks = [
        ("fake_profile.schema.json", profile_files),
        ("apple_payload.schema.json", apple_payload_files),
        ("hidden_reaction_corpus.schema.json", hidden_corpus_files),
        ("survey_run.schema.json", run_json_files),
        ("recorded_responses.schema.json", recorded_files),
        ("page_generation_log.schema.json", page_log_files),
        ("hidden_lookup_coverage.schema.json", coverage_files),
    ]
    for schema_name, files in schema_checks:
        errors.extend(validate_schema_group(schema_name, files))

    errors.extend(check_profile_fixtures(profile_files, apple_payload_files, hidden_corpus_files))
    errors.extend(check_run_artifacts(run_dirs))
    errors.extend(check_visible_data_boundaries(run_dirs))
    errors.extend(check_graph_integrity())
    errors.extend(check_hidden_realism_report())
    errors.extend(check_page_count_backtest())
    errors.extend(check_llm_profile_review())
    errors.extend(check_llm_profile_review_3x3())
    errors.extend(check_survey_evidence_export())

    graph_keys = load_graph_keysets()
    json_paths = [
        *profile_files,
        *apple_payload_files,
        *hidden_corpus_files,
        *run_json_files,
        *recorded_files,
        *page_log_files,
        *coverage_files,
        first_existing_path(
            [
                root
                / "llm_profile_review"
                / "public_packets"
                / "cartenza_survey_output_packet_public_profile_01_A2_Al1_S1.json",
                root
                / "llm_profile_review"
                / "public_packets"
                / "waymark_survey_output_packet_public_profile_01_A2_Al1_S1.json",
            ]
        ),
        root
        / "llm_profile_review"
        / "simulator_private"
        / "hidden_truth_packets"
        / "hidden_truth_public_profile_01_A2_Al1_S1.json",
        root
        / "survey_evidence_export"
        / "alpha1_required_intake"
        / "waymark_survey_output_packet_public_profile_01_A4_Al2_S4_alpha1_intake.json",
        root
        / "survey_evidence_export"
        / "alpha1_required_intake"
        / "public_profile_01_A4_Al2_S4_alpha1_survey_page_packet.json",
        root
        / "survey_evidence_export"
        / "alpha1_required_intake"
        / "public_profile_01_A4_Al2_S4_survey_evidence_export.json",
    ]
    for path in json_paths:
        errors.extend(validate_typed_refs(load_json(path), path, graph_keys))

    if len(run_dirs) != 20:
        errors.append(f"Expected 20 first-slice Page 1 runs; found {len(run_dirs)}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Survey Simulation Harness v0.1.")
    parser.add_argument(
        "--root",
        type=Path,
        default=SIM_DIR,
        help="Survey simulation root directory.",
    )
    args = parser.parse_args()

    try:
        errors = validate(args.root)
    except ValidationError as error:
        print(f"INVALID: {error}", file=sys.stderr)
        return 2

    if errors:
        print(f"INVALID: survey simulation failed {len(errors)} check(s)")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"OK: survey simulation validates at {args.root.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
