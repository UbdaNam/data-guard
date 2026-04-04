"""Ranking utilities for violations and schema changes."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from src.reporting.models import EvidenceReference, RankedSchemaChange, TopViolation
from src.reporting.window_resolver import parse_timestamp


SEVERITY_RANK = {"critical": 4, "high": 3, "medium": 2, "low": 1}
IMPACT_RANK = {"high": 3, "medium": 2, "low": 1, "unknown": 0}


def _as_iso(value: str | None) -> str | None:
    ts = parse_timestamp(value)
    return ts.astimezone(UTC).isoformat() if ts else None


@dataclass(slots=True)
class ViolationAggregate:
    violation_id: str
    severity: str
    affected_surface: str
    owner: str
    recurrence_count: int
    latest_occurrence: str | None
    source_artifact_path: str
    field_path: str | None
    contract_clause_id: str | None
    evidence: list[EvidenceReference]


def rank_top_violations(
    violations: list[dict[str, Any]],
    owner_by_id: dict[str, str],
    *,
    limit: int = 10,
) -> list[TopViolation]:
    groups: dict[str, ViolationAggregate] = {}

    for row in violations:
        key = str(row.get("check_id") or row.get("violation_id") or row.get("report_id") or "unknown")
        severity = str(row.get("severity", "low")).lower()
        surface = str(
            row.get("dataset_id")
            or row.get("surface_id")
            or row.get("contract_id")
            or row.get("column_name")
            or "unknown"
        )
        selector = str(row.get("violation_id") or row.get("check_id") or key)
        schema_anchor = row.get("schema_anchor") if isinstance(row.get("schema_anchor"), dict) else {}
        field_path = str(row.get("column_name") or schema_anchor.get("field_path") or row.get("field_path") or "") or None
        contract_clause_id = str(row.get("check_id") or row.get("source_clause_id") or selector)
        source_artifact_path = str(row.get("_artifact_path", "violation_log/violations.jsonl"))
        evidence = EvidenceReference(
            artifact_path=source_artifact_path,
            record_selector=selector,
            claim_type="incident",
        )

        ownership_id = str(schema_anchor.get("ownership_id") or "")
        owner = owner_by_id.get(ownership_id, "unassigned")

        latest = _as_iso(
            str(
                row.get("detected_at")
                or row.get("event_timestamp")
                or row.get("run_timestamp")
                or ""
            )
        )

        if key not in groups:
            groups[key] = ViolationAggregate(
                violation_id=key,
                severity=severity,
                affected_surface=surface,
                owner=owner,
                recurrence_count=1,
                latest_occurrence=latest,
                source_artifact_path=source_artifact_path,
                field_path=field_path,
                contract_clause_id=contract_clause_id,
                evidence=[evidence],
            )
            continue

        item = groups[key]
        item.recurrence_count += 1
        item.evidence.append(evidence)
        if latest and (item.latest_occurrence is None or latest > item.latest_occurrence):
            item.latest_occurrence = latest
        if SEVERITY_RANK.get(severity, 0) > SEVERITY_RANK.get(item.severity, 0):
            item.severity = severity

    sorted_items = sorted(
        groups.values(),
        key=lambda item: (
            -SEVERITY_RANK.get(item.severity, 0),
            -item.recurrence_count,
            -(parse_timestamp(item.latest_occurrence).timestamp() if parse_timestamp(item.latest_occurrence) else 0.0),
            item.violation_id,
        ),
    )

    result: list[TopViolation] = []
    for idx, item in enumerate(sorted_items[:limit], start=1):
        result.append(
            TopViolation(
                rank=idx,
                violation_id=item.violation_id,
                severity=item.severity,
                recurrence_count=item.recurrence_count,
                latest_occurrence=item.latest_occurrence,
                affected_surface=item.affected_surface,
                owner=item.owner,
                priority_tuple=[
                    SEVERITY_RANK.get(item.severity, 0),
                    item.recurrence_count,
                    item.latest_occurrence or "",
                    item.violation_id,
                ],
                source_artifact_path=item.source_artifact_path,
                field_path=item.field_path,
                contract_clause_id=item.contract_clause_id,
                evidence=item.evidence,
            )
        )
    return result


def build_schema_changes_summary(
    schema_reports: list[dict[str, Any]],
    *,
    limit: int = 10,
) -> list[RankedSchemaChange]:
    ranked: list[RankedSchemaChange] = []

    for report in schema_reports:
        report_path = str(report.get("_artifact_path", "validation_reports/schema_evolution_unknown.json"))
        contract_id = str(report.get("contract_id", "unknown_contract"))
        verdict_obj = report.get("compatibility_verdict") if isinstance(report.get("compatibility_verdict"), dict) else {}
        verdict = str(verdict_obj.get("verdict", "unknown"))
        breaking = "breaking" in verdict.lower()
        impact_scope = "high" if breaking else "medium"

        diffs = report.get("structured_diff") if isinstance(report.get("structured_diff"), list) else []
        if not diffs:
            change_id = f"{contract_id}:{report.get('analysis_id', 'summary')}"
            field_path = str(report.get("field_path") or report.get("affected_field") or "") or None
            ranked.append(
                RankedSchemaChange(
                    change_id=change_id,
                    compatibility_verdict=verdict,
                    impact_scope=impact_scope,
                    detected_at=str(report.get("detected_at") or ""),
                    affected_interface=contract_id,
                    source_artifact_path=report_path,
                    field_path=field_path,
                    contract_clause_id=field_path or change_id,
                    priority_tuple=[1 if breaking else 0, IMPACT_RANK.get(impact_scope, 0), str(report.get("detected_at") or ""), change_id],
                    evidence=[
                        EvidenceReference(
                            artifact_path=report_path,
                            record_selector=change_id,
                            claim_type="schema_change",
                        )
                    ],
                )
            )
            continue

        for idx, diff in enumerate(diffs):
            field_path = str(diff.get("path") or diff.get("field_path") or f"diff_{idx}")
            change_id = f"{contract_id}:{field_path}"
            ranked.append(
                RankedSchemaChange(
                    change_id=change_id,
                    compatibility_verdict=verdict,
                    impact_scope=impact_scope,
                    detected_at=str(report.get("detected_at") or ""),
                    affected_interface=contract_id,
                    source_artifact_path=report_path,
                    field_path=field_path,
                    contract_clause_id=str(diff.get("clause_id") or field_path),
                    priority_tuple=[1 if breaking else 0, IMPACT_RANK.get(impact_scope, 0), str(report.get("detected_at") or ""), change_id],
                    evidence=[
                        EvidenceReference(
                            artifact_path=report_path,
                            record_selector=field_path,
                            claim_type="schema_change",
                        )
                    ],
                )
            )

    ranked.sort(
        key=lambda item: (
            -int(item.priority_tuple[0]),
            -int(item.priority_tuple[1]),
            -(parse_timestamp(item.detected_at).timestamp() if parse_timestamp(item.detected_at) else 0.0),
            item.change_id,
        )
    )
    return ranked[:limit]


def summarize_violations(violations: list[dict[str, Any]]) -> tuple[dict[str, int], dict[str, int], dict[str, int]]:
    by_severity: dict[str, int] = defaultdict(int)
    by_category: dict[str, int] = defaultdict(int)
    by_surface: dict[str, int] = defaultdict(int)

    for row in violations:
        by_severity[str(row.get("severity", "unknown")).lower()] += 1
        by_category[str(row.get("check_type") or row.get("category") or "unknown")] += 1
        by_surface[str(row.get("dataset_id") or row.get("surface_id") or row.get("contract_id") or "unknown")] += 1

    return dict(sorted(by_severity.items())), dict(sorted(by_category.items())), dict(sorted(by_surface.items()))
