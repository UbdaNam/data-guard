# Feature Specification: Validation Execution and Drift Detection Engine

**Feature Branch**: `003-validation-drift-engine`  
**Created**: 2026-04-02  
**Status**: Draft  
**Input**: User description: "Create Feature 3: Validation Execution and Drift Detection Engine for The Data Contract Enforcer."

## Clarifications

### Session 2026-04-02

- Q: How are validation categories defined to remove ambiguity? → A: Structural checks include type/required/nullability/pattern, semantic checks include ranges/enums/relationships, and dataset-level checks include row count/uniqueness/referential integrity.
- Q: How are nested fields validated and how are missing columns handled? → A: Use schema-walk for objects and wildcard iteration for arrays (e.g., `items[*].price`); missing columns return `ERROR` (not `FAIL`) and execution continues.
- Q: How is drift detection behavior defined? → A: Baseline is created on first successful numeric-field run, stored in `schema_snapshots/baselines.json` with mean/stddev/min/max, deviation uses z-score, WARN is `>2 stddev`, FAIL is `>3 stddev`, and baseline is immutable unless explicitly overridden.
- Q: What is the required validation report format? → A: Output schema is fixed, every check emits a result entry, partial failures are included, and each result contains `check_id`, `column_name`, `check_type`, `status`, `actual_value`, `expected`, `severity`, `records_failing`, `sample_failing`, and `message`.
- Q: How is failure handling classified and what report completeness is required? → A: The system never crashes due to bad data; missing columns are `ERROR`, invalid types are `FAIL`, unexpected structure is `ERROR`, partial execution is acceptable, and reports must include all attempted checks.
- Q: What determinism guarantees are required for reports and check diagnostics? → A: Same input data plus same contract must produce identical report content except `report_id` and timestamp fields; check ordering is stable and `sample_failing` is deterministic using first-N canonical ordering.

## User Scenarios & Testing _(mandatory)_

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.

  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - Execute Contract Validation Runs (Priority: P1)

As a data platform operator, I can run validation against governed datasets using generated contracts so that schema, constraint, and semantic violations are detected before downstream use.

**Why this priority**: Contract enforcement is the core value of the platform; without execution, contracts remain passive documents.

**Independent Test**: Run validation for one contract and one dataset snapshot and verify the report includes field-level and dataset-level check outcomes with pass/fail/error status.

**Acceptance Scenarios**:

1. **Given** a valid generated contract and matching canonical dataset snapshot, **When** validation runs, **Then** a structured report is produced with check totals and detailed per-check results.
2. **Given** missing fields or invalid records in the dataset, **When** validation runs, **Then** failed and errored checks are recorded without stopping the full run.

---

### User Story 2 - Detect Statistical Drift (Priority: P2)

As a data quality owner, I can compare current statistics to baseline behavior so that distribution shifts are surfaced early as warnings or failures.

**Why this priority**: Silent scale and distribution changes can break downstream assumptions even when schema-level checks pass.

**Independent Test**: Execute a first run to create baseline statistics, then execute a second run with shifted values and verify drift checks emit WARN above 2 standard deviations and FAIL above 3 standard deviations.

**Acceptance Scenarios**:

1. **Given** no existing baseline for a contract field, **When** validation runs, **Then** baseline statistics are initialized and persisted for future comparison.
2. **Given** an existing baseline and a shifted dataset snapshot, **When** validation runs, **Then** drift severity is classified using the defined standard-deviation thresholds.

---

### User Story 3 - Produce Downstream-Ready Validation Artifacts (Priority: P3)

As downstream feature owners, we can consume deterministic, machine-readable validation reports so that attribution, schema evolution, AI checks, and reporting features can build on trusted outputs.

**Why this priority**: This feature is an upstream dependency for later platform capabilities and must emit stable artifacts.

**Independent Test**: Run validation twice on unchanged input and verify report structure is stable, canonical input/output locations are honored, and downstream-required fields are present.

**Acceptance Scenarios**:

1. **Given** canonical contract and dataset paths, **When** validation runs, **Then** the report and baseline artifacts are generated in canonical locations with complete schema fields.
2. **Given** partial validation failures, **When** run completes, **Then** overall execution still returns a complete report containing passed, failed, warned, and errored counts.

---

### Edge Cases

