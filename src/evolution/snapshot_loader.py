"""Snapshot loading and pair selection logic."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.models.schema_evolution_models import SchemaSnapshot


class SnapshotSelectionError(ValueError):
    """Raised when snapshot pair selection fails."""


def load_contract_snapshots(snapshot_root: Path, contract_id: str) -> tuple[list[SchemaSnapshot], list[str]]:
    contract_dir = snapshot_root / contract_id
    if not contract_dir.exists():
        return [], [f"No snapshot directory found for contract_id={contract_id}"]

    warnings: list[str] = []
    snapshots: list[SchemaSnapshot] = []
    for path in sorted(contract_dir.glob("snapshot_*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            snapshots.append(SchemaSnapshot.model_validate(payload))
        except Exception as exc:
            warnings.append(f"Malformed snapshot skipped: {path.as_posix()} ({exc})")

    snapshots.sort(key=lambda item: (item.snapshot_timestamp, item.snapshot_id))
    return snapshots, warnings


def pick_snapshot_pair(
    snapshots: list[SchemaSnapshot],
    from_snapshot_id: str | None = None,
    to_snapshot_id: str | None = None,
) -> tuple[SchemaSnapshot | None, SchemaSnapshot]:
    if not snapshots:
        raise SnapshotSelectionError("No valid snapshots available")

    index_by_id = {item.snapshot_id: item for item in snapshots}

    if to_snapshot_id:
        to_snapshot = index_by_id.get(to_snapshot_id)
        if to_snapshot is None:
            raise SnapshotSelectionError(f"Unknown to_snapshot_id: {to_snapshot_id}")
    else:
        to_snapshot = snapshots[-1]

    if from_snapshot_id:
        from_snapshot = index_by_id.get(from_snapshot_id)
        if from_snapshot is None:
            raise SnapshotSelectionError(f"Unknown from_snapshot_id: {from_snapshot_id}")
    else:
        candidates = [item for item in snapshots if item.snapshot_timestamp < to_snapshot.snapshot_timestamp or item.snapshot_id != to_snapshot.snapshot_id]
        from_snapshot = candidates[-1] if candidates else None

    if from_snapshot and from_snapshot.contract_id != to_snapshot.contract_id:
        raise SnapshotSelectionError("Snapshot pair must belong to same contract")

    return from_snapshot, to_snapshot


def load_pair(
    snapshot_root: Path,
    contract_id: str,
    from_snapshot_id: str | None = None,
    to_snapshot_id: str | None = None,
) -> tuple[SchemaSnapshot | None, SchemaSnapshot | None, list[str]]:
    snapshots, warnings = load_contract_snapshots(snapshot_root, contract_id)
    if not snapshots:
        return None, None, warnings

    try:
        from_snapshot, to_snapshot = pick_snapshot_pair(snapshots, from_snapshot_id=from_snapshot_id, to_snapshot_id=to_snapshot_id)
        return from_snapshot, to_snapshot, warnings
    except SnapshotSelectionError as exc:
        warnings.append(str(exc))
        return None, None, warnings
