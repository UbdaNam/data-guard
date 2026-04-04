"""Deterministic filesystem and JSON rendering helpers for AI enforcement."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from src.validators.ai_enforcement_validator import validate_ai_metrics_payload


def ensure_output_roots(repo_root: Path) -> dict[str, Path]:
    roots = {
        "validation_reports": repo_root / "validation_reports",
        "violation_log": repo_root / "violation_log",
        "quarantine": repo_root / "outputs" / "quarantine",
        "schema_snapshots_ai": repo_root / "schema_snapshots" / "ai",
    }
    for path in roots.values():
        path.mkdir(parents=True, exist_ok=True)
    return roots


def new_run_timestamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")


def new_run_id() -> str:
    return uuid4().hex


def make_violation_id(run_id: str, category: str, surface_id: str, record_ref: str) -> str:
    raw = f"{run_id}|{category}|{surface_id}|{record_ref}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def sort_key_for_record(record: dict[str, object]) -> tuple[str, str, str]:
    return (
        str(record.get("category", "")),
        str(record.get("surface_id", "")),
        str(record.get("record_ref", "")),
    )


def write_json_atomic(path: Path, payload: dict, validate_metrics: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if validate_metrics:
        validate_ai_metrics_payload(payload, strict=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    temp.replace(path)


def read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))
