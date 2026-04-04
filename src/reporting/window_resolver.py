"""Reporting window resolution utilities."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

from src.reporting.models import ReportingWindow


@dataclass(slots=True)
class WindowResolution:
    window: ReportingWindow

    def includes(self, timestamp_text: str | None) -> bool:
        if not timestamp_text:
            return True
        ts = parse_timestamp(timestamp_text)
        if ts is None:
            return True
        start = parse_timestamp(self.window.start)
        end = parse_timestamp(self.window.end)
        if start is None or end is None:
            return True
        return start <= ts <= end


def parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    text = str(value).strip()
    if not text:
        return None
    text = text.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(text).astimezone(UTC)
    except ValueError:
        return None


def _extract_timestamp(record: dict[str, Any]) -> datetime | None:
    for key in ("detected_at", "run_timestamp", "generated_at", "report_date", "event_timestamp"):
        ts = parse_timestamp(record.get(key))
        if ts is not None:
            return ts
    return None


def resolve_reporting_window(
    *,
    explicit_start: str | None,
    explicit_end: str | None,
    source_records: list[dict[str, Any]],
) -> WindowResolution:
    if explicit_start and explicit_end:
        start = parse_timestamp(explicit_start)
        end = parse_timestamp(explicit_end)
        if start and end and start <= end:
            return WindowResolution(
                window=ReportingWindow(
                    start=start.isoformat(),
                    end=end.isoformat(),
                    selection_mode="explicit",
                    resolved_from_sources=["cli_arguments"],
                )
            )

    timestamps = [ts for ts in (_extract_timestamp(row) for row in source_records) if ts is not None]
    if not timestamps:
        now = datetime.now(UTC)
        return WindowResolution(
            window=ReportingWindow(
                start=(now - timedelta(days=1)).isoformat(),
                end=now.isoformat(),
                selection_mode="latest_available",
                resolved_from_sources=["default_now"],
                resolution_notes=["No source timestamps available; used fallback 24h window."],
            )
        )

    end = max(timestamps)
    start = end - timedelta(days=7)
    return WindowResolution(
        window=ReportingWindow(
            start=start.isoformat(),
            end=end.isoformat(),
            selection_mode="latest_available",
            resolved_from_sources=["artifact_timestamps"],
        )
    )
