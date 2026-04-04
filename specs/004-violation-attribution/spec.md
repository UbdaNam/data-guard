# Feature Specification: Violation Attribution and Blast Radius Analysis

**Feature Branch**: `004-violation-attribution`  
**Created**: 2026-04-04  
**Status**: Draft  
**Input**: User description: "Create Feature 4: Violation Attribution and Blast Radius Analysis for a production-grade Python platform called The Data Contract Enforcer"

## Clarifications

### Session 2026-04-04

- Q: What is the required structure of persisted violation output records? → A: Each persisted violation record MUST include `violation_id`, `check_id`, `detected_at`, contract or dataset identity (`contract_id` and/or `dataset_id` where applicable), `blame_chain[]`, and `blast_radius{}`; `attribution_confidence_summary` is optional but if present MUST be structured and machine-readable.
- Q: What capability boundaries apply to Feature 4? → A: Feature 4 MUST perform attribution and downstream impact estimation, and MUST NOT perform schema evolution classification, stakeholder report generation, or validation execution.

## User Scenarios & Testing _(mandatory)_

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.

  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - Attribute Violations to Plausible Origins (Priority: P1)

As a data platform engineer, I need each attributable validation failure to be
mapped to plausible upstream origins so I can begin remediation without manual
root-cause reconstruction.

**Why this priority**: Attribution is the core value of this feature; without it,
validation failures remain diagnostic but not actionable.

**Independent Test**: Can be fully tested by running attribution on existing
validation reports and confirming each attributable failure produces a bounded,
ranked blame chain with at least one candidate.

**Acceptance Scenarios**:

1. **Given** validation reports containing failed or errored checks, **When**
   attribution runs, **Then** each eligible failure produces a violation record
   with violation identity, check identity, detection timestamp, and ranked
   attribution candidates.
2. **Given** governed schema/interface metadata and lineage snapshots, **When**
   a failing check is mapped to schema elements, **Then** the attribution engine
   traces upstream producer candidates and stops at defined root/external
   boundaries.
3. **Given** attributable violations, **When** attribution candidates are
   produced, **Then** confidence scores are included and ordering is deterministic
   for unchanged inputs.

---

### User Story 2 - Link Violations to Change History (Priority: P2)

As a service owner, I need likely commits and authors associated with an
attributed violation so accountability and triage can start immediately.

**Why this priority**: Git evidence narrows investigation effort and enables
faster operational response.

**Independent Test**: Can be tested by validating that attribution output
includes recent change candidates from repository history, and when file ranges
are available, includes narrowed line-level candidate evidence.

**Acceptance Scenarios**:

1. **Given** implicated files from schema and lineage traversal, **When** git
   history is inspected, **Then** recent candidate commits and author metadata
   are attached to attribution candidates.
2. **Given** source file range context is available, **When** blame analysis is
   performed, **Then** candidate ranking reflects line-level evidence in addition
   to file-level history.
3. **Given** limited or partial git evidence, **When** attribution is emitted,
   **Then** uncertainty is explicit and output remains bounded and reviewable.

---

### User Story 3 - Estimate Blast Radius for Prioritization (Priority: P3)

As an incident manager, I need downstream impact estimates for each violation so
I can prioritize remediation by operational risk.

**Why this priority**: Impact context turns attribution into action planning and
supports downstream reporting features.

**Independent Test**: Can be tested by confirming each persisted violation record
contains a structured blast-radius summary built from downstream lineage and
dependency context.

**Acceptance Scenarios**:

1. **Given** an attributed violation and downstream lineage context, **When**
   blast radius is computed, **Then** the output includes affected systems,
   interfaces, datasets/pipelines, and impacted record estimates where available.
2. **Given** multiple downstream dependency paths, **When** blast radius is
   summarized, **Then** impact is aggregated in machine-readable form suitable for
   later reporting and prioritization.
3. **Given** incomplete downstream evidence, **When** blast radius is emitted,
   **Then** unknowns are represented explicitly rather than omitted.

---

### Edge Cases

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right edge cases.
-->

- A validation report contains only PASS results and therefore has no eligible
  checks for attribution.
- A failing check cannot be mapped to a governed schema element due to missing
  interface or ownership metadata.
- Lineage traversal reaches an external or non-governed node before a clear
  producer origin is identified.
- Multiple upstream producers are equally plausible for the same failing schema
  element.
