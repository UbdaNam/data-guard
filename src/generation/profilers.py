"""Structural and statistical profiling for contract generation."""

from __future__ import annotations

import math
from collections import Counter, defaultdict
from statistics import mean, pstdev
from typing import Any

from src.models.contract_models import ProfiledField, SemanticConfidence

MAX_NESTING_DEPTH = 5


def _walk(value: Any, prefix: str, depth: int, out: dict[str, list[Any]]) -> None:
    if depth > MAX_NESTING_DEPTH:
        return

    if isinstance(value, dict):
        for key, sub in value.items():
            key_str = str(key)
            path = f"{prefix}.{key_str}" if prefix else key_str
            out[path].append(sub)
            _walk(sub, path, depth + 1, out)
        return

    if isinstance(value, list):
        for item in value:
            _walk(item, prefix, depth + 1, out)


def _numeric_summary(values: list[float]) -> dict[str, float]:
    if not values:
        return {}
    sorted_vals = sorted(values)

    def _pct(p: float) -> float:
        idx = min(len(sorted_vals) - 1, max(0, int(round((len(sorted_vals) - 1) * p))))
        return float(sorted_vals[idx])

    return {
        "min": float(sorted_vals[0]),
        "max": float(sorted_vals[-1]),
        "mean": float(mean(sorted_vals)),
        "stddev": float(pstdev(sorted_vals)) if len(sorted_vals) > 1 else 0.0,
        "p50": _pct(0.50),
        "p95": _pct(0.95),
        "p99": _pct(0.99),
    }


def profile_records(records: list[dict[str, Any]]) -> list[ProfiledField]:
    if not records:
        return []

    observed: dict[str, list[Any]] = defaultdict(list)
    for record in records:
        _walk(record, "", 1, observed)

    total_records = max(len(records), 1)
    profiled: list[ProfiledField] = []

    for field_path in sorted(observed):
        values = observed[field_path]
        non_null = [v for v in values if v is not None]
        types = sorted({type(v).__name__ for v in non_null})
        parent = field_path.rsplit(".", 1)[0] if "." in field_path else None

        numeric = [float(v) for v in non_null if isinstance(v, (int, float)) and not isinstance(v, bool)]
        enum_candidates = None
        if non_null:
            cnt = Counter(str(v) for v in non_null)
            if 1 < len(cnt) <= 20:
                enum_candidates = [k for k, _ in cnt.most_common(20)]

        uniq_rate = None
        if non_null:
            uniq_rate = len({jsonable(v) for v in non_null}) / len(non_null)

        confidence = SemanticConfidence.high
        note = None
        if len(types) > 2 or not types:
            confidence = SemanticConfidence.low
            note = "Weak semantic confidence due to heterogeneous or sparse observed types"

        profiled.append(
            ProfiledField(
                field_path=field_path,
                parent_path=parent,
                observed_types=types,
                presence_rate=min(1.0, len(values) / total_records),
                null_rate=1.0 - (len(non_null) / max(1, len(values))),
                numeric_stats=_numeric_summary(numeric) if numeric else None,
                candidate_enum_values=enum_candidates,
                uniqueness_rate=uniq_rate,
                pattern_candidates=None,
                semantic_confidence=confidence,
                uncertainty_note=note,
            )
        )

    return profiled


def jsonable(value: Any) -> str:
    if isinstance(value, (dict, list)):
        return str(value)
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return "nan"
    return str(value)
