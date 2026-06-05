#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import warnings
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_DIR = REPO_ROOT / "data/product_contracts/mission_opportunity_selection_v0_1"
SCHEMA_DIR = CONTRACT_DIR / "schemas"
FIXTURE_DIR = CONTRACT_DIR / "fixtures"
NEGATIVE_FIXTURE_DIR = FIXTURE_DIR / "negative"
TYPE_DIR = CONTRACT_DIR / "types"

REGISTRY_SCHEMA = SCHEMA_DIR / "mission_type_registry_v0_1.schema.json"
EVIDENCE_SCHEMA = SCHEMA_DIR / "evidence_rollup_v0_1.schema.json"
OPPORTUNITY_SCHEMA = SCHEMA_DIR / "mission_opportunity_blob_v0_1.schema.json"
SELECTOR_SCHEMA = SCHEMA_DIR / "selector_output_v0_1.schema.json"
HIDDEN_ORACLE_EVALUATION_SCHEMA = (
    SCHEMA_DIR / "hidden_oracle_evaluation_design_v0_1.schema.json"
)
RANK_USEFULNESS_ANALYSIS_SCHEMA = (
    SCHEMA_DIR / "hidden_oracle_rank_usefulness_analysis_v0_1.schema.json"
)

REGISTRY_FIXTURE = FIXTURE_DIR / "mission_type_registry_sample_v0_1.json"
EVIDENCE_FIXTURE = FIXTURE_DIR / "evidence_rollup_sample_v0_1.json"
OPPORTUNITY_FIXTURE = FIXTURE_DIR / "mission_opportunity_blob_sample_v0_1.json"
SELECTOR_FIXTURE = FIXTURE_DIR / "selector_output_sample_v0_1.json"
SCENARIO_FIXTURE = FIXTURE_DIR / "synthetic_selector_scenarios_v0_1.json"
PROTOTYPE_SELECTOR_FIXTURE = FIXTURE_DIR / "prototype_selector_output_synthetic_v0_1.json"
PROTOTYPE_EARLY_STOP_FIXTURE = FIXTURE_DIR / "prototype_selector_output_early_stop_synthetic_v0_1.json"
PROFILE_SIM_DIR = FIXTURE_DIR / "profile_simulation"
PROFILE_VISIBLE_INPUTS = PROFILE_SIM_DIR / "visible_profile_selector_inputs_v0_1.json"
PROFILE_HIDDEN_ORACLES = PROFILE_SIM_DIR / "hidden_profile_oracles_v0_1.json"
PROFILE_PHASE1_SUMMARY = PROFILE_SIM_DIR / "profile_selector_phase1_summary_v0_1.json"
HIDDEN_ORACLE_EVALUATION_FIXTURE = (
    PROFILE_SIM_DIR / "hidden_oracle_evaluation_design_v0_1.json"
)
RANK_USEFULNESS_ANALYSIS_FIXTURE = (
    PROFILE_SIM_DIR / "hidden_oracle_rank_usefulness_analysis_v0_1.json"
)
PHASE1E_DIR = CONTRACT_DIR / "evaluations/phase1e_expanded_visible_evidence_scale"
PHASE1E_EXPANDED_VISIBLE = PHASE1E_DIR / "expanded_visible_profile_inputs_v0_1.json"
PHASE1E_RANK_USEFULNESS = PHASE1E_DIR / "hidden_oracle_rank_usefulness_by_profile_scale_v0_1.json"
PHASE1E_SUMMARY_JSON = PHASE1E_DIR / "expanded_visible_evidence_scale_summary_v0_1.json"
PHASE1E_SUMMARY_MD = PHASE1E_DIR / "expanded_visible_evidence_scale_summary_v0_1.md"
PHASE1E_SELECTOR_OUTPUT_DIR = PHASE1E_DIR / "selector_outputs_by_profile_scale"
PHASE1E_NEGATIVE_DIR = PHASE1E_DIR / "negative"
PHASE1F_DIR = CONTRACT_DIR / "evaluations/phase1f_song_pack_smell_test"
PHASE1F_SCHEMA = PHASE1F_DIR / "song_pack_simulation_schema_v0_1.schema.json"
PHASE1F_RESULTS = PHASE1F_DIR / "song_pack_simulation_results_v0_1.json"
PHASE1F_SUMMARY_MD = PHASE1F_DIR / "song_pack_simulation_summary_v0_1.md"
PHASE1F_GUARDRAIL_MD = PHASE1F_DIR / "song_pack_simulation_guardrail_report_v0_1.md"
PHASE1F_NEGATIVE_DIR = PHASE1F_DIR / "negative"
PHASE1G_DIR = CONTRACT_DIR / "evaluations/phase1g_construction_policy_llm_review"
PHASE1G_SCHEMA = PHASE1G_DIR / "phase1g_song_pack_schema_v0_1.schema.json"
PHASE1G_RESULTS = PHASE1G_DIR / "phase1g_song_pack_results_v0_1.json"
PHASE1G_SUMMARY_MD = PHASE1G_DIR / "phase1g_song_pack_summary_v0_1.md"
PHASE1G_GUARDRAIL_MD = PHASE1G_DIR / "phase1g_guardrail_report_v0_1.md"
PHASE1G_LLM_PACKET_JSON = PHASE1G_DIR / "llm_sanity_review_packet_v0_1.json"
PHASE1G_LLM_PACKET_MD = PHASE1G_DIR / "llm_sanity_review_packet_v0_1.md"
PHASE1G_NEGATIVE_DIR = PHASE1G_DIR / "negative"
PROFILE_SELECTOR_OUTPUTS = [
    PROFILE_SIM_DIR / "public_profile_01_selector_output_v0_1.json",
    PROFILE_SIM_DIR / "public_profile_05_selector_output_v0_1.json",
    PROFILE_SIM_DIR / "public_profile_06_selector_output_v0_1.json",
]

EXPECTED_MISSION_TYPES = [
    "initial_profile_survey",
    "family_survey",
    "archetype_survey",
    "gateway_test",
    "song_to_archetype_test",
    "artist_depth_test",
    "album_container_test",
    "archetype_depth_test",
    "exception_scope_test",
    "false_nearby_test",
    "context_dependence_test",
    "bridge_test",
    "boundary_test",
    "evidence_repair_test",
]

FORBIDDEN_CONTENT_KEYS = {
    "mission_content",
    "mission_items",
    "mission_title",
    "mission_description",
    "playlist",
    "playback_plan",
    "catalog_resolution",
    "runtime_lifecycle",
    "production_mission",
    "final_mission",
    "final_mission_copy",
    "final_mission_content",
    "mission_tracks",
    "render_payload",
    "candidate_song_ids",
    "candidate_songs",
    "candidate_song_list",
    "song_candidate_refs",
}

FORBIDDEN_LABEL_TOKENS = {
    "personal_mapping",
    "personal_label",
    "private_label",
    "assigned_personal_role",
}

BLOCKED_FALSE_KEYS = {
    "runtime_allowed",
    "runtime_listener_evidence_connected",
    "production_mission_generation_allowed",
    "production_generation_allowed",
    "canonical_graph_mutation_allowed",
    "runtime_listener_evidence_connected",
    "listener_preference_inference_from_affinity_allowed",
    "selector_may_read_hidden_oracle",
}

TYPE_FILES = [
    TYPE_DIR / "mission_type_registry_v0_1.ts",
    TYPE_DIR / "evidence_rollup_v0_1.ts",
    TYPE_DIR / "mission_opportunity_blob_v0_1.ts",
    TYPE_DIR / "selector_output_v0_1.ts",
    TYPE_DIR / "hidden_oracle_evaluation_design_v0_1.ts",
    TYPE_DIR / "hidden_oracle_rank_usefulness_analysis_v0_1.ts",
    TYPE_DIR / "index.ts",
]

NEGATIVE_CASES = [
    (
        "survey ok cannot count as signal",
        EVIDENCE_SCHEMA,
        NEGATIVE_FIXTURE_DIR / "survey_ok_counts_as_signal_evidence_rollup_v0_1.json",
    ),
    (
        "mission ok must be weak evidence",
        EVIDENCE_SCHEMA,
        NEGATIVE_FIXTURE_DIR / "mission_ok_not_weak_evidence_rollup_v0_1.json",
    ),
    (
        "unsupported mission type rejected",
        SELECTOR_SCHEMA,
        NEGATIVE_FIXTURE_DIR / "unsupported_mission_type_selector_output_v0_1.json",
    ),
    (
        "runtime flags remain false",
        SELECTOR_SCHEMA,
        NEGATIVE_FIXTURE_DIR / "runtime_flags_enabled_selector_output_v0_1.json",
    ),
    (
        "production mission generation remains blocked",
        SELECTOR_SCHEMA,
        NEGATIVE_FIXTURE_DIR / "production_generation_enabled_selector_output_v0_1.json",
    ),
    (
        "selector output contains no mission content",
        SELECTOR_SCHEMA,
        NEGATIVE_FIXTURE_DIR / "selector_output_contains_mission_content_v0_1.json",
    ),
    (
        "graph context required for opportunity blobs",
        OPPORTUNITY_SCHEMA,
        NEGATIVE_FIXTURE_DIR / "missing_graph_context_opportunity_v0_1.json",
    ),
]


@dataclass
class ValidationResult:
    passes: list[str] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)

    def pass_(self, message: str) -> None:
        self.passes.append(message)

    def fail(self, message: str) -> None:
        self.failures.append(message)

    @property
    def ok(self) -> bool:
        return not self.failures


def load_json(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        raise SystemExit(f"File not found: {path}") from None
    except json.JSONDecodeError as error:
        raise SystemExit(f"Invalid JSON in {path}: {error}") from None


def format_path(path_parts: Iterable[object]) -> str:
    parts = [str(part) for part in path_parts]
    return "/" + "/".join(parts) if parts else "/"


def jsonschema_tools() -> tuple[Any, Any, Any] | tuple[None, None, None]:
    try:
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                message="jsonschema.RefResolver is deprecated.*",
                category=DeprecationWarning,
            )
            from jsonschema import Draft202012Validator, FormatChecker, RefResolver
    except ModuleNotFoundError:
        return None, None, None
    return Draft202012Validator, FormatChecker, RefResolver


def load_schema_store() -> dict[str, Any]:
    schemas = [
        REGISTRY_SCHEMA,
        EVIDENCE_SCHEMA,
        OPPORTUNITY_SCHEMA,
        SELECTOR_SCHEMA,
        HIDDEN_ORACLE_EVALUATION_SCHEMA,
        RANK_USEFULNESS_ANALYSIS_SCHEMA,
        PHASE1F_SCHEMA,
        PHASE1G_SCHEMA,
    ]
    store: dict[str, Any] = {}
    for schema_path in schemas:
        schema = load_json(schema_path)
        schema_id = schema.get("$id")
        if isinstance(schema_id, str):
            store[schema_id] = schema
        store[schema_path.name] = schema
    return store


def schema_errors(schema_path: Path, document: Any) -> list[str]:
    Draft202012Validator, FormatChecker, RefResolver = jsonschema_tools()
    if Draft202012Validator is None or FormatChecker is None or RefResolver is None:
        return [
            "jsonschema is required. Use `.venv/bin/python` or install "
            "`jsonschema` in the active Python environment."
        ]

    schema = load_json(schema_path)
    store = load_schema_store()
    try:
        Draft202012Validator.check_schema(schema)
    except Exception as error:
        return [f"schema is invalid: {error}"]

    resolver = RefResolver.from_schema(schema, store=store)
    validator = Draft202012Validator(
        schema,
        format_checker=FormatChecker(),
        resolver=resolver,
    )
    return [
        f"{format_path(error.path)}: {error.message}"
        for error in sorted(validator.iter_errors(document), key=lambda item: list(item.path))
    ]


