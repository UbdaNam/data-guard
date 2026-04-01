# Phase 0 Research — Validation Execution and Drift Detection Engine

## Decision 1: JSONL processing mode

- **Decision**: Use streaming JSONL ingestion as default with optional chunked aggregation for heavy dataset-level metrics.
- **Rationale**: Meets large-file constraints without memory spikes and supports deterministic record ordering.
- **Alternatives considered**:
  - Full DataFrame materialization (rejected: memory pressure on large snapshots)
  - External processing engine dependency (rejected: unnecessary complexity for current scope)

## Decision 2: Internal check representation

- **Decision**: Compile contract clauses into a normalized internal `ExecutableCheck` model with deterministic keys.
- **Rationale**: Decouples contract YAML shape from execution logic and guarantees stable ordering.
- **Alternatives considered**:
  - Execute directly from raw clause dictionaries (rejected: fragile and harder to validate)
  - Separate models per clause type only (rejected: increases orchestration complexity)

## Decision 3: Nested field evaluation strategy

- **Decision**: Schema-walk objects and wildcard-iterate arrays (`items[*].field`) with canonical traversal order.
- **Rationale**: Preserves semantic intent for nested schemas while enabling deterministic result generation.
- **Alternatives considered**:
  - Fully flatten and treat arrays as opaque (rejected: loses array element validation)
  - Dynamic runtime path expansion with ad hoc ordering (rejected: nondeterminism risk)

## Decision 4: Drift computation

- **Decision**: Drift applies only to numeric fields using z-score `abs(current_mean - baseline_mean) / baseline_stddev` when `baseline_stddev > 0`.
- **Rationale**: Aligns with spec threshold policy and enables consistent WARN/FAIL classification.
- **Alternatives considered**:
  - Distribution-shape tests (KS, PSI) (deferred: not required in feature scope)
  - Percent-change only (rejected: less robust across scales)

## Decision 5: Baseline persistence policy

- **Decision**: Store baselines in `schema_snapshots/baselines.json`; initialize on first successful numeric run; immutable by default unless explicit refresh mode.
- **Rationale**: Provides reproducible drift reference and protects baseline integrity.
- **Alternatives considered**:
  - Baseline per-run snapshots only (rejected: weak long-term comparison)
  - Auto-overwrite each successful run (rejected: would erase drift signal)

## Decision 6: Failure classification and resilience

- **Decision**: Missing columns and unexpected structure -> `ERROR`; invalid type/value constraints -> `FAIL`; runner never halts full run.
- **Rationale**: Matches clarified contract semantics and supports complete report generation.
- **Alternatives considered**:
  - Treat all anomalies as `FAIL` (rejected: conflates execution errors with contract violations)
  - Fail-fast execution (rejected: violates completeness requirement)

## Decision 7: Deterministic report generation

- **Decision**: Byte-stable report payload for unchanged inputs except `report_id` and `run_timestamp`; deterministic `sample_failing` from first-N failures in canonical order.
- **Rationale**: Required for downstream reproducibility and diff stability.
- **Alternatives considered**:
  - Random failure samples (rejected: nondeterministic)
  - Unordered map/list serialization (rejected: unstable outputs)

## Decision 8: Fixed downstream report schema

- **Decision**: Enforce strict fixed top-level and per-result fields, plus reconciliation validation (`total_checks = passed + failed + warned + errored`).
- **Rationale**: Supports direct consumption by Features 4–7 without translation.
- **Alternatives considered**:
  - Flexible optional result fields (rejected: downstream fragility)
  - Multiple report schema versions in this feature (deferred: out of scope)
