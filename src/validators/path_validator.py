"""Canonical path validation helpers for the foundation feature."""

from __future__ import annotations

from pathlib import PurePosixPath
from typing import Iterable

from src.models.readiness_models import CanonicalPathEntry


def normalize_path(value: str) -> str:
    """Normalize a repository-relative path for deterministic comparison."""

    return PurePosixPath(value).as_posix().lstrip("./")


def validate_canonical_paths(
    expected_paths: Iterable[str],
    inventory: Iterable[CanonicalPathEntry],
) -> dict[str, list[str]]:
    expected = {normalize_path(path) for path in expected_paths}
    observed = {normalize_path(entry.path) for entry in inventory}
    missing = sorted(expected - observed)
    unexpected = sorted(observed - expected)
    return {"missing": missing, "unexpected": unexpected}
