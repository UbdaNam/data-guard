"""Artifact resolution helpers for Feature 4."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from src.models.attribution_models import LoadedGeneratedContract, SchemaAnchor
from src.models.readiness_models import ArtifactStatus, DatasetReadinessEntry, InterfaceRegistryEntry, SchemaOwnershipRecord

REPO_ROOT = Path(__file__).resolve().parents[2]
GENERATED_CONTRACTS_DIR = REPO_ROOT / "generated_contracts"


def _read_json_or_yaml(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        return json.loads(text)
    return yaml.safe_load(text)


def _coerce_list(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    return []


def load_interface_registry(repo_root: Path = REPO_ROOT) -> list[InterfaceRegistryEntry]:
    payload = _read_json_or_yaml(repo_root / "contracts" / "interface_registry.yaml")
    return [InterfaceRegistryEntry.model_validate(item) for item in _coerce_list(payload)]


def load_schema_ownership_map(repo_root: Path = REPO_ROOT) -> list[SchemaOwnershipRecord]:
    payload = _read_json_or_yaml(repo_root / "contracts" / "schema_ownership_map.yaml")
    return [SchemaOwnershipRecord.model_validate(item) for item in _coerce_list(payload)]


def load_dataset_readiness(repo_root: Path = REPO_ROOT) -> list[DatasetReadinessEntry]:
    payload = _read_json_or_yaml(repo_root / "contracts" / "dataset_readiness.json")
    return [DatasetReadinessEntry.model_validate(item) for item in _coerce_list(payload)]


def load_generated_contract(repo_root: Path, contract_id: str) -> LoadedGeneratedContract | None:
    generated_dir = repo_root / "generated_contracts"
    candidates = sorted(generated_dir.glob("*.yaml"))
    for candidate in candidates:
        payload = _read_json_or_yaml(candidate)
        if not isinstance(payload, dict):
            continue
        if payload.get("contract_id") == contract_id:
            return LoadedGeneratedContract.model_validate({"source_path": candidate.as_posix(), **payload})
        if contract_id.startswith(candidate.stem + ".") or contract_id.replace(".", "_").startswith(candidate.stem):
            return LoadedGeneratedContract.model_validate({"source_path": candidate.as_posix(), **payload})
    return None


def build_dataset_index(datasets: list[DatasetReadinessEntry]) -> dict[str, DatasetReadinessEntry]:
    return {entry.dataset_id: entry for entry in datasets}


def build_interface_index(interfaces: list[InterfaceRegistryEntry]) -> dict[str, InterfaceRegistryEntry]:
    return {entry.interface_id: entry for entry in interfaces}


def build_ownership_index(records: list[SchemaOwnershipRecord]) -> dict[str, SchemaOwnershipRecord]:
    return {record.ownership_id: record for record in records}


def resolve_schema_anchor(
    report_contract_id: str,
    result_check_id: str,
    column_name: str | None,
    contract: LoadedGeneratedContract,
    interfaces: list[InterfaceRegistryEntry],
    ownership_records: list[SchemaOwnershipRecord],
    datasets: list[DatasetReadinessEntry],
) -> SchemaAnchor:
    dataset_lookup = build_dataset_index(datasets)
    ownership_index = build_ownership_index(ownership_records)

    dataset = dataset_lookup.get(contract.dataset_id)
    interface = next((entry for entry in interfaces if contract.dataset_id in entry.dataset_refs), None)
    ownership = ownership_index.get(interface.ownership_ref) if interface else None
    schema_name = contract.schema_name or (dataset.schema_name if dataset else None)

    field_path = column_name or next((clause.get("field") for clause in contract.clauses if clause.get("id") == result_check_id), None)
    directness = "dataset" if not field_path else "field"
    source_note = "mapped from contract clause" if field_path else "dataset-level fallback"

    return SchemaAnchor(
        dataset_id=contract.dataset_id,
        contract_id=report_contract_id,
        schema_name=schema_name,
        canonical_path=dataset.canonical_path if dataset else contract.canonical_input_path,
        field_path=field_path,
        check_id=result_check_id,
        interface_id=interface.interface_id if interface else None,
        ownership_id=ownership.ownership_id if ownership else None,
        producer_system=dataset.producer_system if dataset else (interface.source_system if interface else None),
        consumer_systems=list(dataset.consumer_systems if dataset else (interface.dataset_refs if interface else [])),
        status=dataset.readiness_status if dataset else (interface.status if interface else ArtifactStatus.inferred_from_requirement_document),
        directness=directness,
        source_note=source_note,
    )


def resolve_candidate_files(anchor: SchemaAnchor) -> list[str]:
    files: list[str] = []
    if anchor.canonical_path:
        files.append(anchor.canonical_path)
    if anchor.interface_id:
        files.append("contracts/interface_registry.yaml")
    if anchor.ownership_id:
        files.append("contracts/schema_ownership_map.yaml")
    if anchor.dataset_id:
        generated = GENERATED_CONTRACTS_DIR / f"{anchor.dataset_id.replace('.', '_')}.yaml"
        if generated.exists():
            files.append(generated.as_posix())
        report_dir = REPO_ROOT / "validation_reports"
        matching_reports = sorted(report_dir.glob(f"{anchor.dataset_id.replace('.', '_')}.v1_*.json"))
        files.extend(path.as_posix() for path in matching_reports[:3])
    return sorted(dict.fromkeys(files))


def resolve_anchor_context(anchor: SchemaAnchor, interfaces: list[InterfaceRegistryEntry], ownership_records: list[SchemaOwnershipRecord]) -> dict[str, Any]:
    interface = next((entry for entry in interfaces if entry.interface_id == anchor.interface_id), None)
    ownership = next((record for record in ownership_records if record.ownership_id == anchor.ownership_id), None)
    return {
        "interface": interface.model_dump(mode="json") if interface else None,
        "ownership": ownership.model_dump(mode="json") if ownership else None,
        "candidate_files": resolve_candidate_files(anchor),
    }
