# Foundation Checklist: Platform Foundation and Canonical Data Surface

**Purpose**: Validate whether the feature requirements are complete, clear, and review-ready for canonical structure, governed data surfaces, ownership boundaries, and compounding platform outputs.
**Created**: 2026-04-01
**Feature**: [spec.md](../spec.md)

## Requirement Completeness

- [ ] CHK001 Are all required canonical repository areas explicitly enumerated (not just implied as "Week 7 layout")? [Completeness, Spec §FR-001, Ambiguity]
- [ ] CHK002 Are the six governed dataset paths defined as authoritative inputs with no missing or optional-path ambiguity? [Completeness, Spec §FR-002]
- [ ] CHK003 Are all inter-system interfaces from the requirement document listed with an explicit completeness rule for inclusion/exclusion? [Completeness, Spec §FR-003, Gap]
- [ ] CHK004 Do requirements explicitly state where each of the seven stable source-of-truth artifacts lives in the repository? [Completeness, Spec §FR-012a, Gap]

## Requirement Clarity

- [ ] CHK005 Is "canonical Week 7 repository layout" defined with concrete, reviewable path expectations rather than high-level wording? [Clarity, Spec §FR-001, Ambiguity]
- [ ] CHK006 Are producer and consumer definitions unambiguous for multi-producer or multi-consumer interfaces? [Clarity, Spec §FR-004, Edge Case]
- [ ] CHK007 Is "readiness" defined with measurable criteria per status so two reviewers would classify a dataset the same way? [Clarity, Spec §FR-023, Ambiguity]
- [ ] CHK008 Are "migration" vs "normalization" requirements distinguished with clear decision boundaries? [Clarity, Spec §FR-021, Ambiguity]

## Requirement Consistency

- [ ] CHK009 Do requirements about preserving canonical targets remain consistent with mismatch handling requirements (no implicit canonical drift)? [Consistency, Spec §FR-019-FR-022]
- [ ] CHK010 Are provenance-status requirements consistent between functional requirements and success criteria (same enum, same constraints)? [Consistency, Spec §FR-017, Spec §SC-007, Spec §SC-008]
- [ ] CHK011 Do user stories and functional requirements align on "foundation only" scope without introducing implementation behavior? [Consistency, Spec §User Story 1-3, Spec §FR-011]

## Acceptance Criteria Quality

- [ ] CHK012 Can each success metric be verified objectively from specification-defined artifacts without inventing additional acceptance logic? [Measurability, Spec §SC-001-SC-011]
- [ ] CHK013 Is the 90% traceability target tied to a deterministic counting rule (denominator and rounding policy)? [Acceptance Criteria, Spec §SC-005, Ambiguity]
- [ ] CHK014 Is the 5-minute stakeholder lookup criterion defined with clear reviewer conditions and artifact access assumptions? [Acceptance Criteria, Spec §SC-006, Ambiguity]

## Scenario Coverage

- [ ] CHK015 Are primary, exception, and recovery requirement paths all covered for actual-vs-canonical divergence? [Coverage, Spec §User Story 3, Spec §FR-019-FR-023]
- [ ] CHK016 Are unresolved upstream dependencies required to remain visible across artifacts until migration closure? [Coverage, Spec §Clarifications, Spec §FR-017, Gap]

## Edge Case Coverage

- [ ] CHK017 Are semantic mismatch scenarios required to preserve business meaning explicitly (including near-match fields)? [Edge Case, Spec §Edge Cases, Spec §FR-022]
- [ ] CHK018 Are conflicting evidence-source scenarios required to define resolution and escalation ownership? [Edge Case, Spec §Edge Cases, Spec §FR-015, Gap]

## Dependencies & Assumptions

- [ ] CHK019 Is the assumption that the requirement document fully defines inter-system arrows validated or bounded if incomplete? [Assumption, Spec §Assumptions, Spec §FR-003]
- [ ] CHK020 Are assumptions about future feature reuse protected by requirements that prevent parallel artifact definitions? [Dependency, Spec §Assumptions, Spec §FR-012]

## Ambiguities & Conflicts

- [ ] CHK021 Is there a defined rule for resolving conflicts when repository evidence disagrees with requirement-document inference? [Ambiguity, Spec §Clarifications, Gap]
- [ ] CHK022 Are hidden implementation assumptions avoided for "preserve required entry-point structure" (e.g., what counts as preservation at spec level)? [Ambiguity, Spec §FR-010]
- [ ] CHK023 Is independent reviewability explicitly testable at the requirements level for product relevance, not only documentation existence? [Coverage, Spec §User Story 1-3, Spec §SC-006]

## Notes

- This checklist validates requirement quality only (not implementation behavior).
- Use findings to tighten wording before `/speckit.plan`.
