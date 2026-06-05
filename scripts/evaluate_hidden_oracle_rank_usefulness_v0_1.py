#!/usr/bin/env python3
from __future__ import annotations

import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_DIR = REPO_ROOT / "data/product_contracts/mission_opportunity_selection_v0_1"
PROFILE_SIM_DIR = CONTRACT_DIR / "fixtures/profile_simulation"

DESIGN_PATH = PROFILE_SIM_DIR / "hidden_oracle_evaluation_design_v0_1.json"
OUTPUT_PATH = PROFILE_SIM_DIR / "hidden_oracle_rank_usefulness_analysis_v0_1.json"

RANK_WINDOW = 10


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def repo_rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def bounded(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 4)


def correlation(value: float) -> float:
    return round(max(-1.0, min(1.0, value)), 4)


def mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def opportunity_ref(evaluation: dict[str, Any]) -> dict[str, Any]:
    selected = evaluation["selected_opportunity_ref"]
    return {
        "opportunity_id": selected["opportunity_id"],
        "rank": selected["rank"],
        "mission_type": selected["mission_type"],
        "target_object_type": selected["target_object_type"],
        "target_object_ids": selected["target_object_ids"],
        "target_display_name": selected["target_display_name"],
        "selector_score": selected["final_opportunity_score"],
        "learning_usefulness_score": evaluation["expected_metrics"]["learning_usefulness_score"],
    }


def usefulness_ranks(evaluations: list[dict[str, Any]]) -> dict[str, int]:
    sorted_by_usefulness = sorted(
        evaluations,
        key=lambda item: (
            -item["expected_metrics"]["learning_usefulness_score"],
            item["selected_opportunity_ref"]["rank"],
        ),
    )
    return {
        item["selected_opportunity_ref"]["opportunity_id"]: index + 1
        for index, item in enumerate(sorted_by_usefulness)
    }


def spearman_rank_correlation(evaluations: list[dict[str, Any]], usefulness_by_id: dict[str, int]) -> float:
    n = len(evaluations)
    if n < 2:
        return 1.0
    delta_sum = 0.0
    for item in evaluations:
        selected = item["selected_opportunity_ref"]
        selector_rank = selected["rank"]
        usefulness_rank = usefulness_by_id[selected["opportunity_id"]]
        delta_sum += (selector_rank - usefulness_rank) ** 2
    return correlation(1 - (6 * delta_sum) / (n * ((n * n) - 1)))


def ndcg_at(evaluations: list[dict[str, Any]], k: int) -> float:
    relevances = [
        float(item["expected_metrics"]["learning_usefulness_score"])
        for item in evaluations
    ]
    selected = relevances[:k]
    ideal = sorted(relevances, reverse=True)[:k]

    def dcg(values: list[float]) -> float:
        return sum(value / math.log2(index + 2) for index, value in enumerate(values))

    ideal_dcg = dcg(ideal)
    if ideal_dcg == 0:
        return 0.0
    return bounded(dcg(selected) / ideal_dcg)


def oracle_match_tags(match: dict[str, Any]) -> list[str]:
    tags: list[str] = []
    for archetype_id in match["matched_primary_archetype_ids"]:
        tags.append(f"primary_archetype:{archetype_id}")
    for archetype_id in match["matched_secondary_archetype_ids"]:
        tags.append(f"secondary_archetype:{archetype_id}")
    for archetype_id in match["matched_anti_archetype_ids"]:
        tags.append(f"anti_archetype:{archetype_id}")
    if match["matched_unknown_target_ids"]:
        tags.append(f"unknown_targets:{len(match['matched_unknown_target_ids'])}")
    if match["false_nearby_lane_match"]:
        tags.append("false_nearby_lane_match")
    if match["context_lane_match"]:
        tags.append("context_lane_match")
    direct = match["direct_song_reaction_counts"]
    for reaction in ["love", "like", "ok", "dont_like", "unknown"]:
        count = direct.get(reaction, 0)
        if count:
            tags.append(f"direct_song_{reaction}:{count}")
    return tags


def mission_type_summary(
    evaluations: list[dict[str, Any]],
    usefulness_by_id: dict[str, int],
) -> list[dict[str, Any]]:
    by_type: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in evaluations:
        by_type[item["selected_opportunity_ref"]["mission_type"]].append(item)

    summaries: list[dict[str, Any]] = []
    for mission_type, items in by_type.items():
        usefulness_scores = [
            item["expected_metrics"]["learning_usefulness_score"]
            for item in items
        ]
        summaries.append(
            {
                "mission_type": mission_type,
                "count": len(items),
                "best_selector_rank": min(
                    item["selected_opportunity_ref"]["rank"]
                    for item in items
                ),
                "best_usefulness_rank": min(
                    usefulness_by_id[item["selected_opportunity_ref"]["opportunity_id"]]
                    for item in items
                ),
                "mean_learning_usefulness_score": bounded(mean(usefulness_scores)),
                "max_learning_usefulness_score": bounded(max(usefulness_scores)),
            }
        )

    return sorted(
        summaries,
        key=lambda item: (
            -item["max_learning_usefulness_score"],
            item["best_selector_rank"],
            item["mission_type"],
        ),
    )


