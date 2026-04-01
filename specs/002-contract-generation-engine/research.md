# Phase 0 Research — Contract Generation Engine

## Decision 1: JSONL loading strategy

- **Decision**: Use line-by-line JSONL parsing with malformed-line tolerance and per-line error capture.
- **Rationale**: Preserves generation progress for partially bad files while keeping evidence for remediation.
- **Alternatives considered**:
  - Fail-fast on first malformed line (rejected: too brittle for upstream variance).
  - Pre-convert to tabular format (rejected: adds lossy transform and complexity).

## Decision 2: Structural profiling model

- **Decision**: Build a unioned field graph across records with nested path support (`a.b.c`) and null/type frequency statistics.
- **Rationale**: Supports nested schema handling and stable field-level contract generation.
- **Alternatives considered**:
  - First-record schema only (rejected: misses late-appearing fields).
  - Fully flatten everything immediately (rejected: weak parent-child semantics).

## Decision 3: Statistical profiling scope

- **Decision**: Profile numeric distributions (min/max/mean), sparsity, uniqueness indicators, and categorical frequencies for enum candidacy.
- **Rationale**: Enough signal for practical invariant synthesis without heavy compute.
- **Alternatives considered**:
  - Full distribution histograms for all fields (rejected: disproportionate complexity).
  - No statistics (rejected: weak clause quality).

## Decision 4: Invariant synthesis precedence

- **Decision**: Merge inferred invariants with requirement-defined invariants and preserve requirement-defined constraints even when samples do not violate them.
- **Rationale**: Aligns to spec requirement for governed constraints over transient observations.
- **Alternatives considered**:
  - Data-only inferred rules (rejected: drops known policy requirements).
  - Requirement-only rules (rejected: loses discovered quality opportunities).

## Decision 5: Weak semantic confidence handling

- **Decision**: Never invent business meaning; emit explicit uncertainty annotations and optional machine-readable placeholders.
- **Rationale**: Maintains trust and supports future human/LLM enrichment.
- **Alternatives considered**:
  - Auto-semantic guess from naming heuristics only (rejected: high false inference risk).
  - Drop uncertain fields from output (rejected: blocks structural baseline).

## Decision 6: Lineage-aware context injection

- **Decision**: Inject downstream systems, consumed fields, likely breaking fields, and change sensitivity using Feature 1 registry/ownership assets plus Week 4 lineage snapshots when available.
- **Rationale**: Enables downstream blast-radius and schema evolution features without executing them in Feature 2.
- **Alternatives considered**:
  - Add downstream context only in later features (rejected: duplicates discovery work).

## Decision 7: Output rendering and portability

- **Decision**: Primary Bitol-compatible YAML contracts with dbt YAML counterparts for supported mappings (`not_null`, `accepted_values`, `relationships`, `unique`).
- **Rationale**: Keeps enforcement-ready and analytics-tooling-ready artifacts in sync.
- **Alternatives considered**:
  - Single format only (rejected: insufficient downstream interoperability).

## Decision 8: Deterministic writing

- **Decision**: Stable ordering and canonical serialization; only timestamp/version metadata is allowed to differ across unchanged-input runs.
- **Rationale**: Enables human review and reliable diffs.
- **Alternatives considered**:
  - Unordered native serialization (rejected: noisy diffs and weak operability).

## Decision 9: Extensibility architecture

- **Decision**: Dataset-config-driven pipeline with shared modules (`loader -> profile -> infer -> synthesize -> inject -> render -> write`) and no per-dataset forks.
- **Rationale**: Supports adding week1/week2/week4/traces by configuration and artifact registration.
- **Alternatives considered**:
  - Per-dataset scripts (rejected: scaling and maintenance risk).
