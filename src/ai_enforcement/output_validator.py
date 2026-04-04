"""Structured output schema validation for Week 2 governed surface."""

from __future__ import annotations

from typing import Any

from src.models.ai_enforcement_models import AIValidationStatus, StructuredOutputCheckRecord


def _is_expected_type(value: Any, expected_type: str) -> bool:
    if expected_type == "string":
        return isinstance(value, str)
    if expected_type == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected_type == "object":
        return isinstance(value, dict)
    if expected_type == "array":
        return isinstance(value, list)
    if expected_type == "boolean":
        return isinstance(value, bool)
    return True


def validate_output_records(records: list[dict[str, Any]], schema: dict[str, Any]) -> list[StructuredOutputCheckRecord]:
    schema_id = str(schema.get("schema_id", "week2_verdict_structured_output"))
    schema_version = str(schema.get("schema_version", "v1"))
    required = list(schema.get("required", []))
    properties = dict(schema.get("properties", {}))
    allow_additional = bool(schema.get("allow_additional", False))

    results: list[StructuredOutputCheckRecord] = []
    for index, record in enumerate(records):
        record_id = str(record.get("record_id") or record.get("id") or f"line_{index + 1}")
        missing_required: list[str] = []
        unknown_fields: list[str] = []
        type_mismatches: list[dict[str, Any]] = []
        nested_violations: list[dict[str, Any]] = []

        for name in required:
            if name not in record or record.get(name) in (None, ""):
                missing_required.append(name)

        for field_name, value in record.items():
            if field_name not in properties:
                if not allow_additional:
                    unknown_fields.append(field_name)
                continue
            expected_type = str(properties[field_name].get("type", ""))
            if expected_type and not _is_expected_type(value, expected_type):
                type_mismatches.append(
                    {
                        "field": field_name,
                        "expected": expected_type,
                        "actual": type(value).__name__,
                    }
                )
            if expected_type == "object" and not isinstance(value, dict):
                nested_violations.append({"field": field_name, "reason": "expected_object"})
            if expected_type == "array" and not isinstance(value, list):
                nested_violations.append({"field": field_name, "reason": "expected_array"})

        has_failures = bool(missing_required or unknown_fields or type_mismatches or nested_violations)
        results.append(
            StructuredOutputCheckRecord(
                record_id=record_id,
                schema_id=schema_id,
                schema_version=schema_version,
                validation_status=AIValidationStatus.FAIL if has_failures else AIValidationStatus.PASS,
                unknown_fields=sorted(unknown_fields),
                missing_required_fields=sorted(missing_required),
                type_mismatches=sorted(type_mismatches, key=lambda x: str(x.get("field", ""))),
                nested_structure_violations=sorted(nested_violations, key=lambda x: str(x.get("field", ""))),
            )
        )

    return results
