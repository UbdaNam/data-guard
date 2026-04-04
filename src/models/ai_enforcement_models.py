"""Typed models for AI contract enforcement (Feature 6)."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class AIValidationStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    ERROR = "ERROR"


class AIViolationCategory(str, Enum):
    prompt_input = "prompt_input"
    structured_output = "structured_output"
    trace_contract = "trace_contract"
    embedding_drift = "embedding_drift"


class AIViolationSeverity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class AITrendStatus(str, Enum):
    insufficient_history = "insufficient_history"
    stable = "stable"
    improving = "improving"
    degrading = "degrading"


class DriftComparisonStatus(str, Enum):
    baseline_created = "baseline_created"
    compared = "compared"
    insufficient_data = "insufficient_data"
    baseline_unreadable = "baseline_unreadable"
    skipped = "skipped"


class RunContextCompleteness(BaseModel):
    feature1_loaded: bool = False
    feature2_loaded: bool = False
    feature3_conventions_loaded: bool = True
    feature5_context_loaded: bool = False


class AIEnforcementRun(BaseModel):
    run_id: str
    run_timestamp: str
    entrypoint: str = "contracts/ai_extensions.py"
    inputs: dict[str, Any] = Field(default_factory=dict)
    context_completeness: RunContextCompleteness = Field(default_factory=RunContextCompleteness)
    status: str = "completed"


class PromptInputCheckRecord(BaseModel):
    record_id: str
    schema_version: str
    prompt_surface: str
    validation_status: AIValidationStatus
    failure_reasons: list[str] = Field(default_factory=list)
    quarantined: bool = False
    quarantine_path: str | None = None


class StructuredOutputCheckRecord(BaseModel):
    record_id: str
    schema_id: str
    schema_version: str
    validation_status: AIValidationStatus
    unknown_fields: list[str] = Field(default_factory=list)
    missing_required_fields: list[str] = Field(default_factory=list)
    type_mismatches: list[dict[str, Any]] = Field(default_factory=list)
    nested_structure_violations: list[dict[str, Any]] = Field(default_factory=list)


class TraceContractCheckRecord(BaseModel):
    trace_run_id: str
    event_timestamp: str
    contract_id: str
    validation_status: AIValidationStatus
    failure_reasons: list[str] = Field(default_factory=list)


class QuarantineRecord(BaseModel):
    run_id: str
    run_timestamp: str
    record_id: str
    source_dataset: str
    schema_version: str
    failure_reasons: list[str] = Field(default_factory=list)
    original_payload: dict[str, Any] = Field(default_factory=dict)


class AIViolationRecord(BaseModel):
    violation_id: str
    run_id: str
    category: AIViolationCategory
    severity: AIViolationSeverity
    status: str = "open"
    surface_id: str
    record_ref: str
    message: str
    evidence: dict[str, Any] = Field(default_factory=dict)
    owner_context: dict[str, Any] = Field(default_factory=dict)


class EmbeddingBaseline(BaseModel):
    surface_id: str
    baseline_id: str
    algorithm: str = "token_hash_v1"
    vector_dimensions: int = 256
    created_at: str
    sample_size: int
    sample_filters: dict[str, Any] = Field(default_factory=dict)
    source_paths: list[str] = Field(default_factory=list)
    signature_vector: list[float] = Field(default_factory=list)


class EmbeddingComparisonResult(BaseModel):
    run_id: str
    surface_id: str
    baseline_id: str | None = None
    comparison_status: DriftComparisonStatus
    sample_size: int
    cosine_distance: float | None = None
    drift_threshold: float = 0.15
    drift_detected: bool = False
    reason: str = ""


class AIMetricsReport(BaseModel):
    run_id: str
    run_timestamp: str
    totals: dict[str, int] = Field(default_factory=dict)
    rates: dict[str, float] = Field(default_factory=dict)
    trend: dict[str, Any] = Field(default_factory=dict)
    artifacts: dict[str, Any] = Field(default_factory=dict)
    context_completeness: dict[str, Any] = Field(default_factory=dict)
    history: list[dict[str, Any]] = Field(default_factory=list)
