"""Violation attribution entry point."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.attribution.pipeline import run_attribution

REPO_ROOT = Path(__file__).resolve().parents[1]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Violation attribution engine")
    parser.add_argument("--validate", action="store_true", help="Unsupported: validation execution is out of scope")
    parser.add_argument("--schema-evolution", action="store_true", help="Unsupported: schema evolution classification is out of scope")
    parser.add_argument("--ai-checks", action="store_true", help="Unsupported: AI-specific checks are out of scope")
    parser.add_argument("--report", action="store_true", help="Unsupported: stakeholder reporting is out of scope")
    parser.add_argument("--reports", nargs="*", help="Validation report paths or report ids to process")
    parser.add_argument("--report-dir", default="validation_reports", help="Directory containing validation reports")
    parser.add_argument("--output", default="violation_log/violations.jsonl", help="Violation log output path")
    parser.add_argument("--dry-run", action="store_true", help="Run attribution without writing output")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite duplicate suppression for this run")
    parser.add_argument("--max-hops", type=int, default=6, help="Maximum lineage hops to traverse")
    parser.add_argument("--max-candidates", type=int, default=5, help="Maximum blame candidates per violation")
    parser.add_argument("--git-window-days", type=int, default=90, help="Recent git history window")
    parser.add_argument("--git-commit-cap", type=int, default=200, help="Per-file git commit cap")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    unsupported = [
        flag
        for flag, enabled in {
            "validate": args.validate,
            "schema-evolution": args.schema_evolution,
            "ai-checks": args.ai_checks,
            "report": args.report,
        }.items()
        if enabled
    ]
    if unsupported:
        parser.error(f"Unsupported modes are out of scope for Feature 4: {', '.join(unsupported)}")
    result = run_attribution(
        report_paths=args.reports,
        report_dir=args.report_dir,
        output_path=args.output,
        dry_run=args.dry_run,
        overwrite=args.overwrite,
        max_hops=args.max_hops,
        max_candidates=args.max_candidates,
        git_window_days=args.git_window_days,
        git_commit_cap=args.git_commit_cap,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
