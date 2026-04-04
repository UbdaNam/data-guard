# Requirements Quality Checklist: Schema Evolution Intelligence

**Purpose**: Validate whether Feature 5 requirements are complete, clear, consistent, and review-ready for schema snapshot, diff, compatibility, and migration-impact definition quality.
**Created**: 2026-04-04
**Feature**: [spec.md](../spec.md)

## Requirement Completeness

- [ ] CHK001 Are snapshot-write trigger requirements fully defined (generation-run trigger, explicit/manual trigger, and non-trigger conditions)? [Completeness, Spec §FR-002, Gap]
- [ ] CHK002 Are snapshot source requirements explicit about whether snapshots come from generated contracts, inferred schema representations, or both? [Clarity, Spec §FR-013, Gap]
- [ ] CHK003 Are snapshot identity requirements defined for both timestamp and version identity fields? [Completeness, Spec §FR-002, Gap]
- [ ] CHK004 Are duplicate snapshot handling requirements defined for the no-material-change case (skip/write/reference behavior)? [Coverage, Spec §FR-020, Gap]
- [ ] CHK005 Are diff-mode requirements complete for both latest-vs-previous and arbitrary two-snapshot comparison? [Completeness, Spec §FR-003]
- [ ] CHK006 Are migration-impact artifact requirements complete for all mandatory sections requested by stakeholders? [Completeness, Spec §FR-010-FR-011]

## Requirement Clarity

- [ ] CHK007 Is the compatibility taxonomy unambiguous about whether verdicts are single-axis or dual-axis (backward and forward evaluated independently)? [Clarity, Spec §FR-006, Ambiguity]
- [ ] CHK008 Are change-class requirements explicit for add/remove/rename/type/enum/constraint/nested/semantic-scale classes, not just examples? [Clarity, Spec §FR-004-FR-005, Gap]
- [ ] CHK009 Is "semantically dangerous" quantified with objective criteria and decision rules to avoid reviewer interpretation drift? [Measurability, Spec §FR-008, Ambiguity]
- [ ] CHK010 Are rename-detection requirements explicit about evidence precedence (explicit mapping vs heuristic) and confidence thresholds? [Clarity, Spec §FR-004, Gap]
- [ ] CHK011 Are nested-field representation requirements explicit (canonical path notation, parent/child change anchoring, and path escaping rules)? [Clarity, Spec §FR-004-FR-005, Gap]

## Requirement Consistency

- [ ] CHK012 Do snapshot requirements and deterministic-behavior requirements align without conflict when contextual artifacts are missing? [Consistency, Spec §FR-002, §FR-014, §FR-020]
- [ ] CHK013 Do compatibility verdict requirements align with migration-guidance requirements (for example, all breaking changes requiring actionable guidance)? [Consistency, Spec §FR-006-FR-011]
- [ ] CHK014 Are output path requirements consistent with canonical structure requirements and naming conventions across all Feature 5 artifacts? [Consistency, Spec §FR-009-FR-010, Canonical Structure Notes]
- [ ] CHK015 Do context-consumption requirements from Features 1-4 avoid redefining source-of-truth artifacts already governed by earlier features? [Consistency, Spec §FR-012-FR-014, Assumption]

## Acceptance Criteria Quality

- [ ] CHK016 Can each compatibility class be objectively validated from written rules without implementation-specific interpretation? [Measurability, Spec §FR-006, Gap]
- [ ] CHK017 Are success criteria measurable for deterministic diff ordering and normalization outputs, not only presence of artifacts? [Acceptance Criteria, Spec §SC-001-SC-004, Gap]
- [ ] CHK018 Are success criteria defined for migration-guidance quality (specificity/actionability) beyond classification accuracy? [Acceptance Criteria, Spec §SC-003, Gap]

## Scenario Coverage

