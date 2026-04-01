"""Deterministic serialization and atomic writing utilities."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

DEFAULT_ALLOWED_NDETERMINISTIC_FIELDS = {"generated_at", "run_id", "generator_version", "contract_schema_version"}


def _normalize(value: Any, allowed_nondeterministic_fields: set[str]) -> Any:
    if isinstance(value, dict):
        out = {}
        for key in sorted(value):
            if key in allowed_nondeterministic_fields:
                continue
            out[key] = _normalize(value[key], allowed_nondeterministic_fields)
        return out
    if isinstance(value, list):
        normalized = [_normalize(v, allowed_nondeterministic_fields) for v in value]
        try:
            return sorted(normalized, key=lambda x: json.dumps(x, sort_keys=True))
        except TypeError:
            return normalized
    return value


def build_deterministic_signature(payload: dict[str, Any], allowed_nondeterministic_fields: set[str] | None = None) -> str:
    allowed = allowed_nondeterministic_fields or DEFAULT_ALLOWED_NDETERMINISTIC_FIELDS
    normalized = _normalize(payload, allowed)
    raw = json.dumps(normalized, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def atomic_write_yaml(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    text = yaml.safe_dump(payload, sort_keys=True, allow_unicode=True)
    temp.write_text(text, encoding="utf-8")
    temp.replace(path)


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    temp.replace(path)
