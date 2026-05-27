#!/usr/bin/env python3
"""Deterministically load and validate AtlasExplainer render-pack fixtures."""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACK = REPO_ROOT / "data/atlas_explainer/render_pack_v0_1_hardened"

REQUIRED_MANIFEST_FILES = {
    "manifest.json",
    "atlas_explainer_render_pack_family_1_005_family_8_054_v0_1.json",
    "atlas_explainer_render_pack_schema_v0_1.json",
    "atlas_explainer_render_pack_schema_v0_1.md",
    "atlas_explainer_research_pack_schema_v0_1_1.json",
    "atlas_explainer_research_pack_schema_v0_1_1.md",
    "explainer_family_1_archetype_005_brill_building_girl_group_pop_v0_1_1.json",
    "explainer_family_8_archetype_054_cbgb_art_punk_downtown_ny_v0_1_1.json",
    "atlas_explainer_hardening_notes_v0_1.md",
    "atlas_explainer_render_examples_v0_1_1.md",
}

REQUIRED_TOP_LEVEL = {
    "schema_version",
    "pack_id",
    "runtime_contract",
    "rights_policy",
    "non_mutation_policy",
    "alpha_v0_mission_boundary",
    "state_field_contract",
    "render_surfaces",
    "entries",
    "source_references",
    "audit",
}

REQUIRED_RENDER_SURFACES = {
    "atlas_home_region_card",
    "region_scene_page",
    "mission_detail_history_module",
    "did_you_know_card",
    "what_to_listen_for_prompt",
    "personalized_overlay",
    "related_roads_lineage_module",
}

ENTRY_REQUIRED_FIELDS = {
    "render_pack_id",
    "graph_alignment",
    "editorial_status",
    "source_claim_refs",
    "home_region_card",
    "region_scene_page",
    "mission_detail_history_module",
    "did_you_know_card",
    "what_to_listen_for_prompt",
    "personalized_overlay",
    "canonical_examples",
    "related_roads_lineage_module",
}

COPY_VARIANTS = {"compact", "standard", "deep"}


@dataclass
class PackStore:
    files: dict[str, bytes]
    source: Path

    @classmethod
    def from_path(cls, path: Path) -> "PackStore":
        if path.is_file() and path.suffix == ".zip":
            return cls.from_zip(path)
        if path.is_dir():
            return cls.from_directory(path)
        raise ValueError(f"unsupported pack path: {path}")

    @classmethod
    def from_zip(cls, path: Path) -> "PackStore":
        files: dict[str, bytes] = {}
        with zipfile.ZipFile(path) as archive:
            for name in archive.namelist():
                if name.endswith("/"):
                    continue
                basename = Path(name).name
                if basename in files:
                    raise ValueError(f"duplicate basename in zip: {basename}")
                files[basename] = archive.read(name)
        return cls(files=files, source=path)

    @classmethod
    def from_directory(cls, path: Path) -> "PackStore":
        files: dict[str, bytes] = {}
        for file_path in sorted(path.iterdir()):
            if file_path.is_file():
                files[file_path.name] = file_path.read_bytes()
        return cls(files=files, source=path)

    def read_json(self, name: str) -> Any:
        return json.loads(self.files[name].decode("utf-8"))

    def has_file(self, name: str) -> bool:
        return name in self.files


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate AtlasExplainerRenderPack fixture invariants.")
    parser.add_argument("pack", nargs="?", type=Path, default=DEFAULT_PACK)
    parser.add_argument("--report-json", type=Path, default=None)
    args = parser.parse_args()

    try:
        store = PackStore.from_path(args.pack)
    except Exception as exc:  # noqa: BLE001 - command-line validator should report cleanly
        print(f"ATLAS_EXPLAINER_RENDER_PACK_LOAD_FAIL: {exc}", file=sys.stderr)
        return 1

    findings, summary = validate_store(store)
    if args.report_json:
        args.report_json.parent.mkdir(parents=True, exist_ok=True)
        args.report_json.write_text(json.dumps(summary | {"findings": findings}, indent=2) + "\n", encoding="utf-8")

    if findings:
        print(f"ATLAS_EXPLAINER_RENDER_PACK_VALIDATION_FAIL ({len(findings)} finding(s))")
        for finding in findings:
            print(f"- {finding}")
        return 1

    print("ATLAS_EXPLAINER_RENDER_PACK_VALIDATION_PASS")
    print(f"source={rel(store.source)}")
    print(f"render_pack={summary['render_pack_id']}")
    print(f"entries={summary['entry_count']}")
    print(f"claim_refs_checked={summary['claim_refs_checked']}")
    print(f"source_refs_checked={summary['source_refs_checked']}")
    print(f"graph_audit_refs_checked={summary['graph_audit_refs_checked']}")
    print(f"copy_variant_sets_checked={summary['copy_variant_sets_checked']}")
    return 0


