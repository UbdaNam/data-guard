# Research: Violation Attribution and Blast Radius Analysis

## Decision 1: Attribution-eligible validation statuses

- Decision: Attempt attribution for all `FAIL` results plus selected attributable `ERROR` classes: `missing_column`, `unexpected_structure`, and `invalid_type`.
- Rationale: Captures actionable structural/data quality issues while excluding system/runtime failures that do not indicate producer-side schema behavior.
- Alternatives considered:
  - `FAIL` only: simpler but misses meaningful schema-break errors.
  - all `ERROR`: too noisy; includes non-data root causes.

## Decision 2: Mapping validation failures to governed schema anchors

- Decision: Use `column_name` as primary field anchor, parse `check_id` as secondary, and map dataset-level checks to governed dataset/interface constraints when no field anchor exists.
- Rationale: Preserves compatibility with Feature 3 report shapes and supports both field and dataset-level attribution.
- Alternatives considered:
  - rely on `column_name` only: fails for dataset-level checks.
  - rely on `check_id` only: brittle for naming drift.

## Decision 3: Latest Week 4 lineage snapshot selection

- Decision: Select the latest valid snapshot using in-record timestamp fields (`snapshot_timestamp`, `captured_at`, `run_timestamp`) and fall back to deterministic highest valid line index.
- Rationale: Data-driven selection is more reliable than filesystem metadata and still deterministic when timestamps are absent.
- Alternatives considered:
  - filesystem modified time: can drift under copy/sync operations.
  - merge all snapshots: increases ambiguity and non-determinism.

## Decision 4: Traversal strategy and stop conditions

- Decision: BFS upstream traversal from failing schema anchor with stop conditions: external boundary, repository root boundary, no further upstream nodes, and max hop count (default 6).
- Rationale: BFS favors nearest plausible producers and bounded analysis latency.
- Alternatives considered:
  - DFS traversal: deeper branches prioritized over nearest causes.
  - unbounded traversal: non-reviewable output and runtime risk.

## Decision 5: Git history window and enrichment

- Decision: Use last 90 days with max 200 commits per candidate file. Apply line-level blame only when valid source ranges are present.
- Rationale: Bounded and practical for monorepo-scale histories while still capturing likely recent regressions.
- Alternatives considered:
  - full history scan: too expensive and noisy.
  - time-only window without commit cap: unpredictable on high-churn files.

## Decision 6: Confidence scoring model

- Decision: Weighted normalized additive score (0–100): recency (0.30), hop proximity (0.25), file-field directness (0.20), line-level blame availability (0.15), lineage completeness (0.10).
- Rationale: Transparent, tunable, and easy to explain in operational review.
- Alternatives considered:
  - categorical-only confidence bands: insufficient ranking precision.
  - multiplicative probabilistic model: harder to calibrate and explain.

## Decision 7: Blame-chain bounds and deterministic ordering

- Decision: Return 1–5 candidates per attributable violation, sorted by score desc, hops asc, commit time desc, commit hash asc.
- Rationale: Guarantees bounded and reproducible output while preserving candidate diversity.
- Alternatives considered:
  - unbounded candidate list: poor reviewability.
  - fixed single candidate: overclaims certainty.

## Decision 8: Blast radius semantics

- Decision: Compute downstream impact from lineage + Feature 1 interface metadata; direct impact is 1 hop, indirect is >=2 hops; include affected nodes/pipelines/interfaces and estimated impacted records/datasets where inferable.
- Rationale: Keeps impact model explicit and reusable by downstream reporting/prioritization features.
- Alternatives considered:
  - aggregate-only blast metric: loses actionable structure.
  - interface-only impact model: undercounts pipeline/dataset propagation.

## Decision 9: Graceful degradation policy

- Decision: Always emit structured results for attributable violations; when lineage or git evidence is incomplete, lower confidence, include uncertainty reasons, and emit partial blast-radius sections with completeness flags.
- Rationale: Avoids silent data loss and preserves machine-readability for later workflow stages.
- Alternatives considered:
  - hard-fail on missing evidence: blocks operations.
  - omit uncertain fields: makes downstream interpretation ambiguous.

## Decision 10: Violation log persistence strategy

- Decision: Append-safe JSONL writer to `violation_log/violations.jsonl` with deterministic `violation_id` hashing and duplicate suppression on reruns.
- Rationale: Supports repeatable batch execution without record inflation.
- Alternatives considered:
  - rewrite entire log each run: expensive and merge-unfriendly.
  - blind append without dedupe: duplicates on rerun reduce trust.
