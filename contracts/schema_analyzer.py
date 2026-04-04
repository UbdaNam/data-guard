"""Schema evolution analysis entry point for Feature 5."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from src.evolution.pipeline import run_schema_evolution
from src.generation.profilers import profile_records
from src.generation.schema_inference import infer_schema_map


REPO_ROOT = Path(__file__).resolve().parents[1]


def analyze_dataset_schema(records: list[dict[str, Any]]) -> dict[str, dict[str, str | None]]:
    """Profile records and produce a nested schema map for generator orchestration."""

    profiled = profile_records(records)
    return infer_schema_map(profiled)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Schema evolution intelligence")
    parser.add_argument("--snapshot", action="store_true", help="Write schema snapshot only (no diff/classification)")
    parser.add_argument("--contracts", nargs="*", help="Contract YAML paths to analyze (defaults to generated_contracts/*.yaml)")
    parser.add_argument("--from-snapshot-id", help="Explicit source snapshot id for comparison")
    parser.add_argument("--to-snapshot-id", help="Explicit target snapshot id for comparison")
    parser.add_argument("--validate", action="store_true", help="Unsupported: validation execution is out of scope")
    parser.add_argument("--attribution", action="store_true", help="Unsupported: git-blame attribution is out of scope")
    parser.add_argument("--report", action="store_true", help="Unsupported: final stakeholder reporting is out of scope")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    unsupported = [
        name
        for name, enabled in {
            "validate": args.validate,
            "attribution": args.attribution,
            "report": args.report,
        }.items()
        if enabled
    ]
    if unsupported:
        parser.error(f"Unsupported modes are out of scope for Feature 5: {', '.join(unsupported)}")

    result = run_schema_evolution(
        repo_root=REPO_ROOT,
        contract_paths=args.contracts,
        snapshot_only=args.snapshot,
        from_snapshot_id=args.from_snapshot_id,
        to_snapshot_id=args.to_snapshot_id,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not result.get("failed_contracts") else 1


if __name__ == "__main__":
    raise SystemExit(main())
