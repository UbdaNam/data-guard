# Quickstart — Validation Execution and Drift Detection Engine

## Prerequisites

- Active branch: `003-validation-drift-engine`
- Python 3.11+
- Feature 1 canonical dataset paths available under `outputs/`
- Feature 2 contracts generated under `generated_contracts/`

## Execute validation

Primary entry point:

1. Run validation orchestration from `contracts/runner.py`.
2. Validate that one report per processed contract is written to `validation_reports/`.
3. Confirm baseline file behavior in `schema_snapshots/baselines.json`:
   - created on first successful numeric-field validation
   - reused (not overwritten) on normal runs
   - overwritten only with explicit baseline-refresh mode

## Expected report contract

Each report must contain:

- `report_id`, `contract_id`, `snapshot_id`, `run_timestamp`
- `total_checks`, `passed`, `failed`, `warned`, `errored`
- `results[]` with required fields:
  - `check_id`
  - `column_name`
  - `check_type`
  - `status` (`PASS`, `FAIL`, `WARN`, `ERROR`)
  - `actual_value`
  - `expected`
  - `severity`
  - `records_failing`
  - `sample_failing`
  - `message`

## Determinism checks

- Re-run validation on unchanged inputs.
- Confirm payload is identical except `report_id` and `run_timestamp`.
- Confirm stable result ordering and deterministic `sample_failing` (first-N failing records in canonical order).

## Failure-handling checks

- Missing column -> result status `ERROR`.
- Invalid type/constraint mismatch -> result status `FAIL`.
- Unexpected structure -> result status `ERROR`.
- Partial failures do not halt run; all attempted checks appear in `results[]`.
