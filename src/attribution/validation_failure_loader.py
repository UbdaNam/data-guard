"""Validation report ingestion and eligibility filtering for Feature 4."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from src.models.attribution_models import AttributionEligibleResult, AttributionSkipRecord, SkipReason
from src.models.validation_models import ValidationReport, ValidationResult, ValidationStatus
from src.validators.validation_report_validator import validate_report_payload

REPO_ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = REPO_ROOT / "validation_reports"
ATTRIBUTABLE_ERROR_CLASSES = {"missing_column", "unexpected_structure", "invalid_type"}


def _result_order_key(result: ValidationResult) -> tuple[str, str, str, str]:
    return (
        result.status.value if isinstance(result.status, ValidationStatus) else str(result.status),
        result.column_name or "",
        result.check_type,
        result.check_id,
    )


def _report_order_key(path: Path) -> tuple[str, str]:
    return (path.stem, path.as_posix())


def list_report_paths(report_dir: Path = REPORT_DIR) -> list[Path]:
    if not report_dir.exists():
        return []
    paths = [path for path in report_dir.glob("*.json") if path.name != "readiness_index.json"]
    return sorted(paths, key=_report_order_key)


def load_validation_report(path: Path) -> tuple[ValidationReport | None, list[str]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - defensive I/O guard
        return None, [f"Failed to read validation report {path.as_posix()}: {exc}"]

    issues = validate_report_payload(payload, strict=False)
    try:
        report = ValidationReport.model_validate(payload)
    except Exception as exc:  # pragma: no cover - defensive validation guard
        issues.append(str(exc))
        return None, issues
    return report, issues


def load_validation_reports(report_paths: Iterable[Path] | None = None, report_dir: Path = REPORT_DIR) -> list[tuple[Path, ValidationReport | None, list[str]]]:
    paths = list(report_paths) if report_paths is not None else list_report_paths(report_dir)
    return [(path, *load_validation_report(path)) for path in sorted(paths, key=_report_order_key)]


def _is_attributable_error(result: ValidationResult) -> bool:
    if result.status != ValidationStatus.ERROR:
        return False
    if result.check_type in ATTRIBUTABLE_ERROR_CLASSES:
        return True
    reasons = {str(item.get("reason")) for item in result.sample_failing if isinstance(item, dict)}
    return bool(reasons & ATTRIBUTABLE_ERROR_CLASSES)


def _eligible_reason(result: ValidationResult) -> str:
    if result.status == ValidationStatus.FAIL:
        return "failing_check"
    if _is_attributable_error(result):
        return "attributable_error"
    return "non_eligible"


def filter_eligible_results(report: ValidationReport, source_path: Path) -> tuple[list[AttributionEligibleResult], list[AttributionSkipRecord]]:
    eligible: list[AttributionEligibleResult] = []
    skipped: list[AttributionSkipRecord] = []
    dataset_id = report.contract_id.split(".v", 1)[0].replace("_", ".")
    for result in sorted(report.results, key=_result_order_key):
        selected_reason = _eligible_reason(result)
        if selected_reason == "non_eligible":
            skipped.append(
                AttributionSkipRecord(
                    report_id=report.report_id,
                    contract_id=report.contract_id,
                    dataset_id=dataset_id,
                    check_id=result.check_id,
                    check_type=result.check_type,
                    column_name=result.column_name,
                    status=result.status.value if isinstance(result.status, ValidationStatus) else str(result.status),
                    skip_reason=SkipReason.passing_check if result.status == ValidationStatus.PASS else SkipReason.unsupported_status,
                    message=result.message,
                )
            )
            continue
        eligible.append(
            AttributionEligibleResult(
                report_id=report.report_id,
                contract_id=report.contract_id,
                dataset_id=dataset_id,
                check_id=result.check_id,
                check_type=result.check_type,
                column_name=result.column_name,
                status=result.status.value if isinstance(result.status, ValidationStatus) else str(result.status),
                severity=result.severity.value if hasattr(result.severity, "value") else str(result.severity),
                message=result.message,
                sample_failing=list(result.sample_failing),
                selected_reason=selected_reason,
                source_path=source_path.as_posix(),
            )
        )
    return eligible, skipped
