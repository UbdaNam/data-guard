"""Migration impact report generation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from contracts.registry_loader import load_registry, registry_entries
from src.models.schema_evolution_models import (
    ChangeClass,
    CompatibilityVerdict,
    ConsumerImpact,
    MigrationAction,
    SchemaChange,
    Urgency,
)


def _load_yaml_list(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        if isinstance(payload, list):
            return [item for item in payload if isinstance(item, dict)]
    except Exception:
        return []
    return []


def resolve_affected_consumers(repo_root: Path, contract_payload: dict[str, Any]) -> list[ConsumerImpact]:
    dataset_id = str(contract_payload.get("dataset_id") or "")
    schema_name = str(contract_payload.get("schema_name") or "")

    interfaces = _load_yaml_list(repo_root / "contracts" / "interface_registry.yaml")
    ownerships = _load_yaml_list(repo_root / "contracts" / "schema_ownership_map.yaml")
    registry_payload = load_registry(repo_root / "docs" / "governance" / "subscriptions_registry.yaml") if (repo_root / "docs" / "governance" / "subscriptions_registry.yaml").exists() else None
    registry = registry_entries(registry_payload) if registry_payload else []

    interface_hits = [
        row
        for row in interfaces
        if dataset_id in [str(item) for item in row.get("dataset_refs", [])] or schema_name in [str(item) for item in row.get("schema_refs", [])]
    ]

    owner_hits = [row for row in ownerships if str(row.get("schema_name") or "") == schema_name]
    consumer_impacts: dict[str, ConsumerImpact] = {}

    registry_hits = [
        entry
        for entry in registry
        if entry.producer in {dataset_id, schema_name, str(contract_payload.get("contract_id") or "")}
        or entry.consumer in {dataset_id, schema_name, str(contract_payload.get("contract_id") or "")}
    ]

    for item in interface_hits:
        ownership_id = str(item.get("ownership_ref") or "") or None
        for owner in owner_hits:
            for consumer in owner.get("consumer_owners", []) or []:
                key = str(consumer)
                if key not in consumer_impacts:
                    consumer_impacts[key] = ConsumerImpact(
                        consumer_id=key,
                        interface_id=str(item.get("interface_id") or "") or None,
                        ownership_id=ownership_id,
                        likely_failure_modes=[],
                        impact_severity=Urgency.medium,
                    )

    for entry in registry_hits:
        key = entry.consumer
        if key not in consumer_impacts:
            consumer_impacts[key] = ConsumerImpact(
                consumer_id=key,
                interface_id=entry.interface_id,
                ownership_id=None,
                likely_failure_modes=[],
                impact_severity=Urgency.medium,
            )

    if not consumer_impacts:
        consumer_impacts["unknown_consumer"] = ConsumerImpact(
            consumer_id="unknown_consumer",
            interface_id=None,
            ownership_id=None,
            likely_failure_modes=["unknown_downstream_dependency"],
            impact_severity=Urgency.medium,
        )

    return sorted(consumer_impacts.values(), key=lambda item: item.consumer_id)


def _failure_modes_for_change(change: SchemaChange) -> list[str]:
    mapping = {
        ChangeClass.add_nullable_field: ["optional_field_ignored_by_legacy_consumers"],
        ChangeClass.add_required_field: ["missing_required_field_in_producer_payload", "deserializer_required_field_error"],
        ChangeClass.remove_field: ["missing_field_lookup", "contract_clause_resolution_failure"],
        ChangeClass.rename_field: ["field_path_not_found", "mapping_resolution_failure"],
        ChangeClass.widen_type: ["type_coercion_warning"],
        ChangeClass.narrow_type: ["type_cast_failure", "value_out_of_range_after_narrowing"],
        ChangeClass.change_enum_values: ["unknown_enum_value", "dropped_enum_value_breakage"],
        ChangeClass.change_constraints: ["constraint_violation_spike"],
        ChangeClass.change_nested_structure: ["nested_path_resolution_failure"],
        ChangeClass.change_semantic_scale: ["semantic_interpretation_mismatch"],
    }
    return mapping.get(change.change_class, ["unknown_schema_change_impact"])


def assign_failure_modes(consumers: list[ConsumerImpact], changes: list[SchemaChange]) -> list[ConsumerImpact]:
    modes: set[str] = set()
    for change in changes:
        modes.update(_failure_modes_for_change(change))

    severity = Urgency.medium
    if any(change.compatibility and change.compatibility.verdict == CompatibilityVerdict.breaking for change in changes):
        severity = Urgency.high

    hydrated: list[ConsumerImpact] = []
    for consumer in consumers:
        consumer.likely_failure_modes = sorted(set(consumer.likely_failure_modes) | modes)
        consumer.impact_severity = severity
        hydrated.append(consumer)
    return hydrated


def generate_migration_actions(changes: list[SchemaChange], default_owner: str = "schema-evolution-team") -> list[MigrationAction]:
    actions: list[MigrationAction] = []
    order = 1
    for change in changes:
        target = change.to_field.path if change.to_field else change.from_field.path if change.from_field else "dataset"
        actions.append(
            MigrationAction(
                order=order,
                owner=default_owner,
                action=f"Apply migration handling for {change.change_class.value}",
                target=target,
                verification=f"Re-run schema analysis and validate {target} in downstream contracts",
                rollback_step=(
                    f"Restore previous schema contract for {target} and redeploy dependent artifacts"
                    if change.compatibility and change.compatibility.verdict == CompatibilityVerdict.breaking
                    else None
                ),
            )
        )
        order += 1

    if not actions:
        actions.append(
            MigrationAction(
                order=1,
                owner=default_owner,
                action="No migration required",
                target="contract",
                verification="Confirm no material schema changes",
                rollback_step=None,
            )
        )

    return actions


def baseline_urgency_from_verdict(verdict: CompatibilityVerdict) -> Urgency:
    if verdict == CompatibilityVerdict.breaking:
        return Urgency.critical
    if verdict in {CompatibilityVerdict.backward_compatible, CompatibilityVerdict.forward_compatible}:
        return Urgency.medium
    return Urgency.low


def rollback_guidance(changes: list[SchemaChange], verdict: CompatibilityVerdict) -> list[str]:
    if verdict != CompatibilityVerdict.breaking:
        return []

    impacted_paths = sorted(
        {
            change.to_field.path if change.to_field else change.from_field.path if change.from_field else "dataset"
            for change in changes
        }
    )
    return [
        "Restore previous snapshot and contract artifacts for immediate rollback.",
        "Revert producer payload mapping and redeploy producer service.",
        f"Validate impacted paths after rollback: {', '.join(impacted_paths)}",
    ]
