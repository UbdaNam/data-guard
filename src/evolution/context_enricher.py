"""Optional Feature 3/4 context enrichment for schema evolution outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _load_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def load_optional_context(repo_root: Path, contract_id: str) -> tuple[dict[str, Any], list[str]]:
    warnings: list[str] = []
    enrichment: dict[str, Any] = {
        "validation": {},
        "violations": {},
        "evidence_used": [],
    }

    validation_dir = repo_root / "validation_reports"
    related_reports = sorted(validation_dir.glob(f"{contract_id}_*.json"))
    if related_reports:
        latest = related_reports[-1]
        payload = _load_json(latest)
        if payload is None:
            warnings.append(f"Malformed validation context: {latest.as_posix()}")
        else:
            enrichment["validation"] = {
                "path": latest.as_posix(),
                "failed": payload.get("failed", 0),
                "errored": payload.get("errored", 0),
                "total_checks": payload.get("total_checks", 0),
            }
            enrichment["evidence_used"].append("feature3_validation")
    else:
        warnings.append("Missing optional Feature 3 validation context")

    violations_file = repo_root / "violation_log" / "violations.jsonl"
    if violations_file.exists():
        violation_count = 0
        try:
            for line in violations_file.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                payload = json.loads(line)
                if payload.get("contract_id") == contract_id:
                    violation_count += 1
            enrichment["violations"] = {
                "path": violations_file.as_posix(),
                "count": violation_count,
            }
            enrichment["evidence_used"].append("feature4_violations")
        except Exception as exc:
            warnings.append(f"Malformed violation context: {exc}")
    else:
        warnings.append("Missing optional Feature 4 violation context")

    return enrichment, warnings


def context_completeness_from_warnings(warnings: list[str]) -> str:
    optional_missing = [item for item in warnings if item.startswith("Missing optional")]
    malformed = [item for item in warnings if item.startswith("Malformed")]
    if warnings and len(optional_missing) == len(warnings):
        return "minimal"
    if warnings and (malformed or optional_missing):
        return "partial"
    return "complete"


def apply_enrichment(
    baseline_urgency: str,
    enrichment: dict[str, Any],
) -> tuple[str, float]:
    urgency_order = ["low", "medium", "high", "critical"]
    base_index = urgency_order.index(baseline_urgency) if baseline_urgency in urgency_order else 1

    validation = enrichment.get("validation") or {}
    violations = enrichment.get("violations") or {}
    penalty = 0
    if int(validation.get("failed", 0) or 0) > 0 or int(validation.get("errored", 0) or 0) > 0:
        penalty += 1
    if int(violations.get("count", 0) or 0) >= 3:
        penalty += 1

    adjusted_index = min(len(urgency_order) - 1, base_index + penalty)
    confidence = 0.55 + (0.15 * penalty) + (0.1 if enrichment.get("evidence_used") else 0.0)
    return urgency_order[adjusted_index], min(confidence, 0.98)
