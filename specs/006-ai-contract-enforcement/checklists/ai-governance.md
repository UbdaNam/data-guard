# AI Governance Requirements Checklist: AI Contract Enforcement Extensions

**Purpose**: Validate the quality of AI-governed requirements coverage, clarity, measurability, and boundary definitions for Feature 6.
**Created**: 2026-04-04
**Feature**: [../spec.md](../spec.md)

**Note**: This checklist evaluates requirement quality only (completeness, clarity, consistency, measurability, and coverage).

## Requirement Completeness

- [ ] CHK001 Are all minimum governed AI surfaces explicitly and exhaustively enumerated (prompt inputs, Week 2 outputs, trace exports, and embedding drift surface), including version boundaries? [Completeness, Spec §FR-016]
- [ ] CHK002 Are required prompt-input quarantine fields (record ID, schema version, failure reasons, ingestion timestamp, source path) explicitly specified rather than implied? [Gap, Spec §FR-003]
- [ ] CHK003 Are required AI metrics fields in `validation_reports/ai_metrics.json` fully defined (totals, denominators, rates, trend window metadata, and run identifiers)? [Gap, Spec §FR-008, Spec §FR-005]
- [ ] CHK004 Are AI violation record required fields under `violation_log/` fully defined for prompt/output/trace/drift classes? [Gap, Spec §FR-009]
- [ ] CHK005 Are explicit requirements present for handling unreadable/corrupt baseline artifacts and preserving run continuity semantics? [Gap, Spec Edge Cases, Spec §FR-007]

## Requirement Clarity

- [ ] CHK006 Is “governed prompt input schema” defined with unambiguous rule sources, version selection logic, and tie-break behavior for concurrent versions? [Clarity, Spec §FR-002]
- [ ] CHK007 Is “structured Week 2 output schema conformance” defined with precise pass/fail criteria for unknown fields, nullability, and nested-object depth constraints? [Clarity, Spec §FR-004]
- [ ] CHK008 Is “violation rates over time” quantified with explicit interval definitions, aggregation grain, and clock/bucket rules? [Ambiguity, Spec §FR-005]
- [ ] CHK009 Is quarantine path behavior sufficiently precise (timestamp format, collision handling, and ordering guarantees) to ensure deterministic reviewability? [Clarity, Spec §FR-003]
- [ ] CHK010 Is “approved AI-relevant text surface” selection criteria explicitly defined so drift scope cannot vary by implementer interpretation? [Ambiguity, Spec §FR-007, Spec §FR-016]

## Requirement Consistency

- [ ] CHK011 Are reuse requirements for Features 1–5 consistent with separation boundaries so Feature 6 consumes upstream artifacts without redefining ownership or schema authorities? [Consistency, Spec §FR-012, Spec §FR-013, Spec §FR-014, Spec §FR-015, Spec Responsibility Boundaries]
- [ ] CHK012 Do out-of-scope boundaries align across Functional Requirements and Responsibility Boundaries for attribution, schema evolution classification, and final reporting exclusions? [Consistency, Spec §FR-022, Spec §FR-023, Spec Responsibility Boundaries]
- [ ] CHK013 Are canonical artifact path requirements consistent between Functional Requirements and Canonical Structure Notes for quarantine, metrics, violations, drift artifacts, and optional prompt schemas? [Consistency, Spec §FR-003, Spec §FR-008, Spec §FR-009, Spec §FR-010, Spec Canonical Structure Notes]

## Acceptance Criteria Quality

- [ ] CHK014 Are prompt-input outcomes measurable with explicit acceptance criteria for quarantine rate, invalid-record accounting, and no-loss reconciliation between input and outputs? [Measurability, Spec §SC-001]
- [ ] CHK015 Are structured-output and trace outcome criteria measurable with defined formulas for conformance rates and denominator handling under partial ingestion? [Measurability, Spec §SC-002, Spec §SC-003]
- [ ] CHK016 Are drift outcomes measurable with explicit criteria distinguishing baseline-created, baseline-compared, and comparison-deferred states? [Measurability, Spec §SC-004]
- [ ] CHK017 Is “90% of incidents traceable without manual reconstruction” supported by objective evidence rules and audit sampling method definitions? [Ambiguity, Spec §SC-007]

## Scenario Coverage

- [ ] CHK018 Are requirements explicitly defined for invalid prompt input quarantine flows, including downstream visibility and retry/reprocessing eligibility semantics? [Coverage, Spec §FR-003, Spec User Story 1]
- [ ] CHK019 Are requirements explicitly defined for missing prior metrics history when computing trend outputs, including initialization behavior and status signaling? [Gap, Spec §FR-005, Spec §FR-008]
- [ ] CHK020 Are requirements explicitly defined for missing or low-volume drift samples, including defer/fail/fallback decision policy and evidence output? [Coverage, Spec Edge Cases, Spec §FR-007]
- [ ] CHK021 Are requirements explicitly defined for absent Feature 5 context so the run produces complete AI outputs with explicit context-completeness markers? [Coverage, Spec Edge Cases, Spec §FR-015]

## Edge Case Coverage

- [ ] CHK022 Are conflicting schema-version applicability cases for prompt inputs explicitly resolved (latest-wins, strict version pin, or compatibility matrix)? [Edge Case, Spec Edge Cases, Spec §FR-002]
- [ ] CHK023 Are malformed trace timestamp and missing run-id conditions accompanied by explicit requirement language for severity categorization and artifact handling? [Edge Case, Spec Edge Cases, Spec §FR-006, Spec §FR-009]
- [ ] CHK024 Is quarantine-path unavailable behavior fully specified for failure signaling, partial output handling, and rerun safety guarantees? [Edge Case, Spec Edge Cases, Spec §FR-003]

## Non-Functional Requirements

- [ ] CHK025 Are deterministic drift-comparison requirements specified with fixed model/version, preprocessing rules, similarity metric, and threshold governance so outcomes are reviewable over time? [Gap, Spec §FR-007, Spec §FR-010]
- [ ] CHK026 Are artifact durability and reproducibility requirements defined for repeated runs over unchanged inputs (stable ordering, stable IDs, and stable serialization)? [Gap, Spec §FR-008, Spec §FR-009, Spec §FR-010]

## Dependencies & Assumptions

- [ ] CHK027 Are assumptions about Feature 1–3 authority and optional Feature 5 context translated into explicit failure-mode requirements when upstream artifacts are missing, stale, or incompatible? [Assumption, Spec Assumptions, Spec §FR-012, Spec §FR-013, Spec §FR-014, Spec §FR-015]
- [ ] CHK028 Are dependency boundaries explicit about consuming upstream artifact definitions without introducing replacement schemas or duplicate registries? [Dependency, Spec §FR-012, Spec §FR-013]

## Ambiguities & Conflicts

- [ ] CHK029 Is “plain-language operational translation” bounded to machine-readable prerequisites without implying final report generation responsibilities? [Ambiguity, Spec §FR-020, Spec §FR-022]
- [ ] CHK030 Are “real executions or injected test data” requirements accompanied by explicit provenance markers so synthetic evidence cannot be misclassified as production evidence? [Clarity, Spec §FR-021]
