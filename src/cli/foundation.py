"""Foundation CLI for canonical path and readiness validation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, cast

import yaml

from src.models.readiness_models import ArtifactStatus, CanonicalPathEntry, DatasetReadinessEntry
from src.validators.path_validator import validate_canonical_paths
from src.validators.readiness_validator import validate_dataset_readiness

REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_DIR = REPO_ROOT / "contracts"


def load_json_file(path: Path) -> object:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        return json.loads(text)
    return yaml.safe_load(text)


def build_manifest() -> dict[str, object]:
    canonical_paths_file = CONTRACTS_DIR / "canonical_paths.yaml"
    dataset_readiness_file = CONTRACTS_DIR / "dataset_readiness.json"
    return {
        "repository_root": str(REPO_ROOT),
        "canonical_paths_file": str(canonical_paths_file),
        "dataset_readiness_file": str(dataset_readiness_file),
        "allowed_statuses": [status.value for status in ArtifactStatus],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Foundation validation CLI")
    parser.add_argument(
        "command",
        choices=["manifest", "validate-paths", "validate-readiness", "generate-contracts"],
    )
    args = parser.parse_args()

    if args.command == "manifest":
        print(json.dumps(build_manifest(), indent=2))
        return 0

    if args.command == "validate-paths":
        canonical_paths = cast(list[dict[str, Any]], load_json_file(CONTRACTS_DIR / "canonical_paths.yaml") or [])
        expected_paths = [item["path"] for item in canonical_paths]
        inventory = [CanonicalPathEntry.model_validate(item) for item in canonical_paths]
        print(json.dumps(validate_canonical_paths(expected_paths, inventory), indent=2))
        return 0

    if args.command == "validate-readiness":
        readiness_entries = cast(list[dict[str, Any]], load_json_file(CONTRACTS_DIR / "dataset_readiness.json") or [])
        datasets = [DatasetReadinessEntry.model_validate(item) for item in readiness_entries]
        print(json.dumps(validate_dataset_readiness(datasets), indent=2))
        return 0

    if args.command == "generate-contracts":
        from contracts.generator import run_generation

        print(json.dumps(run_generation(), indent=2))
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
