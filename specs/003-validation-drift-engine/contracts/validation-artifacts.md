# Contract Interfaces — Validation Artifacts

## 1) Validation Runner Interface

- **Entry point**: `contracts/runner.py`
- **Inputs**:
  - `generated_contracts/*.yaml`
  - `outputs/.../*.jsonl`
  - `schema_snapshots/baselines.json` (read/update)
- **Outputs**:
  - `validation_reports/{contract_id}_{timestamp}.json`

## 2) Executable Check Mapping Contract

Generated contract clauses are normalized to executable checks with scope:

- **Field scope**: `type`, `required`, `nullability`, `pattern`, `range`, `enum`
- **Record scope**: `relationship` and cross-field predicates
- **Dataset scope**: `row_count`, `uniqueness`, `referential_integrity`
- **Derived scope**: `drift` checks for numeric fields only

## 3) Validation Report JSON Contract

### Top-level required fields

- `report_id`
- `contract_id`
- `snapshot_id`
- `run_timestamp`
- `total_checks`
- `passed`
- `failed`
- `warned`
- `errored`
- `results`

### Per-result required fields

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

## 4) Drift & Baseline Contract

- Baseline storage file: `schema_snapshots/baselines.json`
- Baseline fields per numeric check target:
  - `mean`, `stddev`, `min`, `max`, `sample_size`, `created_at`, `updated_at`
- Drift computation:
  - z-score = `abs(current_mean - baseline_mean) / baseline_stddev` when `baseline_stddev > 0`
- Classification thresholds:
  - `WARN`: z-score `> 2`
  - `FAIL`: z-score `> 3`
- Baseline update policy:
  - initialize on first successful numeric run
  - immutable in normal mode
  - overwrite only under explicit refresh mode

## 5) Error Classification Contract

- Missing columns: `ERROR`
- Unexpected structural shape: `ERROR`
- Invalid type / violated value constraint: `FAIL`
- Unsupported check type: `ERROR`
- Full run never halts due to per-check failures.

## 6) Determinism Contract

- Unchanged contract + unchanged snapshot => byte-stable report except:
  - `report_id`
  - `run_timestamp`
- Stable check ordering key: `(column_name, check_type, check_id)`
- `sample_failing` selection: deterministic first-N failing records in canonical dataset order
