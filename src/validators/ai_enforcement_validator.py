"""Payload validators for AI enforcement artifacts."""

from __future__ import annotations

from typing import Any

from src.models.ai_enforcement_models import AIMetricsReport, AIViolationRecord, EmbeddingBaseline, EmbeddingComparisonResult, QuarantineRecord


def _validate_model(model_cls: Any, payload: dict[str, Any], strict: bool) -> list[str]:
    issues: list[str] = []
    try:
        model_cls.model_validate(payload)
    except Exception as exc:  # pragma: no cover
        issues.append(str(exc))
    if strict and issues:
        raise ValueError("; ".join(issues))
    return issues


def validate_ai_metrics_payload(payload: dict[str, Any], strict: bool = True) -> list[str]:
    return _validate_model(AIMetricsReport, payload, strict)


def validate_ai_violation_payload(payload: dict[str, Any], strict: bool = True) -> list[str]:
    return _validate_model(AIViolationRecord, payload, strict)


def validate_quarantine_payload(payload: dict[str, Any], strict: bool = True) -> list[str]:
    return _validate_model(QuarantineRecord, payload, strict)


def validate_embedding_baseline_payload(payload: dict[str, Any], strict: bool = True) -> list[str]:
    return _validate_model(EmbeddingBaseline, payload, strict)


def validate_embedding_comparison_payload(payload: dict[str, Any], strict: bool = True) -> list[str]:
    return _validate_model(EmbeddingComparisonResult, payload, strict)
