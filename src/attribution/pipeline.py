"""End-to-end attribution pipeline for Feature 4."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.attribution.blast_radius import compute_blast_radius
from src.attribution.confidence_scorer import confidence_band, score_candidate
from src.attribution.git_enricher import GitCandidateWindow, collect_blame, collect_commit_evidence, derive_source_range
from src.attribution.lineage_graph import build_upstream_paths
from src.attribution.lineage_selector import select_latest_snapshot
from src.attribution.result_aggregator import assemble_violation_record, build_confidence_summary, sort_candidates
from src.attribution.schema_mapper import annotate_eligibility
from src.attribution.validation_failure_loader import filter_eligible_results, load_validation_reports
from src.attribution.violation_writer import write_violation_records
from src.models.attribution_models import AttributionRunSummary, BlameCandidate, LineageCompleteness, LineageNode

REPO_ROOT = Path(__file__).resolve().parents[2]


def run_attribution(
    report_paths: list[str] | None = None,
    report_dir: str | None = None,
    output_path: str | None = None,
    dry_run: bool = False,
    overwrite: bool = False,
    max_hops: int = 6,
    max_candidates: int = 5,
    git_window_days: int = 90,
    git_commit_cap: int = 200,
) -> dict[str, Any]:
    resolved_report_paths = [Path(item) for item in report_paths] if report_paths else None
    loaded_reports = load_validation_reports(resolved_report_paths, Path(report_dir) if report_dir else REPO_ROOT / "validation_reports")
    latest_snapshot, snapshot_warnings = select_latest_snapshot()

    summary = AttributionRunSummary(output_path=output_path)
    summary.report_paths = [path.as_posix() for path, report, _ in loaded_reports if report is not None]
    summary.processed_reports = len(loaded_reports)

    records = []
    skipped: list[dict[str, Any]] = []
    window = GitCandidateWindow(days=git_window_days, max_commits=git_commit_cap)

    for source_path, report, parse_issues in loaded_reports:
        if report is None:
            skipped.append(
                {
                    "report_id": source_path.stem,
                    "skip_reason": "malformed_report",
                    "message": "; ".join(parse_issues),
                }
            )
            continue
        eligible, report_skips = filter_eligible_results(report, source_path)
        summary.eligible_results += len(eligible)
        summary.skipped_results += len(report_skips)
        skipped.extend([item.model_dump(mode="json", exclude_none=True) for item in report_skips])
        for item in eligible:
            eligible_item, issues = annotate_eligibility(item)
            if not hasattr(eligible_item, "schema_anchor"):
                skipped.append(getattr(eligible_item, "model_dump", lambda **_: eligible_item)())
                summary.skipped_results += 1
                continue
            anchor = eligible_item.schema_anchor
            if anchor is None:
                skipped.append(getattr(eligible_item, "model_dump", lambda **_: eligible_item)())
                summary.skipped_results += 1
                continue

            lineage_paths = build_upstream_paths(anchor, latest_snapshot, max_hops=max_hops)
            lineage_path = lineage_paths[0] if lineage_paths else None
            if lineage_path is None:
                summary.skipped_results += 1
                continue

            candidate_paths: list[str] = []
            commit_evidence, git_warnings = collect_commit_evidence(anchor, candidate_paths, window)
            source_node = lineage_path.traversed_nodes[0] if lineage_path.traversed_nodes else None
            source_range = derive_source_range(anchor, source_node)
            commit_evidence, blame_warnings = collect_blame(anchor, commit_evidence, source_range)

            candidates: list[BlameCandidate] = []
            if not commit_evidence:
                commit_evidence = []
            if not commit_evidence:
                synthetic = BlameCandidate(
                    candidate_id=f"{anchor.dataset_id}:{anchor.check_id}:0",
                    source_node=source_node or LineageNode(node_id=anchor.dataset_id, label=anchor.dataset_id),
                    evidence_bundle=[],
                    factor_scores={"recency": 0.3, "hop_proximity": 0.5, "directness": 1.0 if anchor.directness == "field" else 0.5, "line_blame": 0.0, "lineage_completeness": 0.5},
                    uncertainty_reasons=sorted({*snapshot_warnings, *git_warnings, *blame_warnings, *issues, "missing_git_history"}),
                )
                synthetic.normalized_score = score_candidate(synthetic, lineage_path, None, max_hops=max_hops, directness=anchor.directness, blame_available=False)
                synthetic.confidence_band = confidence_band(synthetic.normalized_score)
                candidates.append(synthetic)
            else:
                for index, evidence in enumerate(commit_evidence[:max_candidates]):
                    node = lineage_path.traversed_nodes[min(index, len(lineage_path.traversed_nodes) - 1)] if lineage_path.traversed_nodes else LineageNode(node_id=anchor.dataset_id, label=anchor.dataset_id)
                    candidate = BlameCandidate(
                        candidate_id=f"{anchor.dataset_id}:{anchor.check_id}:{index}",
                        source_node=node,
                        evidence_bundle=[evidence],
                        factor_scores={
                            "recency": 0.5,
                            "hop_proximity": 1.0 if node.hop == 0 else max(0.0, 1.0 - node.hop / max_hops),
                            "directness": 1.0 if anchor.directness == "field" else 0.5,
                            "line_blame": 1.0 if evidence.blame_used else 0.4,
                            "lineage_completeness": 1.0 if lineage_path.completeness == LineageCompleteness.complete else 0.5,
                        },
                        uncertainty_reasons=sorted({*parse_issues, *snapshot_warnings, *git_warnings, *blame_warnings, *issues}),
                    )
                    candidate.normalized_score = score_candidate(candidate, lineage_path, evidence.authored_at, max_hops=max_hops, directness=anchor.directness, blame_available=evidence.blame_used)
                    candidate.confidence_band = confidence_band(candidate.normalized_score)
                    candidates.append(candidate)

            candidates = sort_candidates(candidates)[:max_candidates]
            if not candidates:
                continue

            summary.attributed_violations += 1
            blast_radius = compute_blast_radius(anchor, max_hops=max_hops)
            confidence_summary = build_confidence_summary(candidates)
            record = assemble_violation_record(eligible_item, candidates, blast_radius, detected_at=report.run_timestamp, confidence_summary=confidence_summary)
            records.append(record)

    if not dry_run:
        target = Path(output_path) if output_path else REPO_ROOT / "violation_log" / "violations.jsonl"
        write_result = write_violation_records(records, target, overwrite=overwrite)
        summary.written_violations = int(write_result["written"])
        summary.duplicate_violations = int(write_result["duplicates"])
        summary.output_path = str(write_result["output_path"])
    else:
        summary.written_violations = 0
        summary.output_path = output_path or (REPO_ROOT / "violation_log" / "violations.jsonl").as_posix()

    summary.skipped = skipped
    return summary.model_dump(mode="json")
