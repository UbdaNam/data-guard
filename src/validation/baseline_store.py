"""Baseline persistence for statistical drift comparison."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from contracts.artifact_paths import NUMERIC_BASELINES_PATH
from src.models.validation_models import BaselineStatistic, NumericProfile

BASELINE_FILE_NAME = "baselines.json"


@dataclass(slots=True)
class BaselineStore:
    repo_root: Path

    @property
    def path(self) -> Path:
        return NUMERIC_BASELINES_PATH

    def _read_payload(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"version": 1, "contracts": {}}
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            return {"version": 1, "contracts": {}}
        return payload

    @staticmethod
    def _coerce_baseline(raw: dict[str, Any], contract_id: str, column_name: str) -> BaselineStatistic:
        sample_size = raw.get("sample_count", raw.get("sample_size", 0))
        return BaselineStatistic(
            contract_id=str(raw.get("contract_id") or contract_id),
            column_name=str(raw.get("column_name") or column_name),
            mean=float(raw.get("mean", 0.0)),
            stddev=float(raw.get("stddev", 0.0)),
            min=float(raw.get("min", 0.0)),
            max=float(raw.get("max", 0.0)),
            sample_size=int(sample_size or 0),
            created_at=str(raw.get("created_at") or raw.get("generated_at") or datetime.now(UTC).isoformat()),
            updated_at=str(raw.get("updated_at") or raw.get("generated_at") or datetime.now(UTC).isoformat()),
        )

    def load(self) -> dict[str, dict[str, BaselineStatistic]]:
        payload = self._read_payload()
        contracts = payload.get("contracts", {}) or {}
        baselines: dict[str, dict[str, BaselineStatistic]] = {}
        for contract_id, contract_data in contracts.items():
            field_map: dict[str, BaselineStatistic] = {}
            if isinstance(contract_data, list):
                for raw in contract_data:
                    if isinstance(raw, dict):
                        column_name = str(raw.get("column_name") or raw.get("field_name") or "unknown")
                        field_map[column_name] = self._coerce_baseline(raw, str(contract_id), column_name)
            else:
                for column_name, raw in (contract_data or {}).items():
                    if isinstance(raw, dict):
                        field_map[column_name] = self._coerce_baseline(raw, str(contract_id), str(column_name))
            baselines[str(contract_id)] = field_map
        return baselines

    def save(self, baselines: dict[str, dict[str, BaselineStatistic]]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload: dict[str, Any] = {"version": 2, "generated_at": datetime.now(UTC).isoformat(), "contracts": {}}
        for contract_id, contract_fields in sorted(baselines.items()):
            payload["contracts"][contract_id] = {
                column_name: {
                    "contract_id": baseline.contract_id,
                    "column_name": baseline.column_name,
                    "sample_count": baseline.sample_size,
                    "mean": baseline.mean,
                    "stddev": baseline.stddev,
                    "min": baseline.min,
                    "max": baseline.max,
                    "distribution_summary": {
                        "sample_count": baseline.sample_size,
                        "mean": baseline.mean,
                        "stddev": baseline.stddev,
                        "min": baseline.min,
                        "max": baseline.max,
                    },
                    "created_at": baseline.created_at,
                    "updated_at": baseline.updated_at,
                }
                for column_name, baseline in sorted(contract_fields.items())
            }
        temp_path = self.path.with_suffix(".json.tmp")
        temp_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        temp_path.replace(self.path)

    def build_baseline(self, contract_id: str, profile: NumericProfile) -> BaselineStatistic:
        now = datetime.now(UTC).isoformat()
        return BaselineStatistic(
            contract_id=contract_id,
            column_name=profile.column_name,
            mean=profile.mean,
            stddev=profile.stddev,
            min=profile.min,
            max=profile.max,
            sample_size=profile.sample_size,
            created_at=now,
            updated_at=now,
        )

    def update_from_profiles(
        self,
        contract_id: str,
        profiles: dict[str, NumericProfile],
        refresh_allowed: bool,
    ) -> dict[str, dict[str, BaselineStatistic]]:
        baselines = self.load()
        contract_baselines = baselines.setdefault(contract_id, {})
        for column_name, profile in profiles.items():
            existing = contract_baselines.get(column_name)
            if existing is None:
                contract_baselines[column_name] = self.build_baseline(contract_id, profile)
                continue
            if refresh_allowed:
                updated = self.build_baseline(contract_id, profile)
                updated.created_at = existing.created_at
                contract_baselines[column_name] = updated
            else:
                contract_baselines[column_name] = existing
        self.save(baselines)
        return baselines