def validate_json_schema(
    schema_path: Path,
    document_path: Path,
    label: str,
    result: ValidationResult,
) -> Any:
    document = load_json(document_path)
    errors = schema_errors(schema_path, document)
    if errors:
        for error in errors:
            result.fail(f"{label} schema {error}")
    else:
        result.pass_(f"{label} JSON Schema validation passed")
    return document


def expect_schema_failure(
    label: str,
    schema_path: Path,
    document_path: Path,
    result: ValidationResult,
) -> None:
    errors = schema_errors(schema_path, load_json(document_path))
    if errors:
        result.pass_(f"negative fixture rejected: {label}")
    else:
        result.fail(f"negative fixture unexpectedly passed: {label}")


def iter_dict_items(value: Any, path: str = "") -> Iterable[tuple[str, Any, str]]:
    if isinstance(value, dict):
        for key, child in value.items():
            pointer = f"{path}/{key}" if path else f"/{key}"
            yield key, child, pointer
            yield from iter_dict_items(child, pointer)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from iter_dict_items(child, f"{path}/{index}" if path else f"/{index}")


def expect_false_flags(value: Any, result: ValidationResult, label: str) -> None:
    for key, child, pointer in iter_dict_items(value):
        if key in BLOCKED_FALSE_KEYS and child is not False:
            result.fail(f"{label} {pointer} must be false")


def expect_no_forbidden_content_keys(value: Any, result: ValidationResult, label: str) -> None:
    for key, _child, pointer in iter_dict_items(value):
        if key in FORBIDDEN_CONTENT_KEYS:
            result.fail(f"{label} includes forbidden production mission field {pointer}")


def expect_no_personal_private_labels(value: Any, result: ValidationResult, label: str) -> None:
    for key, child, pointer in iter_dict_items(value):
        key_text = str(key).lower()
        if any(token in key_text for token in FORBIDDEN_LABEL_TOKENS):
            result.fail(f"{label} includes forbidden label key {pointer}")
        if isinstance(child, str):
            child_text = child.lower()
            if any(token in child_text for token in FORBIDDEN_LABEL_TOKENS):
                result.fail(f"{label} includes forbidden label token at {pointer}")


def expect_exact(value: Any, expected: Any, pointer: str, result: ValidationResult) -> None:
    if value != expected:
        result.fail(f"{pointer} must be {expected!r}; got {value!r}")


def validate_registry_domain(registry: dict[str, Any], result: ValidationResult) -> None:
    expect_exact(registry.get("global_top_k_opportunities"), 25, "/global_top_k_opportunities", result)
    expect_false_flags(registry, result, "registry")
    expect_no_forbidden_content_keys(registry, result, "registry")
    expect_no_personal_private_labels(registry, result, "registry")

    mission_types = registry.get("mission_types", [])
    mission_type_names = [entry.get("mission_type") for entry in mission_types if isinstance(entry, dict)]
    if mission_type_names != EXPECTED_MISSION_TYPES:
        result.fail("/mission_types must match the approved v0.1 mission type set in order")

    if len(set(mission_type_names)) != len(mission_type_names):
        result.fail("/mission_types contains duplicate mission_type values")

    by_band: dict[str, list[dict[str, Any]]] = {}
    for entry in mission_types:
        if not isinstance(entry, dict):
            continue
        floor = entry.get("score_floor")
        ceiling = entry.get("score_ceiling")
        if isinstance(floor, (int, float)) and isinstance(ceiling, (int, float)) and floor > ceiling:
            result.fail(f"{entry.get('mission_type')} score_floor must be <= score_ceiling")
        by_band.setdefault(str(entry.get("value_band")), []).append(entry)

    band_order = ["low", "lower_medium", "medium", "high", "very_high"]
    for index, band in enumerate(band_order[:-2]):
        lower_ceiling = max(
            (entry["score_ceiling"] for entry in by_band.get(band, []) if "score_ceiling" in entry),
            default=None,
        )
        upper_floor = min(
            (
                entry["score_floor"]
                for entry in by_band.get(band_order[index + 2], [])
                if "score_floor" in entry
            ),
            default=None,
        )
        if lower_ceiling is not None and upper_floor is not None and lower_ceiling > upper_floor:
            result.fail(
                f"{band} ceiling {lower_ceiling} cannot exceed "
                f"{band_order[index + 2]} floor {upper_floor}"
            )

    if result.ok:
        result.pass_("registry domain gates passed")


def validate_evidence_domain(evidence: dict[str, Any], result: ValidationResult) -> None:
    expect_false_flags(evidence, result, "evidence")
    expect_no_forbidden_content_keys(evidence, result, "evidence")
    expect_no_personal_private_labels(evidence, result, "evidence")

    signals = evidence.get("evidence_signals", [])
    saw_survey_ok = False
    saw_mission_ok = False

    for index, signal in enumerate(signals):
        if not isinstance(signal, dict):
            continue
        source_type = signal.get("source_type")
        raw_signal = signal.get("raw_signal")
        pointer = f"/evidence_signals/{index}"

        if source_type == "survey" and raw_signal == "ok":
            saw_survey_ok = True
            expect_exact(signal.get("signal_class"), "no_signal", f"{pointer}/signal_class", result)
            expect_exact(signal.get("signal_weight"), 0, f"{pointer}/signal_weight", result)
            expect_exact(
                signal.get("contributes_to_preference"),
                False,
                f"{pointer}/contributes_to_preference",
                result,
            )
            expect_exact(
                signal.get("can_support_non_failure"),
                False,
                f"{pointer}/can_support_non_failure",
                result,
            )

        if source_type in {"mission_review", "song_review"} and raw_signal == "ok":
            saw_mission_ok = True
            expect_exact(signal.get("signal_class"), "weak_non_failure", f"{pointer}/signal_class", result)
            weight = signal.get("signal_weight")
            if not isinstance(weight, (int, float)) or not 0 < weight <= 0.25:
                result.fail(f"{pointer}/signal_weight must be > 0 and <= 0.25 for review ok")
            expect_exact(
                signal.get("contributes_to_preference"),
                False,
                f"{pointer}/contributes_to_preference",
                result,
            )
            expect_exact(
                signal.get("can_support_non_failure"),
                True,
                f"{pointer}/can_support_non_failure",
                result,
            )

    if not saw_survey_ok:
        result.fail("positive evidence fixture must include a survey ok no-signal example")
    if not saw_mission_ok:
        result.fail("positive evidence fixture must include a mission/song-review ok weak example")

    artist_rollups = evidence.get("rollups", {}).get("by_artist", [])
    survey_ok_artist_rollup = next(
        (
            rollup
            for rollup in artist_rollups
            if rollup.get("rollup_id") == "rollup_artist_synthetic_target"
        ),
        None,
    )
    if survey_ok_artist_rollup is None:
        result.fail("missing survey-ok artist rollup proving ok is ignored")
    else:
        counts = survey_ok_artist_rollup.get("signal_counts", {})
        expect_exact(counts.get("survey_ok_ignored"), 1, "/rollups/by_artist/survey_ok_ignored", result)
        expect_exact(counts.get("total_preference_signals"), 0, "/rollups/by_artist/total_preference_signals", result)
        expect_exact(counts.get("total_non_failure_signals"), 0, "/rollups/by_artist/total_non_failure_signals", result)

    song_rollups = evidence.get("rollups", {}).get("by_song", [])
    mission_ok_song_rollup = next(
        (rollup for rollup in song_rollups if rollup.get("rollup_id") == "rollup_song_gateway_step"),
        None,
    )
    if mission_ok_song_rollup is None:
        result.fail("missing mission-ok song rollup proving weak non-failure")
    else:
        counts = mission_ok_song_rollup.get("signal_counts", {})
        expect_exact(counts.get("mission_ok_weak"), 1, "/rollups/by_song/mission_ok_weak", result)
        expect_exact(counts.get("total_preference_signals"), 0, "/rollups/by_song/total_preference_signals", result)
        expect_exact(counts.get("total_non_failure_signals"), 1, "/rollups/by_song/total_non_failure_signals", result)

    if result.ok:
        result.pass_("evidence reaction semantics gates passed")


VARIANT_SUFFIX_PREFIXES = ("_candidate_", "_floor_fail_", "_low_score_")


def strip_variant_suffix(target_id: str) -> str:
    for prefix in VARIANT_SUFFIX_PREFIXES:
        if prefix in target_id:
            return target_id.split(prefix, 1)[0]
    return target_id


def parse_target_rollup_ref(rollup_ref: str) -> tuple[str | None, str | None]:
    parts = rollup_ref.split(":")
    if len(parts) >= 4 and parts[0] in {"visible_rollup", "synthetic_rollup"}:
        return parts[1], parts[2]
    return None, None


def split_rollup_target_ids(target_object_id: str, target_object_type: str) -> list[str]:
    if target_object_type in {"family_pair", "archetype_pair"}:
        parts = [part for part in target_object_id.split("->") if part]
        if len(parts) >= 2:
            return parts[:2]
    return [target_object_id]


