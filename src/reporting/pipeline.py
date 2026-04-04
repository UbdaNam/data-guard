"""Operational report generation orchestration pipeline."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from src.reporting.action_generator import generate_recommended_actions
from src.reporting.artifact_loader import load_artifacts
from src.reporting.env_config import load_enrichment_config
from src.reporting.json_renderer import write_report_json
from src.reporting.llm_enrichment import maybe_enrich_narratives
from src.reporting.markdown_renderer import build_fallback_narratives, render_markdown
from src.reporting.models import GenerationEnrichment
from src.reporting.report_builder import build_report_data
from src.reporting.window_resolver import resolve_reporting_window


def _resolve_output_paths(output_dir: Path, report_date: str) -> tuple[Path, Path]:
    json_path = output_dir / "report_data.json"
    markdown_path = output_dir / f"report_{report_date}.md"
    return json_path, markdown_path


def run_report_generation(
    *,
    repo_root: Path,
    report_start: str | None,
    report_end: str | None,
    enable_llm_enrichment: bool,
    output_dir: str,
    validation_reports_glob: str,
    violation_log_path: str,
    schema_evolution_glob: str,
    ai_metrics_path: str,
    ownership_map_path: str,
    interface_registry_path: str,
) -> dict[str, Any]:
    started = datetime.now(UTC)

    loaded = load_artifacts(
        repo_root=repo_root,
        validation_reports_glob=validation_reports_glob,
        violation_log_path=violation_log_path,
        schema_evolution_glob=schema_evolution_glob,
        ai_metrics_path=ai_metrics_path,
        ownership_map_path=ownership_map_path,
        interface_registry_path=interface_registry_path,
    )

    source_records = [*loaded.validation_reports, *loaded.violations, *loaded.schema_evolution_reports]
    if loaded.ai_metrics:
        source_records.append(loaded.ai_metrics)
    window = resolve_reporting_window(
        explicit_start=report_start,
        explicit_end=report_end,
        source_records=source_records,
    )

    ai_rates = (loaded.ai_metrics or {}).get("rates") if isinstance((loaded.ai_metrics or {}).get("rates"), dict) else {}
    recommended_actions = generate_recommended_actions(
        top_violations=[],  # set later after report assembly
        schema_change_count=len(loaded.schema_evolution_reports),
        schema_breaking_count=0,
        ai_risk={
            "quarantine_rate": ai_rates.get("prompt_quarantine_rate"),
            "run_timestamp": (loaded.ai_metrics or {}).get("run_timestamp"),
            "_artifact_path": (loaded.ai_metrics or {}).get("_artifact_path"),
        }
        if loaded.ai_metrics
        else None,
    )

    elapsed_ms = int((datetime.now(UTC) - started).total_seconds() * 1000)
    report = build_report_data(
        loaded=loaded,
        window=window,
        recommended_actions=recommended_actions,
        enrichment=GenerationEnrichment(requested=enable_llm_enrichment),
        duration_ms=elapsed_ms,
    )

    # Rebuild actions from ranked violations now that top violations are available.
    recommended_actions = generate_recommended_actions(
        top_violations=report.top_violations,
        schema_change_count=report.schema_changes_summary.total_changes,
        schema_breaking_count=report.schema_changes_summary.breaking_changes,
        ai_risk=(loaded.ai_metrics or {}),
    )
    report.recommended_actions = recommended_actions

    fallback = build_fallback_narratives(report)
    config = load_enrichment_config()
    enrichment_result = maybe_enrich_narratives(
        enabled=enable_llm_enrichment,
        config=config,
        fallback_narratives=fallback,
    )
    report.generation_metadata.enrichment = GenerationEnrichment(
        requested=enable_llm_enrichment,
        provider="openrouter" if enable_llm_enrichment else "none",
        status=enrichment_result.status if enrichment_result.status in {"disabled", "missing_config", "failed", "applied"} else "failed",
        fallback_used=enrichment_result.fallback_used,
    )

    final_elapsed_ms = int((datetime.now(UTC) - started).total_seconds() * 1000)
    report.generation_metadata.duration_ms = final_elapsed_ms

    output_root = repo_root / output_dir
    output_root.mkdir(parents=True, exist_ok=True)
    json_path, markdown_path = _resolve_output_paths(output_root, report.report_date)

    payload = write_report_json(report, json_path)
    markdown_text = render_markdown(report=report, narratives=enrichment_result.narratives)
    markdown_path.write_text(markdown_text, encoding="utf-8")

    return {
        "status": "completed",
        "report_id": report.report_id,
        "report_date": report.report_date,
        "report_data_path": json_path.as_posix(),
        "report_markdown_path": markdown_path.as_posix(),
        "enrichment": report.generation_metadata.enrichment.model_dump(mode="json"),
        "summary": {
            "data_health_score": report.data_health_score.model_dump(mode="json"),
            "top_violations_count": len(report.top_violations),
            "recommended_actions_count": len(report.recommended_actions),
            "schema_changes_count": report.schema_changes_summary.total_changes,
        },
        "section_completeness": {
            key: value.model_dump(mode="json")
            for key, value in report.section_completeness.items()
        },
        "report_data": payload,
    }


def run_report_generation_json(**kwargs: Any) -> str:
    return json.dumps(run_report_generation(**kwargs), indent=2, ensure_ascii=False)
