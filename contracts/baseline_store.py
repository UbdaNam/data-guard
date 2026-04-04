"""Workspace-level baseline store helpers."""

from __future__ import annotations

from pathlib import Path

from src.validation.baseline_store import BaselineStore as _BaselineStore


def build_baseline_store(repo_root: Path | None = None) -> _BaselineStore:
    return _BaselineStore(repo_root or Path(__file__).resolve().parents[1])


BaselineStore = _BaselineStore
