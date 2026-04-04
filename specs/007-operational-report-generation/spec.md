# Feature Specification: Operational Report Generation

**Feature Branch**: `007-operational-report-generation`  
**Created**: 2026-04-04  
**Status**: Draft  
**Input**: User description: "Create Feature 7: Operational Report Generation for a production-grade Python platform called The Data Contract Enforcer."

## Clarifications

### Session 2026-04-04

- Q: What evidence model governs report content selection and prioritization? → A: Each report section must use explicit authoritative upstream artifacts (Feature 3 validation reports for health/validation summary, Feature 4 violations for incident prioritization, Feature 5 schema evolution outputs for schema-change summary, Feature 6 AI metrics for AI risk summary, Feature 1 metadata for naming/ownership context), reporting windows are selected by artifact timestamps using an explicit start/end window with latest-available fallback when not provided, top violations are ranked by severity then recurrence then latest occurrence, schema changes are summarized from changes whose timestamps fall in the window prioritizing breaking and high-impact compatibility outcomes, AI risk signals are included from current-run AI metrics plus available bounded trend indicators, and every report claim must reference structured evidence.
- Q: How is Data Health Score computed? → A: Score is deterministic and evidence-based: `check_penalty = ((1×warned) + (4×failed) + (6×errored)) / max(total_checks,1) × 100`; `critical_penalty = min(30, 8 × critical_violation_count)`; `raw_score = 100 - check_penalty - critical_penalty`; final `data_health_score = clamp(raw_score, 0, 100)` rounded to 1 decimal place. If no validation runs exist in the reporting window, score is `null` with `score_status=insufficient_evidence`.
- Q: How are recommended actions generated and prioritized? → A: Actions are operationally specific and evidence-linked. Priority is determined by severity, recurrence in window, recency, and blast-radius/consumer impact. Each action must include what to change, where (contract/field/file/interface), who owns it (Feature 1 metadata), and how to verify completion. Repeated issues are consolidated by issue type + affected surface + field/interface key, and all actions include machine-readable evidence references.
- Q: What are the required output format and determinism rules? → A: `report_data.json` must include a fixed top-level structure and required keys, markdown must include fixed section order, and listed issues/actions must use deterministic ordering by priority and stable tie-breakers. Allowed non-deterministic fields are limited to report/run metadata such as generated timestamp and report ID. Missing upstream artifacts must not block report generation; affected sections remain present with explicit `insufficient_evidence` status and missing-source references.
- Q: What is the policy for optional LLM narrative enrichment? → A: Enrichment is optional only. OpenRouter is the only approved provider. Required environment variables are `OPENROUTER_API_KEY`, `OPENROUTER_BASE_URL`, and `OPENROUTER_MODEL`. A `.env.example` file must be provided. If OpenRouter is unavailable or fails, generator must use deterministic templated fallback narrative. LLM output must not invent facts beyond structured evidence.
- Q: What are the explicit responsibility boundaries for Feature 7? → A: Feature 7 aggregates and summarizes existing platform outputs, generates structured and human-readable report artifacts, and may optionally enrich narrative through OpenRouter. It does not execute validation, does not perform git-blame attribution, does not classify schema evolution, and does not replace upstream evidence generation.

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

### User Story 1 - Unified Operational Health Summary (Priority: P1)

As an engineer or analyst, I need a single generated operational report that
combines existing platform enforcement outputs so I can quickly understand data
health, major breakages, and immediate risk.

**Why this priority**: Without a single evidence-grounded summary, platform
signals remain fragmented across artifacts and cannot support timely
operational decisions.

**Independent Test**: Can be fully tested by running the report generation entry
point and verifying that report data is generated from existing artifacts and
includes a computed Data Health Score plus required section summaries.

**Acceptance Scenarios**:

1. **Given** existing Feature 3, 4, 5, and 6 artifacts, **When** report
   generation runs, **Then** a unified machine-readable report is produced in
   `enforcer_report/report_data.json`.
2. **Given** validation outcomes and violation records, **When** report
   generation runs, **Then** an overall Data Health Score is computed and
   included with evidence references.