def validate_store(store: PackStore) -> tuple[list[str], dict[str, Any]]:
    findings: list[str] = []
    missing = sorted(REQUIRED_MANIFEST_FILES - set(store.files))
    if missing:
        findings.extend(f"missing fixture file: {name}" for name in missing)
        return findings, empty_summary(store)

    manifest = store.read_json("manifest.json")
    manifest_files = set(manifest.get("files", [])) | {"manifest.json"}
    for name in REQUIRED_MANIFEST_FILES:
        if name not in manifest_files:
            findings.append(f"manifest does not list required file: {name}")

    render_pack = store.read_json("atlas_explainer_render_pack_family_1_005_family_8_054_v0_1.json")
    research_packs = [
        store.read_json("explainer_family_1_archetype_005_brill_building_girl_group_pop_v0_1_1.json"),
        store.read_json("explainer_family_8_archetype_054_cbgb_art_punk_downtown_ny_v0_1_1.json"),
    ]

    context = build_reference_context(render_pack, research_packs)
    findings.extend(validate_render_pack(render_pack, context))

    summary = {
        "source": rel(store.source),
        "manifest_package_id": manifest.get("package_id"),
        "render_pack_id": render_pack.get("pack_id"),
        "entry_count": len(render_pack.get("entries", [])),
        "research_pack_ids": [pack.get("pack_id") for pack in research_packs],
        "claim_bank_size": len(context["claim_ids"]),
        "source_reference_count": len(context["source_ids"]),
        "graph_audit_ref_count": len(context["graph_audit_ids"]),
        "claim_refs_checked": context["claim_refs_checked"],
        "source_refs_checked": context["source_refs_checked"],
        "graph_audit_refs_checked": context["graph_audit_refs_checked"],
        "copy_variant_sets_checked": context["copy_variant_sets_checked"],
    }
    return findings, summary


def build_reference_context(render_pack: dict[str, Any], research_packs: list[dict[str, Any]]) -> dict[str, Any]:
    claim_ids: set[str] = set()
    source_ids: set[str] = set((render_pack.get("source_references") or {}).keys())
    graph_audit_ids: set[str] = set()

    for pack in research_packs:
        claim_ids.update(row.get("claim_id") for row in pack.get("claim_bank", []) if row.get("claim_id"))
        source_ids.update((pack.get("source_references") or {}).keys())
        graph_alignment = pack.get("graph_alignment") or {}
        archetype_ref = str(graph_alignment.get("archetype_ref") or "").replace("/", "-")
        for row in pack.get("graph_ref_integrity_audit", []):
            entity_id = row.get("graph_entity_id")
            if archetype_ref and entity_id:
                graph_audit_ids.add(f"graph-audit-{archetype_ref}-{entity_id}")

    return {
        "claim_ids": claim_ids,
        "source_ids": source_ids,
        "graph_audit_ids": graph_audit_ids,
        "claim_refs_checked": 0,
        "source_refs_checked": 0,
        "graph_audit_refs_checked": 0,
        "copy_variant_sets_checked": 0,
    }


