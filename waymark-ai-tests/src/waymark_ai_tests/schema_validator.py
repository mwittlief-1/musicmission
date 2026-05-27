from __future__ import annotations

import re
from typing import Any, Dict, List


def validate_json(document: Any, schema: Dict[str, Any]) -> Dict[str, Any]:
    try:
        from jsonschema import Draft202012Validator, FormatChecker
    except ModuleNotFoundError:
        errors: List[str] = []
        _validate_subset(document, schema, "<root>", errors, schema)
        return {
            "validator": "builtin_subset",
            "valid": not errors,
            "error_count": len(errors),
            "errors": errors,
        }

    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(document), key=lambda error: list(error.path))
    formatted = []
    for error in errors:
        path = ".".join(str(part) for part in error.path) if error.path else "<root>"
        formatted.append(f"{path}: {error.message}")
    return {
        "validator": "jsonschema",
        "valid": not formatted,
        "error_count": len(formatted),
        "errors": formatted,
    }


def _validate_subset(document: Any, schema: Dict[str, Any], path: str, errors: List[str], root_schema: Dict[str, Any]) -> None:
    if "$ref" in schema:
        schema = _resolve_ref(schema["$ref"], root_schema)

    expected_type = schema.get("type")
    if expected_type is not None and not _matches_type(document, expected_type):
        errors.append(f"{path}: expected {expected_type}, got {type(document).__name__}")
        return

    if "const" in schema and document != schema["const"]:
        errors.append(f"{path}: expected const {schema['const']!r}")

    if "enum" in schema and document not in schema["enum"]:
        errors.append(f"{path}: expected one of {schema['enum']!r}")

    if isinstance(document, str):
        if "minLength" in schema and len(document) < schema["minLength"]:
            errors.append(f"{path}: string shorter than minLength {schema['minLength']}")
        if "pattern" in schema and not re.search(schema["pattern"], document):
            errors.append(f"{path}: string does not match pattern {schema['pattern']}")

    if isinstance(document, (int, float)) and not isinstance(document, bool):
        if "minimum" in schema and document < schema["minimum"]:
            errors.append(f"{path}: number below minimum {schema['minimum']}")
        if "maximum" in schema and document > schema["maximum"]:
            errors.append(f"{path}: number above maximum {schema['maximum']}")

    if isinstance(document, list):
        if "minItems" in schema and len(document) < schema["minItems"]:
            errors.append(f"{path}: array shorter than minItems {schema['minItems']}")
        if "maxItems" in schema and len(document) > schema["maxItems"]:
            errors.append(f"{path}: array longer than maxItems {schema['maxItems']}")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(document):
                _validate_subset(item, item_schema, f"{path}.{index}", errors, root_schema)

    if isinstance(document, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in document:
                errors.append(f"{path}: missing required property {key}")

        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            allowed = set(properties.keys())
            for key in document.keys():
                if key not in allowed:
                    errors.append(f"{path}: unexpected property {key}")

        for key, property_schema in properties.items():
            if key in document:
                _validate_subset(document[key], property_schema, f"{path}.{key}", errors, root_schema)


def _resolve_ref(ref: str, root_schema: Dict[str, Any]) -> Dict[str, Any]:
    if not ref.startswith("#/"):
        return {}
    current: Any = root_schema
    for part in ref[2:].split("/"):
        if not isinstance(current, dict):
            return {}
        current = current.get(part)
    return current if isinstance(current, dict) else {}


def _matches_type(document: Any, expected_type: Any) -> bool:
    if isinstance(expected_type, list):
        return any(_matches_type(document, one_type) for one_type in expected_type)
    if expected_type == "object":
        return isinstance(document, dict)
    if expected_type == "array":
        return isinstance(document, list)
    if expected_type == "string":
        return isinstance(document, str)
    if expected_type == "integer":
        return isinstance(document, int) and not isinstance(document, bool)
    if expected_type == "number":
        return isinstance(document, (int, float)) and not isinstance(document, bool)
    if expected_type == "boolean":
        return isinstance(document, bool)
    if expected_type == "null":
        return document is None
    return True