- Git history exists for an implicated file but no reliable line-level blame is
  available.
- Relevant files were renamed or moved, reducing direct blame continuity.
- Blast radius inputs are partial, resulting in confidence-limited impact
  estimates.
- Attribution graph would exceed configured depth/candidate limits and must be
  truncated with explicit boundary markers.

## Requirements _(mandatory)_

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: The feature MUST provide a violation attribution execution entry
  point at `contracts/attributor.py`.
- **FR-002**: The feature MUST consume validation report artifacts from
  `validation_reports/*.json` and process failures eligible for attribution.
- **FR-003**: The feature MUST consume lineage snapshots from
  `outputs/week4/lineage_snapshots.jsonl` to support upstream and downstream
  traversal.
- **FR-004**: The feature MUST consume canonical interface and ownership metadata
  produced by Feature 1.
- **FR-005**: The feature MUST use generated contracts from Feature 2 when
  needed to map failing checks to governed schema elements.
- **FR-006**: The feature MUST identify attribution-eligible checks from
  validation outcomes and skip non-eligible checks with explicit reason codes.
- **FR-007**: For each eligible check, the feature MUST map the failed check to
  one or more governed schema elements.
- **FR-008**: The feature MUST traverse lineage from each failing schema element
  toward upstream producer candidates and stop at defined root/external
  boundaries.
- **FR-009**: The feature MUST inspect local git history for files implicated by
  schema and lineage traversal.
- **FR-010**: When source ranges are available, the feature MUST incorporate
  line-level blame evidence to refine attribution candidates.
- **FR-011**: The feature MUST produce a ranked blame chain with confidence
  scores for each attributable violation.
- **FR-012**: The feature MUST preserve uncertainty explicitly in output records
  and MUST NOT overstate causal certainty.
- **FR-013**: The feature MUST bound candidate generation and traversal depth so
  blame chains are finite and reviewable.
- **FR-014**: The feature MUST NOT return zero attribution candidates for an
  attributable violation.
- **FR-015**: The feature MUST compute blast radius estimates using downstream
  lineage and dependency context.
- **FR-016**: Blast radius output MUST include structured summaries of affected
  systems, interfaces, pipelines/datasets, and record impact estimates when
  available.
- **FR-017**: The feature MUST persist structured violation records to
  `violation_log/violations.jsonl`.
- **FR-018**: Each violation record MUST include violation identity, check
  identity, detection timestamp, ranked blame chain, blast radius summary, and
  supporting evidence fields required for downstream reporting.
- **FR-019**: The persisted violation format MUST be durable and reusable by
  later features for schema-evolution interpretation, reporting, and operational
  prioritization.
- **FR-020**: Re-running attribution with unchanged inputs MUST produce stable
  ordering and equivalent machine-readable content except for run-level metadata
  identifiers/timestamps.
- **FR-021**: Each persisted violation record MUST include these required fields:
  `violation_id`, `check_id`, `detected_at`, `blame_chain[]`, and
  `blast_radius{}`.
- **FR-022**: Each persisted violation record MUST include contract identity
  and/or dataset identity when applicable to the originating validation artifact.
- **FR-023**: If `attribution_confidence_summary` is emitted, it MUST be a
  structured machine-readable object (not free-form text) and MUST preserve
  uncertainty indicators.
- **FR-024**: `blame_chain[]` entries MUST be bounded and reviewable; candidates
  MUST include confidence metadata and uncertainty notes where evidence is
  incomplete.
- **FR-025**: `blast_radius{}` MUST be structured and MUST include affected
  nodes, affected pipelines, affected interfaces, and estimated impacted records
  or datasets where inferable.
- **FR-026**: This feature MUST perform attribution and downstream impact
  estimation and MUST NOT execute validation.
- **FR-027**: This feature MUST NOT perform schema evolution classification.
- **FR-028**: This feature MUST NOT generate stakeholder-facing reports.

### Key Entities _(include if feature involves data)_

- **Violation Record**: A persistent incident artifact linking one validation
  failure to attribution and impact analysis outputs; includes `violation_id`,
  `check_id`, `detected_at`, identity anchors (`contract_id`/`dataset_id` where
  applicable), `blame_chain[]`, and `blast_radius{}`.
- **Attributed Check**: A failed/errored validation check enriched with schema
  mapping context and eligibility metadata.
