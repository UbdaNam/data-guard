"""Load governing artifacts for Feature 6 from Features 1-5 outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml


def _load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _load_yaml(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return default if data is None else data


def load_governed_prompt_schema(repo_root: Path) -> dict[str, Any]:
    prompt_schema_path = repo_root / "generated_contracts" / "prompt_inputs" / "week3_prompt_input.schema.json"
    return _load_json(prompt_schema_path, {})


def load_governed_output_schema(repo_root: Path) -> dict[str, Any]:
    # Week2 contract may not exist in this phase; fallback remains deterministic.
    default_schema = {
        "schema_id": "week2_verdict_structured_output",
        "schema_version": "v1",
        "required": ["record_id", "verdict"],
        "properties": {
            "record_id": {"type": "string"},
            "verdict": {"type": "string"},
            "score": {"type": "number"},
            "reason": {"type": "string"},
        },
        "allow_additional": False,
    }
    week2_contract = repo_root / "generated_contracts" / "week2_verdicts.schema.json"
    return _load_json(week2_contract, default_schema)


def load_feature1_metadata(repo_root: Path) -> dict[str, Any]:
    contracts_dir = repo_root / "contracts"
    return {
        "canonical_paths": _load_yaml(contracts_dir / "canonical_paths.yaml", {}),
        "interface_registry": _load_yaml(contracts_dir / "interface_registry.yaml", {}),
        "schema_ownership_map": _load_yaml(contracts_dir / "schema_ownership_map.yaml", {}),
        "dataset_readiness": _load_json(contracts_dir / "dataset_readiness.json", []),
    }


def load_feature5_context(repo_root: Path) -> list[dict[str, Any]]:
    reports_dir = repo_root / "validation_reports"
    context: list[dict[str, Any]] = []
    for path in sorted(reports_dir.glob("schema_evolution_*.json")):
        try:
            context.append(_load_json(path, {}))
        except Exception:
            continue
    return context


def build_context(repo_root: Path) -> dict[str, Any]:
    feature1 = load_feature1_metadata(repo_root)
    prompt_schema = load_governed_prompt_schema(repo_root)
    output_schema = load_governed_output_schema(repo_root)
    feature5 = load_feature5_context(repo_root)
    return {
        "feature1": feature1,
        "prompt_schema": prompt_schema,
        "output_schema": output_schema,
        "feature5_context": feature5,
        "context_completeness": {
            "feature1_loaded": bool(feature1.get("canonical_paths")),
            "feature2_loaded": bool(prompt_schema or output_schema),
            "feature3_conventions_loaded": True,
            "feature5_context_loaded": bool(feature5),
        },
    }
