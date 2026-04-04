"""Typed attribution models for Feature 4."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from src.models.readiness_models import ArtifactStatus


class AttributionDecision(str, Enum):
    eligible = "eligible"
    skipped = "skipped"


class SkipReason(str, Enum):
    passing_check = "passing_check"
    unsupported_status = "unsupported_status"
    unsupported_check_class = "unsupported_check_class"
    non_governed_failure = "non_governed_failure"
    missing_contract_context = "missing_contract_context"
    missing_schema_anchor = "missing_schema_anchor"
    missing_lineage_context = "missing_lineage_context"
    missing_git_history = "missing_git_history"
    malformed_report = "malformed_report"


class ConfidenceBand(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"


class LineageCompleteness(str, Enum):
    complete = "complete"
    partial = "partial"
    weak = "weak"
    missing = "missing"


class LineageStopReason(str, Enum):
    external_boundary = "external_boundary"
    repository_root = "repository_root"
    no_further_upstream_nodes = "no_further_upstream_nodes"
    max_hop_count_reached = "max_hop_count_reached"
    incomplete_lineage = "incomplete_lineage"
    graph_unavailable = "graph_unavailable"


class SchemaAnchor(BaseModel):
    model_config = ConfigDict(extra="allow")

    dataset_id: str
    contract_id: str
    schema_name: str | None = None
    canonical_path: str | None = None
    field_path: str | None = None
    check_id: str | None = None
    interface_id: str | None = None
    ownership_id: str | None = None
    producer_system: str | None = None
    consumer_systems: list[str] = Field(default_factory=list)
    status: ArtifactStatus = ArtifactStatus.inferred_from_requirement_document
    directness: str = "dataset"
    source_note: str | None = None

    @field_validator("consumer_systems", mode="before")
    @classmethod
    def _ensure_consumer_systems(cls, value: Any) -> list[str]:
        if value is None:
            return []
        if isinstance(value, list):
            return [str(item) for item in value]
        return [str(value)]


class AttributionEligibleResult(BaseModel):
    model_config = ConfigDict(extra="allow")

    decision: AttributionDecision = AttributionDecision.eligible
    report_id: str
    contract_id: str
    dataset_id: str
    check_id: str
    check_type: str
    column_name: str | None = None
    status: str
    severity: str | None = None
    message: str | None = None
    sample_failing: list[dict[str, Any]] = Field(default_factory=list)
    selected_reason: str = ""
    schema_anchor: SchemaAnchor | None = None


class AttributionSkipRecord(BaseModel):
    model_config = ConfigDict(extra="allow")

    decision: AttributionDecision = AttributionDecision.skipped
    report_id: str
    contract_id: str | None = None
    dataset_id: str | None = None
    check_id: str | None = None
    check_type: str | None = None
    column_name: str | None = None
    status: str | None = None
    skip_reason: SkipReason
    message: str | None = None


class LineageNode(BaseModel):
    model_config = ConfigDict(extra="allow")

    node_id: str
    label: str
    dataset_id: str | None = None
    schema_name: str | None = None
    interface_id: str | None = None
    ownership_id: str | None = None
    source_file: str | None = None
    source_line_start: int | None = None
    source_line_end: int | None = None
    hop: int = 0
    direction: str = "upstream"
    external_boundary: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class LineagePathEvidence(BaseModel):
    model_config = ConfigDict(extra="allow")

    source_node: LineageNode
    traversed_nodes: list[LineageNode] = Field(default_factory=list)
    hop_count: int = 0
    stop_reason: LineageStopReason
    completeness: LineageCompleteness = LineageCompleteness.partial
    warnings: list[str] = Field(default_factory=list)


class CommitEvidence(BaseModel):
    model_config = ConfigDict(extra="allow")

    file_path: str
    commit_hash: str
    author: str
    authored_at: str
    commit_summary: str
    line_range: tuple[int, int] | None = None
    blame_used: bool = False
    reference_path: str | None = None


class BlameCandidate(BaseModel):
    model_config = ConfigDict(extra="allow")

    candidate_id: str
    source_node: LineageNode
    evidence_bundle: list[CommitEvidence] = Field(default_factory=list)
    factor_scores: dict[str, float] = Field(default_factory=dict)
    normalized_score: float = 0.0
    confidence_band: ConfidenceBand = ConfidenceBand.low
    uncertainty_reasons: list[str] = Field(default_factory=list)
    rank: int = 0

    @field_validator("normalized_score")
    @classmethod
    def _score_range(cls, value: float) -> float:
        if value < 0.0 or value > 100.0:
            raise ValueError("normalized_score must be between 0 and 100")
        return value


class BlastRadiusImpact(BaseModel):
    model_config = ConfigDict(extra="allow")

    affected_nodes: list[str] = Field(default_factory=list)
    affected_pipelines: list[str] = Field(default_factory=list)
    affected_interfaces: list[str] = Field(default_factory=list)
    direct_subscribers: list[str] = Field(default_factory=list)
    transitive_downstream_nodes: list[str] = Field(default_factory=list)
    contamination_depth: int = 0
    estimated_impacted_records: int | None = None
    estimated_impacted_datasets: int | None = None
    knowledge_completeness: LineageCompleteness = LineageCompleteness.partial
    unknown_downstream_count: int = 0


class BlastRadiusSummary(BaseModel):
    model_config = ConfigDict(extra="allow")

    direct_impact: BlastRadiusImpact = Field(default_factory=BlastRadiusImpact)
    indirect_impact: BlastRadiusImpact = Field(default_factory=BlastRadiusImpact)
    affected_nodes: list[str] = Field(default_factory=list)
    affected_pipelines: list[str] = Field(default_factory=list)
    affected_interfaces: list[str] = Field(default_factory=list)
    direct_subscribers: list[str] = Field(default_factory=list)
    transitive_downstream_nodes: list[str] = Field(default_factory=list)
    contamination_depth: int = 0
    estimated_impacted_records: int | None = None
    estimated_impacted_datasets: int | None = None
    knowledge_completeness: LineageCompleteness = LineageCompleteness.partial
    unknown_downstream_count: int = 0


class AttributionConfidenceSummary(BaseModel):
    model_config = ConfigDict(extra="allow")

    max_score: float = 0.0
    min_score: float = 0.0
    average_score: float = 0.0
    confidence_band: ConfidenceBand = ConfidenceBand.low
    uncertainty_reasons: list[str] = Field(default_factory=list)


class ViolationRecord(BaseModel):
    model_config = ConfigDict(extra="allow")

    violation_id: str
    report_id: str
    detected_at: str
    contract_id: str
    dataset_id: str
    check_id: str
    check_type: str
    status: str
    column_name: str | None = None
    schema_anchor: SchemaAnchor | None = None
    blame_chain: list[BlameCandidate] = Field(default_factory=list)
    blast_radius: BlastRadiusSummary
    attribution_confidence_summary: AttributionConfidenceSummary | None = None
    selected_reason: str | None = None
    skip_reason: str | None = None

    @model_validator(mode="after")
    def _validate_blame_chain(self) -> ViolationRecord:
        if not self.blame_chain:
            raise ValueError("violation record requires at least one blame candidate")
        if len(self.blame_chain) > 5:
            raise ValueError("violation record cannot contain more than five candidates")
        return self


class LineageSnapshotRecord(BaseModel):
    model_config = ConfigDict(extra="allow")

    source_path: str
    line_number: int
    payload: dict[str, Any]
    snapshot_timestamp: str | None = None
    captured_at: str | None = None
    run_timestamp: str | None = None
    dataset_id: str | None = None
    consumed_fields: list[str] = Field(default_factory=list)


class LoadedGeneratedContract(BaseModel):
    model_config = ConfigDict(extra="allow")

    source_path: str
    contract_id: str
    dataset_id: str
    canonical_input_path: str | None = None
    schema_name: str | None = None
    clauses: list[dict[str, Any]] = Field(default_factory=list)
    downstream_context: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
    mismatch_records: list[dict[str, Any]] = Field(default_factory=list)
    schema_fields: list[dict[str, Any]] = Field(default_factory=list)


class AttributionRunSummary(BaseModel):
    model_config = ConfigDict(extra="allow")

    processed_reports: int = 0
    eligible_results: int = 0
    skipped_results: int = 0
    attributed_violations: int = 0
    written_violations: int = 0
    duplicate_violations: int = 0
    output_path: str | None = None
    report_paths: list[str] = Field(default_factory=list)
    skipped: list[dict[str, Any]] = Field(default_factory=list)
