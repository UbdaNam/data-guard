"""Metrics and trend aggregation for AI enforcement runs."""

from __future__ import annotations

from typing import Any

from src.models.ai_enforcement_models import AITrendStatus, AIMetricsReport


TREND_WINDOW = 10
TREND_EPSILON = 1e-6


def calculate_rate(failures: int, processed: int) -> float:
    return round(float(failures) / float(max(processed, 1)), 6)


def _compute_slope(values: list[float]) -> float | None:
    if len(values) < 3:
        return None
    n = len(values)
    x = list(range(n))
    mean_x = sum(x) / n
    mean_y = sum(values) / n
    numerator = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, values))
    denominator = sum((xi - mean_x) ** 2 for xi in x)
    if denominator <= 0:
        return 0.0
    return numerator / denominator


def _trend_status(slope: float | None, improving_when_negative: bool = True) -> AITrendStatus:
    if slope is None:
        return AITrendStatus.insufficient_history
    if abs(slope) < TREND_EPSILON:
        return AITrendStatus.stable
    if improving_when_negative and slope < 0:
        return AITrendStatus.improving
    if improving_when_negative and slope > 0:
        return AITrendStatus.degrading
    if not improving_when_negative and slope > 0:
        return AITrendStatus.improving
    return AITrendStatus.degrading


def merge_history(previous_metrics: dict[str, Any] | None, run_entry: dict[str, Any]) -> list[dict[str, Any]]:
    history = list((previous_metrics or {}).get("history", []))
    history.append(run_entry)
    return history[-TREND_WINDOW:]


def assemble_metrics_report(
    *,
    run_id: str,
    run_timestamp: str,
    prompt_processed: int,
    prompt_quarantined: int,
    output_processed: int,
    output_failed: int,
    trace_processed: int,
    trace_failed: int,
    drift_checks_requested: int,
    drift_checks_compared: int,
    drift_checks_insufficient: int,
    drift_detected_count: int,
    context_completeness: dict[str, Any],
    artifacts: dict[str, Any],
    previous_metrics: dict[str, Any] | None,
) -> AIMetricsReport:
    totals = {
        "prompt_processed": prompt_processed,
        "prompt_quarantined": prompt_quarantined,
        "outputs_processed": output_processed,
        "outputs_failed": output_failed,
        "traces_processed": trace_processed,
        "traces_failed": trace_failed,
        "drift_checks_requested": drift_checks_requested,
        "drift_checks_compared": drift_checks_compared,
        "drift_checks_insufficient": drift_checks_insufficient,
    }
    rates = {
        "prompt_quarantine_rate": calculate_rate(prompt_quarantined, prompt_processed),
        "output_violation_rate": calculate_rate(output_failed, output_processed),
        "trace_violation_rate": calculate_rate(trace_failed, trace_processed),
        "drift_detection_rate": calculate_rate(drift_detected_count, drift_checks_compared),
    }

    run_history_entry = {
        "run_id": run_id,
        "run_timestamp": run_timestamp,
        "rates": rates,
    }
    history = merge_history(previous_metrics, run_history_entry)

    output_rates = [float((item.get("rates") or {}).get("output_violation_rate", 0.0)) for item in history]
    slope = _compute_slope(output_rates)

    trend = {
        "window_size": TREND_WINDOW,
        "history_points_used": len(history),
        "output_violation_rate_slope": None if slope is None else round(slope, 8),
        "trend_status": _trend_status(slope).value,
    }

    return AIMetricsReport(
        run_id=run_id,
        run_timestamp=run_timestamp,
        totals=totals,
        rates=rates,
        trend=trend,
        artifacts=artifacts,
        context_completeness=context_completeness,
        history=history,
    )