3. **Given** generated report data, **When** stakeholders open the generated
   markdown report, **Then** they can identify the highest-priority risk and
   recommended action without reading raw JSON artifacts.

---

### User Story 2 - Evidence-Backed Risk and Change Narrative (Priority: P2)

As a non-technical stakeholder, I need clear plain-language summaries of
violations, schema changes, and AI reliability signals so I can understand what
changed, what is risky, and what response is needed.

**Why this priority**: Operational action depends on narrative clarity; raw
technical outputs alone are not usable for broad decision support.

**Independent Test**: Can be tested by generating a report from artifacts with
known violations and changes, then confirming all required sections are present
and every statement maps back to concrete evidence.

**Acceptance Scenarios**:

1. **Given** violation records in `violation_log/violations.jsonl`, **When**
   report generation runs, **Then** violations are summarized by severity and
   top significant incidents are listed with evidence references.
2. **Given** schema evolution outputs from Feature 5, **When** report generation
   runs, **Then** recent schema changes and compatibility impacts are summarized
   for the reporting window.
3. **Given** AI metrics from Feature 6, **When** report generation runs, **Then**
   AI system risk assessment is included in a dedicated section.

---

### User Story 3 - Deterministic and Resilient Reporting (Priority: P3)

As a platform operator, I need deterministic report generation that continues to
work without LLM access so reporting remains operationally reliable in all
environments.

**Why this priority**: Reporting must not become unavailable due to optional
narrative dependencies.

**Independent Test**: Can be tested by running report generation with and
without LLM environment configuration and confirming deterministic fallback
reporting still produces complete outputs.

**Acceptance Scenarios**:

1. **Given** no LLM configuration, **When** report generation runs, **Then** a
   complete deterministic report is produced without failure.
2. **Given** optional OpenRouter configuration is present, **When** narrative
   enrichment is attempted and fails, **Then** report generation completes using
   deterministic fallback text.
3. **Given** unchanged input artifacts, **When** report generation runs
   repeatedly, **Then** machine-readable outputs remain deterministically
   ordered except for run timestamp metadata.

---

[Add more user stories as needed, each with an assigned priority]

### Edge Cases

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right edge cases.
-->

- One or more expected input artifact families are missing for the reporting
  window (for example, no schema evolution artifacts yet).
- Validation reports exist but have inconsistent timestamp formats.
- Violation records reference contracts or fields that no longer appear in the
  latest metadata mappings.
- AI metrics exist but include insufficient history for trend interpretation.
- Ownership metadata is incomplete for a high-severity violation.
- LLM enrichment is enabled but OpenRouter credentials or model settings are
  missing or invalid.
- Report output directory exists but one target file is not writable.

## Requirements _(mandatory)_

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: The feature MUST expose operational report generation through
  `contracts/report_generator.py` as the stable entry point.
- **FR-002**: The feature MUST consume validation outputs from
  `validation_reports/*.json` generated by Feature 3.
- **FR-003**: The feature MUST consume violation outputs from
  `violation_log/violations.jsonl` generated by Feature 4.
- **FR-004**: The feature MUST consume schema evolution outputs generated by
  Feature 5 for reporting-window schema change summaries.
- **FR-005**: The feature MUST consume `validation_reports/ai_metrics.json`
  generated by Feature 6 for AI risk summaries.
- **FR-006**: The feature MUST consume Feature 1 ownership and interface metadata
  to enrich naming, ownership context, and consumer impact reporting.
- **FR-007**: The feature MUST generate machine-readable report output at
  `enforcer_report/report_data.json`.
- **FR-008**: The feature MUST generate human-readable report output at
  `enforcer_report/report_{date}.md`.
- **FR-009**: The report MUST include a Data Health Score derived from
  validation outcomes and severity-weighted incident evidence.
- **FR-010**: The report MUST summarize violations for the reporting window by
  severity, category, and impacted contract or surface.
- **FR-011**: The report MUST identify top significant violations using explicit
  prioritization criteria and include evidence references.
- **FR-012**: The report MUST summarize detected schema changes and compatibility
  impact from Feature 5 outputs.
- **FR-013**: The report MUST summarize AI contract health and risk signals from
  Feature 6 outputs.