def validate_render_pack(render_pack: dict[str, Any], context: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    for field in sorted(REQUIRED_TOP_LEVEL):
        if field not in render_pack:
            findings.append(f"render pack missing top-level field: {field}")
    if render_pack.get("schema_version") != "0.1":
        findings.append(f"render pack schema_version must be 0.1 for fixture, got {render_pack.get('schema_version')}")

    runtime_contract = render_pack.get("runtime_contract") or {}
    if runtime_contract.get("deterministic_render_required") is not True:
        findings.append("runtime_contract.deterministic_render_required must be true")
    if runtime_contract.get("history_generation_from_scratch_allowed") is not False:
        findings.append("runtime_contract.history_generation_from_scratch_allowed must be false")
    disallowed_actions = " ".join(runtime_contract.get("small_model_disallowed_actions") or [])
    for phrase in ["invent new historical claims", "invent graph refs", "create missions dynamically"]:
        if phrase not in disallowed_actions:
            findings.append(f"runtime_contract.small_model_disallowed_actions missing: {phrase}")

    findings.extend(validate_rights_policy(render_pack.get("rights_policy") or {}))
    findings.extend(validate_non_mutation_policy(render_pack.get("non_mutation_policy") or {}))
    findings.extend(validate_alpha_boundary(render_pack.get("alpha_v0_mission_boundary") or {}))

    state_fields = render_pack.get("state_field_contract", {}).get("fields") or {}
    if not state_fields:
        findings.append("state_field_contract.fields must not be empty")

    surfaces = set(render_pack.get("render_surfaces") or [])
    for surface in sorted(REQUIRED_RENDER_SURFACES):
        if surface not in surfaces:
            findings.append(f"render_surfaces missing required surface: {surface}")

    entries = render_pack.get("entries")
    if not isinstance(entries, list) or not entries:
        findings.append("entries must be a non-empty array")
        return findings

    seen_entry_ids: set[str] = set()
    for index, entry in enumerate(entries):
        findings.extend(validate_entry(index, entry, context, state_fields))
        entry_id = entry.get("render_pack_id")
        if entry_id in seen_entry_ids:
            findings.append(f"entries[{index}] duplicate render_pack_id: {entry_id}")
        seen_entry_ids.add(entry_id)

    return findings


def validate_rights_policy(policy: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    if policy.get("no_lyrics") is not True:
        findings.append("rights_policy.no_lyrics must be true")
    if policy.get("no_long_quotes") is not True:
        findings.append("rights_policy.no_long_quotes must be true")
    if policy.get("max_verbatim_quote_words_per_source") != 0:
        findings.append("rights_policy.max_verbatim_quote_words_per_source must be 0")
    if policy.get("album_art_dependency") != "none":
        findings.append("rights_policy.album_art_dependency must be none")
    return findings


def validate_non_mutation_policy(policy: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    for field in [
        "canonical_graph_mutation_allowed",
        "renamed_archetypes_allowed",
        "new_taxonomy_allowed",
        "new_graph_identity_allowed",
    ]:
        if policy.get(field) is not False:
            findings.append(f"non_mutation_policy.{field} must be false")
    return findings


def validate_alpha_boundary(boundary: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    if boundary.get("mission_creation_from_atlas_allowed") is not False:
        findings.append("alpha_v0_mission_boundary.mission_creation_from_atlas_allowed must be false")
    if boundary.get("dynamic_route_generation_allowed") is not False:
        findings.append("alpha_v0_mission_boundary.dynamic_route_generation_allowed must be false")
    for field in [
        "atlas.alpha_v0.current_batch_id",
        "atlas.alpha_v0.mission_inclusion[archetype_ref].status",
        "atlas.alpha_v0.mission_inclusion[archetype_ref].mission_refs",
    ]:
        if field not in (boundary.get("state_fields") or {}):
            findings.append(f"alpha_v0_mission_boundary.state_fields missing {field}")
    return findings


def validate_entry(
    index: int,
    entry: dict[str, Any],
    context: dict[str, Any],
    state_fields: dict[str, str],
) -> list[str]:
    findings: list[str] = []
    label = f"entries[{index}]"
    for field in sorted(ENTRY_REQUIRED_FIELDS):
        if field not in entry:
            findings.append(f"{label} missing required field: {field}")

    graph_alignment = entry.get("graph_alignment") or {}
    for field in ["family_id", "family_ref", "family_name", "archetype_id", "archetype_ref", "archetype_name"]:
        if graph_alignment.get(field) in (None, ""):
            findings.append(f"{label}.graph_alignment missing {field}")

    source_claim_refs = entry.get("source_claim_refs") or []
    if not source_claim_refs:
        findings.append(f"{label}.source_claim_refs must not be empty")
    findings.extend(validate_claim_refs(source_claim_refs, context, f"{label}.source_claim_refs"))

    findings.extend(validate_surface_shapes(label, entry))
    findings.extend(validate_copy_modules(label, entry, context))
    findings.extend(validate_personalized_overlay(label, entry.get("personalized_overlay") or {}, state_fields, context))
    findings.extend(validate_canonical_examples(label, entry, context))
    return findings


def validate_surface_shapes(label: str, entry: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    if not (entry.get("home_region_card") or {}).get("subtitle_variants"):
        findings.append(f"{label}.home_region_card missing subtitle_variants")
    region_page = entry.get("region_scene_page") or {}
    for field in ["hero_title", "subtitle_variants", "definition_variants", "history_variants"]:
        if field not in region_page:
            findings.append(f"{label}.region_scene_page missing {field}")
    mission_module = entry.get("mission_detail_history_module") or {}
    if "copy_variants" not in mission_module:
        findings.append(f"{label}.mission_detail_history_module missing copy_variants")
    boundary_copy = mission_module.get("mission_boundary_copy") or {}
    for field in ["included", "related", "not_included", "state_field"]:
        if field not in boundary_copy:
            findings.append(f"{label}.mission_detail_history_module.mission_boundary_copy missing {field}")
    if not (entry.get("did_you_know_card") or {}).get("card_variants"):
        findings.append(f"{label}.did_you_know_card missing card_variants")
    if not (entry.get("what_to_listen_for_prompt") or {}).get("prompt_variants"):
        findings.append(f"{label}.what_to_listen_for_prompt missing prompt_variants")
    related = entry.get("related_roads_lineage_module") or {}
    if "copy_variants" not in related:
        findings.append(f"{label}.related_roads_lineage_module missing copy_variants")
    if "roads" not in related:
        findings.append(f"{label}.related_roads_lineage_module missing roads")
    return findings


def validate_copy_modules(label: str, node: Any, context: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    if isinstance(node, dict):
        if is_variant_container(node):
            context["copy_variant_sets_checked"] += 1
            missing = sorted(COPY_VARIANTS - set(node))
            if missing:
                findings.append(f"{label} variant container missing variants: {', '.join(missing)}")
        if "text" in node and ("claim_refs" in node or "source_refs" in node):
            text = node.get("text")
            if not isinstance(text, str) or not text.strip():
                findings.append(f"{label} copy variant has empty text")
            max_chars = node.get("max_chars")
            if isinstance(max_chars, int) and isinstance(text, str) and len(text) > max_chars:
                findings.append(f"{label} copy variant exceeds max_chars")
            findings.extend(validate_claim_refs(node.get("claim_refs") or [], context, f"{label}.claim_refs"))
            findings.extend(validate_source_refs(node.get("source_refs") or [], context, f"{label}.source_refs"))
        for key, value in node.items():
            findings.extend(validate_copy_modules(f"{label}.{key}", value, context))
    elif isinstance(node, list):
        for index, value in enumerate(node):
            findings.extend(validate_copy_modules(f"{label}[{index}]", value, context))
    return findings


def is_variant_container(node: dict[str, Any]) -> bool:
    if not COPY_VARIANTS.issubset(node.keys()):
        return False
    return all(isinstance(node.get(variant), dict) and "text" in node[variant] for variant in COPY_VARIANTS)


def validate_personalized_overlay(
    label: str,
    overlay: dict[str, Any],
    state_fields: dict[str, str],
    context: dict[str, Any],
) -> list[str]:
    findings: list[str] = []
    hooks = overlay.get("runtime_hooks")
    if not isinstance(hooks, list):
        findings.append(f"{label}.personalized_overlay.runtime_hooks must be an array")
        return findings
    if not overlay.get("fallback_overlay"):
        findings.append(f"{label}.personalized_overlay.fallback_overlay must be present")
    for hook_index, hook in enumerate(hooks):
        hook_label = f"{label}.personalized_overlay.runtime_hooks[{hook_index}]"
        bindings = hook.get("state_field_bindings") or []
        if not bindings:
            findings.append(f"{hook_label}.state_field_bindings must not be empty")
        for binding in bindings:
            if not state_field_allowed(binding, state_fields):
                findings.append(f"{hook_label} binding not allowed by state_field_contract: {binding}")
        for condition_field in condition_fields(hook.get("condition_logic")):
            if not state_field_allowed(condition_field, state_fields):
                findings.append(f"{hook_label} condition field not allowed by state_field_contract: {condition_field}")
        if "copy_variants" not in hook:
            findings.append(f"{hook_label} missing copy_variants")
        if not hook.get("guardrail"):
            findings.append(f"{hook_label} missing guardrail")
        findings.extend(validate_copy_modules(hook_label, hook, context))
    return findings


def validate_canonical_examples(label: str, entry: dict[str, Any], context: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    examples = entry.get("canonical_examples")
    graph_alignment = entry.get("graph_alignment") or {}
    if not isinstance(examples, list) or not examples:
        findings.append(f"{label}.canonical_examples must be a non-empty array")
        return findings
    for index, example in enumerate(examples):
        example_label = f"{label}.canonical_examples[{index}]"
        for field in ["display_label", "object_type", "graph_ref", "reason_compact", "listening_angle", "claim_refs", "graph_audit_ref"]:
            if field not in example:
                findings.append(f"{example_label} missing {field}")
        graph_ref = example.get("graph_ref") or {}
        for field in ["family_id", "archetype_id", "archetype_ref", "object_type", "entity_id"]:
            if graph_ref.get(field) in (None, ""):
                findings.append(f"{example_label}.graph_ref missing {field}")
        for field in ["family_id", "archetype_id", "archetype_ref"]:
            if graph_ref.get(field) != graph_alignment.get(field):
                findings.append(f"{example_label}.graph_ref.{field} does not match graph_alignment")
        findings.extend(validate_claim_refs(example.get("claim_refs") or [], context, f"{example_label}.claim_refs"))
        graph_audit_ref = example.get("graph_audit_ref")
        context["graph_audit_refs_checked"] += 1
        if graph_audit_ref not in context["graph_audit_ids"]:
            findings.append(f"{example_label}.graph_audit_ref not found in research graph audit: {graph_audit_ref}")
    return findings


def validate_claim_refs(refs: list[Any], context: dict[str, Any], label: str) -> list[str]:
    findings: list[str] = []
    if not isinstance(refs, list) or not refs:
        findings.append(f"{label} must be a non-empty array")
        return findings
    for ref in refs:
        context["claim_refs_checked"] += 1
        if ref not in context["claim_ids"]:
            findings.append(f"{label} unknown claim_ref: {ref}")
    return findings


def validate_source_refs(refs: list[Any], context: dict[str, Any], label: str) -> list[str]:
    findings: list[str] = []
    if not isinstance(refs, list) or not refs:
        findings.append(f"{label} must be a non-empty array")
        return findings
    for ref in refs:
        context["source_refs_checked"] += 1
        if ref not in context["source_ids"]:
            findings.append(f"{label} unknown source_ref: {ref}")
    return findings


def condition_fields(node: Any) -> list[str]:
    fields: list[str] = []
    if isinstance(node, dict):
        field = node.get("field")
        if isinstance(field, str):
            fields.append(field)
        for value in node.values():
            fields.extend(condition_fields(value))
    elif isinstance(node, list):
        for value in node:
            fields.extend(condition_fields(value))
    return fields


def state_field_allowed(field: str, allowed_patterns: dict[str, str]) -> bool:
    if field in allowed_patterns:
        return True
    for pattern in allowed_patterns:
        regex = re.escape(pattern)
        regex = regex.replace(r"\[archetype_ref\]", r"\[[^\]]+\]")
        regex = regex.replace(r"\[entity_id\]", r"\[[^\]]+\]")
        regex = regex.replace(r"\[tag_id\]", r"\[[^\]]+\]")
        if re.fullmatch(regex, field):
            return True
    return False


def empty_summary(store: PackStore) -> dict[str, Any]:
    return {
        "source": rel(store.source),
        "render_pack_id": None,
        "entry_count": 0,
        "claim_refs_checked": 0,
        "source_refs_checked": 0,
        "graph_audit_refs_checked": 0,
        "copy_variant_sets_checked": 0,
    }


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


if __name__ == "__main__":
    sys.exit(main())
