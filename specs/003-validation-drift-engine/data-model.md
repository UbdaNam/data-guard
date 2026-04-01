# Data Model — Validation Execution and Drift Detection Engine

## 1) ValidationRun

- **Description**: Execution context across one or more contracts.
- **Fields**:
  - `run_id` (string, UUID-like)
  - `run_timestamp` (ISO-8601 string)
  - `contract_ids` (array[string])
  - `snapshot_ids` (array[string])
  - `status` (enum: `completed`, `completed_with_errors`)

## 2) ExecutableCheck

- **Description**: Normalized check compiled from contract YAML.
- **Fields**:
  - `check_id` (string, unique within contract)
  - `contract_id` (string)
  - `column_name` (string | null)
  - `check_type` (enum: `type`, `required`, `nullability`, `pattern`, `range`, `enum`, `relationship`, `row_count`, `uniqueness`, `referential_integrity`, `drift`)
  - `scope` (enum: `field`, `record`, `dataset`)
  - `expected` (object)
  - `severity` (enum: `low`, `medium`, `high`, `critical`)

## 3) ValidationResult

- **Description**: Per-check result row written to report.
- **Fields**:
  - `check_id` (string)
  - `column_name` (string | null)
  - `check_type` (string)
  - `status` (enum: `PASS`, `FAIL`, `WARN`, `ERROR`)
  - `actual_value` (object | scalar | null)
  - `expected` (object | scalar | null)
  - `severity` (string)
  - `records_failing` (integer, >=0)
  - `sample_failing` (array[object], deterministic first-N)
  - `message` (string)

## 4) ValidationReport

- **Description**: Canonical output artifact per contract execution.
- **Path pattern**: `validation_reports/{contract_id}_{timestamp}.json`
- **Fields**:
  - `report_id` (string)
  - `contract_id` (string)
  - `snapshot_id` (string)
  - `run_timestamp` (string)
  - `total_checks` (integer)
  - `passed` (integer)
  - `failed` (integer)
  - `warned` (integer)
  - `errored` (integer)
  - `results` (array[ValidationResult])

## 5) BaselineStatistic

- **Description**: Drift reference state for numeric field checks.
- **Storage path**: `schema_snapshots/baselines.json`
- **Key**: `{contract_id}:{column_name}:drift_mean`
- **Fields**:
  - `contract_id` (string)
  - `column_name` (string)
  - `mean` (number)
  - `stddev` (number, >=0)
  - `min` (number)
  - `max` (number)
  - `sample_size` (integer, >0)
  - `created_at` (ISO-8601 string)
  - `updated_at` (ISO-8601 string)

## Relationships

- `ValidationRun` 1..\* -> `ValidationReport`
- `ValidationReport` 1..\* -> `ValidationResult`
- `ExecutableCheck` 1..1 -> `ValidationResult` (attempted checks always emit one result)
- `ExecutableCheck` (numeric drift) 0..1 -> `BaselineStatistic`

## State Transitions

- `BaselineStatistic`:
  - `absent` -> `initialized` (first successful numeric run)
  - `initialized` -> `refreshed` (only explicit baseline-refresh mode)
  - `initialized` -> `initialized` (normal runs, no overwrite)

- `ValidationResult.status`:
  - `PASS` | `FAIL` | `WARN` | `ERROR`
  - Missing column: `ERROR`
  - Invalid type/constraint mismatch: `FAIL`
  - Unexpected structure/unsupported check: `ERROR`
