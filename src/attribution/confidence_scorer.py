"""Confidence scoring for attribution candidates."""

from __future__ import annotations

from datetime import datetime, timezone

from src.models.attribution_models import BlameCandidate, ConfidenceBand, LineageCompleteness, LineagePathEvidence


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def score_candidate(
    candidate: BlameCandidate,
    lineage: LineagePathEvidence | None = None,
    commit_time: str | None = None,
    max_hops: int = 6,
    directness: str = "dataset",
    blame_available: bool = False,
) -> float:
    recency = 0.4
    if commit_time:
        try:
            authored_at = datetime.fromisoformat(commit_time.replace("Z", "+00:00"))
            age_days = max((datetime.now(timezone.utc) - authored_at).days, 0)
            recency = _clamp(1.0 - min(age_days / 90.0, 1.0))
        except ValueError:
            recency = 0.4
    hop_proximity = 1.0
    if lineage is not None:
        hop_proximity = _clamp(1.0 - (lineage.hop_count / max(max_hops, 1)))
    directness_score = {
        "field": 1.0,
        "schema": 0.7,
        "dataset": 0.5,
        "inferred": 0.3,
    }.get(directness, 0.3)
    line_blame = 1.0 if blame_available else 0.4
    lineage_completeness = 0.5
    if lineage is not None:
        lineage_completeness = {
            LineageCompleteness.complete: 1.0,
            LineageCompleteness.partial: 0.5,
            LineageCompleteness.weak: 0.2,
            LineageCompleteness.missing: 0.0,
        }.get(lineage.completeness, 0.5)
    score = 100.0 * (
        0.30 * recency
        + 0.25 * hop_proximity
        + 0.20 * directness_score
        + 0.15 * line_blame
        + 0.10 * lineage_completeness
    )
    return max(0.0, min(100.0, round(score, 2)))


def confidence_band(score: float) -> ConfidenceBand:
    if score >= 75:
        return ConfidenceBand.high
    if score >= 50:
        return ConfidenceBand.medium
    return ConfidenceBand.low
