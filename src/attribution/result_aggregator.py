"""Attribution result aggregation helpers."""

from __future__ import annotations

import hashlib
import json
from statistics import mean

from src.attribution.confidence_scorer import confidence_band
from src.models.attribution_models import (
    AttributionConfidenceSummary,
    AttributionEligibleResult,
    BlameCandidate,
    BlastRadiusSummary,
    ViolationRecord,
)


def build_violation_identity(
    report_id: str,
    contract_id: str,
    dataset_id: str,
    check_id: str,
    detected_at: str,
) -> str:
    payload = json.dumps(
        {
            "report_id": report_id,
            "contract_id": contract_id,
            "dataset_id": dataset_id,
            "check_id": check_id,
            "detected_at": detected_at,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def sort_candidates(candidates: list[BlameCandidate]) -> list[BlameCandidate]:
    return sorted(
        candidates,
        key=lambda candidate: (
            -candidate.normalized_score,
            candidate.source_node.hop,
            candidate.evidence_bundle[0].authored_at if candidate.evidence_bundle else "",
            candidate.evidence_bundle[0].commit_hash if candidate.evidence_bundle else "",
            candidate.candidate_id,
        ),
    )


def build_confidence_summary(candidates: list[BlameCandidate]) -> AttributionConfidenceSummary | None:
    if not candidates:
        return None
    scores = [candidate.normalized_score for candidate in candidates]
    return AttributionConfidenceSummary(
        max_score=max(scores),
        min_score=min(scores),
        average_score=round(mean(scores), 2),
        confidence_band=confidence_band(max(scores)),
        uncertainty_reasons=sorted({reason for candidate in candidates for reason in candidate.uncertainty_reasons}),
    )


def assemble_violation_record(
    eligible_result: AttributionEligibleResult,
    blame_chain: list[BlameCandidate],
    blast_radius: BlastRadiusSummary,
    detected_at: str,
    confidence_summary: AttributionConfidenceSummary | None = None,
) -> ViolationRecord:
    sorted_chain = sort_candidates(blame_chain)[:5]
    violation_id = build_violation_identity(
        eligible_result.report_id,
        eligible_result.contract_id,
        eligible_result.dataset_id,
        eligible_result.check_id,
        detected_at,
    )
    return ViolationRecord(
        violation_id=violation_id,
        report_id=eligible_result.report_id,
        detected_at=detected_at,
        contract_id=eligible_result.contract_id,
        dataset_id=eligible_result.dataset_id,
        check_id=eligible_result.check_id,
        check_type=eligible_result.check_type,
        status=eligible_result.status,
        column_name=eligible_result.column_name,
        schema_anchor=eligible_result.schema_anchor,
        blame_chain=sorted_chain,
        blast_radius=blast_radius,
        attribution_confidence_summary=confidence_summary,
        selected_reason=eligible_result.selected_reason,
    )
