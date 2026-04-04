"""Pipeline orchestration for Feature 5 schema evolution intelligence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from src.evolution.classifier import aggregate_compatibility, apply_change_classification
from src.evolution.context_enricher import apply_enrichment, context_completeness_from_warnings, load_optional_context
from src.evolution.differ import compute_schema_diff
from src.evolution.migration_generator import (
    assign_failure_modes,
    baseline_urgency_from_verdict,
    generate_migration_actions,
    resolve_affected_consumers,
    rollback_guidance,
)
from src.evolution.renderer import (
    render_evolution_report,
    render_migration_report,
    write_evolution_report,
    write_migration_report,
)
from src.evolution.snapshot_loader import load_pair
from src.evolution.snapshot_writer import build_snapshot, write_snapshot
from src.validators.schema_evolution_validator import validate_evolution_model, validate_migration_model


def _load_contract(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Invalid contract payload: {path.as_posix()}")
    return payload


def _human_diff_summary(contract_id: str, summary: dict[str, Any], verdict: str) -> str:
    return (
        f"Schema evolution for {contract_id}: total={summary.get('total_changes', 0)}, "
        f"added={summary.get('added', 0)}, removed={summary.get('removed', 0)}, "
        f"renamed={summary.get('renamed', 0)}, modified={summary.get('modified', 0)}, verdict={verdict}."
    )


def analyze_contract(
    contract_path: Path,
    repo_root: Path,
    snapshot_only: bool = False,
    from_snapshot_id: str | None = None,
    to_snapshot_id: str | None = None,
) -> dict[str, Any]:
    payload = _load_contract(contract_path)
    snapshot_root = repo_root / "schema_snapshots"
    snapshot_root.mkdir(parents=True, exist_ok=True)

    snapshot = build_snapshot(payload, contract_path)
    snapshot_result = write_snapshot(snapshot, snapshot_root)

    if snapshot_only:
        return {
            "contract_id": snapshot.contract_id,
            "mode": "snapshot_only",
            "snapshot": snapshot_result,
            "warnings": [],
        }

    from_snapshot, to_snapshot, warnings = load_pair(
        snapshot_root,
        contract_id=snapshot.contract_id,
        from_snapshot_id=from_snapshot_id,
        to_snapshot_id=to_snapshot_id,
    )

    if to_snapshot is None:
        return {
            "contract_id": snapshot.contract_id,
            "mode": "baseline_established",
            "snapshot": snapshot_result,
            "warnings": sorted(set(warnings + ["no_valid_snapshot_pair"])),
        }

    if from_snapshot is None:
        compatibility = aggregate_compatibility([], baseline=True)
        evolution = render_evolution_report(
            contract_id=snapshot.contract_id,
            from_snapshot_id=None,
            to_snapshot_id=to_snapshot.snapshot_id,
            changes=[],
            compatibility=compatibility,
            change_summary={},
            warnings=warnings + ["no_prior_snapshot"],
            context_completeness="minimal",
        )
        validate_evolution_model(evolution)
        evolution_path = write_evolution_report(evolution, repo_root)
        return {
            "contract_id": snapshot.contract_id,
            "mode": "baseline_established",
            "snapshot": snapshot_result,
            "evolution_report": evolution_path.as_posix(),
            "warnings": evolution.warnings,
        }

    changes, change_summary = compute_schema_diff(from_snapshot.fields, to_snapshot.fields)
    classified_changes = apply_change_classification(changes)
    compatibility = aggregate_compatibility(classified_changes)

    enrichment, enrichment_warnings = load_optional_context(repo_root, snapshot.contract_id)
    all_warnings = sorted(set(warnings + enrichment_warnings))
    completeness = context_completeness_from_warnings(all_warnings)

    evolution = render_evolution_report(
        contract_id=snapshot.contract_id,
        from_snapshot_id=from_snapshot.snapshot_id,
        to_snapshot_id=to_snapshot.snapshot_id,
        changes=classified_changes,
        compatibility=compatibility,
        change_summary=change_summary,
        warnings=all_warnings,
        context_completeness=completeness,
    )
    validate_evolution_model(evolution)
    evolution_path = write_evolution_report(evolution, repo_root)

    affected_consumers = assign_failure_modes(resolve_affected_consumers(repo_root, payload), classified_changes)
    actions = generate_migration_actions(classified_changes)
    base_urgency = baseline_urgency_from_verdict(compatibility.verdict).value
    adjusted_urgency, confidence = apply_enrichment(base_urgency, enrichment)
    rollback = rollback_guidance(classified_changes, compatibility.verdict)

    migration = render_migration_report(
        analysis_id=evolution.analysis_id,
        contract_id=snapshot.contract_id,
        human_diff_summary=_human_diff_summary(snapshot.contract_id, change_summary, compatibility.verdict.value),
        changes=classified_changes,
        compatibility=compatibility,
        affected_consumers=affected_consumers,
        migration_checklist=actions,
        rollback_guidance=rollback,
        urgency=adjusted_urgency,
        confidence_change_caused_breakage=confidence,
        enrichment_sources=enrichment,
    )
    validate_migration_model(migration)
    migration_path = write_migration_report(migration, repo_root)

    return {
        "contract_id": snapshot.contract_id,
        "mode": "analysis",
        "snapshot": snapshot_result,
        "change_summary": change_summary,
        "compatibility_verdict": compatibility.model_dump(mode="json"),
        "evolution_report": evolution_path.as_posix(),
        "migration_report": migration_path.as_posix(),
        "warnings": all_warnings,
    }


def run_schema_evolution(
    repo_root: Path,
    contract_paths: list[str] | None = None,
    snapshot_only: bool = False,
    from_snapshot_id: str | None = None,
    to_snapshot_id: str | None = None,
) -> dict[str, Any]:
    generated_dir = repo_root / "generated_contracts"
    selected = [Path(item) for item in contract_paths] if contract_paths else sorted(generated_dir.glob("*.yaml"))

    results: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    for path in selected:
        resolved = path if path.is_absolute() else (repo_root / path)
        if not resolved.exists():
            failures.append({"contract_path": str(path), "error": "contract_not_found"})
            continue
        try:
            results.append(
                analyze_contract(
                    resolved,
                    repo_root=repo_root,
                    snapshot_only=snapshot_only,
                    from_snapshot_id=from_snapshot_id,
                    to_snapshot_id=to_snapshot_id,
                )
            )
        except Exception as exc:
            failures.append({"contract_path": resolved.as_posix(), "error": str(exc)})

    summary = {
        "processed_contracts": len(results) + len(failures),
        "successful_contracts": len(results),
        "failed_contracts": len(failures),
        "snapshot_only": snapshot_only,
        "results": results,
        "failures": failures,
    }
    (repo_root / "validation_reports").mkdir(parents=True, exist_ok=True)
    (repo_root / "validation_reports" / "schema_evolution_run_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return summary
