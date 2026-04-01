"""Result ordering and summary aggregation for validation runs."""

from __future__ import annotations

from collections import Counter
from typing import Iterable

from src.models.validation_models import ValidationReport, ValidationResult, ValidationStatus


def result_order_key(result: ValidationResult) -> tuple[str, str, str]:
    return (
        result.column_name or "",
        result.check_type,
        result.check_id,
    )


def order_results(results: Iterable[ValidationResult]) -> list[ValidationResult]:
    return sorted(list(results), key=result_order_key)


def summarize_results(report_id: str, contract_id: str, snapshot_id: str, run_timestamp: str, results: list[ValidationResult]) -> ValidationReport:
    ordered = order_results(results)
    counter = Counter(result.status for result in ordered)
    return ValidationReport(
        report_id=report_id,
        contract_id=contract_id,
        snapshot_id=snapshot_id,
        run_timestamp=run_timestamp,
        total_checks=len(ordered),
        passed=counter.get(ValidationStatus.PASS, 0),
        failed=counter.get(ValidationStatus.FAIL, 0),
        warned=counter.get(ValidationStatus.WARN, 0),
        errored=counter.get(ValidationStatus.ERROR, 0),
        results=ordered,
    )
