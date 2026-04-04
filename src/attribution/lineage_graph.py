"""Lineage traversal helpers for attribution and blast radius analysis."""

from __future__ import annotations

from collections import deque
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from src.attribution.artifact_resolver import build_dataset_index, load_dataset_readiness, load_interface_registry
from src.models.attribution_models import LineageCompleteness, LineageNode, LineagePathEvidence, LineageSnapshotRecord, LineageStopReason, SchemaAnchor

REPO_ROOT = Path(__file__).resolve().parents[2]


def _make_node(
    label: str,
    dataset_id: str | None = None,
    schema_name: str | None = None,
    interface_id: str | None = None,
    ownership_id: str | None = None,
    hop: int = 0,
    direction: str = "upstream",
    external_boundary: bool = False,
    metadata: dict[str, Any] | None = None,
) -> LineageNode:
    return LineageNode(
        node_id=":".join([part for part in [dataset_id, interface_id, ownership_id, label] if part]),
        label=label,
        dataset_id=dataset_id,
        schema_name=schema_name,
        interface_id=interface_id,
        ownership_id=ownership_id,
        hop=hop,
        direction=direction,
        external_boundary=external_boundary,
        metadata=metadata or {},
    )


def _neighbor_nodes(node: LineageNode, snapshot_payload: dict[str, Any] | None = None) -> list[LineageNode]:
    datasets = build_dataset_index(load_dataset_readiness(REPO_ROOT))
    interfaces = load_interface_registry(REPO_ROOT)
    dataset = datasets.get(node.dataset_id) if node.dataset_id else None
    neighbours: list[LineageNode] = []

    for interface in [entry for entry in interfaces if node.dataset_id and node.dataset_id in entry.dataset_refs]:
        neighbours.append(
            _make_node(
                label=interface.interface_id,
                dataset_id=node.dataset_id,
                schema_name=dataset.schema_name if dataset else None,
                interface_id=interface.interface_id,
                ownership_id=interface.ownership_ref,
                hop=node.hop + 1,
                metadata={"source_system": interface.source_system, "target_system": interface.target_system},
            )
        )
        neighbours.append(
            _make_node(
                label=interface.source_system,
                dataset_id=node.dataset_id,
                schema_name=dataset.schema_name if dataset else None,
                interface_id=interface.interface_id,
                ownership_id=interface.ownership_ref,
                hop=node.hop + 1,
                external_boundary=True,
                metadata={"source_system": interface.source_system, "target_system": interface.target_system},
            )
        )

    if snapshot_payload and isinstance(snapshot_payload.get("upstream"), list):
        for upstream in snapshot_payload["upstream"]:
            if not isinstance(upstream, dict):
                continue
            neighbours.append(
                _make_node(
                    label=str(upstream.get("node_id") or upstream.get("label") or node.label),
                    dataset_id=str(upstream.get("dataset_id") or node.dataset_id or ""),
                    schema_name=str(upstream.get("schema_name") or (dataset.schema_name if dataset else "")),
                    interface_id=upstream.get("interface_id"),
                    ownership_id=upstream.get("ownership_id"),
                    hop=node.hop + 1,
                    external_boundary=bool(upstream.get("external_boundary", False)),
                    metadata=upstream,
                )
            )

    return neighbours


def build_upstream_paths(anchor: SchemaAnchor, snapshot_record: LineageSnapshotRecord | None = None, max_hops: int = 6) -> list[LineagePathEvidence]:
    start = _make_node(
        label=anchor.field_path or anchor.dataset_id,
        dataset_id=anchor.dataset_id,
        schema_name=anchor.schema_name,
        interface_id=anchor.interface_id,
        ownership_id=anchor.ownership_id,
        metadata={"canonical_path": anchor.canonical_path, "source_note": anchor.source_note},
    )
    snapshot_payload = snapshot_record.payload if snapshot_record else None
    queue = deque([(start, 0)])
    visited: set[str] = {start.node_id}
    traversed: list[LineageNode] = []
    warnings: list[str] = []

    if snapshot_record is None:
        warnings.append("No lineage snapshot available; falling back to contract/interface context")

    while queue:
        node, hop = queue.popleft()
        traversed.append(node)
        if hop >= max_hops:
            return [
                LineagePathEvidence(
                    source_node=start,
                    traversed_nodes=traversed,
                    hop_count=hop,
                    stop_reason=LineageStopReason.max_hop_count_reached,
                    completeness=LineageCompleteness.partial,
                    warnings=warnings,
                )
            ]

        neighbours = _neighbor_nodes(node, snapshot_payload)
        if not neighbours:
            stop_reason = LineageStopReason.repository_root if node.dataset_id == anchor.dataset_id else LineageStopReason.no_further_upstream_nodes
            return [
                LineagePathEvidence(
                    source_node=start,
                    traversed_nodes=traversed,
                    hop_count=hop,
                    stop_reason=stop_reason,
                    completeness=LineageCompleteness.complete if hop else LineageCompleteness.partial,
                    warnings=warnings,
                )
            ]

        for neighbour in neighbours:
            if neighbour.node_id in visited:
                continue
            visited.add(neighbour.node_id)
            queue.append((neighbour, hop + 1))

    return [
        LineagePathEvidence(
            source_node=start,
            traversed_nodes=traversed,
            hop_count=max(len(traversed) - 1, 0),
            stop_reason=LineageStopReason.incomplete_lineage,
            completeness=LineageCompleteness.partial,
            warnings=warnings,
        )
    ]
