# Research: AI Contract Enforcement Extensions

## Decision 1: Implement AI enforcement as a dedicated orchestrated pipeline behind `contracts/ai_extensions.py`

- **Decision**: Keep `contracts/ai_extensions.py` as a thin CLI boundary and implement feature logic in a new package `src/ai_enforcement/` with modules for loaders, validators, drift, aggregation, rendering, and persistence.
- **Rationale**: Preserves separation of concerns, keeps stable entry point, and enables deterministic unit testing per module while reusing Feature 3 conventions.
- **Alternatives considered**:
  - Extend `contracts/runner.py` directly: rejected (violates Feature 6 boundary and mixes AI with general validation).
  - Place all logic in one script: rejected (poor maintainability and low testability).

## Decision 2: Reuse Feature 3 evidence conventions without replacing Feature 3 runtime

- **Decision**: Reuse typed result/report patterns (`status`, `severity`, deterministic ordering, atomic write strategy) and validator style from Feature 3 modules, but do not invoke or replace the non-AI runner pipeline.
- **Rationale**: Aligns artifact semantics and review workflows while maintaining explicit feature ownership boundaries.
- **Alternatives considered**:
  - Full runtime coupling to Feature 3 engine: rejected (boundary collapse risk, AI-specific requirements differ).
  - Fully independent format: rejected (breaks downstream consistency).

## Decision 3: Deterministic embedding drift via governed signature vectors (no external model dependency)

- **Decision**: Use a deterministic embedding-signature strategy based on normalized text token hashing into a fixed-dimensional vector (e.g., 256 bins) with cosine distance; store algorithm version and dimensions in baseline artifacts.
- **Rationale**: Works in constrained environments with existing dependencies, is reproducible, and supports auditability with stable parameters.
- **Alternatives considered**:
  - External embedding APIs: rejected (network dependency, non-deterministic provider variance).
  - `sentence-transformers`: rejected for baseline plan due to additional heavyweight dependency and runtime variability.

## Decision 4: Baseline and trend storage policy

- **Decision**: Store drift baselines and comparison evidence under `schema_snapshots/ai/{surface_id}/`, and append run-level violation-rate history in `validation_reports/ai_metrics.json` under a bounded `history` section.
- **Rationale**: Uses canonical artifact locations, keeps history colocated with metrics for downstream review, and avoids introducing new top-level storage roots.
- **Alternatives considered**:
  - Separate `ai_baselines/` directory: rejected (unnecessary path proliferation).
  - DB-backed time series: rejected (out of scope for current file-based platform).

## Decision 5: Quarantine write strategy

- **Decision**: Write quarantine output as newline-delimited JSON to `outputs/quarantine/{run_timestamp}_{run_id}.jsonl` using deterministic record order and atomic temp-file replacement.
- **Rationale**: Supports replayability, avoids partial writes, and preserves all invalid prompt inputs without silent drops.
- **Alternatives considered**:
  - Append to a global shared quarantine file: rejected (race conditions, poor run isolation).
  - One file per invalid record: rejected (high file-count overhead).

## Decision 6: Trend calculation approach for violation rates

- **Decision**: Compute per-surface rate as $rate = failures / max(processed, 1)$ and trend over the last `N=10` runs using linear slope on run-indexed rates; include explicit statuses (`insufficient_history`, `stable`, `improving`, `degrading`).
- **Rationale**: Deterministic, simple, interpretable, and robust when history is sparse.
- **Alternatives considered**:
  - EWMA-only trend: rejected as harder to review manually.
  - Calendar-window trend: rejected due to timestamp irregularity and missing-run sensitivity.

## Decision 7: Graceful degradation contract

- **Decision**: Feature run remains successful when optional contexts are absent (Feature 5 outputs, prior metrics history, or baseline), but must emit explicit completeness/status markers; hard fail only when mandatory output safety guarantees cannot be met (e.g., quarantine path unavailable when invalid prompts exist).
- **Rationale**: Meets feature requirements and edge-case expectations while preventing hidden data loss.
- **Alternatives considered**:
  - Fail on any missing optional artifact: rejected (too brittle).
  - Silent skipping: rejected (violates evidence and operability principles).

## Decision 8: Canonical AI artifact contract additions

- **Decision**: Define explicit required fields for AI metrics, AI violations, and drift baseline/comparison records in design artifacts (`contracts/ai-enforcement-artifacts.md` + `data-model.md`).
- **Rationale**: Removes ambiguity from spec and enables deterministic validation and downstream consumption.
- **Alternatives considered**:
  - Keep field definitions implicit in implementation only: rejected (weak governance and reviewability).