- Contract file is unreadable or malformed; run records contract-level error result and continues processing other contracts.
- Dataset path exists but file includes malformed JSONL lines; valid lines are still validated and malformed line errors are captured.
- Required field or column is fully missing from snapshot; check produces deterministic `ERROR` entries without runtime crash.
- Baseline exists but is incomplete for some fields; available comparisons run, missing baseline entries are initialized.
- Contract includes unsupported check type; report includes explicit errored result with reason `unsupported_check_type`.
- Snapshot contains zero valid rows; dataset-level checks and drift checks return deterministic results with clear zero-data diagnostics.
- Missing column for a configured check is emitted as `ERROR` (never `FAIL`), and all remaining checks still execute.
- Invalid type values for a defined type constraint are emitted as `FAIL` results.
- Unexpected structural shapes (for example scalar where object/array is required) are emitted as `ERROR` results.
- Partial execution is acceptable when some checks error, but report completeness remains mandatory for all attempted checks.
- Repeated runs with identical input contract and snapshot produce identical results payloads except `report_id` and timestamp fields.

## Requirements _(mandatory)_

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: The feature MUST provide a validation execution entry point at `contracts/runner.py`.
- **FR-002**: The feature MUST discover and execute checks from generated contract artifacts located under `generated_contracts/*.yaml`.
- **FR-003**: The feature MUST load governed dataset snapshots from canonical repository paths defined by Feature 1 inventories.
- **FR-004**: The feature MUST execute, at minimum, these validation categories when defined in a contract: field-level checks (required, type, pattern), range checks, enum checks, cross-field checks, and dataset-level checks (row count, uniqueness).
- **FR-005**: The feature MUST perform statistical drift checks for numeric fields against stored baseline statistics.
- **FR-006**: Validation categories MUST be explicitly enforced as follows: structural checks (`type`, `required`, `nullability`, `pattern`), semantic checks (`range`, `enum`, `relationship`), and dataset-level checks (`row_count`, `uniqueness`, `referential_integrity`).
- **FR-007**: Nested validation MUST use schema-walk for object paths and wildcard iteration for arrays (for example `items[*].price`) to ensure deterministic and complete nested-field coverage.
- **FR-008**: Missing columns referenced by checks MUST produce result status `ERROR` (not `FAIL`) and MUST NOT terminate execution of remaining checks.
- **FR-009**: On the first successful run with numeric observations for a field, the feature MUST initialize and persist baseline statistics in `schema_snapshots/baselines.json` including `mean`, `stddev`, `min`, and `max`.
- **FR-010**: Drift detection MUST apply only to numeric fields and MUST compute deviation using z-score: `abs(current_mean - baseline_mean) / baseline_stddev` when `baseline_stddev > 0`.
- **FR-011**: Drift severity thresholds MUST be: `WARN` when deviation `> 2` and `FAIL` when deviation `> 3`.
- **FR-012**: Persisted baseline statistics MUST NOT be overwritten during normal validation runs unless an explicit baseline-refresh mode is requested.
- **FR-013**: Validation execution MUST be fault-tolerant: missing columns, malformed records, unsupported checks, and other per-check failures MUST be captured as structured result entries and MUST NOT terminate the full run.
- **FR-013a**: The validation system MUST never crash due to bad input data quality; execution-level failures MUST degrade to structured check-level `ERROR` results whenever possible.
- **FR-013b**: Invalid type checks MUST be classified as `FAIL` (constraint violation), while unexpected structural shapes MUST be classified as `ERROR` (execution/interpretation failure).
- **FR-014**: Each run MUST produce a complete machine-readable report at `validation_reports/{contract_id}_{timestamp}.json`.
- **FR-015**: Report payload MUST include these top-level fields: `report_id`, `contract_id`, `snapshot_id`, `run_timestamp`, `total_checks`, `passed`, `failed`, `warned`, `errored`, and `results[]`.
- **FR-016**: Report output schema is fixed for this feature version and MUST match the spec-defined schema exactly.
- **FR-017**: Every executed or attempted check MUST produce one `results[]` entry; partial failures MUST be included and MUST NOT be skipped.
- **FR-017a**: Report completeness is mandatory even for partial execution; all attempted checks MUST appear in `results[]` with final status (`PASS`, `FAIL`, `WARN`, or `ERROR`).
- **FR-018**: Each `results[]` entry MUST contain: `check_id`, `column_name`, `check_type`, `status` (`PASS`, `FAIL`, `WARN`, `ERROR`), `actual_value`, `expected`, `severity`, `records_failing`, `sample_failing`, and `message`.
- **FR-019**: Totals in report summary fields MUST reconcile exactly with the statuses present in `results[]`.
- **FR-020**: For unchanged contract and snapshot inputs, validation output MUST be byte-stable except for explicitly time-derived fields `report_id` and `run_timestamp`.
- **FR-020a**: Check execution and `results[]` ordering MUST be stable across unchanged runs using deterministic ordering keys.
- **FR-020b**: `sample_failing` selection MUST be deterministic using first-N failing records in canonical dataset order.
- **FR-021**: The feature MUST preserve compounding behavior by consuming Feature 2 generated contracts and producing report artifacts consumable by Features 4 through 7 without schema translation.
- **FR-022**: Runs MUST process all discovered or requested contracts independently so that a failure in one contract does not block reports for other contracts.

