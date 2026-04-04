"""Deterministic markdown rendering for operational report output."""

from __future__ import annotations

from src.reporting.models import OperationalReportData


SECTION_ORDER = [
    "Data Health Score",
    "Violations this period",
    "Schema changes detected",
    "AI system risk assessment",
    "Recommended actions",
    "Evidence traceability notes",
]


def build_fallback_narratives(report: OperationalReportData) -> dict[str, str]:
    score = report.data_health_score.value
    score_text = "insufficient evidence" if score is None else f"{score:.1f}/100"
    formula = "(checks_passed / total_checks × 100) - (20 × critical_violation_count)"

    return {
        "Data Health Score": (
            f"Computed Data Health Score is {score_text}. "
            f"Status: {report.data_health_score.score_status}. "
            f"Formula: {formula}."
        ),
        "Violations this period": (
            f"Detected {report.violations_summary.total} violation records in the reporting window."
        ),
        "Schema changes detected": (
            f"Detected {report.schema_changes_summary.total_changes} schema change items, "
            f"including {report.schema_changes_summary.breaking_changes} breaking findings."
        ),
        "AI system risk assessment": (
            f"AI trend status: {report.ai_risk_summary.trend_status}. "
            f"Prompt quarantine rate: {report.ai_risk_summary.quarantine_rate}."
        ),
        "Recommended actions": (
            f"Generated {len(report.recommended_actions)} prioritized remediation actions."
        ),
    }


def render_markdown(
    *,
    report: OperationalReportData,
    narratives: dict[str, str] | None = None,
) -> str:
    narratives = narratives or build_fallback_narratives(report)

    lines: list[str] = []
    lines.append("# Operational Report")
    lines.append("")
    lines.append(f"- Report ID: {report.report_id}")
    lines.append(f"- Report Date: {report.report_date}")
    lines.append(f"- Reporting Window: {report.reporting_window.start} to {report.reporting_window.end}")
    lines.append("")

    # 1) Data Health Score
    lines.append("## Data Health Score")
    lines.append("")
    lines.append(narratives.get("Data Health Score", ""))
    lines.append("")
    lines.append(f"- Value: {report.data_health_score.value}")
    lines.append(f"- Status: {report.data_health_score.score_status}")
    lines.append(f"- Formula: (checks_passed / total_checks × 100) - (20 × critical_violation_count)")
    lines.append(f"- Checks passed: {report.data_health_score.checks_passed}")
    lines.append(f"- Total checks: {report.data_health_score.total_checks}")
    lines.append(f"- Critical violations: {report.data_health_score.critical_violation_count}")
    lines.append(f"- Check penalty: {report.data_health_score.check_penalty}")
    lines.append(f"- Critical penalty: {report.data_health_score.critical_penalty}")
    lines.append(f"- Raw score: {report.data_health_score.raw_score}")
    if report.data_health_score.reason:
        lines.append(f"- Reason: {report.data_health_score.reason}")
    lines.append("")

    # 2) Violations this period
    lines.append("## Violations this period")
    lines.append("")
    lines.append(narratives.get("Violations this period", ""))
    lines.append("")
    lines.append(f"- Total: {report.violations_summary.total}")
    for violation in report.top_violations:
        lines.append(
            f"- Rank {violation.rank}: {violation.violation_id} "
            f"(severity={violation.severity}, recurrence={violation.recurrence_count}, owner={violation.owner})"
        )
    lines.append("")

    # 3) Schema changes detected
    lines.append("## Schema changes detected")
    lines.append("")
    lines.append(narratives.get("Schema changes detected", ""))
    lines.append("")
    lines.append(f"- Total changes: {report.schema_changes_summary.total_changes}")
    lines.append(f"- Breaking changes: {report.schema_changes_summary.breaking_changes}")
    lines.append(f"- Non-breaking changes: {report.schema_changes_summary.non_breaking_changes}")
    lines.append("")

    # 4) AI system risk assessment
    lines.append("## AI system risk assessment")
    lines.append("")
    lines.append(narratives.get("AI system risk assessment", ""))
    lines.append("")
    lines.append(f"- Trend status: {report.ai_risk_summary.trend_status}")
    lines.append(f"- Prompt quarantine rate: {report.ai_risk_summary.quarantine_rate}")
    lines.append(f"- Output violation rate: {report.ai_risk_summary.output_violation_rate}")
    lines.append(f"- Trace violation rate: {report.ai_risk_summary.trace_violation_rate}")
    lines.append("")

    # 5) Recommended actions
    lines.append("## Recommended actions")
    lines.append("")
    lines.append(narratives.get("Recommended actions", ""))
    lines.append("")
    for action in report.recommended_actions:
        lines.append(
            f"- [{action.action_id}] priority={action.priority_score} "
            f"target={action.remediation_target} location={action.affected_location} "
            f"owner={action.owner} verify={action.verification_step}"
        )
        if action.source_artifact_path or action.field_path or action.contract_clause_id:
            lines.append(
                f"  - references: file={action.source_artifact_path or 'n/a'} field={action.field_path or 'n/a'} clause={action.contract_clause_id or 'n/a'}"
            )
    lines.append("")

    # 6) Evidence traceability notes
    lines.append("## Evidence traceability notes")
    lines.append("")
    for evidence in report.evidence_index:
        lines.append(
            f"- {evidence.claim_type}: {evidence.artifact_path} :: {evidence.record_selector}"
        )
    lines.append("")

    return "\n".join(lines)
