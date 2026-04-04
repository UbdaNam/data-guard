# Research: Operational Report Generation

## Decision 1: Implement report generation as a thin CLI boundary plus dedicated `src/reporting/` package

- **Decision**: Keep `contracts/report_generator.py` as stable orchestration entrypoint and place implementation in `src/reporting/` modules (`artifact_loader`, `window_resolver`, `health_score`, `ranking`, `action_generator`, renderers, and enrichment adapter).
- **Rationale**: Preserves contract-level interface stability while enabling isolated, testable domain logic and long-term maintainability.
- **Alternatives considered**:
  - Put all logic inside `contracts/report_generator.py`: rejected (poor testability and coupling).
  - Reuse existing feature modules directly: rejected (violates Feature 7 boundaries and ownership separation).

## Decision 2: Use schema-tolerant normalization for heterogeneous upstream artifacts

- **Decision**: Normalize Feature 3/4/5/6 and Feature 1 metadata into internal typed models with strict timestamp normalization and per-source completeness status.
- **Rationale**: Upstream artifacts may vary slightly by run/version; normalization prevents brittle parsing and supports graceful degradation.
- **Alternatives considered**:
  - Strict hard-fail parse on any shape mismatch: rejected (too fragile for operations).
  - Untyped dict-only ingestion: rejected (high ambiguity and hidden defects).

## Decision 3: Deterministic reporting window resolution

- **Decision**: Support explicit CLI `start/end` bounds; otherwise compute deterministic latest-available window from artifact timestamps with stable tie-breaking by source priority and lexical path.
- **Rationale**: Satisfies FR-027 while ensuring reproducibility across repeated runs.
- **Alternatives considered**:
  - Always use current day window: rejected (ignores artifact recency and can miss latest evidence).
  - Source-specific windows: rejected (produces inconsistent cross-section reporting).

## Decision 4: Data Health Score computation must be exact and centralized

- **Decision**: Implement FR-032 formula in a single `health_score.py` module with explicit rounding and null-score behavior from FR-033.
- **Rationale**: Avoids drift in duplicated computations and keeps auditability straightforward.
- **Alternatives considered**:
  - Approximate weighted-score variants: rejected (violates fixed spec formula).
  - Compute in renderer layer: rejected (mixes calculation with presentation).

## Decision 5: Rank violations/schema changes/actions with stable tuple sorting

- **Decision**: Define explicit numeric ranks and tuple comparators:
  - Violations: severity, recurrence, recency, stable ID.
  - Schema changes: breaking-first, impact, recency, stable ID.
  - Actions: priority score, severity, recurrence, recency, stable ID.
- **Rationale**: Guarantees deterministic output ordering required by FR-039.
- **Alternatives considered**:
  - Heuristic free-text ranking: rejected (non-reproducible).
  - Severity-only ranking: rejected (insufficient signal for operational prioritization).

## Decision 6: Generate actions from consolidated issue keys with explicit owner/verification fields

- **Decision**: Consolidate repeated issues by `(issue_type, affected_surface, field_or_interface)` and produce one evidence-linked action with ownership context and verification steps.
- **Rationale**: Reduces noise while preserving accountability and execution clarity.
- **Alternatives considered**:
  - One action per incident: rejected (too noisy and repetitive).
  - Generic high-level actions only: rejected (fails FR-035 specificity).

## Decision 7: OpenRouter-only optional enrichment with strict fallback

- **Decision**: Optional enrichment uses only `OPENROUTER_API_KEY`, `OPENROUTER_BASE_URL`, `OPENROUTER_MODEL`; if missing/invalid/failing, emit deterministic templated narrative.
- **Rationale**: Meets FR-041..FR-046 while preserving availability and determinism.
- **Alternatives considered**:
  - Multiple LLM providers: rejected (violates provider constraint).
  - Mandatory LLM for markdown quality: rejected (violates non-blocking requirement).

## Decision 8: Evidence-grounding guardrail for optional LLM output

- **Decision**: LLM responses are constrained to summarize already structured report content; post-processor rejects unsupported claims and falls back.
- **Rationale**: Prevents hallucinated incidents/actions and preserves trust.
- **Alternatives considered**:
  - Accept raw LLM text directly: rejected (risk of fabricated claims).
  - Disable enrichment entirely: rejected (feature requires optional capability).

## Decision 9: Environment configuration via `.env.example` documentation + runtime environment lookup

- **Decision**: Add/update repository `.env.example` with OpenRouter variables and optional usage notes; runtime reads process environment only.
- **Rationale**: Clear onboarding without embedding secrets or model values in code.
- **Alternatives considered**:
  - Config file with secrets in repo: rejected (security and governance risk).
  - Hardcoded defaults for model/base URL: rejected (violates FR-020/FR-043).

## Decision 10: Partial input handling is explicit and section-preserving

- **Decision**: Missing source families downgrade section completeness to `insufficient_evidence` while preserving all required sections in JSON and Markdown.
- **Rationale**: Aligns with FR-040 and ensures operational continuity.
- **Alternatives considered**:
  - Omit unavailable sections: rejected (breaks required structure and comparability).
  - Fail entire run for any missing family: rejected (too brittle for production operations).
