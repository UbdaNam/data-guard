"""Git enrichment utilities for attribution candidates."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

from src.models.attribution_models import CommitEvidence, LineageNode, SchemaAnchor

REPO_ROOT = Path(__file__).resolve().parents[2]


@dataclass(slots=True)
class GitCandidateWindow:
    days: int = 90
    max_commits: int = 200


def _run_git(args: list[str], repo_root: Path = REPO_ROOT) -> str:
    completed = subprocess.run(["git", *args], cwd=repo_root, check=False, capture_output=True, text=True)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or completed.stdout.strip() or "git command failed")
    return completed.stdout.strip()


def _candidate_paths(anchor: SchemaAnchor, additional_paths: list[str] | None = None) -> list[str]:
    paths = list(additional_paths or [])
    if anchor.canonical_path:
        paths.append(anchor.canonical_path)
    if anchor.dataset_id:
        stem = anchor.dataset_id.replace(".", "_")
        paths.append(f"generated_contracts/{stem}.yaml")
        paths.append(f"generated_contracts/{stem}_dbt.yml")
    if anchor.interface_id:
        paths.append("contracts/interface_registry.yaml")
    if anchor.ownership_id:
        paths.append("contracts/schema_ownership_map.yaml")
    return sorted(dict.fromkeys(path for path in paths if path))


def collect_commit_evidence(anchor: SchemaAnchor, candidate_paths: list[str] | None = None, window: GitCandidateWindow | None = None) -> tuple[list[CommitEvidence], list[str]]:
    window = window or GitCandidateWindow()
    since = (datetime.now(UTC) - timedelta(days=window.days)).isoformat()
    evidence: list[CommitEvidence] = []
    warnings: list[str] = []
    for path in _candidate_paths(anchor, candidate_paths):
        try:
            output = _run_git(["log", f"--since={since}", f"--max-count={window.max_commits}", "--pretty=format:%H%x1f%an%x1f%ad%x1f%s", "--date=iso-strict", "--", path])
        except Exception as exc:
            warnings.append(f"git log unavailable for {path}: {exc}")
            continue
        for line in output.splitlines():
            if not line.strip():
                continue
            parts = line.split("\x1f")
            if len(parts) < 4:
                continue
            evidence.append(
                CommitEvidence(
                    file_path=path,
                    commit_hash=parts[0],
                    author=parts[1],
                    authored_at=parts[2],
                    commit_summary=parts[3],
                    reference_path=path,
                    blame_used=False,
                )
            )
    return evidence[: window.max_commits], warnings


def derive_source_range(anchor: SchemaAnchor, source_node: LineageNode | None = None) -> tuple[int, int] | None:
    if source_node and source_node.source_line_start and source_node.source_line_end:
        return source_node.source_line_start, source_node.source_line_end
    return None


def collect_blame(anchor: SchemaAnchor, evidence: list[CommitEvidence], source_range: tuple[int, int] | None) -> tuple[list[CommitEvidence], list[str]]:
    if not source_range or not anchor.canonical_path:
        return evidence, ["line-level blame unavailable; using file-level history"]
    try:
        start, end = source_range
        blame_output = _run_git(["blame", "-L", f"{start},{end}", "--porcelain", anchor.canonical_path])
    except Exception as exc:
        return evidence, [f"git blame unavailable: {exc}"]

    if not blame_output:
        return evidence, ["git blame returned no lines"]

    first_line = blame_output.splitlines()[0].split()
    commit_hash = first_line[0] if first_line else "unknown"
    enriched = list(evidence)
    enriched.insert(
        0,
        CommitEvidence(
            file_path=anchor.canonical_path,
            commit_hash=commit_hash,
            author="unknown",
            authored_at=datetime.now(UTC).isoformat(),
            commit_summary="line-level blame evidence",
            line_range=source_range,
            blame_used=True,
            reference_path=anchor.canonical_path,
        ),
    )
    return enriched, []
