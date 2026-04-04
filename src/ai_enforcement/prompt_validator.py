"""Prompt input schema validation for Week 3 governed surface."""

from __future__ import annotations

from typing import Any

from src.models.ai_enforcement_models import AIValidationStatus, PromptInputCheckRecord


def _check_type(value: Any, expected_type: str) -> bool:
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


def validate_prompt_records(records: list[dict[str, Any]], schema: dict[str, Any], prompt_surface: str = "week3_prompt_text") -> tuple[list[PromptInputCheckRecord], list[dict[str, Any]]]:
    required = list(schema.get("required", []))
    properties = dict(schema.get("properties", {}))
    schema_version = str(schema.get("schema_version", "v1"))

    results: list[PromptInputCheckRecord] = []
    invalid_payloads: list[dict[str, Any]] = []

    for index, record in enumerate(records):
        record_id = str(record.get("record_id") or record.get("id") or f"line_{index + 1}")
        failures: list[str] = []

        for field_name in required:
            if field_name not in record or record.get(field_name) in (None, ""):
                failures.append(f"missing_required:{field_name}")

        for field_name, field_schema in properties.items():
            if field_name not in record:
                continue
            expected_type = str(field_schema.get("type", ""))
            if expected_type and not _check_type(record.get(field_name), expected_type):
                failures.append(f"type_mismatch:{field_name}:{expected_type}")

        status = AIValidationStatus.PASS if not failures else AIValidationStatus.FAIL
        quarantined = status != AIValidationStatus.PASS

        if quarantined:
            invalid_payloads.append(record)

        results.append(
            PromptInputCheckRecord(
                record_id=record_id,
                schema_version=schema_version,
                prompt_surface=prompt_surface,
                validation_status=status,
                failure_reasons=failures,
                quarantined=quarantined,
                quarantine_path=None,
            )
        )

    return results, invalid_payloads
