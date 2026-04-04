# Data Model: Operational Report Generation

## 1) `ReportingWindow`

- **Purpose**: Deterministic selection bounds for report evidence inclusion.
- **Fields**:
  - `start` (string, required, UTC ISO-8601)
  - `end` (string, required, UTC ISO-8601)
  - `selection_mode` (enum: `explicit`, `latest_available`)
  - `resolved_from_sources` (array[string], required)
  - `resolution_notes` (array[string], optional)

## 2) `EvidenceReference`

- **Purpose**: Traceability unit for all claims.
- **Fields**:
  - `artifact_path` (string, required)
  - `record_selector` (string, required)
  - `claim_type` (enum: `metric`, `incident`, `schema_change`, `ai_risk`, `action`)

## 3) `SectionCompletenessRecord`

- **Purpose**: Explicit section health and missing-source visibility.
- **Fields**:
  - `section` (enum: `data_health_score`, `violations`, `schema_changes`, `ai_risk`, `recommended_actions`)
  - `status` (enum: `complete`, `partial`, `insufficient_evidence`)
  - `missing_sources` (array[string])
  - `reason` (string|null)

## 4) `DataHealthScore`

- **Purpose**: Deterministic health summary from validation and critical incidents.
- **Fields**:
  - `value` (number|null, range 0..100, 1 decimal)
  - `score_status` (enum: `computed`, `insufficient_evidence`)
  - `check_penalty` (number|null)
  - `critical_penalty` (number|null)
  - `raw_score` (number|null)
  - `formula_version` (string, fixed: `fr032_v1`)
  - `reason` (string|null)

## 5) `ViolationsSummary`

- **Purpose**: Aggregated incident view for reporting window.
- **Fields**:
  - `total` (int)
  - `by_severity` (object)
  - `by_category` (object)
  - `by_surface` (object)
  - `evidence` (array[`EvidenceReference`])

## 6) `TopViolation`

- **Purpose**: Deterministically ranked incident record.
- **Fields**:
  - `rank` (int)
  - `violation_id` (string)
  - `severity` (enum: `critical`, `high`, `medium`, `low`)
  - `recurrence_count` (int)
  - `latest_occurrence` (string, UTC ISO-8601)
  - `affected_surface` (string)
  - `owner` (string, default `unassigned`)
  - `priority_tuple` (array[number|string], serialized comparator values)
  - `evidence` (array[`EvidenceReference`])

## 7) `SchemaChangesSummary`

- **Purpose**: Window-scoped summary of schema evolution impacts.
- **Fields**:
  - `total_changes` (int)
  - `breaking_changes` (int)
  - `non_breaking_changes` (int)
  - `top_changes` (array[`RankedSchemaChange`])
  - `evidence` (array[`EvidenceReference`])

### 7a) `RankedSchemaChange`

- **Fields**:
  - `change_id` (string)
  - `compatibility_verdict` (enum: `breaking`, `warning`, `compatible`, `unknown`)
  - `impact_scope` (enum: `high`, `medium`, `low`, `unknown`)
  - `detected_at` (string)
  - `affected_interface` (string|null)
  - `priority_tuple` (array[number|string])
  - `evidence` (array[`EvidenceReference`])

## 8) `AiRiskSummary`

- **Purpose**: AI reliability and risk snapshot from Feature 6 metrics.
- **Fields**:
  - `quarantine_rate` (number|null)
  - `output_violation_rate` (number|null)
  - `trace_violation_rate` (number|null)
  - `drift_status` (string|null)
  - `trend_status` (enum: `insufficient_history`, `stable`, `improving`, `degrading`, `unknown`)
  - `completeness_flags` (object)
  - `evidence` (array[`EvidenceReference`])

## 9) `RecommendedAction`

- **Purpose**: Consolidated remediation instruction with ownership and verification.
- **Fields**:
  - `action_id` (string, deterministic)
  - `issue_key` (object: `issue_type`, `affected_surface`, `field_or_interface`)
  - `priority_score` (number)
  - `severity` (string)
  - `recurrence_count` (int)
  - `latest_occurrence` (string)
  - `remediation_target` (string)
  - `affected_location` (string)
  - `owner` (string, default `unassigned`)
  - `consumer_impact` (string|null)
  - `verification_step` (string)
  - `aggregate_count` (int)
  - `evidence` (array[`EvidenceReference`])

## 10) `GenerationMetadata`

- **Purpose**: Run metadata and enrichment telemetry.
- **Fields**:
  - `generated_at` (string, UTC ISO-8601)
  - `duration_ms` (int)
  - `input_artifact_counts` (object)
  - `enrichment` (object)
    - `requested` (bool)
    - `provider` (enum: `openrouter`, `none`)
    - `status` (enum: `disabled`, `missing_config`, `failed`, `applied`)
    - `fallback_used` (bool)

## 11) `OperationalReportData`

- **Purpose**: Canonical machine-readable report output at `enforcer_report/report_data.json`.
- **Required top-level key order** (FR-037):
  1. `report_id`
  2. `report_date`
  3. `reporting_window`
  4. `data_health_score`
  5. `section_completeness`
  6. `violations_summary`
  7. `top_violations`
  8. `schema_changes_summary`
  9. `ai_risk_summary`
  10. `recommended_actions`
  11. `evidence_index`
  12. `generation_metadata`

## Relationships

- One `OperationalReportData` has exactly one `ReportingWindow`, one `DataHealthScore`, one `ViolationsSummary`, one `SchemaChangesSummary`, one `AiRiskSummary`, and one `GenerationMetadata`.
- One report has many `TopViolation`, many `RecommendedAction`, and many `EvidenceReference` entries in `evidence_index`.
- `SectionCompletenessRecord` has one record per required report section.

## Deterministic Validation Rules

- `data_health_score.value` must be `null` iff `score_status=insufficient_evidence`.
- Every non-empty claim/action in report sections must include at least one `EvidenceReference`.
- Ranking comparators must produce stable sort output for equal-priority records via deterministic ID tie-break.
- Missing source families must not remove required sections; they must downgrade `SectionCompletenessRecord.status`.
- `generation_metadata.enrichment.fallback_used=true` whenever enrichment is requested but unavailable/failed/invalid.
