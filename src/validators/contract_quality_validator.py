"""Quality checks for generated contract outputs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

REQUIRED_METADATA_FIELDS = {
    "run_id",
    "generated_at",
    "generator_version",
    "contract_schema_version",
    "input_artifact_hashes",
    "input_record_counts",
    "malformed_line_count",
    "mismatch_count",
    "deterministic_signature",
}

CANONICAL_OUTPUTS = {
    "week3.extractions": {
        "contract": "generated_contracts/week3_extractions.yaml",
        "dbt": "generated_contracts/week3_extractions_dbt.yml",
    },
    "week5.events": {
        "contract": "generated_contracts/week5_events.yaml",
        "dbt": "generated_contracts/week5_events_dbt.yml",
    },
}

FORBIDDEN_BEHAVIORS = {
    "validation_execution",
    "violation_attribution",
    "schema_evolution_diffing",
    "ai_specific_checks",
    "report_generation",
}


def validate_canonical_output_names(dataset_id: str, contract_path: str, dbt_path: str) -> list[str]:
    expected = CANONICAL_OUTPUTS.get(dataset_id)
    if not expected:
        return []
    issues: list[str] = []
    if contract_path != expected["contract"]:
        issues.append(f"Contract output path mismatch for {dataset_id}: {contract_path}")
    if dbt_path != expected["dbt"]:
        issues.append(f"dbt output path mismatch for {dataset_id}: {dbt_path}")
    return issues


def validate_metadata(metadata: dict[str, Any]) -> list[str]:
    missing = sorted(REQUIRED_METADATA_FIELDS - set(metadata))
    return [f"Missing metadata field: {name}" for name in missing]


def validate_no_forbidden_behaviors(enabled_behaviors: set[str]) -> list[str]:
    bad = sorted(FORBIDDEN_BEHAVIORS & enabled_behaviors)
    return [f"Forbidden behavior enabled: {name}" for name in bad]


def repo_relative(path: Path, repo_root: Path) -> str:
    try:
        return path.relative_to(repo_root).as_posix()
    except ValueError:
        return path.as_posix()
