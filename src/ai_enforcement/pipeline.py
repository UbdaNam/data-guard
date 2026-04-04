"""Orchestrated AI enforcement pipeline."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.ai_enforcement.contract_loader import build_context
from src.ai_enforcement.drift import compare_or_create_baseline, select_surface_samples
from src.ai_enforcement.metrics import assemble_metrics_report
from src.ai_enforcement.output_validator import validate_output_records
from src.ai_enforcement.prompt_validator import validate_prompt_records
from src.ai_enforcement.quarantine_writer import write_quarantine_records
from src.ai_enforcement.renderer import ensure_output_roots, make_violation_id, new_run_id, new_run_timestamp, read_json, write_json_atomic
from src.ai_enforcement.trace_validator import validate_trace_records
from src.ai_enforcement.violation_writer import append_violations
from src.models.ai_enforcement_models import AIEnforcementRun, AIViolationCategory, AIViolationRecord, AIViolationSeverity, DriftComparisonStatus


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        text = raw.strip()
        if not text:
            continue
        try:
            data = json.loads(text)
            if isinstance(data, dict):
                rows.append(data)
        except Exception:
            continue
    return rows


def run_ai_enforcement(
    *,
    repo_root: Path,
    week2_path: str,
    week3_path: str,
    trace_path: str,
    snapshot_root: str,
    validation_report_path: str,
    violation_log_path: str,
    quarantine_dir: str,
    surface_id: str,
) -> dict[str, Any]:
    roots = ensure_output_roots(repo_root)
    run_id = new_run_id()
    run_timestamp = new_run_timestamp()

    governed = build_context(repo_root)

    week2_records = _load_jsonl(repo_root / week2_path)
    week3_records = _load_jsonl(repo_root / week3_path)
    trace_records = _load_jsonl(repo_root / trace_path)

    prompt_results, invalid_prompt_payloads = validate_prompt_records(week3_records, governed.get("prompt_schema", {}), surface_id)
    try:
        quarantine_path = write_quarantine_records(
            quarantine_dir=repo_root / quarantine_dir,
            run_id=run_id,
            run_timestamp=run_timestamp,
            prompt_results=prompt_results,
            source_records=invalid_prompt_payloads,
            source_dataset=week3_path,
        )
    except Exception as exc:
        if any(item.quarantined for item in prompt_results):
            return {
                "run_id": run_id,
                "run_timestamp": run_timestamp,
                "status": "failed",
                "error": f"Quarantine write failed: {exc}",
            }
        quarantine_path = None

    for result in prompt_results:
        if result.quarantined:
            result.quarantine_path = quarantine_path

    output_results = validate_output_records(week2_records, governed.get("output_schema", {}))
    trace_results = validate_trace_records(trace_records)

    drift_samples = select_surface_samples(week3_records, surface_id)
    drift_result, drift_artifacts = compare_or_create_baseline(
        snapshot_root=repo_root / snapshot_root,
        surface_id=surface_id,
        samples=drift_samples,
        run_id=run_id,
        run_timestamp=run_timestamp,
    )

    violations: list[AIViolationRecord] = []
    for result in prompt_results:
        if result.quarantined:
            violations.append(
                AIViolationRecord(
                    violation_id=make_violation_id(run_id, AIViolationCategory.prompt_input.value, surface_id, result.record_id),
                    run_id=run_id,
                    category=AIViolationCategory.prompt_input,
                    severity=AIViolationSeverity.high,
                    surface_id=surface_id,
                    record_ref=result.record_id,
                    message="Prompt input failed schema validation",
                    evidence={"reasons": result.failure_reasons, "schema_version": result.schema_version},
                )
            )

    for result in output_results:
        if result.validation_status.value != "PASS":
            violations.append(
                AIViolationRecord(
                    violation_id=make_violation_id(run_id, AIViolationCategory.structured_output.value, "week2_verdicts", result.record_id),
                    run_id=run_id,
                    category=AIViolationCategory.structured_output,
                    severity=AIViolationSeverity.medium,
                    surface_id="week2_verdicts",
                    record_ref=result.record_id,
                    message="Structured output failed schema validation",
                    evidence=result.model_dump(mode="json"),
                )
            )

    for result in trace_results:
        if result.validation_status.value != "PASS":
            violations.append(
                AIViolationRecord(
                    violation_id=make_violation_id(run_id, AIViolationCategory.trace_contract.value, "trace_runs", result.trace_run_id),
                    run_id=run_id,
                    category=AIViolationCategory.trace_contract,
                    severity=AIViolationSeverity.medium,
                    surface_id="trace_runs",
                    record_ref=result.trace_run_id,
                    message="Trace contract violation",
                    evidence=result.model_dump(mode="json"),
                )
            )

    if drift_result.comparison_status in {DriftComparisonStatus.baseline_unreadable, DriftComparisonStatus.compared} and drift_result.drift_detected:
        violations.append(
            AIViolationRecord(
                violation_id=make_violation_id(run_id, AIViolationCategory.embedding_drift.value, surface_id, run_id),
                run_id=run_id,
                category=AIViolationCategory.embedding_drift,
                severity=AIViolationSeverity.high,
                surface_id=surface_id,
                record_ref=run_id,
                message="Embedding drift detected",
                evidence=drift_result.model_dump(mode="json"),
            )
        )

    appended = append_violations(repo_root / violation_log_path, violations)

    previous_metrics = read_json(repo_root / validation_report_path)
    output_failed = sum(1 for item in output_results if item.validation_status.value != "PASS")
    trace_failed = sum(1 for item in trace_results if item.validation_status.value != "PASS")
    prompt_quarantined = sum(1 for item in prompt_results if item.quarantined)

    metrics = assemble_metrics_report(
        run_id=run_id,
        run_timestamp=run_timestamp,
        prompt_processed=len(prompt_results),
        prompt_quarantined=prompt_quarantined,
        output_processed=len(output_results),
        output_failed=output_failed,
        trace_processed=len(trace_results),
        trace_failed=trace_failed,
        drift_checks_requested=1,
        drift_checks_compared=1 if drift_result.comparison_status == DriftComparisonStatus.compared else 0,
        drift_checks_insufficient=1 if drift_result.comparison_status == DriftComparisonStatus.insufficient_data else 0,
        drift_detected_count=1 if drift_result.drift_detected else 0,
        context_completeness=governed.get("context_completeness", {}),
        artifacts={
            "quarantine_path": quarantine_path,
            "violation_log_path": (repo_root / violation_log_path).as_posix(),
            "drift_artifact_paths": drift_artifacts,
            "violation_records_appended": appended,
        },
        previous_metrics=previous_metrics,
    )

    metrics_payload = metrics.model_dump(mode="json")
    write_json_atomic(repo_root / validation_report_path, metrics_payload, validate_metrics=True)

    run = AIEnforcementRun(
        run_id=run_id,
        run_timestamp=run_timestamp,
        inputs={
            "week2_path": week2_path,
            "week3_path": week3_path,
            "trace_path": trace_path,
        },
        context_completeness=governed.get("context_completeness", {}),
        status="completed_with_warnings" if not governed.get("context_completeness", {}).get("feature5_context_loaded", False) else "completed",
    )

    return {
        "run": run.model_dump(mode="json"),
        "summary": {
            "prompt_processed": len(prompt_results),
            "prompt_quarantined": prompt_quarantined,
            "outputs_processed": len(output_results),
            "outputs_failed": output_failed,
            "traces_processed": len(trace_results),
            "traces_failed": trace_failed,
            "drift_status": drift_result.comparison_status.value,
            "violation_records_appended": appended,
        },
        "artifacts": metrics_payload.get("artifacts", {}),
    }
