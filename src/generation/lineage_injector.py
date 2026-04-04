"""Lineage-aware downstream context injection."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.models.contract_models import ContextCoverageStatus, DownstreamContextAnnotation


def _timestamp_key(row: dict[str, Any]) -> str:
    return str(
        row.get("snapshot_timestamp")
        or row.get("captured_at")
        or row.get("run_timestamp")
        or row.get("generated_at")
        or ""
    )


def _read_optional_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict):
            rows.append(obj)
    return rows


def inject_downstream_context(
    dataset_id: str,
    interface_registry: list[dict[str, Any]],
    ownership_map: list[dict[str, Any]],
    repo_root: Path,
) -> DownstreamContextAnnotation:
    related_interfaces = [i for i in interface_registry if dataset_id in (i.get("dataset_refs") or [])]
    related_owners = [o for o in ownership_map if o.get("schema_name") in {s for i in related_interfaces for s in (i.get("schema_refs") or [])}]
    lineage_rows = _read_optional_jsonl(repo_root / "outputs/week4/lineage_snapshots.jsonl")

    matching_rows = [row for row in lineage_rows if row.get("dataset_id") == dataset_id]
    latest_timestamp = None
    if matching_rows:
        latest_row = max(matching_rows, key=_timestamp_key)
        latest_timestamp = _timestamp_key(latest_row) or None
        if latest_timestamp:
            matching_rows = [row for row in matching_rows if _timestamp_key(row) == latest_timestamp]

    downstream_systems = sorted({str(i.get("target_system")) for i in related_interfaces if i.get("target_system")})
    consumed_fields = sorted(
        {
            str(field)
            for row in matching_rows
            for field in (row.get("consumed_fields") or row.get("consumed_columns") or [])
        }
    )

    likely_breaking_fields = consumed_fields[:]
    consumer_change_sensitivity = [
        {
            "consumer_owner": owner,
            "sensitivity": "high" if likely_breaking_fields else "medium",
        }
        for o in related_owners
        for owner in (o.get("consumer_owners") or [])
    ]

    if downstream_systems and consumed_fields:
        status = ContextCoverageStatus.full
    elif downstream_systems:
        status = ContextCoverageStatus.partial
    else:
        status = ContextCoverageStatus.unknown

    return DownstreamContextAnnotation(
        downstream_systems=downstream_systems,
        consumed_fields=consumed_fields,
        likely_breaking_fields=likely_breaking_fields,
        consumer_change_sensitivity=consumer_change_sensitivity,
        coverage_status=status,
        context_sources=[
            "contracts/interface_registry.yaml",
            "contracts/schema_ownership_map.yaml",
            "outputs/week4/lineage_snapshots.jsonl",
        ],
        latest_snapshot_timestamp=latest_timestamp,
    )
