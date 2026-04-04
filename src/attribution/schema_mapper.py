"""Map validation failures to governed schema anchors."""

from __future__ import annotations

from pathlib import Path

from src.attribution.artifact_resolver import (
    load_dataset_readiness,
    load_generated_contract,
    load_interface_registry,
    load_schema_ownership_map,
    resolve_schema_anchor,
)
from src.models.attribution_models import AttributionEligibleResult, AttributionSkipRecord, SchemaAnchor, SkipReason

REPO_ROOT = Path(__file__).resolve().parents[2]


def map_result_to_anchor(result: AttributionEligibleResult, repo_root: Path = REPO_ROOT) -> tuple[SchemaAnchor | None, list[str]]:
    contract = load_generated_contract(repo_root, result.contract_id)
    if contract is None:
        return None, [f"Missing generated contract for {result.contract_id}"]

    interfaces = load_interface_registry(repo_root)
    ownership_records = load_schema_ownership_map(repo_root)
    datasets = load_dataset_readiness(repo_root)

    anchor = resolve_schema_anchor(
        report_contract_id=result.contract_id,
        result_check_id=result.check_id,
        column_name=result.column_name,
        contract=contract,
        interfaces=interfaces,
        ownership_records=ownership_records,
        datasets=datasets,
    )
    result.schema_anchor = anchor
    return anchor, []


def annotate_eligibility(result: AttributionEligibleResult, repo_root: Path = REPO_ROOT) -> tuple[AttributionEligibleResult | AttributionSkipRecord, list[str]]:
    anchor, issues = map_result_to_anchor(result, repo_root=repo_root)
    if anchor is None:
        return (
            AttributionSkipRecord(
                report_id=result.report_id,
                contract_id=result.contract_id,
                dataset_id=result.dataset_id,
                check_id=result.check_id,
                check_type=result.check_type,
                column_name=result.column_name,
                status=result.status,
                skip_reason=SkipReason.missing_contract_context,
                message="; ".join(issues) if issues else "missing contract context",
            ),
            issues,
        )
    if anchor.interface_id is None and anchor.ownership_id is None and anchor.field_path is None:
        return (
            AttributionSkipRecord(
                report_id=result.report_id,
                contract_id=result.contract_id,
                dataset_id=result.dataset_id,
                check_id=result.check_id,
                check_type=result.check_type,
                column_name=result.column_name,
                status=result.status,
                skip_reason=SkipReason.non_governed_failure,
                message="Result could not be mapped to a governed dataset, interface, or lineage node",
            ),
            issues,
        )
    return result, issues
