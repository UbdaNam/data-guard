"""Dataset readiness validation helpers for the foundation feature."""

from __future__ import annotations

from collections.abc import Iterable

from src.models.readiness_models import ArtifactStatus, DatasetReadinessEntry


def validate_dataset_readiness(
    datasets: Iterable[DatasetReadinessEntry],
) -> dict[str, list[str]]:
    readiness_gaps: list[str] = []
    mismatch_flags: list[str] = []

    for dataset in datasets:
        if dataset.readiness_status in {
            ArtifactStatus.blocked_by_missing_upstream_data,
            ArtifactStatus.pending_migration_or_normalization,
        }:
            readiness_gaps.append(dataset.dataset_id)
        if dataset.mismatch_refs:
            mismatch_flags.append(dataset.dataset_id)

    return {"readiness_gaps": readiness_gaps, "mismatch_flags": mismatch_flags}
