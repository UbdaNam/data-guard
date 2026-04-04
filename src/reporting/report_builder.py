"""Build structured report sections from normalized artifacts."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from src.reporting.completeness import complete, insufficient, status_from_presence
from src.reporting.health_score import compute_data_health_score
from src.reporting.models import (
    AiRiskSummary,
    EvidenceReference,
    GenerationEnrichment,
    GenerationMetadata,
    OperationalReportData,
    SchemaChangesSummary,
    TopViolation,
    ViolationsSummary,
)
from src.reporting.ranking import build_schema_changes_summary, rank_top_violations, summarize_violations
from src.reporting.window_resolver import WindowResolution, parse_timestamp


def _owner_lookup(ownership_map: list[dict]) -> dict[str, str]:
    out: dict[str, str] = {}
    for row in ownership_map:
        ownership_id = str(row.get("ownership_id") or "")
        producer_owner = str(row.get("producer_owner") or "")
        if ownership_id:
            out[ownership_id] = producer_owner or "unassigned"
    return out


def _critical_violation_count(violations: list[dict]) -> int:
    return sum(1 for row in violations if str(row.get("severity", "")).lower() == "critical")


def _filter_to_window(rows: list[dict], window: WindowResolution) -> list[dict]:
    filtered: list[dict] = []
    for row in rows:
        ts = (
            row.get("detected_at")
            or row.get("event_timestamp")
            or row.get("run_timestamp")
            or row.get("generated_at")
            or row.get("report_date")
        )
        if window.includes(str(ts) if ts is not None else None):
            filtered.append(row)
    return filtered


def build_report_data(
    *,
    loaded,
    window: WindowResolution,
    recommended_actions,
    enrichment: GenerationEnrichment,
    duration_ms: int,
) -> OperationalReportData:
    owner_by_id = _owner_lookup(loaded.ownership_map)
    violations_in_window = _filter_to_window(loaded.violations, window)
    validation_in_window = _filter_to_window(loaded.validation_reports, window)
    schema_in_window = _filter_to_window(loaded.schema_evolution_reports, window)

    score = compute_data_health_score(
        validation_reports=validation_in_window,
        critical_violation_count=_critical_violation_count(violations_in_window),
    )

    top_violations = rank_top_violations(violations_in_window, owner_by_id)
    by_severity, by_category, by_surface = summarize_violations(violations_in_window)
    violation_evidence = [
        EvidenceReference(
            artifact_path=str(row.get("_artifact_path", "violation_log/violations.jsonl")),
            record_selector=str(row.get("violation_id") or row.get("check_id") or "unknown"),
            claim_type="incident",
        )
        for row in violations_in_window[:50]
    ]
    violations_summary = ViolationsSummary(
        total=len(violations_in_window),
        by_severity=by_severity,
        by_category=by_category,
        by_surface=by_surface,
        evidence=violation_evidence,
    )

    ranked_changes = build_schema_changes_summary(schema_in_window)
    schema_summary = SchemaChangesSummary(
        total_changes=len(ranked_changes),
        breaking_changes=sum(1 for row in ranked_changes if "breaking" in row.compatibility_verdict.lower()),
        non_breaking_changes=sum(1 for row in ranked_changes if "breaking" not in row.compatibility_verdict.lower()),
        top_changes=ranked_changes,
        evidence=[ref for row in ranked_changes for ref in row.evidence],
    )

    ai_payload = loaded.ai_metrics or {}
    ai_risk_summary = AiRiskSummary(
        quarantine_rate=(ai_payload.get("rates") or {}).get("prompt_quarantine_rate") if isinstance(ai_payload.get("rates"), dict) else None,
        output_violation_rate=(ai_payload.get("rates") or {}).get("output_violation_rate") if isinstance(ai_payload.get("rates"), dict) else None,
        trace_violation_rate=(ai_payload.get("rates") or {}).get("trace_violation_rate") if isinstance(ai_payload.get("rates"), dict) else None,
        drift_status=(ai_payload.get("trend") or {}).get("trend_status") if isinstance(ai_payload.get("trend"), dict) else None,
        trend_status=(ai_payload.get("trend") or {}).get("trend_status", "unknown") if isinstance(ai_payload.get("trend"), dict) else "unknown",
        completeness_flags={
            "has_metrics": bool(loaded.ai_metrics),
            "has_history": bool((ai_payload.get("history") if isinstance(ai_payload, dict) else None)),
        },
        evidence=[
            EvidenceReference(
                artifact_path=str(ai_payload.get("_artifact_path", "validation_reports/ai_metrics.json")),
                record_selector="rates",
                claim_type="ai_risk",
            )
        ]
        if loaded.ai_metrics
        else [],
    )

    section_completeness = {
        "data_health_score": status_from_presence(
            records_count=len(validation_in_window),
            missing_sources=loaded.missing_sources.get("data_health_score", []),
            empty_reason="Validation reports unavailable for reporting window.",
        ),
        "violations": status_from_presence(
            records_count=len(violations_in_window),
            missing_sources=loaded.missing_sources.get("violations", []),
            empty_reason="No violations found for reporting window.",
        ),
        "schema_changes": status_from_presence(
            records_count=len(schema_in_window),
            missing_sources=loaded.missing_sources.get("schema_changes", []),
            empty_reason="Schema evolution outputs unavailable for reporting window.",
        ),
        "ai_risk": complete() if loaded.ai_metrics else insufficient(
            missing_sources=loaded.missing_sources.get("ai_risk", []),
            reason="AI metrics unavailable.",
        ),
        "recommended_actions": complete() if recommended_actions else insufficient(
            missing_sources=[],
            reason="No actionable evidence found in reporting window.",
        ),
    }

    evidence_index: list[EvidenceReference] = []
    for ref in violation_evidence:
        evidence_index.append(ref)
    for row in ranked_changes:
        evidence_index.extend(row.evidence)
    evidence_index.extend(ai_risk_summary.evidence)
    for action in recommended_actions:
        evidence_index.extend(action.evidence)

    # deterministic de-duplication
    seen: set[tuple[str, str, str]] = set()
    deduped_evidence: list[EvidenceReference] = []
    for ref in sorted(evidence_index, key=lambda item: (item.artifact_path, item.record_selector, item.claim_type)):
        key = (ref.artifact_path, ref.record_selector, ref.claim_type)
        if key in seen:
            continue
        seen.add(key)
        deduped_evidence.append(ref)

    report_date = datetime.now(UTC).date().isoformat()
    return OperationalReportData(
        report_id=str(uuid4()),
        report_date=report_date,
        reporting_window=window.window,
        data_health_score=score,
        section_completeness=section_completeness,
        violations_summary=violations_summary,
        top_violations=top_violations,
        schema_changes_summary=schema_summary,
        ai_risk_summary=ai_risk_summary,
        recommended_actions=recommended_actions,
        evidence_index=deduped_evidence,
        generation_metadata=GenerationMetadata(
            generated_at=datetime.now(UTC).isoformat(),
            duration_ms=duration_ms,
            input_artifact_counts=loaded.counts,
            enrichment=enrichment,
        ),
    )
