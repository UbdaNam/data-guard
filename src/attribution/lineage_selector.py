"""Select the latest valid lineage snapshot for Feature 4."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from src.models.attribution_models import LineageSnapshotRecord

REPO_ROOT = Path(__file__).resolve().parents[2]
LINEAGE_PATH = REPO_ROOT / "outputs" / "week4" / "lineage_snapshots.jsonl"


def _parse_timestamp(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def load_lineage_snapshots(path: Path = LINEAGE_PATH) -> tuple[list[LineageSnapshotRecord], list[str]]:
    snapshots: list[LineageSnapshotRecord] = []
    warnings: list[str] = []
    if not path.exists():
        return snapshots, [f"Missing lineage snapshot file: {path.as_posix()}"]
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except Exception as exc:  # pragma: no cover - defensive parser guard
            warnings.append(f"Invalid JSON at line {line_number}: {exc}")
            continue
        snapshots.append(
            LineageSnapshotRecord(
                source_path=path.as_posix(),
                line_number=line_number,
                payload=payload,
                snapshot_timestamp=payload.get("snapshot_timestamp"),
                captured_at=payload.get("captured_at"),
                run_timestamp=payload.get("run_timestamp"),
                dataset_id=payload.get("dataset_id"),
                consumed_fields=list(payload.get("consumed_fields", []) or []),
            )
        )
    return snapshots, warnings


def select_latest_snapshot(path: Path = LINEAGE_PATH) -> tuple[LineageSnapshotRecord | None, list[str]]:
    snapshots, warnings = load_lineage_snapshots(path)
    if not snapshots:
        return None, warnings

    def sort_key(snapshot: LineageSnapshotRecord) -> tuple[int, datetime, int]:
        timestamp = _parse_timestamp(snapshot.snapshot_timestamp) or _parse_timestamp(snapshot.captured_at) or _parse_timestamp(snapshot.run_timestamp) or datetime.min.replace(tzinfo=UTC)
        return (1 if timestamp != datetime.min.replace(tzinfo=UTC) else 0, timestamp, snapshot.line_number)

    return sorted(snapshots, key=sort_key)[-1], warnings
