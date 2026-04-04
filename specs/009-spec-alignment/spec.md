# Feature Specification: Spec Alignment and Platform Completion

**Feature Branch**: `009-spec-alignment`  
**Created**: 2026-04-05  
**Status**: Draft  
**Input**: User description: "Create a single unified update feature for the Data Contract Enforcer that closes the gaps between the current implementation and the platform requirements, adds a dedicated subscriptions registry, strengthens contract generation, validation, attribution, schema evolution, AI contract enforcement, report generation, and standardizes OpenRouter-only optional LLM behavior."

## User Scenarios & Testing _(mandatory)_

### User Story 1 - Governed Subscription Topology (Priority: P1)

As a platform maintainer, I can manage a dedicated machine-readable subscriptions registry that explicitly lists governed producer-consumer interfaces so the platform has a single authoritative source for subscription topology, downstream consumer discovery, and blast radius reasoning.

**Why this priority**: This registry is the new first-class governance artifact that every downstream analysis depends on.

**Independent Test**: A reviewer can inspect the registry file, confirm the required interface fields exist, and verify that attribution and blast-radius outputs reference the registry rather than relying on lineage alone.

**Acceptance Scenarios**:

1. **Given** a governed interface is recorded in the registry, **When** attribution or blast-radius analysis runs, **Then** the registry entry is available as the authoritative topology source and downstream consumers are visible.
2. **Given** a subscription path has both direct and transitive consumers, **When** the registry is consulted, **Then** the output includes contamination depth, direct subscribers, and transitive downstream consumers as distinct machine-readable concepts.

---

### User Story 2 - Deterministic Contract and Validation Alignment (Priority: P1)

As an engineer, I can generate contracts and run validation in a deterministic way that captures numeric baselines, hard confidence bounds, lineage-derived consumers, and drift outcomes so the platform’s governed outputs match the required contract rules.

**Why this priority**: Contract generation and validation are the core enforcement path for the platform.

**Independent Test**: A reviewer can run the generator and validation steps without optional LLM configuration and verify that numeric baselines, confidence constraints, consumer mappings, drift severities, and mode-specific report results are produced consistently.

**Acceptance Scenarios**:

1. **Given** governed numeric fields and confidence fields exist, **When** contract generation runs, **Then** numeric baseline records are written to the canonical baseline artifact and confidence bounds are explicit and constrained to 0.0–1.0.
2. **Given** a numeric field drifts above the configured threshold, **When** validation runs in AUDIT, WARN, or ENFORCE mode, **Then** the report is still constructed, the drift result is classified correctly, and structured ERROR results are preserved without crashing.

---

### User Story 3 - Attribution, Blast Radius, and Schema Evolution Fidelity (Priority: P2)

As a maintainer, I can trace violations and schema changes with spec-exact confidence, candidate ranking, blast-radius detail, and consumer-specific migration impact so I understand what breaks, who is affected, and what recovery steps are required.

**Why this priority**: Attribution and schema analysis are the decision-making layers that turn validated outputs into operational guidance.

**Independent Test**: A reviewer can supply a known violation or breaking schema change and confirm the confidence formula, blame-chain cap, blast-radius fields, CRITICAL narrowing rule, and consumer-level failure modes are present in the outputs.

**Acceptance Scenarios**:

1. **Given** a violation with lineage and registry evidence, **When** attribution runs, **Then** confidence is computed with the required formula, the blame chain contains no more than five ranked candidates, and at least one candidate is returned when attribution is possible.
2. **Given** a schema change narrows a governed field from float 0.0–1.0 to int 0–100, **When** schema evolution analysis runs, **Then** the change is classified as CRITICAL, the migration report names affected consumers and likely failure modes, and rollback or baseline re-establishment requirements are explicit.

---

### User Story 4 - AI Enforcement, Reporting, and Operational Guidance (Priority: P2)

As a platform operator, I can run AI contract enforcement, generate reports, and read updated workflow guidance so optional LLM behavior remains OpenRouter-only, non-blocking, and fully documented.

**Why this priority**: AI behavior and report quality must be complete, but the deterministic baseline remains the default operating path.

**Independent Test**: A reviewer can run the AI enforcement and report steps with and without OpenRouter configuration and confirm that invalid prompt inputs are quarantined, embedding drift is measured, schema violations are tracked, report actions are specific, and documentation reflects the supported modes.

**Acceptance Scenarios**:

