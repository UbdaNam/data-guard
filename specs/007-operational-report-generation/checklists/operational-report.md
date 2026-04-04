# Operational Reporting Requirements Checklist: Operational Report Generation

**Purpose**: Validate requirement quality for report structure, evidence model, scoring clarity, recommendation logic, deterministic outputs, degradation behavior, optional OpenRouter enrichment, environment configuration, and responsibility boundaries.
**Created**: 2026-04-04
**Feature**: [spec.md](../spec.md)

**Note**: This checklist evaluates the quality of written requirements (completeness, clarity, consistency, measurability, and coverage), not runtime behavior.

## Requirement Completeness

- [ ] CHK001 Are required report sections fully enumerated for both machine-readable and human-readable outputs, including evidence traceability notes? [Completeness, Spec §FR-015, Spec §FR-038]
- [ ] CHK002 Are authoritative evidence inputs defined for every section with no unmapped section-to-source dependency? [Completeness, Spec §FR-026, Spec §Evidence Model for Report Sections]
- [ ] CHK003 Are required top-level report data fields fully specified, including section completeness and generation metadata? [Completeness, Spec §FR-037]
- [ ] CHK004 Are required action attributes fully specified (target, location, owner context, verification step) for all recommended actions? [Completeness, Spec §FR-035]
- [ ] CHK005 Is the optional LLM configuration surface complete, including required environment variable names and repository-level template documentation? [Completeness, Spec §FR-043, Spec §FR-044]

## Requirement Clarity

- [ ] CHK006 Is the Data Health Score formula unambiguous, including penalty terms, clamping boundaries, and rounding precision? [Clarity, Spec §FR-032]
- [ ] CHK007 Is the no-validation-runs condition explicitly defined with exact nullability and status semantics? [Clarity, Spec §FR-033]
- [ ] CHK008 Are recommendation prioritization factors defined with clear ordering and deterministic tie-break expectations? [Clarity, Spec §FR-034]
- [ ] CHK009 Is repeated-issue consolidation defined with an explicit normalization key and retained aggregate metadata? [Clarity, Spec §FR-036]
- [ ] CHK010 Are allowed non-deterministic fields explicitly bounded so readers can distinguish variable metadata from stable content? [Clarity, Spec §FR-039]

## Requirement Consistency

- [ ] CHK011 Do report section requirements align across section lists, output structure requirements, and success criteria without naming conflicts? [Consistency, Spec §FR-015, Spec §FR-038, Spec §SC-002]
- [ ] CHK012 Do evidence traceability requirements remain consistent between per-section evidence rules and global claim traceability constraints? [Consistency, Spec §FR-016, Spec §FR-031, Spec §Evidence Model for Report Sections]
- [ ] CHK013 Do optional enrichment rules consistently indicate optional-only behavior across functional requirements, assumptions, and success criteria? [Consistency, Spec §FR-041, Spec §FR-045, Spec §SC-006, Spec §Assumptions]
- [ ] CHK014 Do boundary constraints consistently separate Feature 7 reporting responsibilities from upstream validation, attribution, schema classification, and AI metric generation duties? [Consistency, Spec §FR-025, Spec §FR-047, Spec §Responsibility Boundaries]

## Acceptance Criteria Quality

- [ ] CHK015 Are success criteria objectively measurable with explicit denominators/scope for "100%" statements and sampling method details where applicable? [Measurability, Spec §SC-001, Spec §SC-002, Spec §SC-003, Spec §SC-004, Spec §SC-005]
- [ ] CHK016 Is acceptance quality for deterministic output defined in measurable terms that reference stable ordering and bounded variable fields? [Acceptance Criteria, Spec §FR-039, Spec §User Story 3]
- [ ] CHK017 Are acceptance expectations for missing-input handling measurable through explicit section status semantics rather than general resilience language? [Acceptance Criteria, Spec §FR-040, Spec §FR-023]

## Scenario Coverage

- [ ] CHK018 Are primary, alternate, and exception requirement scenarios all represented for report generation, enrichment failure, and missing artifact families? [Coverage, Spec §User Stories, Spec §Edge Cases, Spec §FR-040, Spec §FR-045]
- [ ] CHK019 Are reporting-window requirements complete for both explicit window bounds and deterministic fallback window resolution? [Coverage, Spec §FR-027]
- [ ] CHK020 Are scenario requirements for insufficient trend history and incomplete ownership metadata explicitly linked to section completeness semantics? [Coverage, Spec §FR-030, Spec §Edge Cases, Spec §FR-023]

## Non-Functional & Configuration Requirements

- [ ] CHK021 Are deterministic output requirements specific enough to prevent interpretation drift across implementations and reviewers? [Non-Functional, Spec §FR-037, Spec §FR-038, Spec §FR-039]
- [ ] CHK022 Are provider constraints for optional enrichment explicit enough to exclude non-OpenRouter providers without ambiguity? [Non-Functional, Spec §FR-019, Spec §FR-042]
- [ ] CHK023 Are environment-based configuration requirements explicit about source of truth and prohibition of hardcoded secrets/models? [Non-Functional, Spec §FR-020, Spec §FR-043, Spec §FR-044]

## Dependencies, Assumptions & Gaps

- [ ] CHK024 Are upstream artifact format and timestamp assumptions sufficiently specified to avoid inconsistent window filtering and evidence selection outcomes? [Assumption, Spec §Assumptions, Spec §Edge Cases, Spec §FR-027]
- [ ] CHK025 Are compatibility and migration expectations for report schema evolution specific enough for downstream automation consumers? [Dependency, Spec §Downstream Impact]
- [ ] CHK026 Is an explicit requirement present for how unresolved evidence conflicts are represented when multiple artifact sources disagree? [Gap]

## Ambiguities & Conflict Risks

- [ ] CHK027 Is "downstream blast-radius/consumer impact" quantified or constrained so recommendation ranking remains reproducible? [Ambiguity, Spec §FR-034]
- [ ] CHK028 Is "deterministic latest available window" defined with precise tie-breaking when artifact timestamps are equal or partially missing? [Ambiguity, Spec §FR-027]
- [ ] CHK029 Do "top violations" and "recommended actions" ordering rules align when priority and severity dimensions could conflict? [Conflict, Spec §FR-028, Spec §FR-039]
- [ ] CHK030 Is "complete report outputs" under enrichment failure clearly scoped to required sections, completeness flags, and evidence references? [Ambiguity, Spec §FR-045, Spec §FR-015, Spec §FR-023]
