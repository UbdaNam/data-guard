"""Validation execution entry point for Feature 3."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any
from uuid import uuid4

from src.models.validation_models import ValidationResult, ValidationRun, ValidationStatus
from src.validation.baseline_store import BaselineStore
from src.validation.check_engine import ExecutionContext, execute_contract_checks
from src.validation.contract_loader import build_contract_load_context, load_contract
from src.validation.dataset_loader import load_dataset
from src.validation.report_writer import new_report_id, new_timestamp, write_report
from src.validation.result_aggregator import summarize_results
from src.validators.validation_report_validator import validate_report_model

REPO_ROOT = Path(__file__).resolve().parents[1]


def _snapshot_id(snapshot_path: str) -> str:
    path = Path(snapshot_path)
    if not path.exists():
        return f"missing:{path.as_posix()}"
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def _contract_load_error_result(contract_id: str, error: str) -> ValidationResult:
    return ValidationResult(
        check_id=f"{contract_id}.contract.load",
        column_name=None,
        check_type="contract_load",
        status=ValidationStatus.ERROR,
        actual_value=None,
        expected={"contract_id": contract_id},
        message=error,
    )


def run_validation(contract_ids: list[str] | None = None, baseline_refresh: bool = False, sample_limit: int = 5) -> dict[str, Any]:
    context = build_contract_load_context(REPO_ROOT)
    contract_paths = sorted(context.contracts_dir.glob("*.yaml"))
    requested = set(contract_ids or [])
    summary = {
        "processed_contracts": 0,
        "generated_reports": 0,
        "failed_contracts": 0,
        "errored_checks": 0,
        "failed_checks": 0,
        "warned_checks": 0,
        "passed_checks": 0,
        "report_paths": [],
        "snapshot_ids": [],
        "contract_ids": [],
        "contract_errors": [],
    }

    for contract_path in contract_paths:
        try:
            loaded_contract = load_contract(contract_path, context, baseline_refresh_allowed=baseline_refresh)
        except Exception as exc:  # pragma: no cover - defensive runner guard
            contract_id = contract_path.stem
            if requested and contract_id not in requested and str(contract_path) not in requested:
                continue
            summary["processed_contracts"] += 1
            summary["contract_ids"].append(contract_id)
            summary["failed_contracts"] += 1
            error_message = f"Contract load failed for {contract_path.as_posix()}: {exc}"
            summary["contract_errors"].append({"contract_id": contract_id, "error": error_message})
            report = summarize_results(
                report_id=new_report_id(),
                contract_id=contract_id,
                snapshot_id="unknown",
                run_timestamp=new_timestamp(),
                results=[_contract_load_error_result(contract_id, error_message)],
            )
            report_path = write_report(report, REPO_ROOT / "validation_reports")
            summary["generated_reports"] += 1
            summary["report_paths"].append(report_path.as_posix())
            summary["errored_checks"] += report.errored
            continue

        if requested and loaded_contract.contract_id not in requested and str(contract_path) not in requested and contract_path.stem not in requested:
            continue

        summary["processed_contracts"] += 1
        summary["contract_ids"].append(loaded_contract.contract_id)
        dataset = load_dataset(loaded_contract.dataset_id, loaded_contract.snapshot_path)
        snapshot_id = _snapshot_id(loaded_contract.snapshot_path)
        summary["snapshot_ids"].append(snapshot_id)

        if dataset.errors:
            results = [
                ValidationResult(
                    check_id=check.check_id,
                    column_name=check.column_name,
                    check_type=check.check_type,
                    status=ValidationStatus.ERROR,
                    actual_value=None,
                    expected=check.expected,
                    severity=check.severity,
                    records_failing=0,
                    sample_failing=[],
                    message=f"Dataset load failed: {'; '.join(dataset.errors)}",
                )
                for check in loaded_contract.checks
            ] or [
                ValidationResult(
                    check_id=f"{loaded_contract.contract_id}.dataset.load",
                    column_name=None,
                    check_type="dataset_load",
                    status=ValidationStatus.ERROR,
                    actual_value=None,
                    expected={"snapshot_path": loaded_contract.snapshot_path},
                    message=f"Dataset load failed: {'; '.join(dataset.errors)}",
                )
            ]
        else:
            engine_context = ExecutionContext(repo_root=REPO_ROOT, baseline_refresh_allowed=baseline_refresh, sample_limit=sample_limit)
            results, numeric_profiles, _ = execute_contract_checks(loaded_contract, dataset, engine_context)
            if numeric_profiles:
                baseline_store = BaselineStore(REPO_ROOT)
                baseline_store.update_from_profiles(loaded_contract.contract_id, numeric_profiles, refresh_allowed=baseline_refresh)

        run_timestamp = new_timestamp()
        report = summarize_results(
            report_id=new_report_id(),
            contract_id=loaded_contract.contract_id,
            snapshot_id=snapshot_id,
            run_timestamp=run_timestamp,
            results=results,
        )
        validate_report_model(report)
        report_path = write_report(report, REPO_ROOT / "validation_reports")

        summary["generated_reports"] += 1
        summary["report_paths"].append(report_path.as_posix())
        summary["passed_checks"] += report.passed
        summary["failed_checks"] += report.failed
        summary["warned_checks"] += report.warned
        summary["errored_checks"] += report.errored
        if report.failed or report.errored:
            summary["failed_contracts"] += 1

    validation_run = ValidationRun(
        run_id=str(uuid4()),
        run_timestamp=new_timestamp(),
        contract_ids=summary["contract_ids"],
        snapshot_ids=summary["snapshot_ids"],
        status="completed_with_errors" if summary["failed_contracts"] else "completed",
    )
    summary["validation_run"] = validation_run.model_dump(mode="json")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Validation execution engine")
    parser.add_argument("--contracts", nargs="*", help="Specific contract ids or file stems to execute")
    parser.add_argument("--baseline-refresh", action="store_true", help="Allow baseline overwrite during this run")
    parser.add_argument("--sample-limit", type=int, default=5, help="Maximum failing samples to capture per check")
    args = parser.parse_args()

    result = run_validation(contract_ids=args.contracts, baseline_refresh=args.baseline_refresh, sample_limit=args.sample_limit)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
