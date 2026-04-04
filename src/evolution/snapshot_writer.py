"""Snapshot creation and persistence for schema evolution."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from src.evolution.normalizer import normalize_contract
from src.models.schema_evolution_models import SchemaSnapshot


def _utc_timestamp() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _compact_timestamp(iso_timestamp: str) -> str:
    return iso_timestamp.replace("-", "").replace(":", "").replace("T", "_").replace("Z", "")


def compute_schema_hash(normalized_payload: dict[str, Any]) -> str:
    blob = json.dumps(normalized_payload, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


def build_snapshot(contract_payload: dict[str, Any], source_contract_path: Path) -> SchemaSnapshot:
    normalized = normalize_contract(contract_payload)
    schema_hash = compute_schema_hash(normalized)
    return SchemaSnapshot(
        snapshot_id=schema_hash,
        snapshot_timestamp=_utc_timestamp(),
        contract_id=str(normalized.get("contract_id") or source_contract_path.stem),
        schema_version=str(normalized.get("schema_version") or "1.0"),
        schema_hash=schema_hash,
        source_contract_path=source_contract_path.as_posix(),
        fields=[item for item in normalized.get("fields", [])],
        rules=[item for item in normalized.get("rules", [])],
        metadata={
            "dataset_id": normalized.get("dataset_id"),
            "schema_name": normalized.get("schema_name"),
            "normalization_version": "feature5.v1",
        },
    )


def _latest_snapshot_path(contract_dir: Path) -> Path | None:
    candidates = sorted(contract_dir.glob("snapshot_*.json"))
    if not candidates:
        return None
    return candidates[-1]


def write_snapshot(snapshot: SchemaSnapshot, snapshot_root: Path) -> dict[str, Any]:
    contract_dir = snapshot_root / snapshot.contract_id
    contract_dir.mkdir(parents=True, exist_ok=True)

    latest = _latest_snapshot_path(contract_dir)
    if latest is not None:
        try:
            latest_payload = json.loads(latest.read_text(encoding="utf-8"))
            latest_hash = latest_payload.get("schema_hash")
            if latest_hash == snapshot.schema_hash:
                return {
                    "written": False,
                    "no_material_change": True,
                    "snapshot_id": snapshot.snapshot_id,
                    "snapshot_path": latest.as_posix(),
                }
        except Exception:
            # Continue to write a new snapshot if latest is malformed.
            pass

    file_name = f"snapshot_{_compact_timestamp(snapshot.snapshot_timestamp)}_{snapshot.schema_hash}.json"
    target = contract_dir / file_name
    target.write_text(json.dumps(snapshot.model_dump(mode="json"), indent=2, sort_keys=True), encoding="utf-8")
    return {
        "written": True,
        "no_material_change": False,
        "snapshot_id": snapshot.snapshot_id,
        "snapshot_path": target.as_posix(),
    }
