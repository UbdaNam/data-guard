"""Typed contract-generation models for Feature 2."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class SemanticConfidence(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"


class InvariantSource(str, Enum):
    inferred = "inferred"
    requirement_defined = "requirement_defined"
    merged = "merged"


class ContextCoverageStatus(str, Enum):
    full = "full"
    partial = "partial"
    unknown = "unknown"


class DatasetTarget(BaseModel):
    dataset_id: str
    canonical_input_path: str
    canonical_contract_output_path: str
    canonical_dbt_output_path: str
    schema_name: str
    readiness_status: str


class ProfiledField(BaseModel):
    field_path: str
    parent_path: str | None = None
    observed_types: list[str] = Field(default_factory=list)
    presence_rate: float = 0.0
    null_rate: float = 0.0
    numeric_stats: dict[str, Any] | None = None
    candidate_enum_values: list[str] | None = None
    uniqueness_rate: float | None = None
    pattern_candidates: list[str] | None = None
    semantic_confidence: SemanticConfidence = SemanticConfidence.medium
    uncertainty_note: str | None = None
    annotation_note: str | None = None
    annotation_source: str | None = None


class InvariantClause(BaseModel):
    clause_id: str
    field_path: str | None = None
    clause_type: str
    source: InvariantSource
    expression: dict[str, Any] = Field(default_factory=dict)
    confidence: SemanticConfidence = SemanticConfidence.medium
    supported_in_dbt: bool = False


class DownstreamContextAnnotation(BaseModel):
    downstream_systems: list[str] = Field(default_factory=list)
    consumed_fields: list[str] = Field(default_factory=list)
    likely_breaking_fields: list[str] = Field(default_factory=list)
    consumer_change_sensitivity: list[dict[str, Any]] = Field(default_factory=list)
    coverage_status: ContextCoverageStatus = ContextCoverageStatus.unknown
    context_sources: list[str] = Field(default_factory=list)
    latest_snapshot_timestamp: str | None = None


class CanonicalMismatchRecord(BaseModel):
    dataset_id: str
    mismatch_type: str
    canonical_value: str
    observed_value: str
    impact_note: str
    migration_or_normalization_required: bool = False


class DbtSchemaArtifact(BaseModel):
    model_name: str
    columns: list[dict[str, Any]] = Field(default_factory=list)
    tests: list[dict[str, Any]] = Field(default_factory=list)
    unsupported_clause_mappings: list[str] = Field(default_factory=list)


class GenerationMetadata(BaseModel):
    run_id: str
    generated_at: str
    generator_version: str = "0.2.0"
    contract_schema_version: str = "1.0"
    input_artifact_hashes: dict[str, str] = Field(default_factory=dict)
    input_record_counts: dict[str, int] = Field(default_factory=dict)
    malformed_line_count: int = 0
    mismatch_count: int = 0
    deterministic_signature: str = ""


class GeneratedContract(BaseModel):
    contract_id: str
    dataset_target: DatasetTarget
    schema_fields: list[ProfiledField] = Field(default_factory=list)
    clauses: list[InvariantClause] = Field(default_factory=list)
    downstream_context: DownstreamContextAnnotation = Field(default_factory=DownstreamContextAnnotation)
    mismatch_records: list[CanonicalMismatchRecord] = Field(default_factory=list)
    metadata: GenerationMetadata


class DatasetLoadResult(BaseModel):
    target: DatasetTarget
    records: list[dict[str, Any]] = Field(default_factory=list)
    malformed_lines: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)

    @property
    def valid_record_count(self) -> int:
        return len(self.records)
