"""Data Health Score computation (FR-032 / FR-033)."""

from __future__ import annotations

from typing import Any

from src.reporting.models import DataHealthScore


def compute_data_health_score(
    *,
    validation_reports: list[dict[str, Any]],
    critical_violation_count: int,
) -> DataHealthScore:
    if not validation_reports:
        return DataHealthScore(
            value=None,
            score_status="insufficient_evidence",
            check_penalty=None,
            critical_penalty=None,
            raw_score=None,
            checks_passed=None,
            total_checks=None,
            critical_violation_count=critical_violation_count,
            reason="No validation runs found in reporting window.",
        )

    passed = 0
    failed = 0
    errored = 0
    total_checks = 0

    for report in validation_reports:
        passed += int(report.get("passed", 0) or 0)
        failed += int(report.get("failed", 0) or 0)
        errored += int(report.get("errored", 0) or 0)
        if isinstance(report.get("results"), list):
            total_checks += len(report["results"])
        else:
            total_checks += int(report.get("passed", 0) or 0) + int(report.get("failed", 0) or 0) + int(report.get("errored", 0) or 0) + int(report.get("warned", 0) or 0)

    if total_checks <= 0:
        return DataHealthScore(
            value=None,
            score_status="insufficient_evidence",
            check_penalty=None,
            critical_penalty=None,
            raw_score=None,
            checks_passed=None,
            total_checks=None,
            critical_violation_count=critical_violation_count,
            reason="Validation reports contain no check results.",
        )

    checks_passed = max(0, total_checks - failed - errored)
    pass_rate = (checks_passed / max(total_checks, 1)) * 100.0
    check_penalty = 100.0 - pass_rate
    critical_penalty = 20.0 * critical_violation_count
    raw_score = pass_rate - critical_penalty
    score = max(0.0, min(100.0, raw_score))

    return DataHealthScore(
        value=round(score, 1),
        score_status="computed",
        check_penalty=round(check_penalty, 3),
        critical_penalty=round(critical_penalty, 3),
        raw_score=round(raw_score, 3),
        checks_passed=checks_passed,
        total_checks=total_checks,
        critical_violation_count=critical_violation_count,
        reason=None,
    )
