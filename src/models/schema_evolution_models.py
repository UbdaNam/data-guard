"""Typed models for Feature 5 schema evolution intelligence."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class NestedKind(str, Enum):
    scalar = "scalar"
    object = "object"
    array = "array"
    map = "map"


class MatchType(str, Enum):
    exact = "exact"
    explicit_rename = "explicit_rename"
    heuristic_rename = "heuristic_rename"
    unmatched = "unmatched"


class ChangeClass(str, Enum):
    add_nullable_field = "add_nullable_field"
    add_required_field = "add_required_field"
    remove_field = "remove_field"
    rename_field = "rename_field"
    widen_type = "widen_type"
    narrow_type = "narrow_type"
    change_enum_values = "change_enum_values"
    change_constraints = "change_constraints"
    change_nested_structure = "change_nested_structure"
    change_semantic_scale = "change_semantic_scale"


class CompatibilityVerdict(str, Enum):
    fully_compatible = "fully-compatible"
    backward_compatible = "backward-compatible"
    forward_compatible = "forward-compatible"
    breaking = "breaking"


class ContextCompleteness(str, Enum):
    complete = "complete"
    partial = "partial"
    minimal = "minimal"


class Urgency(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class NormalizedField(BaseModel):
    path: str
    type: str
    nullable: bool = False
    required: bool = False
    enum_values: list[str] | None = None
    pattern: str | None = None
    minimum: float | None = None
    maximum: float | None = None
    nested_kind: NestedKind = NestedKind.scalar
    raw_constraints: dict[str, Any] = Field(default_factory=dict)


class ContractRule(BaseModel):
    rule_id: str
    rule_scope: str = "dataset"
    rule_type: str
    rule_payload: dict[str, Any] = Field(default_factory=dict)


class SchemaSnapshot(BaseModel):
    snapshot_id: str
    snapshot_timestamp: str
    contract_id: str
    schema_version: str | None = None
    schema_hash: str
    source_contract_path: str
    fields: list[NormalizedField] = Field(default_factory=list)
    rules: list[ContractRule] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class FieldMatch(BaseModel):
    from_path: str | None = None
    to_path: str | None = None
    match_type: MatchType = MatchType.unmatched
    confidence: float = 0.0
    evidence: list[str] = Field(default_factory=list)


class CompatibilityAssessment(BaseModel):
    is_backward_compatible: bool
    is_forward_compatible: bool
    verdict: CompatibilityVerdict
    rationale: str


class SchemaChange(BaseModel):
    change_id: str
    change_class: ChangeClass
    from_field: NormalizedField | None = None
    to_field: NormalizedField | None = None
    details: dict[str, Any] = Field(default_factory=dict)
    compatibility: CompatibilityAssessment | None = None


class ConsumerImpact(BaseModel):
    consumer_id: str
    interface_id: str | None = None
    ownership_id: str | None = None
    likely_failure_modes: list[str] = Field(default_factory=list)
    impact_severity: Urgency = Urgency.medium


class MigrationAction(BaseModel):
    order: int
    owner: str
    action: str
    target: str
    verification: str
    rollback_step: str | None = None


class SchemaEvolutionReport(BaseModel):
    analysis_id: str
    contract_id: str
    from_snapshot_id: str | None = None
    to_snapshot_id: str
    change_summary: dict[str, Any] = Field(default_factory=dict)
    structured_diff: list[SchemaChange] = Field(default_factory=list)
    compatibility_verdict: CompatibilityAssessment
    determinism_keys: dict[str, Any] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
    context_completeness: ContextCompleteness = ContextCompleteness.minimal


class MigrationImpactReport(BaseModel):
    report_id: str
    analysis_id: str
    contract_id: str
    human_diff_summary: str
    structured_diff: list[SchemaChange] = Field(default_factory=list)
    compatibility_verdict: CompatibilityAssessment
    affected_consumers: list[ConsumerImpact] = Field(default_factory=list)
    migration_checklist: list[MigrationAction] = Field(default_factory=list)
    rollback_guidance: list[str] = Field(default_factory=list)
    urgency: Urgency = Urgency.medium
    confidence_change_caused_breakage: float = 0.5
    enrichment_sources: dict[str, Any] = Field(default_factory=dict)
