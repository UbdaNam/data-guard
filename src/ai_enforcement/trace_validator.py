"""LangSmith trace contract validation helpers."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from src.models.ai_enforcement_models import AIValidationStatus, TraceContractCheckRecord


def _is_iso_timestamp(value: str) -> bool:
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except Exception:
        return False


def validate_trace_records(records: list[dict[str, Any]], contract_id: str = "langsmith_trace_contract") -> list[TraceContractCheckRecord]:
    results: list[TraceContractCheckRecord] = []

    for index, record in enumerate(records):
        run_id = str(record.get("run_id") or record.get("trace_id") or "")
        timestamp = str(record.get("timestamp") or record.get("event_timestamp") or "")
        failures: list[str] = []

        if not run_id:
            failures.append("missing_run_id")
            run_id = f"line_{index + 1}"
        if not timestamp:
            failures.append("missing_timestamp")
        elif not _is_iso_timestamp(timestamp):
            failures.append("malformed_timestamp")

        results.append(
            TraceContractCheckRecord(
                trace_run_id=run_id,
                event_timestamp=timestamp,
                contract_id=contract_id,
                validation_status=AIValidationStatus.FAIL if failures else AIValidationStatus.PASS,
                failure_reasons=failures,
            )
        )

    return results
