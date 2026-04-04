"""Deterministic schema diff generation."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from src.evolution.matcher import match_fields
from src.models.schema_evolution_models import ChangeClass, FieldMatch, MatchType, NormalizedField, SchemaChange

CHANGE_CLASS_ORDER = {
    ChangeClass.add_nullable_field: 0,
    ChangeClass.add_required_field: 1,
    ChangeClass.remove_field: 2,
    ChangeClass.rename_field: 3,
    ChangeClass.widen_type: 4,
    ChangeClass.narrow_type: 5,
    ChangeClass.change_enum_values: 6,
    ChangeClass.change_constraints: 7,
    ChangeClass.change_nested_structure: 8,
    ChangeClass.change_semantic_scale: 9,
}

NUMERIC_ORDER = {
    "bool": 0,
    "int": 1,
    "float": 2,
    "decimal": 3,
    "str": 4,
    "object": 5,
    "array": 6,
    "unknown": 7,
}


def _stable_change_id(change_class: ChangeClass, from_field: NormalizedField | None, to_field: NormalizedField | None, details: dict[str, Any]) -> str:
    payload = {
        "change_class": change_class.value,
        "from": from_field.model_dump(mode="json") if from_field else None,
        "to": to_field.model_dump(mode="json") if to_field else None,
        "details": details,
    }
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


def _make_change(change_class: ChangeClass, from_field: NormalizedField | None, to_field: NormalizedField | None, details: dict[str, Any] | None = None) -> SchemaChange:
    details = details or {}
    return SchemaChange(
        change_id=_stable_change_id(change_class, from_field, to_field, details),
        change_class=change_class,
        from_field=from_field,
        to_field=to_field,
        details=details,
    )


def _compare_type(from_type: str, to_type: str) -> ChangeClass | None:
    left_rank = NUMERIC_ORDER.get(from_type, NUMERIC_ORDER["unknown"])
    right_rank = NUMERIC_ORDER.get(to_type, NUMERIC_ORDER["unknown"])
    if left_rank == right_rank:
        return None
    if left_rank < right_rank:
        return ChangeClass.widen_type
    return ChangeClass.narrow_type


def _compare_constraints(source: NormalizedField, target: NormalizedField) -> list[SchemaChange]:
    changes: list[SchemaChange] = []

    if source.enum_values != target.enum_values:
        source_values = source.enum_values or []
        target_values = target.enum_values or []
        details = {
            "added": sorted(set(target_values) - set(source_values)),
            "removed": sorted(set(source_values) - set(target_values)),
        }
        changes.append(_make_change(ChangeClass.change_enum_values, source, target, details))

    constraint_delta = {
        "required_before": source.required,
        "required_after": target.required,
        "nullable_before": source.nullable,
        "nullable_after": target.nullable,
        "minimum_before": source.minimum,
        "minimum_after": target.minimum,
        "maximum_before": source.maximum,
        "maximum_after": target.maximum,
        "pattern_before": source.pattern,
        "pattern_after": target.pattern,
    }
    if any(
        constraint_delta[key_before] != constraint_delta[key_after]
        for key_before, key_after in (
            ("required_before", "required_after"),
            ("nullable_before", "nullable_after"),
            ("minimum_before", "minimum_after"),
            ("maximum_before", "maximum_after"),
            ("pattern_before", "pattern_after"),
        )
    ):
        changes.append(_make_change(ChangeClass.change_constraints, source, target, constraint_delta))

    if (
        source.minimum is not None
        and target.minimum is not None
        and target.minimum > source.minimum
        or source.maximum is not None
        and target.maximum is not None
        and target.maximum < source.maximum
    ):
        classification = None
        if (
            source.minimum == 0.0
            and source.maximum == 1.0
            and target.minimum == 0.0
            and target.maximum == 100.0
        ):
            classification = "CRITICAL"
        changes.append(
            _make_change(
                ChangeClass.change_semantic_scale,
                source,
                target,
                {
                    "from_range": [source.minimum, source.maximum],
                    "to_range": [target.minimum, target.maximum],
                    **({"classification": classification} if classification else {}),
                },
            )
        )

    if source.nested_kind != target.nested_kind:
        changes.append(
            _make_change(
                ChangeClass.change_nested_structure,
                source,
                target,
                {
                    "from_nested_kind": source.nested_kind.value,
                    "to_nested_kind": target.nested_kind.value,
                },
            )
        )

    return changes


def compute_structured_diff(
    from_fields: list[NormalizedField],
    to_fields: list[NormalizedField],
    matches: list[FieldMatch],
    unmatched_from_paths: set[str],
    unmatched_to_paths: set[str],
) -> list[SchemaChange]:
    from_by_path = {field.path: field for field in from_fields}
    to_by_path = {field.path: field for field in to_fields}

    changes: list[SchemaChange] = []

    for path in sorted(unmatched_to_paths):
        field = to_by_path[path]
        change_class = ChangeClass.add_required_field if field.required else ChangeClass.add_nullable_field
        changes.append(_make_change(change_class, None, field))

    for path in sorted(unmatched_from_paths):
        changes.append(_make_change(ChangeClass.remove_field, from_by_path[path], None))

    for match in matches:
        if not match.from_path or not match.to_path:
            continue
        source = from_by_path[match.from_path]
        target = to_by_path[match.to_path]

        if match.match_type in {MatchType.explicit_rename, MatchType.heuristic_rename} and source.path != target.path:
            changes.append(
                _make_change(
                    ChangeClass.rename_field,
                    source,
                    target,
                    {
                        "match_type": match.match_type.value,
                        "confidence": match.confidence,
                        "evidence": match.evidence,
                    },
                )
            )

        type_change = _compare_type(source.type, target.type)
        if type_change:
            changes.append(_make_change(type_change, source, target, {"from_type": source.type, "to_type": target.type}))

        changes.extend(_compare_constraints(source, target))

    return sorted(
        changes,
        key=lambda change: (
            CHANGE_CLASS_ORDER[change.change_class],
            (change.from_field.path if change.from_field else "~"),
            (change.to_field.path if change.to_field else "~"),
            change.change_id,
        ),
    )


def compute_schema_diff(
    from_fields: list[NormalizedField],
    to_fields: list[NormalizedField],
    explicit_renames: dict[str, str] | None = None,
) -> tuple[list[SchemaChange], dict[str, Any]]:
    matches, unmatched_from, unmatched_to = match_fields(
        from_fields,
        to_fields,
        explicit_renames=explicit_renames,
    )
    changes = compute_structured_diff(from_fields, to_fields, matches, unmatched_from, unmatched_to)
    summary = {
        "total_changes": len(changes),
        "added": sum(1 for item in changes if item.change_class in {ChangeClass.add_nullable_field, ChangeClass.add_required_field}),
        "removed": sum(1 for item in changes if item.change_class == ChangeClass.remove_field),
        "renamed": sum(1 for item in changes if item.change_class == ChangeClass.rename_field),
        "modified": sum(
            1
            for item in changes
            if item.change_class
            in {
                ChangeClass.widen_type,
                ChangeClass.narrow_type,
                ChangeClass.change_enum_values,
                ChangeClass.change_constraints,
                ChangeClass.change_nested_structure,
                ChangeClass.change_semantic_scale,
            }
        ),
    }
    return changes, summary
