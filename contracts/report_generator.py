"""Operational report generation entry point for Feature 7."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.reporting.pipeline import run_report_generation


REPO_ROOT = Path(__file__).resolve().parents[1]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate operational report artifacts from upstream evidence.")
    parser.add_argument("--report-start", default=None, help="Optional explicit reporting window start (ISO-8601).")
    parser.add_argument("--report-end", default=None, help="Optional explicit reporting window end (ISO-8601).")
    parser.add_argument("--enable-llm-enrichment", action="store_true", help="Enable optional OpenRouter narrative enrichment.")
    parser.add_argument("--output-dir", default="enforcer_report", help="Output directory for report_data.json and markdown report.")
    parser.add_argument("--validation-reports-glob", default="validation_reports/*.json")
    parser.add_argument("--violation-log-path", default="violation_log/violations.jsonl")
    parser.add_argument("--schema-evolution-glob", default="validation_reports/schema_evolution_*.json")
    parser.add_argument("--ai-metrics-path", default="validation_reports/ai_metrics.json")
    parser.add_argument("--ownership-map-path", default="contracts/schema_ownership_map.yaml")
    parser.add_argument("--interface-registry-path", default="contracts/interface_registry.yaml")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = run_report_generation(
        repo_root=REPO_ROOT,
        report_start=args.report_start,
        report_end=args.report_end,
        enable_llm_enrichment=args.enable_llm_enrichment,
        output_dir=args.output_dir,
        validation_reports_glob=args.validation_reports_glob,
        violation_log_path=args.violation_log_path,
        schema_evolution_glob=args.schema_evolution_glob,
        ai_metrics_path=args.ai_metrics_path,
        ownership_map_path=args.ownership_map_path,
        interface_registry_path=args.interface_registry_path,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result.get("status") == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
