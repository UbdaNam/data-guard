"""Canonical artifact and dataset loading utilities."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from src.models.contract_models import DatasetLoadResult, DatasetTarget


@dataclass(slots=True)
class Feature1Artifacts:
    canonical_paths: list[dict[str, Any]]
    dataset_readiness: list[dict[str, Any]]
    interface_registry: list[dict[str, Any]]
    schema_ownership_map: list[dict[str, Any]]
    data_flow_reference_path: str
    domain_notes: str
    requirement_traceability: list[dict[str, Any]]


def _read_structured(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        return json.loads(text)
    return yaml.safe_load(text)


def load_feature1_artifacts(repo_root: Path) -> Feature1Artifacts:
    contracts_dir = repo_root / "contracts"
    domain_notes_path = repo_root / "DOMAIN_NOTES.md"

    required_paths = {
        "canonical_paths": contracts_dir / "canonical_paths.yaml",
        "dataset_readiness": contracts_dir / "dataset_readiness.json",
        "interface_registry": contracts_dir / "interface_registry.yaml",
        "schema_ownership_map": contracts_dir / "schema_ownership_map.yaml",
        "data_flow_architecture": contracts_dir / "data_flow_architecture.mmd",
        "requirement_traceability": contracts_dir / "requirement_traceability.yaml",
        "domain_notes": domain_notes_path,
    }

    missing = [name for name, path in required_paths.items() if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing required Feature 1 artifacts: {', '.join(sorted(missing))}")

    return Feature1Artifacts(
        canonical_paths=list(_read_structured(required_paths["canonical_paths"]) or []),
        dataset_readiness=list(_read_structured(required_paths["dataset_readiness"]) or []),
        interface_registry=list(_read_structured(required_paths["interface_registry"]) or []),
        schema_ownership_map=list(_read_structured(required_paths["schema_ownership_map"]) or []),
        data_flow_reference_path=str(required_paths["data_flow_architecture"].as_posix()),
        domain_notes=required_paths["domain_notes"].read_text(encoding="utf-8"),
        requirement_traceability=list(_read_structured(required_paths["requirement_traceability"]) or []),
    )


def resolve_dataset_targets(artifacts: Feature1Artifacts, dataset_ids: list[str] | None = None) -> list[DatasetTarget]:
    desired = dataset_ids or ["week3.extractions", "week5.events"]
    by_id = {row.get("dataset_id"): row for row in artifacts.dataset_readiness}

    targets: list[DatasetTarget] = []
    for dataset_id in desired:
        row = by_id.get(dataset_id)
        if not row:
            raise ValueError(f"Dataset '{dataset_id}' missing from dataset readiness inventory")

        canonical_path = str(row.get("canonical_path", "")).strip()
        slug = dataset_id.replace(".", "_")
        targets.append(
            DatasetTarget(
                dataset_id=dataset_id,
                canonical_input_path=canonical_path,
                canonical_contract_output_path=f"generated_contracts/{slug}.yaml",
                canonical_dbt_output_path=f"generated_contracts/{slug}_dbt.yml",
                schema_name=str(row.get("schema_name", "unknown_schema")),
                readiness_status=str(row.get("readiness_status", "unknown")),
            )
        )

    return targets


def load_jsonl_dataset(repo_root: Path, target: DatasetTarget) -> DatasetLoadResult:
    dataset_path = repo_root / target.canonical_input_path
    result = DatasetLoadResult(target=target)

    if not dataset_path.exists():
        result.errors.append(f"Missing dataset path: {target.canonical_input_path}")
        return result

    for line_number, line in enumerate(dataset_path.read_text(encoding="utf-8").splitlines(), start=1):
        raw = line.strip()
        if not raw:
            continue
        try:
            value = json.loads(raw)
        except json.JSONDecodeError:
            result.malformed_lines.append(f"line {line_number}: {raw[:200]}")
            continue
        if isinstance(value, dict):
            result.records.append(value)
        else:
            result.malformed_lines.append(f"line {line_number}: non-object JSON value")

    if not result.records:
        result.errors.append(f"No valid object records in dataset: {target.canonical_input_path}")

    return result
