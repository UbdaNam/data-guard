"""AI contract enforcement entry point for Feature 6."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.ai_enforcement.pipeline import run_ai_enforcement


REPO_ROOT = Path(__file__).resolve().parents[1]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AI-specific contract enforcement")
    parser.add_argument("--week2-path", default="outputs/week2/verdicts.jsonl")
    parser.add_argument("--week3-path", default="outputs/week3/extractions.jsonl")
    parser.add_argument("--trace-path", default="outputs/traces/runs.jsonl")
    parser.add_argument("--contracts-dir", default="generated_contracts")
    parser.add_argument("--feature1-metadata-root", default="contracts")
    parser.add_argument("--snapshot-root", default="schema_snapshots")
    parser.add_argument("--validation-report-path", default="validation_reports/ai_metrics.json")
    parser.add_argument("--violation-log-path", default="violation_log/ai_violations.jsonl")
    parser.add_argument("--quarantine-dir", default="outputs/quarantine")
    parser.add_argument("--surface-id", default="week3_prompt_text")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    result = run_ai_enforcement(
        repo_root=REPO_ROOT,
        week2_path=args.week2_path,
        week3_path=args.week3_path,
        trace_path=args.trace_path,
        snapshot_root=args.snapshot_root,
        validation_report_path=args.validation_report_path,
        violation_log_path=args.violation_log_path,
        quarantine_dir=args.quarantine_dir,
        surface_id=args.surface_id,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("run", {}).get("status") != "failed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