1. **Given** invalid prompt input or a structured output schema violation threshold breach, **When** AI contract enforcement runs, **Then** invalid inputs are routed to quarantine, drift and violation metrics are recorded, and WARN entries are written when the threshold is exceeded.
2. **Given** validation, attribution, and schema outputs exist, **When** report generation runs, **Then** the report shows the exact data health score calculation, recommends actions with file path, field, and contract clause references, and optional OpenRouter enrichment remains non-blocking.

### Edge Cases

- The registry contains a producer-consumer interface that exists in lineage but not in the latest snapshot; the authoritative registry still drives topology, while missing lineage is recorded as a coverage gap.
- A drift value lands exactly at 2.0 standard deviations or exactly at 3.0 standard deviations; the result remains below the WARN and FAIL thresholds because the required thresholds are strict exceedances.
- A numeric baseline is missing for a newly governed field; the platform records the absence explicitly and avoids inventing drift statistics until a baseline exists.
- A confidence field contains a value outside 0.0–1.0; validation records a range violation independently from any drift result.
- Attribution evidence is weak but still present; the platform returns the best available candidate set instead of suppressing the result, and weak confidence is preserved.
- OpenRouter environment variables are absent; LLM-assisted behavior is skipped and the deterministic baseline remains fully supported.
- A prompt input fails JSON Schema validation or an LLM output violates structure; the affected payload is quarantined or warned on without crashing the run.

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: The system MUST maintain the canonical subscriptions registry at `docs/governance/subscriptions_registry.yaml`, and that registry MUST be the authoritative source for subscription topology.
- **FR-002**: The registry MUST use a top-level mapping with `version`, `generated_at`, and `interfaces`, where `interfaces` is a list of entries and each entry MUST include `interface_id`, `producer`, `consumer`, `schema_name` or `record_type`, `criticality`, and `dependency_type` or `directness`.
- **FR-003**: Violation attribution and blast-radius logic MUST consult the subscriptions registry before or alongside lineage traversal.
- **FR-004**: Blast-radius outputs MUST include `affected_nodes`, `affected_pipelines`, `direct_subscribers`, `transitive_downstream_nodes`, and `contamination_depth`; `direct_subscribers` MUST mean one-hop registry subscribers, `transitive_downstream_nodes` MUST mean all downstream registry descendants beyond the first hop, and `contamination_depth` MUST mean the maximum hop distance from the violating node to any affected downstream node.
- **FR-005**: Contract generation MUST write authoritative numeric baseline statistics for governed numeric fields to `schema_snapshots/baselines.json`, using a JSON object keyed by contract or surface identifier and field name with at least the field value distribution, sample count, mean, and standard deviation needed for later drift detection.
- **FR-006**: Contract generation MUST emit explicit hard confidence constraints for every governed field whose semantic role is confidence or probability, including fields named `confidence`, `confidence_score`, `confidence_probability`, or equivalent governed variants, and MUST constrain those fields to the 0.0–1.0 range.
- **FR-007**: Contract generation MUST inject downstream consumers from the latest successfully produced Week 4 lineage snapshot file under `outputs/week4/lineage_snapshots.jsonl` into generated contracts.
- **FR-008**: Contract generation MAY add ambiguous-field annotations only when OpenRouter-backed LLM configuration is present and only for fields that are already ambiguous after deterministic parsing; otherwise the generation path MUST remain deterministic and non-LLM.
- **FR-009**: Validation execution MUST load numeric baselines from `schema_snapshots/baselines.json` before computing drift and MUST load embedding drift baselines from `schema_snapshots/ai/<surface_id>/baseline_token_hash_v1.json` when AI drift checks are enabled.
- **FR-010**: Validation execution MUST compute drift in standard-deviation units and MUST treat values greater than 2 standard deviations and less than or equal to 3 standard deviations as WARN, and values greater than 3 standard deviations as FAIL.
- **FR-011**: Validation execution MUST enforce confidence-range checks independently from drift logic, including explicit range failures for any confidence field outside 0.0–1.0.
- **FR-012**: Validation execution MUST support a `--mode` flag with `AUDIT`, `WARN`, and `ENFORCE` behaviors while still constructing the full report in every mode: `AUDIT` records all checks and threshold outcomes without escalation, `WARN` records threshold breaches as WARN while still completing the report, and `ENFORCE` escalates threshold breaches to FAIL while still completing the report.
- **FR-013**: Validation execution MUST preserve structured ERROR results and MUST not crash when inputs are malformed or incomplete; missing columns MUST remain ERROR in every mode.
- **FR-014**: Violation attribution MUST calculate confidence exactly as `1.0 − (days_since_commit × 0.1) − (lineage_hops × 0.2)`.
- **FR-015**: Violation attribution MUST rank no more than five blame-chain candidates and MUST return at least one candidate whenever attribution evidence exists.
- **FR-016**: Violation attribution MUST preserve uncertainty when evidence quality is weak instead of suppressing the record.
- **FR-017**: Schema evolution analysis MUST classify a narrow change from float 0.0–1.0 to int 0–100 as a CRITICAL breaking change.
- **FR-018**: Schema evolution reports MUST surface severity or urgency indicators that reflect the breaking-change classification.
- **FR-019**: Schema evolution analysis MUST perform per-consumer failure-mode analysis using both the subscriptions registry and lineage data.
- **FR-020**: Migration impact outputs MUST name specific downstream consumers, likely failure modes, and rollback or baseline re-establishment requirements for each named consumer.
- **FR-021**: AI contract enforcement MUST validate governed prompt inputs against a JSON Schema and route invalid inputs to quarantine outputs; the mandatory governed prompt surface is the prompt-input schema for `contracts/ai_extensions.py`, and the mandatory governed output surface is the structured LLM output schema used by the same module.
- **FR-022**: AI contract enforcement MUST detect embedding drift using cosine distance and MUST persist embedding baseline centroid artifacts in `schema_snapshots/ai/<surface_id>/baseline_token_hash_v1.json`.
- **FR-023**: AI contract enforcement MUST track structured LLM output schema-violation rates and MUST write WARN entries to `violation_log/ai_violations.jsonl` when the configured threshold is exceeded.
- **FR-024**: All AI extensions MUST execute through contracts/ai_extensions.py and MUST keep optional LLM usage OpenRouter-only and environment-driven.
- **FR-025**: AI contract enforcement MUST preserve deterministic non-LLM fallback behavior when LLM assistance is unavailable or disabled.
- **FR-026**: Operational report generation MUST calculate the data health score exactly as `(checks_passed / total_checks × 100) − (20 × critical_violation_count)`.
- **FR-027**: Operational report generation MUST display the score calculation explicitly in generated reports, including the inputs used to compute the score.
- **FR-028**: Recommended report actions MUST explicitly name the file path, field, and contract clause they address, and MUST derive those references from the top violation or schema change record that triggered the recommendation.
- **FR-029**: Report recommendations MUST tie directly to the top violations or schema changes that produced them, and optional OpenRouter narrative enrichment MUST remain additive and non-blocking.
- **FR-030**: Environment configuration MUST read all LLM settings from environment variables only and MUST not hardcode API keys or model names in source code.
- **FR-031**: `.env.example` MUST document `OPENROUTER_API_KEY`, `OPENROUTER_BASE_URL`, and `OPENROUTER_MODEL` as placeholder-only optional variables and MUST preserve the deterministic baseline as the default supported path.
- **FR-032**: Workflow documentation MUST be updated to explain the subscriptions registry, AI extension completion, the validation modes, report-generation behavior, and deterministic fallback paths for every optional LLM-assisted step.
- **FR-033**: Existing platform boundaries from Features 2–8 MUST remain intact; this feature MUST extend existing outputs and artifacts rather than introduce parallel systems or alternate sources of truth.

