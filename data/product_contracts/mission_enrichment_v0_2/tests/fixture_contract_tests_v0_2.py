#!/usr/bin/env python3
"""Fixture contract tests for Cartenza Mission Enrichment v0.2."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

try:
    import jsonschema
except ImportError as exc:  # pragma: no cover - local dependency guard.
    jsonschema = None
    JSONSCHEMA_IMPORT_ERROR = exc
else:
    JSONSCHEMA_IMPORT_ERROR = None


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_ROOT = PACKAGE_ROOT / "scripts"
sys.path.insert(0, str(SCRIPT_ROOT))

from prefilter_secondary_tags_v0_2 import load_registry, prefilter_secondary_tags
from validate_mission_enrichment_output_v0_2 import validate_contract


REGISTRY_PATH = PACKAGE_ROOT / "registry" / "secondary_reaction_tag_registry_v0_2.json"
INPUT_SCHEMA_PATH = PACKAGE_ROOT / "schemas" / "mission_enrichment_input_v0_2.schema.json"
OUTPUT_SCHEMA_PATH = PACKAGE_ROOT / "schemas" / "mission_enrichment_output_v0_2.schema.json"
REGISTRY_SCHEMA_PATH = PACKAGE_ROOT / "schemas" / "secondary_reaction_tag_registry_v0_2.schema.json"
POSITIVE_DIR = PACKAGE_ROOT / "fixtures" / "positive"
NEGATIVE_DIR = PACKAGE_ROOT / "fixtures" / "negative"

POSITIVE_INPUT_FIXTURES = [
    "build45_like_runtime_candidate_input.json",
    "pop_forward_first_mission_input.json",
    "hiphop_rnb_forward_input.json",
    "country_folk_forward_input.json",
    "jazz_classical_instrumental_input.json",
    "electronic_dance_forward_input.json",
    "low_information_first_mission_input.json",
    "mature_mission_40_input.json",
    "boundary_test_mixed_signal_input.json",
    "context_dependence_mission_input.json",
]

NEGATIVE_INPUT_MAP = {
    "instrumental_with_lyrics_tag_output.json": "jazz_classical_instrumental_input.json",
    "voice_chip_on_non_vocal_track_output.json": "jazz_classical_instrumental_input.json",
    "less_like_this_after_ok_output.json": "boundary_test_mixed_signal_input.json",
}


def load_json(path: Path):
    return json.loads(path.read_text())


@unittest.skipIf(jsonschema is None, f"jsonschema unavailable: {JSONSCHEMA_IMPORT_ERROR}")
class MissionEnrichmentFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry_payload = load_json(REGISTRY_PATH)
        cls.registry = load_registry(REGISTRY_PATH)
        cls.input_schema = load_json(INPUT_SCHEMA_PATH)
        cls.output_schema = load_json(OUTPUT_SCHEMA_PATH)
        cls.registry_schema = load_json(REGISTRY_SCHEMA_PATH)

    def assert_schema_valid(self, instance, schema):
        validator = jsonschema.Draft202012Validator(schema)
        errors = sorted(validator.iter_errors(instance), key=lambda err: list(err.path))
        self.assertEqual([], [f"{list(error.path)}: {error.message}" for error in errors])

    def test_registry_schema_and_tag_policy(self):
        self.assert_schema_valid(self.registry_payload, self.registry_schema)
        tags = self.registry_payload["tags"]
        for tag_id, entry in tags.items():
            self.assertEqual(tag_id, entry["tag_id"])
        self.assertIn("DID_NOT_HOLD_ATTENTION", tags)
        self.assertIn("WRONG_VERSION_OR_RECORDING", tags)
        self.assertEqual(["dislike"], tags["LESS_LIKE_THIS"]["valid_primary_reactions"])
        for excluded in ("SLOP_SIGNAL", "TOO_HEAVY", "TOO_POLISHED", "RIFF_WORKED"):
            self.assertNotIn(excluded, tags)

    def test_positive_input_fixtures_validate_and_prefilter_bounds_hold(self):
        for fixture_name in POSITIVE_INPUT_FIXTURES:
            with self.subTest(fixture=fixture_name):
                payload = load_json(POSITIVE_DIR / fixture_name)
                self.assert_schema_valid(payload, self.input_schema)
                mission = payload["mission_context"]
                for route_item in payload["route_items"]:
                    prefiltered = route_item["prefiltered_secondary_tag_ids"]
                    self.assertGreaterEqual(len(prefiltered), 8)
                    self.assertLessEqual(len(prefiltered), 14)
                    recomputed = prefilter_secondary_tags(
                        route_item=route_item,
                        registry=self.registry,
                        mission_type=mission["mission_type"],
                        risk_level=mission["risk_level"],
                        user_atlas_context_brief=payload["user_atlas_context_brief"],
                    )
                    self.assertEqual(prefiltered, recomputed)
                    for tag_id in prefiltered:
                        self.assertIn(tag_id, payload["allowed_secondary_reaction_tags"])

    def test_positive_output_fixture_validates(self):
        input_payload = load_json(POSITIVE_DIR / "build45_like_runtime_candidate_input.json")
        output_payload = load_json(POSITIVE_DIR / "build45_like_runtime_candidate_output.json")
        self.assert_schema_valid(output_payload, self.output_schema)
        report = validate_contract(input_payload, output_payload, self.registry_payload)
        self.assertTrue(report.passed, report.as_dict())

    def test_negative_output_fixtures_are_rejected(self):
        default_input = "build45_like_runtime_candidate_input.json"
        negative_files = sorted(path.name for path in NEGATIVE_DIR.glob("*.json"))
        self.assertGreaterEqual(len(negative_files), 15)
        for fixture_name in negative_files:
            with self.subTest(fixture=fixture_name):
                input_name = NEGATIVE_INPUT_MAP.get(fixture_name, default_input)
                input_payload = load_json(POSITIVE_DIR / input_name)
                output_payload = load_json(NEGATIVE_DIR / fixture_name)
                report = validate_contract(input_payload, output_payload, self.registry_payload)
                self.assertFalse(report.passed, f"{fixture_name} unexpectedly passed")


if __name__ == "__main__":
    unittest.main()