def diagnostic_findings(
    top1: dict[str, Any],
    best: dict[str, Any],
    rank_regret: float,
    spearman: float,
    best_rank: int,
) -> list[str]:
    findings: list[str] = []
    if top1["selected_opportunity_ref"]["opportunity_id"] == best["selected_opportunity_ref"]["opportunity_id"]:
        findings.append("Selector rank 1 is also the oracle-usefulness best item in the analysis window.")
    else:
        findings.append(
            "Oracle-usefulness best item appears at selector rank "
            f"{best_rank}, with rank regret {rank_regret:.4f}."
        )
    if best_rank <= 3:
        findings.append("The oracle-usefulness best item remains recoverable by a top-3 portfolio selector.")
    elif best_rank <= 5:
        findings.append("The oracle-usefulness best item is still recoverable by a top-5 portfolio selector.")
    else:
        findings.append("The oracle-usefulness best item falls below top 5 and needs scoring review.")
    if spearman >= 0.50:
        findings.append("Selector rank order has strong monotonic alignment with oracle usefulness.")
    elif spearman >= 0.20:
        findings.append("Selector rank order has mixed monotonic alignment with oracle usefulness.")
    else:
        findings.append("Selector rank order has weak monotonic alignment with oracle usefulness.")
    return findings


def tuning_notes(rank_regret: float, spearman: float, best: dict[str, Any]) -> list[str]:
    notes: list[str] = []
    best_type = best["selected_opportunity_ref"]["mission_type"]
    if rank_regret > 0.10:
        notes.append(
            f"Review whether {best_type} hidden-learning proxies should influence offline scoring more strongly."
        )
    if spearman < 0.20:
        notes.append("Inspect target-fit and learning-value weights for rank inversions in the top window.")
    if best_type in {"boundary_test", "context_dependence_test", "false_nearby_test"}:
        notes.append(
            "Diagnostic mission types are carrying high oracle usefulness; preserve them for later portfolio selection."
        )
    if not notes:
        notes.append("No immediate scoring change is indicated by this profile-level rank analysis.")
    return notes


def build_profile_analysis(profile: dict[str, Any]) -> dict[str, Any]:
    evaluations = profile["top_opportunity_evaluations"][:RANK_WINDOW]
    usefulness_by_id = usefulness_ranks(evaluations)
    top1 = evaluations[0]
    best = max(
        evaluations,
        key=lambda item: (
            item["expected_metrics"]["learning_usefulness_score"],
            -item["selected_opportunity_ref"]["rank"],
        ),
    )
    top1_score = top1["expected_metrics"]["learning_usefulness_score"]
    best_score = best["expected_metrics"]["learning_usefulness_score"]
    best_rank = best["selected_opportunity_ref"]["rank"]
    rank_regret = bounded(best_score - top1_score)
    spearman = spearman_rank_correlation(evaluations, usefulness_by_id)

    rank_rows = []
    for item in evaluations:
        selected = item["selected_opportunity_ref"]
        usefulness_rank = usefulness_by_id[selected["opportunity_id"]]
        learning = item["expected_metrics"]["learning_usefulness_score"]
        rank_rows.append(
            {
                "rank": selected["rank"],
                "opportunity_id": selected["opportunity_id"],
                "mission_type": selected["mission_type"],
                "target_display_name": selected["target_display_name"],
                "selector_score": selected["final_opportunity_score"],
                "learning_usefulness_score": learning,
                "usefulness_rank": usefulness_rank,
                "usefulness_delta_from_top1": round(learning - top1_score, 4),
                "oracle_match_tags": oracle_match_tags(item["oracle_match_summary"]),
            }
        )

    return {
        "profile_id": profile["profile_id"],
        "selector_output_ref": profile["selector_output_ref"],
        "evaluation_design_profile_ref": f"{repo_rel(DESIGN_PATH)}#{profile['profile_id']}",
        "rank_window": len(evaluations),
        "top_selector_opportunity": opportunity_ref(top1),
        "best_oracle_usefulness_opportunity": opportunity_ref(best),
        "top1_learning_usefulness_score": bounded(top1_score),
        "best_learning_usefulness_score": bounded(best_score),
        "rank_regret": rank_regret,
        "best_usefulness_rank": best_rank,
        "top1_is_best": best_rank == 1,
        "best_in_top3": best_rank <= 3,
        "best_in_top5": best_rank <= 5,
        "spearman_rank_correlation": spearman,
        "ndcg_at_3": ndcg_at(evaluations, 3),
        "ndcg_at_5": ndcg_at(evaluations, 5),
        "ndcg_at_10": ndcg_at(evaluations, 10),
        "rank_rows": rank_rows,
        "mission_type_usefulness_summary": mission_type_summary(
            evaluations,
            usefulness_by_id,
        ),
        "diagnostic_findings": diagnostic_findings(
            top1,
            best,
            rank_regret,
            spearman,
            best_rank,
        ),
        "recommended_selector_tuning_notes": tuning_notes(rank_regret, spearman, best),
    }


