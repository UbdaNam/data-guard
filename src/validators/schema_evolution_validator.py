"""Validation helpers for Feature 5 schema evolution artifacts."""

from __future__ import annotations

from typing import Any

from src.models.schema_evolution_models import (
    ChangeClass,
    CompatibilityVerdict,
    MigrationImpactReport,
    SchemaEvolutionReport,
)

EVOLUTION_REQUIRED_FIELDS = {
    "analysis_id",
    "contract_id",
    "from_snapshot_id",
    "to_snapshot_id",
    "structured_diff",
    "compatibility_verdict",
    "change_summary",
    "warnings",
    "context_completeness",
}

MIGRATION_REQUIRED_FIELDS = {
    "report_id",
    "analysis_id",
    "contract_id",
    "human_diff_summary",
    "structured_diff",
    "compatibility_verdict",
    "affected_consumers",
    "migration_checklist",
    "rollback_guidance",
    "urgency",
    "confidence_change_caused_breakage",
    "enrichment_sources",
}

CHANGE_CLASS_ORDER = [
    ChangeClass.add_nullable_field.value,
    ChangeClass.add_required_field.value,
    ChangeClass.remove_field.value,
    ChangeClass.rename_field.value,
    ChangeClass.widen_type.value,
    ChangeClass.narrow_type.value,
    ChangeClass.change_enum_values.value,
    ChangeClass.change_constraints.value,
    ChangeClass.change_nested_structure.value,
    ChangeClass.change_semantic_scale.value,
]


def _validate_required_fields(payload: dict[str, Any], required: set[str], label: str) -> list[str]:
    issues: list[str] = []
    missing = sorted(required - set(payload))
    for field in missing:
        issues.append(f"Missing {label} field: {field}")
    return issues


def _validate_diff_order(structured_diff: list[dict[str, Any]]) -> list[str]:
    issues: list[str] = []
    last_rank = -1
    last_key = ""
    for index, change in enumerate(structured_diff):
        change_class = str(change.get("change_class", ""))
        if change_class not in CHANGE_CLASS_ORDER:
            issues.append(f"Unknown change class at index {index}: {change_class}")
            continue
        rank = CHANGE_CLASS_ORDER.index(change_class)
        from_path = (change.get("from_field") or {}).get("path", "")
        to_path = (change.get("to_field") or {}).get("path", "")
        key = f"{min(from_path, to_path)}|{max(from_path, to_path)}"
        if rank < last_rank:
            issues.append("structured_diff is not ordered by required change class precedence")
            continue
        if rank == last_rank and key < last_key:
            issues.append("structured_diff is not path-sorted within change class")
            continue
        last_rank = rank
        last_key = key
    return issues


def validate_evolution_payload(payload: dict[str, Any], strict: bool = True) -> list[str]:
    issues = _validate_required_fields(payload, EVOLUTION_REQUIRED_FIELDS, "evolution")
    verdict = ((payload.get("compatibility_verdict") or {}).get("verdict"))
    if verdict not in {item.value for item in CompatibilityVerdict}:
        issues.append(f"Invalid compatibility verdict: {verdict}")

    structured_diff = payload.get("structured_diff", [])
    if not isinstance(structured_diff, list):
        issues.append("Field 'structured_diff' must be a list")
    else:
        issues.extend(_validate_diff_order([item for item in structured_diff if isinstance(item, dict)]))

    if strict and issues:
        raise ValueError("; ".join(issues))
    return issues


def validate_migration_payload(payload: dict[str, Any], strict: bool = True) -> list[str]:
    issues = _validate_required_fields(payload, MIGRATION_REQUIRED_FIELDS, "migration")
    verdict = ((payload.get("compatibility_verdict") or {}).get("verdict"))
    if verdict == CompatibilityVerdict.breaking.value and not payload.get("rollback_guidance"):
        issues.append("Breaking compatibility verdict requires rollback_guidance")

    checklist = payload.get("migration_checklist", [])
    if not isinstance(checklist, list):
        issues.append("Field 'migration_checklist' must be a list")
        checklist = []
    for index, item in enumerate(checklist):
        if not isinstance(item, dict):
            issues.append(f"Checklist entry at index {index} must be an object")
            continue
        for field_name in ("owner", "action", "target", "verification"):
            if not item.get(field_name):
                issues.append(f"Checklist entry at index {index} missing field '{field_name}'")

    if strict and issues:
        raise ValueError("; ".join(issues))
    return issues


def validate_evolution_model(report: SchemaEvolutionReport) -> list[str]:
    return validate_evolution_payload(report.model_dump(mode="json"), strict=False)


def validate_migration_model(report: MigrationImpactReport) -> list[str]:
    return validate_migration_payload(report.model_dump(mode="json"), strict=False)