### Key Entities _(include if feature involves data)_

- **Subscriptions Registry Entry**: A governed producer-consumer interface record with topology, criticality, and dependency-directness metadata.
- **Numeric Baseline Record**: Authoritative statistics for governed numeric fields, used for drift calculations and revalidation.
- **Drift Assessment**: The validation result that compares current numeric values against numeric baselines in standard-deviation units.
- **Attribution Candidate**: A ranked violation-related entity with a computed confidence score and evidence summary.
- **Blast Radius Summary**: The downstream impact record that lists affected nodes, pipelines, direct subscribers, transitive nodes, and contamination depth.
- **Schema Evolution Finding**: A compatibility and migration impact record describing breaking changes, severity, affected consumers, and recovery requirements.
- **AI Enforcement Result**: The combined prompt-validation, embedding-drift, and structured-output outcome for governed AI extensions.
- **Report Action**: A generated operational recommendation that ties a top issue to a file path, field, and contract clause.

### Data Contract & Evidence Artifacts _(mandatory for this project)_

- **Canonical Schema Asset(s)**: `docs/governance/subscriptions_registry.yaml` is the authoritative subscriptions registry; it must be version-controlled and consumed by attribution, blast-radius, and schema-analysis logic. The file schema is a YAML mapping with `version`, `generated_at`, and `interfaces`, where each interface item is a governed producer-consumer relationship record.
- **Lineage Mapping Asset(s)**: `outputs/week4/lineage_snapshots.jsonl` remains the canonical lineage source for downstream consumer injection and evidence cross-checking.
- **Validation Output Artifact(s)**: `validation_reports/*.json` and `schema_snapshots/baselines.json` are generated by `contracts/runner.py` in all supported modes.
- **Violation Record Artifact(s)**: `violation_log/violations.jsonl` and `violation_log/ai_violations.jsonl` record attribution, drift, and AI-warning outcomes.
- **Schema Drift/Mismatch Evidence**: `validation_reports/schema_evolution_*.json`, `migration_impact_*.json`, and `schema_snapshots/ai/*` capture divergence, failure modes, and embedding evidence.
- **AI Prompt Evidence**: `outputs/quarantine/*` and prompt-validation records preserve invalid or rejected AI inputs for review.

