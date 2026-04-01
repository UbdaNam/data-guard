"""Baseline persistence for statistical drift comparison."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from src.models.validation_models import BaselineStatistic, NumericProfile

BASELINE_FILE_NAME = "baselines.json"


@dataclass(slots=True)
class BaselineStore:
    repo_root: Path

    @property
    def path(self) -> Path:
        return self.repo_root / "schema_snapshots" / BASELINE_FILE_NAME

    def _read_payload(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"version": 1, "contracts": {}}
        return json.loads(self.path.read_text(encoding="utf-8"))

    def load(self) -> dict[str, dict[str, BaselineStatistic]]:
        payload = self._read_payload()
        contracts = payload.get("contracts", {}) or {}
        baselines: dict[str, dict[str, BaselineStatistic]] = {}
        for contract_id, contract_data in contracts.items():
            field_map: dict[str, BaselineStatistic] = {}
            for column_name, raw in (contract_data or {}).items():
                if isinstance(raw, dict):
                    field_map[column_name] = BaselineStatistic.model_validate(raw)
            baselines[contract_id] = field_map
        return baselines

    def save(self, baselines: dict[str, dict[str, BaselineStatistic]]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload: dict[str, Any] = {"version": 1, "contracts": {}}
        for contract_id, contract_fields in sorted(baselines.items()):
            payload["contracts"][contract_id] = {
                column_name: baseline.model_dump(mode="json")
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
