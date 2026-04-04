"""Generate deterministic evidence-grounded recommended actions."""

from __future__ import annotations

import hashlib
from collections import defaultdict
from typing import Any

from src.reporting.models import EvidenceReference, RecommendedAction, TopViolation


_SEVERITY_WEIGHT = {"critical": 4.0, "high": 3.0, "medium": 2.0, "low": 1.0}


def _make_action_id(issue_type: str, affected_surface: str, field_or_interface: str) -> str:
    raw = f"{issue_type}|{affected_surface}|{field_or_interface}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def _priority_score(*, severity: str, recurrence: int, recency_bonus: float, blast_radius: float) -> float:
    return round((_SEVERITY_WEIGHT.get(severity, 1.0) * 10.0) + (recurrence * 2.0) + recency_bonus + blast_radius, 2)


def generate_recommended_actions(
    *,
    top_violations: list[TopViolation],
    schema_change_count: int,
    schema_breaking_count: int,
    ai_risk: dict[str, Any] | None,
) -> list[RecommendedAction]:
    grouped: dict[tuple[str, str, str], list[RecommendedAction]] = defaultdict(list)

    for violation in top_violations:
        issue_type = "violation"
        affected_surface = violation.affected_surface
        field_or_interface = violation.affected_surface
        action_id = _make_action_id(issue_type, affected_surface, field_or_interface)
        action = RecommendedAction(
            action_id=action_id,
            issue_key={
                "issue_type": issue_type,
                "affected_surface": affected_surface,
                "field_or_interface": field_or_interface,
            },
            priority_score=_priority_score(
                severity=violation.severity,
                recurrence=violation.recurrence_count,
                recency_bonus=3.0 if violation.latest_occurrence else 0.0,
                blast_radius=2.0,
            ),
            severity=violation.severity,
            recurrence_count=violation.recurrence_count,
            latest_occurrence=violation.latest_occurrence,
            remediation_target="data_contract_or_upstream_payload",
            affected_location=affected_surface,
            owner=violation.owner,
            consumer_impact="Potential downstream contract breakage and reporting inaccuracies.",
            verification_step="Re-run validation and confirm the violation no longer appears in report_data.json top_violations.",
            aggregate_count=violation.recurrence_count,
            evidence=[
                EvidenceReference(
                    artifact_path=ref.artifact_path,
                    record_selector=ref.record_selector,
                    claim_type="action",
                )
                for ref in violation.evidence
            ],
        )
        grouped[(issue_type, affected_surface, field_or_interface)].append(action)

    if schema_change_count > 0:
        issue_type = "schema_change"
        affected_surface = "schema_evolution"
        field_or_interface = "compatibility"
        severity = "high" if schema_breaking_count > 0 else "medium"
        action_id = _make_action_id(issue_type, affected_surface, field_or_interface)
        grouped[(issue_type, affected_surface, field_or_interface)].append(
            RecommendedAction(
                action_id=action_id,
                issue_key={
                    "issue_type": issue_type,
                    "affected_surface": affected_surface,
                    "field_or_interface": field_or_interface,
                },
                priority_score=_priority_score(
                    severity=severity,
                    recurrence=max(schema_change_count, 1),
                    recency_bonus=2.0,
                    blast_radius=2.0,
                ),
                severity=severity,
                recurrence_count=max(schema_change_count, 1),
                latest_occurrence=None,
                remediation_target="schema_migration_plan",
                affected_location="validation_reports/schema_evolution_*.json",
                owner="unassigned",
                consumer_impact="Schema incompatibilities can disrupt downstream consumers.",
                verification_step="Confirm compatibility verdict improves and run summary reports no new breaking changes.",
                aggregate_count=max(schema_change_count, 1),
                evidence=[
                    EvidenceReference(
                        artifact_path="validation_reports/schema_evolution_*.json",
                        record_selector="compatibility_verdict",
                        claim_type="action",
                    )
                ],
            )
        )

    if isinstance(ai_risk, dict):
        quarantine_rate = float(ai_risk.get("quarantine_rate") or 0.0)
        if quarantine_rate > 0.0:
            issue_type = "ai_risk"
            affected_surface = "ai_metrics"
            field_or_interface = "prompt_quarantine_rate"
            action_id = _make_action_id(issue_type, affected_surface, field_or_interface)
            grouped[(issue_type, affected_surface, field_or_interface)].append(
                RecommendedAction(
                    action_id=action_id,
                    issue_key={
                        "issue_type": issue_type,
                        "affected_surface": affected_surface,
                        "field_or_interface": field_or_interface,
                    },
                    priority_score=_priority_score(
                        severity="high" if quarantine_rate >= 0.2 else "medium",
                        recurrence=1,
                        recency_bonus=1.0,
                        blast_radius=1.5,
                    ),
                    severity="high" if quarantine_rate >= 0.2 else "medium",
                    recurrence_count=1,
                    latest_occurrence=str(ai_risk.get("run_timestamp") or ""),
                    remediation_target="prompt_input_quality_controls",
                    affected_location="validation_reports/ai_metrics.json",
                    owner="unassigned",
                    consumer_impact="Elevated AI quarantine rates can reduce reliable downstream outputs.",
                    verification_step="Reduce quarantine rate and confirm trend improves in ai_metrics history.",
                    aggregate_count=1,
                    evidence=[
                        EvidenceReference(
                            artifact_path=str(ai_risk.get("_artifact_path", "validation_reports/ai_metrics.json")),
                            record_selector="rates.prompt_quarantine_rate",
                            claim_type="action",
                        )
                    ],
                )
            )

    consolidated: list[RecommendedAction] = []
    for key, actions in grouped.items():
        base = actions[0]
        base.aggregate_count = sum(item.aggregate_count for item in actions)
        base.recurrence_count = max(item.recurrence_count for item in actions)
        base.evidence = [ref for item in actions for ref in item.evidence]
        consolidated.append(base)

    consolidated.sort(
        key=lambda item: (
            -item.priority_score,
            -_SEVERITY_WEIGHT.get(item.severity, 1.0),
            -item.recurrence_count,
            item.latest_occurrence or "",
            item.action_id,
        )
    )
    return consolidated
