"""Confidence scoring for attribution candidates."""

from __future__ import annotations

from datetime import datetime, timezone

from src.models.attribution_models import BlameCandidate, ConfidenceBand, LineageCompleteness, LineagePathEvidence


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def days_since_commit(commit_time: str | None) -> int:
    if not commit_time:
        return 0
    try:
        authored_at = datetime.fromisoformat(commit_time.replace("Z", "+00:00"))
    except ValueError:
        return 0
    return max((datetime.now(timezone.utc) - authored_at).days, 0)


def confidence_formula(*, days_since_commit: int, lineage_hops: int) -> float:
    return _clamp(1.0 - (days_since_commit * 0.1) - (lineage_hops * 0.2))


def score_candidate(
    candidate: BlameCandidate,
    lineage: LineagePathEvidence | None = None,
    commit_time: str | None = None,
    max_hops: int = 6,
    directness: str = "dataset",
    blame_available: bool = False,
) -> float:
    lineage_hops = lineage.hop_count if lineage is not None else 0
    confidence = confidence_formula(days_since_commit=days_since_commit(commit_time), lineage_hops=lineage_hops)
    return max(0.0, min(100.0, round(confidence * 100.0, 2)))


def confidence_band(score: float) -> ConfidenceBand:
    if score >= 75:
        return ConfidenceBand.high
    if score >= 50:
        return ConfidenceBand.medium
    return ConfidenceBand.low