- **FR-014**: The report MUST generate prioritized recommended actions grounded
  in observed evidence and linked to relevant systems, fields, files, contracts,
  or outputs when available.
- **FR-015**: The report MUST include these sections: Data Health Score,
  Violations this period, Schema changes detected, AI system risk assessment,
  and Recommended actions.
- **FR-016**: Every reported claim MUST preserve traceability to one or more
  generated evidence artifacts and include machine-readable evidence references
  in report data.
- **FR-017**: The feature MUST NOT emit speculative or fabricated incidents,
  claims, or recommendations.
- **FR-018**: Report generation MUST function deterministically without requiring
  LLM access.
- **FR-019**: If optional narrative enrichment is enabled, it MUST use
  OpenRouter-configured models only.
- **FR-020**: Any optional LLM configuration MUST come from environment
  variables; no API keys or model names may be hardcoded.
- **FR-021**: LLM unavailability or enrichment failure MUST NOT block report
  generation and deterministic fallback narrative MUST be used.
- **FR-022**: The feature MUST preserve canonical repository locations for
  schemas, contract clauses, lineage mappings, validation outputs, and
  violation records as read-only upstream inputs.
- **FR-023**: The feature MUST include graceful degradation behavior when one or
  more optional inputs are absent, and MUST explicitly indicate section
  completeness status in machine-readable output.
- **FR-024**: Operational artifacts produced by this feature MUST be generated
  from existing platform evidence and/or explicitly injected test data only.
- **FR-025**: The feature MUST remain separated from direct validation execution,
  git attribution, schema evolution classification logic, and AI contract
  enforcement execution responsibilities.
- **FR-026**: The feature MUST use this authoritative section-to-source mapping:
  Data Health Score and validation coverage from Feature 3
  `validation_reports/*.json`; violations summary and top incidents from Feature
  4 `violation_log/violations.jsonl`; schema changes summary from Feature 5
  schema evolution outputs; AI risk assessment from Feature 6
  `validation_reports/ai_metrics.json`; ownership/naming enrichment from Feature
  1 metadata artifacts.
- **FR-027**: Reporting window selection MUST support explicit start/end bounds;
  if bounds are not provided, the feature MUST use a deterministic latest
  available window derived from source artifact timestamps and record the final
  resolved window in report data.
- **FR-028**: Top significant violations MUST be ranked deterministically by
  severity (critical > high > medium > low), then recurrence count within the
  window, then latest occurrence timestamp, with stable tie-breaking by
  violation identifier.
- **FR-029**: Schema change summaries MUST include only Feature 5 changes that
  fall within the resolved reporting window, with prioritization favoring
  breaking compatibility verdicts and higher downstream impact context.
- **FR-030**: AI risk inclusion MUST use Feature 6 current-run metrics and
  available trend indicators for quarantine rate, violation rates, drift status,
  and completeness flags; absent trend history MUST be reported as insufficient
  evidence rather than inferred risk.
- **FR-031**: Every rendered section and recommended action MUST include
  machine-readable evidence references (`artifact_path`, `record_selector`, and
  `claim_type`) so claims are fully traceable to structured platform artifacts.
- **FR-032**: Data Health Score MUST use this exact deterministic computation:
  `check_penalty = ((1×warned) + (4×failed) + (6×errored)) / max(total_checks,1) × 100`;
  `critical_penalty = min(30, 8 × critical_violation_count)`;
  `raw_score = 100 - check_penalty - critical_penalty`;
  final score `= clamp(raw_score, 0, 100)` rounded to 1 decimal place.
- **FR-033**: If no validation runs exist in the resolved reporting window, the
  feature MUST set `data_health_score` to `null`, set `score_status` to
  `insufficient_evidence`, and include a deterministic reason message in report
  data and markdown output.
- **FR-034**: Recommended actions MUST be prioritized deterministically using
  severity, recurrence, recency, and downstream blast-radius/consumer impact;
  ties MUST be resolved by stable identifier ordering.
- **FR-035**: Every recommended action MUST be operationally specific (not
  generic) and include: remediation target, affected location
  (contract/field/file/interface), ownership context from Feature 1 metadata,
  and a concrete verification step.
