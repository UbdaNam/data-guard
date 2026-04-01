"""Streaming dataset loading and nested value extraction."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator

from src.models.validation_models import LoadedDataset


@dataclass(slots=True)
class PathToken:
    name: str
    wildcard: bool = False


def parse_path(path: str) -> list[PathToken]:
    tokens: list[PathToken] = []
    for segment in path.split("."):
        if segment.endswith("[*]"):
            tokens.append(PathToken(name=segment[:-3], wildcard=True))
        else:
            tokens.append(PathToken(name=segment, wildcard=False))
    return tokens


def iter_jsonl_records(path: Path) -> Iterator[tuple[int, dict[str, Any] | None, str | None]]:
    if not path.exists():
        yield 0, None, f"Missing dataset file: {path.as_posix()}"
        return

    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        text = raw_line.strip()
        if not text:
            continue
        try:
            record = json.loads(text)
        except json.JSONDecodeError as exc:
            yield line_number, None, f"Malformed JSONL line {line_number}: {exc.msg}"
            continue
        if isinstance(record, dict):
            yield line_number, record, None
        else:
            yield line_number, None, f"Non-object JSON value on line {line_number}"


def load_dataset(dataset_id: str, snapshot_path: str) -> LoadedDataset:
    path = Path(snapshot_path)
    rows: list[dict[str, Any]] = []
    malformed_lines: list[dict[str, Any]] = []
    errors: list[str] = []

    for line_number, record, error in iter_jsonl_records(path):
        if error is not None:
            if line_number == 0:
                errors.append(error)
            else:
                malformed_lines.append({"line_number": line_number, "error": error})
            continue
        rows.append(record or {})

    if not rows and not errors:
        errors.append(f"No valid records found in dataset: {path.as_posix()}")

    return LoadedDataset(
        dataset_id=dataset_id,
        snapshot_path=path.as_posix(),
        rows=rows,
        malformed_lines=malformed_lines,
        errors=errors,
    )


def _extract_from_value(value: Any, tokens: list[PathToken], depth: int = 0) -> list[Any]:
    if depth >= len(tokens):
        return [value]

    token = tokens[depth]
    if isinstance(value, dict):
        if token.name not in value:
            return []
        next_value = value[token.name]
        if token.wildcard:
            if not isinstance(next_value, list):
                return []
            collected: list[Any] = []
            for item in next_value:
                collected.extend(_extract_from_value(item, tokens, depth + 1))
            return collected
        return _extract_from_value(next_value, tokens, depth + 1)

    if isinstance(value, list):
        collected: list[Any] = []
        for item in value:
            collected.extend(_extract_from_value(item, tokens, depth))
        return collected

    return []


def extract_values(record: dict[str, Any], field_path: str) -> list[Any]:
    return _extract_from_value(record, parse_path(field_path))


def extract_first_value(record: dict[str, Any], field_path: str) -> Any:
    values = extract_values(record, field_path)
    return values[0] if values else None


def field_exists(record: dict[str, Any], field_path: str) -> bool:
    return bool(extract_values(record, field_path))
