"""Contract loading and executable check normalization."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from src.models.readiness_models import DatasetReadinessEntry
from src.models.validation_models import CheckScope, ExecutableCheck, LoadedContract, ValidationSeverity


@dataclass(slots=True)
class ContractLoadContext:
    repo_root: Path
    contracts_dir: Path
    readiness_index: dict[str, DatasetReadinessEntry]


def _load_structured(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        return json.loads(text)
    return yaml.safe_load(text)


def build_contract_load_context(repo_root: Path) -> ContractLoadContext:
    contracts_dir = repo_root / "generated_contracts"
    readiness_path = repo_root / "contracts" / "dataset_readiness.json"
    readiness_rows = _load_structured(readiness_path) or []
    readiness_index = {
        row["dataset_id"]: DatasetReadinessEntry.model_validate(row)
        for row in readiness_rows
        if isinstance(row, dict) and row.get("dataset_id")
    }
    return ContractLoadContext(repo_root=repo_root, contracts_dir=contracts_dir, readiness_index=readiness_index)


def _normalize_clause(contract_id: str, clause: dict[str, Any]) -> ExecutableCheck:
    check_type = str(clause.get("type", "unknown"))
    field_name = clause.get("field")
    if field_name in (None, "null"):
        field_name = None
    field_name = str(field_name) if field_name is not None else None
    scope = CheckScope.dataset if check_type == "dataset_check" else CheckScope.field
    if check_type == "relationship":
        scope = CheckScope.record
    if check_type in {"row_count", "uniqueness", "referential_integrity"}:
        scope = CheckScope.dataset
    if check_type in {"relationship"}:
        scope = CheckScope.record
    if check_type == "drift":
        scope = CheckScope.drift
    severity = ValidationSeverity(clause.get("confidence", "medium") if clause.get("confidence") in ValidationSeverity.__members__ else "medium")
    expression = clause.get("expression") or {}
    if not isinstance(expression, dict):
        expression = {"value": expression}
    return ExecutableCheck(
        check_id=str(clause.get("id")),
        contract_id=contract_id,
        column_name=field_name,
        check_type=check_type,
        scope=scope,
        expected={**expression, "source": clause.get("source", "inferred")},
        severity=severity,
        source_clause_id=str(clause.get("id")),
    )


def load_contract(path: Path, context: ContractLoadContext, baseline_refresh_allowed: bool = False) -> LoadedContract:
    raw = _load_structured(path) or {}
    if not isinstance(raw, dict):
        raise ValueError(f"Contract file is not a mapping: {path}")

    contract_id = str(raw.get("contract_id") or path.stem)
    dataset_id = str(raw.get("dataset_id") or contract_id.rsplit(".", 1)[0])
    readiness_entry = context.readiness_index.get(dataset_id)
    snapshot_path = readiness_entry.canonical_path if readiness_entry else str(raw.get("canonical_input_path") or "")
    clauses = raw.get("clauses") or []
    schema_fields = raw.get("schema_fields") or []
    metadata = raw.get("metadata") or {}
    numeric_fields = [
        str(field.get("field_path"))
        for field in schema_fields
        if isinstance(field, dict) and field.get("numeric_stats") is not None and field.get("field_path")
    ]
    checks = [
        _normalize_clause(contract_id, clause)
        for clause in clauses
        if isinstance(clause, dict) and clause.get("id")
    ]

    for field in schema_fields:
        if not isinstance(field, dict):
            continue
        field_path = field.get("field_path")
        if not field_path:
            continue
        observed_types = [str(item) for item in field.get("types", []) if item]
        if observed_types:
            checks.append(
                ExecutableCheck(
                    check_id=f"{contract_id}.{field_path}.type",
                    contract_id=contract_id,
                    column_name=str(field_path),
                    check_type="type",
                    scope=CheckScope.field,
                    expected={"types": observed_types},
                    severity=ValidationSeverity.medium,
                    source_clause_id=f"{contract_id}.{field_path}.type",
                )
            )
        checks.append(
            ExecutableCheck(
                check_id=f"{contract_id}.{field_path}.nullability",
                contract_id=contract_id,
                column_name=str(field_path),
                check_type="nullability",
                scope=CheckScope.field,
                expected={"nullable": bool(field.get("null_rate", 0.0))},
                severity=ValidationSeverity.medium,
                source_clause_id=f"{contract_id}.{field_path}.nullability",
            )
        )

    expected_row_count = None
    input_record_counts = metadata.get("input_record_counts") if isinstance(metadata, dict) else {}
    if isinstance(input_record_counts, dict):
        expected_row_count = input_record_counts.get(dataset_id)
    if expected_row_count is not None:
        checks.append(
            ExecutableCheck(
                check_id=f"{contract_id}.dataset.row_count",
                contract_id=contract_id,
                column_name=None,
                check_type="row_count",
                scope=CheckScope.dataset,
                expected={"row_count": int(expected_row_count)},
                severity=ValidationSeverity.medium,
                source_clause_id=f"{contract_id}.dataset.row_count",
            )
        )

    for field_name in numeric_fields:
        checks.append(
            ExecutableCheck(
                check_id=f"{contract_id}.{field_name}.drift",
                contract_id=contract_id,
                column_name=field_name,
                check_type="drift",
                scope=CheckScope.drift,
                expected={"numeric_field": field_name},
                severity=ValidationSeverity.medium,
                is_drift=True,
            )
        )
    return LoadedContract(
        contract_id=contract_id,
        dataset_id=dataset_id,
        contract_path=str(path.as_posix()),
        snapshot_path=str(snapshot_path),
        source_contract=raw,
        checks=checks,
        numeric_fields=numeric_fields,
        schema_fields=schema_fields,
        baseline_refresh_allowed=baseline_refresh_allowed,
    )


def load_contracts(repo_root: Path, contract_ids: list[str] | None = None, baseline_refresh_allowed: bool = False) -> list[LoadedContract]:
    context = build_contract_load_context(repo_root)
    candidates = sorted(context.contracts_dir.glob("*.yaml"))
    selected: list[LoadedContract] = []
    requested = set(contract_ids or [])
    for path in candidates:
        if requested and path.stem not in requested and str(path.with_suffix("")) not in requested:
            continue
        selected.append(load_contract(path, context, baseline_refresh_allowed=baseline_refresh_allowed))
    return selected
