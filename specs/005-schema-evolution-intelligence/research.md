# Research: Schema Evolution Intelligence

## Decision 1: Snapshot discipline and write triggers

- Decision: Write snapshots automatically after successful contract generation and allow explicit snapshot capture through `contracts/schema_analyzer.py --snapshot`.
- Rationale: Ensures continuous schema history while preserving operator control for backfill/recovery.
- Alternatives considered:
  - analyzer-only snapshot writes: can miss intermediate schema states.
  - schedule-only snapshots: can drift from actual contract publication events.

## Decision 2: Snapshot source representation

- Decision: Snapshot payload is derived primarily from normalized `generated_contracts/*.yaml`; inferred clause-derived schema hints may be retained as supplemental metadata.
- Rationale: Keeps Feature 2 contracts as canonical schema source while preserving contextual evidence.
- Alternatives considered:
  - inferred-only snapshot model: too lossy for contract-level determinism.
  - raw contract dumps without normalization: unstable diffs and noisy review.

## Decision 3: Snapshot identity and naming

- Decision: Use `schema_snapshots/{contract_id}/snapshot_{timestamp}_{schema_hash}.json` with `snapshot_id=schema_hash` and UTC ISO-8601 timestamps.
- Rationale: Stable identity and deterministic collision handling for unchanged schemas.
- Alternatives considered:
  - timestamp-only naming: cannot detect duplicate/no-change snapshots deterministically.
  - incremental integer versions only: fragile under branch/rebase workflows.

## Decision 4: Duplicate/no-material-change behavior

- Decision: If normalized schema hash equals latest snapshot hash for same contract, do not create a new snapshot; emit `no_material_change` summary state.
- Rationale: Avoids snapshot inflation and keeps audit history meaningful.
- Alternatives considered:
  - always write snapshots: pollutes history and slows diff selection.
  - delete old duplicate snapshots: mutates audit trail.

## Decision 5: Diff mode support

- Decision: Support both latest-vs-previous and explicit two-snapshot comparison by snapshot identifiers.
- Rationale: Covers default operational drift checks and directed investigations.
- Alternatives considered:
  - latest-only: insufficient for root-cause replay.
  - arbitrary only: adds operational friction for routine runs.

## Decision 6: Field matching and rename detection

- Decision: Matching precedence is exact path -> explicit rename map -> heuristic rename above confidence threshold; otherwise fallback to remove+add.
- Rationale: Minimizes false-positive renames while preserving useful automation.
- Alternatives considered:
  - heuristic-first rename detection: too error-prone.
  - no rename detection: loses useful continuity context.

## Decision 7: Nested representation and deterministic diff rendering

- Decision: Flatten nested fields into canonical dotted paths; render diff classes in fixed order (additions, removals, renames, modifications), then path-sorted.
- Rationale: Enables deterministic review and stable machine consumption.
- Alternatives considered:
  - preserve source nesting shape in output: non-deterministic ordering complexity.
  - class-agnostic sort only: less readable change narratives.

## Decision 8: Compatibility taxonomy semantics

- Decision: Use dual-axis compatibility (`is_backward_compatible`, `is_forward_compatible`) and derive verdict: fully-compatible / backward-compatible / forward-compatible / breaking.
- Rationale: Preserves both producer and consumer perspectives.
- Alternatives considered:
  - backward-only model: hides producer risks.
  - forward-only model: hides consumer breakage.

## Decision 9: Migration-impact content requirements

- Decision: Require all migration reports to include human-readable summary, machine-readable structured diff, compatibility verdict, affected consumers, per-consumer failure modes, ordered migration checklist, rollback guidance for breaking changes, and urgency enum (`low|medium|high|critical`).
- Rationale: Ensures operational actionability and downstream automation readiness.
- Alternatives considered:
  - summary-only outputs: insufficient for automation and audit.
  - structured-only outputs: poor usability for human operations.

## Decision 10: Optional Feature 3/4 enrichment policy

- Decision: Schema-diff classification is baseline; Feature 3 validation and Feature 4 violation evidence may adjust severity/confidence/prioritization when present; baseline behavior remains complete when absent.
- Rationale: Keeps schema evolution deterministic and independent while leveraging real operational evidence when available.
- Alternatives considered:
  - always override with context artifacts: unstable severity under sparse evidence.
  - ignore context artifacts entirely: loses actionable prioritization quality.

## Decision 11: Graceful degradation and boundary behavior

- Decision: Feature degrades with explicit completeness flags for missing snapshots, malformed snapshots, missing metadata, and missing optional context; it does not execute validation, perform git-blame attribution, or generate final stakeholder-facing reports.
- Rationale: Preserves clear responsibility boundaries and reliable outputs under partial data conditions.
- Alternatives considered:
  - hard-fail on missing context: blocks operational workflows.
  - silent fallback without flags: reduces trust and auditability.
