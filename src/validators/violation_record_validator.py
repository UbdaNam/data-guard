"""Violation record validation helpers for Feature 4."""

from __future__ import annotations

from typing import Any

from src.models.attribution_models import ViolationRecord


def validate_violation_record_payload(payload: dict[str, Any], strict: bool = True) -> list[str]:
    issues: list[str] = []
    try:
        ViolationRecord.model_validate(payload)
    except Exception as exc:  # pragma: no cover - defensive validation guard
        issues.append(str(exc))
    if strict and issues:
        raise ValueError("; ".join(issues))
    return issues


def validate_violation_records_payload(payloads: list[dict[str, Any]], strict: bool = True) -> list[str]:
    issues: list[str] = []
    for index, payload in enumerate(payloads):
        try:
            ViolationRecord.model_validate(payload)
        except Exception as exc:  # pragma: no cover - defensive validation guard
            issues.append(f"Record {index}: {exc}")
    if strict and issues:
        raise ValueError("; ".join(issues))
    return issues
