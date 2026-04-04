"""Deterministic embedding-like drift baseline and comparison logic."""

from __future__ import annotations

import hashlib
import math
from pathlib import Path
from typing import Any

from src.ai_enforcement.renderer import read_json, write_json_atomic
from src.models.ai_enforcement_models import DriftComparisonStatus, EmbeddingBaseline, EmbeddingComparisonResult
from src.validators.ai_enforcement_validator import validate_embedding_baseline_payload, validate_embedding_comparison_payload


ALGORITHM = "token_hash_v1"
VECTOR_DIMENSIONS = 256
MIN_SAMPLE_SIZE = 3


def select_surface_samples(records: list[dict[str, Any]], surface_id: str) -> list[str]:
    candidates = [
        surface_id,
        "prompt_text",
        "text",
        "content",
        "extraction",
    ]
    selected: list[str] = []
    for record in records:
        value: Any = None
        for key in candidates:
            if key in record:
                value = record.get(key)
                break
        if isinstance(value, str) and value.strip():
            selected.append(value.strip())
    return sorted(selected)


def _normalize_token(token: str) -> str:
    return "".join(ch.lower() for ch in token if ch.isalnum())


def build_signature(samples: list[str], dimensions: int = VECTOR_DIMENSIONS) -> list[float]:
    bins = [0.0] * dimensions
    for sample in samples:
        for token in sample.split():
            normalized = _normalize_token(token)
            if not normalized:
                continue
            idx = int(hashlib.sha256(normalized.encode("utf-8")).hexdigest(), 16) % dimensions
            bins[idx] += 1.0
    magnitude = math.sqrt(sum(x * x for x in bins))
    if magnitude <= 0:
        return bins
    return [round(x / magnitude, 12) for x in bins]


def _cosine_distance(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 1.0
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(y * y for y in b))
    if mag_a <= 0 or mag_b <= 0:
        return 1.0
    cosine_sim = max(min(dot / (mag_a * mag_b), 1.0), -1.0)
    return round(1.0 - cosine_sim, 12)


def _baseline_path(snapshot_root: Path, surface_id: str) -> Path:
    return snapshot_root / "ai" / surface_id / f"baseline_{ALGORITHM}.json"


def _comparison_path(snapshot_root: Path, surface_id: str, run_timestamp: str, run_id: str) -> Path:
    return snapshot_root / "ai" / surface_id / f"comparison_{run_timestamp}_{run_id}.json"


def compare_or_create_baseline(
    *,
    snapshot_root: Path,
    surface_id: str,
    samples: list[str],
    run_id: str,
    run_timestamp: str,
    drift_threshold: float = 0.15,
) -> tuple[EmbeddingComparisonResult, list[str]]:
    drift_artifacts: list[str] = []
    comparison_out: EmbeddingComparisonResult

    if len(samples) < MIN_SAMPLE_SIZE:
        comparison_out = EmbeddingComparisonResult(
            run_id=run_id,
            surface_id=surface_id,
            comparison_status=DriftComparisonStatus.insufficient_data,
            sample_size=len(samples),
            drift_threshold=drift_threshold,
            reason="insufficient sample size for reliable comparison",
        )
    else:
        baseline_path = _baseline_path(snapshot_root, surface_id)
        comparison_path = _comparison_path(snapshot_root, surface_id, run_timestamp, run_id)

        current_signature = build_signature(samples)
        baseline_payload = read_json(baseline_path)

        if baseline_payload is None:
            baseline = EmbeddingBaseline(
                surface_id=surface_id,
                baseline_id=f"{surface_id}:{run_timestamp}",
                created_at=run_timestamp,
                sample_size=len(samples),
                sample_filters={"surface_id": surface_id},
                source_paths=["outputs/week3/extractions.jsonl"],
                signature_vector=current_signature,
            )
            payload = baseline.model_dump(mode="json")
            validate_embedding_baseline_payload(payload, strict=True)
            write_json_atomic(baseline_path, payload)
            drift_artifacts.append(baseline_path.as_posix())
            comparison_out = EmbeddingComparisonResult(
                run_id=run_id,
                surface_id=surface_id,
                baseline_id=baseline.baseline_id,
                comparison_status=DriftComparisonStatus.baseline_created,
                sample_size=len(samples),
                drift_threshold=drift_threshold,
                reason="baseline created",
            )
        else:
            try:
                validate_embedding_baseline_payload(baseline_payload, strict=True)
                baseline_signature = list(baseline_payload.get("signature_vector", []))
                distance = _cosine_distance(current_signature, baseline_signature)
                detected = distance > drift_threshold
                comparison_out = EmbeddingComparisonResult(
                    run_id=run_id,
                    surface_id=surface_id,
                    baseline_id=str(baseline_payload.get("baseline_id", "")),
                    comparison_status=DriftComparisonStatus.compared,
                    sample_size=len(samples),
                    cosine_distance=distance,
                    drift_threshold=drift_threshold,
                    drift_detected=detected,
                    reason="distance above threshold" if detected else "within threshold",
                )
            except Exception:
                comparison_out = EmbeddingComparisonResult(
                    run_id=run_id,
                    surface_id=surface_id,
                    comparison_status=DriftComparisonStatus.baseline_unreadable,
                    sample_size=len(samples),
                    drift_threshold=drift_threshold,
                    reason="baseline artifact unreadable or invalid",
                )

        comparison_payload = comparison_out.model_dump(mode="json")
        validate_embedding_comparison_payload(comparison_payload, strict=True)
        write_json_atomic(comparison_path, comparison_payload)
        drift_artifacts.append(comparison_path.as_posix())

    return comparison_out, drift_artifacts
