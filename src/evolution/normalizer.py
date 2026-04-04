"""Normalization utilities for schema evolution snapshots."""

from __future__ import annotations

from typing import Any

from src.models.schema_evolution_models import ContractRule, NestedKind, NormalizedField


def _pick_field_type(types: list[str] | None) -> str:
    if not types:
        return "unknown"
    clean = [str(item).lower() for item in types if item is not None]
    if not clean:
        return "unknown"
    if "dict" in clean:
        return "object"
    if "list" in clean:
        return "array"
    return sorted(clean)[0]


def _nested_kind(path: str, field_type: str) -> NestedKind:
    if field_type == "object":
        return NestedKind.object
    if field_type == "array":
        return NestedKind.array
    if path.endswith("{}"):
        return NestedKind.map
    return NestedKind.scalar


def _aggregate_clause_constraints(clauses: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    by_field: dict[str, dict[str, Any]] = {}
    for clause in clauses:
        field = clause.get("field")
        if not field:
            continue
        expression = clause.get("expression") if isinstance(clause.get("expression"), dict) else {}
        by_field.setdefault(str(field), {})[str(clause.get("type", "unknown"))] = expression
    return by_field


def normalize_fields(contract_payload: dict[str, Any]) -> list[NormalizedField]:
    clauses = contract_payload.get("clauses") if isinstance(contract_payload.get("clauses"), list) else []
    constraints = _aggregate_clause_constraints([item for item in clauses if isinstance(item, dict)])

    normalized: list[NormalizedField] = []
    raw_fields = contract_payload.get("schema_fields") if isinstance(contract_payload.get("schema_fields"), list) else []
    for item in raw_fields:
        if not isinstance(item, dict):
            continue
        path = str(item.get("field_path") or "").strip()
        if not path:
            continue

        field_constraints = constraints.get(path, {})
        enum_values = field_constraints.get("enum", {}).get("accepted_values")
        range_payload = field_constraints.get("range", {})
        required = bool(item.get("presence_rate", 0) >= 1.0)
        nullable = bool(item.get("null_rate", 0) > 0)

        field_type = _pick_field_type(item.get("types"))
        normalized.append(
            NormalizedField(
                path=path,
                type=field_type,
                nullable=nullable,
                required=required,
                enum_values=[str(value) for value in enum_values] if isinstance(enum_values, list) else None,
                pattern=(field_constraints.get("pattern", {}) or {}).get("regex"),
                minimum=float(range_payload.get("min")) if range_payload.get("min") is not None else None,
                maximum=float(range_payload.get("max")) if range_payload.get("max") is not None else None,
                nested_kind=_nested_kind(path, field_type),
                raw_constraints=field_constraints,
            )
        )

    return sorted(normalized, key=lambda field: field.path)


def normalize_rules(contract_payload: dict[str, Any]) -> list[ContractRule]:
    rules: list[ContractRule] = []
    raw_clauses = contract_payload.get("clauses") if isinstance(contract_payload.get("clauses"), list) else []
    for clause in raw_clauses:
        if not isinstance(clause, dict):
            continue
        rule_id = clause.get("id")
        if not rule_id:
            continue
        rules.append(
            ContractRule(
                rule_id=str(rule_id),
                rule_scope="field" if clause.get("field") else "dataset",
                rule_type=str(clause.get("type", "unknown")),
                rule_payload=clause.get("expression") if isinstance(clause.get("expression"), dict) else {},
            )
        )
    return sorted(rules, key=lambda rule: rule.rule_id)


def normalize_contract(contract_payload: dict[str, Any]) -> dict[str, Any]:
    """Return deterministic normalized schema payload for hashing and snapshots."""

    return {
        "contract_id": contract_payload.get("contract_id"),
        "schema_version": (contract_payload.get("metadata") or {}).get("contract_schema_version"),
        "dataset_id": contract_payload.get("dataset_id"),
        "schema_name": contract_payload.get("schema_name"),
        "fields": [field.model_dump(mode="json") for field in normalize_fields(contract_payload)],
        "rules": [rule.model_dump(mode="json") for rule in normalize_rules(contract_payload)],
    }
