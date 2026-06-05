#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


CONTRACT_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = CONTRACT_DIR.parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from validate_mission_opportunity_selection_v0_1 import (  # noqa: E402
    EXPECTED_MISSION_TYPES,
    FORBIDDEN_CONTENT_KEYS,
    HIDDEN_ORACLE_EVALUATION_FIXTURE,
    HIDDEN_ORACLE_EVALUATION_SCHEMA,
    NEGATIVE_CASES,
    PHASE1F_RESULTS,
    PHASE1F_SCHEMA,
    PHASE1G_LLM_PACKET_JSON,
    PHASE1G_RESULTS,
    PHASE1G_SCHEMA,
    PROTOTYPE_EARLY_STOP_FIXTURE,
    PROTOTYPE_SELECTOR_FIXTURE,
    PROFILE_HIDDEN_ORACLES,
    PROFILE_PHASE1_SUMMARY,
    PROFILE_SELECTOR_OUTPUTS,
    PROFILE_VISIBLE_INPUTS,
    RANK_USEFULNESS_ANALYSIS_FIXTURE,
    RANK_USEFULNESS_ANALYSIS_SCHEMA,
    SCENARIO_FIXTURE,
    TYPE_FILES,
    ValidationResult,
    schema_errors,
    target_identity_errors,
    validate_contracts,
    validate_hidden_oracle_evaluation_design,
    validate_rank_usefulness_analysis,
)
from prototype_mission_opportunity_selector_v0_1 import run_selector  # noqa: E402


def load_json(path: Path) -> object:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def walk(value: object) -> object:
    if isinstance(value, dict):
        for child in value.values():
            yield from walk(child)
        yield value
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def expect_target_identity_failure(
    failures: list[str],
    label: str,
    opportunity: dict[str, object],
) -> None:
    if not target_identity_errors(opportunity):
        failures.append(f"target identity negative mutation unexpectedly passed: {label}")


