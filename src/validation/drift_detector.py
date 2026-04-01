"""Numeric drift classification based on persisted baselines."""

from __future__ import annotations

from math import fabs

from src.models.validation_models import BaselineStatistic, DriftOutcome, NumericProfile, ValidationSeverity, ValidationStatus


def evaluate_drift(profile: NumericProfile, baseline: BaselineStatistic | None) -> DriftOutcome:
    if baseline is None:
        return DriftOutcome(
            column_name=profile.column_name,
            status=ValidationStatus.ERROR,
            message="Missing baseline statistic for numeric drift comparison",
            baseline=None,
            current_profile=profile,
            severity=ValidationSeverity.medium,
        )

    if baseline.stddev == 0:
        if profile.mean == baseline.mean:
            return DriftOutcome(
                column_name=profile.column_name,
                z_score=0.0,
                status=ValidationStatus.PASS,
                message="No drift detected against zero-variance baseline",
                baseline=baseline,
                current_profile=profile,
                severity=ValidationSeverity.low,
            )
        return DriftOutcome(
            column_name=profile.column_name,
            z_score=None,
            status=ValidationStatus.FAIL,
            message="Baseline standard deviation is zero and observed mean differs from baseline",
            baseline=baseline,
            current_profile=profile,
            severity=ValidationSeverity.high,
        )

    z_score = fabs(profile.mean - baseline.mean) / baseline.stddev
    if z_score > 3:
        status = ValidationStatus.FAIL
        severity = ValidationSeverity.high
        message = f"Drift threshold exceeded: z_score={z_score:.4f} > 3"
    elif z_score > 2:
        status = ValidationStatus.WARN
        severity = ValidationSeverity.medium
        message = f"Drift warning: z_score={z_score:.4f} > 2"
    else:
        status = ValidationStatus.PASS
        severity = ValidationSeverity.low
        message = f"No drift detected: z_score={z_score:.4f}"
    return DriftOutcome(
        column_name=profile.column_name,
        z_score=z_score,
        status=status,
        message=message,
        baseline=baseline,
        current_profile=profile,
        severity=severity,
    )
