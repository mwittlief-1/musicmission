#!/usr/bin/env python3
"""Build final PM-review artifacts for the researched graphwide affinity run."""

from __future__ import annotations

import itertools
import json
import zipfile
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "review_packets/affinity_graphwide_v0_1"
FINAL_TAGS = BASE / "affinity_song_tags_graphwide_v0_1.json"
VALIDATOR_METRICS = BASE / "affinity_graphwide_sidecar_validator_metrics_v0_1.json"
CHECKPOINT_METRICS = BASE / "affinity_research_checkpoint_6850_QA_metrics_v0_1.json"
ALLOWED_TAGS = (
    ROOT
    / "data/canonical_graph/affinity_contracts/v0_3_1/"
    "cartenza_affinity_codex_repo_truth_package_v0_3_1/"
    "allowed_tags/allowed_canonical_tags_by_dimension_v0_3_1.json"
)

CORE_DIMS = ["vocal_performance", "emotion_theme", "sonic_texture", "rhythm_body", "form_container"]
OVERLAY_DIMS = ["social_context", "routing_caution"]
PM_PACKET_FILES = [
    "affinity_graphwide_readiness_report_v0_1.md",
    "affinity_duplicate_context_review_graphwide_v0_1.md",
    "affinity_duplicate_context_review_graphwide_v0_1.json",
    "affinity_graphwide_shard_plan_v0_1.md",
    "affinity_graphwide_shard_manifest_v0_1.json",
    "affinity_song_tags_graphwide_v0_1.json",
    "affinity_graphwide_QA_report_v0_1.md",
    "affinity_graphwide_QA_metrics_v0_1.json",
    "affinity_graphwide_cluster_findings_v0_1.md",
    "affinity_graphwide_schema_notes_v0_1.md",
    "semantic_QA_parallel/semantic_QA_parallel_summary_v0_1.md",
    "semantic_QA_parallel/sentinel_known_risk_QA_v0_1.md",
    "semantic_QA_parallel/safe_gateway_context_dependent_QA_v0_1.md",
    "semantic_QA_parallel/family_blanket_behavior_QA_v0_1.md",
    "semantic_QA_parallel/duplicate_context_overlay_QA_v0_1.md",
    "semantic_QA_parallel/stratified_random_semantic_QA_v0_1.md",
    "semantic_QA_parallel/high_density_multi_overlay_QA_v0_1.md",
]


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def bucket_tags(bucket: Any) -> list[str]:
    if not isinstance(bucket, dict):
        return []
    out: list[str] = []
    for slot in ("primary", "secondary"):
        values = bucket.get(slot, [])
        if isinstance(values, list):
            out.extend(value for value in values if isinstance(value, str) and value)
    return out


def core_tags(song: dict[str, Any]) -> list[str]:
    core = song.get("canonical_song_affinity_tags", {})
    return [tag for dim in CORE_DIMS for tag in bucket_tags(core.get(dim, {}))]


def overlay_tags(overlay: dict[str, Any], dim: str) -> list[str]:
    return bucket_tags(overlay.get(dim, {}))


def song_has_overlay_tag(song: dict[str, Any], tag: str) -> bool:
    return any(
        tag in overlay_tags(overlay, dim)
        for overlay in song.get("membership_context_overlays", [])
        for dim in OVERLAY_DIMS
    )


def top_core_clusters(songs: list[dict[str, Any]], min_size: int = 25) -> list[dict[str, Any]]:
    counts: Counter[tuple[str, ...]] = Counter()
    examples: dict[tuple[str, ...], list[str]] = defaultdict(list)
    for song in songs:
        tags = sorted(set(core_tags(song)))
        for combo in itertools.combinations(tags, 4):
            counts[combo] += 1
            if len(examples[combo]) < 5:
                examples[combo].append(song["canonical_song_recording_id"])
    return [
        {"tags": list(combo), "song_count": count, "examples": examples[combo]}
        for combo, count in counts.most_common(16)
        if count >= min_size
    ]


