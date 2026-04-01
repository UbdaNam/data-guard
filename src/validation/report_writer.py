"""Fixed-schema validation report writer."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from src.models.validation_models import ValidationReport
from src.validators.validation_report_validator import validate_report_payload


def build_report_filename(contract_id: str, run_timestamp: str) -> str:
    safe_contract_id = contract_id.replace("/", "_").replace(":", "_")
    safe_timestamp = (
        run_timestamp.replace(":", "-")
        .replace("+", "_")
        .replace(".", "-")
        .replace("T", "T")
    )
    return f"{safe_contract_id}_{safe_timestamp}.json"


def write_report(report: ValidationReport, output_dir: Path, strict: bool = True) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = report.model_dump(mode="json")
    validate_report_payload(payload, strict=strict)
    report_path = output_dir / build_report_filename(report.contract_id, report.run_timestamp)
    temp_path = report_path.with_suffix(".json.tmp")
    temp_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    temp_path.replace(report_path)
    return report_path


def new_report_id() -> str:
    return str(uuid4())


def new_timestamp() -> str:
    return datetime.now(UTC).isoformat()
