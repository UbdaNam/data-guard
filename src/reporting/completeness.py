"""Section completeness utilities."""

from __future__ import annotations

from src.reporting.models import SectionCompletenessRecord


def complete() -> SectionCompletenessRecord:
    return SectionCompletenessRecord(status="complete")


def partial(*, missing_sources: list[str], reason: str) -> SectionCompletenessRecord:
    return SectionCompletenessRecord(
        status="partial",
        missing_sources=sorted(set(missing_sources)),
        reason=reason,
    )


def insufficient(*, missing_sources: list[str], reason: str) -> SectionCompletenessRecord:
    return SectionCompletenessRecord(
        status="insufficient_evidence",
        missing_sources=sorted(set(missing_sources)),
        reason=reason,
    )


def status_from_presence(
    *,
    records_count: int,
    missing_sources: list[str],
    empty_reason: str,
) -> SectionCompletenessRecord:
    if records_count > 0 and not missing_sources:
        return complete()
    if records_count > 0 and missing_sources:
        return partial(missing_sources=missing_sources, reason=empty_reason)
    return insufficient(missing_sources=missing_sources, reason=empty_reason)