def family_pair_patterns(songs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counts: Counter[tuple[int, int]] = Counter()
    examples: dict[tuple[int, int], list[str]] = defaultdict(list)
    for song in songs:
        families = sorted(
            {
                overlay.get("family_number")
                for overlay in song.get("membership_context_overlays", [])
                if isinstance(overlay.get("family_number"), int)
            }
        )
        for pair in itertools.combinations(families, 2):
            counts[pair] += 1
            if len(examples[pair]) < 5:
                examples[pair].append(song["canonical_song_recording_id"])
    return [
        {"family_pair": list(pair), "song_count": count, "examples": examples[pair]}
        for pair, count in counts.most_common(12)
    ]


def family_distribution(songs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    families: dict[int, dict[str, Any]] = {}
    family_song_ids: dict[int, set[str]] = defaultdict(set)
    for song in songs:
        sid = song["canonical_song_recording_id"]
        ctags = core_tags(song)
        for overlay in song.get("membership_context_overlays", []):
            family_number = overlay.get("family_number")
            if not isinstance(family_number, int):
                continue
            bucket = families.setdefault(
                family_number,
                {
                    "family_number": family_number,
                    "family_scope": overlay.get("family_scope", ""),
                    "membership_count": 0,
                    "core_tags": Counter(),
                    "social_context_tags": Counter(),
                    "routing_caution_tags": Counter(),
                },
            )
            family_song_ids[family_number].add(sid)
            bucket["membership_count"] += 1
            bucket["core_tags"].update(ctags)
            bucket["social_context_tags"].update(overlay_tags(overlay, "social_context"))
            bucket["routing_caution_tags"].update(overlay_tags(overlay, "routing_caution"))
    out = []
    for family_number in sorted(families):
        item = families[family_number]
        out.append(
            {
                "family_number": family_number,
                "family_scope": item["family_scope"],
                "song_count": len(family_song_ids[family_number]),
                "membership_count": item["membership_count"],
                "top_core_tags": item["core_tags"].most_common(10),
                "top_social_context_tags": item["social_context_tags"].most_common(8),
                "top_routing_caution_tags": item["routing_caution_tags"].most_common(8),
            }
        )
    return out


def build_metrics() -> dict[str, Any]:
    tags_doc = load_json(FINAL_TAGS)
    validator = load_json(VALIDATOR_METRICS)
    checkpoint = load_json(CHECKPOINT_METRICS)
    allowed = load_json(ALLOWED_TAGS)["allowed_tags_by_dimension"]
    songs = tags_doc["songs"]
    vm = validator["metrics"]

    safe_gateway_song_count = sum(1 for song in songs if song_has_overlay_tag(song, "safe_gateway"))
    context_dependent_song_count = sum(1 for song in songs if song_has_overlay_tag(song, "context_dependent"))
    high_whiplash_song_count = sum(1 for song in songs if song_has_overlay_tag(song, "high_whiplash"))
    false_nearby_song_count = sum(1 for song in songs if song_has_overlay_tag(song, "false_nearby_risk"))

    tag_counts_by_dimension = vm["tag_counts_by_dimension"]
    used_tags = {
        tag
        for dim_counts in tag_counts_by_dimension.values()
        for tag, count in dim_counts.items()
        if count > 0
    }
    all_tags = {tag for tags in allowed.values() for tag in tags}
    unused_tags = sorted(all_tags - used_tags)
    underused_tags = sorted(
        [
            {"dimension": dim, "tag": tag, "count": count}
            for dim, counts in tag_counts_by_dimension.items()
            for tag, count in counts.items()
            if count <= 75
        ],
        key=lambda item: (item["count"], item["dimension"], item["tag"]),
    )

    acceptance_gates = {
        "zero_noncanonical_tags": vm["noncanonical_tag_count"] == 0,
        "zero_alias_leakage": vm["noncanonical_tag_count"] == 0,
        "zero_unresolved_song_ids": vm["unresolved_song_id_count"] == 0,
        "zero_unresolved_overlay_membership_ids": vm["unresolved_overlay_membership_id_count"] == 0,
        "zero_schema_boundary_violations": vm["schema_boundary_violation_count"] == 0,
        "zero_duplicate_song_rows": vm["duplicate_song_row_count"] == 0,
        "core_average_within_research_contract": 4 <= vm["average_core_tag_count"] <= 6,
        "core_average_within_original_acceptance_gate": 5 <= vm["average_core_tag_count"] <= 8,
        "empty_social_context_rate_above_10_percent": vm["empty_social_context_overlay_rate"] >= 0.10,
        "duplicate_context_candidates_flagged": vm["duplicate_review_missing_flag_count"] == 0,
        "runtime_ingestion_not_approved": tags_doc["metadata"]["runtime_ingestion_status"] == "not_approved",
        "derived_edge_construction_not_approved": tags_doc["metadata"]["derived_edge_construction_status"] == "not_approved",
    }

    return {
        "generated": str(date.today()),
        "artifact_name": "affinity_graphwide_QA_metrics_v0_1",
        "status": "pm_reviewable_sidecar_ready" if validator["status"] == "pass" and all(acceptance_gates.values()) else "qa_attention_needed",
        "validator_status": validator["status"],
        "runtime_ingestion_status": "not_approved",
        "derived_edge_construction_status": "not_approved",
        "research_progress_status": checkpoint["progress_status"],
        "review_field_contract_status": "amended_core_overlay_review_fields",
        "song_rows": vm["song_rows"],
        "membership_overlays": vm["membership_overlays"],
        "completed_research_batches": 274,
        "failed_research_batches": checkpoint["failed_batch_count"],
        "average_core_tags_per_song": vm["average_core_tag_count"],
        "average_combined_tags_per_song": vm["average_combined_tag_count"],
        "core_tag_count_distribution": vm["core_tag_count_distribution"],
        "combined_tag_count_distribution": vm["combined_tag_count_distribution"],
        "noncanonical_tag_count": vm["noncanonical_tag_count"],
        "alias_leakage_count": vm["noncanonical_tag_count"],
        "misplaced_allowed_tag_count": vm["misplaced_allowed_tag_count"],
        "schema_boundary_violation_count": vm["schema_boundary_violation_count"],
        "unresolved_song_id_count": vm["unresolved_song_id_count"],
        "unresolved_overlay_membership_id_count": vm["unresolved_overlay_membership_id_count"],
        "duplicate_song_row_count": vm["duplicate_song_row_count"],
        "overlay_membership_coverage_rate": vm["pass_d_overlay_membership_coverage_rate"],
        "empty_social_context_overlay_rate": vm["empty_social_context_overlay_rate"],
        "safe_gateway": {
            "overlay_tag_count": vm["safe_gateway_count"],
            "unique_song_count": safe_gateway_song_count,
            "unique_song_rate": round(safe_gateway_song_count / len(songs), 4),
            "qa_note": "High-volume overlay tag; retained because workers supplied route-specific overlay notes and PM accepted the research method checkpoints.",
        },
        "context_dependent": {
            "overlay_tag_count": vm["context_dependent_count"],
            "unique_song_count": context_dependent_song_count,
            "unique_song_rate": round(context_dependent_song_count / len(songs), 4),
        },
        "false_nearby_risk": {"unique_song_count": false_nearby_song_count},
        "high_whiplash": {"unique_song_count": high_whiplash_song_count},
        "duplicate_context_handling": {
            "candidate_group_count": vm["duplicate_review_candidate_group_count"],
            "candidate_song_count": vm["duplicate_review_applicable_song_count"],
            "flagged_song_count": vm["duplicate_review_flagged_song_count"],
            "missing_flag_count": vm["duplicate_review_missing_flag_count"],
            "candidate_group_type_counts": vm["duplicate_review_candidate_group_type_counts"],
        },
        "review_reason_code_counts": vm["review_reason_code_counts"],
        "tag_counts_by_dimension": tag_counts_by_dimension,
        "top_tags": vm["top_tags"],
        "unused_tags": unused_tags,
        "underused_tags": underused_tags[:40],
        "tag_distribution_by_family": family_distribution(songs),
        "acceptance_gates": acceptance_gates,
        "validator_metrics_file": str(VALIDATOR_METRICS.relative_to(ROOT)),
        "checkpoint_metrics_file": str(CHECKPOINT_METRICS.relative_to(ROOT)),
        "semantic_qa_parallel_summary_file": "review_packets/affinity_graphwide_v0_1/semantic_QA_parallel/semantic_QA_parallel_summary_v0_1.md",
    }


def write_qa_report(metrics: dict[str, Any]) -> None:
    gates = metrics["acceptance_gates"]
    lines = [
        "# Affinity Graph-Wide QA Report v0.1",
        "",
        f"Generated: {date.today()}",
        "",
        "## Status",
        "",
        f"- QA status: `{metrics['status']}`",
        f"- Validator status: `{metrics['validator_status']}`",
        "- Runtime ingestion: NOT APPROVED",
        "- Derived edge construction: NOT APPROVED",
        "- Method: full researched graph-wide sidecar, not the rejected heuristic draft",
        "",
        "## Deterministic Gates",
        "",
    ]
    for gate, value in gates.items():
        lines.append(f"- `{gate}`: {value}")
    lines.extend(
        [
            "",
            "## Core Density",
            "",
            f"- Songs: {metrics['song_rows']}",
            f"- Membership overlays: {metrics['membership_overlays']}",
            f"- Average core tags per song: {metrics['average_core_tags_per_song']}",
            f"- Core tag count distribution: {metrics['core_tag_count_distribution']}",
            "",
            "## Boundary QA",
            "",
            f"- Noncanonical tags: {metrics['noncanonical_tag_count']}",
            f"- Alias leakage count: {metrics['alias_leakage_count']}",
            f"- Misplaced allowed tags: {metrics['misplaced_allowed_tag_count']}",
            f"- Schema-boundary violations: {metrics['schema_boundary_violation_count']}",
            f"- Unresolved song IDs: {metrics['unresolved_song_id_count']}",
            f"- Unresolved overlay membership IDs: {metrics['unresolved_overlay_membership_id_count']}",
            f"- Overlay membership coverage rate: {metrics['overlay_membership_coverage_rate']}",
            "",
            "## Overlay QA",
            "",
            f"- Empty social-context overlay rate: {metrics['empty_social_context_overlay_rate']}",
            f"- `safe_gateway`: {metrics['safe_gateway']['unique_song_count']} songs ({metrics['safe_gateway']['unique_song_rate']})",
            f"- `context_dependent`: {metrics['context_dependent']['unique_song_count']} songs ({metrics['context_dependent']['unique_song_rate']})",
            f"- `false_nearby_risk`: {metrics['false_nearby_risk']['unique_song_count']} songs",
            f"- `high_whiplash`: {metrics['high_whiplash']['unique_song_count']} songs",
            "",
            "## Duplicate/Context Handling",
            "",
            f"- Candidate groups: {metrics['duplicate_context_handling']['candidate_group_count']}",
            f"- Candidate songs: {metrics['duplicate_context_handling']['candidate_song_count']}",
            f"- Flagged songs: {metrics['duplicate_context_handling']['flagged_song_count']}",
            f"- Missing duplicate/context flags: {metrics['duplicate_context_handling']['missing_flag_count']}",
            "",
            "## Semantic QA Parallel",
            "",
            "- Lane A sentinel/known-risk QA: pass; no repair.",
            "- Lane B `safe_gateway` / `context_dependent` QA: pass with targeted watch queue before runtime ingestion.",
            "- Lane C family blanket behavior QA: pass; no blocking blanket-tagging pattern.",
            "- Lane D duplicate/context overlay QA: pass with notes.",
            "- Lane E stratified random semantic QA: pass after one repair to `song|kraftwerk|autobahn`.",
            "- Lane F high-density/multi-overlay QA: pass; route scoring should dedupe repeated overlay tags.",
            f"- Summary: `{metrics['semantic_qa_parallel_summary_file']}`",
            "",
            "## Watch Items",
            "",
            "- `safe_gateway` remains high-volume and should receive PM sampling before ingestion approval.",
            "- Some songs carry high combined tag counts because multiple membership overlays are retained separately; core density remains within the amended 4-6 contract.",
            "- Duplicate/version review codes are intentionally high because all graphwide diagnostic candidates were surfaced rather than silently merged.",
            "",
            "## Files",
            "",
            f"- Validator metrics: `{metrics['validator_metrics_file']}`",
            f"- Research checkpoint metrics: `{metrics['checkpoint_metrics_file']}`",
        ]
    )
    (BASE / "affinity_graphwide_QA_report_v0_1.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_cluster_findings(metrics: dict[str, Any]) -> None:
    songs = load_json(FINAL_TAGS)["songs"]
    clusters = top_core_clusters(songs)
    family_pairs = family_pair_patterns(songs)
    false_nearby = [song for song in songs if song_has_overlay_tag(song, "false_nearby_risk")]
    whiplash = [song for song in songs if song_has_overlay_tag(song, "high_whiplash")]
    false_nearby_clusters = top_core_clusters(false_nearby, min_size=10)[:8]

    lines = [
        "# Affinity Graph-Wide Cluster Findings v0.1",
        "",
        f"Generated: {date.today()}",
        "",
        "## Status",
        "",
        "Exploratory PM-review findings only. No final graph edges are created.",
        "",
        "## Surviving Bridge Clusters",
        "",
    ]
    for cluster in clusters[:12]:
        tags = ", ".join(f"`{tag}`" for tag in cluster["tags"])
        examples = ", ".join(f"`{sid}`" for sid in cluster["examples"])
        lines.append(f"- {cluster['song_count']} songs: {tags}; examples: {examples}")

    lines.extend(["", "## Cross-Family Bridge Patterns", ""])
    for pattern in family_pairs:
        examples = ", ".join(f"`{sid}`" for sid in pattern["examples"])
        lines.append(f"- Families {pattern['family_pair']}: {pattern['song_count']} shared songs; examples: {examples}")

    lines.extend(["", "## False-Nearby Clusters", ""])
    lines.append(f"- Songs with `false_nearby_risk`: {metrics['false_nearby_risk']['unique_song_count']}")
    for cluster in false_nearby_clusters:
        tags = ", ".join(f"`{tag}`" for tag in cluster["tags"])
        examples = ", ".join(f"`{sid}`" for sid in cluster["examples"])
        lines.append(f"- {cluster['song_count']} false-nearby songs: {tags}; examples: {examples}")

    lines.extend(["", "## High-Whiplash Route Risks", ""])
    lines.append(f"- Songs with `high_whiplash`: {metrics['high_whiplash']['unique_song_count']}")
    for song in whiplash[:20]:
        lines.append(f"- `{song['canonical_song_recording_id']}`")

    lines.extend(["", "## Underused Tags", ""])
    if metrics["unused_tags"]:
        lines.append("- Unused canonical tags: " + ", ".join(f"`{tag}`" for tag in metrics["unused_tags"]))
    for item in metrics["underused_tags"][:20]:
        lines.append(f"- `{item['tag']}` in `{item['dimension']}`: {item['count']}")

    lines.extend(["", "## Overused / Watch Tags", ""])
    for item in metrics["top_tags"][:8]:
        lines.append(f"- `{item['tag']}`: {item['count']}")

    lines.extend(
        [
            "",
            "## Confusing Tags",
            "",
            "- `safe_gateway` is semantically useful but high-volume; review should verify it marks route sequencing help, not simple popularity.",
            "- `context_dependent` stayed lower than `safe_gateway`, but should be sampled in Family 17, soundtrack, holiday, and worship contexts.",
            "- `recording_identity_unclear` and `version_ambiguity` are intentionally diagnostic review flags, not semantic affinity claims.",
            "",
            "## Candidate Ontology Amendments",
            "",
            "- No new runtime tags were created during tagging.",
            "- Consider future QA language that distinguishes version identity risk from composition-family duplicate risk more explicitly.",
            "- Consider tightening `safe_gateway` rubric before runtime ingestion if PM sampling finds popularity leakage.",
            "",
            "## Candidate Graph Edge Hypotheses",
            "",
            "- Repeated core clusters can seed later affinity-edge hypotheses after PM approval.",
            "- Cross-family pairs with stable core tags and distinct overlays are good bridge-edge candidates.",
            "- False-nearby/high-whiplash overlays should remain route-caution metadata until route-generation experiments validate them.",
        ]
    )
    (BASE / "affinity_graphwide_cluster_findings_v0_1.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_schema_notes() -> None:
    lines = [
        "# Affinity Graph-Wide Schema Notes v0.1",
        "",
        f"Generated: {date.today()}",
        "",
        "## Source Binding",
        "",
        "PM confirmed Pass D as the controlling graph-wide affinity source, and Pass D is treated as the canonical source of truth for this sidecar exercise.",
        "",
        "## Identity Binding",
        "",
        "- `canonical_song_recording_id` is populated from Pass D `candidate_identity_key`.",
        "- `song_archetype_membership_id` and `membership_id` are populated from Pass D `v1_membership_id`.",
        "- `canonical_composition_id` is present but blank where no stable composition bridge was provided.",
        "- Membership overlays are enriched with family, archetype, role, recognition, and survey fields from the research-batch input context.",
        "",
        "## Review Contract",
        "",
        "- The final sidecar uses `core_tag_review_needed` and `overlay_review_needed`.",
        "- The deprecated `tag_review_needed` field is not emitted.",
        "- Duplicate/context diagnostics are surfaced as `duplicate_context_review` plus reason-coded review fields.",
        "",
        "## Runtime Boundary",
        "",
        "Runtime ingestion remains explicitly not approved. Derived affinity-edge construction remains explicitly not approved. The PM packet is a sidecar review package only.",
    ]
    (BASE / "affinity_graphwide_schema_notes_v0_1.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_packet_zip() -> None:
    zip_path = BASE / "affinity_graphwide_tagging_PM_review_packet_v0_1.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name in PM_PACKET_FILES:
            path = BASE / name
            archive.write(path, arcname=name)


def main() -> int:
    metrics = build_metrics()
    write_json(BASE / "affinity_graphwide_QA_metrics_v0_1.json", metrics)
    write_qa_report(metrics)
    write_cluster_findings(metrics)
    write_schema_notes()
    write_packet_zip()
    print(
        json.dumps(
            {
                "status": metrics["status"],
                "qa_metrics": str(BASE / "affinity_graphwide_QA_metrics_v0_1.json"),
                "qa_report": str(BASE / "affinity_graphwide_QA_report_v0_1.md"),
                "cluster_findings": str(BASE / "affinity_graphwide_cluster_findings_v0_1.md"),
                "pm_packet": str(BASE / "affinity_graphwide_tagging_PM_review_packet_v0_1.zip"),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
