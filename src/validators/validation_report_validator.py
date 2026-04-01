"""Validation report schema and completeness checks."""

from __future__ import annotations

from typing import Any

from src.models.validation_models import ValidationReport, ValidationResult, ValidationStatus

REQUIRED_TOP_LEVEL_FIELDS = {
    "report_id",
    "contract_id",
    "snapshot_id",
    "run_timestamp",
    "total_checks",
    "passed",
    "failed",
    "warned",
    "errored",
    "results",
}

REQUIRED_RESULT_FIELDS = {
    "check_id",
    "column_name",
    "check_type",
    "status",
    "actual_value",
    "expected",
    "severity",
    "records_failing",
    "sample_failing",
    "message",
}


def validate_report_payload(payload: dict[str, Any], strict: bool = True) -> list[str]:
    issues: list[str] = []
    missing_top = sorted(REQUIRED_TOP_LEVEL_FIELDS - set(payload))
    for field_name in missing_top:
        issues.append(f"Missing top-level field: {field_name}")

    results = payload.get("results", [])
    if not isinstance(results, list):
        issues.append("Field 'results' must be a list")
        results = []

    for index, result in enumerate(results):
        if not isinstance(result, dict):
            issues.append(f"Result at index {index} must be an object")
            continue
        missing = REQUIRED_RESULT_FIELDS - set(result)
        for field_name in sorted(missing):
            issues.append(f"Missing result field at index {index}: {field_name}")
        if result.get("status") not in {status.value for status in ValidationStatus}:
            issues.append(f"Invalid result status at index {index}: {result.get('status')}")

    if strict and issues:
        raise ValueError("; ".join(issues))
    return issues


def validate_report_model(report: ValidationReport) -> list[str]:
    return validate_report_payload(report.model_dump(mode="json"), strict=False)
