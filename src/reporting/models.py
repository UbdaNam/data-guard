"""Typed models for operational report generation."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ReportingWindow(BaseModel):
    start: str
    end: str
    selection_mode: Literal["explicit", "latest_available"]
    resolved_from_sources: list[str] = Field(default_factory=list)
    resolution_notes: list[str] = Field(default_factory=list)


class EvidenceReference(BaseModel):
    artifact_path: str
    record_selector: str
    claim_type: Literal["metric", "incident", "schema_change", "ai_risk", "action"]


class SectionCompletenessRecord(BaseModel):
    status: Literal["complete", "partial", "insufficient_evidence"]
    missing_sources: list[str] = Field(default_factory=list)
    reason: str | None = None


class DataHealthScore(BaseModel):
    value: float | None
    score_status: Literal["computed", "insufficient_evidence"]
    check_penalty: float | None
    critical_penalty: float | None
    raw_score: float | None
    formula_version: str = "fr032_v1"
    reason: str | None = None


class ViolationsSummary(BaseModel):
    total: int = 0
    by_severity: dict[str, int] = Field(default_factory=dict)
    by_category: dict[str, int] = Field(default_factory=dict)
    by_surface: dict[str, int] = Field(default_factory=dict)
    evidence: list[EvidenceReference] = Field(default_factory=list)


class TopViolation(BaseModel):
    rank: int
    violation_id: str
    severity: str
    recurrence_count: int
    latest_occurrence: str | None
    affected_surface: str
    owner: str = "unassigned"
    priority_tuple: list[str | int | float] = Field(default_factory=list)
    evidence: list[EvidenceReference] = Field(default_factory=list)


class RankedSchemaChange(BaseModel):
    change_id: str
    compatibility_verdict: str
    impact_scope: str
    detected_at: str | None
    affected_interface: str | None
    priority_tuple: list[str | int | float] = Field(default_factory=list)
    evidence: list[EvidenceReference] = Field(default_factory=list)


class SchemaChangesSummary(BaseModel):
    total_changes: int = 0
    breaking_changes: int = 0
    non_breaking_changes: int = 0
    top_changes: list[RankedSchemaChange] = Field(default_factory=list)
    evidence: list[EvidenceReference] = Field(default_factory=list)


class AiRiskSummary(BaseModel):
    quarantine_rate: float | None = None
    output_violation_rate: float | None = None
    trace_violation_rate: float | None = None
    drift_status: str | None = None
    trend_status: str = "unknown"
    completeness_flags: dict[str, bool] = Field(default_factory=dict)
    evidence: list[EvidenceReference] = Field(default_factory=list)


class RecommendedAction(BaseModel):
    action_id: str
    issue_key: dict[str, str]
    priority_score: float
    severity: str
    recurrence_count: int
    latest_occurrence: str | None
    remediation_target: str
    affected_location: str
    owner: str = "unassigned"
    consumer_impact: str | None = None
    verification_step: str
    aggregate_count: int
    evidence: list[EvidenceReference] = Field(default_factory=list)


class GenerationEnrichment(BaseModel):
    requested: bool = False
    provider: Literal["openrouter", "none"] = "none"
    status: Literal["disabled", "missing_config", "failed", "applied"] = "disabled"
    fallback_used: bool = True


class GenerationMetadata(BaseModel):
    generated_at: str
    duration_ms: int
    input_artifact_counts: dict[str, int] = Field(default_factory=dict)
    enrichment: GenerationEnrichment


class OperationalReportData(BaseModel):
    report_id: str
    report_date: str
    reporting_window: ReportingWindow
    data_health_score: DataHealthScore
    section_completeness: dict[str, SectionCompletenessRecord]
    violations_summary: ViolationsSummary
    top_violations: list[TopViolation]
    schema_changes_summary: SchemaChangesSummary
    ai_risk_summary: AiRiskSummary
    recommended_actions: list[RecommendedAction]
    evidence_index: list[EvidenceReference]
    generation_metadata: GenerationMetadata
