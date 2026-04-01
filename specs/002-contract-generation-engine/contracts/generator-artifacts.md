# Contract Interfaces — Generator Artifacts

## Primary Output Contracts

### 1) Bitol-Compatible Contract YAML

- **Path**: `generated_contracts/week3_extractions.yaml`, `generated_contracts/week5_events.yaml`
- **Contains**:
  - dataset identity + canonical schema target
  - structural profile summary
  - invariant clauses (inferred + requirement-defined)
  - mismatch evidence
  - downstream context annotation
  - generation metadata

### 1b) Generation Metadata JSON

- **Path**: `generated_contracts/week3_extractions.metadata.json`, `generated_contracts/week5_events.metadata.json`
- **Contains**:
  - run_id and generated_at
  - input artifact and record count diagnostics
  - malformed line diagnostics
  - deterministic signature
  - quality issue list

### 2) dbt-Compatible Schema YAML

- **Path**: `generated_contracts/week3_extractions_dbt.yml`, `generated_contracts/week5_events_dbt.yml`
- **Contains**:
  - model/column definitions
  - supported mappings from primary contract clauses:
    - required/not null -> `not_null`
    - accepted values/enums -> `accepted_values`
    - relationships/referential integrity -> `relationships`
    - uniqueness -> `unique`
  - unsupported mapping notes when a clause has no dbt counterpart

## Determinism Contract

- Stable ordering of datasets, fields, and clauses across unchanged-input runs.
- Canonical serialization settings for YAML output.
- Permitted non-deterministic fields:
  - `generated_at`
  - explicitly versioned metadata fields

## Error/Status Contract

- Missing inputs and malformed lines are represented in generation metadata and status records.
- Canonical mismatch records are always emitted when observed data diverges from canonical target.
- Weak semantic confidence never blocks structural baseline generation.
- Dataset-level generation outcome summary is emitted in `validation_reports/readiness_index.json`.
