"""Loader and graph helpers for the canonical subscriptions registry."""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from contracts.artifact_paths import REPO_ROOT, SUBSCRIPTIONS_REGISTRY_PATH


@dataclass(slots=True)
class SubscriptionRegistryEntry:
    interface_id: str
    producer: str
    consumer: str
    schema_or_record_type: str
    criticality: str
    dependency_type: str
    directness: str = "direct"
    notes: str | None = None


def load_registry(path: Path | None = None) -> dict[str, Any]:
    registry_path = path or SUBSCRIPTIONS_REGISTRY_PATH
    payload = yaml.safe_load(registry_path.read_text(encoding="utf-8")) if registry_path.exists() else None
    if not isinstance(payload, dict):
        raise FileNotFoundError(f"Subscriptions registry not found or invalid: {registry_path.as_posix()}")
    return payload


def _entry_from_raw(raw: dict[str, Any]) -> SubscriptionRegistryEntry:
    return SubscriptionRegistryEntry(
        interface_id=str(raw.get("interface_id") or ""),
        producer=str(raw.get("producer") or ""),
        consumer=str(raw.get("consumer") or ""),
        schema_or_record_type=str(raw.get("schema_or_record_type") or raw.get("schema_name") or raw.get("record_type") or ""),
        criticality=str(raw.get("criticality") or "medium"),
        dependency_type=str(raw.get("dependency_type") or "direct"),
        directness=str(raw.get("directness") or raw.get("dependency_type") or "direct"),
        notes=str(raw.get("notes") or "") or None,
    )


def registry_entries(payload: dict[str, Any] | None = None) -> list[SubscriptionRegistryEntry]:
    resolved = payload or load_registry()
    rows = resolved.get("subscriptions") or resolved.get("interfaces") or []
    entries: list[SubscriptionRegistryEntry] = []
    for raw in rows:
        if isinstance(raw, dict):
            entries.append(_entry_from_raw(raw))
    return entries


def registry_graph(payload: dict[str, Any] | None = None) -> dict[str, set[str]]:
    graph: dict[str, set[str]] = defaultdict(set)
    for entry in registry_entries(payload):
        graph[entry.producer].add(entry.consumer)
    return graph


def direct_subscribers(node: str, payload: dict[str, Any] | None = None) -> list[str]:
    graph = registry_graph(payload)
    return sorted(graph.get(node, set()))


def transitive_downstream_consumers(node: str, payload: dict[str, Any] | None = None) -> list[str]:
    graph = registry_graph(payload)
    visited: set[str] = set()
    queue: deque[str] = deque(graph.get(node, set()))
    while queue:
        current = queue.popleft()
        if current in visited:
            continue
        visited.add(current)
        queue.extend(graph.get(current, set()))
    return sorted(visited)


def contamination_depth(node: str, payload: dict[str, Any] | None = None) -> int:
    graph = registry_graph(payload)
    depth = 0
    frontier = {node}
    visited: set[str] = {node}
    while frontier:
        next_frontier: set[str] = set()
        for current in frontier:
            for consumer in graph.get(current, set()):
                if consumer in visited:
                    continue
                visited.add(consumer)
                next_frontier.add(consumer)
        if next_frontier:
            depth += 1
        frontier = next_frontier
    return depth


def registry_index(payload: dict[str, Any] | None = None) -> dict[str, SubscriptionRegistryEntry]:
    return {entry.interface_id: entry for entry in registry_entries(payload) if entry.interface_id}
