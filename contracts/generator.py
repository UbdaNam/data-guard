"""Deferred contract generation entry point.

Feature 1 only preserves this interface boundary. Contract execution is not
implemented in the foundation feature.
"""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from src.generation.dataset_loader import load_feature1_artifacts, load_jsonl_dataset, resolve_dataset_targets
from src.generation.deterministic_writer import atomic_write_json, atomic_write_yaml, build_deterministic_signature
from src.generation.invariant_synthesizer import synthesize_invariants
from src.generation.lineage_injector import inject_downstream_context
from src.generation.profilers import profile_records
from src.generation.renderers import render_bitol_contract, render_dbt_schema, render_dbt_yaml_payload
from src.models.contract_models import CanonicalMismatchRecord, GeneratedContract, GenerationMetadata
from src.validators.contract_quality_validator import validate_canonical_output_names, validate_metadata


REPO_ROOT = Path(__file__).resolve().parents[1]


def _build_mismatch_records(dataset_id: str, readiness_status: str) -> list[CanonicalMismatchRecord]:
    if readiness_status in {"blocked_by_missing_upstream_data", "pending_migration_or_normalization"}:
        return [
            CanonicalMismatchRecord(
                dataset_id=dataset_id,
                mismatch_type="semantic",
                canonical_value="canonical_governed_schema",
                observed_value="upstream_variant",
                impact_note="Observed data may diverge from canonical target",
                migration_or_normalization_required=True,
            )
        ]
    return []


def run_generation(dataset_ids: list[str] | None = None) -> dict[str, Any]:
    artifacts = load_feature1_artifacts(REPO_ROOT)
    targets = resolve_dataset_targets(artifacts, dataset_ids)

    summary: dict[str, Any] = {"generated": [], "failed": []}
    readiness_rows: list[dict[str, Any]] = []

    for target in targets:
        load_result = load_jsonl_dataset(REPO_ROOT, target)
        if load_result.errors:
            readiness_rows.append(
                {
                    "dataset_id": target.dataset_id,
                    "status": "failed",
                    "reason": "; ".join(load_result.errors),
                }
            )
            summary["failed"].append(
                {
                    "dataset_id": target.dataset_id,
                    "errors": load_result.errors,
                }
            )
            continue

        profiled_fields = profile_records(load_result.records)
        clauses = synthesize_invariants(target.dataset_id, profiled_fields, artifacts.requirement_traceability)
        downstream_context = inject_downstream_context(
            target.dataset_id,
            artifacts.interface_registry,
            artifacts.schema_ownership_map,
            REPO_ROOT,
        )
        mismatch_records = _build_mismatch_records(target.dataset_id, target.readiness_status)

        metadata = GenerationMetadata(
            run_id=str(uuid4()),
            generated_at=datetime.now(UTC).isoformat(),
            input_artifact_hashes={},
            input_record_counts={target.dataset_id: load_result.valid_record_count},
            malformed_line_count=len(load_result.malformed_lines),
            mismatch_count=len(mismatch_records),
        )

        contract = GeneratedContract(
            contract_id=f"{target.dataset_id.replace('.', '_')}.v1",
            dataset_target=target,
            schema_fields=profiled_fields,
            clauses=clauses,
            downstream_context=downstream_context,
            mismatch_records=mismatch_records,
            metadata=metadata,
        )

        contract_payload = render_bitol_contract(contract)
        dbt_artifact = render_dbt_schema(contract)
        dbt_payload = render_dbt_yaml_payload(dbt_artifact)
        signature = build_deterministic_signature(contract_payload)
        contract_payload.setdefault("metadata", {})["deterministic_signature"] = signature
        metadata.deterministic_signature = signature

        quality_issues = []
        quality_issues.extend(
            validate_canonical_output_names(
                target.dataset_id,
                target.canonical_contract_output_path,
                target.canonical_dbt_output_path,
            )
        )
        quality_issues.extend(validate_metadata(contract_payload.get("metadata", {})))

        contract_out = REPO_ROOT / target.canonical_contract_output_path
        dbt_out = REPO_ROOT / target.canonical_dbt_output_path
        metadata_out = REPO_ROOT / "generated_contracts" / f"{target.dataset_id.replace('.', '_')}.metadata.json"

        atomic_write_yaml(contract_out, contract_payload)
        atomic_write_yaml(dbt_out, dbt_payload)
        atomic_write_json(
            metadata_out,
            {
                "dataset_id": target.dataset_id,
                "metadata": metadata.model_dump(),
                "malformed_lines": load_result.malformed_lines,
                "quality_issues": quality_issues,
            },
        )

        summary["generated"].append(
            {
                "dataset_id": target.dataset_id,
                "contract_output": target.canonical_contract_output_path,
                "dbt_output": target.canonical_dbt_output_path,
                "metadata_output": str(metadata_out.relative_to(REPO_ROOT).as_posix()),
                "quality_issues": quality_issues,
            }
        )
        readiness_rows.append(
            {
                "dataset_id": target.dataset_id,
                "status": "generated",
                "contract_output": target.canonical_contract_output_path,
                "dbt_output": target.canonical_dbt_output_path,
                "metadata_output": str(metadata_out.relative_to(REPO_ROOT).as_posix()),
                "quality_issues": quality_issues,
            }
        )

    atomic_write_json(
        REPO_ROOT / "validation_reports" / "readiness_index.json",
        {
            "feature": "contract-generation-engine",
            "generated_count": len(summary["generated"]),
            "failed_count": len(summary["failed"]),
            "datasets": readiness_rows,
        },
    )

    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Contract generation engine")
    parser.add_argument(
        "--datasets",
        nargs="*",
        default=["week3.extractions", "week5.events"],
        help="Dataset IDs to generate",
    )
    args = parser.parse_args()

    result = run_generation(args.datasets)
    print(result)
    return 0 if not result.get("failed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
