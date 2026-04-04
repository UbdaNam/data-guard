"""Quarantine writer for invalid prompt records."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.models.ai_enforcement_models import PromptInputCheckRecord, QuarantineRecord
from src.validators.ai_enforcement_validator import validate_quarantine_payload


def write_quarantine_records(
    *,
    quarantine_dir: Path,
    run_id: str,
    run_timestamp: str,
    prompt_results: list[PromptInputCheckRecord],
    source_records: list[dict[str, Any]],
    source_dataset: str,
) -> str | None:
    invalid_pairs: list[tuple[PromptInputCheckRecord, dict[str, Any]]] = []
    invalid_iter = iter(source_records)
    for result in prompt_results:
        if result.quarantined:
            invalid_pairs.append((result, next(invalid_iter, {})))

    if not invalid_pairs:
        return None

    quarantine_dir.mkdir(parents=True, exist_ok=True)
    output_path = quarantine_dir / f"{run_timestamp}_{run_id}.jsonl"
    temp_path = output_path.with_suffix(".jsonl.tmp")

    ordered = sorted(invalid_pairs, key=lambda item: item[0].record_id)
    lines: list[str] = []
    for result, payload in ordered:
        record = QuarantineRecord(
            run_id=run_id,
            run_timestamp=run_timestamp,
            record_id=result.record_id,
            source_dataset=source_dataset,
            schema_version=result.schema_version,
            failure_reasons=result.failure_reasons,
            original_payload=payload,
        )
        validate_quarantine_payload(record.model_dump(mode="json"), strict=True)
        lines.append(json.dumps(record.model_dump(mode="json"), sort_keys=True))

    temp_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    temp_path.replace(output_path)

    return output_path.as_posix()
