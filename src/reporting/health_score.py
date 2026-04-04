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
            reason="No validation runs found in reporting window.",
        )

    warned = 0
    failed = 0
    errored = 0
    total_checks = 0

    for report in validation_reports:
        warned += int(report.get("warned", 0) or 0)
        failed += int(report.get("failed", 0) or 0)
        errored += int(report.get("errored", 0) or 0)
        if isinstance(report.get("results"), list):
            total_checks += len(report["results"])
        else:
            total_checks += int(report.get("passed", 0) or 0) + int(report.get("failed", 0) or 0) + int(report.get("errored", 0) or 0)

    if total_checks <= 0:
        return DataHealthScore(
            value=None,
            score_status="insufficient_evidence",
            check_penalty=None,
            critical_penalty=None,
            raw_score=None,
            reason="Validation reports contain no check results.",
        )

    check_penalty = (((1 * warned) + (4 * failed) + (6 * errored)) / max(total_checks, 1)) * 100
    critical_penalty = min(30.0, 8.0 * critical_violation_count)
    raw_score = 100.0 - check_penalty - critical_penalty
    score = max(0.0, min(100.0, raw_score))

    return DataHealthScore(
        value=round(score, 1),
        score_status="computed",
        check_penalty=round(check_penalty, 3),
        critical_penalty=round(critical_penalty, 3),
        raw_score=round(raw_score, 3),
        reason=None,
    )