- **FR-036**: Repeated issues MUST be consolidated into one action per
  normalized issue key (`issue_type`, `affected_surface`, `field_or_interface`)
  while preserving aggregated count and latest occurrence metadata.
- **FR-037**: `enforcer_report/report_data.json` MUST include this required
  top-level key order: `report_id`, `report_date`, `reporting_window`,
  `data_health_score`, `section_completeness`, `violations_summary`,
  `top_violations`, `schema_changes_summary`, `ai_risk_summary`,
  `recommended_actions`, `evidence_index`, `generation_metadata`.
- **FR-038**: `enforcer_report/report_{date}.md` MUST include this fixed section
  order: Data Health Score, Violations this period, Schema changes detected, AI
  system risk assessment, Recommended actions, Evidence traceability notes.
- **FR-039**: Deterministic ordering rules MUST sort listed issues/actions by
  priority then severity then recurrence then latest timestamp then stable ID;
  only report metadata fields (`report_id`, `generated_at`, duration metrics)
  may vary run-to-run on unchanged evidence.
- **FR-040**: If one or more upstream artifact families are missing, report
  generation MUST continue and keep affected sections present with
  `insufficient_evidence` status plus explicit missing artifact path references.
- **FR-041**: Narrative enrichment MUST be optional-only and MUST NOT be
  required for successful report generation.
- **FR-042**: OpenRouter is the only approved LLM provider for optional
  enrichment.
- **FR-043**: LLM configuration MUST be sourced only from environment variables
  `OPENROUTER_API_KEY`, `OPENROUTER_BASE_URL`, and `OPENROUTER_MODEL`.
- **FR-044**: The repository MUST provide `.env.example` documenting required
  optional enrichment environment variables.
- **FR-045**: If optional OpenRouter enrichment is unavailable or fails, the
  feature MUST fall back to deterministic templated narrative and still produce
  complete report outputs.
- **FR-046**: Optional LLM output MUST be strictly evidence-grounded and MUST
  NOT introduce facts, incidents, or recommendations that are unsupported by
  structured input artifacts.
- **FR-047**: Responsibility boundaries MUST be enforced: Feature 7 aggregates
  and summarizes upstream artifacts and generates report outputs, but MUST NOT
  execute validation, perform git-blame attribution, classify schema evolution,
  or replace upstream evidence generation responsibilities.

### Key Entities _(include if feature involves data)_

- **Operational Report Data**: Machine-readable output containing report
  metadata, health score, section summaries, recommended actions, and evidence
  reference links.
- **Reporting Window**: The resolved start/end time bounds used to include
  evidence records for this report run.
- **Data Health Score**: A normalized score representing overall data health for
  the reporting window, derived from validation and incident evidence.
- **Violation Summary**: Aggregated view of incidents grouped by severity,
  category, impacted contracts/surfaces, and ownership context.
- **Top Violation Ranking Record**: Prioritized violation record with rank,
  severity, recurrence, latest occurrence, and traceable evidence reference.
- **Schema Change Summary**: Aggregated summary of recent schema evolution
  changes and compatibility impact from Feature 5 outputs.
- **AI Risk Summary**: Summary of AI contract reliability signals derived from
  Feature 6 metrics.
- **Recommended Action**: Prioritized, evidence-linked remediation item with
  rationale, owner/consumer context, and urgency.
- **Action Priority Score**: Deterministic rank signal derived from severity,
  recurrence, recency, and blast-radius/consumer impact factors.
- **Evidence Reference**: Structured link to a source artifact path and record
  selector supporting a reported claim.

### Data Contract & Evidence Artifacts _(mandatory for this project)_

- **Canonical Schema Asset(s)**: Reuses canonical schema and contract assets from
  `generated_contracts/` and metadata/context assets from `contracts/`.
- **Lineage Mapping Asset(s)**: Reuses Feature 1 interface and ownership metadata
  for naming and downstream consumer context in reported findings/actions.
- **Validation Output Artifact(s)**: Consumes Feature 3 validation artifacts in
  `validation_reports/*.json`; produces `enforcer_report/report_data.json`.
