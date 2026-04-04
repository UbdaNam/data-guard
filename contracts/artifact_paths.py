"""Canonical artifact path helpers for the Data Guard workspace."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

GOVERNANCE_DIR = REPO_ROOT / "docs" / "governance"
SUBSCRIPTIONS_REGISTRY_PATH = GOVERNANCE_DIR / "subscriptions_registry.yaml"

GENERATED_CONTRACTS_DIR = REPO_ROOT / "generated_contracts"
VALIDATION_REPORTS_DIR = REPO_ROOT / "validation_reports"
VIOLATION_LOG_DIR = REPO_ROOT / "violation_log"
SCHEMA_SNAPSHOTS_DIR = REPO_ROOT / "schema_snapshots"
AI_SCHEMA_SNAPSHOTS_DIR = SCHEMA_SNAPSHOTS_DIR / "ai"
WEEK4_LINEAGE_SNAPSHOT_PATH = REPO_ROOT / "outputs" / "week4" / "lineage_snapshots.jsonl"

NUMERIC_BASELINES_PATH = SCHEMA_SNAPSHOTS_DIR / "baselines.json"
