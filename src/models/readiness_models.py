"""Typed foundation models for canonical paths, readiness, ownership, and traceability."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ArtifactStatus(str, Enum):
    confirmed_from_repository_evidence = "confirmed_from_repository_evidence"
    inferred_from_requirement_document = "inferred_from_requirement_document"
    blocked_by_missing_upstream_data = "blocked_by_missing_upstream_data"
    pending_migration_or_normalization = "pending_migration_or_normalization"


class CanonicalPathEntry(BaseModel):
    path: str
    path_type: str = Field(pattern="^(file|directory)$")
    required: bool = True
    owner_team: str
    status: ArtifactStatus


class DatasetReadinessEntry(BaseModel):
    dataset_id: str
    canonical_path: str
    schema_name: str
    producer_system: str
    consumer_systems: list[str]
    readiness_status: ArtifactStatus
    mismatch_refs: list[str] = Field(default_factory=list)
    evidence_notes: str | None = None


class InterfaceRegistryEntry(BaseModel):
    interface_id: str
    version: str
    source_system: str
    target_system: str
    dataset_refs: list[str]
    schema_refs: list[str] = Field(default_factory=list)
    ownership_ref: str
    status: ArtifactStatus
    semantic_contract: str | None = None


class SchemaOwnershipRecord(BaseModel):
    ownership_id: str
    schema_name: str
    producer_owner: str
    consumer_owners: list[str]
    blast_radius_notes: str
    migration_required: bool
    status: ArtifactStatus


class SchemaMismatchRecord(BaseModel):
    mismatch_id: str
    dataset_id: str
    mismatch_type: str
    observed_value: Any
    canonical_value: Any
    business_meaning_risk: str
    resolution_type: str
    status: ArtifactStatus


class RequirementTraceRecord(BaseModel):
    requirement_id: str
    artifact_paths: list[str]
    coverage_type: str
    status: ArtifactStatus
