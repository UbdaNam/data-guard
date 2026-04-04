# Attribution Requirements Checklist: Violation Attribution and Blast Radius Analysis

**Purpose**: Validate that Feature 4 requirements are complete, clear, consistent, and measurable for attribution and blast-radius specification quality.
**Created**: 2026-04-04
**Feature**: [spec.md](../spec.md)

## Requirement Completeness

- [ ] CHK001 Are attribution eligibility requirements explicit about which validation result statuses trigger attribution attempts? [Completeness, Gap]
- [ ] CHK002 Are non-eligible result classes and skip-reason requirements fully enumerated rather than implied? [Completeness, Spec §FR-006]
- [ ] CHK003 Are rules defined for mapping `check_id` and `column_name` to governed schema elements across field-level and dataset-level checks? [Completeness, Gap]
- [ ] CHK004 Are dataset-level failures without a single field anchor required to map to governed interface/dataset constraints with deterministic fallback behavior? [Completeness, Gap]
- [ ] CHK005 Are attribution preconditions defined so attribution applies only when a violation is connected to a governed dataset, interface, or lineage node? [Completeness, Gap]
- [ ] CHK006 Are required violation record fields complete and non-optional where needed (`violation_id`, `check_id`, `detected_at`, identity anchors, `blame_chain[]`, `blast_radius{}`)? [Completeness, Spec §FR-021-§FR-023]

## Requirement Clarity

- [ ] CHK007 Is the lineage snapshot selection rule quantified (for example, “latest valid Week 4 snapshot” with deterministic tie handling)? [Clarity, Gap]
- [ ] CHK008 Is traversal direction explicitly defined from failing element toward upstream producers with no ambiguity about reverse traversal? [Clarity, Gap]
- [ ] CHK009 Is traversal strategy explicitly defined (for example, breadth-first) rather than left implementation-defined? [Clarity, Gap]
- [ ] CHK010 Are stopping conditions explicitly listed and bounded (external boundary, repository root, no further upstream nodes, max hop count)? [Clarity, Gap]
- [ ] CHK011 Is the recent git history window specified with objective limits (time and/or commit cap)? [Clarity, Gap]
- [ ] CHK012 Are conditions for file-level history vs line-level blame clearly specified, including when source ranges are unavailable? [Clarity, Spec §FR-009-§FR-010]

## Requirement Consistency

- [ ] CHK013 Do attribution-candidate cardinality requirements avoid conflict between “bounded output” and “never zero candidates for attributable violations”? [Consistency, Spec §FR-013-§FR-014]
- [ ] CHK014 Are confidence-scoring requirements consistent between per-candidate confidence and optional `attribution_confidence_summary` semantics? [Consistency, Spec §FR-011, §FR-023-§FR-024]
- [ ] CHK015 Are blast-radius structure requirements consistent across FRs and Key Entities (affected nodes/pipelines/interfaces/records)? [Consistency, Spec §FR-016, §FR-025]
- [ ] CHK016 Are scope-boundary requirements aligned with scenario text so validation execution, schema evolution classification, and stakeholder reporting remain out of scope everywhere? [Consistency, Spec §FR-026-§FR-028]

## Acceptance Criteria Quality

- [ ] CHK017 Can the specification objectively verify stable ranking order and deterministic tie-breaking for blame candidates? [Measurability, Gap]
- [ ] CHK018 Can reviewers objectively verify min/max number of returned blame candidates from the current requirements? [Measurability, Gap]
- [ ] CHK019 Are confidence score thresholds/bands defined so low-confidence attribution is measurable and not subjective? [Measurability, Gap]
- [ ] CHK020 Are success criteria for graceful degradation measurable when lineage or git evidence is incomplete? [Acceptance Criteria, Spec §SC-005, Ambiguity]

## Scenario Coverage

- [ ] CHK021 Are primary, alternate, and exception scenarios specified for incomplete, stale, and missing lineage evidence? [Coverage, Gap]
- [ ] CHK022 Are recovery/partial-output scenarios specified when git evidence is missing but lineage evidence exists (and vice versa)? [Coverage, Gap]
- [ ] CHK023 Are requirements defined for stale or conflicting metadata between Feature 1 ownership/interface artifacts and Feature 3 validation outputs? [Coverage, Gap]

## Non-Functional & Dependency Coverage

- [ ] CHK024 Are machine-readability and stable output-path requirements explicit and sufficient for downstream consumers without reinterpretation? [Non-Functional, Spec §FR-017-§FR-025]
- [ ] CHK025 Are dependency boundaries on Features 1–3 explicit enough to prevent silent redefinition of canonical artifacts in Feature 4? [Dependencies, Spec §FR-002-§FR-005]
- [ ] CHK026 Is uncertainty representation required at both candidate and record levels whenever causality confidence is limited? [Non-Functional, Spec §FR-012, §FR-023-§FR-024]

## Ambiguities & Conflicts

- [ ] CHK027 Is there an explicit requirement for how commits are associated to candidate files when renames/moves occur? [Ambiguity, Gap]
- [ ] CHK028 Is there an explicit rule for computing direct vs indirect blast radius classification (for example, hop-based definition)? [Ambiguity, Gap]
- [ ] CHK029 Is there an explicit statement of how partial blast radius should be encoded when downstream mapping is incomplete? [Ambiguity, Spec §FR-025, Gap]
- [ ] CHK030 Is terminology consistent for “violation,” “failure,” “eligible check,” and “attributable violation” across scenarios and FRs? [Consistency, Ambiguity]
