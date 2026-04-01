"""Streaming numeric profiling for drift detection."""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from typing import Any

from src.models.validation_models import NumericProfile
from src.validation.dataset_loader import extract_values


@dataclass(slots=True)
class RunningStats:
    count: int = 0
    mean: float = 0.0
    m2: float = 0.0
    min_value: float = float("inf")
    max_value: float = float("-inf")

    def update(self, value: float) -> None:
        self.count += 1
        delta = value - self.mean
        self.mean += delta / self.count
        delta2 = value - self.mean
        self.m2 += delta * delta2
        self.min_value = min(self.min_value, value)
        self.max_value = max(self.max_value, value)

    def to_profile(self, column_name: str) -> NumericProfile | None:
        if self.count == 0:
            return None
        variance = self.m2 / self.count if self.count > 0 else 0.0
        stddev = sqrt(variance) if variance > 0 else 0.0
        return NumericProfile(
            column_name=column_name,
            sample_size=self.count,
            mean=self.mean,
            stddev=stddev,
            min=self.min_value,
            max=self.max_value,
        )


def profile_numeric_fields(rows: list[dict[str, Any]], field_names: list[str]) -> dict[str, NumericProfile]:
    stats = {field_name: RunningStats() for field_name in field_names}
    for row in rows:
        for field_name in field_names:
            for value in extract_values(row, field_name):
                if isinstance(value, bool):
                    continue
                if isinstance(value, (int, float)):
                    stats[field_name].update(float(value))
    profiles: dict[str, NumericProfile] = {}
    for field_name, running in stats.items():
        profile = running.to_profile(field_name)
        if profile is not None:
            profiles[field_name] = profile
    return profiles
