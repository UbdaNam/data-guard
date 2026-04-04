"""AI-specific violation writer."""

from __future__ import annotations

import json
from pathlib import Path

from src.ai_enforcement.renderer import sort_key_for_record
from src.models.ai_enforcement_models import AIViolationRecord
from src.validators.ai_enforcement_validator import validate_ai_violation_payload


def append_violations(path: Path, violations: list[AIViolationRecord]) -> int:
    if not violations:
        return 0
    path.parent.mkdir(parents=True, exist_ok=True)

    ordered = sorted([item.model_dump(mode="json") for item in violations], key=sort_key_for_record)
    for payload in ordered:
        validate_ai_violation_payload(payload, strict=True)

    with path.open("a", encoding="utf-8") as handle:
        for payload in ordered:
            handle.write(json.dumps(payload, sort_keys=True) + "\n")

    return len(ordered)