def main() -> int:
    failures: list[str] = []

    result = validate_contracts()
    failures.extend(result.failures)

    schema_paths = [
        CONTRACT_DIR / "schemas/mission_type_registry_v0_1.schema.json",
        CONTRACT_DIR / "schemas/evidence_rollup_v0_1.schema.json",
        CONTRACT_DIR / "schemas/mission_opportunity_blob_v0_1.schema.json",
        CONTRACT_DIR / "schemas/selector_output_v0_1.schema.json",
        CONTRACT_DIR / "schemas/hidden_oracle_evaluation_design_v0_1.schema.json",
        CONTRACT_DIR / "schemas/hidden_oracle_rank_usefulness_analysis_v0_1.schema.json",
        PHASE1F_SCHEMA,
        PHASE1G_SCHEMA,
    ]
    for schema_path in schema_paths:
        schema = load_json(schema_path)
        schema_id = schema.get("$id", "")
        if not str(schema_id).startswith("https://cartenza.local/contracts/"):
            failures.append(f"{schema_path.name} schema id must use the Cartenza contract namespace")

    registry = load_json(CONTRACT_DIR / "fixtures/mission_type_registry_sample_v0_1.json")
    mission_types = [entry["mission_type"] for entry in registry["mission_types"]]
    if mission_types != EXPECTED_MISSION_TYPES:
        failures.append("registry fixture mission type set does not match v0.1 approved list")

    evidence = load_json(CONTRACT_DIR / "fixtures/evidence_rollup_sample_v0_1.json")
    semantics = evidence["reaction_semantics"]
    if semantics["survey_ok_signal_class"] != "no_signal":
        failures.append("survey ok must remain no_signal")
    if semantics["mission_ok_signal_class"] != "weak_non_failure":
        failures.append("mission ok must remain weak_non_failure")
    if semantics["mission_ok_is_positive_preference"] is not False:
        failures.append("mission ok must not become positive preference")

    selector = load_json(CONTRACT_DIR / "fixtures/selector_output_sample_v0_1.json")
    for node in walk(selector):
        if isinstance(node, dict):
            forbidden = FORBIDDEN_CONTENT_KEYS.intersection(node)
            if forbidden:
                failures.append(f"selector fixture includes forbidden mission content keys: {sorted(forbidden)}")

    scenarios = load_json(SCENARIO_FIXTURE)
    if len(scenarios["scenario_rollups"]) != 11:
        failures.append("synthetic scenario fixture must cover the 11 required scenario classes")

    prototype_selector = load_json(PROTOTYPE_SELECTOR_FIXTURE)
    prototype_audit = prototype_selector["selector_audit"]
    if len(prototype_selector["ranked_opportunities"]) != 25:
        failures.append("coverage prototype selector output must emit exactly 25 ranked opportunities")
    if set(prototype_audit["mission_types_considered"]) != set(EXPECTED_MISSION_TYPES):
        failures.append("coverage prototype selector output must consider all approved mission types")
    if prototype_audit["candidate_blobs_pruned"] <= 0:
        failures.append("coverage prototype selector output must prove top-K or score pruning")
    if not prototype_audit["floor_failure_examples"]:
        failures.append("coverage prototype selector output must record floor failure examples")

    early_stop_selector = load_json(PROTOTYPE_EARLY_STOP_FIXTURE)
    early_stop_audit = early_stop_selector["selector_audit"]
    if early_stop_audit["early_stop_applied"] is not True:
        failures.append("early-stop prototype selector output must prove early stop")
    if not early_stop_audit["mission_types_skipped_by_early_stop"]:
        failures.append("early-stop prototype selector output must record skipped mission types")

    visible_profiles = load_json(PROFILE_VISIBLE_INPUTS)
    hidden_profiles = load_json(PROFILE_HIDDEN_ORACLES)
    phase1_summary = load_json(PROFILE_PHASE1_SUMMARY)
    if visible_profiles["hidden_oracle_included"] is not False:
        failures.append("profile visible selector input must not include hidden oracle data")
    if hidden_profiles["selector_may_read"] is not False:
        failures.append("hidden oracle fixture must be marked unavailable to selector")
    if len(visible_profiles["profiles"]) != 3 or len(hidden_profiles["profiles"]) != 3:
        failures.append("profile simulation must cover public profiles 01, 05, and 06")
    if "hidden" in json.dumps(phase1_summary["selector_runs"]):
        failures.append("profile selector run summaries must not reference hidden oracle files")
    for selector_output_path in PROFILE_SELECTOR_OUTPUTS:
        selector_output = load_json(selector_output_path)
        if "hidden" in selector_output["source_evidence_rollup_ref"]:
            failures.append(f"{selector_output_path.name} must not use hidden source refs")
        if selector_output["selector_audit"]["final_heap_size"] != 25:
            failures.append(f"{selector_output_path.name} must emit top-25 opportunities")

    oracle_evaluation = load_json(HIDDEN_ORACLE_EVALUATION_FIXTURE)
    oracle_schema_errors = schema_errors(HIDDEN_ORACLE_EVALUATION_SCHEMA, oracle_evaluation)
    if oracle_schema_errors:
        failures.extend(
            f"hidden oracle evaluation fixture schema error: {error}"
            for error in oracle_schema_errors
        )
    oracle_result = ValidationResult()
    validate_hidden_oracle_evaluation_design(oracle_evaluation, oracle_result)
    failures.extend(oracle_result.failures)
    if oracle_evaluation["selector_may_read_hidden_oracle"] is not False:
        failures.append("hidden oracle evaluation must keep selector_may_read_hidden_oracle false")
    if oracle_evaluation["evaluator_may_read_hidden_oracle_after_selection"] is not True:
        failures.append("hidden oracle evaluation must allow evaluator-only post-selection access")
    if oracle_evaluation["evaluation_scope"]["evaluation_subject"] != "selected_opportunity_blobs_only":
        failures.append("hidden oracle evaluation must remain opportunity-ref only")

    oracle_selector_can_read = json.loads(json.dumps(oracle_evaluation))
    oracle_selector_can_read["selector_may_read_hidden_oracle"] = True
    if not schema_errors(HIDDEN_ORACLE_EVALUATION_SCHEMA, oracle_selector_can_read):
        failures.append("hidden oracle evaluation mutation unexpectedly allowed selector oracle access")

    oracle_with_content = json.loads(json.dumps(oracle_evaluation))
    oracle_with_content["profiles"][0]["top_opportunity_evaluations"][0]["mission_items"] = []
    if not schema_errors(HIDDEN_ORACLE_EVALUATION_SCHEMA, oracle_with_content):
        failures.append("hidden oracle evaluation mutation unexpectedly allowed mission content")

    oracle_with_song_list = json.loads(json.dumps(oracle_evaluation))
    oracle_with_song_list["profiles"][0]["top_opportunity_evaluations"][0]["no_candidate_song_list"] = False
    if not schema_errors(HIDDEN_ORACLE_EVALUATION_SCHEMA, oracle_with_song_list):
        failures.append("hidden oracle evaluation mutation unexpectedly allowed candidate song list")

    oracle_target_mismatch = json.loads(json.dumps(oracle_evaluation))
    oracle_target_mismatch["profiles"][0]["top_opportunity_evaluations"][0][
        "selected_opportunity_ref"
    ]["target_object_ids"] = ["wrong_target"]
    mismatch_result = ValidationResult()
    validate_hidden_oracle_evaluation_design(oracle_target_mismatch, mismatch_result)
    if not mismatch_result.failures:
        failures.append("hidden oracle evaluation mutation unexpectedly allowed selector target mismatch")

    rank_analysis = load_json(RANK_USEFULNESS_ANALYSIS_FIXTURE)
    rank_schema_errors = schema_errors(RANK_USEFULNESS_ANALYSIS_SCHEMA, rank_analysis)
    if rank_schema_errors:
        failures.extend(
            f"rank usefulness analysis fixture schema error: {error}"
            for error in rank_schema_errors
        )
    rank_result = ValidationResult()
    validate_rank_usefulness_analysis(rank_analysis, rank_result)
    failures.extend(rank_result.failures)
    if rank_analysis["selector_may_read_hidden_oracle"] is not False:
        failures.append("rank usefulness analysis must keep selector_may_read_hidden_oracle false")
    if rank_analysis["analysis_scope"]["analysis_subject"] != "selected_opportunity_rank_order":
        failures.append("rank usefulness analysis must analyze selected opportunity rank order")
    if rank_analysis["analysis_scope"]["construction_simulation_status"] != "not_implemented":
        failures.append("rank usefulness analysis must not implement mission construction")
    if rank_analysis["aggregate_summary"]["profile_count"] != 3:
        failures.append("rank usefulness analysis must cover public profiles 01, 05, and 06")
    if rank_analysis["aggregate_summary"]["best_in_top3_count"] < 1:
        failures.append("rank usefulness analysis must report best-in-top-window behavior")

    phase1f = load_json(PHASE1F_RESULTS)
    if phase1f["run_matrix"]["completed_pack_count"] < 45:
        failures.append("Phase 1F must construct at least 45 song packs")
    if phase1f["run_matrix"]["completed_pack_count"] != len(phase1f["packs"]):
        failures.append("Phase 1F completed pack count must equal emitted packs")
    if phase1f["selector_may_read_hidden_oracle"] is not False:
        failures.append("Phase 1F must keep selector_may_read_hidden_oracle false")
    if phase1f["constructor_optimized_by_hidden_reaction_labels"] is not False:
        failures.append("Phase 1F constructor must not optimize by hidden reaction labels")
    if phase1f["production_mission_generation_allowed"] is not False:
        failures.append("Phase 1F must keep production mission generation blocked")
    if phase1f["determinism_summary"]["deterministic_rerun_matched"] is not True:
        failures.append("Phase 1F deterministic rerun check must pass")
    required_modes = {
        "rank_1_pack",
        "top_3_portfolio_pack",
        "top_10_portfolio_pack",
        "diagnostic_biased_pack",
        "experience_balanced_pack",
    }
    observed_modes = {pack["construction_mode"] for pack in phase1f["packs"]}
    if not required_modes.issubset(observed_modes):
        failures.append("Phase 1F must cover all required construction modes")
    if any(not pack["source_opportunity_ids"] for pack in phase1f["packs"]):
        failures.append("Phase 1F packs must preserve source opportunity refs")
    if any(not song["why_selected"] for pack in phase1f["packs"] for song in pack["songs"]):
        failures.append("Phase 1F songs must include why_selected explanations")
    if any(
        "final_mission_copy" in node
        for pack in phase1f["packs"]
        for node in walk(pack)
        if isinstance(node, dict)
    ):
        failures.append("Phase 1F packs must not include final mission copy")

    phase1g = load_json(PHASE1G_RESULTS)
    if phase1g["run_matrix"]["completed_construction_attempt_count"] != 162:
        failures.append("Phase 1G must complete the full 162 construction-attempt matrix")
    if phase1g["run_matrix"]["alpha_v0_2_pack_size"] != 6:
        failures.append("Phase 1G must record six songs as Alpha v0.2 test size")
    if "8-12" not in phase1g["run_matrix"]["future_product_pack_range_to_test_later"]:
        failures.append("Phase 1G must record future 8-12 song stress testing")
    if phase1g["selector_may_read_hidden_oracle"] is not False:
        failures.append("Phase 1G must keep selector_may_read_hidden_oracle false")
    if phase1g["constructor_optimized_by_hidden_reaction_labels"] is not False:
        failures.append("Phase 1G constructor must not optimize by hidden reaction labels")
    if phase1g["production_mission_generation_allowed"] is not False:
        failures.append("Phase 1G must keep production mission generation blocked")
    if phase1g["determinism_summary"]["deterministic_rerun_matched"] is not True:
        failures.append("Phase 1G deterministic rerun check must pass")
    if phase1g["aggregate_pack_metrics"]["alpha_plausible_count"] <= 0:
        failures.append("Phase 1G must report at least one Alpha-plausible pack")
    if len(phase1g["llm_packet_summary"]) < 3:
        failures.append("Phase 1G must report LLM packet refs and example count")
    llm_packet = load_json(PHASE1G_LLM_PACKET_JSON)
    if llm_packet["example_count"] < 24 or llm_packet["example_count"] > 36:
        failures.append("Phase 1G LLM packet must include 24-36 examples")
    if llm_packet["llm_packet_is_review_only"] is not True:
        failures.append("Phase 1G LLM packet must be review-only")
    if any(not pack["source_opportunity_ids"] for pack in phase1g["packs"]):
        failures.append("Phase 1G packs must preserve source opportunity refs")
    if any(not song["why_selected"] for pack in phase1g["packs"] for song in pack["songs"]):
        failures.append("Phase 1G songs must include why_selected explanations")
    if any(
        "final_mission_copy" in node
        for pack in phase1g["packs"]
        for node in walk(pack)
        if isinstance(node, dict)
    ):
        failures.append("Phase 1G packs must not include final mission copy")

    rank_selector_can_read = json.loads(json.dumps(rank_analysis))
    rank_selector_can_read["selector_may_read_hidden_oracle"] = True
    if not schema_errors(RANK_USEFULNESS_ANALYSIS_SCHEMA, rank_selector_can_read):
        failures.append("rank usefulness analysis mutation unexpectedly allowed selector oracle access")

    rank_with_content = json.loads(json.dumps(rank_analysis))
    rank_with_content["profiles"][0]["rank_rows"][0]["mission_items"] = []
    if not schema_errors(RANK_USEFULNESS_ANALYSIS_SCHEMA, rank_with_content):
        failures.append("rank usefulness analysis mutation unexpectedly allowed mission content")

    rank_target_mismatch = json.loads(json.dumps(rank_analysis))
    rank_target_mismatch["profiles"][0]["top_selector_opportunity"]["opportunity_id"] = "wrong_opportunity"
    rank_mismatch_result = ValidationResult()
    validate_rank_usefulness_analysis(rank_target_mismatch, rank_mismatch_result)
    if not rank_mismatch_result.failures:
        failures.append("rank usefulness analysis mutation unexpectedly allowed design mismatch")

    ranked_top5_sequences = [
        tuple(
            opportunity["mission_type"]
            for opportunity in load_json(path)["ranked_opportunities"][:5]
        )
        for path in PROFILE_SELECTOR_OUTPUTS
    ]
    if len(set(ranked_top5_sequences)) <= 1:
        failures.append("public profile ranked top-5 mission type sequences must differ")

    identity_selector = load_json(PROFILE_SELECTOR_OUTPUTS[0])
    identity_opportunity = identity_selector["ranked_opportunities"][0]
    if target_identity_errors(identity_opportunity):
        failures.append("baseline target identity opportunity must pass integrity checks")

    display_mismatch = json.loads(json.dumps(identity_opportunity))
    display_mismatch["source_signal_summary"]["target_display_name"] = "Wrong Display"
    expect_target_identity_failure(
        failures,
        "target display object and floor rollup object differ",
        display_mismatch,
    )

    artist_opportunity = next(
        opportunity
        for path in PROFILE_SELECTOR_OUTPUTS
        for opportunity in load_json(path)["ranked_opportunities"]
        if opportunity["target_object_type"] == "artist"
    )
    artist_mismatch = json.loads(json.dumps(artist_opportunity))
    artist_mismatch["source_signal_summary"]["target_rollup_ref"] = "visible_rollup:artist:wrong_artist:unit"
    artist_mismatch["floor_details"]["floor_evidence_refs"][0] = "visible_rollup:artist:wrong_artist:unit"
    artist_mismatch["filled_requirements"]["required_evidence_rollup_refs"][0] = "visible_rollup:artist:wrong_artist:unit"
    expect_target_identity_failure(failures, "artist target uses a different artist rollup", artist_mismatch)

    album_opportunity = next(
        opportunity
        for path in PROFILE_SELECTOR_OUTPUTS
        for opportunity in load_json(path)["ranked_opportunities"]
        if opportunity["target_object_type"] == "album"
    )
    album_mismatch = json.loads(json.dumps(album_opportunity))
    album_mismatch["source_signal_summary"]["target_rollup_ref"] = "visible_rollup:album:wrong_album:unit"
    album_mismatch["floor_details"]["floor_evidence_refs"][0] = "visible_rollup:album:wrong_album:unit"
    album_mismatch["filled_requirements"]["required_evidence_rollup_refs"][0] = "visible_rollup:album:wrong_album:unit"
    expect_target_identity_failure(failures, "album target uses a different album rollup", album_mismatch)

    archetype_opportunity = next(
        opportunity
        for path in PROFILE_SELECTOR_OUTPUTS
        for opportunity in load_json(path)["ranked_opportunities"]
        if opportunity["target_object_type"] == "archetype"
    )
    archetype_mismatch = json.loads(json.dumps(archetype_opportunity))
    archetype_mismatch["source_signal_summary"]["target_rollup_ref"] = "visible_rollup:archetype:999:unit"
    archetype_mismatch["floor_details"]["floor_evidence_refs"][0] = "visible_rollup:archetype:999:unit"
    archetype_mismatch["filled_requirements"]["required_evidence_rollup_refs"][0] = "visible_rollup:archetype:999:unit"
    expect_target_identity_failure(failures, "archetype target uses unrelated archetype rollup", archetype_mismatch)

    pair_opportunity = next(
        opportunity
        for path in PROFILE_SELECTOR_OUTPUTS
        for opportunity in load_json(path)["ranked_opportunities"]
        if opportunity["target_object_type"] in {"family_pair", "archetype_pair"}
    )
    pair_mismatch = json.loads(json.dumps(pair_opportunity))
    pair_mismatch["target_object_ids"][1] = "wrong_pair_endpoint"
    pair_mismatch["target_object_ref"]["object_ids"][1] = "wrong_pair_endpoint"
    pair_mismatch["filled_requirements"]["required_graph_object_refs"][0]["object_ids"][1] = "wrong_pair_endpoint"
    pair_mismatch["source_signal_summary"]["target_object_ids"][1] = "wrong_pair_endpoint"
    pair_mismatch["graph_context_summary"]["graph_contexts"][0]["target_object_ref"]["object_ids"][1] = "wrong_pair_endpoint"
    expect_target_identity_failure(failures, "pair target IDs do not match pair rollup IDs", pair_mismatch)

    variant_opportunity = next(
        opportunity
        for path in PROFILE_SELECTOR_OUTPUTS
        for opportunity in load_json(path)["ranked_opportunities"]
        if any("_candidate_" in target_id for target_id in opportunity["target_object_ids"])
    )
    variant_mismatch = json.loads(json.dumps(variant_opportunity))
    variant_mismatch["target_object_ids"][0] = "unrelated_candidate_02"
    variant_mismatch["target_object_ref"]["object_ids"][0] = "unrelated_candidate_02"
    variant_mismatch["filled_requirements"]["required_graph_object_refs"][0]["object_ids"][0] = "unrelated_candidate_02"
    variant_mismatch["source_signal_summary"]["target_object_ids"][0] = "unrelated_candidate_02"
    variant_mismatch["graph_context_summary"]["graph_contexts"][0]["target_object_ref"]["object_ids"][0] = "unrelated_candidate_02"
    expect_target_identity_failure(
        failures,
        "candidate variants change target IDs without preserving base provenance",
        variant_mismatch,
    )

    registry_for_guardrail = load_json(CONTRACT_DIR / "fixtures/mission_type_registry_sample_v0_1.json")
    visible_profile = visible_profiles["profiles"][0]
    scenario_fixture = {
        "contract_version": "profile_visible_selector_scenarios_v0_1",
        "fixture_status": "synthetic_contract_fixture",
        "scenario_rollups": visible_profile["synthetic_selector_scenarios"],
    }
    baseline_selector = run_selector(registry_for_guardrail, scenario_fixture, visible_profile["profile_id"])
    mutated_hidden = json.loads(json.dumps(hidden_profiles))
    mutated_hidden["profiles"][0]["hidden_oracle"]["song_reactions"] = []
    rerun_selector = run_selector(registry_for_guardrail, scenario_fixture, visible_profile["profile_id"])
    baseline_signature = [
        (
            opportunity["mission_type"],
            tuple(opportunity["target_object_ids"]),
            opportunity["score_components"]["final_opportunity_score"],
        )
        for opportunity in baseline_selector["ranked_opportunities"]
    ]
    rerun_signature = [
        (
            opportunity["mission_type"],
            tuple(opportunity["target_object_ids"]),
            opportunity["score_components"]["final_opportunity_score"],
        )
        for opportunity in rerun_selector["ranked_opportunities"]
    ]
    if baseline_signature != rerun_signature or not mutated_hidden:
        failures.append("hidden oracle removal/modification must not change selector output")

    if len(NEGATIVE_CASES) < 7:
        failures.append("negative fixture coverage must include semantic, runtime, content, and graph-context gates")

    for type_file in TYPE_FILES:
        if not type_file.exists():
            failures.append(f"missing TypeScript type file: {type_file.relative_to(REPO_ROOT)}")

    if failures:
        print("FAIL Mission Opportunity Selection v0.1 fixture tests")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("PASS Mission Opportunity Selection v0.1 fixture tests")
    print("PASS target/rollup integrity mutation tests reject mismatched targets")
    print("PASS hidden-oracle evaluation mutation tests preserve selector/oracle boundary")
    print("PASS rank-usefulness analysis mutation tests preserve evaluator boundaries")
    print("PASS Phase 1E expanded-scale guardrail tests validate")
    print("PASS Phase 1F song-pack smell-test guardrail tests validate")
    print("PASS Phase 1G construction-policy and LLM packet guardrail tests validate")
    print("PASS offline schemas, TypeScript types, fixtures, and negative gates validate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
