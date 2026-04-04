"""Append-safe violation record writer."""

from __future__ import annotations

import json
from pathlib import Path

from src.models.attribution_models import ViolationRecord

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = REPO_ROOT / "violation_log" / "violations.jsonl"


def ensure_output_path(output_path: Path = DEFAULT_OUTPUT) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not output_path.exists():
        output_path.touch()
    return output_path


def load_existing_violation_ids(output_path: Path = DEFAULT_OUTPUT) -> set[str]:
    if not output_path.exists():
        return set()
    ids: set[str] = set()
    for line in output_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except Exception:
            continue
        violation_id = payload.get("violation_id")
        if violation_id:
            ids.add(str(violation_id))
    return ids


def write_violation_records(records: list[ViolationRecord], output_path: Path = DEFAULT_OUTPUT, overwrite: bool = False) -> dict[str, object]:
    output_path = ensure_output_path(output_path)
    ordered = sorted(
        records,
        key=lambda record: (
            record.detected_at,
            record.contract_id,
            record.check_id,
            record.violation_id,
        ),
    )
    existing_ids = set() if overwrite else load_existing_violation_ids(output_path)
    written = 0
    duplicates = 0
    with output_path.open("a", encoding="utf-8") as handle:
        for record in ordered:
            if record.violation_id in existing_ids:
                duplicates += 1
                continue
            handle.write(json.dumps(record.model_dump(mode="json", exclude_none=True), sort_keys=True) + "\n")
            existing_ids.add(record.violation_id)
            written += 1
    return {"output_path": output_path.as_posix(), "written": written, "duplicates": duplicates}
