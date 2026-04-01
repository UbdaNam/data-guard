"""Bitol and dbt-compatible rendering for generated contracts."""

from __future__ import annotations

from typing import Any

from src.models.contract_models import DbtSchemaArtifact, GeneratedContract


def render_bitol_contract(contract: GeneratedContract) -> dict[str, Any]:
    return {
        "contract_id": contract.contract_id,
        "dataset_id": contract.dataset_target.dataset_id,
        "schema_name": contract.dataset_target.schema_name,
        "canonical_input_path": contract.dataset_target.canonical_input_path,
        "clauses": [
            {
                "id": clause.clause_id,
                "field": clause.field_path,
                "type": clause.clause_type,
                "source": clause.source.value,
                "expression": clause.expression,
                "confidence": clause.confidence.value,
            }
            for clause in contract.clauses
        ],
        "schema_fields": [
            {
                "field_path": field.field_path,
                "parent_path": field.parent_path,
                "types": field.observed_types,
                "presence_rate": field.presence_rate,
                "null_rate": field.null_rate,
                "numeric_stats": field.numeric_stats,
                "semantic_confidence": field.semantic_confidence.value,
                "uncertainty_note": field.uncertainty_note,
            }
            for field in contract.schema_fields
        ],
        "downstream_context": contract.downstream_context.model_dump(mode="json"),
        "mismatch_records": [m.model_dump() for m in contract.mismatch_records],
        "metadata": contract.metadata.model_dump(mode="json"),
    }


def render_dbt_schema(contract: GeneratedContract) -> DbtSchemaArtifact:
    model_name = contract.dataset_target.dataset_id.replace(".", "_")
    columns: list[dict[str, Any]] = []
    tests: list[dict[str, Any]] = []
    unsupported: list[str] = []

    grouped: dict[str, list[dict[str, Any]]] = {}
    for clause in contract.clauses:
        if not clause.field_path:
            continue
        grouped.setdefault(clause.field_path, []).append(
            {
                "type": clause.clause_type,
                "expression": clause.expression,
            }
        )

    for field_path, clauses in sorted(grouped.items()):
        column_tests: list[Any] = []
        for clause in clauses:
            ctype = clause["type"]
            expression = clause["expression"]
            if ctype == "required":
                column_tests.append("not_null")
                tests.append({"field": field_path, "test": "not_null"})
            elif ctype == "enum":
                vals = expression.get("accepted_values") or []
                column_tests.append({"accepted_values": {"values": vals}})
                tests.append({"field": field_path, "test": "accepted_values", "values": vals})
            elif ctype == "uniqueness":
                column_tests.append("unique")
                tests.append({"field": field_path, "test": "unique"})
            elif ctype == "relationship":
                rel = expression.get("to") or "unknown_model"
                col = expression.get("field") or "id"
                column_tests.append({"relationships": {"to": rel, "field": col}})
                tests.append({"field": field_path, "test": "relationships", "to": rel, "column": col})
            else:
                unsupported.append(f"{field_path}:{ctype}")

        columns.append(
            {
                "name": field_path,
                "description": "Generated contract field",
                "tests": column_tests,
            }
        )

    return DbtSchemaArtifact(
        model_name=model_name,
        columns=columns,
        tests=tests,
        unsupported_clause_mappings=sorted(set(unsupported)),
    )


def render_dbt_yaml_payload(artifact: DbtSchemaArtifact) -> dict[str, Any]:
    return {
        "version": 2,
        "models": [
            {
                "name": artifact.model_name,
                "columns": artifact.columns,
            }
        ],
        "unsupported_clause_mappings": artifact.unsupported_clause_mappings,
    }
