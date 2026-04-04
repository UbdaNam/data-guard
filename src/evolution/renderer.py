"""Deterministic rendering for schema evolution and migration artifacts."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from src.models.schema_evolution_models import (
    CompatibilityAssessment,
    ContextCompleteness,
    MigrationImpactReport,
    SchemaChange,
    SchemaEvolutionReport,
    Urgency,
)


def _hash_json(payload: Any) -> str:
    text = json.dumps(payload, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _utc_timestamp_slug() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H-%M-%SZ")


def build_analysis_id(contract_id: str, from_snapshot_id: str | None, to_snapshot_id: str, changes: list[SchemaChange]) -> str:
    diff_hash = _hash_json([change.model_dump(mode="json") for change in changes])[:16]
    seed = f"{contract_id}|{from_snapshot_id or 'none'}|{to_snapshot_id}|{diff_hash}"
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()[:16]


def render_evolution_report(
    contract_id: str,
    from_snapshot_id: str | None,
    to_snapshot_id: str,
    changes: list[SchemaChange],
    compatibility: CompatibilityAssessment,
    change_summary: dict[str, Any],
    warnings: list[str],
    context_completeness: str,
) -> SchemaEvolutionReport:
    analysis_id = build_analysis_id(contract_id, from_snapshot_id, to_snapshot_id, changes)
    return SchemaEvolutionReport(
        analysis_id=analysis_id,
        contract_id=contract_id,
        from_snapshot_id=from_snapshot_id,
        to_snapshot_id=to_snapshot_id,
        change_summary=change_summary,
        structured_diff=changes,
        compatibility_verdict=compatibility,
        determinism_keys={
            "sort_order": "class_then_path",
            "analysis_id_strategy": "contract+pair+diff_hash",
        },
        warnings=sorted(set(warnings)),
        context_completeness=ContextCompleteness(context_completeness),
    )


def render_migration_report(
    analysis_id: str,
    contract_id: str,
    human_diff_summary: str,
    changes: list[SchemaChange],
    compatibility: CompatibilityAssessment,
    affected_consumers: list[Any],
    migration_checklist: list[Any],
    rollback_guidance: list[str],
    urgency: str,
    confidence_change_caused_breakage: float,
    enrichment_sources: dict[str, Any],
) -> MigrationImpactReport:
    report_id = hashlib.sha256(f"{analysis_id}|migration".encode("utf-8")).hexdigest()[:16]
    return MigrationImpactReport(
        report_id=report_id,
        analysis_id=analysis_id,
        contract_id=contract_id,
        human_diff_summary=human_diff_summary,
        structured_diff=changes,
        compatibility_verdict=compatibility,
        affected_consumers=affected_consumers,
        migration_checklist=migration_checklist,
        rollback_guidance=rollback_guidance,
        urgency=Urgency(urgency),
        confidence_change_caused_breakage=confidence_change_caused_breakage,
        enrichment_sources=enrichment_sources,
    )


def write_evolution_report(report: SchemaEvolutionReport, repo_root: Path) -> Path:
    out_dir = repo_root / "validation_reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / f"schema_evolution_{report.contract_id}.json"
    target.write_text(json.dumps(report.model_dump(mode="json"), indent=2, sort_keys=True), encoding="utf-8")
    return target


def write_migration_report(report: MigrationImpactReport, repo_root: Path) -> Path:
    file_name = f"migration_impact_{report.contract_id}_{_utc_timestamp_slug()}.json"
    target = repo_root / file_name
    target.write_text(json.dumps(report.model_dump(mode="json"), indent=2, sort_keys=True), encoding="utf-8")
    return target
