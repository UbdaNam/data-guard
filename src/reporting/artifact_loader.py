"""Load and normalize upstream evidence artifacts for report generation."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml


@dataclass(slots=True)
class LoadedArtifacts:
    validation_reports: list[dict[str, Any]] = field(default_factory=list)
    violations: list[dict[str, Any]] = field(default_factory=list)
    schema_evolution_reports: list[dict[str, Any]] = field(default_factory=list)
    ai_metrics: dict[str, Any] | None = None
    ownership_map: list[dict[str, Any]] = field(default_factory=list)
    interface_registry: list[dict[str, Any]] = field(default_factory=list)
    missing_sources: dict[str, list[str]] = field(default_factory=dict)
    counts: dict[str, int] = field(default_factory=dict)


def _to_iso_utc(value: str) -> str | None:
    text = value.strip()
    if not text:
        return None
    text = text.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(text).astimezone(UTC).isoformat()
    except ValueError:
        pass
    # handle timestamp in filenames like 2026-04-01T22-33-26-689378_00-00
    try:
        fixed = text.replace("_", "+", 1)
        parts = fixed.split("T")
        if len(parts) == 2:
            time_part = parts[1]
            time_fields = time_part.split("+")[0].split("-")
            if len(time_fields) >= 3:
                hh, mm, ss = time_fields[0], time_fields[1], time_fields[2]
                rebuilt = f"{parts[0]}T{hh}:{mm}:{ss}+00:00"
                return datetime.fromisoformat(rebuilt).astimezone(UTC).isoformat()
    except Exception:
        return None
    return None


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        text = raw.strip()
        if not text:
            continue
        try:
            obj = json.loads(text)
            if isinstance(obj, dict):
                rows.append(obj)
        except Exception:
            continue
    return rows


def _read_yaml_list(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    try:
        parsed = yaml.safe_load(path.read_text(encoding="utf-8"))
        if isinstance(parsed, list):
            return [item for item in parsed if isinstance(item, dict)]
    except Exception:
        return []
    return []


def _augment_timestamps_from_filename(item: dict[str, Any], path: Path) -> None:
    if any(k in item for k in ("detected_at", "run_timestamp", "generated_at", "report_date")):
        return
    parts = path.stem.split("_")
    for token in parts:
        iso = _to_iso_utc(token)
        if iso:
            item["detected_at"] = iso
            return


def load_artifacts(
    *,
    repo_root: Path,
    validation_reports_glob: str,
    violation_log_path: str,
    schema_evolution_glob: str,
    ai_metrics_path: str,
    ownership_map_path: str,
    interface_registry_path: str,
) -> LoadedArtifacts:
    loaded = LoadedArtifacts()

    validation_missing: list[str] = []
    for path in sorted((repo_root).glob(validation_reports_glob)):
        if path.name == "ai_metrics.json":
            continue
        if path.name.startswith("schema_evolution"):
            continue
        payload = _read_json(path)
        if isinstance(payload, dict):
            payload["_artifact_path"] = path.as_posix()
            _augment_timestamps_from_filename(payload, path)
            loaded.validation_reports.append(payload)
    if not loaded.validation_reports:
        validation_missing.append((repo_root / validation_reports_glob.replace("*", "<pattern>")).as_posix())

    violations_path = repo_root / violation_log_path
    loaded.violations = _read_jsonl(violations_path)
    for row in loaded.violations:
        row.setdefault("_artifact_path", violations_path.as_posix())
    if not loaded.violations:
        loaded.missing_sources["violations"] = [violations_path.as_posix()]

    schema_missing: list[str] = []
    for path in sorted(repo_root.glob(schema_evolution_glob)):
        if path.name == "schema_evolution_run_summary.json":
            continue
        payload = _read_json(path)
        if isinstance(payload, dict):
            payload["_artifact_path"] = path.as_posix()
            _augment_timestamps_from_filename(payload, path)
            loaded.schema_evolution_reports.append(payload)
    if not loaded.schema_evolution_reports:
        schema_missing.append((repo_root / schema_evolution_glob.replace("*", "<pattern>")).as_posix())

    ai_metrics_file = repo_root / ai_metrics_path
    loaded.ai_metrics = _read_json(ai_metrics_file)
    if isinstance(loaded.ai_metrics, dict):
        loaded.ai_metrics["_artifact_path"] = ai_metrics_file.as_posix()
    else:
        loaded.missing_sources["ai_risk"] = [ai_metrics_file.as_posix()]

    ownership_file = repo_root / ownership_map_path
    interface_file = repo_root / interface_registry_path
    loaded.ownership_map = _read_yaml_list(ownership_file)
    loaded.interface_registry = _read_yaml_list(interface_file)
    if not loaded.ownership_map:
        loaded.missing_sources.setdefault("ownership", []).append(ownership_file.as_posix())
    if not loaded.interface_registry:
        loaded.missing_sources.setdefault("ownership", []).append(interface_file.as_posix())

    if validation_missing:
        loaded.missing_sources["data_health_score"] = validation_missing
    if schema_missing:
        loaded.missing_sources["schema_changes"] = schema_missing

    loaded.counts = {
        "validation_reports": len(loaded.validation_reports),
        "violations": len(loaded.violations),
        "schema_evolution_reports": len(loaded.schema_evolution_reports),
        "ownership_map_records": len(loaded.ownership_map),
        "interface_registry_records": len(loaded.interface_registry),
        "ai_metrics": 1 if loaded.ai_metrics else 0,
    }
    return loaded
