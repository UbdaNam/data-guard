"""Compatibility taxonomy classification for schema changes."""

from __future__ import annotations

from src.models.schema_evolution_models import (
    ChangeClass,
    CompatibilityAssessment,
    CompatibilityVerdict,
    SchemaChange,
)


def _derive_verdict(backward: bool, forward: bool) -> CompatibilityVerdict:
    if backward and forward:
        return CompatibilityVerdict.fully_compatible
    if backward and not forward:
        return CompatibilityVerdict.backward_compatible
    if (not backward) and forward:
        return CompatibilityVerdict.forward_compatible
    return CompatibilityVerdict.breaking


def classify_change(change: SchemaChange) -> CompatibilityAssessment:
    rules: dict[ChangeClass, tuple[bool, bool, str]] = {
        ChangeClass.add_nullable_field: (True, False, "Nullable field addition is typically backward-compatible."),
        ChangeClass.add_required_field: (False, False, "Required field addition is breaking for existing producers/consumers."),
        ChangeClass.remove_field: (False, False, "Field removal is breaking."),
        ChangeClass.rename_field: (False, False, "Field rename is breaking unless explicit compatibility mapping exists."),
        ChangeClass.widen_type: (True, False, "Type widening is usually backward-compatible but not forward-compatible."),
        ChangeClass.narrow_type: (False, False, "Type narrowing is breaking."),
        ChangeClass.change_enum_values: (False, False, "Enum changes can invalidate existing values and are treated as breaking."),
        ChangeClass.change_constraints: (False, False, "Constraint changes are breaking by default without explicit waiver."),
        ChangeClass.change_nested_structure: (False, False, "Nested shape changes are breaking unless additive-only at optional paths."),
        ChangeClass.change_semantic_scale: (False, False, "Semantic scale changes are breaking by default."),
    }

    backward, forward, rationale = rules.get(change.change_class, (False, False, "Unknown change class"))

    # Fine-grained adjustment for enum expansion vs narrowing and relaxed constraints.
    if change.change_class == ChangeClass.change_enum_values:
        added = set(change.details.get("enum_added") or [])
        removed = set(change.details.get("enum_removed") or [])
        if added and not removed:
            backward, forward = True, False
            rationale = "Enum expansion is typically backward-compatible."
    if change.change_class == ChangeClass.change_constraints:
        if bool(change.details.get("relaxed")) and not bool(change.details.get("tightened")):
            backward, forward = True, False
            rationale = "Constraint relaxation is usually backward-compatible."

    return CompatibilityAssessment(
        is_backward_compatible=backward,
        is_forward_compatible=forward,
        verdict=_derive_verdict(backward, forward),
        rationale=rationale,
    )


def apply_change_classification(changes: list[SchemaChange]) -> list[SchemaChange]:
    classified: list[SchemaChange] = []
    for change in changes:
        change.compatibility = classify_change(change)
        classified.append(change)
    return classified


def aggregate_compatibility(changes: list[SchemaChange], baseline: bool = False) -> CompatibilityAssessment:
    if baseline:
        return CompatibilityAssessment(
            is_backward_compatible=True,
            is_forward_compatible=True,
            verdict=CompatibilityVerdict.fully_compatible,
            rationale="Baseline established: no comparison snapshot available.",
        )

    if not changes:
        return CompatibilityAssessment(
            is_backward_compatible=True,
            is_forward_compatible=True,
            verdict=CompatibilityVerdict.fully_compatible,
            rationale="No material schema changes detected.",
        )

    backward = all(change.compatibility and change.compatibility.is_backward_compatible for change in changes)
    forward = all(change.compatibility and change.compatibility.is_forward_compatible for change in changes)
    return CompatibilityAssessment(
        is_backward_compatible=bool(backward),
        is_forward_compatible=bool(forward),
        verdict=_derive_verdict(bool(backward), bool(forward)),
        rationale="Aggregate verdict derived from per-change compatibility assessment.",
    )
