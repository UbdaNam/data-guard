"""Deterministic JSON rendering for operational reports."""

from __future__ import annotations

import json
from pathlib import Path

from src.reporting.models import OperationalReportData


def _ordered_report_payload(report: OperationalReportData) -> dict:
    payload = report.model_dump(mode="json")
    return {
        "report_id": payload["report_id"],
        "report_date": payload["report_date"],
        "reporting_window": payload["reporting_window"],
        "data_health_score": payload["data_health_score"],
        "section_completeness": payload["section_completeness"],
        "violations_summary": payload["violations_summary"],
        "top_violations": payload["top_violations"],
        "schema_changes_summary": payload["schema_changes_summary"],
        "ai_risk_summary": payload["ai_risk_summary"],
        "recommended_actions": payload["recommended_actions"],
        "evidence_index": payload["evidence_index"],
        "generation_metadata": payload["generation_metadata"],
    }


def write_report_json(report: OperationalReportData, destination: Path) -> dict:
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = _ordered_report_payload(report)
    temp = destination.with_suffix(destination.suffix + ".tmp")
    temp.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    temp.replace(destination)
    return payload