- **Violation Record Artifact(s)**: Consumes Feature 4 incident evidence in
  `violation_log/violations.jsonl`.
- **Schema Drift/Mismatch Evidence**: Consumes Feature 5 schema evolution outputs
  and Feature 6 AI metrics as evidence inputs for report sections.
- **Human-readable Report Artifact**: Produces
  `enforcer_report/report_{date}.md` as the operational narrative output.

### Evidence Model for Report Sections

- **Data Health Score**: Authoritative source is Feature 3
  `validation_reports/*.json` with Feature 4 violation severity weighting as
  secondary evidence.
- **Violations this period**: Authoritative source is Feature 4
  `violation_log/violations.jsonl`, scoped by resolved reporting window.
- **Schema changes detected**: Authoritative source is Feature 5 schema
  evolution outputs within reporting window.
- **AI system risk assessment**: Authoritative source is Feature 6
  `validation_reports/ai_metrics.json` (current metrics + bounded trend signals
  if present).
- **Recommended actions**: Derived from authoritative section evidence and
  enriched by Feature 1 ownership/interface metadata for responsibility context.
- **Traceability contract**: Every claim must include `artifact_path`,
  `record_selector`, and `claim_type` in machine-readable report data.

### Downstream Impact _(mandatory for schema/interface changes)_

- **Affected Consumers**: Repository reviewers, operations stakeholders,
  engineering owners, and future alerting/dashboard integrations consuming
  report data.
- **Blast Radius**: Missing or low-fidelity reporting reduces ability to detect
  urgent risk, slows remediation prioritization, and weakens operational handoff.
- **Migration Plan**: Any evolution of report schema requires compatibility
  maintenance for downstream automation consumers and explicit version notes.
- **Compatibility Window**: Transitional support for report data schema changes
  must be explicitly documented with a clear deprecation endpoint.

### Responsibility Boundaries _(mandatory)_

- **In Scope**: Aggregate and summarize existing platform outputs, generate
  machine-readable and human-readable report artifacts, and optionally enrich
  narrative through OpenRouter.
- **Out of Scope**: Executing validation, performing git-blame attribution,
  classifying schema evolution, and replacing upstream evidence generation.

## Success Criteria _(mandatory)_

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: 100% of successful report runs generate both
  `enforcer_report/report_data.json` and `enforcer_report/report_{date}.md`.
- **SC-002**: 100% of report runs include all five required sections in both
  machine-readable and human-readable outputs.
- **SC-003**: 100% of reported claims in report data include at least one
  traceable evidence reference to a platform-generated artifact.
- **SC-004**: 100% of successful runs produce a Data Health Score and explicit
  section completeness indicators.
- **SC-005**: At least 90% of sampled non-engineer reviewers can identify the
  top current risk and recommended response within 5 minutes using only the
  generated markdown report.
- **SC-006**: 100% of runs complete report generation when LLM configuration is
  absent or enrichment fails.
- **SC-007**: 0 report claims reference fabricated incidents or sources outside
  declared platform evidence artifacts.

## Assumptions

- Prior features continue generating artifacts in canonical paths and formats
  defined by their approved specifications.
- Reporting window defaults to latest available artifacts unless explicitly
  configured.
- Feature 4 violations and Feature 5/6 summaries may be empty for some windows;
  report generation still completes with explicit section completeness flags.
- Optional narrative enrichment is supplementary only and deterministic narrative
  fallback remains the baseline behavior.
- Future alerting/dashboard integrations consume `report_data.json` directly and
  do not require markdown parsing.

## Canonical Structure Notes _(mandatory)_

- Feature preserves canonical repository layout and uses existing artifact roots
  as read-only evidence inputs.
- New outputs are confined to `enforcer_report/` with machine-readable and
  human-readable report artifacts.
- Optional PDF-compatible output may be added later without replacing required
  report data and markdown outputs.

## Implementation Prompt Integrity Checklist _(mandatory)_

- Prompt builds on prior approved specs and platform architecture.
- Prompt describes durable product capability, not submission checkpoint milestones.
- Prompt preserves data contract first-class artifact expectations.
