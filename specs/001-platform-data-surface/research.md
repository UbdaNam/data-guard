# Research: Platform Foundation and Canonical Data Surface

## Decision 1: Canonical metadata format strategy

- Decision: Use YAML for mostly human-maintained registries and JSON for machine-emitted readiness/validation indexes.
- Rationale: YAML improves reviewability for ownership/interfaces; JSON is deterministic for generated status outputs.
- Alternatives considered:
  - All JSON: simpler parser path but less reviewer-friendly for curated registries.
  - All YAML: readable, but less strict for machine output interoperability.

## Decision 2: Authoritative artifact set and location

- Decision: Store all source-of-truth foundation artifacts under `contracts/` at repository root, with operational outputs in canonical output directories.
- Rationale: Keeps governed contract metadata discoverable and consistent with required canonical paths.
- Alternatives considered:
  - Store under `src/contracts/`: mixes runtime code and source-of-truth metadata.
  - Store under `docs/`: weak machine-consumption ergonomics for downstream features.

## Decision 3: Readiness state model

- Decision: Enforce a closed enum for every artifact record:
  - `confirmed_from_repository_evidence`
  - `inferred_from_requirement_document`
  - `blocked_by_missing_upstream_data`
  - `pending_migration_or_normalization`
- Rationale: Prevents ad hoc statuses and enables deterministic downstream logic.
- Alternatives considered:
  - Free-form status strings: flexible but inconsistent across features.
  - Boolean readiness only: insufficient for migration and missing-data scenarios.

## Decision 4: Actual-vs-canonical mismatch handling

- Decision: Preserve canonical filenames/shapes/semantics as platform standard; record mismatches explicitly with migration or normalization requirements.
- Rationale: Satisfies evidence-over-assumption and avoids silent meaning drift.
- Alternatives considered:
  - Auto-remap upstream semantics into canonical model: faster short-term, but introduces hidden business reinterpretation.
  - Delay mismatch capture to later features: breaks foundation compounding requirement.

## Decision 5: Interface representation and versioning

- Decision: Represent inter-system interfaces in versioned YAML entries (`interface_id`, `version`, `producer`, `consumers`, `dataset_refs`, `semantic_contract`).
- Rationale: Provides stable identifiers for future generator/runner/attributor modules.
- Alternatives considered:
  - Markdown-only interface table: readable but weak for direct machine consumption.
  - Per-interface file sprawl: high maintenance overhead for early foundation stage.

## Decision 6: Path validation approach

- Decision: Implement deterministic path validation from canonical inventory with normalized path checks and strict required/optional flags.
- Rationale: Prevents path drift and enables CI enforcement.
- Alternatives considered:
  - Dynamic directory scan without registry: ambiguous and non-authoritative.
  - Hard-coded checks in multiple modules: duplicates logic and increases drift risk.

## Decision 7: Data flow architecture source format

- Decision: Use Mermaid (`contracts/data_flow_architecture.mmd`) as the editable source of architecture truth.
- Rationale: Human-readable, diff-friendly, and directly embeddable in docs/reports.
- Alternatives considered:
  - Binary diagram tools: poor diffability and review friction.
  - No diagram source (text only): weaker comprehension for cross-team consumers.

## Decision 8: Python foundation module boundaries

- Decision: Keep runtime logic in `src/models`, `src/validators`, and `src/cli`; keep product-contract assets in canonical root directories.
- Rationale: Separates implementation behavior from governed artifacts while preserving required canonical layout.
- Alternatives considered:
  - Put all logic in `contracts/*.py`: couples runtime code with source-of-truth data artifacts.
  - Deep package hierarchy now: unnecessary complexity before capability features begin.