- **Schema Element Reference**: A canonical identifier for a dataset/interface
  field or rule target used during lineage traversal.
- **Blame Candidate**: A ranked plausible origin containing source node,
  implicated file(s), commit/author evidence, confidence score, and uncertainty
  notes.
- **Blame Chain**: A bounded ordered set of attribution candidates representing
  plausible upstream origins.
- **Blast Radius Summary**: Structured downstream impact estimate listing
  affected consumers, interfaces, pipelines/datasets, and risk indicators.

### Data Contract & Evidence Artifacts _(mandatory for this project)_

- **Canonical Schema Asset(s)**: Feature 1 canonical schema/interface and
  ownership artifacts used to resolve governed schema element identities.
- **Lineage Mapping Asset(s)**: `outputs/week4/lineage_snapshots.jsonl` used for
  upstream attribution traversal and downstream blast-radius estimation.
- **Validation Output Artifact(s)**: `validation_reports/*.json` from Feature 3,
  serving as direct violation-detection input.
- **Violation Record Artifact(s)**: `violation_log/violations.jsonl`, generated
  by the Feature 4 attribution flow and persisted for later features.
- **Schema Drift/Mismatch Evidence**: Violations include structured evidence
  references to failing checks, mapped schema elements, and candidate change
  history for reviewable causality analysis.

### Downstream Impact _(mandatory for schema/interface changes)_

- **Affected Consumers**: Internal producer/consumer systems represented in
  canonical interface definitions and lineage snapshots.
- **Blast Radius**: Unattributed or unprioritized violations can delay incident
  response, allow cascading downstream data quality degradation, and reduce trust
  in contract enforcement outputs.
- **Migration Plan**: Violation records provide machine-readable incident inputs
  that later features can use for remediation workflows and migration planning.
- **Compatibility Window**: Transitional ambiguity is allowed only when
  uncertainty markers and confidence limits are explicit in violation records.

## Success Criteria _(mandatory)_

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: 100% of attribution-eligible validation failures produce at least
  one ranked blame candidate.
- **SC-002**: 100% of persisted violation records include required identity,
  timestamp, blame chain, and blast-radius fields.
- **SC-003**: 100% of attribution outputs are bounded by configured traversal and
  candidate limits, with explicit truncation markers when limits are reached.
- **SC-004**: At least 90% of attributable violations include both lineage-based
  origin evidence and repository change-history evidence.
- **SC-005**: 100% of violation records include explicit uncertainty annotations
  whenever confidence is below the highest confidence tier.
- **SC-006**: 100% of violation records include a machine-readable downstream
  impact summary that can be consumed directly by later reporting workflows.
- **SC-007**: Re-running on unchanged inputs yields identical candidate ordering
  and blast-radius structure for at least 99% of records (excluding run-level
  identifiers/timestamps).
- **SC-008**: 100% of persisted violation records contain all required fields:
  `violation_id`, `check_id`, `detected_at`, identity anchor(s), `blame_chain[]`,
  and `blast_radius{}`.
- **SC-009**: 100% of records with `attribution_confidence_summary` use
  structured confidence and uncertainty fields (no free-form-only summaries).
- **SC-010**: 0 feature outputs perform schema evolution classification,
  stakeholder report generation, or validation execution.

## Assumptions

- Validation reports from Feature 3 contain sufficient check identifiers and
  field references to map most failures to governed schema elements.
- Week 4 lineage snapshots contain enough producer/consumer context to support
  both upstream attribution and downstream blast-radius estimation.
- Local repository git metadata is available in execution environments where
  attribution is run.
- Attribution confidence is probabilistic and reviewable; human investigation
  remains the final decision authority for incident ownership.
- Feature 4 scope is limited to attribution and impact estimation; it does not
  perform remediation, auto-rollbacks, or stakeholder narrative generation.

## Canonical Structure Notes _(mandatory)_

- Preserves canonical repository layout by using `contracts/attributor.py` as the
  feature entry point and `violation_log/violations.jsonl` as the durable output
  artifact.
- Consumes canonical upstream artifacts from Features 1-3 and Week 4 lineage
  outputs without redefining locations.
- No repository structure deviations are introduced by this specification.

## Implementation Prompt Integrity Checklist _(mandatory)_

- Prompt builds on prior approved specs and platform architecture.
- Prompt describes durable product capability, not submission checkpoint milestones.
- Prompt preserves data contract first-class artifact expectations.
