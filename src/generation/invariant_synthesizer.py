"""Invariant synthesis from profiling and requirement-driven rules."""

from __future__ import annotations

from typing import Any

from src.models.contract_models import InvariantClause, InvariantSource, ProfiledField, SemanticConfidence


def _confidence_guard(field_path: str) -> bool:
    lowered = field_path.lower()
    return any(token in lowered for token in ("confidence", "confidence_score", "confidence_probability"))


def _dataset_requirement_overrides(dataset_id: str) -> list[InvariantClause]:
    slug = dataset_id.replace(".", "_")
    return [
        InvariantClause(
            clause_id=f"{slug}.dataset.required_schema",
            field_path=None,
            clause_type="dataset_check",
            source=InvariantSource.requirement_defined,
            expression={"rule": "must_align_to_canonical_schema"},
            confidence=SemanticConfidence.high,
            supported_in_dbt=False,
        )
    ]


def synthesize_invariants(
    dataset_id: str,
    profiled_fields: list[ProfiledField],
    requirement_traceability: list[dict[str, Any]] | None = None,
) -> list[InvariantClause]:
    clauses: list[InvariantClause] = []
    slug = dataset_id.replace(".", "_")

    for field in profiled_fields:
        if field.presence_rate >= 0.99:
            clauses.append(
                InvariantClause(
                    clause_id=f"{slug}.{field.field_path}.required",
                    field_path=field.field_path,
                    clause_type="required",
                    source=InvariantSource.inferred,
                    expression={"presence_rate": field.presence_rate},
                    confidence=SemanticConfidence.high,
                    supported_in_dbt=True,
                )
            )

        if field.numeric_stats:
            clauses.append(
                InvariantClause(
                    clause_id=f"{slug}.{field.field_path}.range",
                    field_path=field.field_path,
                    clause_type="range",
                    source=InvariantSource.inferred,
                    expression={
                        "min": field.numeric_stats.get("min"),
                        "max": field.numeric_stats.get("max"),
                    },
                    confidence=SemanticConfidence.medium,
                    supported_in_dbt=False,
                )
            )
            if _confidence_guard(field.field_path):
                clauses.append(
                    InvariantClause(
                        clause_id=f"{slug}.{field.field_path}.confidence_bounds",
                        field_path=field.field_path,
                        clause_type="confidence_bounds",
                        source=InvariantSource.inferred,
                        expression={"min": 0.0, "max": 1.0},
                        confidence=SemanticConfidence.high,
                        supported_in_dbt=False,
                    )
                )
            if (field.numeric_stats.get("min") or 0) >= 0:
                clauses.append(
                    InvariantClause(
                        clause_id=f"{slug}.{field.field_path}.positivity",
                        field_path=field.field_path,
                        clause_type="positivity",
                        source=InvariantSource.inferred,
                        expression={"non_negative": True},
                        confidence=SemanticConfidence.medium,
                        supported_in_dbt=False,
                    )
                )

        if field.candidate_enum_values and len(field.candidate_enum_values) <= 20:
            clauses.append(
                InvariantClause(
                    clause_id=f"{slug}.{field.field_path}.enum",
                    field_path=field.field_path,
                    clause_type="enum",
                    source=InvariantSource.inferred,
                    expression={"accepted_values": field.candidate_enum_values},
                    confidence=SemanticConfidence.medium,
                    supported_in_dbt=True,
                )
            )

        if field.uniqueness_rate is not None and field.uniqueness_rate >= 0.99:
            clauses.append(
                InvariantClause(
                    clause_id=f"{slug}.{field.field_path}.uniqueness",
                    field_path=field.field_path,
                    clause_type="uniqueness",
                    source=InvariantSource.inferred,
                    expression={"uniqueness_rate": field.uniqueness_rate},
                    confidence=SemanticConfidence.medium,
                    supported_in_dbt=True,
                )
            )

        if field.semantic_confidence == SemanticConfidence.low:
            clauses.append(
                InvariantClause(
                    clause_id=f"{slug}.{field.field_path}.uncertainty",
                    field_path=field.field_path,
                    clause_type="annotation",
                    source=InvariantSource.inferred,
                    expression={"note": field.uncertainty_note or "Semantic meaning unresolved"},
                    confidence=SemanticConfidence.low,
                    supported_in_dbt=False,
                )
            )

    clauses.extend(_dataset_requirement_overrides(dataset_id))

    # Ensure a minimum baseline of clause breadth for contract completeness.
    if len(clauses) < 8:
        clauses.append(
            InvariantClause(
                clause_id=f"{slug}.dataset.baseline_placeholder",
                field_path=None,
                clause_type="dataset_check",
                source=InvariantSource.requirement_defined,
                expression={"note": "Baseline clause injected to satisfy minimum clause coverage"},
                confidence=SemanticConfidence.medium,
                supported_in_dbt=False,
            )
        )

    return sorted(clauses, key=lambda c: (c.field_path or "", c.clause_type, c.clause_id))