def aggregate_summary(profiles: list[dict[str, Any]]) -> dict[str, Any]:
    profile_count = len(profiles)
    mean_spearman = correlation(mean([item["spearman_rank_correlation"] for item in profiles]))
    mean_rank_regret = bounded(mean([item["rank_regret"] for item in profiles]))
    top1_is_best_count = sum(1 for item in profiles if item["top1_is_best"])
    best_in_top3_count = sum(1 for item in profiles if item["best_in_top3"])
    best_in_top5_count = sum(1 for item in profiles if item["best_in_top5"])
    if mean_spearman >= 0.50 and mean_rank_regret <= 0.05:
        alignment_label = "strong"
    elif mean_spearman >= 0.20 or best_in_top3_count == profile_count:
        alignment_label = "mixed"
    else:
        alignment_label = "weak"

    findings = [
        f"Oracle-usefulness best item is in top 3 for {best_in_top3_count}/{profile_count} profiles.",
        f"Oracle-usefulness best item is in top 5 for {best_in_top5_count}/{profile_count} profiles.",
    ]
    if top1_is_best_count < profile_count:
        findings.append(
            "Selector top rank is not always oracle-best; later portfolio selection should preserve the top window."
        )
    if mean_rank_regret > 0.10:
        findings.append("Mean rank regret is high enough to justify score-component review.")
    else:
        findings.append("Mean rank regret is modest in the accepted synthetic profile set.")

    return {
        "profile_count": profile_count,
        "mean_top1_learning_usefulness_score": bounded(
            mean([item["top1_learning_usefulness_score"] for item in profiles])
        ),
        "mean_best_learning_usefulness_score": bounded(
            mean([item["best_learning_usefulness_score"] for item in profiles])
        ),
        "mean_rank_regret": mean_rank_regret,
        "top1_is_best_count": top1_is_best_count,
        "best_in_top3_count": best_in_top3_count,
        "best_in_top5_count": best_in_top5_count,
        "mean_spearman_rank_correlation": mean_spearman,
        "mean_ndcg_at_3": bounded(mean([item["ndcg_at_3"] for item in profiles])),
        "mean_ndcg_at_5": bounded(mean([item["ndcg_at_5"] for item in profiles])),
        "mean_ndcg_at_10": bounded(mean([item["ndcg_at_10"] for item in profiles])),
        "alignment_label": alignment_label,
        "aggregate_findings": findings,
    }


def build_payload() -> dict[str, Any]:
    design = load_json(DESIGN_PATH)
    profiles = [build_profile_analysis(profile) for profile in design["profiles"]]
    return {
        "contract_version": "hidden_oracle_rank_usefulness_analysis_v0_1",
        "fixture_status": "synthetic_contract_fixture",
        "created_at": now_iso(),
        "phase": "hidden_oracle_rank_usefulness_analysis",
        "runtime_allowed": False,
        "runtime_listener_evidence_connected": False,
        "production_mission_generation_allowed": False,
        "canonical_graph_mutation_allowed": False,
        "listener_preference_inference_from_affinity_allowed": False,
        "opportunity_only": True,
        "selector_may_read_hidden_oracle": False,
        "evaluator_may_read_hidden_oracle_after_selection": True,
        "source_hidden_oracle_evaluation_design_ref": repo_rel(DESIGN_PATH),
        "analysis_scope": {
            "analysis_subject": "selected_opportunity_rank_order",
            "rank_window": RANK_WINDOW,
            "rank_score_field": "selected_opportunity_ref.final_opportunity_score",
            "usefulness_score_field": "expected_metrics.learning_usefulness_score",
            "hidden_oracle_use": "post_selection_metrics_only",
            "selector_input_rule": "visible_evidence_only",
            "construction_simulation_status": "not_implemented",
            "candidate_song_selection_status": "not_in_scope",
            "allowed_outputs": [
                "rank_rows",
                "rank_usefulness_metrics",
                "mission_type_usefulness_summary",
                "aggregate_rank_alignment",
                "review_notes",
            ],
        },
        "aggregate_summary": aggregate_summary(profiles),
        "profiles": profiles,
    }


def main() -> int:
    payload = build_payload()
    write_json(OUTPUT_PATH, payload)
    print(f"Wrote {repo_rel(OUTPUT_PATH)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