- [ ] CHK019 Are primary scenarios defined for snapshot write, snapshot compare, taxonomy classification, and migration-impact generation as separate requirement flows? [Coverage, Spec §User Story 1-2]
- [ ] CHK020 Are alternate scenarios defined for manual two-snapshot comparison and selected historical comparison by explicit identifiers? [Coverage, Spec §FR-003, Gap]
- [ ] CHK021 Are non-functional determinism scenarios defined for repeated runs with unchanged inputs and equal output ordering? [Coverage, Spec §FR-020, §SC-004]

## Edge Case Coverage

- [ ] CHK022 Are missing-snapshot and malformed-snapshot handling requirements explicit about fail-fast vs degrade behavior and emitted diagnostics? [Edge Case, Spec §Edge Cases, Gap]
- [ ] CHK023 Are low-confidence rename scenarios explicitly defined to fall back to remove+add classification when confidence is below threshold? [Edge Case, Spec §FR-004, Ambiguity]
- [ ] CHK024 Are "contracts differ too much" conditions defined with objective criteria for confidence downgrade and reviewer flags? [Edge Case, Spec §Edge Cases, Gap]

## Dependencies & Boundaries

- [ ] CHK025 Are responsibility boundaries explicit that Feature 5 detects/classifies and generates migration impact, but does not execute validation, perform git-blame attribution, or generate final stakeholder reports? [Boundary, Spec §FR-001-FR-020, Gap]
- [ ] CHK026 Are dependency requirements explicit that Feature 5 may consume Feature 3/4 evidence for severity/confidence/prioritization but must function when absent? [Dependency, Spec §FR-014]

## Downstream Readiness

- [ ] CHK027 Are migration-impact outputs specified as both human-readable and machine-readable in a way that enables downstream reporting and operational decision workflows without reinterpretation? [Downstream Readiness, Spec §FR-010-FR-011, §FR-017, Gap]

## Targeted Validation Pass (Requested Scope)

- [ ] CHK028 Do requirements fully cover the end-to-end responsibility chain of snapshot capture, diff generation, compatibility classification, and migration-impact output production? [Completeness, Spec §FR-002-FR-011]
- [ ] CHK029 Are compatibility taxonomy definitions and change classes stated with explicit decision rules rather than implied examples? [Clarity, Spec §FR-004-FR-008, Gap]
- [ ] CHK030 Are deterministic expectations explicit for both snapshot materialization and diff normalization/ordering across repeated unchanged runs? [Determinism, Spec §FR-020, §SC-004]
- [ ] CHK031 Are nested-field handling and rename handling requirements unambiguous regarding matching strategy, confidence thresholds, and fallback behavior? [Clarity, Spec §FR-004-FR-005, Edge Case]
- [ ] CHK032 Do migration-impact requirements explicitly require human-readable summary, machine-readable diff, compatibility verdict, consumer impact, ordered actions, rollback guidance, and urgency? [Completeness, Spec §FR-010-FR-011, Gap]
- [ ] CHK033 Are degradation rules explicit for missing snapshots, malformed snapshots, and missing Feature 3/4 context while preserving analyzable outputs? [Coverage, Spec §FR-014, Edge Cases]
- [ ] CHK034 Do dependency requirements correctly consume Feature 1-4 artifacts as context without redefining canonical ownership, interface, validation, or violation contracts? [Dependency Consistency, Spec §FR-012-FR-014]
- [ ] CHK035 Are boundaries explicitly stated that Feature 5 does not execute validation, perform attribution/blame, or produce final stakeholder-facing reports? [Boundary, Spec §FR-001-FR-020, Gap]
- [ ] CHK036 Are output contracts sufficiently operational and reporting-ready for downstream decision pipelines without ad hoc reinterpretation? [Downstream Readiness, Spec §FR-017, §Downstream Impact]

## Notes

- This checklist validates requirement quality only; it does not test implementation behavior.
- `plan.md` and `tasks.md` were not available at checklist time, so checks are anchored to [spec.md](../spec.md).
