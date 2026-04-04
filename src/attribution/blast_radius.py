"""Blast radius analysis for Feature 4."""

from __future__ import annotations

from pathlib import Path

from src.attribution.artifact_resolver import build_dataset_index, load_dataset_readiness, load_interface_registry
from src.models.attribution_models import BlastRadiusImpact, BlastRadiusSummary, LineageCompleteness, SchemaAnchor

REPO_ROOT = Path(__file__).resolve().parents[2]


def compute_blast_radius(anchor: SchemaAnchor, max_hops: int = 6) -> BlastRadiusSummary:
    interfaces = load_interface_registry(REPO_ROOT)
    datasets = build_dataset_index(load_dataset_readiness(REPO_ROOT))

    direct_nodes: list[str] = []
    direct_pipelines: list[str] = []
    direct_interfaces: list[str] = []
    indirect_nodes: list[str] = []
    indirect_pipelines: list[str] = []
    indirect_interfaces: list[str] = []

    direct_matches = [entry for entry in interfaces if anchor.dataset_id in entry.dataset_refs]
    for interface in direct_matches:
        direct_nodes.append(interface.target_system)
        direct_pipelines.append(f"{interface.source_system}->{interface.target_system}")
        direct_interfaces.append(interface.interface_id)

    frontier = list(direct_nodes)
    visited = set(direct_nodes)
    hops = 1
    while frontier and hops < max_hops:
        next_frontier: list[str] = []
        for system_name in frontier:
            for interface in interfaces:
                if interface.source_system != system_name:
                    continue
                if interface.interface_id not in direct_interfaces:
                    indirect_interfaces.append(interface.interface_id)
                if interface.target_system not in visited:
                    indirect_nodes.append(interface.target_system)
                    indirect_pipelines.append(f"{interface.source_system}->{interface.target_system}")
                    next_frontier.append(interface.target_system)
                    visited.add(interface.target_system)
        frontier = next_frontier
        hops += 1

    direct = BlastRadiusImpact(
        affected_nodes=sorted(dict.fromkeys(direct_nodes)),
        affected_pipelines=sorted(dict.fromkeys(direct_pipelines)),
        affected_interfaces=sorted(dict.fromkeys(direct_interfaces)),
        estimated_impacted_records=len(direct_nodes) or None,
        estimated_impacted_datasets=1 if datasets.get(anchor.dataset_id) else None,
        knowledge_completeness=LineageCompleteness.complete if direct_nodes else LineageCompleteness.partial,
        unknown_downstream_count=0 if direct_nodes else 1,
    )
    indirect = BlastRadiusImpact(
        affected_nodes=sorted(dict.fromkeys(indirect_nodes)),
        affected_pipelines=sorted(dict.fromkeys(indirect_pipelines)),
        affected_interfaces=sorted(dict.fromkeys(indirect_interfaces)),
        estimated_impacted_records=len(indirect_nodes) or None,
        estimated_impacted_datasets=len(set(indirect_nodes)) or None,
        knowledge_completeness=LineageCompleteness.partial if indirect_nodes else LineageCompleteness.missing,
        unknown_downstream_count=0 if indirect_nodes else 1,
    )
    return BlastRadiusSummary(
        direct_impact=direct,
        indirect_impact=indirect,
        affected_nodes=sorted(dict.fromkeys(direct_nodes + indirect_nodes)),
        affected_pipelines=sorted(dict.fromkeys(direct_pipelines + indirect_pipelines)),
        affected_interfaces=sorted(dict.fromkeys(direct_interfaces + indirect_interfaces)),
        estimated_impacted_records=direct.estimated_impacted_records,
        estimated_impacted_datasets=direct.estimated_impacted_datasets or indirect.estimated_impacted_datasets,
        knowledge_completeness=LineageCompleteness.complete if direct_nodes else LineageCompleteness.partial,
        unknown_downstream_count=direct.unknown_downstream_count + indirect.unknown_downstream_count,
    )