def target_identity_errors(opportunity: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    target_ref = opportunity.get("target_object_ref", {})
    target_object_type = opportunity.get("target_object_type")
    target_ids = opportunity.get("target_object_ids", [])
    source_summary = opportunity.get("source_signal_summary", {})
    filled = opportunity.get("filled_requirements", {})
    graph_contexts = opportunity.get("graph_context_summary", {}).get("graph_contexts", [])
    floor_refs = opportunity.get("floor_details", {}).get("floor_evidence_refs", [])
    required_rollups = filled.get("required_evidence_rollup_refs", [])
    required_graph_refs = filled.get("required_graph_object_refs", [])

    if target_ref.get("object_type") != target_object_type:
        errors.append("target_object_ref object_type differs from opportunity target_object_type")
    if target_ref.get("object_ids") != target_ids:
        errors.append("target_object_ref object_ids differ from target_object_ids")
    if source_summary.get("target_object_type") != target_object_type:
        errors.append("source_signal_summary target_object_type differs from opportunity target_object_type")
    if source_summary.get("target_object_ids") != target_ids:
        errors.append("source_signal_summary target_object_ids differ from target_object_ids")
    if source_summary.get("target_display_name") != target_ref.get("display_name"):
        errors.append("target display object and source rollup display object differ")

    if not required_graph_refs:
        errors.append("required_graph_object_refs must include the target object ref")
    elif required_graph_refs[0] != target_ref:
        errors.append("required_graph_object_refs first ref differs from target_object_ref")

    if not graph_contexts:
        errors.append("graph_context_summary graph_contexts missing")
    else:
        for index, context in enumerate(graph_contexts):
            if context.get("target_object_ref") != target_ref:
                errors.append(f"graph_context_summary graph_contexts/{index} target ref differs")

    if not floor_refs or not required_rollups:
        errors.append("floor and required evidence rollup refs must be present")
        return errors

    floor_rollup_ref = floor_refs[0]
    required_rollup_ref = required_rollups[0]
    source_rollup_ref = source_summary.get("target_rollup_ref")
    if floor_rollup_ref != required_rollup_ref or floor_rollup_ref != source_rollup_ref:
        errors.append("floor, required, and source target rollup refs differ")

    rollup_type, rollup_target_id = parse_target_rollup_ref(floor_rollup_ref)
    if rollup_type is None or rollup_target_id is None:
        errors.append("target rollup ref must use visible_rollup/synthetic_rollup:<level>:<target_id>:<source>")
        return errors

    if rollup_type != target_object_type:
        errors.append(f"{target_object_type} target uses a different {rollup_type} rollup")

    expected_base_ids = split_rollup_target_ids(rollup_target_id, str(target_object_type))
    actual_base_ids = [strip_variant_suffix(str(target_id)) for target_id in target_ids]
    if actual_base_ids != expected_base_ids:
        errors.append("target ids do not preserve provenance to the target rollup base ids")

    if target_object_type in {"family_pair", "archetype_pair"} and len(expected_base_ids) != 2:
        errors.append("pair target IDs do not match pair rollup IDs")

    return errors


def validate_opportunity_domain(
    opportunity: dict[str, Any],
    result: ValidationResult,
    label: str = "opportunity",
) -> None:
    expect_false_flags(opportunity, result, label)
    expect_no_forbidden_content_keys(opportunity, result, label)
    expect_no_personal_private_labels(opportunity, result, label)
    expect_exact(opportunity.get("opportunity_only"), True, f"{label}/opportunity_only", result)
    expect_exact(opportunity.get("construction_status"), "not_constructed", f"{label}/construction_status", result)

    graph_contexts = opportunity.get("graph_context_summary", {}).get("graph_contexts", [])
    if not isinstance(graph_contexts, list) or not graph_contexts:
        result.fail(f"{label}/graph_context_summary/graph_contexts must be non-empty")

    score = opportunity.get("score_components", {}).get("final_opportunity_score")
    if not isinstance(score, (int, float)) or not 0 <= score <= 1:
        result.fail(f"{label}/score_components/final_opportunity_score must be between 0 and 1")

    raw_score = opportunity.get("score_components", {}).get("raw_score")
    if not isinstance(raw_score, (int, float)) or not 0 <= raw_score <= 1:
        result.fail(f"{label}/score_components/raw_score must be between 0 and 1")

    for error in target_identity_errors(opportunity):
        result.fail(f"{label} target identity integrity: {error}")


def validate_selector_ranked_opportunities(selector: dict[str, Any], result: ValidationResult) -> None:
    opportunities = selector.get("ranked_opportunities", [])
    opportunity_schema = load_json(OPPORTUNITY_SCHEMA)
    Draft202012Validator, FormatChecker, RefResolver = jsonschema_tools()
    if Draft202012Validator is None or FormatChecker is None or RefResolver is None:
        result.fail("jsonschema is required to validate selector ranked opportunities")
        return

    resolver = RefResolver.from_schema(opportunity_schema, store=load_schema_store())
    validator = Draft202012Validator(
        opportunity_schema,
        format_checker=FormatChecker(),
        resolver=resolver,
    )
    previous_score: float | None = None

    for index, opportunity in enumerate(opportunities):
        item_errors = sorted(validator.iter_errors(opportunity), key=lambda error: list(error.path))
        if item_errors:
            for error in item_errors:
                result.fail(
                    "selector ranked opportunity "
                    f"/ranked_opportunities/{index}{format_path(error.path)}: {error.message}"
                )
            continue

        validate_opportunity_domain(opportunity, result, f"selector/ranked_opportunities/{index}")
        score = opportunity.get("score_components", {}).get("final_opportunity_score")
        if isinstance(score, (int, float)):
            if previous_score is not None and score > previous_score:
                result.fail("/ranked_opportunities must be sorted by descending final_opportunity_score")
            previous_score = score

    if not opportunities:
        result.fail("selector positive fixture must include at least one ranked opportunity")

    if result.ok:
        result.pass_("selector ranked opportunities satisfy opportunity schema")


def validate_selector_domain(selector: dict[str, Any], result: ValidationResult) -> None:
    expect_false_flags(selector, result, "selector")
    expect_no_forbidden_content_keys(selector, result, "selector")
    expect_no_personal_private_labels(selector, result, "selector")
    expect_exact(selector.get("opportunity_only"), True, "/opportunity_only", result)
    expect_exact(selector.get("global_top_k_opportunities"), 25, "/global_top_k_opportunities", result)
    expect_exact(selector.get("selector_audit", {}).get("heap_max_size"), 25, "/selector_audit/heap_max_size", result)
    expect_exact(
        selector.get("selector_audit", {}).get("selection_mode"),
        "offline_synthetic_fixture",
        "/selector_audit/selection_mode",
        result,
    )
    audit = selector.get("selector_audit", {})
    if audit.get("final_heap_size") != len(selector.get("ranked_opportunities", [])):
        result.fail("/selector_audit/final_heap_size must equal ranked opportunity count")
    if len(selector.get("ranked_opportunities", [])) > 25:
        result.fail("/ranked_opportunities must enforce global top-K limit of 25")
    for key in [
        "candidate_blobs_generated",
        "candidate_blobs_floor_passed",
        "candidate_blobs_scored",
        "candidate_blobs_pruned",
    ]:
        if not isinstance(audit.get(key), int) or audit.get(key) < 0:
            result.fail(f"/selector_audit/{key} must be a non-negative integer")
    if audit.get("candidate_blobs_generated", 0) and not audit.get("floor_failure_examples"):
        result.fail("/selector_audit/floor_failure_examples must record floor failures")
    duplicate_summary = audit.get("duplicate_control_summary", {})
    if duplicate_summary.get("exact_duplicate_mission_type_target_count") != 0:
        result.fail("/selector_audit/duplicate_control_summary must suppress exact mission type + target duplicates")
    if not isinstance(duplicate_summary.get("mission_type_concentration"), list):
        result.fail("/selector_audit/duplicate_control_summary/mission_type_concentration must be present")
    validate_selector_ranked_opportunities(selector, result)

    if result.ok:
        result.pass_("selector output gates passed")


def validate_type_files(result: ValidationResult) -> None:
    missing = [path for path in TYPE_FILES if not path.exists()]
    if missing:
        for path in missing:
            result.fail(f"missing TypeScript type file: {path.relative_to(REPO_ROOT)}")
        return

    blocked_substrings = [
        "MusicAtlasController",
        "supabase/functions",
        "mission_construction_v0_2",
        "mission_construction_contract_v0_2",
    ]
    for path in TYPE_FILES:
        text = path.read_text(encoding="utf-8")
        for blocked in blocked_substrings:
            if blocked in text:
                result.fail(f"{path.relative_to(REPO_ROOT)} must not import or reuse {blocked}")

    if result.ok:
        result.pass_("TypeScript selector contract files are present and offline-only")


def validate_scenario_fixture(scenarios: dict[str, Any], result: ValidationResult) -> None:
    expect_false_flags(scenarios, result, "synthetic scenarios")
    expect_no_forbidden_content_keys(scenarios, result, "synthetic scenarios")
    expect_no_personal_private_labels(scenarios, result, "synthetic scenarios")

    scenario_rollups = scenarios.get("scenario_rollups", [])
    if len(scenario_rollups) != 11:
        result.fail("/scenario_rollups must contain the 11 required synthetic scenarios")
    scenario_ids = {scenario.get("scenario_id") for scenario in scenario_rollups if isinstance(scenario, dict)}
    required_ids = {
        "sparse_post_intake_survey_ok",
        "one_strong_song_weak_archetype",
        "family_positive_weak_archetype_clarity",
        "strong_archetype_shallow_depth",
        "one_artist_shallow_depth",
        "one_album_container_signal",
        "bridge_source_positive_target_gap",
        "mixed_nearby_boundary",
        "context_heavy_signals",
        "recent_surprise_signal",
        "high_signal_low_survey_dominated",
    }
    if scenario_ids != required_ids:
        result.fail(f"/scenario_rollups scenario id mismatch: {sorted(scenario_ids)}")

    for index, scenario in enumerate(scenario_rollups):
        expected = scenario.get("expected_top_mission_types", [])
        for mission_type in expected:
            if mission_type not in EXPECTED_MISSION_TYPES:
                result.fail(f"/scenario_rollups/{index}/expected_top_mission_types has unsupported type {mission_type}")

    if result.ok:
        result.pass_("synthetic selector scenario fixture gates passed")


def validate_profile_simulation_fixtures(result: ValidationResult) -> None:
    visible = load_json(PROFILE_VISIBLE_INPUTS)
    hidden = load_json(PROFILE_HIDDEN_ORACLES)
    summary = load_json(PROFILE_PHASE1_SUMMARY)

    expect_exact(visible.get("selector_may_read"), True, "/profile_visible/selector_may_read", result)
    expect_exact(visible.get("hidden_oracle_included"), False, "/profile_visible/hidden_oracle_included", result)
    expect_false_flags(visible, result, "profile visible inputs")
    expect_no_forbidden_content_keys(visible, result, "profile visible inputs")
    expect_no_personal_private_labels(visible, result, "profile visible inputs")

    for key, _child, pointer in iter_dict_items(visible):
        if key == "hidden_oracle":
            result.fail(f"profile visible inputs must not contain hidden_oracle payloads at {pointer}")
        if key.startswith("source_hidden"):
            result.fail(f"profile visible inputs must not contain hidden source refs at {pointer}")

    expect_exact(hidden.get("selector_may_read"), False, "/profile_hidden/selector_may_read", result)
    expect_exact(hidden.get("not_allowed_for_selector"), True, "/profile_hidden/not_allowed_for_selector", result)
    expect_false_flags(hidden, result, "profile hidden oracles")

    visible_profiles = visible.get("profiles", [])
    hidden_profiles = hidden.get("profiles", [])
    if len(visible_profiles) != 3 or len(hidden_profiles) != 3:
        result.fail("profile simulation fixtures must include exactly profiles 01, 05, and 06")

    visible_ids = [profile.get("profile_id") for profile in visible_profiles]
    hidden_ids = [profile.get("profile_id") for profile in hidden_profiles]
    if visible_ids != ["public_profile_01", "public_profile_05", "public_profile_06"]:
        result.fail(f"profile visible ids mismatch: {visible_ids}")
    if hidden_ids != visible_ids:
        result.fail("hidden oracle profile ids must match visible profile ids")

    for index, profile in enumerate(visible_profiles):
        counts = profile.get("visible_evidence", {}).get("survey_signals_summary", {})
        if counts.get("survey_ok_ignored", 0) <= 0:
            result.fail(f"/profile_visible/profiles/{index} must prove survey ok ignored")
        if counts.get("total_non_failure_signals") != counts.get("survey_love", 0) + counts.get("survey_like", 0):
            result.fail(f"/profile_visible/profiles/{index} survey ok must not count as non-failure")
        if "hidden_oracle" in profile:
            result.fail(f"/profile_visible/profiles/{index} must not contain hidden_oracle")

    for index, profile in enumerate(hidden_profiles):
        oracle = profile.get("hidden_oracle", {})
        song_reactions = oracle.get("song_reactions", [])
        reactions = {item.get("reaction") for item in song_reactions}
        if not {"love", "like", "ok", "dont_like"}.issubset(reactions):
            result.fail(f"/profile_hidden/profiles/{index}/hidden_oracle/song_reactions must cover love/like/ok/dont_like")
        if profile.get("selector_may_read") is not False:
            result.fail(f"/profile_hidden/profiles/{index}/selector_may_read must be false")

    if summary.get("visible_selector_input_ref") != str(PROFILE_VISIBLE_INPUTS.relative_to(REPO_ROOT)):
        result.fail("/profile_summary/visible_selector_input_ref must point to visible fixture")
    if summary.get("hidden_oracle_ref") != str(PROFILE_HIDDEN_ORACLES.relative_to(REPO_ROOT)):
        result.fail("/profile_summary/hidden_oracle_ref must point to hidden oracle fixture")

    top5_sequences: list[tuple[str, ...]] = []

    for output_path in PROFILE_SELECTOR_OUTPUTS:
        selector = load_json(output_path)
        errors = schema_errors(SELECTOR_SCHEMA, selector)
        if errors:
            for error in errors:
                result.fail(f"{output_path.relative_to(REPO_ROOT)} schema {error}")
            continue
        validate_selector_domain(selector, result)
        source_ref = selector.get("source_evidence_rollup_ref", "")
        if "hidden" in source_ref or "oracle" in source_ref:
            result.fail(f"{output_path.name} selector source must not reference hidden oracle")
        if str(PROFILE_VISIBLE_INPUTS.relative_to(REPO_ROOT)) not in source_ref:
            result.fail(f"{output_path.name} selector source must reference visible profile fixture")
        if selector.get("selector_audit", {}).get("final_heap_size") != 25:
            result.fail(f"{output_path.name} selector must keep a full top-25 heap")

        profile_id = output_path.name.replace("_selector_output_v0_1.json", "")
        visible_profile = next(
            (profile for profile in visible_profiles if profile.get("profile_id") == profile_id),
            None,
        )
        if visible_profile is None:
            result.fail(f"{output_path.name} has no matching visible profile")
            continue

        ranked = selector.get("ranked_opportunities", [])
        top5 = tuple(opportunity.get("mission_type") for opportunity in ranked[:5])
        top10 = [opportunity.get("mission_type") for opportunity in ranked[:10]]
        expected = set(
            visible_profile.get("expected_selector_behavior", {}).get(
                "likely_top_mission_types",
                [],
            )
        )
        top5_sequences.append(top5)

        if len(expected.intersection(top5)) < 1:
            result.fail(f"{output_path.name} must place at least one visible-expected mission type in top 5")
        if len(expected.intersection(top10)) < 2:
            result.fail(f"{output_path.name} must place at least two visible-expected mission types in top 10")

        ranked_types = {opportunity.get("mission_type") for opportunity in ranked}
        initial_suppressed = "initial_profile_survey" not in ranked_types
        if not initial_suppressed:
            result.fail(f"{output_path.name} must suppress initial_profile_survey when sparse floor is not met")

    if len(set(top5_sequences)) <= 1:
        result.fail("profile selector top-5 mission type sequences must not be identical for all public profiles")

    if result.ok:
        result.pass_("profile oracle phase-1 fixtures preserve selector/oracle separation")


def ref_path(ref: str) -> Path:
    return REPO_ROOT / ref.split("#", 1)[0]


def validate_metric_scores(value: dict[str, Any], result: ValidationResult, label: str) -> None:
    expected_metrics = {
        "opportunity_relevance",
        "hidden_hit_rate_proxy",
        "diagnostic_value",
        "boundary_discovery_potential",
        "false_nearby_detection_potential",
        "context_detection_potential",
        "overfit_prevention_score",
        "survey_decay_score",
        "learning_usefulness_score",
    }
    if set(value) != expected_metrics:
        result.fail(f"{label} metric set mismatch: {sorted(value)}")
        return
    for key, score in value.items():
        if not isinstance(score, (int, float)) or not 0 <= score <= 1:
            result.fail(f"{label}/{key} must be between 0 and 1")


def validate_hidden_oracle_evaluation_design(
    evaluation: dict[str, Any],
    result: ValidationResult,
) -> None:
    expect_false_flags(evaluation, result, "hidden oracle evaluation design")
    expect_no_forbidden_content_keys(evaluation, result, "hidden oracle evaluation design")
    expect_no_personal_private_labels(evaluation, result, "hidden oracle evaluation design")
    expect_exact(
        evaluation.get("phase"),
        "post_selection_oracle_evaluation_design",
        "/hidden_oracle_evaluation/phase",
        result,
    )
    expect_exact(
        evaluation.get("selector_may_read_hidden_oracle"),
        False,
        "/hidden_oracle_evaluation/selector_may_read_hidden_oracle",
        result,
    )
    expect_exact(
        evaluation.get("evaluator_may_read_hidden_oracle_after_selection"),
        True,
        "/hidden_oracle_evaluation/evaluator_may_read_hidden_oracle_after_selection",
        result,
    )

    visible_ref = evaluation.get("selector_visible_input_ref", "")
    hidden_ref = evaluation.get("hidden_oracle_ref", "")
    if visible_ref != str(PROFILE_VISIBLE_INPUTS.relative_to(REPO_ROOT)):
        result.fail("/hidden_oracle_evaluation/selector_visible_input_ref must point to visible profile inputs")
    if hidden_ref != str(PROFILE_HIDDEN_ORACLES.relative_to(REPO_ROOT)):
        result.fail("/hidden_oracle_evaluation/hidden_oracle_ref must point to hidden oracle fixture")
    if "hidden" in visible_ref or "oracle" in visible_ref:
        result.fail("/hidden_oracle_evaluation/selector_visible_input_ref must not reference hidden oracle data")

    scope = evaluation.get("evaluation_scope", {})
    expect_exact(
        scope.get("evaluation_subject"),
        "selected_opportunity_blobs_only",
        "/hidden_oracle_evaluation/evaluation_scope/evaluation_subject",
        result,
    )
    expect_exact(
        scope.get("hidden_oracle_use"),
        "post_selection_evaluator_only",
        "/hidden_oracle_evaluation/evaluation_scope/hidden_oracle_use",
        result,
    )
    expect_exact(
        scope.get("selector_input_rule"),
        "visible_evidence_only",
        "/hidden_oracle_evaluation/evaluation_scope/selector_input_rule",
        result,
    )
    expect_exact(
        scope.get("construction_simulation_status"),
        "not_implemented",
        "/hidden_oracle_evaluation/evaluation_scope/construction_simulation_status",
        result,
    )
    expect_exact(
        scope.get("candidate_song_selection_status"),
        "not_in_scope",
        "/hidden_oracle_evaluation/evaluation_scope/candidate_song_selection_status",
        result,
    )

    metric_names = {
        definition.get("metric_name")
        for definition in evaluation.get("metric_definitions", [])
        if isinstance(definition, dict)
    }
    expected_metric_names = {
        "opportunity_relevance",
        "hidden_hit_rate_proxy",
        "diagnostic_value",
        "boundary_discovery_potential",
        "false_nearby_detection_potential",
        "context_detection_potential",
        "overfit_prevention_score",
        "survey_decay_score",
        "learning_usefulness_score",
    }
    if metric_names != expected_metric_names:
        result.fail(f"/hidden_oracle_evaluation/metric_definitions mismatch: {sorted(metric_names)}")

    visible = load_json(PROFILE_VISIBLE_INPUTS)
    hidden = load_json(PROFILE_HIDDEN_ORACLES)
    visible_ids = [profile.get("profile_id") for profile in visible.get("profiles", [])]
    hidden_ids = [profile.get("profile_id") for profile in hidden.get("profiles", [])]

    selector_output_refs = set(evaluation.get("selector_output_refs", []))
    expected_selector_refs = {
        str(path.relative_to(REPO_ROOT))
        for path in PROFILE_SELECTOR_OUTPUTS
    }
    if selector_output_refs != expected_selector_refs:
        result.fail("/hidden_oracle_evaluation/selector_output_refs must match public profile selector outputs")

    evaluated_ids: list[str] = []
    for profile_index, profile in enumerate(evaluation.get("profiles", [])):
        label = f"/hidden_oracle_evaluation/profiles/{profile_index}"
        profile_id = profile.get("profile_id")
        evaluated_ids.append(profile_id)
        if profile_id not in visible_ids or profile_id not in hidden_ids:
            result.fail(f"{label}/profile_id has no matching visible and hidden fixtures")

        selector_output_ref = str(profile.get("selector_output_ref", ""))
        if selector_output_ref not in expected_selector_refs:
            result.fail(f"{label}/selector_output_ref must reference a known selector output")
            continue
        if "hidden" in selector_output_ref or "oracle" in selector_output_ref:
            result.fail(f"{label}/selector_output_ref must not reference hidden oracle data")

        visible_evidence_ref = str(profile.get("visible_evidence_ref", ""))
        if not visible_evidence_ref.startswith(str(PROFILE_VISIBLE_INPUTS.relative_to(REPO_ROOT))):
            result.fail(f"{label}/visible_evidence_ref must reference visible inputs")
        if "hidden" in visible_evidence_ref or "oracle" in visible_evidence_ref:
            result.fail(f"{label}/visible_evidence_ref must not reference hidden oracle data")

        hidden_profile_ref = str(profile.get("hidden_oracle_profile_ref", ""))
        if not hidden_profile_ref.startswith(str(PROFILE_HIDDEN_ORACLES.relative_to(REPO_ROOT))):
            result.fail(f"{label}/hidden_oracle_profile_ref must reference hidden oracle fixture")

        selector = load_json(ref_path(selector_output_ref))
        ranked_by_id = {
            opportunity.get("opportunity_id"): (index + 1, opportunity)
            for index, opportunity in enumerate(selector.get("ranked_opportunities", []))
        }

        for eval_index, opportunity_eval in enumerate(profile.get("top_opportunity_evaluations", [])):
            eval_label = f"{label}/top_opportunity_evaluations/{eval_index}"
            expect_false_flags(opportunity_eval, result, eval_label)
            expect_no_forbidden_content_keys(opportunity_eval, result, eval_label)
            selected_ref = opportunity_eval.get("selected_opportunity_ref", {})
            opportunity_id = selected_ref.get("opportunity_id")
            ranked_match = ranked_by_id.get(opportunity_id)
            if ranked_match is None:
                result.fail(f"{eval_label}/selected_opportunity_ref/opportunity_id is not in selector output")
                continue
            rank, opportunity = ranked_match
            comparisons = {
                "rank": rank,
                "mission_type": opportunity.get("mission_type"),
                "target_object_type": opportunity.get("target_object_type"),
                "target_object_ids": opportunity.get("target_object_ids"),
                "target_display_name": opportunity.get("target_object_ref", {}).get("display_name"),
                "final_opportunity_score": opportunity.get("score_components", {}).get("final_opportunity_score"),
            }
            for key, expected in comparisons.items():
                if selected_ref.get(key) != expected:
                    result.fail(f"{eval_label}/selected_opportunity_ref/{key} differs from selector output")

            expect_exact(
                opportunity_eval.get("construction_status"),
                "not_constructed",
                f"{eval_label}/construction_status",
                result,
            )
            expect_exact(
                opportunity_eval.get("candidate_song_selection_status"),
                "not_in_scope",
                f"{eval_label}/candidate_song_selection_status",
                result,
            )
            expect_exact(
                opportunity_eval.get("no_candidate_song_list"),
                True,
                f"{eval_label}/no_candidate_song_list",
                result,
            )
            evaluator_refs = opportunity_eval.get("evaluator_use_only_hidden_refs", [])
            if not evaluator_refs or not all("hidden_profile_oracles_v0_1.json" in ref for ref in evaluator_refs):
                result.fail(f"{eval_label}/evaluator_use_only_hidden_refs must point to hidden oracle fixture")
            validate_metric_scores(
                opportunity_eval.get("expected_metrics", {}),
                result,
                f"{eval_label}/expected_metrics",
            )

        validate_metric_scores(
            profile.get("aggregate_metrics", {}),
            result,
            f"{label}/aggregate_metrics",
        )

    if evaluated_ids != visible_ids:
        result.fail(f"/hidden_oracle_evaluation/profiles ids mismatch: {evaluated_ids}")

    if result.ok:
        result.pass_("hidden oracle post-selection evaluation design gates passed")


def opportunity_ref_from_evaluation(evaluation: dict[str, Any]) -> dict[str, Any]:
    selected = evaluation.get("selected_opportunity_ref", {})
    metrics = evaluation.get("expected_metrics", {})
    return {
        "opportunity_id": selected.get("opportunity_id"),
        "rank": selected.get("rank"),
        "mission_type": selected.get("mission_type"),
        "target_object_type": selected.get("target_object_type"),
        "target_object_ids": selected.get("target_object_ids"),
        "target_display_name": selected.get("target_display_name"),
        "selector_score": selected.get("final_opportunity_score"),
        "learning_usefulness_score": metrics.get("learning_usefulness_score"),
    }


def validate_rank_usefulness_analysis(
    analysis: dict[str, Any],
    result: ValidationResult,
) -> None:
    expect_false_flags(analysis, result, "rank usefulness analysis")
    expect_no_forbidden_content_keys(analysis, result, "rank usefulness analysis")
    expect_no_personal_private_labels(analysis, result, "rank usefulness analysis")
    expect_exact(
        analysis.get("phase"),
        "hidden_oracle_rank_usefulness_analysis",
        "/rank_usefulness_analysis/phase",
        result,
    )
    expect_exact(
        analysis.get("selector_may_read_hidden_oracle"),
        False,
        "/rank_usefulness_analysis/selector_may_read_hidden_oracle",
        result,
    )
    expect_exact(
        analysis.get("source_hidden_oracle_evaluation_design_ref"),
        str(HIDDEN_ORACLE_EVALUATION_FIXTURE.relative_to(REPO_ROOT)),
        "/rank_usefulness_analysis/source_hidden_oracle_evaluation_design_ref",
        result,
    )
    scope = analysis.get("analysis_scope", {})
    expect_exact(
        scope.get("analysis_subject"),
        "selected_opportunity_rank_order",
        "/rank_usefulness_analysis/analysis_scope/analysis_subject",
        result,
    )
    expect_exact(
        scope.get("hidden_oracle_use"),
        "post_selection_metrics_only",
        "/rank_usefulness_analysis/analysis_scope/hidden_oracle_use",
        result,
    )
    expect_exact(
        scope.get("selector_input_rule"),
        "visible_evidence_only",
        "/rank_usefulness_analysis/analysis_scope/selector_input_rule",
        result,
    )
    expect_exact(
        scope.get("construction_simulation_status"),
        "not_implemented",
        "/rank_usefulness_analysis/analysis_scope/construction_simulation_status",
        result,
    )
    expect_exact(
        scope.get("candidate_song_selection_status"),
        "not_in_scope",
        "/rank_usefulness_analysis/analysis_scope/candidate_song_selection_status",
        result,
    )

    design = load_json(HIDDEN_ORACLE_EVALUATION_FIXTURE)
    design_by_id = {profile.get("profile_id"): profile for profile in design.get("profiles", [])}
    profiles = analysis.get("profiles", [])
    if analysis.get("aggregate_summary", {}).get("profile_count") != len(profiles):
        result.fail("/rank_usefulness_analysis/aggregate_summary/profile_count must equal profile count")

    top1_is_best_count = 0
    best_in_top3_count = 0
    best_in_top5_count = 0
    for profile_index, profile in enumerate(profiles):
        label = f"/rank_usefulness_analysis/profiles/{profile_index}"
        profile_id = profile.get("profile_id")
        design_profile = design_by_id.get(profile_id)
        if design_profile is None:
            result.fail(f"{label}/profile_id must exist in hidden oracle evaluation design")
            continue
        rank_window = profile.get("rank_window")
        design_evaluations = design_profile.get("top_opportunity_evaluations", [])[:rank_window]
        if len(profile.get("rank_rows", [])) != len(design_evaluations):
            result.fail(f"{label}/rank_rows count must match design evaluation rank window")

        expected_profile_ref = f"{str(HIDDEN_ORACLE_EVALUATION_FIXTURE.relative_to(REPO_ROOT))}#{profile_id}"
        expect_exact(
            profile.get("evaluation_design_profile_ref"),
            expected_profile_ref,
            f"{label}/evaluation_design_profile_ref",
            result,
        )
        expect_exact(
            profile.get("selector_output_ref"),
            design_profile.get("selector_output_ref"),
            f"{label}/selector_output_ref",
            result,
        )

        expected_by_id = {
            evaluation.get("selected_opportunity_ref", {}).get("opportunity_id"): evaluation
            for evaluation in design_evaluations
        }
        sorted_by_usefulness = sorted(
            design_evaluations,
            key=lambda item: (
                -item.get("expected_metrics", {}).get("learning_usefulness_score", 0),
                item.get("selected_opportunity_ref", {}).get("rank", 999),
            ),
        )
        usefulness_rank_by_id = {
            item.get("selected_opportunity_ref", {}).get("opportunity_id"): index + 1
            for index, item in enumerate(sorted_by_usefulness)
        }
        top_design_eval = design_evaluations[0]
        best_design_eval = sorted_by_usefulness[0]
        if profile.get("top_selector_opportunity") != opportunity_ref_from_evaluation(top_design_eval):
            result.fail(f"{label}/top_selector_opportunity must match design rank 1 evaluation")
        if profile.get("best_oracle_usefulness_opportunity") != opportunity_ref_from_evaluation(best_design_eval):
            result.fail(f"{label}/best_oracle_usefulness_opportunity must match best design usefulness")

        top1_score = top_design_eval.get("expected_metrics", {}).get("learning_usefulness_score")
        best_score = best_design_eval.get("expected_metrics", {}).get("learning_usefulness_score")
        if profile.get("top1_learning_usefulness_score") != top1_score:
            result.fail(f"{label}/top1_learning_usefulness_score must match design rank 1")
        if profile.get("best_learning_usefulness_score") != best_score:
            result.fail(f"{label}/best_learning_usefulness_score must match best design usefulness")
        expected_regret = round(max(0, float(best_score) - float(top1_score)), 4)
        if profile.get("rank_regret") != expected_regret:
            result.fail(f"{label}/rank_regret must equal best minus top1 usefulness")

        best_rank = best_design_eval.get("selected_opportunity_ref", {}).get("rank")
        if profile.get("best_usefulness_rank") != best_rank:
            result.fail(f"{label}/best_usefulness_rank must equal selector rank of best usefulness")
        if profile.get("top1_is_best") != (best_rank == 1):
            result.fail(f"{label}/top1_is_best mismatch")
        if profile.get("best_in_top3") != (best_rank <= 3):
            result.fail(f"{label}/best_in_top3 mismatch")
        if profile.get("best_in_top5") != (best_rank <= 5):
            result.fail(f"{label}/best_in_top5 mismatch")

        top1_is_best_count += 1 if profile.get("top1_is_best") else 0
        best_in_top3_count += 1 if profile.get("best_in_top3") else 0
        best_in_top5_count += 1 if profile.get("best_in_top5") else 0

        for row_index, row in enumerate(profile.get("rank_rows", [])):
            row_label = f"{label}/rank_rows/{row_index}"
            design_eval = expected_by_id.get(row.get("opportunity_id"))
            if design_eval is None:
                result.fail(f"{row_label}/opportunity_id must exist in design evaluation")
                continue
            selected = design_eval.get("selected_opportunity_ref", {})
            metrics = design_eval.get("expected_metrics", {})
            expected_values = {
                "rank": selected.get("rank"),
                "mission_type": selected.get("mission_type"),
                "target_display_name": selected.get("target_display_name"),
                "selector_score": selected.get("final_opportunity_score"),
                "learning_usefulness_score": metrics.get("learning_usefulness_score"),
                "usefulness_rank": usefulness_rank_by_id.get(row.get("opportunity_id")),
            }
            for key, expected in expected_values.items():
                if row.get(key) != expected:
                    result.fail(f"{row_label}/{key} must match design evaluation")

    aggregate = analysis.get("aggregate_summary", {})
    expect_exact(
        aggregate.get("top1_is_best_count"),
        top1_is_best_count,
        "/rank_usefulness_analysis/aggregate_summary/top1_is_best_count",
        result,
    )
    expect_exact(
        aggregate.get("best_in_top3_count"),
        best_in_top3_count,
        "/rank_usefulness_analysis/aggregate_summary/best_in_top3_count",
        result,
    )
    expect_exact(
        aggregate.get("best_in_top5_count"),
        best_in_top5_count,
        "/rank_usefulness_analysis/aggregate_summary/best_in_top5_count",
        result,
    )
    if aggregate.get("alignment_label") not in {"strong", "mixed", "weak"}:
        result.fail("/rank_usefulness_analysis/aggregate_summary/alignment_label must be present")

    if result.ok:
        result.pass_("hidden oracle rank-usefulness analysis gates passed")


PHASE1E_HIDDEN_FIELD_KEYS = {
    "hidden_oracle_lane_metadata",
    "hidden_lane_id",
    "hidden_lane_metadata",
    "hidden_archetype_weights",
    "hidden_expected_usefulness",
    "oracle_usefulness_score",
    "oracle_metrics",
}


def phase1e_hidden_field_errors(value: Any, label: str) -> list[str]:
    errors: list[str] = []
    allowed_hidden_keys = {"hidden_oracle_included"}
    for key, child, pointer in iter_dict_items(value):
        lowered = str(key).lower()
        if lowered in PHASE1E_HIDDEN_FIELD_KEYS:
            errors.append(f"{label} includes hidden/oracle-only field {pointer}")
        if ("oracle" in lowered or "hidden" in lowered) and lowered not in allowed_hidden_keys:
            errors.append(f"{label} includes selector-visible hidden/oracle field {pointer}")
        if isinstance(child, str):
            text = child.lower()
            blocked_tokens = [
                "hidden_lane",
                "hidden_oracle_lane",
                "oracle_usefulness",
                "hidden_expected_usefulness",
            ]
            if any(token in text for token in blocked_tokens):
                errors.append(f"{label} includes hidden/oracle-only value at {pointer}")
    return errors


def phase1e_rank_output_errors(rank_output: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    probe = ValidationResult()
    expect_false_flags(rank_output, probe, "phase1e rank output")
    expect_no_forbidden_content_keys(rank_output, probe, "phase1e rank output")
    expect_no_personal_private_labels(rank_output, probe, "phase1e rank output")
    errors.extend(probe.failures)
    if rank_output.get("selector_may_read_hidden_oracle") is not False:
        errors.append("/selector_may_read_hidden_oracle must be false")
    if rank_output.get("evaluator_may_read_hidden_oracle_after_selection") is not True:
        errors.append("/evaluator_may_read_hidden_oracle_after_selection must be true")
    if rank_output.get("candidate_song_selection_status") != "not_in_scope":
        errors.append("/candidate_song_selection_status must be not_in_scope")
    if rank_output.get("final_mission_construction_status") != "not_in_scope":
        errors.append("/final_mission_construction_status must be not_in_scope")
    if len(rank_output.get("runs", [])) < 12:
        errors.append("/runs must include at least 12 expanded scale analyses")
    for index, run in enumerate(rank_output.get("runs", [])):
        if run.get("rank_window") != len(run.get("rank_rows", [])):
            errors.append(f"/runs/{index}/rank_window must equal rank_rows count")
        for row_index, row in enumerate(run.get("rank_rows", [])):
            if "candidate_song_ids" in row:
                errors.append(f"/runs/{index}/rank_rows/{row_index}/candidate_song_ids is forbidden")
            learning = row.get("learning_usefulness_score")
            if not isinstance(learning, (int, float)) or not 0 <= learning <= 1:
                errors.append(f"/runs/{index}/rank_rows/{row_index}/learning_usefulness_score must be 0..1")
    return errors


def validate_phase1e_outputs(result: ValidationResult) -> None:
    required_files = [
        PHASE1E_EXPANDED_VISIBLE,
        PHASE1E_RANK_USEFULNESS,
        PHASE1E_SUMMARY_JSON,
        PHASE1E_SUMMARY_MD,
    ]
    missing = [path for path in required_files if not path.exists()]
    if missing:
        for path in missing:
            result.fail(f"missing Phase 1E output: {path.relative_to(REPO_ROOT)}")
        return

    expanded = load_json(PHASE1E_EXPANDED_VISIBLE)
    rank_output = load_json(PHASE1E_RANK_USEFULNESS)
    summary = load_json(PHASE1E_SUMMARY_JSON)
    expect_false_flags(expanded, result, "phase1e expanded visible")
    expect_no_forbidden_content_keys(expanded, result, "phase1e expanded visible")
    expect_no_personal_private_labels(expanded, result, "phase1e expanded visible")
    expect_exact(expanded.get("selector_may_read"), True, "/phase1e_expanded/selector_may_read", result)
    expect_exact(expanded.get("hidden_oracle_included"), False, "/phase1e_expanded/hidden_oracle_included", result)
    expect_exact(
        expanded.get("fixture_construction_policy", {}).get("evaluation_metrics_written_to_selector_input"),
        False,
        "/phase1e_expanded/fixture_construction_policy/evaluation_metrics_written_to_selector_input",
        result,
    )

    for error in phase1e_hidden_field_errors(expanded, "phase1e expanded visible"):
        result.fail(error)

    profiles = expanded.get("profiles", [])
    expected_profiles = {"public_profile_01", "public_profile_05", "public_profile_06"}
    expected_scales = {72, 150, 200, 300}
    expected_modes = {"profile_weighted_balanced", "edge_heavy", "song_heavy"}
    observed_matrix = {
        (profile.get("profile_id"), profile.get("evidence_atom_count"), profile.get("sampling_mode"))
        for profile in profiles
    }
    expected_matrix = {
        (profile_id, scale, mode)
        for profile_id in expected_profiles
        for scale in expected_scales
        for mode in expected_modes
    }
    if observed_matrix != expected_matrix:
        result.fail("Phase 1E expanded visible run matrix must be 3 profiles x 4 scales x 3 modes")

    for index, profile in enumerate(profiles):
        label = f"/phase1e_expanded/profiles/{index}"
        if profile.get("selector_may_read") is not True:
            result.fail(f"{label}/selector_may_read must be true")
        if profile.get("hidden_oracle_included") is not False:
            result.fail(f"{label}/hidden_oracle_included must be false")
        visible = profile.get("visible_evidence", {})
        atoms = visible.get("sampled_visible_evidence_atoms", [])
        if len(atoms) != profile.get("evidence_atom_count"):
            result.fail(f"{label}/visible_evidence/sampled_visible_evidence_atoms count must match evidence_atom_count")
        counts = visible.get("survey_signals_summary", {})
        if counts.get("total_visible_atoms") != profile.get("evidence_atom_count"):
            result.fail(f"{label}/survey_signals_summary/total_visible_atoms must match evidence_atom_count")
        if counts.get("total_preference_signals") != counts.get("survey_love", 0) + counts.get("survey_like", 0) + counts.get("survey_dislike", 0):
            result.fail(f"{label}/total_preference_signals must count love/like/dislike only")
        if counts.get("total_non_failure_signals") != counts.get("survey_love", 0) + counts.get("survey_like", 0) + counts.get("mission_ok_weak", 0):
            result.fail(f"{label}/total_non_failure_signals must include mission ok weak but not survey ok")
        if counts.get("survey_ok_ignored", 0) < 0 or counts.get("mission_ok_weak", 0) < 0:
            result.fail(f"{label}/ok counts must be non-negative")

    rank_errors = phase1e_rank_output_errors(rank_output)
    for error in rank_errors:
        result.fail(f"phase1e rank output {error}")
    if rank_output.get("source_expanded_visible_profile_inputs_ref") != str(PHASE1E_EXPANDED_VISIBLE.relative_to(REPO_ROOT)):
        result.fail("/phase1e_rank/source_expanded_visible_profile_inputs_ref must point to expanded visible fixture")

    run_by_id = {run.get("run_id"): run for run in rank_output.get("runs", [])}
    summary_runs = summary.get("per_run_metrics", [])
    if len(summary_runs) != 36 or summary.get("run_matrix", {}).get("completed_run_count") != 36:
        result.fail("Phase 1E summary must include the 36-run stretch matrix")
    if summary.get("determinism_summary", {}).get("all_deterministic") is not True:
        result.fail("Phase 1E deterministic rerun check must pass for all runs")
    if summary.get("candidate_song_selection_status") != "not_in_scope":
        result.fail("Phase 1E summary candidate_song_selection_status must be not_in_scope")
    if summary.get("final_mission_construction_status") != "not_in_scope":
        result.fail("Phase 1E summary final_mission_construction_status must be not_in_scope")
    if summary.get("oracle_evaluation_fed_back_into_selector") is not False:
        result.fail("Phase 1E oracle evaluation must not feed back into selector")

    for run in summary_runs:
        run_id = run.get("run_id")
        if run_id not in run_by_id:
            result.fail(f"Phase 1E summary run {run_id} missing rank output")
            continue
        selector_ref = run.get("selector_output_ref")
        if not isinstance(selector_ref, str):
            result.fail(f"Phase 1E run {run_id} missing selector_output_ref")
            continue
        selector_path = REPO_ROOT / selector_ref
        if not selector_path.exists():
            result.fail(f"Phase 1E selector output missing: {selector_ref}")
            continue
        selector = load_json(selector_path)
        selector_errors = schema_errors(SELECTOR_SCHEMA, selector)
        for error in selector_errors:
            result.fail(f"{selector_ref} schema {error}")
        if not selector_errors:
            validate_selector_domain(selector, result)
        source_ref = selector.get("source_evidence_rollup_ref", "")
        if str(PHASE1E_EXPANDED_VISIBLE.relative_to(REPO_ROOT)) not in source_ref:
            result.fail(f"{selector_ref} must reference Phase 1E expanded visible fixture")
        if "hidden" in source_ref or "oracle" in source_ref:
            result.fail(f"{selector_ref} selector source must not reference hidden/oracle data")
        if run.get("deterministic_rerun_matched") is not True:
            result.fail(f"Phase 1E run {run_id} deterministic rerun must match")
        if not isinstance(run.get("final_heap_size"), int) or not 0 <= run.get("final_heap_size") <= 25:
            result.fail(f"Phase 1E run {run_id} final_heap_size must be between 0 and 25")

    negative_expectations = [
        (
            "expanded visible hidden lane leak",
            PHASE1E_NEGATIVE_DIR / "expanded_visible_hidden_lane_leak_v0_1.json",
            lambda payload: phase1e_hidden_field_errors(payload, "negative expanded visible"),
        ),
        (
            "selector output oracle usefulness score",
            PHASE1E_NEGATIVE_DIR / "selector_output_contains_oracle_usefulness_score_v0_1.json",
            lambda payload: schema_errors(SELECTOR_SCHEMA, payload),
        ),
        (
            "rank output candidate song list",
            PHASE1E_NEGATIVE_DIR / "rank_usefulness_contains_candidate_song_list_v0_1.json",
            phase1e_rank_output_errors,
        ),
        (
            "runtime flag true",
            PHASE1E_NEGATIVE_DIR / "phase1e_runtime_flag_true_v0_1.json",
            phase1e_rank_output_errors,
        ),
        (
            "determinism mismatch",
            PHASE1E_NEGATIVE_DIR / "phase1e_determinism_mismatch_v0_1.json",
            lambda payload: [] if payload.get("deterministic_rerun_matched") is True else ["deterministic_rerun_matched must be true"],
        ),
    ]
    for label, path, validator in negative_expectations:
        if not path.exists():
            result.fail(f"missing Phase 1E negative fixture: {path.relative_to(REPO_ROOT)}")
            continue
        errors = validator(load_json(path))
        if errors:
            result.pass_(f"Phase 1E negative fixture rejected: {label}")
        else:
            result.fail(f"Phase 1E negative fixture unexpectedly passed: {label}")

    if result.ok:
        result.pass_("Phase 1E expanded visible evidence scale outputs passed")


PHASE1F_CONSTRUCTOR_INPUT_FORBIDDEN_KEYS = {
    "reaction",
    "hidden_oracle_reaction",
    "reason_tags",
    "confidence",
    "familiarity_band",
    "hidden_lane_id",
    "hidden_lane_metadata",
    "hidden_archetype_weights",
}


def phase1f_constructor_input_errors(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key, _child, pointer in iter_dict_items(payload):
        if key in PHASE1F_CONSTRUCTOR_INPUT_FORBIDDEN_KEYS:
            errors.append(f"constructor selection input includes hidden-only field {pointer}")
    return errors


def phase1f_selector_leak_errors(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key, _child, pointer in iter_dict_items(payload):
        if str(key).lower() in {
            "hidden_oracle_reaction",
            "hidden_oracle_confidence",
            "oracle_metrics",
            "overall_smell_score",
        }:
            errors.append(f"selector output includes post-selection oracle field {pointer}")
    return errors


def phase1f_result_errors(payload: dict[str, Any]) -> list[str]:
    errors = schema_errors(PHASE1F_SCHEMA, payload)
    probe = ValidationResult()
    expect_false_flags(payload, probe, "phase1f song-pack simulation")
    expect_no_forbidden_content_keys(payload, probe, "phase1f song-pack simulation")
    expect_no_personal_private_labels(payload, probe, "phase1f song-pack simulation")
    errors.extend(probe.failures)

    if payload.get("phase") != "offline_top_window_song_pack_smell_test":
        errors.append("/phase must be offline_top_window_song_pack_smell_test")
    if payload.get("selector_may_read_hidden_oracle") is not False:
        errors.append("/selector_may_read_hidden_oracle must be false")
    if payload.get("constructor_optimized_by_hidden_reaction_labels") is not False:
        errors.append("/constructor_optimized_by_hidden_reaction_labels must be false")
    if payload.get("oracle_evaluation_fed_back_into_selector") is not False:
        errors.append("/oracle_evaluation_fed_back_into_selector must be false")
    if payload.get("song_pack_construction_status") != "offline_smell_test_only":
        errors.append("/song_pack_construction_status must be offline_smell_test_only")

    run_matrix = payload.get("run_matrix", {})
    if run_matrix.get("completed_pack_count") != len(payload.get("packs", [])):
        errors.append("/run_matrix/completed_pack_count must equal pack count")
    if run_matrix.get("completed_pack_count", 0) < 45:
        errors.append("/run_matrix/completed_pack_count must be at least 45")
    if run_matrix.get("top_window_size") != 10:
        errors.append("/run_matrix/top_window_size must be 10")
    if run_matrix.get("pack_size") != 6:
        errors.append("/run_matrix/pack_size must be 6")

    guardrail = payload.get("guardrail_summary", {})
    required_guardrails = {
        "selector_did_not_read_hidden_oracle": True,
        "constructor_selection_pool_reaction_labels_visible": False,
        "constructor_selection_pool_hidden_reason_tags_visible": False,
        "oracle_reactions_joined_after_pack_construction": True,
        "runtime_flags_remain_false": True,
        "production_mission_generation_remains_false": True,
        "final_mission_copy_absent": True,
        "canonical_graph_mutation_remains_false": True,
        "oracle_metrics_written_back_to_selector_input": False,
    }
    for key, expected in required_guardrails.items():
        if guardrail.get(key) != expected:
            errors.append(f"/guardrail_summary/{key} must be {expected}")

    deterministic = payload.get("determinism_summary", {})
    if deterministic.get("deterministic_rerun_matched") is not True:
        errors.append("/determinism_summary/deterministic_rerun_matched must be true")
    if deterministic.get("pack_signature_sha256") != deterministic.get("rerun_signature_sha256"):
        errors.append("/determinism_summary signatures must match")

    expected_modes = {
        "rank_1_pack",
        "top_3_portfolio_pack",
        "top_10_portfolio_pack",
        "diagnostic_biased_pack",
        "experience_balanced_pack",
    }
    observed_modes = {pack.get("construction_mode") for pack in payload.get("packs", [])}
    if not expected_modes.issubset(observed_modes):
        errors.append("/packs must cover all required construction modes")

    for index, pack in enumerate(payload.get("packs", [])):
        label = f"/packs/{index}"
        source_ids = pack.get("source_opportunity_ids", [])
        if not source_ids:
            errors.append(f"{label}/source_opportunity_ids must not be empty")
        songs = pack.get("songs", [])
        if pack.get("song_count") != len(songs):
            errors.append(f"{label}/song_count must equal songs length")
        if len({song.get("song_id") for song in songs}) != len(songs):
            errors.append(f"{label}/songs must not repeat song_id values")
        counts = Counter(song.get("hidden_oracle_reaction") for song in songs)
        expected_counts = {
            "love_count": counts.get("love", 0),
            "like_count": counts.get("like", 0),
            "ok_count": counts.get("ok", 0),
            "dont_like_count": counts.get("dont_like", 0),
            "unknown_count": counts.get("unknown", 0),
        }
        for key, expected in expected_counts.items():
            if pack.get(key) != expected:
                errors.append(f"{label}/{key} must equal song reaction count")
        policy = pack.get("construction_policy", {})
        if policy.get("selection_input_reaction_labels_visible") is not False:
            errors.append(f"{label}/construction_policy must hide reaction labels during selection")
        if policy.get("optimized_for_hidden_reaction_labels") is not False:
            errors.append(f"{label}/construction_policy must not optimize by hidden reactions")
        for song_index, song in enumerate(songs):
            song_label = f"{label}/songs/{song_index}"
            if not song.get("source_opportunity_id"):
                errors.append(f"{song_label}/source_opportunity_id must be present")
            if song.get("source_opportunity_id") not in source_ids:
                errors.append(f"{song_label}/source_opportunity_id must reference source_opportunity_ids")
            if not song.get("why_selected"):
                errors.append(f"{song_label}/why_selected must be present")
            if song.get("hidden_oracle_reaction") not in {"love", "like", "ok", "dont_like", "unknown"}:
                errors.append(f"{song_label}/hidden_oracle_reaction must be normalized")

    source_refs = payload.get("source_refs", {})
    expanded_ref = source_refs.get("expanded_visible_profile_inputs_ref")
    if expanded_ref != str(PHASE1E_EXPANDED_VISIBLE.relative_to(REPO_ROOT)):
        errors.append("/source_refs/expanded_visible_profile_inputs_ref must point to Phase 1E visible input")
    if expanded_ref and Path(expanded_ref).name:
        expanded_path = REPO_ROOT / expanded_ref
        if expanded_path.exists():
            expanded = load_json(expanded_path)
            for key, _child, pointer in iter_dict_items(expanded):
                if str(key) in {
                    "overall_smell_score",
                    "hidden_oracle_reaction",
                    "oracle_metrics",
                }:
                    errors.append(f"expanded visible fixture contains post-selection field at {pointer}")

    selector_refs = {
        pack.get("source_selector_output_ref")
        for pack in payload.get("packs", [])
        if isinstance(pack.get("source_selector_output_ref"), str)
    }
    for selector_ref in sorted(selector_refs):
        selector_path = REPO_ROOT / selector_ref
        if not selector_path.exists():
            errors.append(f"selector output missing: {selector_ref}")
            continue
        selector = load_json(selector_path)
        errors.extend(
            f"{selector_ref} {error}"
            for error in phase1f_selector_leak_errors(selector)
        )

    return errors


def validate_phase1f_outputs(result: ValidationResult) -> None:
    required_files = [
        PHASE1F_SCHEMA,
        PHASE1F_RESULTS,
        PHASE1F_SUMMARY_MD,
        PHASE1F_GUARDRAIL_MD,
    ]
    missing = [path for path in required_files if not path.exists()]
    if missing:
        for path in missing:
            result.fail(f"missing Phase 1F output: {path.relative_to(REPO_ROOT)}")
        return

    payload = load_json(PHASE1F_RESULTS)
    errors = phase1f_result_errors(payload)
    for error in errors:
        result.fail(f"phase1f song-pack simulation {error}")

    if not errors:
        result.pass_("Phase 1F song-pack simulation output validated")

    pack_card_refs = payload.get("human_llm_smell_test_packet_refs", [])
    if len(pack_card_refs) != 3:
        result.fail("/phase1f/human_llm_smell_test_packet_refs must include one card file per profile")
    for ref in pack_card_refs:
        if not (REPO_ROOT / ref).exists():
            result.fail(f"Phase 1F pack card missing: {ref}")

    negative_expectations = [
        (
            "constructor input includes hidden reaction labels",
            PHASE1F_NEGATIVE_DIR / "constructor_input_hidden_reaction_labels_v0_1.json",
            phase1f_constructor_input_errors,
        ),
        (
            "selector output includes hidden reaction labels",
            PHASE1F_NEGATIVE_DIR / "selector_output_hidden_reaction_labels_v0_1.json",
            phase1f_selector_leak_errors,
        ),
        (
            "production mission generation allowed",
            PHASE1F_NEGATIVE_DIR / "pack_production_generation_true_v0_1.json",
            phase1f_result_errors,
        ),
        (
            "pack includes final mission copy",
            PHASE1F_NEGATIVE_DIR / "pack_final_mission_copy_v0_1.json",
            phase1f_result_errors,
        ),
        (
            "pack has no source opportunity refs",
            PHASE1F_NEGATIVE_DIR / "pack_missing_source_opportunity_refs_v0_1.json",
            phase1f_result_errors,
        ),
        (
            "pack song lacks why_selected",
            PHASE1F_NEGATIVE_DIR / "pack_song_missing_why_selected_v0_1.json",
            phase1f_result_errors,
        ),
        (
            "same seed produces different pack",
            PHASE1F_NEGATIVE_DIR / "pack_determinism_mismatch_v0_1.json",
            lambda payload: []
            if payload.get("deterministic_rerun_matched") is True
            else ["deterministic_rerun_matched must be true"],
        ),
    ]
    for label, path, validator in negative_expectations:
        if not path.exists():
            result.fail(f"missing Phase 1F negative fixture: {path.relative_to(REPO_ROOT)}")
            continue
        negative_errors = validator(load_json(path))
        if negative_errors:
            result.pass_(f"Phase 1F negative fixture rejected: {label}")
        else:
            result.fail(f"Phase 1F negative fixture unexpectedly passed: {label}")

    if result.ok:
        result.pass_("Phase 1F offline song-pack smell-test gates passed")


PHASE1G_MISSION_TYPES = {
    "archetype_depth_test",
    "artist_depth_test",
    "album_container_test",
    "boundary_test",
    "bridge_test",
    "context_dependence_test",
}
PHASE1G_POLICIES = {
    "mission_type_native_policy",
    "experience_balanced_policy",
    "diagnostic_biased_policy",
}


def phase1g_result_errors(payload: dict[str, Any]) -> list[str]:
    errors = schema_errors(PHASE1G_SCHEMA, payload)
    probe = ValidationResult()
    expect_false_flags(payload, probe, "phase1g construction policy output")
    expect_no_forbidden_content_keys(payload, probe, "phase1g construction policy output")
    expect_no_personal_private_labels(payload, probe, "phase1g construction policy output")
    errors.extend(probe.failures)

    if payload.get("phase") != "mission_type_construction_policy_hardening_llm_review":
        errors.append("/phase must be mission_type_construction_policy_hardening_llm_review")
    if payload.get("selector_may_read_hidden_oracle") is not False:
        errors.append("/selector_may_read_hidden_oracle must be false")
    if payload.get("constructor_optimized_by_hidden_reaction_labels") is not False:
        errors.append("/constructor_optimized_by_hidden_reaction_labels must be false")
    if payload.get("oracle_evaluation_fed_back_into_selector") is not False:
        errors.append("/oracle_evaluation_fed_back_into_selector must be false")
    if payload.get("final_mission_construction_status") != "not_in_scope":
        errors.append("/final_mission_construction_status must be not_in_scope")

    run_matrix = payload.get("run_matrix", {})
    packs = payload.get("packs", [])
    if run_matrix.get("completed_construction_attempt_count") != len(packs):
        errors.append("/run_matrix/completed_construction_attempt_count must equal pack count")
    if run_matrix.get("completed_construction_attempt_count") != 162:
        errors.append("/run_matrix/completed_construction_attempt_count must be the full 162-pack matrix")
    if run_matrix.get("alpha_v0_2_pack_size") != 6:
        errors.append("/run_matrix/alpha_v0_2_pack_size must be 6")
    if set(run_matrix.get("mission_types", [])) != PHASE1G_MISSION_TYPES:
        errors.append("/run_matrix/mission_types must match Phase 1G target mission types")
    if set(run_matrix.get("construction_policies", [])) != PHASE1G_POLICIES:
        errors.append("/run_matrix/construction_policies must match Phase 1G policies")

    observed_matrix = {
        (pack.get("profile_id"), pack.get("sampling_mode"), pack.get("mission_type"), pack.get("construction_policy"))
        for pack in packs
    }
    expected_matrix = {
        (profile_id, sampling_mode, mission_type, policy)
        for profile_id in {"public_profile_01", "public_profile_05", "public_profile_06"}
        for sampling_mode in {"profile_weighted_balanced", "edge_heavy", "song_heavy"}
        for mission_type in PHASE1G_MISSION_TYPES
        for policy in PHASE1G_POLICIES
    }
    if observed_matrix != expected_matrix:
        errors.append("Phase 1G packs must cover 3 profiles x 3 modes x 6 mission types x 3 policies")

    guardrail = payload.get("guardrail_summary", {})
    expected_guardrails = {
        "selector_did_not_read_hidden_oracle": True,
        "constructor_selection_pool_reaction_labels_visible": False,
        "constructor_selection_pool_hidden_reason_tags_visible": False,
        "hidden_reactions_joined_only_after_pack_construction": True,
        "runtime_remains_false": True,
        "production_mission_generation_remains_false": True,
        "final_mission_copy_absent": True,
        "canonical_graph_mutation_remains_false": True,
        "oracle_metrics_written_back_to_selector_input": False,
        "llm_packet_review_only": True,
    }
    for key, expected in expected_guardrails.items():
        if guardrail.get(key) != expected:
            errors.append(f"/guardrail_summary/{key} must be {expected}")

    determinism = payload.get("determinism_summary", {})
    if determinism.get("deterministic_rerun_matched") is not True:
        errors.append("/determinism_summary/deterministic_rerun_matched must be true")
    if determinism.get("pack_signature_sha256") != determinism.get("rerun_signature_sha256"):
        errors.append("/determinism_summary signatures must match")

    alpha_count = 0
    alpha_preferred_count = 0
    proxy_count = 0
    for index, pack in enumerate(packs):
        label = f"/packs/{index}"
        if pack.get("song_count") != 6 or len(pack.get("songs", [])) != 6:
            errors.append(f"{label} must contain exactly six songs")
        if not pack.get("source_opportunity_ids"):
            errors.append(f"{label}/source_opportunity_ids must not be empty")
        if set(pack.get("source_mission_types", [])) & {"initial_profile_survey", "family_survey", "archetype_survey"}:
            errors.append(f"{label}/source_mission_types must not use broad survey controls in Phase 1G")
        if pack.get("source_opportunity_exact_match") is False:
            proxy_count += 1
        if pack.get("alpha_plausible"):
            alpha_count += 1
        if pack.get("alpha_preferred"):
            alpha_preferred_count += 1
        counts = Counter(song.get("hidden_oracle_reaction") for song in pack.get("songs", []))
        expected_counts = {
            "love_count": counts.get("love", 0),
            "like_count": counts.get("like", 0),
            "ok_count": counts.get("ok", 0),
            "dont_like_count": counts.get("dont_like", 0),
            "unknown_count": counts.get("unknown", 0),
        }
        for key, expected in expected_counts.items():
            if pack.get(key) != expected:
                errors.append(f"{label}/{key} must equal song reaction count")
        if not isinstance(pack.get("generic_overall_smell_score"), (int, float)):
            errors.append(f"{label}/generic_overall_smell_score must be numeric")
        if not isinstance(pack.get("mission_type_adjusted_smell_score"), (int, float)):
            errors.append(f"{label}/mission_type_adjusted_smell_score must be numeric")
        if pack.get("non_failure_rate", 0) >= 0.67 and pack.get("negative_hit_rate", 1) <= 0.33 and not pack.get("too_random_flag"):
            if pack.get("anchor_count", 0) >= 1 and pack.get("probe_count", 0) + pack.get("comparator_count", 0) >= 1:
                if not pack.get("alpha_plausible"):
                    errors.append(f"{label}/alpha_plausible should pass gate criteria")
        for song_index, song in enumerate(pack.get("songs", [])):
            song_label = f"{label}/songs/{song_index}"
            if not song.get("why_selected"):
                errors.append(f"{song_label}/why_selected must be present")
            if not song.get("source_opportunity_id"):
                errors.append(f"{song_label}/source_opportunity_id must be present")
            if song.get("hidden_oracle_reaction") not in {"love", "like", "ok", "dont_like", "unknown"}:
                errors.append(f"{song_label}/hidden_oracle_reaction must be normalized")

    aggregate = payload.get("aggregate_pack_metrics", {})
    if aggregate.get("alpha_plausible_count") != alpha_count:
        errors.append("/aggregate_pack_metrics/alpha_plausible_count must equal pack count")
    if aggregate.get("alpha_preferred_count") != alpha_preferred_count:
        errors.append("/aggregate_pack_metrics/alpha_preferred_count must equal pack count")
    if aggregate.get("proxy_source_opportunity_pack_count") != proxy_count:
        errors.append("/aggregate_pack_metrics/proxy_source_opportunity_pack_count must equal pack count")

    llm_summary = payload.get("llm_packet_summary", {})
    for key in ["llm_sanity_review_packet_json_ref", "llm_sanity_review_packet_md_ref"]:
        ref = llm_summary.get(key)
        if not isinstance(ref, str) or not (REPO_ROOT / ref).exists():
            errors.append(f"/llm_packet_summary/{key} must point to an existing packet")
    example_count = llm_summary.get("llm_sanity_review_example_count")
    if not isinstance(example_count, int) or not 24 <= example_count <= 36:
        errors.append("/llm_packet_summary/llm_sanity_review_example_count must be 24..36")

    if PHASE1G_LLM_PACKET_JSON.exists():
        llm_packet = load_json(PHASE1G_LLM_PACKET_JSON)
        if llm_packet.get("llm_packet_is_review_only") is not True:
            errors.append("/llm_packet/llm_packet_is_review_only must be true")
        if llm_packet.get("example_count") != example_count:
            errors.append("/llm_packet/example_count must match result summary")
        if llm_packet.get("production_mission_generation_allowed") is not False:
            errors.append("/llm_packet/production_mission_generation_allowed must be false")
        for index, example in enumerate(llm_packet.get("examples", [])):
            if len(example.get("review_questions", [])) != 7:
                errors.append(f"/llm_packet/examples/{index}/review_questions must include 7 questions")
            if "hidden_lane" in json.dumps(example).lower():
                errors.append(f"/llm_packet/examples/{index} must not expose hidden lane internals")

    source_refs = {
        pack.get("source_selector_output_ref")
        for pack in packs
        if isinstance(pack.get("source_selector_output_ref"), str)
    }
    for selector_ref in sorted(source_refs):
        selector_path = REPO_ROOT / selector_ref
        if not selector_path.exists():
            errors.append(f"selector output missing: {selector_ref}")
            continue
        selector = load_json(selector_path)
        errors.extend(
            f"{selector_ref} {error}"
            for error in phase1f_selector_leak_errors(selector)
        )

    return errors


def validate_phase1g_outputs(result: ValidationResult) -> None:
    required_files = [
        PHASE1G_SCHEMA,
        PHASE1G_RESULTS,
        PHASE1G_SUMMARY_MD,
        PHASE1G_GUARDRAIL_MD,
        PHASE1G_LLM_PACKET_JSON,
        PHASE1G_LLM_PACKET_MD,
    ]
    missing = [path for path in required_files if not path.exists()]
    if missing:
        for path in missing:
            result.fail(f"missing Phase 1G output: {path.relative_to(REPO_ROOT)}")
        return

    payload = load_json(PHASE1G_RESULTS)
    errors = phase1g_result_errors(payload)
    for error in errors:
        result.fail(f"phase1g construction policy output {error}")
    if not errors:
        result.pass_("Phase 1G construction policy output validated")

    card_refs = payload.get("human_pack_card_refs", [])
    if len(card_refs) != 3:
        result.fail("/phase1g/human_pack_card_refs must include one card file per profile")
    for ref in card_refs:
        if not (REPO_ROOT / ref).exists():
            result.fail(f"Phase 1G pack card missing: {ref}")

    negative_expectations = [
        (
            "constructor input includes hidden reaction labels",
            PHASE1G_NEGATIVE_DIR / "constructor_input_hidden_reaction_labels_v0_1.json",
            phase1f_constructor_input_errors,
        ),
        (
            "selector output includes hidden reaction labels",
            PHASE1G_NEGATIVE_DIR / "selector_output_hidden_reaction_labels_v0_1.json",
            phase1f_selector_leak_errors,
        ),
        (
            "production mission generation allowed",
            PHASE1G_NEGATIVE_DIR / "pack_production_generation_true_v0_1.json",
            phase1g_result_errors,
        ),
        (
            "pack includes final mission copy",
            PHASE1G_NEGATIVE_DIR / "pack_final_mission_copy_v0_1.json",
            phase1g_result_errors,
        ),
        (
            "pack has no source opportunity refs",
            PHASE1G_NEGATIVE_DIR / "pack_missing_source_opportunity_refs_v0_1.json",
            phase1g_result_errors,
        ),
        (
            "pack song lacks why_selected",
            PHASE1G_NEGATIVE_DIR / "pack_song_missing_why_selected_v0_1.json",
            phase1g_result_errors,
        ),
        (
            "same seed produces different pack",
            PHASE1G_NEGATIVE_DIR / "pack_determinism_mismatch_v0_1.json",
            lambda payload: []
            if payload.get("deterministic_rerun_matched") is True
            else ["deterministic_rerun_matched must be true"],
        ),
    ]
    for label, path, validator in negative_expectations:
        if not path.exists():
            result.fail(f"missing Phase 1G negative fixture: {path.relative_to(REPO_ROOT)}")
            continue
        negative_errors = validator(load_json(path))
        if negative_errors:
            result.pass_(f"Phase 1G negative fixture rejected: {label}")
        else:
            result.fail(f"Phase 1G negative fixture unexpectedly passed: {label}")

    if result.ok:
        result.pass_("Phase 1G construction policy and LLM review gates passed")


def validate_prototype_selector_output(
    selector: dict[str, Any],
    result: ValidationResult,
    label: str,
    expect_early_stop: bool,
) -> None:
    validate_selector_domain(selector, result)
    audit = selector.get("selector_audit", {})
    if audit.get("final_heap_size") != 25:
        result.fail(f"{label} must return a full top-25 heap")
    if audit.get("candidate_blobs_pruned", 0) <= 0:
        result.fail(f"{label} must prove pruning occurred")
    if audit.get("early_stop_applied") is not expect_early_stop:
        result.fail(f"{label} early_stop_applied must be {expect_early_stop}")
    if expect_early_stop and not audit.get("mission_types_skipped_by_early_stop"):
        result.fail(f"{label} must record mission types skipped by early stop")
    if not expect_early_stop:
        considered = audit.get("mission_types_considered", [])
        if set(considered) != set(EXPECTED_MISSION_TYPES):
            result.fail(f"{label} must consider every approved mission type in coverage mode")

    if result.ok:
        result.pass_(f"{label} prototype selector gates passed")


def validate_contracts() -> ValidationResult:
    result = ValidationResult()

    registry = validate_json_schema(REGISTRY_SCHEMA, REGISTRY_FIXTURE, "mission type registry", result)
    evidence = validate_json_schema(EVIDENCE_SCHEMA, EVIDENCE_FIXTURE, "evidence rollup", result)
    opportunity = validate_json_schema(OPPORTUNITY_SCHEMA, OPPORTUNITY_FIXTURE, "mission opportunity blob", result)
    selector = validate_json_schema(SELECTOR_SCHEMA, SELECTOR_FIXTURE, "selector output", result)
    hidden_oracle_evaluation = validate_json_schema(
        HIDDEN_ORACLE_EVALUATION_SCHEMA,
        HIDDEN_ORACLE_EVALUATION_FIXTURE,
        "hidden oracle evaluation design",
        result,
    )
    rank_usefulness_analysis = validate_json_schema(
        RANK_USEFULNESS_ANALYSIS_SCHEMA,
        RANK_USEFULNESS_ANALYSIS_FIXTURE,
        "hidden oracle rank-usefulness analysis",
        result,
    )
    prototype_selector = validate_json_schema(
        SELECTOR_SCHEMA,
        PROTOTYPE_SELECTOR_FIXTURE,
        "prototype selector output",
        result,
    )
    prototype_early_stop_selector = validate_json_schema(
        SELECTOR_SCHEMA,
        PROTOTYPE_EARLY_STOP_FIXTURE,
        "prototype early-stop selector output",
        result,
    )
    scenarios = load_json(SCENARIO_FIXTURE)

    validate_registry_domain(registry, result)
    validate_evidence_domain(evidence, result)
    validate_opportunity_domain(opportunity, result)
    if result.ok:
        result.pass_("mission opportunity blob gates passed")
    validate_selector_domain(selector, result)
    validate_scenario_fixture(scenarios, result)
    validate_hidden_oracle_evaluation_design(hidden_oracle_evaluation, result)
    validate_rank_usefulness_analysis(rank_usefulness_analysis, result)
    validate_phase1e_outputs(result)
    validate_phase1f_outputs(result)
    validate_phase1g_outputs(result)
    validate_prototype_selector_output(prototype_selector, result, "coverage selector output", False)
    validate_prototype_selector_output(prototype_early_stop_selector, result, "early-stop selector output", True)
    validate_profile_simulation_fixtures(result)
    validate_type_files(result)

    for label, schema_path, document_path in NEGATIVE_CASES:
        expect_schema_failure(label, schema_path, document_path, result)

    return result


def main() -> int:
    result = validate_contracts()
    for message in result.passes:
        print(f"PASS {message}")
    for message in result.failures:
        print(f"FAIL {message}", file=sys.stderr)
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
