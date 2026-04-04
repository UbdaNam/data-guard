"""Typed validation models for Feature 3."""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class ValidationStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    WARN = "WARN"
    ERROR = "ERROR"


class CheckScope(str, Enum):
    field = "field"
    record = "record"
    dataset = "dataset"
    drift = "drift"


class ValidationSeverity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class ExecutableCheck(BaseModel):
    check_id: str
    contract_id: str
    column_name: str | None = None
    check_type: str
    scope: CheckScope
    expected: dict[str, Any] = Field(default_factory=dict)
    severity: ValidationSeverity = ValidationSeverity.medium
    source_clause_id: str | None = None
    is_drift: bool = False


class ValidationResult(BaseModel):
    check_id: str
    column_name: str | None = None
    check_type: str
    status: ValidationStatus
    actual_value: Any = None
    expected: Any = None
    severity: ValidationSeverity = ValidationSeverity.medium
    records_failing: int = 0
    sample_failing: list[dict[str, Any]] = Field(default_factory=list)
    message: str = ""


class ValidationReport(BaseModel):
    report_id: str
    contract_id: str
    snapshot_id: str
    run_timestamp: str
    total_checks: int
    passed: int
    failed: int
    warned: int
    errored: int
    results: list[ValidationResult] = Field(default_factory=list)


class BaselineStatistic(BaseModel):
    contract_id: str
    column_name: str
    mean: float
    stddev: float
    min: float
    max: float
    sample_size: int
    created_at: str
    updated_at: str


class BaselineArtifactRecord(BaseModel):
    contract_id: str
    column_name: str
    sample_count: int
    mean: float
    stddev: float
    min: float
    max: float
    created_at: str
    updated_at: str


class ValidationRun(BaseModel):
    run_id: str
    run_timestamp: str
    contract_ids: list[str] = Field(default_factory=list)
    snapshot_ids: list[str] = Field(default_factory=list)
    status: str = "completed"


class LoadedContract(BaseModel):
    contract_id: str
    dataset_id: str
    contract_path: str
    snapshot_path: str
    source_contract: dict[str, Any]
    checks: list[ExecutableCheck] = Field(default_factory=list)
    numeric_fields: list[str] = Field(default_factory=list)
    schema_fields: list[dict[str, Any]] = Field(default_factory=list)
    baseline_refresh_allowed: bool = False


class LoadedDataset(BaseModel):
    dataset_id: str
    snapshot_path: str
    rows: list[dict[str, Any]] = Field(default_factory=list)
    malformed_lines: list[dict[str, Any]] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)

    @property
    def record_count(self) -> int:
        return len(self.rows)


class NumericProfile(BaseModel):
    column_name: str
    sample_size: int
    mean: float
    stddev: float
    min: float
    max: float


class DriftOutcome(BaseModel):
    column_name: str
    z_score: float | None = None
    status: ValidationStatus
    message: str
    baseline: BaselineStatistic | None = None
    current_profile: NumericProfile | None = None
    severity: ValidationSeverity = ValidationSeverity.medium


class RunnerSummary(BaseModel):
    processed_contracts: int = 0
    generated_reports: int = 0
    failed_contracts: int = 0
    errored_checks: int = 0
    failed_checks: int = 0
    warned_checks: int = 0
    passed_checks: int = 0
    report_paths: list[str] = Field(default_factory=list)
    contract_errors: list[dict[str, Any]] = Field(default_factory=list)