### Downstream Impact _(mandatory for schema/interface changes)_

- **Affected Consumers**: Contract generation, validation, attribution, schema evolution analysis, AI contract enforcement, report generation, and any downstream consumer named in the subscriptions registry.
- **Blast Radius**: Uncoordinated registry, contract, or schema changes can hide impacted subscribers, understate contamination depth, suppress critical drift signals, or generate incomplete stakeholder reports.
- **Migration Plan**: Registry updates must be reflected in regenerated contracts, refreshed numeric baselines, updated lineage-derived consumer mappings, rerun validation, rerun attribution, rerun schema analysis, rerun AI enforcement, and regenerate reports.
- **Compatibility Window**: Additive or non-breaking changes may coexist with existing baselines until refresh completes; the float 0.0–1.0 to int 0–100 narrowing rule has no compatibility window and is CRITICAL.

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: 100% of governed producer-consumer interfaces in the test dataset appear in the subscriptions registry with the required fields populated.
- **SC-002**: In regression scenarios, a drift value greater than 2 standard deviations is classified as WARN and a drift value greater than 3 standard deviations is classified as FAIL in 100% of runs.
- **SC-003**: 100% of governed confidence fields in generated contracts are constrained to the 0.0–1.0 range, and repeated runs without OpenRouter produce deterministic matching output for those fields.
- **SC-004**: Attribution returns no more than five ranked candidates, and when evidence exists it returns at least one candidate in 100% of tested cases.
- **SC-005**: The float 0.0–1.0 to int 0–100 schema change is classified as CRITICAL in 100% of tested migration scenarios, with named downstream consumers and recovery guidance present.
- **SC-006**: Invalid prompt inputs are quarantined, embedding drift is measured by cosine distance, and structured-output schema violations produce WARN entries whenever the configured threshold is exceeded.
- **SC-007**: Generated reports always show the exact data health score calculation and every recommended action names a file path, field, and contract clause.
- **SC-008**: When OpenRouter is not configured, the documented platform workflows still complete on the deterministic baseline with no hardcoded credentials or model names.

## Assumptions

- The existing Features 2–8 artifacts remain the upstream source of truth for contracts, lineage, validation, attribution, schema evolution, AI metrics, and reporting.
- The canonical subscriptions registry will live at `docs/governance/subscriptions_registry.yaml` and will be the only authoritative source for subscription topology.
- OpenRouter is the only approved optional LLM provider for platform-assisted behavior, and all LLM-related configuration is read from environment variables.
- The latest Week 4 lineage snapshot is available through the existing workflow outputs and can be refreshed before contract generation or attribution when needed.
- Deterministic non-LLM behavior remains the default operating mode even when optional LLM-assisted behavior is available.

## Canonical Structure Notes _(mandatory)_

- This feature preserves the existing repository layout and extends it with one new governance artifact: `docs/governance/subscriptions_registry.yaml`.
- Existing output families remain authoritative: generated contracts, validation reports, lineage snapshots, violation logs, schema snapshots, and stakeholder reports.
- No parallel registry, alternate LLM provider, or duplicate source of truth is introduced.

## Implementation Prompt Integrity Checklist _(mandatory)_

- Prompt builds on prior approved specs and platform architecture.
- Prompt describes durable platform capability, not a milestone checkpoint or temporary migration task.
- Prompt preserves data-contract first-class artifact expectations and extends existing outputs instead of replacing them.
