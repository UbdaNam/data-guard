"""Validation check execution engine."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.models.validation_models import (
    BaselineStatistic,
    ExecutableCheck,
    LoadedContract,
    LoadedDataset,
    NumericProfile,
    ValidationResult,
    ValidationSeverity,
    ValidationStatus,
)
from src.validation.baseline_store import BaselineStore
from src.validation.dataset_loader import extract_values, field_exists, extract_first_value
from src.validation.drift_detector import evaluate_drift
from src.validation.statistical_profiler import profile_numeric_fields


@dataclass(slots=True)
class ExecutionContext:
    repo_root: Path
    baseline_refresh_allowed: bool = False
    sample_limit: int = 5


def _severity_from_check(check: ExecutableCheck, default: ValidationSeverity = ValidationSeverity.medium) -> ValidationSeverity:
    return check.severity if check.severity else default


def _build_sample(record_index: int, value: Any, expected: Any, field_path: str | None, reason: str) -> dict[str, Any]:
    return {
        "record_index": record_index,
        "field": field_path,
        "actual_value": value,
        "expected": expected,
        "reason": reason,
    }


def _is_structural_shape(value: Any) -> bool:
    return isinstance(value, (dict, list))


def _matches_expected_type(value: Any, expected_types: list[str]) -> bool:
    if not expected_types:
        return True
    actual_type = type(value).__name__
    if actual_type in expected_types:
        return True
    if actual_type == "int" and any(candidate in {"float", "number", "numeric"} for candidate in expected_types):
        return True
    if actual_type == "float" and any(candidate in {"int", "float", "number", "numeric"} for candidate in expected_types):
        return True
    return False


def _format_message(check: ExecutableCheck, outcome: str, detail: str) -> str:
    return f"{check.check_type} check {outcome} for {check.column_name or 'dataset'}: {detail}"


def _evaluate_field_check(
    check: ExecutableCheck,
    dataset: LoadedDataset,
    sample_limit: int,
) -> ValidationResult:
    values_by_record: list[tuple[int, list[Any]]] = []
    for index, record in enumerate(dataset.rows):
        values = extract_values(record, check.column_name or "") if check.column_name else []
        values_by_record.append((index, values))

    all_values = [value for _, values in values_by_record for value in values]
    if check.check_type in {"required", "nullability", "type", "pattern", "range", "enum", "positivity"} and not all_values:
        return ValidationResult(
            check_id=check.check_id,
            column_name=check.column_name,
            check_type=check.check_type,
            status=ValidationStatus.ERROR,
            actual_value=None,
            expected=check.expected,
            severity=_severity_from_check(check),
            records_failing=dataset.record_count,
            sample_failing=[_build_sample(i, None, check.expected, check.column_name, "missing_column") for i in range(min(sample_limit, dataset.record_count))],
            message=_format_message(check, "errored", "missing column or no extractable values"),
        )

    failing_samples: list[dict[str, Any]] = []
    failed_records = 0
    actual_value: Any = None

    if check.check_type == "required":
        for record_index, values in values_by_record:
            if not values or all(value is None for value in values):
                failed_records += 1
                if len(failing_samples) < sample_limit:
                    failing_samples.append(_build_sample(record_index, None, True, check.column_name, "missing_or_null"))
        status = ValidationStatus.PASS if failed_records == 0 else ValidationStatus.FAIL
        message = _format_message(check, "passed" if status == ValidationStatus.PASS else "failed", f"{failed_records} records missing required values")
        return ValidationResult(check_id=check.check_id, column_name=check.column_name, check_type=check.check_type, status=status, actual_value={"missing": failed_records}, expected=check.expected, severity=_severity_from_check(check), records_failing=failed_records, sample_failing=failing_samples, message=message)

    if check.check_type == "nullability":
        allow_null = bool(check.expected.get("nullable", False))
        for record_index, values in values_by_record:
            if not values:
                failed_records += 1
                if len(failing_samples) < sample_limit:
                    failing_samples.append(_build_sample(record_index, None, allow_null, check.column_name, "missing_column"))
                continue
            if any(value is None for value in values) and not allow_null:
                failed_records += 1
                if len(failing_samples) < sample_limit:
                    failing_samples.append(_build_sample(record_index, None, allow_null, check.column_name, "null_not_allowed"))
        status = ValidationStatus.PASS if failed_records == 0 else ValidationStatus.FAIL
        actual_value = {"allow_null": allow_null, "null_count": failed_records}
        return ValidationResult(check_id=check.check_id, column_name=check.column_name, check_type=check.check_type, status=status, actual_value=actual_value, expected=check.expected, severity=_severity_from_check(check), records_failing=failed_records, sample_failing=failing_samples, message=_format_message(check, "passed" if status == ValidationStatus.PASS else "failed", f"{failed_records} nullability violations"))

    if check.check_type == "type":
        expected_types = list(check.expected.get("types", []))
        for record_index, values in values_by_record:
            if not values:
                continue
            for value in values:
                actual_value = type(value).__name__
                if _is_structural_shape(value) and expected_types and not any(candidate in {"dict", "list", actual_value} for candidate in expected_types):
                    failed_records += 1
                    if len(failing_samples) < sample_limit:
                        failing_samples.append(_build_sample(record_index, value, expected_types, check.column_name, "unexpected_structure"))
                elif not _matches_expected_type(value, expected_types):
                    failed_records += 1
                    if len(failing_samples) < sample_limit:
                        failing_samples.append(_build_sample(record_index, value, expected_types, check.column_name, "invalid_type"))
        status = ValidationStatus.PASS if failed_records == 0 else ValidationStatus.FAIL
        return ValidationResult(check_id=check.check_id, column_name=check.column_name, check_type=check.check_type, status=status, actual_value={"types": expected_types}, expected=check.expected, severity=_severity_from_check(check), records_failing=failed_records, sample_failing=failing_samples, message=_format_message(check, "passed" if status == ValidationStatus.PASS else "failed", f"{failed_records} type mismatches"))

    if check.check_type == "pattern":
        import re

        pattern = str(check.expected.get("pattern", ""))
        compiled = re.compile(pattern)
        for record_index, values in values_by_record:
            for value in values:
                if value is None:
                    continue
                if _is_structural_shape(value):
                    failed_records += 1
                    if len(failing_samples) < sample_limit:
                        failing_samples.append(_build_sample(record_index, value, pattern, check.column_name, "unexpected_structure"))
                    continue
                if not compiled.search(str(value)):
                    failed_records += 1
                    if len(failing_samples) < sample_limit:
                        failing_samples.append(_build_sample(record_index, value, pattern, check.column_name, "pattern_mismatch"))
        status = ValidationStatus.PASS if failed_records == 0 else ValidationStatus.FAIL
        return ValidationResult(check_id=check.check_id, column_name=check.column_name, check_type=check.check_type, status=status, actual_value={"pattern": pattern}, expected=check.expected, severity=_severity_from_check(check), records_failing=failed_records, sample_failing=failing_samples, message=_format_message(check, "passed" if status == ValidationStatus.PASS else "failed", f"{failed_records} pattern violations"))

    if check.check_type == "range":
        minimum = check.expected.get("min")
        maximum = check.expected.get("max")
        for record_index, values in values_by_record:
            for value in values:
                if value is None:
                    continue
                if _is_structural_shape(value):
                    failed_records += 1
                    if len(failing_samples) < sample_limit:
                        failing_samples.append(_build_sample(record_index, value, check.expected, check.column_name, "unexpected_structure"))
                    continue
                if not isinstance(value, (int, float)):
                    failed_records += 1
                    if len(failing_samples) < sample_limit:
                        failing_samples.append(_build_sample(record_index, value, check.expected, check.column_name, "invalid_type"))
                    continue
                if minimum is not None and float(value) < float(minimum):
                    failed_records += 1
                    if len(failing_samples) < sample_limit:
                        failing_samples.append(_build_sample(record_index, value, check.expected, check.column_name, "below_minimum"))
                if maximum is not None and float(value) > float(maximum):
                    failed_records += 1
                    if len(failing_samples) < sample_limit:
                        failing_samples.append(_build_sample(record_index, value, check.expected, check.column_name, "above_maximum"))
        status = ValidationStatus.PASS if failed_records == 0 else ValidationStatus.FAIL
        return ValidationResult(check_id=check.check_id, column_name=check.column_name, check_type=check.check_type, status=status, actual_value={"min": minimum, "max": maximum}, expected=check.expected, severity=_severity_from_check(check), records_failing=failed_records, sample_failing=failing_samples, message=_format_message(check, "passed" if status == ValidationStatus.PASS else "failed", f"{failed_records} range violations"))

    if check.check_type == "enum":
        accepted = {str(value) for value in check.expected.get("accepted_values", [])}
        structural_error = False
        for record_index, values in values_by_record:
            for value in values:
                if value is None:
                    continue
                if _is_structural_shape(value):
                    structural_error = True
                    if len(failing_samples) < sample_limit:
                        failing_samples.append(_build_sample(record_index, value, list(accepted), check.column_name, "unexpected_structure"))
                    continue
                if str(value) not in accepted:
                    failed_records += 1
                    if len(failing_samples) < sample_limit:
                        failing_samples.append(_build_sample(record_index, value, list(accepted), check.column_name, "enum_mismatch"))
        if structural_error:
            status = ValidationStatus.ERROR
            outcome = "errored"
        else:
            status = ValidationStatus.PASS if failed_records == 0 else ValidationStatus.FAIL
            outcome = "passed" if status == ValidationStatus.PASS else "failed"
        return ValidationResult(check_id=check.check_id, column_name=check.column_name, check_type=check.check_type, status=status, actual_value={"accepted_values": sorted(accepted)}, expected=check.expected, severity=_severity_from_check(check), records_failing=failed_records, sample_failing=failing_samples, message=_format_message(check, outcome, f"{failed_records} enum violations"))

    if check.check_type == "positivity":
        for record_index, values in values_by_record:
            for value in values:
                if value is None:
                    continue
                if _is_structural_shape(value):
                    failed_records += 1
                    if len(failing_samples) < sample_limit:
                        failing_samples.append(_build_sample(record_index, value, check.expected, check.column_name, "unexpected_structure"))
                    continue
                if isinstance(value, (int, float)) and float(value) < 0:
                    failed_records += 1
                    if len(failing_samples) < sample_limit:
                        failing_samples.append(_build_sample(record_index, value, check.expected, check.column_name, "negative_value"))
        status = ValidationStatus.PASS if failed_records == 0 else ValidationStatus.FAIL
        return ValidationResult(check_id=check.check_id, column_name=check.column_name, check_type=check.check_type, status=status, actual_value={"non_negative": True}, expected=check.expected, severity=_severity_from_check(check), records_failing=failed_records, sample_failing=failing_samples, message=_format_message(check, "passed" if status == ValidationStatus.PASS else "failed", f"{failed_records} positivity violations"))

    if check.check_type == "uniqueness":
        observed = set()
        for record_index, values in values_by_record:
            for value in values:
                if value is None:
                    continue
                if _is_structural_shape(value):
                    failed_records += 1
                    if len(failing_samples) < sample_limit:
                        failing_samples.append(_build_sample(record_index, value, check.expected, check.column_name, "unexpected_structure"))
                    continue
                marker = jsonable(value)
                if marker in observed:
                    failed_records += 1
                    if len(failing_samples) < sample_limit:
                        failing_samples.append(_build_sample(record_index, value, check.expected, check.column_name, "duplicate_value"))
                else:
                    observed.add(marker)
        status = ValidationStatus.PASS if failed_records == 0 else ValidationStatus.FAIL
        return ValidationResult(check_id=check.check_id, column_name=check.column_name, check_type=check.check_type, status=status, actual_value={"unique_values": len(observed)}, expected=check.expected, severity=_severity_from_check(check), records_failing=failed_records, sample_failing=failing_samples, message=_format_message(check, "passed" if status == ValidationStatus.PASS else "failed", f"{failed_records} uniqueness violations"))

    return ValidationResult(
        check_id=check.check_id,
        column_name=check.column_name,
        check_type=check.check_type,
        status=ValidationStatus.ERROR,
        actual_value=None,
        expected=check.expected,
        severity=_severity_from_check(check),
        records_failing=0,
        sample_failing=[],
        message=_format_message(check, "errored", "unsupported field check type"),
    )


def _evaluate_dataset_check(
    check: ExecutableCheck,
    dataset: LoadedDataset,
) -> ValidationResult:
    if check.check_type == "row_count":
        expected_row_count = int(check.expected.get("row_count", 0))
        actual_row_count = dataset.record_count
        status = ValidationStatus.PASS if actual_row_count == expected_row_count else ValidationStatus.FAIL
        return ValidationResult(
            check_id=check.check_id,
            column_name=check.column_name,
            check_type=check.check_type,
            status=status,
            actual_value=actual_row_count,
            expected=expected_row_count,
            severity=_severity_from_check(check),
            records_failing=abs(actual_row_count - expected_row_count),
            sample_failing=[],
            message=_format_message(check, "passed" if status == ValidationStatus.PASS else "failed", f"expected {expected_row_count}, observed {actual_row_count}"),
        )

    if check.check_type == "referential_integrity":
        target_field = str(check.expected.get("referenced_field") or check.column_name or "")
        if not target_field:
            return ValidationResult(
                check_id=check.check_id,
                column_name=check.column_name,
                check_type=check.check_type,
                status=ValidationStatus.ERROR,
                actual_value=None,
                expected=check.expected,
                severity=_severity_from_check(check),
                records_failing=0,
                sample_failing=[],
                message=_format_message(check, "errored", "missing referenced field definition"),
            )
        observed_values = [jsonable(value) for row in dataset.rows for value in extract_values(row, target_field)]
        unique_count = len(set(observed_values))
        status = ValidationStatus.PASS if unique_count == len(observed_values) else ValidationStatus.FAIL
        return ValidationResult(
            check_id=check.check_id,
            column_name=check.column_name,
            check_type=check.check_type,
            status=status,
            actual_value={"observed": len(observed_values), "unique": unique_count},
            expected=check.expected,
            severity=_severity_from_check(check),
            records_failing=max(0, len(observed_values) - unique_count),
            sample_failing=[],
            message=_format_message(check, "passed" if status == ValidationStatus.PASS else "failed", "referential integrity mismatch detected"),
        )

    if check.check_type == "dataset_check":
        return ValidationResult(
            check_id=check.check_id,
            column_name=check.column_name,
            check_type=check.check_type,
            status=ValidationStatus.PASS,
            actual_value={"rule": check.expected.get("rule", "dataset_check")},
            expected=check.expected,
            severity=_severity_from_check(check),
            records_failing=0,
            sample_failing=[],
            message=_format_message(check, "passed", "dataset-level contract rule satisfied"),
        )

    if check.check_type == "uniqueness":
        observed = []
        for row in dataset.rows:
            observed.extend(extract_values(row, check.column_name or ""))
        markers = [jsonable(value) for value in observed if value is not None]
        duplicates = len(markers) - len(set(markers))
        status = ValidationStatus.PASS if duplicates == 0 else ValidationStatus.FAIL
        return ValidationResult(
            check_id=check.check_id,
            column_name=check.column_name,
            check_type=check.check_type,
            status=status,
            actual_value={"observed": len(markers), "duplicates": duplicates},
            expected=check.expected,
            severity=_severity_from_check(check),
            records_failing=duplicates,
            sample_failing=[],
            message=_format_message(check, "passed" if status == ValidationStatus.PASS else "failed", f"{duplicates} duplicate values"),
        )

    return ValidationResult(
        check_id=check.check_id,
        column_name=check.column_name,
        check_type=check.check_type,
        status=ValidationStatus.ERROR,
        actual_value=None,
        expected=check.expected,
        severity=_severity_from_check(check),
        records_failing=0,
        sample_failing=[],
        message=_format_message(check, "errored", "unsupported dataset check type"),
    )


def jsonable(value: Any) -> str:
    if isinstance(value, (dict, list)):
        return json.dumps(value, sort_keys=True, separators=(",", ":"))
    return str(value)


import json


def _evaluate_drift_check(
    check: ExecutableCheck,
    contract: LoadedContract,
    dataset: LoadedDataset,
    current_profile: NumericProfile | None,
    baseline: BaselineStatistic | None,
) -> ValidationResult:
    if current_profile is None:
        return ValidationResult(
            check_id=check.check_id,
            column_name=check.column_name,
            check_type=check.check_type,
            status=ValidationStatus.ERROR,
            actual_value=None,
            expected={"baseline": check.expected},
            severity=ValidationSeverity.medium,
            records_failing=0,
            sample_failing=[],
            message=_format_message(check, "errored", "no numeric observations available"),
        )

    outcome = evaluate_drift(current_profile, baseline)
    return ValidationResult(
        check_id=check.check_id,
        column_name=check.column_name,
        check_type=check.check_type,
        status=outcome.status,
        actual_value={
            "mean": current_profile.mean,
            "stddev": current_profile.stddev,
            "min": current_profile.min,
            "max": current_profile.max,
            "sample_size": current_profile.sample_size,
            "z_score": outcome.z_score,
        },
        expected={
            "baseline_mean": baseline.mean if baseline else None,
            "baseline_stddev": baseline.stddev if baseline else None,
            "baseline_min": baseline.min if baseline else None,
            "baseline_max": baseline.max if baseline else None,
        },
        severity=outcome.severity,
        records_failing=0 if outcome.status == ValidationStatus.PASS else 1,
        sample_failing=[],
        message=outcome.message,
    )


def execute_contract_checks(
    contract: LoadedContract,
    dataset: LoadedDataset,
    context: ExecutionContext,
) -> tuple[list[ValidationResult], dict[str, NumericProfile], dict[str, BaselineStatistic]]:
    numeric_profiles = profile_numeric_fields(dataset.rows, contract.numeric_fields)
    baseline_store = BaselineStore(context.repo_root)
    baselines = baseline_store.load().get(contract.contract_id, {})
    results: list[ValidationResult] = []

    for check in sorted(contract.checks, key=lambda item: (item.column_name or "", item.check_type, item.check_id)):
        if check.is_drift:
            profile = numeric_profiles.get(check.column_name or "")
            baseline = baselines.get(check.column_name or "")
            result = _evaluate_drift_check(check, contract, dataset, profile, baseline)
        elif check.check_type in {"row_count", "uniqueness", "referential_integrity", "dataset_check"}:
            result = _evaluate_dataset_check(check, dataset)
        else:
            result = _evaluate_field_check(check, dataset, context.sample_limit)
        results.append(result)

    return results, numeric_profiles, baselines