### Key Entities _(include if feature involves data)_

- **Validation Run**: A single execution context over one or more contracts and dataset snapshots; includes run timestamp, execution scope, and aggregated status totals.
- **Validation Report**: Machine-readable artifact for one contract execution containing summary counters and detailed check-level diagnostics.
- **Validation Result**: Per-check outcome entry including check type, scope, status (`PASS`, `FAIL`, `WARN`, `ERROR`), observed metrics, expected rule, and diagnostic reason.
- **Baseline Statistic**: Persisted reference distribution attributes for a numeric field (`mean`, `stddev`, `min`, `max`) used for drift comparison.
- **Dataset Snapshot**: Immutable input slice from canonical dataset path used for a specific validation run.

### Data Contract & Evidence Artifacts _(mandatory for this project)_

- **Canonical Schema Asset(s)**: `generated_contracts/*.yaml` produced by Feature 2; versioned by contract metadata and consumed as authoritative validation rule source.
- **Lineage Mapping Asset(s)**: `contracts/interface_registry.yaml` and `contracts/schema_ownership_map.yaml` remain upstream references for downstream interpretation of violations.
- **Validation Output Artifact(s)**: `validation_reports/{contract_id}_{timestamp}.json` produced by the validation runner entry point.
- **Violation Record Artifact(s)**: Check-level failures and errors are embedded in `results[]` and are the source signal for Feature 4 attribution workflows.
- **Schema Drift/Mismatch Evidence**: Drift status and deviation diagnostics are captured per numeric-field check in report `results[]` using z-score thresholding; baseline state is persisted in `schema_snapshots/baselines.json` and remains immutable unless explicit refresh is requested.

### Downstream Impact _(mandatory for schema/interface changes)_

- **Affected Consumers**: Violation Attribution (Feature 4), Schema Evolution Analyzer (Feature 5), AI Extensions (Feature 6), Enforcer Report (Feature 7), plus platform operators.
- **Blast Radius**: Incomplete or non-deterministic report schema breaks downstream parsing, reduces trust in enforcement signals, and delays violation response.
- **Migration Plan**: Preserve stable report schema for this feature version; additive fields are allowed only when existing required fields and semantics remain unchanged.
- **Compatibility Window**: Backward-compatible report schema is maintained for the remainder of the current feature train through Feature 7 completion.

## Success Criteria _(mandatory)_

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: 100% of validation runs produce a report artifact, even when one or more checks encounter errors.
- **SC-002**: For injected schema and constraint violations, at least 95% are surfaced as `FAIL` or `ERROR` results in the same run.
- **SC-003**: For injected numeric distribution shifts, drift checks classify deviations above 2 standard deviations as `WARN` and above 3 standard deviations as `FAIL` with 100% threshold adherence.
- **SC-004**: Report summary counters always reconcile with check-level outcomes (`total_checks = passed + failed + warned + errored`) in 100% of runs.
- **SC-005**: Re-running validation on unchanged inputs yields identical check outcomes and diagnostics, excluding time-derived identifiers.
- **SC-006**: 100% of checks attempted in a run produce a corresponding `results[]` entry, including partial-failure and error scenarios.
- **SC-007**: On unchanged inputs, report payload equivalence is 100% after excluding `report_id` and `run_timestamp`, including stable `results[]` ordering and `sample_failing` values.

## Assumptions

- Contract artifacts generated by Feature 2 are present and readable before validation execution begins.
- Canonical dataset path mappings from Feature 1 remain the authoritative source for snapshot discovery.
- Dataset snapshots are JSONL with one record per line and may contain partial corruption.
- Contract check definitions are treated as authoritative even when sample data appears compliant.
- This feature focuses on execution and reporting, not ownership attribution logic or remediation workflow execution.
- Baseline refresh is an explicit operator action and is disabled by default for routine runs.

## Canonical Structure Notes _(mandatory)_

- Preserves canonical layout by using `contracts/runner.py` as entry point, consuming `generated_contracts/*.yaml`, reading canonical datasets from `outputs/.../*.jsonl`, writing baselines to `schema_snapshots/baselines.json`, and emitting reports to `validation_reports/`.
- No structure deviations are introduced.

## Implementation Prompt Integrity Checklist _(mandatory)_

- [x] Prompt builds on prior approved specs and platform architecture.
- [x] Prompt describes durable product capability, not submission checkpoint milestones.
- [x] Prompt preserves data contract first-class artifact expectations.
